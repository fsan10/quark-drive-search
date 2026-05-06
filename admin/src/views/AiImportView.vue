<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="14">
        <div class="box-card">
          <div class="section-header">
            <span>粘贴分享文本</span>
            <el-select v-model="selectedModel" size="small" style="width: 200px" placeholder="选择AI模型">
              <el-option v-for="m in models" :key="m.id" :label="`${m.name} (${m.provider})`" :value="m.id" />
            </el-select>
          </div>
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="14"
            placeholder="请粘贴网盘分享文本，支持多条（用空行分隔）"
            resize="vertical"
          />
          <div class="action-bar">
            <el-button type="primary" :loading="parsing" @click="handleParse">
              <el-icon class="mr-1"><MagicStick /></el-icon>
              AI 智能识别
            </el-button>
            <el-button @click="handleClear">清空</el-button>
            <el-button v-if="parsedResults.length > 0" type="success" :loading="saving" @click="handleSaveAll">
              一键入库 ({{ parsedResults.length }})
            </el-button>
          </div>
          <el-alert type="info" :closable="false" class="mt-4" show-icon title="粘贴完整的分享文本，AI会自动提取标题、链接和提取码。支持批量粘贴多条分享内容。" />
        </div>
      </el-col>

      <el-col :span="10">
        <div class="box-card">
          <div class="section-header">
            <span>识别结果</span>
            <el-tag v-if="parsedResults.length > 0" type="success" size="small">{{ parsedResults.length }} 条</el-tag>
          </div>

          <div v-if="parsing" class="loading-state">
            <el-icon class="is-loading" :size="32" color="#409EFF"><Loading /></el-icon>
            <p>AI 正在识别中...</p>
          </div>

          <div v-else-if="parsedResults.length > 0" class="result-list">
            <div v-for="(item, index) in parsedResults" :key="index" class="result-item">
              <div class="result-item-header">
                <span class="result-index">{{ index + 1 }}</span>
                <el-tag size="small" :type="linkTypeTag(item.link_type)">{{ linkTypeLabel(item.link_type) }}</el-tag>
                <el-icon v-if="savedIds.has(index)" class="saved-icon" color="#67C23A"><CircleCheckFilled /></el-icon>
              </div>
              <div class="result-item-title">{{ item.title }}</div>
              <div class="result-item-link">{{ item.link }}</div>
              <div v-if="item.extraction_code" class="result-item-code">提取码: {{ item.extraction_code }}</div>
            </div>
          </div>

          <div v-else-if="hasParsed" class="empty-state">未识别到有效的网盘链接</div>
          <div v-else class="empty-state">粘贴文本后点击识别</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MagicStick, Loading, CircleCheckFilled } from '@element-plus/icons-vue'
import { aiParse, aiParseAndSave, getAvailableModels } from '../api'
import { ElMessage } from 'element-plus'

const inputText = ref('')
const parsedResults = ref([])
const parsing = ref(false)
const saving = ref(false)
const hasParsed = ref(false)
const savedIds = ref(new Set())
const models = ref([])
const selectedModel = ref('qwen3.6-plus')

const linkTypeTag = (type) => ({ quark: '', baidu: 'success', alibaba: 'warning', xunlei: 'success', '123pan': 'danger', lanzou: 'info' }[type] || 'info')
const linkTypeLabel = (type) => ({ quark: '夸克网盘', baidu: '百度网盘', alibaba: '阿里云盘', xunlei: '迅雷云盘', '123pan': '123云盘', lanzou: '蓝奏云', other: '其他' }[type] || type)

onMounted(async () => {
  try {
    const res = await getAvailableModels()
    models.value = res.data.models || []
    selectedModel.value = res.data.current || 'qwen3.6-plus'
  } catch {}
})

const handleParse = async () => {
  if (!inputText.value.trim()) { ElMessage.warning('请先粘贴分享文本'); return }
  parsing.value = true
  hasParsed.value = false
  try {
    const res = await aiParse({ text: inputText.value, model: selectedModel.value })
    parsedResults.value = res.data.parsed || []
    hasParsed.value = true
    if (parsedResults.value.length > 0) ElMessage.success(`识别到 ${parsedResults.value.length} 条资源`)
    else ElMessage.warning('未识别到有效的网盘链接')
  } catch { ElMessage.error('识别失败') }
  finally { parsing.value = false }
}

const handleSaveAll = async () => {
  if (!parsedResults.value.length) return
  saving.value = true
  try {
    const res = await aiParseAndSave({ text: inputText.value, model: selectedModel.value })
    const { success_count, fail_count } = res.data
    if (success_count > 0) {
      ElMessage.success(`入库 ${success_count} 条${fail_count > 0 ? `，失败 ${fail_count} 条` : ''}`)
      parsedResults.value.forEach((_, i) => savedIds.value.add(i))
    } else ElMessage.error('入库失败')
  } catch { ElMessage.error('入库失败') }
  finally { saving.value = false }
}

const handleClear = () => {
  inputText.value = ''
  parsedResults.value = []
  hasParsed.value = false
  savedIds.value = new Set()
}
</script>

<style scoped>
.box-card {
  background: #fff;
  padding: 20px;
  box-shadow: 4px 4px 40px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.action-bar {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #999;
  gap: 12px;
}

.result-list {
  max-height: 500px;
  overflow-y: auto;
}

.result-item {
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 8px;
  transition: border-color 0.3s;
}

.result-item:hover {
  border-color: #409EFF;
}

.result-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.result-index {
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

.result-item-title {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  margin-bottom: 4px;
}

.result-item-link {
  font-size: 12px;
  color: #999;
  word-break: break-all;
}

.result-item-code {
  font-size: 12px;
  color: #e6a23c;
  margin-top: 4px;
}

.saved-icon {
  margin-left: auto;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 60px 0;
  font-size: 14px;
}

.mt-4 {
  margin-top: 16px;
}
</style>
