<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h3 class="login-title">系统登录</h3>
        <el-icon class="refresh-icon" @click="handleReset"><Refresh /></el-icon>
      </div>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" @keyup.enter="handleLogin">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" :type="showPassword ? '' : 'password'" placeholder="密码" size="large" @keyup.enter="handleLogin">
            <template #prefix><el-icon><Lock /></el-icon></template>
            <template #suffix>
              <el-icon class="pwd-toggle" @click="showPassword = !showPassword">
                <View v-if="showPassword" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button :loading="loading" type="primary" size="large" class="login-btn" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api'
import { ElMessage } from 'element-plus'
import { User, Lock, View, Hide, Refresh } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const showPassword = ref(false)
const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await login(form)
    localStorage.setItem('admin_token', res.data.access_token)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (e) {
    const msg = e.response?.data?.detail || '登录失败，请检查用户名和密码'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  form.username = ''
  form.password = ''
  showPassword.value = false
}
</script>

<style scoped>
.login-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  background-color: #2d3a4b;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.login-box {
  width: 380px;
  max-width: 90%;
}

.login-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 0 2px;
}

.login-title {
  font-size: 26px;
  color: #fff;
  font-weight: bold;
  margin: 0;
}

.refresh-icon {
  color: #889aa4;
  font-size: 18px;
  cursor: pointer;
  transition: transform 0.5s ease, color 0.3s ease;
}

.refresh-icon:hover {
  color: #fff;
  transform: rotate(180deg);
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  box-shadow: none;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.2);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
}

:deep(.el-input__inner) {
  color: #fff;
}

:deep(.el-input__inner::placeholder) {
  color: #889aa4;
}

:deep(.el-input__inner:-webkit-autofill) {
  box-shadow: 0 0 0 1000px rgba(255, 255, 255, 0.1) inset !important;
  -webkit-text-fill-color: #fff !important;
}

:deep(.el-input__prefix .el-icon),
:deep(.el-input__suffix .el-icon) {
  color: #889aa4;
}

.pwd-toggle {
  cursor: pointer;
  transition: color 0.3s ease;
}

.pwd-toggle:hover {
  color: #fff;
}

.login-btn {
  width: 100%;
  letter-spacing: 4px;
}
</style>
