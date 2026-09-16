location            = "Australia East"
resource_group_name = "koalatech-week08-rg"

# Globally unique, alphanumeric only, lowercase
acr_name = "koalatechacrs225273076"

# Globally unique, 3-24 lowercase letters and numbers
storage_account_name = "koalatechsts225273076"

aks_cluster_name = "koalatech-aks-s225273076"
aks_dns_prefix   = "koalatech"

# Week 08 requires 3 nodes: staging and production both run
# persistent PostgreSQL workloads on the same cluster.
aks_node_count   = 3
aks_node_vm_size = "Standard_D2s_v3"

# Leave kubernetes_version unset so Azure picks the regional default.
# To pin a version, check what is available first:
#   az aks get-versions --location australiaeast --output table
# kubernetes_version = "1.31.2"

environment = "development"

tags = {
    Project     = "KoalaTech Course Platform"
    ManagedBy   = "Terraform"
    Practical   = "Week08"
    Environment = "Development"
}
