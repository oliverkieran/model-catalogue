import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { modelsApi } from "@/lib/api";
import type {
  AIModelCreate,
  AIModelUpdate,
  ListParams,
  SearchParams,
} from "@/types/api";

/**
 * Custom hooks for models data fetching with React Query
 */

// Query keys for cache management
export const modelKeys = {
  all: ["models"] as const,
  lists: () => [...modelKeys.all, "list"] as const,
  list: (params?: ListParams) => [...modelKeys.lists(), params] as const,
  details: () => [...modelKeys.all, "detail"] as const,
  detail: (id: number) => [...modelKeys.details(), id] as const,
  search: (params: SearchParams) =>
    [...modelKeys.all, "search", params] as const,
};

/**
 * Fetch all models with pagination
 */
export function useModels(params?: ListParams) {
  return useQuery({
    queryKey: modelKeys.list(params),
    queryFn: () => modelsApi.list(params),
  });
}

/**
 * Fetch a single model by ID
 */
export function useModel(id: number) {
  return useQuery({
    queryKey: modelKeys.detail(id),
    queryFn: () => modelsApi.getById(id),
    enabled: !!id, // Only fetch if id is truthy
  });
}

/**
 * Search models by query
 */
export function useSearchModels(params: SearchParams) {
  return useQuery({
    queryKey: modelKeys.search(params),
    queryFn: () => modelsApi.search(params),
    enabled: params.q.length > 2, // Only search if query is long enough
  });
}

/**
 * Create a new model
 */
export function useCreateModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AIModelCreate) => modelsApi.create(data),
    onSuccess: () => {
      // Invalidate and refetch models list
      queryClient.invalidateQueries({ queryKey: modelKeys.lists() });
    },
  });
}

/**
 * Update an existing model
 */
export function useUpdateModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: AIModelUpdate }) =>
      modelsApi.update(id, data),
    onSuccess: (_, variables) => {
      // Invalidate specific model and lists
      queryClient.invalidateQueries({
        queryKey: modelKeys.detail(variables.id),
      });
      queryClient.invalidateQueries({ queryKey: modelKeys.lists() });
    },
  });
}

/**
 * Delete a model
 */
export function useDeleteModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => modelsApi.delete(id),
    onSuccess: () => {
      // Invalidate models list
      queryClient.invalidateQueries({ queryKey: modelKeys.lists() });
    },
  });
}
