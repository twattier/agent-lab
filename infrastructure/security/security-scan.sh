#!/bin/bash

# AgentLab Container Security Scanning Script
# Performs vulnerability scanning on Docker images using trivy

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCAN_OUTPUT_DIR="./infrastructure/security/scan-results"
SEVERITY_THRESHOLD="HIGH"
IMAGES_TO_SCAN=(
    "postgres:15.4"
    "redis:7.0-alpine"
    "nginx:1.25-alpine"
    "python:3.11.5-slim"
    "node:18.17.0-alpine"
)

# Custom images (built locally)
CUSTOM_IMAGES=(
    "agentlab/api:latest"
    "agentlab/web:latest"
)

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v trivy &> /dev/null; then
        log_error "trivy is not installed. Please install it first:"
        echo "  # For Ubuntu/Debian:"
        echo "  sudo apt-get update && sudo apt-get install wget apt-transport-https gnupg lsb-release"
        echo "  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -"
        echo "  echo \"deb https://aquasecurity.github.io/trivy-repo/deb \$(lsb_release -sc) main\" | sudo tee -a /etc/apt/sources.list.d/trivy.list"
        echo "  sudo apt-get update && sudo apt-get install trivy"
        echo ""
        echo "  # For macOS:"
        echo "  brew install aquasecurity/trivy/trivy"
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    log_success "All dependencies are available"
}

create_output_directory() {
    log_info "Creating output directory: $SCAN_OUTPUT_DIR"
    mkdir -p "$SCAN_OUTPUT_DIR"
}

update_trivy_db() {
    log_info "Updating Trivy vulnerability database..."
    trivy image --download-db-only
    log_success "Trivy database updated"
}

scan_base_images() {
    log_info "Scanning base images for vulnerabilities..."

    for image in "${IMAGES_TO_SCAN[@]}"; do
        log_info "Scanning image: $image"

        # Generate safe filename
        safe_name=$(echo "$image" | sed 's/[^a-zA-Z0-9._-]/_/g')
        output_file="$SCAN_OUTPUT_DIR/base_${safe_name}_scan.json"
        report_file="$SCAN_OUTPUT_DIR/base_${safe_name}_report.txt"

        # Scan for vulnerabilities
        if trivy image \
            --format json \
            --output "$output_file" \
            --severity "$SEVERITY_THRESHOLD,CRITICAL" \
            --no-progress \
            "$image"; then

            # Generate human-readable report
            trivy image \
                --format table \
                --output "$report_file" \
                --severity "$SEVERITY_THRESHOLD,CRITICAL" \
                --no-progress \
                "$image"

            # Count vulnerabilities
            high_count=$(jq '[.Results[]? | .Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$output_file" 2>/dev/null || echo "0")
            critical_count=$(jq '[.Results[]? | .Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$output_file" 2>/dev/null || echo "0")

            if [[ $critical_count -gt 0 ]]; then
                log_error "Image $image has $critical_count CRITICAL vulnerabilities"
            elif [[ $high_count -gt 0 ]]; then
                log_warning "Image $image has $high_count HIGH vulnerabilities"
            else
                log_success "Image $image passed security scan"
            fi
        else
            log_error "Failed to scan image: $image"
        fi

        echo ""
    done
}

scan_custom_images() {
    log_info "Scanning custom images for vulnerabilities..."

    for image in "${CUSTOM_IMAGES[@]}"; do
        log_info "Checking if custom image exists: $image"

        if docker image inspect "$image" >/dev/null 2>&1; then
            log_info "Scanning custom image: $image"

            # Generate safe filename
            safe_name=$(echo "$image" | sed 's/[^a-zA-Z0-9._-]/_/g')
            output_file="$SCAN_OUTPUT_DIR/custom_${safe_name}_scan.json"
            report_file="$SCAN_OUTPUT_DIR/custom_${safe_name}_report.txt"

            # Scan for vulnerabilities
            if trivy image \
                --format json \
                --output "$output_file" \
                --severity "$SEVERITY_THRESHOLD,CRITICAL" \
                --no-progress \
                "$image"; then

                # Generate human-readable report
                trivy image \
                    --format table \
                    --output "$report_file" \
                    --severity "$SEVERITY_THRESHOLD,CRITICAL" \
                    --no-progress \
                    "$image"

                # Count vulnerabilities
                high_count=$(jq '[.Results[]? | .Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$output_file" 2>/dev/null || echo "0")
                critical_count=$(jq '[.Results[]? | .Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$output_file" 2>/dev/null || echo "0")

                if [[ $critical_count -gt 0 ]]; then
                    log_error "Custom image $image has $critical_count CRITICAL vulnerabilities"
                elif [[ $high_count -gt 0 ]]; then
                    log_warning "Custom image $image has $high_count HIGH vulnerabilities"
                else
                    log_success "Custom image $image passed security scan"
                fi
            else
                log_error "Failed to scan custom image: $image"
            fi
        else
            log_warning "Custom image $image not found (may need to be built first)"
        fi

        echo ""
    done
}

generate_summary_report() {
    log_info "Generating summary report..."

    summary_file="$SCAN_OUTPUT_DIR/security_scan_summary.txt"

    cat > "$summary_file" << EOF
AgentLab Security Scan Summary
Generated: $(date)
Scan Threshold: $SEVERITY_THRESHOLD and CRITICAL

Base Images Scanned:
EOF

    for image in "${IMAGES_TO_SCAN[@]}"; do
        echo "  - $image" >> "$summary_file"
    done

    cat >> "$summary_file" << EOF

Custom Images Scanned:
EOF

    for image in "${CUSTOM_IMAGES[@]}"; do
        echo "  - $image" >> "$summary_file"
    done

    cat >> "$summary_file" << EOF

Scan Results:
EOF

    # Process scan results
    total_critical=0
    total_high=0

    for json_file in "$SCAN_OUTPUT_DIR"/*.json; do
        if [[ -f "$json_file" ]]; then
            high_count=$(jq '[.Results[]? | .Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$json_file" 2>/dev/null || echo "0")
            critical_count=$(jq '[.Results[]? | .Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$json_file" 2>/dev/null || echo "0")

            total_high=$((total_high + high_count))
            total_critical=$((total_critical + critical_count))

            filename=$(basename "$json_file" .json)
            echo "  $filename: $critical_count CRITICAL, $high_count HIGH" >> "$summary_file"
        fi
    done

    cat >> "$summary_file" << EOF

Total Vulnerabilities Found:
  CRITICAL: $total_critical
  HIGH: $total_high

For detailed reports, see individual scan files in: $SCAN_OUTPUT_DIR

Recommendations:
  - Review and address all CRITICAL vulnerabilities immediately
  - Plan remediation for HIGH severity vulnerabilities
  - Consider updating base images to newer versions
  - Regularly re-run security scans as part of CI/CD pipeline
EOF

    log_success "Summary report generated: $summary_file"

    # Display summary
    echo ""
    log_info "SCAN SUMMARY:"
    echo "  Total CRITICAL vulnerabilities: $total_critical"
    echo "  Total HIGH vulnerabilities: $total_high"

    if [[ $total_critical -gt 0 ]]; then
        log_error "Action required: $total_critical CRITICAL vulnerabilities found"
        return 1
    elif [[ $total_high -gt 0 ]]; then
        log_warning "Review recommended: $total_high HIGH vulnerabilities found"
        return 0
    else
        log_success "All scanned images passed security requirements"
        return 0
    fi
}

# Main execution
main() {
    log_info "Starting AgentLab security scan..."

    check_dependencies
    create_output_directory
    update_trivy_db
    scan_base_images
    scan_custom_images

    if generate_summary_report; then
        log_success "Security scan completed successfully"
        exit 0
    else
        log_error "Security scan completed with issues that require attention"
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
AgentLab Container Security Scanning Script

Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -t, --threshold LEVEL   Set severity threshold (LOW, MEDIUM, HIGH, CRITICAL)
                           Default: $SEVERITY_THRESHOLD

Examples:
    $0                      # Run scan with default settings
    $0 -t MEDIUM           # Scan for MEDIUM and higher severity issues

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--threshold)
            SEVERITY_THRESHOLD="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main "$@"