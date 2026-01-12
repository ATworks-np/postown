"use client"
import { useEffect, useMemo, useState } from 'react'
import { collection, getDocs, query, where } from 'firebase/firestore'
import { db } from '../firebase'
import type { Building } from '../models/building'

export interface UseBuildingsOptions {
  category?: string
}

export interface UseBuildingsResult {
  data: (Building & { id: string })[]
  loading: boolean
  error: string | null
}

export function useBuildings(townId: string, opts: UseBuildingsOptions = {}): UseBuildingsResult {
  const [data, setData] = useState<(Building & { id: string })[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const qDeps = useMemo(() => ({ townId, category: opts.category }), [townId, opts.category])

  useEffect(() => {
    let canceled = false
    async function run() {
      setLoading(true)
      setError(null)
      try {
        const base = collection(db, 'towns', qDeps.townId, 'buildings')
        const qRef = qDeps.category ? query(base, where('category', '==', qDeps.category)) : base
        const snap = await getDocs(qRef)
        const rows: (Building & { id: string })[] = []
        snap.forEach(docSnap => {
          const raw = docSnap.data() as Building
          rows.push({ ...raw, id: docSnap.id })
        })
        if (!canceled) setData(rows)
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Unknown error'
        if (!canceled) setError(msg)
      } finally {
        if (!canceled) setLoading(false)
      }
    }
    run()
    return () => { canceled = true }
  }, [qDeps])

  return { data, loading, error }
}
