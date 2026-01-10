import apiClient from "../api-client";
import type {
  AIModel,
  AIModelCreate,
  AIModelUpdate,
  BenchmarkResult,
  ListParams,
  SearchParams,
} from "@/types/api";

/**
 * AIModels API Service
 *
 * Provides functions for interacting with /api/v1/models endpoints
 */

const BASE_PATH = "/api/v1/models";

export const modelsApi = {
  /**
   * List all models with pagination
   */
  async list(params?: ListParams): Promise<AIModel[]> {
    const response = await apiClient.get<AIModel[]>(BASE_PATH, { params });
    return response.data;
  },

  /**
   * Get a single model by ID
   */
  async getById(id: number): Promise<AIModel> {
    const response = await apiClient.get<AIModel>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  /**
   * Get a model by its unique name
   */
  async getByName(name: string): Promise<AIModel> {
    const response = await apiClient.get<AIModel>(`${BASE_PATH}/name/${name}`);
    return response.data;
  },

  /**
   * Search models by query
   */
  async search(params: SearchParams): Promise<AIModel[]> {
    const response = await apiClient.get<AIModel[]>(`${BASE_PATH}/search/`, {
      params,
    });
    return response.data;
  },

  /**
   * Get benchmark results for a specific model
   */
  async getBenchmarks(
    id: number,
    params?: ListParams
  ): Promise<BenchmarkResult[]> {
    const response = await apiClient.get<BenchmarkResult[]>(
      `${BASE_PATH}/${id}/benchmarks`,
      { params }
    );
    return response.data;
  },

  /**
   * Create a new model
   */
  async create(data: AIModelCreate): Promise<AIModel> {
    const response = await apiClient.post<AIModel>(BASE_PATH, data);
    return response.data;
  },

  /**
   * Update an existing model
   */
  async update(id: number, data: AIModelUpdate): Promise<AIModel> {
    const response = await apiClient.patch<AIModel>(`${BASE_PATH}/${id}`, data);
    return response.data;
  },

  /**
   * Delete a model
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/${id}`);
  },
};
