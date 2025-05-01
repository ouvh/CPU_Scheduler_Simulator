<!-- filepath: c:\Users\OussamaLaaroussi\Desktop\CS__s6\OS\OS_scheduler\frontend\src\App.vue -->
<script setup>
import { ref, onMounted, inject,nextTick } from 'vue'
import { useSimulationStore } from '@/stores/simulation'
import ProcessForm from '@/components/ProcessForm.vue'
import ProcessList from '@/components/ProcessList.vue'
import SimulationControls from '@/components/SimulationControls.vue'
import MetricsDisplay from '@/components/MetricsDisplay.vue'
import GanttChart from '@/components/GanttChart.vue'
import ComparisonReport from '@/components/ComparisonReport.vue'


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
    // i have made a change here to fix a bug
    store.saveFinalMetrics(data)
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

const showComparisonReport = ref(false)
const comparisonReport = ref(null)

// Handler for the openComparison event
const handleOpenComparison = () => {
  showComparisonReport.value = true
  
  // Wait for the modal to be rendered and then call runComparison
  nextTick(() => {
    if (comparisonReport.value) {
      comparisonReport.value.runComparison()
    }
  })
}

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
          <SimulationControls @openComparison="handleOpenComparison"  :disabled="store.processes.length === 0" />
          <ProcessList />
        </div>
        
        <div class="lg:col-span-2 space-y-6">
          <MetricsDisplay />
          <GanttChart />
        </div>
      </div>


      <div v-if="showComparisonReport" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg shadow-xl w-11/12 max-w-5xl max-h-[90vh] overflow-y-auto">
    <div class="p-4 border-b flex justify-between items-center">
      <h2 class="text-xl font-bold">Scheduler Algorithm Comparison</h2>
      <button @click="showComparisonReport = false" class="text-gray-500 hover:text-gray-700">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>
    <div class="p-6">
      <ComparisonReport ref="comparisonReport" />
    </div>
  </div>
</div>




    </div>
  </div>
</template>