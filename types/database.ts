export interface Profile {
  id: string
  avatar_url?: string | null
  display_name?: string | null
  email?: string | null
  preferred_domain_id?: string | null
  theme_mode: 'light' | 'dark' | 'system'
  notification_settings: {
    email: {
      marketing: boolean
      security: boolean
      updates: boolean
    }
    push: {
      mentions: boolean
      comments: boolean
      updates: boolean
    }
  }
  settings: {
    language: string
    timezone: string
    date_format: string
  }
} 