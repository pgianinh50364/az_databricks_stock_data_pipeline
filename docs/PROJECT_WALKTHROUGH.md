# Stock Data Streaming Project Walkthrough 🚀

This comprehensive guide walks you through the complete setup, deployment, and operation of the Stock Data Streaming platform from start to finish.

## 🎯 Project Overview

This project implements a modern data engineering pipeline that:
- Ingests stock market data from Yahoo Finance API and CSV files
- Streams data through Apache Kafka for real-time processing
- Processes data in Azure Databricks using Delta Live Tables
- Implements a medallion architecture (Bronze → Silver → Gold)
- Stores processed data in Azure Data Lake Storage

## 📋 Prerequisites

Before starting, ensure you have:

- **Azure Subscription** with appropriate permissions
- **Python 3.12+** installed
- **Terraform** (v1.0+) for infrastructure deployment
- **Azure CLI** for authentication
- **Databricks CLI** configured
- **Administrative privileges** on your local machine

## 🏗️ Phase 1: Infrastructure Setup

### Step 1: Install Dependencies

```powershell
# Install UV package manager
pip install uv

# Navigate to project directory
cd c:\Users\gianinh50365\Desktop\data_streaming

# Create virtual environment and install dependencies
uv sync --dev

# Activate virtual environment  
.venv\Scripts\activate  # Windows
```

### Step 2: Deploy Azure Infrastructure with Terraform

```powershell
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Deploy infrastructure (takes 5-10 minutes)
terraform apply

# Note down the outputs:
# - resource_group_name
# - storage_account_name  
# - databricks_workspace_url
```

**Resources Created:**
- **Resource Group**: `RG-StockProjekt`
- **Storage Account**: `stockstreametl` (Data Lake Gen2)
- **Databricks Workspace**: `databricks-etl-workspace`
- **Access Connector**: `databricks-etl-con` (for secure integration)
- **Storage Containers**: `raw`, `bronze`, `silver`, `gold`, `metastore`

### Step 3: Configure Azure Permissions
**In Azure cloud console**:
- Go to your azure blob storage account IAM
- Add your databricks access connector as a *storage blob data contributor* 


## 🔐 Phase 2: Databricks Workspace Configuration

### Step 4: Initial Databricks Setup

```powershell
# Sign in to Databricks workspace for the first time using your email
# Visit: https://accounts.azuredatabricks.net/login
# Use Microsoft Entra ID authentication
```

**In Databricks Account Console:**
1. Navigate to **Account Settings**
2. Add your email as **Account Admin**
3. Assign your user to the workspace with **Admin** privileges

### Step 5: Configure Databricks Metastore

**In Databricks Account Console::**

1. **Create Unity Catalog Metastore:**
   - Go to **Catalog** → **Create Metastore**
   - Name: `stock_data_metastore`
   - Region: `Southeast Asia` (match your resources)
   - Storage Root: `abfss://metastore@stockstreametl.dfs.core.windows.net/`
   - Access Connector: Select `databricks-etl-con`

2. **Assign Metastore to Workspace:**
   - Select your workspace
   - Assign the metastore
   - Set your account as **Metastore Admin**

3. **Create Catalog and Schema:**
   - Upload or Run the command in `Setup.ipynb` notebook  

### Step 6: Create External Locations

**In your Databricks workspace**
1. **Create your databricks credential:**
   - Go to catalog and create a credential with your Databricks access connector principal ID
2.  **For each storage container (except the metastore), create external locations:**
   - Use the credential that you've created to create a new external location


## 📦 Phase 3: Databricks Asset Bundle Deployment

### Step 7: Configure Databricks CLI

```powershell
# Authenticate with Databricks
databricks auth login

# Follow prompts to:
# 1. Enter your Databricks workspace URL
# 2. Complete OAuth authentication in browser
# 3. Create a profile (e.g., "AZ_DEV")
```

### Step 8: Deploy Asset Bundle

```powershell
# Navigate to bundle directory
cd ..\stock_bundles

# Deploy bundle to development environment
databricks bundle deploy --target dev -p AZ_DEV
```

**Expected Error on First Deploy if you haven't create a catalog:**
```
Error: cannot create pipeline: Catalog 'stock_data_cata' does not exist.
```

**Solution:**
1. Open Databricks workspace UI
2. Create/run the Databricks setup notebook manually or trigger the job in Job & Pipelines tab
3. Ensure catalog and schemas exist
4. Re-run the bundle deploy command

### Step 9: Upload Sample Data

**For testing purposes, upload data to raw volume, Using Databricks UI:**
1. Go to Catalog → stock_data_cata → raw → rawvolume
2. Upload first 10 stock symbol folders
3. Save remaining 5 symbols for CDC (Change Data Capture) testing


## 🔄 Phase 4: Data Pipeline Execution

### Step 10: Run Bronze Ingestion Job

```powershell
# Run bronze layer ingestion
databricks bundle run bronze_ingestion --target dev -p AZ_DEV

# Monitor job execution in Databricks UI
# Job will process ticker data and run incremental loading
```

### Step 11: Execute Silver Pipeline

```powershell
# Run silver data transformation pipeline
databricks bundle run pipeline_silver_run --target dev -p AZ_DEV --wait

# Pipeline features:
# - Auto-optimization enabled
# - Schema evolution support
# - Data quality checks
```

### Step 12: Execute Gold Pipeline

```powershell
# Run gold analytics pipeline (serverless)
databricks bundle run pipeline_gold_run --target dev -p AZ_DEV --wait

# Gold layer provides:
# - Aggregated data for analytics
# - Optimized query performance
# - Business-ready datasets
```

## 💾 Phase 5: Data Persistence & Testing

### Step 13: Save Processed Data

**Using Data Saving Notebook:**
1. Open the data saving notebook in Databricks
2. Configure output paths to storage containers
3. Run notebook to persist gold layer data
4. Verify data is saved to appropriate containers

### Step 14: Test Incremental Loading
1. Upload new data for each stock symbols to test incremental loading
2. In Databricks UI, go to your Volumes/{catalog_name}/{schema_name}/{volume_name} (the old data uploaded file path) to upload all the data in data/new_data folder
3. Trigger `bronze_ingestion` → `pipeline_silver_run` → `pipeline_gold_run` to get the latest data.
*(Note: `pipeline_gold_run` must perform a full request)*

## 🧹 Phase 5: Cleanup & Destruction

### Step 15: Clean Development Environment

```powershell
# Destroy Databricks bundle
databricks bundle destroy --target dev -p AZ_DEV --auto-approve
```

### Step 16: Destroy Azure Infrastructure

```powershell
# Navigate to terraform directory
cd terraform

# Destroy all Azure resources
terraform destroy --auto-approve
```

## 🆘 Troubleshooting Guide


1. **Azure quotas limit exceeded**: Request more cores or go serverless (recommend)
2. **Terraform error**: Delete `.terraform`, `terraform.lock.hcl`, `terraform.tfstate`, `terraform.tfstate.var` files.
3. **Databricks permission only have view permission**: Modify your host in {your-databricks-asset-bundle}/databricks.yml with your current Azure databricks workspace.
4. **Databricks profile no permission in workspace**: Go to `"C:\Users\<your-user-name>\.databrickscfg"` and delete the profile that have no permission, then re-create with proper `databricks auth login`

## 📚 Next Steps

After successful deployment:

1. **Explore advanced features**: Schema evolution, time travel, data lineage
2. **Implement monitoring**: Set up alerts for pipeline failures
3. **Scale the solution**: Add more data sources and transformation logic
4. **Optimize performance**: Tune cluster sizing and partition strategies
5. **Production deployment**: Use production target with proper security configurations

---

**🎯 You've successfully implemented a production-ready data streaming platform!**