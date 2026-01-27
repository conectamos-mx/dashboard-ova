# =============================================================================
# MAIN TERRAFORM CONFIGURATION - DASHBOARD OVA
# =============================================================================
#
# Infraestructura: Cloud Run (serverless)
# Base de datos: No aplica (usa Excel de OneDrive via Microsoft Graph API)
#
# =============================================================================

# =============================================================================
# LOCAL VARIABLES
# =============================================================================

locals {
  # Workspace-based naming
  is_production    = terraform.workspace == "dashboard-ova"
  workspace_suffix = terraform.workspace == "dashboard-ova" ? "-prod" : "-dev"

  # Resource naming
  service_name = var.service_name

  # Environment variables for Cloud Run
  environment_variables = {
    # Microsoft Graph API
    MICROSOFT_CLIENT_ID     = var.microsoft_client_id
    MICROSOFT_CLIENT_SECRET = var.microsoft_client_secret
    MICROSOFT_TENANT_ID     = var.microsoft_tenant_id
    MICROSOFT_ACCESS_TOKEN  = var.microsoft_access_token
    MICROSOFT_REFRESH_TOKEN = var.microsoft_refresh_token
    MICROSOFT_DRIVE_ID      = var.microsoft_drive_id

    # Excel file IDs
    EXCEL_ALMACEN_ITEM_ID = var.excel_almacen_item_id
    EXCEL_VENTAS_ITEM_ID  = var.excel_ventas_item_id

    # Feature flags
    USE_ONEDRIVE   = var.use_onedrive
    PYTHON_VERSION = var.python_version
  }

  # Common labels
  common_labels = merge(
    var.common_labels,
    {
      environment = var.app_env
      workspace   = terraform.workspace
    }
  )
}

# =============================================================================
# CLOUD RUN SERVICE
# =============================================================================

resource "google_cloud_run_v2_service" "service" {
  name     = local.service_name
  location = var.region

  labels = local.common_labels

  template {
    # Scaling configuration
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    # Container configuration
    containers {
      image = var.docker_image

      # Resource limits
      resources {
        limits = {
          cpu    = var.service_cpu
          memory = var.service_memory
        }

        cpu_idle          = var.cpu_idle
        startup_cpu_boost = true
      }

      # Environment variables
      dynamic "env" {
        for_each = local.environment_variables
        content {
          name  = env.key
          value = env.value
        }
      }

      # Health check probes
      startup_probe {
        http_get {
          path = "/api/health"
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 5
      }

      liveness_probe {
        http_get {
          path = "/api/health"
        }
        initial_delay_seconds = 0
        timeout_seconds       = 1
        period_seconds        = 10
        failure_threshold     = 3
      }
    }

    timeout = "${var.timeout_seconds}s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.required_apis
  ]
}

# =============================================================================
# PUBLIC ACCESS IAM POLICY
# =============================================================================

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count = var.allow_public_access ? 1 : 0

  location = google_cloud_run_v2_service.service.location
  name     = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
