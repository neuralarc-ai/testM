import React, { useState, useEffect } from 'react'
import { useTask } from '../contexts/TaskContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Plus,
  Search,
  Filter,
  MoreVertical,
  Play,
  Pause,
  Square,
  Trash2,
  Eye,
  Download,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Bot,
  Image,
  Video,
  FileText,
  Code,
  BarChart3,
  Loader2,
} from 'lucide-react'

const TasksPage = () => {
  const { 
    tasks, 
    loading, 
    createTask, 
    updateTask, 
    deleteTask, 
    cancelTask, 
    loadTasks,
    getAgentRecommendations 
  } = useTask()
  
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [selectedTask, setSelectedTask] = useState(null)
  const [showTaskDetails, setShowTaskDetails] = useState(false)
  
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    task_type: '',
    priority: 'medium',
    parameters: {},
  })

  const taskTypes = [
    { value: 'image', label: 'Image Generation', icon: Image, description: 'Create custom images and graphics' },
    { value: 'video', label: 'Video Creation', icon: Video, description: 'Generate videos and animations' },
    { value: 'slides', label: 'Presentation', icon: FileText, description: 'Build slide presentations' },
    { value: 'webpage', label: 'Web Development', icon: Code, description: 'Create websites and web apps' },
    { value: 'analysis', label: 'Data Analysis', icon: BarChart3, description: 'Process and analyze data' },
    { value: 'research', label: 'Research', icon: FileText, description: 'Conduct research and summarization' },
    { value: 'code', label: 'Code Generation', icon: Code, description: 'Generate and debug code' },
    { value: 'audio', label: 'Audio Processing', icon: Bot, description: 'Create and process audio content' },
  ]

  const priorities = [
    { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-800' },
    { value: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-800' },
    { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800' },
    { value: 'urgent', label: 'Urgent', color: 'bg-red-100 text-red-800' },
  ]

  const statuses = [
    { value: 'all', label: 'All Tasks' },
    { value: 'pending', label: 'Pending' },
    { value: 'running', label: 'Running' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' },
    { value: 'cancelled', label: 'Cancelled' },
  ]

  useEffect(() => {
    loadTasks()
  }, [])

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || task.status === statusFilter
    const matchesType = typeFilter === 'all' || task.task_type === typeFilter
    
    return matchesSearch && matchesStatus && matchesType
  })

  const handleCreateTask = async () => {
    if (!newTask.title || !newTask.task_type) {
      return
    }

    const result = await createTask(newTask)
    if (result.success) {
      setShowCreateDialog(false)
      setNewTask({
        title: '',
        description: '',
        task_type: '',
        priority: 'medium',
        parameters: {},
      })
    }
  }

  const handleTaskAction = async (taskId, action) => {
    switch (action) {
      case 'cancel':
        await cancelTask(taskId)
        break
      case 'delete':
        await deleteTask(taskId)
        break
      case 'view':
        const task = tasks.find(t => t.id === taskId)
        setSelectedTask(task)
        setShowTaskDetails(true)
        break
      default:
        break
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'running': return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
      case 'failed': return <XCircle className="h-4 w-4 text-red-600" />
      case 'cancelled': return <XCircle className="h-4 w-4 text-gray-600" />
      case 'pending': return <Clock className="h-4 w-4 text-yellow-600" />
      default: return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'running': return 'bg-blue-100 text-blue-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'cancelled': return 'bg-gray-100 text-gray-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTaskTypeIcon = (type) => {
    const taskType = taskTypes.find(t => t.value === type)
    return taskType ? taskType.icon : Bot
  }

  const getProgressValue = (task) => {
    switch (task.status) {
      case 'completed': return 100
      case 'running': return task.progress || 50
      case 'failed': return 0
      case 'cancelled': return 0
      default: return 0
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tasks</h1>
          <p className="text-muted-foreground">
            Manage and monitor your AI agent tasks
          </p>
        </div>
        
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button size="lg" className="gap-2">
              <Plus className="h-5 w-5" />
              New Task
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Task</DialogTitle>
              <DialogDescription>
                Choose a task type and provide details for your AI agent
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="task-type">Task Type</Label>
                <Select value={newTask.task_type} onValueChange={(value) => 
                  setNewTask(prev => ({ ...prev, task_type: value }))
                }>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a task type" />
                  </SelectTrigger>
                  <SelectContent>
                    {taskTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        <div className="flex items-center space-x-2">
                          <type.icon className="h-4 w-4" />
                          <div>
                            <div className="font-medium">{type.label}</div>
                            <div className="text-xs text-muted-foreground">{type.description}</div>
                          </div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  placeholder="Enter task title"
                  value={newTask.title}
                  onChange={(e) => setNewTask(prev => ({ ...prev, title: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe what you want the AI to do..."
                  value={newTask.description}
                  onChange={(e) => setNewTask(prev => ({ ...prev, description: e.target.value }))}
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Select value={newTask.priority} onValueChange={(value) => 
                  setNewTask(prev => ({ ...prev, priority: value }))
                }>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {priorities.map((priority) => (
                      <SelectItem key={priority.value} value={priority.value}>
                        <Badge variant="secondary" className={priority.color}>
                          {priority.label}
                        </Badge>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateTask} disabled={!newTask.title || !newTask.task_type}>
                  Create Task
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tasks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {statuses.map((status) => (
                  <SelectItem key={status.value} value={status.value}>
                    {status.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {taskTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tasks List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : filteredTasks.length > 0 ? (
          filteredTasks.map((task) => {
            const TaskIcon = getTaskTypeIcon(task.task_type)
            const priority = priorities.find(p => p.value === task.priority)
            
            return (
              <Card key={task.id} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center">
                        <TaskIcon className="h-6 w-6" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className="font-semibold truncate">{task.title}</h3>
                          <Badge variant="secondary" className={priority?.color}>
                            {priority?.label}
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                          {task.description}
                        </p>
                        
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                          <span>Created {new Date(task.created_at).toLocaleDateString()}</span>
                          <span>•</span>
                          <span>{task.estimated_credits} credits</span>
                          {task.agent_name && (
                            <>
                              <span>•</span>
                              <span>Agent: {task.agent_name}</span>
                            </>
                          )}
                        </div>
                        
                        {task.status === 'running' && (
                          <div className="mt-2">
                            <Progress value={getProgressValue(task)} className="w-full h-2" />
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <div className="flex items-center space-x-1">
                        {getStatusIcon(task.status)}
                        <Badge variant="secondary" className={getStatusColor(task.status)}>
                          {task.status}
                        </Badge>
                      </div>
                      
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleTaskAction(task.id, 'view')}>
                            <Eye className="mr-2 h-4 w-4" />
                            View Details
                          </DropdownMenuItem>
                          {task.status === 'running' && (
                            <DropdownMenuItem onClick={() => handleTaskAction(task.id, 'cancel')}>
                              <Square className="mr-2 h-4 w-4" />
                              Cancel
                            </DropdownMenuItem>
                          )}
                          {task.status === 'completed' && task.output_files?.length > 0 && (
                            <DropdownMenuItem>
                              <Download className="mr-2 h-4 w-4" />
                              Download Results
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem 
                            onClick={() => handleTaskAction(task.id, 'delete')}
                            className="text-red-600"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })
        ) : (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <Bot className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No tasks found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
                    ? 'Try adjusting your filters'
                    : 'Create your first task to get started'
                  }
                </p>
                {!searchTerm && statusFilter === 'all' && typeFilter === 'all' && (
                  <Button onClick={() => setShowCreateDialog(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Task
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Task Details Dialog */}
      <Dialog open={showTaskDetails} onOpenChange={setShowTaskDetails}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>{selectedTask?.title}</DialogTitle>
            <DialogDescription>
              Task details and execution information
            </DialogDescription>
          </DialogHeader>
          
          {selectedTask && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium">Status</Label>
                    <div className="flex items-center space-x-2 mt-1">
                      {getStatusIcon(selectedTask.status)}
                      <Badge className={getStatusColor(selectedTask.status)}>
                        {selectedTask.status}
                      </Badge>
                    </div>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium">Type</Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      {taskTypes.find(t => t.value === selectedTask.task_type)?.label}
                    </p>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium">Priority</Label>
                    <Badge 
                      variant="secondary" 
                      className={priorities.find(p => p.value === selectedTask.priority)?.color}
                    >
                      {priorities.find(p => p.value === selectedTask.priority)?.label}
                    </Badge>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium">Created</Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      {new Date(selectedTask.created_at).toLocaleString()}
                    </p>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium">Credits</Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      {selectedTask.estimated_credits} estimated
                    </p>
                  </div>
                  
                  {selectedTask.agent_name && (
                    <div>
                      <Label className="text-sm font-medium">Agent</Label>
                      <p className="text-sm text-muted-foreground mt-1">
                        {selectedTask.agent_name}
                      </p>
                    </div>
                  )}
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium">Description</Label>
                <p className="text-sm text-muted-foreground mt-1">
                  {selectedTask.description}
                </p>
              </div>
              
              {selectedTask.status === 'running' && (
                <div>
                  <Label className="text-sm font-medium">Progress</Label>
                  <Progress value={getProgressValue(selectedTask)} className="w-full mt-2" />
                </div>
              )}
              
              {selectedTask.error_message && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    {selectedTask.error_message}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default TasksPage

