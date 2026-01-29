<template>
  <div class="home-page">
    <header class="hero">
      <div class="hero-content">
        <h1>网络安全知识图谱学习平台</h1>
      </div>
    </header>

    <div class="auth-container">
      <LoginForm v-if="currentView === 'login'" @switch-to-register="currentView = 'register'" />
      <RegisterForm v-else @switch-to-login="currentView = 'login'" />
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import LoginForm from '@/components/User/LoginForm.vue'
import RegisterForm from '@/components/User/RegisterForm.vue'

export default {
  name: 'HomeView',
  components: {
    LoginForm,
    RegisterForm
  },
  setup() {
    const currentView = ref('login') // 默认显示登录界面

    return {
      currentView
    }
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: #ffffff;
  color: #333333;
}

.hero {
  padding: 60px 20px 20px;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.hero h1 {
  font-size: 34px;
  font-weight: 800;
  margin-bottom: 16px;
  color: #333333;
}

.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  min-height: calc(100vh - 200px);
}
</style>