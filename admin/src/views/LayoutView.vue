<template>
  <div :class="['app-wrapper', isCollapse ? 'hide-sidebar' : 'open-sidebar']">
    <div class="sidebar-container">
      <div class="sidebar-logo-container">
        <router-link to="/dashboard" class="sidebar-logo-link">
          <div class="logo-icon-wrapper">
            <el-icon :size="22" color="#fff"><Search /></el-icon>
          </div>
          <transition name="sidebar-logo-fade">
            <span v-if="!isCollapse" class="logo-title">云盘搜索</span>
          </transition>
        </router-link>
      </div>

      <el-scrollbar wrap-class="scrollbar-wrapper">
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          :unique-opened="false"
          router
          class="sidebar-menu"
        >
          <el-menu-item
            v-for="item in menuItems"
            :key="item.path"
            :index="item.path"
            class="sidebar-menu-item"
          >
            <el-icon class="sidebar-icon" :size="18"><component :is="item.iconComp" /></el-icon>
            <template #title>
              <span class="sidebar-title">{{ item.label }}</span>
            </template>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </div>

    <div class="main-container">
      <div class="fixed-header">
        <div class="navbar">
          <div class="navbar-left">
            <div class="hamburger-wrapper" @click="toggleSidebar">
              <el-icon class="hamburger-icon" :size="20">
                <Fold v-if="!isCollapse" />
                <Expand v-else />
              </el-icon>
            </div>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ $route.meta.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <div class="navbar-right">
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-info">
                <div class="user-avatar">
                  <el-icon :size="16" color="#fff"><User /></el-icon>
                </div>
                <span class="user-name">管理员</span>
                <el-icon class="user-arrow"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <div class="app-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Odometer, Document, MagicStick, Upload, Folder, User,
  Fold, Expand, ArrowDown, SwitchButton, Search,
  Bell, Star, Present
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)
const activeMenu = computed(() => route.path)

const menuItems = [
  { path: '/dashboard', label: '仪表盘', iconComp: Odometer },
  { path: '/resources', label: '资源管理', iconComp: Document },
  { path: '/ai-import', label: 'AI 导入', iconComp: MagicStick },
  { path: '/csv-import', label: 'CSV 导入', iconComp: Upload },
  { path: '/categories', label: '分类管理', iconComp: Folder },
  { path: '/announcements', label: '公告管理', iconComp: Bell },
  { path: '/wishes', label: '许愿池', iconComp: Star },
  { path: '/donation', label: '打赏配置', iconComp: Present },
  { path: '/users', label: '用户管理', iconComp: User },
]

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    localStorage.removeItem('admin_token')
    router.push('/login')
  }
}
</script>

<style scoped>
.app-wrapper {
  position: relative;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.sidebar-container {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  width: 210px;
  height: 100%;
  background-color: #304156;
  overflow: hidden;
  transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.hide-sidebar .sidebar-container {
  width: 54px;
}

.sidebar-logo-container {
  height: 50px;
  line-height: 50px;
  background-color: #2b2f3a;
  overflow: hidden;
  white-space: nowrap;
}

.sidebar-logo-link {
  display: inline-flex;
  align-items: center;
  height: 50px;
  padding-left: 14px;
  text-decoration: none;
  cursor: pointer;
}

.logo-icon-wrapper {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: #409eff;
  border-radius: 6px;
  flex-shrink: 0;
}

.logo-title {
  display: inline-block;
  margin-left: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  vertical-align: middle;
  white-space: nowrap;
  letter-spacing: 1px;
}

.sidebar-logo-fade-enter-active {
  transition: opacity 0.3s ease;
}

.sidebar-logo-fade-enter-from,
.sidebar-logo-fade-leave-to {
  opacity: 0;
}

.sidebar-menu {
  border: none !important;
  height: 100%;
  width: 100% !important;
  background-color: #304156;
}

.sidebar-menu-item {
  height: 56px;
  line-height: 56px;
  margin: 0 8px;
  border-radius: 4px;
  color: #bfcbd9;
  font-size: 14px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: transparent;
}

.sidebar-menu-item:hover {
  color: #fff;
  background-color: #263445;
}

.sidebar-menu-item.is-active {
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.15);
  font-weight: 500;
}

.sidebar-icon {
  vertical-align: middle;
  margin-right: 12px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-menu-item:hover .sidebar-icon {
  transform: scale(1.15);
  color: #fff;
}

.sidebar-menu-item.is-active .sidebar-icon {
  color: #409eff;
}

.sidebar-title {
  vertical-align: middle;
  transition: opacity 0.25s ease;
}

.main-container {
  min-height: 100%;
  transition: margin-left 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  margin-left: 210px;
  position: relative;
}

.hide-sidebar .main-container {
  margin-left: 54px;
}

.fixed-header {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9;
  width: calc(100% - 210px);
  transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.hide-sidebar .fixed-header {
  width: calc(100% - 54px);
}

.navbar {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hamburger-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 4px;
  border-radius: 4px;
}

.hamburger-wrapper:hover {
  transform: scale(1.1);
  background-color: rgba(0, 0, 0, 0.04);
}

.hamburger-wrapper:active {
  transform: scale(0.95);
}

.hamburger-icon {
  color: #5a5e66;
}

.navbar-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 20px;
  transition: background-color 0.25s ease;
}

.user-info:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-name {
  margin-left: 8px;
  font-size: 14px;
  color: #303133;
}

.user-arrow {
  margin-left: 4px;
  font-size: 12px;
  color: #909399;
  transition: transform 0.3s ease;
}

.app-main {
  min-height: calc(100vh - 50px);
  padding: 20px;
  background-color: #f0f2f5;
  margin-top: 50px;
}

:deep(.sidebar-menu .el-menu-item) {
  background-color: transparent !important;
}

:deep(.sidebar-menu .el-menu-item:hover) {
  background-color: #263445 !important;
}

:deep(.sidebar-menu .el-menu-item.is-active) {
  background-color: rgba(64, 158, 255, 0.15) !important;
}

:deep(.el-breadcrumb__inner) {
  color: #303133;
  font-weight: 500;
}

:deep(.el-breadcrumb__inner.is-link) {
  color: #606266;
}

:deep(.el-breadcrumb__inner.is-link:hover) {
  color: #409eff;
}
</style>
