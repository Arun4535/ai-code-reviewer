import { ReviewDetails } from "@/components/review-details";

export default async function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <ReviewDetails reviewId={Number(id)} />;
}
