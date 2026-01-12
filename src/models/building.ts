import {BuildingPost} from "@/models/building_post";
import { Timestamp } from 'firebase/firestore';

export interface Building {
  _created_at: Timestamp
  _deleted_at?: Timestamp | null
  category: string
  image_url: string
  level: number
  name: string
  grid_size: number
  row: number
  col: number
  posts: BuildingPost[]
}
