import React from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, ReferenceLine } from "recharts"
import { Activity, Thermometer } from "lucide-react"

function CustomTooltip({ active, payload, label, unit = "", color }) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-md border border-gray-700 bg-[#27272a] px-3 py-2 shadow-xl text-xs font-mono">
        <p className="text-gray-400 mb-1">{label}</p>
        <p style={{ color }} className="font-bold text-sm">
          {payload[0].value.toFixed(1)}
          <span className="text-gray-400 font-normal ml-1">{unit}</span>
        </p>
      </div>
    )
  }
  return null
}

export function PerformanceCharts({ hashrateData, temperatureData }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="rounded-lg border border-gray-800 bg-[#18181b] p-5">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <div className="rounded p-1.5 bg-orange-500/10">
              <Activity size={15} className="text-orange-500" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Hashrate</h3>
              <p className="text-[10px] text-gray-500 uppercase tracking-wider">Live Activity</p>
            </div>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={hashrateData}>
            <defs>
              <linearGradient id="hashrateGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f97316" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
            <XAxis dataKey="time" hide />
            <YAxis tick={{ fill: "#71717a", fontSize: 10 }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip unit="H/s" color="#f97316" />} />
            <Area type="monotone" dataKey="value" stroke="#f97316" strokeWidth={2} fill="url(#hashrateGrad)" dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="rounded-lg border border-gray-800 bg-[#18181b] p-5">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <div className="rounded p-1.5 bg-teal-500/10">
              <Thermometer size={15} className="text-teal-500" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">CPU Temperature</h3>
              <p className="text-[10px] text-gray-500 uppercase tracking-wider">Thermal Status</p>
            </div>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={temperatureData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
            <XAxis dataKey="time" hide />
            <YAxis tick={{ fill: "#71717a", fontSize: 10 }} axisLine={false} tickLine={false} domain={[30, 100]} />
            <Tooltip content={<CustomTooltip unit="°C" color="#14b8a6" />} />
            <ReferenceLine y={80} stroke="#ef4444" strokeDasharray="3 3" />
            <Line type="monotone" dataKey="value" stroke="#14b8a6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
