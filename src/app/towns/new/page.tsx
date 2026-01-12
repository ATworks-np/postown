"use client"
import { Container, Paper, Typography, Button, Stack } from '@mui/material'
import { useRouter } from 'next/navigation'

export default function NewTownPage() {
  const router = useRouter()

  return (
    <Container maxWidth="sm" sx={{ py: 6 }}>
      <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
        <Stack spacing={2}>
          <Typography variant="h4" component="h1">
            新しい街を作成
          </Typography>
          <Typography variant="body1" color="text.secondary">
            入力されたIDに該当する街が見つかりませんでした。新しい街を作成しますか？
          </Typography>
          <Stack direction="row" spacing={1}>
            <Button variant="contained" color="primary" disabled>
              街を作成（準備中）
            </Button>
            <Button variant="text" onClick={() => router.push('/')}>戻る</Button>
          </Stack>
        </Stack>
      </Paper>
    </Container>
  )
}
