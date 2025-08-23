import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string;

// Check if Supabase is properly configured
const isSupabaseConfigured = supabaseUrl && supabaseAnonKey && 
  supabaseUrl !== 'disabled-for-local-deployment' && 
  supabaseAnonKey !== 'disabled-for-local-deployment';

if (!isSupabaseConfigured) {
  // eslint-disable-next-line no-console
  console.warn("Supabase is disabled or not properly configured");
}

// Create a dummy client for non-configured environments
export const supabase = isSupabaseConfigured 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : createClient('https://placeholder.supabase.co', 'placeholder-key');
