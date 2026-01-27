# =============================================================================
# CLOUD PROVIDER CONFIGURATION
# =============================================================================

variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
  default     = "conectamos-ai"
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-central1"
}

# =============================================================================
# SERVICE CONFIGURATION
# =============================================================================

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "dashboard-ova"
}

variable "docker_image" {
  description = "Full Docker image URL with tag"
  type        = string
}

# =============================================================================
# COMPUTE RESOURCES
# =============================================================================

variable "service_memory" {
  description = "Memory allocation (e.g., 512Mi, 1Gi)"
  type        = string
  default     = "512Mi"
}

variable "service_cpu" {
  description = "CPU allocation (e.g., 1, 2)"
  type        = string
  default     = "1"
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "cpu_idle" {
  description = "Allow CPU throttling when idle"
  type        = bool
  default     = false
}

variable "timeout_seconds" {
  description = "Request timeout in seconds"
  type        = number
  default     = 300
}

variable "allow_public_access" {
  description = "Allow unauthenticated access"
  type        = bool
  default     = true
}

# =============================================================================
# APPLICATION ENVIRONMENT
# =============================================================================

variable "app_env" {
  description = "Application environment (development, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "production"], var.app_env)
    error_message = "Environment must be: development or production"
  }
}

# =============================================================================
# MICROSOFT GRAPH API CONFIGURATION
# =============================================================================

variable "microsoft_client_id" {
  description = "Microsoft Azure App Client ID"
  type        = string
  sensitive   = true
}

variable "microsoft_client_secret" {
  description = "Microsoft Azure App Client Secret"
  type        = string
  sensitive   = true
}

variable "microsoft_tenant_id" {
  description = "Microsoft Tenant ID (use 'consumers' for personal accounts)"
  type        = string
  default     = "consumers"
}

variable "microsoft_access_token" {
  description = "Microsoft Graph API Access Token"
  type        = string
  sensitive   = true
}

variable "microsoft_refresh_token" {
  description = "Microsoft Graph API Refresh Token"
  type        = string
  sensitive   = true
}

variable "microsoft_drive_id" {
  description = "OneDrive Drive ID"
  type        = string
}

# =============================================================================
# EXCEL FILE CONFIGURATION (OneDrive Item IDs)
# =============================================================================

variable "excel_almacen_item_id" {
  description = "OneDrive Item ID for Almacen Excel file"
  type        = string
}

variable "excel_ventas_item_id" {
  description = "OneDrive Item ID for Ventas Excel file"
  type        = string
}

# =============================================================================
# FEATURE FLAGS
# =============================================================================

variable "use_onedrive" {
  description = "Use OneDrive as data source (true) or local files (false)"
  type        = string
  default     = "true"
}

variable "python_version" {
  description = "Python version for reference"
  type        = string
  default     = "3.12"
}

# =============================================================================
# RESOURCE LABELS
# =============================================================================

variable "common_labels" {
  description = "Common labels for all resources"
  type        = map(string)
  default = {
    project    = "dashboard-ova"
    managed-by = "terraform"
  }
}
