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
    history: []
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
      
      // Save history for Gantt chart
      if (payload.time !== undefined) {
        this.history.push({
          time: payload.time,
          running: payload.running,
          ready: [...payload.ready] || [],
          blocked: [...payload.blocked] || []
        })
      }
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
    }
  }
})