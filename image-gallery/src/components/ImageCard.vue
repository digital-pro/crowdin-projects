<template>
  <div class="image-card">
    <div class="image-container">
      <img
        :src="props.image.publicPath"
        :alt="props.image.filename"
        @load="onImageLoad"
        @error="onImageError"
        :class="{ loaded: imageLoaded, error: imageError }"
      />
      <div v-if="!imageLoaded && !imageError" class="image-loading">
        Loading...
      </div>
      <div v-if="imageError" class="image-error">
        Failed to load image
      </div>
    </div>
    
    <div class="image-info">
      <h3 class="image-title">{{ props.image.filename }}</h3>
      <div class="image-meta">
        <span class="task-badge">{{ formatTaskName(props.image.taskName) }}</span>
        <span class="file-size">{{ formatFileSize(props.image.size) }}</span>
      </div>
      <div class="core-task-info" v-if="props.image.coreTaskName">
        <div class="core-task-badge" :class="{ 'implemented': props.image.hasTaskImplementation, 'not-implemented': !props.image.hasTaskImplementation }">
          <span class="core-task-label">Core Task:</span>
          <span class="core-task-name">{{ formatTaskName(props.image.coreTaskName) }}</span>
          <span class="implementation-status">
            {{ props.image.hasTaskImplementation ? '✅' : '❌' }}
          </span>
        </div>
        <div class="reference-status" v-if="props.image.isReferencedInTask">
          <small>🔗 Referenced in task code</small>
        </div>
      </div>
      
      <!-- Item-level information -->
      <div v-if="hasItemInfo" class="item-info">
        <div class="item-header">Item Details:</div>
        <div class="item-details">
          <span v-if="props.image.itemNumber !== null" class="item-tag item-number">
            #{{ props.image.itemNumber }}
          </span>
          <span v-if="props.image.variant" class="item-tag item-variant">
            {{ formatVariant(props.image.variant) }}
          </span>
          <span v-if="props.image.condition" class="item-tag item-condition">
            {{ formatCondition(props.image.condition) }}
          </span>
        </div>
        <div v-if="props.image.itemDescription" class="item-description">
          {{ props.image.itemDescription }}
        </div>
      </div>
      
      <div class="image-details">
        <small class="resolution" v-if="props.image.width && props.image.height">
          {{ props.image.width }} × {{ props.image.height }} px
        </small>
        <small class="last-modified">
          Modified: {{ formatDate(props.image.lastModified) }}
        </small>
      </div>
    </div>
    
    <div class="image-actions">
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
import { ref, computed } from 'vue'
import type { ImageData } from '../types/Image'

const props = defineProps<{
  image: ImageData
}>()

const imageLoaded = ref(false)
const imageError = ref(false)

// Computed properties
const hasItemInfo = computed(() => {
  return props.image.itemNumber !== null || 
         props.image.variant !== null || 
         props.image.condition !== null || 
         props.image.itemDescription !== null
})

const onImageLoad = (): void => {
  imageLoaded.value = true
  imageError.value = false
}

const onImageError = (): void => {
  imageLoaded.value = false
  imageError.value = true
  console.warn(`Failed to load image: ${props.image.publicPath}`)
}

const formatTaskName = (taskName: string): string => {
  return taskName.split('-').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString()
}

const formatVariant = (variant: string): string => {
  if (variant.length === 1) {
    return `Option ${variant.toUpperCase()}`
  }
  return variant.charAt(0).toUpperCase() + variant.slice(1)
}

const formatCondition = (condition: string): string => {
  return condition.charAt(0).toUpperCase() + condition.slice(1)
}

const openFullscreen = (): void => {
  window.open(props.image.publicPath, '_blank')
}

const copyPath = async (): Promise<void> => {
  try {
    await navigator.clipboard.writeText(props.image.relativePath)
    console.log('Path copied to clipboard')
  } catch (err) {
    console.error('Failed to copy path:', err)
  }
}
</script>

<style scoped>
.image-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.image-card:hover {
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
  color: #6c757d;
  font-size: 0.9rem;
}

.image-error {
  color: #dc3545;
}

.image-info {
  padding: 15px;
}

.image-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  word-break: break-word;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 10px;
}

.task-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.file-size {
  color: #6c757d;
  font-size: 0.8rem;
  white-space: nowrap;
}

.image-details {
  margin-bottom: 15px;
}

.resolution {
  color: #28a745;
  font-size: 0.75rem;
  font-weight: 500;
  display: block;
  margin-bottom: 4px;
}

.last-modified {
  color: #6c757d;
  font-size: 0.75rem;
}

.core-task-info {
  margin-bottom: 10px;
}

.core-task-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  margin-bottom: 4px;
}

.core-task-badge.implemented {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.core-task-badge.not-implemented {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.core-task-label {
  font-weight: 500;
}

.core-task-name {
  font-weight: 600;
}

.implementation-status {
  margin-left: auto;
}

.reference-status {
  color: #17a2b8;
  font-size: 0.7rem;
  font-style: italic;
}

.item-info {
  margin: 10px 0;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #007bff;
}

.item-header {
  font-size: 0.8rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 6px;
}

.item-details {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.item-tag {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 500;
}

.item-number {
  background: #e3f2fd;
  color: #1976d2;
}

.item-variant {
  background: #f3e5f5;
  color: #7b1fa2;
}

.item-condition {
  background: #e8f5e8;
  color: #388e3c;
}

.item-description {
  font-size: 0.8rem;
  color: #495057;
  font-style: italic;
}

.image-actions {
  display: flex;
  gap: 8px;
  padding: 0 15px 15px;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.action-btn:not(.secondary) {
  background: #3498db;
  color: white;
}

.action-btn:not(.secondary):hover {
  background: #2980b9;
}

.action-btn.secondary {
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.action-btn.secondary:hover {
  background: #e9ecef;
  color: #495057;
}

@media (max-width: 768px) {
  .image-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .image-actions {
    flex-direction: column;
  }
}
</style> 