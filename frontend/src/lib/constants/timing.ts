// Animation and timing constants
export const ANIMATION_DURATIONS = {
    SHORT: 300,
    MEDIUM: 1000,
    LONG: 3000,
    EXTRA_LONG: 5000,
} as const;

// Navigation delays
export const NAVIGATION_DELAYS = {
    SUCCESS_REDIRECT: 500,
    ERROR_REDIRECT: 1000,
} as const;

// Progress update intervals
export const PROGRESS_INTERVALS = {
    FAST: 500,
    NORMAL: 1000,
    SLOW: 2000,
} as const;

// File upload delays
export const UPLOAD_DELAYS = {
    MINIMUM: 100,
    STANDARD: 200,
    EXTENDED: 500,
} as const;
