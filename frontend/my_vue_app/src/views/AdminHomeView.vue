<template>
  <div class="admin-home-page">
    <header class="top-bar">
      <div class="left">
        <h1>管理员中心</h1>
        <p>管理系统功能和用户体验</p>
      </div>
      <div class="right">
        <button class="btn ghost" @click="goProfile">个人中心</button>
        <button class="btn danger" @click="logout">退出登录</button>
      </div>
    </header>

    <main class="content">
      <section class="card admin-card" @click="goSystemConsole">
        <h3>用户系统管理</h3>
        <p>管理系统用户、查看统计数据和用户权限</p>
        <div class="card-features">
          <span class="feature-tag">用户管理</span>
          <span class="feature-tag">数据统计</span>
          <span class="feature-tag">权限控制</span>
        </div>
      </section>

      <section class="card admin-card" @click="goKnowledgeManagement">
        <h3>学习管理</h3>
        <p>管理知识库、课程内容和学习资源</p>
        <div class="card-features">
          <span class="feature-tag">知识图谱</span>
          <span class="feature-tag">内容管理</span>
          <span class="feature-tag">学习统计</span>
        </div>
      </section>

      <section class="card admin-card" @click="goUserFunctionTest">
        <h3>用户功能测试</h3>
        <p>体验普通用户功能，进行功能测试和调试</p>
        <div class="card-features">
          <span class="feature-tag">学习界面</span>
          <span class="feature-tag">个人中心</span>
          <span class="feature-tag">功能测试</span>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'AdminHomeView',
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

    const goProfile = () => {
      router.push('/admin/profile')
    }

    const goSystemConsole = () => {
      router.push('/admin/system')
    }

    const goKnowledgeManagement = () => {
      router.push('/admin/knowledge')
    }

    const goUserFunctionTest = () => {
      router.push('/dashboard')
    }

    return {
      user,
      logout,
      goProfile,
      goSystemConsole,
      goKnowledgeManagement,
      goUserFunctionTest
    }
  }
}
</script>

<style scoped>
.admin-home-page {
  min-height: 100vh;
  background-color: #ffffff;
  padding: 24px 16px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
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
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 999px;
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
  color: #f9fafb;
}

.btn.danger:hover {
  background-color: #b91c1c;
  transform: translateY(-1px);
}

.content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 32px 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  text-align: center;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
  border-color: #e0e0e0;
}

.admin-card {
  background: white;
  color: #1e40af;
  border: 2px solid #dbeafe;
  position: relative;
  overflow: hidden;
}

.admin-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 50%, #93c5fd 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.admin-card:hover::before {
  opacity: 1;
}

.admin-card:nth-child(2)::before {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 50%, #f59e0b 100%);
}

.admin-card:nth-child(3)::before {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 50%, #10b981 100%);
}


.card h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1e40af;
  position: relative;
  z-index: 1;
}

.card p {
  font-size: 15px;
  color: #3730a3;
  line-height: 1.5;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.card-features {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
  position: relative;
  z-index: 1;
}

.feature-tag {
  background: #dbeafe;
  color: #2563eb;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #bfdbfe;
}

@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .top-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .right {
    align-self: stretch;
    justify-content: flex-end;
  }
}
</style>