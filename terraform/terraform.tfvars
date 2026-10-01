location            = "Australia East"
resource_group_name = "koalatech-week06-ex2-rg"

# Unique name for Azure Container Registry (using student ID suffix)
acr_name             = "koalatechomacr847"

# Unique name for Azure Storage Account (using student ID suffix)
storage_account_name = "koalatechomstor847"

# Name for Azure Kubernetes Service cluster
aks_cluster_name = "koalatechomaks847"
aks_dns_prefix   = "koalatech"

aks_node_count   = 2
aks_node_vm_size = "Standard_B2s_v2"

environment = "development"

tags = {
    Project    = "KoalaTech Course Platform"
    ManagedBy  = "Terraform"
    Practical  = "Week06"
    Environment = "Development"
}
