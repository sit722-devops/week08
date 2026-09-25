variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "australiaeast"
}

variable "resource_group_name" {
  description = "Name of the main resource group for the application infrastructure"
  type        = string
  default     = "sit722w8-rg"
}

variable "acr_name" {
  description = "Name of the Azure Container Registry (must be globally unique)"
  type        = string
  default     = "sit722w8acrlvk5h"
}

variable "aks_cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
  default     = "sit722w8-aks"
}

variable "aks_node_count" {
  description = "Number of nodes in the default AKS node pool"
  type        = number
  default     = 1
}

variable "aks_node_vm_size" {
  description = "VM size for the AKS nodes"
  type        = string
  default     = "Standard_B2s"
}

variable "app_storage_account_prefix" {
  description = "Prefix used for the generated app storage account name (a random suffix is appended for uniqueness)"
  type        = string
  default     = "sit722w8st"
}
