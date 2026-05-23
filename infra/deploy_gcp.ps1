# ======================================================================
# SYNAPSE GRID — GCP DEPLOYMENT AUTOMATION ENGINE (POWERSHELL)
# ======================================================================
# Resolve script directory and project root dynamically
$SCRIPT_DIR = $PSScriptRoot
if (!$SCRIPT_DIR) { $SCRIPT_DIR = Get-Location }
$PROJECT_ROOT = (Resolve-Path "$SCRIPT_DIR\..").Path

# Project Configuration
$PROJECT_ID = "synapsegrid-497207"
$REGION = "us-central1"
$REPO_NAME = "synapse-grid-repo"
$REGISTRY = "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME"

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "    STARTING DEPLOYMENT FOR PROJECT: $PROJECT_ID" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

# 1. Set Active GCP Project Context
Write-Host "[1/5] Setting gcloud project context..." -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

# 2. Enable Google Cloud APIs
Write-Host "[2/5] Enabling GCP API services..." -ForegroundColor Cyan
gcloud services enable artifactregistry.googleapis.com run.googleapis.com sqladmin.googleapis.com

# 3. Create Artifact Registry Repository
Write-Host "[3/5] Creating Artifact Registry Repository: $REPO_NAME..." -ForegroundColor Cyan
gcloud artifacts repositories create $REPO_NAME `
    --repository-format=docker `
    --location=$REGION `
    --description="Synapse Grid Production Registry"

# 4. Configure Docker Authentication (Wiping old config to clear typos)
Write-Host "[4/5] Clearing docker config typos and authenticating..." -ForegroundColor Cyan
Remove-Item -Path "$HOME\.docker\config.json" -ErrorAction SilentlyContinue
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

# 5. Build, Tag, and Push Microservices Mesh
$SERVICES = @(
    "persistence_mcp",
    "telemetry_ingestion_mcp",
    "behavior_anomaly_mcp",
    "gnn_flow_predictor_mcp",
    "marl_orchestrator_mcp",
    "stats_analysis_mcp",
    "gateway_mcp"
)

Write-Host "[5/5] Compiling and pushing container mesh locally..." -ForegroundColor Cyan
foreach ($service in $SERVICES) {
    # Replace underscore with dash for container naming compatibility
    $image_name = $service.Replace("_", "-")
    Write-Host "Building $service as $image_name..." -ForegroundColor Yellow
    
    # Execute build using central root Dockerfile
    docker build --build-arg SERVICE_NAME=$service -t "$REGISTRY/$image_name:latest" "$PROJECT_ROOT"
    
    Write-Host "Pushing $image_name to Google Artifact Registry..." -ForegroundColor Yellow
    docker push "$REGISTRY/$image_name:latest"
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "    MICROSERVICES MESH PUSHED TO GCP ARTIFACT REGISTRY!   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Provision a Cloud SQL PostgreSQL Database in console or run:" -ForegroundColor White
Write-Host "   gcloud sql instances create synapse-db --database-version=POSTGRES_15 --tier=db-f1-micro --region=$REGION" -ForegroundColor Gray
Write-Host "   gcloud sql databases create synapse_grid --instance=synapse-db" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Deploy persistence-mcp (Pass Cloud SQL Connection):" -ForegroundColor White
Write-Host "   gcloud run deploy persistence-mcp --image=$REGISTRY/persistence-mcp:latest --region=$REGION --no-allow-unauthenticated --add-cloudsql-instances=$PROJECT_ID:$REGION:synapse-db --set-env-vars DATABASE_URL='postgresql://postgres:[PASSWORD]@/synapse_grid?host=/cloudsql/$PROJECT_ID:$REGION:synapse-db'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Deploy Gateway and downstream MCP services using gcloud run deploy." -ForegroundColor White
