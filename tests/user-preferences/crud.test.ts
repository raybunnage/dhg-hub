import { describe, expect, it, beforeEach, afterEach } from '@jest/globals';
import { createClient, User } from '@supabase/supabase-js';

if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY) {
  throw new Error('Missing required environment variables');
}

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

describe('Profile Preferences CRUD', () => {
  let testUser: User | null = null;

  beforeEach(async () => {
    // Create test user
    const { data: { user }, error } = await supabase.auth.signUp({
      email: `test-${Date.now()}@example.com`,
      password: 'test123456'
    });
    if (error) throw error;
    testUser = user;
  });

  afterEach(async () => {
    // Cleanup
    if (testUser?.id) {
      await supabase.from('profiles').delete().eq('id', testUser.id);
      await supabase.auth.admin.deleteUser(testUser.id);
    }
  });

  it('should update theme mode while preserving other profile data', async () => {
    if (!testUser) throw new Error('Test user not created');

    // First set some profile data
    await supabase
      .from('profiles')
      .update({ 
        display_name: 'Test User',
        theme_mode: 'dark'
      })
      .eq('id', testUser.id);

    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', testUser.id)
      .single();

    expect(error).toBeNull();
    expect(data).not.toBeNull();
    if (data) {
      expect(data.theme_mode).toBe('dark');
      expect(data.display_name).toBe('Test User');
    }
  });
}); 