import { apiClient } from '@/lib/api-client'
import { Client } from '@/types/api'

export const clientService = {
  async getClients(): Promise<Client[]> {
    return apiClient.get<Client[]>('/clients')
  },

  async getClient(id: string): Promise<Client> {
    return apiClient.get<Client>(`/clients/${id}`)
  },

  async createClient(data: Omit<Client, 'id'>): Promise<Client> {
    return apiClient.post<Client>('/clients', data)
  },

  async updateClient(id: string, data: Partial<Client>): Promise<Client> {
    return apiClient.put<Client>(`/clients/${id}`, data)
  },

  async deleteClient(id: string): Promise<void> {
    return apiClient.delete<void>(`/clients/${id}`)
  },
}
