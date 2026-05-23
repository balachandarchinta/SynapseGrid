import os
import json
import httpx
from fastapi import FastAPI, HTTPException, Request
from jsonschema import validate, ValidationError

app = FastAPI(title="MARL Orchestrator MCP Service (Upgraded)", description="Autonomous Multi-Agent command unit executing self-correcting RAG loops and Saga pattern compensations.")

# Configuration
PERSISTENCE_URL = os.getenv("PERSISTENCE_URL", "http://localhost:8007")
SCHEMA_PATH = os.getenv("SCHEMA_PATH", os.path.join(os.path.dirname(__file__), "../../contracts/situation.schema.json"))

def load_schema():
    try:
        with open(SCHEMA_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema: {e}")
        return None

schema_cache = load_schema()

# ----------------- SELF-CORRECTING AGENTIC RAG RETRIEVAL -----------------
def hybrid_retrieve_precedent(anomaly_type: str, query_density: float, relax_factor: float = 0.0):
    """Simulates a localized vector database containing venue Standard Operating Procedures (SOPs)."""
    sop_rules = [
        {"anomaly": "STAMPEDE_PANIC", "target_density_min": 3.0, "rules": "EMERGENCY SIGN OVERRIDE: OPEN BYPASS EXIT CORRIDORS IMMEDIATELY"},
        {"anomaly": "CROWD_CRUSH_HAZARD", "target_density_min": 5.0, "rules": "STOP CONTROL ENGAGED: THROTTLE TURNSTILES AND ROUTE CROWDS TO SEATING CORRIDORS"},
        {"anomaly": "TURBULENCE_WARNING", "target_density_min": 2.5, "rules": "RESTRICTED ACCESS: THROTTLE INFLOW CHANNELS BY 50%"},
    ]
    
    matches = []
    for rule in sop_rules:
        if rule["anomaly"] == anomaly_type:
            # Validation constraint: density must exceed the SOP's minimum density threshold
            # Under relaxed constraints, we decrease the threshold requirement
            threshold = rule["target_density_min"] - relax_factor
            if query_density >= threshold:
                matches.append(rule)
                
    return matches

def execute_agentic_rag_loop(anomaly_type: str, query_density: float) -> str:
    """Runs a self-correcting RAG loop (max 2 iterations) to retrieve verified SOP guidelines."""
    # Iteration 1: Strict query constraints
    print(f"[RAG LOOP - ITERATION 1] Initiating precedent search for {anomaly_type} (Density: {query_density:.2f})...")
    matches = hybrid_retrieve_precedent(anomaly_type, query_density, relax_factor=0.0)
    
    if matches:
        print(f"[RAG LOOP - SUCCESS] Strict SOP context verified successfully on Iteration 1.")
        return matches[0]["rules"]
        
    # Iteration 2: Self-correction (Relaxing retrieval constraints)
    print(f"[RAG LOOP - WARNING] Strict SOP context empty or failed validation! Relaxing search constraints by 1.5 units...")
    matches = hybrid_retrieve_precedent(anomaly_type, query_density, relax_factor=1.5)
    
    if matches:
        print(f"[RAG LOOP - SUCCESS] SOP context verified under relaxed criteria on Iteration 2.")
        return matches[0]["rules"]
        
    # Fallback to basic venue safety regulations
    print(f"[RAG LOOP - RETRY FAILED] Precedent SOP database exhausted. Falling back to basic venue safety regulations.")
    return "WARNING: HIGH DENSITY DETECTED. PROCEED CAUTIOUSLY TO EXITS."

# ----------------- DISTRIBUTED SAGA TRANSACTION ENGINES -----------------
async def execute_physical_gate_updates(override_policy: str, node: str):
    """Simulates physical signage update for a single stadium node."""
    # Simulate network drop for physical display boards
    # We simulate a failure on Gate B when executing Concourse Flow Control to show Saga rollbacks
    if node == "Gate B" and override_policy == "CONCOURSE_FLOW_CONTROL":
        print(f"[SAGA STEP - FAILURE] Connection timeout on Gate B physical display signage board!")
        raise ConnectionError("Timeout connecting to display socket.")
        
    print(f"[SAGA STEP] Successfully changed signage state at {node} to: {override_policy}")

async def compensate_saga_transaction(updated_nodes: list):
    """Saga Compensation Rollback: Reverts all successfully updated signs back to safe ticketing baselines."""
    print(f"[SAGA COMPENSATING] Initiating backward-facing compensation rollback for successfully modified nodes...")
    for node in updated_nodes:
        print(f"[SAGA COMPENSATE] Reverted signage board at {node} back to 'PROCEED: Ticket Scan Active'.")
    print(f"[SAGA COMPENSATING] globally verified, physically safe configuration restored successfully.")

# ----------------- PRIMARY COORDINATION -----------------
@app.post("/orchestrate")
async def orchestrate_action(request: Request):
    """Evaluates frame and anomaly assessments, resolves self-correcting RAG loops, and executes Saga physical steps."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    frame = payload.get("frame", {})
    assessments = payload.get("assessments", {})

    if schema_cache and frame:
        try:
            validate(instance=frame, schema=schema_cache)
        except ValidationError as ve:
            raise HTTPException(status_code=422, detail=f"Schema Validation Error: {ve.message}")

    # Standard signage baselines
    signage_states = {
        "Gate A": "PROCEED: Ticket Scan Active",
        "Gate B": "PROCEED: Ticket Scan Active",
        "Main Concourse": "FLOW CLEAR: Keep Moving",
        "South Seating": "ACCESS OK: Follow Section Signs",
        "North Seating": "ACCESS OK: Follow Section Signs",
        "Food Court": "OPEN: Standard Operations"
    }
    
    overrides_triggered = []

    # Coordinate physical display sign updates
    async with httpx.AsyncClient() as client:
        for node_id, assess in assessments.items():
            anomaly_type = assess.get("anomaly_type", "NORMAL")
            
            # Skip if normal
            if anomaly_type == "NORMAL":
                continue

            node_info = frame.get("nodes", {}).get(node_id, {})
            density = node_info.get("domain_numeric_values", {}).get("density_per_sqm", 0.0)

            # 1. Resolve self-correcting RAG loop to get verified policy override
            rules_instruction = execute_agentic_rag_loop(anomaly_type, density)

            # Map anomaly to nodes to update
            if anomaly_type == "STAMPEDE_PANIC" and node_id in ["Gate A", "Gate B"]:
                override_policy = "BYPASS_ENGAGED"
                nodes_to_update = ["Gate A", "Main Concourse"]
            elif anomaly_type == "CROWD_CRUSH_HAZARD" and node_id == "Main Concourse":
                override_policy = "CONCOURSE_FLOW_CONTROL"
                nodes_to_update = ["Gate A", "Gate B", "Main Concourse"]
            elif anomaly_type == "TURBULENCE_WARNING" and node_id == "Food Court":
                override_policy = "RESTRICT_FLOW"
                nodes_to_update = ["Food Court"]
            else:
                override_policy = "BASE_SAFETY_ALERTS"
                nodes_to_update = [node_id]

            # 2. Execute physical signage updates as a Saga Transaction Chain
            print(f"[SAGA] Initiating transaction chain for {override_policy} updates across: {nodes_to_update}")
            successful_updates = []
            try:
                for node in nodes_to_update:
                    await execute_physical_gate_updates(override_policy, node)
                    successful_updates.append(node)
                
                # Apply the updates to virtual state list
                for node in successful_updates:
                    signage_states[node] = rules_instruction
                
                overrides_triggered.append({
                    "target_node": node_id,
                    "policy_code": override_policy,
                    "reason": f"Active: {anomaly_type} (Rules: {rules_instruction})"
                })
                
                # Log success to persistence layer
                try:
                    await client.post(
                        f"{PERSISTENCE_URL}/log_telemetry",
                        json={
                            "agent_name": "MARL Saga Orchestrator",
                            "metric_type": "marl_saga_success",
                            "target_node_id": node_id,
                            "value": 1.0,
                            "metadata_str": f"Policy: {override_policy}, Successfully deployed signs."
                        }
                    )
                except Exception:
                    pass

            except ConnectionError as ce:
                # SAGA TRANSACTION CHAIN ENCOUNTERED A FAILURE! Trigger backward-facing compensations!
                print(f"[SAGA CHAIN ERROR] SAGA step failed. Reverting transaction chain...")
                await compensate_saga_transaction(successful_updates)
                
                # Revert signage configurations back to safety defaults
                for node in nodes_to_update:
                    signage_states[node] = "SAGA ROLLBACK: USE NEAREST SAFE EXIT!"
                
                # Log compensation to persistence storage
                try:
                    await client.post(
                        f"{PERSISTENCE_URL}/log_anomaly",
                        json={
                            "anomaly_type": "SAGA_CHAIN_COMPENSATION",
                            "confidence": 0.95,
                            "raw_log_str": f"Saga chain failed on physical sign updates due to Gate connection drop. Compesating rollbacks completed."
                        }
                    )
                except Exception:
                    pass

    return {
        "status": "success",
        "signage_states": signage_states,
        "overrides_triggered": overrides_triggered
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
