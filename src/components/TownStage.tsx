"use client"
import { Box, CircularProgress, Typography, Divider } from '@mui/material'
import type { SxProps, Theme } from '@mui/material/styles'
import { useTown } from '../hooks/useTown'
import { useBuildings } from '../hooks/useBuildings'
import { useWindowSize } from '../hooks/useWindowSize'
import BuildingItem from './BuildingItem'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import BuildingOverlay from './BuildingOverlay'
import { useSelectedBuilding } from '../hooks/useSelectedBuilding'
import BuildingPostsList from './BuildingPostsList'

export type TownStageProps = {
  townId: string
  unitPx?: number
  minWidth?: number
  minHeight?: number
  containerVerticalPadding?: number
  containerSx?: SxProps<Theme>
  children?: React.ReactNode
}

export default function TownStage(props: TownStageProps) {
  const {
    townId,
    unitPx = 100,
    minWidth = 320,
    minHeight = 240,
    // ルートの Container の上下パディング分（py:4 = 32px * 2）をデフォルトで差し引く
    containerVerticalPadding = 64,
    containerSx,
    children,
  } = props

  const town = useTown(townId)
  const buildings = useBuildings(townId)
  const win = useWindowSize({ width: 960, height: 640 })

  const { selected, open, select, clear } = useSelectedBuilding()

  // Zoom (unitPx) — wheel to change smoothly
  const [zoomPx, setZoomPx] = useState(unitPx)
  const targetZoomRef = useRef(unitPx)
  const rafRef = useRef<number | null>(null)

  // sync when prop unitPx changes from outside (animate to it without direct setState)
  useEffect(() => {
    targetZoomRef.current = unitPx
    animateZoom()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [unitPx])

  const animateZoom = useCallback(() => {
    // Smoothly approach target using exponential smoothing
    const tick = () => {
      const target = targetZoomRef.current
      let shouldStop = false
      setZoomPx(prev => {
        const diff = target - prev
        if (Math.abs(diff) < 0.05) {
          shouldStop = true
          return target
        }
        const next = prev + diff * 0.18 // smoothing factor
        return next
      })
      if (shouldStop) {
        if (rafRef.current) cancelAnimationFrame(rafRef.current)
        rafRef.current = null
        return
      }
      rafRef.current = requestAnimationFrame(tick)
    }
    if (rafRef.current == null) {
      rafRef.current = requestAnimationFrame(tick)
    }
  }, [])

  const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v))

  const handleWheel = useCallback((e: React.WheelEvent) => {
    // BuildingOverlay が開いている間はズームを変更しない
    if (open) return
    // Prevent page scroll while zooming stage
    e.preventDefault()
    // deltaY positive means wheel down → zoom out
    // Use an exponential scale for smooth feel independent of frame rate
    const sensitivity = 0.0016
    const factor = Math.exp(-e.deltaY * sensitivity)
    const minPx = 40
    const maxPx = 260
    const nextTarget = clamp(targetZoomRef.current * factor, minPx, maxPx)
    targetZoomRef.current = nextTarget
    animateZoom()
  }, [animateZoom, open])

  const loading = town.loading || buildings.loading
  const error = town.error || buildings.error

  const stageW = Math.max(minWidth, win.width)
  const stageH = Math.max(minHeight, win.height - containerVerticalPadding)

  // 画面中心（x=0,y=0）
  const cx = stageW / 2
  const cy = stageH / 2

  if (loading) {
    return (
      <Box display="flex" alignItems="center" justifyContent="center" minHeight={minHeight} sx={containerSx}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Typography color="error" sx={containerSx}>
        {error}
      </Typography>
    )
  }

  return (
    <Box
      sx={{
        position: 'relative',
        width: stageW,
        height: stageH,
        mx: 'auto',
        overflow: 'hidden',
        ...containerSx,
      }}
      onWheel={handleWheel}
    >
      {(buildings.data ?? []).map(b => {
        const logicalSize = b.grid_size ?? 1
        const widthPx = logicalSize * zoomPx
        // isometric 風変換: x'=(x-y)*sqrt(2)/4, y'=(x+y)*sqrt(2)/4
        const x0 = b.row ?? 0
        const y0 = b.col ?? 0
        const scale = Math.SQRT2 / 4 + (Math.SQRT2/6)
        const xPrime = (x0 + y0 - 1) * scale
        const yPrime = (x0 - y0 - 1) * scale
        // UI ピクセルへ変換（左下アンカーは BuildingItem 側の transform で維持）
        const left = Math.round(cx + xPrime * zoomPx)
        const top = Math.round(cy - yPrime * zoomPx)
        return (
          <BuildingItem
            key={b.id}
            src={b.image_url}
            alt={b.name}
            widthPx={widthPx}
            left={left}
            top={top}
            sx={{ zIndex:  - x0 + y0 + 100 }}
            hoverFilter={'drop-shadow(0 0 14px rgba(255,255,0,0.9))'}
            cursor={'pointer'}
            onClick={() => {console.log(buildings.data); select(b)}}
          />
        )
      })}

      {children}

      <BuildingOverlay
        open={open}
        title={selected?.name}
        onClose={clear}
      >
        {selected && (
          <Box>
            <Typography variant="body1" color="text.secondary">
              Category: {selected.category}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Level: {selected.level}
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Grid Size: {selected.grid_size} / Pos: ({selected.row}, {selected.col})
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Posts
            </Typography>
            <BuildingPostsList posts={selected.posts} />
          </Box>
        )}
      </BuildingOverlay>
    </Box>
  )
}
