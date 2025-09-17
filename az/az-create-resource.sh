# Set your variables
RESOURCE_GROUP=week09
LOCATION=australiaeast   # or your preferred Azure region
ACR_NAME=week09acr$RANDOM   # must be globally unique
AKS_NAME=week09aks

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create ACR
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Create AKS and attach ACR
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --node-count 1 \
  --generate-ssh-keys \
  --attach-acr $ACR_NAME