# External Services Setup Guide

This document provides detailed instructions for setting up external services required by AgentLab.

## Claude API Setup

### Account Creation

1. **Visit Console**
   - Go to [console.anthropic.com](https://console.anthropic.com)
   - Click "Sign Up" or "Log In"

2. **Account Verification**
   - Complete email verification
   - Provide required account information
   - Accept terms of service

3. **Billing Setup**
   - Add payment method (required for API access)
   - Review pricing at [anthropic.com/pricing](https://anthropic.com/pricing)
   - Set up billing alerts to monitor usage

### API Key Generation

1. **Navigate to API Keys**
   - From the console dashboard, go to "API Keys"
   - Click "Create Key"

2. **Key Configuration**
   - Provide a descriptive name (e.g., "AgentLab Development")
   - Set appropriate permissions
   - Note the key immediately (it won't be shown again)

3. **Environment Configuration**
   ```bash
   # Add to your .env file
   CLAUDE_API_KEY=sk-ant-api03-your-key-here
   ```

### Rate Limits and Monitoring

- **Check Current Limits**: Visit console dashboard
- **Monitor Usage**: Set up alerts for approaching limits
- **Upgrade Plans**: Scale as needed for production

### Security Guidelines

- **Key Rotation**: Rotate keys every 90 days
- **Access Control**: Use separate keys for different environments
- **Monitoring**: Implement usage monitoring and alerting
- **Incident Response**: Have key revocation process ready

## Optional LLM Providers

### OpenAI API (Fallback Provider)

1. **Account Setup**
   - Visit [platform.openai.com](https://platform.openai.com)
   - Create account and verify email
   - Add payment method

2. **API Key Creation**
   - Go to API Keys section
   - Click "Create new secret key"
   - Copy and store securely

3. **Configuration**
   ```bash
   # Add to .env file
   OPENAI_API_KEY=sk-your-openai-key-here
   ```

### OLLAMA (Local Development)

1. **Installation**

   **macOS:**
   ```bash
   brew install ollama
   ```

   **Linux:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

   **Windows:**
   - Download from [ollama.ai](https://ollama.ai)
   - Run the installer

2. **Model Setup**
   ```bash
   # Pull required models
   ollama pull llama2
   ollama pull codellama

   # Start OLLAMA service
   ollama serve
   ```

3. **Configuration**
   ```bash
   # Add to .env file
   OLLAMA_HOST=http://localhost:11434
   ```

## Environment Variables Reference

### Required Variables

```bash
# Claude API (Required)
CLAUDE_API_KEY=sk-ant-api03-your-key-here

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/agentlab
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET=your-secure-jwt-secret
SESSION_SECRET=your-secure-session-secret
```

### Optional Variables

```bash
# Optional LLM Providers
OPENAI_API_KEY=sk-your-openai-key-here
OLLAMA_HOST=http://localhost:11434

# Development
NODE_ENV=development
LOG_LEVEL=debug
BMAD_DEBUG=true
```

## Credential Security

### Development Environment

1. **Local Development**
   - Use `.env` file in project root
   - Never commit `.env` to version control
   - Use `.env.example` as template

2. **Environment Isolation**
   - Separate keys for development/staging/production
   - Use different API accounts when possible
   - Implement key rotation schedule

### Production Environment

1. **Environment Variable Injection**
   - Use container orchestration secrets
   - Implement secure key management (AWS Secrets Manager, etc.)
   - Never store secrets in container images

2. **Access Controls**
   - Principle of least privilege
   - Regular access reviews
   - Audit logging for key usage

### Security Best Practices

1. **Key Management**
   - Rotate keys quarterly
   - Monitor for unusual usage patterns
   - Implement automated alerts
   - Maintain key inventory

2. **Incident Response**
   - Have key revocation process documented
   - Monitor for key exposure in logs/code
   - Implement breach notification procedures
   - Regular security audits

3. **Development Guidelines**
   - Never log API keys
   - Use masked values in debugging
   - Implement rate limiting
   - Add timeout configurations

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API key format and validity
   - Check account billing status
   - Ensure proper environment variable loading

2. **Rate Limiting**
   - Monitor usage against limits
   - Implement exponential backoff
   - Consider upgrading plan or using multiple keys

3. **Network Issues**
   - Check firewall configurations
   - Verify DNS resolution
   - Test connectivity with curl/ping

### Support Resources

- **Claude API**: [docs.anthropic.com](https://docs.anthropic.com)
- **OpenAI API**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **OLLAMA**: [ollama.ai/docs](https://ollama.ai/docs)

### Monitoring and Alerts

1. **Usage Monitoring**
   ```bash
   # Example monitoring script
   curl -H "Authorization: Bearer $CLAUDE_API_KEY" \
        https://api.anthropic.com/v1/usage
   ```

2. **Alert Configuration**
   - Set up billing alerts
   - Monitor for failed requests
   - Track response times
   - Log error patterns

---

For additional support, create an issue in the repository or consult the official documentation for each service.