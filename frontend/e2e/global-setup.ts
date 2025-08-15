import { chromium, FullConfig } from '@playwright/test'

async function globalSetup(config: FullConfig) {
    const browser = await chromium.launch()
    const page = await browser.newPage()

    // Set up test data or environment
    console.log('Setting up test environment...')

    // You can add setup logic here such as:
    // - Creating test users
    // - Setting up test database
    // - Configuring test environment variables
    // - Setting up mock services

    // Example: Create test user if needed
    try {
        // Navigate to registration page
        await page.goto('http://localhost:3000/auth/register')

        // Fill registration form
        await page.fill('[name="email"]', 'demo@curagenie.com')
        await page.fill('[name="username"]', 'demo')
        await page.fill('[name="password"]', 'demo123')
        await page.fill('[name="confirm_password"]', 'demo123')
        await page.selectOption('[name="role"]', 'patient')

        // Submit registration
        await page.click('button[type="submit"]')

        // Wait for successful registration
        await page.waitForURL('/dashboard', { timeout: 10000 })

        console.log('Test user created successfully')
    } catch (error) {
        console.log('Test user may already exist or setup failed:', error.message)
    }

    await browser.close()
}

export default globalSetup
