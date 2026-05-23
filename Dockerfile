# ======================================================================
# SYNAPSE GRID — UNIFIED PRODUCTION DOCKER BUILD ENGINE (GCP COMPATIBLE)
# ======================================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Pre-install all unified dependencies
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    jsonschema \
    httpx \
    redis \
    pydantic \
    numpy \
    pandas \
    psycopg2-binary \
    mcp

# Specify the microservice to build via Build Argument
# Options: telemetry_ingestion_mcp, behavior_anomaly_mcp, gnn_flow_predictor_mcp, 
#          marl_orchestrator_mcp, stats_analysis_mcp, persistence_mcp, gateway_mcp
ARG SERVICE_NAME
ENV SERVICE_NAME=${SERVICE_NAME}

# Copy specific microservice codebase
COPY mcp/${SERVICE_NAME}/ /app/

# Copy shared validation contract schemas
COPY contracts/ /app/contracts/

# Google Cloud Run default dynamic port binding
EXPOSE 8080
ENV PORT=8080
ENV SCHEMA_PATH="/app/contracts/situation.schema.json"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
