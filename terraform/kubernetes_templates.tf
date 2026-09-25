resource "local_file" "application_secret" {
  content = templatefile("${path.module}/templates/application-secret.yaml.tftpl", {
    storage_connection_string = azurerm_storage_account.storage_account.primary_connection_string
  })

  filename = "${path.module}/../kubernetes/07-application-secret-generated.yaml"
}

locals {
  kubernetes_templates = {
    "08-user-service-generated.yaml"       = "user-service.yaml.tftpl"
    "09-student-service-generated.yaml"    = "student-service.yaml.tftpl"
    "10-lecturer-service-generated.yaml"   = "lecturer-service.yaml.tftpl"
    "11-course-service-generated.yaml"     = "course-service.yaml.tftpl"
    "12-enrollment-service-generated.yaml" = "enrollment-service.yaml.tftpl"
    "13-frontend-generated.yaml"           = "frontend.yaml.tftpl"
  }
}

resource "local_file" "kubernetes_manifests" {
  for_each = local.kubernetes_templates

  content = templatefile("${path.module}/templates/${each.value}", {
    acr_login_server = azurerm_container_registry.acr.login_server
  })

  filename = "${path.module}/../kubernetes/${each.key}"
}