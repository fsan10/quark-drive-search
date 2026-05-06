import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('user_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const searchResources = (params) => api.get('/search', { params })
export const getHotSearches = () => api.get('/search/hot')
export const getCategories = () => api.get('/search/categories')

export const register = (data) => api.post('/auth/register', data)
export const login = (data) => api.post('/auth/login', data)
export const getMe = () => api.get('/auth/me')

export const getAnnouncements = () => api.get('/announcements')
export const getDonation = () => api.get('/donation')

export const createWish = (data) => api.post('/wishes', data)
export const getMyWishes = () => api.get('/wishes/my')
export const getMyReplies = () => api.get('/wishes/replies')
export const getUnreadCount = () => api.get('/wishes/unread-count')
export const markRepliesAsRead = () => api.post('/wishes/mark-read')

export default api
