import React, { createContext, useContext, useState, useEffect } from 'react';
import { orchestrationAPI, tasksAPI } from '../services/api';

const TaskContext = createContext({});

export const useTask = () => {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error('useTask must be used within a TaskProvider');
  }
  return context;
};

export const TaskProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [orchestrationTasks, setOrchestrationTasks] = useState([]);
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Load initial data
  useEffect(() => {
    loadTemplates();
    loadTasks();
    loadOrchestrationTasks();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await orchestrationAPI.getTemplates();
      if (response.success) {
        setTemplates(response.templates);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await tasksAPI.getTasks();
      if (response.success) {
        setTasks(response.tasks);
      }
    } catch (error) {
      console.error('Error loading tasks:', error);
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const loadOrchestrationTasks = async () => {
    try {
      const response = await orchestrationAPI.getTasks();
      if (response.success) {
        setOrchestrationTasks(response.tasks);
      }
    } catch (error) {
      console.error('Error loading orchestration tasks:', error);
    }
  };

  const refreshTasks = async () => {
    try {
      setRefreshing(true);
      await Promise.all([
        loadTasks(),
        loadOrchestrationTasks()
      ]);
    } finally {
      setRefreshing(false);
    }
  };

  const createTask = async (taskData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await tasksAPI.createTask(taskData);
      
      if (response.success) {
        // Add new task to the list
        setTasks(prevTasks => [response.task, ...prevTasks]);
        return { success: true, task: response.task };
      } else {
        setError(response.error || 'Failed to create task');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const createTaskFromTemplate = async (templateName, parameters) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await orchestrationAPI.createTaskFromTemplate(templateName, parameters);
      
      if (response.success) {
        // Refresh orchestration tasks
        await loadOrchestrationTasks();
        return { success: true, taskId: response.task_id };
      } else {
        setError(response.error || 'Failed to create task from template');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const createCustomTask = async (taskData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await orchestrationAPI.createCustomTask(taskData);
      
      if (response.success) {
        // Refresh orchestration tasks
        await loadOrchestrationTasks();
        return { success: true, taskId: response.task_id };
      } else {
        setError(response.error || 'Failed to create custom task');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const getTask = async (taskId) => {
    try {
      const response = await tasksAPI.getTask(taskId);
      if (response.success) {
        return { success: true, task: response.task };
      } else {
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      return { success: false, error: errorMessage };
    }
  };

  const getOrchestrationTask = async (taskId) => {
    try {
      const response = await orchestrationAPI.getTask(taskId);
      if (response.success) {
        return { success: true, task: response.task };
      } else {
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      return { success: false, error: errorMessage };
    }
  };

  const updateTask = async (taskId, taskData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await tasksAPI.updateTask(taskId, taskData);
      
      if (response.success) {
        // Update task in the list
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === taskId ? { ...task, ...response.task } : task
          )
        );
        return { success: true, task: response.task };
      } else {
        setError(response.error || 'Failed to update task');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await tasksAPI.deleteTask(taskId);
      
      if (response.success) {
        // Remove task from the list
        setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
        return { success: true };
      } else {
        setError(response.error || 'Failed to delete task');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const executeTask = async (taskId) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await tasksAPI.executeTask(taskId);
      
      if (response.success) {
        // Update task status
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === taskId ? { ...task, status: 'running' } : task
          )
        );
        return { success: true };
      } else {
        setError(response.error || 'Failed to execute task');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const cancelTask = async (taskId) => {
    try {
      const response = await orchestrationAPI.cancelTask(taskId);
      
      if (response.success) {
        // Update task status
        setOrchestrationTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === taskId ? { ...task, status: 'cancelled' } : task
          )
        );
        return { success: true };
      } else {
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      return { success: false, error: errorMessage };
    }
  };

  const pauseTask = async (taskId) => {
    try {
      const response = await orchestrationAPI.pauseTask(taskId);
      
      if (response.success) {
        // Update task status
        setOrchestrationTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === taskId ? { ...task, status: 'paused' } : task
          )
        );
        return { success: true };
      } else {
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      return { success: false, error: errorMessage };
    }
  };

  const resumeTask = async (taskId) => {
    try {
      const response = await orchestrationAPI.resumeTask(taskId);
      
      if (response.success) {
        // Update task status
        setOrchestrationTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === taskId ? { ...task, status: 'running' } : task
          )
        );
        return { success: true };
      } else {
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      return { success: false, error: errorMessage };
    }
  };

  const getTaskStatus = async (taskId) => {
    try {
      const response = await orchestrationAPI.getTaskStatus(taskId);
      if (response.success) {
        return { success: true, status: response.status };
      } else {
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Network error';
      return { success: false, error: errorMessage };
    }
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    tasks,
    orchestrationTasks,
    templates,
    loading,
    error,
    refreshing,
    loadTasks,
    loadOrchestrationTasks,
    refreshTasks,
    createTask,
    createTaskFromTemplate,
    createCustomTask,
    getTask,
    getOrchestrationTask,
    updateTask,
    deleteTask,
    executeTask,
    cancelTask,
    pauseTask,
    resumeTask,
    getTaskStatus,
    clearError,
  };

  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  );
};

