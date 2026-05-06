<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
    <header class="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-slate-100">
      <div class="max-w-3xl mx-auto px-4 py-3">
        <div class="flex items-center gap-3">
          <router-link to="/" class="shrink-0">
            <div class="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center">
              <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </router-link>
          <div class="flex items-center gap-2 text-sm">
            <router-link to="/" class="text-slate-400 hover:text-slate-600 transition">首页</router-link>
            <span class="text-slate-200">/</span>
            <span class="text-slate-600 font-medium">{{ categoryName }}</span>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 py-6">
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
              <div class="flex items-center gap-2 mt-3">
                <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-blue-50 text-blue-600">
                  {{ linkTypeLabel(item.link_type) }}
                </span>
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

      <div v-else class="text-center py-20">
        <svg class="w-12 h-12 text-slate-200 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
        </svg>
        <p class="text-slate-300 text-sm">该分类暂无资源</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { searchResources } from '../api'

const route = useRoute()
const categoryName = ref('分类')
const resources = ref([])
const copiedId = ref(null)

const linkTypeLabel = (type) => {
  const map = {
    quark: '夸克网盘', baidu: '百度网盘', alibaba: '阿里云盘',
    xunlei: '迅雷云盘', '123pan': '123云盘', lanzou: '蓝奏云', other: '其他',
  }
  return map[type] || type
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
    const res = await searchResources({ category_id: route.params.id, page: 1, page_size: 100, keyword: '' })
    resources.value = res.data.items || []
    categoryName.value = resources.value.length && resources.value[0].category_name
      ? resources.value[0].category_name : '分类'
  } catch {}
})
</script>
