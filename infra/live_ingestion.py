import os
import time
import random
import httpx

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8001/api/match_cast")

BATSMEN = ["Virat Kohli", "MS Dhoni", "Rinku Singh", "Hardik Pandya", "Dinesh Karthik", "Ravindra Jadeja"]
BOWLERS = ["Jasprit Bumrah", "Mohit Sharma", "Rashid Khan", "Mohammed Shami", "Yuzvendra Chahal"]

class T20Simulation:
    def __init__(self):
        self.overs = 18
        self.balls = 0
        self.runs = 175
        self.wickets = 4
        self.primary_batsman = "Virat Kohli"
        self.secondary_batsman = "Hardik Pandya"
        self.active_bowler = "Jasprit Bumrah"
        self.match_phase = "Steady Play"
        
        # Initial spatial states
        self.nodes = {
            "Gate A": {"crowd_velocity_mps": 0.8, "density_per_sqm": 1.1, "turnstile_flow_rate": 35.0, "cognitive_drift_index": 0.12},
            "Gate B": {"crowd_velocity_mps": 0.9, "density_per_sqm": 1.3, "turnstile_flow_rate": 40.0, "cognitive_drift_index": 0.15},
            "Main Concourse": {"crowd_velocity_mps": 1.2, "density_per_sqm": 1.8, "turnstile_flow_rate": 0.0, "cognitive_drift_index": 0.18},
            "South Seating": {"crowd_velocity_mps": 0.4, "density_per_sqm": 4.8, "turnstile_flow_rate": 0.0, "cognitive_drift_index": 0.10},
            "North Seating": {"crowd_velocity_mps": 0.3, "density_per_sqm": 4.5, "turnstile_flow_rate": 0.0, "cognitive_drift_index": 0.11},
            "Food Court": {"crowd_velocity_mps": 0.8, "density_per_sqm": 2.2, "turnstile_flow_rate": 0.0, "cognitive_drift_index": 0.20}
        }

    def step(self):
        """Advances T20 state machine by 1 ball, simulating crowd impacts & phase changes."""
        # Egress post-match logic
        if self.overs >= 20:
            self.overs = 20
            self.balls = 0
            self.match_phase = "Post Match Egress"
            narrative = "MATCH COMPLETE! Post Match Egress phase engaged. Crowd flushing systems fully active across all walkways."
            
            # Post-match egress spatial surges
            for name, metrics in self.nodes.items():
                if "Gate" in name:
                    metrics["crowd_velocity_mps"] = round(random.uniform(4.5, 5.5), 2)
                    metrics["density_per_sqm"] = round(random.uniform(4.0, 5.0), 2)
                    metrics["turnstile_flow_rate"] = round(random.uniform(150.0, 190.0), 2)
                elif "Concourse" in name:
                    metrics["crowd_velocity_mps"] = round(random.uniform(3.0, 4.0), 2)
                    metrics["density_per_sqm"] = round(random.uniform(5.0, 6.0), 2)
                else:
                    metrics["crowd_velocity_mps"] = round(random.uniform(2.0, 3.0), 2)
                    metrics["density_per_sqm"] = round(random.uniform(3.5, 4.5), 2)
            
            return narrative

        # Tick ball count
        self.balls += 1
        if self.balls > 6:
            self.balls = 1
            self.overs += 1
            self.active_bowler = random.choice(BOWLERS)

        # Transition match phase based on match states
        # Over 19.0 to 19.2: Innings Break (simulated brief halt)
        if self.overs == 19 and self.balls in [1, 2]:
            self.match_phase = "Innings Break"
            narrative = "INNINGS BREAK! Mid-innings interval. Spectator columns surging toward Food Court."
            self.nodes["Food Court"]["density_per_sqm"] = round(random.uniform(4.2, 5.8), 2)
            self.nodes["Food Court"]["crowd_velocity_mps"] = round(random.uniform(1.2, 1.8), 2)
        elif self.overs == 19 and self.balls == 3:
            self.match_phase = "Play Halted"
            narrative = "RAIN DELAY! Play Halted temporarily due to weather. Crowd seeking cover under concourse."
            self.nodes["Main Concourse"]["density_per_sqm"] = round(random.uniform(4.8, 6.5), 2)
            self.nodes["Main Concourse"]["crowd_velocity_mps"] = round(random.uniform(0.3, 0.7), 2)
        else:
            self.match_phase = "Steady Play"

            # Random cricket outcome weightings
            outcome = random.choices(
                [0, 1, 2, 4, 6, "W"],
                weights=[30, 40, 10, 10, 5, 5]
            )[0]

            # Process cricket logic
            if outcome == "W":
                self.wickets += 1
                self.primary_batsman = random.choice(BATSMEN)
                narrative = f"OUT! Wicket falls! {self.primary_batsman} walks to crease. Shock wave sweeps spectator seating."
                
                # Shock causes chaotic movement adjustments in concourses
                self.nodes["Main Concourse"]["crowd_velocity_mps"] = round(random.uniform(1.4, 1.8), 2)
                self.nodes["Main Concourse"]["density_per_sqm"] = round(random.uniform(3.0, 4.0), 2)
                self.nodes["South Seating"]["cognitive_drift_index"] = round(random.uniform(0.3, 0.5), 2)
            else:
                self.runs += outcome
                if outcome == 0:
                    narrative = f"Dot ball. Under-pressure batsman defends. Static crowd states."
                    self.nodes["Main Concourse"]["crowd_velocity_mps"] = round(random.uniform(0.8, 1.2), 2)
                elif outcome in [1, 2]:
                    narrative = f"{outcome} run(s) scored. Quick transit around seating pathways."
                elif outcome in [4, 6]:
                    narrative = f"BOUNDARY! Crowd erupts into celebration! High spatiotemporal energy."
                    self.nodes["South Seating"]["crowd_velocity_mps"] = round(random.uniform(0.4, 0.7), 2)
                    self.nodes["Main Concourse"]["crowd_velocity_mps"] = round(random.uniform(1.3, 1.7), 2)
                    self.nodes["Main Concourse"]["cognitive_drift_index"] = round(random.uniform(0.2, 0.4), 2)

        # Turnstile entrance queues build up in late overs (Gate A gets high congestion)
        if self.overs >= 19:
            self.nodes["Gate A"]["density_per_sqm"] = round(random.uniform(5.5, 9.0), 2)
            self.nodes["Gate A"]["turnstile_flow_rate"] = round(random.uniform(140.0, 190.0), 2)
            self.nodes["Gate A"]["crowd_velocity_mps"] = round(random.uniform(0.01, 0.1), 2)
        else:
            self.nodes["Gate A"]["density_per_sqm"] = round(random.uniform(1.0, 3.0), 2)
            self.nodes["Gate A"]["turnstile_flow_rate"] = round(random.uniform(30.0, 90.0), 2)

        # General Food Court adjustment
        if self.match_phase != "Innings Break":
            if self.balls == 6:
                self.nodes["Food Court"]["density_per_sqm"] = round(random.uniform(3.5, 4.5), 2)
                self.nodes["Food Court"]["crowd_velocity_mps"] = round(random.uniform(0.5, 0.9), 2)
            else:
                self.nodes["Food Court"]["density_per_sqm"] = round(random.uniform(1.5, 2.5), 2)

        return narrative

    def generate_payload(self, narrative):
        nodes_payload = {}
        for name, metrics in self.nodes.items():
            density = metrics["density_per_sqm"]
            status = "NORMAL"
            if density > 5.0:
                status = "CRITICAL"
            elif density > 3.0:
                status = "WARNING"

            nodes_payload[name] = {
                "node_id": name,
                "status": status,
                "domain_numeric_values": {
                    "crowd_velocity_mps": metrics["crowd_velocity_mps"],
                    "density_per_sqm": metrics["density_per_sqm"],
                    "turnstile_flow_rate": metrics["turnstile_flow_rate"],
                    "cognitive_drift_index": metrics["cognitive_drift_index"]
                }
            }

        # 5G MEC Edge Processing: Anonymize plates & faces
        # Flatten all 6 nodes' numeric details into a 24-dimensional vector embedding
        feature_vector = []
        node_order = ["Gate A", "Gate B", "Main Concourse", "South Seating", "North Seating", "Food Court"]
        for node_name in node_order:
            node_vals = nodes_payload[node_name]["domain_numeric_values"]
            feature_vector.extend([
                node_vals["crowd_velocity_mps"],
                node_vals["density_per_sqm"],
                node_vals["turnstile_flow_rate"],
                node_vals["cognitive_drift_index"]
            ])

        return {
            "match_id": "IPL_2026_M56_LIVE",
            "event_id": "IPL_LIVE_FEED_M56",
            "marker": f"Over {self.overs}.{self.balls}",
            "score_summary": f"{self.runs}/{self.wickets} ({self.overs}.{self.balls} Ov)",
            "primary_actor": self.primary_batsman,
            "secondary_actor": self.secondary_batsman,
            "match_phase": self.match_phase,
            "plate_redacted": True,
            "faces_redacted": True,
            "feature_vector": feature_vector,
            "nodes": nodes_payload
        }

async def stream_live():
    print("=" * 60)
    print("    SYNAPSE GRID — UPGRADED 5G MEC SIMULATOR LIVE STREAMER    ")
    print("=" * 60)
    print(f"Target Gateway URL: {GATEWAY_URL}")
    print("Streaming MEC telemetry updates with 24D embeddings every 4 seconds...\n")

    sim = T20Simulation()
    
    async with httpx.AsyncClient() as client:
        while True:
            narrative = sim.step()
            payload = sim.generate_payload(narrative)
            
            # Embed narrative
            payload["narrative"] = narrative
            
            try:
                resp = await client.post(GATEWAY_URL, json=payload, timeout=3.0)
                if resp.status_code == 200:
                    print(f"[{payload['marker']} | {payload['match_phase']}] Ingested to Gateway. Score: {payload['score_summary']}")
                else:
                    print(f"[ERROR] Gateway rejected payload: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"[CONNECTION WARNING] Cannot stream to Gateway: {e}")

            time.sleep(4.0)

if __name__ == "__main__":
    import asyncio
    asyncio.run(stream_live())
