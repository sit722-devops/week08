variable "prefix" {
  description = "Short prefix used to name all resources (must be globally unique for ACR/Storage), e.g. sit722w08<yourstudentid>"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "australiaeast"
}

variable "node_count" {
  description = "Number of AKS worker nodes. Must be 3 for Week 08 (staging + production both run PostgreSQL)."
  type        = number
  default     = 3
}

variable "vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_B2s_v2"
}