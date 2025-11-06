import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Box, Typography, IconButton, Button, InputBase, Paper } from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Register from './pages/Register'
import RegistryView from './pages/RegistryView'
import NewRegistry from './pages/NewRegistry'
import Profile from './pages/Profile'
import apiClient from './utils/api'

function Header(){
  return (
    <AppBar position="static" color="default" elevation={1}>
      <Toolbar className="container" sx={{display:'flex',gap:2}}>
        <Link to="/" className="header-brand">
          <Typography variant="h6" color="primary">GiftRegistry</Typography>
        </Link>
        <Paper component="form" sx={{display:'flex',alignItems:'center',width:500,ml:2,px:1}} onSubmit={(e)=>{ e.preventDefault(); /* implement quick search */ }}>
          <InputBase sx={{ml:1,flex:1}} placeholder="Search gifts, items, registries" inputProps={{ 'aria-label': 'search' }} />
          <IconButton type="submit" sx={{p:1}}><SearchIcon /></IconButton>
        </Paper>
        <Box sx={{ml:'auto',display:'flex',gap:1}}>
          <Button component={Link} to="/profile">Profile</Button>
          <Button component={Link} to="/login" variant="contained">Login</Button>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default function App(){
  return (
    <div>
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/registries/new" element={<NewRegistry />} />
          <Route path="/registries/:shareId" element={<RegistryView />} />
        </Routes>
      </main>
    </div>
  )
}
