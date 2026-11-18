export const MODES = ['conservative', 'upside']
export const LAMS = [0, 0.1, 0.5]
export const MAX_STEP = 671
export const DAY_STEPS = 96
export const SUN_NOTE = "Sun follows the simulator's PV, which peaks at 10:00 (not a real Italian January)"

const WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

// "YYYY-MM-DDTHH:MM:SS" -> parts, no timezone conversion (Date.UTC only for the weekday)
export function parts(t) {
  const [y, m, d] = t.slice(0, 10).split('-').map(Number)
  return { y, m, d, hm: t.slice(11, 16), wd: WD[new Date(Date.UTC(y, m - 1, d)).getUTCDay()] }
}
export const dayLabel = (t) => { const p = parts(t); return `${p.wd} ${p.d} ${MON[p.m - 1]}` }
export const timeLabel = (t) => `${dayLabel(t)} ${parts(t).hm}`
export const weekday = (t) => parts(t).wd
export function nextDayWeekday(t) {
  const p = parts(t)
  return WD[new Date(Date.UTC(p.y, p.m - 1, p.d + 1)).getUTCDay()]
}

export const sgn = (v, n = 2) => (v < 0 ? '−' : '+') + Math.abs(v).toFixed(n)
export const eur = (v, n = 2) => (v < 0 ? '−' : '') + '€' + Math.abs(v).toFixed(n)
export const num = (v, n = 2) => { const s = Math.abs(v).toFixed(n); return (v < 0 && +s ? '−' : '') + s } // no "−0.00"
export const kfmt = (n) => (n >= 1000 ? (n / 1000).toFixed(1) + 'k' : String(n))

// Per step {alt 0..1, isNight, p} from the data: sunrise/sunset = first/last step with pv_kw > 0 on each calendar day.
// The window starts at 11:00 and ends at 10:45, so the partial first/last days borrow the missing edge from the neighbour day.
export function sunSeries(schedule) {
  const mins = (t) => +t.slice(11, 13) * 60 + +t.slice(14, 16)
  const days = {}
  schedule.forEach((r) => {
    if (r.pv_kw <= 0) return
    const d = (days[r.t.slice(0, 10)] ||= { rise: 1e9, set: -1 })
    d.rise = Math.min(d.rise, mins(r.t))
    d.set = Math.max(d.set, mins(r.t))
  })
  const keys = Object.keys(days).sort()
  days[keys[0]].rise = days[keys[1]].rise
  days[keys.at(-1)].set = days[keys.at(-2)].set
  return schedule.map((r) => {
    const d = days[r.t.slice(0, 10)]
    const m = mins(r.t)
    const day = d && m >= d.rise && m <= d.set
    // p: 0..1 through daylight (sun) or through the night set -> next rise (moon); no day entry = mid-night
    const night = d ? 1440 - (d.set - d.rise) : 1
    const p = !d ? 0.5 : day ? (m - d.rise) / (d.set - d.rise) : ((m - d.set + 1440) % 1440) / night
    return { alt: day ? Math.sin(Math.PI * p) : 0, isNight: !day, p }
  })
}
