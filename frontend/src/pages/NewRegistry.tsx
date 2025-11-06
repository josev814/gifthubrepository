import React, { useState } from 'react'
import { Box, TextField, Button, Typography, FormControlLabel, Switch } from '@mui/material'
import api from '../utils/api'
import { useNavigate } from 'react-router-dom'

export default function NewRegistry(){
  const [name,setName]=useState(''); const [occasion,setOccasion]=useState('Birthday'); const [isPublic,setIsPublic]=useState(true)
  const nav = useNavigate()
  async function submit(e:any){
    e.preventDefault()
    try{
      const res = await api.post('/api/registries/', { name, occasion, is_public: isPublic })
      nav('/registries/'+res.data.share_id)
    }catch(err){ alert('Create failed') }
  }
  return (
    <Box sx={{maxWidth:600}}>
      <Typography variant="h5">Create Registry</Typography>
      <form onSubmit={submit}>
        <TextField label="Name" fullWidth value={name} onChange={e=>setName(e.target.value)} sx={{mb:2}} />
        <TextField label="Occasion" fullWidth value={occasion} onChange={e=>setOccasion(e.target.value)} sx={{mb:2}} />
        <FormControlLabel control={<Switch checked={isPublic} onChange={e=>setIsPublic(e.target.checked)} />} label="Public" />
        <Box sx={{mt:2}}><Button type="submit" variant="contained">Create</Button></Box>
      </form>
    </Box>
  )
}
