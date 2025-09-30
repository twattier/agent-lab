import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  clientService,
  type CreateClientDto,
  type UpdateClientDto,
} from '@/services/client-service';
import {
  projectService,
  type CreateProjectDto,
  type UpdateProjectDto,
} from '@/services/project-service';
import type { Client, Project } from '@/types/api';

/**
 * Query keys for React Query cache management
 */
export const queryKeys = {
  clients: ['clients'] as const,
  client: (id: string) => ['clients', id] as const,
  projects: ['projects'] as const,
  project: (id: string) => ['projects', id] as const,
  projectsByService: (serviceId: string) =>
    ['projects', 'service', serviceId] as const,
};

// ============================================================================
// Client Hooks
// ============================================================================

/**
 * Hook to fetch all clients
 * @returns React Query result with clients array
 */
export function useClients() {
  return useQuery({
    queryKey: queryKeys.clients,
    queryFn: () => clientService.getClients(),
  });
}

/**
 * Hook to fetch a single client by ID
 * @param id - The client ID
 * @returns React Query result with client data
 */
export function useClient(id: string) {
  return useQuery({
    queryKey: queryKeys.client(id),
    queryFn: () => clientService.getClient(id),
    enabled: !!id,
  });
}

/**
 * Hook to create a new client
 * @returns React Query mutation for creating clients
 */
export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateClientDto) => clientService.createClient(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients });
    },
  });
}

/**
 * Hook to update an existing client
 * @returns React Query mutation for updating clients
 */
export function useUpdateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateClientDto }) =>
      clientService.updateClient(id, data),
    onSuccess: (updatedClient: Client) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients });
      queryClient.invalidateQueries({
        queryKey: queryKeys.client(updatedClient.id),
      });
    },
  });
}

/**
 * Hook to delete a client
 * @returns React Query mutation for deleting clients
 */
export function useDeleteClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => clientService.deleteClient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients });
    },
  });
}

// ============================================================================
// Project Hooks
// ============================================================================

/**
 * Hook to fetch all projects
 * @returns React Query result with projects array
 */
export function useProjects() {
  return useQuery({
    queryKey: queryKeys.projects,
    queryFn: () => projectService.getProjects(),
  });
}

/**
 * Hook to fetch projects by service ID
 * @param serviceId - The service ID to filter projects
 * @returns React Query result with filtered projects array
 */
export function useProjectsByService(serviceId: string) {
  return useQuery({
    queryKey: queryKeys.projectsByService(serviceId),
    queryFn: () => projectService.getProjectsByService(serviceId),
    enabled: !!serviceId,
  });
}

/**
 * Hook to fetch a single project by ID
 * @param id - The project ID
 * @returns React Query result with project data
 */
export function useProject(id: string) {
  return useQuery({
    queryKey: queryKeys.project(id),
    queryFn: () => projectService.getProject(id),
    enabled: !!id,
  });
}

/**
 * Hook to create a new project
 * @returns React Query mutation for creating projects
 */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProjectDto) => projectService.createProject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
}

/**
 * Hook to update an existing project
 * @returns React Query mutation for updating projects
 */
export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProjectDto }) =>
      projectService.updateProject(id, data),
    onSuccess: (updatedProject: Project) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
      queryClient.invalidateQueries({
        queryKey: queryKeys.project(updatedProject.id),
      });
    },
  });
}

/**
 * Hook to delete a project
 * @returns React Query mutation for deleting projects
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => projectService.deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
}

/**
 * Hook to update project workflow state
 * @returns React Query mutation for updating project workflow
 */
export function useUpdateProjectWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      workflowState,
    }: {
      id: string;
      workflowState: unknown;
    }) => projectService.updateWorkflowState(id, workflowState),
    onSuccess: (updatedProject: Project) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
      queryClient.invalidateQueries({
        queryKey: queryKeys.project(updatedProject.id),
      });
    },
  });
}
