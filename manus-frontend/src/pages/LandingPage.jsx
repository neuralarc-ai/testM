import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Zap,
  Bot,
  Image,
  Video,
  FileText,
  Code,
  BarChart3,
  Globe,
  Sparkles,
  ArrowRight,
  CheckCircle,
  Star,
  Users,
  Clock,
  Shield,
} from 'lucide-react'

const LandingPage = () => {
  const navigate = useNavigate()

  const features = [
    {
      icon: Bot,
      title: 'Multi-Agent System',
      description: 'Coordinated AI agents working together to complete complex tasks autonomously.',
    },
    {
      icon: Image,
      title: 'Content Generation',
      description: 'Create images, videos, presentations, and documents with AI-powered tools.',
    },
    {
      icon: Code,
      title: 'Code Development',
      description: 'Generate, debug, and deploy code across multiple programming languages.',
    },
    {
      icon: BarChart3,
      title: 'Data Analysis',
      description: 'Process data, create visualizations, and generate insights automatically.',
    },
    {
      icon: Globe,
      title: 'Web Automation',
      description: 'Automate web browsing, form filling, and data extraction tasks.',
    },
    {
      icon: FileText,
      title: 'Research & Writing',
      description: 'Conduct research, synthesize information, and create comprehensive reports.',
    },
  ]

  const useCases = [
    'Create marketing presentations',
    'Build websites and applications',
    'Generate social media content',
    'Analyze business data',
    'Automate repetitive tasks',
    'Research and summarize topics',
    'Design graphics and visuals',
    'Write technical documentation',
  ]

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Marketing Director',
      content: 'Manus AI has revolutionized our content creation process. What used to take days now takes hours.',
      rating: 5,
    },
    {
      name: 'David Rodriguez',
      role: 'Software Engineer',
      content: 'The code generation capabilities are incredible. It\'s like having a senior developer on demand.',
      rating: 5,
    },
    {
      name: 'Emily Johnson',
      role: 'Business Analyst',
      content: 'The data analysis features have transformed how we make decisions. Insights in minutes, not weeks.',
      rating: 5,
    },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold">Manus AI</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/login">
                <Button variant="ghost">Sign In</Button>
              </Link>
              <Link to="/register">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <Badge variant="secondary" className="mb-4">
              <Sparkles className="w-4 h-4 mr-1" />
              World's First Autonomous AI Agent
            </Badge>
            <h1 className="text-4xl lg:text-6xl font-bold tracking-tight mb-6">
              The AI that{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                bridges mind and action
              </span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              Manus AI is the world's first autonomous AI agent that can understand your goals, 
              plan complex tasks, and execute them independently across multiple domains.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" onClick={() => navigate('/register')} className="text-lg px-8">
                Start Building
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8">
                Watch Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">
              Autonomous AI Capabilities
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Our multi-agent system can handle complex tasks across multiple domains, 
              from content creation to software development.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mb-4">
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold mb-6">
                What can Manus AI do for you?
              </h2>
              <p className="text-xl text-muted-foreground mb-8">
                From simple tasks to complex projects, Manus AI adapts to your needs 
                and delivers results autonomously.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {useCases.map((useCase, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span className="text-sm">{useCase}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-8 text-white">
                <div className="space-y-6">
                  <div className="flex items-center space-x-3">
                    <Users className="h-6 w-6" />
                    <span className="text-lg font-semibold">10+ Specialized Agents</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Clock className="h-6 w-6" />
                    <span className="text-lg font-semibold">24/7 Autonomous Operation</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Shield className="h-6 w-6" />
                    <span className="text-lg font-semibold">Enterprise-Grade Security</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-muted/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">
              Trusted by professionals worldwide
            </h2>
            <p className="text-xl text-muted-foreground">
              See what our users are saying about Manus AI
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-lg">
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-muted-foreground mb-4">"{testimonial.content}"</p>
                  <div>
                    <p className="font-semibold">{testimonial.name}</p>
                    <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold mb-6">
            Ready to experience the future of AI?
          </h2>
          <p className="text-xl text-muted-foreground mb-8">
            Join thousands of professionals who are already using Manus AI to 
            automate their workflows and boost productivity.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => navigate('/register')} className="text-lg px-8">
              Get Started Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8">
              Schedule Demo
            </Button>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            No credit card required • 1000 free credits • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Zap className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold">Manus AI</span>
              </div>
              <p className="text-muted-foreground mb-4">
                The world's first autonomous AI agent that bridges mind and action.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link to="#" className="hover:text-foreground">Features</Link></li>
                <li><Link to="#" className="hover:text-foreground">Pricing</Link></li>
                <li><Link to="#" className="hover:text-foreground">API</Link></li>
                <li><Link to="#" className="hover:text-foreground">Documentation</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link to="#" className="hover:text-foreground">About</Link></li>
                <li><Link to="#" className="hover:text-foreground">Blog</Link></li>
                <li><Link to="#" className="hover:text-foreground">Careers</Link></li>
                <li><Link to="#" className="hover:text-foreground">Contact</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
            <p>&copy; 2025 Manus AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage

