import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

export function HealthCheck() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await api.get('/health')
      return response.data
    },
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {(error as Error).message}</div>

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-lg font-semibold">API Status</h2>
      <pre className="mt-2">{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
} 