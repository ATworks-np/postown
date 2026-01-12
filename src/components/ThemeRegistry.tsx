"use client"
import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { theme } from '../theme/theme'
import React from 'react'

type Props = {
  children: React.ReactNode
}

export function ThemeRegistry({ children }: Props) {
  return (
    <AppRouterCacheProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </AppRouterCacheProvider>
  )
}

export default ThemeRegistry
