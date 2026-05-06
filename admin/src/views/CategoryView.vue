<template>
  <div>
    <div class="filter-container">
      <span class="page-title">分类列表</span>
      <el-tag size="small" type="info">{{ categories.length }} 个</el-tag>
      <el-button type="primary" @click="openDialog()" class="ml-auto">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增分类
      </el-button>
    </div>

    <el-table :data="categories" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" align="center" />
      <el-table-column prop="name" label="分类名称" min-width="140" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">{{ row.description || '-' }}</template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="80" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="140" align="center">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除该分类？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button text type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑分类' : '新增分类'" width="440px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="分类名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
        </el-form-item>
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
import { getCategories, createCategory, updateCategory, deleteCategory } from '../api'
import { ElMessage } from 'element-plus'

const categories = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const form = reactive({ name: '', description: '', sort_order: 0 })

const fetchData = async () => {
  try {
    const res = await getCategories()
    categories.value = res.data || []
  } catch {}
}

const openDialog = (row) => {
  if (row) {
    editingId.value = row.id
    form.name = row.name
    form.description = row.description || ''
    form.sort_order = row.sort_order || 0
  } else {
    editingId.value = null
    form.name = ''
    form.description = ''
    form.sort_order = 0
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!form.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  submitting.value = true
  try {
    if (editingId.value) {
      await updateCategory(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createCategory(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch {} finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deleteCategory(id)
    ElMessage.success('删除成功')
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
</style>
