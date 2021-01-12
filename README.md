# DNS Record Generator for Google Compute Engine
Listens for new virtual machines created in Google Compute Engine and creates DNS entries in Cloud DNS.

This module creates a Cloud Function, PubSub Topic, and other resources that keep your Google Compute Engine virtual machines in sync with Cloud DNS.

When you create a virtual machine in any project within a folder, this module will automatically create a corresponding A Record in a Cloud DNS managed zone that you specify.

## Usage
Deployment uses [Terraform](https://learn.hashicorp.com/collections/terraform/gcp-get-started). Fill out the `terraform.tfvars` file, and use Terraform to create resources in your environment.

## Required Permissions
**Folder Level**
* IAM Admin
* Logging Admin

**Cloud DNS Project**
* IAM Admin

**Cloud Functions Project**
* PubSub Admin
* Cloud Build Admin
* Cloud Functions Admin

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| cloud\_dns\_project\_id | Project where Cloud DNS is configured | `string` | n/a | yes |
| cloud\_dns\_zone | Name of Cloud DNS zone | `string` | n/a | yes |
| folder\_id | Folder to listen for new GCE create and delete events | `string` | n/a | yes |
| project\_id | Google Cloud Project to crate Cloud Function and other resources | `string` | n/a | yes |
| region | Google Cloud region for Cloud Function | `string` | `"us-central1"` | no |
