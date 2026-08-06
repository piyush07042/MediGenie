import api from "./client";
import { ApiResponse } from "../types/api";

export type ChatPayload = {
  patient_context?: Record<string, any>;
  message: string;
  symptoms?: string[];
  medications?: string[];
  allergies?: string[];
  report_text?: string;
};

export const sendChat = async (payload: ChatPayload): Promise<ApiResponse<{ reply: string }>> => {
  const response = await api.post<ApiResponse<{ reply: string }>>("/chat/", payload);
  return response.data;
};
