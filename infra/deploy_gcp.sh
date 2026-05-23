#!/bin/bash
# Get the directory of this script and resolve project root dynamically
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Project Configuration
PROJECT_ID="synapsegrid-497207"
REGION="us-central1"
REPO_NAME="synapse-grid-repo"
REGISTRY="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME"

set -e # Exit immediately on error

echo "=========================================================="
echo "    STARTING DEPLOYMENT FOR PROJECT: $PROJECT_ID"
echo "=========================================================="

# 1. Set Active GCP Project Context
echo "[1/5] Setting gcloud project context..."
gcloud config set project $PROJECT_ID

# 2. Enable Google Cloud APIs
echo "[2/5] Enabling GCP API services..."
gcloud services enable artifactregistry.googleapis.com run.googleapis.com sqladmin.googleapis.com

# 3. Create Artifact Registry Repository
echo "[3/5] Creating Artifact Registry Repository: $REPO_NAME..."
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Synapse Grid Production Registry" || true

# 4. Configure Docker Authentication (Wiping old config to clear typos)
echo "[4/5] Clearing docker config typos and authenticating..."
rm -f ~/.docker/config.json
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

# 5. Build, Tag, and Push Microservices Mesh
SERVICES=(
    "persistence_mcp"
    "telemetry_ingestion_mcp"
    "behavior_anomaly_mcp"
    "gnn_flow_predictor_mcp"
    "marl_orchestrator_mcp"
    "stats_analysis_mcp"
    "gateway_mcp"
)

echo "[5/5] Compiling and pushing container mesh locally..."
for service in "${SERVICES[@]}"; do
    # Replace underscore with dash for container naming compatibility
    image_name=$(echo "$service" | tr '_' '-')
    echo "Building $service as $image_name..."
    
    # Execute build using central root Dockerfile
    docker build --build-arg SERVICE_NAME="$service" -t "$REGISTRY/$image_name:latest" "$PROJECT_ROOT"
    
    echo "Pushing $image_name to Google Artifact Registry..."
    docker push "$REGISTRY/$image_name:latest"
done

echo "=========================================================="
echo "    MICROSERVICES MESH PUSHED TO GCP ARTIFACT REGISTRY!   "
echo "=========================================================="
echo ""
echo "NEXT STEPS:"
echo "1. Provision a Cloud SQL PostgreSQL Database in console or run:"
echo "   gcloud sql instances create synapse-db --database-version=POSTGRES_15 --tier=db-f1-micro --region=$REGION"
echo "   gcloud sql databases create synapse_grid --instance=synapse-db"
echo ""
echo "2. Deploy persistence-mcp (Pass Cloud SQL Connection):"
echo "   gcloud run deploy persistence-mcp --image=$REGISTRY/persistence-mcp:latest --region=$REGION --no-allow-unauthenticated --add-cloudsql-instances=$PROJECT_ID:$REGION:synapse-db --set-env-vars DATABASE_URL='postgresql://postgres:[PASSWORD]@/synapse_grid?host=/cloudsql/$PROJECT_ID:$REGION:synapse-db'"
echo ""
echo "3. Deploy Gateway and downstream MCP services using gcloud run deploy."
