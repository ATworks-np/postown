"use client"
import { Container, TextField, Button, Paper } from '@mui/material'
import { useXListId } from '../hooks/useXListId'
import TownStage from '../components/TownStage'
import { useRouter } from 'next/navigation'
import { db } from '../firebase'
import { collection, getDocs, limit, query, where } from 'firebase/firestore'

const TOWN_ID = '3PJ0B7ZqINXYirzCvVEt'

export default function Home() {
  const xlist = useXListId()
  const router = useRouter()

  return (
    <Container disableGutters sx={{ py: 4 }}>
      <TownStage townId={TOWN_ID} unitPx={80}>
        {/* 画面中央下側の入力 + Go ボタン（ステージ上に重ねて表示） */}
        <Paper
          elevation={3}
          sx={{
            position: 'absolute',
            left: '50%',
            bottom: '30%',
            transform: 'translateX(-50%)',
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            px: 1.5,
            py: 1,
            borderRadius: 2,
            zIndex: 10,
            bgcolor: (theme) => theme.palette.background.paper,
          }}
        >
          <TextField
            size="small"
            variant="filled"
            label="x list idを入力"
            value={xlist.value}
            onChange={(e) => xlist.setValue(e.target.value)}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={async () => {
              const input = xlist.value?.trim()
              if (!input) {
                console.warn('x list id is empty')
                return
              }

              try {
                const townsRef = collection(db, 'towns')
                const q = query(
                  townsRef,
                  where('post_group_id', '==', input),
                  limit(1)
                )
                const snap = await getDocs(q)

                if (snap.empty) {
                  console.warn('No town found for post_group_id:', input)
                  router.push('/towns/new')
                  return
                }

                const doc = snap.docs[0]
                router.push(`/towns/${doc.id}`)
              } catch (e) {
                console.error('Failed to search town by post_group_id', e)
              }
            }}
          >
            街に訪れる
          </Button>
        </Paper>
      </TownStage>
    </Container>
  )
}
