<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">注册</h1>
      <p class="auth-subtitle">创建一个新账号，开始使用知识图谱学习平台</p>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model.trim="form.username"
            type="text"
            placeholder="3-20 位字母、数字或下划线"
            required
          />
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model.trim="form.email"
            type="email"
            placeholder="请输入常用邮箱"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="至少 6 位密码"
            required
          />
        </div>

        <p v-if="error" class="error-text">{{ error }}</p>
        <p v-if="success" class="success-text">{{ success }}</p>

        <button class="btn primary" type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="switch-text">
        已有账号？
        <router-link to="/login">去登录</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// 根据你的后端实际地址修改
const API_BASE_URL = 'http://localhost:5005/api'

export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter()

    const form = ref({
      username: '',
      email: '',
      password: ''
    })
    const loading = ref(false)
    const error = ref('')
    const success = ref('')

    const handleRegister = async () => {
      error.value = ''
      success.value = ''

      if (!form.value.username || !form.value.email || !form.value.password) {
        error.value = '请填写所有必填项'
        return
      }

      loading.value = true
      try {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: form.value.username,
            email: form.value.email,
            password: form.value.password
          })
        })

        const data = await res.json()

        if (!res.ok || !data.success) {
          throw new Error(data.message || '注册失败')
        }

        // 注册成功：保存 token 和用户信息，并跳转到仪表盘
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))

        success.value = '注册成功，正在跳转...'

        setTimeout(() => {
          router.replace('/dashboard')
        }, 600)
      } catch (e) {
        error.value = e.message || '注册失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      error,
      success,
      handleRegister
    }
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ffffff;
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 460px;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 32px 28px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.auth-title {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 4px;
  color: #111827;
}

.auth-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  font-size: 14px;
  color: #4b5563;
  margin-bottom: 6px;
}

input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.btn {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: none;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.1s ease, background-color 0.2s ease;
}

.btn.primary {
  background-color: #007bff;
  color: #ffffff;
}

.btn.primary:hover {
  background-color: #0056b3;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.error-text {
  color: #dc2626;
  font-size: 13px;
  margin: 4px 0 10px;
}

.success-text {
  color: #16a34a;
  font-size: 13px;
  margin: 4px 0 10px;
}

.switch-text {
  margin-top: 16px;
  font-size: 14px;
  color: #6b7280;
  text-align: center;
}

.switch-text a {
  color: #2563eb;
  text-decoration: none;
}

.switch-text a:hover {
  text-decoration: underline;
}
</style>