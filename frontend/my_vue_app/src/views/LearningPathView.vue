<template>
  <div class="learning-path-page">
    <header class="top-bar">
      <div class="left">
        <h1>学习路径规划</h1>
        <p class="subtitle">个性化学习路线，助您高效掌握知识</p>
      </div>
      <div class="right">
        <button class="btn btn-primary" @click="showGenerateDialog = true">
          智能生成学习路径
        </button>
      </div>
    </header>

    <main class="content">
      <!-- 标签页 -->
      <div class="tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'system' }"
          @click="activeTab = 'system'"
        >
          基础学习路径
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'my' }"
          @click="activeTab = 'my'"
        >
          我的学习路径
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 我的学习路径 -->
      <div v-else-if="activeTab === 'my'" class="paths-section">
        <div v-if="userPaths.length === 0" class="empty-state">
          <h3>还没有开始的学习路径</h3>
          <p>选择一个基础路径开始学习</p>
          <button class="btn btn-primary" @click="activeTab = 'system'">
            查看基础路径
          </button>
        </div>
        <div v-else class="paths-grid">
          <div 
            v-for="userPath in userPaths" 
            :key="userPath.id"
            class="path-card"
            @click="viewPathDetail(userPath.id)"
          >
            <div class="path-header">
              <h3>{{ userPath.path.name }}</h3>
              <span class="status-badge" :class="userPath.status">
                {{ getStatusText(userPath.status) }}
              </span>
            </div>
            <p class="path-description">{{ userPath.path.description || '暂无描述' }}</p>
            <div class="path-meta">
              <span class="meta-item">
                <span class="meta-label">难度:</span>
                {{ getDifficultyText(userPath.path.difficulty) }}
              </span>
              <span class="meta-item">
                <span class="meta-label">节点数:</span>
                {{ userPath.path.node_count || 0 }}
              </span>
            </div>
            <div class="progress-section">
              <div class="progress-header">
                <span>学习进度</span>
                <span class="progress-percent">{{ Math.round(userPath.progress) }}%</span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: userPath.progress + '%' }"
                ></div>
              </div>
            </div>
            <div class="path-footer">
              <span class="time-info">
                开始于 {{ formatDate(userPath.started_at) }}
              </span>
              <button 
                class="btn-small btn-primary"
                @click.stop="continueLearning(userPath.id)"
              >
                继续学习
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 基础学习路径 -->
      <div v-else-if="activeTab === 'system'" class="paths-section">
        <!-- 固定的基础学习路径组件（不依赖后端数据） -->
        <BaseFoundationPath />

        <!-- 如果后端配置了更多系统路径，在基础路径组件下方继续展示 -->
        <div v-if="systemPaths.length > 0" class="paths-grid extra-system-paths">
          <div 
            v-for="path in systemPaths" 
            :key="path.id"
            class="path-card"
          >
            <div class="path-header">
              <h3>{{ path.name }}</h3>
              <span class="system-badge">系统</span>
            </div>
            <p class="path-description">{{ path.description || '暂无描述' }}</p>
            <div class="path-meta">
              <span class="meta-item">
                <span class="meta-label">难度:</span>
                {{ getDifficultyText(path.difficulty) }}
              </span>
              <span class="meta-item">
                <span class="meta-label">节点数:</span>
                {{ path.node_count || 0 }}
              </span>
              <span class="meta-item">
                <span class="meta-label">预计时长:</span>
                {{ path.estimated_duration || 0 }} 小时
              </span>
            </div>
            <div class="path-footer">
              <button 
                class="btn btn-primary"
                @click="startPath(path.id)"
              >
                开始学习
              </button>
              <button 
                class="btn btn-secondary"
                @click="viewPathInfo(path.id)"
              >
                查看详情
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 智能生成对话框 -->
    <div v-if="showGenerateDialog" class="modal-overlay" @click.self="closeGenerateDialog">
      <div class="modal-content large">
        <div class="modal-header">
          <h3>智能生成学习路径</h3>
          <button @click="closeGenerateDialog" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>选择目标知识点</label>
            <p class="form-hint">从知识图谱中选择您想要学习的目标知识点</p>
            <div class="knowledge-selector">
              <button 
                class="btn btn-secondary"
                @click="showKnowledgeGraph = true"
              >
                从知识图谱选择
              </button>
              <div v-if="selectedKnowledge.length > 0" class="selected-knowledge">
                <div 
                  v-for="(item, idx) in selectedKnowledge" 
                  :key="idx"
                  class="knowledge-tag"
                >
                  {{ item.label }}
                  <button @click="removeKnowledge(idx)" class="tag-remove">×</button>
                </div>
              </div>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>难度等级</label>
              <select v-model="generateConfig.difficulty" class="form-select">
                <option value="beginner">初级</option>
                <option value="intermediate">中级</option>
                <option value="advanced">高级</option>
              </select>
            </div>
            <div class="form-group">
              <label>最大节点数</label>
              <input 
                v-model.number="generateConfig.max_nodes" 
                type="number" 
                class="form-input"
                min="5"
                max="20"
              />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeGenerateDialog" class="btn btn-secondary">取消</button>
          <button 
            @click="generatePath" 
            class="btn btn-primary"
            :disabled="selectedKnowledge.length === 0 || generating"
          >
            {{ generating ? '生成中...' : '生成路径' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 路径详情对话框 -->
    <div v-if="showDetailDialog && currentPathDetail" class="modal-overlay" @click.self="closeDetailDialog">
      <div class="modal-content large">
        <div class="modal-header">
          <h3>{{ currentPathDetail.path.name }}</h3>
          <button @click="closeDetailDialog" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="path-detail-info">
            <p class="path-description">{{ currentPathDetail.path.description }}</p>
            <div class="path-stats">
              <div class="stat-item">
                <span class="stat-label">进度</span>
                <span class="stat-value">{{ Math.round(currentPathDetail.progress) }}%</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">状态</span>
                <span class="stat-value">{{ getStatusText(currentPathDetail.status) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">节点数</span>
                <span class="stat-value">{{ currentPathDetail.path.nodes?.length || 0 }}</span>
              </div>
            </div>
          </div>
          
          <div class="path-nodes-list">
            <h4>学习节点</h4>
            <div 
              v-for="(node, idx) in currentPathDetail.path.nodes" 
              :key="node.id"
              class="path-node-item"
              :class="getNodeStatusClass(node.progress?.status)"
            >
              <div class="node-order">{{ idx + 1 }}</div>
              <div class="node-content">
                <div class="node-header">
                  <h5>{{ node.node_name }}</h5>
                  <span class="node-status">{{ getNodeStatusText(node.progress?.status) }}</span>
                </div>
                <p v-if="node.description" class="node-description">{{ node.description }}</p>
                <div class="node-progress" v-if="node.progress">
                  <div class="progress-bar small">
                    <div 
                      class="progress-fill" 
                      :style="{ width: node.progress.completion_percentage + '%' }"
                    ></div>
                  </div>
                  <span class="progress-text">{{ Math.round(node.progress.completion_percentage) }}%</span>
                </div>
              </div>
              <div class="node-actions">
                <button 
                  v-if="node.progress?.status !== 'completed'"
                  class="btn-small btn-primary"
                  @click="updateNodeProgress(node.id, node.progress)"
                >
                  {{ node.progress?.status === 'not_started' ? '开始' : '继续' }}
                </button>
                <button 
                  v-if="node.progress?.status === 'in_progress'"
                  class="btn-small btn-secondary"
                  @click="skipNode(node.id)"
                >
                  跳过
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="adjustPath" class="btn btn-secondary">调整路径</button>
          <button @click="closeDetailDialog" class="btn btn-primary">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import BaseFoundationPath from '@/components/LearningPath/BaseFoundationPath.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export default {
  name: 'LearningPathView',
  components: {
    BaseFoundationPath
  },
  setup() {
    const router = useRouter()
    
    // 状态
    const loading = ref(false)
    const activeTab = ref('system')
    const userPaths = ref([])
    const systemPaths = ref([])
    const showGenerateDialog = ref(false)
    const showDetailDialog = ref(false)
    const showKnowledgeGraph = ref(false)
    const currentPathDetail = ref(null)
    const generating = ref(false)
    
    const selectedKnowledge = ref([])
    const generateConfig = ref({
      difficulty: 'beginner',
      max_nodes: 10
    })
    
    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        'not_started': '未开始',
        'in_progress': '进行中',
        'completed': '已完成',
        'paused': '已暂停'
      }
      return statusMap[status] || status
    }
    
    const getDifficultyText = (difficulty) => {
      const difficultyMap = {
        'beginner': '初级',
        'intermediate': '中级',
        'advanced': '高级'
      }
      return difficultyMap[difficulty] || difficulty
    }
    
    const getNodeStatusText = (status) => {
      const statusMap = {
        'not_started': '未开始',
        'in_progress': '进行中',
        'completed': '已完成',
        'skipped': '已跳过'
      }
      return statusMap[status] || '未开始'
    }
    
    const getNodeStatusClass = (status) => {
      return status ? `status-${status}` : 'status-not_started'
    }
    
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    }

    // 本地获取带 token 的请求头（简单版）
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token')
      if (!token) return {}
      return { Authorization: `Bearer ${token}` }
    }
    
    // API调用
    const fetchUserPaths = async () => {
      try {
        loading.value = true
        const response = await fetch(`${API_BASE_URL}/learning_path/user/paths`, {
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          }
        })
        const data = await response.json()
        if (data.code === 200) {
          userPaths.value = data.data || []
        }
      } catch (err) {
        console.error('获取用户路径失败:', err)
      } finally {
        loading.value = false
      }
    }
    
    const fetchSystemPaths = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/learning_path/paths?include_system=true&category=`, {
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          }
        })
        const data = await response.json()
        if (data.code === 200) {
          systemPaths.value = (data.data || []).filter(p => p.is_system)
        }
      } catch (err) {
        console.error('获取系统路径失败:', err)
      }
    }
    
    const startPath = async (pathId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/learning_path/user/paths`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          },
          body: JSON.stringify({ path_id: pathId })
        })
        const data = await response.json()
        if (data.code === 200) {
          alert('开始学习成功')
          fetchUserPaths()
          activeTab.value = 'my'
        } else {
          alert('开始学习失败: ' + data.message)
        }
      } catch (err) {
        console.error('开始学习失败:', err)
        alert('开始学习失败')
      }
    }
    
    const generatePath = async () => {
      if (selectedKnowledge.value.length === 0) {
        alert('请至少选择一个目标知识点')
        return
      }
      
      try {
        generating.value = true
        const response = await fetch(`${API_BASE_URL}/learning_path/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          },
          body: JSON.stringify({
            target_knowledge: selectedKnowledge.value.map(k => k.id),
            difficulty: generateConfig.value.difficulty,
            max_nodes: generateConfig.value.max_nodes
          })
        })
        const data = await response.json()
        if (data.code === 200) {
          // 创建路径
          const pathData = {
            name: `智能生成路径 - ${new Date().toLocaleDateString()}`,
            description: '基于知识图谱智能生成的学习路径',
            difficulty: generateConfig.value.difficulty,
            category: 'general',
            estimated_duration: Math.ceil(data.data.estimated_duration / 60)
          }
          
          const createResponse = await fetch(`${API_BASE_URL}/learning_path/paths`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...getAuthHeaders()
            },
            body: JSON.stringify(pathData)
          })
          const createData = await createResponse.json()
          
          if (createData.code === 200) {
            const pathId = createData.data.id
            // 添加节点
            for (const node of data.data.nodes) {
              await fetch(`${API_BASE_URL}/learning_path/paths/${pathId}/nodes`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  ...getAuthHeaders()
                },
                body: JSON.stringify(node)
              })
            }
            
            alert('路径生成成功，是否开始学习？')
            closeGenerateDialog()
            await startPath(pathId)
          }
        } else {
          alert('生成失败: ' + data.message)
        }
      } catch (err) {
        console.error('生成路径失败:', err)
        alert('生成失败')
      } finally {
        generating.value = false
      }
    }
    
    const viewPathDetail = async (userPathId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/learning_path/user/paths/${userPathId}`, {
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          }
        })
        const data = await response.json()
        if (data.code === 200) {
          currentPathDetail.value = data.data
          showDetailDialog.value = true
        }
      } catch (err) {
        console.error('获取路径详情失败:', err)
      }
    }
    
    const viewPathInfo = async (pathId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/learning_path/paths/${pathId}`, {
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          }
        })
        const data = await response.json()
        if (data.code === 200) {
          // 显示路径信息，但不包含用户进度
          alert(`路径名称: ${data.data.name}\n节点数: ${data.data.nodes?.length || 0}`)
        }
      } catch (err) {
        console.error('获取路径信息失败:', err)
      }
    }
    
    const continueLearning = (userPathId) => {
      viewPathDetail(userPathId)
    }
    
    const updateNodeProgress = async (nodeId, progress) => {
      if (!currentPathDetail.value) return
      
      const status = progress?.status === 'not_started' ? 'in_progress' : 'in_progress'
      const completion = progress?.completion_percentage || 0
      
      try {
        const response = await fetch(`${API_BASE_URL}/learning_path/user/paths/${currentPathDetail.value.id}/progress`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          },
          body: JSON.stringify({
            path_node_id: nodeId,
            status: status,
            completion_percentage: Math.min(completion + 10, 100)
          })
        })
        const data = await response.json()
        if (data.code === 200) {
          await viewPathDetail(currentPathDetail.value.id)
          await fetchUserPaths()
        }
      } catch (err) {
        console.error('更新进度失败:', err)
      }
    }
    
    const skipNode = async (nodeId) => {
      if (!currentPathDetail.value) return
      
      try {
        const response = await fetch(`${API_BASE_URL}/learning_path/user/paths/${currentPathDetail.value.id}/progress`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          },
          body: JSON.stringify({
            path_node_id: nodeId,
            status: 'skipped'
          })
        })
        const data = await response.json()
        if (data.code === 200) {
          await viewPathDetail(currentPathDetail.value.id)
          await fetchUserPaths()
        }
      } catch (err) {
        console.error('跳过节点失败:', err)
      }
    }
    
    const adjustPath = () => {
      alert('路径调整功能开发中...')
    }
    
    const removeKnowledge = (idx) => {
      selectedKnowledge.value.splice(idx, 1)
    }
    
    const closeGenerateDialog = () => {
      showGenerateDialog.value = false
      selectedKnowledge.value = []
      generateConfig.value = {
        difficulty: 'beginner',
        max_nodes: 10
      }
    }
    
    const closeDetailDialog = () => {
      showDetailDialog.value = false
      currentPathDetail.value = null
    }
    
    onMounted(() => {
      fetchUserPaths()
      fetchSystemPaths()
    })
    
    return {
      loading,
      activeTab,
      userPaths,
      systemPaths,
      showGenerateDialog,
      showDetailDialog,
      showKnowledgeGraph,
      currentPathDetail,
      generating,
      selectedKnowledge,
      generateConfig,
      getStatusText,
      getDifficultyText,
      getNodeStatusText,
      getNodeStatusClass,
      formatDate,
      startPath,
      generatePath,
      viewPathDetail,
      viewPathInfo,
      continueLearning,
      updateNodeProgress,
      skipNode,
      adjustPath,
      removeKnowledge,
      closeGenerateDialog,
      closeDetailDialog
    }
  }
}
</script>

<style scoped>
.learning-path-page {
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

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #e2e8f0;
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: none;
  font-size: 14px;
  font-weight: 500;
  color: #718096;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
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

.paths-section {
  min-height: 400px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.empty-state p {
  margin: 0 0 24px 0;
  color: #718096;
}

.paths-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.path-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.path-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #667eea;
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 12px;
}

.path-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.in_progress {
  background: #e6fffa;
  color: #047857;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.not_started {
  background: #f3f4f6;
  color: #6b7280;
}

.system-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: #ede9fe;
  color: #6d28d9;
}

.path-description {
  color: #718096;
  font-size: 14px;
  margin: 0 0 16px 0;
  line-height: 1.6;
}

.path-meta {
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

.progress-section {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: #4a5568;
}

.progress-percent {
  font-weight: 600;
  color: #667eea;
}

.progress-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar.small {
  height: 6px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
}

.path-footer {
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

.modal-content.large {
  max-width: 900px;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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
  margin: 4px 0 12px 0;
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
}

.knowledge-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selected-knowledge {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.knowledge-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #ede9fe;
  color: #6d28d9;
  border-radius: 16px;
  font-size: 13px;
}

.tag-remove {
  background: none;
  border: none;
  color: #6d28d9;
  cursor: pointer;
  font-size: 18px;
  padding: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.tag-remove:hover {
  background: rgba(109, 40, 217, 0.1);
}

.path-detail-info {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.path-stats {
  display: flex;
  gap: 24px;
  margin-top: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #718096;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.path-nodes-list h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #2c3e50;
}

.path-node-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.path-node-item:hover {
  border-color: #667eea;
  background: #f8fafc;
}

.path-node-item.status-completed {
  background: #f0fdf4;
  border-color: #86efac;
}

.path-node-item.status-in_progress {
  background: #eff6ff;
  border-color: #93c5fd;
}

.node-order {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  font-weight: 600;
  flex-shrink: 0;
}

.node-content {
  flex: 1;
  min-width: 0;
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.node-header h5 {
  margin: 0;
  font-size: 15px;
  color: #2c3e50;
}

.node-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  background: #f3f4f6;
  color: #6b7280;
}

.node-description {
  font-size: 13px;
  color: #718096;
  margin: 0 0 8px 0;
}

.node-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #718096;
  min-width: 40px;
}

.node-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
</style>
