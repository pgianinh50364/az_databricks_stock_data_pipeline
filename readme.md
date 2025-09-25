# Stock Data Analytics Platform 

## 🚀 Key Features

### �📊 Data Pipeline Architecture
- **Medallion Architecture**: Bronze → Silver → Gold data layers using Delta Live Tables
- **Multi-source Ingestion**: Yahoo Finance API, historical CSV files, and batch processing
- **Delta Lake Storage**: ACID transactions, schema evolution, and time travel capabilities
- **Unity Catalog**: Centralized data governance and metadata management

### ☁️ Cloud-Native Infrastructure
- **Infrastructure as Code**: Terraform deployment with Azure resources
- **Databricks Asset Bundles**: Automated deployment of notebooks, jobs, and pipelines
- **Azure Integration**: Data Lake Storage Gen2, Access Connector, and Databricks Workspace
- **Serverless Computing**: Auto-scaling compute resources for cost optimization

### 🔧 Modern Development Experience
- **UV Package Manager**: Fast, reliable Python dependency management
- **Environment Isolation**: Development and production deployment targets
- **Git Integration**: Version control with proper security practices
- **Cross-platform Support**: Works on Windows, Linux, and macOS

## 📊 Data Processing Flow

1. **Data Ingestion**: Stock data from Yahoo Finance API and CSV files
2. **Bronze Layer**: Raw data landing with minimal transformation
3. **Silver Layer**: Data cleansing, validation, and standardization
4. **Gold Layer**: Business-ready aggregations and analytics datasets
5. **Storage Optimization**: Delta Lake format with auto-compaction and Z-ordering

## 🎯 Data engineering solution built on Azure that processes and analyzes stock market data using Databricks Delta Live Tables (Lakeflow Declarative Pipeline)

A comprehensive **Azure-based data engineering solution** that ingests, processes, and analyzes stock market data using modern data pipeline technologies including Kafka, Databricks, and Delta Lake.

## 🏗️ Architecture Overview

![alt text](https://github.com/pgianinh50364/az_databricks_stock_data_pipeline/blob/b417d9431bce568b6fd8def3d9b86ad191a07d03/docs/architecture.png)

## � Security-First Design

- ✅ **Secret management** for Databricks
- ✅ **Secure cleanup scripts** for complete reversal

## 📊 Data Flow

1. **Network Bridge**: Secure port forwarding connects ADLS to Databricks
2. **DLT Processing**: Databricks consumes stream and processes to Delta Lake
3. **Clean Architecture**: Bronze → Silver → Gold layers with proper schema evolution

## 🚀 Features

- **Data Lakehouse**: Modern architecture combining data lake flexibility with data warehouse performance
- **Asset Bundle Deployment**: Automated CI/CD for Databricks resources
- **Security First**: Azure Active Directory integration and managed identity
- **Cost Optimization**: Serverless compute and auto-scaling capabilities
- **Data Quality**: Built-in validation and monitoring throughout the pipeline

## 📁 Project Structure

```
data_streaming/
├── 📂 terraform/                 # Infrastructure as Code
│   ├── main.tf                   # Azure resources definition
│   └── variables.tf              # Configurable parameters
├── 📂 stock_bundles/             # Databricks Asset Bundle  
│   ├── databricks.yml            # Bundle configuration
│   ├── resources/                # Pipeline definitions
│   │   ├── bronze.ingestion.yml  # Bronze layer jobs
│   │   ├── silver.pipeline.yml   # Silver DLT pipeline
│   │   └── gold.pipeline.yml     # Gold DLT pipeline
│   └── src/                      # Source code
│       ├── dlt_pipelines/        # Delta Live Tables
│       ├── notebook/             # Databricks notebooks
│       └── utilities/            # Helper functions
├── 📂 data/                      # Sample datasets
│   ├── new_data/                 # Latest stock data (10+ symbols)
│   └── pre-test/                 # Historical test data
├── 📂 docs/                      # Documentation
│   ├── Project_walkthrough.md    # Step-by-step guide
│   ├── TERRAFORM_SETUP.md        # Infrastructure setup
│   └── DATABRICKS_BUNDLE.md      # Asset bundle guide
├── requirements.txt              # Python project configuration
├── LICENSE                       # MIT License
└── main.py                       # Entry point script
```

## 🛠️ Prerequisites

### Required Software
- **Python 3.12+** with UV package manager
- **Azure CLI** for authentication
- **Terraform** (v1.0+) for infrastructure deployment
- **Databricks CLI** for asset bundle management

### Azure Requirements
- **Azure Subscription** with appropriate permissions
- **Contributor role** on subscription or resource group level
- **Databricks workspace** deployment permissions

## ⚡ Quick Start

### 1. 🏗️ Deploy Azure Infrastructure 

```powershell
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Review and deploy infrastructure
terraform plan
terraform apply
```

**Resources Created:**
- Azure Resource Group (`RG-StockProjekt`)
- Storage Account with Data Lake Gen2 (`stockstreametl`)
- Databricks Workspace (`databricks-etl-workspace`)
- Access Connector for secure integration

### 2. 🐍 Setup Python Environment

```powershell
# Install UV package manager
pip install uv

# Navigate to project root and setup environment
cd ..
uv sync --dev

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 3. 📦 Deploy Databricks Asset Bundle

```powershell
cd stock_bundles

# Authenticate with Databricks
databricks auth login

# Deploy bundle to development environment
databricks bundle deploy --target dev

# Run the complete data pipeline
databricks bundle run bronze_ingestion --target dev
databricks bundle run pipeline_silver_run --target dev --wait
databricks bundle run pipeline_gold_run --target dev --wait
```

## Stock Data Coverage

### Supported Stock Symbols
The project includes comprehensive data for major stocks across multiple sectors:

**Technology**: AAPL, MSFT, GOOGL, AMZN, ADBE, AMD, AVGO  
**Healthcare**: ABT, AMGN  
**Financial**: BAC, AXP, BKNG  

### Data Timeframes
- **Historical Data**: 2022-01-01 to 2025-06-01 (Training/Analysis)
- **Recent Data**: 2025-06-02 to 2025-09-01 (Testing/Validation)
- **Update Frequency**: Daily OHLCV (Open, High, Low, Close, Volume) data
- **Data Source**: Yahoo Finance API

## 🔧 Configuration

### Azure Resource Configuration

| Resource | Name | Purpose |
|----------|------|---------|
| **Resource Group** | `RG-StockProjekt` | Container for all resources |
| **Storage Account** | `stockstreametl` | Data Lake Gen2 storage |
| **Databricks Workspace** | `databricks-etl-workspace` | Data processing platform |
| **Access Connector** | `databricks-etl-con` | Secure storage integration |

### Storage Container Structure
- **`raw`** - Landing zone for all incoming data
- **`bronze`** - Cleansed, unified data with basic validation
- **`silver`** - Business logic applied, standardized schemas
- **`gold`** - Analytics-ready aggregated data
- **`metastore`** - Unity Catalog metadata storage

## 🔄 Data Pipeline Architecture

### Bronze Layer (Data Ingestion)
- **Purpose**: Raw data landing with minimal processing
- **Sources**: Yahoo Finance API, CSV file uploads
- **Process**: Ticker loading → Parallel incremental ingestion
- **Output**: Delta format with original data structure
- **Features**: Schema inference, data validation, audit logging

### Silver Layer (Data Transformation) 
- **Purpose**: Cleansed and standardized business data
- **Process**: Data quality checks → Schema standardization → Business rules
- **Features**: Auto-optimization, schema evolution, deduplication
- **Output**: Dimensional data model optimized for analytics
- **Configuration**: Continuous=false, auto-compaction enabled

### Gold Layer (Analytics Ready)
- **Purpose**: Aggregated data for reporting and analytics
- **Process**: Calculate metrics → Create aggregations → Optimize queries
- **Compute**: Serverless runtime for cost efficiency
- **Output**: Business-ready datasets and KPIs
- **Features**: Time-based aggregations, performance optimization

## 📊 Data Schema

### Stock Data Schema

```json
{
  "symbol": "string",           // Stock ticker symbol
  "date": "date",              // Trading date
  "timestamp": "timestamp",     // Exact timestamp (for intraday)
  "open": "double",            // Opening price
  "high": "double",            // High price
  "low": "double",             // Low price
  "close": "double",           // Closing price
  "volume": "long",            // Trading volume
  "adj_close": "double",       // Adjusted closing price
  "source": "string",          // "batch" or "stream"
  "processed_timestamp": "timestamp"  // Processing time
}
```

## 🚀 Usage Examples

### Data Pipeline Execution

```powershell
# Navigate to Databricks bundle
cd stock_bundles

# Deploy and run complete pipeline
databricks bundle deploy --target dev

# Execute bronze layer (data ingestion)
databricks bundle run bronze_ingestion --target dev

# Execute silver layer (transformation)
databricks bundle run pipeline_silver_run --target dev --wait

# Execute gold layer (analytics)
databricks bundle run pipeline_gold_run --target dev --wait
```

### Manual Data Upload (Development)

```powershell
# Upload sample data to Databricks workspace
# 1. Go to Databricks UI → Catalog → stock_data_cata → raw → rawvolume
# 2. Upload CSV files from data/pre-test/ directory
# 3. Organize by symbol folders (AAPL/, MSFT/, etc.)
```

## 🔄 Data Processing Features

### Incremental Loading Strategy
1. **Change Data Capture**: Automatic detection of new and updated records
2. **Merge Operations**: Efficient upserts using Delta Lake MERGE operations  
3. **Deduplication**: Hash-based duplicate detection across all layers
4. **Schema Evolution**: Automatic handling of schema changes over time

### Performance Optimizations
- **Z-Ordering**: Optimize data layout for query performance
- **Auto-Compaction**: Automatic small file consolidation
- **Liquid Clustering**: Dynamic data organization for better performance
- **Serverless Compute**: Cost-effective auto-scaling resources

## 🛡️ Security & Best Practices

### Authentication & Authorization
1. **Azure Active Directory**: Integrated authentication for all services
2. **Managed Identity**: Access Connector provides secure storage access
3. **Unity Catalog**: Centralized access control and data governance

### Production Security Recommendations
- **Azure Key Vault**: Store sensitive configuration and secrets
- **Private Endpoints**: Network-level security for Azure services  
- **Data Encryption**: Encryption at rest (default) and in transit
- **Audit Logging**: Enable diagnostic logging for compliance
- **Identity Governance**: Regular access reviews and least privilege

## 📊 Performance & Optimization

### Databricks Configuration
```python
# Recommended Spark settings for stock data processing
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true") 
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")

# Or configure this in ./stock_bundles/databricks.yml

# Delta table optimization for time-series data
OPTIMIZE stock_data_cata.silver.stock_data ZORDER BY (symbol, date);
OPTIMIZE stock_data_cata.gold.stock_aggregates ZORDER BY (date, symbol);
```

### Scaling & Cost Optimization
- **Serverless Compute**: Use for intermittent workloads (Gold layer)
- **Auto-scaling Clusters**: Dynamic scaling based on workload
- **Spot Instances**: Cost reduction for non-critical processing
- **Storage Tiers**: Hot/Cool/Archive tiers based on access patterns
- **Compute Scheduling**: Run jobs during off-peak hours

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

**Issue**: Terraform connectivity issues:
**Solution**: Extend the the retry length, if the problem persist, wait 30s
```powershell
$env:TF_HTTP_RETRY_MAX="10"; $env:TF_HTTP_RETRY_WAIT_MIN="5"; $env:TF_HTTP_RETRY_WAIT_MAX="30"
```
**Issue**: Permission denied accessing storage  
**Solution**: Verify Access Connector has Storage Blob Data Contributor role

**Issue**: Pipeline execution timeouts  
**Solution**: Increase cluster size or enable auto-scaling

**Issue**: Quotas exceed on databricks
**Solution**: Increase cores (not recommended unless you know what you are doing) or go serverless.


## 🚀 Future Enhancements

### Advanced Analytics
1. **Machine Learning Integration**: Stock price prediction models using Azure ML
2. **Real-time Dashboards**: Power BI integration with Direct Lake mode
3. **Advanced Aggregations**: Moving averages, volatility calculations, correlation analysis
4. **Alert System**: Automated notifications for significant price movements

### Data Engineering Improvements  
1. **Stream Processing**: Real-time data ingestion using Event Hubs or Kafka
2. **Data Mesh Architecture**: Decentralized data ownership and governance
3. **Multi-Region Setup**: Global data replication and disaster recovery
4. **Advanced Scheduling**: Complex workflow orchestration with dependencies

### DevOps & Monitoring
1. **CI/CD Pipelines**: Automated testing and deployment using GitHub Actions
2. **Infrastructure Monitoring**: Azure Monitor dashboards and alerting
3. **Data Lineage**: Complete data flow tracking and impact analysis
4. **Cost Management**: Automated resource optimization and budget alerts

## 📚 Documentation & Resources

- [📖 Project Walkthrough](docs/Project_walkthrough.md) - Complete setup guide
- [🏗️ Terraform Setup](docs/TERRAFORM_SETUP.md) - Infrastructure deployment
- [📦 Databricks Bundle Guide](docs/DATABRICKS_BUNDLE.md) - Asset bundle documentation

### External Resources
- [Azure Databricks Documentation](https://docs.microsoft.com/en-us/azure/databricks/)
- [Delta Live Tables Guide](https://docs.databricks.com/workflows/delta-live-tables/)
- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest)

## 📄 License
- This project is licensed under the MIT License
