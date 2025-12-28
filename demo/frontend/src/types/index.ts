// API Types
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  username: string
}

export interface ParseTextRequest {
  text: string
  verbose?: boolean
}

export interface ParseResponse {
  success: boolean
  features: HouseFeatures
  raw_text: string
}

export interface HouseFeatures {
  City?: string          // Thành phố (Hồ Chí Minh, Hà Nội, Bình Dương, Đà Nẵng)
  Area?: number
  Bedrooms?: number
  Bathrooms?: number
  Floors?: number
  Frontage?: number
  AccessRoad?: number
  District?: string
  Ward?: string
  Street?: string
  Direction?: string
  BalconyDirection?: string
  LegalStatus?: string
  Furniture?: string
  [key: string]: any
}

export interface PredictRequest {
  features: HouseFeatures
  model_name?: string
  use_ensemble?: boolean
}

export interface PredictionResponse {
  prediction: number
  prediction_formatted: string
  confidence: number
  model_used: string
  features_used: HouseFeatures
}

export interface EnsemblePredictionResponse {
  ensemble_prediction: number
  ensemble_prediction_formatted: string
  ensemble_std: number
  confidence: number
  individual_predictions: Record<string, { prediction: number; confidence: number }>
  models_used: string[]
  features_used: HouseFeatures
}

export interface ParseAndPredictRequest {
  text: string
  model_name?: string
  use_ensemble?: boolean
}

export interface ModelInfo {
  name: string
  available: boolean
  metadata: ModelMetadata
}

export interface ModelMetadata {
  name: string
  params: Record<string, any>
  feature_names: string[]
  training_time: number
  timestamp: string
  categorical_values?: {
    directions?: string[]
    balcony_directions?: string[]
    legal_statuses?: string[]
    districts?: string[]
    furniture?: string[]
  }
}

export interface AvailableModelsResponse {
  models: string[]
  default_model: string
}

export interface HealthResponse {
  status: string
  version: string
  models_loaded: number
  llm_available: boolean
}

export interface MessageResponse {
  message: string
}

// UI State Types
export interface User {
  username: string
  token: string
}

export interface LocationInfo {
  lat: number
  lng: number
  address: string
  district?: string
}
