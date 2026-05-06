<template>
  <div>
    <div class="filter-container">
      <span class="page-title">用户列表</span>
      <el-tag size="small" type="info">{{ total }} 个</el-tag>
      <el-select v-model="filterRole" placeholder="角色筛选" clearable style="width: 140px" @change="fetchData">
        <el-option label="超级管理员" value="super_admin" />
        <el-option label="管理员" value="admin" />
        <el-option label="普通用户" value="user" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 120px" @change="fetchData">
        <el-option label="正常" :value="true" />
        <el-option label="禁用" :value="false" />
      </el-select>
      <el-button type="danger" :disabled="!selectedIds.length" @click="confirmBatchDelete" class="ml-auto">
        批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
      </el-button>
    </div>

    <el-table :data="users" border style="width: 100%" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="45" align="center" :selectable="canSelectRow" />
      <el-table-column prop="id" label="ID" width="60" align="center" />
      <el-table-column prop="username" label="用户名" min-width="130">
        <template #default="{ row }">
          <div class="user-cell">
            <div class="user-avatar" :class="avatarClass(row)">{{ row.username.charAt(0).toUpperCase() }}</div>
            <span>{{ row.username }}</span>
            <el-tag v-if="row.role === 'super_admin'" size="small" type="danger" class="role-tag">超管</el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="role" label="角色" width="110" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="roleTagType(row)">{{ roleLabel(row) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="openEditDialog(row)" :disabled="!canEditRow(row)">编辑</el-button>
          <el-button text type="danger" size="small" @click="confirmDelete(row)" :disabled="!canDeleteRow(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="fetchData" small />
    </div>

    <!-- 编辑用户弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑用户" width="440px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input :model-value="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" :disabled="!isSuperAdmin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="editForm.is_active" active-text="正常" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleEditSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 操作验证密码弹窗 -->
    <el-dialog v-model="passwordDialogVisible" :title="passwordDialogTitle" width="400px" destroy-on-close>
      <p class="mb-3 text-sm text-gray-500">{{ passwordDialogDesc }}</p>
      <el-input v-model="adminPassword" type="password" placeholder="请输入当前管理员密码" show-password @keyup.enter="handlePasswordConfirm" />
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="verifying" @click="handlePasswordConfirm">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { getUsers, updateUser, deleteUser, batchDeleteUsers, verifyCurrentPassword } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const users = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const filterRole = ref('')
const filterStatus = ref('')
const editDialogVisible = ref(false)
const submitting = ref(false)
const editForm = reactive({ id: null, username: '', email: '', role: 'user', is_active: true })
const selectedIds = ref([])

const passwordDialogVisible = ref(false)
const adminPassword = ref('')
const verifying = ref(false)
const pendingAction = ref(null)
const pendingTarget = ref({})

const currentAdminId = ref(null)
const currentAdminRole = ref('admin')

const isSuperAdmin = computed(() => currentAdminRole.value === 'super_admin')

const passwordDialogTitle = computed(() => {
  if (!pendingAction.value) return '密码验证'
  if (pendingAction.value === 'edit') return '验证管理员密码'
  if (pendingAction.value === 'delete') return '验证管理员密码'
  if (pendingAction.value === 'batch-delete') return '验证管理员密码'
  return '密码验证'
})

const passwordDialogDesc = computed(() => {
  if (!pendingAction.value) return ''
  if (pendingAction.value === 'edit') return `修改用户 ${pendingTarget.value.username} 的信息，请验证当前管理员密码：`
  if (pendingAction.value === 'delete') return `删除用户 ${pendingTarget.value.username}，请验证当前管理员密码：`
  if (pendingAction.value === 'batch-delete') return `批量删除 ${pendingTarget.value.count} 个用户，请验证当前管理员密码：`
  return ''
})

const avatarClass = (row) => {
  if (row.role === 'super_admin') return 'super-admin'
  if (row.role === 'admin') return 'admin'
  return ''
}

const roleTagType = (row) => {
  if (row.role === 'super_admin') return 'danger'
  if (row.role === 'admin') return 'warning'
  return 'info'
}

const roleLabel = (row) => {
  if (row.role === 'super_admin') return '超级管理员'
  if (row.role === 'admin') return '管理员'
  return '普通用户'
}

const canSelectRow = (row) => {
  if (row.role === 'super_admin') return false
  if (row.id === currentAdminId.value) return false
  if (row.role === 'admin' && !isSuperAdmin.value) return false
  return true
}

const canEditRow = (row) => {
  if (row.role === 'super_admin') return false
  if (row.id === currentAdminId.value) return false
  if (row.role === 'admin' && !isSuperAdmin.value) return false
  return true
}

const canDeleteRow = (row) => {
  if (row.role === 'super_admin') return false
  if (row.id === currentAdminId.value) return false
  if (row.role === 'admin' && !isSuperAdmin.value) return false
  return true
}

const fetchData = async () => {
  try {
    const params = { page: page.value, page_size: pageSize }
    if (filterRole.value) params.role = filterRole.value
    if (filterStatus.value !== '' && filterStatus.value !== null) params.is_active = filterStatus.value
    const res = await getUsers(params)
    users.value = res.data.items || []
    total.value = res.data.total || 0
    currentAdminId.value = res.data.current_admin_id
    currentAdminRole.value = res.data.current_admin_role || 'admin'
  } catch {}
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(s => s.id)
}

const openEditDialog = (row) => {
  pendingAction.value = 'edit'
  pendingTarget.value = { id: row.id, username: row.username }
  editForm.id = row.id
  editForm.username = row.username
  editForm.email = row.email
  editForm.role = row.role
  editForm.is_active = row.is_active
  adminPassword.value = ''
  passwordDialogVisible.value = true
}

const confirmDelete = (row) => {
  if (row.role === 'super_admin') {
    ElMessage.warning('超级管理员账户不可删除')
    return
  }
  if (row.id === currentAdminId.value) {
    ElMessage.warning('不能删除自己的账号')
    return
  }
  if (row.role === 'admin' && !isSuperAdmin.value) {
    ElMessage.warning('仅超级管理员可删除管理员账户')
    return
  }
  pendingAction.value = 'delete'
  pendingTarget.value = { id: row.id, username: row.username }
  adminPassword.value = ''
  passwordDialogVisible.value = true
}

const confirmBatchDelete = async () => {
  if (!selectedIds.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 个用户吗？`,
      '批量删除确认',
      { type: 'warning' }
    )
    pendingAction.value = 'batch-delete'
    pendingTarget.value = { count: selectedIds.value.length, ids: [...selectedIds.value] }
    adminPassword.value = ''
    passwordDialogVisible.value = true
  } catch {}
}

const handlePasswordConfirm = async () => {
  if (!adminPassword.value) {
    ElMessage.warning('请输入密码')
    return
  }
  verifying.value = true
  try {
    await verifyCurrentPassword(adminPassword.value)
    passwordDialogVisible.value = false

    if (pendingAction.value === 'edit') {
      editDialogVisible.value = true
    } else if (pendingAction.value === 'delete') {
      await executeDelete(pendingTarget.value.id)
    } else if (pendingAction.value === 'batch-delete') {
      await executeBatchDelete(pendingTarget.value.ids)
    }
  } catch {
    ElMessage.error('密码验证失败')
  } finally {
    verifying.value = false
  }
}

const handleEditSubmit = async () => {
  submitting.value = true
  try {
    await updateUser(editForm.id, {
      email: editForm.email,
      role: editForm.role,
      is_active: editForm.is_active,
    })
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    fetchData()
  } catch {} finally {
    submitting.value = false
  }
}

const executeDelete = async (userId) => {
  try {
    await deleteUser(userId)
    ElMessage.success('删除成功')
    fetchData()
  } catch {}
}

const executeBatchDelete = async (ids) => {
  try {
    const res = await batchDeleteUsers(ids)
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

.pagination-container {
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #c0c4cc;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-avatar.admin {
  background: #409EFF;
}

.user-avatar.super-admin {
  background: #F56C6C;
}

.role-tag {
  margin-left: 2px;
}

.mb-3 {
  margin-bottom: 12px;
}
</style>
