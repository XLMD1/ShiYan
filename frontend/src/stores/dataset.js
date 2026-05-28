import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useDatasetStore = defineStore('dataset', () => {
  const datasets = ref([])
  const currentDataset = ref(null)
  const previewData = ref(null)
  const loading = ref(false)
  const uploading = ref(false)

  async function fetchDatasets() {
    loading.value = true
    try {
      const { data } = await api.get('/datasets/')
      datasets.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchDataset(id) {
    const { data } = await api.get(`/datasets/${id}/`)
    currentDataset.value = data
    return data
  }

  async function uploadFile(file, onProgress) {
    uploading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await api.post('/datasets/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (onProgress && e.total) {
            onProgress(Math.round((e.loaded * 100) / e.total))
          }
        },
      })
      currentDataset.value = data
      return data
    } finally {
      uploading.value = false
    }
  }

  async function previewDataset(id, page = 1, pageSize = 100) {
    const { data } = await api.get(`/datasets/${id}/preview/`, {
      params: { page, page_size: pageSize },
    })
    previewData.value = data
    return data
  }

  async function deleteDataset(id) {
    await api.delete(`/datasets/${id}/delete/`)
    datasets.value = datasets.value.filter((d) => d.id !== id)
  }

  function getExportUrl(id, format = 'csv') {
    const token = localStorage.getItem('access_token')
    return `/api/datasets/${id}/export/?file_type=${format}&token=${token}`
  }

  async function fetchData(source) {
    const { data } = await api.post('/datasets/fetch/', { source })
    currentDataset.value = data
    return data
  }

  return {
    datasets,
    currentDataset,
    previewData,
    loading,
    uploading,
    fetchDatasets,
    fetchDataset,
    uploadFile,
    previewDataset,
    deleteDataset,
    getExportUrl,
    fetchData,
  }
})