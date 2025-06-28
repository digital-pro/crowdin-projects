<template>
  <div class="app">
    <header class="header">
      <h1>LEVANTE Core Task Assets Gallery</h1>
      <p class="subtitle">High-resolution assets from LEVANTE cognitive tasks</p>
      <p class="github-link">
        <small>
          📂 Source: 
          <a :href="currentSourceUrl" target="_blank" rel="noopener">
            {{ currentSourceText }}
          </a>
        </small>
      </p>
    </header>

    <!-- Tab Navigation -->
    <div class="tab-navigation">
      <button 
        @click="activeTab = 'assets'" 
        :class="{ active: activeTab === 'assets' }"
        class="tab-button"
      >
        📁 Assets
      </button>
      <button 
        @click="activeTab = 'github-screenshots'" 
        :class="{ active: activeTab === 'github-screenshots' }"
        class="tab-button"
      >
        📸 GitHub Screenshots
      </button>
      <button 
        @click="activeTab = 'crowdin-screenshots'" 
        :class="{ active: activeTab === 'crowdin-screenshots' }"
        class="tab-button"
      >
        🌐 Crowdin Screenshots
      </button>
    </div>

    <!-- Assets Tab Content -->
    <div v-if="activeTab === 'assets'" class="tab-content">
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

    <!-- GitHub Screenshots Tab Content -->
    <div v-if="activeTab === 'github-screenshots'" class="tab-content">
      <div class="controls">
        <div class="filter-controls">
          <div class="control-group">
            <label for="github-search">Search Screenshots:</label>
            <input
              id="github-search"
              type="text"
              v-model="githubScreenshotFilters.searchTerm"
              @input="applyGitHubScreenshotFilters"
              placeholder="Search by filename..."
            />
          </div>

          <div class="control-group">
            <label for="github-sort">Sort by:</label>
            <select id="github-sort" v-model="githubScreenshotSortOptions.field" @change="applyGitHubScreenshotSorting">
              <option value="filename">Filename</option>
              <option value="path">Path</option>
              <option value="size">File Size</option>
            </select>
            <button @click="toggleGitHubScreenshotSortDirection" class="sort-direction-btn">
              {{ githubScreenshotSortOptions.direction === 'asc' ? '↑' : '↓' }}
            </button>
          </div>
        </div>

        <div class="stats">
          <span>Showing {{ filteredGitHubScreenshots.length }} of {{ totalGitHubScreenshots }} screenshots</span>
        </div>
      </div>

      <div class="gallery" v-if="filteredGitHubScreenshots.length > 0">
        <GitHubScreenshotCard
          v-for="screenshot in filteredGitHubScreenshots"
          :key="screenshot.publicPath"
          :screenshot="screenshot"
        />
      </div>

      <div v-else-if="githubScreenshotsLoading" class="loading">
        Loading GitHub screenshots...
      </div>

      <div v-else class="no-results">
        <p>No screenshots found matching your criteria.</p>
        <div class="github-info">
          <h3>📸 GitHub Screenshots</h3>
          <p>Screenshots from the LEVANTE core-tasks repository Cypress tests.</p>
          <p>Source: <a href="https://github.com/levante-framework/core-tasks/tree/14337ff781dda568b50f09be5f636259bc917245/task-launcher/cypress/screenshots" target="_blank" rel="noopener">core-tasks/cypress/screenshots</a></p>
        </div>
      </div>
    </div>

    <!-- Crowdin Screenshots Tab Content -->
    <div v-if="activeTab === 'crowdin-screenshots'" class="tab-content">
      <div class="screenshots-info">
        <h3>🌐 Crowdin Screenshots</h3>
        <p>Browse screenshots from the LEVANTE translations project on Crowdin.</p>
        <div class="crowdin-setup">
          <h4>🔧 Setup Required</h4>
          <p>To access Crowdin screenshots, you'll need:</p>
          <ol>
            <li>Crowdin API access token</li>
            <li>Project identifier: <code>levantetranslations</code></li>
            <li>Configure API credentials in the app</li>
          </ol>
          <p>See <a href="https://crowdin.com/project/levantetranslations/screenshots" target="_blank" rel="noopener">Crowdin Screenshots</a> for direct access.</p>
          <p>For setup instructions, see <code>CROWDIN_SETUP.md</code></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ImageCard from './components/ImageCard.vue'
import ScreenshotCard from './components/ScreenshotCard.vue'
import GitHubScreenshotCard from './components/GitHubScreenshotCard.vue'
import ResolutionChart from './components/ResolutionChart.vue'
import type { ImageData, ImageMetadata, FilterOptions, SortOptions, ResolutionAnalysis } from './types/Image'
import type { CrowdinScreenshot } from './services/crowdinService'
import type { GitHubScreenshot } from './services/githubService'
import { crowdinService } from './services/crowdinService'
import { githubService } from './services/githubService'
import { isCrowdinConfigured } from './config/crowdin'

// Tab state
const activeTab = ref<'assets' | 'github-screenshots' | 'crowdin-screenshots'>('assets')

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

// GitHub screenshots data
const githubScreenshotsLoading = ref(false)
const githubScreenshots = ref<GitHubScreenshot[]>([])
const totalGitHubScreenshots = ref(0)

const githubScreenshotFilters = ref({
  searchTerm: ''
})

const githubScreenshotSortOptions = ref({
  field: 'filename',
  direction: 'asc'
})

// Crowdin screenshots data
const screenshotsLoading = ref(false)
const screenshots = ref<CrowdinScreenshot[]>([])
const totalScreenshots = ref(0)

const screenshotFilters = ref({
  searchTerm: ''
})

const screenshotSortOptions = ref({
  field: 'name',
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

// GitHub screenshots computed properties
const filteredGitHubScreenshots = computed(() => {
  let result = [...githubScreenshots.value]

  // Apply search filter
  if (githubScreenshotFilters.value.searchTerm) {
    const searchTerm = githubScreenshotFilters.value.searchTerm.toLowerCase()
    result = result.filter(screenshot => 
      screenshot.filename.toLowerCase().includes(searchTerm) ||
      screenshot.relativePath.toLowerCase().includes(searchTerm)
    )
  }

  // Apply sorting
  result.sort((a, b) => {
    const field = githubScreenshotSortOptions.value.field
    let aVal: string | number
    let bVal: string | number

    switch (field) {
      case 'filename':
        aVal = a.filename.toLowerCase()
        bVal = b.filename.toLowerCase()
        break
      case 'path':
        aVal = a.relativePath.toLowerCase()
        bVal = b.relativePath.toLowerCase()
        break
      case 'size':
        aVal = a.size
        bVal = b.size
        break
      default:
        aVal = String(a[field]).toLowerCase()
        bVal = String(b[field]).toLowerCase()
    }

    if (aVal < bVal) return githubScreenshotSortOptions.value.direction === 'asc' ? -1 : 1
    if (aVal > bVal) return githubScreenshotSortOptions.value.direction === 'asc' ? 1 : -1
    return 0
  })

  return result
})

// Crowdin screenshots computed properties
const filteredScreenshots = computed(() => {
  let result = [...screenshots.value]

  // Apply search filter
  if (screenshotFilters.value.searchTerm) {
    const searchTerm = screenshotFilters.value.searchTerm.toLowerCase()
    result = result.filter(screenshot => 
      screenshot.name.toLowerCase().includes(searchTerm) ||
      screenshot.tags.some(tag => tag.toLowerCase().includes(searchTerm))
    )
  }

  // Apply sorting
  result.sort((a, b) => {
    const field = screenshotSortOptions.value.field
    let aVal: string | number
    let bVal: string | number

    switch (field) {
      case 'name':
        aVal = a.name.toLowerCase()
        bVal = b.name.toLowerCase()
        break
      case 'createdAt':
        aVal = new Date(a.createdAt).getTime()
        bVal = new Date(b.createdAt).getTime()
        break
      case 'updatedAt':
        aVal = new Date(a.updatedAt).getTime()
        bVal = new Date(b.updatedAt).getTime()
        break
      case 'stringsCount':
        aVal = a.strings.length
        bVal = b.strings.length
        break
      default:
        aVal = String(a[field]).toLowerCase()
        bVal = String(b[field]).toLowerCase()
    }

    if (aVal < bVal) return screenshotSortOptions.value.direction === 'asc' ? -1 : 1
    if (aVal > bVal) return screenshotSortOptions.value.direction === 'asc' ? 1 : -1
    return 0
  })

  return result
})

// Source link computed properties
const currentSourceUrl = computed(() => {
  switch (activeTab.value) {
    case 'assets':
      return 'https://github.com/levante-framework/core-task-assets'
    case 'github-screenshots':
      return 'https://github.com/levante-framework/core-tasks/tree/14337ff781dda568b50f09be5f636259bc917245/task-launcher/cypress/screenshots'
    case 'crowdin-screenshots':
      return 'https://crowdin.com/project/levantetranslations/screenshots'
    default:
      return 'https://github.com/levante-framework/core-task-assets'
  }
})

const currentSourceText = computed(() => {
  switch (activeTab.value) {
    case 'assets':
      return 'levante-framework/core-task-assets'
    case 'github-screenshots':
      return 'core-tasks/cypress/screenshots'
    case 'crowdin-screenshots':
      return 'Crowdin Translations Project'
    default:
      return 'levante-framework/core-task-assets'
  }
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

// GitHub screenshots methods
const applyGitHubScreenshotFilters = (): void => {
  // Filters are reactive, so this just triggers reactivity
}

const applyGitHubScreenshotSorting = (): void => {
  // Sorting is reactive, so this just triggers reactivity
}

const toggleGitHubScreenshotSortDirection = (): void => {
  githubScreenshotSortOptions.value.direction = githubScreenshotSortOptions.value.direction === 'asc' ? 'desc' : 'asc'
}

const loadGitHubScreenshots = async (): Promise<void> => {
  githubScreenshotsLoading.value = true
  try {
    const allScreenshots = await githubService.getAllScreenshots()
    githubScreenshots.value = allScreenshots
    totalGitHubScreenshots.value = allScreenshots.length
  } catch (error) {
    console.error('Failed to load GitHub screenshots:', error)
  } finally {
    githubScreenshotsLoading.value = false
  }
}

// Crowdin screenshots methods
const applyScreenshotFilters = (): void => {
  // Filters are reactive, so this just triggers reactivity
}

const applyScreenshotSorting = (): void => {
  // Sorting is reactive, so this just triggers reactivity
}

const toggleScreenshotSortDirection = (): void => {
  screenshotSortOptions.value.direction = screenshotSortOptions.value.direction === 'asc' ? 'desc' : 'asc'
}

const loadScreenshots = async (): Promise<void> => {
  if (!isCrowdinConfigured()) {
    return
  }

  screenshotsLoading.value = true
  try {
    const allScreenshots = await crowdinService.getAllScreenshots()
    screenshots.value = allScreenshots
    totalScreenshots.value = allScreenshots.length
  } catch (error) {
    console.error('Failed to load screenshots:', error)
  } finally {
    screenshotsLoading.value = false
  }
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
  loadGitHubScreenshots()
  loadScreenshots()
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

/* Tab Navigation Styles */
.tab-navigation {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #ecf0f1;
  flex-wrap: wrap;
  gap: 5px;
}

.tab-button {
  padding: 12px 20px;
  margin: 0 2px;
  background: #f8f9fa;
  border: none;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  color: #7f8c8d;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
  min-width: 140px;
}

.tab-button:hover {
  background: #e9ecef;
  color: #495057;
}

.tab-button.active {
  background: white;
  color: #3498db;
  border-bottom-color: #3498db;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
}

.tab-content {
  min-height: 400px;
}

/* Screenshots Tab Styles */
.screenshots-info {
  text-align: center;
  padding: 50px 20px;
  max-width: 800px;
  margin: 0 auto;
}

.screenshots-info h3 {
  color: #2c3e50;
  font-size: 2rem;
  margin-bottom: 15px;
}

.screenshots-info p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin-bottom: 30px;
}

.crowdin-setup {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: left;
  margin-top: 20px;
}

.crowdin-setup h4 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 15px;
}

.crowdin-setup p {
  color: #7f8c8d;
  font-size: 1rem;
  margin-bottom: 15px;
}

.crowdin-setup ol {
  list-style-type: decimal;
  padding-left: 20px;
  margin-bottom: 15px;
}

.crowdin-setup li {
  color: #7f8c8d;
  font-size: 1rem;
  margin-bottom: 8px;
}

.crowdin-setup code {
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: #e74c3c;
}

.crowdin-setup a {
  color: #3498db;
  text-decoration: none;
}

.crowdin-setup a:hover {
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

  .tab-navigation {
    flex-direction: column;
    align-items: stretch;
  }

  .tab-button {
    border-radius: 8px;
    margin: 2px 0;
    min-width: auto;
    text-align: center;
  }

  .tab-button.active {
    border-bottom-color: transparent;
    border-left: 3px solid #3498db;
    box-shadow: none;
  }
}
</style> 