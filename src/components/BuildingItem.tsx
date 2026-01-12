"use client"
import { Box } from '@mui/material'
import type { SxProps, Theme } from '@mui/material/styles'
import Image from 'next/image'

export type BuildingItemProps = {
  src: string
  alt: string
  widthPx: number
  left?: number
  top?: number
  absolute?: boolean
  baseFilter?: string
  hoverFilter?: string
  cursor?: 'default' | 'pointer'
  sx?: SxProps<Theme>
  onClick?: () => void
}

export default function BuildingItem(props: BuildingItemProps) {
  const {
    src,
    alt,
    widthPx,
    left,
    top,
    absolute = true,
    baseFilter = 'drop-shadow(0 0 0 rgba(0,0,0,0))',
    hoverFilter,
    cursor = 'default',
    sx,
    onClick,
  } = props

  const containerSx: SxProps<Theme> = {
    position: absolute ? 'absolute' : 'relative',
    left,
    top,
    transform: 'translateY(-100%)', // 左下基準にするため（top が下端に対応）
    ...sx,
    '& img': {
      transition: 'filter 0.3s ease',
      filter: baseFilter,
      cursor,
    },
    ...(hoverFilter
      ? {
          '&:hover img': {
            filter: hoverFilter,
          },
        }
      : {}),
  }

  return (
    <Box sx={containerSx} onClick={onClick}>
      <Image
        src={src}
        alt={alt}
        width={0}
        height={0}
        sizes={`${Math.round(widthPx)}px`}
        style={{ width: `${widthPx}px`, height: 'auto' }}
      />
    </Box>
  )
}
