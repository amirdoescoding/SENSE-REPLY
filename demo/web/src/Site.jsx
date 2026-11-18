// Fixed contract: <Site row={schedule[step]} step={step} sun={{ alt, isNight, p }} reducedMotion={bool} />
// Card backdrop: CSS sky + discs + stars under a transparent orthographic three.js canvas. The scene is built once;
// props go through a ref and an own rAF loop (step changes ~19x/s). Geometry and lighting ported from docs/mockups/sky.html.
import { useEffect, useRef } from 'react'
import * as T from 'three'
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import { SUN_NOTE, num, timeLabel } from './lib.js'

const sm = (a, b, x) => { x = Math.min(1, Math.max(0, (x - a) / (b - a))); return x * x * (3 - 2 * x) }
const col = (s) => new T.Color(s)
const mix = (o, a, b, k) => o.copy(a).lerp(b, k)

const K = Object.fromEntries(Object.entries({
  nTop: '#1A2432', dTop: '#5B6E92', fTop: '#C9DDF2', nHor: '#2A3A4E', dHor: '#EFAE7C', fHor: '#F4F8FC',
  nAmb: '#A9BBD2', dAmb: '#E4E9F0', white: '#FFFFFF', warm: '#FFC48A', moon: '#9FB4D6', paper: '#F4F8FC',
  gridD: '#D6E0EA', gridN: '#7D8996', trD: '#DCE5EE', trN: '#6D7A88', idD: '#C4D0DC', idN: '#7D8996',
  sun: '#F2A900', store: '#02B843', grid: '#586674', win: '#F6C56B', winOff: '#B9CCDD', ledOff: '#8D99A5',
}).map(([k, v]) => [k, col(v)]))

// deterministic stars, percent positions
const STARS = (() => { let s = 7; const r = () => (s = (s * 16807) % 2147483647) / 2147483647; return Array.from({ length: 90 }, (_, i) => ({ l: r() * 100, t: r() * 54, o: 0.4 + 0.6 * ((i * 7) % 5) / 4 })) })()

// chip anchors: name, 3D point, pixel offset
const CHIPS = [['PV', -4.4, 2.3, 4.0, 0, -2], ['House', 0, 4.3, -1.7, 0, 0], ['Battery', 5.2, 2.4, 2.4, 125, 20], ['Grid', 6.3, 6.3, -3.6, 0, 0]]

function build(canvas) {
  const R = new T.WebGLRenderer({ canvas, antialias: true, alpha: true })
  R.setPixelRatio(Math.min(devicePixelRatio, 2))
  R.shadowMap.enabled = true; R.shadowMap.type = T.PCFShadowMap; R.shadowMap.autoUpdate = false
  const sc = new T.Scene()
  const M = (c) => new T.MeshLambertMaterial({ color: c, flatShading: true })
  const WH = M('#FFFFFF'), GR = M('#E8EDF2'), DK = M('#26364A'), IK = M('#3F4D5A'), PM = M('#586674')
  const add = (g, m, x, y, z, par = sc) => { const o = new T.Mesh(g, m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; par.add(o); return o }
  const bx = (w, h, d, m, x, y, z, par) => add(new T.BoxGeometry(w, h, d), m, x, y, z, par)
  const lines = (v, color, par = sc) => { const o = new T.LineSegments(new T.BufferGeometry().setAttribute('position', new T.Float32BufferAttribute(v, 3)), new T.LineBasicMaterial({ color })); par.add(o); return o }

  // floor
  const slabMat = M('#F4F8FC')
  bx(15, 0.3, 13, slabMat, 0, -0.15, 0)
  const gl = []
  for (let i = -7; i <= 7; i++) gl.push(i, 0.01, -6.5, i, 0.01, 6.5)
  for (let j = -6; j <= 6; j++) gl.push(-7.5, 0.01, j + 0.5, 7.5, 0.01, j + 0.5)
  const gridLines = lines(gl, '#D6E0EA')

  // house
  const gx = 0, gz = -2.2
  bx(4.4, 2.2, 3.2, WH, gx, 1.1, gz)
  const sh = new T.Shape(); sh.moveTo(-2.05, 0); sh.lineTo(2.05, 0); sh.lineTo(0, 1.5); sh.closePath()
  const rg = new T.ExtrudeGeometry(sh, { depth: 4.9, bevelEnabled: true, bevelSize: 0.07, bevelThickness: 0.07, bevelSegments: 1 })
  rg.translate(0, 0, -2.45); rg.rotateY(Math.PI / 2)
  add(rg, GR, gx, 2.2, gz)
  bx(0.5, 1.3, 0.5, GR, gx + 1.2, 3.0, gz - 0.4); bx(0.64, 0.1, 0.64, WH, gx + 1.2, 3.7, gz - 0.4)
  bx(0.9, 1.5, 0.08, IK, gx - 1.2, 0.75, gz + 1.64); bx(0.08, 0.08, 0.04, GR, gx - 0.95, 0.8, gz + 1.7)
  const winMat = new T.MeshLambertMaterial({ color: '#B9CCDD', flatShading: true, emissive: '#F6C56B', emissiveIntensity: 0 })
  bx(1.1, 0.9, 0.1, GR, gx + 1.0, 1.2, gz + 1.62); bx(0.9, 0.7, 0.1, winMat, gx + 1.0, 1.2, gz + 1.64)
  for (const z of [-0.6, 0.7]) { bx(0.1, 0.9, 1.0, GR, gx + 2.2, 1.2, gz + z); bx(0.1, 0.7, 0.8, winMat, gx + 2.22, 1.2, gz + z) }

  // PV 3x3
  const px = -4.4, pz = 4.0
  const cellV = []
  for (let i = 1; i < 6; i++) cellV.push(-0.665 + i * 1.33 / 6, 0.07, -0.49, -0.665 + i * 1.33 / 6, 0.07, 0.49)
  for (let j = 1; j < 4; j++) cellV.push(-0.665, 0.07, -0.49 + j * 0.98 / 4, 0.665, 0.07, -0.49 + j * 0.98 / 4)
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
    const g = new T.Group(); g.position.set(px + (c - 1) * 1.55, 0.95, pz + (r - 1) * 1.25); g.rotation.x = 0.5; sc.add(g)
    bx(1.45, 0.07, 1.1, GR, 0, 0, 0, g); bx(1.33, 0.05, 0.98, DK, 0, 0.04, 0, g); lines(cellV, '#5A7192', g)
  }
  for (let r = 0; r < 3; r++) for (const x of [-2.3, 2.3]) { const z = pz + (r - 1) * 1.25; bx(0.08, 0.9, 0.08, GR, px + x, 0.45, z - 0.3); bx(0.08, 0.5, 0.08, GR, px + x, 0.25, z + 0.4) }
  bx(4.9, 0.06, 0.06, IK, px, 0.75, pz - 1.3)

  // battery cabinet with live SoC bar and LED
  const bxp = 5.2, bzp = 2.4
  bx(1.7, 2.1, 1.2, WH, bxp, 1.05, bzp); bx(1.8, 0.12, 1.3, GR, bxp, 2.16, bzp)
  for (let i = 0; i < 5; i++) bx(0.04, 0.07, 0.9, IK, bxp + 0.86, 0.5 + i * 0.16, bzp)
  bx(0.5, 0.5, 0.04, IK, bxp + 0.3, 1.0, bzp + 0.61); bx(0.22, 1.5, 0.04, IK, bxp - 0.45, 1.1, bzp + 0.61)
  const barG = new T.BoxGeometry(0.14, 1, 0.05); barG.translate(0, 0.5, 0)
  const bar = add(barG, M('#02B843'), bxp - 0.45, 0.4, bzp + 0.62)
  const led = new T.MeshLambertMaterial({ color: '#8D99A5', emissive: '#02B843', emissiveIntensity: 0 })
  bx(0.14, 0.14, 0.05, led, bxp + 0.45, 1.7, bzp + 0.62)

  // pylon: all lattice beams merged into one mesh
  const ox = 6.3, oz = -3.6, beams = []
  const beam = (a, b, t) => {
    const A = new T.Vector3(...a), B = new T.Vector3(...b), o = new T.Object3D()
    o.position.copy(A).add(B).multiplyScalar(0.5); o.lookAt(B); o.updateMatrix()
    beams.push(new T.BoxGeometry(t, t, A.distanceTo(B)).applyMatrix4(o.matrix))
  }
  const P4 = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
  for (const [sx, sz] of P4) beam([ox + sx * 0.7, 0, oz + sz * 0.7], [ox + sx * 0.12, 6, oz + sz * 0.12], 0.07)
  for (let h = 0; h < 6; h++) {
    const a = 0.7 - h * 0.097, b = 0.7 - (h + 1) * 0.097
    for (let i = 0; i < 4; i++) { const [s1, t1] = P4[i], [s2, t2] = P4[(i + 1) % 4]; beam([ox + s1 * a, h, oz + t1 * a], [ox + s2 * b, h + 1, oz + t2 * b], 0.04) }
  }
  for (const y of [4.7, 5.5]) beam([ox - 1.7, y, oz + 1.7], [ox + 1.7, y, oz - 1.7], 0.07)
  const pyl = new T.Mesh(mergeGeometries(beams), PM); pyl.castShadow = true; sc.add(pyl)
  const wireM = new T.LineBasicMaterial({ color: '#586674' })
  for (const y of [4.7, 5.5]) for (const s of [-1.7, 1.7]) {
    const a = new T.Vector3(ox + s, y, oz - s), b = new T.Vector3(ox + s, y - 0.3, oz - s - 40), pts = []
    for (let i = 0; i <= 40; i++) { const u = i / 40, v = a.clone().lerp(b, u); v.y -= Math.sin(Math.PI * u) * 0.9 + u * 0.8; pts.push(v) }
    sc.add(new T.Line(new T.BufferGeometry().setFromPoints(pts), wireM))
  }

  // flow paths on the floor: trench + coloured core + particles (one Points per path)
  const dot = (() => { const c = document.createElement('canvas'); c.width = c.height = 32; const x = c.getContext('2d'); x.fillStyle = '#fff'; x.beginPath(); x.arc(16, 16, 15, 0, 7); x.fill(); return new T.CanvasTexture(c) })()
  const defs = [
    ['pv', K.sun, [[px + 0.5, pz - 1.7], [px + 0.5, 0.2], [-0.8, 0.2], [-0.8, gz + 1.7]]],
    ['pvbat', K.sun, [[px + 2.5, pz + 0.4], [bxp - 0.3, pz + 0.4], [bxp - 0.3, bzp + 0.7]]],
    ['bat', K.store, [[bxp - 0.9, bzp - 0.3], [0.9, bzp - 0.3], [0.9, gz + 1.7]]],
    ['grid', K.grid, [[ox, oz + 0.6], [ox, gz], [gx + 2.4, gz]]],
  ]
  const trenchMat = new T.MeshBasicMaterial()
  const paths = defs.map(([id, c, pts]) => {
    const P = pts.map(([x, z]) => new T.Vector3(x, 0.02, z)), cum = [0]
    const coreMat = new T.MeshBasicMaterial()
    for (let i = 0; i < P.length - 1; i++) {
      const a = P[i], b = P[i + 1], len = a.distanceTo(b); cum.push(cum[i] + len)
      for (const [w, mat, y] of [[0.28, trenchMat, 0.015], [0.07, coreMat, 0.02]]) {
        const m = new T.Mesh(new T.PlaneGeometry(w, len + w), mat)
        m.rotation.x = -Math.PI / 2; m.position.copy(a).add(b).multiplyScalar(0.5); m.position.y = y
        if (Math.abs(b.x - a.x) > Math.abs(b.z - a.z)) m.rotation.z = Math.PI / 2
        sc.add(m)
      }
    }
    const tot = cum[P.length - 1], N = Math.max(6, Math.round(tot * 1.1)), pos = new Float32Array(N * 3)
    const geo = new T.BufferGeometry().setAttribute('position', new T.BufferAttribute(pos, 3)); geo.setDrawRange(0, 0)
    const pts3 = new T.Points(geo, new T.PointsMaterial({ color: c, size: 9, sizeAttenuation: false, map: dot, alphaTest: 0.5, transparent: true, depthTest: false }))
    pts3.frustumCulled = false; sc.add(pts3)
    return { id, c, P, cum, tot, N, pos, geo, pts3, coreMat, phase: 0, fade: 0 }
  })

  // lights
  const amb = new T.AmbientLight(), dl = new T.DirectionalLight()
  dl.castShadow = true; dl.shadow.mapSize.set(1024, 1024)
  Object.assign(dl.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 70 })
  dl.shadow.radius = 3; dl.shadow.bias = -0.0005
  sc.add(amb, dl)

  const cam = new T.OrthographicCamera(-1, 1, 1, -1, 0.1, 200)
  const e = 35.264 * Math.PI / 180
  cam.position.set(Math.cos(e) * Math.sin(Math.PI / 4), Math.sin(e), Math.cos(e) * Math.cos(Math.PI / 4)).multiplyScalar(40)
  cam.lookAt(0, 0.9, 0)

  const v = new T.Vector3()
  function resize(W, H) {
    const ppu = Math.min(W / 30, H / 13)
    R.setSize(W, H, false)
    Object.assign(cam, { left: -W / 2 / ppu, right: W / 2 / ppu, top: H / 2 / ppu, bottom: -H / 2 / ppu })
    cam.setViewOffset(W, H, 0, -0.06 * H, W, H); cam.updateProjectionMatrix(); cam.updateMatrixWorld()
    return CHIPS.map(([, x, y, z, dx, dy]) => { v.set(x, y, z).project(cam); return [(v.x * 0.5 + 0.5) * W + dx, (-v.y * 0.5 + 0.5) * H + dy] })
  }
  const dispose = () => { sc.traverse((o) => { o.geometry?.dispose(); o.material?.dispose?.() }); dot.dispose(); R.dispose(); R.forceContextLoss() }
  return { R, sc, cam, resize, dispose, paths, bar, led, winMat, slabMat, gridLines, trenchMat, amb, dl, gz, bxp }
}

export default function Site({ row, step, sun, reducedMotion }) {
  const card = useRef(), canvas = useRef(), sky = useRef(), sunEl = useRef(), moonEl = useRef(), stars = useRef()
  const chipEls = useRef([]), live = useRef()
  live.current = { row, sun, reducedMotion }

  useEffect(() => {
    const S = build(canvas.current)
    let W = 1, H = 1 // cached by the observer: reading layout in the rAF loop forced a reflow every frame
    const place = () => {
      ({ width: W, height: H } = card.current.getBoundingClientRect())
      S.resize(W, H).forEach(([x, y], i) => { chipEls.current[i].style.left = x + 'px'; chipEls.current[i].style.top = y + 'px' })
    }
    const ro = new ResizeObserver(place); ro.observe(card.current); place()

    // smoothed state: alt (deg, <0 below horizon), p (day fraction), mq (moon fraction), tmp colours reused every frame
    let cur = null, last = performance.now(), raf
    const top = new T.Color(), hor = new T.Color(), c1 = new T.Color(), c2 = new T.Color()
    const dir = new T.Vector3(), lastDir = new T.Vector3(), nDir = new T.Vector3(-0.5, 1, 0.8).normalize()
    const flow = new Float32Array(4)
    const tick = (now) => {
      raf = requestAnimationFrame(tick)
      const dt = Math.min(0.1, (now - last) / 1000); last = now
      if (document.hidden) return
      const { row: r, sun: sn, reducedMotion: rm } = live.current
      const p = sn.isNight ? 1 : sn.p, mq = sn.isNight ? sn.p : 0
      const tAlt = sn.isNight ? -20 : 65 * sn.alt
      if (!cur) cur = { alt: tAlt, p, mq }
      const k = rm ? 1 : 1 - Math.exp(-dt * 6)
      cur.alt += (tAlt - cur.alt) * k
      cur.p = Math.abs(p - cur.p) < 0.2 ? cur.p + (p - cur.p) * k : p
      cur.mq = Math.abs(mq - cur.mq) < 0.2 ? cur.mq + (mq - cur.mq) * k : mq

      // sky
      const kn = sm(-10, 0, cur.alt), kd = sm(0, 30, cur.alt), night = 1 - kn
      mix(top, mix(c1, K.nTop, K.dTop, kn), K.fTop, kd); mix(hor, mix(c2, K.nHor, K.dHor, kn), K.fHor, kd)
      sky.current.style.background = `linear-gradient(${top.getStyle()} 0%,${hor.getStyle()} 75%)`
      const disc = (el, a, altN, op) => { // arc along the top of the card
        el.style.left = (0.06 + 0.88 * a) * W + 'px'; el.style.top = H * (0.1 + 0.2 * (1 - Math.max(0, altN))) + 'px'; el.style.opacity = op
      }
      disc(sunEl.current, cur.p, cur.alt / 65, sm(-8, -2, cur.alt))
      const moonIn = cur.mq >= 0 && cur.mq <= 1
      disc(moonEl.current, cur.mq, Math.sin(Math.PI * Math.min(1, Math.max(0, cur.mq))) * 0.85, moonIn ? sm(0.2, 0.8, night) : 0)
      stars.current.style.opacity = night
      card.current.classList.toggle('dark', night > 0.5 || cur.alt < 8)

      // lights, floor
      const dim = 1 - 0.3 * night
      mix(c1, K.nAmb, K.dAmb, kn); mix(S.amb.color, c1, K.white, kd)
      S.amb.intensity = 1.8 + 0.9 * night * (1 - kd) // ~2.7 at night, 1.8 by day
      const se = Math.max(cur.alt, 14) * Math.PI / 180, th = (-70 + 140 * cur.p + 22) * Math.PI / 180
      const nl = sm(0.3, 0.7, night)
      dir.set(Math.sin(th) * Math.cos(se), Math.sin(se), Math.cos(th) * Math.cos(se)).lerp(nDir, nl).normalize()
      mix(S.dl.color, mix(c2, K.warm, K.white, kd), K.moon, nl)
      S.dl.intensity = (1.9 + 0.4 * kn) * (1 - nl) + 1.0 * nl
      S.dl.position.copy(dir).multiplyScalar(30)
      if (dir.distanceToSquared(lastDir) > 1e-6) { S.R.shadowMap.needsUpdate = true; lastDir.copy(dir) } // shadow pass only when the light moves
      S.slabMat.color.copy(K.paper).multiplyScalar(dim)
      mix(S.gridLines.material.color, K.gridD, K.gridN, night * 0.7)
      mix(S.trenchMat.color, K.trD, K.trN, night * 0.6)

      // devices
      const glow = cur.alt < 12 && r.load_kw > 0
      S.winMat.emissiveIntensity += ((glow ? 1 : 0) - S.winMat.emissiveIntensity) * k
      mix(S.winMat.color, K.winOff, K.win, S.winMat.emissiveIntensity)
      S.bar.scale.y = Math.max(0.001, 1.4 * r.soc); S.bar.position.y = 0.4
      S.led.emissiveIntensity = Math.abs(r.battery_kw) > 0.02 ? 1 : 0
      S.led.color.copy(S.led.emissiveIntensity ? K.store : K.ledOff)

      // flows (kW, signed along the path direction: + = towards the house/battery)
      const pvH = Math.min(r.pv_kw, r.load_kw), pvB = Math.max(0, Math.min(r.battery_kw, r.pv_kw - pvH))
      flow[0] = pvH; flow[1] = pvB; flow[2] = -Math.min(0, r.battery_kw) - Math.max(0, r.battery_kw - pvB); // grid charging (upside) runs house -> battery flow[3] = r.grid_kw
      S.paths.forEach((q, i) => {
        const f = flow[i], on = Math.abs(f) >= 0.02
        q.fade += ((on ? 1 : 0) - q.fade) * (rm ? 1 : Math.min(1, dt / 0.2))
        mix(q.coreMat.color, mix(c1, K.idD, K.idN, night * 0.6), q.c, 0.6 * q.fade) // idle -> path colour
        const show = on && !rm
        q.geo.setDrawRange(0, show ? Math.min(q.N, Math.ceil(q.N * Math.min(1, 0.3 + Math.abs(f) / 4))) : 0)
        if (!show) return
        q.phase = (q.phase + Math.sign(f) * (0.5 + 0.3 * Math.abs(f)) * dt / q.tot * 2 + 1) % 1
        const pos = q.pos
        for (let j = 0; j < q.N; j++) {
          const d = ((q.phase + j / q.N) % 1) * q.tot
          let s = 0
          while (s < q.P.length - 2 && d > q.cum[s + 1]) s++
          const u = (d - q.cum[s]) / (q.cum[s + 1] - q.cum[s]), a = q.P[s], b = q.P[s + 1]
          pos[j * 3] = a.x + (b.x - a.x) * u; pos[j * 3 + 1] = 0.12; pos[j * 3 + 2] = a.z + (b.z - a.z) * u
        }
        q.geo.attributes.position.needsUpdate = true
      })
      S.R.render(S.sc, S.cam)
    }
    raf = requestAnimationFrame(tick)
    return () => { cancelAnimationFrame(raf); ro.disconnect(); S.dispose() }
  }, [])

  const vals = [`${num(row.pv_kw)} kW`, `${num(row.load_kw)} kW`, `SoC ${Math.round(row.soc * 100)} %`, `${num(row.grid_kw)} kW`]
  const dots = ['var(--sun)', 'var(--ink-2)', 'var(--store)', 'var(--grid)']
  return (
    <section ref={card} className="card site">
      <div ref={sky} className="site-sky">
        <div ref={stars}>{STARS.map((s, i) => <i key={i} className="star" style={{ left: s.l + '%', top: s.t + '%', opacity: s.o }} />)}</div>
        <div ref={sunEl} className="disc" title={SUN_NOTE} style={{ background: 'var(--sun)' }} />
        <div ref={moonEl} className="disc" style={{ background: '#F1F3F0' }} />
      </div>
      <canvas ref={canvas} className="site-canvas" />
      {CHIPS.map(([n], i) => (
        <div key={n} ref={(el) => (chipEls.current[i] = el)} className="lab">
          <div className="n">{n}</div>
          <div className="c mono"><i className="dot" style={{ background: dots[i] }} />{vals[i]}</div>
          <div className="l" />
        </div>
      ))}
      <span className="muted">Site, replaying 15-minute steps</span>
      <span className="site-time mono">{timeLabel(row.t)}</span>
      <div className="legend">
        <span><i className="dot" style={{ background: 'var(--sun)' }} />Solar</span>
        <span><i className="dot" style={{ background: 'var(--store)' }} />Battery</span>
        <span><i className="dot" style={{ background: 'var(--grid)' }} />Grid</span>
      </div>
    </section>
  )
}
