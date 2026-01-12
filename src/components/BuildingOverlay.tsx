"use client"
import React from 'react'
import { Box, IconButton, Paper, Typography } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import { useTheme } from '@mui/material/styles'
import useMediaQuery from '@mui/material/useMediaQuery'
import { keyframes } from '@emotion/react'

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

  // Mount-while-exiting to enable fade-out/slide-out animations
  const [render, setRender] = React.useState<boolean>(open)
  const [exiting, setExiting] = React.useState<boolean>(false)

  React.useEffect(() => {
    if (open) {
      setRender(true)
      setExiting(false)
      return
    }
    if (render) {
      // start exit animation then unmount after it finishes
      setExiting(true)
      const t = setTimeout(() => {
        setRender(false)
        setExiting(false)
      }, 260) // match panel animation duration
      return () => clearTimeout(t)
    }
  }, [open, render])

  if (!render) return null

  const panelWidth = isDesktop ? 500 : '100%'

  const slideIn = keyframes({
    from: { transform: 'translateX(100%)' },
    to: { transform: 'translateX(0%)' },
  })

  const slideOut = keyframes({
    from: { transform: 'translateX(0%)' },
    to: { transform: 'translateX(100%)' },
  })

  const fadeIn = keyframes({
    from: { opacity: 0 },
    to: { opacity: 1 },
  })

  const fadeOut = keyframes({
    from: { opacity: 1 },
    to: { opacity: 0 },
  })

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
          animation: `${exiting ? fadeOut : fadeIn} 240ms ease-out forwards`,
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
          animation: `${exiting ? slideOut : slideIn} 260ms cubic-bezier(0.2, 0, 0, 1) forwards`,
          willChange: 'transform',
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
