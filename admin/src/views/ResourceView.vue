<template>
  <div>
    <div class="filter-container">
      <el-input v-model="keyword" placeholder="搜索资源..." style="width: 200px" clearable @clear="fetchData" @keyup.enter="fetchData">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filterLinkType" placeholder="网盘类型" clearable style="width: 130px" @change="fetchData">
        <el-option v-for="item in linkTypes" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-select v-model="filterCategoryId" placeholder="分类" clearable style="width: 130px" @change="fetchData">
        <el-option v-for="cat in categoryList" :key="cat.id" :label="cat.name" :value="cat.id" />
      </el-select>
      <el-select v-model="filterFileSize" placeholder="文件大小" clearable style="width: 130px" @change="fetchData">
        <el-option label="小于 100MB" value="lt100mb" />
        <el-option label="100MB - 1GB" value="100mb-1gb" />
        <el-option label="1GB - 10GB" value="1gb-10gb" />
        <el-option label="大于 10GB" value="gt10gb" />
      </el-select>
      <el-button type="primary" @click="openDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增
      </el-button>
      <el-button type="danger" :disabled="!selectedIds.length" @click="confirmBatchDelete">
        批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
      </el-button>
      <el-dropdown v-if="selectedIds.length" @command="handleBatchVisibility" trigger="click">
        <el-button type="warning">
          批量可见性 ({{ selectedIds.length }})<el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="visible">设为可见</el-dropdown-item>
            <el-dropdown-item command="hidden">设为隐藏</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <el-table :data="tableData" border style="width: 100%" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="45" align="center" />
      <el-table-column prop="id" label="ID" width="60" align="center" />
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="link_type" label="网盘" width="100" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="linkTypeTag(row.link_type)">{{ linkTypeLabel(row.link_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="category_name" label="分类" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.category_name">{{ row.category_name }}</span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="file_size" label="大小" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.file_size">{{ row.file_size }}</span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="link" label="链接" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <el-link type="primary" :href="row.link" target="_blank" :underline="false">{{ row.link }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="extraction_code" label="提取码" width="80" align="center">
        <template #default="{ row }">
          <span v-if="row.extraction_code">{{ row.extraction_code }}</span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="is_visible" label="可见" width="80" align="center">
        <template #default="{ row }">
          <el-switch v-model="row.is_visible" @change="(val) => handleToggleVisibility(row, val)" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="130" align="center" fixed="right">
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

    <div class="pagination-container">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="fetchData" small />
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑资源' : '新增资源'" width="560px" destroy-on-close>
      <el-form :model="form" label-width="90px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="资源标题" />
        </el-form-item>
        <el-form-item label="链接" required>
          <el-input v-model="form.link" placeholder="网盘分享链接" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="网盘类型">
              <el-select v-model="form.link_type" style="width: 100%">
                <el-option v-for="item in linkTypes" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="提取码">
              <el-input v-model="form.extraction_code" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="form.category_id" clearable style="width: 100%">
                <el-option v-for="cat in categoryList" :key="cat.id" :label="cat.name" :value="cat.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="文件大小">
              <el-input v-model="form.file_size" placeholder="如 2.5GB" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
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
import { Search, Plus, ArrowDown } from '@element-plus/icons-vue'
import { getResources, createResource, updateResource, deleteResource, getCategories, batchDeleteResources, batchUpdateVisibility, toggleResourceVisibility } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const keyword = ref('')
const filterLinkType = ref('')
const filterCategoryId = ref('')
const filterFileSize = ref('')
const tableData = ref([])
const page = ref(1)
const pageSize = 20
const total = ref(0)
const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const categoryList = ref([])
const selectedIds = ref([])

const linkTypes = [
  { value: 'quark', label: '夸克网盘' },
  { value: 'baidu', label: '百度网盘' },
  { value: 'alibaba', label: '阿里云盘' },
  { value: 'xunlei', label: '迅雷云盘' },
  { value: '123pan', label: '123云盘' },
  { value: 'lanzou', label: '蓝奏云' },
  { value: 'other', label: '其他' },
]

const linkTypeTag = (type) => ({ quark: '', baidu: 'success', alibaba: 'warning', xunlei: 'success', '123pan': 'danger', lanzou: 'info' }[type] || 'info')
const linkTypeLabel = (type) => (linkTypes.find(t => t.value === type) || { label: type }).label

const form = reactive({
  title: '', link: '', link_type: 'quark', extraction_code: '',
  category_id: null, file_size: '', description: '',
})

const fetchData = async () => {
  try {
    const params = {
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value || undefined,
      link_type: filterLinkType.value || undefined,
      category_id: filterCategoryId.value || undefined,
      file_size_filter: filterFileSize.value || undefined,
    }
    const res = await getResources(params)
    tableData.value = res.data.items || []
    total.value = res.data.total || 0
  } catch {}
}

const fetchCategories = async () => {
  try {
    const res = await getCategories()
    categoryList.value = res.data || []
  } catch {}
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(s => s.id)
}

const handleToggleVisibility = async (row, val) => {
  try {
    await toggleResourceVisibility(row.id, val)
    ElMessage.success(val ? '已设为可见' : '已设为隐藏')
  } catch {
    row.is_visible = !val
  }
}

const openDialog = (row) => {
  if (row) {
    editingId.value = row.id
    Object.assign(form, {
      title: row.title, link: row.link, link_type: row.link_type,
      extraction_code: row.extraction_code || '', category_id: row.category_id,
      file_size: row.file_size || '', description: row.description || '',
    })
  } else {
    editingId.value = null
    Object.assign(form, { title: '', link: '', link_type: 'quark', extraction_code: '', category_id: null, file_size: '', description: '' })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!form.title || !form.link) {
    ElMessage.warning('标题和链接不能为空')
    return
  }
  submitting.value = true
  try {
    const data = { ...form, category_id: form.category_id || undefined, extraction_code: form.extraction_code || undefined }
    if (editingId.value) {
      await updateResource(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createResource(data)
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
    await deleteResource(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch {}
}

const confirmBatchDelete = async () => {
  if (!selectedIds.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 个资源吗？`,
      '批量删除确认',
      { type: 'warning' }
    )
    const res = await batchDeleteResources(selectedIds.value)
    ElMessage.success(res.data.message || '批量删除成功')
    fetchData()
  } catch {}
}

const handleBatchVisibility = async (command) => {
  const is_visible = command === 'visible'
  const label = is_visible ? '可见' : '隐藏'
  try {
    await ElMessageBox.confirm(
      `确定要将选中的 ${selectedIds.value.length} 个资源设为${label}吗？`,
      '批量修改可见性',
      { type: 'warning' }
    )
    const res = await batchUpdateVisibility(selectedIds.value, is_visible)
    ElMessage.success(res.data.message || `批量设为${label}成功`)
    fetchData()
  } catch {}
}

onMounted(() => {
  fetchData()
  fetchCategories()
})
</script>

<style scoped>
.filter-container {
  padding-bottom: 16px;
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.pagination-container {
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.text-muted {
  color: #c0c4cc;
}
</style>
