import React, { useEffect, useRef } from 'react'
import { Terminal, Brain } from "lucide-react"

const levelStyles = {
  INFO: "bg-teal-500/15 text-teal-400 border border-teal-500/30",
  WARN: "bg-yellow-500/15 text-yellow-400 border border-yellow-500/30",
  AI:   "bg-purple-500/15 text-purple-400 border border-purple-500/30",
  ERR:  "bg-red-500/15 text-red-400 border border-red-500/30",
  SYS:  "bg-orange-500/15 text-orange-400 border border-orange-500/30",
}

export function AiLogTerminal({ logs }) {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [logs])

  return (
    <div className="rounded-lg border border-gray-800 bg-[#18181b] flex flex-col h-80">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800 bg-[#27272a] rounded-t-lg">
        <div className="flex items-center gap-2.5">
          <span className="h-3 w-3 rounded-full bg-red-500/70" />
          <span className="h-3 w-3 rounded-full bg-yellow-500/70" />
          <span className="h-3 w-3 rounded-full bg-green-500/70" />
          <div className="ml-2 flex items-center gap-2">
            <Brain size={13} className="text-purple-500" />
            <span className="text-xs font-semibold text-white tracking-wide">AI Learning Log</span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3 font-mono text-xs space-y-1.5">
        {logs.map((log, i) => (
          <div key={i} className="flex items-start gap-2.5">
            <span className="text-gray-600 shrink-0 w-[72px]">{log.timestamp}</span>
            <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-widest ${levelStyles[log.level]}`}>
              {log.level}
            </span>
            <span className="text-gray-300">{log.message}</span>
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  )
}
