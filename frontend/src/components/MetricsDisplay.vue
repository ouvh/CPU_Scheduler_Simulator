<!-- filepath: c:\Users\OussamaLaaroussi\Desktop\CS__s6\OS\OS_scheduler\frontend\src\components\MetricsDisplay.vue -->
<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4">Simulation Metrics</h2>
    
    <!-- Simulation Status -->
    <div class="grid grid-cols-2 gap-4 mb-4">
      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="font-semibold text-gray-700">Current Time</h3>
        <p class="text-2xl font-bold text-blue-600">{{ metrics.currentTime }}</p>
      </div>
      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="font-semibold text-gray-700">Running Process</h3>
        <p class="text-2xl font-bold" 
           :class="metrics.currentProcess ? 'text-green-600' : 'text-gray-400'">
          {{ metrics.currentProcess || 'None' }}
        </p>
      </div>
    </div>
    
    <!-- Process Queues -->
    <div class="grid grid-cols-2 gap-4 mb-4">
      <div class="bg-gray-50 p-4 rounded-lg">
        <div class="flex justify-between items-center mb-2">
          <h3 class="font-semibold">Ready Queue</h3>
          <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
            {{ metrics.readyQueue.length }}
          </span>
        </div>
        <div class="max-h-32 overflow-y-auto">
          <ul v-if="metrics.readyQueue.length > 0" class="space-y-1">
            <li v-for="pid in metrics.readyQueue" :key="pid" 
                class="bg-white p-2 rounded shadow-sm flex items-center">
              <div class="h-3 w-3 rounded-full bg-yellow-400 mr-2"></div>
              Process {{ pid }}
            </li>
          </ul>
          <p v-else class="text-gray-400 text-sm italic">Empty queue</p>
        </div>
      </div>
      
      <div class="bg-gray-50 p-4 rounded-lg">
        <div class="flex justify-between items-center mb-2">
          <h3 class="font-semibold">Blocked Processes</h3>
          <span class="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs">
            {{ metrics.blocked.length }}
          </span>
        </div>
        <div class="max-h-32 overflow-y-auto">
          <ul v-if="metrics.blocked.length > 0" class="space-y-1">
            <li v-for="pid in metrics.blocked" :key="pid" 
                class="bg-white p-2 rounded shadow-sm flex items-center">
              <div class="h-3 w-3 rounded-full bg-red-500 mr-2"></div>
              Process {{ pid }}
            </li>
          </ul>
          <p v-else class="text-gray-400 text-sm italic">No blocked processes</p>
        </div>
      </div>
    </div>

    <!-- Performance Metrics -->
    <div class="bg-gray-50 p-4 rounded-lg">
      <h3 class="font-semibold mb-2">Performance Metrics</h3>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div class="bg-white p-3 rounded shadow-sm">
          <p class="text-sm text-gray-600">Avg Turnaround Time</p>
          <p class="text-lg font-semibold">
            {{ metrics.avg_turnaround.toFixed(2) }}
          </p>
        </div>
        <div class="bg-white p-3 rounded shadow-sm">
          <p class="text-sm text-gray-600">Avg Waiting Time</p>
          <p class="text-lg font-semibold">
            {{ metrics.avg_waiting.toFixed(2) }}
          </p>
        </div>
        <div class="bg-white p-3 rounded shadow-sm">
          <p class="text-sm text-gray-600">CPU Utilization</p>
          <p class="text-lg font-semibold">
            {{ metrics.cpu_utilization.toFixed(2) }}%
          </p>
        </div>
        <div class="bg-white p-3 rounded shadow-sm">
          <p class="text-sm text-gray-600">Total Time</p>
          <p class="text-lg font-semibold">
            {{ metrics.total_time }}
          </p>
        </div>
        <div class="bg-white p-3 rounded shadow-sm">
          <p class="text-sm text-gray-600">Completed Processes</p>
          <p class="text-lg font-semibold">
            {{ metrics.throughput }}
          </p>
        </div>
        <div class="bg-white p-3 rounded shadow-sm">
          <p class="text-sm text-gray-600">Total I/O Blocks</p>
          <p class="text-lg font-semibold">
            {{ metrics.total_io_blocks }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { computed } from 'vue'
import { useSimulationStore } from '@/stores/simulation'
  
const store = useSimulationStore()
const metrics = computed(() => store.metrics)
</script>