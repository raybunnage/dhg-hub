import { api } from '../services/api';

export const testBackendConnection = async () => {
  try {
    const response = await api.get('/health');
    console.log('Backend connection successful:', response.data);
    return true;
  } catch (error) {
    console.error('Backend connection failed:', error);
    return false;
  }
}; 