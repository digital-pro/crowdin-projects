<template>
  <div class="app">
    <header class="header">
      <h1>LEVANTE Core Task Assets Gallery</h1>
      <p class="subtitle">High-resolution assets from LEVANTE cognitive tasks</p>
      <p class="github-link">
        <small>
          📂 Source: 
          <a href="https://github.com/levante-framework/core-task-assets" target="_blank" rel="noopener">
            levante-framework/core-task-assets
          </a>
        </small>
      </p>
    </header>

    <!-- Resolution Chart (hidden for now) -->
    <!-- <ResolutionChart 
      v-if="resolutionAnalysis" 
      :resolutionAnalysis="resolutionAnalysis" 
    /> -->

    <div class="controls">
      <div class="filter-controls">
        <div class="control-group">
          <label for="task-filter">Filter by Task:</label>
          <select id="task-filter" v-model="filters.task" @change="applyFilters">
            <option value="">All Tasks</option>
            <option v-for="task in tasks" :key="task" :value="task">
              {{ formatTaskName(task) }} ({{ getTaskImageCount(task) }})
            </option>
          </select>
        </div>

        <div class="control-group">
          <label for="search">Search Images:</label>
          <input
            id="search"
            type="text"
            v-model="filters.searchTerm"
            @input="applyFilters"
            placeholder="Search by filename..."
          />
        </div>

        <div class="control-group">
          <label for="implementation-filter">Implementation Status:</label>
          <select id="implementation-filter" v-model="filters.implementationStatus" @change="applyFilters">
            <option value="">All Images</option>
            <option value="implemented">Has Core-Task Implementation</option>
            <option value="not-implemented">No Core-Task Implementation</option>
            <option value="referenced">Referenced in Task Code</option>
          </select>
        </div>

        <div class="control-group">
          <label for="sort-field">Sort by:</label>
          <select id="sort-field" v-model="sortOptions.field" @change="applySorting">
            <option value="filename">Filename</option>
            <option value="taskName">Task Name</option>
            <option value="size">File Size</option>
            <option value="lastModified">Last Modified</option>
          </select>
          <button @click="toggleSortDirection" class="sort-direction-btn">
            {{ sortOptions.direction === 'asc' ? '↑' : '↓' }}
          </button>
        </div>
      </div>

      <div class="stats">
        <span>Showing {{ filteredImages.length }} of {{ totalImages }} images</span>
      </div>
    </div>

    <div class="gallery" v-if="filteredImages.length > 0">
      <ImageCard
        v-for="image in filteredImages"
        :key="image.publicPath"
        :image="image"
      />
    </div>

    <div v-else-if="loading" class="loading">
      Loading images...
    </div>

    <div v-else class="no-results">
      <p>No images found matching your criteria.</p>
      <div class="github-info">
        <h3>🔧 Setup Required</h3>
        <p>If no images are loading, you may need to:</p>
        <ol>
          <li>Upload your assets to a public GitHub repository</li>
          <li>Update the GitHub URL in <code>config.js</code></li>
          <li>Regenerate the metadata with <code>node generate-image-metadata.js</code></li>
        </ol>
        <p>See <code>GITHUB_SETUP.md</code> for detailed instructions.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ImageCard from './components/ImageCard.vue'
import ResolutionChart from './components/ResolutionChart.vue'
import type { ImageData, ImageMetadata, FilterOptions, SortOptions, ResolutionAnalysis } from './types/Image'

// Reactive data
const loading = ref(true)
const images = ref<ImageData[]>([])
const tasks = ref<string[]>([])
const totalImages = ref(0)
const resolutionAnalysis = ref<ResolutionAnalysis | null>(null)

const filters = ref<FilterOptions>({
  task: '',
  searchTerm: '',
  implementationStatus: ''
})

const sortOptions = ref<SortOptions>({
  field: 'filename',
  direction: 'asc'
})

// Computed properties
const filteredImages = computed(() => {
  let result = [...images.value]

  // Apply task filter
  if (filters.value.task) {
    result = result.filter(img => img.taskName === filters.value.task)
  }

  // Apply search filter
  if (filters.value.searchTerm) {
    const searchTerm = filters.value.searchTerm.toLowerCase()
    result = result.filter(img => 
      img.filename.toLowerCase().includes(searchTerm) ||
      img.taskName.toLowerCase().includes(searchTerm) ||
      (img.coreTaskName && img.coreTaskName.toLowerCase().includes(searchTerm))
    )
  }

  // Apply implementation status filter
  if (filters.value.implementationStatus) {
    switch (filters.value.implementationStatus) {
      case 'implemented':
        result = result.filter(img => img.hasTaskImplementation)
        break
      case 'not-implemented':
        result = result.filter(img => !img.hasTaskImplementation)
        break
      case 'referenced':
        result = result.filter(img => img.isReferencedInTask)
        break
    }
  }

  // Apply sorting
  result.sort((a, b) => {
    const field = sortOptions.value.field
    let aVal: string | number = a[field]
    let bVal: string | number = b[field]

    if (field === 'size') {
      aVal = a.size
      bVal = b.size
    } else if (field === 'lastModified') {
      aVal = new Date(a.lastModified).getTime()
      bVal = new Date(b.lastModified).getTime()
    } else {
      aVal = String(aVal).toLowerCase()
      bVal = String(bVal).toLowerCase()
    }

    if (aVal < bVal) return sortOptions.value.direction === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOptions.value.direction === 'asc' ? 1 : -1
    return 0
  })

  return result
})

// Methods
const formatTaskName = (taskName: string): string => {
  return taskName.split('-').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const getTaskImageCount = (taskName: string): number => {
  return images.value.filter(img => img.taskName === taskName).length
}

const applyFilters = (): void => {
  // Filters are reactive, so this just triggers reactivity
}

const applySorting = (): void => {
  // Sorting is reactive, so this just triggers reactivity
}

const toggleSortDirection = (): void => {
  sortOptions.value.direction = sortOptions.value.direction === 'asc' ? 'desc' : 'asc'
}

const loadImageMetadata = async (): Promise<void> => {
  try {
    const response = await fetch('/imageMetadata.json')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const metadata: ImageMetadata = await response.json()
    
    images.value = metadata.images
    tasks.value = metadata.tasks
    totalImages.value = metadata.totalImages
    resolutionAnalysis.value = metadata.resolutionAnalysis || null
    loading.value = false
  } catch (error) {
    console.error('Failed to load image metadata:', error)
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadImageMetadata()
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.github-link {
  margin-top: 10px;
}

.github-link a {
  color: #3498db;
  text-decoration: none;
}

.github-link a:hover {
  text-decoration: underline;
}

.controls {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.filter-controls {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  align-items: end;
  margin-bottom: 15px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.control-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.control-group select,
.control-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.sort-direction-btn {
  padding: 8px 12px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-left: 5px;
}

.sort-direction-btn:hover {
  background: #2980b9;
}

.stats {
  text-align: right;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.loading {
  text-align: center;
  padding: 50px;
  font-size: 1.2rem;
  color: #7f8c8d;
}

.no-results {
  text-align: center;
  padding: 50px;
  color: #7f8c8d;
}

.github-info {
  margin-top: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.github-info h3 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 10px;
}

.github-info p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.github-info ol {
  list-style-type: decimal;
  padding-left: 20px;
  margin-bottom: 10px;
}

.github-info li {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin-bottom: 5px;
}

@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .gallery {
    grid-template-columns: 1fr;
  }
  
  .header h1 {
    font-size: 2rem;
  }
}
</style> 