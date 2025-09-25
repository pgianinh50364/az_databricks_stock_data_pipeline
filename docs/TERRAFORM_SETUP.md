# Terraform Infrastructure Setup Guide 🏗️

Complete guide for deploying and managing the Azure infrastructure for the Stock Data Streaming project using Infrastructure as Code (IaC) principles.

## 📋 Prerequisites

Before starting, ensure you have:

- **Azure Subscription** with appropriate permissions (Contributor or Owner role)

## 🛠️ Step 1: Install Required Tools

### 1.1 Install Terraform

**Using Windows Package Manager:**
```powershell
# Install Terraform via winget
winget install HashiCorp.Terraform
```
*Or visit: https://developer.hashicorp.com/terraform/install*

### 1.2 Install Azure CLI

```powershell
# Install Azure CLI
winget install --exact --id Microsoft.AzureCLI
```

### 1.3 Verify Installations

**Open a new PowerShell window** and verify:

```powershell
# Check Terraform
terraform version

# Check Azure CLI
az version
```

Expected output:
```
Terraform v1.9.5
{
  "azure-cli": "2.77.0",
  ...
}
```

## 🔐 Step 2: Azure Authentication

### 2.1 Login to Azure

```powershell
# Navigate to terraform directory
cd C:\Users\<your_user_name>\Desktop\data_streaming\terraform

# Login to Azure (this will open a browser)
az login --use-device-code
```

**Follow these steps:**
1. A browser window will open or you'll get a device code
2. If device code: Go to https://microsoft.com/devicelogin and enter the code
3. Sign in with your Azure account
4. Complete MFA if required
5. Select your subscription when prompted

### 2.2 Verify Authentication

```powershell
# Check your current subscription
az account show

# List available subscriptions
az account list --output table
```

### 2.3 Set Default Subscription (if needed)

```powershell
# If you have multiple subscriptions, set the correct one
az account set --subscription "Azure subscription 1"
```

## ⚙️ Step 3: Configure Terraform

### 3.1 Initialize Terraform

```powershell
# Navigate to terraform directory
cd C:\Users\gianinh50365\Desktop\data_streaming\terraform

# Initialize Terraform (downloads Azure provider)
terraform init
```

### 3.2 Validate Configuration

```powershell
# Validate Terraform configuration
terraform validate
```

## 🔍 Step 4: Plan and Review

### 4.1 Run Terraform Plan

```powershell
# See what resources will be created
terraform plan
```

**Review the output carefully. You should see:**
- ✅ Resource Group: `RG-StockProjekt`
- ✅ Storage Account: `stockstreametl` (with Data Lake Gen2)
- ✅ 5 Storage Containers: raw, bronze, silver, gold, metastore
- ✅ Databricks Workspace: `databricks-stock-etl`

### 4.2 Save the Plan (Optional)

```powershell
# Save the plan for consistent deployment
terraform plan -out=tfplan
```

## 🚀 Step 5: Deploy Infrastructure

### Deploy Everything at Once

```powershell
# Deploy all resources
terraform apply
# Type 'yes' when prompted to confirm
```

## 📊 Step 6: Verify Deployment

### 6.1 Check Terraform State

```powershell
# List created resources
terraform state list

# Show resource details
terraform show
```

### 6.2 Verify in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to Resource Groups → `RG-StockProjekt`
3. Verify all resources are created:
   - Storage account `stockstreametl`
   - Databricks workspace `databricks-etl-workspace`
   - Access connector `databricks-etl-con`

### 6.3 Get Connection Information

```powershell
# Display sensitive outputs
terraform output resource_group_name
terraform output storage_account_name
terraform output databricks_workspace_url
```

## 🔄 Step 7: Making Changes

### To Modify Resources:
1. Edit the `.tf` files
2. Run `terraform plan` to preview changes
3. Run `terraform apply` to implement changes

### To Destroy Resources:
```powershell
# Destroy all resources (BE CAREFUL!)
terraform destroy

# Destroy specific resources
terraform destroy -target="your-resource"
```

---

**✅ Deployment Complete!** Your Azure infrastructure for the stock data streaming project is now ready!