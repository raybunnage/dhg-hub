ALTER TABLE public.profiles 
ADD COLUMN theme_mode text NOT NULL DEFAULT 'light',
ADD COLUMN notification_settings jsonb NOT NULL DEFAULT '{
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
ADD COLUMN settings jsonb NOT NULL DEFAULT '{
    "language": "en",
    "timezone": "UTC",
    "date_format": "YYYY-MM-DD"
}'::jsonb,
ADD CONSTRAINT valid_theme_mode CHECK (theme_mode IN ('light', 'dark', 'system')); 