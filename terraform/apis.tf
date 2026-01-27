# =============================================================================
# GOOGLE CLOUD APIS
# =============================================================================
#
# Habilita automaticamente las APIs necesarias para la infraestructura.
#
# =============================================================================

resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",              # Cloud Run
    "artifactregistry.googleapis.com", # Artifact Registry (Docker images)
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy         = false
  disable_dependent_services = false
}
