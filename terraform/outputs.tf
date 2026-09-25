output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "app_storage_account_name" {
  value = azurerm_storage_account.app.name
}

output "app_storage_account_primary_connection_string" {
  value     = azurerm_storage_account.app.primary_connection_string
  sensitive = true
}

output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.monitoring.id
}
