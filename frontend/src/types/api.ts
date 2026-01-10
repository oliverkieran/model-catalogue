/**
 * API Types - Match FastAPI backend schemas
 */

// ============================================================================
// Base Types
// ============================================================================

export type AIModelType = "language" | "vision" | "audio" | "multimodal";

// ============================================================================
// AI Model Types
// ============================================================================

export interface AIModel {
  id: number;
  name: string;
  display_name: string;
  organization: string;
  release_date: string | null; // ISO date string from API
  description: string | null;
  license: string | null;
  metadata_: Record<string, string | number | boolean | object> | null;
  created_at: string; // ISO datetime string from API
  updated_at: string;
}

export interface AIModelCreate {
  name: string;
  display_name: string;
  organization: string;
  release_date?: string | null;
  description?: string | null;
  license?: string | null;
  metadata_?: Record<string, string | number | boolean | object> | null;
}

export interface AIModelUpdate {
  name?: string;
  display_name?: string;
  organization?: string;
  release_date?: string | null;
  description?: string | null;
  license?: string | null;
  metadata_?: Record<string, string | number | boolean | object> | null;
}

// ============================================================================
// Benchmark Types
// ============================================================================

export interface Benchmark {
  id: number;
  name: string;
  category: string;
  description: string | null;
  url: string | null;
  created_at: string;
  updated_at: string;
}

export interface BenchmarkCreate {
  name: string;
  category: string;
  description?: string | null;
  url?: string | null;
}

export interface BenchmarkUpdate {
  name?: string;
  category?: string;
  description?: string | null;
  url?: string | null;
}

// ============================================================================
// Benchmark Result Types
// ============================================================================

export interface BenchmarkResult {
  id: number;
  model_id: number;
  benchmark_id: number;
  score: number;
  date_tested: string | null; // ISO date string
  source: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  // Relationships (when eager loaded)
  model?: AIModel;
  benchmark?: Benchmark;
}

export interface BenchmarkResultCreate {
  model_id: number;
  benchmark_id: number;
  score: number;
  date_tested?: string | null;
  source?: string | null;
  notes?: string | null;
}

export interface BenchmarkResultUpdate {
  score?: number;
  date_tested?: string | null;
  source?: string | null;
  notes?: string | null;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface APIError {
  detail: string;
}

// ============================================================================
// Query Parameters
// ============================================================================

export interface ListParams {
  skip?: number;
  limit?: number;
}

export interface ModelListParams extends ListParams {
  organization?: string;
}

export interface BenchmarkListParams extends ListParams {
  category?: string;
}

export interface BenchmarkResultListParams extends ListParams {
  model_id?: number;
  benchmark_id?: number;
}

export interface SearchParams extends ListParams {
  q: string;
}
