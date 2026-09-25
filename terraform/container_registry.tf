resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  sku           = "Basic"
  admin_enabled = false

  tags = {
    project     = "SIT722"
    task        = "10.2D"
    environment = "week10"
    purpose     = "infrastructure-security-monitoring"
  }
}
