resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = false
  tags                = var.tags
}

resource "azurerm_storage_account" "photos" {
  name                            = var.storage_account_name
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  tags                            = var.tags
}

# Names match AZURE_STORAGE_CONTAINER_NAME in kubernetes/*/08 and 09 manifests
resource "azurerm_storage_container" "student_photos" {
  name                  = "student-profile-photo"
  storage_account_id    = azurerm_storage_account.photos.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "lecturer_photos" {
  name                  = "lecturer-profile-photo"
  storage_account_id    = azurerm_storage_account.photos.id
  container_access_type = "private"
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_cluster_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "koalatech-w08"

  default_node_pool {
    name       = "system"
    node_count = var.node_count
    vm_size    = var.node_vm_size

    upgrade_settings {
      drain_timeout_in_minutes      = 0
      max_surge                     = "10%"
      node_soak_duration_in_minutes = 0
    }
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Lets AKS pull images from ACR. Created once from my own account
# (the pipeline principal only has Contributor and cannot write role assignments).
resource "azurerm_role_assignment" "acr_pull" {
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
}
