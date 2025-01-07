import { useState } from 'react';
import { api } from '../services/api';

export function TestButton() {
  console.log('TestButton component rendering');
  const [result, setResult] = useState<string>('');

  const testBackend = async () => {
    try {
      const response = await api.get('/health');
      setResult(`Success: ${JSON.stringify(response.data)}`);
    } catch (error) {
      setResult(`Error: ${error.message}`);
    }
  };

  return (
    <div>
      <button onClick={testBackend}>Test Backend Connection</button>
      {result && <pre>{result}</pre>}
    </div>
  );
} 