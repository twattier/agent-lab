import { http, HttpResponse } from 'msw';
import type { Client } from '@/types/api';

const API_BASE_URL = 'http://localhost:8001/api/v1';

interface CreateClientRequest {
  name: string;
  businessDomain: string;
}

interface HealthResponse {
  status: string;
  timestamp: string;
}

export const handlers = [
  // Health check endpoint
  http.get(`${API_BASE_URL}/health`, () => {
    const response: HealthResponse = {
      status: 'ok',
      timestamp: new Date().toISOString(),
    };
    return HttpResponse.json(response);
  }),

  // Clients endpoints
  http.get(`${API_BASE_URL}/clients`, () => {
    const clients: Client[] = [
      {
        id: '1',
        name: 'Test Client',
        businessDomain: 'Technology',
        services: [],
      },
    ];
    return HttpResponse.json(clients);
  }),

  http.post(`${API_BASE_URL}/clients`, async ({ request }) => {
    const body = (await request.json()) as CreateClientRequest;
    const newClient: Client = {
      id: '2',
      name: body.name,
      businessDomain: body.businessDomain,
      services: [],
    };
    return HttpResponse.json(newClient, { status: 201 });
  }),
];
