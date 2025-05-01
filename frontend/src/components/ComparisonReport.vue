<!-- filepath: c:\Users\OussamaLaaroussi\Desktop\CS__s6\OS\OS_scheduler\frontend\src\components\ComparisonReport.vue -->
<script setup>
import { ref, computed, onMounted, onBeforeUnmount, inject, watch, nextTick } from 'vue'
import { useSimulationStore } from '@/stores/simulation'
import Chart from 'chart.js/auto'
import html2pdf from 'html2pdf.js'

const store = useSimulationStore()
const socket = inject('socket')

const isLoading = ref(false)
const results = ref({})

// Chart references with unique IDs
const turnaroundChart = ref(null)
const waitingChart = ref(null)
const utilizationChart = ref(null)
const timeChart = ref(null)

// Chart instances object
const chartInstances = {
  turnaround: null,
  waiting: null,
  utilization: null,
  time: null
}

const hasResults = computed(() => Object.keys(results.value).length > 0)

// Run all scheduler algorithms
const runComparison = () => {
  isLoading.value = true
  results.value = {}
  destroyAllCharts() // Make sure to destroy any existing charts
  socket.emit('compare_schedulers')
}

// Safely destroy all chart instances
const destroyAllCharts = () => {
  // First approach - destroy by instance reference
  Object.entries(chartInstances).forEach(([key, chart]) => {
    if (chart) {
      try {
        chart.destroy()
        console.log(`Destroyed ${key} chart`)
      } catch (e) {
        console.warn(`Error destroying ${key} chart:`, e)
      }
    }
    chartInstances[key] = null
  })
  
  // Second approach - destroy any chart linked to our canvas elements
  const canvasRefs = [turnaroundChart, waitingChart, utilizationChart, timeChart]
  canvasRefs.forEach((canvasRef, index) => {
    if (canvasRef && canvasRef.value) {
      const canvasId = canvasRef.value.id || index
      try {
        const chartInstance = Chart.getChart(canvasRef.value)
        if (chartInstance) {
          chartInstance.destroy()
          console.log(`Destroyed chart on canvas ${canvasId}`)
        }
      } catch (e) {
        console.warn(`Error destroying chart on canvas ${canvasId}:`, e)
      }
    }
  })
}

// Get algorithm with best metric
const getBestAlgorithm = (metric, lowest = false) => {
  if (!hasResults.value) return 'N/A'
  
  let bestAlgo = Object.keys(results.value)[0]
  let bestValue = results.value[bestAlgo].metrics[metric]
  
  for (const algo in results.value) {
    const value = results.value[algo].metrics[metric]
    if ((lowest && value < bestValue) || (!lowest && value > bestValue)) {
      bestAlgo = algo
      bestValue = value
    }
  }
  
  return bestAlgo
}

const getBestMetric = (metric, lowest = false) => {
  if (!hasResults.value) return 0
  return results.value[getBestAlgorithm(metric, lowest)].metrics[metric]
}

// Generate appropriate recommendation based on metrics
const getRecommendation = () => {
  if (!hasResults.value) return ''
  
  let recommendation = 'Based on the simulation results: '
  
  // Get the best overall algorithm
  let scores = {}
  for (const algo in results.value) {
    scores[algo] = 0
    
    // Lower is better for turnaround and waiting
    if (getBestAlgorithm('avg_turnaround', true) === algo) scores[algo] += 3
    if (getBestAlgorithm('avg_waiting', true) === algo) scores[algo] += 3
    
    // Higher is better for CPU utilization
    if (getBestAlgorithm('cpu_utilization') === algo) scores[algo] += 2
    
    // Lower is better for total time
    if (getBestAlgorithm('total_time', true) === algo) scores[algo] += 2
  }
  
  const bestAlgo = Object.keys(scores).reduce((a, b) => scores[a] > scores[b] ? a : b)
  
  recommendation += `<strong>${bestAlgo}</strong> provides the best overall performance for your process set. `
  
  // Add specific recommendations
  if (results.value[bestAlgo].metrics.avg_waiting < 5) {
    recommendation += 'The waiting time is relatively low, which is great for interactive processes. '
  } 
  
  if (results.value[bestAlgo].metrics.cpu_utilization > 90) {
    recommendation += 'CPU utilization is excellent, maximizing system throughput. '
  } else if (results.value[bestAlgo].metrics.cpu_utilization < 70) {
    recommendation += 'Consider optimizing I/O operations to improve CPU utilization. '
  }
  
  return recommendation
}

// Safe chart creation function
const createSingleChart = (canvasElement, type, data, options = {}) => {
  if (!canvasElement) {
    console.error("Canvas element is null")
    return null
  }
  
  // Check if there's already a chart instance on this canvas
  try {
    const existingChart = Chart.getChart(canvasElement)
    if (existingChart) {
      console.log(`Destroying existing chart on ${canvasElement.id || 'unnamed canvas'}`)
      existingChart.destroy()
    }
  } catch (e) {
    console.warn('Error checking for existing chart:', e)
  }
  
  try {
    // Create new chart
    const chart = new Chart(canvasElement, {
      type,
      data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 500
        },
        ...options
      }
    })
    
    console.log(`Created new ${type} chart on ${canvasElement.id || 'unnamed canvas'}`)
    return chart
  } catch (e) {
    console.error(`Error creating ${type} chart:`, e)
    return null
  }
}

// Create all charts - redesigned to be more reliable
const createAllCharts = async () => {
  console.log("Starting chart creation...")
  
  // First destroy any existing charts
  destroyAllCharts()
  
  // Wait for Vue to update DOM
  await nextTick()
  
  if (!hasResults.value) {
    console.log("No results available, skipping chart creation")
    return
  }
  
  const algorithms = Object.keys(results.value)
  if (algorithms.length === 0) {
    console.warn("No algorithm data available")
    return
  }
  
  // Chart colors
  const colors = [
    'rgba(54, 162, 235, 0.8)',
    'rgba(255, 99, 132, 0.8)',
    'rgba(75, 192, 192, 0.8)',
    'rgba(255, 206, 86, 0.8)',
    'rgba(153, 102, 255, 0.8)'
  ]
  
  // Wait longer to ensure DOM is ready
  await new Promise(resolve => setTimeout(resolve, 300))
  
  try {
    console.log("Creating turnaround chart...")
    if (turnaroundChart.value) {
      chartInstances.turnaround = createSingleChart(
        turnaroundChart.value,
        'bar',
        {
          labels: algorithms,
          datasets: [{
            label: 'Average Turnaround Time',
            data: algorithms.map(algo => results.value[algo].metrics.avg_turnaround),
            backgroundColor: colors,
            borderWidth: 1
          }]
        },
        {
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      )
    }
    
    console.log("Creating waiting chart...")
    if (waitingChart.value) {
      chartInstances.waiting = createSingleChart(
        waitingChart.value,
        'bar',
        {
          labels: algorithms,
          datasets: [{
            label: 'Average Waiting Time',
            data: algorithms.map(algo => results.value[algo].metrics.avg_waiting),
            backgroundColor: colors,
            borderWidth: 1
          }]
        },
        {
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      )
    }
    
    console.log("Creating utilization chart...")
    if (utilizationChart.value) {
      chartInstances.utilization = createSingleChart(
        utilizationChart.value,
        'radar',
        {
          labels: algorithms,
          datasets: [{
            label: 'CPU Utilization (%)',
            data: algorithms.map(algo => results.value[algo].metrics.cpu_utilization),
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(54, 162, 235, 1)'
          }]
        },
        {
          plugins: {
            legend: { display: false }
          },
          scales: {
            r: {
              beginAtZero: true,
              max: 100,
              ticks: { stepSize: 20 }
            }
          }
        }
      )
    }
    
    console.log("Creating time chart...")
    if (timeChart.value) {
      chartInstances.time = createSingleChart(
        timeChart.value,
        'bar',
        {
          labels: algorithms,
          datasets: [{
            label: 'Total Execution Time',
            data: algorithms.map(algo => results.value[algo].metrics.total_time),
            backgroundColor: colors,
            borderWidth: 1
          }]
        },
        {
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      )
    }
    
    console.log("All charts created successfully")
    return true
  } catch (e) {
    console.error("Error creating charts:", e)
    return false
  }
}

// Captures chart snapshots for PDF generation
const captureChartImages = async () => {
  const chartImages = {}
  
  console.log("Capturing chart images for PDF...")
  
  try {
    // Force charts to render with any pending animations
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Capture each chart
    if (chartInstances.turnaround && turnaroundChart.value) {
      chartImages.turnaround = turnaroundChart.value.toDataURL('image/png')
    }
    
    if (chartInstances.waiting && waitingChart.value) {
      chartImages.waiting = waitingChart.value.toDataURL('image/png')
    }
    
    if (chartInstances.utilization && utilizationChart.value) {
      chartImages.utilization = utilizationChart.value.toDataURL('image/png')
    }
    
    if (chartInstances.time && timeChart.value) {
      chartImages.time = timeChart.value.toDataURL('image/png')
    }
    
    return chartImages
  } catch (e) {
    console.error("Error capturing chart images:", e)
    return {}
  }
}
// this feature is not supported , some related to the library don't work
// Improved PDF download function
// const downloadReportAsPDF = async () => {
//   console.log("Starting PDF generation process...")
  
//   // 1. Make sure charts are fully rendered
//   const chartsCreated = await createAllCharts()
//   if (!chartsCreated) {
//     console.error("Failed to create charts for PDF")
//     alert("Unable to generate PDF with charts. Please try again.")
//     return
//   }
  
//   // 2. Capture chart images
//   await nextTick();
//   const chartImages = await captureChartImages()
  
//   // Create a container outside the try block so we can clean it up even on error
//   const pdfContainer = document.createElement('div')
  
//   try {
//     // 3. Style the container
//     pdfContainer.style.padding = '20px'
//     pdfContainer.style.backgroundColor = 'white'
//     pdfContainer.style.fontFamily = 'Arial, sans-serif'
//     pdfContainer.style.width = '800px'
    
//     // Position off-screen for generation
//     pdfContainer.style.position = 'fixed'
//     pdfContainer.style.left = '-9999px'
//     pdfContainer.style.top = '0'
//     pdfContainer.style.zIndex = '-1000'
    
//     // Add to DOM
//     document.body.appendChild(pdfContainer)
    
//     // 4. Add title
//     console.log("Building PDF content...")
//     const title = document.createElement('h1')
//     title.textContent = 'Scheduler Algorithm Comparison Report'
//     title.style.fontSize = '24px'
//     title.style.marginBottom = '20px'
//     title.style.textAlign = 'center'
//     title.style.color = '#333'
//     pdfContainer.appendChild(title)
    
//     // 5. Add timestamp
//     const timestamp = document.createElement('p')
//     const now = new Date()
//     timestamp.textContent = `Generated on: ${now.toLocaleDateString()} at ${now.toLocaleTimeString()}`
//     timestamp.style.textAlign = 'center'
//     timestamp.style.marginBottom = '30px'
//     timestamp.style.color = '#666'
//     pdfContainer.appendChild(timestamp)
    
//     // 6. Create table with results
//     const tableSection = document.createElement('div')
//     tableSection.style.marginBottom = '30px'
    
//     const tableTitle = document.createElement('h2')
//     tableTitle.textContent = 'Performance Metrics'
//     tableTitle.style.fontSize = '18px'
//     tableTitle.style.marginBottom = '10px'
//     tableSection.appendChild(tableTitle)
    
//     const table = document.createElement('table')
//     table.style.width = '100%'
//     table.style.borderCollapse = 'collapse'
//     table.style.marginBottom = '20px'
    
//     // Table header
//     const thead = document.createElement('thead')
//     thead.style.backgroundColor = '#f3f4f6'
//     const headerRow = document.createElement('tr')
    
//     const headers = ['Algorithm', 'Avg Turnaround', 'Avg Waiting', 'CPU Utilization', 'Total Time']
//     headers.forEach(text => {
//       const th = document.createElement('th')
//       th.textContent = text
//       th.style.padding = '8px'
//       th.style.border = '1px solid #ddd'
//       th.style.textAlign = 'left'
//       headerRow.appendChild(th)
//     })
    
//     thead.appendChild(headerRow)
//     table.appendChild(thead)
    
//     // Table body
//     const tbody = document.createElement('tbody')
    
//     if (Object.keys(results.value).length === 0) {
//       console.error("No results available for PDF generation")
//       throw new Error("No comparison results available")
//     }
    
//     Object.entries(results.value).forEach(([algorithm, result]) => {
//       const row = document.createElement('tr')
      
//       const algorithmCell = document.createElement('td')
//       algorithmCell.textContent = algorithm
//       algorithmCell.style.padding = '8px'
//       algorithmCell.style.border = '1px solid #ddd'
//       row.appendChild(algorithmCell)
      
//       const turnaroundCell = document.createElement('td')
//       turnaroundCell.textContent = result.metrics.avg_turnaround.toFixed(2)
//       turnaroundCell.style.padding = '8px'
//       turnaroundCell.style.border = '1px solid #ddd'
//       row.appendChild(turnaroundCell)
      
//       const waitingCell = document.createElement('td')
//       waitingCell.textContent = result.metrics.avg_waiting.toFixed(2)
//       waitingCell.style.padding = '8px'
//       waitingCell.style.border = '1px solid #ddd'
//       row.appendChild(waitingCell)
      
//       const utilizationCell = document.createElement('td')
//       utilizationCell.textContent = `${result.metrics.cpu_utilization.toFixed(2)}%`
//       utilizationCell.style.padding = '8px'
//       utilizationCell.style.border = '1px solid #ddd'
//       row.appendChild(utilizationCell)
      
//       const timeCell = document.createElement('td')
//       timeCell.textContent = result.metrics.total_time
//       timeCell.style.padding = '8px'
//       timeCell.style.border = '1px solid #ddd'
//       row.appendChild(timeCell)
      
//       tbody.appendChild(row)
//     })
    
//     table.appendChild(tbody)
//     tableSection.appendChild(table)
//     pdfContainer.appendChild(tableSection)
    
//     // 7. Add charts as images
//     const chartsTitle = document.createElement('h2')
//     chartsTitle.textContent = 'Performance Charts'
//     chartsTitle.style.fontSize = '18px'
//     chartsTitle.style.marginBottom = '15px'
//     pdfContainer.appendChild(chartsTitle)
    
//     // Create a grid for charts
//     const chartsGrid = document.createElement('div')
//     chartsGrid.style.display = 'grid'
//     chartsGrid.style.gridTemplateColumns = '1fr 1fr'
//     chartsGrid.style.gap = '20px'
//     chartsGrid.style.marginBottom = '30px'
    
//     // Chart data with titles
//     const chartData = [
//       { id: 'turnaround', title: 'Average Turnaround Time', dataUrl: chartImages.turnaround },
//       { id: 'waiting', title: 'Average Waiting Time', dataUrl: chartImages.waiting },
//       { id: 'utilization', title: 'CPU Utilization', dataUrl: chartImages.utilization },
//       { id: 'time', title: 'Total Execution Time', dataUrl: chartImages.time }
//     ]
    
//     // Add each chart as an image
//     chartData.forEach(chart => {
//       // Create chart container
//       const chartBox = document.createElement('div')
//       chartBox.style.padding = '10px'
//       chartBox.style.backgroundColor = '#f9fafb'
//       chartBox.style.borderRadius = '5px'
      
//       // Add chart title
//       const chartTitle = document.createElement('h3')
//       chartTitle.textContent = chart.title
//       chartTitle.style.fontSize = '16px'
//       chartTitle.style.marginBottom = '10px'
//       chartTitle.style.textAlign = 'center'
//       chartBox.appendChild(chartTitle)
      
//       // Use either the captured image or a placeholder
//       if (chart.dataUrl) {
//         const img = document.createElement('img')
//         img.src = chart.dataUrl
//         img.style.width = '100%'
//         img.style.display = 'block'
//         img.style.height = '200px'
//         img.style.objectFit = 'contain'
//         img.style.backgroundColor = 'white'
//         img.style.padding = '5px'
//         chartBox.appendChild(img)
//       } else {
//         const placeholder = document.createElement('div')
//         placeholder.textContent = `Chart not available`
//         placeholder.style.height = '150px'
//         placeholder.style.display = 'flex'
//         placeholder.style.alignItems = 'center'
//         placeholder.style.justifyContent = 'center'
//         placeholder.style.backgroundColor = '#f0f0f0'
//         placeholder.style.color = '#666'
//         chartBox.appendChild(placeholder)
//       }
      
//       chartsGrid.appendChild(chartBox)
//     })
    
//     pdfContainer.appendChild(chartsGrid)
    
//     // 8. Add performance summary
//     const summaryTitle = document.createElement('h2')
//     summaryTitle.textContent = 'Performance Summary'
//     summaryTitle.style.fontSize = '18px'
//     summaryTitle.style.marginBottom = '15px'
//     pdfContainer.appendChild(summaryTitle)
    
//     const summaryBox = document.createElement('div')
//     summaryBox.style.backgroundColor = '#EFF6FF'
//     summaryBox.style.padding = '15px'
//     summaryBox.style.borderRadius = '5px'
//     summaryBox.style.marginBottom = '20px'
    
//     const summaryGrid = document.createElement('div')
//     summaryGrid.style.display = 'grid'
//     summaryGrid.style.gridTemplateColumns = '1fr 1fr'
//     summaryGrid.style.gap = '10px'
    
//     // Add summary items
//     const summaryItems = [
//       { 
//         title: 'Best for Turnaround Time',
//         value: getBestAlgorithm('avg_turnaround', true),
//         metric: getBestMetric('avg_turnaround', true).toFixed(2)
//       },
//       {
//         title: 'Best for Waiting Time',
//         value: getBestAlgorithm('avg_waiting', true),
//         metric: getBestMetric('avg_waiting', true).toFixed(2)
//       },
//       {
//         title: 'Best for CPU Utilization',
//         value: getBestAlgorithm('cpu_utilization'),
//         metric: `${getBestMetric('cpu_utilization').toFixed(2)}%`
//       },
//       {
//         title: 'Best for Total Time',
//         value: getBestAlgorithm('total_time', true),
//         metric: String(getBestMetric('total_time', true))
//       }
//     ]
    
//     summaryItems.forEach(item => {
//       const itemBox = document.createElement('div')
//       itemBox.style.backgroundColor = 'white'
//       itemBox.style.padding = '10px'
//       itemBox.style.borderRadius = '5px'
      
//       const itemTitle = document.createElement('p')
//       itemTitle.textContent = item.title
//       itemTitle.style.fontSize = '14px'
//       itemTitle.style.color = '#666'
//       itemTitle.style.margin = '0 0 5px 0'
//       itemBox.appendChild(itemTitle)
      
//       const itemValue = document.createElement('p')
//       itemValue.textContent = item.value
//       itemValue.style.fontSize = '16px'
//       itemValue.style.fontWeight = 'bold'
//       itemValue.style.color = '#2563eb'
//       itemValue.style.margin = '0 0 5px 0'
//       itemBox.appendChild(itemValue)
      
//       const itemMetric = document.createElement('p')
//       itemMetric.textContent = item.metric
//       itemMetric.style.fontSize = '12px'
//       itemMetric.style.color = '#6b7280'
//       itemMetric.style.margin = '0'
//       itemBox.appendChild(itemMetric)
      
//       summaryGrid.appendChild(itemBox)
//     })
    
//     summaryBox.appendChild(summaryGrid)
//     pdfContainer.appendChild(summaryBox)
    
//     // 9. Add recommendation
//     const recommendationTitle = document.createElement('h2')
//     recommendationTitle.textContent = 'Algorithm Recommendation'
//     recommendationTitle.style.fontSize = '18px'
//     recommendationTitle.style.marginBottom = '15px'
//     pdfContainer.appendChild(recommendationTitle)
    
//     const recommendationBox = document.createElement('div')
//     recommendationBox.style.backgroundColor = '#ECFDF5'
//     recommendationBox.style.padding = '15px'
//     recommendationBox.style.borderRadius = '5px'
    
//     const recommendationText = document.createElement('div')
//     recommendationText.innerHTML = getRecommendation()
//     recommendationText.style.color = '#374151'
    
//     recommendationBox.appendChild(recommendationText)
//     pdfContainer.appendChild(recommendationBox)
    
//     // Verify content
//     console.log("Content elements:", pdfContainer.childNodes.length)
    
//     // 10. Generate PDF using jsPDF directly for better control
//     console.log("Generating PDF...")
//     const opt = {
//       margin: 10,
//       filename: 'cpu-scheduler-report.pdf',
//       image: { 
//         type: 'jpeg',
//         quality: 1.0  // Maximum quality for images
//       },
//       html2canvas: { 
//         scale: 2,
//         useCORS: true,
//         allowTaint: true,
//         backgroundColor: '#FFFFFF',
//         imageTimeout: 5000,
//         logging: false,
//         removeContainer: true
//       },
//       jsPDF: { 
//         unit: 'mm', 
//         format: 'a4', 
//         orientation: 'portrait',
//         compress: true
//       }
//     }
    
//     // Use a timeout to ensure rendering is complete
//     await new Promise(resolve => setTimeout(resolve, 500))
//     await html2pdf()
//       .set(opt)
//       .from(pdfContainer)
//       .save()
//       .then(() => {
//         console.log("PDF generated successfully")
//       })
//       .catch(error => {
//         console.error("PDF generation error:", error)
//         alert("There was an error generating the PDF. Please try again.")
//       })
//   } catch (e) {
//     console.error("Error generating PDF:", e)
//     alert("Failed to generate PDF report. Please check console for details.")
//   } finally {
//     // Always clean up, even if there was an error
//     if (document.body.contains(pdfContainer)) {
//       document.body.removeChild(pdfContainer)
//     }
//   }
// }


// Socket handling with cleanup
onMounted(() => {
  // Remove any existing listeners to prevent duplicates
  socket.off('comparison_results')
  
  // Add listener for comparison results
  socket.on('comparison_results', async (data) => {
    console.log("Received comparison results")
    isLoading.value = false
    results.value = data
    
    // Give DOM time to update before creating charts
    setTimeout(async () => {
      await createAllCharts()
    }, 500)
  })
})

// Ensure we clean up properly
onBeforeUnmount(() => {
  socket.off('comparison_results')
  destroyAllCharts()
})

// Debounced watcher for results
let chartsCreationTimeout = null
watch(() => hasResults.value, (newVal) => {
  if (chartsCreationTimeout) {
    clearTimeout(chartsCreationTimeout)
  }
  
  if (newVal) {
    chartsCreationTimeout = setTimeout(async () => {
      await createAllCharts()
      chartsCreationTimeout = null
    }, 500)
  } else {
    destroyAllCharts()
  }
})

// Expose functions to template
defineExpose({
  runComparison
})
</script>

<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-bold">Scheduling Algorithms Comparison</h2>
      <!-- <div class="space-x-2">
        <button 
          @click="downloadReportAsPDF" 
          class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
          :disabled="!hasResults"
        >
          Download PDF
        </button>
      </div> -->

    </div>
    
    <div v-if="isLoading" class="text-center py-20">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
      <p class="text-gray-600">Running all scheduling algorithms...</p>
      <p class="text-sm text-gray-500">This may take a moment</p>
    </div>
    
    <div v-else-if="!hasResults" class="text-center py-20 text-gray-500">
      Click "Compare All Algorithms" to generate a comparative report
    </div>
    
    <div v-else id="report-content">
      <div class="mb-8">
        <h3 class="text-lg font-medium mb-4">Performance Metrics Comparison</h3>
        
        <!-- Summary Table -->
        <div class="overflow-x-auto">
          <table class="min-w-full bg-white border border-gray-200">
            <thead class="bg-gray-100">
              <tr>
                <th class="py-2 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Algorithm</th>
                <th class="py-2 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Turnaround</th>
                <th class="py-2 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Waiting</th>
                <th class="py-2 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPU Utilization</th>
                <th class="py-2 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Time</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="(result, algorithm) in results" :key="algorithm" class="hover:bg-gray-50">
                <td class="py-3 px-4">{{ algorithm }}</td>
                <td class="py-3 px-4">{{ result.metrics.avg_turnaround.toFixed(2) }}</td>
                <td class="py-3 px-4">{{ result.metrics.avg_waiting.toFixed(2) }}</td>
                <td class="py-3 px-4">{{ result.metrics.cpu_utilization.toFixed(2) }}%</td>
                <td class="py-3 px-4">{{ result.metrics.total_time }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Charts Section -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="text-md font-medium mb-2 text-center">Average Turnaround Time</h4>
          <div class="chart-container" style="height: 300px; position: relative">
            <canvas ref="turnaroundChart" id="turnaroundChart"></canvas>
          </div>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="text-md font-medium mb-2 text-center">Average Waiting Time</h4>
          <div class="chart-container" style="height: 300px; position: relative">
            <canvas ref="waitingChart" id="waitingChart"></canvas>
          </div>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="text-md font-medium mb-2 text-center">CPU Utilization</h4>
          <div class="chart-container" style="height: 300px; position: relative">
            <canvas ref="utilizationChart" id="utilizationChart"></canvas>
          </div>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="text-md font-medium mb-2 text-center">Total Execution Time</h4>
          <div class="chart-container" style="height: 300px; position: relative">
            <canvas ref="timeChart" id="timeChart"></canvas>
          </div>
        </div>
      </div>
      
      <!-- Best Performance Section -->
      <div class="bg-blue-50 p-4 rounded-lg mb-8">
        <h3 class="text-lg font-medium mb-4 text-blue-800">Performance Summary</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white p-3 rounded-md shadow-sm">
            <p class="text-sm text-gray-600">Best for Turnaround Time</p>
            <p class="text-lg font-bold text-blue-600">{{ getBestAlgorithm('avg_turnaround', true) }}</p>
            <p class="text-xs text-gray-500">{{ getBestMetric('avg_turnaround', true).toFixed(2) }}</p>
          </div>
          <div class="bg-white p-3 rounded-md shadow-sm">
            <p class="text-sm text-gray-600">Best for Waiting Time</p>
            <p class="text-lg font-bold text-blue-600">{{ getBestAlgorithm('avg_waiting', true) }}</p>
            <p class="text-xs text-gray-500">{{ getBestMetric('avg_waiting', true).toFixed(2) }}</p>
          </div>
          <div class="bg-white p-3 rounded-md shadow-sm">
            <p class="text-sm text-gray-600">Best for CPU Utilization</p>
            <p class="text-lg font-bold text-blue-600">{{ getBestAlgorithm('cpu_utilization') }}</p>
            <p class="text-xs text-gray-500">{{ getBestMetric('cpu_utilization').toFixed(2) }}%</p>
          </div>
          <div class="bg-white p-3 rounded-md shadow-sm">
            <p class="text-sm text-gray-600">Best for Total Time</p>
            <p class="text-lg font-bold text-blue-600">{{ getBestAlgorithm('total_time', true) }}</p>
            <p class="text-xs text-gray-500">{{ getBestMetric('total_time', true) }}</p>
          </div>
        </div>
      </div>
      
      <!-- Recommendation -->
      <div class="bg-green-50 p-4 rounded-lg">
        <h3 class="text-lg font-medium mb-2 text-green-800">Algorithm Recommendation</h3>
        <p class="text-gray-700" v-html="getRecommendation()"></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
canvas {
  width: 100% !important;
  height: 100% !important;
  position: absolute;
  top: 0;
  left: 0;
}

.chart-container {
  position: relative;
  height: 300px;
}
</style>