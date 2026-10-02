locals {
  generated_kubernetes_dir = "${path.module}/../kubernetes/generated"
}

resource "local_file" "application_secret" {
  content = templatefile(
    "${path.module}/templates/07-application-secret.yaml.tftpl",
    {
      storage_connection_string = azurerm_storage_account.storage_account.primary_connection_string
    }
  )

  filename = "${local.generated_kubernetes_dir}/07-application-secret.yaml"
}

resource "local_file" "user_service" {
  content = templatefile(
    "${path.module}/templates/08-user-service.yaml.tftpl",
    {
      acr_login_server = azurerm_container_registry.acr.login_server
    }
  )

  filename = "${local.generated_kubernetes_dir}/08-user-service.yaml"
}

resource "local_file" "student_service" {
  content = templatefile(
    "${path.module}/templates/09-student-service.yaml.tftpl",
    {
      acr_login_server = azurerm_container_registry.acr.login_server
    }
  )

  filename = "${local.generated_kubernetes_dir}/09-student-service.yaml"
}

resource "local_file" "lecturer_service" {
  content = templatefile(
    "${path.module}/templates/10-lecturer-service.yaml.tftpl",
    {
      acr_login_server = azurerm_container_registry.acr.login_server
    }
  )

  filename = "${local.generated_kubernetes_dir}/10-lecturer-service.yaml"
}

resource "local_file" "course_service" {
  content = templatefile(
    "${path.module}/templates/11-course-service.yaml.tftpl",
    {
      acr_login_server = azurerm_container_registry.acr.login_server
    }
  )

  filename = "${local.generated_kubernetes_dir}/11-course-service.yaml"
}

resource "local_file" "enrollment_service" {
  content = templatefile(
    "${path.module}/templates/12-enrollment-service.yaml.tftpl",
    {
      acr_login_server = azurerm_container_registry.acr.login_server
    }
  )

  filename = "${local.generated_kubernetes_dir}/12-enrollment-service.yaml"
}

resource "local_file" "frontend" {
  content = templatefile(
    "${path.module}/templates/13-frontend-service.yaml.tftpl",
    {
      acr_login_server = azurerm_container_registry.acr.login_server
    }
  )

  filename = "${local.generated_kubernetes_dir}/13-frontend.yaml"
}