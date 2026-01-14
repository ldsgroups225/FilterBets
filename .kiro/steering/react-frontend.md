---
inclusion: fileMatch
fileMatchPattern: "frontend/**/*.{ts,tsx}"
---

# React Frontend Standards

## Component Structure

### Functional Components

Always use functional components with TypeScript:

```tsx
import { useState } from 'react';
import type { Filter } from '@/types';

interface FilterCardProps {
  filter: Filter;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

export function FilterCard({ filter, onEdit, onDelete }: FilterCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{filter.name}</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Component content */}
      </CardContent>
    </Card>
  );
}
```

### File Naming

- Components: `PascalCase.tsx` (e.g., `FilterBuilder.tsx`)
- Hooks: `use[Name].ts` (e.g., `useFilters.ts`)
- Utilities: `camelCase.ts` (e.g., `formatDate.ts`)
- Types: `types.ts` or `[domain].types.ts`

## Data Fetching with TanStack Query

### Query Hooks

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchFilters, createFilter, deleteFilter } from '@/services/api';

// Fetch data
export function useFilters() {
  return useQuery({
    queryKey: ['filters'],
    queryFn: fetchFilters,
  });
}

// Mutations with cache invalidation
export function useCreateFilter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createFilter,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['filters'] });
    },
  });
}
```

### Using Queries in Components

```tsx
export function FilterList() {
  const { data: filters, isLoading, error } = useFilters();
  const createMutation = useCreateFilter();

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      {filters?.map((filter) => (
        <FilterCard key={filter.id} filter={filter} />
      ))}
    </div>
  );
}
```

## UI Components (shadcn/ui)

### Using shadcn Components

```tsx
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
```

### Form Handling

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const filterSchema = z.object({
  name: z.string().min(1).max(100),
  rules: z.array(ruleSchema).min(1).max(10),
});

type FilterFormData = z.infer<typeof filterSchema>;

export function FilterForm({ onSubmit }: { onSubmit: (data: FilterFormData) => void }) {
  const form = useForm<FilterFormData>({
    resolver: zodResolver(filterSchema),
    defaultValues: { name: '', rules: [] },
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
}
```

## Tables with TanStack Table

### Table Definition

```tsx
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  flexRender,
} from '@tanstack/react-table';

const columns = [
  {
    accessorKey: 'name',
    header: 'Filter Name',
  },
  {
    accessorKey: 'createdAt',
    header: 'Created',
    cell: ({ row }) => formatDate(row.original.createdAt),
  },
  {
    id: 'actions',
    cell: ({ row }) => <ActionMenu filter={row.original} />,
  },
];

export function FiltersTable({ data }: { data: Filter[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <Table>
      {/* Table rendering */}
    </Table>
  );
}
```

## Type Definitions

### API Types

```typescript
// types/filter.ts
export interface Filter {
  id: number;
  name: string;
  description: string | null;
  rules: FilterRule[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface FilterRule {
  field: string;
  operator: '=' | '!=' | '>' | '<' | '>=' | '<=' | 'in' | 'between';
  value: string | number | string[] | [number, number];
}

export interface CreateFilterRequest {
  name: string;
  description?: string;
  rules: FilterRule[];
  isActive?: boolean;
}
```

## API Service Layer

### API Client

```typescript
// services/api.ts
const API_BASE = '/api/v1';

async function fetchWithAuth<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

export const fetchFilters = () => fetchWithAuth<Filter[]>('/filters');
export const createFilter = (data: CreateFilterRequest) =>
  fetchWithAuth<Filter>('/filters', {
    method: 'POST',
    body: JSON.stringify(data),
  });
```

## Styling with Tailwind

### Class Organization

```tsx
// Group classes logically: layout, spacing, typography, colors, states
<div className="flex items-center gap-4 p-4 text-sm text-gray-600 hover:bg-gray-50">
  {/* Content */}
</div>
```

### Responsive Design

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Responsive grid */}
</div>
```
