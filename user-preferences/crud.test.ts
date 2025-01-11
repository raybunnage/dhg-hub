import * as dotenv from 'dotenv';
import { resolve } from 'path';
const backendEnvPath = resolve(process.cwd(), 'backend', '.env');
dotenv.config({ path: backendEnvPath });

// Separated auth tests
describe('Supabase Auth Tests', () => {
    // Verifies auth service is working
    it('should be able to access auth service', async () => {
        // ... auth verification ...
    });

    // More comprehensive signup test
    it('should be able to sign up a test user', async () => {
        // Checks auth config first
        const { data: settings } = await supabase
            .from('auth.config')
            .select('*')
            .single();
        
        // Better error logging
        // ... rest of signup test ...
    });
}); 