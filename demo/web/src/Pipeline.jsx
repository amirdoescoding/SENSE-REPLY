import { useEffect, useRef, useState } from 'react'
import { DAY_STEPS, MAX_STEP } from './lib.js'

const NODES = [
  ['inputs', 'Inputs', 'M6 8h12M6 12h12M6 16h8'],
  ['agent', 'Agent, 1×/day', 'M5 6h14v10h-7l-4 3v-3H5zM8.5 9.5h7M8.5 12.5h4'],
  ['validator', 'Validator + gate', 'M6 12.5l4 4 8-9'],
  ['rule', 'Rule, every 15 min', 'M6 8h12M6 12h12M6 16h12M10 6v4M15 10v4M9 14v4'],
  ['clamp', 'Clamp 10–90 %, 5 kW', 'M6 5h12M6 19h12M12 8.5v7M9.5 11l2.5-2.5 2.5 2.5M9.5 13l2.5 2.5 2.5-2.5'],
  ['site', 'Site', 'M5 12l7-6 7 6M7 11v7h10v-7'],
  ['memory', 'Memory', 'M7 5h10v14H7zM10 9h4M10 13h4'],
]
const X = (i) => 70 + i * 203
const Y = 96
const EVENING = 36 // plan offset of 20:00 (plans start 11:00): the memory packet lands well before the next decision, even at 16×
const EASE ='cubic-bezier(.77,0,.175,1)'
const ARC = `M${X(6)} ${Y - 38} C ${X(6) - 80} 14, ${X(1) + 80} 14, ${X(1)} ${Y - 38}` // clears a node enlarged to 1.18×

// active / fail: node id or null (active = held cue, e.g. a live server stage; status = one line under it). epoch changes on every seek or run switch: in-flight packets are dropped then.
// Packets and node pulses are Web Animations kept in `live`, so they can be paused and cancelled together.
export default function Pipeline({ active, fail, status, step, epoch, playing, speed, reduced }) {
  const live = useRef(new Set())
  const prev = useRef({ step, epoch })
  const resumed = useRef(false)
  const layer = useRef(null)
  const ov = useRef({})
  const nd = useRef({})
  const lb = useRef({})
  const svg = useRef(null)
  const busy = useRef(0) // packets in flight: the executor loop rests so one stage reads as 'now'
  // one mono line under a stage: the live status, else why a blocked day runs the previous plan
  const line = status && active ? [active, status] : fail === 'validator' && !active ? ['validator', 'blocked, previous plan used'] : null
  const [k, setK] = useState(1) // viewBox units per px when the card is narrower than 1400: keeps labels at their real px size

  useEffect(() => {
    const ro = new ResizeObserver(([e]) => { if (e.contentRect.width) setK(Math.min(1.7, Math.max(1, 1400 / e.contentRect.width))) }) // width 0 while the tab is hidden
    ro.observe(svg.current)
    return () => ro.disconnect()
  }, [])

  const go = (el, keys, opts) => {
    const a = el.animate(keys, opts)
    live.current.add(a)
    const packet = el.tagName === 'circle'
    if (packet) busy.current++
    let done = false // cancel() after finish still fires oncancel: count once
    a.onfinish = a.oncancel = () => { if (done) return; done = true; live.current.delete(a); if (packet) { el.remove(); busy.current-- } }
    return a
  }
  const packet = () => {
    const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    c.setAttribute('r', 4.5)
    c.setAttribute('class', 'packet')
    layer.current.append(c)
    return c
  }
  // Enlarge a stage for `hold` ms from `delay`: up 200 ms ease-out, down 160 ms. Same WAAPI set as the packets.
  const cue = (id, delay, hold, bad, tick) => {
    const t = hold + 360, a = 200 / t, b = (200 + hold) / t
    const keys = (off, on) => [{ ...off, easing: 'cubic-bezier(.23,1,.32,1)' }, { ...on, offset: a }, { ...on, offset: b, easing: 'ease-in-out' }, off]
    const on = bad ? { fill: '#FDE7EC', stroke: 'var(--alert)' } : { fill: 'var(--agent-soft)', stroke: 'var(--agent)' }
    for (const a of [go(nd.current[id], keys({ transform: 'scale(1)' }, { transform: 'scale(1.18)' }), { delay, duration: t }),
      go(nd.current[id].firstChild, keys({}, on), { delay, duration: t }),
      go(lb.current[id], keys({ fill: 'var(--ink-2)', fontWeight: 400 }, { fill: 'var(--ink)', fontWeight: 500 }), { delay, duration: t })]) if (tick) a.tick = delay
  }
  // a packet starts: drop executor ticks that have not begun (running ones finish, so nothing snaps back)
  const quiet = () => live.current.forEach((a) => a.tick !== undefined && a.currentTime < a.tick && a.cancel())
  // Inputs > Agent (breathes) > Validator (holds) > Site; a blocked day turns the dot red on the dashed link.
  const decision = (dur, blocked) => {
    quiet()
    const ha = Math.min(600, dur * 0.35), hv = Math.min(450, dur * 0.3), u = (dur - ha - hv) / 5
    const t = [0, u, u + ha, 2 * u + ha, 2 * u + ha + hv, dur], x = [0, 1, 1, 2, 2, 5]
    go(packet(), t.map((v, k) => ({
      offset: v / dur, opacity: 1, transform: `translate(${X(x[k])}px, ${Y}px)`, easing: k % 2 ? 'linear' : EASE,
      ...(blocked && { fill: k < 3 ? 'var(--agent)' : 'var(--alert)' }),
    })), { duration: dur })
    const pulse = { easing: EASE, duration: 0 }
    go(ov.current.agent, [{ opacity: 0 }, { opacity: 1 }, { opacity: 0 }], { ...pulse, delay: u, duration: ha })
    cue('agent', u, Math.max(0, ha + u - 360)) // settles as the validator rises: one stage at a time
    cue('validator', 2 * u + ha, blocked ? hv + 600 : hv, blocked)
    if (blocked) go(ov.current.validator, [{ opacity: 0 }, { opacity: 1, offset: 0.4 }, { opacity: 0 }], { ...pulse, delay: 2 * u + ha, duration: hv })
  }
  const outcome = (dur) => {
    quiet()
    // sample the arc into translate() keyframes (offset-path on SVG children is unreliable across browsers)
    const c = packet(), path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    path.setAttribute('d', ARC)
    layer.current.append(path)
    const len = path.getTotalLength()
    const keys = Array.from({ length: 25 }, (_, i) => {
      const pt = path.getPointAtLength((len * i) / 24)
      return { opacity: 1, transform: `translate(${pt.x}px, ${pt.y}px)` }
    })
    path.remove()
    go(c, keys, { duration: dur, easing: EASE })
    cue('memory', 0, dur * 0.4)
  }

  useEffect(() => {
    const p = prev.current
    prev.current = { step, epoch }
    if (p.epoch !== epoch || step < p.step || resumed.current) {
      resumed.current = false
      return live.current.forEach((a) => a.cancel())
    }
    if (reduced || !playing) return
    const dur = Math.min(1500, 0.6 * (DAY_STEPS / (4.8 * speed)) * 1000) // 1 day = 96 steps at 4.8 steps/s per speed unit
    if (Math.floor(step / DAY_STEPS) > Math.floor(p.step / DAY_STEPS)) decision(dur, fail === 'validator')
    if (Math.floor((step - EVENING) / DAY_STEPS) > Math.floor((p.step - EVENING) / DAY_STEPS)) outcome(dur)
  }, [step, epoch])

  // Executor loop while playing: Rule > Clamp > Site in turn every 1.8 s (fixed: a 15-min step is ~50 ms at 4x)
  useEffect(() => {
    if (!playing || reduced || active) return
    const f = () => { if (!busy.current && !document.hidden) ['rule', 'clamp', 'site'].forEach((n, i) => cue(n, i * 600, 200, false, true)) }
    f()
    const id = setInterval(f, 1800)
    return () => clearInterval(id)
  }, [playing, reduced, active])

  useEffect(() => {
    if (!playing && step >= MAX_STEP) return // the week ended: let the last packet finish
    live.current.forEach((a) => (playing ? a.play() : a.pause()))
  }, [playing])

  useEffect(() => { // nothing queued for a hidden tab
    const f = () => { if (document.hidden) { resumed.current = true; live.current.forEach((a) => a.cancel()) } }
    document.addEventListener('visibilitychange', f)
    return () => document.removeEventListener('visibilitychange', f)
  }, [])

  return (
    <section className="card pipeline">
      <svg ref={svg} viewBox={`0 0 1400 ${line ? Math.round(190 + 22 * k) : 190}`} style={{ '--k': k }} className={reduced ? 'held' : undefined} role="img" aria-label="Decision pipeline: inputs, agent, validator and gate, rule, clamp, site, memory">
        <defs>
          <marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M1 1l6 3-6 3" fill="none" stroke="context-stroke" strokeWidth="1.2" />
          </marker>
        </defs>
        <path d={ARC} className="arc" markerEnd="url(#arr)" />
        <text x={(X(1) + X(6)) / 2} y="26" textAnchor="middle" className="arc-label">Every evening: the 3 most similar past days go back to the agent (live: this run's days join them)</text>
        {NODES.slice(1).map(([id], i) => (
          <line key={id} x1={X(i) + 34} x2={X(i + 1) - 34} y1={Y} y2={Y} markerEnd="url(#arr)"
            className={'link' + (fail === 'validator' && i === 2 ? ' fail-dash' : '')} stroke={i < 2 ? 'var(--agent)' : 'var(--line)'} />
        ))}
        {!reduced && [3, 4].map((i) => (
          <line key={i} x1={X(i) + 34} x2={X(i + 1) - 34} y1={Y} y2={Y} className="flow"
            style={{ animationDuration: `${1.5 / speed}s`, animationPlayState: playing ? 'running' : 'paused' }} />
        ))}
        {NODES.map(([id, label, d], i) => (
          <g key={id} className={(active === id ? 'on' : active ? 'dim' : '') + (fail === id ? ' fail' : '')} data-id={id}>
            <g ref={(e) => { nd.current[id] = e }} className="nd">{/* scaled as one: rect, overlay, icon; the label stays put */}
              <rect x={X(i) - 28} y={Y - 28} width="56" height="56" rx="14" className="node" />
              {(id === 'agent' || id === 'validator') && (
                <rect ref={(e) => { ov.current[id] = e }} x={X(i) - 28} y={Y - 28} width="56" height="56" rx="14" className={'ov ' + id} />
              )}
              <path d={d} transform={`translate(${X(i) - 12} ${Y - 12})`} className="icon" />
            </g>
            <text ref={(e) => { lb.current[id] = e }} x={X(i)} y={Y + 58} textAnchor="middle" className="node-label">
              {k > 1.2 ? label.split(', ').map((t, j) => <tspan key={j} x={X(i)} dy={j ? '1.2em' : 0}>{t}</tspan>) : label}
            </text>
            {line && line[0] === id && <text x={X(i)} y={Y + 58} dy={k > 1.2 && label.includes(', ') ? '2.6em' : '1.4em'} textAnchor="middle" className="node-status mono">{line[1]}</text>}
          </g>
        ))}
        <g ref={layer} />
      </svg>
    </section>
  )
}
