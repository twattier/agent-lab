# API Specification

## REST API Specification

The AgentLab API follows REST principles with OpenAPI 3.0 specification for comprehensive documentation and client SDK generation. All endpoints use JSON for request/response bodies and follow consistent naming conventions.

### Base Configuration
- **Base URL:** `http://localhost:8000/api/v1`
- **Authentication:** Bearer token via NextAuth.js
- **Content-Type:** `application/json`
- **API Documentation:** Available at `/docs` (Swagger UI) and `/redoc`

### Endpoint Categories

#### Client Management
- `GET /clients` - List all clients with pagination
- `POST /clients` - Create new client
- `GET /clients/{id}` - Get specific client details
- `PUT /clients/{id}` - Update client information
- `DELETE /clients/{id}` - Delete client (with confirmation)

#### Service Management
- `GET /clients/{clientId}/services` - List services for client
- `POST /clients/{clientId}/services` - Create new service
- `GET /services/{id}` - Get service details
- `PUT /services/{id}` - Update service
- `DELETE /services/{id}` - Delete service
- `GET /services/{id}/contacts` - List contacts for service
- `POST /services/{id}/contacts` - Assign contact to service
- `PUT /services/{id}/contacts/{contactId}` - Update service-contact relationship
- `DELETE /services/{id}/contacts/{contactId}` - Remove contact from service
- `GET /services/{id}/categories` - List service categories
- `POST /services/{id}/categories` - Assign category to service
- `DELETE /services/{id}/categories/{categoryId}` - Remove category from service

#### Contact Management
- `GET /contacts` - List all contacts with pagination and filtering
- `POST /contacts` - Create new contact
- `GET /contacts/{id}` - Get contact details
- `PUT /contacts/{id}` - Update contact information
- `DELETE /contacts/{id}` - Delete contact (with confirmation)
- `GET /contacts/{id}/services` - List services associated with contact
- `GET /contacts/{id}/projects` - List projects associated with contact

#### Service Categories
- `GET /service-categories` - List all service categories
- `POST /service-categories` - Create new service category
- `GET /service-categories/{id}` - Get service category details
- `PUT /service-categories/{id}` - Update service category
- `DELETE /service-categories/{id}` - Delete service category

#### Implementation Types
- `GET /implementation-types` - List all implementation types
- `POST /implementation-types` - Create new implementation type
- `GET /implementation-types/{id}` - Get implementation type details
- `PUT /implementation-types/{id}` - Update implementation type
- `DELETE /implementation-types/{id}` - Delete implementation type

#### Project Management
- `GET /projects` - List projects with filtering and pagination
- `POST /projects` - Create new project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project (with confirmation)
- `POST /projects/{id}/sync` - Trigger Claude Code synchronization
- `GET /projects/{id}/contacts` - List project contacts
- `POST /projects/{id}/contacts` - Assign contact to project
- `PUT /projects/{id}/contacts/{contactId}` - Update project-contact relationship
- `DELETE /projects/{id}/contacts/{contactId}` - Remove contact from project
- `GET /projects/{id}/user-categories` - List project user categories
- `POST /projects/{id}/user-categories` - Assign user category to project
- `DELETE /projects/{id}/user-categories/{categoryId}` - Remove user category from project

#### Document Management
- `GET /projects/{projectId}/documents` - List project documents
- `POST /projects/{projectId}/documents` - Create new document
- `GET /documents/{id}` - Get document content
- `PUT /documents/{id}` - Update document
- `GET /documents/{id}/versions` - Get document version history
- `POST /documents/{id}/comments` - Add comment to document

#### Workflow Management
- `GET /projects/{projectId}/workflow` - Get current workflow state
- `POST /projects/{projectId}/workflow/advance` - Advance workflow stage
- `POST /projects/{projectId}/workflow/approve` - Approve gate
- `POST /projects/{projectId}/workflow/reject` - Reject gate
- `GET /projects/{projectId}/workflow/history` - Get workflow event history

#### Agent Interface
- `POST /projects/{projectId}/chat` - Send message to project agent
- `GET /projects/{projectId}/chat/history` - Get conversation history
- `POST /projects/{projectId}/analyze` - Request project analysis

### Response Formats

#### Success Response
```typescript
interface ApiResponse<T> {
  data: T;
  message?: string;
  meta?: {
    pagination?: PaginationMeta;
    filters?: Record<string, any>;
  };
}
```

#### Error Response
```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  timestamp: string;
  path: string;
}
```

### Authentication & Authorization

All API endpoints require authentication via Bearer token obtained through NextAuth.js. The API implements role-based access control with the following roles:

- **Admin:** Full system access
- **Product Owner:** Project management and workflow control
- **Viewer:** Read-only access to assigned projects

---
[← Back to Data Models](data-models.md) | [Architecture Index](index.md) | [Next: Components →](components.md)