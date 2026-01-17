<template>
  <div class="knowledge-graph-page">
    <!-- 顶部信息栏 -->
    <div class="top-bar">
      <div class="page-title">
        <h1>知识图谱</h1>
        <p class="subtitle">知识节点与关系网络可视化</p>
      </div>
    </div>

    <div class="main-layout">
      <!-- 左侧控制面板 -->
      <div class="left-panel">
        <div class="control-section">
          <h3>视图控制</h3>
          
          <!-- 聚焦模式控制 -->
          <div class="control-group" v-if="focusMode">
            <label>关联深度</label>
            <div class="depth-control">
              <button 
                v-for="depth in [2, 3, 4]" 
                :key="depth"
                @click="setFocusDepth(depth)"
                class="depth-btn"
                :class="{ active: focusDepth === depth }"
              >
                {{ getDepthLabel(depth) }}
              </button>
            </div>
          </div>
          
          <div class="control-buttons">
            <button @click="resetView" class="btn btn-secondary">
              重置视图
            </button>
            <button @click="autoLayout" class="btn btn-primary">
              自动布局
            </button>
            <!-- 聚焦/退出聚焦按钮 -->
            <button 
              v-if="selectedNode && !focusMode"
              @click="enterFocusMode"
              class="btn btn-primary"
            >
              聚焦模式
            </button>
            <button 
              v-else-if="focusMode"
              @click="exitFocusMode"
              class="btn btn-secondary"
            >
              退出聚焦
            </button>
          </div>
        </div>

        <div class="legend-section">
          <h3>类型图例</h3>
          <div class="legend-items">
            <div 
              v-for="type in typeDistribution" 
              :key="type.type" 
              class="legend-item"
              @click="highlightType(type.type)"
              @mouseover="highlightType(type.type)"
              @mouseout="resetTypeHighlight"
            >
              <div 
                class="legend-color" 
                :style="{ backgroundColor: getTypeColor(type.type) }"
              ></div>
              <span class="legend-label">{{ type.type }}</span>
              <span class="legend-count">{{ type.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间图谱区域 -->
      <div class="center-panel">
        <div class="graph-header">
          <div class="status-display">
            <div v-if="loading" class="loading-indicator">
              <span class="spinner"></span>
              正在加载图谱数据...
            </div>
            <div v-else-if="error" class="error-indicator">
              加载失败: {{ error }}
              <button @click="fetchData" class="btn-small">重试</button>
            </div>
            <div v-else-if="!nodes.length" class="empty-indicator">
              暂无图谱数据
            </div>
            <div v-else class="ready-indicator">
              <template v-if="focusMode">
                聚焦模式: 显示 {{ visibleNodes.length }}/{{ nodes.length }} 个节点，{{ visibleEdges.length }}/{{ edges.length }} 条边
                <span class="focus-indicator">
                  {{ getFocusDepthText() }}
                </span>
              </template>
              <template v-else>
                已加载 {{ nodes.length }} 个节点和 {{ edges.length }} 条关系
              </template>
            </div>
          </div>
          
          <div class="view-controls">
            <!-- 删除按钮（聚焦模式下显示） -->
            <button 
              v-if="focusMode && selectedNode" 
              @click="deleteSelectedNode"
              class="btn-small btn-danger"
              title="删除选中节点"
            >
              删除节点
            </button>
            
            <div class="zoom-controls">
              <button @click="zoomOut" class="zoom-btn" title="缩小">
                <span class="icon">−</span>
              </button>
              <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
              <button @click="zoomIn" class="zoom-btn" title="放大">
                <span class="icon">+</span>
              </button>
            </div>
            <div class="canvas-buttons">
              <button 
                @click="showNodeLabels = !showNodeLabels" 
                class="btn-small"
                :class="{ active: showNodeLabels }"
              >
                标签: {{ showNodeLabels ? '显示' : '隐藏' }}
              </button>
            </div>
          </div>
        </div>

        <div class="graph-container">
          <!-- 画布区域 -->
          <div 
            class="graph-canvas"
            ref="canvasRef"
            @mousedown="startDrag"
            @mousemove="handleDrag"
            @mouseup="stopDrag"
            @mouseleave="stopDrag"
            @wheel="handleWheel"
            :class="{ dragging: isDragging }"
          >
            <!-- 关系连接线 - 改为直线 -->
            <svg class="edges-layer" :width="canvasWidth" :height="canvasHeight">
              <g v-for="edge in visibleEdges" :key="edge.id">
                <line
                  :x1="getNodePosition(edge.source).x"
                  :y1="getNodePosition(edge.source).y"
                  :x2="getNodePosition(edge.target).x"
                  :y2="getNodePosition(edge.target).y"
                  :stroke="getEdgeColor(edge.type)"
                  stroke-width="2"
                  :opacity="getEdgeOpacity(edge)"
                  class="edge-line"
                  @mouseenter="hoverEdge = edge"
                  @mouseleave="hoverEdge = null"
                />
                
                <!-- 边标签（可显示） -->
                <text
                  v-if="showEdgeLabels && edge.label"
                  :x="(getNodePosition(edge.source).x + getNodePosition(edge.target).x) / 2"
                  :y="(getNodePosition(edge.source).y + getNodePosition(edge.target).y) / 2"
                  text-anchor="middle"
                  dy="3"
                  class="edge-label"
                >
                  {{ edge.label }}
                </text>
              </g>
            </svg>

            <!-- 节点 -->
            <div
              v-for="node in visibleNodes"
              :key="node.id"
              class="knowledge-node"
              :style="getNodeStyle(node)"
              @click="selectNode(node)"
              @mousedown="startNodeDrag(node, $event)"
              @mouseenter="hoverNode = node"
              @mouseleave="handleNodeMouseLeave"
              :class="{
                selected: selectedNode?.id === node.id,
                hovered: hoverNode?.id === node.id,
                dragging: draggedNode?.id === node.id,
                highlighted: highlightedType === node.type,
                'focus-root': focusMode && focusRootNodes.some(n => n.id === node.id),
                'focus-level-1': focusMode && !focusRootNodes.some(n => n.id === node.id) && focusNodeLevels[node.id] === 1,
                'focus-level-2': focusMode && !focusRootNodes.some(n => n.id === node.id) && focusNodeLevels[node.id] === 2,
                'focus-level-3': focusMode && !focusRootNodes.some(n => n.id === node.id) && focusNodeLevels[node.id] === 3
              }"
              :title="getNodeTooltip(node)"
            >
              <!-- 节点卡片主体 -->
              <div class="node-card" :style="{ '--type-color': getTypeColor(node.type) }">
                <!-- 类型指示器 -->
                <div class="node-type-indicator" :style="{ backgroundColor: getTypeColor(node.type) }"></div>

                <!-- 节点内容 -->
                <div class="node-content">
                  <!-- 主要标签 -->
                  <div class="node-main-label">
                    {{ truncateText(node.label || node.id, 15) }}
                  </div>

                  <!-- 类型标签 -->
                  <div class="node-type-label" :style="{ color: getTypeColor(node.type) }">
                    {{ node.type }}
                  </div>
                </div>

                <!-- 装饰元素 -->
                <div class="node-decoration"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧详情面板 -->
      <div class="right-panel">
        <div class="details-panel">
          <div class="panel-header">
            <h3 v-if="focusMode">聚焦模式</h3>
            <h3 v-else>节点详情</h3>
            <div class="panel-actions">
              <button @click="clearSelection" class="icon-btn" title="清除选择">
                清除
              </button>
            </div>
          </div>
          
          <div class="panel-content">
            <!-- 聚焦模式说明 -->
            <div v-if="focusMode && selectedNode" class="focus-info">
              <div class="focus-header">
                <div class="focus-title">
                  <h4>聚焦模式</h4>
                  <p class="focus-description">
                    {{ getFocusDepthDescription() }}
                  </p>
                </div>
              </div>
              
              <div class="depth-info">
                <div class="depth-stat">
                  <span class="stat-label">根节点</span>
                  <span class="stat-value">1</span>
                </div>
                <div class="depth-stat">
                  <span class="stat-label">一级关联节点</span>
                  <span class="stat-value">{{ getLevelNodeCount(1) }}</span>
                </div>
                <div class="depth-stat">
                  <span class="stat-label">二级关联节点</span>
                  <span class="stat-value">{{ getLevelNodeCount(2) }}</span>
                </div>
                <div v-if="focusDepth >= 4" class="depth-stat">
                  <span class="stat-label">三级关联节点</span>
                  <span class="stat-value">{{ getLevelNodeCount(3) }}</span>
                </div>
              </div>
            </div>
            
            <!-- 选中节点信息 -->
            <div v-if="selectedNode" class="selected-node-info">
              <div class="node-header">
                <div class="node-type-large" :style="{ backgroundColor: getTypeColor(selectedNode.type) }">
                  {{ getTypeAbbr(selectedNode.type) }}
                </div>
                <div class="node-title">
                  <h4>{{ selectedNode.label || selectedNode.id }}</h4>
                  <div class="node-meta">
                    <span class="type-tag">{{ selectedNode.type }}</span>
                    <span v-if="focusMode" class="focus-tag">聚焦中</span>
                  </div>
                </div>
              </div>
              
              <div class="details-grid">
                <div class="detail-row">
                  <label>节点ID</label>
                  <div class="value">{{ selectedNode.id }}</div>
                </div>
                
                <div v-if="selectedNode.properties" class="detail-section">
                  <h5>属性信息</h5>
                  <div class="properties-grid">
                    <div 
                      v-for="(value, key) in selectedNode.properties" 
                      :key="key"
                      class="property-item"
                    >
                      <span class="property-key">{{ key }}</span>
                      <span class="property-value">{{ formatPropertyValue(value) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="connections-section" v-if="getNodeConnections(selectedNode.id).length > 0">
                <h5>关联节点 ({{ getNodeConnections(selectedNode.id).length }})</h5>
                <div class="connections-list">
                  <div 
                    v-for="conn in getNodeConnections(selectedNode.id)" 
                    :key="conn.target.id + '-' + conn.direction"
                    class="connection-item"
                    @click="selectNode(conn.target)"
                    @mouseenter="hoverEdge = conn.edge"
                    @mouseleave="handleConnectionMouseLeave"
                  >
                    <div class="connection-direction">
                      <span v-if="conn.direction === 'out'">→</span>
                      <span v-else-if="conn.direction === 'in'">←</span>
                      <span v-else>↔</span>
                    </div>
                    <div class="connection-info">
                      <div class="connection-target">
                        {{ conn.target.label || conn.target.id }}
                      </div>
                      <div class="connection-meta">
                        {{ conn.edge.type || '关联' }}
                      </div>
                    </div>
                    <div class="connection-type-tag">{{ conn.target.type }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 未选中时的概览信息 -->
            <div v-else class="overview-info">
              <h4>图谱统计</h4>
              
              <div class="stats-overview">
                <div class="stat-overview-item">
                  <span class="stat-label">节点总数</span>
                  <span class="stat-value">{{ nodes.length }}</span>
                </div>
                <div class="stat-overview-item">
                  <span class="stat-label">关系总数</span>
                  <span class="stat-value">{{ edges.length }}</span>
                </div>
              </div>
              
              <div class="focus-hint" v-if="!focusMode">
                <p class="hint-text">选择一个节点进入聚焦模式，分析节点关联关系</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'

export default {
  name: 'KnowledgeGraph',
  setup() {
    // 数据状态
    const loading = ref(false)
    const error = ref('')
    const nodes = ref([])
    const edges = ref([])
    
    // 视图状态
    const selectedNode = ref(null)
    const selectedEdge = ref(null)
    const hoverNode = ref(null)
    const hoverEdge = ref(null)
    const draggedNode = ref(null)
    const isDragging = ref(false)
    const dragStart = ref({ x: 0, y: 0 })
    
    // 视图控制
    const nodeScale = ref(0.8)
    const zoom = ref(1)
    const showNodeLabels = ref(true)
    const showEdgeLabels = ref(true)
    const highlightedType = ref(null)
    
    // 聚焦模式状态
    const focusMode = ref(false)
    const focusDepth = ref(2) // 默认深度为2（一级关联）
    const focusNodes = ref([]) // 聚焦模式下显示的节点ID列表
    const focusRootNodes = ref([]) // 聚焦的根节点（选中的节点）
    const focusEdges = ref([]) // 聚焦模式下显示的边ID列表
    const focusNodeLevels = ref({}) // 记录每个节点的层级（0:根节点，1:一级关联，2:二级关联，3:三级关联）
    
    // 画布设置
    const canvasWidth = 2000
    const canvasHeight = 1200
    const offsetX = ref(0)
    const offsetY = ref(0)
    const nodePositions = ref({})
    
    // 计算属性
    const typeDistribution = computed(() => {
      const counts = {}
      nodes.value.forEach(node => {
        counts[node.type] = (counts[node.type] || 0) + 1
      })
      
      return Object.entries(counts)
        .map(([type, count]) => ({
          type,
          count,
          percentage: Math.round((count / nodes.value.length) * 100)
        }))
        .sort((a, b) => b.count - a.count)
    })
    
    // 可见节点和边（聚焦模式下只显示关联节点和边）
    const visibleNodes = computed(() => {
      if (!focusMode.value) return nodes.value
      
      // 聚焦模式下，只显示聚焦相关的节点
      return nodes.value.filter(node => focusNodes.value.includes(node.id))
    })
    
    const visibleEdges = computed(() => {
      if (!focusMode.value) return edges.value
      
      // 聚焦模式下，只显示聚焦相关的边
      // 重要：确保边只在两个节点都在可见节点中时才显示
      return edges.value.filter(edge => {
        // 检查边的源节点和目标节点是否都在可见节点列表中
        const sourceVisible = focusNodes.value.includes(edge.source)
        const targetVisible = focusNodes.value.includes(edge.target)
        return sourceVisible && targetVisible
      })
    })
    
    // 类型颜色映射
    const typeColors = {
      'Tactic': '#e74c3c',
      'TA': '#e74c3c',
      'Technique': '#f39c12',
      'TE': '#f39c12',
      'tactic': '#e74c3c',
      'technique': '#f39c12',
      'Person': '#3498db',
      'Organization': '#2ecc71',
      'Location': '#9b59b6',
      'Event': '#f59e0b',
      'Concept': '#1abc9c',
      'Product': '#34495e',
      'Topic': '#8e44ad',
      'Technology': '#d35400',
      'Industry': '#16a085',
      'Skill': '#27ae60',
      'default': '#7f8c8d'
    }
    
    // 边类型颜色映射
    const edgeColors = {
      'RELATES_TO': '#3498db',
      'PART_OF': '#2ecc71',
      'LOCATED_IN': '#e74c3c',
      'CREATED': '#f59e0b',
      'HAS_SKILL': '#9b59b6',
      'WORKS_IN': '#1abc9c',
      'BELONGS_TO': '#34495e',
      'USES': '#d35400',
      'default': '#95a5a6'
    }
    
    // 获取类型颜色
    const getTypeColor = (type) => {
      return typeColors[type] || typeColors.default
    }
    
    // 获取边颜色
    const getEdgeColor = (edgeType) => {
      return edgeColors[edgeType] || edgeColors.default
    }
    
    // 获取类型缩写
    const getTypeAbbr = (type) => {
      return type.substring(0, 2).toUpperCase()
    }

    // 检查是否为tactic类型节点
    const isTacticNode = (node) => {
      return node.type.toLowerCase().includes('tactic') ||
             node.type.toLowerCase() === 'ta'
    }

    // 检查是否为technique类型节点
    const isTechniqueNode = (node) => {
      return node.type.toLowerCase().includes('technique') ||
             node.type.toLowerCase() === 'te'
    }
    
    // 获取节点连接
    const getNodeConnections = (nodeId) => {
      const connections = []
      
      edges.value.forEach(edge => {
        if (edge.source === nodeId) {
          const target = nodes.value.find(n => n.id === edge.target)
          if (target) {
            connections.push({
              edge,
              target,
              direction: 'out'
            })
          }
        }
        if (edge.target === nodeId) {
          const source = nodes.value.find(n => n.id === edge.source)
          if (source) {
            connections.push({
              edge,
              target: source,
              direction: 'in'
            })
          }
        }
      })
      
      return connections
    }
    
    // 处理节点鼠标离开事件
    const handleNodeMouseLeave = () => {
      if (!draggedNode.value) hoverNode.value = null
    }
    
    // 处理连接项鼠标离开事件
    const handleConnectionMouseLeave = () => {
      if (!selectedEdge.value) hoverEdge.value = null
    }
    
    // 获取数据
    const fetchData = async () => {
      try {
        loading.value = true
        error.value = ''
        
        console.log('正在请求数据...')
        const response = await fetch('/api/graph/get_subgraph')
        console.log('响应状态:', response.status, response.statusText)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        console.log('响应数据:', data)

        if (data.code !== 200) {
          throw new Error(data.message || 'API返回错误')
        }

        nodes.value = data.nodes || []
        edges.value = data.edges || []
        
        console.log('数据加载完成:', nodes.value.length, '节点,', edges.value.length, '边')
        
        // 如果没有数据，使用模拟数据
        if (nodes.value.length === 0) {
          console.log('API返回空数据，使用模拟数据...')
          useMockData()
        } else {
          initNodePositions()
        }
        
      } catch (err) {
        console.error('加载失败:', err)
        error.value = `请求失败: ${err.message}`
        
        // 如果API失败，使用模拟数据
        console.log('API请求失败，使用模拟数据...')
        useMockData()
      } finally {
        loading.value = false
      }
    }
    
    // 使用模拟数据
    const useMockData = () => {
      // 模拟数据示例
      nodes.value = [
        { id: '1', label: '网络安全', type: 'Topic', properties: { description: '网络安全主题' } },
        { id: '2', label: '防火墙', type: 'Technology', properties: { description: '网络安全技术' } },
        { id: '3', label: '入侵检测', type: 'Technology', properties: { description: '入侵检测系统' } },
        { id: '4', label: '加密技术', type: 'Technology', properties: { description: '数据加密技术' } },
        { id: '5', label: '企业网络', type: 'Organization', properties: { description: '企业网络架构' } },
        { id: '6', label: '云计算', type: 'Technology', properties: { description: '云平台技术' } },
        { id: '7', label: '数据备份', type: 'Technology', properties: { description: '数据备份方案' } },
        { id: '8', label: '访问控制', type: 'Concept', properties: { description: '访问控制机制' } },
        { id: '9', label: '身份认证', type: 'Technology', properties: { description: '身份认证技术' } },
        { id: '10', label: '风险评估', type: 'Concept', properties: { description: '安全风险评估' } },
        { id: '11', label: '安全策略', type: 'Concept', properties: { description: '安全策略制定' } },
        { id: '12', label: '漏洞扫描', type: 'Technology', properties: { description: '漏洞扫描工具' } },
        { id: '13', label: '安全意识', type: 'Concept', properties: { description: '员工安全意识' } },
        { id: '14', label: '合规要求', type: 'Concept', properties: { description: '法规合规要求' } },
        { id: '15', label: '应急响应', type: 'Concept', properties: { description: '安全应急响应' } },
        { id: '16', label: '数据加密', type: 'Technology', properties: { description: '数据加密技术' } },
        { id: '17', label: '网络安全法', type: 'Concept', properties: { description: '网络安全法律法规' } },
        { id: '18', label: '网络隔离', type: 'Technology', properties: { description: '网络隔离技术' } },
        { id: '19', label: '安全审计', type: 'Concept', properties: { description: '安全审计流程' } },
        { id: '20', label: '威胁情报', type: 'Concept', properties: { description: '威胁情报收集' } }
      ]
      
      edges.value = [
        { id: 'e1', source: '1', target: '2', type: 'INCLUDES', label: '包含' },
        { id: 'e2', source: '1', target: '3', type: 'INCLUDES', label: '包含' },
        { id: 'e3', source: '1', target: '4', type: 'INCLUDES', label: '包含' },
        { id: 'e4', source: '2', target: '5', type: 'USED_IN', label: '应用于' },
        { id: 'e5', source: '3', target: '5', type: 'USED_IN', label: '应用于' },
        { id: 'e6', source: '4', target: '5', type: 'USED_IN', label: '应用于' },
        { id: 'e7', source: '5', target: '6', type: 'RELATES_TO', label: '关联' },
        { id: 'e8', source: '5', target: '7', type: 'RELATES_TO', label: '关联' },
        { id: 'e9', source: '5', target: '8', type: 'HAS', label: '拥有' },
        { id: 'e10', source: '8', target: '9', type: 'REQUIRES', label: '需要' },
        { id: 'e11', source: '5', target: '10', type: 'PERFORMS', label: '执行' },
        { id: 'e12', source: '10', target: '11', type: 'PRODUCES', label: '产生' },
        { id: 'e13', source: '11', target: '12', type: 'REQUIRES', label: '需要' },
        { id: 'e14', source: '13', target: '5', type: 'APPLIES_TO', label: '应用于' },
        { id: 'e15', source: '14', target: '11', type: 'INFLUENCES', label: '影响' },
        { id: 'e16', source: '15', target: '5', type: 'PROTECTS', label: '保护' },
        { id: 'e17', source: '12', target: '16', type: 'USES', label: '使用' },
        { id: 'e18', source: '17', target: '14', type: 'DEFINES', label: '定义' },
        { id: 'e19', source: '18', target: '5', type: 'PROTECTS', label: '保护' },
        { id: 'e20', source: '19', target: '10', type: 'SUPPORTS', label: '支持' },
        { id: 'e21', source: '20', target: '3', type: 'INFORMS', label: '通知' },
        { id: 'e22', source: '9', target: '16', type: 'USES', label: '使用' },
        { id: 'e23', source: '7', target: '6', type: 'STORED_IN', label: '存储于' }
      ]
      
      console.log('模拟数据加载完成:', nodes.value.length, '节点,', edges.value.length, '边')
      initNodePositions()
    }
    
    // 初始化节点位置
    const initNodePositions = () => {
      nodePositions.value = {}

      if (nodes.value.length === 0) return

      // 智能布局：重点关注tactic和technique之间的关系
      useIntelligentLayout()
    }

    // 智能布局算法
    const useIntelligentLayout = () => {
      const centerX = canvasWidth / 2
      const centerY = canvasHeight / 2

      // 1. 识别不同类型节点
      const tacticNodes = nodes.value.filter(node => isTacticNode(node))
      const techniqueNodes = nodes.value.filter(node => isTechniqueNode(node))
      const otherNodes = nodes.value.filter(node =>
        !tacticNodes.includes(node) && !techniqueNodes.includes(node)
      )

      // 2. 分析technique的连接关系
      const techniqueConnections = new Map()
      techniqueNodes.forEach(technique => {
        const connectedTactics = []
        edges.value.forEach(edge => {
          if (edge.source === technique.id) {
            const targetNode = nodes.value.find(n => n.id === edge.target)
            if (targetNode && tacticNodes.includes(targetNode)) {
              connectedTactics.push(targetNode)
            }
          }
          if (edge.target === technique.id) {
            const sourceNode = nodes.value.find(n => n.id === edge.source)
            if (sourceNode && tacticNodes.includes(sourceNode)) {
              connectedTactics.push(sourceNode)
            }
          }
        })
        techniqueConnections.set(technique, connectedTactics)
      })

      // 3. 分类techniques
      const singleTacticTechniques = new Map()
      const multiTacticTechniques = []

      techniqueConnections.forEach((tactics, technique) => {
        if (tactics.length === 1) {
          const tactic = tactics[0]
          if (!singleTacticTechniques.has(tactic)) {
            singleTacticTechniques.set(tactic, [])
          }
          singleTacticTechniques.get(tactic).push(technique)
        } else if (tactics.length > 1) {
          multiTacticTechniques.push({ technique, tactics })
        }
      })

      // 4. 计算布局参数
      const tacticSpacing = 500
      const techniqueRadius = 200
      const otherNodeSpacing = 200

      // 5. 智能布局tactics
      const tacticPositions = new Map()

      if (tacticNodes.length === 1) {
        const tactic = tacticNodes[0]
        const tacticX = centerX
        const tacticY = centerY
        tacticPositions.set(tactic, { x: tacticX, y: tacticY })

        const singleTechniques = singleTacticTechniques.get(tactic) || []
        layoutSingleTechniquesAroundTactic(singleTechniques, tacticX, tacticY)

      } else {
        const numTactics = tacticNodes.length
        const preliminaryPositions = new Map()

        const regions = calculateOptimalRegions(numTactics)

        tacticNodes.forEach((tactic, index) => {
          const region = regions[index]
          const singleTechniques = singleTacticTechniques.get(tactic) || []
          const multiTechniques = multiTacticTechniques.filter(mt => mt.tactics.includes(tactic))

          const estimatedWidth = Math.max(400, Math.sqrt(singleTechniques.length + multiTechniques.length) * 150)
          const estimatedHeight = estimatedWidth

          const tacticX = region.x + region.width * 0.5
          const tacticY = region.y + region.height * 0.5

          preliminaryPositions.set(tactic, { x: tacticX, y: tacticY })
        })

        const optimizedPositions = optimizeTacticPositions(preliminaryPositions, singleTacticTechniques, multiTacticTechniques)
        optimizedPositions.forEach((pos, tactic) => {
          tacticPositions.set(tactic, pos)
        })

        tacticPositions.forEach((pos, tactic) => {
          nodePositions.value[tactic.id] = pos

          const singleTechniques = singleTacticTechniques.get(tactic) || []
          layoutSingleTechniquesAroundTactic(singleTechniques, pos.x, pos.y)
        })
      }

      // 6. 布局多tactic techniques
      multiTacticTechniques.forEach(({ technique, tactics }) => {
        if (tactics.length === 0) return

        let centerX = 0, centerY = 0
        tactics.forEach(tactic => {
          const pos = nodePositions.value[tactic.id]
          if (pos) {
            centerX += pos.x
            centerY += pos.y
          }
        })
        centerX /= tactics.length
        centerY /= tactics.length

        const optimalPos = findOptimalPositionForTechnique(centerX, centerY, technique)
        nodePositions.value[technique.id] = optimalPos
      })

      // 7. 布局其他类型节点
      layoutOtherNodes(otherNodes)

      // 辅助函数
      function calculateOptimalRegions(numTactics) {
        const regions = []
        const cols = Math.ceil(Math.sqrt(numTactics))
        const rows = Math.ceil(numTactics / cols)

        const regionWidth = (canvasWidth - tacticSpacing * 2) / cols
        const regionHeight = (canvasHeight - tacticSpacing * 2) / rows

        for (let row = 0; row < rows; row++) {
          for (let col = 0; col < cols; col++) {
            if (regions.length >= numTactics) break

            const x = tacticSpacing + col * regionWidth
            const y = tacticSpacing + row * regionHeight

            regions.push({
              x,
              y,
              width: regionWidth,
              height: regionHeight
            })
          }
        }

        return regions
      }

      function optimizeTacticPositions(preliminaryPositions, singleTacticTechniques, multiTacticTechniques) {
        const optimized = new Map(preliminaryPositions)
        const maxIterations = 50
        const minDistance = 300

        for (let iteration = 0; iteration < maxIterations; iteration++) {
          let hasMovement = false

          const forces = new Map()

          preliminaryPositions.forEach((pos, tactic) => {
            let forceX = 0
            let forceY = 0

            const singleTechniques = singleTacticTechniques.get(tactic) || []
            singleTechniques.forEach(technique => {
              if (nodePositions.value[technique.id]) {
                const techPos = nodePositions.value[technique.id]
                const distance = Math.sqrt(Math.pow(techPos.x - pos.x, 2) + Math.pow(techPos.y - pos.y, 2))
                if (distance > techniqueRadius * 0.8) {
                  forceX += (techPos.x - pos.x) * 0.1
                  forceY += (techPos.y - pos.y) * 0.1
                }
              }
            })

            multiTacticTechniques.forEach(({ technique, tactics }) => {
              if (tactics.includes(tactic) && nodePositions.value[technique.id]) {
                const techPos = nodePositions.value[technique.id]
                const distance = Math.sqrt(Math.pow(techPos.x - pos.x, 2) + Math.pow(techPos.y - pos.y, 2))
                if (distance > 200) {
                  forceX += (techPos.x - pos.x) * 0.05
                  forceY += (techPos.y - pos.y) * 0.05
                }
              }
            })

            preliminaryPositions.forEach((otherPos, otherTactic) => {
              if (otherTactic !== tactic) {
                const distance = Math.sqrt(Math.pow(otherPos.x - pos.x, 2) + Math.pow(otherPos.y - pos.y, 2))
                if (distance < minDistance) {
                  const repulsion = (minDistance - distance) * 0.1
                  forceX -= (otherPos.x - pos.x) / distance * repulsion
                  forceY -= (otherPos.y - pos.y) / distance * repulsion
                }
              }
            })

            forces.set(tactic, { x: forceX, y: forceY })
          })

          forces.forEach((force, tactic) => {
            const currentPos = optimized.get(tactic)
            const newX = Math.max(100, Math.min(canvasWidth - 100, currentPos.x + force.x))
            const newY = Math.max(100, Math.min(canvasHeight - 100, currentPos.y + force.y))

            if (Math.abs(newX - currentPos.x) > 0.1 || Math.abs(newY - currentPos.y) > 0.1) {
              hasMovement = true
              optimized.set(tactic, { x: newX, y: newY })
            }
          })

          if (!hasMovement) break
        }

        return optimized
      }

      function layoutSingleTechniquesAroundTactic(techniques, tacticX, tacticY) {
        if (techniques.length === 0) return

        const totalNodes = techniques.length
        const angleStep = (2 * Math.PI) / Math.max(totalNodes, 8)

        techniques.forEach((technique, index) => {
          const angle = index * angleStep
          const radius = techniqueRadius + (Math.floor(index / 8) * 100)
          const x = tacticX + radius * Math.cos(angle)
          const y = tacticY + radius * Math.sin(angle)

          nodePositions.value[technique.id] = { x, y }
        })
      }

      function findOptimalPositionForTechnique(centerX, centerY, technique) {
        const candidates = []

        for (let i = 0; i < 12; i++) {
          const angle = (i / 12) * 2 * Math.PI
          const radius = 150 + Math.floor(i / 4) * 100
          const x = centerX + radius * Math.cos(angle)
          const y = centerY + radius * Math.sin(angle)
          candidates.push({ x, y })
        }

        let bestPos = candidates[0]
        let minOverlaps = Infinity

        candidates.forEach(pos => {
          let overlaps = 0
          Object.values(nodePositions.value).forEach(existingPos => {
            const distance = Math.sqrt(
              Math.pow(pos.x - existingPos.x, 2) + Math.pow(pos.y - existingPos.y, 2)
            )
            if (distance < 180) {
              overlaps++
            }
          })
          if (overlaps < minOverlaps) {
            minOverlaps = overlaps
            bestPos = pos
          }
        })

        return bestPos
      }

      function layoutOtherNodes(otherNodes) {
        if (otherNodes.length === 0) return

        const startX = tacticSpacing * 0.5
        const startY = canvasHeight - tacticSpacing
        const gridSpacing = otherNodeSpacing

        const cols = Math.ceil(Math.sqrt(otherNodes.length))
        const rows = Math.ceil(otherNodes.length / cols)

        otherNodes.forEach((node, index) => {
          const row = Math.floor(index / cols)
          const col = index % cols
          const x = startX + col * gridSpacing
          const y = startY + row * gridSpacing
          nodePositions.value[node.id] = { x, y }
        })
      }
    }
    
    // 自动布局
    const autoLayout = () => {
      initNodePositions()
    }
    
    // 获取节点位置（考虑缩放和偏移）
    const getNodePosition = (nodeId) => {
      const pos = nodePositions.value[nodeId] || { x: 0, y: 0 }
      return {
        x: (pos.x + offsetX.value) * zoom.value,
        y: (pos.y + offsetY.value) * zoom.value
      }
    }
    
    // 获取节点样式
    const getNodeStyle = (node) => {
      const pos = getNodePosition(node.id)
      const width = 140 * nodeScale.value
      const height = 60 * nodeScale.value

      return {
        left: `${pos.x - width / 2}px`,
        top: `${pos.y - height / 2}px`,
        width: `${width}px`,
        height: `${height}px`,
        transform: `scale(${zoom.value})`,
        zIndex: selectedNode.value?.id === node.id ? 100 : (hoverNode.value?.id === node.id ? 50 : 10)
      }
    }
    
    // 获取节点提示文本
    const getNodeTooltip = (node) => {
      const connections = getNodeConnections(node.id)
      let tooltip = `${node.label || node.id}\n` +
             `类型: ${node.type}\n` +
             `连接数: ${connections.length}\n` +
             `ID: ${node.id}`
      
      if (focusMode.value) {
        if (focusRootNodes.value.some(n => n.id === node.id)) {
          tooltip += '\n根节点'
        } else if (focusNodeLevels.value[node.id]) {
          tooltip += `\n${focusNodeLevels.value[node.id]}级关联节点`
        }
      }
      
      return tooltip
    }
    
    // 获取边透明度
    const getEdgeOpacity = (edge) => {
      let opacity = 0.6
      
      if (focusMode.value) {
        // 聚焦模式下：显示相关的边，隐藏无关的边
        const isFocusRelated = focusEdges.value.includes(edge.id)
        opacity = isFocusRelated ? 0.8 : 0.1
      } else if (selectedNode.value) {
        // 非聚焦模式下：高亮与选中节点相关的边
        const isRelated = edge.source === selectedNode.value.id || edge.target === selectedNode.value.id
        if (!isRelated) opacity = 0.2
      }
      
      if (hoverEdge.value?.id === edge.id) opacity = 1
      if (selectedEdge.value?.id === edge.id) opacity = 1
      
      if (highlightedType.value) {
        const sourceNode = nodes.value.find(n => n.id === edge.source)
        const targetNode = nodes.value.find(n => n.id === edge.target)
        if (sourceNode?.type === highlightedType.value || targetNode?.type === highlightedType.value) {
          opacity = 0.9
        }
      }
      
      return opacity
    }
    
    // 截断文本
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }
    
    // 格式化属性值
    const formatPropertyValue = (value) => {
      if (typeof value === 'object') return JSON.stringify(value, null, 2)
      return String(value)
    }
    
    // 选择节点
    const selectNode = (node) => {
      if (draggedNode.value) return
      selectedNode.value = selectedNode.value?.id === node.id ? null : node
      selectedEdge.value = null
    }
    
    // 开始拖拽节点
    const startNodeDrag = (node, event) => {
      event.preventDefault()
      event.stopPropagation()
      draggedNode.value = node
      dragStart.value = {
        x: event.clientX,
        y: event.clientY,
        nodeX: nodePositions.value[node.id].x,
        nodeY: nodePositions.value[node.id].y
      }
      
      const onMouseMove = (moveEvent) => {
        if (!draggedNode.value) return
        
        const deltaX = (moveEvent.clientX - dragStart.value.x) / zoom.value
        const deltaY = (moveEvent.clientY - dragStart.value.y) / zoom.value
        
        nodePositions.value[draggedNode.value.id] = {
          x: dragStart.value.nodeX + deltaX,
          y: dragStart.value.nodeY + deltaY
        }
      }
      
      const onMouseUp = () => {
        draggedNode.value = null
        document.removeEventListener('mousemove', onMouseMove)
        document.removeEventListener('mouseup', onMouseUp)
      }
      
      document.addEventListener('mousemove', onMouseMove)
      document.addEventListener('mouseup', onMouseUp)
    }
    
    // 开始拖动画布
    const startDrag = (event) => {
      if (event.target.closest('.knowledge-node')) return

      event.preventDefault()
      isDragging.value = true
      dragStart.value = {
        x: event.clientX,
        y: event.clientY,
        offsetX: offsetX.value,
        offsetY: offsetY.value
      }
    }
    
    // 处理画布拖拽
    const handleDrag = (event) => {
      if (!isDragging.value) return
      
      const deltaX = event.clientX - dragStart.value.x
      const deltaY = event.clientY - dragStart.value.y
      
      offsetX.value = dragStart.value.offsetX + deltaX / zoom.value
      offsetY.value = dragStart.value.offsetY + deltaY / zoom.value
    }
    
    // 停止拖拽
    const stopDrag = () => {
      isDragging.value = false
    }
    
    // 处理滚轮缩放
    const handleWheel = (event) => {
      event.preventDefault()

      const delta = event.deltaY > 0 ? -0.1 : 0.1
      const newZoom = Math.max(0.3, Math.min(3, zoom.value + delta))

      // 计算缩放中心点
      const rect = event.target.getBoundingClientRect()
      const mouseX = event.clientX - rect.left
      const mouseY = event.clientY - rect.top

      // 调整偏移以保持鼠标位置固定
      const scaleFactor = newZoom / zoom.value
      offsetX.value = mouseX * (1 - scaleFactor) / newZoom + offsetX.value * scaleFactor
      offsetY.value = mouseY * (1 - scaleFactor) / newZoom + offsetY.value * scaleFactor

      zoom.value = newZoom
    }
    
    // 缩放控制
    const zoomIn = () => {
      zoom.value = Math.min(2, zoom.value + 0.1)
    }
    
    const zoomOut = () => {
      zoom.value = Math.max(0.5, zoom.value - 0.1)
    }
    
    // 重置视图
    const resetView = () => {
      zoom.value = 1
      offsetX.value = 0
      offsetY.value = 0
      selectedNode.value = null
      selectedEdge.value = null
      hoverNode.value = null
      hoverEdge.value = null
      highlightedType.value = null
      exitFocusMode()
    }
    
    // 清除选择
    const clearSelection = () => {
      selectedNode.value = null
      selectedEdge.value = null
      highlightedType.value = null
      exitFocusMode()
    }
    
    // 高亮类型
    const highlightType = (type) => {
      highlightedType.value = type
    }
    
    // 重置类型高亮
    const resetTypeHighlight = () => {
      if (!selectedNode.value) {
        highlightedType.value = null
      }
    }
    
    // ============= 聚焦模式相关函数 =============
    
    // 进入聚焦模式
    const enterFocusMode = () => {
      if (!selectedNode.value) return
      
      focusMode.value = true
      focusRootNodes.value = [selectedNode.value]
      calculateFocusElements()
    }
    
    // 退出聚焦模式
    const exitFocusMode = () => {
      focusMode.value = false
      focusNodes.value = []
      focusEdges.value = []
      focusRootNodes.value = []
      focusNodeLevels.value = {}
    }
    
    // 计算聚焦元素 - 修复边隐藏问题
    const calculateFocusElements = () => {
      if (!focusMode.value || focusRootNodes.value.length === 0) return
      
      // 重置状态
      const visitedNodes = new Set()
      const nodeLevels = {}
      const relevantEdges = new Set()
      
      // 计算实际遍历深度：focusDepth-1
      const maxDepth = focusDepth.value - 1
      
      // BFS遍历，收集指定深度内的节点
      const queue = [...focusRootNodes.value.map(node => ({ node, depth: 0 }))]
      
      while (queue.length > 0) {
        const { node, depth } = queue.shift()
        
        if (depth > maxDepth) continue
        if (visitedNodes.has(node.id)) continue
        
        visitedNodes.add(node.id)
        nodeLevels[node.id] = depth
        
        // 找到与该节点相连的边
        const connectedEdges = edges.value.filter(edge => 
          edge.source === node.id || edge.target === node.id
        )
        
        connectedEdges.forEach(edge => {
          // 确定相邻节点
          const neighborId = edge.source === node.id ? edge.target : edge.source
          const neighborNode = nodes.value.find(n => n.id === neighborId)
          
          // 只有当相邻节点在已访问或将要访问的集合中时，才添加这条边
          if (neighborNode) {
            // 添加相邻节点到队列（如果未超过深度限制）
            if (depth < maxDepth && !visitedNodes.has(neighborId)) {
              queue.push({ node: neighborNode, depth: depth + 1 })
            }
            
            // 只有当两个节点都在可见范围内时，才添加这条边
            // 这里我们会在遍历结束后重新计算，但先添加这条边
            relevantEdges.add(edge.id)
          }
        })
      }
      
      // 更新聚焦状态
      focusNodes.value = Array.from(visitedNodes)
      focusEdges.value = Array.from(relevantEdges)
      focusNodeLevels.value = nodeLevels
      
      console.log(`聚焦模式: 深度=${focusDepth.value}, 显示节点=${focusNodes.value.length}, 显示边=${focusEdges.value.length}`)
    }
    
    // 设置聚焦深度
    const setFocusDepth = (depth) => {
      focusDepth.value = depth
      calculateFocusElements()
    }
    
    // 获取深度标签
    const getDepthLabel = (depth) => {
      switch(depth) {
        case 2: return '一级关联'
        case 3: return '二级关联'
        case 4: return '三级关联'
        default: return `${depth-1}级关联`
      }
    }
    
    // 获取深度文本描述
    const getFocusDepthText = () => {
      return getDepthLabel(focusDepth.value)
    }
    
    // 获取深度详细描述
    const getFocusDepthDescription = () => {
      if (focusDepth.value === 2) {
        return '显示选中节点及其直接关联的节点'
      } else if (focusDepth.value === 3) {
        return '显示选中节点、直接关联节点及其关联的节点'
      } else if (focusDepth.value === 4) {
        return '显示选中节点、直接关联节点、二级关联节点及其关联的节点'
      }
      return ''
    }
    
    // 获取指定层级的节点数量
    const getLevelNodeCount = (level) => {
      if (!focusMode.value) return 0
      
      return Object.values(focusNodeLevels.value).filter(l => l === level).length
    }
    
    // 删除选中节点
    const deleteSelectedNode = async () => {
      if (!selectedNode.value) return
      
      if (!confirm(`确定要删除节点 "${selectedNode.value.label}" 吗？此操作将同步删除后端数据。`)) {
        return
      }
      
      try {
        loading.value = true
        
        // 调用后端API删除节点
        const response = await fetch(`/api/graph/delete_node/${selectedNode.value.id}`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          // 从前端数据中移除节点及其关联边
          const nodeId = selectedNode.value.id
          
          // 移除节点
          nodes.value = nodes.value.filter(n => n.id !== nodeId)
          
          // 移除关联边
          edges.value = edges.value.filter(e => e.source !== nodeId && e.target !== nodeId)
          
          // 退出聚焦模式
          exitFocusMode()
          selectedNode.value = null
          
          // 重新初始化布局
          initNodePositions()
          
          console.log('节点删除成功')
        } else {
          throw new Error('删除失败')
        }
      } catch (err) {
        console.error('删除节点失败:', err)
        alert('删除失败，请重试')
      } finally {
        loading.value = false
      }
    }
    
    // 监听聚焦深度变化
    watch(focusDepth, () => {
      if (focusMode.value) {
        calculateFocusElements()
      }
    })
    
    onMounted(() => {
      fetchData()
    })
    
    return {
      // 数据状态
      loading,
      error,
      nodes,
      edges,
      
      // 视图状态
      selectedNode,
      selectedEdge,
      hoverNode,
      hoverEdge,
      draggedNode,
      isDragging,
      
      // 视图控制
      zoom,
      showNodeLabels,
      showEdgeLabels,
      highlightedType,
      
      // 聚焦模式
      focusMode,
      focusDepth,
      focusNodes,
      focusEdges,
      focusRootNodes,
      focusNodeLevels,
      
      // 计算属性
      typeDistribution,
      visibleNodes,
      visibleEdges,
      
      // 方法
      fetchData,
      getTypeColor,
      getEdgeColor,
      getTypeAbbr,
      isTacticNode,
      isTechniqueNode,
      getNodeConnections,
      handleNodeMouseLeave,
      handleConnectionMouseLeave,
      getNodePosition,
      getNodeStyle,
      getNodeTooltip,
      getEdgeOpacity,
      truncateText,
      formatPropertyValue,
      selectNode,
      startNodeDrag,
      startDrag,
      handleDrag,
      stopDrag,
      handleWheel,
      zoomIn,
      zoomOut,
      resetView,
      clearSelection,
      highlightType,
      resetTypeHighlight,
      autoLayout,
      
      // 聚焦模式方法
      enterFocusMode,
      exitFocusMode,
      setFocusDepth,
      getDepthLabel,
      getFocusDepthText,
      getFocusDepthDescription,
      getLevelNodeCount,
      deleteSelectedNode
    }
  }
}
</script>

<style scoped>
.knowledge-graph-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  overflow: hidden;
}

/* 顶部信息栏 */
.top-bar {
  background: white;
  padding: 15px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
  flex-shrink: 0;
}

.page-title h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.subtitle {
  margin: 4px 0 0;
  color: #7f8c8d;
  font-size: 14px;
}

/* 主布局 */
.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧控制面板 */
.left-panel {
  width: 280px;
  background: white;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  border-right: 1px solid #eaeaea;
  overflow-y: auto;
  flex-shrink: 0;
}

.control-section h3,
.legend-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.control-group {
  margin-bottom: 20px;
}

.control-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

/* 深度控制 */
.depth-control {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.depth-btn {
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #4a5568;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.depth-btn:hover {
  background: #f7fafc;
}

.depth-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

.control-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  flex: 1;
  padding: 12px 16px;
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

/* 图例 */
.legend-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.legend-item:hover {
  background: #f7fafc;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 14px;
  color: #2d3748;
}

.legend-count {
  font-size: 12px;
  color: #718096;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
}

/* 中间图谱区域 */
.center-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.graph-header {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.status-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4a5568;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e53e3e;
}

.ready-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #38a169;
}

.focus-indicator {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
}

.btn-small {
  padding: 6px 12px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #4a5568;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-small:hover {
  background: #edf2f7;
}

.btn-small.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.btn-danger {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border: none;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
}

.view-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 4px;
}

.zoom-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #4a5568;
  transition: all 0.2s;
}

.zoom-btn:hover {
  background: #f7fafc;
}

.zoom-level {
  min-width: 50px;
  text-align: center;
  font-size: 13px;
  color: #718096;
}

/* 图谱画布 */
.graph-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #f8fafc;
}

.graph-canvas {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  cursor: grab;
}

.graph-canvas.dragging {
  cursor: grabbing;
}

/* 边 - 改为直线 */
.edges-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.edge-line {
  pointer-events: stroke;
  transition: all 0.3s ease;
  stroke-linecap: round;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.edge-line:hover {
  opacity: 1 !important;
  stroke-width: 3px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
}

.edge-label {
  font-size: 11px;
  fill: #4a5568;
  font-weight: 600;
  pointer-events: none;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
}

/* 节点 */
.knowledge-node {
  position: absolute;
  cursor: pointer;
  transition: transform 0.3s ease, z-index 0.3s ease;
}

/* 节点卡片 */
.node-card {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  align-items: center;
}

/* 类型指示器 */
.node-type-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  background-color: var(--type-color);
  transition: all 0.3s ease;
}

/* 节点内容 */
.node-content {
  flex: 1;
  padding: 8px 12px 8px 18px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

/* 主要标签 */
.node-main-label {
  font-size: 13px;
  font-weight: 600;
  color: #2d3748;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 类型标签 */
.node-type-label {
  font-size: 10px;
  font-weight: 500;
  color: var(--type-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.8;
}

/* 装饰元素 */
.node-decoration {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 4px;
  background: var(--type-color);
  border-radius: 50%;
  opacity: 0.4;
}

/* Tactic节点特殊样式 */
.knowledge-node[class*="tactic"] .node-card,
.knowledge-node[class*="TA"] .node-card {
  border-color: #e74c3c;
  box-shadow: 0 6px 24px rgba(231, 76, 60, 0.15);
}

.knowledge-node[class*="tactic"] .node-type-indicator,
.knowledge-node[class*="TA"] .node-type-indicator {
  background: linear-gradient(180deg, #e74c3c 0%, #c0392b 100%);
  width: 8px;
}

.knowledge-node[class*="tactic"] .node-decoration,
.knowledge-node[class*="TA"] .node-decoration {
  background: #e74c3c;
  box-shadow: 0 0 8px rgba(231, 76, 60, 0.4);
}

/* Technique节点特殊样式 */
.knowledge-node[class*="technique"] .node-card,
.knowledge-node[class*="TE"] .node-card {
  border-color: #f39c12;
  box-shadow: 0 6px 24px rgba(243, 156, 18, 0.15);
}

.knowledge-node[class*="technique"] .node-type-indicator,
.knowledge-node[class*="TE"] .node-type-indicator {
  background: linear-gradient(180deg, #f39c12 0%, #e67e22 100%);
  width: 8px;
}

.knowledge-node[class*="technique"] .node-decoration,
.knowledge-node[class*="TE"] .node-decoration {
  background: #f39c12;
  box-shadow: 0 0 8px rgba(243, 156, 18, 0.4);
}

/* 悬停效果 */
.knowledge-node:hover .node-card {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-color: var(--type-color);
}

.knowledge-node:hover .node-type-indicator {
  width: 10px;
}

.knowledge-node:hover .node-decoration {
  opacity: 0.8;
  transform: translateY(-50%) scale(1.2);
}

/* 选中状态 */
.knowledge-node.selected .node-card {
  border-color: var(--type-color);
  border-width: 3px;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), 0 12px 40px rgba(0, 0, 0, 0.15);
  background: linear-gradient(135deg, #fefefe 0%, #f8fafc 100%);
}

.knowledge-node.selected .node-type-indicator {
  width: 12px;
  box-shadow: 0 0 12px rgba(102, 126, 234, 0.3);
}

.knowledge-node.selected .node-decoration {
  opacity: 1;
  box-shadow: 0 0 12px rgba(102, 126, 234, 0.4);
}

/* 聚焦模式节点样式 */
.knowledge-node.focus-root .node-card {
  border-width: 3px;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2), 0 12px 40px rgba(102, 126, 234, 0.3);
}

.knowledge-node.focus-level-1 .node-card {
  border-color: #48bb78;
  box-shadow: 0 4px 20px rgba(72, 187, 120, 0.2);
}

.knowledge-node.focus-level-2 .node-card {
  border-color: #f59e0b;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.2);
}

.knowledge-node.focus-level-3 .node-card {
  border-color: #9b59b6;
  box-shadow: 0 4px 20px rgba(155, 89, 182, 0.2);
}

/* 拖拽状态 */
.knowledge-node.dragging .node-card {
  opacity: 0.9;
  transform: rotate(2deg) scale(1.05);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
}

/* 高亮状态 */
.knowledge-node.highlighted .node-card {
  border-color: var(--type-color);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.knowledge-node.highlighted .node-type-indicator {
  width: 8px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
}

/* 右侧详情面板 */
.right-panel {
  width: 320px;
  background: white;
  padding: 20px;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #eaeaea;
  overflow-y: auto;
  flex-shrink: 0;
}

.details-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eaeaea;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  padding: 6px 12px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #4a5568;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #edf2f7;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
}

/* 聚焦模式信息 */
.focus-info {
  background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.focus-header {
  margin-bottom: 16px;
}

.focus-title h4 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.focus-description {
  margin: 4px 0 0;
  font-size: 13px;
  color: #718096;
}

.depth-info {
  display: grid;
  gap: 8px;
}

.depth-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.depth-stat .stat-label {
  font-size: 13px;
  color: #4a5568;
  font-weight: 500;
}

.depth-stat .stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
  min-width: 30px;
  text-align: center;
}

/* 选中节点信息 */
.selected-node-info {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.node-header {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eaeaea;
}

.node-type-large {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.node-title {
  flex: 1;
}

.node-title h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
}

.node-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.type-tag {
  background: #f1f5f9;
  color: #4a5568;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.focus-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.details-grid {
  margin-bottom: 24px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.detail-row label {
  font-size: 13px;
  color: #718096;
  font-weight: 500;
}

.detail-row .value {
  font-size: 14px;
  color: #2d3748;
  font-weight: 500;
  max-width: 180px;
  word-break: break-all;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}

.properties-grid {
  display: grid;
  gap: 8px;
}

.property-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
}

.property-key {
  font-size: 13px;
  color: #718096;
  font-weight: 500;
}

.property-value {
  font-size: 13px;
  color: #2d3748;
  font-weight: 500;
  max-width: 140px;
  word-break: break-word;
  text-align: right;
}

.connections-section {
  border-top: 1px solid #eaeaea;
  padding-top: 16px;
}

.connections-section h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}

.connections-list {
  max-height: 300px;
  overflow-y: auto;
}

.connection-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.connection-item:hover {
  background: #edf2f7;
  transform: translateX(2px);
}

.connection-direction {
  width: 24px;
  height: 24px;
  background: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #667eea;
  font-weight: bold;
  flex-shrink: 0;
}

.connection-info {
  flex: 1;
  min-width: 0;
}

.connection-target {
  font-size: 13px;
  color: #4a5568;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.connection-meta {
  font-size: 11px;
  color: #a0aec0;
  margin-top: 2px;
}

.connection-type-tag {
  font-size: 11px;
  color: #718096;
  background: #e2e8f0;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

/* 概览信息 */
.overview-info {
  animation: fadeIn 0.3s ease;
}

.stats-overview {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.stat-overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-overview-item .stat-label {
  font-size: 13px;
  color: #718096;
  font-weight: 500;
}

.stat-overview-item .stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
}

/* 聚焦提示 */
.focus-hint {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
  border-radius: 12px;
  margin-top: 20px;
}

.hint-text {
  margin: 0;
  font-size: 14px;
  color: #718096;
}
</style>