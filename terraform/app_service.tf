resource "azurerm_service_plan" "app_service_plan" {
  name                = var.app_service_plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = var.app_service_plan_sku

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

resource "azurerm_linux_web_app" "web_app" {
  name                = var.app_service_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.app_service_plan.id

  https_only = true

  app_settings = {
    WEBSITES_PORT                     = "80"
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"
  }

  site_config {
    always_on = true

    application_stack {
      docker_image_name        = "${azurerm_container_registry.acr.login_server}/koalatech-frontend:latest"
      docker_registry_url      = "https://${azurerm_container_registry.acr.login_server}"
      docker_registry_username = azurerm_container_registry.acr.admin_username
      docker_registry_password = azurerm_container_registry.acr.admin_password
    }
  }

  identity {
    type = "SystemAssigned"
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

resource "azurerm_linux_web_app_slot" "staging" {
  name           = var.app_service_staging_slot_name
  app_service_id = azurerm_linux_web_app.web_app.id

  https_only = true

  app_settings = {
    WEBSITES_PORT                     = "80"
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"
  }

  site_config {
    always_on = true

    application_stack {
      docker_image_name        = "${azurerm_container_registry.acr.login_server}/koalatech-frontend:latest"
      docker_registry_url      = "https://${azurerm_container_registry.acr.login_server}"
      docker_registry_username = azurerm_container_registry.acr.admin_username
      docker_registry_password = azurerm_container_registry.acr.admin_password
    }
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}
