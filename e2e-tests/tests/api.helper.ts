import { APIRequestContext } from '@playwright/test';

export class ApiHelper {
  private context: APIRequestContext;
  private baseURL: string;

  constructor(context: APIRequestContext, baseURL: string = 'http://localhost:8000') {
    this.context = context;
    this.baseURL = baseURL;
  }

  async post<T = any>(endpoint: string, data: any, headers?: Record<string, string>): Promise<{ status: number; body: T }> {
    const response = await this.context.post(`${this.baseURL}${endpoint}`, {
      data,
      headers,
    });
    const status = response.status();
    const text = await response.text();
    const body = (status === 204 || !text.trim()) ? {} as T : JSON.parse(text) as T;
    return { status, body };
  }

  async postForm<T = any>(endpoint: string, data: Record<string, string>, headers?: Record<string, string>): Promise<{ status: number; body: T }> {
    const response = await this.context.post(`${this.baseURL}${endpoint}`, {
      form: data,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        ...headers
      },
    });
    const status = response.status();
    const text = await response.text();
    const body = (status === 204 || !text.trim()) ? {} as T : JSON.parse(text) as T;
    return { status, body };
  }

  async put<T = any>(endpoint: string, data: any, headers?: Record<string, string>): Promise<{ status: number; body: T }> {
    const response = await this.context.put(`${this.baseURL}${endpoint}`, {
      data,
      headers,
    });
    const status = response.status();
    const text = await response.text();
    const body = (status === 204 || !text.trim()) ? {} as T : JSON.parse(text) as T;
    return { status, body };
  }

  async get<T = any>(endpoint: string, headers?: Record<string, string>): Promise<{ status: number; body: T }> {
    const response = await this.context.get(`${this.baseURL}${endpoint}`, {
      headers,
    });
    const status = response.status();
    const text = await response.text();
    const body = (status === 204 || !text.trim()) ? {} as T : JSON.parse(text) as T;
    return { status, body };
  }

  async getNoContent(endpoint: string, headers?: Record<string, string>): Promise<{ status: number }> {
    const response = await this.context.get(`${this.baseURL}${endpoint}`, {
      headers,
    });
    return {
      status: response.status(),
    };
  }

  async postNoContent(endpoint: string, data: any, headers?: Record<string, string>): Promise<{ status: number }> {
    const response = await this.context.post(`${this.baseURL}${endpoint}`, {
      data,
      headers,
    });
    return {
      status: response.status(),
    };
  }

  async putNoContent(endpoint: string, data: any, headers?: Record<string, string>): Promise<{ status: number }> {
    const response = await this.context.put(`${this.baseURL}${endpoint}`, {
      data,
      headers,
    });
    return {
      status: response.status(),
    };
  }
}

export interface NayaResponse<T = any> {
  status: number;
  statusMessage: string;
  data?: T;
  pagination?: {
    count: number;
    currentPage: number;
    nextPage: number | null;
    prevPage: number | null;
    lastPage: number;
  };
  error?: {
    code: string;
    data: any;
  };
}

export interface AuthResponse {
  status: string;
  access_token: string;
  refresh_token: string;
  user_type: string;
}

export interface PatientResponse {
  id: string;
  name: string;
  email: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
  patient_id: string;
}

export interface ErrorResponse {
  status: number;
  statusMessage: string;
  error: {
    code: string;
    data: any;
  };
}
