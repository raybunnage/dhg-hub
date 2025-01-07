import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function TestConnection() {
  console.log('TestConnection component rendering');
  const [status, setStatus] = useState<string>('Loading...');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await api.get('/health');
        setStatus(response.data.message);
      } catch (err) {
        setError('Failed to connect to backend');
        console.error(err);
      }
    };

    checkConnection();
  }, []);

  return (
    <div>
      <h2>Backend Connection Test</h2>
      {error ? (
        <p style={{ color: 'red' }}>{error}</p>
      ) : (
        <p style={{ color: 'green' }}>{status}</p>
      )}
    </div>
  );
} 