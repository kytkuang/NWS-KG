<template>
  <div class="add-content-manager">
    <div class="manager-container">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3>内容管理</h3>
        </div>
        <nav class="sidebar-nav">
          <button 
            class="nav-item" 
            :class="{ active: activeTab === 'graph' }"
            @click="activeTab = 'graph'"
          >
            <span class="nav-label">管理图谱</span>
          </button>
          <button 
            class="nav-item" 
            :class="{ active: activeTab === 'materials' }"
            @click="activeTab = 'materials'"
          >
            <span class="nav-label">管理资料</span>
          </button>
        </nav>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <!-- 管理图谱（暂未实现） -->
        <div v-if="activeTab === 'graph'" class="content-section">
          <div class="empty-state">
            <h3>管理图谱</h3>
            <p>该功能正在开发中，敬请期待</p>
          </div>
        </div>

        <!-- 管理资料 -->
        <div v-else-if="activeTab === 'materials'" class="content-section">
          <div class="section-header">
            <h2>资料管理</h2>
            <div class="header-actions">
              <button 
                v-if="selectedMaterials.length > 0"
                class="btn btn-secondary"
                @click="batchDownload"
              >
                批量下载 ({{ selectedMaterials.length }})
              </button>
              <button 
                v-if="selectedMaterials.length > 0"
                class="btn btn-danger"
                @click="batchDelete"
              >
                批量删除 ({{ selectedMaterials.length }})
              </button>
              <button class="btn btn-primary" @click="showUploadDialog = true">
                上传资料
              </button>
              <button class="btn btn-secondary" @click="showBatchUploadDialog = true">
                批量上传
              </button>
            </div>
          </div>

          <!-- 筛选 -->
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
          <div v-else-if="filteredMaterials.length > 0" class="materials-table">
            <table>
              <thead>
                <tr>
                  <th style="width: 40px;">
                    <input 
                      type="checkbox" 
                      :checked="allSelected"
                      @change="toggleSelectAll"
                    />
                  </th>
                  <th>标题</th>
                  <th>关联知识点</th>
                  <th>文件类型</th>
                  <th>文件大小</th>
                  <th>上传时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="material in filteredMaterials" :key="material.id">
                  <td>
                    <input 
                      type="checkbox" 
                      :value="material.id"
                      v-model="selectedMaterials"
                    />
                  </td>
                  <td>{{ material.title }}</td>
                  <td>
                    <span v-if="material.component_name" class="component-badge">
                      {{ getComponentDisplayName(material.component_name) }}
                    </span>
                    <span v-else class="text-muted">未关联</span>
                  </td>
                  <td>{{ material.file_type.toUpperCase() }}</td>
                  <td>{{ formatFileSize(material.file_size) }}</td>
                  <td>{{ formatDate(material.created_at) }}</td>
                  <td>
                    <div class="action-buttons">
                      <button 
                        class="btn-small btn-secondary"
                        @click="editMaterial(material)"
                      >
                        编辑
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <h3>暂无资料</h3>
            <p>点击"上传资料"按钮添加学习资料</p>
          </div>
        </div>
      </main>
    </div>

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
            <label>关联知识点</label>
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
            <p>上传中...</p>
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

    <!-- 批量上传对话框 -->
    <div v-if="showBatchUploadDialog" class="modal-overlay" @click.self="closeBatchUploadDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h3>批量上传资料</h3>
          <button @click="closeBatchUploadDialog" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>关联知识点</label>
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
          <div class="form-group">
            <label>选择文件 *</label>
            <input 
              type="file" 
              accept=".pdf"
              multiple
              @change="handleBatchFileSelect"
              class="form-input"
            />
            <p class="form-hint">仅支持PDF格式文件，可同时选择多个文件</p>
            <div v-if="batchUploadFiles.length > 0" class="file-list">
              <p>已选择 {{ batchUploadFiles.length }} 个文件：</p>
              <ul>
                <li v-for="(file, index) in batchUploadFiles" :key="index">
                  {{ file.name }}
                </li>
              </ul>
            </div>
          </div>
          <div v-if="uploading" class="upload-progress">
            <p>上传中...</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeBatchUploadDialog" class="btn btn-secondary">取消</button>
          <button 
            @click="batchUpload" 
            class="btn btn-primary"
            :disabled="batchUploadFiles.length === 0 || uploading"
          >
            上传
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5005/api'

export default {
  name: 'AddContentManager',
  setup() {
    const activeTab = ref('materials')
    const loading = ref(false)
    const materials = ref([])
    const selectedComponent = ref('')
    const showUploadDialog = ref(false)
    const showEditDialog = ref(false)
    const selectedFile = ref(null)
    const uploading = ref(false)
    const editingMaterial = ref(null)
    const componentOptions = ref([])

    const materialForm = ref({
      title: '',
      description: '',
      component_name: 'other'
    })

    const selectedMaterials = ref([])
    const showBatchUploadDialog = ref(false)
    const batchUploadFiles = ref([])

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

    // 筛选后的资料列表
    const filteredMaterials = computed(() => {
      if (!selectedComponent.value) {
        return materials.value
      }
      return materials.value.filter(m => m.component_name === selectedComponent.value)
    })

    // 全选/取消全选
    const allSelected = computed(() => {
      return filteredMaterials.value.length > 0 && 
             selectedMaterials.value.length === filteredMaterials.value.length
    })

    const toggleSelectAll = () => {
      if (allSelected.value) {
        selectedMaterials.value = []
      } else {
        selectedMaterials.value = filteredMaterials.value.map(m => m.id)
      }
    }

    // 获取认证头
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token')
      if (!token) return {}
      return { Authorization: `Bearer ${token}` }
    }

    // 获取组件显示名称
    const getComponentDisplayName = (componentId) => {
      const comp = componentOptions.value.find(c => c.id === componentId)
      return comp ? comp.name : componentId
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

    // 获取组件选项列表
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

        const formData = new FormData()
        formData.append('file', selectedFile.value)
        // 传递组件名称用于分类存储
        formData.append('component_name', materialForm.value.component_name || 'other')

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

    // 批量删除
    const batchDelete = async () => {
      if (selectedMaterials.value.length === 0) {
        alert('请选择要删除的资料')
        return
      }

      if (!confirm(`确定要删除选中的 ${selectedMaterials.value.length} 个资料吗？`)) {
        return
      }

      try {
        let successCount = 0
        let failCount = 0

        for (const materialId of selectedMaterials.value) {
          try {
            const response = await fetch(`${API_BASE_URL}/materials/${materialId}`, {
              method: 'DELETE',
              headers: {
                ...getAuthHeaders()
              }
            })
            const data = await response.json()
            if (data.code === 200) {
              successCount++
            } else {
              failCount++
            }
          } catch (err) {
            failCount++
            console.error(`删除资料 ${materialId} 失败:`, err)
          }
        }

        alert(`删除完成：成功 ${successCount} 个，失败 ${failCount} 个`)
        selectedMaterials.value = []
        fetchMaterials()
      } catch (err) {
        console.error('批量删除失败:', err)
        alert('批量删除失败')
      }
    }

    // 批量下载
    const batchDownload = async () => {
      if (selectedMaterials.value.length === 0) {
        alert('请选择要下载的资料')
        return
      }

      try {
        for (const materialId of selectedMaterials.value) {
          const material = materials.value.find(m => m.id === materialId)
          if (!material) continue

          try {
            const response = await fetch(`${API_BASE_URL}/materials/${materialId}/download`, {
              headers: {
                ...getAuthHeaders()
              }
            })

            if (response.ok) {
              const blob = await response.blob()
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

              // 延迟一下，避免浏览器阻止多个下载
              await new Promise(resolve => setTimeout(resolve, 200))
            }
          } catch (err) {
            console.error(`下载资料 ${materialId} 失败:`, err)
          }
        }

        alert(`已开始下载 ${selectedMaterials.value.length} 个文件`)
      } catch (err) {
        console.error('批量下载失败:', err)
        alert('批量下载失败')
      }
    }

    // 批量上传文件选择
    const handleBatchFileSelect = (event) => {
      const files = Array.from(event.target.files)
      const pdfFiles = files.filter(file => file.type === 'application/pdf')
      
      if (pdfFiles.length !== files.length) {
        alert('只支持PDF文件，已过滤非PDF文件')
      }

      batchUploadFiles.value = pdfFiles
    }

    // 批量上传
    const batchUpload = async () => {
      if (batchUploadFiles.value.length === 0) {
        alert('请选择要上传的文件')
        return
      }

      try {
        uploading.value = true
        let successCount = 0
        let failCount = 0

        for (const file of batchUploadFiles.value) {
          try {
            // 上传文件
            const formData = new FormData()
            formData.append('file', file)
            formData.append('component_name', materialForm.value.component_name || 'other')

            const token = localStorage.getItem('token')
            const headers = {}
            if (token) {
              headers['Authorization'] = `Bearer ${token}`
            }

            const uploadResponse = await fetch(`${API_BASE_URL}/materials/upload`, {
              method: 'POST',
              headers: headers,
              body: formData
            })

            const uploadData = await uploadResponse.json()
            if (uploadData.code === 200) {
              // 创建资料记录
              const createResponse = await fetch(`${API_BASE_URL}/materials`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  ...getAuthHeaders()
                },
                body: JSON.stringify({
                  title: file.name.replace(/\.pdf$/i, ''),
                  description: '',
                  component_name: materialForm.value.component_name === 'other' ? null : materialForm.value.component_name,
                  file_path: uploadData.data.file_path,
                  file_name: uploadData.data.file_name,
                  file_size: uploadData.data.file_size,
                  file_type: uploadData.data.file_type
                })
              })

              const createData = await createResponse.json()
              if (createData.code === 200) {
                successCount++
              } else {
                failCount++
              }
            } else {
              failCount++
            }
          } catch (err) {
            failCount++
            console.error(`上传文件 ${file.name} 失败:`, err)
          }
        }

        alert(`批量上传完成：成功 ${successCount} 个，失败 ${failCount} 个`)
        closeBatchUploadDialog()
        fetchMaterials()
      } catch (err) {
        console.error('批量上传失败:', err)
        alert('批量上传失败')
      } finally {
        uploading.value = false
      }
    }

    // 关闭批量上传对话框
    const closeBatchUploadDialog = () => {
      showBatchUploadDialog.value = false
      batchUploadFiles.value = []
      materialForm.value = {
        title: '',
        description: '',
        component_name: 'other'
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
      fetchComponents()
      fetchMaterials()
    })

    return {
      activeTab,
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
      getComponentDisplayName,
      formatFileSize,
      formatDate,
      handleFileSelect,
      saveMaterial,
      editMaterial,
      deleteMaterial,
      closeDialog,
      selectedMaterials,
      allSelected,
      toggleSelectAll,
      batchDelete,
      batchDownload,
      showBatchUploadDialog,
      batchUploadFiles,
      handleBatchFileSelect,
      batchUpload,
      closeBatchUploadDialog
    }
  }
}
</script>

<style scoped>
.add-content-manager {
  width: 100%;
  height: 100%;
  background: #f5f7fa;
}

.manager-container {
  display: flex;
  height: calc(100vh - 200px);
  min-height: 600px;
}

/* 侧边栏 */
.sidebar {
  width: 200px;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 0;
}

.nav-item {
  width: 100%;
  padding: 12px 20px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
  color: #4a5568;
  font-size: 14px;
}

.nav-item:hover {
  background: #f7fafc;
  color: #2c3e50;
}

.nav-item.active {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
  border-right: 3px solid #2563eb;
}

.nav-label {
  display: block;
}

/* 主内容区 */
.main-content {
  flex: 1;
  overflow-y: auto;
  background: white;
}

.content-section {
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

/* 筛选 */
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

/* 表格 */
.materials-table {
  overflow-x: auto;
}

.materials-table table {
  width: 100%;
  border-collapse: collapse;
}

.materials-table th,
.materials-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.materials-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #4a5568;
  font-size: 13px;
}

.materials-table td {
  font-size: 14px;
  color: #2c3e50;
}

.component-badge {
  padding: 4px 8px;
  background: #ede9fe;
  color: #6d28d9;
  border-radius: 4px;
  font-size: 12px;
}

.text-muted {
  color: #718096;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

/* 加载和空状态 */
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

.file-list {
  margin-top: 12px;
  padding: 12px;
  background: #f7fafc;
  border-radius: 6px;
}

.file-list p {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 600;
  color: #4a5568;
}

.file-list ul {
  margin: 0;
  padding-left: 20px;
  list-style: disc;
}

.file-list li {
  font-size: 13px;
  color: #2c3e50;
  margin-bottom: 4px;
}
</style>
