import os
import sys
import time
import subprocess
import signal

# Absolute path resolutions
INFRA_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(INFRA_DIR)
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "contracts", "situation.schema.json")

# Define all service targets
# Format: (Service Name, Folder Name, Port)
SERVICES = [
    ("Persistence Service", "persistence_mcp", 8007),
    ("Telemetry Ingestion", "telemetry_ingestion_mcp", 8002),
    ("Behavior Anomaly", "behavior_anomaly_mcp", 8003),
    ("GNN Flow Predictor", "gnn_flow_predictor_mcp", 8004),
    ("MARL Orchestrator", "marl_orchestrator_mcp", 8005),
    ("Stats Analysis", "stats_analysis_mcp", 8006),
    ("Gateway MCP & Web UI", "gateway_mcp", 8001),
]

processes = []

def shutdown_services(sig=None, frame=None):
    print("\n[Ecosystem Bootstrapper] Intercepted shutdown command. Initiating clean termination sequence...")
    for name, proc in processes:
        print(f"Terminating service process: {name} (PID: {proc.pid})")
        try:
            # On Windows, taskkill or standard terminate kills cleanly
            if os.name == 'nt':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                proc.terminate()
        except Exception as e:
            print(f"Error terminating {name}: {e}")
    print("[Ecosystem Bootstrapper] Clean shutdown complete. All background slots cleared.")
    sys.exit(0)

# Register signal intercepts for Ctrl+C
signal.signal(signal.SIGINT, shutdown_services)
signal.signal(signal.SIGTERM, shutdown_services)

def main():
    print("=" * 70)
    print("    SYNAPSE GRID — VENUE OPERATING SYSTEM (LOCAL ECOSYSTEM RUNNER)    ")
    print("=" * 70)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Validation Schema: {SCHEMA_PATH}")
    print("Initializing FastAPI microservices mesh on localhost...\n")

    # Start persistence first to allow DB schema initialization
    persistence_dir = os.path.join(PROJECT_ROOT, "mcp", "persistence_mcp")
    env = os.environ.copy()
    env["PORT"] = "8007"
    env["SCHEMA_PATH"] = SCHEMA_PATH

    print("[1/7] Booting Persistence storage MCP server on Port 8007...")
    p_proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=persistence_dir,
        env=env
    )
    processes.append(("Persistence Service", p_proc))
    
    # Wait for SQLite to compile
    time.sleep(2.0)

    # Launch remaining nodes
    for i, (name, folder, port) in enumerate(SERVICES[1:], start=2):
        print(f"[{i}/7] Booting {name} on Port {port}...")
        service_dir = os.path.join(PROJECT_ROOT, "mcp", folder)
        
        s_env = os.environ.copy()
        s_env["PORT"] = str(port)
        s_env["SCHEMA_PATH"] = SCHEMA_PATH
        s_env["PERSISTENCE_URL"] = "http://localhost:8007"
        s_env["INGESTION_URL"] = "http://localhost:8002"
        s_env["ANOMALY_URL"] = "http://localhost:8003"
        s_env["GNN_URL"] = "http://localhost:8004"
        s_env["MARL_URL"] = "http://localhost:8005"
        s_env["STATS_URL"] = "http://localhost:8006"

        proc = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=service_dir,
            env=s_env
        )
        processes.append((name, proc))
        time.sleep(0.5)

    print("\n" + "=" * 70)
    print("    SYNAPSE GRID BOOTED SUCCESSFULY!    ")
    print("    Access Dashboard: http://localhost:8001/    ")
    print("    (Press Ctrl+C to terminate the ecosystem)    ")
    print("=" * 70)

    # Keep bootstrapper thread alive
    while True:
        try:
            time.sleep(1.0)
            # Check if any process has died
            for name, proc in processes:
                poll = proc.poll()
                if poll is not None:
                    print(f"\n[CRITICAL WARNING] Service '{name}' terminated unexpectedly with code {poll}!")
                    shutdown_services()
        except (KeyboardInterrupt, SystemExit):
            shutdown_services()

if __name__ == "__main__":
    main()
