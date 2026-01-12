"use client"
import { useEffect, useRef, useCallback } from 'react'

declare global {
  interface Window {
    twttr?: {
      widgets: {
        load: (element?: Element) => void
      }
    }
  }
}

export function useTwitterWidgets() {
  const loadedRef = useRef<boolean>(false)
  const callbacksRef = useRef<(() => void)[]>([])

  useEffect(() => {
    if (typeof window === 'undefined') return
    if (window.twttr?.widgets) {
      loadedRef.current = true
      callbacksRef.current.forEach(cb => cb())
      callbacksRef.current = []
      return
    }

    const existed = document.querySelector('script[data-twitter-widgets]') as HTMLScriptElement | null
    if (existed) return

    const script = document.createElement('script')
    script.src = 'https://platform.twitter.com/widgets.js'
    script.async = true
    script.defer = true
    script.setAttribute('data-twitter-widgets', 'true')
    script.onload = () => {
      loadedRef.current = true
      callbacksRef.current.forEach(cb => cb())
      callbacksRef.current = []
    }
    document.body.appendChild(script)
  }, [])

  const load = useCallback((el?: Element) => {
    const doLoad = () => {
      try {
        window.twttr?.widgets?.load(el)
      } catch {
        // no-op
      }
    }
    if (loadedRef.current) {
      doLoad()
    } else {
      callbacksRef.current.push(doLoad)
    }
  }, [])

  return { load }
}
