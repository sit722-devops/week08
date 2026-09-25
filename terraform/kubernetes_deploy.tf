resource "local_file" "kubernetes_deploy_script" {
  content = <<-EOT
    az aks get-credentials --resource-group ${azurerm_resource_group.rg.name} --name ${azurerm_kubernetes_cluster.aks.name} --overwrite-existing

    kubectl apply -f ../kubernetes/07-application-secret-generated.yaml
    kubectl apply -f ../kubernetes/08-user-service-generated.yaml
    kubectl apply -f ../kubernetes/09-student-service-generated.yaml
    kubectl apply -f ../kubernetes/10-lecturer-service-generated.yaml
    kubectl apply -f ../kubernetes/11-course-service-generated.yaml
    kubectl apply -f ../kubernetes/12-enrollment-service-generated.yaml
    kubectl apply -f ../kubernetes/13-frontend-generated.yaml

    kubectl get pods
    kubectl get services
  EOT

  filename = "${path.module}/../kubernetes-deploy-generated.ps1"
}