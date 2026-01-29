<template>
  <div class="auth-card">
    <h1 class="auth-title">登录</h1>
    <p class="auth-subtitle">欢迎回来，请输入账号信息</p>

    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">用户名或邮箱</label>
        <input
          id="username"
          v-model.trim="form.username"
          type="text"
          placeholder="请输入用户名或邮箱"
          required
        />
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          required
        />
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>

      <button class="btn primary" type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>

    <p class="switch-text">
      还没有账号？
      <a href="#" @click.prevent="$emit('switch-to-register')">去注册</a>
    </p>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// 根据你的后端实际地址修改
const API_BASE_URL = 'http://localhost:5005/api'

export default {
  name: 'LoginForm',
  emits: ['switch-to-register'],
  setup() {
    const router = useRouter()
    const route = useRoute()

    const form = ref({
      username: '',
      password: ''
    })
    const loading = ref(false)
    const error = ref('')

    const handleLogin = async () => {
      error.value = ''
      if (!form.value.username || !form.value.password) {
        error.value = '请填写用户名/邮箱和密码'
        return
      }

      loading.value = true
      try {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: form.value.username,
            password: form.value.password
          })
        })

        const data = await res.json()

        if (!res.ok || !data.success) {
          throw new Error(data.message || '登录失败')
        }

        // 保存 token 和用户信息
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))

        // 登录成功后根据角色跳转
        const redirect = route.query.redirect
        if (redirect) {
          router.replace(redirect)
        } else {
          // 根据用户角色跳转到对应页面
          const isAdmin = data.user && data.user.is_admin
          router.replace(isAdmin ? '/admin' : '/dashboard')
        }
      } catch (e) {
        error.value = e.message || '登录失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.auth-card {
  width: 100%;
  max-width: 420px;
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
  box-sizing: border-box;
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
