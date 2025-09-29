# AgentLab Terraform Variables
# Global variables for multi-cloud infrastructure deployment

# General Configuration
variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "cloud_provider" {
  description = "Cloud provider to deploy to (aws, gcp, azure)"
  type        = string
  validation {
    condition     = contains(["aws", "gcp", "azure"], var.cloud_provider)
    error_message = "Cloud provider must be one of: aws, gcp, azure."
  }
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "agentlab.local"
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC/VNet"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for multi-AZ deployment"
  type        = list(string)
  default     = ["a", "b", "c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# AWS Configuration
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-west-2"
}

variable "app_instance_type" {
  description = "EC2 instance type for application servers"
  type        = string
  default     = "t3.medium"
}

variable "db_instance_class" {
  description = "RDS instance class for PostgreSQL"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache node type for Redis"
  type        = string
  default     = "cache.t3.micro"
}

variable "ssl_certificate_arn" {
  description = "AWS ACM certificate ARN for SSL"
  type        = string
  default     = ""
}

# GCP Configuration
variable "gcp_project" {
  description = "GCP project ID"
  type        = string
  default     = ""
}

variable "gcp_region" {
  description = "GCP region for deployment"
  type        = string
  default     = "us-west1"
}

variable "gcp_zone" {
  description = "GCP zone for deployment"
  type        = string
  default     = "us-west1-a"
}

variable "gcp_app_machine_type" {
  description = "GCE machine type for application servers"
  type        = string
  default     = "e2-medium"
}

variable "gcp_db_tier" {
  description = "Cloud SQL tier for PostgreSQL"
  type        = string
  default     = "db-f1-micro"
}

variable "gcp_redis_memory_gb" {
  description = "Memory size in GB for Cloud Memorystore Redis"
  type        = number
  default     = 1
}

variable "gcp_ssl_certificate" {
  description = "GCP SSL certificate for HTTPS"
  type        = string
  default     = ""
}

# Azure Configuration
variable "azure_location" {
  description = "Azure location for deployment"
  type        = string
  default     = "West US 2"
}

variable "azure_resource_group" {
  description = "Azure resource group name"
  type        = string
  default     = "agentlab-rg"
}

variable "azure_app_vm_size" {
  description = "Azure VM size for application servers"
  type        = string
  default     = "Standard_B2s"
}

variable "azure_db_sku_name" {
  description = "Azure Database for PostgreSQL SKU"
  type        = string
  default     = "B_Gen5_1"
}

variable "azure_redis_capacity" {
  description = "Azure Cache for Redis capacity"
  type        = number
  default     = 1
}

variable "azure_ssl_certificate" {
  description = "Azure SSL certificate for HTTPS"
  type        = string
  default     = ""
}

# Application Configuration
variable "app_replicas" {
  description = "Number of application replicas"
  type        = number
  default     = 2
}

variable "enable_auto_scaling" {
  description = "Enable auto scaling for application servers"
  type        = bool
  default     = true
}

variable "min_capacity" {
  description = "Minimum capacity for auto scaling"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum capacity for auto scaling"
  type        = number
  default     = 10
}

# Database Configuration
variable "db_allocated_storage" {
  description = "Allocated storage for database in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for database in GB"
  type        = number
  default     = 100
}

variable "enable_db_backup" {
  description = "Enable automated database backups"
  type        = bool
  default     = true
}

variable "db_backup_retention" {
  description = "Database backup retention period in days"
  type        = number
  default     = 7
}

# Monitoring and Logging
variable "monitoring_config" {
  description = "Monitoring and alerting configuration"
  type = object({
    enable_monitoring = bool
    enable_alerting   = bool
    log_retention     = number
  })
  default = {
    enable_monitoring = true
    enable_alerting   = true
    log_retention     = 30
  }
}