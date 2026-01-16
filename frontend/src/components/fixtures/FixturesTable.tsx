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
import { cn } from '@/lib/utils'

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
        header: ({ column }) => (
          <Button
            variant="ghost"
            size="sm"
            className="-ml-3 h-8 data-[state=open]:bg-accent font-black uppercase text-[10px] tracking-widest text-muted-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Match Time
            <IconArrowsSort className="ml-2 h-3 w-3" />
          </Button>
        ),
        cell: ({ row }) => {
          const date = new Date(row.original.match_date)
          return (
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 flex-col items-center justify-center rounded-xl bg-white/5 border border-white/5 group-hover:bg-primary/10 group-hover:border-primary/20 transition-colors">
                <span className="text-[10px] font-black uppercase leading-none opacity-50">{format(date, 'MMM')}</span>
                <span className="text-sm font-black mt-0.5">{format(date, 'dd')}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-bold">{format(date, 'HH:mm')}</span>
                <span className="text-[10px] font-medium text-muted-foreground opacity-60 uppercase tracking-tighter">Live Odds</span>
              </div>
            </div>
          )
        },
      },
      {
        accessorKey: 'league_name',
        header: () => <span className="font-black uppercase text-[10px] tracking-widest text-muted-foreground">League</span>,
        cell: ({ row }) => (
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-primary" />
            <span className="text-xs font-bold truncate max-w-[140px]">{row.original.league_name}</span>
          </div>
        ),
      },
      {
        id: 'teams',
        header: () => <span className="font-black uppercase text-[10px] tracking-widest text-muted-foreground">Matchup</span>,
        cell: ({ row }) => (
          <div className="flex flex-col gap-2 min-w-[200px]">
            <div className="flex items-center justify-between group/team">
              <div className="flex items-center gap-2.5">
                <div className="h-5 w-5 rounded-md bg-white/5 flex items-center justify-center border border-white/5 group-hover/team:border-primary/30 transition-colors">
                  <span className="text-[8px] font-black">{row.original.home_team_name[0]}</span>
                </div>
                <span className="text-sm font-bold tracking-tight">{row.original.home_team_name}</span>
              </div>
              {row.original.home_score !== null && (
                <span className="text-sm font-black text-primary">{row.original.home_score}</span>
              )}
            </div>
            <div className="flex items-center justify-between group/team">
              <div className="flex items-center gap-2.5">
                <div className="h-5 w-5 rounded-md bg-white/5 flex items-center justify-center border border-white/5 group-hover/team:border-primary/30 transition-colors">
                  <span className="text-[8px] font-black">{row.original.away_team_name[0]}</span>
                </div>
                <span className="text-sm font-bold tracking-tight">{row.original.away_team_name}</span>
              </div>
              {row.original.away_score !== null && (
                <span className="text-sm font-black text-primary">{row.original.away_score}</span>
              )}
            </div>
          </div>
        ),
      },
      {
        id: 'odds',
        header: () => <span className="font-black uppercase text-[10px] tracking-widest text-muted-foreground">Market Odds</span>,
        cell: ({ row }) => {
          const { home_odds, draw_odds, away_odds } = row.original
          if (!home_odds || !draw_odds || !away_odds)
            return <span className="text-[10px] font-bold opacity-30 uppercase">N/A</span>
          return (
            <div className="flex gap-1.5">
              <div className="flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-lg bg-white/5 border border-white/5 min-w-[42px] group-hover:bg-white/10 transition-colors">
                <span className="text-[8px] font-black text-muted-foreground uppercase leading-none">1</span>
                <span className="text-xs font-black">{home_odds.toFixed(2)}</span>
              </div>
              <div className="flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-lg bg-white/5 border border-white/5 min-w-[42px] group-hover:bg-white/10 transition-colors">
                <span className="text-[8px] font-black text-muted-foreground uppercase leading-none">X</span>
                <span className="text-xs font-black">{draw_odds.toFixed(2)}</span>
              </div>
              <div className="flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-lg bg-white/5 border border-white/5 min-w-[42px] group-hover:bg-white/10 transition-colors">
                <span className="text-[8px] font-black text-muted-foreground uppercase leading-none">2</span>
                <span className="text-xs font-black">{away_odds.toFixed(2)}</span>
              </div>
            </div>
          )
        },
      },
      {
        accessorKey: 'status_id',
        header: () => <span className="font-black uppercase text-[10px] tracking-widest text-muted-foreground">Status</span>,
        cell: ({ row }) => {
          const statusId = row.original.status_id
          const statuses: Record<number, { label: string, color: string }> = {
            1: { label: 'Scheduled', color: 'bg-muted/20 text-muted-foreground' },
            2: { label: 'Live', color: 'bg-destructive/20 text-destructive border-destructive/20 animate-pulse' },
            3: { label: 'Finished', color: 'bg-primary/20 text-primary border-primary/20' },
          }
          const s = statuses[statusId] || { label: 'Unknown', color: 'bg-muted/20 text-muted-foreground' }
          return (
            <Badge variant="outline" className={cn('px-2 py-0.5 rounded-lg font-black text-[10px] uppercase tracking-widest border-transparent', s.color)}>
              {s.label}
            </Badge>
          )
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
    state: { sorting },
    initialState: { pagination: { pageSize: 20 } },
  })

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-white/5 bg-transparent overflow-hidden">
        <Table>
          <TableHeader className="bg-white/2 border-b border-white/5 h-12">
            {table.getHeaderGroups().map(hg => (
              <TableRow key={hg.id} className="hover:bg-transparent border-none">
                {hg.headers.map(h => (
                  <TableHead key={h.id} className="text-muted-foreground px-6">
                    {h.isPlaceholder ? null : flexRender(h.column.columnDef.header, h.getContext())}
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
                      className={cn(
                        'group border-white/5 px-6 transition-all duration-200',
                        onRowClick ? 'cursor-pointer hover:bg-white/[0.04]' : '',
                      )}
                    >
                      {row.getVisibleCells().map(cell => (
                        <TableCell key={cell.id} className="py-4 px-6 border-none">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                )
              : (
                  <TableRow>
                    <TableCell colSpan={columns.length} className="h-32 text-center text-muted-foreground/30 font-bold italic border-none">
                      No fixtures match your criteria.
                    </TableCell>
                  </TableRow>
                )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between px-2">
        <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground opacity-50">
          Page
          {' '}
          {table.getState().pagination.pageIndex + 1}
          {' '}
          of
          {' '}
          {table.getPageCount()}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            className="rounded-xl h-8 text-[10px] font-black uppercase tracking-widest hover:bg-white/5"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Prev
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="rounded-xl h-8 text-[10px] font-black uppercase tracking-widest hover:bg-white/5"
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
