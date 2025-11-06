import React, { useEffect, useState } from 'react'
import { Card, CardContent, Typography, Button, MenuItem, Select, Box } from '@mui/material'
import api from '../utils/api'
import dayjs from 'dayjs'

export default function GiftCard({gift, onUpdate}:{gift:any, onUpdate:any}){
  const [countdown,setCountdown]=useState('')
  const [reserveFor,setReserveFor]=useState(60)
  useEffect(()=>{
    let t:any
    if (gift.reservation && gift.reservation.expires_at){
      const update = ()=> {
        const diff = dayjs(gift.reservation.expires_at).diff(dayjs())
        if (diff <= 0){ setCountdown('Expired'); onUpdate(); clearInterval(t) }
        else { setCountdown(Math.floor(diff/60000) + 'm ' + Math.floor((diff%60000)/1000)+'s') }
      }
      update(); t=setInterval(update,1000)
    }
    return ()=> clearInterval(t)
  },[gift,onUpdate])

  const reserve = async ()=> {
    try{
      await api.post('/api/reservations/'+gift.id, { duration_minutes: reserveFor })
      onUpdate()
    }catch(e){ alert(e.response?.data?.detail || 'Reserve failed') }
  }
  const confirm = async ()=>{
    try{ await api.post('/api/reservations/'+gift.id+'/confirm'); onUpdate() }catch(e){ alert('Confirm failed') }
  }

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography className="product-title">{gift.title}</Typography>
        <Typography variant="body2" sx={{mb:1}} color="text.secondary">{gift.url}</Typography>
        {gift.bought ? <Typography color="success.main">Already bought</Typography> : gift.reservation ? (
          <Box>
            <Typography>Reserved — {countdown}</Typography>
            <Button variant="contained" sx={{mt:1}} onClick={confirm}>Confirm Purchase</Button>
          </Box>
        ) : (
          <Box sx={{display:'flex',gap:1,alignItems:'center'}}>
            <Select size="small" value={reserveFor} onChange={(e)=>setReserveFor(Number(e.target.value))}>
              <MenuItem value={15}>15 minutes</MenuItem>
              <MenuItem value={60}>1 hour</MenuItem>
              <MenuItem value={1440}>24 hours</MenuItem>
            </Select>
            <Button variant="contained" onClick={reserve}>Reserve</Button>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
