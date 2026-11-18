import { useEffect, useRef, useState } from 'react'
import { DAY_STEPS, MAX_STEP } from './lib.js'

const NODES = [
  ['inputs', 'Inputs', 'M6 8h12M6 12h12M6 16h8'],
  ['agent', 'Agent, 1×/day', 'M12 5l2 4.5 5 .6-3.7 3.4 1 5-4.3-2.5-4.3 2.5 1-5L5 10.1l5-.6z'],
  ['validator', 'Validator + gate', 'M6 12.5l4 4 8-9'],
  ['rule', 'Rule, every 15 min', 'M6 8h12M6 12h12M6 16h12M10 6v4M15 10v4M9 14v4'],
  ['clamp', 'Clamp 10–90 %, 5 kW', 'M8 6v12M16 6v12M8 12h8'],
  ['site', 'Site', 'M5 12l7-6 7 6M7 11v7h10v-7'],
  ['memory', 'Memory', 'M7 5h10v14H7zM10 9h4M10 13h4'],
]
const X = (i) => 70 + i * 203
const Y = 96
const EASE = 'cubic-bezier(.77,0,.175,1)'
const ARC = `M${X(6)} ${Y - 34} C ${X(6) - 80} 14, ${X(1) + 80} 14, ${X(1)} ${Y - 34}`

// active / fail: node id or null. epoch changes on every seek or run switch: in-flight packets are dropped then.
// Packets and node pulses are Web Animations kept in `live`, so they can be paused and cancelled together.
export default function Pipeline({ active, fail, step, epoch, playing, speed, reduced }) {
  const live = useRef(new Set())
  const prev = useRef({ step, epoch })
  const resumed = useRef(false)
  const layer = useRef(null)
  const ov = useRef({})
  const svg = useRef(null)
  const [k, setK] = useState(1) // viewBox units per px when the card is narrower than 1400: keeps labels at their real px size

  useEffect(() => {
    const ro = new ResizeObserver(([e]) => { if (e.contentRect.width) setK(Math.min(1.7, Math.max(1, 1400 / e.contentRect.width))) }) // width 0 while the tab is hidden
    ro.observe(svg.current)
    return () => ro.disconnect()
  }, [])

  const go = (el, keys, opts) => {
    const a = el.animate(keys, opts)
    live.current.add(a)
    a.onfinish = a.oncancel = () => { live.current.delete(a); if (el.tagName === 'circle') el.remove() }
  }
  const packet = () => {
    const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    c.setAttribute('r', 4.5)
    c.setAttribute('class', 'packet')
    layer.current.append(c)
    return c
  }
  // Inputs > Agent (breathes) > Validator (holds) > Site; a blocked day turns the dot red on the dashed link.
  const decision = (dur, blocked) => {
    const ha = Math.min(300, dur * 0.2), hv = Math.min(300, dur * 0.25), u = (dur - ha - hv) / 5
    const t = [0, u, u + ha, 2 * u + ha, 2 * u + ha + hv, dur], x = [0, 1, 1, 2, 2, 5]
    go(packet(), t.map((v, k) => ({
      offset: v / dur, opacity: 1, transform: `translate(${X(x[k])}px, ${Y}px)`, easing: k % 2 ? 'linear' : EASE,
      ...(blocked && { fill: k < 3 ? 'var(--agent)' : 'var(--alert)' }),
    })), { duration: dur })
    const pulse = { easing: EASE, duration: 0 }
    go(ov.current.agent, [{ opacity: 0 }, { opacity: 1 }, { opacity: 0 }], { ...pulse, delay: u, duration: ha })
    if (blocked) go(ov.current.validator, [{ opacity: 0 }, { opacity: 1, offset: 0.4 }, { opacity: 0 }], { ...pulse, delay: 2 * u + ha, duration: hv })
  }
  const outcome = (dur) => {
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
    if (Math.floor((step + 1) / DAY_STEPS) > Math.floor((p.step + 1) / DAY_STEPS)) outcome(dur)
  }, [step, epoch])

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
      <svg ref={svg} viewBox="0 0 1400 190" style={{ '--k': k }} role="img" aria-label="Decision pipeline: inputs, agent, validator and gate, rule, clamp, site, memory">
        <defs>
          <marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M1 1l6 3-6 3" fill="none" stroke="context-stroke" strokeWidth="1.2" />
          </marker>
        </defs>
        <path d={ARC} className="arc" markerEnd="url(#arr)" />
        <text x={(X(1) + X(6)) / 2} y="26" textAnchor="middle" className="arc-label">Every evening: 3–5 most similar good days go back to the agent</text>
        {NODES.slice(1).map(([id], i) => (
          <line key={id} x1={X(i) + 34} x2={X(i + 1) - 34} y1={Y} y2={Y} markerEnd="url(#arr)"
            className={'link' + (fail === 'validator' && i === 2 ? ' fail-dash' : '')} stroke={i < 2 ? 'var(--agent)' : 'var(--line)'} />
        ))}
        {!reduced && [3, 4].map((i) => (
          <line key={i} x1={X(i) + 34} x2={X(i + 1) - 34} y1={Y} y2={Y} className="flow"
            style={{ animationDuration: `${1.5 / speed}s`, animationPlayState: playing ? 'running' : 'paused' }} />
        ))}
        {NODES.map(([id, label, d], i) => (
          <g key={id}>
            <rect x={X(i) - 28} y={Y - 28} width="56" height="56" rx="14"
              className={'node' + (active === id ? ' active' : '') + (fail === id ? ' fail' : '')} />
            {(id === 'agent' || id === 'validator') && (
              <rect ref={(e) => { ov.current[id] = e }} x={X(i) - 28} y={Y - 28} width="56" height="56" rx="14" className={'ov ' + id} />
            )}
            <path d={d} transform={`translate(${X(i) - 12} ${Y - 12})`} className="icon" />
            <text x={X(i)} y={Y + 58} textAnchor="middle" className={'node-label' + (active === id ? ' on' : '')}>
              {k > 1.2 ? label.split(', ').map((t, j) => <tspan key={j} x={X(i)} dy={j ? '1.2em' : 0}>{t}</tspan>) : label}
            </text>
          </g>
        ))}
        <g ref={layer} />
      </svg>
    </section>
  )
}
