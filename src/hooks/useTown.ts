"use client"
import { useEffect, useState } from 'react'
import { doc, getDoc } from 'firebase/firestore'
import { db } from '../firebase'
import type { Town } from '../models/town'

export interface UseTownResult {
  data: (Town & { id: string }) | null
  loading: boolean
  error: string | null
}

export function useTown(townId: string): UseTownResult {
  const [data, setData] = useState<(Town & { id: string }) | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let canceled = false
    async function run() {
      setLoading(true)
      setError(null)
      try {
        const ref = doc(db, 'towns', townId)
        const snap = await getDoc(ref)
        if (!snap.exists()) {
          if (!canceled) setError('Town not found')
          return
        }
        const raw = snap.data() as Town
        if (!canceled) setData({ ...raw, id: snap.id })
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Unknown error'
        if (!canceled) setError(msg)
      } finally {
        if (!canceled) setLoading(false)
      }
    }
    run()
    return () => {
      canceled = true
    }
  }, [townId])

  return { data, loading, error }
}
