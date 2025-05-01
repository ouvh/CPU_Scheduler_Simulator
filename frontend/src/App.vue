<!-- filepath: c:\Users\OussamaLaaroussi\Desktop\CS__s6\OS\OS_scheduler\frontend\src\App.vue -->
<script setup>
import { ref, onMounted, inject } from 'vue'
import { useSimulationStore } from '@/stores/simulation'
import ProcessForm from '@/components/ProcessForm.vue'
import ProcessList from '@/components/ProcessList.vue'
import SimulationControls from '@/components/SimulationControls.vue'
import MetricsDisplay from '@/components/MetricsDisplay.vue'
import GanttChart from '@/components/GanttChart.vue'

const socket = inject('socket')
const store = useSimulationStore()
const error = ref('')

onMounted(() => {
  // Initial status
  socket.on('status', (data) => {
    console.log('Received status:', data)
    store.isRunning = data.running
  })
  
  // Process added
  socket.on('process_added', (process) => {
    console.log('Process added:', process)
    store.addProcess(process)
  })
  
  // Process removed
  socket.on('process_removed', (data) => {
    console.log('Process removed:', data)
    store.removeProcess(data.pid)
  })
  
  // Simulation updates
  socket.on('update', (data) => {
    console.log('Simulation update:', data)
    store.updateMetrics(data)
  })
  
  // Simulation completed
  socket.on('complete', (data) => {
    console.log('Simulation complete:', data)
    store.isRunning = false
    store.updateMetrics(data)
    // Save the final metrics
    store.saveFinalMetrics(data.metrics)
  })
  
  // Reset confirmation
  socket.on('reset_done', () => {
    console.log('Reset completed')
    store.reset()
  })
  
  // Clear all data (processes + simulation)
  socket.on('clear_all', () => {
    console.log('All data cleared')
    store.fullReset()
  })
  
  // Error handling
  socket.on('error', (data) => {
    console.error('Error:', data.message)
    error.value = data.message
    
    // Auto-hide error after 5 seconds
    setTimeout(() => {
      if (error.value === data.message) {
        error.value = ''
      }
    }, 5000)
  })
})
</script>

<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-7xl mx-auto space-y-6">
      <h1 class="text-3xl font-bold text-gray-800">CPU Scheduler Simulation</h1>
      
      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6">
        <strong class="font-bold">Error:</strong>
        <span class="block sm:inline">{{ error }}</span>
        <button @click="error = ''" class="absolute top-0 right-0 px-4 py-3">
          <span class="sr-only">Close</span>
          &times;
        </button>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1 space-y-6">
          <ProcessForm :disabled="store.isRunning" />
          <SimulationControls :disabled="store.processes.length === 0" />
          <ProcessList />
        </div>
        
        <div class="lg:col-span-2 space-y-6">
          <MetricsDisplay />
          <GanttChart />
        </div>
      </div>
    </div>
  </div>
</template>