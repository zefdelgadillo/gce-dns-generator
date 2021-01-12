provider "random" {
  version = "~> 2.0"
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "google_service_account" "service_account" {
  project      = var.project_id
  account_id   = "dns-record-maintainer"
  display_name = "Maintains Cloud DNS records based on VMs"
}

resource "google_folder_iam_binding" "function-folder" {
  folder = "folders/${var.folder_id}"
  role   = "roles/compute.viewer"

  members = [
    "serviceAccount:${google_service_account.service_account.email}",
  ]
}

resource "google_project_iam_binding" "function-dns-project" {
  project = var.cloud_dns_project_id
  role    = "roles/dns.admin"

  members = [
    "serviceAccount:${google_service_account.service_account.email}",
  ]
}


module "dns-record-create" {
  source     = "terraform-google-modules/event-function/google"
  version    = "1.4.0"
  project_id = var.project_id

  name                  = "dns-creation-${random_id.suffix.hex}"
  description           = "Creates DNS records on the presence of new VMs within the specified Folder"
  region                = var.region
  runtime               = "python37"
  source_directory      = "${path.module}/src"
  entry_point           = "create"
  event_trigger         = module.gce-create-event-entry.function_event_trigger
  service_account_email = google_service_account.service_account.email

  environment_variables = {
    CLOUD_DNS_PROJECT = var.cloud_dns_project_id
    CLOUD_DNS_ZONE    = var.cloud_dns_zone
  }
}

module "dns-record-delete" {
  source     = "terraform-google-modules/event-function/google"
  version    = "1.4.0"
  project_id = var.project_id

  name                  = "dns-deletion-${random_id.suffix.hex}"
  description           = "Removes DNS records on the presence of deleted VMs within the specified Folder"
  region                = var.region
  runtime               = "python37"
  source_directory      = "${path.module}/src"
  entry_point           = "delete"
  event_trigger         = module.gce-delete-event-entry.function_event_trigger
  service_account_email = google_service_account.service_account.email

  environment_variables = {
    CLOUD_DNS_PROJECT = var.cloud_dns_project_id
    CLOUD_DNS_ZONE    = var.cloud_dns_zone
  }
}

module "gce-create-event-entry" {
  source     = "terraform-google-modules/event-function/google//modules/event-folder-log-entry"
  version    = "1.4.0"
  project_id = var.project_id


  filter           = "resource.type=\"gce_instance\" operation.last=\"true\" protoPayload.methodName=\"beta.compute.instances.insert\""
  name             = "create-dns-${random_id.suffix.hex}"
  folder_id        = var.folder_id
  include_children = "true"
}

module "gce-delete-event-entry" {
  source     = "terraform-google-modules/event-function/google//modules/event-folder-log-entry"
  version    = "1.4.0"
  project_id = var.project_id


  filter           = "resource.type=\"gce_instance\" operation.last=\"true\" protoPayload.methodName=\"v1.compute.instances.delete\""
  name             = "delete-dns-${random_id.suffix.hex}"
  folder_id        = var.folder_id
  include_children = "true"
}