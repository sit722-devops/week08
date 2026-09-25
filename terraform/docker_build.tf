resource "local_file" "docker_build_script" {
  content = <<-EOT
    $ACR="${azurerm_container_registry.acr.login_server}"

    az acr login --name ${azurerm_container_registry.acr.name}

    docker build -t $ACR/koalatech-user-service:v1 ../user-service
    docker push $ACR/koalatech-user-service:v1

    docker build -t $ACR/koalatech-student-service:v1 ../student-service
    docker push $ACR/koalatech-student-service:v1

    docker build -t $ACR/koalatech-lecturer-service:v1 ../lecturer-service
    docker push $ACR/koalatech-lecturer-service:v1

    docker build -t $ACR/koalatech-course-service:v1 ../course-service
    docker push $ACR/koalatech-course-service:v1

    docker build -t $ACR/koalatech-enrollment-service:v1 ../enrollment-service
    docker push $ACR/koalatech-enrollment-service:v1

    docker build -t $ACR/koalatech-frontend:v1 ../frontend
    docker push $ACR/koalatech-frontend:v1
  EOT

  filename = "${path.module}/../docker-build-generated.ps1"
}