'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'

export default function ApiTestPage() {
  const [healthStatus, setHealthStatus] = useState<string>('Not tested')
  const [clients, setClients] = useState<string>('Not fetched')
  const [error, setError] = useState<string>('')

  const testHealth = async () => {
    try {
      setError('')
      const response = await apiClient.get('/health')
      setHealthStatus(JSON.stringify(response, null, 2))
    } catch (err) {
      setError((err as Error).message || 'Health check failed')
      setHealthStatus('Failed')
    }
  }

  const testClients = async () => {
    try {
      setError('')
      const response = await apiClient.get('/clients')
      setClients(JSON.stringify(response, null, 2))
    } catch (err) {
      setError((err as Error).message || 'Clients fetch failed')
      setClients('Failed')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">API Integration Test</h1>
        <p className="text-muted-foreground">
          Test frontend-backend connectivity (Backend must be running on {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'})
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/15 p-4">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Health Check</CardTitle>
            <CardDescription>GET /api/v1/health</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button onClick={testHealth}>Test Health Endpoint</Button>
            <pre className="rounded-md bg-muted p-4 text-sm">
              {healthStatus}
            </pre>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Clients API</CardTitle>
            <CardDescription>GET /api/v1/clients</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button onClick={testClients}>Test Clients Endpoint</Button>
            <pre className="rounded-md bg-muted p-4 text-sm overflow-auto max-h-48">
              {clients}
            </pre>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Environment Variables</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium">API URL:</dt>
              <dd className="text-sm text-muted-foreground">{process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1 (default)'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium">App Name:</dt>
              <dd className="text-sm text-muted-foreground">{process.env.NEXT_PUBLIC_APP_NAME}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium">App Version:</dt>
              <dd className="text-sm text-muted-foreground">{process.env.NEXT_PUBLIC_APP_VERSION}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  )
}
