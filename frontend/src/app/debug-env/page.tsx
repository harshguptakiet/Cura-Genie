'use client'

export default function DebugEnvPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL
  
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Environment Debug</h1>
      
      <div className="space-y-4">
        <div className="p-4 border rounded">
          <h2 className="font-semibold">API URL</h2>
          <p className="text-sm text-gray-600">NEXT_PUBLIC_API_URL</p>
          <p className="font-mono bg-gray-100 p-2 rounded">{apiUrl || 'NOT SET'}</p>
        </div>
        
        <div className="p-4 border rounded">
          <h2 className="font-semibold">Expected Value</h2>
          <p className="font-mono bg-green-100 p-2 rounded">https://cura-genie-production.up.railway.app</p>
        </div>
        
        <div className="p-4 border rounded">
          <h2 className="font-semibold">Test Connection</h2>
          <button 
            onClick={async () => {
              try {
                const url = apiUrl || 'http://localhost:8000'
                const response = await fetch(`${url}/health`)
                const data = await response.json()
                alert(`Connected! Response: ${JSON.stringify(data, null, 2)}`)
              } catch (error) {
                alert(`Connection failed: ${error.message}`)
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Test API Connection
          </button>
        </div>
        
        <div className="p-4 border rounded">
          <h2 className="font-semibold">All Environment Variables</h2>
          <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto">
            {JSON.stringify(
              Object.fromEntries(
                Object.entries(process.env).filter(([key]) => key.startsWith('NEXT_PUBLIC_'))
              ), 
              null, 
              2
            )}
          </pre>
        </div>
      </div>
    </div>
  )
}
