import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './utils/queryClient'
import './styles/index.css'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-100">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4">
            <h1 className="text-3xl font-bold text-gray-900">
              Your Project Name
            </h1>
          </div>
        </header>
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Your content will go here */}
        </main>
      </div>
    </QueryClientProvider>
  )
}

export default App
