variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
}

variable "location" {
  description = "Azure region where resources will be deployed"
  type        = string
  default     = "Australia East"
}

variable "acr_name" {
  description = "Globally unique Azure Container Registry name"
  type        = string
}

variable "aks_name" {
  description = "Name of the Azure Kubernetes Service cluster"
  type        = string
}

variable "storage_account_name" {
  description = "Globally unique Azure Storage Account name"
  type        = string
}

variable "aks_node_count" {
  description = "Number of AKS worker nodes"
  type        = number
  default     = 3
}

variable "aks_vm_size" {
  description = "VM size used by the AKS default node pool"
  type        = string
}