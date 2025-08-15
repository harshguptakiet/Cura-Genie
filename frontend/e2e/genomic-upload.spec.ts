import { test, expect } from '@playwright/test'

test.describe('Genomic File Upload Workflow', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to the login page
        await page.goto('/auth/login')

        // Login with test credentials
        await page.fill('[name="email"]', 'demo@curagenie.com')
        await page.fill('[name="password"]', 'demo123')
        await page.click('button[type="submit"]')

        // Wait for successful login and redirect
        await page.waitForURL('/dashboard')
    })

    test('complete genomic file upload workflow', async ({ page }) => {
        // Navigate to dashboard
        await page.goto('/dashboard')

        // Click on upload genomic data button
        await page.click('text=Upload Genomic Data')

        // Wait for upload page to load
        await page.waitForURL('/dashboard/genomic-upload')

        // Verify upload form is visible
        await expect(page.locator('h1')).toContainText('Upload Genomic Data')

        // Select file type
        await page.selectOption('select[name="file_type"]', 'vcf')

        // Upload sample VCF file
        const fileInput = page.locator('input[type="file"]')
        await fileInput.setInputFiles('fixtures/sample.vcf')

        // Fill additional metadata
        await page.fill('input[name="description"]', 'Test VCF file for diabetes analysis')

        // Submit upload
        await page.click('button:has-text("Upload")')

        // Verify upload success
        await expect(page.locator('.upload-success')).toBeVisible()
        await expect(page.locator('text=Processing started')).toBeVisible()

        // Wait for processing to complete
        await page.waitForSelector('.processing-complete', { timeout: 30000 })

        // Verify processing results
        await expect(page.locator('text=Processing completed')).toBeVisible()
        await expect(page.locator('text=Variants detected')).toBeVisible()
    })

    test('file validation and error handling', async ({ page }) => {
        // Navigate to upload page
        await page.goto('/dashboard/genomic-upload')

        // Try to upload invalid file type
        const fileInput = page.locator('input[type="file"]')
        await fileInput.setInputFiles('fixtures/invalid.txt')

        // Submit without selecting file type
        await page.click('button:has-text("Upload")')

        // Verify error message
        await expect(page.locator('.error-message')).toContainText('Invalid file type')

        // Try to upload without file
        await page.selectOption('select[name="file_type"]', 'vcf')
        await page.click('button:has-text("Upload")')

        // Verify error message
        await expect(page.locator('.error-message')).toContainText('Please select a file')
    })

    test('upload progress tracking', async ({ page }) => {
        // Navigate to upload page
        await page.goto('/dashboard/genomic-upload')

        // Start upload
        await page.selectOption('select[name="file_type"]', 'vcf')
        await page.locator('input[type="file"]').setInputFiles('fixtures/sample.vcf')
        await page.click('button:has-text("Upload")')

        // Verify progress bar appears
        await expect(page.locator('.progress-bar')).toBeVisible()

        // Wait for upload to complete
        await page.waitForSelector('.upload-complete', { timeout: 30000 })

        // Verify progress shows 100%
        await expect(page.locator('.progress-percentage')).toContainText('100%')
    })

    test('file size limits', async ({ page }) => {
        // Navigate to upload page
        await page.goto('/dashboard/genomic-upload')

        // Try to upload very large file (simulated)
        const largeFile = 'fixtures/large.vcf' // This would be a very large file

        // Mock file size check
        await page.evaluate(() => {
            Object.defineProperty(File.prototype, 'size', {
                value: 1024 * 1024 * 1024, // 1GB
                writable: true
            })
        })

        await page.locator('input[type="file"]').setInputFiles(largeFile)
        await page.click('button:has-text("Upload")')

        // Verify file size error
        await expect(page.locator('.error-message')).toContainText('File size exceeds limit')
    })
})

test.describe('Genomic Data Management', () => {
    test.beforeEach(async ({ page }) => {
        // Login
        await page.goto('/auth/login')
        await page.fill('[name="email"]', 'demo@curagenie.com')
        await page.fill('[name="password"]', 'demo123')
        await page.click('button[type="submit"]')
        await page.waitForURL('/dashboard')
    })

    test('view uploaded genomic data', async ({ page }) => {
        // Navigate to genomic data list
        await page.goto('/dashboard/genomic-data')

        // Verify data is displayed
        await expect(page.locator('h1')).toContainText('Genomic Data')

        // Check if uploaded files are listed
        await expect(page.locator('.genomic-data-item')).toHaveCount(1)
        await expect(page.locator('text=sample.vcf')).toBeVisible()

        // Click on data item to view details
        await page.click('.genomic-data-item')

        // Verify detail view
        await expect(page.locator('h2')).toContainText('File Details')
        await expect(page.locator('text=File Type: VCF')).toBeVisible()
        await expect(page.locator('text=Status: Completed')).toBeVisible()
    })

    test('delete genomic data', async ({ page }) => {
        // Navigate to genomic data list
        await page.goto('/dashboard/genomic-data')

        // Find delete button for first item
        const deleteButton = page.locator('.delete-button').first()

        // Click delete and confirm
        await deleteButton.click()
        await page.click('button:has-text("Confirm")')

        // Verify deletion
        await expect(page.locator('text=Data deleted successfully')).toBeVisible()

        // Verify item is removed from list
        await expect(page.locator('.genomic-data-item')).toHaveCount(0)
    })
})

test.describe('PRS Calculation Workflow', () => {
    test.beforeEach(async ({ page }) => {
        // Login
        await page.goto('/auth/login')
        await page.fill('[name="email"]', 'demo@curagenie.com')
        await page.fill('[name="password"]', 'demo123')
        await page.click('button[type="submit"]')
        await page.waitForURL('/dashboard')
    })

    test('calculate PRS score', async ({ page }) => {
        // Navigate to PRS calculation
        await page.goto('/dashboard/prs-calculator')

        // Select disease type
        await page.selectOption('select[name="disease"]', 'diabetes')

        // Select genomic data file
        await page.selectOption('select[name="genomic_data"]', 'sample.vcf')

        // Start calculation
        await page.click('button:has-text("Calculate PRS")')

        // Wait for calculation to complete
        await page.waitForSelector('.calculation-complete', { timeout: 60000 })

        // Verify results
        await expect(page.locator('text=PRS Score')).toBeVisible()
        await expect(page.locator('.prs-score')).toBeVisible()
        await expect(page.locator('text=Risk Level')).toBeVisible()
        await expect(page.locator('.risk-level')).toBeVisible()
    })

    test('view PRS history', async ({ page }) => {
        // Navigate to PRS history
        await page.goto('/dashboard/prs-history')

        // Verify history is displayed
        await expect(page.locator('h1')).toContainText('PRS History')

        // Check if previous calculations are listed
        await expect(page.locator('.prs-history-item')).toHaveCount(1)

        // Click on history item to view details
        await page.click('.prs-history-item')

        // Verify detail view
        await expect(page.locator('h2')).toContainText('PRS Details')
        await expect(page.locator('text=Disease: Diabetes')).toBeVisible()
        await expect(page.locator('text=Score:')).toBeVisible()
    })
})
