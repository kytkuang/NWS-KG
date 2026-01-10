<template>
  <div class="learning-path-page">
    <header class="top-bar">
      <div class="left">
        <h1>学习路线</h1>
      </div>
      <div class="right">
        <button class="btn ghost" @click="goBack">返回</button>
      </div>
    </header>

    <main class="content">
      <section class="card">
        <h2>学习路线规划</h2>
        <p>学习路线功能正在开发中...</p>
        <div class="placeholder">
          <div class="icon">🚧</div>
          <p>敬请期待</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'LearningPathView',
  setup() {
    const router = useRouter()

    const goBack = () => {
      router.go(-1)
    }

    return {
      goBack
    }
  }
}
</script>

<style scoped>
.learning-path-page {
  min-height: 100vh;
  background-color: #ffffff;
  padding: 24px 16px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.top-bar h1 {
  font-size: 24px;
  margin-bottom: 4px;
}

.right {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
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

.content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 18px 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  text-align: center;
}

.card h2 {
  font-size: 18px;
  margin-bottom: 10px;
}

.placeholder {
  margin-top: 20px;
}

.icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.placeholder p {
  color: #6b7280;
  font-size: 14px;
}
</style>