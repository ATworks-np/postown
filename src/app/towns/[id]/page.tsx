import TownStage from '@/components/TownStage'

export default async function TownByIdPage({
                                             params
                                           }: {
  params: Promise<{ id: string }>
}) {
  const resolvedParams = await params;
  const id = resolvedParams.id;

  if (!id) return null;

  return <TownStage townId={id} />;
}