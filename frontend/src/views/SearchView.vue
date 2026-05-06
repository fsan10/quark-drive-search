<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
    <header class="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-slate-100">
      <div class="max-w-3xl mx-auto px-4 py-3">
        <div class="flex items-center gap-3">
          <router-link to="/" class="shrink-0">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center">
                <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </router-link>
          <div class="flex-1 relative">
            <input
              v-model="keyword"
              @keyup.enter="doSearch"
              type="text"
              placeholder="搜索..."
              class="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300 transition-all"
            />
          </div>
          <button @click="doSearch" class="shrink-0 px-5 py-2 bg-slate-800 text-white text-sm font-medium rounded-xl hover:bg-slate-700 active:scale-95 transition-all">
            搜索
          </button>
        </div>
        <div class="flex items-center gap-2 mt-2.5 flex-wrap">
          <div v-if="categories.length" class="relative">
            <select
              v-model="selectedCategoryId"
              @change="doSearch"
              class="appearance-none text-xs text-slate-600 bg-white border border-slate-200 rounded-lg pl-3 pr-8 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300 cursor-pointer hover:border-slate-300 transition-colors min-w-[100px]"
            >
              <option value="">全部分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
            <svg class="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </div>
          <div class="relative">
            <select
              v-model="selectedLinkType"
              @change="doSearch"
              class="appearance-none text-xs text-slate-600 bg-white border border-slate-200 rounded-lg pl-3 pr-8 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300 cursor-pointer hover:border-slate-300 transition-colors min-w-[100px]"
            >
              <option value="">全部网盘</option>
              <option v-for="lt in linkTypes" :key="lt.value" :value="lt.value">{{ lt.label }}</option>
            </select>
            <svg class="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </div>
          <div class="relative">
            <select
              v-model="selectedFileSize"
              @change="doSearch"
              class="appearance-none text-xs text-slate-600 bg-white border border-slate-200 rounded-lg pl-3 pr-8 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300 cursor-pointer hover:border-slate-300 transition-colors min-w-[100px]"
            >
              <option value="">全部大小</option>
              <option value="lt100mb">小于 100MB</option>
              <option value="100mb-1gb">100MB - 1GB</option>
              <option value="1gb-10gb">1GB - 10GB</option>
              <option value="gt10gb">大于 10GB</option>
            </select>
            <svg class="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 py-6">
      <div v-if="searched" class="mb-5">
        <p v-if="total > 0" class="text-sm text-slate-400">
          找到 <span class="text-slate-600 font-medium">{{ total }}</span> 个结果
        </p>
        <p v-else class="text-sm text-slate-400">未找到与 "{{ lastKeyword }}" 相关的资源</p>
      </div>

      <div v-if="resources.length" class="space-y-3">
        <div
          v-for="item in resources"
          :key="item.id"
          class="group bg-white rounded-xl border border-slate-100 p-5 hover:border-slate-200 hover:shadow-sm transition-all duration-200"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-medium text-slate-800 truncate group-hover:text-blue-600 transition-colors">
                {{ item.title }}
              </h3>
              <p v-if="item.description" class="text-xs text-slate-400 mt-1 truncate">{{ item.description }}</p>
              <div class="flex items-center flex-wrap gap-2 mt-3">
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium"
                  :class="linkTypeClass(item.link_type)"
                >
                  {{ linkTypeLabel(item.link_type) }}
                </span>
                <span v-if="item.category_name" class="text-xs text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded">{{ item.category_name }}</span>
                <span v-if="item.file_size" class="text-xs text-slate-300">{{ item.file_size }}</span>
                <span v-if="item.extraction_code" class="text-xs text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                  提取码: {{ item.extraction_code }}
                </span>
              </div>
            </div>
            <button
              @click="copyLink(item.link, item.id)"
              class="shrink-0 px-3.5 py-1.5 text-xs font-medium rounded-lg border transition-all duration-200"
              :class="copiedId === item.id
                ? 'bg-green-50 border-green-200 text-green-600'
                : 'bg-slate-50 border-slate-200 text-slate-500 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600'"
            >
              {{ copiedId === item.id ? '已复制' : '复制链接' }}
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="searched && total === 0" class="text-center py-20">
        <svg class="w-12 h-12 text-slate-200 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-slate-300 text-sm">试试其他关键词</p>
      </div>

      <div v-if="loading" class="text-center py-12">
        <p class="text-sm text-slate-300">搜索中...</p>
      </div>

      <div v-if="totalPages > 1" class="flex justify-center mt-8 gap-1.5">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="goPage(p)"
          class="w-8 h-8 rounded-lg text-xs font-medium transition-all"
          :class="p === page
            ? 'bg-slate-800 text-white shadow-sm'
            : 'bg-white border border-slate-200 text-slate-500 hover:border-slate-300'"
        >
          {{ p }}
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { searchResources, getCategories } from '../api'

const route = useRoute()
const router = useRouter()

const keyword = ref('')
const lastKeyword = ref('')
const resources = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const searched = ref(false)
const loading = ref(false)
const copiedId = ref(null)
const selectedCategoryId = ref('')
const selectedLinkType = ref('')
const selectedFileSize = ref('')
const categories = ref([])

const linkTypes = [
  { value: 'quark', label: '夸克网盘' },
  { value: 'baidu', label: '百度网盘' },
  { value: 'alibaba', label: '阿里云盘' },
  { value: 'xunlei', label: '迅雷云盘' },
  { value: '123pan', label: '123云盘' },
  { value: 'lanzou', label: '蓝奏云' },
]

const totalPages = computed(() => Math.ceil(total.value / pageSize))

const linkTypeClass = (type) => {
  const map = {
    quark: 'bg-blue-50 text-blue-600',
    baidu: 'bg-blue-50 text-blue-500',
    alibaba: 'bg-orange-50 text-orange-600',
    xunlei: 'bg-emerald-50 text-emerald-600',
    '123pan': 'bg-red-50 text-red-500',
    lanzou: 'bg-violet-50 text-violet-600',
    other: 'bg-slate-50 text-slate-500',
  }
  return map[type] || map.other
}

const linkTypeLabel = (type) => {
  const map = {
    quark: '夸克网盘', baidu: '百度网盘', alibaba: '阿里云盘',
    xunlei: '迅雷云盘', '123pan': '123云盘', lanzou: '蓝奏云', other: '其他',
  }
  return map[type] || type
}

const doSearch = async () => {
  page.value = 1
  lastKeyword.value = keyword.value.trim()
  const query = {}
  if (lastKeyword.value) query.keyword = lastKeyword.value
  if (selectedCategoryId.value) query.category_id = selectedCategoryId.value
  if (selectedLinkType.value) query.link_type = selectedLinkType.value
  if (selectedFileSize.value) query.file_size_filter = selectedFileSize.value
  router.replace({ query })
  await fetchResults()
}

const fetchResults = async () => {
  if (!lastKeyword.value && !selectedCategoryId.value && !selectedLinkType.value && !selectedFileSize.value) return
  loading.value = true
  try {
    const params = {
      keyword: lastKeyword.value || undefined,
      page: page.value,
      page_size: pageSize,
    }
    if (selectedCategoryId.value) params.category_id = selectedCategoryId.value
    if (selectedLinkType.value) params.link_type = selectedLinkType.value
    if (selectedFileSize.value) params.file_size_filter = selectedFileSize.value
    const res = await searchResources(params)
    resources.value = res.data.items || []
    total.value = res.data.total || 0
    searched.value = true
  } catch {
    resources.value = []
    total.value = 0
    searched.value = true
  } finally {
    loading.value = false
  }
}

const goPage = (p) => {
  page.value = p
  fetchResults()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const copyLink = async (link, id) => {
  try {
    await navigator.clipboard.writeText(link)
    copiedId.value = id
    setTimeout(() => { copiedId.value = null }, 2000)
  } catch {}
}

onMounted(async () => {
  try {
    const catRes = await getCategories().catch(() => ({ data: [] }))
    categories.value = catRes.data || []
  } catch {}

  if (route.query.keyword) {
    keyword.value = route.query.keyword
    lastKeyword.value = route.query.keyword
  }
  if (route.query.category_id) {
    selectedCategoryId.value = route.query.category_id
  }
  if (route.query.link_type) {
    selectedLinkType.value = route.query.link_type
  }
  if (route.query.file_size_filter) {
    selectedFileSize.value = route.query.file_size_filter
  }
  if (lastKeyword.value || selectedCategoryId.value || selectedLinkType.value || selectedFileSize.value) {
    fetchResults()
  }
})

watch(() => route.query, (val) => {
  if (val.keyword && val.keyword !== keyword.value) {
    keyword.value = val.keyword
    lastKeyword.value = val.keyword
    page.value = 1
    fetchResults()
  }
  if (val.category_id !== undefined && val.category_id !== selectedCategoryId.value) {
    selectedCategoryId.value = val.category_id || ''
    page.value = 1
    fetchResults()
  }
  if (val.link_type !== undefined && val.link_type !== selectedLinkType.value) {
    selectedLinkType.value = val.link_type || ''
    page.value = 1
    fetchResults()
  }
  if (val.file_size_filter !== undefined && val.file_size_filter !== selectedFileSize.value) {
    selectedFileSize.value = val.file_size_filter || ''
    page.value = 1
    fetchResults()
  }
})
</script>
