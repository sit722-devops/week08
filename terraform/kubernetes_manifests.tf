locals {
  kubernetes_manifest_vars = {
    acr_login_server          = azurerm_container_registry.acr.login_server
    storage_connection_string = azurerm_storage_account.storage_account.primary_connection_string
    image_tag                 = var.image_tag
  }

  kubernetes_manifest_templates = {
    "07-application-secret.yaml" = "07-application-secret.yaml.tpl"
    "08-user-service.yaml"       = "08-user-service.yaml.tpl"
    "09-student-service.yaml"    = "09-student-service.yaml.tpl"
    "10-lecturer-service.yaml"   = "10-lecturer-service.yaml.tpl"
    "11-course-service.yaml"     = "11-course-service.yaml.tpl"
    "12-enrollment-service.yaml" = "12-enrollment-service.yaml.tpl"
    "13-frontend.yaml"           = "13-frontend.yaml.tpl"
  }
}

resource "local_file" "kubernetes_manifests" {
  for_each = local.kubernetes_manifest_templates

  content  = templatefile("${path.module}/templates/${each.value}", local.kubernetes_manifest_vars)
  filename = "${path.module}/../kubernetes/${each.key}"
}
