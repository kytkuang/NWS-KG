<template>
  <div class="profile-page">
    <header class="top-bar">
      <div class="left">
        <h1>管理员个人中心</h1>
        <p>管理您的账户信息和系统权限</p>
      </div>
      <div class="right">
        <button class="btn ghost" @click="goBack">返回</button>
      </div>
    </header>

    <main class="content">
      <!-- 账户信息 -->
      <section class="section">
        <h2 class="section-title">账户信息</h2>
        <div class="profile-header">
          <div class="avatar">
            <span>👑</span>
          </div>
          <div class="profile-info">
            <h3>{{ user?.username }}</h3>
            <p class="role-badge">系统管理员</p>
          </div>
        </div>

        <div class="info-list">
          <div class="info-item">
            <span class="label">邮箱：</span>
            <span class="value">{{ user?.email }}</span>
          </div>
          <div class="info-item">
            <span class="label">注册时间：</span>
            <span class="value">{{ formatDate(user?.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">最后登录：</span>
            <span class="value">{{ formatDate(user?.last_login) }}</span>
          </div>
        </div>
      </section>

      <!-- 系统权限概览 -->
      <section class="section">
        <h2 class="section-title">系统权限</h2>
        <div class="permissions-overview">
          <div class="permission-badge">
            <span class="permission-text">用户管理</span>
          </div>
          <div class="permission-badge">
            <span class="permission-text">内容管理</span>
          </div>
          <div class="permission-badge">
            <span class="permission-text">系统设置</span>
          </div>
          <div class="permission-badge">
            <span class="permission-text">数据分析</span>
          </div>
        </div>
      </section>

      <!-- 账户设置 -->
      <section class="section">
        <h2 class="section-title">账户设置</h2>
        <div class="settings-list">
          <button class="setting-item" @click="changePassword">
            <div class="setting-content">
              <div class="setting-title">修改密码</div>
              <div class="setting-desc">定期更换密码保护账户安全</div>
            </div>
            <div class="setting-arrow">→</div>
          </button>
          <button class="setting-item" @click="systemSettings">
            <div class="setting-content">
              <div class="setting-title">系统配置</div>
              <div class="setting-desc">配置系统参数和偏好设置</div>
            </div>
            <div class="setting-arrow">→</div>
          </button>
        </div>
      </section>

      <!-- 退出登录 -->
      <section class="section logout-section">
        <button class="btn danger logout-btn" @click="logout">
          退出登录
        </button>
      </section>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'AdminProfileView',
  setup() {
    const router = useRouter()
    const user = ref(null)

    onMounted(() => {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        user.value = JSON.parse(storedUser)
      }
    })

    const logout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.replace('/login')
    }

    const goBack = () => {
      router.go(-1)
    }

    const changePassword = () => {
      // TODO: 实现修改密码功能
      alert('修改密码功能正在开发中')
    }

    const systemSettings = () => {
      // TODO: 实现系统配置功能
      alert('系统配置功能正在开发中')
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      try {
        return new Date(dateString).toLocaleDateString('zh-CN')
      } catch {
        return dateString
      }
    }

    return {
      user,
      logout,
      goBack,
      changePassword,
      systemSettings,
      formatDate
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 24px 16px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  padding: 20px 24px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.top-bar h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
  color: #111827;
}

.top-bar p {
  font-size: 14px;
  color: #6b7280;
}

.right {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn.danger {
  background-color: #dc2626;
  color: #f9fafb;
}

.btn.danger:hover {
  background-color: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 38, 38, 0.3);
}

.content {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #111827;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border-radius: 8px;
  border: 1px solid #93c5fd;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  border: 2px solid #3b82f6;
  color: #1e40af;
  flex-shrink: 0;
}

.profile-info h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1e40af;
}

.role-badge {
  background: rgba(255, 255, 255, 0.8);
  color: #7c3aed;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  display: inline-block;
  border: 1px solid #c4b5fd;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
}

.value {
  color: #111827;
  font-size: 14px;
  font-weight: 500;
}

.permissions-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.permission-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.permission-text {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.setting-item:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.setting-content {
  flex: 1;
}

.setting-title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 2px;
}

.setting-desc {
  font-size: 12px;
  color: #6b7280;
}

.setting-arrow {
  font-size: 14px;
  color: #9ca3af;
}

.logout-section {
  margin-top: 20px;
}

.logout-btn {
  width: 100%;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

@media (max-width: 768px) {
  .permissions-overview {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>