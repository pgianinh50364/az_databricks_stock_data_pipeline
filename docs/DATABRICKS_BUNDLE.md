# Databricks Asset Bundle Guide 📦

Complete documentation for the Databricks Asset Bundle implementation in the Stock Data Streaming project, covering deployment, configuration, and management of data pipelines.

## 🎯 Overview

The Databricks Asset Bundle provides Infrastructure as Code (IaC) for Databricks workspaces, enabling:

- **Version-controlled deployments** of notebooks, jobs, and pipelines
- **Environment management** (dev, staging, prod) with different configurations
- **Automated CI/CD** integration for data pipelines
- **Dependency management** and artifact building
- **Resource lifecycle management** and cleanup

## 📁 Bundle Structure

```
stock_bundles/
├── 📄 databricks.yml                   # Main bundle configuration
├── 📄 pyproject.toml                   # Python package configuration  
├── 📂 resources/                       # Pipeline and job definitions
│   ├── bronze.ingestion.yml            # Bronze layer job configuration
│   ├── silver.pipeline.yml             # Silver DLT pipeline
│   ├── gold.pipeline.yml               # Gold DLT pipeline
│   └── workspace.config.yml            # Workspace configuration
├── 📂 src/                             # Source code
│   ├── 📂 dlt_pipelines/               # Delta Live Tables pipelines
│   │   ├── silver_dlt_pipeline/        # Silver layer transformations
│   │   └── gold_dlt_pipeline/          # Gold layer aggregations
│   ├── 📂 notebook/                    # Databricks notebooks
│   │   ├── stock_name.ipynb            # Ticker loading notebook
│   │   ├── bronze_ingestion.ipynb      # Bronze ingestion logic
│   │   └── data_saving.ipynb           # Data persistence notebook
│   └── 📂 utilities/                   # Helper functions and utilities
└── 📂 .venv/                           # Virtual environment (created by uv)
```

## ⚙️ Configuration Files

### 1. Main Bundle Configuration (`databricks.yml`)

```yaml
bundle:
  name: stock_bundles
  uuid: 96c3405a-409e-49f1-9abd-f08b45103dd5

artifacts:
  python_artifact:
    type: whl
    build: uv build --wheel

include:
  - resources/*.yml
  - resources/*/*.yml

targets:
  dev:
    presets:
      name_prefix: "${workspace.current_user.short_name}_test_dev_"
    mode: development
    default: true
    workspace:
      host: <modify-this-to-your-workspace-url>
    permissions:
      - level: CAN_MANAGE
        user_name: "${workspace.current_user.userName}"

  prod:
    presets:
      name_prefix: "${workspace.current_user.short_name}_deploy_prod_"
    mode: production
    workspace:
      host: <modify-this-to-your-workspace-url>
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    permissions:
      - level: CAN_MANAGE
        user_name: "${workspace.current_user.userName}"
```

**Key Configuration Elements:**
- **Bundle Name**: Unique identifier for the asset bundle
- **Artifacts**: Python wheel building using UV package manager
- **Targets**: Environment-specific configurations (dev/prod)
- **Permissions**: Access control for workspace resources

### 2. Bronze Layer Job (`resources/bronze.ingestion.yml`)

```yaml
resources:
  jobs:
    bronze_ingestion:
      name: bronze_ingestion
      tasks:
        - task_key: ticker_loader
          notebook_task:
            notebook_path: ../src/notebook/stock_name.ipynb
            source: WORKSPACE
        - task_key: incremental_loader
          depends_on:
            - task_key: ticker_loader
          for_each_task:
            inputs: "{{tasks.ticker_loader.values.output_key}}"
            task:
              task_key: incremental_loader_iteration
              notebook_task:
                notebook_path: ../src/notebook/bronze_ingestion.ipynb
                base_parameters:
                  ticker: "{{input.ticker}}"
                source: WORKSPACE
      queue:
        enabled: true
      performance_target: STANDARD
```

**Features:**
- **Task Dependencies**: ticker_loader runs before incremental_loader
- **Dynamic Parallelization**: for_each_task processes multiple tickers
- **Parameter Passing**: ticker symbols passed between tasks
- **Queue Management**: Job queuing enabled for resource optimization

### 3. Silver DLT Pipeline (`resources/silver.pipeline.yml`)

```yaml
resources:
  pipelines:
    pipeline_silver_run:
      name: silver_run
      libraries:
        - glob:
            include: ../src/dlt_pipelines/silver_dlt_pipeline/transformation/**
      schema: silver
      continuous: false
      development: false
      channel: CURRENT
      catalog: stock_data_cata
      root_path: ../src/dlt_pipelines/silver_dlt_pipeline
      configuration:
        spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite: "true"
        spark.databricks.delta.properties.defaults.autoOptimize.autoCompact: "true"
      environment:
        dependencies:
          - yfinance==0.2.65
      permissions:
      - level: CAN_MANAGE
        user_name: "${workspace.current_user.userName}"
```

**Configuration Details:**
- **Schema Target**: Data written to `silver` schema
- **Auto-Optimization**: Write optimization and auto-compaction enabled
- **Dependencies**: yfinance library for stock data processing
- **Channel**: CURRENT channel for latest runtime features

### 4. Gold DLT Pipeline (`resources/gold.pipeline.yml`)

```yaml
resources:
  pipelines:
    pipeline_gold_run:
      name: gold_run
      libraries:
        - glob:
            include: ../src/dlt_pipelines/gold_dlt_pipeline/transformation/**
      schema: gold
      catalog: stock_data_cata
      serverless: true
      root_path: ../src/dlt_pipelines/gold_dlt_pipeline
      configuration:
        spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite: "true"
        spark.databricks.delta.properties.defaults.autoOptimize.autoCompact: "true"
      environment:
        dependencies:
          - yfinance==0.2.65
```

**Key Features:**
- **Serverless Compute**: Cost-optimized serverless runtime
- **Gold Schema**: Business-ready aggregated data
- **Library Dependencies**: External package management

## 🚀 Deployment Guide

### Prerequisites

```powershell
# Install UV package manager
pip install uv

# Install Databricks CLI
pip install databricks-cli

# Navigate to bundle directory
cd stock_bundles

# Initialize Python environment
uv sync --dev
```

### Step 1: Authentication Setup

```powershell
# Configure Databricks authentication
databricks auth login

# Follow prompts:
# 1. Enter workspace URL: https://adb-1302389120332807.7.azuredatabricks.net
# 2. Complete OAuth flow in browser
# 3. Create profile name (e.g., "AZ_DEV")
```

### Step 2: Validate Bundle Configuration

```powershell
# Validate bundle configuration
databricks bundle validate --target dev

# Expected output:
# Configuration is valid
```

### Step 3: Deploy to Development

```powershell
# Deploy bundle to development environment
databricks bundle deploy --target dev -p AZ_DEV

# Monitor deployment progress
# Resources will be prefixed with your username for isolation
```

**Deployment Process:**
1. **Artifact Building**: Python wheel created using UV
2. **Resource Validation**: All YAML configurations checked
3. **Workspace Upload**: Notebooks and libraries uploaded
4. **Job Creation**: Jobs and pipelines created/updated
5. **Permission Assignment**: Access control applied

### Step 4: Execute Pipeline Components

```powershell
# Run bronze ingestion job
databricks bundle run bronze_ingestion --target dev -p AZ_DEV

# Run silver transformation pipeline
databricks bundle run pipeline_silver_run --target dev -p AZ_DEV --wait

# Run gold aggregation pipeline
databricks bundle run pipeline_gold_run --target dev -p AZ_DEV --wait
```

## 🔄 Data Pipeline Architecture

### Bronze Layer (Raw Data Ingestion)
- **Purpose**: Land raw data from various sources
- **Process**: Load ticker symbols → Parallel incremental loading
- **Output**: Raw stock data in Delta format
- **Location**: `stock_data_cata.bronze.*`

### Silver Layer (Data Transformation)
- **Purpose**: Clean, standardize, and enrich data
- **Process**: Data quality checks → Schema standardization → Business logic
- **Features**: Auto-optimization, schema evolution
- **Output**: Cleansed dimensional data
- **Location**: `stock_data_cata.silver.*`

### Gold Layer (Analytics Ready)
- **Purpose**: Aggregate data for analytics and reporting
- **Process**: Calculate metrics → Create aggregations → Optimize for queries
- **Compute**: Serverless for cost efficiency
- **Output**: Business-ready datasets
- **Location**: `stock_data_cata.gold.*`

## 🎛️ Environment Management

### Development Environment (`--target dev`)
- **Name Prefix**: `{username}_test_dev_`
- **Mode**: Development (schedules paused, resource prefixing)
- **Purpose**: Testing and development work
- **Isolation**: User-specific resource naming

### Production Environment (`--target prod`)
- **Name Prefix**: `{username}_deploy_prod_`
- **Mode**: Production (full functionality enabled)
- **Root Path**: Explicit workspace path
- **Purpose**: Production workloads

### Environment Variables

```yaml
# Available variables in bundle configuration
${workspace.current_user.userName}     # Current user's email
${workspace.current_user.short_name}   # Short username
${bundle.name}                         # Bundle name
${bundle.target}                       # Current target (dev/prod)
```

## 🔧 Advanced Configuration

### Schedule Configuration

```yaml
# Add to job configuration  
schedule:
  quartz_cron_expression: "0 0 2 * * ?"  # Daily at 2 AM
  timezone_id: "UTC"
  pause_status: "PAUSED"  # Start paused in dev
```

### Notification Setup

```yaml
# Add to job configuration
notification_settings:
  no_alert_for_skipped_runs: false
  no_alert_for_canceled_runs: false
```

## 📊 Monitoring & Management

### Bundle Status Commands

```powershell
# Check bundle status
databricks bundle summary --target dev

# List deployed resources
databricks bundle resources --target dev

# View pipeline status
databricks bundle run pipeline_silver_run --target dev --wait
```

### Resource Management

```powershell
# Update specific resource
databricks bundle deploy --target dev --resource jobs/bronze_ingestion

# Redeploy entire bundle
databricks bundle deploy --target dev --force

# Clean up old resources
databricks bundle destroy --target dev --auto-approve
```

### Logs and Debugging

```powershell
# View job run details
databricks jobs runs list --job-id <job-id>

# Get pipeline run logs
databricks pipelines events list --pipeline-id <pipeline-id>

# Bundle deployment logs
databricks bundle deploy --target dev --verbose
```

## 🛠️ Development Workflow

### 1. Local Development

```powershell
# Make changes to notebooks or pipeline code
# Edit files in src/ directory

# Validate changes locally
databricks bundle validate --target dev

# Test deployment
databricks bundle deploy --target dev
```

### 2. Testing Changes

```powershell
# Deploy with test data
databricks bundle deploy --target dev

# Run subset of pipeline
databricks bundle run bronze_ingestion --target dev

# Validate output
# Check Databricks UI for pipeline results
```

### 3. Production Deployment

```powershell
# Deploy to production
databricks bundle deploy --target prod

# Schedule production jobs
# Enable schedules through Databricks UI or bundle config
```

## 🚨 Troubleshooting

### Common Issues

**Issue**: `Catalog 'stock_data_cata' does not exist`
```powershell
# Solution: Create catalog manually in Databricks UI
# Or run Unity Catalog setup notebook first
```

**Issue**: Permission errors
```powershell
# Solution: Check workspace permissions
databricks workspace permissions get /path/to/notebook

# Or delete the bundle configuration when deploy the databricks, then re-deploy
```

**Issue**: Bundle deployment timeout (connectivity issues)
```powershell
# Solution: Wait around 30s then re-deploy
```

### Debug Commands

```powershell
# Validate bundle syntax
databricks bundle validate --target dev

# Show what would be deployed
databricks bundle deploy --target dev --dry-run

# Force redeploy all resources
databricks bundle deploy --target dev --force

# View detailed resource information
databricks bundle resources --target dev --verbose
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Databricks Bundle
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install uv databricks-cli
          cd stock_bundles
          uv sync
      - name: Deploy bundle
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          cd stock_bundles
          databricks bundle deploy --target prod
```

## 📚 Best Practices

### 1. Resource Naming
- Use consistent naming conventions
- Include environment in resource names
- Use descriptive names for jobs and pipelines

### 2. Configuration Management
- Keep sensitive data in Databricks secrets
- Use environment-specific configurations
- Version control all bundle configurations

### 3. Dependencies
- Pin library versions in environment section
- Use UV for consistent dependency management
- Document external dependencies

### 4. Testing
- Test bundle validation before deployment
- Use development environment for testing
- Implement data quality checks in pipelines

### 5. Monitoring
- Enable pipeline monitoring and alerting
- Use Databricks UI for pipeline visibility
- Implement logging in notebook code

---

**🚀 Your Databricks Asset Bundle is now ready for production data processing!**