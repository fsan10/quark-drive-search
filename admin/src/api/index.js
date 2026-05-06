import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/admin/login'
    } else if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    }
    return Promise.reject(error)
  }
)

export const login = (data) => api.post('/auth/admin-login', data)
export const getMe = () => api.get('/auth/me')

export const getResources = (params) => api.get('/admin/resources', { params })
export const createResource = (data) => api.post('/admin/resources', data)
export const updateResource = (id, data) => api.put(`/admin/resources/${id}`, data)
export const deleteResource = (id) => api.delete(`/admin/resources/${id}`)
export const batchCreateResources = (data) => api.post('/admin/resources/batch', data)
export const batchDeleteResources = (ids) => api.post('/admin/resources/batch-delete', { ids })
export const batchUpdateVisibility = (ids, is_visible) => api.post('/admin/resources/batch-visibility', { ids, is_visible })
export const toggleResourceVisibility = (id, is_visible) => api.put(`/admin/resources/${id}/visibility`, null, { params: { is_visible } })

export const aiParse = (data) => api.post('/admin/ai/parse', data)
export const aiBatchParse = (data) => api.post('/admin/ai/parse-batch', data)
export const aiParseAndSave = (data) => api.post('/admin/ai/parse-and-save', data)
export const getAvailableModels = () => api.get('/admin/models/available')

export const importCsv = (formData) => api.post('/admin/resources/import/csv', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})

export const getCategories = (params) => api.get('/admin/categories', { params })
export const createCategory = (data) => api.post('/admin/categories', data)
export const updateCategory = (id, data) => api.put(`/admin/categories/${id}`, data)
export const deleteCategory = (id) => api.delete(`/admin/categories/${id}`)

export const getUsers = (params) => api.get('/admin/users', { params })
export const updateUser = (id, data) => api.put(`/admin/users/${id}`, data)
export const deleteUser = (id) => api.delete(`/admin/users/${id}`)
export const batchDeleteUsers = (ids) => api.post('/admin/users/batch-delete', { ids })
export const verifyUserPassword = (id, password) => api.post(`/admin/users/${id}/verify-password`, { password })
export const verifyCurrentPassword = (password) => api.post('/admin/users/verify-current-password', { password })

export const getStats = () => api.get('/admin/stats/overview')

export const getAnnouncements = () => api.get('/admin/announcements')
export const createAnnouncement = (data) => api.post('/admin/announcements', data)
export const updateAnnouncement = (id, data) => api.put(`/admin/announcements/${id}`, data)
export const deleteAnnouncement = (id) => api.delete(`/admin/announcements/${id}`)
export const batchDeleteAnnouncements = (ids) => api.post('/admin/announcements/batch-delete', { ids })

export const getWishes = (params) => api.get('/admin/wishes', { params })
export const replyWish = (id, data) => api.post(`/admin/wishes/${id}/reply`, data)
export const deleteWish = (id) => api.delete(`/admin/wishes/${id}`)
export const batchDeleteWishes = (ids) => api.post('/admin/wishes/batch-delete', { ids })

export const getDonation = () => api.get('/admin/donation')
export const updateDonation = (data) => api.put('/admin/donation', data)

export const uploadImage = (formData) => api.post('/admin/upload/image', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})

export default api
