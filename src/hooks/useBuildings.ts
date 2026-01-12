"use client"
import { useEffect, useMemo, useState } from 'react'
import { collection, getDocs, query, where } from 'firebase/firestore'
import { db } from '../firebase'
import type { Building } from '../models/building'
import type { BuildingPost } from '../models/building_post'

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

        // Fetch subcollection posts for each building (in parallel)
        const rows: (Building & { id: string })[] = await Promise.all(
          snap.docs.map(async (docSnap): Promise<Building & { id: string }> => {
            const raw = docSnap.data() as Building
            let posts: BuildingPost[] = []
            try {
              const postsCol = collection(db, 'towns', qDeps.townId, 'buildings', docSnap.id, 'posts')
              const postsSnap = await getDocs(postsCol)
              posts = postsSnap.docs.map(d => d.data() as BuildingPost)
              // Sort by created_at desc if available (ISO8601 string)
              posts.sort((a, b) => (b._created_at || '').localeCompare(a._created_at || ''))
            } catch {
              // If posts fetch fails for this building, fallback to empty array
              posts = []
            }
            return { ...raw, id: docSnap.id, posts }
          })
        )
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
