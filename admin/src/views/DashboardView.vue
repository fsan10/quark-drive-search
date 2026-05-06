<template>
  <div>
    <el-row :gutter="20" class="panel-group">
      <el-col :xs="12" :sm="6" v-for="card in statCards" :key="card.label">
        <div class="card-panel" @click="card.action">
          <div class="card-panel-icon-wrapper" :class="card.iconClass">
            <el-icon :size="24"><component :is="card.iconComp" /></el-icon>
          </div>
          <div class="card-panel-description">
            <div class="card-panel-text">{{ card.label }}</div>
            <div class="card-panel-num">{{ card.value }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="16">
        <div class="chart-wrapper">
          <div class="section-header">最近搜索</div>
          <div v-if="recentSearches.length" class="search-list">
            <div v-for="(item, i) in recentSearches" :key="i" class="search-item">
              <div class="search-item-left">
                <span class="search-rank" :class="{ top: i < 3 }">{{ i + 1 }}</span>
                <span class="search-keyword">{{ item.keyword }}</span>
              </div>
              <div class="search-item-right">
                <span class="search-count">{{ item.result_count }} 条</span>
                <span class="search-time">{{ item.time }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">暂无搜索记录</div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="8">
        <div class="chart-wrapper">
          <div class="section-header">快捷操作</div>
          <div class="quick-actions">
            <router-link v-for="action in quickActions" :key="action.to" :to="action.to" class="quick-action-item">
              <el-icon :size="20" :color="action.color"><component :is="action.iconComp" /></el-icon>
              <span class="quick-action-text">{{ action.title }}</span>
            </router-link>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStats } from '../api'
import { Document, MagicStick, Upload, Folder, User, Search, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()
const stats = ref({})
const recentSearches = ref([])

const statCards = computed(() => [
  { label: '资源总数', value: stats.value.total_resources || 0, iconComp: Document, iconClass: 'icon-blue', action: () => router.push('/resources') },
  { label: '用户总数', value: stats.value.total_users || 0, iconComp: User, iconClass: 'icon-green', action: () => router.push('/users') },
  { label: '搜索总量', value: stats.value.total_searches || 0, iconComp: Search, iconClass: 'icon-purple', action: () => {} },
  { label: '今日搜索', value: stats.value.today_searches || 0, iconComp: TrendCharts, iconClass: 'icon-orange', action: () => {} },
])

const quickActions = [
  { to: '/ai-import', title: 'AI 智能导入', iconComp: MagicStick, color: '#409EFF' },
  { to: '/csv-import', title: 'CSV 批量导入', iconComp: Upload, color: '#67C23A' },
  { to: '/resources', title: '资源管理', iconComp: Document, color: '#E6A23C' },
  { to: '/categories', title: '分类管理', iconComp: Folder, color: '#F56C6C' },
]

onMounted(async () => {
  try {
    const res = await getStats()
    stats.value = res.data
  } catch {}
})
</script>

<style scoped>
.panel-group {
  margin-bottom: 20px;
}

.card-panel {
  height: 108px;
  cursor: pointer;
  font-size: 12px;
  position: relative;
  overflow: hidden;
  color: #666;
  background: #fff;
  box-shadow: 4px 4px 40px rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  padding: 0 20px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.card-panel:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-panel:hover .card-panel-icon-wrapper {
  color: #fff;
}

.card-panel:hover .icon-blue { background: #409EFF; }
.card-panel:hover .icon-green { background: #67C23A; }
.card-panel:hover .icon-purple { background: #7c4dff; }
.card-panel:hover .icon-orange { background: #e6a23c; }

.card-panel-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.38s ease-out;
  margin-right: 20px;
}

.icon-blue { background: #ecf5ff; color: #409EFF; }
.icon-green { background: #f0f9eb; color: #67C23A; }
.icon-purple { background: #f3e8ff; color: #7c4dff; }
.icon-orange { background: #fdf6ec; color: #e6a23c; }

.card-panel-description {
  flex: 1;
  text-align: right;
}

.card-panel-text {
  line-height: 18px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 16px;
  margin-bottom: 12px;
}

.card-panel-num {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.chart-wrapper {
  background: #fff;
  padding: 20px;
  box-shadow: 4px 4px 40px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.section-header {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.search-list {
  max-height: 320px;
  overflow-y: auto;
}

.search-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}

.search-item:last-child {
  border-bottom: none;
}

.search-item-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-rank {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #f5f5f5;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.search-rank.top {
  background: #409EFF;
  color: #fff;
}

.search-keyword {
  font-size: 14px;
  color: #333;
}

.search-item-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-count {
  font-size: 12px;
  color: #999;
}

.search-time {
  font-size: 12px;
  color: #ccc;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.quick-action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  text-decoration: none;
  transition: all 0.3s;
  gap: 8px;
}

.quick-action-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

.quick-action-text {
  font-size: 13px;
  color: #333;
}
</style>
