# AgentLab Terraform Outputs
# Output values for infrastructure components

# General outputs
output "environment" {
  description = "Deployment environment"
  value       = var.environment
}

output "cloud_provider" {
  description = "Cloud provider used for deployment"
  value       = var.cloud_provider
}

# AWS outputs
output "aws_vpc_id" {
  description = "AWS VPC ID"
  value       = var.cloud_provider == "aws" ? module.aws_infrastructure[0].vpc_id : null
}

output "aws_load_balancer_dns" {
  description = "AWS Application Load Balancer DNS name"
  value       = var.cloud_provider == "aws" ? module.aws_infrastructure[0].load_balancer_dns : null
}

output "aws_database_endpoint" {
  description = "AWS RDS PostgreSQL endpoint"
  value       = var.cloud_provider == "aws" ? module.aws_infrastructure[0].database_endpoint : null
  sensitive   = true
}

output "aws_redis_endpoint" {
  description = "AWS ElastiCache Redis endpoint"
  value       = var.cloud_provider == "aws" ? module.aws_infrastructure[0].redis_endpoint : null
  sensitive   = true
}

# GCP outputs
output "gcp_network_name" {
  description = "GCP VPC network name"
  value       = var.cloud_provider == "gcp" ? module.gcp_infrastructure[0].network_name : null
}

output "gcp_load_balancer_ip" {
  description = "GCP Load Balancer IP address"
  value       = var.cloud_provider == "gcp" ? module.gcp_infrastructure[0].load_balancer_ip : null
}

output "gcp_database_connection" {
  description = "GCP Cloud SQL connection name"
  value       = var.cloud_provider == "gcp" ? module.gcp_infrastructure[0].database_connection : null
  sensitive   = true
}

output "gcp_redis_host" {
  description = "GCP Cloud Memorystore Redis host"
  value       = var.cloud_provider == "gcp" ? module.gcp_infrastructure[0].redis_host : null
  sensitive   = true
}

# Azure outputs
output "azure_resource_group" {
  description = "Azure resource group name"
  value       = var.cloud_provider == "azure" ? module.azure_infrastructure[0].resource_group_name : null
}

output "azure_app_gateway_ip" {
  description = "Azure Application Gateway public IP"
  value       = var.cloud_provider == "azure" ? module.azure_infrastructure[0].app_gateway_ip : null
}

output "azure_database_fqdn" {
  description = "Azure Database for PostgreSQL FQDN"
  value       = var.cloud_provider == "azure" ? module.azure_infrastructure[0].database_fqdn : null
  sensitive   = true
}

output "azure_redis_hostname" {
  description = "Azure Cache for Redis hostname"
  value       = var.cloud_provider == "azure" ? module.azure_infrastructure[0].redis_hostname : null
  sensitive   = true
}

# Application URLs
output "application_url" {
  description = "Application URL"
  value = var.cloud_provider == "aws" ? (
    module.aws_infrastructure[0].load_balancer_dns
    ) : var.cloud_provider == "gcp" ? (
    "http://${module.gcp_infrastructure[0].load_balancer_ip}"
    ) : var.cloud_provider == "azure" ? (
    "http://${module.azure_infrastructure[0].app_gateway_ip}"
  ) : null
}

output "api_url" {
  description = "API endpoint URL"
  value = var.cloud_provider == "aws" ? (
    "${module.aws_infrastructure[0].load_balancer_dns}/api"
    ) : var.cloud_provider == "gcp" ? (
    "http://${module.gcp_infrastructure[0].load_balancer_ip}/api"
    ) : var.cloud_provider == "azure" ? (
    "http://${module.azure_infrastructure[0].app_gateway_ip}/api"
  ) : null
}

# Database connection strings
output "database_url" {
  description = "Database connection URL"
  value = var.cloud_provider == "aws" ? (
    "postgresql://agentlab_user:${random_password.db_password.result}@${module.aws_infrastructure[0].database_endpoint}:5432/agentlab"
    ) : var.cloud_provider == "gcp" ? (
    "postgresql://agentlab_user:${random_password.db_password.result}@${module.gcp_infrastructure[0].database_connection}/agentlab"
    ) : var.cloud_provider == "azure" ? (
    "postgresql://agentlab_user:${random_password.db_password.result}@${module.azure_infrastructure[0].database_fqdn}:5432/agentlab"
  ) : null
  sensitive = true
}

output "redis_url" {
  description = "Redis connection URL"
  value = var.cloud_provider == "aws" ? (
    "redis://:${random_password.redis_password.result}@${module.aws_infrastructure[0].redis_endpoint}:6379"
    ) : var.cloud_provider == "gcp" ? (
    "redis://${module.gcp_infrastructure[0].redis_host}:6379"
    ) : var.cloud_provider == "azure" ? (
    "redis://:${random_password.redis_password.result}@${module.azure_infrastructure[0].redis_hostname}:6380"
  ) : null
  sensitive = true
}

# Security
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "random_password" "redis_password" {
  length  = 32
  special = false
}

# Monitoring
output "monitoring_dashboard_url" {
  description = "Monitoring dashboard URL"
  value       = module.shared_resources.monitoring_dashboard_url
}

output "log_aggregation_endpoint" {
  description = "Log aggregation endpoint"
  value       = module.shared_resources.log_aggregation_endpoint
  sensitive   = true
}