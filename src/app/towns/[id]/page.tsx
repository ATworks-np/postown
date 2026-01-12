import TownStage from '@/components/TownStage'

// 静的エクスポート前提で動的挙動を禁止（保険）
export const dynamic = 'error'
export const dynamicParams = false

export function generateStaticParams(): { id: string }[] {
  const fromEnv = process.env.NEXT_PUBLIC_TOWN_IDS ?? ''
  const ids = fromEnv
    .split(',')
    .map(s => s.trim())
    .filter(Boolean)
  const params = ids.map(id => ({ id }))
  // Build 時の確認用ログ（Next.js は build 中に出力する場合があります）
  if (process.env.NODE_ENV === 'production') {
    console.log('[generateStaticParams] towns/[id] ->', params)
  }
  return params
}

export default function TownByIdPage({ params }: { params: { id: string } }) {
  const id = Array.isArray(params?.id) ? params.id[0] : params?.id
  if (!id) return null
  return <TownStage townId={id} />
}
