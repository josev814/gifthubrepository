import React, { useState } from 'react'
import { Box, TextField, Button, Typography } from '@mui/material'
import api from '../utils/api'
import { useNavigate } from 'react-router-dom'

export default function Register(){
  const [email,setEmail]=useState(''); const [password,setPassword]=useState('')
  const nav = useNavigate()
  async function submit(e:any){
    e.preventDefault()
    try{
      const res = await api.post('/api/register', { email, password })
      localStorage.setItem('token', res.data.access_token)
      nav('/')
    }catch(err){ alert('Register failed') }
  }
  return (
    <Box sx={{maxWidth:480,mt:4}}>
      <Typography variant="h5" gutterBottom>Register</Typography>
      <form onSubmit={submit}>
        <TextField label="Email" fullWidth value={email} onChange={e=>setEmail(e.target.value)} sx={{mb:2}} />
        <TextField label="Password" fullWidth type="password" value={password} onChange={e=>setPassword(e.target.value)} sx={{mb:2}} />
        <Button type="submit" variant="contained">Register</Button>
      </form>
    </Box>
  )
}
