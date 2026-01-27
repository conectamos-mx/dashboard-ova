# =============================================================================
# TERRAFORM OUTPUTS - DASHBOARD OVA
# =============================================================================

# =============================================================================
# SERVICE OUTPUTS
# =============================================================================

output "service_url" {
  description = "Public URL of the deployed service"
  value       = google_cloud_run_v2_service.service.uri
}

output "service_name" {
  description = "Name of the deployed service"
  value       = var.service_name
}

output "service_id" {
  description = "Unique identifier of the service"
  value       = google_cloud_run_v2_service.service.id
}

output "service_location" {
  description = "Region where the service is deployed"
  value       = var.region
}

# =============================================================================
# CONTAINER REGISTRY OUTPUTS
# =============================================================================

output "container_registry_url" {
  description = "URL for pushing Docker images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.service_name}"
}

# =============================================================================
# DEPLOYMENT INFO
# =============================================================================

output "deployed_image" {
  description = "Docker image currently deployed"
  value       = var.docker_image
}

output "environment" {
  description = "Application environment"
  value       = var.app_env
}

output "health_check_url" {
  description = "Health check endpoint URL"
  value       = "${google_cloud_run_v2_service.service.uri}/api/health"
}

# =============================================================================
# DEPLOYMENT SUMMARY
# =============================================================================

output "deployment_summary" {
  description = "Summary of the deployment configuration"
  value = {
    service_name  = var.service_name
    region        = var.region
    environment   = var.app_env
    service_url   = google_cloud_run_v2_service.service.uri
    min_instances = var.min_instances
    max_instances = var.max_instances
    memory        = var.service_memory
    cpu           = var.service_cpu
    use_onedrive  = var.use_onedrive
  }
}
