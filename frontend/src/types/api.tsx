export type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T | null;
};

export type AuthToken = {
  access_token: string;
  token_type: string;
  user: User;
};

export type User = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
};

export type Patient = {
  id: number;
  doctor_id: number;
  first_name: string;
  last_name: string;
  age: number;
  gender: string;
  medical_history?: Record<string, any>;
  allergies?: string[];
  current_medications?: string[];
  created_at: string;
};

export type StrokePredictionRequest = {
  age?: number;
  hypertension?: number;
  heart_disease?: number;
  avg_glucose_level?: number;
  bmi?: number;
  smoking_status?: string;
  name?: string;
};

export type StrokePredictionResponse = {
  success: boolean;
  disease: string;
  prediction: number;
  probability: number;
  confidence: number;
  confidence_label: string;
  class_probabilities: Record<string, number>;
  explanations: Array<Record<string, any>>;
  fallback_reason?: string;
  recommendations?: Array<Record<string, any>>;
  report?: Record<string, any>;
};

export type HealthStatus = {
  status: string;
  service: string;
  model_loaded?: boolean;
  model_directory?: string;
};
