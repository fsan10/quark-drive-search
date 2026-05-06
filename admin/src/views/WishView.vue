<template>
  <div>
    <div class="filter-container">
      <span class="page-title">许愿池</span>
      <el-select v-model="filterResolved" placeholder="状态" clearable style="width: 120px" @change="fetchData">
        <el-option label="未回应" :value="false" />
        <el-option label="已回应" :value="true" />
      </el-select>
      <el-button type="danger" :disabled="!selectedIds.length" @click="confirmBatchDelete" class="ml-auto">
        批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
      </el-button>
    </div>

    <el-table :data="wishes" border style="width: 100%" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="45" align="center" />
      <el-table-column prop="id" label="ID" width="60" align="center" />
      <el-table-column prop="username" label="用户" width="100" />
      <el-table-column prop="content" label="许愿内容" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_resolved" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="row.is_resolved ? 'success' : 'warning'">{{ row.is_resolved ? '已回应' : '待回应' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reply_count" label="回复" width="60" align="center" />
      <el-table-column prop="created_at" label="时间" width="170">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="openReplyDialog(row)">回复</el-button>
          <el-popconfirm title="确认删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button text type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="replyDialogVisible" title="回复许愿" width="560px" destroy-on-close>
      <div class="mb-4 p-3 bg-gray-50 rounded">
        <p class="text-sm text-gray-500">许愿内容：</p>
        <p class="text-sm text-gray-800 mt-1">{{ currentWish.content }}</p>
      </div>
      <el-form :model="replyForm" label-width="90px">
        <el-form-item label="回复内容" required>
          <el-input v-model="replyForm.content" type="textarea" :rows="3" placeholder="回复内容" />
        </el-form-item>
        <el-form-item label="资源标题">
          <el-input v-model="replyForm.resource_title" placeholder="如有关联资源，填写标题" />
        </el-form-item>
        <el-form-item label="资源链接">
          <el-input v-model="replyForm.resource_link" placeholder="如有关联资源，填写链接" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="网盘类型">
              <el-select v-model="replyForm.resource_link_type" style="width: 100%">
                <el-option label="夸克网盘" value="quark" />
                <el-option label="百度网盘" value="baidu" />
                <el-option label="阿里云盘" value="alibaba" />
                <el-option label="迅雷云盘" value="xunlei" />
                <el-option label="123云盘" value="123pan" />
                <el-option label="蓝奏云" value="lanzou" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="提取码">
              <el-input v-model="replyForm.resource_extraction_code" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="replying" @click="handleReply">回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getWishes, replyWish, deleteWish, batchDeleteWishes } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const wishes = ref([])
const filterResolved = ref('')
const replyDialogVisible = ref(false)
const replying = ref(false)
const currentWish = ref({})
const selectedIds = ref([])

const replyForm = reactive({
  content: '',
  resource_link: '',
  resource_link_type: 'quark',
  resource_extraction_code: '',
  resource_title: '',
})

const fetchData = async () => {
  try {
    const params = {}
    if (filterResolved.value !== '' && filterResolved.value !== null) {
      params.resolved = filterResolved.value
    }
    const res = await getWishes(params)
    wishes.value = res.data || []
  } catch {}
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(s => s.id)
}

const openReplyDialog = (wish) => {
  currentWish.value = wish
  replyForm.content = ''
  replyForm.resource_link = ''
  replyForm.resource_link_type = 'quark'
  replyForm.resource_extraction_code = ''
  replyForm.resource_title = ''
  replyDialogVisible.value = true
}

const handleReply = async () => {
  if (!replyForm.content.trim()) { ElMessage.warning('请输入回复内容'); return }
  replying.value = true
  try {
    await replyWish(currentWish.value.id, replyForm)
    ElMessage.success('回复成功')
    replyDialogVisible.value = false
    fetchData()
  } catch {} finally { replying.value = false }
}

const handleDelete = async (id) => {
  try {
    await deleteWish(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch {}
}

const confirmBatchDelete = async () => {
  if (!selectedIds.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 个许愿吗？`,
      '批量删除确认',
      { type: 'warning' }
    )
    const res = await batchDeleteWishes(selectedIds.value)
    ElMessage.success(res.data.message || '批量删除成功')
    fetchData()
  } catch {}
}

const formatDate = (str) => {
  if (!str) return ''
  return str.replace('T', ' ').substring(0, 19)
}

onMounted(fetchData)
</script>

<style scoped>
.filter-container {
  padding-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.page-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}
.ml-auto {
  margin-left: auto;
}
.mb-4 {
  margin-bottom: 16px;
}
</style>
