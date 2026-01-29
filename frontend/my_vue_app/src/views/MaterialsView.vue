<template>
  <div class="materials-page">
    <header class="top-bar">
      <div class="left">
        <h1>学习资料</h1>
      </div>
      <div class="right" v-if="isAdmin">
        <button class="btn btn-primary" @click="showUploadDialog = true">
          上传资料
        </button>
      </div>
    </header>

    <main class="content">
      <!-- 组件筛选 -->
      <div class="filter-section">
        <div class="filter-label">按知识点筛选：</div>
        <div class="filter-buttons">
          <button 
            class="filter-btn" 
            :class="{ active: selectedComponent === '' }"
            @click="selectedComponent = ''"
          >
            全部
          </button>
          <button 
            v-for="comp in availableComponents" 
            :key="comp"
            class="filter-btn"
            :class="{ active: selectedComponent === comp }"
            @click="selectedComponent = comp"
          >
            {{ getComponentDisplayName(comp) }}
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 资料列表 -->
      <div v-else-if="filteredMaterials.length > 0" class="materials-grid">
        <div 
          v-for="material in filteredMaterials" 
          :key="material.id"
          class="material-card"
        >
          <div class="material-header">
            <h3>{{ material.title }}</h3>
            <div class="material-badge" v-if="material.component_name">
              {{ getComponentDisplayName(material.component_name) }}
            </div>
          </div>
          <p class="material-description">{{ material.description || '暂无描述' }}</p>
          <div class="material-meta">
            <span class="meta-item">
              <span class="meta-label">文件类型:</span>
              {{ material.file_type.toUpperCase() }}
            </span>
            <span class="meta-item">
              <span class="meta-label">文件大小:</span>
              {{ formatFileSize(material.file_size) }}
            </span>
            <span class="meta-item" v-if="material.creator">
              <span class="meta-label">上传者:</span>
              {{ material.creator.username }}
            </span>
          </div>
          <div class="material-footer">
            <span class="time-info">
              {{ formatDate(material.created_at) }}
            </span>
            <div class="material-actions">
              <button 
                class="btn-small btn-primary"
                @click="downloadMaterial(material)"
              >
                下载
              </button>
              <button 
                v-if="isAdmin"
                class="btn-small btn-secondary"
                @click="editMaterial(material)"
              >
                编辑
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <h3>暂无资料</h3>
        <p v-if="isAdmin">点击"上传资料"按钮添加学习资料</p>
        <p v-else>当前筛选条件下没有可用的学习资料</p>
      </div>
    </main>

    <!-- 上传/编辑对话框 -->
    <div v-if="showUploadDialog || showEditDialog" class="modal-overlay" @click.self="closeDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ showEditDialog ? '编辑资料' : '上传资料' }}</h3>
          <button @click="closeDialog" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>资料标题 *</label>
            <input 
              v-model="materialForm.title" 
              type="text" 
              class="form-input"
              placeholder="请输入资料标题"
            />
          </div>
          <div class="form-group">
            <label>资料描述</label>
            <textarea 
              v-model="materialForm.description" 
              class="form-textarea"
              placeholder="请输入资料描述"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label>关联知识点（组件）</label>
            <select v-model="materialForm.component_name" class="form-select">
              <option value="other">其他</option>
              <option 
                v-for="comp in componentOptions" 
                :key="comp.id"
                :value="comp.id"
              >
                {{ comp.name }}
              </option>
            </select>
          </div>
          <div class="form-group" v-if="!showEditDialog">
            <label>选择文件 *</label>
            <input 
              type="file" 
              accept=".pdf"
              @change="handleFileSelect"
              class="form-input"
            />
            <p class="form-hint">仅支持PDF格式文件</p>
          </div>
          <div v-if="uploading" class="upload-progress">
            <p>上传中... {{ uploadProgress }}%</p>
          </div>
        </div>
        <div class="modal-footer">
          <button 
            v-if="showEditDialog"
            @click="deleteMaterial(editingMaterial)"
            class="btn btn-danger"
          >
            删除
          </button>
          <button @click="closeDialog" class="btn btn-secondary">取消</button>
          <button 
            @click="saveMaterial" 
            class="btn btn-primary"
            :disabled="!materialForm.title || (!showEditDialog && !selectedFile) || uploading"
          >
            {{ showEditDialog ? '保存' : '上传' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5005/api'

export default {
  name: 'MaterialsView',
  setup() {
    const route = useRoute()
    const loading = ref(false)
    const materials = ref([])
    const selectedComponent = ref('')
    const showUploadDialog = ref(false)
    const showEditDialog = ref(false)
    const selectedFile = ref(null)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const editingMaterial = ref(null)
    const isAdmin = ref(false)

    const materialForm = ref({
      title: '',
      description: '',
      component_name: ''
    })

    // 组件列表（从后端获取）
    const componentOptions = ref([])

    // 组件名称映射（用于显示）
    const getComponentDisplayName = (componentId) => {
      const comp = componentOptions.value.find(c => c.id === componentId)
      return comp ? comp.name : componentId
    }

    // 获取所有可用的组件名称（用于筛选显示）
    const availableComponents = computed(() => {
      const components = new Set()
      materials.value.forEach(m => {
        if (m.component_name) {
          components.add(m.component_name)
        }
      })
      return Array.from(components).sort()
    })

    // 获取组件选项列表（从后端）
    const fetchComponents = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/materials/components`, {
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          }
        })
        const data = await response.json()
        if (data.code === 200) {
          componentOptions.value = data.data || []
        }
      } catch (err) {
        console.error('获取组件列表失败:', err)
      }
    }

    // 筛选后的资料列表
    const filteredMaterials = computed(() => {
      if (!selectedComponent.value) {
        return materials.value
      }
      return materials.value.filter(m => m.component_name === selectedComponent.value)
    })

    // 获取认证头
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token')
      if (!token) return {}
      return { Authorization: `Bearer ${token}` }
    }

    // 检查是否为管理员
    const checkAdmin = () => {
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          isAdmin.value = user.is_admin || false
        }
      } catch (e) {
        isAdmin.value = false
      }
    }


    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    }

    // 获取资料列表
    const fetchMaterials = async () => {
      try {
        loading.value = true
        const response = await fetch(`${API_BASE_URL}/materials`, {
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          }
        })
        const data = await response.json()
        if (data.code === 200) {
          materials.value = data.data || []
        }
      } catch (err) {
        console.error('获取资料列表失败:', err)
        alert('获取资料列表失败')
      } finally {
        loading.value = false
      }
    }

    // 下载资料
    const downloadMaterial = async (material) => {
      try {
        const response = await fetch(`${API_BASE_URL}/materials/${material.id}/download`, {
          headers: {
            ...getAuthHeaders()
          }
        })
        
        if (response.ok) {
          const blob = await response.blob()
          
          // 使用title作为下载文件名，如果没有title则使用file_name
          let filename = material.title || material.file_name || '资料'
          if (!filename.toLowerCase().endsWith('.pdf')) {
            filename = filename + '.pdf'
          }
          
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = filename
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          window.URL.revokeObjectURL(url)
        } else {
          // 尝试解析错误信息
          try {
            const data = await response.json()
            alert(data.message || '下载失败')
          } catch {
            alert('下载失败')
          }
        }
      } catch (err) {
        console.error('下载失败:', err)
        alert('下载失败: ' + err.message)
      }
    }

    // 选择文件
    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        if (file.type !== 'application/pdf') {
          alert('只支持PDF文件')
          return
        }
        selectedFile.value = file
      }
    }

    // 上传文件
    const uploadFile = async () => {
      if (!selectedFile.value) {
        alert('请选择文件')
        return
      }

      try {
        uploading.value = true
        uploadProgress.value = 0

        const formData = new FormData()
        formData.append('file', selectedFile.value)
        // 传递组件名称用于分类存储
        formData.append('component_name', materialForm.value.component_name || 'other')

        // 注意：上传文件时不要设置Content-Type，让浏览器自动设置
        const token = localStorage.getItem('token')
        const headers = {}
        if (token) {
          headers['Authorization'] = `Bearer ${token}`
        }

        const response = await fetch(`${API_BASE_URL}/materials/upload`, {
          method: 'POST',
          headers: headers,
          body: formData
        })

        const data = await response.json()
        if (data.code === 200) {
          return data.data
        } else {
          alert(data.message || '上传失败')
          return null
        }
      } catch (err) {
        console.error('上传失败:', err)
        alert('上传失败: ' + err.message)
        return null
      } finally {
        uploading.value = false
        uploadProgress.value = 0
      }
    }

    // 保存资料
    const saveMaterial = async () => {
      if (!materialForm.value.title.trim()) {
        alert('请输入资料标题')
        return
      }

      try {
        if (showEditDialog.value) {
          // 编辑模式
          const response = await fetch(`${API_BASE_URL}/materials/${editingMaterial.value.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              ...getAuthHeaders()
            },
            body: JSON.stringify(materialForm.value)
          })
          const data = await response.json()
          if (data.code === 200) {
            alert('更新成功')
            closeDialog()
            fetchMaterials()
          } else {
            alert(data.message || '更新失败')
          }
        } else {
          // 上传模式
          const uploadResult = await uploadFile()
          if (!uploadResult) return

          const response = await fetch(`${API_BASE_URL}/materials`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...getAuthHeaders()
            },
            body: JSON.stringify({
              title: materialForm.value.title,
              description: materialForm.value.description,
              component_name: materialForm.value.component_name === 'other' ? null : materialForm.value.component_name,
              file_path: uploadResult.file_path,
              file_name: uploadResult.file_name,
              file_size: uploadResult.file_size,
              file_type: uploadResult.file_type
            })
          })
          const data = await response.json()
          if (data.code === 200) {
            alert('上传成功')
            closeDialog()
            fetchMaterials()
          } else {
            alert(data.message || '创建失败')
          }
        }
      } catch (err) {
        console.error('保存失败:', err)
        alert('保存失败')
      }
    }

    // 编辑资料
    const editMaterial = (material) => {
      editingMaterial.value = material
      materialForm.value = {
        title: material.title,
        description: material.description || '',
        component_name: material.component_name || 'other'
      }
      showEditDialog.value = true
    }

    // 删除资料
    const deleteMaterial = async (material) => {
      if (!material) {
        material = editingMaterial.value
      }
      if (!material) return
      
      if (!confirm(`确定要删除资料"${material.title}"吗？`)) {
        return
      }

      try {
        const response = await fetch(`${API_BASE_URL}/materials/${material.id}`, {
          method: 'DELETE',
          headers: {
            ...getAuthHeaders()
          }
        })
        const data = await response.json()
        if (data.code === 200) {
          alert('删除成功')
          closeDialog()
          fetchMaterials()
        } else {
          alert(data.message || '删除失败')
        }
      } catch (err) {
        console.error('删除失败:', err)
        alert('删除失败')
      }
    }

    // 关闭对话框
    const closeDialog = () => {
      showUploadDialog.value = false
      showEditDialog.value = false
      editingMaterial.value = null
      selectedFile.value = null
      materialForm.value = {
        title: '',
        description: '',
        component_name: 'other'
      }
    }

    onMounted(() => {
      checkAdmin()
      fetchComponents()
      // 如果URL中有component查询参数，设置筛选
      if (route.query.component) {
        selectedComponent.value = route.query.component
      }
      fetchMaterials()
    })

    return {
      loading,
      materials,
      selectedComponent,
      filteredMaterials,
      availableComponents,
      componentOptions,
      showUploadDialog,
      showEditDialog,
      materialForm,
      selectedFile,
      uploading,
      uploadProgress,
      isAdmin,
      getComponentDisplayName,
      fetchComponents,
      formatFileSize,
      formatDate,
      downloadMaterial,
      handleFileSelect,
      saveMaterial,
      editMaterial,
      deleteMaterial,
      closeDialog
    }
  }
}
</script>

<style scoped>
.materials-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 20px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.top-bar h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  color: #2c3e50;
}

.subtitle {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.right {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #edf2f7;
}

.btn-danger {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.btn-danger:hover {
  background: #fecaca;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

.content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 6px;
  font-size: 13px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.filter-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.materials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.material-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;
}

.material-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #667eea;
}

.material-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 12px;
}

.material-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
  flex: 1;
}

.material-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: #ede9fe;
  color: #6d28d9;
  white-space: nowrap;
}

.material-description {
  color: #718096;
  font-size: 14px;
  margin: 0 0 16px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.material-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #4a5568;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-label {
  color: #718096;
}

.material-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.time-info {
  font-size: 12px;
  color: #718096;
}

.material-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.empty-state p {
  margin: 0;
  color: #718096;
}

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
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
}

.modal-close {
  background: none;
  border: none;
  font-size: 28px;
  color: #718096;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f7fafc;
  color: #2c3e50;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.form-hint {
  font-size: 12px;
  color: #718096;
  margin: 4px 0 0 0;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #2d3748;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.upload-progress {
  padding: 12px;
  background: #f7fafc;
  border-radius: 6px;
  text-align: center;
  color: #4a5568;
}
</style>
