<template>
  <div class="github-screenshot-card">
    <div class="image-container">
      <img
        :src="props.screenshot.publicPath"
        :alt="props.screenshot.filename"
        @load="onImageLoad"
        @error="onImageError"
        :class="{ loaded: imageLoaded, error: imageError }"
      />
      <div v-if="!imageLoaded && !imageError" class="image-loading">
        Loading...
      </div>
      <div v-if="imageError" class="image-error">
        Failed to load screenshot
      </div>
    </div>
    
    <div class="screenshot-info">
      <h3 class="screenshot-title">{{ props.screenshot.filename }}</h3>
      
      <div class="screenshot-meta">
        <span class="file-path">{{ formatPath(props.screenshot.relativePath) }}</span>
        <span class="file-size">{{ formatFileSize(props.screenshot.size) }}</span>
      </div>
      
      <div class="screenshot-details">
        <small class="github-link">
          <a :href="props.screenshot.githubUrl" target="_blank" rel="noopener">
            View on GitHub
          </a>
        </small>
      </div>
    </div>
    
    <div class="screenshot-actions">
      <button @click="openFullscreen" class="action-btn">
        View Full Size
      </button>
      <button @click="copyPath" class="action-btn secondary">
        Copy Path
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { GitHubScreenshot } from '../services/githubService'

const props = defineProps<{
  screenshot: GitHubScreenshot
}>()

const imageLoaded = ref(false)
const imageError = ref(false)

const onImageLoad = (): void => {
  imageLoaded.value = true
  imageError.value = false
}

const onImageError = (): void => {
  imageLoaded.value = false
  imageError.value = true
  console.warn(`Failed to load GitHub screenshot: ${props.screenshot.publicPath}`)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatPath = (path: string): string => {
  // Show the directory structure in a more readable format
  return path.split('/').slice(0, -1).join(' / ') || 'Root'
}

const openFullscreen = (): void => {
  window.open(props.screenshot.publicPath, '_blank')
}

const copyPath = async (): Promise<void> => {
  try {
    await navigator.clipboard.writeText(props.screenshot.relativePath)
    console.log('GitHub screenshot path copied to clipboard')
  } catch (err) {
    console.error('Failed to copy path:', err)
  }
}
</script>

<style scoped>
.github-screenshot-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.github-screenshot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.image-container {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-container img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-container img.loaded {
  opacity: 1;
}

.image-container img.error {
  display: none;
}

.image-loading,
.image-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #7f8c8d;
  font-size: 0.9rem;
}

.image-error {
  color: #e74c3c;
}

.screenshot-info {
  padding: 15px;
}

.screenshot-title {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
  color: #2c3e50;
  font-weight: 600;
  word-break: break-word;
}

.screenshot-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.file-path {
  font-weight: 500;
  color: #34495e;
  max-width: 60%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  background: #3498db;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  white-space: nowrap;
}

.screenshot-details {
  margin-bottom: 10px;
}

.github-link a {
  color: #3498db;
  text-decoration: none;
  font-size: 0.9rem;
}

.github-link a:hover {
  text-decoration: underline;
}

.screenshot-actions {
  padding: 15px;
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.action-btn:first-child {
  background: #3498db;
  color: white;
}

.action-btn:first-child:hover {
  background: #2980b9;
}

.action-btn.secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.action-btn.secondary:hover {
  background: #d5dbdb;
}
</style> 