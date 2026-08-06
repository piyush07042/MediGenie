import api from "./client";
import { ApiResponse } from "../types/api";

export type DrugSafetyPayload = {
  medications: string[];
  allergies?: string[];
};

export type DrugSafetyAssessment = {
  id: number;
  created_at: string;
  assessment: string;
};

export const analyzeDrugSafety = async (payload: DrugSafetyPayload): Promise<ApiResponse<string>> => {
  const response = await api.post<ApiResponse<string>>("/drug-safety/analyze", payload);
  return response.data;
};

export const getDrugSafetyForPatient = async (patientId: number): Promise<ApiResponse<DrugSafetyAssessment[]>> => {
  const response = await api.get<ApiResponse<DrugSafetyAssessment[]>>(`/drug-safety/patient/${patientId}`);
  return response.data;
};
