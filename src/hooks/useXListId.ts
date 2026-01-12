"use client"
import { useState, useCallback } from 'react'

export interface UseXListIdResult {
  value: string
  setValue: (v: string) => void
  clear: () => void
}

// x list id の入力値を管理するカスタムフック
export function useXListId(initial = ''): UseXListIdResult {
  const [value, setValue] = useState<string>(initial)
  const clear = useCallback(() => setValue(''), [])
  return { value, setValue, clear }
}

export default useXListId
