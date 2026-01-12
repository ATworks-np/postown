import TownStage from '@/components/TownStage'

export default function TownByIdPage({ params }: { params: { id: string } }) {
  const id = Array.isArray(params?.id) ? params.id[0] : params?.id
  if (!id) return null
  return <TownStage townId={id} />
}
