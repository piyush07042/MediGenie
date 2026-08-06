import axios from "axios";
import api from "../api/client";
import type { User } from "../types/api";

export type LoginPayload = {
  email: string;
  password: string;
  rememberMe?: boolean;
};

export type RegisterPayload = {
  email: string;
  password: string;
  full_name: string;
  username?: string;
  role?: string;
};

export type AuthSession = {
  access_token: string;
  token_type: string;
  user: User;
};

export type AuthStateSnapshot = {
  token: string | null;
  user: User | null;
};

type LoginApiResponse = {
  success: boolean;
  message: string;
  access_token: string;
  token_type: string;
  data: {
    access_token: string;
    token_type: string;
    user: User;
  };
};

type RegisterApiResponse = {
  success: boolean;
  message: string;
  data: User;
};

function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail.map((item) => (typeof item === "string" ? item : item.msg ?? "Request failed.")).join(" ");
    }

    if (typeof detail === "object" && detail && "msg" in detail) {
      return String(detail.msg);
    }

    if (error.response?.status === 401) {
      return "Incorrect email or password.";
    }

    if (error.response?.status === 403) {
      return "You are not authorized to perform this action.";
    }

    if (error.response?.status === 500) {
      return "The server is currently unavailable. Please try again shortly.";
    }

    return "Unable to complete the request right now.";
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Unexpected error occurred.";
}

export async function login(payload: LoginPayload): Promise<AuthSession> {
  const form = new URLSearchParams();
  form.append("username", payload.email);
  form.append("password", payload.password);

  try {
    const response = await api.post<LoginApiResponse>("/auth/login", form, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    return {
      access_token: response.data.data.access_token,
      token_type: response.data.data.token_type,
      user: response.data.data.user,
    };
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
}

export async function register(payload: RegisterPayload): Promise<User> {
  try {
    const response = await api.post<RegisterApiResponse>("/auth/register", {
      email: payload.email,
      password: payload.password,
      full_name: payload.full_name,
      role: payload.role ?? "doctor",
    });

    return response.data.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
}

export async function refreshAuth(): Promise<AuthStateSnapshot> {
  const raw = localStorage.getItem("medigenie_auth");

  if (!raw) {
    return { token: null, user: null };
  }

  try {
    const parsed = JSON.parse(raw) as AuthStateSnapshot;
    return {
      token: parsed.token ?? null,
      user: parsed.user ?? null,
    };
  } catch {
    return { token: null, user: null };
  }
}

export function logoutClientSession(): void {
  localStorage.removeItem("medigenie_auth");
}

export { extractErrorMessage };
