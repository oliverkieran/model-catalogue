import apiClient from "../api-client";
import type {
  Benchmark,
  BenchmarkCreate,
  BenchmarkUpdate,
  BenchmarkResult,
  BenchmarkListParams,
  ListParams,
} from "@/types/api";

const BASE_PATH = "/api/v1/benchmarks";

export const benchmarksApi = {
  async list(params?: BenchmarkListParams): Promise<Benchmark[]> {
    const response = await apiClient.get<Benchmark[]>(BASE_PATH, { params });
    return response.data;
  },

  async getById(id: number): Promise<Benchmark> {
    const response = await apiClient.get<Benchmark>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  async getCategories(): Promise<string[]> {
    const response = await apiClient.get<string[]>(`${BASE_PATH}/categories`);
    return response.data;
  },

  async getResults(
    id: number,
    params?: ListParams
  ): Promise<BenchmarkResult[]> {
    const response = await apiClient.get<BenchmarkResult[]>(
      `${BASE_PATH}/${id}/results`,
      { params }
    );
    return response.data;
  },

  async create(data: BenchmarkCreate): Promise<Benchmark> {
    const response = await apiClient.post<Benchmark>(BASE_PATH, data);
    return response.data;
  },

  async update(id: number, data: BenchmarkUpdate): Promise<Benchmark> {
    const response = await apiClient.patch<Benchmark>(
      `${BASE_PATH}/${id}`,
      data
    );
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/${id}`);
  },
};
