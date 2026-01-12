"use client"
import React from 'react'
import { Box, Stack, Typography, Divider } from '@mui/material'
import type { BuildingPost } from '@/models/building_post'
import { Tweet } from 'react-tweet'

export type BuildingPostsListProps = {
  posts: BuildingPost[] | undefined
}

export default function BuildingPostsList(props: BuildingPostsListProps) {
  const { posts } = props
  const containerRef = React.useRef<HTMLDivElement | null>(null)

  if (!posts || posts.length === 0) {
    return (
      <Box>
        <Typography variant="body2" color="text.secondary">
          投稿はまだありません。
        </Typography>
      </Box>
    )
  }

  return (
    <Stack ref={containerRef} spacing={0}>
      {posts.map((p) => {
        const id = p.tweet_id ?? p.post_id
        if (!id) return null
        return (
          <Box key={id} sx={{ width: '100%' }} data-theme={'light'}>
            <Tweet id={id}/>
          </Box>
        )
      })}
    </Stack>
  )
}
