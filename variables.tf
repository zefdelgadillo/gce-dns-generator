variable "project_id" {
  type        = string
  description = "Google Cloud Project to crate Cloud Function and other resources"
}
variable "region" {
  type        = string
  default     = "us-central1"
  description = "Google Cloud region for Cloud Function"
}
variable "folder_id" {
  type        = "string"
  description = "Folder to listen for new GCE create and delete events"
}
variable "cloud_dns_project_id" {
  type        = string
  description = "Project where Cloud DNS is configured"
}
variable "cloud_dns_zone" {
  type        = string
  description = "Name of Cloud DNS zone"
}