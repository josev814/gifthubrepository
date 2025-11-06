import { createTheme } from '@mui/material/styles'
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#ff6f00' },
  },
  typography: {
    fontFamily: ['Inter', 'Helvetica', 'Arial', 'sans-serif'].join(','),
  },
})
export default theme
