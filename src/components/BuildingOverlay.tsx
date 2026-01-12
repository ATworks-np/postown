"use client"
import React from 'react'
import { Box, IconButton, Paper, Typography } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import { useTheme } from '@mui/material/styles'
import useMediaQuery from '@mui/material/useMediaQuery'

export type BuildingOverlayProps = {
  open: boolean
  title?: string
  onClose: () => void
  children?: React.ReactNode
}

export default function BuildingOverlay(props: BuildingOverlayProps) {
  const { open, title, onClose, children } = props
  const theme = useTheme()
  const isDesktop = useMediaQuery(theme.breakpoints.up('sm'))

  if (!open) return null

  const panelWidth = isDesktop ? 500 : '100%'

  return (
    <Box
      sx={{
        position: 'fixed',
        inset: 0,
        zIndex: theme.zIndex.modal,
      }}
    >
      {/* Backdrop */}
      <Box
        onClick={onClose}
        sx={{
          position: 'absolute',
          inset: 0,
          backgroundColor: 'rgba(0,0,0,0.4)',
        }}
      />

      {/* Panel */}
      <Paper
        elevation={8}
        square
        sx={{
          position: 'absolute',
          right: 0,
          top: 0,
          height: '100%',
          width: panelWidth,
          display: 'flex',
          flexDirection: 'column',
          borderTopLeftRadius: 8,
          borderBottomLeftRadius: 8,
          overflow: 'hidden',
        }}
      >
        <Box sx={{ position: 'relative', p: 2, borderBottom: `1px solid ${theme.palette.divider}` }}>
          <Typography variant="h6" component="h2">
            {title}
          </Typography>
          <IconButton
            aria-label="close"
            onClick={onClose}
            sx={{ position: 'absolute', right: 8, top: 8 }}
            size="small"
          >
            <CloseIcon />
          </IconButton>
        </Box>
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>{children}</Box>
      </Paper>
    </Box>
  )
}
