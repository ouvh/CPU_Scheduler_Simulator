import { defineStore } from 'pinia'

export const useSimulationStore = defineStore('simulation', {
  state: () => ({
    processes: [],
    metrics: {
      currentTime: 0,
      currentProcess: null,
      readyQueue: [],
      blocked: [],
      avg_turnaround: 0,
      avg_waiting: 0,
      cpu_utilization: 0,
      total_time: 0,
      throughput: 0,
      total_io_blocks: 0
    },
    isRunning: false,
    schedulerType: 'fcfs',
    timeQuantum: 4,
    history: [],
    finalMetrics: null // To store final metrics separately
  }),
  actions: {
    updateMetrics(payload) {
      // Map backend data to frontend store
      this.metrics = {
        currentTime: payload.time || 0,
        currentProcess: payload.running,
        readyQueue: payload.ready || [],
        blocked: payload.blocked || [],
        avg_turnaround: payload.metrics?.avg_turnaround || 0,
        avg_waiting: payload.metrics?.avg_waiting || 0,
        cpu_utilization: payload.metrics?.cpu_utilization || 0,
        total_time: payload.metrics?.total_time || 0,
        throughput: payload.metrics?.throughput || 0,
        total_io_blocks: payload.metrics?.total_io_blocks || 0
      }
      
      // Save history for Gantt chart and timeline
      if (payload.time !== undefined) {
        // Check if we already have an entry for this time
        const existingIndex = this.history.findIndex(h => h.time === payload.time)
        
        // New timeline entry
        const timelineEntry = {
          time: payload.time,
          running: payload.running,
          ready: [...(payload.ready || [])],
          blocked: [...(payload.blocked || [])]
        }
        
        if (existingIndex !== -1) {
          // Update existing entry
          this.history[existingIndex] = timelineEntry
        } else {
          // Add new entry
          this.history.push(timelineEntry)
          
          // Sort history by time
          this.history.sort((a, b) => a.time - b.time)
        }
      }
    },
    
    saveFinalMetrics(metrics) {
      // Store the final metrics separately so they don't get lost
      this.finalMetrics = { ...metrics }
    },
    
    addProcess(process) {
      this.processes.push(process)
    },
    
    removeProcess(pid) {
      const index = this.processes.findIndex(p => p.pid === pid)
      if (index !== -1) {
        this.processes.splice(index, 1)
      }
    },
    
    clearProcesses() {
      this.processes = []
    },
    
    reset() {
      this.isRunning = false
      this.history = []
      this.metrics = {
        currentTime: 0,
        currentProcess: null,
        readyQueue: [],
        blocked: [],
        avg_turnaround: 0,
        avg_waiting: 0,
        cpu_utilization: 0,
        total_time: 0,
        throughput: 0,
        total_io_blocks: 0
      }
      // Keep the finalMetrics intact for reference
    },
    
    // Complete reset, including processes and final metrics
    fullReset() {
      this.reset()
      this.processes = []
      this.finalMetrics = null
    }
  }
})