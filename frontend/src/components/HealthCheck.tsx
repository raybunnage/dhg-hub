import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

export const HealthCheck = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await api.get('/api/v1/health')
      return response.data
    },
  })

  if (isLoading) return <div>Checking API connection...</div>
  if (error) return <div>Error: API is not responding</div>

  return <div>API Status: {data?.status}</div>
} 