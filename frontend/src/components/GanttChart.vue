<!-- filepath: c:\Users\OussamaLaaroussi\Desktop\CS__s6\OS\OS_scheduler\frontend\src\components\GanttChart.vue -->
<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4">Process Execution Timeline</h2>
    
    <div v-if="history.length === 0" class="text-center py-8 text-gray-500">
      No execution data yet. Start the simulation to see the timeline.
    </div>
    
    <div v-else>
      <!-- Timeline Controls with Play Button -->
      <div class="flex items-center justify-between mb-4">
        <div>
          <span class="text-sm font-medium">Time Point: {{ selectedTime }}</span>
        </div>
        
        <div class="flex items-center space-x-4">
          <!-- Playback Controls -->
          <div class="flex items-center space-x-2">
            <button 
              @click="isPlaying ? stopPlayback() : startPlayback()" 
              class="px-3 py-1.5 rounded text-white focus:outline-none"
              :class="isPlaying ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'"
            >
              {{ isPlaying ? 'Pause' : 'Play' }}
            </button>
            
            <div class="flex items-center space-x-2">
              <span class="text-xs text-gray-600">Speed:</span>
              <select 
                v-model="playbackSpeed" 
                class="text-sm border rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="0.5">0.5x</option>
                <option value="1">1x</option>
                <option value="2">2x</option>
                <option value="3">3x</option>
                <option value="5">5x</option>
              </select>
            </div>
          </div>
          
          <!-- Navigation Controls -->
          <div class="flex items-center space-x-2">
            <button @click="moveTimePointer(-5)" class="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300">&lt;&lt;</button>
            <button @click="moveTimePointer(-1)" class="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300">&lt;</button>
            <button @click="moveTimePointer(1)" class="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300">&gt;</button>
            <button @click="moveTimePointer(5)" class="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300">&gt;&gt;</button>
          </div>
        </div>
      </div>
      
      <div class="overflow-x-auto mb-4">
        <div class="min-w-max"> <!-- Changed to min-w-max to ensure it grows horizontally -->
          <!-- Time markers -->
          <div class="flex border-b border-gray-200 pb-1">
            <div class="w-24 flex-shrink-0"></div> <!-- Label area -->
            <div class="flex-grow flex">
              <div 
                v-for="t in timeRangeToShow" 
                :key="t" 
                @click="selectedTime = t"
                class="flex-shrink-0 w-10 text-center text-xs text-gray-600 cursor-pointer hover:bg-blue-50"
                :class="{ 'bg-blue-100': selectedTime === t }"
              >
                {{ t }}
              </div>
            </div>
          </div>
          
          <!-- Running Process Timeline -->
          <div class="flex items-center border-b border-gray-100 py-2">
            <div class="w-24 text-sm font-medium text-gray-700">Running</div>
            <div class="flex-grow flex">
              <div 
                v-for="t in timeRangeToShow" 
                :key="t" 
                @click="selectedTime = t"
                class="flex-shrink-0 w-10 h-10 flex items-center justify-center cursor-pointer hover:bg-blue-50"
                :class="{ 'bg-blue-50': selectedTime === t }"
              >
                <div 
                  v-if="getProcessRunningAt(t) !== null"
                  class="w-8 h-8 rounded flex items-center justify-center text-xs font-medium text-white"
                  style="background-color: #10B981;"
                >
                  P{{ getProcessRunningAt(t) }}
                </div>
                <div v-else class="w-8 h-8 bg-gray-100 rounded"></div>
              </div>
            </div>
          </div>
          
          <!-- Ready Queue -->
          <div class="flex items-center border-b border-gray-100 py-2">
            <div class="w-24 text-sm font-medium text-gray-700">Ready Queue</div>
            <div class="flex-grow flex">
              <div 
                v-for="t in timeRangeToShow" 
                :key="t" 
                @click="selectedTime = t"
                class="flex-shrink-0 w-10 h-10 flex items-center justify-center cursor-pointer hover:bg-blue-50"
                :class="{ 'bg-blue-50': selectedTime === t }"
              >
                <div 
                  class="w-8 h-8 rounded flex items-center justify-center text-xs font-medium"
                  :class="{
                    'bg-yellow-100 text-yellow-800': getReadyQueueAt(t).length > 0,
                    'bg-gray-100 text-gray-400': getReadyQueueAt(t).length === 0
                  }"
                >
                  {{ getReadyQueueAt(t).length }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Blocked Processes -->
          <div class="flex items-center py-2">
            <div class="w-24 text-sm font-medium text-gray-700">Blocked</div>
            <div class="flex-grow flex">
              <div 
                v-for="t in timeRangeToShow" 
                :key="t" 
                @click="selectedTime = t"
                class="flex-shrink-0 w-10 h-10 flex items-center justify-center cursor-pointer hover:bg-blue-50"
                :class="{ 'bg-blue-50': selectedTime === t }"
              >
                <div 
                  class="w-8 h-8 rounded flex items-center justify-center text-xs font-medium"
                  :class="{
                    'bg-red-100 text-red-800': getBlockedProcessesAt(t).length > 0,
                    'bg-gray-100 text-gray-400': getBlockedProcessesAt(t).length === 0
                  }"
                >
                  {{ getBlockedProcessesAt(t).length }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Timeline progress indicator -->
          <div class="relative">
            <div 
              class="absolute top-0 h-full border-l-2 border-blue-500 transition-all duration-200"
              :style="{ left: `${(24 + selectedTime * 10 + 5)}px` }"
            ></div>
          </div>
        </div>
      </div>
      
      <!-- Time Point Details Panel -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="text-lg font-medium mb-3">Time Point {{ selectedTime }} Details</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Running Process -->
          <div class="bg-white p-3 rounded shadow-sm">
            <h4 class="text-sm font-semibold text-gray-600 mb-2">Running Process</h4>
            <div v-if="getProcessRunningAt(selectedTime) !== null" class="flex items-center">
              <div class="h-4 w-4 rounded-full bg-green-500 mr-2"></div>
              <span class="text-lg font-medium">Process {{ getProcessRunningAt(selectedTime) }}</span>
            </div>
            <div v-else class="text-gray-500 italic">No process running</div>
          </div>
          
          <!-- Ready Queue -->
          <div class="bg-white p-3 rounded shadow-sm">
            <div class="flex justify-between items-center mb-2">
              <h4 class="text-sm font-semibold text-gray-600">Ready Queue</h4>
              <span class="bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full text-xs">
                {{ getReadyQueueAt(selectedTime).length }}
              </span>
            </div>
            <div class="max-h-32 overflow-y-auto">
              <ul v-if="getReadyQueueAt(selectedTime).length > 0" class="space-y-1">
                <li v-for="pid in getReadyQueueAt(selectedTime)" :key="pid"
                    class="flex items-center text-sm bg-yellow-50 py-1 px-2 rounded">
                  <div class="h-3 w-3 rounded-full bg-yellow-400 mr-2"></div>
                  Process {{ pid }}
                </li>
              </ul>
              <p v-else class="text-sm text-gray-500 italic">Queue is empty</p>
            </div>
          </div>
          
          <!-- Blocked Processes -->
          <div class="bg-white p-3 rounded shadow-sm">
            <div class="flex justify-between items-center mb-2">
              <h4 class="text-sm font-semibold text-gray-600">Blocked Processes</h4>
              <span class="bg-red-100 text-red-800 px-2 py-0.5 rounded-full text-xs">
                {{ getBlockedProcessesAt(selectedTime).length }}
              </span>
            </div>
            <div class="max-h-32 overflow-y-auto">
              <ul v-if="getBlockedProcessesAt(selectedTime).length > 0" class="space-y-1">
                <li v-for="pid in getBlockedProcessesAt(selectedTime)" :key="pid"
                    class="flex items-center text-sm bg-red-50 py-1 px-2 rounded">
                  <div class="h-3 w-3 rounded-full bg-red-500 mr-2"></div>
                  Process {{ pid }}
                </li>
              </ul>
              <p v-else class="text-sm text-gray-500 italic">No blocked processes</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Legend -->
      <div class="mt-4 flex space-x-4 text-sm">
        <div class="flex items-center">
          <div class="w-3 h-3 bg-green-500 rounded-full mr-1"></div>
          <span class="text-gray-600">Running</span>
        </div>
        <div class="flex items-center">
          <div class="w-3 h-3 bg-yellow-400 rounded-full mr-1"></div>
          <span class="text-gray-600">Ready</span>
        </div>
        <div class="flex items-center">
          <div class="w-3 h-3 bg-red-500 rounded-full mr-1"></div>
          <span class="text-gray-600">Blocked</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useSimulationStore } from '@/stores/simulation'

const store = useSimulationStore()
const selectedTime = ref(0)
const windowSize = ref(12) // Number of time points to show at once

// Playback controls
const isPlaying = ref(false)
const playbackSpeed = ref(1)
const playbackInterval = ref(null)

// Get all history entries from the store
const history = computed(() => store.history)

// Get the maximum time in the history
const maxTime = computed(() => {
  if (history.value.length === 0) return 0
  return Math.max(...history.value.map(entry => entry.time))
})

// Calculate the start time for the current window view
const windowStartTime = computed(() => {
  // If selectedTime is less than half the window size, start from 0
  if (selectedTime.value < windowSize.value / 2) {
    return 0
  }
  
  // If selectedTime is close to the end, ensure we show the full window
  if (selectedTime.value > maxTime.value - windowSize.value / 2) {
    return Math.max(0, maxTime.value - windowSize.value + 1)
  }
  
  // Otherwise center the window around the selected time
  return Math.max(0, selectedTime.value - Math.floor(windowSize.value / 2))
})

// Calculate the range of time points to display
const timeRangeToShow = computed(() => {
  const start = windowStartTime.value
  const end = Math.min(maxTime.value + 1, start + windowSize.value)
  return Array.from({ length: end - start }, (_, i) => start + i)
})

// Watch for changes in history length to update selected time
watch(() => history.value.length, (newLength) => {
  if (newLength > 0) {
    selectedTime.value = history.value[newLength - 1].time
  }
})

// Watch for changes in current time from live updates
watch(() => store.metrics.currentTime, (newTime) => {
  if (!isPlaying.value && store.isRunning) {
    selectedTime.value = newTime
  }
})

// Methods to get data at a specific time
function getHistoryEntryAt(time) {
  return history.value.find(entry => entry.time === time) || {
    time,
    running: null,
    ready: [],
    blocked: []
  }
}

function getProcessRunningAt(time) {
  return getHistoryEntryAt(time).running
}

function getReadyQueueAt(time) {
  return getHistoryEntryAt(time).ready || []
}

function getBlockedProcessesAt(time) {
  return getHistoryEntryAt(time).blocked || []
}

// Method to move time pointer
function moveTimePointer(delta) {
  const newTime = selectedTime.value + delta
  if (newTime >= 0 && newTime <= maxTime.value) {
    selectedTime.value = newTime
  }
}

// Playback functions
function startPlayback() {
  if (isPlaying.value) return
  
  isPlaying.value = true
  
  playbackInterval.value = setInterval(() => {
    if (selectedTime.value < maxTime.value) {
      selectedTime.value++
    } else {
      stopPlayback()
    }
  }, 1000 / playbackSpeed.value)
}

function stopPlayback() {
  if (playbackInterval.value) {
    clearInterval(playbackInterval.value)
    playbackInterval.value = null
  }
  isPlaying.value = false
}

// Clean up interval on component unmount
onBeforeUnmount(() => {
  stopPlayback()
})

// Watch for changes in playback speed
watch(playbackSpeed, () => {
  if (isPlaying.value) {
    stopPlayback()
    startPlayback()
  }
})
</script>