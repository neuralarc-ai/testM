import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useTask } from '../contexts/TaskContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts'
import {
  Plus,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Bot,
  FileText,
  Image,
  Video,
  Code,
  BarChart3,
  Calendar,
  Activity,
} from 'lucide-react'

const DashboardPage = () => {
  const { user } = useAuth()
  const { tasks, taskStats, loadTaskStats, createTask } = useTask()
  const [recentTasks, setRecentTasks] = useState([])

  useEffect(() => {
    loadTaskStats()
    // Get recent tasks (last 5)
    setRecentTasks(tasks.slice(0, 5))
  }, [tasks])

  const quickActions = [
    {
      title: 'Create Presentation',
      description: 'Generate slides with AI',
      icon: FileText,
      color: 'bg-blue-500',
      action: () => createQuickTask('slides'),
    },
    {
      title: 'Generate Image',
      description: 'Create custom visuals',
      icon: Image,
      color: 'bg-green-500',
      action: () => createQuickTask('image'),
    },
    {
      title: 'Build Website',
      description: 'Develop web applications',
      icon: Code,
      color: 'bg-purple-500',
      action: () => createQuickTask('webpage'),
    },
    {
      title: 'Analyze Data',
      description: 'Process and visualize data',
      icon: BarChart3,
      color: 'bg-orange-500',
      action: () => createQuickTask('analysis'),
    },
  ]

  const createQuickTask = (type) => {
    // Navigate to task creation with pre-selected type
    // This would typically open a modal or navigate to tasks page
    console.log(`Creating ${type} task`)
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'running': return 'text-blue-600 bg-blue-100'
      case 'failed': return 'text-red-600 bg-red-100'
      case 'pending': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getTaskIcon = (type) => {
    switch (type) {
      case 'image': return Image
      case 'video': return Video
      case 'slides': return FileText
      case 'webpage': return Code
      case 'analysis': return BarChart3
      default: return Bot
    }
  }

  // Sample data for charts
  const taskTypeData = [
    { name: 'Images', value: taskStats.by_type?.image || 0, color: '#8884d8' },
    { name: 'Videos', value: taskStats.by_type?.video || 0, color: '#82ca9d' },
    { name: 'Slides', value: taskStats.by_type?.slides || 0, color: '#ffc658' },
    { name: 'Webpages', value: taskStats.by_type?.webpage || 0, color: '#ff7300' },
    { name: 'Analysis', value: taskStats.by_type?.analysis || 0, color: '#00ff00' },
  ]

  const weeklyData = [
    { day: 'Mon', tasks: 12 },
    { day: 'Tue', tasks: 19 },
    { day: 'Wed', tasks: 15 },
    { day: 'Thu', tasks: 25 },
    { day: 'Fri', tasks: 22 },
    { day: 'Sat', tasks: 18 },
    { day: 'Sun', tasks: 8 },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Welcome back, {user?.first_name || user?.username}!
          </h1>
          <p className="text-muted-foreground mt-1">
            Here's what's happening with your AI agents today.
          </p>
        </div>
        <Button size="lg" className="gap-2">
          <Plus className="h-5 w-5" />
          New Task
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{taskStats.total || 0}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{taskStats.completed || 0}</div>
            <p className="text-xs text-muted-foreground">
              +8% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{taskStats.running || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active right now
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Credits Used</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{taskStats.credits_used || 0}</div>
            <p className="text-xs text-muted-foreground">
              {user?.credits_balance} remaining
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Start a new task with our most popular AI agents
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <Button
                key={index}
                variant="outline"
                className="h-auto p-4 flex flex-col items-center space-y-2"
                onClick={action.action}
              >
                <div className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center`}>
                  <action.icon className="h-6 w-6 text-white" />
                </div>
                <div className="text-center">
                  <div className="font-medium">{action.title}</div>
                  <div className="text-xs text-muted-foreground">{action.description}</div>
                </div>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Analytics and Recent Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Analytics */}
        <Card>
          <CardHeader>
            <CardTitle>Analytics</CardTitle>
            <CardDescription>
              Your task performance over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="weekly" className="space-y-4">
              <TabsList>
                <TabsTrigger value="weekly">Weekly</TabsTrigger>
                <TabsTrigger value="types">By Type</TabsTrigger>
              </TabsList>
              
              <TabsContent value="weekly" className="space-y-4">
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={weeklyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="tasks" 
                      stroke="#8884d8" 
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </TabsContent>
              
              <TabsContent value="types" className="space-y-4">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={taskTypeData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label
                    >
                      {taskTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Recent Tasks */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Tasks</CardTitle>
            <CardDescription>
              Your latest AI agent activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentTasks.length > 0 ? (
                recentTasks.map((task) => {
                  const TaskIcon = getTaskIcon(task.task_type)
                  return (
                    <div key={task.id} className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                        <TaskIcon className="h-5 w-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {task.title}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(task.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge 
                        variant="secondary" 
                        className={getStatusColor(task.status)}
                      >
                        {task.status}
                      </Badge>
                    </div>
                  )
                })
              ) : (
                <div className="text-center py-8">
                  <Bot className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No tasks yet</p>
                  <p className="text-sm text-muted-foreground">
                    Create your first task to get started
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Credit Usage */}
      <Card>
        <CardHeader>
          <CardTitle>Credit Usage</CardTitle>
          <CardDescription>
            Track your monthly credit consumption
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                Credits Used This Month
              </span>
              <span className="text-sm text-muted-foreground">
                {taskStats.credits_used || 0} / {user?.subscription_type === 'free' ? 300 : user?.subscription_type === 'premium' ? 1000 : 5000}
              </span>
            </div>
            <Progress 
              value={((taskStats.credits_used || 0) / (user?.subscription_type === 'free' ? 300 : user?.subscription_type === 'premium' ? 1000 : 5000)) * 100} 
              className="w-full"
            />
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Resets on {new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1).toLocaleDateString()}</span>
              {user?.subscription_type === 'free' && (
                <Button variant="link" size="sm" className="h-auto p-0">
                  Upgrade for more credits
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default DashboardPage

