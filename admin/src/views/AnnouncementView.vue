<template>
  <div>
    <div class="filter-container">
      <span class="page-title">公告列表</span>
      <el-button type="primary" @click="openDialog()" class="ml-auto">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增公告
      </el-button>
      <el-button type="danger" :disabled="!selectedIds.length" @click="confirmBatchDelete">
        批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
      </el-button>
    </div>

    <el-table :data="announcements" border style="width: 100%" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="45" align="center" />
      <el-table-column prop="id" label="ID" width="60" align="center" />
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_published" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="row.is_published ? 'success' : 'info'">{{ row.is_published ? '已发布' : '草稿' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="70" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="140" align="center">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button text type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑公告' : '新增公告'" width="900px" destroy-on-close top="5vh">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="公告标题" />
        </el-form-item>
        <el-form-item label="内容" required>
          <MdEditor v-model="form.content" :style="{ height: '400px' }" language="zh-CN" :onUploadImg="onUploadImg" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort_order" :min="0" :max="999" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发布">
              <el-switch v-model="form.is_published" active-text="发布" inactive-text="草稿" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { getAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement, batchDeleteAnnouncements, uploadImage } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

const announcements = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const selectedIds = ref([])
const form = reactive({ title: '', content: '', is_published: true, sort_order: 0 })

const fetchData = async () => {
  try {
    const res = await getAnnouncements()
    announcements.value = res.data || []
  } catch {}
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(s => s.id)
}

const openDialog = (row) => {
  if (row) {
    editingId.value = row.id
    form.title = row.title
    form.content = row.content
    form.is_published = row.is_published
    form.sort_order = row.sort_order || 0
  } else {
    editingId.value = null
    form.title = ''
    form.content = ''
    form.is_published = true
    form.sort_order = 0
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!form.title.trim()) { ElMessage.warning('请输入标题'); return }
  if (!form.content.trim()) { ElMessage.warning('请输入内容'); return }
  submitting.value = true
  try {
    if (editingId.value) {
      await updateAnnouncement(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createAnnouncement(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch {} finally { submitting.value = false }
}

const handleDelete = async (id) => {
  try {
    await deleteAnnouncement(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch {}
}

const confirmBatchDelete = async () => {
  if (!selectedIds.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 个公告吗？`,
      '批量删除确认',
      { type: 'warning' }
    )
    const res = await batchDeleteAnnouncements(selectedIds.value)
    ElMessage.success(res.data.message || '批量删除成功')
    fetchData()
  } catch {}
}

const formatDate = (str) => {
  if (!str) return ''
  return str.replace('T', ' ').substring(0, 19)
}

const onUploadImg = async (files, callback) => {
  const urls = []
  for (const file of files) {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await uploadImage(formData)
      urls.push(res.data.url)
    } catch {
      ElMessage.error(`图片 ${file.name} 上传失败`)
    }
  }
  callback(urls)
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
:deep(.md-editor-toolbar-wrapper) {
  display: flex;
  align-items: center;
}
:deep(.md-editor-toolbar) {
  display: flex;
  align-items: center;
}
:deep(.md-editor-content) {
  display: flex;
}
:deep(.md-editor-footer) {
  display: flex;
  align-items: center;
  height: 28px;
  line-height: 28px;
}
</style>
