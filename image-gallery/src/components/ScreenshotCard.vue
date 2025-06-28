<template>
  <div class="screenshot-card">
    <div class="screenshot-container">
      <img
        :src="props.screenshot.url"
        :alt="props.screenshot.name"
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
      <h3 class="screenshot-title">{{ props.screenshot.name }}</h3>
      
      <div class="screenshot-meta">
        <span class="screenshot-id">ID: {{ props.screenshot.id }}</span>
        <span class="strings-count">{{ props.screenshot.strings.length }} strings</span>
      </div>
      
      <div class="screenshot-tags" v-if="props.screenshot.tags.length > 0">
        <div class="tags-header">Tags:</div>
        <div class="tags-list">
          <span 
            v-for="tag in props.screenshot.tags" 
            :key="tag" 
            class="tag"
          >
            {{ tag }}
          </span>
        </div>
      </div>
      
      <div class="screenshot-dates">
        <small class="created-date">
          Created: {{ formatDate(props.screenshot.createdAt) }}
        </small>
        <small class="updated-date">
          Updated: {{ formatDate(props.screenshot.updatedAt) }}
        </small>
      </div>
    </div>
    
    <div class="screenshot-actions">
      <button @click="openFullscreen" class="action-btn">
        View Full Size
      </button>
      <button @click="copyUrl" class="action-btn secondary">
        Copy URL
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { CrowdinScreenshot } from '../services/crowdinService'

const props = defineProps<{
  screenshot: CrowdinScreenshot
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
  console.warn(`Failed to load screenshot: ${props.screenshot.url}`)
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString()
}

const openFullscreen = (): void => {
  window.open(props.screenshot.url, '_blank')
}

const copyUrl = async (): Promise<void> => {
  try {
    await navigator.clipboard.writeText(props.screenshot.url)
    console.log('Screenshot URL copied to clipboard')
  } catch (err) {
    console.error('Failed to copy URL:', err)
  }
}
</script>

<style scoped>
.screenshot-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.screenshot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.screenshot-container {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.screenshot-container img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.screenshot-container img.loaded {
  opacity: 1;
}

.screenshot-container img.error {
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
}

.screenshot-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.screenshot-id {
  font-weight: 600;
}

.strings-count {
  background: #3498db;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.screenshot-tags {
  margin-bottom: 10px;
}

.tags-header {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag {
  background: #ecf0f1;
  color: #2c3e50;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.screenshot-dates {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.8rem;
  color: #95a5a6;
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