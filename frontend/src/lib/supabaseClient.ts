import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Check if Supabase is properly configured
const isSupabaseConfigured = supabaseUrl && supabaseAnonKey &&
  supabaseUrl !== "https://your-project.supabase.co" &&
  supabaseAnonKey !== "your-anon-key-here";

if (!isSupabaseConfigured) {
  console.warn("Supabase not configured - file upload features will be disabled");
}

// Create client only if properly configured, otherwise create a mock client
export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey)
  : {
    storage: {
      from: () => ({
        uploadToSignedUrl: async () => ({ error: new Error("Supabase not configured") })
      })
    }
  } as any;

// Export configuration status
export const isSupabaseEnabled = isSupabaseConfigured;
