import { Timestamp } from 'firebase/firestore';

export interface BuildingPost {
  _created_at: Timestamp
  post_id: string
  original_post_id: string | undefined
}
