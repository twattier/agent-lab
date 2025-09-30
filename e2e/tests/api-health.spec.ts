import { test, expect } from '@playwright/test';

/**
 * E2E Test: API Health Check
 *
 * Verifies that the backend API health endpoint is accessible and returns
 * the expected response indicating the service is running.
 */
test.describe('API Health Check', () => {
  test('should return healthy status from /api/v1/health', async ({
    request,
  }) => {
    // Make a GET request to the health endpoint
    const response = await request.get('http://localhost:8001/api/v1/health');

    // Verify response status
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);

    // Parse and verify response body
    const body = await response.json();
    expect(body).toHaveProperty('status');
    expect(body.status).toBe('healthy');
  });

  test('should have correct response structure', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/health');
    const body = await response.json();

    // Verify expected fields exist
    expect(body).toHaveProperty('status');
    expect(body).toHaveProperty('database');
    expect(body.database).toMatch(/connected|disconnected/);
  });
});
