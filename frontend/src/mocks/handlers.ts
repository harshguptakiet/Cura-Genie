import { http, HttpResponse } from 'msw'

// Mock data
const mockUsers = [
    {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        role: 'patient',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
    },
]

const mockGenomicData = [
    {
        id: 1,
        filename: 'sample.vcf',
        file_type: 'vcf',
        status: 'completed',
        file_size: 1024000,
        upload_date: '2024-01-01T00:00:00Z',
        user_id: 1,
    },
]

const mockPRSScores = [
    {
        id: 1,
        disease: 'diabetes',
        score: 0.75,
        percentile: 85,
        risk_level: 'high',
        calculated_at: '2024-01-01T00:00:00Z',
        user_id: 1,
    },
]

const mockMRIScans = [
    {
        id: 1,
        filename: 'brain_scan.dcm',
        scan_type: 'brain',
        status: 'completed',
        file_size: 52428800,
        upload_date: '2024-01-01T00:00:00Z',
        user_id: 1,
    },
]

// API handlers
export const handlers = [
    // Health check
    http.get('/api/health', () => {
        return HttpResponse.json({
            status: 'healthy',
            timestamp: new Date().toISOString(),
        })
    }),

    // Authentication
    http.post('/api/auth/register', async ({ request }) => {
        const body = await request.json()

        // Simulate duplicate email check
        if (body.email === 'duplicate@example.com') {
            return HttpResponse.json(
                { detail: 'Email already registered' },
                { status: 400 }
            )
        }

        return HttpResponse.json({
            id: 2,
            email: body.email,
            username: body.username,
            role: body.role,
            is_active: true,
            created_at: new Date().toISOString(),
        }, { status: 201 })
    }),

    http.post('/api/auth/login', async ({ request }) => {
        const body = await request.json()

        if (body.email === 'nonexistent@example.com') {
            return HttpResponse.json(
                { detail: 'Invalid credentials' },
                { status: 401 }
            )
        }

        return HttpResponse.json({
            access_token: 'mock_jwt_token_12345',
            token_type: 'bearer',
            user: {
                id: 1,
                email: body.email,
                username: 'testuser',
                role: 'patient',
            },
        })
    }),

    // Genomic data
    http.get('/api/genomic/data', () => {
        return HttpResponse.json(mockGenomicData)
    }),

    http.get('/api/genomic/data/:id', ({ params }) => {
        const id = params.id
        const data = mockGenomicData.find(item => item.id === Number(id))

        if (!data) {
            return HttpResponse.json(
                { detail: 'Genomic data not found' },
                { status: 404 }
            )
        }

        return HttpResponse.json(data)
    }),

    http.post('/api/genomic/upload', async ({ request }) => {
        const formData = await request.formData()
        const file = formData.get('file') as File
        const fileType = formData.get('file_type') as string

        return HttpResponse.json({
            id: 2,
            filename: file?.name || 'uploaded_file',
            file_type: fileType,
            status: 'uploaded',
            file_size: file?.size || 0,
            upload_date: new Date().toISOString(),
            user_id: 1,
        })
    }),

    // PRS scores
    http.get('/api/prs/scores', () => {
        return HttpResponse.json(mockPRSScores)
    }),

    http.post('/api/prs/calculate', async ({ request }) => {
        const body = await request.json()

        return HttpResponse.json({
            id: 2,
            disease: body.disease,
            score: 0.65,
            percentile: 70,
            risk_level: 'moderate',
            calculated_at: new Date().toISOString(),
            user_id: 1,
            genomic_data_id: body.genomic_data_id,
        })
    }),

    // User profile
    http.get('/api/profile/me', () => {
        return HttpResponse.json({
            id: 1,
            email: 'test@example.com',
            username: 'testuser',
            first_name: 'John',
            last_name: 'Doe',
            role: 'patient',
            is_active: true,
            created_at: '2024-01-01T00:00:00Z',
        })
    }),

    http.put('/api/profile/me', async ({ request }) => {
        const body = await request.json()

        return HttpResponse.json({
            id: 1,
            email: 'test@example.com',
            username: 'testuser',
            first_name: body.first_name,
            last_name: body.last_name,
            phone: body.phone,
            role: 'patient',
            is_active: true,
            created_at: '2024-01-01T00:00:00Z',
        })
    }),

    // MRI scans
    http.get('/api/mri/scans', () => {
        return HttpResponse.json(mockMRIScans)
    }),

    http.post('/api/mri/upload', async ({ request }) => {
        const formData = await request.formData()
        const file = formData.get('file') as File
        const scanType = formData.get('scan_type') as string

        return HttpResponse.json({
            id: 2,
            filename: file?.name || 'uploaded_scan',
            scan_type: scanType,
            status: 'uploaded',
            file_size: file?.size || 0,
            upload_date: new Date().toISOString(),
            user_id: 1,
        })
    }),

    // Reports
    http.get('/api/reports', () => {
        return HttpResponse.json([
            {
                id: 1,
                title: 'Genomic Analysis Report',
                report_type: 'genomic',
                content: 'This is a sample genomic analysis report.',
                generated_at: '2024-01-01T00:00:00Z',
                status: 'final',
                user_id: 1,
            },
        ])
    }),

    // Chatbot
    http.post('/api/chatbot/query', async ({ request }) => {
        const body = await request.json()

        return HttpResponse.json({
            id: 'chat_123',
            query: body.query,
            response: 'This is a mock response to your query about genomic data.',
            timestamp: new Date().toISOString(),
            user_id: 1,
        })
    }),

    // Fallback handler
    http.all('*', () => {
        return HttpResponse.json(
            { detail: 'Endpoint not found' },
            { status: 404 }
        )
    }),
]
