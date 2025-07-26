import React, { createContext, useContext, useState, useEffect } from 'react'
import { toast } from 'sonner'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api'

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  // API helper function
  const apiCall = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'An error occurred')
      }

      return data
    } catch (error) {
      console.error('API call failed:', error)
      throw error
    }
  }

  // Load user data on mount
  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          const data = await apiCall('/auth/me')
          setUser(data.user)
        } catch (error) {
          console.error('Failed to load user:', error)
          localStorage.removeItem('token')
          setToken(null)
        }
      }
      setLoading(false)
    }

    loadUser()
  }, [token])

  const login = async (email, password) => {
    try {
      const data = await apiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })

      setToken(data.access_token)
      setUser(data.user)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      toast.success('Login successful!')
      return { success: true }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  const register = async (userData) => {
    try {
      const data = await apiCall('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      })

      setToken(data.access_token)
      setUser(data.user)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      toast.success('Registration successful!')
      return { success: true }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  const googleLogin = async (googleToken) => {
    try {
      const data = await apiCall('/auth/google', {
        method: 'POST',
        body: JSON.stringify({ token: googleToken }),
      })

      setToken(data.access_token)
      setUser(data.user)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      toast.success('Google login successful!')
      return { success: true }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    toast.success('Logged out successfully')
  }

  const updateProfile = async (profileData) => {
    try {
      const data = await apiCall('/auth/update-profile', {
        method: 'PUT',
        body: JSON.stringify(profileData),
      })

      setUser(data.user)
      toast.success('Profile updated successfully!')
      return { success: true }
    } catch (error) {
      toast.error(error.message)
      return { success: false, error: error.message }
    }
  }

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) throw new Error('No refresh token')

      const data = await apiCall('/auth/refresh', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${refreshToken}`,
        },
      })

      setToken(data.access_token)
      setUser(data.user)
      localStorage.setItem('token', data.access_token)
      
      return { success: true }
    } catch (error) {
      logout()
      return { success: false, error: error.message }
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    googleLogin,
    logout,
    updateProfile,
    refreshToken,
    apiCall,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

