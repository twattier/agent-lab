import { apiClient } from '@/lib/api-client';
import type { Client } from '@/types/api';

export interface CreateClientDto {
  name: string;
  businessDomain: string;
  services?: never[];
}

export interface UpdateClientDto {
  name?: string;
  businessDomain?: string;
}

/**
 * Service for managing client resources
 */
export const clientService = {
  /**
   * Fetch all clients from the API
   * @returns Promise resolving to an array of clients
   */
  async getClients(): Promise<Client[]> {
    return apiClient.get<Client[]>('/clients');
  },

  /**
   * Fetch a single client by ID
   * @param id - The client ID
   * @returns Promise resolving to the client
   */
  async getClient(id: string): Promise<Client> {
    return apiClient.get<Client>(`/clients/${id}`);
  },

  /**
   * Create a new client
   * @param data - The client data to create
   * @returns Promise resolving to the created client
   */
  async createClient(data: CreateClientDto): Promise<Client> {
    return apiClient.post<Client>('/clients', data);
  },

  /**
   * Update an existing client
   * @param id - The client ID to update
   * @param data - The partial client data to update
   * @returns Promise resolving to the updated client
   */
  async updateClient(id: string, data: UpdateClientDto): Promise<Client> {
    return apiClient.put<Client>(`/clients/${id}`, data);
  },

  /**
   * Delete a client by ID
   * @param id - The client ID to delete
   * @returns Promise resolving when deletion is complete
   */
  async deleteClient(id: string): Promise<void> {
    return apiClient.delete<void>(`/clients/${id}`);
  },
};
