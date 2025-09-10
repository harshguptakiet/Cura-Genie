"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'
import { 
  Star, 
  MessageSquare, 
  Bug, 
  Lightbulb, 
  Heart, 
  ArrowRight,
  CheckCircle,
  Send,
  Brain,
  Activity,
  Shield,
  Users,
  Smartphone,
  Mail,
  Phone,
  MapPin,
  Menu,
  X,
  Linkedin
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

interface FeedbackFormData {
  name: string
  email: string
  feedback_type: string
  message: string
  rating: number
}

export default function FeedbackPage() {
  const router = useRouter()
  const [formData, setFormData] = useState<FeedbackFormData>({
    name: '',
    email: '',
    feedback_type: '',
    message: '',
    rating: 0
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [hoveredStar, setHoveredStar] = useState(0)
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const feedbackTypes = [
    { value: 'bug_report', label: 'Bug Report', icon: Bug, description: 'Report an issue or problem' },
    { value: 'feature_request', label: 'Feature Request', icon: Lightbulb, description: 'Suggest a new feature' },
    { value: 'general_feedback', label: 'General Feedback', icon: Heart, description: 'Share your thoughts' }
  ]

  const handleInputChange = (field: keyof FeedbackFormData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.feedback_type || !formData.message.trim()) {
      toast.error('Please select a feedback type and provide a message')
      return
    }

    if (formData.message.trim().length < 10) {
      toast.error('Message must be at least 10 characters long')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name || undefined,
          email: formData.email || undefined,
          feedback_type: formData.feedback_type,
          message: formData.message,
          rating: formData.rating || undefined
        }),
      })

      let result
      try {
        result = await response.json()
      } catch (jsonError) {
        // If response is not JSON (e.g., HTML error page)
        throw new Error('Server returned an invalid response')
      }

      if (response.ok) {
        toast.success('Thank you for your feedback!', {
          duration: 5000,
          style: { color: 'black' },
        })
        
        // Reset form
        setFormData({
          name: '',
          email: '',
          feedback_type: '',
          message: '',
          rating: 0
        })
      } else {
        toast.error('Failed to submit feedback', {
          description: result.detail || 'Please try again later',
        })
      }
    } catch (error) {
      console.error('Error submitting feedback:', error)
      toast.error('Failed to submit feedback', {
        description: 'Please check your connection and try again',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStars = () => {
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            className="focus:outline-none"
            onMouseEnter={() => setHoveredStar(star)}
            onMouseLeave={() => setHoveredStar(0)}
            onClick={() => handleInputChange('rating', star)}
          >
            <Star
              className={`w-8 h-8 transition-colors duration-200 ${
                star <= (hoveredStar || formData.rating)
                  ? 'text-yellow-400 fill-yellow-400'
                  : 'text-gray-400 hover:text-yellow-300'
              }`}
            />
          </button>
        ))}
        <span className="ml-2 text-sm text-gray-400">
          {formData.rating > 0 ? `${formData.rating} star${formData.rating > 1 ? 's' : ''}` : 'Rate your experience'}
        </span>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 relative overflow-hidden" suppressHydrationWarning>
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%222%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 transition-all duration-500 bg-slate-900/95 backdrop-blur-xl shadow-2xl border-b border-white/10">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="relative">
                <Brain className="h-10 w-10 text-cyan-400 group-hover:text-cyan-300 transition-colors duration-300" />
                <div className="absolute inset-0 bg-cyan-400/20 rounded-full blur-lg group-hover:blur-xl transition-all duration-300" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent group-hover:from-cyan-400 group-hover:to-blue-400 transition-all duration-300">
                CuraGenie
              </span>
            </Link>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/" className="text-gray-300 hover:text-white transition-colors duration-300">
                Home
              </Link>
              <Link href="/feedback" className="text-cyan-400 font-medium">
                Feedback
              </Link>
              <Button
                onClick={() => router.push('/dashboard')}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white px-6 py-2 rounded-xl shadow-lg hover:shadow-cyan-500/25 transition-all duration-300 hover:scale-105"
              >
                Launch Platform
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden text-white p-2 rounded-lg hover:bg-white/10 transition-all duration-300"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {isMenuOpen && (
            <div className="md:hidden absolute top-full left-0 right-0 px-4 animate-slide-down">
              <div className="bg-slate-900/95 backdrop-blur-xl border border-white/10 shadow-xl overflow-hidden">
                <div className="flex flex-col items-center py-6 space-y-4">
                  <Link 
                    href="/" 
                    className="text-gray-300 hover:text-white transition-colors duration-300"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Home
                  </Link>
                  <Link 
                    href="/feedback" 
                    className="text-cyan-400 font-medium"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Feedback
                  </Link>
                  <Button
                    onClick={() => {
                      router.push('/dashboard')
                      setIsMenuOpen(false)
                    }}
                    className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white px-6 py-2 rounded-xl shadow-lg hover:shadow-cyan-500/25 transition-all duration-300 hover:scale-105"
                  >
                    Launch Platform
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>
      
      <div className="relative z-10 container mx-auto px-4 py-16 pt-32">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            Share Your
            <span className="inline-block bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent ml-3">
              Feedback
            </span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Help us improve CuraGenie by sharing your thoughts, suggestions, and experiences. 
            Your feedback is invaluable in making our platform better for everyone.
          </p>
        </div>

        {/* Feedback Form */}
        <div className="max-w-2xl mx-auto">
          <Card className="bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-xl border-white/10 shadow-2xl">
            <CardHeader className="text-center pb-8">
              <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center">
                <MessageSquare className="h-8 w-8 text-white" />
              </div>
               <CardTitle className="text-2xl font-bold text-white">
                 Tell Us What You Think
               </CardTitle>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                 {/* Feedback Type Selection */}
                 <div className="space-y-3">
                   <Label className="text-lg font-semibold text-white">
                     What type of feedback do you have?
                   </Label>
                   <Select
                     value={formData.feedback_type}
                     onValueChange={(value) => handleInputChange('feedback_type', value)}
                   >
                     <SelectTrigger className="bg-slate-700/50 border-slate-600/50 rounded-xl text-white focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 h-14">
                       <SelectValue placeholder="Choose the type of feedback you'd like to share..." />
                     </SelectTrigger>
                     <SelectContent className="bg-slate-800 border-slate-600">
                       {feedbackTypes.map((type) => {
                         const IconComponent = type.icon
                         return (
                           <SelectItem 
                             key={type.value} 
                             value={type.value}
                             className="text-white hover:bg-slate-700 focus:bg-slate-700"
                           >
                             <div className="flex items-center space-x-3">
                               <IconComponent className="h-5 w-5 text-cyan-400" />
                               <div>
                                 <div className="font-semibold">{type.label}</div>
                                 <div className="text-sm text-gray-400">{type.description}</div>
                               </div>
                             </div>
                           </SelectItem>
                         )
                       })}
                     </SelectContent>
                   </Select>
                 </div>

                 {/* Name (Optional) */}
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-lg font-semibold text-white">
                    Name (Optional)
                  </Label>
                   <Input
                     id="name"
                     type="text"
                     value={formData.name}
                     onChange={(e) => handleInputChange('name', e.target.value)}
                     className="bg-slate-700/50 border-slate-600/50 rounded-xl text-white placeholder-gray-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 h-14"
                     placeholder="Enter your name"
                   />
                </div>

                {/* Email (Optional) */}
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-lg font-semibold text-white">
                    Email (Optional)
                  </Label>
                   <Input
                     id="email"
                     type="email"
                     value={formData.email}
                     onChange={(e) => handleInputChange('email', e.target.value)}
                     className="bg-slate-700/50 border-slate-600/50 rounded-xl text-white placeholder-gray-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 h-14"
                     placeholder="Enter your email address"
                   />
                </div>

                {/* Message */}
                <div className="space-y-2">
                  <Label htmlFor="message" className="text-lg font-semibold text-white">
                    Your Feedback <span className="text-red-400">*</span>
                  </Label>
                  <Textarea
                    id="message"
                    value={formData.message}
                    onChange={(e) => handleInputChange('message', e.target.value)}
                    required
                    rows={6}
                    className="bg-slate-700/50 border-slate-600/50 rounded-xl text-white placeholder-gray-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 resize-none"
                    placeholder="Please share your detailed feedback, suggestions, or report any issues you've encountered..."
                  />
                   <p className="text-sm text-gray-400">
                     {formData.message.length}/500 characters (minimum 10 required)
                   </p>
                 </div>

                 {/* Rating */}
                 <div className="space-y-3">
                   <Label className="text-lg font-semibold text-white">
                     How would you rate your overall experience?
                   </Label>
                   {renderStars()}
                 </div>

                 {/* Submit Button */}
                <Button
                  type="submit"
                  disabled={isSubmitting || !formData.feedback_type || formData.message.trim().length < 10}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white text-lg font-semibold py-6 rounded-xl shadow-2xl hover:shadow-cyan-500/25 transition-all duration-500 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send className="mr-3 h-6 w-6" />
                      Submit Feedback
                      <ArrowRight className="ml-3 h-6 w-6" />
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Additional Info */}
          <div className="mt-8 text-center">
            <p className="text-gray-400 text-sm">
              Your feedback is anonymous unless you provide contact information. 
              We typically respond within 24-48 hours for urgent issues.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-16 px-6 bg-slate-900/95 backdrop-blur-xl border-t border-white/10 relative">
        <div className="container mx-auto max-w-6xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">

          {/* Logo + Description */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center space-x-3 group">
              <Brain className="h-10 w-10 text-cyan-400 group-hover:text-cyan-300 transition-colors duration-300" />
              <span className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                CuraGenie
              </span>
            </div>
            <p className="text-gray-400 text-base">
              Revolutionizing healthcare through advanced AI technology and personalized medicine.
              Built with ❤️ for a healthier tomorrow.
            </p>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Features</h4>
            <ul className="space-y-3 text-gray-400">
              <li>
                <span className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Brain className="w-4 h-4" />
                  <span>AI Powered Analysis</span>
                </span>
              </li>
              <li>
                <span className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Activity className="w-4 h-4" />
                  <span>Real-time Monitoring</span>
                </span>
              </li>
              <li>
                <span className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Smartphone className="w-4 h-4" />
                  <span>Mobile-First Design</span>
                </span>
              </li>
              <li>
                <span className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Shield className="w-4 h-4" />
                  <span>Data Security</span>
                </span>
              </li>
              <li>
                <span className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Users className="w-4 h-4" />
                  <span>Collaborative Care</span>
                </span>
              </li>
              <li>
                <span className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Heart className="w-4 h-4" />
                  <span>Personalized Experience</span>
                </span>
              </li>
            </ul>
          </div>

          {/* Services */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Services</h4>
            <ul className="space-y-3 text-gray-400">
              <li>
                <span className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Activity className="w-4 h-4" />
                  <span>Health Dashboard</span>
                </span>
              </li>
              <li>
                <span className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Brain className="w-4 h-4" />
                  <span>AI Health Analytics</span>
                </span>
              </li>
              <li>
                <span className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Smartphone className="w-4 h-4" />
                  <span>Mobile Health Platform</span>
                </span>
              </li>
              <li>
                <Link href="/feedback" className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <MessageSquare className="w-4 h-4" />
                  <span>Feedback</span>
                </Link>
              </li>
            </ul>
          </div>

          {/* Socials */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Socials</h4>
            <ul className="space-y-3 text-gray-400">
              <li>
                <a href="mailto:guptasecularharsh@gmail.com" className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Mail className="w-4 h-4" />
                  <span>Email Support</span>
                </a>
              </li>
              <li>
                <a href="tel:+918081434149" className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Phone className="w-4 h-4" />
                  <span>Developer Contact</span>
                </a>
              </li>
              <li>
                <a href="https://linkedin.com/in/harsh-gupta-kiet/" target="_blank" rel="noopener noreferrer" className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <Linkedin className="w-4 h-4" />
                  <span>LinkedIn</span>
                </a>
              </li>
              <li>
                <Link href="/" className="flex items-center space-x-2 hover:text-cyan-400 transition">
                  <MapPin className="w-4 h-4" />
                  <span>Project Location</span>
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="container mx-auto mt-12 border-t border-slate-700/50 pt-8 flex flex-col md:flex-row items-center justify-around text-gray-500 text-sm">
          <p>
            © 2025 CuraGenie - Developed by
            <span className="text-cyan-400 font-semibold"> Harsh Gupta</span>.
            All rights reserved.
          </p>
          <p className="mt-4 md:mt-0">
            Built with cutting-edge technology: React, Next.js, TypeScript & AI/ML
          </p>
        </div>
      </footer>
    </div>
  )
}
