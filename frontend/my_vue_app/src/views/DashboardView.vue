<template>
  <div class="dashboard-page">
    <header class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">欢迎使用知识图谱学习系统</h1>
        <p class="hero-subtitle">探索知识网络，提升学习效率，发现更多学习乐趣</p>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">{{ user?.study_hours || 0 }}</span>
            <span class="stat-label">学习时长</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ user?.completed_tasks || 0 }}</span>
            <span class="stat-label">完成任务</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ user?.study_streak || 0 }}</span>
            <span class="stat-label">连续学习</span>
          </div>
        </div>
      </div>
      <div class="hero-actions">
        <button v-if="user?.is_admin" class="btn primary" @click="goBackToAdmin">返回管理员中心</button>
        <button class="btn ghost" @click="goProfile">个人中心</button>
      </div>
    </header>

    <main class="content">
      <div class="content-header">
        <h2>学习入口</h2>
        <p>选择您想要探索的学习方式</p>
      </div>

      <div class="learning-cards-grid">
        <section class="card learning-card" @click="goKnowledgeGraph">
          <h3>知识图谱</h3>
          <p>探索知识网络，深入理解概念关系</p>
        </section>

        <section class="card learning-card" @click="goLearningPath">
          <h3>学习路线</h3>
          <p>系统化的学习路径规划</p>
        </section>

        <section class="card learning-card" @click="goMaterials">
          <h3>学习资料</h3>
          <p>查看与学习路径相关的学习资料</p>
        </section>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'DashboardView',
  setup() {
    const router = useRouter()
    const user = ref(null)

    onMounted(() => {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        user.value = JSON.parse(storedUser)
      }
    })

    const goProfile = () => {
      router.push('/profile')
    }

    const goKnowledgeGraph = () => {
      router.push('/learn')
    }

    const goLearningPath = () => {
      router.push('/learning-path')
    }

    const goMaterials = () => {
      router.push('/materials')
    }

    const goBackToAdmin = () => {
      router.push('/admin')
    }

    return {
      user,
      goProfile,
      goKnowledgeGraph,
      goLearningPath,
      goMaterials,
      goBackToAdmin
    }
  }
}
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  padding: 0;
}

.hero-section {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  padding: 80px 24px 60px;
  color: #1e40af;
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid #93c5fd;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="1.5" fill="rgba(255,255,255,0.15)"/><circle cx="80" cy="80" r="1.5" fill="rgba(255,255,255,0.15)"/><circle cx="60" cy="30" r="1" fill="rgba(255,255,255,0.15)"/></svg>');
  opacity: 0.4;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 42px;
  font-weight: 800;
  margin-bottom: 16px;
  line-height: 1.2;
  color: #1e40af;
  letter-spacing: -0.5px;
}

.hero-subtitle {
  font-size: 18px;
  color: #3730a3;
  margin-bottom: 48px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
  opacity: 0.9;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-bottom: 48px;
}

.stat-item {
  text-align: center;
  padding: 0 16px;
}

.stat-number {
  display: block;
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 6px;
  color: #1e40af;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #3730a3;
  font-weight: 500;
  opacity: 0.8;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  position: relative;
  z-index: 2;
}

.btn {
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.btn.primary {
  background-color: #2563eb;
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.btn.primary:hover {
  background-color: #1d4ed8;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35);
}

.btn.ghost {
  background-color: rgba(255, 255, 255, 0.95);
  color: #2563eb;
  border: 2px solid #2563eb;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15);
}

.btn.ghost:hover {
  background-color: #2563eb;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
}

.content {
  max-width: 1200px;
  margin: -40px auto 60px;
  padding: 60px 24px;
  background: white;
  border-radius: 24px 24px 0 0;
  box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 2;
}

.content-header {
  text-align: center;
  margin-bottom: 48px;
}

.content-header h2 {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.content-header p {
  font-size: 16px;
  color: #6b7280;
  opacity: 0.9;
}

.learning-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.learning-card {
  text-align: center;
  padding: 40px 32px;
  cursor: pointer;
  background: white;
  color: #1e40af;
  border-radius: 16px;
  border: 2px solid #dbeafe;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.learning-card::before {
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

.learning-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(37, 99, 235, 0.2);
  border-color: #3b82f6;
}

.learning-card:hover::before {
  opacity: 0.05;
}

.card-icon {
  font-size: 48px;
  margin-bottom: 20px;
  opacity: 0.9;
}

.learning-card h3 {
  font-size: 22px;
  margin-bottom: 16px;
  color: #1e40af;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

.learning-card p {
  font-size: 15px;
  color: #3730a3;
  line-height: 1.6;
  margin: 0;
  position: relative;
  z-index: 1;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-section {
    padding: 60px 20px 40px;
  }
  
  .hero-title {
    font-size: 32px;
  }
  
  .hero-subtitle {
    font-size: 16px;
    margin-bottom: 32px;
  }
  
  .hero-stats {
    gap: 32px;
    margin-bottom: 32px;
  }
  
  .stat-number {
    font-size: 28px;
  }
  
  .content {
    margin: -20px auto 40px;
    padding: 40px 20px;
    border-radius: 20px 20px 0 0;
  }
  
  .content-header h2 {
    font-size: 26px;
  }
  
  .learning-cards-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .learning-card {
    padding: 32px 24px;
  }
}

@media (min-width: 769px) {
  .learning-cards-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 480px) {
  .hero-stats {
    flex-direction: column;
    gap: 24px;
  }
  
  .stat-item {
    padding: 8px 0;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
  }
}
</style>