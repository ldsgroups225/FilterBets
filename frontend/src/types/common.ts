// Pagination metadata from backend
export interface PaginationMeta {
  page: number
  per_page: number
  total_items: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

// Generic paginated response
export interface PaginatedResponse<T> {
  items: T[]
  meta: PaginationMeta
}
