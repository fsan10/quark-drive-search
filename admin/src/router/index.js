import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { noAuth: true },
  },
  {
    path: '/',
    component: () => import('../views/LayoutView.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'resources',
        name: 'Resources',
        component: () => import('../views/ResourceView.vue'),
        meta: { title: '资源管理' },
      },
      {
        path: 'ai-import',
        name: 'AiImport',
        component: () => import('../views/AiImportView.vue'),
        meta: { title: 'AI导入' },
      },
      {
        path: 'csv-import',
        name: 'CsvImport',
        component: () => import('../views/CsvImportView.vue'),
        meta: { title: 'CSV导入' },
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/CategoryView.vue'),
        meta: { title: '分类管理' },
      },
      {
        path: 'announcements',
        name: 'Announcements',
        component: () => import('../views/AnnouncementView.vue'),
        meta: { title: '公告管理' },
      },
      {
        path: 'wishes',
        name: 'Wishes',
        component: () => import('../views/WishView.vue'),
        meta: { title: '许愿池' },
      },
      {
        path: 'donation',
        name: 'Donation',
        component: () => import('../views/DonationView.vue'),
        meta: { title: '打赏配置' },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/UserView.vue'),
        meta: { title: '用户管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  if (!to.meta.noAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
