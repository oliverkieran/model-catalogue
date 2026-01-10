# Module 4: Frontend Development - Building the Model Catalogue UI

**Duration:** 3-4 hours
**Difficulty:** Intermediate
**Prerequisites:** Module 2.2 (CRUD Operations & Error Handling) complete

---

## Introduction: From Backend to User Interface

You've built a powerful FastAPI backend with full CRUD operations, sophisticated error handling, and comprehensive data management. Your API serves models, benchmarks, and benchmark results with pagination, filtering, and search capabilities. But here's the question: **How do users actually interact with your data?**

The answer: **A modern, responsive web interface.**

In this module, we'll take the **ai-model-explorer** repository (a complete React application built with modern tools) and adapt it to work with your FastAPI backend. This isn't starting from scratch—it's **smart reuse** of existing, high-quality frontend code.

**Why use ai-model-explorer as a starting point?**

The ai-model-explorer repository already has:

- ✅ **React 18 + TypeScript** - Type-safe component development
- ✅ **Vite** - Lightning-fast development server
- ✅ **shadcn/ui** - Beautiful, accessible component library
- ✅ **TanStack Query** - Powerful data fetching and caching
- ✅ **Tailwind CSS** - Utility-first styling
- ✅ **Model browsing UI** - Cards, filters, search, comparison
- ✅ **Responsive design** - Mobile-friendly layouts

**What we'll change:**

Currently, ai-model-explorer uses **hardcoded data** in `src/data/models.ts`. We'll:

- Replace hardcoded data with **API calls** to your FastAPI backend
- Adapt data models to match your **backend schemas**
- Add **CRUD operations** for creating and editing models
- Implement **error handling** for API failures
- Set up **development environment** with proper CORS
- Add **loading states** and **optimistic updates**

**But first, let's address a crucial question: Why not build the frontend from scratch?**

```typescript
// ❌ Starting from scratch (weeks of work)
// - Set up build tooling (Vite config, TypeScript, Tailwind)
// - Install and configure component library
// - Design layout and navigation
// - Build reusable components (cards, filters, modals)
// - Implement responsive grid layouts
// - Add loading states and error handling
// - Create routing structure
// - Design and implement state management
// ... and much more

// ✅ Adapting ai-model-explorer (hours of work)
// - Copy existing codebase to frontend/
// - Update data models to match backend schemas
// - Replace hardcoded data with API calls
// - Configure API client for FastAPI
// - Test and refine
```

**The pragmatic approach wins every time.** Professional developers reuse proven code whenever possible.

In this module, you'll learn:

- **Integrating a React frontend** with your FastAPI backend
- **Setting up API clients** with TanStack Query
- **Replacing static data** with dynamic API calls
- **Handling loading and error states** gracefully
- **Type-safe data fetching** with TypeScript
- **CORS configuration** for local development
- **Environment variables** for API URLs
- **Optimistic UI updates** for better UX

By the end, you'll have a **fully functional web application** where users can browse, search, compare, and manage AI models through an intuitive interface.

---

## What You'll Build

By the end of this module, you'll have:

- ✅ Complete React frontend integrated with your FastAPI backend
- ✅ Type-safe API client using TanStack Query
- ✅ Dynamic data loading from your database
- ✅ Search, filter, and comparison features working with real data
- ✅ Loading states and error handling
- ✅ Responsive UI that works on all devices
- ✅ CORS properly configured for local development
- ✅ Environment-based configuration for API URLs
- ✅ Foundation for adding CRUD operations (future module)

---

## Understanding the Frontend Architecture

Before we dive into code, let's understand how the pieces fit together.

### The Modern React Stack

**React 18** provides:

- Component-based UI development
- Declarative rendering
- Virtual DOM for performance
- Hooks for state and side effects

**TypeScript** adds:

- Type safety at compile time
- IntelliSense and autocomplete
- Catch errors before runtime
- Self-documenting code

**Vite** delivers:

- Instant server start
- Lightning-fast HMR (Hot Module Replacement)
- Optimized production builds
- Native ES modules support

**TanStack Query** handles:

- Data fetching and caching
- Loading and error states
- Automatic refetching
- Optimistic updates
- Request deduplication

**shadcn/ui** provides:

- Beautiful, accessible components
- Customizable with Tailwind
- Copy-paste component code
- Dark mode support

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Components                   │
│  (ModelCard, FilterBar, Hero, SearchBar)            │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Uses hooks (useQuery, useMutation)
                 │
┌────────────────▼────────────────────────────────────┐
│               TanStack Query                         │
│  (Data fetching, caching, state management)         │
└────────────────┬────────────────────────────────────┘
                 │
                 │ HTTP requests
                 │
┌────────────────▼────────────────────────────────────┐
│                  API Client                          │
│  (Axios/Fetch wrapper with base URL)                │
└────────────────┬────────────────────────────────────┘
                 │
                 │ REST calls
                 │
┌────────────────▼────────────────────────────────────┐
│            FastAPI Backend                           │
│  (localhost:8000/api/v1/...)                        │
└────────────────┬────────────────────────────────────┘
                 │
                 │ SQL queries
                 │
┌────────────────▼────────────────────────────────────┐
│           Supabase Database                          │
│  (PostgreSQL with models, benchmarks, results)      │
└─────────────────────────────────────────────────────┘
```

### The ai-model-explorer Structure

The repository we're adapting has this structure:

```
ai-model-explorer/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Hero.tsx         # Landing section with search
│   │   ├── FilterBar.tsx    # Type and provider filters
│   │   ├── ModelCard.tsx    # Individual model cards
│   │   ├── ModelDetail.tsx  # Detailed model modal
│   │   ├── ComparePanel.tsx # Side-by-side comparison
│   │   └── ui/              # shadcn/ui components
│   ├── data/
│   │   └── models.ts        # 🔥 HARDCODED DATA - we'll replace this
│   ├── pages/
│   │   └── Index.tsx        # Main page component
│   ├── lib/
│   │   └── utils.ts         # Utility functions
│   └── hooks/               # Custom React hooks (we'll add API hooks)
├── package.json             # Dependencies
└── vite.config.ts           # Vite configuration
```

**Our strategy:**

1. **Keep the UI components** - they're already great
2. **Replace data layer** - swap hardcoded data with API calls
3. **Add API hooks** - create custom hooks for data fetching
4. **Update TypeScript types** - match backend schemas
5. **Configure environment** - API URL, CORS, etc.

**🎯 Checkpoint:** You understand the frontend architecture and our adaptation strategy.

---

## Step 1: Setting Up the Frontend Project

Let's copy the ai-model-explorer repository into your project structure. Since both ai-model-explorer and model-catalogue are Git repositories, we'll copy **just the code files** (not the Git history) to avoid nested repository issues.

### Copy the Repository (Without Git History)

**Why not just clone?** Cloning would create a nested Git repository inside your model-catalogue repo, which causes complications. We want the frontend to be part of your main repository.

```bash
# From your model-catalogue directory
cd /Users/oli/Documents/Coding/Web\ Development/model-catalogue

# Clone to a temporary location
git clone https://github.com/oliverkieran/ai-model-explorer.git /tmp/ai-model-explorer

# Copy contents (excluding .git) to your frontend folder
# Using rsync to exclude the .git directory
rsync -av --exclude='.git' /tmp/ai-model-explorer/ frontend/

# Clean up temporary clone
rm -rf /tmp/ai-model-explorer

# Verify the copy worked
ls frontend/
```

**What this does:**

- ✅ Copies all source code, configuration files, and assets
- ✅ Excludes `.git` directory (no nested repository)
- ✅ Frontend becomes part of your model-catalogue repository
- ✅ You can commit frontend changes directly to model-catalogue

### Add Frontend to Your Repository

```bash
# From your model-catalogue directory
cd /Users/oli/Documents/Coding/Web\ Development/model-catalogue

# Add frontend to git
git add frontend/

# Commit the frontend initialization
git commit -m "feat: initialize frontend from ai-model-explorer"
```

### Install Dependencies

The project uses **npm** (you can also use **bun** or **yarn** if preferred):

```bash
cd frontend

# Install all dependencies
npm install

# This installs:
# - React 18 and React DOM
# - TypeScript and type definitions
# - Vite for development
# - TanStack Query for data fetching
# - shadcn/ui components
# - Tailwind CSS for styling
# - React Router for navigation
```

### Test the Development Server

```bash
# Start the dev server
npm run dev
```

You should see:

```
  VITE v5.4.19  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Visit http://localhost:5173/** - you should see the model catalogue with hardcoded data.

**🎯 Checkpoint:** Your frontend is running locally with hardcoded data.

---

## Step 2: Understanding the Current Data Layer

Before we replace it, let's understand how data currently flows.

### Examine the Hardcoded Data

Open `frontend/src/data/models.ts`:

```typescript
export interface AIModel {
  id: string;
  name: string;
  provider: string;
  type: ModelType;
  description: string;
  releaseDate: string;
  parameters: string;
  contextWindow: string;
  pricing: {
    input: string;
    output: string;
  };
  benchmarks: Benchmark[];
  useCases: UseCase[];
  opinions: Opinion[];
  tags: string[];
  featured?: boolean;
}

export const models: AIModel[] = [
  {
    id: "gpt-4o",
    name: "GPT-4o",
    provider: "OpenAI",
    type: "multimodal",
    description: "OpenAI's most advanced multimodal model...",
    releaseDate: "2024-05",
    // ... hardcoded data
  },
  // ... more hardcoded models
];
```

### Compare with Backend Schema

Your backend (from Module 2) has this schema:

```python
# backend/app/models/models.py
class ModelResponse(ModelBase):
    id: int                    # Integer, not string
    name: str
    display_name: str          # NEW: not in frontend
    organization: str          # Called "provider" in frontend
    release_date: date | None  # Date type, not string
    description: str | None
    license: str | None        # NEW: not in frontend
    metadata_: dict | None     # NEW: not in frontend
    created_at: datetime
    updated_at: datetime
```

**Key differences:**

| Frontend                                 | Backend                                | Notes                                       |
| ---------------------------------------- | -------------------------------------- | ------------------------------------------- |
| `id: string`                             | `id: int`                              | Type mismatch                               |
| `provider`                               | `organization`                         | Different field name                        |
| `releaseDate`                            | `release_date`                         | Naming convention (camelCase vs snake_case) |
| `parameters`, `contextWindow`, `pricing` | None                                   | Frontend-only fields (not in DB)            |
| `benchmarks: Benchmark[]`                | Relationship                           | Frontend embeds, backend uses IDs           |
| None                                     | `display_name`, `license`, `metadata_` | Backend has additional fields               |
| None                                     | `created_at`, `updated_at`             | Backend has timestamps                      |

**Two approaches to handle this:**

1. **Adapt frontend types to backend** (recommended)
2. **Transform backend data to frontend format** (mapper layer)

**We'll use approach #1** - update frontend types to match backend schemas.

**🎯 Checkpoint:** You understand the data model mismatches we need to fix.

---

## Step 3: Creating TypeScript Types for Backend Schemas

Let's create TypeScript interfaces that match your FastAPI backend.

### Create API Types File

Create `frontend/src/types/api.ts`:

```typescript
/**
 * API Types - Match FastAPI backend schemas
 *
 * These types mirror the Pydantic schemas from backend/app/models/models.py
 */

// ============================================================================
// Base Types
// ============================================================================

export type ModelType = "language" | "vision" | "audio" | "multimodal";

// ============================================================================
// Model Types
// ============================================================================

export interface Model {
  id: number;
  name: string;
  display_name: string;
  organization: string;
  release_date: string | null; // ISO date string from API
  description: string | null;
  license: string | null;
  metadata_: Record<string, any> | null;
  created_at: string; // ISO datetime string from API
  updated_at: string;
}

export interface ModelCreate {
  name: string;
  display_name: string;
  organization: string;
  release_date?: string | null;
  description?: string | null;
  license?: string | null;
  metadata_?: Record<string, any> | null;
}

export interface ModelUpdate {
  name?: string;
  display_name?: string;
  organization?: string;
  release_date?: string | null;
  description?: string | null;
  license?: string | null;
  metadata_?: Record<string, any> | null;
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
  model?: Model;
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
```

**Why this structure?**

### 1. Exact Type Matching

```typescript
export interface Model {
  id: number;           // Matches backend: id: int
  name: string;         // Matches backend: name: str
  release_date: string | null;  // Backend returns ISO string
```

**Backend sends:**

```json
{
  "id": 1,
  "name": "gpt-4",
  "release_date": "2023-03-14"
}
```

**TypeScript knows:**

- `id` is always a number
- `release_date` might be null
- All fields are present (no optional `?`)

### 2. Separate Create/Update Types

```typescript
export interface ModelCreate {
  name: string; // Required
  display_name: string; // Required
  organization: string; // Required
  release_date?: string; // Optional
}

export interface ModelUpdate {
  name?: string; // Optional (partial update)
  display_name?: string; // Optional
  organization?: string; // Optional
}
```

**Enables type-safe forms:**

```typescript
// Create form - TypeScript ensures required fields
const createModel = (data: ModelCreate) => {
  // TypeScript error if name is missing!
};

// Update form - all fields optional
const updateModel = (id: number, data: ModelUpdate) => {
  // Can send only changed fields
};
```

### 3. Query Parameter Types

```typescript
export interface BenchmarkResultListParams extends ListParams {
  model_id?: number;
  benchmark_id?: number;
}
```

**Enables type-safe API calls:**

```typescript
// TypeScript validates parameters
const getResults = (params: BenchmarkResultListParams) => {
  return api.get("/benchmark-results", { params });
};

// ✅ Valid
getResults({ model_id: 5, limit: 10 });

// ❌ TypeScript error: wrong type
getResults({ model_id: "5" }); // string instead of number
```

**🎯 Checkpoint:** You have TypeScript types matching your backend schemas.

---

## Step 4: Creating the API Client

Now let's build a reusable API client for communicating with your FastAPI backend.

### Install Axios

```bash
cd frontend
npm install axios
```

### Create API Client

Create `frontend/src/lib/api-client.ts`:

```typescript
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
  timeout: 10000, // 10 second timeout
});

// Request interceptor (for future auth tokens)
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Add auth token when authentication is implemented
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
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
    // Transform error to a consistent format
    const message =
      error.response?.data?.detail || error.message || "An error occurred";

    console.error("API Error:", {
      status: error.response?.status,
      message,
      url: error.config?.url,
    });

    // Re-throw with user-friendly message
    throw new Error(message);
  }
);

export default apiClient;
```

**Key patterns in the API client:**

### 1. Environment Variable Configuration

```typescript
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
```

**Vite exposes env vars** that start with `VITE_`:

- Development: Uses `http://localhost:8000` (your FastAPI server)
- Production: Can be overridden with `VITE_API_BASE_URL` env var

**Create `.env` file** in `frontend/`:

```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

### 2. Request Interceptor

```typescript
apiClient.interceptors.request.use((config) => {
  // Future: Add authentication headers
  return config;
});
```

**Interceptors run before every request:**

- Add auth tokens (when you implement authentication)
- Add custom headers
- Log requests (in development)
- Modify request config

### 3. Response Interceptor for Error Handling

```typescript
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIError>) => {
    const message = error.response?.data?.detail || error.message;
    throw new Error(message);
  }
);
```

**Centralizes error handling:**

- Extracts `detail` from FastAPI error responses
- Logs errors for debugging
- Transforms to consistent Error objects
- Components get clean error messages

**Example error flow:**

```typescript
// Backend returns 404
{
  "detail": "Model with id 999 not found"
}

// Interceptor transforms to:
throw new Error("Model with id 999 not found");

// Component receives:
catch (error) {
  console.log(error.message);  // "Model with id 999 not found"
}
```

**🎯 Checkpoint:** You have a configured API client ready to communicate with FastAPI.

---

## Step 5: Creating API Service Functions

Now let's create service functions for each resource (models, benchmarks, benchmark results).

### Create Models API Service

Create `frontend/src/lib/api/models.ts`:

```typescript
import apiClient from "../api-client";
import type {
  Model,
  ModelCreate,
  ModelUpdate,
  BenchmarkResult,
  ListParams,
  SearchParams,
} from "@/types/api";

/**
 * Models API Service
 *
 * Provides functions for interacting with /api/v1/models endpoints
 */

const BASE_PATH = "/api/v1/models";

export const modelsApi = {
  /**
   * List all models with pagination
   */
  async list(params?: ListParams): Promise<Model[]> {
    const response = await apiClient.get<Model[]>(BASE_PATH, { params });
    return response.data;
  },

  /**
   * Get a single model by ID
   */
  async getById(id: number): Promise<Model> {
    const response = await apiClient.get<Model>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  /**
   * Get a model by its unique name
   */
  async getByName(name: string): Promise<Model> {
    const response = await apiClient.get<Model>(`${BASE_PATH}/name/${name}`);
    return response.data;
  },

  /**
   * Search models by query
   */
  async search(params: SearchParams): Promise<Model[]> {
    const response = await apiClient.get<Model[]>(`${BASE_PATH}/search/`, {
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
  async create(data: ModelCreate): Promise<Model> {
    const response = await apiClient.post<Model>(BASE_PATH, data);
    return response.data;
  },

  /**
   * Update an existing model
   */
  async update(id: number, data: ModelUpdate): Promise<Model> {
    const response = await apiClient.patch<Model>(`${BASE_PATH}/${id}`, data);
    return response.data;
  },

  /**
   * Delete a model
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/${id}`);
  },
};
```

### Create Benchmarks API Service

Create `frontend/src/lib/api/benchmarks.ts`:

```typescript
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
```

### Create Benchmark Results API Service

Create `frontend/src/lib/api/benchmark-results.ts`:

```typescript
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
```

### Create Barrel Export

Create `frontend/src/lib/api/index.ts`:

```typescript
/**
 * API Services Barrel Export
 *
 * Re-exports all API service modules for convenient importing
 */

export * from "./models";
export * from "./benchmarks";
export * from "./benchmark-results";
```

**Now you can import easily:**

```typescript
import { modelsApi, benchmarksApi } from "@/lib/api";

// Use the APIs
const models = await modelsApi.list();
const benchmarks = await benchmarksApi.list();
```

**🎯 Checkpoint:** You have type-safe API service functions for all resources!

---

## Step 6: Configuring CORS for Local Development

Your FastAPI backend needs to allow requests from the React dev server.

### Update Backend CORS Configuration

Edit `backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
```

**What this does:**

- `allow_origins`: Only requests from localhost:5173 (Vite) are accepted
- `allow_credentials`: Allows cookies (for future auth)
- `allow_methods`: Allows GET, POST, PATCH, DELETE, etc.
- `allow_headers`: Allows Content-Type, Authorization, etc.

**Why CORS?**

Browsers block requests from `http://localhost:5173` (frontend) to `http://localhost:8000` (backend) by default. This is a security feature called **Same-Origin Policy**.

**CORS** (Cross-Origin Resource Sharing) tells the browser: "It's okay, these origins can talk to each other."

### Restart Backend Server

```bash
cd backend
uv run uvicorn app.main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**🎯 Checkpoint:** Your backend now accepts requests from your frontend!

---

## Step 7: Creating React Query Hooks

TanStack Query (formerly React Query) provides powerful data fetching hooks. Let's create custom hooks for our API.

### Create Models Hooks

Create `frontend/src/hooks/useModels.ts`:

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { modelsApi } from "@/lib/api";
import type {
  Model,
  ModelCreate,
  ModelUpdate,
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
    enabled: params.q.length >= 2, // Only search if query is long enough
  });
}

/**
 * Create a new model
 */
export function useCreateModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ModelCreate) => modelsApi.create(data),
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
    mutationFn: ({ id, data }: { id: number; data: ModelUpdate }) =>
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
```

**Understanding the hooks:**

### 1. Query Keys

```typescript
export const modelKeys = {
  all: ["models"] as const,
  lists: () => [...modelKeys.all, "list"] as const,
  list: (params?: ListParams) => [...modelKeys.lists(), params] as const,
  detail: (id: number) => [...modelKeys.details(), id] as const,
};
```

**Query keys identify cached data:**

```typescript
["models"][("models", "list")][("models", "list", { skip: 0, limit: 20 })][ // All model-related queries // All list queries // Specific list query
  ("models", "detail", 5)
]; // Model with ID 5
```

**Why this structure?**

- **Hierarchical**: Easy to invalidate groups of queries
- **Type-safe**: TypeScript validates keys
- **Cacheable**: React Query caches by key

**Example invalidation:**

```typescript
// Invalidate all model queries
queryClient.invalidateQueries({ queryKey: ["models"] });

// Invalidate only lists (keeps detail caches)
queryClient.invalidateQueries({ queryKey: ["models", "list"] });

// Invalidate specific model
queryClient.invalidateQueries({ queryKey: ["models", "detail", 5] });
```

### 2. useQuery Hook

```typescript
export function useModels(params?: ListParams) {
  return useQuery({
    queryKey: modelKeys.list(params),
    queryFn: () => modelsApi.list(params),
  });
}
```

**What you get:**

```typescript
const { data, isLoading, error, refetch } = useModels({ limit: 10 });

// data: Model[] | undefined
// isLoading: boolean (true while fetching)
// error: Error | null (if request failed)
// refetch: () => void (manually refetch)
```

**React Query automatically:**

- Caches results
- Deduplicates requests
- Refetches on window focus
- Retries failed requests
- Provides loading/error states

### 3. useMutation Hook

```typescript
export function useCreateModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ModelCreate) => modelsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: modelKeys.lists() });
    },
  });
}
```

**What you get:**

```typescript
const { mutate, isLoading, error } = useCreateModel();

// Create a model
mutate(
  { name: "gpt-5", display_name: "GPT-5", organization: "OpenAI" },
  {
    onSuccess: (createdModel) => {
      console.log("Created:", createdModel);
    },
    onError: (error) => {
      console.error("Failed:", error);
    },
  }
);
```

**Auto-invalidation:**

- After creating a model, `onSuccess` runs
- Invalidates the models list cache
- React Query refetches the list automatically
- UI updates with new model

**🎯 Checkpoint:** You have powerful, type-safe React Query hooks for models!

---

## Step 8: Updating the Index Page to Use Real Data

Now let's replace the hardcoded data with API calls.

### Update Index Component

Edit `frontend/src/pages/Index.tsx`:

```typescript
import { useState, useMemo } from "react";
import { Hero } from "@/components/Hero";
import { FilterBar } from "@/components/FilterBar";
import { ModelCard } from "@/components/ModelCard";
import { ModelDetail } from "@/components/ModelDetail";
import { ComparePanel } from "@/components/ComparePanel";
import { CompareFloatingBar } from "@/components/CompareFloatingBar";
import { Helmet } from "react-helmet-async";
import { useModels } from "@/hooks/useModels";
import type { Model } from "@/types/api";

const Index = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedOrganizations, setSelectedOrganizations] = useState<string[]>(
    []
  );
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [compareModels, setCompareModels] = useState<Model[]>([]);
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  // Fetch models from API
  const { data: models, isLoading, error } = useModels({ limit: 100 });

  // Filter models based on search and filters
  const filteredModels = useMemo(() => {
    if (!models) return [];

    return models.filter((model) => {
      const matchesSearch =
        model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        model.organization.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (model.description?.toLowerCase() || "").includes(
          searchQuery.toLowerCase()
        );

      const matchesOrganization =
        selectedOrganizations.length === 0 ||
        selectedOrganizations.includes(model.organization);

      return matchesSearch && matchesOrganization;
    });
  }, [models, searchQuery, selectedOrganizations]);

  const toggleCompare = (model: Model) => {
    setCompareModels((prev) => {
      if (prev.find((m) => m.id === model.id)) {
        return prev.filter((m) => m.id !== model.id);
      }
      if (prev.length >= 4) return prev;
      return [...prev, model];
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading models...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold mb-2 text-destructive">
            Error Loading Models
          </h2>
          <p className="text-muted-foreground mb-4">{error.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>AI Model Catalogue - Compare & Discover AI Models</title>
        <meta
          name="description"
          content="Discover, compare, and choose the perfect AI model for your project. Browse benchmarks, use cases, and expert reviews."
        />
      </Helmet>

      <main className="min-h-screen bg-background">
        <Hero
          searchValue={searchQuery}
          onSearchChange={setSearchQuery}
          modelCount={models?.length || 0}
        />

        <section className="container py-12">
          <FilterBar
            selectedOrganizations={selectedOrganizations}
            onOrganizationChange={setSelectedOrganizations}
            organizations={Array.from(
              new Set(models?.map((m) => m.organization) || [])
            )}
          />

          <div className="mt-12">
            <h2 className="text-2xl font-bold mb-6">
              Models
              <span className="text-muted-foreground font-normal ml-2">
                ({filteredModels.length})
              </span>
            </h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {filteredModels.map((model, idx) => (
                <div
                  key={model.id}
                  className="animate-slide-up"
                  style={{ animationDelay: `${idx * 0.05}s` }}
                >
                  <ModelCard
                    model={model}
                    onClick={() => setSelectedModel(model)}
                    isComparing={compareModels.some((m) => m.id === model.id)}
                    onCompareToggle={() => toggleCompare(model)}
                  />
                </div>
              ))}
            </div>

            {filteredModels.length === 0 && (
              <div className="text-center py-20">
                <p className="text-xl text-muted-foreground">
                  No models found matching your criteria.
                </p>
                <p className="text-muted-foreground mt-2">
                  Try adjusting your search or filters.
                </p>
              </div>
            )}
          </div>
        </section>

        <ModelDetail
          model={selectedModel}
          onClose={() => setSelectedModel(null)}
        />

        <CompareFloatingBar
          models={compareModels}
          onOpen={() => setIsCompareOpen(true)}
          onClear={() => setCompareModels([])}
        />

        <ComparePanel
          models={compareModels}
          onRemove={(id) =>
            setCompareModels((prev) => prev.filter((m) => m.id !== id))
          }
          onClear={() => setCompareModels([])}
          isOpen={isCompareOpen}
          onOpenChange={setIsCompareOpen}
        />
      </main>
    </>
  );
};

export default Index;
```

**Key changes:**

### 1. Using the useModels Hook

```typescript
// OLD: Import hardcoded data
import { models } from "@/data/models";

// NEW: Fetch from API
const { data: models, isLoading, error } = useModels({ limit: 100 });
```

**Automatic benefits:**

- Data fetched on component mount
- Loading state handled automatically
- Errors caught and exposed
- Cached for subsequent renders
- Refetched on window focus

### 2. Loading State UI

```typescript
if (isLoading) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      <p className="text-muted-foreground">Loading models...</p>
    </div>
  );
}
```

**Professional loading UX:**

- Centered spinner
- Clear message
- Branded colors (uses Tailwind theme)
- Full-height container

### 3. Error State UI

```typescript
if (error) {
  return (
    <div className="text-center max-w-md">
      <h2 className="text-2xl font-bold text-destructive">
        Error Loading Models
      </h2>
      <p className="text-muted-foreground">{error.message}</p>
      <button onClick={() => window.location.reload()}>Retry</button>
    </div>
  );
}
```

**User-friendly error handling:**

- Shows actual error message (from API)
- Provides retry action
- Uses semantic colors (destructive for errors)
- Doesn't crash the app

**🎯 Checkpoint:** Your index page now fetches real data from the FastAPI backend!

---

## Step 9: Testing the Integration

Let's verify everything works end-to-end.

### Start Both Servers

**Terminal 1 - Backend:**

```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

### Create Test Data

Use your backend API to create some models:

```bash
# Create GPT-4
curl -X POST http://localhost:8000/api/v1/models/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "gpt-4",
    "display_name": "GPT-4",
    "organization": "OpenAI",
    "release_date": "2023-03-14",
    "description": "Most capable GPT-4 model with broad general knowledge"
  }'

# Create Claude 3.5 Sonnet
curl -X POST http://localhost:8000/api/v1/models/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "claude-3.5-sonnet",
    "display_name": "Claude 3.5 Sonnet",
    "organization": "Anthropic",
    "release_date": "2024-06-20",
    "description": "Anthropic'\''s most intelligent model with strong reasoning"
  }'

# Create Gemini 1.5 Pro
curl -X POST http://localhost:8000/api/v1/models/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "gemini-1.5-pro",
    "display_name": "Gemini 1.5 Pro",
    "organization": "Google",
    "release_date": "2024-02-15",
    "description": "Google'\''s most capable multimodal model"
  }'
```

### Visit the Frontend

Open **http://localhost:5173/** in your browser.

**You should see:**

1. ✅ **Models load** from your database
2. ✅ **Search works** by filtering models
3. ✅ **Filter by organization** works
4. ✅ **Model cards display** correctly
5. ✅ **No console errors** in browser DevTools

**Open DevTools Network Tab:**

- You should see a `GET` request to `http://localhost:8000/api/v1/models/`
- Status: `200 OK`
- Response shows your models as JSON

### Test Error Handling

**Stop the backend server** (Ctrl+C) and refresh the page.

**You should see:**

- Error message: "Network Error" or "Failed to fetch"
- Retry button
- No app crash

**Restart backend** and click retry - data loads again!

**🎯 Checkpoint:** Full-stack integration working! Frontend fetches real data from FastAPI backend.

---

## What You've Accomplished

Congratulations! You've successfully integrated a modern React frontend with your FastAPI backend. Here's what you now have:

### 1. Complete Frontend Integration

- ✅ React application serving from Vite dev server
- ✅ Type-safe API client with Axios
- ✅ TanStack Query for data fetching and caching
- ✅ Loading and error states handled gracefully

### 2. Type Safety Throughout

- ✅ TypeScript types matching backend schemas
- ✅ API service functions with proper typing
- ✅ React Query hooks with type inference
- ✅ Component props type-checked

### 3. Professional UX

- ✅ Loading spinners while fetching
- ✅ Error messages with retry functionality
- ✅ Search and filtering on real data
- ✅ Responsive design working on all devices

### 4. Development Environment

- ✅ CORS configured for local development
- ✅ Environment variables for API URL
- ✅ Hot module replacement (instant updates)
- ✅ Both servers running concurrently

---

## Key Takeaways

**On Frontend Integration:**

- **Reuse existing code** - adapting is faster than building from scratch
- **Type safety prevents bugs** - TypeScript catches errors at compile time
- **API clients centralize logic** - one place for headers, error handling, base URL
- **React Query simplifies data fetching** - automatic caching, loading states, refetching

**On API Design:**

- **CORS must be configured** - browsers block cross-origin requests by default
- **Environment variables** - different URLs for dev/staging/production
- **Consistent error format** - FastAPI's `{"detail": "..."}` makes frontend parsing easy

**On User Experience:**

- **Loading states are essential** - users need feedback while waiting
- **Error messages should guide** - tell users what went wrong and how to fix it
- **Optimistic updates feel fast** - update UI before API confirms (we'll add this later)

**On Development Workflow:**

- **Run backend and frontend** - two separate dev servers
- **Test in browser DevTools** - Network tab shows API calls
- **Environment parity** - dev environment matches production as closely as possible

---

## What's Next?

In **Module 5: CRUD UI & Form Handling** (future module), you'll:

- **Build create/edit forms** for models and benchmarks
- **Implement optimistic updates** for instant UI feedback
- **Add delete confirmations** with proper UX
- **Add form validation** matching backend constraints

For now, you have a fully functional frontend that displays real data from your backend!

---

## Hands-On Exercises

Before moving forward, practice and extend what you've learned:

### Exercise 1: Add Benchmarks Page

Create a dedicated page for browsing benchmarks:

**Requirements:**

- New route: `/benchmarks`
- List all benchmarks with categories
- Filter by category
- Click to view models with results on that benchmark

### Exercise 2: Implement Search with Debouncing

Improve the search performance:

**Requirements:**

- Use `useDeferredValue` or `useDebounce` hook
- Only search after user stops typing (300ms delay)
- Show "Searching..." indicator while debouncing
- Use `useSearchModels` hook with dynamic query

### Exercise 3: Add Model Detail Page

Create a dedicated page for each model:

**Requirements:**

- Route: `/models/:id`
- Fetch model with `useModel` hook
- Show all model details
- List benchmark results
- Back button to return to list

### Exercise 4: Environment Configuration

Set up proper environment configuration:

**Requirements:**

- Create `.env.development` and `.env.production`
- Different API URLs for each environment
- Add `.env.example` with template
- Update `.gitignore` to exclude `.env` files

---

**Congratulations!** Your Model Catalogue now has a beautiful, functional frontend powered by real data from your FastAPI backend. You're ready to build the full CRUD interface in the next module!
