# External APIs

## Claude Code MCP Integration

AgentLab integrates with Claude Code through the Model Context Protocol (MCP) for bidirectional file synchronization and context sharing. This integration enables seamless workflow between project qualification and development environments.

### MCP Protocol Implementation Details

#### Connection Management
- Persistent WebSocket connection to Claude Code MCP server
- Automatic reconnection with exponential backoff
- Connection health monitoring and status reporting
- Graceful degradation when Claude Code is unavailable

#### File Synchronization
- Real-time bidirectional file sync between AgentLab and Claude Code
- Conflict detection and resolution strategies
- Change detection using content hashing
- Selective sync based on file patterns and project configuration

#### Context Sharing
- Project metadata synchronization
- Workflow state communication
- Document version tracking
- Feedback and validation result writing

### File Conflict Resolution
- **Last Writer Wins:** Default strategy for non-critical files
- **Manual Resolution:** Interactive conflict resolution for important documents
- **Version Branching:** Create separate versions when conflicts cannot be auto-resolved
- **Backup Strategy:** Automatic backups before any destructive operations

## LLM Provider APIs (Multiple Options)

AgentLab supports multiple LLM providers through a unified abstraction layer, enabling flexibility in AI service selection based on requirements and budget constraints.

### Supported Providers
- **OpenAI API:** GPT-4, GPT-3.5-turbo with function calling support
- **Anthropic Claude:** Claude-3, Claude-3.5 with constitutional AI capabilities
- **OLLAMA:** Local LLM deployment for fully self-hosted solutions
- **OpenAI-Compatible APIs:** Any service implementing OpenAI API specification

### Provider Configuration
```typescript
interface LLMConfig {
  provider: 'openai' | 'anthropic' | 'ollama' | 'custom';
  apiKey?: string;
  baseUrl?: string;
  model: string;
  maxTokens: number;
  temperature: number;
}
```

## Bilingual Content Architecture

### Language Detection and Management
AgentLab automatically detects document language and provides appropriate handling for French business requirements and English technical documentation.

#### Features
- Automatic language detection using content analysis
- Seamless switching between French and English interfaces
- Document categorization by language and content type
- Translation assistance integration (optional)

### Frontend Language Switching
```typescript
interface LanguageContext {
  currentLanguage: 'fr' | 'en';
  switchLanguage: (lang: 'fr' | 'en') => void;
  documentLanguage: 'fr' | 'en';
  interfaceLanguage: 'fr' | 'en';
}
```

---
[← Back to Components](components.md) | [Architecture Index](index.md) | [Next: Core Workflows →](core-workflows.md)