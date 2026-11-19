import { useEffect, useMemo, useState } from 'react'
import AgentPanel from './AgentPanel.jsx'
import Kpis from './Kpis.jsx'
import Pipeline from './Pipeline.jsx'
import Site from './Site.jsx'
import useLive from './useLive.js'
import usePlayback from './usePlayback.js'
import { DAY_STEPS, LAMS, MAX_STEP, MODES, num, sgn, sunSeries, timeLabel, weekday } from './lib.js'

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
const key = (mode, lam) => `${mode}_${lam}`

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

function Header({ tab, live }) {
  return (
    <header className="header">
      <img src="/logo.avif" alt="Sense Reply" height="36" />
      <nav>
        {[['sim', 'Simulation'], ['kpis', 'KPIs']].map(([id, label]) => (
          <a key={id} href={'#' + id} className={tab === id ? 'on' : ''} aria-current={tab === id ? 'page' : undefined}>{label}</a>
        ))}
      </nav>
      <div className="meta-list muted">
        <span>{live ? 'Live agent run' : 'Replay'} 5–12 Jan 2026 on run C's sun, load and prices, start SoC 80 %</span>
        <span>Gemini Flash, stand-in for Devstral 2</span>
        <span>Site: Italy (assumed) · CO2 0.356 kg/kWh</span>
      </div>
    </header>
  )
}

function KpiStrip({ kpis, mode, lam, live }) {
  const ours = live?.kpis || kpis.columns[`Ours ${mode} λ=${lam.toFixed(1)}`]
  const pilot = kpis.columns.C
  const note = !live ? '' : live.kpis ? ' · live run' : ' · precomputed, the live week is still running'
  return (
    <section className="card" aria-labelledby="kpis-h">
      <h2 id="kpis-h" className="kpis-h">Week result, ours vs pilot C on the same inputs{note && <span className="muted">{note}</span>}</h2>
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

function PlaybackBar({ pb, run, day, mode, lam, setMode, setLam, live, onLive }) {
  const busy = live?.status === 'running'
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
          const bad = !d.pending && (!d.gate.passed || d.used !== 'plan')
          return (
            <button key={d.start} className={'chip' + (i === day ? ' cur' : '') + (d.pending ? ' pending' : '')} onClick={() => pb.seek(i * DAY_STEPS)} disabled={d.pending}
              aria-label={`${weekday(d.start)}${bad ? ', blocked by the replay gate' : ''}`}
              title={`Plan decided ${weekday(d.start)} 11:00, runs to the next day 10:45${bad ? ', blocked by the replay gate' : ''}`}>
              <i className={'dot' + (bad ? ' blocked' : '')} />{weekday(d.start)}
            </button>
          )
        })}
      </div>
      <div className="seg" role="group" aria-label="Mode">
        {MODES.map((m) => (
          <button key={m} className={mode === m ? 'on' : ''} onClick={() => setMode(m)} disabled={busy}>
            {m === 'conservative' ? 'Conservative' : 'Upside, shadow'}
          </button>
        ))}
      </div>
      <label className="lam">
        <span className="muted">λ €/kg</span>
        <span className="slider">
          <input type="range" min="0" max="2" step="1" value={LAMS.indexOf(lam)} onChange={(e) => setLam(LAMS[e.target.value])} disabled={busy} />
          <span className="ticks mono muted"><span>0</span><span>0.10</span><span>0.50</span></span>
        </span>
      </label>
      <div className="live">
        <button className="btn" onClick={onLive}>{!live ? 'Run the agent live' : busy ? 'Stop' : 'Back to replay'}</button>
        <span className="small muted" role="status">
          {!live ? 'Gemini plans each day now' : busy ? `Live · plan ${live.days.length + 1} of 7`
            : live.status === 'done' ? `Live week done · ${live.tokens.calls}/7 plans from Gemini` : live.error}
        </span>
      </div>
    </section>
  )
}

function Sim({ data, run, live, liveCtl, mode, lam, setMode, setLam }) {
  const reduced = useReducedMotion()
  const stepParam = q.get('step')
  const running = live?.status === 'running'
  const frontier = live && live.status !== 'done' ? Math.max(0, live.days.length * DAY_STEPS - 1) : MAX_STEP // playback waits for the live run
  // autoplay only without reduced motion, and without a step param unless ?play=1
  const pb = usePlayback(Math.min(MAX_STEP, Math.max(0, Math.floor(+stepParam) || 0)), !reduced && (q.get('play') === '1' || stepParam === null), frontier)
  const waiting = running && pb.step >= frontier
  const [, tick] = useState(0)
  useEffect(() => { // the live status line counts seconds while the agent works
    if (!waiting) return
    const id = setInterval(() => tick((n) => n + 1), 1000)
    return () => clearInterval(id)
  }, [waiting])
  const st = live?.stage
  const status = waiting && (/retry/.test(st.msg) ? st.msg : `${st.msg} · ${Math.round((Date.now() - st.t) / 1000)} s`)
  const onLive = () => {
    if (live) return liveCtl.stop()
    liveCtl.start(mode, lam, key(mode, lam))
    pb.seek(0)
    if (!pb.playing) pb.toggle()
  }
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

  const blocked = !d.pending && !d.gate.passed
  return (
    <main className="sim">
      <KpiStrip kpis={data.kpis} mode={mode} lam={lam} live={live} />
      <Site row={run.schedule[pb.step]} step={pb.step} sun={sun[pb.step]} reducedMotion={reduced} />
      <Pipeline active={waiting ? st.stage : reduced && pb.step % DAY_STEPS < 3 ? 'agent' : null} status={status} fail={blocked ? 'validator' : null}
        step={pb.step} epoch={pb.seeks + key(mode, lam)} playing={pb.playing} speed={pb.speed} reduced={reduced} />
      <PlaybackBar pb={pb} run={run} day={day} mode={mode} lam={lam} setMode={setMode} setLam={setLam} live={live} onLive={onLive} />
      <AgentPanel run={run} compare={data.compare} day={day} step={pb.step} mode={mode} lam={lam} />
    </main>
  )
}

export default function App() {
  const [tab, setTab] = useState(hashTab())
  const [data, setData] = useState(null)
  const [err, setErr] = useState(null)
  const [mode, setMode] = useState(MODES.includes(q.get('mode')) ? q.get('mode') : 'conservative')
  const [lam, setLam] = useState(LAMS.includes(+q.get('lambda')) && q.get('lambda') ? +q.get('lambda') : 0.1)
  const liveCtl = useLive()
  const { live } = liveCtl
  const k = key(mode, lam)
  const base = data?.runs[k]
  // a live run overlays its finished days and steps on the precomputed run (same sun, load and prices)
  const run = useMemo(() => !base || live?.key !== k ? base : {
    ...base,
    days: base.days.map((d, i) => live.days[i] || { ...d, pending: true }),
    schedule: base.schedule.map((r, i) => live.rows[i] || r),
  }, [base, live, k])
  const mine = live?.key === k ? live : null
  const pick = (set) => (v) => { if (live?.status !== 'running') { liveCtl.stop(); set(v) } }

  useEffect(() => {
    const f = () => setTab(hashTab())
    addEventListener('hashchange', f)
    return () => removeEventListener('hashchange', f)
  }, [])

  useEffect(() => {
    const get = (u) => fetch(u).then((r) => (r.ok ? r.json() : Promise.reject(new Error(u + ' ' + r.status))))
    const keys = MODES.flatMap((m) => LAMS.map((l) => [m, l]))
    Promise.all([get('/api/kpis'), get('/api/compare'), ...keys.map(([m, l]) => get(`/api/run?mode=${m}&lambda=${l.toFixed(1)}`))])
      .then(([kpis, compare, ...runs]) => setData({ kpis, compare, runs: Object.fromEntries(keys.map(([m, l], i) => [key(m, l), runs[i]])) }))
      .catch(setErr)
  }, [])

  return (
    <>
      <Header tab={tab} live={!!mine} />
      {err ? <p className="status">Could not load the replay data: {err.message}</p>
        : !data ? <p className="status muted">Loading the replay</p>
        : <>
          {tab === 'kpis' && <Kpis kpis={data.kpis} run={mine?.status === 'done' ? run : base} mode={mode} lam={lam} />}
          <div hidden={tab === 'kpis'}><Sim data={data} run={run} live={mine} liveCtl={liveCtl} mode={mode} lam={lam} setMode={pick(setMode)} setLam={pick(setLam)} /></div>{/* kept mounted: the replay keeps its place across tabs */}
        </>}
    </>
  )
}
