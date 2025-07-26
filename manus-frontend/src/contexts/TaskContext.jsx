import React, { createContext, useContext, useState, useEffect } from 'react'
import { useAuth } from './AuthContext'
import { toast } from 'sonner'

const TaskContext = createContext()

export const useTask = () => {
  const context = useContext(TaskContext)
  if (!context) {
    throw new Error('useTask must be used within a TaskProvider')
  }
  return context
}

export const TaskProvider = ({ children }) => {
  const { apiCall, user } = useAuth()
  const [tasks, setTasks] = useState([])
  const [agents, setAgents] = useState([])
  const [content, setContent] = useState([])
  const [loading, setLoading] = useState(false)
  const [taskStats, setTaskStats] = useState({})

  // Load tasks
  const loadTasks = async (filters = {}) => {
    try {
      setLoading(true)
      const params = new URLSearchParams(filters).toString()
      const data = await apiCall(`/tasks?${params}`)
      setTasks(data.tasks)
      return data
    } catch (error) {
      toast.error('Failed to load tasks')
      console.error('Load tasks error:', error)
    } finally {
      setLoading(false)
    }
  }

  // Create new task
  const createTask = async (taskData) => {
    try {
      const data = await apiCall('/tasks', {
        method: 'POST',
        body: JSON.stringify(taskData),
      })

      setTasks(prev => [data.task, ...prev])
      toast.success('Task created successfully!')
      return { success: true, task: data.task }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  // Update task
  const updateTask = async (taskId, updates) => {
    try {
      const data = await apiCall(`/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      })

      setTasks(prev => prev.map(task => 
        task.id === taskId ? data.task : task
      ))
      toast.success('Task updated successfully!')
      return { success: true, task: data.task }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  // Delete task
  const deleteTask = async (taskId) => {
    try {
      await apiCall(`/tasks/${taskId}`, {
        method: 'DELETE',
      })

      setTasks(prev => prev.filter(task => task.id !== taskId))
      toast.success('Task deleted successfully!')
      return { success: true }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  // Cancel task
  const cancelTask = async (taskId) => {
    try {
      const data = await apiCall(`/tasks/${taskId}/cancel`, {
        method: 'POST',
      })

      setTasks(prev => prev.map(task => 
        task.id === taskId ? data.task : task
      ))
      toast.success('Task cancelled successfully!')
      return { success: true, task: data.task }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  // Load agents
  const loadAgents = async () => {
    try {
      const data = await apiCall('/agents')
      setAgents(data.agents)
      return data
    } catch (error) {
      toast.error('Failed to load agents')
      console.error('Load agents error:', error)
    }
  }

  // Get agent recommendations
  const getAgentRecommendations = async (taskDescription, taskType) => {
    try {
      const data = await apiCall('/agents/recommend', {
        method: 'POST',
        body: JSON.stringify({
          task_description: taskDescription,
          task_type: taskType,
        }),
      })
      return data.recommended_agents
    } catch (error) {
      toast.error('Failed to get agent recommendations')
      console.error('Agent recommendations error:', error)
      return []
    }
  }

  // Load content
  const loadContent = async (filters = {}) => {
    try {
      const params = new URLSearchParams(filters).toString()
      const data = await apiCall(`/content?${params}`)
      setContent(data.content)
      return data
    } catch (error) {
      toast.error('Failed to load content')
      console.error('Load content error:', error)
    }
  }

  // Upload content
  const uploadContent = async (file, contentType, taskId = null) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('content_type', contentType)
      if (taskId) formData.append('task_id', taskId)

      const data = await apiCall('/content/upload', {
        method: 'POST',
        body: formData,
        headers: {}, // Remove Content-Type to let browser set it for FormData
      })

      setContent(prev => [data.content, ...prev])
      toast.success('File uploaded successfully!')
      return { success: true, content: data.content }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  // Delete content
  const deleteContent = async (contentId) => {
    try {
      await apiCall(`/content/${contentId}`, {
        method: 'DELETE',
      })

      setContent(prev => prev.filter(item => item.id !== contentId))
      toast.success('Content deleted successfully!')
      return { success: true }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  // Load task statistics
  const loadTaskStats = async () => {
    try {
      const data = await apiCall('/tasks/stats')
      setTaskStats(data.stats)
      return data.stats
    } catch (error) {
      console.error('Load task stats error:', error)
    }
  }

  // Load initial data when user is available
  useEffect(() => {
    if (user) {
      loadTasks()
      loadAgents()
      loadContent()
      loadTaskStats()
    }
  }, [user])

  const value = {
    tasks,
    agents,
    content,
    taskStats,
    loading,
    loadTasks,
    createTask,
    updateTask,
    deleteTask,
    cancelTask,
    loadAgents,
    getAgentRecommendations,
    loadContent,
    uploadContent,
    deleteContent,
    loadTaskStats,
  }

  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  )
}

