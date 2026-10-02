# Week 08 – Continuous Delivery with GitHub Actions and Kubernetes

In Week 07, we implemented a Continuous Integration (CI) pipeline using GitHub Actions. The pipeline automatically tested the backend services, built Docker images, and pushed the successfully built images to Azure Container Registry (ACR).

In Week 08, we extend this workflow to implement **Continuous Delivery (CD)**.

The application will first be automatically deployed to a **staging environment**. After deployment, automated tests will verify that the staging application is working correctly. A tested version can then be manually promoted to the **production environment**.

The same Docker images that are tested in staging are deployed to production. The application is **not rebuilt** during production deployment.

---

## 1. Continuous Delivery Workflow

The Week 08 pipeline consists of four GitHub Actions workflows:

![](./workflow.png)

The first three workflows run automatically.

Production deployment is intentionally manual.

---

# 2. Prepare the Infrastructure

Create the Terraform infrastructure files using the same approach demonstrated in **Week 06**.

The infrastructure should provide the Azure resources required by the application, including the Kubernetes infrastructure, Azure Container Registry, and Azure Storage configuration used by the application.

### Important AKS Change

When creating the Kubernetes infrastructure, update the AKS node count to:

```hcl
node_count = 3
```

Three nodes are required for this practical because both the staging and production environments run persistent PostgreSQL database workloads.

After running Terraform, verify that the AKS cluster contains three nodes:

```bash
kubectl get nodes
```

---

# 4. Fork the Repository

Fork the provided Week 08 repository into your own GitHub account.

Clone your fork:

```bash
git clone <YOUR-FORK-URL>
```

Move into the project:

```bash
cd week08
```

Ensure that your remote points to your fork:

```bash
git remote -v
```

---

# 5. Create Azure Service Principal

GitHub Actions requires permission to interact with Azure.

Create a Service Principal following the same process introduced previously.

The Service Principal must have sufficient permissions to:

* authenticate with Azure;
* push Docker images to Azure Container Registry;
* access the AKS cluster;
* deploy Kubernetes workloads.

Store the Service Principal credentials as a GitHub Repository Secret named:

```text
AZURE_CREDENTIALS
```

The value must use the following structure:

```json
{
  "clientId": "YOUR_CLIENT_ID",
  "clientSecret": "YOUR_CLIENT_SECRET",
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "tenantId": "YOUR_TENANT_ID"
}
```

Do not commit these credentials to the repository.

---

# 6. Configure GitHub Repository Variables

Go to:

```text
GitHub Repository
→ Settings
→ Secrets and variables
→ Actions
→ Variables
```

Create the following **Repository Variables**.

### ACR_NAME

The name of your Azure Container Registry.

---

### ACR_LOGIN_SERVER

The complete ACR login server.

---

### AKS_RESOURCE_GROUP

The Resource Group containing your AKS cluster.

---

### AKS_CLUSTER_NAME

The name of your AKS cluster.

---

# 7. Repository Secret

Under:

```text
Settings
→ Secrets and variables
→ Actions
→ Secrets
```

create:

```text
AZURE_CREDENTIALS
```

This contains the Service Principal authentication JSON.

---

# 8. Create the Staging GitHub Environment

Go to:

```text
GitHub Repository
→ Settings
→ Environments
→ New environment
```

Create:

```text
staging
```

Add the following **Environment Secrets**:

```text
POSTGRES_USER = postgres
POSTGRES_PASSWORD = postgres
JWT_SECRET_KEY = koalatech-local-development-secret
DEFAULT_ADMIN_USERNAME = admin
DEFAULT_ADMIN_EMAIL = admin@koalatech.edu.au
DEFAULT_ADMIN_PASSWORD = AdminPassword123!
AZURE_STORAGE_CONNECTION_STRING = <YOUR_STORAGE_ACCOUNT_CONNECTION_STRING>
```
---

# 9. Create the Production GitHub Environment

Create another environment:

```text
production
```

Add the same Environment Secret names:

```text
POSTGRES_USER = postgres
POSTGRES_PASSWORD = postgres
JWT_SECRET_KEY = koalatech-local-development-secret
DEFAULT_ADMIN_USERNAME = admin
DEFAULT_ADMIN_EMAIL = admin@koalatech.edu.au
DEFAULT_ADMIN_PASSWORD = AdminPassword123!
AZURE_STORAGE_CONNECTION_STRING = <YOUR_STORAGE_ACCOUNT_CONNECTION_STRING>
```

Staging and production therefore have independent environment configuration.

---

# 10. GitHub Configuration Summary

The final GitHub configuration should be:

| Type                          | Name                              |
| ----------------------------- | --------------------------------- |
| Repository Secret             | `AZURE_CREDENTIALS`               |
| Repository Variable           | `ACR_NAME`                        |
| Repository Variable           | `ACR_LOGIN_SERVER`                |
| Repository Variable           | `AKS_RESOURCE_GROUP`              |
| Repository Variable           | `AKS_CLUSTER_NAME`                |
| Staging Environment Secret    | `POSTGRES_USER`                   |
| Staging Environment Secret    | `POSTGRES_PASSWORD`               |
| Staging Environment Secret    | `JWT_SECRET_KEY`                  |
| Staging Environment Secret    | `DEFAULT_ADMIN_USERNAME`          |
| Staging Environment Secret    | `DEFAULT_ADMIN_EMAIL`             |
| Staging Environment Secret    | `DEFAULT_ADMIN_PASSWORD`          |
| Staging Environment Secret    | `AZURE_STORAGE_CONNECTION_STRING` |
| Production Environment Secret | `POSTGRES_USER`                   |
| Production Environment Secret | `POSTGRES_PASSWORD`               |
| Production Environment Secret | `JWT_SECRET_KEY`                  |
| Production Environment Secret | `DEFAULT_ADMIN_USERNAME`          |
| Production Environment Secret | `DEFAULT_ADMIN_EMAIL`             |
| Production Environment Secret | `DEFAULT_ADMIN_PASSWORD`          |
| Production Environment Secret | `AZURE_STORAGE_CONNECTION_STRING` |

---

# 11. GitHub Actions Workflows

The repository contains four workflow files:

```text
.github/
└── workflows/
    ├── 01-ci.yml
    ├── 02-deploy-staging.yml
    ├── 03-staging-test.yml
    └── 04-deploy-production.yml
```

---

# 12. Run and Verify the Staging Application

Verify that the following workflows complete successfully:

01 - CI
02 - Deploy to Staging
03 - Staging Test

Once the deployment is complete, verify the Kubernetes resources in the staging namespace and access the staging application using the frontend external IP.

Confirm that the application is working correctly before proceeding to production.

13. Deploy to Production

Production deployment is performed manually.

Go to:

GitHub Repository
→ Actions
→ 04 - Deploy to Production
→ Run workflow

Provide the image SHA that successfully passed the staging deployment and testing process.

### Find the Image SHA

Before running the production workflow, obtain the Git commit SHA of the version that was successfully deployed and tested in staging:

```bash
git rev-parse HEAD
```

Copy the returned SHA and provide it as the `image_tag` when manually running the **04 - Deploy to Production** workflow.

> Make sure the SHA belongs to the version that successfully passed the staging pipeline.


Run the production workflow and verify that it completes successfully.

Important: Production must use the same image version that was tested in staging. Do not rebuild the Docker images for production.

14. Verify the Production Application

After the production deployment completes:

- Verify the Kubernetes resources in the production namespace.
- Find the external IP of the production frontend service.
- Access the production application.
- Confirm that the application is working correctly.
- Verify that production is running the same image SHA that was tested in staging.# CI trigger 09/20/2026 16:26:12
# CI trigger 09/20/2026 16:27:34



---

# Cheat Sheet: Docker + Terraform + Azure + AKS + GitHub Actions

Quick reference for the SIT722 6.2P / 9.2P viva. Replace `<...>` placeholders with your own values.

**Pipeline in one sentence:** Git/GitHub holds the code → GitHub Actions tests it → Docker builds images → images are pushed to ACR (tagged with the commit SHA) → AKS pulls and runs them → Terraform creates the Azure infrastructure.

| Tool | Role | Remember |
| --- | --- | --- |
| Git / GitHub | Version control / hosting + Actions | Git = tool, GitHub = service |
| Docker | Packages the app into images | image = template, container = running instance |
| Docker Compose | Runs multi-container apps locally | one YAML, one command |
| ACR | Private image registry | stores images, does NOT run them |
| AKS / Kubernetes | Runs and manages containers | Deployment = replicas, Service = stable access |
| Terraform | Infrastructure as Code | declarative: describe the end state |
| GitHub Actions | CI/CD automation | trigger → workflow → jobs → steps |

---

## 1. Azure CLI basics

```bash
az login                                      # interactive login
az account show                               # active subscription
az account list -o table
az account set --subscription "<SUBSCRIPTION_ID>"

az group list -o table                        # resource groups
az acr list -o table                          # container registries
az aks list -o table                          # AKS clusters
az storage account list -o table
```

Create the base resources manually (only needed if not using Terraform):

```bash
az group create --name <RG_NAME> --location australiaeast
az acr create --resource-group <RG_NAME> --name <ACR_NAME> --sku Basic
```

Clean up (saves CloudLabs credits, deletes everything in the group):

```bash
az group delete --name <RG_NAME> --yes --no-wait
```

---

## 2. Docker

### Dockerfile (from `student-service/Dockerfile`)

```dockerfile
FROM python:3.12-slim                 # base image
WORKDIR /app                          # working directory
COPY requirements.txt .               # copy deps first (layer caching)
RUN pip install --no-cache-dir -r requirements.txt   # build-time command
COPY . .                              # copy the app code
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser                          # do not run as root
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]   # start command
```

### Build / run / inspect

```bash
docker build -t user-service:v1 ./user-service     # build image (NOT a container yet)
docker images                                      # prove the image exists
docker run -d --name user-service -p 8000:8000 user-service:v1
docker ps                                          # running containers
docker ps -a                                       # including stopped
docker logs user-service
docker exec -it user-service sh                    # shell inside container
docker stop user-service
docker rm user-service
docker rmi user-service:v1
```

### Docker problem seen in the unit: container-name conflict

```bash
docker ps -a                        # find the old container using that name
docker rm -f <container_name>       # remove it
docker compose up -d                # start again
```

---

## 3. Docker Compose

```bash
docker compose config               # validate + show the resolved file (safe to demo)
docker compose up -d                # create and start in background
docker compose up -d --build        # rebuild images first
docker compose ps                   # status
docker compose logs -f <service>    # follow logs
docker compose down                 # stop + remove containers and networks
docker compose down -v              # also remove volumes (wipes DB data)
```

Key parts of `docker-compose.yml` (services / ports / env / volumes):

```yaml
services:
  user-service:
    build:
      context: ./user-service
      dockerfile: Dockerfile
    image: koalatech-user-service:v1
    ports:
      - "8000:8000"            # host:container
    env_file:
      - ./user-service/.env    # environment variables
    depends_on:
      user-db:
        condition: service_healthy
    networks:
      - koalatech-network

  user-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: users
    volumes:
      - user-db-data:/var/lib/postgresql/data    # persistent storage
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d users"]
```

Frontend: http://localhost:3000

---

## 4. Push an image to ACR

Order: **build → tag → login → push → verify**.

```bash
# 1. Build
docker build -t koalatech-user-service:v1 ./user-service

# 2. Tag with the ACR login server (<ACR_NAME>.azurecr.io)
docker tag koalatech-user-service:v1 <ACR_NAME>.azurecr.io/koalatech-user-service:v1

# 3. Authenticate
az acr login --name <ACR_NAME>

# 4. Push
docker push <ACR_NAME>.azurecr.io/koalatech-user-service:v1

# 5. Verify
az acr repository list --name <ACR_NAME> -o table
az acr repository show-tags --name <ACR_NAME> --repository koalatech-user-service -o table
```

Tag with the Git commit SHA (traceable, used by the pipeline):

```bash
SHA=$(git rev-parse HEAD)
docker tag koalatech-user-service:v1 <ACR_NAME>.azurecr.io/koalatech-user-service:$SHA
docker push <ACR_NAME>.azurecr.io/koalatech-user-service:$SHA
```

Get the login server / admin credentials if needed:

```bash
az acr show --name <ACR_NAME> --query loginServer -o tsv
az acr credential show --name <ACR_NAME>
```

---

## 5. Terraform

### Commands (in order)

```bash
terraform init             # download providers (azurerm), first command in a project
terraform fmt              # format files (fmt -check = only report)
terraform validate         # syntax/consistency check, creates nothing (safe viva demo)
terraform plan             # preview create/change/destroy
terraform apply            # make the changes (type yes, or -auto-approve)
terraform output           # show output values
terraform state list       # resources tracked in state
terraform destroy          # tear everything down (cleanup)
```

Safe viva demo: `terraform fmt -check` then `terraform validate`.
Running `apply` twice → "No changes" because Terraform compares desired config with state.

### Suggested file layout

```text
terraform/
├── providers.tf
├── variables.tf
├── main.tf
└── outputs.tf
```

### providers.tf

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}
```

### variables.tf

```hcl
variable "subscription_id" {
  type = string
}

variable "location" {
  type    = string
  default = "australiaeast"
}

variable "resource_group_name" {
  type    = string
  default = "rg-koalatech"
}

variable "acr_name" {
  type        = string
  description = "Globally unique, lowercase letters and digits only"
}

variable "aks_name" {
  type    = string
  default = "aks-koalatech"
}

variable "storage_account_name" {
  type        = string
  description = "Globally unique, 3-24 lowercase letters and digits"
}
```

### main.tf

```hcl
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = var.aks_name

  default_node_pool {
    name       = "default"
    node_count = 3            # Week 08: 3 nodes for the staging + production PostgreSQL workloads
    vm_size    = "Standard_DS2_v2"
  }

  identity {
    type = "SystemAssigned"
  }
}

# Allow AKS to pull images from ACR (prevents ImagePullBackOff)
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
}

resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "photos" {
  name                  = "photos"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}
```

### outputs.tf

```hcl
output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "storage_connection_string" {
  value     = azurerm_storage_account.storage.primary_connection_string
  sensitive = true
}
```

Read the sensitive value (goes into the `AZURE_STORAGE_CONNECTION_STRING` environment secret):

```bash
terraform output -raw storage_connection_string
```

Pass values on the command line instead of a hard-coded default:

```bash
terraform apply -var="subscription_id=<SUB_ID>" -var="acr_name=<ACRNAME>" -var="storage_account_name=<STORAGENAME>"
```

> Version numbers and VM size are examples, so check what your subscription/region allows. `AuthorizationFailed` = wrong subscription or missing permission, not an app bug. Check `az account show` first.

---

## 6. Connect kubectl to AKS

```bash
az aks get-credentials --resource-group <RG_NAME> --name <AKS_NAME> --overwrite-existing
kubectl get nodes            # Week 08: must show 3 nodes
kubectl config current-context
```

Attach ACR to AKS if you did not create the role assignment in Terraform:

```bash
az aks update --resource-group <RG_NAME> --name <AKS_NAME> --attach-acr <ACR_NAME>
```

---

## 7. Azure Service Principal (for GitHub Actions)

```bash
SUB_ID=$(az account show --query id -o tsv)

az ad sp create-for-rbac \
  --name "sp-koalatech-github" \
  --role Contributor \
  --scopes /subscriptions/$SUB_ID/resourceGroups/<RG_NAME> \
  --sdk-auth
```

The JSON output goes into the repository secret `AZURE_CREDENTIALS`:

```json
{
  "clientId": "YOUR_CLIENT_ID",
  "clientSecret": "YOUR_CLIENT_SECRET",
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "tenantId": "YOUR_TENANT_ID"
}
```

If the SP also needs to push to ACR and deploy to AKS, add roles:

```bash
az role assignment create --assignee <CLIENT_ID> --role AcrPush --scope $(az acr show -n <ACR_NAME> --query id -o tsv)
az role assignment create --assignee <CLIENT_ID> --role "Azure Kubernetes Service Cluster User Role" --scope $(az aks show -g <RG_NAME> -n <AKS_NAME> --query id -o tsv)
```

Never commit this JSON. If the CLI rejects `--sdk-auth`, build the JSON by hand from `appId`, `password`, `tenant` and your subscription id.

---

## 8. GitHub configuration

**Repository → Settings → Secrets and variables → Actions**

| Type | Name | Value |
| --- | --- | --- |
| Secret | `AZURE_CREDENTIALS` | Service Principal JSON |
| Variable | `ACR_NAME` | ACR name |
| Variable | `ACR_LOGIN_SERVER` | `<ACR_NAME>.azurecr.io` |
| Variable | `AKS_RESOURCE_GROUP` | Resource group of AKS |
| Variable | `AKS_CLUSTER_NAME` | AKS cluster name |

**Settings → Environments → `staging` and `production`** (same secret names in both):

`POSTGRES_USER`, `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, `DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_EMAIL`, `DEFAULT_ADMIN_PASSWORD`, `AZURE_STORAGE_CONNECTION_STRING`

Secret = sensitive (masked in logs). Variable = normal config.

Optional, using the GitHub CLI:

```bash
gh secret set AZURE_CREDENTIALS < sp.json
gh variable set ACR_NAME --body "<ACR_NAME>"
gh variable set ACR_LOGIN_SERVER --body "<ACR_NAME>.azurecr.io"
gh variable set AKS_RESOURCE_GROUP --body "<RG_NAME>"
gh variable set AKS_CLUSTER_NAME --body "<AKS_NAME>"
gh secret set POSTGRES_PASSWORD --env staging --body "postgres"
```

---

## 9. GitHub Actions concepts and snippets

| Term | Meaning |
| --- | --- |
| Workflow | The whole YAML automation |
| Trigger (`on:`) | Event that starts it: `push`, `workflow_dispatch`, `workflow_run` |
| Job | Group of steps on one runner |
| Step | One action or command |
| Runner | Machine running the job (`ubuntu-latest`) |
| Matrix | Same job repeated for several values (one per microservice) |
| `needs` | Job waits for another job to succeed |
| `environment` | Links a job to a GitHub Environment (secrets, approvals) |

### The four workflows in this repo

| File | Trigger | What it does |
| --- | --- | --- |
| `01-ci.yml` | push to `main` / manual | Test each service (matrix) → build and push images to ACR tagged with the commit SHA |
| `02-deploy-staging.yml` | after 01 succeeds (`workflow_run`) | Apply manifests to `staging`, `kubectl set image` with the SHA, wait for rollouts |
| `03-staging-test.yml` | after staging deploy | Smoke-test the staging app |
| `04-deploy-production.yml` | **manual** (`workflow_dispatch`, input `image_tag`) | Deploy the already-tested SHA to `production`, no rebuild |

### Trigger + matrix + needs

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  backend-test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        service: [user-service, student-service, lecturer-service, course-service, enrollment-service]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - working-directory: ${{ matrix.service }}
        run: |
          pip install -r requirements.txt
          pytest -v

  build-and-push:
    needs: [backend-test]          # skipped if tests fail
    runs-on: ubuntu-latest
    steps: [...]
```

### Login to Azure, then build and push tagged with the SHA

```yaml
- uses: actions/checkout@v4

- name: Login to Azure
  uses: azure/login@v3
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}

- name: Login to ACR
  run: az acr login --name ${{ vars.ACR_NAME }}

- name: Build and push
  run: |
    IMAGE=${{ vars.ACR_LOGIN_SERVER }}/koalatech-user-service:${{ github.sha }}
    docker build -t $IMAGE ./user-service
    docker push $IMAGE
```

### Staging deploy pattern (from `02-deploy-staging.yml`)

```yaml
environment:
  name: staging
steps:
  - uses: actions/checkout@v4
    with:
      ref: ${{ github.event.workflow_run.head_sha }}      # the tested commit
  - uses: azure/login@v3
    with:
      creds: ${{ secrets.AZURE_CREDENTIALS }}
  - run: az aks get-credentials --resource-group ${{ vars.AKS_RESOURCE_GROUP }} --name ${{ vars.AKS_CLUSTER_NAME }} --overwrite-existing
  - run: kubectl create namespace staging --dry-run=client -o yaml | kubectl apply -f -
  - run: |
      kubectl create secret generic application-secret \
        --namespace staging \
        --from-literal=JWT_SECRET_KEY="${{ secrets.JWT_SECRET_KEY }}" \
        --dry-run=client -o yaml | kubectl apply -f -
  - run: kubectl apply -f kubernetes/staging/
  - run: |
      kubectl set image deployment/user-service \
        user-service=${{ vars.ACR_LOGIN_SERVER }}/koalatech-user-service:${{ github.event.workflow_run.head_sha }} \
        -n staging
  - run: kubectl rollout status deployment/user-service -n staging --timeout=300s
```

### Manual production trigger

```yaml
on:
  workflow_dispatch:
    inputs:
      image_tag:
        description: "Tested image SHA to deploy"
        required: true
        type: string
# use ${{ inputs.image_tag }} in the kubectl set image commands
```

CI failing demo: break a frontend test → `frontend-test` fails → `build-and-push` is **skipped** because of `needs`.
Frontend CI failure seen earlier: missing `VITE_*` service URL env vars in the test job. Add test values in the job `env:`.

---

## 10. Kubernetes cheat sheet

```bash
# Inspect
kubectl get nodes
kubectl get ns
kubectl get pods -n staging
kubectl get deploy,svc,pvc -n staging
kubectl get all -n staging

# Deploy
kubectl apply -f kubernetes/staging/                 # apply a folder of manifests
kubectl set image deployment/frontend frontend=<ACR_LOGIN_SERVER>/koalatech-frontend:<SHA> -n staging
kubectl rollout status deployment/frontend -n staging
kubectl rollout history deployment/frontend -n staging
kubectl rollout undo deployment/frontend -n staging  # rollback

# Scale
kubectl scale deployment/frontend --replicas=3 -n staging

# Troubleshoot
kubectl describe pod <pod> -n staging                # events: image pull, scheduling, probes
kubectl logs <pod> -n staging
kubectl logs <pod> -n staging --previous             # logs of the crashed container
kubectl exec -it <pod> -n staging -- sh

# Public IP of the frontend
kubectl get svc frontend -n staging -w               # wait for EXTERNAL-IP
kubectl get svc frontend -n production
```

Verify which image is running (should equal the tested SHA):

```bash
kubectl get deployment frontend -n production -o jsonpath='{.spec.template.spec.containers[0].image}'
```

Minimal Deployment + Service example:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: staging
spec:
  replicas: 2
  selector:
    matchLabels: { app: frontend }
  template:
    metadata:
      labels: { app: frontend }
    spec:
      containers:
        - name: frontend
          image: <ACR_LOGIN_SERVER>/koalatech-frontend:<SHA>
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: staging
spec:
  type: LoadBalancer       # ClusterIP = internal only
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 80
```

### Errors

| Error | Meaning | Check |
| --- | --- | --- |
| `ImagePullBackOff` | Cannot pull the image | Image name/tag correct? Image in ACR? AKS has `AcrPull` on ACR? |
| `CrashLoopBackOff` | Container starts then crashes repeatedly | `kubectl logs --previous`, `describe pod`, env vars/secrets |
| `Pending` pod | Not scheduled | Not enough node CPU/memory (Week 08 needs 3 nodes), PVC unbound |
| `AuthorizationFailed` (Azure) | Missing permissions | `az account show`, correct RG/subscription, role assignments |

---

## 11. Full Week 08 run order

```bash
# 1. Infrastructure
cd terraform
terraform init && terraform fmt && terraform validate
terraform plan
terraform apply
terraform output

# 2. Cluster access
az aks get-credentials -g <RG_NAME> -n <AKS_NAME> --overwrite-existing
kubectl get nodes                       # expect 3 nodes

# 3. Service Principal + GitHub secrets/variables/environments (sections 7 and 8)

# 4. Push code -> 01 CI -> 02 Deploy Staging -> 03 Staging Test run automatically
git add . && git commit -m "Trigger CI" && git push origin main

# 5. Verify staging
kubectl get pods,svc,pvc -n staging
kubectl get svc frontend -n staging     # open EXTERNAL-IP in the browser

# 6. Promote to production (manual)
git rev-parse HEAD                      # SHA that passed staging
# GitHub -> Actions -> 04 - Deploy to Production -> Run workflow -> image_tag = <SHA>

# 7. Verify production
kubectl get pods,svc,pvc -n production
kubectl get svc frontend -n production

# 8. Clean up when finished (saves credits)
terraform destroy
# or: az group delete --name <RG_NAME> --yes --no-wait
```

---

## 12. Viva quick answers

- **Image vs container:** image is a read-only template; a container is a running instance of it.
- **ACR:** Azure private registry. It stores images and does not run them; AKS pulls from it and runs them.
- **Push to ACR:** build → tag with the login server → `az acr login` → `docker push` → verify.
- **Why commit SHA as tag:** it traces an image to exact code, and the same tested image is promoted to production (rollback = redeploy an older SHA).
- **Pod / Deployment / Service:** Pod = smallest unit; Deployment keeps N replicas running; Service = stable network access.
- **ClusterIP vs LoadBalancer:** internal only vs public IP.
- **ConfigMap vs Secret:** non-sensitive config vs sensitive data.
- **plan vs apply:** plan previews, apply changes real infrastructure.
- **Terraform state:** maps config to real resources so Terraform knows what exists.
- **Provider:** plugin that talks to a platform (`azurerm` for Azure).
- **Declarative:** describe the desired end state, and Terraform works out the steps.
- **CI:** automatic build and test on every change.
- **Continuous Delivery vs Deployment:** Delivery is always release-ready with a manual production step; Deployment auto-releases every passing change. This repo is **Delivery** (manual step 04).
- **Why staging:** finds deployment, config and network problems that unit tests miss.
- **`needs`:** a job waits for other jobs to succeed, so failed tests stop the image push.
- **Secret vs variable:** a secret is sensitive and masked; a variable is plain config (`ACR_NAME`).
- **Why delete resources:** cloud resources keep using CloudLabs credits.


# SIT722 Viva: Commands From Start to Finish (matched to this machine's directories)

Shell: Git Bash (bash). Run block by block.
Legend: ✅ safe (read/check/validate) | 💲 may create Azure cost | ⚠️ changes or deletes things (only if the tutor asks).

## Directory map (verified 2026-09-24)

| What | Path |
| --- | --- |
| App repo (Docker, Compose, K8s manifests, workflows) | `/d/Github/SIT722-week08` (Windows: `D:\Github\SIT722-week08`) |
| Terraform (real Week 08 infra) | `/d/Github/week08/terraform` (separate folder, **not** inside the repo above) |
| Week 06 examples | `/d/Github/week06` |

Repo facts that shape the commands:

- Workflows: `.github/workflows/01-ci.yml`, `02-deploy-staging.yml`, `03-staging-test.yml`, `04-deploy-production.yml`.
- `01-ci.yml` has two jobs: `backend-test` (matrix of 5 services) and `build-and-push` (`needs: backend-test`). **There is no frontend-test job in this repo.**
- Compose host ports: frontend `3000`; services `8000` user, `8001` student, `8002` lecturer, `8003` course, `8004` enrollment; databases `5433`–`5437`.
- Each service only has `.env.test`. Compose needs `.env` (gitignored), so Section 4 creates them.
- K8s manifests: `kubernetes/staging/` and `kubernetes/production/`.
- Git remotes: `origin` = `RSainarayan/SIT722-week08`, `upstream` = `sit722-devops/week08`.

Real Azure resources (verify with Section 2 first):

| Item | Value |
| --- | --- |
| Subscription | Deakin labs DS - 1069 |
| Resource group | koalatech-week08-rg |
| ACR | acrs225404454w08x (acrs225404454w08x.azurecr.io) |
| AKS | aks-koalatech-s225404454-w08 |

Never delete: `deakinuni`, `NetworkWatcherRG`, `DefaultResourceGroup-EAU`.

---

## 1. Go to the project ✅

```bash
cd /d/Github/SIT722-week08
pwd
ls
git status
git log --oneline -5
git remote -v
```

Say: "Git manages my code. These commands show the project, its state, and my GitHub fork."

---

## 2. Check Azure (always before using any resource) ✅

```bash
az account show -o table
az group list -o table
az acr list -o table
az aks list -o table
az resource list --query "[].{Name:name,Type:type,ResourceGroup:resourceGroup,Location:location}" -o table
kubectl config current-context
```

Say: "Before using any Azure resource I check what really exists in my subscription."
If `az acr list` or `az aks list` is empty, the resource has been deleted. Do not recreate it; explain the manifests or Terraform instead.

---

## 3. Docker ✅

```bash
cd /d/Github/SIT722-week08
cat user-service/Dockerfile
docker build -t viva-user-service:v1 ./user-service
docker images | grep viva-user-service
```

Optional: run it alone (no database, so it may exit; `docker logs` shows why):

```bash
docker run -d --name viva-user -p 8000:8000 viva-user-service:v1
docker ps
docker logs viva-user
docker rm -f viva-user
```

Say: "The Dockerfile is the recipe, and `docker build` makes an image. An image is the template. A container is a running instance."
Base image `python:3.12-slim`, runs as non-root `appuser`, starts with `uvicorn` on port 8000.

---

## 4. Docker Compose

Compose reads `./<service>/.env`, and only `.env.test` exists. Create the `.env` files from it. The test files use `POSTGRES_HOST=localhost`, but inside Compose the host must be the database container name:

```bash
cd /d/Github/SIT722-week08
for s in user student lecturer course enrollment; do
  sed -e "s/^POSTGRES_HOST=.*/POSTGRES_HOST=$s-db/" \
      -e "s/^POSTGRES_PORT=.*/POSTGRES_PORT=5432/" \
      $s-service/.env.test > $s-service/.env
done
ls -a user-service
cat user-service/.env
```

`.env` is in `.gitignore`, so it won't be committed. If the services still cannot reach their database, check `.env.test` for other variables that need changing.

```bash
cat docker-compose.yml
docker compose config          # ✅ validate only
docker compose up -d --build   # builds and starts all 5 services, 5 databases and the frontend
docker compose ps
docker compose logs --tail=50
```

Open: http://localhost:3000 (frontend). Service APIs: http://localhost:8000 to :8004.
Login (from the env file): `admin` / `AdminPassword123!`.

```bash
docker compose down            # cleanup (add -v to also wipe DB volumes)
```

Container-name conflict (containers are named `user-service`, `user-db` and so on):

```bash
docker ps -a
docker rm -f user-service      # use the name that docker ps -a shows
docker compose up -d
```

Say: "Compose defines the services, ports, environment variables, volumes and network in one YAML and starts everything together."

---

## 5. Push an image to ACR 💲 (small: storage only)

```bash
ACR_NAME=$(az acr list --query "[0].name" -o tsv)
echo "$ACR_NAME"

ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)
echo "$ACR_LOGIN_SERVER"

az acr login --name "$ACR_NAME"

docker tag viva-user-service:v1 "$ACR_LOGIN_SERVER/viva-user-service:v1"
docker push "$ACR_LOGIN_SERVER/viva-user-service:v1"

az acr repository list --name "$ACR_NAME" --output table
az acr repository show-tags --name "$ACR_NAME" --repository viva-user-service --output table
```

The pipeline names images `koalatech-<service>` tagged with the commit SHA. To show them:

```bash
az acr repository show-tags --name "$ACR_NAME" --repository koalatech-user-service --output table
```

Say: "The sequence is build, tag, login, push, verify. ACR only stores images. It does not run them."
Portal: Container registries → your registry → Overview (login server) → Services → Repositories.

---

## 6. Kubernetes / AKS ✅

```bash
RG=$(az aks list --query "[0].resourceGroup" -o tsv)
AKS=$(az aks list --query "[0].name" -o tsv)
echo "$RG $AKS"

az aks get-credentials --resource-group "$RG" --name "$AKS" --overwrite-existing
kubectl config current-context
kubectl get nodes                      # Week 08 expects 3 nodes
kubectl get ns
kubectl get pods -n staging
kubectl get deployments -n staging
kubectl get services -n staging
kubectl get pvc -n staging
kubectl get pods -n production
kubectl get services -n production
```

If a namespace is not found, that environment has not been deployed. Say so.

Manifests in the repo:

```bash
cd /d/Github/SIT722-week08
ls kubernetes/staging kubernetes/production
cat kubernetes/staging/12-frontend.yaml
```

Which image is running (should be the commit SHA):

```bash
kubectl get deployment frontend -n staging -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
kubectl get svc frontend -n staging        # EXTERNAL-IP = the public address
```

Troubleshooting (take a real pod name from `kubectl get pods -n staging`):

```bash
kubectl describe pod <POD_NAME> -n staging
kubectl logs <POD_NAME> -n staging
```

Say: "Pods run the containers, the Deployment keeps the replicas running, and the Service gives stable access. ClusterIP is internal and LoadBalancer is external. The database Pods use PVCs so data survives restarts."
ImagePullBackOff = cannot pull the image (check name, tag, ACR permission). CrashLoopBackOff = the container keeps crashing (check logs).

---

## 7. Terraform ✅ (real folder: `/d/Github/week08/terraform`)

```bash
cd /d/Github/week08/terraform
pwd
ls
```

Files present: `resource_group.tf`, `container_registry.tf`, `kubernetes_service.tf`, `storage_account.tf`, `variables.tf`, `versions.tf`, `output.tf`, `terraform.tfvars`, `setup-terraform.ps1`, plus existing state files.

```bash
cat versions.tf
cat variables.tf
cat kubernetes_service.tf          # node_count = var.aks_node_count (default 3)
cat terraform.tfvars

terraform version
terraform init
terraform fmt -check
terraform validate
```

`plan` only previews changes; nothing is created. Since the infrastructure already exists and is in state, it should report "No changes":

```bash
terraform plan
terraform state list
terraform output
```

Say: "`init` downloads the azurerm provider, `fmt -check` checks the formatting, `validate` checks the syntax, and `plan` previews the changes without creating anything. It says no changes because the state already matches the real resources."

Do not run `terraform apply` or `terraform destroy` unless the tutor asks. `destroy` would delete the live ACR, AKS and storage, and `terraform.tfstate` here is the record of them. Do not delete the state files.

### ⚠️ 💲 Only if the tutor asks

```bash
terraform apply                # type: yes
terraform destroy              # type: yes. This removes the real week08 infrastructure
```

Fallback if the tutor wants to see a new resource group created from scratch (separate from the real state):

```bash
mkdir -p ~/viva-terraform && cd ~/viva-terraform
cat > main.tf <<'TF'
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "viva" {
  name     = "viva-terraform-rg"
  location = "Australia East"
}
TF
export ARM_SUBSCRIPTION_ID=$(az account show --query id -o tsv)
terraform init && terraform fmt && terraform validate && terraform plan
# only if asked: terraform apply, then az group show --name viva-terraform-rg -o table, then terraform destroy
```

---

## 8. GitHub Actions / CI ✅

```bash
cd /d/Github/SIT722-week08
ls -la .github/workflows
cat .github/workflows/01-ci.yml
grep -n "uses:" .github/workflows/*.yml
grep -n -A3 "needs:" .github/workflows/*.yml
grep -n "secrets\." .github/workflows/*.yml
grep -n "vars\." .github/workflows/*.yml
gh run list --limit 10
gh secret list
gh variable list
```

Say: "A push to main triggers 01-CI. `backend-test` runs as a matrix, one job per service, each with its own PostgreSQL service container. `build-and-push` has `needs: backend-test`, so images are only built and pushed after the tests pass, tagged with the commit SHA. 02 deploys to staging, 03 tests staging, and 04 is the manual production deployment."

Backend tests locally (example for one service; the CI does this per service):

```bash
cd /d/Github/SIT722-week08/user-service
pip install -r requirements.txt
pytest -v          # needs PostgreSQL on localhost:5433 (see .env.test)
```

Frontend tests exist locally (Vitest) but are not part of this repo's CI:

```bash
cd /d/Github/SIT722-week08/frontend
npm ci
VITE_USER_SERVICE_URL=http://localhost:8000 \
VITE_STUDENT_SERVICE_URL=http://localhost:8001 \
VITE_LECTURER_SERVICE_URL=http://localhost:8002 \
VITE_COURSE_SERVICE_URL=http://localhost:8003 \
VITE_ENROLLMENT_SERVICE_URL=http://localhost:8004 \
npm run test:run
```

Say: "A secret is sensitive, like `AZURE_CREDENTIALS`. A variable is normal configuration, like `ACR_NAME`."

To demonstrate "failed test → build skipped": break one backend test on a throwaway branch, push, and show `build-and-push` as skipped in the Actions tab. Do not do this on `main` unless asked.

---

## 9. Staging → production (Continuous Delivery)

```bash
cd /d/Github/SIT722-week08
gh run list --workflow "02 - Deploy to Staging" --limit 5
gh run list --workflow "03 - Staging Test" --limit 5
git rev-parse HEAD
```

Use the SHA from the successful staging run, not just `HEAD` if newer commits exist.

⚠️ 💲 Only if asked to run the production deployment:

```bash
gh workflow run "04 - Deploy to Production" -f image_tag=<SHA_THAT_PASSED_STAGING>
gh run watch
kubectl get svc frontend -n production
```

Say: "Delivery keeps the release ready but production is a manual step. Deployment would send every passing change to production automatically. The same tested image is promoted, with no rebuild."

---

## 10. Monitoring ✅ (only if it is installed)

```bash
kubectl get pods -n monitoring
helm list -n monitoring
```

If the namespace does not exist, monitoring is not installed. Explain it instead.

```bash
kubectl port-forward -n monitoring service/prometheus-kube-prometheus-prometheus 9090:9090
# http://localhost:9090   queries: up | kube_pod_status_phase{namespace="staging", phase="Running"}

kubectl port-forward -n monitoring service/prometheus-grafana 3000:80
# http://localhost:3000   (do not show passwords; stop Compose first, since it also uses port 3000)
```

Say: "Prometheus collects metrics. Grafana shows them in dashboards."

---

## 11. Cleanup ⚠️ (saves credits; only for resources you created)

The week08 ACR and AKS are running and cost credits. Preferably tear them down with Terraform, since it owns them:

```bash
cd /d/Github/week08/terraform
terraform destroy              # type: yes
```

Or delete the whole group:

```bash
az group list -o table
az group delete --name koalatech-week08-rg --yes --no-wait
```

If you use `az group delete`, Terraform state becomes stale. Do not delete `deakinuni`, `NetworkWatcherRG` or `DefaultResourceGroup-EAU`.

---

## 12. One-line pipeline answer

"Git manages the code, GitHub Actions runs the tests, Docker packages the application, ACR stores the images, Kubernetes/AKS runs the containers, Terraform creates the Azure infrastructure, and monitoring watches it after deployment."
