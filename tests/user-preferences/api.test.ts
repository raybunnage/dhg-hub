import { describe, expect, it, beforeEach, afterEach } from '@jest/globals';
import { createClient, User } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || 'http://localhost:54321';
const supabaseKey = process.env.SUPABASE_ANON_KEY || 'your-default-anon-key';

const supabase = createClient(supabaseUrl, supabaseKey);

describe('Profile Preferences API', () => {
  let testUser: User | null = null;
  let accessToken: string | null = null;

  beforeEach(async () => {
    // Create and sign in test user
    const { data: { user, session }, error } = await supabase.auth.signUp({
      email: `test-${Date.now()}@example.com`,
      password: 'test123456'
    });
    if (error) throw error;
    testUser = user;
    accessToken = session?.access_token ?? null;
  });

  afterEach(async () => {
    if (testUser?.id) {
      await supabase.from('profiles').delete().eq('id', testUser.id);
      await supabase.auth.admin.deleteUser(testUser.id);
    }
  });

  describe('GET /api/profile', () => {
    it('should return profile with preferences when authenticated', async () => {
      if (!testUser || !accessToken) throw new Error('Test setup failed');

      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', testUser.id)
        .single();

      expect(error).toBeNull();
      expect(data).toMatchObject({
        id: testUser.id,
        theme_mode: 'light'
      });
    });

    it('should return 401 when not authenticated', async () => {
      // Create a new supabase client without auth
      const anonClient = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!);
      
      const { data, error } = await anonClient
        .from('profiles')
        .select('*')
        .eq('id', testUser?.id)
        .single();

      expect(error).not.toBeNull();
      expect(error?.message).toContain('authentication');
    });
  });

  describe('PATCH /api/profile', () => {
    it('should update profile preferences when authenticated', async () => {
      if (!testUser || !accessToken) throw new Error('Test setup failed');

      const updates = {
        theme_mode: 'dark',
        settings: {
          language: 'fr',
          timezone: 'Europe/Paris'
        }
      };

      const { error: updateError } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', testUser.id);

      expect(updateError).toBeNull();

      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', testUser.id)
        .single();

      expect(error).toBeNull();
      expect(data).toMatchObject(updates);
    });

    it('should return 401 when not authenticated', async () => {
      const anonClient = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!);
      
      const { error } = await anonClient
        .from('profiles')
        .update({ theme_mode: 'dark' })
        .eq('id', testUser?.id);

      expect(error).not.toBeNull();
      expect(error?.message).toContain('authentication');
    });
  });
}); 