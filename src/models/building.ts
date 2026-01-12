import {BuildingPost} from "@/models/building_post";

export interface Building {
  _created_at: string
  _deleted_at?: string | null
  category: string
  image_url: string
  level: number
  name: string
  grid_size: number
  row: number
  col: number
  posts: BuildingPost[]
}
