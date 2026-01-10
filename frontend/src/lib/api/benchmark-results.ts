import apiClient from "../api-client";
import type {
  BenchmarkResult,
  BenchmarkResultCreate,
  BenchmarkResultUpdate,
  BenchmarkResultListParams,
} from "@/types/api";

const BASE_PATH = "/api/v1/benchmark-results";

export const benchmarkResultsApi = {
  async list(params?: BenchmarkResultListParams): Promise<BenchmarkResult[]> {
    const response = await apiClient.get<BenchmarkResult[]>(BASE_PATH, {
      params,
    });
    return response.data;
  },

  async getById(id: number): Promise<BenchmarkResult> {
    const response = await apiClient.get<BenchmarkResult>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  async create(data: BenchmarkResultCreate): Promise<BenchmarkResult> {
    const response = await apiClient.post<BenchmarkResult>(BASE_PATH, data);
    return response.data;
  },

  async update(
    id: number,
    data: BenchmarkResultUpdate
  ): Promise<BenchmarkResult> {
    const response = await apiClient.patch<BenchmarkResult>(
      `${BASE_PATH}/${id}`,
      data
    );
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/${id}`);
  },
};
