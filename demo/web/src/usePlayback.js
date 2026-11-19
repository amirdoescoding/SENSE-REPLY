import { useEffect, useRef, useState } from 'react'
import { MAX_STEP } from './lib.js'

// 1 simulated day (96 steps) takes about 20 s at 1x, so 4.8 steps per second per speed unit.
// cap: last step that exists (a live run still computing); playback waits there.
export default function usePlayback(initialStep, autoplay, cap = MAX_STEP) {
  const [step, setStep] = useState(initialStep)
  const [speed, setSpeed] = useState(4)
  const [playing, setPlaying] = useState(autoplay)
  const [seeks, setSeeks] = useState(0)
  const acc = useRef(initialStep) // fractional step
  const capRef = useRef(cap)
  capRef.current = cap

  useEffect(() => {
    if (!playing) return
    let last = performance.now()
    let id
    const tick = (now) => {
      acc.current = Math.min(capRef.current, acc.current + Math.max(0, Math.min(0.1, (now - last) / 1000)) * 4.8 * speed) // clamp: no jump after a hidden tab; rAF `now` can precede `last` (step -1 crashed the page)
      last = now
      const s = Math.floor(acc.current)
      setStep(s)
      if (s >= MAX_STEP) return setPlaying(false)
      id = requestAnimationFrame(tick)
    }
    id = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(id)
  }, [playing, speed])

  const seek = (n) => {
    acc.current = Math.max(0, Math.min(capRef.current, Math.floor(n)))
    setStep(acc.current)
    setSeeks((n) => n + 1)
  }
  const toggle = () => {
    if (!playing && step >= MAX_STEP) seek(0)
    setPlaying(!playing)
  }
  return { step, seeks, speed, playing, setSpeed, toggle, seek }
}
