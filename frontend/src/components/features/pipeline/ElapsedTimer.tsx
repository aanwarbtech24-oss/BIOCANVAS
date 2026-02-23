import { useState, useEffect } from 'react'

/** Live ticking elapsed timer — shows "Xs" or "Xm Ys". */
export function ElapsedTimer({ startTs, running }: { startTs: number; running: boolean }) {
  const [now, setNow] = useState(Date.now() / 1000)

  useEffect(() => {
    if (!running) return
    const id = setInterval(() => setNow(Date.now() / 1000), 1000)
    return () => clearInterval(id)
  }, [running])

  const elapsed = Math.max(0, Math.floor(now - startTs))
  const mins = Math.floor(elapsed / 60)
  const secs = elapsed % 60

  return (
    <span className="tabular-nums">
      {mins > 0 ? `${mins}m ${secs}s` : `${secs}s`}
    </span>
  )
}
