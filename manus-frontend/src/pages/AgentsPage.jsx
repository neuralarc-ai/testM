import React, { useEffect, useState } from 'react'
import { useTask } from '../contexts/TaskContext'
import { useAuth } from '../contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Bot,
  Brain,
  Search,
  FileText,
  Image,
  Video,
  Code,
  BarChart3,
  Globe,
  Zap,
  Shield,
  Clock,
  CheckCircle,
  Star,
  Users,
  Activity,
  Cpu,
  Database,
  Network,
} from 'lucide-react'

const AgentsPage = () => {
  const { agents, loadAgents } = useTask()
  const { user } = useAuth()
  const [selectedAgent, setSelectedAgent] = useState(null)

  useEffect(() => {
    loadAgents()
  }, [])

  const agentCategories = [
    {
      id: 'core',
      name: 'Core Agents',
      description: 'Essential AI agents for primary tasks',
      agents: agents.filter(agent => ['executor', 'planning', 'knowledge'].includes(agent.agent_type))
    },
    {
      id: 'content',
      name: 'Content Creation',
      description: 'Specialized agents for content generation',
      agents: agents.filter(agent => ['content', 'image', 'video'].includes(agent.agent_type))
    },
    {
      id: 'technical',
      name: 'Technical',
      description: 'Development and analysis focused agents',
      agents: agents.filter(agent => ['code', 'data', 'web'].includes(agent.agent_type))
    },
    {
      id: 'specialized',
      name: 'Specialized',
      description: 'Domain-specific expert agents',
      agents: agents.filter(agent => ['research', 'communication'].includes(agent.agent_type))
    }
  ]

  const getAgentIcon = (type) => {
    switch (type) {
      case 'executor': return Bot
      case 'planning': return Brain
      case 'knowledge': return Search
      case 'content': return FileText
      case 'image': return Image
      case 'video': return Video
      case 'code': return Code
      case 'data': return BarChart3
      case 'web': return Globe
      case 'research': return FileText
      case 'communication': return Users
      default: return Bot
    }
  }

  const getAgentColor = (type) => {
    switch (type) {
      case 'executor': return 'bg-blue-500'
      case 'planning': return 'bg-purple-500'
      case 'knowledge': return 'bg-green-500'
      case 'content': return 'bg-orange-500'
      case 'image': return 'bg-pink-500'
      case 'video': return 'bg-red-500'
      case 'code': return 'bg-indigo-500'
      case 'data': return 'bg-yellow-500'
      case 'web': return 'bg-cyan-500'
      case 'research': return 'bg-teal-500'
      case 'communication': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  const getSubscriptionAccess = (agentType) => {
    const freeAgents = ['executor', 'planning', 'knowledge', 'content']
    const premiumAgents = ['image', 'video', 'code', 'data']
    const enterpriseAgents = ['web', 'research', 'communication']

    if (freeAgents.includes(agentType)) return 'free'
    if (premiumAgents.includes(agentType)) return 'premium'
    if (enterpriseAgents.includes(agentType)) return 'enterprise'
    return 'enterprise'
  }

  const canAccessAgent = (agentType) => {
    const requiredTier = getSubscriptionAccess(agentType)
    const userTier = user?.subscription_type || 'free'

    if (requiredTier === 'free') return true
    if (requiredTier === 'premium' && ['premium', 'enterprise'].includes(userTier)) return true
    if (requiredTier === 'enterprise' && userTier === 'enterprise') return true
    return false
  }

  const getAccessBadge = (agentType) => {
    const tier = getSubscriptionAccess(agentType)
    const colors = {
      free: 'bg-green-100 text-green-800',
      premium: 'bg-blue-100 text-blue-800',
      enterprise: 'bg-purple-100 text-purple-800'
    }
    
    return (
      <Badge variant="secondary" className={colors[tier]}>
        {tier.toUpperCase()}
      </Badge>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">AI Agents</h1>
        <p className="text-muted-foreground">
          Discover and manage your specialized AI agents
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agents.length}</div>
            <p className="text-xs text-muted-foreground">
              Available in your plan
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {agents.filter(a => a.status === 'active').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently running
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Accessible</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {agents.filter(a => canAccessAgent(a.agent_type)).length}
            </div>
            <p className="text-xs text-muted-foreground">
              With your subscription
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Efficiency</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94%</div>
            <p className="text-xs text-muted-foreground">
              Average success rate
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Agent Categories */}
      <Tabs defaultValue="core" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          {agentCategories.map((category) => (
            <TabsTrigger key={category.id} value={category.id}>
              {category.name}
            </TabsTrigger>
          ))}
        </TabsList>

        {agentCategories.map((category) => (
          <TabsContent key={category.id} value={category.id} className="space-y-4">
            <div className="text-center mb-6">
              <h2 className="text-xl font-semibold">{category.name}</h2>
              <p className="text-muted-foreground">{category.description}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {category.agents.map((agent) => {
                const AgentIcon = getAgentIcon(agent.agent_type)
                const isAccessible = canAccessAgent(agent.agent_type)
                
                return (
                  <Card 
                    key={agent.id} 
                    className={`hover:shadow-lg transition-shadow cursor-pointer ${
                      !isAccessible ? 'opacity-60' : ''
                    }`}
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className={`w-12 h-12 rounded-lg ${getAgentColor(agent.agent_type)} flex items-center justify-center`}>
                          <AgentIcon className="h-6 w-6 text-white" />
                        </div>
                        {getAccessBadge(agent.agent_type)}
                      </div>
                      <CardTitle className="text-lg">{agent.name}</CardTitle>
                      <CardDescription className="text-sm">
                        {agent.description}
                      </CardDescription>
                    </CardHeader>
                    
                    <CardContent className="space-y-4">
                      {/* Capabilities */}
                      <div>
                        <h4 className="text-sm font-medium mb-2">Capabilities</h4>
                        <div className="flex flex-wrap gap-1">
                          {agent.capabilities?.slice(0, 3).map((capability, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {capability}
                            </Badge>
                          ))}
                          {agent.capabilities?.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{agent.capabilities.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* Performance Metrics */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span>Success Rate</span>
                          <span>{agent.success_rate || 95}%</span>
                        </div>
                        <Progress value={agent.success_rate || 95} className="h-2" />
                      </div>

                      {/* Status and Actions */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          {agent.status === 'active' ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <Clock className="h-4 w-4 text-gray-600" />
                          )}
                          <span className="text-xs text-muted-foreground">
                            {agent.status === 'active' ? 'Ready' : 'Standby'}
                          </span>
                        </div>
                        
                        {isAccessible ? (
                          <Button size="sm" variant="outline">
                            Use Agent
                          </Button>
                        ) : (
                          <Button size="sm" variant="outline" disabled>
                            Upgrade Required
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>
        ))}
      </Tabs>

      {/* Agent Performance Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Performance Overview</CardTitle>
          <CardDescription>
            Real-time metrics and system status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Cpu className="h-5 w-5 text-blue-600" />
                <span className="font-medium">System Load</span>
              </div>
              <Progress value={68} className="w-full" />
              <p className="text-xs text-muted-foreground">68% - Optimal performance</p>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Database className="h-5 w-5 text-green-600" />
                <span className="font-medium">Memory Usage</span>
              </div>
              <Progress value={45} className="w-full" />
              <p className="text-xs text-muted-foreground">45% - Efficient allocation</p>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Network className="h-5 w-5 text-purple-600" />
                <span className="font-medium">Network Latency</span>
              </div>
              <Progress value={25} className="w-full" />
              <p className="text-xs text-muted-foreground">25ms - Excellent response</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Upgrade Prompt for Free Users */}
      {user?.subscription_type === 'free' && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
                <Star className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-blue-900">Unlock More AI Agents</h3>
                <p className="text-sm text-blue-700">
                  Upgrade to Premium or Enterprise to access advanced agents for image generation, 
                  video creation, code development, and more.
                </p>
              </div>
              <Button className="bg-blue-600 hover:bg-blue-700">
                Upgrade Now
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default AgentsPage

