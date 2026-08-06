import api from "./client";
import { ApiResponse } from "../types/api";

export const uploadReport = async (file: File, patientContext?: Record<string, any>): Promise<ApiResponse<any>> => {
  const formData = new FormData();
  formData.append("file", file);

  if (patientContext) {
    formData.append("patient_context_json", JSON.stringify(patientContext));
  }

  const response = await api.post<ApiResponse<any>>("/upload/report", formData);
  return response.data;
};
