// Fixed contract: <Site row={schedule[step]} step={step} sun={{ alt, isNight }} reducedMotion={bool} />
// Placeholder: card frame, legend, time and a sky keyed on sun.alt. The 3D scene replaces the readout chips.
import { timeLabel } from './lib.js'

export default function Site({ row, sun }) {
  const top = `color-mix(in srgb, #C9DDF3 ${Math.round(sun.alt * 100)}%, #AEBBCB)`
  return (
    <section className="card site" style={{ background: `linear-gradient(${top}, var(--paper) 70%)` }}>
      <span className="muted">Site, replaying 15-minute steps</span>
      <span className="site-time mono">{timeLabel(row.t)}</span>
      <div className="site-readout mono">
        <span><i className="dot" style={{ background: 'var(--sun)' }} />PV {row.pv_kw.toFixed(2)} kW</span>
        <span><i className="dot" style={{ background: 'var(--ink-2)' }} />House {row.load_kw.toFixed(2)} kW</span>
        <span><i className="dot" style={{ background: 'var(--store)' }} />SoC {(row.soc * 100).toFixed(0)} %</span>
        <span><i className="dot" style={{ background: 'var(--grid)' }} />Grid {row.grid_kw.toFixed(2)} kW</span>
      </div>
      <div className="legend">
        <span><i className="dot" style={{ background: 'var(--sun)' }} />Solar</span>
        <span><i className="dot" style={{ background: 'var(--store)' }} />Battery</span>
        <span><i className="dot" style={{ background: 'var(--grid)' }} />Grid</span>
      </div>
    </section>
  )
}
