
import type { AppProps } from 'next/app'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'
import { SnackbarProvider } from 'notistack'
import Head from 'next/head'

import Layout from '@/components/Layout'
import { useSystemStore } from '@/stores/systemStore'
import { useEffect } from 'react'

// Create Material-UI theme optimized for Mac
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#007AFF', // iOS blue
      light: '#5AC8FA',
      dark: '#0051D5',
    },
    secondary: {
      main: '#FF9500', // iOS orange
      light: '#FFCC02',
      dark: '#FF6D00',
    },
    background: {
      default: '#F2F2F7', // iOS background
      paper: '#FFFFFF',
    },
    text: {
      primary: '#000000',
      secondary: '#8E8E93',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      'SF Pro Display',
      'SF Pro Text',
      'Helvetica Neue',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      letterSpacing: '-0.025em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      letterSpacing: '-0.025em',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      letterSpacing: '-0.025em',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.43,
    },
  },
  shape: {
    borderRadius: 12, // iOS-style rounded corners
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
})

export default function App({ Component, pageProps }: AppProps) {
  const { initializeSystem } = useSystemStore()

  useEffect(() => {
    // Initialize system on app start
    initializeSystem()
  }, [initializeSystem])

  return (
    <>
      <Head>
        <title>Enhanced CPAS - Personal AI System</title>
        <meta name="description" content="Comprehensive Personal AI System with advanced capabilities" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <SnackbarProvider 
            maxSnack={3}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <Layout>
              <Component {...pageProps} />
            </Layout>
          </SnackbarProvider>
        </LocalizationProvider>
      </ThemeProvider>
    </>
  )
}
