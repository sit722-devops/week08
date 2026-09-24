location            = "Australia East"
resource_group_name = "koalatech-week08-rg"

acr_name             = "aswin22528acr08"
storage_account_name = "aswin22528st08"

aks_cluster_name = "aswin722aks22528w08"
aks_dns_prefix   = "koalatech08"

aks_node_count   = 3
aks_node_vm_size = "Standard_D2s_v3"

environment = "development"

tags = {
  Project     = "KoalaTech Course Platform"
  ManagedBy   = "Terraform"
  Practical   = "Week08"
  Environment = "Development"
}