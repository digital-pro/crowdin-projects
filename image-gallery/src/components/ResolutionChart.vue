<template>
  <div class="resolution-chart">
    <h3>📊 Resolution Distribution</h3>
    <div class="chart-description">
      <p>Number of images by horizontal resolution ({{ resolutionAnalysis.totalWithDimensions }} images with dimension data)</p>
      <p class="chart-note">
        <strong>Note:</strong> Purple bars indicate resolutions shared by multiple tasks. 
        The large 1200px bar includes {{ get1200pxBreakdown() }} images.
      </p>
    </div>
    
    <div class="chart-container">
      <svg :width="chartWidth" :height="chartHeight" class="chart-svg">
        <!-- Y-axis labels -->
        <g class="y-axis">
          <text 
            v-for="tick in yAxisTicks" 
            :key="tick"
            :x="margin.left - 10" 
            :y="getYPosition(tick) + 4"
            text-anchor="end"
            class="axis-label"
          >
            {{ tick }}
          </text>
        </g>
        
        <!-- X-axis labels -->
        <g class="x-axis">
          <text 
            v-for="(bucket, index) in displayBuckets" 
            :key="bucket.width"
            :x="getXPosition(index) + barWidth / 2" 
            :y="chartHeight - margin.bottom + 15"
            text-anchor="middle"
            class="axis-label"
            :class="{ 'rotated': displayBuckets.length > 15 }"
          >
            {{ bucket.width }}px
          </text>
        </g>
        
        <!-- Bars -->
        <g class="bars">
          <rect
            v-for="(bucket, index) in displayBuckets"
            :key="bucket.width"
            :x="getXPosition(index)"
            :y="getYPosition(bucket.count)"
            :width="barWidth"
            :height="getBarHeight(bucket.count)"
            :class="getBarClass(bucket)"
            @mouseover="showTooltip($event, bucket)"
            @mouseout="hideTooltip"
          />
        </g>
        
        <!-- Grid lines -->
        <g class="grid">
          <line
            v-for="tick in yAxisTicks"
            :key="`grid-${tick}`"
            :x1="margin.left"
            :y1="getYPosition(tick)"
            :x2="chartWidth - margin.right"
            :y2="getYPosition(tick)"
            class="grid-line"
          />
        </g>
      </svg>
    </div>
    
    <!-- Tooltip -->
    <div 
      v-if="tooltip.visible && tooltip.data" 
      class="tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <strong>{{ tooltip.data.width }}px width</strong><br>
      {{ tooltip.data.count }} images total<br>
      <small>
        <span v-if="tooltip.data.tasks.length === 1">
          Task: {{ formatTaskName(tooltip.data.tasks[0]) }}
        </span>
        <span v-else>
          Tasks: {{ tooltip.data.tasks.map(t => formatTaskName(t)).join(', ') }}
        </span>
      </small>
    </div>
    
    <!-- Legend -->
    <div class="legend">
      <div class="legend-item">
        <div class="legend-color trog"></div>
        <span>TROG only</span>
      </div>
      <div class="legend-item">
        <div class="legend-color theory-of-mind"></div>
        <span>Theory of Mind only</span>
      </div>
      <div class="legend-item">
        <div class="legend-color mental-rotation"></div>
        <span>Mental Rotation only</span>
      </div>
      <div class="legend-item">
        <div class="legend-color mixed"></div>
        <span>Multiple tasks</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ResolutionAnalysis, ResolutionBucket } from '../types/Image'

interface Props {
  resolutionAnalysis: ResolutionAnalysis
}

const props = defineProps<Props>()

// Chart dimensions
const chartWidth = 800
const chartHeight = 400
const margin = { top: 20, right: 20, bottom: 60, left: 60 }

// Tooltip state
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  data: null as ResolutionBucket | null
})

// Computed properties
const displayBuckets = computed(() => {
  // Show only buckets with 2+ images to reduce clutter
  return props.resolutionAnalysis.resolutionBuckets
    .filter(bucket => bucket.count >= 2)
    .slice(0, 30) // Limit to top 30 for readability
})

const maxCount = computed(() => {
  return Math.max(...displayBuckets.value.map(b => b.count))
})

const yAxisTicks = computed(() => {
  const max = maxCount.value
  const tickCount = 5
  const step = Math.ceil(max / tickCount)
  return Array.from({ length: tickCount + 1 }, (_, i) => i * step)
})

const barWidth = computed(() => {
  const availableWidth = chartWidth - margin.left - margin.right
  return Math.max(10, availableWidth / displayBuckets.value.length - 2)
})

// Methods
const getXPosition = (index: number): number => {
  const availableWidth = chartWidth - margin.left - margin.right
  const spacing = availableWidth / displayBuckets.value.length
  return margin.left + index * spacing
}

const getYPosition = (count: number): number => {
  const availableHeight = chartHeight - margin.top - margin.bottom
  const ratio = count / maxCount.value
  return margin.top + availableHeight * (1 - ratio)
}

const getBarHeight = (count: number): number => {
  const availableHeight = chartHeight - margin.top - margin.bottom
  return (count / maxCount.value) * availableHeight
}

const getBarClass = (bucket: ResolutionBucket): string => {
  if (bucket.tasks.length > 1) return 'bar mixed'
  if (bucket.tasks.includes('TROG')) return 'bar trog'
  if (bucket.tasks.includes('theory-of-mind')) return 'bar theory-of-mind'
  if (bucket.tasks.includes('mental-rotation')) return 'bar mental-rotation'
  return 'bar default'
}

const showTooltip = (event: MouseEvent, bucket: ResolutionBucket): void => {
  tooltip.value = {
    visible: true,
    x: event.pageX + 10,
    y: event.pageY - 10,
    data: bucket
  }
}

const hideTooltip = (): void => {
  tooltip.value.visible = false
}

const formatTaskName = (taskName: string): string => {
  return taskName.split('-').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const get1200pxBreakdown = (): string => {
  const bucket1200 = props.resolutionAnalysis.resolutionBuckets.find(b => b.width === 1200)
  if (!bucket1200) return 'unknown'
  return `${bucket1200.count} (${bucket1200.tasks.map(t => formatTaskName(t)).join(', ')})`
}
</script>

<style scoped>
.resolution-chart {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.resolution-chart h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.chart-description {
  color: #7f8c8d;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.chart-container {
  overflow-x: auto;
}

.chart-svg {
  display: block;
  margin: 0 auto;
}

.axis-label {
  font-size: 12px;
  fill: #666;
}

.axis-label.rotated {
  transform-origin: center;
  transform: rotate(-45deg);
}

.grid-line {
  stroke: #e0e0e0;
  stroke-width: 1;
}

.bar {
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.bar:hover {
  opacity: 0.8;
}

.bar.trog {
  fill: #3498db;
}

.bar.theory-of-mind {
  fill: #e74c3c;
}

.bar.mental-rotation {
  fill: #2ecc71;
}

.bar.mixed {
  fill: #9b59b6;
}

.bar.default {
  fill: #95a5a6;
}

.tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 1000;
  max-width: 200px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 20px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 2px;
}

.legend-color.trog {
  background-color: #3498db;
}

.legend-color.theory-of-mind {
  background-color: #e74c3c;
}

.legend-color.mental-rotation {
  background-color: #2ecc71;
}

.legend-color.mixed {
  background-color: #9b59b6;
}

@media (max-width: 768px) {
  .chart-container {
    overflow-x: scroll;
  }
  
  .legend {
    flex-direction: column;
    align-items: center;
  }
}
</style> 