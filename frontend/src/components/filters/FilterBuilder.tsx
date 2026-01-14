import { useState } from 'react'
import { IconPlus } from '@tabler/icons-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { RuleRow } from './RuleRow'
import { BET_TYPES } from '@/lib/filterFields'
import type { FilterRule, CreateFilterRequest } from '@/types/filter'

interface FilterBuilderProps {
  initialData?: {
    name: string
    description: string
    bet_type: string
    rules: FilterRule[]
    is_active: boolean
  }
  onSubmit: (data: CreateFilterRequest) => void
  onCancel: () => void
  isSubmitting?: boolean
}

export function FilterBuilder({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: FilterBuilderProps) {
  const [name, setName] = useState(initialData?.name || '')
  const [description, setDescription] = useState(initialData?.description || '')
  const [betType, setBetType] = useState(initialData?.bet_type || 'home_win')
  const [rules, setRules] = useState<FilterRule[]>(
    initialData?.rules || [
      {
        field: 'home_odds',
        operator: '>=',
        value: 1.5,
      },
    ]
  )
  const [isActive, setIsActive] = useState(initialData?.is_active ?? true)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleAddRule = () => {
    setRules([
      ...rules,
      {
        field: 'home_odds',
        operator: '>=',
        value: 1.5,
      },
    ])
  }

  const handleRuleChange = (index: number, rule: FilterRule) => {
    const newRules = [...rules]
    newRules[index] = rule
    setRules(newRules)
  }

  const handleRemoveRule = (index: number) => {
    if (rules.length > 1) {
      setRules(rules.filter((_, i) => i !== index))
    }
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!name.trim()) {
      newErrors.name = 'Filter name is required'
    } else if (name.length > 100) {
      newErrors.name = 'Filter name must be less than 100 characters'
    }

    if (description && description.length > 500) {
      newErrors.description = 'Description must be less than 500 characters'
    }

    if (rules.length === 0) {
      newErrors.rules = 'At least one rule is required'
    } else if (rules.length > 10) {
      newErrors.rules = 'Maximum 10 rules allowed'
    }

    // Validate each rule
    rules.forEach((rule, index) => {
      if (!rule.field) {
        newErrors[`rule_${index}_field`] = 'Field is required'
      }
      if (!rule.operator) {
        newErrors[`rule_${index}_operator`] = 'Operator is required'
      }
      if (rule.value === null || rule.value === undefined || rule.value === '') {
        newErrors[`rule_${index}_value`] = 'Value is required'
      }
    })

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    onSubmit({
      name: name.trim(),
      description: description.trim() || undefined,
      bet_type: betType,
      rules,
      is_active: isActive,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Info */}
      <Card>
        <CardHeader>
          <CardTitle>Filter Information</CardTitle>
          <CardDescription>Basic details about your filter strategy</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">
              Filter Name <span className="text-destructive">*</span>
            </Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., High Home Odds Filter"
              maxLength={100}
            />
            {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe your filter strategy..."
              rows={3}
              maxLength={500}
            />
            {errors.description && (
              <p className="text-sm text-destructive">{errors.description}</p>
            )}
          </div>

          {/* Bet Type */}
          <div className="space-y-2">
            <Label htmlFor="bet-type">
              Bet Type <span className="text-destructive">*</span>
            </Label>
            <Select value={betType} onValueChange={setBetType}>
              <SelectTrigger id="bet-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {BET_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Active Status */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is-active"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
              className="h-4 w-4"
            />
            <Label htmlFor="is-active" className="cursor-pointer">
              Activate filter immediately
            </Label>
          </div>
        </CardContent>
      </Card>

      {/* Filter Rules */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Filter Rules</CardTitle>
              <CardDescription>
                Define conditions that fixtures must meet ({rules.length}/10 rules)
              </CardDescription>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAddRule}
              disabled={rules.length >= 10}
            >
              <IconPlus className="h-4 w-4 mr-2" />
              Add Rule
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {errors.rules && <p className="text-sm text-destructive">{errors.rules}</p>}
          {rules.map((rule, index) => (
            <RuleRow
              key={index}
              rule={rule}
              index={index}
              onChange={handleRuleChange}
              onRemove={handleRemoveRule}
            />
          ))}
        </CardContent>
      </Card>

      {/* Matching Fixtures Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Matching Fixtures</CardTitle>
          <CardDescription>Preview of fixtures that meet your criteria</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Preview feature coming soon. Save your filter to see matching fixtures.
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex gap-3 justify-end">
        <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Saving...' : initialData ? 'Update Filter' : 'Create Filter'}
        </Button>
      </div>
    </form>
  )
}
