# Frontend Architecture

## Component Architecture

### Component Organization
The frontend follows a hierarchical component structure with clear separation of concerns:

```
apps/web/src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui base components
│   ├── forms/          # Form components with validation
│   ├── charts/         # Data visualization components
│   ├── contacts/       # Contact management components
│   ├── categories/     # Category selection and management
│   └── layout/         # Layout and navigation components
├── app/                # Next.js App Router pages
│   ├── dashboard/      # Portfolio dashboard
│   ├── projects/       # Project management
│   ├── clients/        # Client management
│   ├── contacts/       # Contact management
│   └── settings/       # Application settings
├── lib/                # Utility functions and configurations
├── hooks/              # Custom React hooks
├── store/              # Zustand state management
├── services/           # API service layer
└── types/              # TypeScript type definitions
```

### Component Template
```typescript
interface ComponentProps {
  // Define props with TypeScript
}

export function Component({ ...props }: ComponentProps) {
  // Component logic
  return (
    <div className="component-wrapper">
      {/* JSX content */}
    </div>
  );
}
```

## State Management Architecture

### State Structure
The application uses a hybrid approach combining React Query for server state and Zustand for client state:

#### Server State (React Query)
- **Projects:** Project data, workflow states, and CRUD operations
- **Clients/Services:** Hierarchical client data management
- **Documents:** Document content, versions, and change tracking
- **Workflow Events:** Real-time workflow progression tracking

#### Client State (Zustand)
- **UI State:** Modal visibility, sidebar state, theme preferences
- **User Preferences:** Language settings, dashboard layout
- **Navigation:** Current route, breadcrumb state
- **Agent Interface:** Conversation state, context management

### State Management Patterns
```typescript
// Zustand store example
interface AppState {
  sidebarOpen: boolean;
  currentLanguage: 'en' | 'fr';
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setLanguage: (lang: 'en' | 'fr') => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  currentLanguage: 'en',
  theme: 'light',
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setLanguage: (lang) => set({ currentLanguage: lang }),
}));
```

## Routing Architecture

### Route Organization
Next.js App Router with file-based routing and layout hierarchy:

```
app/
├── layout.tsx              # Root layout with auth
├── page.tsx               # Dashboard homepage
├── dashboard/
│   ├── layout.tsx         # Dashboard layout
│   ├── page.tsx          # Portfolio overview
│   └── projects/
│       ├── page.tsx      # Project list
│       └── [id]/
│           ├── page.tsx  # Project detail
│           └── edit/
│               └── page.tsx # Project editing
├── clients/
│   ├── page.tsx          # Client management
│   └── [id]/
│       └── services/
│           └── page.tsx  # Service management
└── settings/
    └── page.tsx          # Application settings
```

### Protected Route Pattern
```typescript
// middleware.ts - Route protection
export function middleware(request: NextRequest) {
  const token = request.cookies.get('next-auth.session-token');

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/auth/signin', request.url));
  }
}
```

## Frontend Services Layer

### API Client Setup
```typescript
// lib/api-client.ts
class ApiClient {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new ApiError(response);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
```

### Service Examples

```typescript
// services/contact-service.ts
export const contactService = {
  getContacts: (filters?: ContactFilters): Promise<PaginatedResponse<Contact>> =>
    apiClient.request('/contacts', {
      method: 'GET',
      params: filters
    }),

  createContact: (contact: CreateContactRequest): Promise<Contact> =>
    apiClient.request('/contacts', {
      method: 'POST',
      body: JSON.stringify(contact)
    }),

  updateContact: (id: string, updates: UpdateContactRequest): Promise<Contact> =>
    apiClient.request(`/contacts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    }),

  getContactServices: (contactId: string): Promise<ServiceContact[]> =>
    apiClient.request(`/contacts/${contactId}/services`),

  getContactProjects: (contactId: string): Promise<ProjectContact[]> =>
    apiClient.request(`/contacts/${contactId}/projects`),
};

// services/project-service.ts
export const projectService = {
  getProjects: (filters?: ProjectFilters): Promise<PaginatedResponse<Project>> =>
    apiClient.request('/projects', {
      method: 'GET',
      params: filters
    }),

  createProject: (project: CreateProjectRequest): Promise<Project> =>
    apiClient.request('/projects', {
      method: 'POST',
      body: JSON.stringify(project)
    }),

  updateProject: (id: string, updates: UpdateProjectRequest): Promise<Project> =>
    apiClient.request(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    }),

  // Contact management
  getProjectContacts: (projectId: string): Promise<ProjectContact[]> =>
    apiClient.request(`/projects/${projectId}/contacts`),

  assignContactToProject: (projectId: string, assignment: ProjectContactAssignment): Promise<ProjectContact> =>
    apiClient.request(`/projects/${projectId}/contacts`, {
      method: 'POST',
      body: JSON.stringify(assignment)
    }),

  updateProjectContact: (projectId: string, contactId: string, updates: ProjectContactUpdate): Promise<ProjectContact> =>
    apiClient.request(`/projects/${projectId}/contacts/${contactId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    }),

  // User category management
  getProjectUserCategories: (projectId: string): Promise<ProjectServiceCategory[]> =>
    apiClient.request(`/projects/${projectId}/user-categories`),

  assignUserCategoryToProject: (projectId: string, categoryId: string): Promise<ProjectServiceCategory> =>
    apiClient.request(`/projects/${projectId}/user-categories`, {
      method: 'POST',
      body: JSON.stringify({ categoryId })
    }),
};

// services/service-service.ts
export const serviceService = {
  getServices: (clientId?: string): Promise<Service[]> =>
    apiClient.request(clientId ? `/clients/${clientId}/services` : '/services'),

  createService: (clientId: string, service: CreateServiceRequest): Promise<Service> =>
    apiClient.request(`/clients/${clientId}/services`, {
      method: 'POST',
      body: JSON.stringify(service)
    }),

  // Contact management
  getServiceContacts: (serviceId: string): Promise<ServiceContact[]> =>
    apiClient.request(`/services/${serviceId}/contacts`),

  assignContactToService: (serviceId: string, assignment: ServiceContactAssignment): Promise<ServiceContact> =>
    apiClient.request(`/services/${serviceId}/contacts`, {
      method: 'POST',
      body: JSON.stringify(assignment)
    }),

  // Category management
  getServiceCategories: (serviceId: string): Promise<ServiceServiceCategory[]> =>
    apiClient.request(`/services/${serviceId}/categories`),

  assignCategoryToService: (serviceId: string, categoryId: string): Promise<ServiceServiceCategory> =>
    apiClient.request(`/services/${serviceId}/categories`, {
      method: 'POST',
      body: JSON.stringify({ categoryId })
    }),
};

// services/reference-data-service.ts
export const referenceDataService = {
  getServiceCategories: (): Promise<ServiceCategory[]> =>
    apiClient.request('/service-categories'),

  getImplementationTypes: (): Promise<ImplementationType[]> =>
    apiClient.request('/implementation-types'),

  createServiceCategory: (category: CreateServiceCategoryRequest): Promise<ServiceCategory> =>
    apiClient.request('/service-categories', {
      method: 'POST',
      body: JSON.stringify(category)
    }),

  createImplementationType: (type: CreateImplementationTypeRequest): Promise<ImplementationType> =>
    apiClient.request('/implementation-types', {
      method: 'POST',
      body: JSON.stringify(type)
    }),
};
```

---
[← Back to Database Schema](database-schema.md) | [Architecture Index](index.md) | [Next: Backend Architecture →](backend-architecture.md)