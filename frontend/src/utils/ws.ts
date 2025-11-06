export function createWS(onMessage:(data:any)=>void){
  const base = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
  const ws = new WebSocket(base + '/ws')
  ws.onopen = ()=> console.log('ws open')
  ws.onmessage = (e)=> {
    try { onMessage(JSON.parse(e.data)) } catch(err){ console.error(err) }
  }
  ws.onclose = ()=> setTimeout(()=>createWS(onMessage), 2000)
  return ws
}
