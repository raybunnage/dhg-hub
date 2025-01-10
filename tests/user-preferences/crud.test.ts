import { describe, expect, it, beforeEach, afterEach } from '@jest/globals';
import { createClient, User } from '@supabase/supabase-js';

// More graceful handling of missing env vars
const supabaseUrl = process.env.SUPABASE_URL || 'http://localhost:54321';
const supabaseKey = process.env.SUPABASE_ANON_KEY || 'your-default-anon-key';

const supabase = createClient(supabaseUrl, supabaseKey);

describe('Profile Preferences', () => {
  let testUser: User | null = null;

  beforeEach(async () => {
    // Create a new test user before each test
    const { data: { user }, error } = await supabase.auth.signUp({
      email: `test-${Date.now()}@example.com`,
      password: 'test123456'
    });
    if (error) throw error;
    testUser = user;
  });

  afterEach(async () => {
    // Cleanup after each test
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