<template>
    <div class="bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-xl font-bold mb-4">Process Execution Timeline</h2>
      
      <div v-if="history.length === 0" class="text-center py-8 text-gray-500">
        No execution data yet. Start the simulation to see the timeline.
      </div>
      
      <div v-else class="overflow-x-auto">
        <div class="min-w-full">
          <!-- Time scale -->
          <div class="flex border-b pb-2">
            <div class="w-16 flex-shrink-0"></div>
            <div class="flex-grow flex">
              <div 
                v-for="time in maxTime + 1" 
                :key="time" 
                class="flex-shrink-0 w-8 text-center text-xs text-gray-600"
              >
                {{ time - 1 }}
              </div>
            </div>
          </div>
          
          <!-- Gantt Chart -->
          <div class="pt-2">
            <!-- Running Process Timeline -->
            <div class="flex items-center py-2">
              <div class="w-16 text-sm text-gray-700 font-medium">Running</div>
              <div class="flex-grow flex">
                <div 
                  v-for="time in maxTime" 
                  :key="time" 
                  class="flex-shrink-0 w-8 h-8 flex items-center justify-center"
                >
                  <div 
                    v-if="getProcessAtTime(time - 1)"
                    class="w-7 h-7 bg-green-500 rounded flex items-center justify-center text-xs text-white font-medium"
                  >
                    {{ getProcessAtTime(time - 1) }}
                  </div>
                  <div v-else class="w-7 h-7 bg-gray-100 rounded"></div>
                </div>
              </div>
            </div>
            
            <!-- Ready Queue Length -->
            <div class="flex items-center py-2">
              <div class="w-16 text-sm text-gray-700 font-medium">Ready</div>
              <div class="flex-grow flex">
                <div 
                  v-for="time in maxTime" 
                  :key="time" 
                  class="flex-shrink-0 w-8 h-8 flex items-center justify-center"
                >
                  <div 
                    class="w-7 h-7 rounded flex items-center justify-center text-xs font-medium"
                    :class="[
                      getReadyCountAtTime(time - 1) > 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-50 text-gray-400'
                    ]"
                  >
                    {{ getReadyCountAtTime(time - 1) }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Blocked Count -->
            <div class="flex items-center py-2">
              <div class="w-16 text-sm text-gray-700 font-medium">Blocked</div>
              <div class="flex-grow flex">
                <div 
                  v-for="time in maxTime" 
                  :key="time" 
                  class="flex-shrink-0 w-8 h-8 flex items-center justify-center"
                >
                  <div 
                    class="w-7 h-7 rounded flex items-center justify-center text-xs font-medium"
                    :class="[
                      getBlockedCountAtTime(time - 1) > 0 ? 'bg-red-100 text-red-800' : 'bg-gray-50 text-gray-400'
                    ]"
                  >
                    {{ getBlockedCountAtTime(time - 1) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Legend -->
        <div class="mt-4 flex justify-end space-x-4">
          <div class="flex items-center">
            <div class="w-4 h-4 bg-green-500 rounded mr-1"></div>
            <span class="text-xs text-gray-600">Running</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 bg-yellow-100 rounded mr-1"></div>
            <span class="text-xs text-gray-600">Ready</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 bg-red-100 rounded mr-1"></div>
            <span class="text-xs text-gray-600">Blocked</span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import { useSimulationStore } from '@/stores/simulation'
  
  const store = useSimulationStore()
  
  const history = computed(() => store.history)
  const maxTime = computed(() => {
    if (history.value.length === 0) return 0
    return Math.max(...history.value.map(h => h.time)) + 1
  })
  
  // Get process running at a specific time
  const getProcessAtTime = (time) => {
    const entry = history.value.find(h => h.time === time)
    return entry ? entry.running : null
  }
  
  // Get ready queue count at a specific time
  const getReadyCountAtTime = (time) => {
    const entry = history.value.find(h => h.time === time)
    return entry ? entry.ready.length : 0
  }
  
  // Get blocked process count at a specific time
  const getBlockedCountAtTime = (time) => {
    const entry = history.value.find(h => h.time === time)
    return entry ? entry.blocked.length : 0
  }
  </script>