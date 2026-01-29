import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DashboardView from '../views/DashboardView.vue'
import ProfileView from '../views/ProfileView.vue'
import AdminHomeView from '../views/AdminHomeView.vue'
import AdminProfileView from '../views/AdminProfileView.vue'

// 简单认证工具函数（不依赖独立 auth.js）
function isTokenExpired(token) {
  if (!token) return true
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return true
    const payload = JSON.parse(atob(parts[1]))
    if (!payload.exp) return false
    const expTime = payload.exp * 1000
    return Date.now() >= expTime
  } catch {
    return true
  }
}

function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

function isAuthenticated() {
  const token = localStorage.getItem('token')
  if (!token) return false
  if (isTokenExpired(token)) {
    clearAuth()
    return false
  }
  return true
}

// 判断是否管理员
function isAdmin() {
  try {
    const userStr = localStorage.getItem('user')
    if (!userStr) return false
    const user = JSON.parse(userStr)
    return !!user.is_admin
  } catch {
    return false
  }
}

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { guestOnly: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminHome',
    component: AdminHomeView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/profile',
    name: 'AdminProfile',
    component: AdminProfileView,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫：处理登录态和跳转
router.beforeEach((to, from, next) => {
  // 检查 token 是否过期，如果过期则清除
  const token = localStorage.getItem('token')
  if (token && isTokenExpired(token)) {
    clearAuth()
  }
  
  const authed = isAuthenticated()

  // 已登录用户访问登录/注册页，根据角色跳转到不同页面
  if (to.meta.guestOnly && authed) {
    return next(isAdmin() ? { name: 'AdminHome' } : { name: 'Dashboard' })
  }

  // 访问需要登录的页面但未登录，跳转到首页
  if (to.meta.requiresAuth && !authed) {
    return next({
      name: 'Home',
      query: { redirect: to.fullPath }
    })
  }

  // 访问管理员页面但不是管理员
  if (to.meta.requiresAdmin && !isAdmin()) {
    return next({ name: 'Dashboard' })
  }

  next()
})

export default router