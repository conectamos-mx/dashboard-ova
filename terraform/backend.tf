# =============================================================================
# TERRAFORM REMOTE STATE BACKEND
# =============================================================================
#
# Setup requerido:
# 1. Crear workspace en Terraform Cloud (https://app.terraform.io)
# 2. Crear workspace "dashboard-ova" (produccion)
# 3. Crear workspace "dashboard-ova-dev" (desarrollo) si es necesario
# 4. Obtener API token y guardarlo en GitHub Secrets como TF_API_TOKEN
#
# El workspace se selecciona via TF_WORKSPACE env var en CI/CD
# =============================================================================

terraform {
  cloud {
    organization = "CONECTAMOSAI"

    workspaces {
      tags = ["dashboard-ova"]
    }
  }
}
