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

output "app_service_plan_name" {
  description = "Name of the App Service plan"
  value       = azurerm_service_plan.app_service_plan.name
}

output "app_service_name" {
  description = "Name of the production App Service"
  value       = azurerm_linux_web_app.web_app.name
}

output "app_service_default_hostname" {
  description = "Default hostname of the production App Service"
  value       = "https://${azurerm_linux_web_app.web_app.default_hostname}"
}

output "staging_slot_name" {
  description = "Name of the App Service staging slot"
  value       = azurerm_linux_web_app_slot.staging.name
}

output "staging_slot_hostname" {
  description = "Default hostname of the App Service staging slot"
  value       = "https://${azurerm_linux_web_app_slot.staging.default_hostname}"
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

output "app_service_swap_command" {
  description = "Command used to swap the staging slot into production"
  value       = "az webapp deployment slot swap --name ${azurerm_linux_web_app.web_app.name} --resource-group ${azurerm_resource_group.rg.name} --slot ${azurerm_linux_web_app_slot.staging.name} --target-slot production"
}

output "app_service_staging_configure_command" {
  description = "Command used to configure the staging slot container image"
  value       = "az webapp config container set --name ${azurerm_linux_web_app.web_app.name} --resource-group ${azurerm_resource_group.rg.name} --slot ${azurerm_linux_web_app_slot.staging.name} --docker-custom-image-name ${azurerm_container_registry.acr.login_server}/koalatech-frontend:latest --docker-registry-server-url https://${azurerm_container_registry.acr.login_server} --docker-registry-server-user ${azurerm_container_registry.acr.admin_username} --docker-registry-server-password ${azurerm_container_registry.acr.admin_password}"
  sensitive   = true
}
