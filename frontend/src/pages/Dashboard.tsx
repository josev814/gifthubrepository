import React, { useEffect, useState } from 'react'
import { Box, Typography, Grid, Card, CardContent, Button } from '@mui/material'
import api from '../utils/api'
import { Link } from 'react-router-dom'

export default function Dashboard(){
  const [registries, setRegistries] = useState<any[]>([])
  useEffect(()=>{ api.get('/api/registries/').then(r=>setRegistries(r.data)).catch(()=>setRegistries([])) },[])
  return (
    <Box>
      <Box sx={{display:'flex',justifyContent:'space-between',alignItems:'center',mb:3}}>
        <Typography variant="h5">Your Registries</Typography>
        <Button component={Link} to="/registries/new" variant="contained">Create Registry</Button>
      </Box>
      <Grid container spacing={2}>
        {registries.length === 0 ? <Typography>No registries yet.</Typography> : registries.map(r=>(
          <Grid item xs={12} md={6} key={r.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{r.name}</Typography>
                <Typography color="text.secondary">{r.occasion}</Typography>
                <Button component={Link} to={'/registries/'+r.share_id} sx={{mt:1}}>Open</Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}
