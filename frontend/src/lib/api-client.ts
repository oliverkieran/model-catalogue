import axios, { AxiosInstance, AxiosError } from "axios";
import type { APIError } from "@/types/api";

/**
 * API Client for Model Catalogue Backend
 *
 * Provides a configured axios instance with:
 * - Base URL from environment
 * - JSON content type
 * - Error transformation
 */

// Get API base URL from environment variable
// Defaults to localhost:8000 for development
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Create axios instance with defaults
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 seconds timeout
});

// Request interceptor (for future auth tokens)
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Add auth token when authentication is implemented
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIError>) => {
    // Transform error to a constant format
    const message =
      error.response?.data?.detail || error.message || "An error occurred";
    console.error("API Error:", {
      status: error.response?.status,
      message,
      url: error.config?.url,
    });

    // Rethrow with user-friendly message
    throw new Error(message);
  }
);

export default apiClient;
