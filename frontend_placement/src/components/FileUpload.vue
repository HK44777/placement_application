<template>
  <div>
    <!-- Drag & Drop Zone -->
    <div 
      v-if="!file"
      class="file-upload-zone"
      :class="{ 'dragover': isDragover, 'is-invalid': error }"
      @dragover.prevent="isDragover = true"
      @dragleave.prevent="isDragover = false"
      @drop.prevent="handleDrop"
      @click="$refs.fileInput.click()"
    >
      <div class="mb-2">
        <svg xmlns="http://www.w3.org/-2000/svg" width="32" height="32" fill="currentColor" class="bi bi-cloud-arrow-up text-muted" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M7.646 5.146a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1-.708.708L8.5 6.707V10.5a.5.5 0 0 1-1 0V6.707L6.354 7.854a.5.5 0 1 1-.708-.708z"/>
          <path d="M4.406 3.342A5.53 5.53 0 0 1 8 2c2.69 0 4.923 2 5.166 4.579C14.758 6.804 16 8.137 16 9.773 16 11.569 14.502 13 12.687 13H3.781C1.708 13 0 11.366 0 9.318c0-1.763 1.266-3.223 2.942-3.593.143-.863.698-1.723 1.464-2.383m.653.757c-.757.653-1.153 1.44-1.153 2.056v.448l-.445.049C2.064 6.805 1 7.952 1 9.318 1 10.785 2.23 12 3.781 12h8.906C13.98 12 15 10.988 15 9.773c0-1.216-1.02-2.228-2.313-2.228h-.5v-.5C12.188 4.825 10.328 3 8 3a4.53 4.53 0 0 0-2.941 1.1z"/>
        </svg>
      </div>
      <p class="mb-0 text-muted fw-medium">{{ label || 'Click or drag file to upload' }}</p>
      <small class="text-muted" v-if="accept">Allowed: {{ accept.split(',').map(ext => ext.trim().toUpperCase().replace('.', '')).join(', ') }}</small>
      <input 
        type="file" 
        class="d-none" 
        ref="fileInput" 
        :accept="accept"
        @change="handleFileSelect"
      />
    </div>
    
    <!-- File Pill -->
    <div v-else class="file-pill">
      <div class="file-pill-info">
        <svg xmlns="http://www.w3.org/-2000/svg" width="24" height="24" fill="#dc3545" class="bi bi-file-earmark-pdf-fill" viewBox="0 0 16 16">
          <path d="M5.523 12.424q.21-.124.459-.238a8 8 0 0 1-.45.606c-.28.337-.498.516-.635.572q-.288.12-.497-.189c-.225-.333-.122-.92.21-1.503a9 9 0 0 1 .913-1.229 9 9 0 0 1 1.954-1.701 8 8 0 0 1 1.49-.687c.2-.07.414-.131.637-.182h.001c.214-.047.424-.092.627-.134.19-.038.384-.075.572-.113.125-.025.251-.05.378-.073.497-.095.96-.153 1.353-.16a1.4 1.4 0 0 1 .494.032c.114.034.204.091.266.166.088.106.126.241.111.413-.017.202-.102.433-.243.66a2.8 2.8 0 0 1-.504.605c-.328.283-.715.405-1.109.349a2.5 2.5 0 0 1-.958-.337 7 7 0 0 1-1.391-.849c-.611.517-1.22 1.144-1.796 1.839a24 24 0 0 0-1.427 1.951c-.327.525-.664 1.15-.961 1.769q-.185.385-.36.78Z"/>
          <path d="M9.293 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.707A1 1 0 0 0 13.293 4L10 .707A1 1 0 0 0 9.293 0M9.5 1.5v2a1 1 0 0 0 1 1h2zM5.5 8h.5a.5.5 0 0 1 0 1h-.5a.5.5 0 0 1 0-1m2.5 0h.5a.5.5 0 0 1 0 1h-.5a.5.5 0 0 1 0-1m2.5 0h.5a.5.5 0 0 1 0 1h-.5a.5.5 0 0 1 0-1"/>
        </svg>
        <div>
          <div class="file-pill-name" :title="file.name">{{ file.name }}</div>
          <div class="file-pill-size">{{ formatSize(file.size) }}</div>
        </div>
      </div>
      <button type="button" class="file-pill-remove" @click.prevent="removeFile" title="Remove file">
        <svg xmlns="http://www.w3.org/-2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">
          <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  label: String,
  accept: {
    type: String,
    default: '.pdf'
  },
  error: Boolean,
  modelValue: {
    type: File,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const file = ref(props.modelValue)
const isDragover = ref(false)

const handleFile = (newFile) => {
  if (newFile) {
    if (props.accept && !newFile.name.toLowerCase().endsWith(props.accept.toLowerCase().replace('.', ''))) {
      // Basic extension check
      return
    }
    file.value = newFile
    emit('update:modelValue', newFile)
  }
}

const handleFileSelect = (event) => {
  handleFile(event.target.files[0])
}

const handleDrop = (event) => {
  isDragover.value = false
  if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
    handleFile(event.dataTransfer.files[0])
  }
}

const removeFile = () => {
  file.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('update:modelValue', null)
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>
