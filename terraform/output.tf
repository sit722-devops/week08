output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.rg.name
}

output "acr_name" {
  description = "Name of the Azure Container Registry"
  value       = azurerm_container_registry.acr.name
}

output "acr_login_server" {
  description = "Login server of the Azure Container Registry"
  value       = azurerm_container_registry.acr.login_server
}

output "storage_account_name" {
  description = "Name of the Azure Storage Account"
  value       = azurerm_storage_account.storage_account.name
}

output "storage_connection_string" {
  description = "Connection string used by the application to access Blob Storage"
  value       = azurerm_storage_account.storage_account.primary_connection_string
  sensitive   = true
}

output "student_profile_container" {
  description = "Student profile photo Blob container"
  value       = azurerm_storage_container.student_profile_photo.name
}

output "lecturer_profile_container" {
  description = "Lecturer profile photo Blob container"
  value       = azurerm_storage_container.lecturer_profile_photo.name
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "log_analytics_workspace_name" {
  description = "Name of the Log Analytics workspace used by AKS Container Insights"
  value       = azurerm_log_analytics_workspace.law.name
}

output "aks_get_credentials_command" {
  description = "Azure CLI command used to configure kubectl"
  value = join(" ", [
    "az aks get-credentials",
    "--resource-group",
    azurerm_resource_group.rg.name,
    "--name",
    azurerm_kubernetes_cluster.aks.name,
    "--overwrite-existing"
  ])
}

output "acr_login_command" {
  description = "Azure CLI command used to log in to ACR"
  value       = "az acr login --name ${azurerm_container_registry.acr.name}"
}

output "generated_kubernetes_manifests" {
  description = "Kubernetes manifest files generated automatically from Terraform templates"
  value       = [for manifest in local_file.kubernetes_manifests : manifest.filename]
}

output "image_tag" {
  description = "Container image tag written into generated Kubernetes manifests"
  value       = var.image_tag
}