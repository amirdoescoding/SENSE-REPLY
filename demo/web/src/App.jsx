import { useEffect, useMemo, useState } from 'react'
import AgentPanel from './AgentPanel.jsx'
import Kpis from './Kpis.jsx'
import Pipeline from './Pipeline.jsx'
import Site from './Site.jsx'
import usePlayback from './usePlayback.js'
import { DAY_STEPS, LAMS, MAX_STEP, gateReason, num, sgn, sunSeries, timeLabel, weekday } from './lib.js'

const KPIS = [
  ['N1', 'net value after AI', '€/wk', (v) => sgn(v)],
  ['VORB', 'value over free rule', '€/wk', (v) => sgn(v)],
  ['VCR', 'share of best saving', '', (v) => num(v)],
  ['S1', 'grid CO2', 'kg/wk', (v) => num(v, 1)],
  ['O1', 'LLM calls per decision', '', (v) => num(v)],
  ['O5', 'AI cost', '€/wk', (v) => num(v)],
]
const VERDICT = { Good: ['good', '✓ Good'], Improvable: ['imp', '↑ Improvable'] }

const q = new URLSearchParams(location.search)
const hashTab = () => (location.hash === '#kpis' ? 'kpis' : 'sim')

function useReducedMotion() {
  const [r, setR] = useState(() => matchMedia('(prefers-reduced-motion: reduce)').matches)
  useEffect(() => {
    const m = matchMedia('(prefers-reduced-motion: reduce)')
    const f = () => setR(m.matches)
    m.addEventListener('change', f)
    return () => m.removeEventListener('change', f)
  }, [])
  return r
}

function Header({ tab }) {
  return (
    <header className="header">
      <img src="/logo.avif" alt="Sense Reply" height="36" />
      <nav>
        {[['sim', 'Simulation'], ['kpis', 'KPIs']].map(([id, label]) => (
          <a key={id} href={'#' + id} className={tab === id ? 'on' : ''} aria-current={tab === id ? 'page' : undefined}>{label}</a>
        ))}
      </nav>
      <div className="meta-list muted">
        <span>Replay 5–12 Jan 2026 on run C's sun, load and prices, start SoC 80 %</span>
        <span>Ministral 3 8B, self-hosted (Q3 on a laptop)</span>
        <span>Site: Italy (assumed) · CO2 0.356 kg/kWh</span>
      </div>
    </header>
  )
}

function KpiStrip({ kpis, lam }) {
  const ours = kpis.columns[`New framework λ=${lam.toFixed(1)}`]
  const pilot = kpis.columns.C
  return (
    <section className="card" aria-labelledby="kpis-h">
      <h2 id="kpis-h" className="kpis-h">Week result, new framework vs pilot C on the same inputs</h2>
      <div className="kpis">
      {KPIS.map(([id, name, unit, f]) => {
        const [cls, text] = VERDICT[ours[id].verdict] || ['', ours[id].verdict]
        return (
          <div className="kpi" key={id}>
            <div className="muted">{id} · {name}</div>
            <div className="kpi-v">
              <span className="mono big">{f(ours[id].value)}</span>
              {unit && <span className="mono muted">{unit}</span>}
            </div>
            <div className="kpi-foot">
              <span className="mono vs" title={`Pilot C: ${f(pilot[id].value).replace(/^\+/, '')}`}>{sgn(ours[id].value - pilot[id].value, id === 'S1' ? 1 : 2)} vs C</span>
              <span className={'tag ' + cls}>{text}</span>
            </div>
          </div>
        )
      })}
      </div>
    </section>
  )
}

function PlaybackBar({ pb, run, day, lam, setLam }) {
  return (
    <section className="card bar">
      <button className="play" onClick={pb.toggle} aria-label={pb.playing ? 'Pause' : 'Play'}>
        {pb.playing ? <svg width="18" height="18"><path d="M4 2h3.5v14H4zM10.5 2H14v14h-3.5z" fill="#fff" /></svg>
          : <svg width="18" height="18"><path d="M4 2l11 7-11 7z" fill="#fff" /></svg>}
      </button>
      <span className="mono time">{timeLabel(run.schedule[pb.step].t)}</span>
      <div className="group" role="group" aria-label="Speed">
        {[1, 4, 16].map((s) => (
          <button key={s} className={'chip' + (pb.speed === s ? ' solid' : '')} onClick={() => pb.setSpeed(s)}>{s}×</button>
        ))}
      </div>
      <div className="group" role="group" aria-label="Plan day">
        <span className="muted small plan-label">Plan</span>
        {run.days.map((d, i) => {
          const bad = !d.gate.passed || d.used !== 'plan'
          return (
            <button key={d.start} className={'chip' + (i === day ? ' cur' : '')} onClick={() => pb.seek(i * DAY_STEPS)}
              aria-label={`${weekday(d.start)}${bad ? ', blocked by the replay gate' : ''}`}
              title={`Plan decided ${weekday(d.start)} 11:00, runs to the next day 10:45${bad ? ', blocked by the replay gate' : ''}`}>
              <i className={'dot' + (bad ? ' blocked' : '')} />{weekday(d.start)}
            </button>
          )
        })}
      </div>
      <label className="lam">
        <span className="muted">λ €/kg</span>
        <span className="slider">
          <input type="range" min="0" max="2" step="1" value={LAMS.indexOf(lam)} onChange={(e) => setLam(LAMS[e.target.value])} />
          <span className="ticks mono muted"><span>0</span><span>0.10</span><span>0.50</span></span>
        </span>
      </label>
    </section>
  )
}

function Sim({ data, run, lam, setLam }) {
  const reduced = useReducedMotion()
  const stepParam = q.get('step')
  // autoplay only without reduced motion, and without a step param unless ?play=1
  const pb = usePlayback(Math.min(MAX_STEP, Math.max(0, Math.floor(+stepParam) || 0)), !reduced && (q.get('play') === '1' || stepParam === null))
  const sun = useMemo(() => sunSeries(run.schedule), [run])
  const day = Math.floor(pb.step / DAY_STEPS)
  const d = run.days[day]

  useEffect(() => {
    const onKey = (e) => {
      if (hashTab() === 'kpis') return // hidden replay: let Space scroll the KPI page
      if (e.target.closest('input, textarea, select, summary')) return
      if (e.code === 'Space' && e.target.matches('button:focus-visible, a:focus-visible')) return // keyboard focus keeps native Space; mouse-left focus still toggles
      if (e.code === 'Space') { e.preventDefault(); if (!e.repeat) pb.toggle() }
      else if (e.key === 'ArrowLeft') pb.seek(pb.step - 1)
      else if (e.key === 'ArrowRight') pb.seek(pb.step + 1)
    }
    const noClick = (e) => { if (hashTab() !== 'kpis' && e.code === 'Space' && !e.target.matches('input, textarea, select, summary, :focus-visible')) e.preventDefault() } // else a mouse-focused button clicks on keyup
    addEventListener('keydown', onKey)
    addEventListener('keyup', noClick)
    return () => { removeEventListener('keydown', onKey); removeEventListener('keyup', noClick) }
  })

  const blocked = !d.gate.passed
  return (
    <main className="sim">
      <KpiStrip kpis={data.kpis} lam={lam} />
      <Site row={run.schedule[pb.step]} step={pb.step} sun={sun[pb.step]} reducedMotion={reduced} />
      <Pipeline active={reduced && pb.step % DAY_STEPS < 3 ? 'agent' : null} fail={blocked ? 'validator' : null} status={blocked ? 'blocked' : null} reason={blocked ? gateReason(d, lam) : null}
        step={pb.step} epoch={pb.seeks + '_' + lam} playing={pb.playing} speed={pb.speed} reduced={reduced} />
      <PlaybackBar pb={pb} run={run} day={day} lam={lam} setLam={setLam} />
      <AgentPanel run={run} compare={data.compare} day={day} step={pb.step} lam={lam} />
    </main>
  )
}

export default function App() {
  const [tab, setTab] = useState(hashTab())
  const [data, setData] = useState(null)
  const [err, setErr] = useState(null)
  const [lam, setLam] = useState(LAMS.includes(+q.get('lambda')) && q.get('lambda') ? +q.get('lambda') : 0.1)
  const run = data?.runs[lam]

  useEffect(() => {
    const f = () => setTab(hashTab())
    addEventListener('hashchange', f)
    return () => removeEventListener('hashchange', f)
  }, [])

  useEffect(() => {
    const get = (u) => fetch(u).then((r) => (r.ok ? r.json() : Promise.reject(new Error(u + ' ' + r.status))))
    Promise.all([get('/api/kpis'), get('/api/compare'), ...LAMS.map((l) => get(`/api/run?lambda=${l.toFixed(1)}`))])
      .then(([kpis, compare, ...runs]) => setData({ kpis, compare, runs: Object.fromEntries(LAMS.map((l, i) => [l, runs[i]])) }))
      .catch(setErr)
  }, [])

  return (
    <>
      <Header tab={tab} />
      {err ? <p className="status">Could not load the replay data: {err.message}</p>
        : !data ? <p className="status muted">Loading the replay</p>
        : <>
          {tab === 'kpis' && <Kpis kpis={data.kpis} run={run} lam={lam} />}
          <div hidden={tab === 'kpis'}><Sim data={data} run={run} lam={lam} setLam={setLam} /></div>{/* kept mounted: the replay keeps its place across tabs */}
        </>}
    </>
  )
}
