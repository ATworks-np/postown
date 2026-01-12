"use client"
import { useEffect, useState } from 'react'

export interface WindowSize {
  width: number
  height: number
}

// 現在の window サイズを返すカスタムフック（SSR セーフ、rAF でリサイズをスロットル）
export function useWindowSize(initial: WindowSize = { width: 960, height: 640 }): WindowSize {
  const [size, setSize] = useState<WindowSize>(initial)

  useEffect(() => {
    let frame = 0

    const update = () => {
      setSize({ width: window.innerWidth, height: window.innerHeight })
    }

    // 初回
    update()

    const onResize = () => {
      if (frame) cancelAnimationFrame(frame)
      frame = requestAnimationFrame(() => {
        frame = 0
        update()
      })
    }

    window.addEventListener('resize', onResize)
    return () => {
      if (frame) cancelAnimationFrame(frame)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  return size
}

export default useWindowSize
