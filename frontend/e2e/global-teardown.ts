import { chromium, FullConfig } from '@playwright/test'

async function globalTeardown(config: FullConfig) {
    const browser = await chromium.launch()
    const page = await browser.newPage()

    // Clean up test data or environment
    console.log('Cleaning up test environment...')

    // You can add cleanup logic here such as:
    // - Removing test users
    // - Cleaning up test database
    // - Resetting test environment variables
    // - Stopping mock services

    // Example: Clean up test user if needed
    try {
        // Login as test user
        await page.goto('http://localhost:3000/auth/login')
        await page.fill('[name="email"]', 'demo@curagenie.com')
        await page.fill('[name="password"]', 'demo123')
        await page.click('button[type="submit"]')

        // Wait for login
        await page.waitForURL('/dashboard', { timeout: 10000 })

        // Navigate to settings/delete account
        await page.goto('http://localhost:3000/dashboard/settings/delete-account')

        // Delete account
        await page.fill('[name="confirmation"]', 'DELETE')
        await page.click('button:has-text("Delete Account")')

        // Confirm deletion
        await page.click('button:has-text("Confirm")')

        console.log('Test user cleaned up successfully')
    } catch (error) {
        console.log('Test user cleanup failed or not needed:', error.message)
    }

    await browser.close()
}

export default globalTeardown
