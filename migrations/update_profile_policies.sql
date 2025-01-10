-- Assuming you already have basic profile policies, 
-- you might want to add or modify them for the new fields

-- Example policy if you need specific control over preference fields
CREATE POLICY "Users can update their own preferences"
    ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (
        auth.uid() = id
        AND (
            CASE WHEN theme_mode IS NOT NULL 
                THEN theme_mode IN ('light', 'dark', 'system')
            ELSE TRUE
            END
        )
    ); 