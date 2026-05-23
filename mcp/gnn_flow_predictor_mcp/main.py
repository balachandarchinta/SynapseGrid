import os
import json
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from jsonschema import validate, ValidationError

app = FastAPI(title="GNN Flow Predictor MCP Service", description="Forecasts spatiotemporal crowd bottlenecks across stadium nodes.")

SCHEMA_PATH = os.getenv("SCHEMA_PATH", os.path.join(os.path.dirname(__file__), "../../contracts/situation.schema.json"))

def load_schema():
    try:
        with open(SCHEMA_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema: {e}")
        return None

schema_cache = load_schema()

# Stadium directed pathway edges representing walkway networks
# Format: (Source, Target, Baseline Pathway Capacity Weight w_uv)
EDGES = [
    ("Gate A", "Main Concourse", 0.8),
    ("Gate B", "Main Concourse", 0.8),
    ("Main Concourse", "Food Court", 0.6),
    ("Main Concourse", "South Seating", 0.7),
    ("Main Concourse", "North Seating", 0.7),
    ("Food Court", "South Seating", 0.5),
    ("Food Court", "North Seating", 0.5),
    ("South Seating", "Main Concourse", 0.4),  # Egress flows
    ("North Seating", "Main Concourse", 0.4)
]

# Max safe threshold capacity densities per node
NODE_CAPACITIES = {
    "Gate A": 4.0,
    "Gate B": 4.0,
    "Main Concourse": 5.0,
    "South Seating": 6.0,
    "North Seating": 6.0,
    "Food Court": 4.5
}

@app.post("/predict")
async def predict_flow(request: Request):
    """Parses situation frame and uses GNN message passing to forecast 10-minute node spillovers."""
    try:
        frame = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if schema_cache:
        try:
            validate(instance=frame, schema=schema_cache)
        except ValidationError as ve:
            raise HTTPException(status_code=422, detail=f"Schema Validation Error: {ve.message}")

    nodes_data = frame.get("nodes", {})

    # Extract initial features (h_u^(0) = density)
    h_density = {}
    h_velocity = {}
    for node_name in NODE_CAPACITIES.keys():
        node_info = nodes_data.get(node_name, {})
        domain_vals = node_info.get("domain_numeric_values", {})
        h_density[node_name] = domain_vals.get("density_per_sqm", 0.0)
        h_velocity[node_name] = domain_vals.get("crowd_velocity_mps", 0.0)

    # GNN Message Passing Layer
    # Message from u to v: M_uv = w_uv * Density_u * (Velocity_u / 2.0)
    messages = {node: [] for node in NODE_CAPACITIES.keys()}
    
    for u, v, weight in EDGES:
        density_u = h_density[u]
        velocity_u = h_velocity[u]
        
        # Message is propagated only if source is starting to get congested (density_u > 1.5)
        if density_u > 1.5:
            # Kinetic-driven transfer energy
            msg = weight * density_u * (velocity_u / 2.0)
            messages[v].append(msg)

    # Node aggregation: h_v^(1) = h_v^(0) + sum(messages to v)
    predicted_densities = {}
    spillover_probabilities = {}
    forecasts = {}

    for node_name, baseline_density in h_density.items():
        incoming_msgs = messages[node_name]
        total_message = sum(incoming_msgs) if incoming_msgs else 0.0
        
        # Predicted density 10 minutes out
        # We model this as: PredDensity = CurrentDensity + 10-min accumulated message flow
        pred_density = float(np.clip(baseline_density + total_message * 0.8, 0.0, 15.0))
        predicted_densities[node_name] = pred_density

        # Spillover probability = Sigmoid( (Predicted Density - Node Capacity) * ScalingFactor )
        capacity = NODE_CAPACITIES[node_name]
        scaling_factor = 1.5
        diff = pred_density - capacity
        spillover_prob = float(1.0 / (1.0 + np.exp(-diff * scaling_factor)))
        spillover_probabilities[node_name] = spillover_prob

        # Categorize spillover
        if spillover_prob > 0.8:
            risk_level = "HIGH_SPILLOVER_RISK"
            desc = f"Bottleneck imminent. Overflow likelihood: {spillover_prob:.1%}. Activate re-routing."
        elif spillover_prob > 0.5:
            risk_level = "MODERATE_SPILLOVER_RISK"
            desc = f"Elevated build-up detected. Monitoring adjacencies."
        else:
            risk_level = "LOW_RISK"
            desc = "Flow rates balanced across transit corridors."

        forecasts[node_name] = {
            "node_id": node_name,
            "current_density": baseline_density,
            "predicted_density_10m": pred_density,
            "spillover_probability": spillover_prob,
            "risk_level": risk_level,
            "action_recommendation": desc
        }

    return {
        "status": "success",
        "predicted_densities": predicted_densities,
        "spillover_probabilities": spillover_probabilities,
        "forecasts": forecasts
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
