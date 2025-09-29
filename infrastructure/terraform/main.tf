# AgentLab Infrastructure as Code
# Main Terraform configuration for multi-cloud deployment

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # Remote state backend (configure based on chosen provider)
  backend "s3" {
    # AWS S3 backend example
    bucket         = "agentlab-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "agentlab-terraform-locks"
  }
}

# Local variables
locals {
  project_name = "agentlab"
  environment  = var.environment

  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "terraform"
    CreatedAt   = timestamp()
  }
}

# Data sources for current configuration
data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "agentlab-terraform-state"
    key    = "network/${var.environment}/terraform.tfstate"
    region = var.aws_region
  }
}

# Module configurations based on cloud provider
module "aws_infrastructure" {
  count  = var.cloud_provider == "aws" ? 1 : 0
  source = "./modules/aws"

  project_name = local.project_name
  environment  = local.environment
  aws_region   = var.aws_region

  # Network configuration
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  private_subnet_cidrs = var.private_subnet_cidrs
  public_subnet_cidrs  = var.public_subnet_cidrs

  # Application configuration
  app_instance_type = var.app_instance_type
  db_instance_class = var.db_instance_class
  redis_node_type   = var.redis_node_type

  # Security configuration
  allowed_cidr_blocks = var.allowed_cidr_blocks
  ssl_certificate_arn = var.ssl_certificate_arn

  tags = local.common_tags
}

module "gcp_infrastructure" {
  count  = var.cloud_provider == "gcp" ? 1 : 0
  source = "./modules/gcp"

  project_name = local.project_name
  environment  = local.environment
  gcp_project  = var.gcp_project
  gcp_region   = var.gcp_region
  gcp_zone     = var.gcp_zone

  # Network configuration
  network_cidr         = var.vpc_cidr
  subnet_cidrs         = var.private_subnet_cidrs

  # Application configuration
  app_machine_type = var.gcp_app_machine_type
  db_tier          = var.gcp_db_tier
  redis_memory_gb  = var.gcp_redis_memory_gb

  # Security configuration
  allowed_cidr_blocks = var.allowed_cidr_blocks
  ssl_certificate     = var.gcp_ssl_certificate

  labels = local.common_tags
}

module "azure_infrastructure" {
  count  = var.cloud_provider == "azure" ? 1 : 0
  source = "./modules/azure"

  project_name      = local.project_name
  environment       = local.environment
  azure_location    = var.azure_location
  resource_group    = var.azure_resource_group

  # Network configuration
  vnet_cidr           = var.vpc_cidr
  subnet_cidrs        = var.private_subnet_cidrs

  # Application configuration
  app_vm_size     = var.azure_app_vm_size
  db_sku_name     = var.azure_db_sku_name
  redis_capacity  = var.azure_redis_capacity

  # Security configuration
  allowed_cidr_blocks = var.allowed_cidr_blocks
  ssl_certificate     = var.azure_ssl_certificate

  tags = local.common_tags
}

# Shared resources module
module "shared_resources" {
  source = "./modules/shared"

  project_name = local.project_name
  environment  = local.environment

  # DNS and monitoring configuration
  domain_name     = var.domain_name
  monitoring_config = var.monitoring_config

  tags = local.common_tags
}