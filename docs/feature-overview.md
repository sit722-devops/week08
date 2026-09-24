# Blue/Green Deployment and Automated Rollback

## Introduction

This project implements continuous delivery for the KoalaTech University application using GitHub Actions, Docker, Azure Container Registry (ACR), and Azure App Service deployment slots. The selected feature is a blue/green deployment strategy with automated production verification and rollback.

A new application version is built once, deployed to an isolated staging slot, and tested before promotion. Production is updated by swapping the staging slot with the production slot. If the promoted version fails production verification, the workflow performs a reverse slot swap to restore the previous working version.

This separates building, testing, releasing, and recovery into a repeatable process. It also ensures that the image tested in staging is the same image promoted to production.

## Feature Overview

The delivery process consists of four connected GitHub Actions workflows:

1. **Continuous Integration:** Backend tests run, Terraform is validated, and Docker images are built and pushed to ACR using the Git commit SHA as the image tag.
2. **Staging Deployment:** The exact frontend image produced by CI is configured on the Azure App Service staging slot through the Azure Resource Manager API.
3. **Staging Smoke Test:** GitHub Actions requests the staging hostname and confirms that the application responds with valid frontend HTML.
4. **Production Promotion:** The staging slot is swapped into production. The live production endpoint is tested. If verification fails, the workflow swaps the slots back and marks the deployment as failed.

The production and staging slots are hosted by the same Linux App Service plan. ACR stores immutable Docker images, while GitHub Actions orchestrates deployment and recovery.

## Deployment Flow

```text
Git push to main
        |
        v
01 - CI
  tests, Terraform validation, image build and ACR push
        |
        v
02 - Deploy to Staging
  deploy SHA-tagged image to the staging slot
        |
        v
03 - Test Staging
  verify staging responds with valid HTML
        |
        v
04 - Deploy to Production
  swap staging into production
        |
        v
Production verification
        |
   +----+----+
   |         |
 pass      fail
   |         |
 success   reverse slot swap
             |
          production restored
```

The Docker image is not rebuilt during promotion. This reduces the possibility that staging and production run different artifacts.

## Verification and Rollback

Staging verification checks that the staging hostname responds successfully and contains expected HTML markers such as `html`, `doctype`, `KoalaTech`, or `Login`. Production verification repeats the check after the slot swap against the production hostname.

The production workflow treats a failed HTTP request or unexpected response as a deployment failure. It then executes a real Azure slot swap in the reverse direction. Since deployment slots exchange their running versions, the reverse swap restores the version that was previously serving production. The workflow remains failed so the rejected release is visible in GitHub Actions, while the service is returned to a healthy state.

The demonstration fault is limited to the frontend Nginx configuration. It returns HTTP 503 only for the production hostname. The faulty version can therefore pass the staging smoke test but fail after promotion, exercising the real rollback path without changing application data, databases, or infrastructure.

## Benefits

- Lower deployment risk through isolated staging validation.
- Immutable, SHA-tagged Docker artifacts.
- Consistent promotion of the tested image.
- Minimal production interruption through slot swapping.
- Automated recovery when production verification fails.
- Traceable evidence through GitHub Actions and Azure activity logs.
- Controlled failure testing without damaging databases or Terraform-managed infrastructure.

Overall, the feature demonstrates how blue/green delivery combines release isolation, automated testing, production verification, and recovery into one repeatable deployment process.
