import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate required fields
    if (!body.feedback_type || !body.message) {
      return NextResponse.json(
        { detail: 'Feedback type and message are required' },
        { status: 400 }
      )
    }

    if (body.message.trim().length < 10) {
      return NextResponse.json(
        { detail: 'Message must be at least 10 characters long' },
        { status: 400 }
      )
    }

    // Validate feedback type
    const validTypes = ['bug_report', 'feature_request', 'general_feedback']
    if (!validTypes.includes(body.feedback_type)) {
      return NextResponse.json(
        { detail: `Invalid feedback type. Must be one of: ${validTypes.join(', ')}` },
        { status: 400 }
      )
    }

    // Validate rating if provided
    if (body.rating !== undefined && (body.rating < 1 || body.rating > 5)) {
      return NextResponse.json(
        { detail: 'Rating must be between 1 and 5' },
        { status: 400 }
      )
    }

    // Generate feedback ID
    const feedbackId = `FB_${Date.now()}`

    // Log the feedback (in production, you'd save to database)
    console.log('Feedback received:', {
      id: feedbackId,
      type: body.feedback_type,
      rating: body.rating,
      hasName: !!body.name,
      hasEmail: !!body.email,
      messageLength: body.message.length
    })

    // Here you would typically:
    // 1. Save to database
    // 2. Send email notification to support team
    // 3. Store in analytics system

    return NextResponse.json({
      success: true,
      message: "Thank you for your feedback! We'll review it and get back to you if needed.",
      feedback_id: feedbackId
    })

  } catch (error) {
    console.error('Error processing feedback:', error)
    return NextResponse.json(
      { detail: 'An error occurred while processing your feedback. Please try again.' },
      { status: 500 }
    )
  }
}
