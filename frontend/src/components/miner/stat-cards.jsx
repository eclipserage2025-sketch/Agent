import React from 'react'
import { Cpu, Hash, CheckCircle2, Brain, TrendingUp, TrendingDown, Minus } from "lucide-react"

const accentStyles = {
  orange: {
    border: "border-orange-500/30",
    iconBg: "bg-orange-500/10",
    iconColor: "text-orange-500",
    valueColor: "text-orange-500",
  },
  teal: {
    border: "border-teal-500/30",
    iconBg: "bg-teal-500/10",
    iconColor: "text-teal-500",
    valueColor: "text-teal-500",
  },
  green: {
    border: "border-green-500/30",
    iconBg: "bg-green-500/10",
    iconColor: "text-green-500",
    valueColor: "text-green-500",
  },
  purple: {
    border: "border-purple-500/30",
    iconBg: "bg-purple-500/10",
    iconColor: "text-purple-500",
    valueColor: "text-purple-500",
  },
}

function StatCard({ title, value, unit, icon, trend, trendValue, accentColor, subtitle }) {
  const styles = accentStyles[accentColor]
  return (
    <div className={`relative rounded-lg border ${styles.border} bg-[#18181b] p-5 flex flex-col gap-3 overflow-hidden`}>
      <div className={`absolute top-0 left-0 right-0 h-[2px] ${accentColor === "orange" ? "bg-orange-500" : accentColor === "teal" ? "bg-teal-500" : accentColor === "green" ? "bg-green-500" : "bg-purple-500"}`} />
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium uppercase tracking-widest text-gray-400">{title}</span>
          {subtitle && <span className="text-[10px] text-gray-500">{subtitle}</span>}
        </div>
        <div className={`rounded-md p-2 ${styles.iconBg}`}>
          <span className={styles.iconColor}>{icon}</span>
        </div>
      </div>
      <div className="flex items-end gap-2">
        <span className={`text-3xl font-bold font-mono tracking-tight ${styles.valueColor}`}>{value}</span>
        {unit && <span className="text-sm text-gray-400 mb-1">{unit}</span>}
      </div>
      {trend && trendValue && (
        <div className="flex items-center gap-1.5">
          {trend === "up" ? (
            <TrendingUp size={12} className="text-green-500" />
          ) : trend === "down" ? (
            <TrendingDown size={12} className="text-red-500" />
          ) : (
            <Minus size={12} className="text-gray-400" />
          )}
          <span className={`text-xs font-medium ${trend === "up" ? "text-green-500" : trend === "down" ? "text-red-500" : "text-gray-400"}`}>
            {trendValue}
          </span>
        </div>
      )}
    </div>
  )
}

export function StatCards({ hashrate, sharesFound, activeThreads, aiConfidence, isRunning }) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Hashrate"
        value={hashrate >= 1000 ? (hashrate / 1000).toFixed(2) : hashrate.toFixed(1)}
        unit={hashrate >= 1000 ? "KH/s" : "H/s"}
        icon={<Hash size={18} />}
        trend={isRunning ? "up" : "neutral"}
        trendValue={isRunning ? "+2.4% vs avg" : "Stopped"}
        accentColor="orange"
        subtitle="RandomX Algorithm"
      />
      <StatCard
        title="Shares Found"
        value={sharesFound.toLocaleString()}
        unit="total"
        icon={<CheckCircle2 size={18} />}
        trend="up"
        trendValue="Active"
        accentColor="teal"
        subtitle="Accepted"
      />
      <StatCard
        title="Active Threads"
        value={String(activeThreads)}
        unit="cores"
        icon={<Cpu size={18} />}
        trend="neutral"
        trendValue="Optimal load"
        accentColor="green"
        subtitle="Utilization"
      />
      <StatCard
        title="AI Confidence"
        value={aiConfidence.toFixed(1)}
        unit="%"
        icon={<Brain size={18} />}
        trend={aiConfidence > 80 ? "up" : "neutral"}
        trendValue="Learning"
        accentColor="purple"
        subtitle="Self-Learning"
      />
    </div>
  )
}
