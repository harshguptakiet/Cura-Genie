'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth-store'
import { toast } from 'sonner'
import { NAVIGATION_DELAYS } from '@/lib/constants/timing'
import { Button } from '@/components/ui/button'
import {
  User,
  Brain,
  Activity,
  Shield,
  Users,
  Smartphone,
  CheckCircle,
  Mail,
  Phone,
  MapPin,
  Menu,
  X,
  ChevronDown,
  Star,
  Heart,
  Zap,
  ArrowRight,
  Play,
  Pause,
  SkipForward,
  Volume2,
  Wifi,
  Battery,
  Signal,
  Linkedin
} from 'lucide-react'
import Image from 'next/image'

export default function LandingPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [scrollY, setScrollY] = useState(0)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [activeSection, setActiveSection] = useState('home')
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isVisible, setIsVisible] = useState({})

  // Handle scroll effects
  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY)

      // Update active section based on scroll position
      const sections = ['home', 'features', 'services', 'stats', 'contact']
      const current = sections.find(section => {
        const element = document.getElementById(section)
        if (element) {
          const rect = element.getBoundingClientRect()
          return rect.top <= 100 && rect.bottom >= 100
        }
        return false
      })
      if (current) setActiveSection(current)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Handle mouse movement for glow effects
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Intersection Observer for animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(prev => ({ ...prev, [entry.target.id]: true }))
          }
        })
      },
      { threshold: 0.1 }
    )

    const elements = document.querySelectorAll('[data-animate]')
    elements.forEach(el => observer.observe(el))

    return () => observer.disconnect()
  }, [])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
    setIsMenuOpen(false)
  }

  const handleLaunchPlatform = () => {
    toast.success('Redirecting to CuraGenie Platform...', {
      description: 'Taking you to the login page',
      duration: 2000,
    })
    // Use proper navigation delay for better UX
    setTimeout(() => {
      router.push('/auth/login')
    }, NAVIGATION_DELAYS.SUCCESS_REDIRECT)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 relative overflow-x-hidden">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Gradient Orbs */}
        <div
          className="absolute w-96 h-96 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-full blur-3xl animate-pulse"
          style={{
            left: mousePosition.x - 192 + 'px',
            top: mousePosition.y - 192 + 'px',
            transform: `translate(-50%, -50%) scale(${1 + scrollY * 0.0005})`
          }}
        />
        <div className="absolute top-1/4 right-1/4 w-64 h-64 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-full blur-2xl animate-bounce" />
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 rounded-full blur-2xl animate-pulse" />

        {/* Floating Particles */}
        {Array.from({ length: 50 }).map((_, i) => {
          // Use seed-based random values to ensure consistency between server and client
          const seed1 = (i * 9301 + 49297) % 233280;
          const seed2 = (i * 9301 + 49297 + 12345) % 233280;
          const seed3 = (i * 9301 + 49297 + 23456) % 233280;
          const seed4 = (i * 9301 + 49297 + 34567) % 233280;

          const left = (seed1 / 233280) * 100;
          const top = (seed2 / 233280) * 100;
          const delay = (seed3 / 233280) * 3;
          const duration = 2 + (seed4 / 233280) * 3;

          return (
            <div
              key={i}
              className="absolute w-1 h-1 bg-cyan-400/40 rounded-full animate-pulse"
              style={{
                left: left + '%',
                top: top + '%',
                animationDelay: delay + 's',
                animationDuration: duration + 's'
              }}
            />
          );
        })}
      </div>

      {/* Authenticated User Notification - NO RED ALERT */}
      {isAuthenticated && (
        <div className="fixed top-6 right-6 z-50 bg-emerald-500/95 backdrop-blur-lg text-white px-6 py-3 rounded-2xl shadow-2xl border border-emerald-400/30 glow-emerald animate-slide-in-right">
          <div className="flex items-center gap-3">
            <div className="relative">
              <User className="h-5 w-5" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping" />
            </div>
            <span className="font-medium">Welcome back!</span>
            <Button
              size="sm"
              variant="ghost"
              className="text-white hover:bg-white/20 px-3 py-1 rounded-lg transition-all duration-300 hover:scale-105"
              onClick={() => router.push('/dashboard')}
            >
              Dashboard →
            </Button>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-40 transition-all duration-500 ${scrollY > 50
          ? 'bg-slate-900/95 backdrop-blur-xl shadow-2xl border-b border-white/10'
          : 'bg-transparent'
        }`}>
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <div className="flex items-center space-x-3 group cursor-pointer" onClick={() => scrollToSection('home')}>
              <div className="relative">
                <Brain className="h-10 w-10 text-cyan-400 group-hover:text-cyan-300 transition-colors duration-300" />
                <div className="absolute inset-0 bg-cyan-400/20 rounded-full blur-lg group-hover:blur-xl transition-all duration-300" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent group-hover:from-cyan-400 group-hover:to-blue-400 transition-all duration-300">
                CuraGenie
              </span>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center space-x-8">
              {[
                { id: 'home', label: 'Home' },
                { id: 'features', label: 'Features' },
                { id: 'services', label: 'Services' },
                { id: 'stats', label: 'About' },
                { id: 'contact', label: 'Contact' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className={`relative text-sm font-medium transition-all duration-300 hover:scale-105 ${activeSection === item.id
                      ? 'text-cyan-400'
                      : 'text-gray-300 hover:text-white'
                    }`}
                >
                  {item.label}
                  {activeSection === item.id && (
                    <div className="absolute -bottom-1 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-blue-400 rounded-full" />
                  )}
                </button>
              ))}
              <Button
                onClick={handleLaunchPlatform}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white px-6 py-2 rounded-xl shadow-lg hover:shadow-cyan-500/25 transition-all duration-300 hover:scale-105 glow-cyan"
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
            <div className="md:hidden absolute top-full left-0 right-0 bg-slate-900/98 backdrop-blur-xl border-b border-white/10 animate-slide-down">
              <div className="px-6 py-4 space-y-4">
                {[
                  { id: 'home', label: 'Home' },
                  { id: 'features', label: 'Features' },
                  { id: 'services', label: 'Services' },
                  { id: 'stats', label: 'About' },
                  { id: 'contact', label: 'Contact' }
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToSection(item.id)}
                    className="block w-full text-left px-4 py-3 text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-all duration-300"
                  >
                    {item.label}
                  </button>
                ))}
                <Button
                  onClick={handleLaunchPlatform}
                  className="w-full mt-4 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 rounded-xl"
                >
                  Launch Platform
                </Button>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="relative min-h-screen flex items-center justify-center px-6">
        <div className="container mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Hero Text */}
            <div className={`text-center lg:text-left space-y-8 ${isVisible.home ? 'animate-fade-in-up' : 'opacity-0'}`} data-animate id="home">
              <h1 className="text-6xl lg:text-7xl font-bold leading-tight">
                <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent animate-gradient-x">
                  CuraGenie
                </span>
              </h1>

              <h2 className="text-3xl lg:text-4xl font-semibold text-white/90">
                AI-Powered Healthcare Platform
              </h2>

              <p className="text-xl text-gray-300 leading-relaxed max-w-2xl">
                Transform your healthcare experience with our intelligent medical platform
                featuring AI diagnostics, virtual consultations, and personalized health insights.
              </p>

              <div className="flex flex-col sm:flex-row gap-6 justify-center lg:justify-start pt-4">
                <Button
                  onClick={handleLaunchPlatform}
                  size="lg"
                  className="group bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white px-8 py-4 text-lg font-semibold rounded-2xl shadow-2xl hover:shadow-cyan-500/25 transition-all duration-500 hover:scale-110 glow-cyan"
                >
                  <Zap className="mr-3 h-6 w-6 group-hover:animate-pulse" />
                  Launch Platform
                  <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-1 transition-transform duration-300" />
                </Button>

                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => scrollToSection('features')}
                  className="border-2 border-cyan-400/50 text-cyan-400 hover:bg-cyan-400/10 hover:border-cyan-400 px-8 py-4 text-lg rounded-2xl backdrop-blur-sm transition-all duration-500 hover:scale-105"
                >
                  <Play className="mr-3 h-6 w-6" />
                  Explore Features
                </Button>
              </div>
            </div>

            {/* Hero Visual - Enhanced Medical Dashboard */}
            <div className={`relative ${isVisible.home ? 'animate-fade-in-right' : 'opacity-0'}`} data-animate>
              <div className="relative bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl rounded-3xl p-8 border border-white/10 shadow-2xl hover:shadow-cyan-500/10 transition-all duration-500 hover:scale-105 glow-subtle">
                {/* Window Controls */}
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-4 h-4 rounded-full bg-slate-400 animate-pulse" />
                  <div className="w-4 h-4 rounded-full bg-yellow-400 animate-pulse" style={{ animationDelay: '0.2s' }} />
                  <div className="w-4 h-4 rounded-full bg-green-400 animate-pulse" style={{ animationDelay: '0.4s' }} />
                  <div className="flex-1" />
                  <div className="flex items-center gap-2 text-gray-400">
                    <Wifi className="h-4 w-4" />
                    <Signal className="h-4 w-4" />
                    <Battery className="h-4 w-4" />
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-8">
                  <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-cyan-400 to-blue-400 rounded-full animate-loading-bar" />
                  </div>
                </div>

                {/* Health Metrics */}
                <div className="grid grid-cols-3 gap-6 mb-8">
                  <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-2xl p-4 text-center border border-white/5 hover:border-cyan-400/30 transition-all duration-300 hover:scale-105 glow-subtle">
                    <Activity className="h-8 w-8 text-cyan-400 mx-auto mb-2 animate-pulse" />
                    <div className="text-2xl font-bold text-white mb-1 animate-counter" data-target="72">72</div>
                    <div className="text-sm text-gray-400">BPM</div>
                  </div>

                  <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-2xl p-4 text-center border border-white/5 hover:border-emerald-400/30 transition-all duration-300 hover:scale-105 glow-subtle">
                    <div className="text-3xl mb-2 animate-pulse">🌡️</div>
                    <div className="text-2xl font-bold text-white mb-1 animate-counter" data-target="98.6">98.6</div>
                    <div className="text-sm text-gray-400">°F</div>
                  </div>

                  <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-2xl p-4 text-center border border-white/5 hover:border-purple-400/30 transition-all duration-300 hover:scale-105 glow-subtle">
                    <div className="text-3xl mb-2 animate-pulse">🫁</div>
                    <div className="text-2xl font-bold text-white mb-1 animate-counter" data-target="16">16</div>
                    <div className="text-sm text-gray-400">RPM</div>
                  </div>
                </div>

                {/* Status Indicators */}
                <div className="flex justify-between items-center text-sm">
                  <div className="flex items-center gap-2 text-green-400">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-ping" />
                    <span>All Systems Normal</span>
                  </div>
                  <div className="text-gray-400">Last Updated: Now</div>
                </div>
              </div>

              {/* Floating Elements */}
              <div className="absolute -top-4 -right-4 w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-400 rounded-full animate-bounce" />
              <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full animate-pulse" />
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="flex flex-col items-center gap-2 text-gray-400 hover:text-white transition-colors duration-300 cursor-pointer" onClick={() => scrollToSection('features')}>
            <div className="text-sm font-medium">Scroll to explore</div>
            <ChevronDown className="h-6 w-6 animate-pulse" />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 px-6 relative">
        <div className="container mx-auto">
          <div className={`text-center mb-20 ${isVisible.features ? 'animate-fade-in-up' : 'opacity-0'}`} data-animate id="features">
            <h2 className="text-5xl font-bold text-white mb-6">
              Revolutionary
              <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Features</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Experience the future of healthcare technology with our cutting-edge AI-powered platform
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Brain,
                title: "AI-Powered Analysis",
                description: "Advanced machine learning algorithms provide instant health insights and personalized recommendations based on your medical data.",
                color: "from-purple-500 to-pink-500",
                glowColor: "purple"
              },
              {
                icon: Activity,
                title: "Real-time Monitoring",
                description: "Continuous health tracking with real-time alerts and comprehensive dashboard visualization for all your vital signs.",
                color: "from-cyan-500 to-blue-500",
                glowColor: "cyan"
              },
              {
                icon: Smartphone,
                title: "Mobile-First Design",
                description: "Seamless experience across all devices with responsive design and offline capabilities for healthcare on-the-go.",
                color: "from-green-500 to-emerald-500",
                glowColor: "emerald"
              },
              {
                icon: Shield,
                title: "Data Security",
                description: "Enterprise-grade encryption and HIPAA-compliant security measures ensure your medical data remains private and secure.",
                color: "from-yellow-500 to-orange-500",
                glowColor: "yellow"
              },
              {
                icon: Users,
                title: "Collaborative Care",
                description: "Connect with healthcare providers, family members, and care teams for comprehensive collaborative health management.",
                color: "from-indigo-500 to-purple-500",
                glowColor: "indigo"
              },
              {
                icon: Heart,
                title: "Personalized Experience",
                description: "Tailored health recommendations and treatment plans powered by AI that learns and adapts to your unique health profile.",
                color: "from-pink-500 to-purple-500",
                glowColor: "purple"
              }
            ].map((feature, index) => (
              <div
                key={index}
                className={`group relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl rounded-3xl p-8 border border-white/10 hover:border-white/20 transition-all duration-500 hover:scale-105 hover:shadow-2xl ${isVisible.features ? `animate-fade-in-up` : 'opacity-0'
                  }`}
                style={{ animationDelay: `${index * 0.1}s` }}
                data-animate
              >
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${feature.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 glow-${feature.glowColor}`}>
                  <feature.icon className="h-8 w-8 text-white" />
                </div>

                <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-cyan-400 transition-colors duration-300">
                  {feature.title}
                </h3>

                <p className="text-gray-300 leading-relaxed group-hover:text-gray-200 transition-colors duration-300">
                  {feature.description}
                </p>

                {/* Hover Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-purple-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-32 px-6 bg-gradient-to-b from-slate-900/50 to-transparent relative">
        <div className="container mx-auto">
          <div className={`text-center mb-20 ${isVisible.services ? 'animate-fade-in-up' : 'opacity-0'}`} data-animate id="services">
            <h2 className="text-5xl font-bold text-white mb-6">
              Platform
              <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Services</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Comprehensive healthcare solutions designed to meet all your medical needs in one integrated platform
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            {[
              {
                icon: Activity,
                title: "Health Dashboard",
                description: "Comprehensive health monitoring and data visualization platform for complete healthcare management.",
                features: ["Real-time health metrics", "Interactive data visualization", "Personalized insights", "Progress tracking", "Health goal setting"]
              },
              {
                icon: Brain,
                title: "AI Health Analytics",
                description: "Advanced artificial intelligence for health data analysis and predictive healthcare insights.",
                features: ["Intelligent data processing", "Pattern recognition", "Predictive health analysis", "Personalized recommendations", "Risk assessment"]
              },
              {
                icon: Smartphone,
                title: "Mobile Health Platform",
                description: "Cross-platform mobile application with responsive design for seamless healthcare access anywhere.",
                features: ["Cross-platform compatibility", "Responsive design", "Offline capabilities", "Push notifications", "Secure data sync"]
              }
            ].map((service, index) => (
              <div
                key={index}
                className={`group bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-xl rounded-3xl p-10 border border-white/10 hover:border-cyan-400/30 transition-all duration-500 hover:scale-105 hover:shadow-2xl glow-subtle ${isVisible.services ? `animate-fade-in-up` : 'opacity-0'
                  }`}
                style={{ animationDelay: `${index * 0.2}s` }}
                data-animate
              >
                <div className="w-20 h-20 rounded-3xl bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-300 glow-cyan">
                  <service.icon className="h-10 w-10 text-white" />
                </div>

                <h3 className="text-3xl font-bold text-white mb-6 group-hover:text-cyan-400 transition-colors duration-300">
                  {service.title}
                </h3>

                <p className="text-gray-300 text-lg mb-8 leading-relaxed">
                  {service.description}
                </p>

                <ul className="space-y-4 mb-8">
                  {service.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center text-gray-300 group-hover:text-gray-200 transition-colors duration-300">
                      <CheckCircle className="h-5 w-5 text-cyan-400 mr-3 group-hover:text-cyan-300" />
                      <span className="text-base">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  variant="outline"
                  onClick={handleLaunchPlatform}
                  className="w-full border-2 border-cyan-400/50 text-cyan-400 hover:bg-cyan-400/10 hover:border-cyan-400 py-3 rounded-2xl font-semibold transition-all duration-300 hover:scale-105"
                >
                  Explore {service.title}
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Statistics/About Section */}
      <section id="stats" className="py-32 px-6 relative">
        <div className="container mx-auto">
          <div className={`text-center mb-20 ${isVisible.stats ? 'animate-fade-in-up' : 'opacity-0'}`} data-animate id="stats">
            <h2 className="text-5xl font-bold text-white mb-6">
              Platform
              <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Statistics</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Trusted by healthcare providers and patients worldwide for delivering exceptional medical care
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-20">
            {[
              { number: "10K+", label: "Active Users", icon: Users },
              { number: "50+", label: "AI Features", icon: Brain },
              { number: "99.9%", label: "Uptime", icon: Shield },
              { number: "24/7", label: "Support", icon: Heart }
            ].map((stat, index) => (
              <div
                key={index}
                className={`group text-center bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl rounded-3xl p-8 border border-white/10 hover:border-cyan-400/30 transition-all duration-500 hover:scale-110 glow-subtle ${isVisible.stats ? `animate-fade-in-up` : 'opacity-0'
                  }`}
                style={{ animationDelay: `${index * 0.1}s` }}
                data-animate
              >
                <stat.icon className="h-12 w-12 text-cyan-400 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300" />
                <div className="text-4xl font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors duration-300 animate-counter" data-target={stat.number}>
                  {stat.number}
                </div>
                <div className="text-gray-300 font-medium group-hover:text-gray-200 transition-colors duration-300">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Developer Section */}
          <div className={`bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-xl rounded-3xl p-12 border border-white/10 max-w-4xl mx-auto text-center glow-subtle ${isVisible.stats ? 'animate-fade-in-up' : 'opacity-0'
            }`} data-animate style={{ animationDelay: '0.5s' }}>
            <div className="w-32 h-32 rounded-full overflow-hidden mx-auto mb-8 shadow-2xl hover:scale-110 transition-transform duration-300 glow-cyan cursor-pointer border-4 border-cyan-400/50">
              <Image
                src="/curagenie-hero.png"
                alt="Harsh Gupta - CuraGenie Developer"
                width={128}
                height={128}
                className="w-full h-full object-cover"
                quality={95}
              />
            </div>

            <h3 className="text-4xl font-bold text-white mb-4">Harsh Gupta</h3>
            <p className="text-xl text-cyan-400 mb-6 font-semibold">Full Stack Developer & Healthcare Tech Innovator</p>

            <p className="text-lg text-gray-300 leading-relaxed mb-8 max-w-2xl mx-auto">
              Passionate about revolutionizing healthcare through cutting-edge technology.
              CuraGenie represents the perfect fusion of AI innovation and healthcare accessibility,
              designed to transform how we approach medical care in the digital age.
            </p>

            <div className="flex flex-wrap justify-center gap-3 mb-8">
              {["React", "Next.js", "Node.js", "AI/ML", "Healthcare Tech", "TypeScript"].map((skill) => (
                <span key={skill} className="px-4 py-2 bg-gradient-to-r from-slate-700 to-slate-800 text-cyan-400 rounded-full text-sm font-semibold border border-cyan-400/20 hover:border-cyan-400/50 transition-all duration-300 hover:scale-105">
                  {skill}
                </span>
              ))}
            </div>

            <div className="flex justify-center space-x-4">
              {[
                { icon: Mail, label: "Email", href: "mailto:guptasecularharsh@gmail.com" },
                { icon: Phone, label: "Phone", href: "tel:+918081434149" },
                { icon: Linkedin, label: "LinkedIn", href: "https://linkedin.com/in/harsh-gupta-kiet/" }
              ].map((contact, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="lg"
                  className="border-cyan-400/50 text-cyan-400 hover:bg-cyan-400/10 hover:border-cyan-400 rounded-2xl px-6 py-3 transition-all duration-300 hover:scale-105"
                  onClick={() => window.open(contact.href, '_blank', 'noopener,noreferrer')}
                >
                  <contact.icon className="h-5 w-5" />
                  <span className="sr-only">{contact.label}</span>
                </Button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-32 px-6 bg-gradient-to-t from-slate-900/50 to-transparent relative">
        <div className="container mx-auto">
          <div className={`text-center mb-20 ${isVisible.contact ? 'animate-fade-in-up' : 'opacity-0'}`} data-animate id="contact">
            <h2 className="text-5xl font-bold text-white mb-6">
              Get In
              <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Touch</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Ready to revolutionize your healthcare experience? Let's connect and explore how CuraGenie can transform your medical journey.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-16">
            {/* Contact Info */}
            <div className={`space-y-8 ${isVisible.contact ? 'animate-fade-in-left' : 'opacity-0'}`} data-animate style={{ animationDelay: '0.2s' }}>
              {[
                {
                  icon: MapPin,
                  title: "Project Location",
                  details: ["CuraGenie Platform", "AI-Powered Healthcare Solution"]
                },
                {
                  icon: Phone,
                  title: "Developer Contact",
                  details: ["+91 8081434149", "Harsh Gupta - Full Stack Developer"]
                },
                {
                  icon: Mail,
                  title: "Email Support",
                  details: ["guptasecularharsh@gmail.com", "Technical Support & Inquiries"]
                }
              ].map((contact, index) => (
                <div key={index} className="flex items-start space-x-6 group">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center group-hover:scale-110 transition-transform duration-300 glow-cyan">
                    <contact.icon className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h4 className="text-2xl font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors duration-300">
                      {contact.title}
                    </h4>
                    {contact.details.map((detail, idx) => (
                      <p key={idx} className="text-gray-300 text-lg group-hover:text-gray-200 transition-colors duration-300">
                        {detail}
                      </p>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Contact Form */}
            <div className={`bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-xl rounded-3xl p-10 border border-white/10 glow-subtle ${isVisible.contact ? 'animate-fade-in-right' : 'opacity-0'}`} data-animate style={{ animationDelay: '0.4s' }}>
              <form className="space-y-6" onSubmit={(e) => {
                e.preventDefault()
                const formData = new FormData(e.currentTarget)
                const name = formData.get('name') as string
                toast.success(`Thank you ${name}! Your message has been received.`, {
                  description: "We'll get back to you within 24 hours.",
                  duration: 3000,
                })
                e.currentTarget.reset()
              }}>
                <div>
                  <label htmlFor="name" className="block text-lg font-semibold text-white mb-3">
                    Full Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    className="w-full px-6 py-4 bg-slate-700/50 border border-slate-600/50 rounded-2xl text-white placeholder-gray-400 text-lg focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all duration-300 backdrop-blur-sm"
                    placeholder="Enter your full name"
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-lg font-semibold text-white mb-3">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    className="w-full px-6 py-4 bg-slate-700/50 border border-slate-600/50 rounded-2xl text-white placeholder-gray-400 text-lg focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all duration-300 backdrop-blur-sm"
                    placeholder="Enter your email address"
                  />
                </div>

                <div>
                  <label htmlFor="message" className="block text-lg font-semibold text-white mb-3">
                    Message
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={6}
                    className="w-full px-6 py-4 bg-slate-700/50 border border-slate-600/50 rounded-2xl text-white placeholder-gray-400 text-lg focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all duration-300 backdrop-blur-sm resize-none"
                    placeholder="Tell us about your healthcare needs or questions..."
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white text-lg font-semibold py-4 rounded-2xl shadow-2xl hover:shadow-cyan-500/25 transition-all duration-500 hover:scale-105 glow-cyan"
                >
                  <Mail className="mr-3 h-6 w-6" />
                  Send Message
                  <ArrowRight className="ml-3 h-6 w-6" />
                </Button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 px-6 bg-slate-900/80 backdrop-blur-xl border-t border-white/10 relative">
        <div className="container mx-auto">
          <div className="text-center space-y-6">
            {/* Logo */}
            <div className="flex items-center justify-center space-x-3 group">
              <Brain className="h-12 w-12 text-cyan-400 group-hover:text-cyan-300 transition-colors duration-300" />
              <span className="text-3xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                CuraGenie
              </span>
            </div>

            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Revolutionizing healthcare through advanced AI technology and personalized medicine.
              Built with ❤️ for a healthier tomorrow.
            </p>

            {/* Social Links */}
            <div className="flex justify-center space-x-6">
              {[
                { icon: Mail, label: "Email", href: "mailto:guptasecularharsh@gmail.com" },
                { icon: Phone, label: "Phone", href: "tel:+918081434149" },
                { icon: Linkedin, label: "LinkedIn", href: "https://linkedin.com/in/harsh-gupta-kiet/" }
              ].map((social, index) => (
                <div
                  key={index}
                  className="w-12 h-12 rounded-full bg-slate-700/50 flex items-center justify-center cursor-pointer hover:bg-cyan-500/20 hover:text-cyan-400 transition-all duration-300 hover:scale-110 glow-subtle"
                  onClick={() => window.open(social.href, '_blank', 'noopener,noreferrer')}
                >
                  <social.icon className="h-6 w-6 text-gray-400 hover:text-cyan-400" />
                </div>
              ))}
            </div>

            {/* Copyright */}
            <div className="border-t border-slate-700/50 pt-8 space-y-2">
              <p className="text-gray-400 text-lg">
                © 2025 CuraGenie - Developed by
                <span className="text-cyan-400 font-semibold"> Harsh Gupta</span>.
                All rights reserved.
              </p>
              <p className="text-gray-500 text-sm">
                Built with cutting-edge technology: React, Next.js, TypeScript & AI/ML
              </p>
            </div>
          </div>
        </div>
      </footer>

      {/* Custom Styles */}
      <style jsx global>{`
        @keyframes gradient-x {
          0%, 100% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
        }
        
        @keyframes loading-bar {
          0% { width: 0%; }
          50% { width: 75%; }
          100% { width: 100%; }
        }
        
        @keyframes counter {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fade-in-left {
          from {
            opacity: 0;
            transform: translateX(-30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes fade-in-right {
          from {
            opacity: 0;
            transform: translateX(30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes slide-in-right {
          from {
            opacity: 0;
            transform: translateX(100px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes slide-down {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-gradient-x {
          background-size: 400% 400%;
          animation: gradient-x 3s ease infinite;
        }
        
        .animate-loading-bar {
          animation: loading-bar 3s ease-in-out infinite;
        }
        
        .animate-counter {
          animation: counter 0.5s ease-out;
        }
        
        .animate-fade-in-up {
          animation: fade-in-up 0.8s ease-out forwards;
        }
        
        .animate-fade-in-left {
          animation: fade-in-left 0.8s ease-out forwards;
        }
        
        .animate-fade-in-right {
          animation: fade-in-right 0.8s ease-out forwards;
        }
        
        .animate-slide-in-right {
          animation: slide-in-right 0.5s ease-out;
        }
        
        .animate-slide-down {
          animation: slide-down 0.3s ease-out;
        }
        
        .glow-cyan {
          box-shadow: 0 0 20px rgba(34, 211, 238, 0.3);
        }
        
        .glow-emerald {
          box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
        }
        
        .glow-purple {
          box-shadow: 0 0 20px rgba(147, 51, 234, 0.3);
        }
        
        .glow-yellow {
          box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
        }
        
        .glow-rose {
          box-shadow: 0 0 20px rgba(244, 63, 94, 0.3);
        }
        
        .glow-indigo {
          box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
        }
        
        .glow-subtle {
          box-shadow: 0 0 40px rgba(255, 255, 255, 0.05);
        }
        
        .glow-subtle:hover {
          box-shadow: 0 0 60px rgba(34, 211, 238, 0.1);
        }
        
        .animate-spin-slow {
          animation: spin 8s linear infinite;
        }
        
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
        
        /* Smooth scrolling */
        html {
          scroll-behavior: smooth;
        }
        
        /* Hide scrollbar but keep functionality */
        ::-webkit-scrollbar {
          width: 8px;
        }
        
        ::-webkit-scrollbar-track {
          background: rgba(15, 23, 42, 0.8);
        }
        
        ::-webkit-scrollbar-thumb {
          background: rgba(34, 211, 238, 0.5);
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: rgba(34, 211, 238, 0.7);
        }
      `}</style>
    </div>
  )
}
