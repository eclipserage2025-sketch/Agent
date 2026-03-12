import React, { useState } from 'react'
import { Settings, Save, Wifi, Brain } from "lucide-react"

export function ConfigPanel({ config, onSave, isRunning }) {
  const [local, setLocal] = useState(config)
  const [saved, setSaved] = useState(false)

  function handleSave() {
    onSave(local)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="rounded-lg border border-gray-800 bg-[#18181b] p-5">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2.5">
          <div className="rounded p-1.5 bg-orange-500/10">
            <Settings size={15} className="text-orange-500" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Configuration</h3>
            <p className="text-[10px] text-gray-500 uppercase tracking-wider">Pool & Wallet</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">Pool Host</label>
          <input
            type="text"
            value={local.poolHost}
            onChange={(e) => setLocal({ ...local, poolHost: e.target.value })}
            className="rounded-md bg-[#27272a] border border-gray-800 text-white text-sm font-mono px-3 py-2 focus:ring-1 focus:ring-orange-500 outline-none"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">Port</label>
          <input
            type="text"
            value={local.poolPort}
            onChange={(e) => setLocal({ ...local, poolPort: e.target.value })}
            className="rounded-md bg-[#27272a] border border-gray-800 text-white text-sm font-mono px-3 py-2 focus:ring-1 focus:ring-orange-500 outline-none"
          />
        </div>
        <div className="flex flex-col gap-1.5 md:col-span-2">
          <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">Wallet Address</label>
          <input
            type="text"
            value={local.walletAddress}
            onChange={(e) => setLocal({ ...local, walletAddress: e.target.value })}
            className="rounded-md bg-[#27272a] border border-gray-800 text-white text-sm font-mono px-3 py-2 focus:ring-1 focus:ring-orange-500 outline-none"
          />
        </div>
      </div>

      <div className="mt-5 flex justify-end">
        <button
          onClick={handleSave}
          className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition-all ${saved ? "bg-green-500 text-black" : "bg-orange-500 text-black hover:brightness-110"}`}
        >
          <Save size={14} />
          {saved ? "Saved!" : "Save Configuration"}
        </button>
      </div>
    </div>
  )
}
