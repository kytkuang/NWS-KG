<template>
  <div class="admin-home-page">
    <header class="top-bar">
      <div class="left">
        <h1>管理员中心</h1>
      </div>
      <div class="right">
        <button class="btn ghost" @click="goProfile">个人中心</button>
        <button class="btn danger" @click="logout">退出登录</button>
      </div>
    </header>

    <div class="admin-layout">
      <aside class="sidebar">
        <nav class="sidebar-nav">
          <div 
            class="nav-item" 
            :class="{ active: activeMenu === 'system' }"
            @click="navigateTo('system')"
          >
            <div class="nav-dot nav-dot-blue"></div>
            <div class="nav-content">
              <div class="nav-title">用户系统管理</div>
            </div>
          </div>

          <div 
            class="nav-item" 
            :class="{ active: activeMenu === 'knowledge' }"
            @click="navigateTo('knowledge')"
          >
            <div class="nav-dot nav-dot-green"></div>
            <div class="nav-content">
              <div class="nav-title">学习管理</div>
            </div>
          </div>

          <div 
            class="nav-item" 
            :class="{ active: activeMenu === 'test' }"
            @click="navigateTo('test')"
          >
            <div class="nav-dot nav-dot-purple"></div>
            <div class="nav-content">
              <div class="nav-title">用户功能测试</div>
            </div>
          </div>
        </nav>
      </aside>

      <main class="main-content">
        <div v-if="activeMenu === ''" class="welcome-section">
          <h2>欢迎使用管理员中心</h2>
          <p>请从左侧菜单选择要管理的功能模块</p>
        </div>
        <SystemManager v-else-if="activeMenu === 'system'" />
        <KnowledgeManager v-else-if="activeMenu === 'knowledge'" />
        <div v-else-if="activeMenu === 'test'" class="test-section">
          <h2>用户功能测试</h2>
          <p>此功能将跳转到用户端界面进行测试</p>
          <button class="btn primary" @click="goToDashboard">前往用户端</button>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SystemManager from '@/components/Admin/SystemManager.vue'
import KnowledgeManager from '@/components/Admin/KnowledgeManager.vue'

export default {
  name: 'AdminHomeView',
  components: {
    SystemManager,
    KnowledgeManager
  },
  setup() {
    const router = useRouter()
    const user = ref(null)
    const activeMenu = ref('system')

    onMounted(() => {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        user.value = JSON.parse(storedUser)
      }
    })

    const logout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.replace('/')
    }

    const goProfile = () => {
      router.push('/admin/profile')
    }

    const navigateTo = (menu) => {
      activeMenu.value = menu
    }

    const goToDashboard = () => {
      router.push('/dashboard')
    }

    return {
      user,
      activeMenu,
      logout,
      goProfile,
      navigateTo,
      goToDashboard
    }
  }
}
</script>

<style scoped>
.admin-home-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.top-bar h1 {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: #111827;
}

.right {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
  font-weight: 500;
}

.btn.ghost {
  background-color: #ffffff;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn.ghost:hover {
  background-color: #f9fafb;
  transform: translateY(-1px);
}

.btn.danger {
  background-color: #dc2626;
  color: #ffffff;
}

.btn.danger:hover {
  background-color: #b91c1c;
  transform: translateY(-1px);
}

.btn.primary {
  background-color: #007bff;
  color: #ffffff;
}

.btn.primary:hover {
  background-color: #0056b3;
  transform: translateY(-1px);
}

.admin-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 100px;
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
  padding: 20px 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 8px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 8px;
  border-radius: 12px 0 0 12px;
  border-left: 4px solid transparent;
  background: linear-gradient(to right, #ffffff 0%, #f8fafc 100%);
  min-height: 90px;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.05);
  position: relative;
  gap: 8px;
}

.nav-item::before {
  content: '';
  position: absolute;
  right: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 8px solid #f8fafc;
  transition: all 0.3s ease;
}

.nav-item:hover {
  border-left-color: #3b82f6;
  background: linear-gradient(to right, #eff6ff 0%, #dbeafe 100%);
  box-shadow: 2px 0 6px rgba(59, 130, 246, 0.15);
}

.nav-item:hover::before {
  border-left-color: #dbeafe;
}

.nav-item.active {
  border-left-color: #2563eb;
  background: linear-gradient(to right, #dbeafe 0%, #bfdbfe 100%);
  box-shadow: 2px 0 8px rgba(59, 130, 246, 0.25);
}

.nav-item.active::before {
  border-left-color: #bfdbfe;
}

.nav-item.active .nav-title {
  color: #2563eb;
  font-weight: 600;
}

/* 实心圆点样式 */
.nav-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.nav-dot-blue {
  background-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.nav-item.active .nav-dot-blue {
  background-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
  transform: scale(1.2);
}

.nav-dot-green {
  background-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.nav-item.active .nav-dot-green {
  background-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.3);
  transform: scale(1.2);
}

.nav-dot-purple {
  background-color: #8b5cf6;
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
}

.nav-item.active .nav-dot-purple {
  background-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.3);
  transform: scale(1.2);
}

.nav-content {
  width: 100%;
  text-align: center;
}

.nav-title {
  font-size: 12px;
  font-weight: 500;
  color: #111827;
  white-space: normal;
  line-height: 1.4;
  word-break: break-all;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: all 0.3s ease;
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

.welcome-section {
  text-align: center;
  padding: 60px 20px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
}

.welcome-section h2 {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 12px;
}

.welcome-section p {
  font-size: 16px;
  color: #6b7280;
}

.test-section {
  text-align: center;
  padding: 60px 20px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
}

.test-section h2 {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 12px;
}

.test-section p {
  font-size: 16px;
  color: #6b7280;
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .admin-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100% !important;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    padding: 12px 0;
  }

  .sidebar-nav {
    flex-direction: row;
    overflow-x: auto;
    padding: 0 12px;
  }

  .nav-item {
    min-width: 100px;
    flex-shrink: 0;
    min-height: 90px;
  }

  .nav-item::before {
    display: none;
  }

  .top-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 16px;
  }

  .right {
    align-self: stretch;
    justify-content: flex-end;
  }
}
</style>