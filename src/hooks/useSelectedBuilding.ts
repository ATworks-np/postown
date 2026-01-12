"use client"
import React from 'react'
import type { Building } from '../models/building'

export interface SelectedBuildingState {
  selected: (Building & { id: string }) | null
  open: boolean
}

export interface UseSelectedBuildingResult extends SelectedBuildingState {
  select: (b: Building & { id: string }) => void
  clear: () => void
}

export function useSelectedBuilding(): UseSelectedBuildingResult {
  const [selected, setSelected] = React.useState<(Building & { id: string }) | null>(null)
  const open = !!selected

  const select = React.useCallback((b: Building & { id: string }) => setSelected(b), [])
  const clear = React.useCallback(() => setSelected(null), [])

  return { selected, open, select, clear }
}
