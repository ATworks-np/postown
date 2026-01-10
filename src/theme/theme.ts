import { createTheme } from "@mui/material/styles";

// カスタムカラーの定義
const cottageColors = {
  roofRed: '#D66D5E',       // 屋根の赤：少し彩度を落としたテラコッタ
  grassGreen: '#9CB071',    // 草の緑：落ち着いたオリーブグリーン
  woodBrown: '#8D6E63',     // 木材の茶：柱やドアの色
  paperWhite: '#FAF9F6',    // 紙の白：わずかに黄みがかったオフホワイト
  wallCream: '#FDFCF0',     // 壁のクリーム：カードやエリア背景用
  inkDark: '#42342B',       // インクの黒茶：文字色（完全な黒は使わない）
};

export const theme = createTheme({
  palette: {
    // 全体的な色のトーン（light/dark）
    mode: 'light',

    // メインカラー：屋根の色（ボタンやリンク）
    primary: {
      main: cottageColors.roofRed,
      contrastText: '#FFFFFF',
    },
    // サブカラー：草木の色（FABやアクセント）
    secondary: {
      main: cottageColors.grassGreen,
      contrastText: '#FFFFFF',
    },
    // 背景色
    background: {
      default: cottageColors.paperWhite, // アプリ全体の背景（画用紙）
      paper: cottageColors.wallCream,    // CardやModalの背景（家の壁）
    },
    // テキストカラー
    text: {
      primary: cottageColors.inkDark,     // メインの文字
      secondary: 'rgba(66, 52, 43, 0.7)', // 薄い文字も茶色ベースで透明度を下げる
    },
    // 区切り線など
    divider: 'rgba(66, 52, 43, 0.12)',
  },

  // フォント設定（手書き風の雰囲気に合うように丸みを推奨）
  typography: {
    fontFamily: [
      '"M PLUS Rounded 1c"', // 日本語の丸ゴシック（Google Fonts等で読み込み推奨）
      '"Nunito"',            // 英語の丸みのあるフォント
      '"Helvetica"',
      '"Arial"',
      'sans-serif',
    ].join(','),
    h1: {
      color: cottageColors.roofRed, // 見出しを屋根の色にするのも可愛い
      fontWeight: 700,
    },
    button: {
      textTransform: 'none', // アルファベットの強制大文字化を解除（優しく見せるため）
      fontWeight: 600,
    },
  },

  // コンポーネントのスタイル上書き（水彩風の「ゆらぎ」や「柔らかさ」を表現）
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '12px', // 角を少し丸くする
          boxShadow: 'none',    // デフォルトの影を消してフラットに（水彩っぽく）
          '&:hover': {
            boxShadow: '0 4px 12px rgba(214, 109, 94, 0.2)', // ホバー時だけふんわり影
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '16px',
          boxShadow: '0 4px 20px rgba(66, 52, 43, 0.08)', // 優しい影
          border: '1px solid rgba(66, 52, 43, 0.05)',     // うっすら輪郭線
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          // 紙の質感を出すならここにテクスチャ画像を背景に入れるのもアリ
        }
      }
    }
  },
});