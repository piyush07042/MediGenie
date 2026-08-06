export type LoginFormValues = {
  email: string;
  password: string;
};

export type RegisterFormValues = {
  email: string;
  password: string;
  full_name: string;
};

export type PatientFormValues = {
  first_name: string;
  last_name: string;
  age: number;
  gender: string;
  allergies: string;
  current_medications: string;
  medical_history: string;
};

export type StrokeFormValues = {
  age: number;
  hypertension: number;
  heart_disease: number;
  avg_glucose_level: number;
  bmi: number;
  smoking_status: string;
  name: string;
};

export type DrugSafetyFormValues = {
  medications: string;
  allergies: string;
};

export type ChatFormValues = {
  message: string;
};
