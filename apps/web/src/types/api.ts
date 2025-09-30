// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

export interface ApiError {
  message: string
  status: number
  errors?: Record<string, string[]>
}

// Core Entity Types (will be shared with backend via packages/types/)
export interface Client {
  id: string
  name: string
  businessDomain: string
  services?: Service[]
}

export interface Service {
  id: string
  name: string
  description: string
  clientId: string
  projects?: Project[]
}

export interface Project {
  id: string
  name: string
  description: string
  serviceId: string
  projectType: string
  status: string
  workflowState?: unknown
}
