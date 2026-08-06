import api from "./client";
import { ApiResponse, Patient } from "../types/api";

export type CreatePatientPayload = {
  first_name: string;
  last_name: string;
  age: number;
  gender: string;
  medical_history?: Record<string, any>;
  allergies?: string[];
  current_medications?: string[];
};

export const listPatients = async (): Promise<ApiResponse<Patient[]>> => {
  const response = await api.get<ApiResponse<Patient[]>>("/patients/");
  return response.data;
};

export const createPatient = async (payload: CreatePatientPayload): Promise<ApiResponse<Patient>> => {
  const response = await api.post<ApiResponse<Patient>>("/patients/", payload);
  return response.data;
};
