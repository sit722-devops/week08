location            = "Australia East"
resource_group_name = "koalatech-week08-rg"

acr_name             = "koalatech8acr226035073"
storage_account_name = "koalatech8st226035073"

app_service_plan_name = "koalatech-week08-plan"
app_service_plan_sku  = "S1"
app_service_name      = "koalatech-week08-webapp-226035073"

aks_cluster_name = "koalatech-week08-aks"
aks_dns_prefix   = "koalatech-week08"

aks_node_count   = 3
aks_node_vm_size = "Standard_D2s_v3"

environment = "week08"

tags = {
  Project     = "KoalaTech Course Platform"
  ManagedBy   = "Terraform"
  Practical   = "Week08"
  Environment = "Week08"
}