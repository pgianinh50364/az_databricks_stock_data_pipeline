# Configure the Azure Provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
  
  # Optional: Use environment variables for authentication
  # subscription_id = var.subscription_id
  # client_id       = var.client_id
  # client_secret   = var.client_secret
  # tenant_id       = var.tenant_id
  
  # Skip provider registration if you don't have permissions
  skip_provider_registration = true
}

# Create Resource Group
resource "azurerm_resource_group" "stock_project" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Create Storage Account
resource "azurerm_storage_account" "stock_storage" {
  name                     = "stockstreametl"
  resource_group_name      = azurerm_resource_group.stock_project.name
  location                 = azurerm_resource_group.stock_project.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true # Enable hierarchical namespace for Data Lake Gen2

  tags = {
    environment = "development"
    project     = "stock-etl"
  }
}

# Create containers in the storage account
resource "azurerm_storage_container" "containers" {
  for_each              = toset(["raw", "bronze", "silver", "gold", "metastore"])
  name                  = each.value
  storage_account_name  = azurerm_storage_account.stock_storage.name
  container_access_type = "private"
}

# Create Access Connector for Azure Databricks
resource "azurerm_databricks_access_connector" "databricks_connector" {
  name                = "databricks-etl-con"
  resource_group_name = azurerm_resource_group.stock_project.name
  location            = azurerm_resource_group.stock_project.location

  identity {
    type = "SystemAssigned"
  }

  tags = {
    environment = "development"
    project     = "stock-etl"
  }
}

# Create Azure Databricks Workspace
resource "azurerm_databricks_workspace" "databricks" {
  name                = "databricks-etl-workspace"
  resource_group_name = azurerm_resource_group.stock_project.name
  location            = azurerm_resource_group.stock_project.location
  sku                 = "trial"

  tags = {
    environment = "development"
    project     = "stock-etl"
  }
}

# Output important values
output "resource_group_name" {
  value = azurerm_resource_group.stock_project.name
}

output "storage_account_name" {
  value = azurerm_storage_account.stock_storage.name
}

output "databricks_workspace_url" {
  value = azurerm_databricks_workspace.databricks.workspace_url
}