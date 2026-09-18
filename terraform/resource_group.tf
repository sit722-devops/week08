resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    project     = "SIT722"
    task        = "8.1P"
    environment = "week08"
  }
}