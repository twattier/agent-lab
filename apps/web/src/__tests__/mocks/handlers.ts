import { http, HttpResponse } from 'msw'

const API_BASE_URL = 'http://localhost:8001/api/v1'

export const handlers = [
  // Health check endpoint
  http.get(`${API_BASE_URL}/health`, () => {
    return HttpResponse.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
    })
  }),

  // Clients endpoints
  http.get(`${API_BASE_URL}/clients`, () => {
    return HttpResponse.json([
      {
        id: '1',
        name: 'Test Client',
        businessDomain: 'Technology',
        services: [],
      },
    ])
  }),

  http.post(`${API_BASE_URL}/clients`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json(
      {
        id: '2',
        ...body,
      },
      { status: 201 }
    )
  }),
]
