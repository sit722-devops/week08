terraform {
  backend "azurerm" {
    resource_group_name = "sit722w8-tfstate-rg"
    storage_account_name = "sit722w8tfstate"
    container_name       = "tfstate"
    key                   = "week08.tfstate"
  }
}
