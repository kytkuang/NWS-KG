<template>
  <div class="admin-page">
    <header class="top-bar">
      <div>
        <h1>知识管理</h1>
        <p>维护网络安全知识点及其关系，支撑学习路线与测验设计。</p>
      </div>
    </header>

    <main class="content">
      <section class="panel panel-left">
        <header class="panel-header">
          <div class="search-row">
            <input
              v-model.trim="query"
              class="search-input"
              type="text"
              placeholder="搜索知识点名称..."
            />
            <button class="btn small" @click="loadNodes">搜索</button>
            <button class="btn small ghost" @click="resetSearch">重置</button>
          </div>
          <button class="btn primary small" @click="startCreate">新增知识点</button>
        </header>

        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>名称</th>
                <th>类别</th>
                <th>来源</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in nodes" :key="item.id" :class="{ active: item.id === currentId }">
                <td>{{ item.id }}</td>
                <td>{{ item.name }}</td>
                <td>{{ item.category }}</td>
                <td>{{ item.source }}</td>
                <td>
                  <button class="link-btn" @click="selectNode(item)">编辑</button>
                  <button class="link-btn danger" @click="removeNode(item)">删除</button>
                </td>
              </tr>
              <tr v-if="!nodes.length">
                <td colspan="5" class="empty-cell">暂无数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="panel panel-right">
        <header class="panel-header">
          <h2>{{ editingMode === 'create' ? '新增知识点' : '编辑知识点' }}</h2>
        </header>

        <div v-if="form" class="form-wrapper">
          <div class="form-group">
            <label>名称</label>
            <input v-model.trim="form.name" type="text" placeholder="请输入知识点名称" />
          </div>

          <div class="form-group">
            <label>类别</label>
            <input v-model.trim="form.category" type="text" placeholder="如 tactic / technique / concept ..." />
          </div>

          <div class="form-group">
            <label>来源</label>
            <input v-model.trim="form.source" type="text" placeholder="如 mitre / custom ..." />
          </div>

          <div class="form-group">
            <label>Neo4j 业务 ID（可选）</label>
            <input v-model.trim="form.neo4j_id" type="text" placeholder="用于与图数据库节点对齐" />
          </div>

          <div class="form-group">
            <label>描述</label>
            <textarea
              v-model="form.description"
              rows="4"
              placeholder="补充对该知识点的说明，如用途、示例等"
            ></textarea>
          </div>

          <p v-if="error" class="error-text">{{ error }}</p>
          <p v-if="success" class="success-text">{{ success }}</p>

          <div class="form-actions">
            <button class="btn primary" @click="saveNode" :disabled="loading">
              {{ loading ? '保存中...' : '保存' }}
            </button>
            <button class="btn ghost" @click="startCreate">新增空白</button>
          </div>
        </div>
        <p v-else class="empty-cell">请选择左侧知识点或点击“新增知识点”。</p>
      </section>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

const API_BASE_URL = '/api/knowledge'

export default {
  name: 'AdminKnowledgeView',
  setup() {
    const nodes = ref([])
    const query = ref('')
    const currentId = ref(null)
    const form = ref(null)
    const editingMode = ref('create') // create | update
    const loading = ref(false)
    const error = ref('')
    const success = ref('')

    const authHeaders = () => {
      const token = localStorage.getItem('token')
      return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      }
    }

    const loadNodes = async () => {
      error.value = ''
      try {
        const params = new URLSearchParams()
        if (query.value) params.append('q', query.value)
        const res = await fetch(`${API_BASE_URL}/nodes?${params.toString()}`, {
          headers: authHeaders()
        })
        const data = await res.json()
        if (!res.ok || !data.success) {
          throw new Error(data.message || '加载知识点失败')
        }
        nodes.value = data.items || []
      } catch (e) {
        error.value = e.message || '加载知识点失败'
      }
    }

    const resetSearch = () => {
      query.value = ''
      loadNodes()
    }

    const startCreate = () => {
      editingMode.value = 'create'
      currentId.value = null
      error.value = ''
      success.value = ''
      form.value = {
        name: '',
        category: 'concept',
        source: 'custom',
        neo4j_id: '',
        description: ''
      }
    }

    const selectNode = (item) => {
      editingMode.value = 'update'
      currentId.value = item.id
      error.value = ''
      success.value = ''
      form.value = {
        name: item.name,
        category: item.category,
        source: item.source,
        neo4j_id: item.neo4j_id || '',
        description: item.description || ''
      }
    }

    const saveNode = async () => {
      if (!form.value || !form.value.name) {
        error.value = '名称不能为空'
        return
      }
      error.value = ''
      success.value = ''
      loading.value = true
      try {
        const payload = { ...form.value }
        const url =
          editingMode.value === 'update' && currentId.value
            ? `${API_BASE_URL}/nodes/${currentId.value}`
            : `${API_BASE_URL}/nodes`
        const method = editingMode.value === 'update' ? 'PUT' : 'POST'

        const res = await fetch(url, {
          method,
          headers: authHeaders(),
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (!res.ok || !data.success) {
          throw new Error(data.message || '保存失败')
        }
        success.value = '保存成功'
        await loadNodes()
        if (data.item) {
          currentId.value = data.item.id
          editingMode.value = 'update'
        }
      } catch (e) {
        error.value = e.message || '保存失败'
      } finally {
        loading.value = false
      }
    }

    const removeNode = async (item) => {
      if (!window.confirm(`确定要删除知识点「${item.name}」及其关系吗？`)) return
      error.value = ''
      success.value = ''
      try {
        const res = await fetch(`${API_BASE_URL}/nodes/${item.id}`, {
          method: 'DELETE',
          headers: authHeaders()
        })
        const data = await res.json()
        if (!res.ok || !data.success) {
          throw new Error(data.message || '删除失败')
        }
        if (currentId.value === item.id) {
          form.value = null
          currentId.value = null
        }
        await loadNodes()
      } catch (e) {
        error.value = e.message || '删除失败'
      }
    }

    onMounted(() => {
      loadNodes()
      startCreate()
    })

    return {
      nodes,
      query,
      currentId,
      form,
      editingMode,
      loading,
      error,
      success,
      loadNodes,
      resetSearch,
      startCreate,
      selectNode,
      saveNode,
      removeNode
    }
  }
}
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background-color: #ffffff;
  padding: 24px 16px;
}

.top-bar h1 {
  font-size: 24px;
  margin-bottom: 4px;
}

.top-bar p {
  font-size: 14px;
  color: #6b7280;
}

.content {
  margin-top: 18px;
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 16px;
}

.panel {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 16px 14px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.search-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-input {
  padding: 8px 10px;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  font-size: 13px;
  min-width: 180px;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.btn {
  border: none;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease, box-shadow 0.1s ease;
}

.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

.btn.primary {
  background-color: #007bff;
  color: #ffffff;
}

.btn.primary:hover {
  background-color: #0056b3;
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

.table-wrapper {
  margin-top: 8px;
  overflow: auto;
  max-height: 420px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead {
  background-color: #f3f4f6;
}

.data-table th,
.data-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}

.data-table tr.active {
  background-color: #eff6ff;
}

.empty-cell {
  text-align: center;
  color: #9ca3af;
  padding: 18px 0;
}

.link-btn {
  padding: 0;
  border: none;
  background: none;
  color: #2563eb;
  font-size: 12px;
  cursor: pointer;
  margin-right: 8px;
}

.link-btn.danger {
  color: #dc2626;
}

.form-wrapper {
  margin-top: 4px;
}

.form-group {
  margin-bottom: 10px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: #4b5563;
  margin-bottom: 4px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  font-size: 13px;
  outline: none;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.form-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.error-text {
  font-size: 12px;
  color: #dc2626;
  margin-top: 4px;
}

.success-text {
  font-size: 12px;
  color: #16a34a;
  margin-top: 4px;
}
</style>

