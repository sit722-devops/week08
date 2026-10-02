location = "Australia East"

resource_group_name = "Week-09-224734529"

acr_name = "week09224734529"

storage_account_name = "week09224734529storage"

aks_cluster_name = "week09-aks-224734529"
aks_dns_prefix   = "week09koalatech224734529"

aks_node_count   = 3
aks_node_vm_size = "Standard_B2s"

environment = "development"

tags = {
  Project     = "KoalaTech Course Platform"
  ManagedBy   = "Terraform"
  Practical   = "Week09"
  Environment = "Development"
}