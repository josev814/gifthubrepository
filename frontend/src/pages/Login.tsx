import React, { useState } from 'react'
import { Box, TextField, Button, Typography } from '@mui/material'
import api from '../utils/api'
import { useNavigate } from 'react-router-dom'

export default function Login(){
  const [email,setEmail]=useState(''); const [password,setPassword]=useState('')
  const nav = useNavigate()
  async function submit(e:any){
    e.preventDefault()
    const body = new URLSearchParams()
    body.append('username', email)
    body.append('password', password)
    try{
      const res = await api.post('/api/token', body)
      localStorage.setItem('token', res.data.access_token)
      nav('/')
    }catch(err){ alert('Login failed') }
  }
  return (
    <Box sx={{maxWidth:480,mt:4}}>
      <Typography variant="h5" gutterBottom>Login</Typography>
      <form onSubmit={submit}>
        <TextField label="Email" fullWidth value={email} onChange={e=>setEmail(e.target.value)} sx={{mb:2}} />
        <TextField label="Password" fullWidth type="password" value={password} onChange={e=>setPassword(e.target.value)} sx={{mb:2}} />
        <Button type="submit" variant="contained">Login</Button>
      </form>
    </Box>
  )
}
