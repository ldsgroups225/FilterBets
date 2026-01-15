import type { ColumnDef, SortingState } from '@tanstack/react-table'
import type { Fixture } from '@/types/fixture'
import { IconArrowsSort } from '@tabler/icons-react'
import {

  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,

  useReactTable,
} from '@tanstack/react-table'
import { format } from 'date-fns'
import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface FixturesTableProps {
  fixtures: Fixture[]
  onRowClick?: (fixture: Fixture) => void
}

export function FixturesTable({ fixtures, onRowClick }: FixturesTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])

  const columns = useMemo<ColumnDef<Fixture>[]>(
    () => [
      {
        accessorKey: 'match_date',
        header: ({ column }) => {
          return (
            <Button
              variant="ghost"
              onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            >
              Date
              <IconArrowsSort className="ml-2 h-4 w-4" />
            </Button>
          )
        },
        cell: ({ row }) => {
          const date = new Date(row.original.match_date)
          return (
            <div className="flex flex-col">
              <span className="font-medium">{format(date, 'MMM dd, yyyy')}</span>
              <span className="text-xs text-muted-foreground">{format(date, 'HH:mm')}</span>
            </div>
          )
        },
      },
      {
        accessorKey: 'league_name',
        header: 'League',
        cell: ({ row }) => (
          <Badge variant="outline" className="font-normal">
            {row.original.league_name}
          </Badge>
        ),
      },
      {
        id: 'match',
        header: 'Match',
        cell: ({ row }) => (
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span className="font-medium">{row.original.home_team_name}</span>
              {row.original.home_score !== null && (
                <Badge variant="secondary">{row.original.home_score}</Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">{row.original.away_team_name}</span>
              {row.original.away_score !== null && (
                <Badge variant="secondary">{row.original.away_score}</Badge>
              )}
            </div>
          </div>
        ),
      },
      {
        id: 'odds',
        header: 'Odds (H / D / A)',
        cell: ({ row }) => {
          const { home_odds, draw_odds, away_odds } = row.original
          if (!home_odds || !draw_odds || !away_odds) {
            return <span className="text-muted-foreground">N/A</span>
          }
          return (
            <div className="flex gap-2 font-mono text-sm">
              <span>{home_odds.toFixed(2)}</span>
              <span className="text-muted-foreground">/</span>
              <span>{draw_odds.toFixed(2)}</span>
              <span className="text-muted-foreground">/</span>
              <span>{away_odds.toFixed(2)}</span>
            </div>
          )
        },
      },
      {
        accessorKey: 'status_id',
        header: 'Status',
        cell: ({ row }) => {
          const statusId = row.original.status_id
          const statusMap: Record<number, { label: string, variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
            1: { label: 'Scheduled', variant: 'default' },
            2: { label: 'Live', variant: 'destructive' },
            3: { label: 'Finished', variant: 'secondary' },
            4: { label: 'Postponed', variant: 'outline' },
          }
          const status = statusMap[statusId] || { label: 'Unknown', variant: 'outline' }
          return <Badge variant={status.variant}>{status.label}</Badge>
        },
      },
    ],
    [],
  )

  const table = useReactTable({
    data: fixtures,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
    initialState: {
      pagination: {
        pageSize: 20,
      },
    },
  })

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map(headerGroup => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length
              ? (
                  table.getRowModel().rows.map(row => (
                    <TableRow
                      key={row.id}
                      onClick={() => onRowClick?.(row.original)}
                      className={onRowClick ? 'cursor-pointer hover:bg-muted/50' : ''}
                    >
                      {row.getVisibleCells().map(cell => (
                        <TableCell key={cell.id}>
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                )
              : (
                  <TableRow>
                    <TableCell colSpan={columns.length} className="h-24 text-center">
                      No fixtures found.
                    </TableCell>
                  </TableRow>
                )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Showing
          {' '}
          {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}
          {' '}
          to
          {' '}
          {Math.min(
            (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
            fixtures.length,
          )}
          {' '}
          of
          {' '}
          {fixtures.length}
          {' '}
          fixtures
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
