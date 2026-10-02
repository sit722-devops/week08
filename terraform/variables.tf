variable "location" {
  description = "Azure region"
  type        = string
  default     = "australiaeast"
}

variable "resource_group_name" {
  type = string
}

variable "acr_name" {
  type = string
}

variable "storage_account_name" {
  type = string
}

variable "aks_cluster_name" {
  type = string
}

variable "node_count" {
  description = "Staging + production + monitoring needs 3 nodes"
  type        = number
  default     = 3
}

variable "node_vm_size" {
  type    = string
  default = "Standard_B2s_v2"
}

variable "tags" {
  type = map(string)
  default = {
    project    = "koalatech"
    unit       = "SIT722"
    managed_by = "terraform"
    task       = "10.2D"
  }
}
