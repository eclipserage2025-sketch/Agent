import React, { useState, useEffect, useCallback } from 'react'
import { StatCards } from './components/miner/stat-cards'
import { PerformanceCharts } from './components/miner/performance-charts'
import { AiLogTerminal } from './components/miner/ai-log-terminal'
import { ConfigPanel } from './components/miner/config-panel'
import { Play, Square, Wifi, WifiOff, RefreshCw } from "lucide-react"

function formatUptime(seconds) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}h ${m}m ${s}s`
  return `${m}m ${s}s`
}

function nowLabel() {
  return new Date().toLocaleTimeString("en-US", { hour12: false })
}

export default function App() {
  const [isRunning, setIsRunning] = useState(false)
  const [stats, setStats] = useState({
    hashrate: 0,
    temperature: 0,
    shares_found: 0,
    active_threads: 0,
    ai_confidence: 0,
    uptime_seconds: 0,
    is_mining: false
  })
  const [hashrateHistory, setHashrateHistory] = useState([])
  const [tempHistory, setTempHistory] = useState([])
  const [logs, setLogs] = useState([
    { timestamp: nowLabel(), level: "SYS", message: "AI Monero Miner Initialized." }
  ])
  const [config, setConfig] = useState({
    poolHost: "pool.supportxmr.com",
    poolPort: "3333",
    walletAddress: "",
    threads: 4,
    autotune: true
  })

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch("/stats")
      const data = await res.json()

      setStats({
        hashrate: data.hash_rate,
        temperature: data.cpu_temp || 0,
        shares_found: data.shares_found,
        active_threads: data.threads,
        ai_confidence: data.ai_trained ? 95 : 0,
        uptime_seconds: 0, // Logic for uptime can be added to backend
        is_mining: data.is_mining
      })
      setIsRunning(data.is_mining)

      const label = nowLabel()
      setHashrateHistory(prev => [...prev.slice(-59), { time: label, value: data.hash_rate }])
      setTempHistory(prev => [...prev.slice(-59), { time: label, value: data.cpu_temp || 0 }])

      if (data.ai_trained && logs.length < 2) {
          setLogs(prev => [...prev, { timestamp: nowLabel(), level: "AI", message: "Neural Model trained and persistent." }])
      }
    } catch (e) {
      console.error("Fetch error", e)
    }
  }, [logs])

  useEffect(() => {
    const id = setInterval(fetchStats, 2000)
    return () => clearInterval(id)
  }, [fetchStats])

  async function handleStart() {
    const formData = new FormData()
    formData.append("host", config.poolHost)
    formData.append("port", config.poolPort)
    formData.append("user", config.walletAddress)
    formData.append("threads", config.threads)
    formData.append("autotune", config.autotune ? "on" : "off")

    await fetch("/start", { method: "POST", body: formData })
    setIsRunning(true)
    setLogs(prev => [...prev, { timestamp: nowLabel(), level: "SYS", message: "Mining started." }])
  }

  async function handleStop() {
    await fetch("/stop", { method: "POST" })
    setIsRunning(false)
    setLogs(prev => [...prev, { timestamp: nowLabel(), level: "SYS", message: "Mining stopped." }])
  }

  return (
    <div className="min-h-screen bg-[#09090b] text-white">
      <header className="sticky top-0 z-10 border-b border-gray-800 bg-[#09090b]/95 backdrop-blur-sm">
        <div className="max-w-screen-2xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-orange-500 flex items-center justify-center font-bold text-black">X</div>
            <div>
              <div className="text-sm font-bold">Pro Miner</div>
              <div className="text-[10px] text-gray-500 font-mono">AI · MONERO</div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {isRunning ? (
              <button onClick={handleStop} className="flex items-center gap-2 bg-red-500/10 border border-red-500/40 text-red-500 px-4 py-1.5 rounded-md text-sm font-bold">
                <Square size={14} fill="currentColor" /> Stop
              </button>
            ) : (
              <button onClick={handleStart} className="flex items-center gap-2 bg-orange-500 text-black px-4 py-1.5 rounded-md text-sm font-bold">
                <Play size={14} fill="currentColor" /> Start
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-screen-2xl mx-auto px-6 py-6 flex flex-col gap-6">
        <StatCards
          hashrate={stats.hashrate}
          sharesFound={stats.shares_found}
          activeThreads={stats.active_threads}
          aiConfidence={stats.ai_confidence}
          isRunning={isRunning}
        />

        <PerformanceCharts
          hashrateData={hashrateHistory}
          temperatureData={tempHistory}
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ConfigPanel
            config={config}
            onSave={setConfig}
            isRunning={isRunning}
          />
          <AiLogTerminal logs={logs} />
        </div>
      </main>
    </div>
  )
}
