import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Box, Grid, Typography } from '@mui/material'
import api from '../utils/api'
import GiftCard from '../components/GiftCard'
import { createWS } from '../utils/ws'

export default function RegistryView(){
  const { shareId } = useParams()
  const [registry, setRegistry] = useState<any>(null)
  const load = async ()=>{
    const id = shareId || 'public'
    try{
      const res = await api.get('/api/registries/'+id)
      setRegistry(res.data)
    }catch(err){ setRegistry(null) }
  }
  useEffect(()=>{ load()
    const ws = createWS((msg)=>{ if(msg.type==='reservation') load() })
    return ()=> ws.close()
  },[])
  if(!registry) return <Typography>Loading...</Typography>
  return (
    <Box>
      <Typography variant="h5" gutterBottom>{registry.name} — {registry.occasion}</Typography>
      <Grid container spacing={2}>
        {registry.items.map((it:any)=>(
          <Grid item xs={12} sm={6} md={4} key={it.id}>
            <GiftCard gift={it} onUpdate={load} />
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}
