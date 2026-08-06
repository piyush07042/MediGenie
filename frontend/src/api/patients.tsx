import axios from "axios";
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

export type UpdatePatientPayload = Partial<CreatePatientPayload>;

export const listPatients = async (): Promise<ApiResponse<Patient[]>> => {
  const response = await api.get<ApiResponse<Patient[]>>("/patients/");
  return response.data;
};

export const createPatient = async (payload: CreatePatientPayload): Promise<ApiResponse<Patient>> => {
  const response = await api.post<ApiResponse<Patient>>("/patients/", payload);
  return response.data;
};

export const getPatientDetails = async (patientId: number): Promise<Patient | null> => {
  try {
    const response = await api.get<ApiResponse<Patient>>(`/patients/${patientId}`);
    return response.data.data;
  } catch (error) {
    if (axios.isAxiosError(error) && [404, 405].includes(error.response?.status ?? 0)) {
      const list = await listPatients();
      return list.data?.find((patient) => patient.id === patientId) ?? null;
    }
    throw error;
  }
};

export const updatePatient = async (
  patientId: number,
  payload: UpdatePatientPayload
): Promise<ApiResponse<Patient>> => {
  const response = await api.put<ApiResponse<Patient>>(`/patients/${patientId}`, payload);
  return response.data;
};

export const deletePatient = async (patientId: number): Promise<ApiResponse<null>> => {
  const response = await api.delete<ApiResponse<null>>(`/patients/${patientId}`);
  return response.data;
};
