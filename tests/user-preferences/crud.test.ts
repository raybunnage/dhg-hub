import { describe, expect, it, beforeEach, afterEach, beforeAll } from '@jest/globals';
import { createClient, User } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import { resolve } from 'path';

// Explicitly use backend .env
const backendEnvPath = resolve(process.cwd(), 'backend', '.env');
console.log('\n=== Environment Setup ===');
console.log('Loading .env from:', backendEnvPath);

// Only load the backend .env
dotenv.config({ path: backendEnvPath });

// Debug output
console.log('\nEnvironment Variables from backend/.env:');
console.log('SUPABASE_URL:', process.env.SUPABASE_URL ? '✓ Set' : '✗ Missing');
console.log('SUPABASE_ANON_KEY:', process.env.SUPABASE_KEY ? '✓ Set' : '✗ Missing');

if (!process.env.SUPABASE_URL || !process.env.SUPABASE_KEY) {
    console.error('\nError: Environment variables not found in backend/.env');
    throw new Error('Missing required environment variables in backend/.env');
}

// Create client with backend credentials
const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_KEY
);

// Add debug logging
console.log('Attempting to connect to:', process.env.SUPABASE_URL);

// Add more detailed logging
console.log('Environment check:');
console.log('- SUPABASE_URL:', process.env.SUPABASE_URL ? '✓ Set' : '✗ Missing');
console.log('- SUPABASE_ANON_KEY:', process.env.SUPABASE_KEY ? '✓ Set' : '✗ Missing');

// Add key format verification
const anonKey = process.env.SUPABASE_ANON_KEY || '';
console.log('API Key format check:');
console.log('- Starts with "eyJ":', anonKey.startsWith('eyJ') ? '✓' : '✗');
console.log('- Length > 100:', anonKey.length > 100 ? '✓' : '✗');

// Test the connection before running tests
beforeAll(async () => {
  try {
    const { data, error } = await supabase.from('profiles').select('count').limit(1);
    if (error) throw error;
    console.log('Successfully connected to Supabase');
  } catch (error) {
    console.error('Failed to connect to Supabase:', error);
    throw error;
  }
});

describe('Profile Preferences', () => {
  let testUser: User | null = null;

  beforeEach(async () => {
    // Creates a unique test user before each test
    const { data: { user }, error } = await supabase.auth.signUp({
      email: `test-${Date.now()}@example.com`,
      password: 'test123456'
    });
    if (error) throw error;
    testUser = user;
  });

  afterEach(async () => {
    // Cleanup: Deletes test user and their profile after each test
    if (testUser?.id) {
      await supabase.from('profiles').delete().eq('id', testUser.id);
      await supabase.auth.admin.deleteUser(testUser.id);
    }
  });

  describe('Default Profile', () => {
    it('should create profile with default preferences for new user', async () => {
      if (!testUser) throw new Error('Test user not created');
      
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', testUser.id)
        .single();

      expect(error).toBeNull();
      expect(data).toMatchObject({
        id: testUser.id,
        theme_mode: 'light',
        notification_settings: {
          email: {
            marketing: true,
            security: true,
            updates: true
          },
          push: {
            mentions: true,
            comments: true,
            updates: true
          }
        },
        settings: {
          language: 'en',
          timezone: 'UTC',
          date_format: 'YYYY-MM-DD'
        }
      });
    });
  });

  describe('Theme Preferences', () => {
    it('should update theme mode', async () => {
      if (!testUser) throw new Error('Test user not created');

      const { error: updateError } = await supabase
        .from('profiles')
        .update({ theme_mode: 'dark' })
        .eq('id', testUser.id);

      expect(updateError).toBeNull();

      const { data, error } = await supabase
        .from('profiles')
        .select('theme_mode')
        .eq('id', testUser.id)
        .single();

      expect(error).toBeNull();
      expect(data?.theme_mode).toBe('dark');
    });

    it('should reject invalid theme mode', async () => {
      if (!testUser) throw new Error('Test user not created');

      const { error } = await supabase
        .from('profiles')
        .update({ theme_mode: 'invalid_theme' })
        .eq('id', testUser.id);

      expect(error).not.toBeNull();
      expect(error?.message).toContain('valid_theme_mode');
    });
  });

  describe('Notification Settings', () => {
    it('should update notification preferences', async () => {
      if (!testUser) throw new Error('Test user not created');

      const newNotificationSettings = {
        email: {
          marketing: false,
          security: true,
          updates: false
        },
        push: {
          mentions: true,
          comments: false,
          updates: true
        }
      };

      const { error: updateError } = await supabase
        .from('profiles')
        .update({ notification_settings: newNotificationSettings })
        .eq('id', testUser.id);

      expect(updateError).toBeNull();

      const { data, error } = await supabase
        .from('profiles')
        .select('notification_settings')
        .eq('id', testUser.id)
        .single();

      expect(error).toBeNull();
      expect(data?.notification_settings).toMatchObject(newNotificationSettings);
    });
  });

  describe('User Settings', () => {
    it('should update user settings', async () => {
      if (!testUser) throw new Error('Test user not created');

      const newSettings = {
        language: 'es',
        timezone: 'Europe/London',
        date_format: 'DD/MM/YYYY'
      };

      const { error: updateError } = await supabase
        .from('profiles')
        .update({ settings: newSettings })
        .eq('id', testUser.id);

      expect(updateError).toBeNull();

      const { data, error } = await supabase
        .from('profiles')
        .select('settings')
        .eq('id', testUser.id)
        .single();

      expect(error).toBeNull();
      expect(data?.settings).toMatchObject(newSettings);
    });
  });
}); 