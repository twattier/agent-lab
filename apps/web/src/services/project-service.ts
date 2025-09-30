import { apiClient } from '@/lib/api-client';
import type { Project } from '@/types/api';

export interface CreateProjectDto {
  name: string;
  description: string;
  serviceId: string;
  projectType: string;
  status: string;
}

export interface UpdateProjectDto {
  name?: string;
  description?: string;
  projectType?: string;
  status?: string;
  workflowState?: unknown;
}

/**
 * Service for managing project resources
 */
export const projectService = {
  /**
   * Fetch all projects from the API
   * @returns Promise resolving to an array of projects
   */
  async getProjects(): Promise<Project[]> {
    return apiClient.get<Project[]>('/projects');
  },

  /**
   * Fetch projects by service ID
   * @param serviceId - The service ID to filter projects
   * @returns Promise resolving to an array of projects
   */
  async getProjectsByService(serviceId: string): Promise<Project[]> {
    return apiClient.get<Project[]>(`/services/${serviceId}/projects`);
  },

  /**
   * Fetch a single project by ID
   * @param id - The project ID
   * @returns Promise resolving to the project
   */
  async getProject(id: string): Promise<Project> {
    return apiClient.get<Project>(`/projects/${id}`);
  },

  /**
   * Create a new project
   * @param data - The project data to create
   * @returns Promise resolving to the created project
   */
  async createProject(data: CreateProjectDto): Promise<Project> {
    return apiClient.post<Project>('/projects', data);
  },

  /**
   * Update an existing project
   * @param id - The project ID to update
   * @param data - The partial project data to update
   * @returns Promise resolving to the updated project
   */
  async updateProject(id: string, data: UpdateProjectDto): Promise<Project> {
    return apiClient.put<Project>(`/projects/${id}`, data);
  },

  /**
   * Delete a project by ID
   * @param id - The project ID to delete
   * @returns Promise resolving when deletion is complete
   */
  async deleteProject(id: string): Promise<void> {
    return apiClient.delete<void>(`/projects/${id}`);
  },

  /**
   * Update project workflow state
   * @param id - The project ID
   * @param workflowState - The new workflow state
   * @returns Promise resolving to the updated project
   */
  async updateWorkflowState(
    id: string,
    workflowState: unknown
  ): Promise<Project> {
    return apiClient.put<Project>(`/projects/${id}/workflow`, {
      workflowState,
    });
  },
};
