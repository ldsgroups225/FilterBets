import type { FilterRule } from '@/types/filter'
import { IconTrash } from '@tabler/icons-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { FILTER_FIELDS, getFieldConfig, OPERATOR_LABELS } from '@/lib/filterFields'

interface RuleRowProps {
  rule: FilterRule
  index: number
  onChange: (index: number, rule: FilterRule) => void
  onRemove: (index: number) => void
}

export function RuleRow({ rule, index, onChange, onRemove }: RuleRowProps) {
  const fieldConfig = getFieldConfig(rule.field)

  const handleFieldChange = (field: string | null) => {
    if (!field)
      return
    const config = getFieldConfig(field)
    const defaultOperator = config?.operators[0] || '='
    onChange(index, {
      field,
      operator: defaultOperator,
      value: config?.type === 'number' ? 0 : '',
    })
  }

  const handleOperatorChange = (operator: string | null) => {
    if (!operator)
      return
    onChange(index, {
      ...rule,
      operator: operator as FilterRule['operator'],
      value: operator === 'between' ? [0, 0] : operator === 'in' ? [] : rule.value,
    })
  }

  const handleValueChange = (value: string | number | string[] | [number, number]) => {
    onChange(index, { ...rule, value })
  }

  const renderValueInput = () => {
    if (!fieldConfig)
      return null

    // Between operator - two number inputs
    if (rule.operator === 'between') {
      const values = Array.isArray(rule.value) ? rule.value : [0, 0]
      return (
        <div className="flex gap-2 items-center">
          <Input
            type="number"
            value={values[0]}
            onChange={e => handleValueChange([Number.parseFloat(e.target.value), values[1] as number])}
            min={fieldConfig.min}
            max={fieldConfig.max}
            step={fieldConfig.step}
            className="w-24"
          />
          <span className="text-muted-foreground">and</span>
          <Input
            type="number"
            value={values[1]}
            onChange={e => handleValueChange([values[0] as number, Number.parseFloat(e.target.value)])}
            min={fieldConfig.min}
            max={fieldConfig.max}
            step={fieldConfig.step}
            className="w-24"
          />
        </div>
      )
    }

    // In operator with select - multiple values
    if (rule.operator === 'in' && fieldConfig.type === 'select' && fieldConfig.options) {
      const currentValues = Array.isArray(rule.value) ? (rule.value as string[]) : []
      return (
        <Select
          value={currentValues[0] || ''}
          onValueChange={(value) => {
            if (!value)
              return
            if (!currentValues.includes(value)) {
              handleValueChange([...currentValues, value])
            }
          }}
        >
          <SelectTrigger className="w-48">
            <SelectValue>
              {currentValues.length > 0
                ? `${currentValues.length} selected`
                : 'Select values'}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {fieldConfig.options.map(option => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )
    }

    // Select field
    if (fieldConfig.type === 'select' && fieldConfig.options) {
      return (
        <Select
          value={typeof rule.value === 'string' ? rule.value : ''}
          onValueChange={value => value && handleValueChange(value)}
        >
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {fieldConfig.options.map(option => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )
    }

    // Number field
    if (fieldConfig.type === 'number') {
      return (
        <Input
          type="number"
          value={typeof rule.value === 'number' ? rule.value : 0}
          onChange={e => handleValueChange(Number.parseFloat(e.target.value))}
          min={fieldConfig.min}
          max={fieldConfig.max}
          step={fieldConfig.step}
          className="w-32"
        />
      )
    }

    // String field (fallback)
    return (
      <Input
        type="text"
        value={typeof rule.value === 'string' ? rule.value : ''}
        onChange={e => handleValueChange(e.target.value)}
        className="w-48"
      />
    )
  }

  return (
    <div className="flex gap-3 items-end p-4 border rounded-lg bg-muted/50">
      {/* Field Selection */}
      <div className="flex-1 space-y-2">
        <Label>Field</Label>
        <Select value={rule.field} onValueChange={handleFieldChange}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {FILTER_FIELDS.map(field => (
              <SelectItem key={field.field} value={field.field}>
                {field.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Operator Selection */}
      <div className="w-40 space-y-2">
        <Label>Operator</Label>
        <Select value={rule.operator} onValueChange={handleOperatorChange}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {fieldConfig?.operators.map(op => (
              <SelectItem key={op} value={op}>
                {OPERATOR_LABELS[op]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Value Input */}
      <div className="flex-1 space-y-2">
        <Label>Value</Label>
        {renderValueInput()}
      </div>

      {/* Remove Button */}
      <Button
        type="button"
        variant="outline"
        size="icon"
        onClick={() => onRemove(index)}
        className="flex-shrink-0"
      >
        <IconTrash className="h-4 w-4 text-destructive" />
      </Button>
    </div>
  )
}
