import axios, { AxiosError } from 'axios'
import type {
  LoginRequest,
  LoginResponse,
  ParseTextRequest,
  ParseResponse,
  PredictRequest,
  PredictionResponse,
  EnsemblePredictionResponse,
  ParseAndPredictRequest,
  AvailableModelsResponse,
  ModelInfo,
  HealthResponse,
  MessageResponse,
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  logout: async (): Promise<MessageResponse> => {
    const response = await api.post<MessageResponse>('/auth/logout')
    return response.data
  },

  getMe: async (): Promise<{ username: string }> => {
    const response = await api.get('/auth/me')
    return response.data
  },
}

// Parse API
export const parseAPI = {
  parseText: async (data: ParseTextRequest): Promise<ParseResponse> => {
    const response = await api.post<ParseResponse>('/parse', data)
    return response.data
  },
}

// Predict API
export const predictAPI = {
  predict: async (
    data: PredictRequest
  ): Promise<PredictionResponse | EnsemblePredictionResponse> => {
    const response = await api.post<PredictionResponse | EnsemblePredictionResponse>(
      '/predict',
      data
    )
    return response.data
  },

  parseAndPredict: async (
    data: ParseAndPredictRequest
  ): Promise<PredictionResponse | EnsemblePredictionResponse> => {
    const response = await api.post<PredictionResponse | EnsemblePredictionResponse>(
      '/parse-and-predict',
      data
    )
    return response.data
  },
}

// Models API
export const modelsAPI = {
  getAvailableModels: async (): Promise<AvailableModelsResponse> => {
    const response = await api.get<AvailableModelsResponse>('/models')
    return response.data
  },

  getModelInfo: async (modelName: string): Promise<ModelInfo> => {
    const response = await api.get<ModelInfo>(`/models/${modelName}`)
    return response.data
  },

  getModelMetadata: async (modelName?: string): Promise<any> => {
    const endpoint = modelName ? `/models/${modelName}/metadata` : '/models/metadata'
    const response = await api.get(endpoint)
    return response.data
  },
}

// Health API
export const healthAPI = {
  check: async (): Promise<HealthResponse> => {
    const response = await api.get<HealthResponse>('/health')
    return response.data
  },
}

// Error helper
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail || error.message || 'An error occurred'
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unknown error occurred'
}
