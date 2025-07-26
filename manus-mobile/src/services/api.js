import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Base URL for the API - Update this to your backend URL
const BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear storage and redirect to login
      await AsyncStorage.removeItem('authToken');
      await AsyncStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  updateProfile: async (userData) => {
    const response = await api.put('/auth/profile', userData);
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getProfile: async () => {
    const response = await api.get('/users/profile');
    return response.data;
  },

  updateProfile: async (userData) => {
    const response = await api.put('/users/profile', userData);
    return response.data;
  },

  getCredits: async () => {
    const response = await api.get('/users/credits');
    return response.data;
  },

  getSubscription: async () => {
    const response = await api.get('/users/subscription');
    return response.data;
  },

  updateSubscription: async (plan) => {
    const response = await api.put('/users/subscription', { plan });
    return response.data;
  },
};

// Tasks API
export const tasksAPI = {
  getTasks: async (page = 1, limit = 20) => {
    const response = await api.get(`/tasks?page=${page}&limit=${limit}`);
    return response.data;
  },

  getTask: async (taskId) => {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  },

  createTask: async (taskData) => {
    const response = await api.post('/tasks', taskData);
    return response.data;
  },

  updateTask: async (taskId, taskData) => {
    const response = await api.put(`/tasks/${taskId}`, taskData);
    return response.data;
  },

  deleteTask: async (taskId) => {
    const response = await api.delete(`/tasks/${taskId}`);
    return response.data;
  },

  executeTask: async (taskId) => {
    const response = await api.post(`/tasks/${taskId}/execute`);
    return response.data;
  },

  getTaskStats: async () => {
    const response = await api.get('/tasks/stats');
    return response.data;
  },
};

// Agents API
export const agentsAPI = {
  getAgents: async () => {
    const response = await api.get('/agents');
    return response.data;
  },

  getAgent: async (agentId) => {
    const response = await api.get(`/agents/${agentId}`);
    return response.data;
  },

  getAgentRecommendations: async (taskType) => {
    const response = await api.get(`/agents/recommendations?task_type=${taskType}`);
    return response.data;
  },

  executeAgentTask: async (agentId, taskData) => {
    const response = await api.post(`/agents/${agentId}/execute`, taskData);
    return response.data;
  },
};

// Content API
export const contentAPI = {
  getContent: async (page = 1, limit = 20) => {
    const response = await api.get(`/content?page=${page}&limit=${limit}`);
    return response.data;
  },

  uploadContent: async (formData) => {
    const response = await api.post('/content/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deleteContent: async (contentId) => {
    const response = await api.delete(`/content/${contentId}`);
    return response.data;
  },

  getContentStats: async () => {
    const response = await api.get('/content/stats');
    return response.data;
  },
};

// Computer API
export const computerAPI = {
  createSession: async (sessionName) => {
    const response = await api.post('/computer/sessions', { session_name: sessionName });
    return response.data;
  },

  getSessions: async () => {
    const response = await api.get('/computer/sessions');
    return response.data;
  },

  automateTask: async (sessionId, taskDescription, url) => {
    const response = await api.post(`/computer/sessions/${sessionId}/automate`, {
      task_description: taskDescription,
      url: url,
    });
    return response.data;
  },

  getSessionStatus: async (sessionId) => {
    const response = await api.get(`/computer/sessions/${sessionId}/status`);
    return response.data;
  },
};

// Media API
export const mediaAPI = {
  generatePresentation: async (data) => {
    const response = await api.post('/media/presentations', data);
    return response.data;
  },

  generateAIPresentation: async (data) => {
    const response = await api.post('/media/presentations/ai-generate', data);
    return response.data;
  },

  generateDocument: async (data) => {
    const response = await api.post('/media/documents', data);
    return response.data;
  },

  generateAIDocument: async (data) => {
    const response = await api.post('/media/documents/ai-generate', data);
    return response.data;
  },

  generateImage: async (data) => {
    const response = await api.post('/media/images/generate', data);
    return response.data;
  },

  generateSpeech: async (data) => {
    const response = await api.post('/media/audio/generate-speech', data);
    return response.data;
  },

  createInfographic: async (data) => {
    const response = await api.post('/media/infographics', data);
    return response.data;
  },

  generateAIInfographic: async (data) => {
    const response = await api.post('/media/infographics/ai-generate', data);
    return response.data;
  },
};

// Orchestration API
export const orchestrationAPI = {
  getTemplates: async () => {
    const response = await api.get('/orchestration/tasks/templates');
    return response.data;
  },

  createTaskFromTemplate: async (templateName, parameters) => {
    const response = await api.post('/orchestration/tasks/create-from-template', {
      template_name: templateName,
      parameters: parameters,
    });
    return response.data;
  },

  createCustomTask: async (taskData) => {
    const response = await api.post('/orchestration/tasks/create-custom', taskData);
    return response.data;
  },

  getTask: async (taskId) => {
    const response = await api.get(`/orchestration/tasks/${taskId}`);
    return response.data;
  },

  getTasks: async () => {
    const response = await api.get('/orchestration/tasks');
    return response.data;
  },

  getTaskStatus: async (taskId) => {
    const response = await api.get(`/orchestration/tasks/${taskId}/status`);
    return response.data;
  },

  cancelTask: async (taskId) => {
    const response = await api.post(`/orchestration/tasks/${taskId}/cancel`);
    return response.data;
  },

  pauseTask: async (taskId) => {
    const response = await api.post(`/orchestration/tasks/${taskId}/pause`);
    return response.data;
  },

  resumeTask: async (taskId) => {
    const response = await api.post(`/orchestration/tasks/${taskId}/resume`);
    return response.data;
  },

  getQueueStatus: async () => {
    const response = await api.get('/orchestration/queue/status');
    return response.data;
  },
};

export default api;

