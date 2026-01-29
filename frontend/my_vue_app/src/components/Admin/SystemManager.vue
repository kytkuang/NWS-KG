<template>
  <div class="system-manager">
    <div class="section-header">
      <h2>用户系统管理</h2>
    </div>

    <main class="system-content">
      <!-- 用户统计卡片 -->
      <section class="stats-section">
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.total_users }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.active_users }}</div>
            <div class="stat-label">活跃用户</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.admin_users }}</div>
            <div class="stat-label">管理员</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.recent_users }}</div>
            <div class="stat-label">最近7天注册</div>
          </div>
        </div>
      </section>

      <!-- 用户管理 -->
      <section class="users-section">
        <div class="section-header-inner">
          <h3>用户管理</h3>
          <button class="btn primary" @click="openCreateUserModal">
            创建用户
          </button>
        </div>

        <!-- 搜索和筛选 -->
        <div class="filters-bar">
          <div class="search-box">
            <input
              v-model.trim="searchQuery"
              type="text"
              placeholder="搜索用户名或邮箱..."
              @input="debouncedSearch"
            />
            <button class="search-btn" @click="searchUsers">
              搜索
            </button>
          </div>

          <div class="filter-selects">
            <select v-model="statusFilter" @change="loadUsers">
              <option value="">所有状态</option>
              <option value="active">活跃用户</option>
              <option value="inactive">非活跃用户</option>
            </select>

            <select v-model="roleFilter" @change="loadUsers">
              <option value="">所有角色</option>
              <option value="admin">管理员</option>
              <option value="user">普通用户</option>
            </select>
          </div>
        </div>

        <!-- 用户列表 -->
        <div class="users-table-container">
          <table class="users-table" v-if="users.length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>状态</th>
                <th>注册时间</th>
                <th>最后登录</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>
                  <span class="role-badge" :class="{ admin: user.is_admin }">
                    {{ user.is_admin ? '管理员' : '普通用户' }}
                  </span>
                </td>
                <td>
                  <span class="status-badge" :class="{ active: user.is_active }">
                    {{ user.is_active ? '活跃' : '停用' }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>{{ user.last_login ? formatDate(user.last_login) : '从未登录' }}</td>
                <td>
                  <div class="action-buttons">
                    <button class="action-btn edit" @click="editUser(user)" title="编辑">
                      编辑
                    </button>
                    <button class="action-btn delete" @click="deleteUser(user)" title="删除">
                      删除
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-else-if="!loading" class="empty-state">
            <p>暂无用户数据</p>
          </div>

          <div v-if="loading" class="loading-state">
            <p>加载中...</p>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination" v-if="totalPages > 1">
          <button
            class="page-btn"
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
          >
            上一页
          </button>

          <span class="page-info">
            第 {{ currentPage }} 页，共 {{ totalPages }} 页
          </span>

          <button
            class="page-btn"
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === totalPages"
          >
            下一页
          </button>
        </div>
      </section>
    </main>

    <!-- 创建/编辑用户模态框 -->
    <div v-if="showUserModal" class="modal-overlay" @click="closeUserModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑用户' : '创建用户' }}</h3>
          <button class="close-btn" @click="closeUserModal">✕</button>
        </div>

        <form @submit.prevent="saveUser" class="user-form">
          <div class="form-group">
            <label>用户名</label>
            <input
              v-model.trim="userForm.username"
              type="text"
              required
              :disabled="isEditing"
              placeholder="输入用户名"
            />
          </div>

          <div class="form-group">
            <label>邮箱</label>
            <input
              v-model.trim="userForm.email"
              type="email"
              required
              placeholder="输入邮箱地址"
            />
          </div>

          <div v-if="!isEditing" class="form-group">
            <label>初始密码</label>
            <input
              v-model="userForm.password"
              type="password"
              required
              placeholder="输入初始密码"
            />
          </div>

          <div v-if="isEditing" class="form-group">
            <label>
              <input type="checkbox" v-model="resetPasswordFlag" />
              重置密码
            </label>
            <div v-if="resetPasswordFlag" class="password-input">
              <input
                v-model="userForm.password"
                type="password"
                placeholder="输入新密码（留空将自动生成）"
              />
            </div>
          </div>

          <div class="form-group">
            <label>角色</label>
            <select v-model="userForm.is_admin">
              <option :value="false">普通用户</option>
              <option :value="true">管理员</option>
            </select>
          </div>

          <div class="form-group">
            <label>状态</label>
            <select v-model="userForm.is_active">
              <option :value="true">活跃</option>
              <option :value="false">停用</option>
            </select>
          </div>

          <div class="form-actions">
            <button type="button" class="btn secondary" @click="closeUserModal">
              取消
            </button>
            <button type="submit" class="btn primary" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'SystemManager',
  setup() {
    // 数据状态
    const users = ref([])
    const loading = ref(false)
    const saving = ref(false)

    // 统计数据
    const stats = ref({
      total_users: 0,
      active_users: 0,
      admin_users: 0,
      recent_users: 0
    })

    // 搜索和筛选
    const searchQuery = ref('')
    const statusFilter = ref('')
    const roleFilter = ref('')

    // 分页
    const currentPage = ref(1)
    const totalPages = ref(1)
    const perPage = 20

    // 模态框状态
    const showUserModal = ref(false)
    const isEditing = ref(false)
    const selectedUser = ref(null)

    // 表单数据
    const userForm = ref({
      username: '',
      email: '',
      password: '',
      is_admin: false,
      is_active: true
    })

    const resetPasswordFlag = ref(false)

    // 防抖搜索
    let searchTimeout = null
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        currentPage.value = 1
        loadUsers()
      }, 500)
    }

    const authHeaders = () => {
      const token = localStorage.getItem('token')
      return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      }
    }

    const loadStats = async () => {
      try {
        const response = await fetch('/api/admin/stats', {
          headers: authHeaders()
        })

        const data = await response.json()
        if (data.success) {
          stats.value = data.stats
        } else {
          console.error('获取统计信息失败:', data.message)
        }
      } catch (error) {
        console.error('加载统计信息失败:', error)
      }
    }

    const loadUsers = async () => {
      try {
        loading.value = true

        const params = new URLSearchParams({
          page: currentPage.value,
          per_page: perPage,
          ...(searchQuery.value && { search: searchQuery.value }),
          ...(statusFilter.value && { status: statusFilter.value }),
          ...(roleFilter.value && { role: roleFilter.value })
        })

        const response = await fetch(`/api/admin/users?${params}`, {
          headers: authHeaders()
        })

        const data = await response.json()
        if (data.success) {
          users.value = data.users
          totalPages.value = data.pagination.pages
        } else {
          alert('加载用户列表失败：' + data.message)
        }
      } catch (error) {
        console.error('加载用户列表失败:', error)
        alert('加载用户列表失败')
      } finally {
        loading.value = false
      }
    }

    const searchUsers = () => {
      currentPage.value = 1
      loadUsers()
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadUsers()
      }
    }

    const openCreateUserModal = () => {
      isEditing.value = false
      userForm.value = {
        username: '',
        email: '',
        password: '',
        is_admin: false,
        is_active: true
      }
      showUserModal.value = true
    }

    const editUser = (user) => {
      isEditing.value = true
      selectedUser.value = user
      resetPasswordFlag.value = false
      userForm.value = {
        username: user.username,
        email: user.email,
        password: '',
        is_admin: user.is_admin,
        is_active: user.is_active
      }
      showUserModal.value = true
    }

    const closeUserModal = () => {
      showUserModal.value = false
      resetPasswordFlag.value = false
      userForm.value = {
        username: '',
        email: '',
        password: '',
        is_admin: false,
        is_active: true
      }
    }

    const saveUser = async () => {
      try {
        saving.value = true

        const url = isEditing.value
          ? `/api/admin/users/${selectedUser.value.id}`
          : '/api/admin/users'

        const method = isEditing.value ? 'PUT' : 'POST'

        const payload = { ...userForm.value }
        if (isEditing.value && !resetPasswordFlag.value) {
          delete payload.password
        }

        const response = await fetch(url, {
          method,
          headers: authHeaders(),
          body: JSON.stringify(payload)
        })

        const data = await response.json()
        if (data.success) {
          alert(isEditing.value ? '用户更新成功' : '用户创建成功')
          closeUserModal()
          loadUsers()
          loadStats()
        } else {
          alert('保存失败：' + data.message)
        }
      } catch (error) {
        console.error('保存用户失败:', error)
        alert('保存失败')
      } finally {
        saving.value = false
      }
    }

    const deleteUser = async (user) => {
      if (!confirm(`确定要永久删除用户"${user.username}"吗？\n\n此操作不可恢复！`)) {
        return
      }

      try {
        const response = await fetch(`/api/admin/users/${user.id}?force=true`, {
          method: 'DELETE',
          headers: authHeaders()
        })

        const data = await response.json()
        if (data.success) {
          alert('用户已被永久删除')
          loadUsers()
          loadStats()
        } else {
          alert('删除用户失败：' + data.message)
        }
      } catch (error) {
        console.error('删除用户失败:', error)
        alert('删除用户失败')
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }

    onMounted(() => {
      loadStats()
      loadUsers()
    })

    return {
      users,
      stats,
      loading,
      saving,
      searchQuery,
      statusFilter,
      roleFilter,
      currentPage,
      totalPages,
      showUserModal,
      isEditing,
      userForm,
      resetPasswordFlag,
      debouncedSearch,
      loadUsers,
      searchUsers,
      changePage,
      openCreateUserModal,
      editUser,
      closeUserModal,
      saveUser,
      deleteUser,
      formatDate
    }
  }
}
</script>

<style scoped>
.system-manager {
  width: 100%;
  height: 100%;
}

.section-header {
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.system-content {
  width: 100%;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  padding: 24px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  border-color: #3b82f6;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.users-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
}

.section-header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header-inner h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn.primary {
  background-color: #007bff;
  color: white;
}

.btn.primary:hover {
  background-color: #0056b3;
  transform: translateY(-1px);
}

.btn.secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn.secondary:hover {
  background: #d1d5db;
}

.filters-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  flex: 1;
  min-width: 300px;
}

.search-box input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px 0 0 6px;
  font-size: 14px;
  outline: none;
}

.search-box input:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.search-btn {
  padding: 10px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 0 6px 6px 0;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.search-btn:hover {
  background: #0056b3;
}

.filter-selects {
  display: flex;
  gap: 12px;
}

.filter-selects select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  outline: none;
  cursor: pointer;
}

.filter-selects select:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.users-table-container {
  margin-bottom: 24px;
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.users-table th,
.users-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.users-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.role-badge,
.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge:not(.active) {
  background: #fee2e2;
  color: #dc2626;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
  background: #f3f4f6;
  color: #374151;
}

.action-btn.edit:hover {
  background: #dbeafe;
  color: #2563eb;
}

.action-btn.delete:hover {
  background: #fee2e2;
  color: #dc2626;
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 48px;
  color: #6b7280;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #007bff;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #111827;
}

.user-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-group input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

.password-input {
  margin-top: 8px;
  padding-left: 24px;
}

.form-group input:disabled {
  background: #f9fafb;
  color: #6b7280;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
  }

  .search-box {
    min-width: auto;
  }

  .users-table-container {
    overflow-x: auto;
  }

  .users-table {
    min-width: 800px;
  }

  .modal-content {
    width: 95%;
    margin: 16px;
  }
}
</style>
