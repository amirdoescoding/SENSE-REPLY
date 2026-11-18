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

// active / fail: node id or null. Decision and energy packets go in <g id="packets"> later.
export default function Pipeline({ active, fail }) {
  return (
    <section className="card pipeline">
      <svg viewBox="0 0 1400 190" role="img" aria-label="Decision pipeline: inputs, agent, validator and gate, rule, clamp, site, memory">
        <defs>
          <marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M1 1l6 3-6 3" fill="none" stroke="context-stroke" strokeWidth="1.2" />
          </marker>
        </defs>
        <path d={`M${X(6)} ${Y - 34} C ${X(6) - 80} 14, ${X(1) + 80} 14, ${X(1)} ${Y - 34}`} className="arc" markerEnd="url(#arr)" />
        <text x={(X(1) + X(6)) / 2} y="26" textAnchor="middle" className="arc-label">Every evening: 3–5 most similar good days go back to the agent</text>
        {NODES.slice(1).map(([id], i) => (
          <line key={id} x1={X(i) + 34} x2={X(i + 1) - 34} y1={Y} y2={Y} markerEnd="url(#arr)"
            className={'link' + (fail === 'validator' && i === 2 ? ' fail-dash' : '')} stroke={i < 2 ? 'var(--agent)' : 'var(--line)'} />
        ))}
        {NODES.map(([id, label, d], i) => (
          <g key={id}>
            <rect x={X(i) - 28} y={Y - 28} width="56" height="56" rx="14"
              className={'node' + (active === id ? ' active' : '') + (fail === id ? ' fail' : '')} />
            <path d={d} transform={`translate(${X(i) - 12} ${Y - 12})`} className="icon" />
            <text x={X(i)} y={Y + 58} textAnchor="middle" className={'node-label' + (active === id ? ' on' : '')}>{label}</text>
          </g>
        ))}
        <g id="packets" />
      </svg>
    </section>
  )
}
