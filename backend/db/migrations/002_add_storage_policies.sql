-- =============================================================
-- Storage Policies for 'injury-images' Bucket
-- =============================================================

-- Ensure the 'injury-images' bucket exists (idempotent insert)
INSERT INTO storage.buckets (id, name, public)
VALUES ('injury-images', 'injury-images', false)
ON CONFLICT (id) DO NOTHING;

-- 1. Allow Uploads (INSERT)
-- User can only upload to folder matching their user_id
-- Path: {user_id}/{assessment_id}/{filename}
CREATE POLICY "Allow user uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'injury-images' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- 2. Allow Reads (SELECT)
-- User can view their own files
CREATE POLICY "Allow user downloads"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'injury-images' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- 3. Allow Deletes (DELETE)
-- User can delete their own files (e.g. if we add delete functionality later)
CREATE POLICY "Allow user deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'injury-images' AND
    (storage.foldername(name))[1] = auth.uid()::text
);
