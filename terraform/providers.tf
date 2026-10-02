terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # Remote state so the GitHub Actions runner and my laptop share one state file.
  # Authentication to the state container uses ARM_ACCESS_KEY (never committed).
  backend "azurerm" {
    resource_group_name  = "koalatech-tfstate-rg"
    storage_account_name = "tfstates225404454w08"
    container_name       = "tfstate"
    key                  = "week10.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}

  # The pipeline service principal is scoped to one resource group, so it cannot
  # register subscription-level resource providers. They are already registered.
  resource_provider_registrations = "none"

  # subscription_id is read from ARM_SUBSCRIPTION_ID
}
