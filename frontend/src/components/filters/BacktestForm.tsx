import type { BacktestRequest, BetType } from '@/types/backtest'
import { IconChartBar } from '@tabler/icons-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface BacktestFormProps {
  onSubmit: (data: BacktestRequest) => void
  isLoading?: boolean
}

const BET_TYPES: Array<{ value: BetType, label: string }> = [
  { value: 'home_win', label: 'Home Win' },
  { value: 'away_win', label: 'Away Win' },
  { value: 'draw', label: 'Draw' },
  { value: 'over_2_5', label: 'Over 2.5 Goals' },
  { value: 'under_2_5', label: 'Under 2.5 Goals' },
]

const AVAILABLE_SEASONS = [2020, 2021, 2022, 2023, 2024, 2025]

export function BacktestForm({ onSubmit, isLoading = false }: BacktestFormProps) {
  const [betType, setBetType] = useState<BetType>('home_win')
  const [selectedSeasons, setSelectedSeasons] = useState<number[]>([2024, 2025])
  const [stake, setStake] = useState<number>(10)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSeasonToggle = (season: number) => {
    if (selectedSeasons.includes(season)) {
      setSelectedSeasons(selectedSeasons.filter(s => s !== season))
    }
    else {
      if (selectedSeasons.length < 5) {
        setSelectedSeasons([...selectedSeasons, season].sort())
      }
    }
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (selectedSeasons.length === 0) {
      newErrors.seasons = 'Select at least one season'
    }

    if (stake <= 0) {
      newErrors.stake = 'Stake must be greater than 0'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    onSubmit({
      bet_type: betType,
      seasons: selectedSeasons,
      stake,
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <IconChartBar className="h-5 w-5" />
          Run Backtest
        </CardTitle>
        <CardDescription>
          Test your filter against historical data to evaluate performance
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Bet Type */}
          <div className="space-y-2">
            <Label htmlFor="bet-type">
              Bet Type
              {' '}
              <span className="text-destructive">*</span>
            </Label>
            <Select value={betType} onValueChange={value => setBetType(value as BetType)}>
              <SelectTrigger id="bet-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {BET_TYPES.map(type => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Seasons */}
          <div className="space-y-2">
            <Label>
              Seasons
              {' '}
              <span className="text-destructive">*</span>
            </Label>
            <div className="flex flex-wrap gap-2">
              {AVAILABLE_SEASONS.map(season => (
                <button
                  key={season}
                  type="button"
                  onClick={() => handleSeasonToggle(season)}
                  className={`px-4 py-2 rounded-md border transition-colors ${selectedSeasons.includes(season)
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'bg-background hover:bg-muted border-input'
                  }`}
                >
                  {season}
                </button>
              ))}
            </div>
            {errors.seasons && <p className="text-sm text-destructive">{errors.seasons}</p>}
            <p className="text-sm text-muted-foreground">
              Selected:
              {' '}
              {selectedSeasons.length}
              {' '}
              season
              {selectedSeasons.length !== 1 ? 's' : ''}
              {' '}
              (max
              5)
            </p>
          </div>

          {/* Stake */}
          <div className="space-y-2">
            <Label htmlFor="stake">
              Stake Amount
              {' '}
              <span className="text-destructive">*</span>
            </Label>
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">$</span>
              <Input
                id="stake"
                type="number"
                value={stake}
                onChange={e => setStake(Number.parseFloat(e.target.value))}
                min={0.01}
                step={0.01}
                className="w-32"
              />
            </div>
            {errors.stake && <p className="text-sm text-destructive">{errors.stake}</p>}
            <p className="text-sm text-muted-foreground">Flat stake amount per bet</p>
          </div>

          {/* Submit Button */}
          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? 'Running Backtest...' : 'Run Backtest'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
