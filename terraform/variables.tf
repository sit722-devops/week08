variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name for the 10.2D environment"
  type        = string
  default     = "koalatech-10-2d-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "australiaeast"
}

variable "aks_cluster_name" {
  description = "AKS cluster name"
  type        = string
  default     = "koalatech-10-2d-aks"
}