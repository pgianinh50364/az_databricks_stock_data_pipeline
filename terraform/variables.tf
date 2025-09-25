# Variables for Azure authentication and configuration

variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  default     = null
}

variable "client_id" {
  description = "Azure Client ID (Application ID)"
  type        = string
  default     = null
}

variable "client_secret" {
  description = "Azure Client Secret"
  type        = string
  default     = null
  sensitive   = true
}

variable "tenant_id" {
  description = "Azure Tenant ID"
  type        = string
  default     = null
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "RG-StockProjekt"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "Southeast Asia"
}

variable "storage_account_name" {
  description = "Name of the storage account"
  type        = string
  default     = "stockstreametl"
}

variable "databricks_workspace_name" {
  description = "Name of the Databricks workspace"
  type        = string
  default     = "databricks-etl-workspace"
}

variable "eventhub_namespace_name" {
  description = "Name of the Event Hub namespace"
  type        = string
  default     = "stocketl"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    environment = "development"
    project     = "stock-etl"
    created_by  = "terraform"
  }
}