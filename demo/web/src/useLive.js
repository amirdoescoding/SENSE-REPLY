import { useRef, useState } from 'react'

// One live agent week from /api/live (server-sent events read with fetch, so 409/429 messages reach the UI).
// live = null | { key, status: running|done|error, days, rows, stage {day, stage, msg, t}, kpis, tokens, error }
export default function useLive() {
  const [live, setLive] = useState(null)
  const ctl = useRef(null)
  const on = (ev, d) => setLive((l) => {
    if (ev === 'stage') return { ...l, stage: { ...d, t: Date.now() } }
    if (ev === 'day') return { ...l, days: [...l.days, d.day], rows: [...l.rows, ...d.schedule] }
    if (ev === 'done') return { ...l, status: 'done', kpis: d.kpis, tokens: d.tokens }
    if (ev === 'error') return { ...l, status: 'error', error: `server error (${d.msg})` }
    return l
  })
  const start = async (mode, lam, key) => {
    ctl.current?.abort()
    const c = (ctl.current = new AbortController())
    setLive({ key, status: 'running', days: [], rows: [], stage: { day: 0, stage: 'agent', msg: 'connecting', t: Date.now() } })
    try {
      const r = await fetch(`/api/live?mode=${mode}&lambda=${lam.toFixed(1)}`, { signal: c.signal })
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `server said ${r.status}`)
      const rd = r.body.pipeThrough(new TextDecoderStream()).getReader()
      let buf = ''
      for (;;) {
        const { value, done } = await rd.read()
        if (done) break
        buf += value
        for (let i; (i = buf.indexOf('\n\n')) >= 0; buf = buf.slice(i + 2)) {
          const block = buf.slice(0, i)
          const ev = /^event: (.*)$/m.exec(block)?.[1]
          if (ev) on(ev, JSON.parse(/^data: (.*)$/m.exec(block)[1]))
        }
      }
      setLive((l) => (l.status === 'running' ? { ...l, status: 'error', error: 'the stream closed early' } : l))
    } catch (e) {
      if (e.name !== 'AbortError') setLive((l) => ({ ...l, status: 'error', error: e.name === 'TypeError' ? 'connection lost' : e.message }))
    }
  }
  const stop = () => { ctl.current?.abort(); setLive(null) }
  return { live, start, stop }
}
