CREATE TABLE public.user_preferences (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    theme_mode text NOT NULL DEFAULT 'light',
    notification_settings jsonb NOT NULL DEFAULT '{
        "email": {
            "marketing": true,
            "security": true,
            "updates": true
        },
        "push": {
            "mentions": true,
            "comments": true,
            "updates": true
        }
    }'::jsonb,
    settings jsonb NOT NULL DEFAULT '{
        "language": "en",
        "timezone": "UTC",
        "date_format": "YYYY-MM-DD"
    }'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT valid_theme_mode CHECK (theme_mode IN ('light', 'dark', 'system')),
    CONSTRAINT user_preferences_user_id_unique UNIQUE (user_id)
);

-- Index for faster lookups
CREATE INDEX user_preferences_user_id_idx ON public.user_preferences(user_id); 