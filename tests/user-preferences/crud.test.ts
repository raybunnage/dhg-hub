import { describe, expect, it, beforeEach, afterEach, beforeAll } from '@jest/globals';
import { createClient, User } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import { resolve } from 'path';

const backendEnvPath = resolve(process.cwd(), 'backend', '.env');
dotenv.config({ path: backendEnvPath });

const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_KEY!
);

// Add this logging at the start of your test file to debug
console.log('SUPABASE_KEY:', process.env.SUPABASE_KEY?.substring(0, 10) + '...');
console.log('SUPABASE_URL:', process.env.SUPABASE_URL);

// First, let's test basic auth functionality
describe('Supabase Auth Tests', () => {
    it('should be able to access auth service', async () => {
        const { data, error } = await supabase.auth.getSession();
        expect(error).toBeNull();
        console.log('Auth service response:', data);
    });

    it('should be able to sign up a test user', async () => {
        const testEmail = `test-${Date.now()}@example.com`;
        
        // First, check if email auth is enabled
        const { data: settings, error: settingsError } = await supabase
            .from('auth.config')
            .select('*')
            .single();
        
        console.log('Auth settings:', settings);
        console.log('Auth settings error:', settingsError);

        const { data, error } = await supabase.auth.signUp({
            email: testEmail,
            password: 'test123456'
        });

        if (error) {
            console.error('SignUp error:', {
                message: error.message,
                status: error.status,
                name: error.name
            });
        }

        expect(error).toBeNull();
        expect(data.user).toBeTruthy();
        console.log('Signup response:', {
            user: data.user ? {
                id: data.user.id,
                email: data.user.email,
                created_at: data.user.created_at
            } : null,
            session: data.session ? 'Present' : 'None'
        });
    });
});

// Only run the main tests if auth is working
describe('Profile Preferences', () => {
    let testUser: User | null = null;

    beforeEach(async () => {
        const testEmail = `test-${Date.now()}@example.com`;
        console.log('\nCreating test user:', testEmail);

        const { data, error } = await supabase.auth.signUp({
            email: testEmail,
            password: 'test123456'
        });

        if (error) {
            console.error('Failed to create test user:', error);
            throw error;
        }

        testUser = data.user;
        console.log('Test user created:', testUser?.id);
    });

    it('should create a default profile', async () => {
        expect(testUser).toBeTruthy();
        
        const { data, error } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', testUser!.id)
            .single();

        expect(error).toBeNull();
        expect(data).toBeTruthy();
    });

    // ... rest of your tests ...
}); 