// User types
export type UserRole = "admin" | "doctor" | "nurse";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  department?: string;
  is_active: boolean;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  full_name: string;
  role: UserRole;
}

// Patient types
export interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  gender?: string;
  mrn?: string;
  phone_number?: string;
  email?: string;
  address?: string;
  created_at: string;
  updated_at?: string;
}

export interface ClinicalData {
  id: string;
  patient_id: string;
  timestamp: string;
  heart_rate?: number;
  respiratory_rate?: number;
  temperature?: number;
  systolic_bp?: number;
  diastolic_bp?: number;
  oxygen_saturation?: number;
  blood_glucose?: number;
  wbc_count?: number;
  platelet_count?: number;
  lactate?: number;
  creatinine?: number;
  bilirubin?: number;
  created_at: string;
}

export interface PatientSummary {
  patient: Patient;
  latest_vitals: Record<string, any>;
  recent_clinical_data: ClinicalData[];
  sepsis_predictions: SepsisPrediction[];
  latest_prediction?: SepsisPrediction;
  active_alerts: Alert[];
  alert_count: number;
}

// Prediction types
export interface ShapExplanation {
  features: string[];
  shap_values: number[];
  base_value: number;
}

export interface SepsisPrediction {
  id: string;
  patient_id: string;
  probability: number;
  is_sepsis_risk: boolean;
  features_used: Record<string, any>;
  model_version: string;
  timestamp: string;
  explanation?: ShapExplanation;
}

export interface RiskFactor {
  feature_name: string;
  value: number;
  impact: number;
  impact_type: "risk_factor" | "protective_factor";
  contribution_pct: number;
}

// Alert types
export type AlertStatus =
  | "pending"
  | "acknowledged"
  | "action_taken"
  | "dismissed";

export interface Alert {
  id: string;
  patient_id: string;
  prediction_id: string;
  alert_type: string;
  severity: number; // 1-5, 5 being most severe
  status: AlertStatus;
  message: string;
  created_at: string;
  acknowledged_at?: string;
  acknowledged_by?: string;
  patient?: {
    id: string;
    first_name: string;
    last_name: string;
    mrn?: string;
  };
}

// Feedback types
export type FeedbackType =
  | "correct"
  | "false_positive"
  | "false_negative"
  | "unsure";

export interface Feedback {
  id: string;
  prediction_id: string;
  user_id: string;
  feedback_type: FeedbackType;
  comments?: string;
  created_at: string;
  user_name?: string;
}
