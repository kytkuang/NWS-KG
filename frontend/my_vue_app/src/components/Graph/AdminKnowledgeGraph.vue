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
          <div class="control-group">
            <label>布局类型</label>
            <select v-model="layoutType" class="select-input">
              <option value="circular">智能布局（战术-技术关系优化）</option>
              <option value="grid">网格布局</option>
            </select>
          </div>
          
          <div class="control-buttons">
            <button @click="resetView" class="btn btn-secondary">
              重置视图
            </button>
            <button @click="autoLayout" class="btn btn-primary">
              自动布局
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
              已加载 {{ nodes.length }} 个节点和 {{ edges.length }} 条关系
            </div>
          </div>
          
          <div class="view-controls">
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
            <!-- 关系连接线 -->
            <svg class="edges-layer" :width="canvasWidth" :height="canvasHeight">
              <defs>
                <marker 
                  id="arrowhead" 
                  markerWidth="10" 
                  markerHeight="7" 
                  refX="9" 
                  refY="3.5" 
                  orient="auto"
                >
                  <polygon points="0 0, 10 3.5, 0 7" fill="#666" opacity="0.7" />
                </marker>
              </defs>
              
              <g v-for="edge in edges" :key="edge.id">
                <line
                  :x1="getNodePosition(edge.source).x"
                  :y1="getNodePosition(edge.source).y"
                  :x2="getNodePosition(edge.target).x"
                  :y2="getNodePosition(edge.target).y"
                  :stroke="getEdgeColor(edge.type)"
                  stroke-width="2"
                  :marker-end="'url(#arrowhead)'"
                  :opacity="getEdgeOpacity(edge)"
                  class="edge-line"
                  @mouseenter="hoverEdge = edge"
                  @mouseleave="hoverEdge = null"
                />
                
              </g>
            </svg>

            <!-- 节点 -->
            <div
              v-for="node in nodes"
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
                highlighted: highlightedType === node.type
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
            <h3>节点详情</h3>
            <div class="panel-actions">
              <button @click="clearSelection" class="icon-btn" title="清除选择">
                清除
              </button>
            </div>
          </div>
          
          <div class="panel-content">
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
                    </div>
                    <div class="connection-type-tag">{{ conn.target.type }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 未选中时的概览信息 -->
            <div v-else class="overview-info">
              <h4>图谱概览</h4>
              <div class="type-distribution-chart">
                <div 
                  v-for="type in typeDistribution" 
                  :key="type.type"
                  class="type-bar"
                  @click="highlightType(type.type)"
                  @mouseover="highlightType(type.type)"
                  @mouseout="resetTypeHighlight"
                  :style="{
                    width: `${(type.count / nodes.length) * 100}%`,
                    backgroundColor: getTypeColor(type.type)
                  }"
                >
                  <span class="type-bar-label">{{ type.type }} ({{ type.count }})</span>
                </div>
              </div>
              
              <div class="stats-overview">
                <div class="stat-overview-item">
                  <span class="stat-label">节点总数</span>
                  <span class="stat-value">{{ nodes.length }}</span>
                </div>
                <div class="stat-overview-item">
                  <span class="stat-label">关系总数</span>
                  <span class="stat-value">{{ edges.length }}</span>
                </div>
                <div class="stat-overview-item">
                  <span class="stat-label">平均连接度</span>
                  <span class="stat-value">
                    {{ nodes.length > 0 ? (edges.length / nodes.length).toFixed(2) : 0 }}
                  </span>
                </div>
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
    const layoutType = ref('circular') // 智能布局
    const nodeScale = ref(0.8)
    const zoom = ref(1)
    const showNodeLabels = ref(true)
    const highlightedType = ref(null)
    
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
    
    // 类型颜色映射
    const typeColors = {
      // 特殊类型：tactic和technique（MITRE ATT&CK相关）
      'Tactic': '#e74c3c',      // 鲜红色 - tactic
      'TA': '#e74c3c',          // 鲜红色 - tactic缩写
      'Technique': '#f39c12',   // 橙色 - technique
      'TE': '#f39c12',          // 橙色 - technique缩写
      'tactic': '#e74c3c',      // 小写兼容
      'technique': '#f39c12',   // 小写兼容

      // 其他类型
      'Person': '#3498db',      // 蓝色
      'Organization': '#2ecc71', // 绿色
      'Location': '#9b59b6',    // 紫色
      'Event': '#f59e0b',       // 橙黄色
      'Concept': '#1abc9c',     // 青色
      'Product': '#34495e',     // 深蓝灰
      'Topic': '#8e44ad',       // 深紫色
      'Technology': '#d35400',  // 棕色
      'Industry': '#16a085',    // 深青色
      'Skill': '#27ae60',       // 深绿色
      'default': '#7f8c8d'      // 灰色
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
        { id: '1', label: '人工智能', type: 'Technology', properties: { description: '模拟的人工智能节点' } },
        { id: '2', label: '机器学习', type: 'Concept', properties: { description: '模拟的机器学习节点' } },
        { id: '3', label: 'Python', type: 'Technology', properties: { description: '模拟的Python节点' } },
        { id: '4', label: 'TensorFlow', type: 'Technology', properties: { description: '模拟的TensorFlow节点' } },
        { id: '5', label: '神经网络', type: 'Concept', properties: { description: '模拟的神经网络节点' } },
        { id: '6', label: '数据科学', type: 'Topic', properties: { description: '模拟的数据科学节点' } },
        { id: '7', label: '深度学习', type: 'Concept', properties: { description: '模拟的深度学习节点' } },
        { id: '8', label: '大数据', type: 'Technology', properties: { description: '模拟的大数据节点' } },
        { id: '9', label: '云计算', type: 'Technology', properties: { description: '模拟的云计算节点' } },
        { id: '10', label: '张量', type: 'Concept', properties: { description: '模拟的张量节点' } }
      ]
      
      edges.value = [
        { id: 'e1', source: '1', target: '2', type: 'RELATES_TO', label: '包含' },
        { id: 'e2', source: '2', target: '3', type: 'USES', label: '使用' },
        { id: 'e3', source: '2', target: '4', type: 'USES', label: '使用' },
        { id: 'e4', source: '2', target: '5', type: 'CONTAINS', label: '包含' },
        { id: 'e5', source: '5', target: '7', type: 'RELATES_TO', label: '关联' },
        { id: 'e6', source: '6', target: '2', type: 'INCLUDES', label: '包括' },
        { id: 'e7', source: '6', target: '8', type: 'RELATES_TO', label: '关联' },
        { id: 'e8', source: '6', target: '9', type: 'RELATES_TO', label: '关联' },
        { id: 'e9', source: '4', target: '10', type: 'USES', label: '使用' },
        { id: 'e10', source: '7', target: '4', type: 'IMPLEMENTS', label: '实现' }
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

    // 智能布局算法 - 优化tactic-technique关系布局，减少交叉
    const useIntelligentLayout = () => {
      const centerX = canvasWidth / 2
      const centerY = canvasHeight / 2

      // 1. 识别tactic和technique节点
      const tacticNodes = nodes.value.filter(node => isTacticNode(node))
      const techniqueNodes = nodes.value.filter(node => isTechniqueNode(node))
      const otherNodes = nodes.value.filter(node =>
        !tacticNodes.includes(node) && !techniqueNodes.includes(node)
      )

      console.log(`智能布局: ${tacticNodes.length} tactics, ${techniqueNodes.length} techniques, ${otherNodes.length} others`)

      // 2. 分析technique的连接关系
      const techniqueConnections = new Map() // technique -> 连接的tactics

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
      const singleTacticTechniques = new Map() // tactic -> techniques（只连接一个tactic）
      const multiTacticTechniques = [] // 连接多个tactic的techniques

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

      console.log(`Technique分类: 单tactic ${Array.from(singleTacticTechniques.values()).flat().length} 个, 多tactic ${multiTacticTechniques.length} 个`)

      // 4. 计算布局参数
      const tacticSpacing = 500 // 大幅增大tactic之间的距离
      const techniqueRadius = 200 // 增大technique围绕tactic的半径
      const otherNodeSpacing = 200 // 其他节点间距

      // 5. 智能布局tactics - 让tactic靠近自己的techniques
      const tacticPositions = new Map()

      if (tacticNodes.length === 1) {
        // 只有一个tactic，放在中心
        const tactic = tacticNodes[0]
        const tacticX = centerX
        const tacticY = centerY
        tacticPositions.set(tactic, { x: tacticX, y: tacticY })

        // 布局该tactic的单techniques
        const singleTechniques = singleTacticTechniques.get(tactic) || []
        layoutSingleTechniquesAroundTactic(singleTechniques, tacticX, tacticY)

      } else {
        // 多个tactics - 使用基于邻近关系的智能布局
        const numTactics = tacticNodes.length

        // 预估每个tactic的最佳位置（基于其techniques的数量和分布）
        const preliminaryPositions = new Map()

        // 为每个tactic分配一个初始区域
        const regions = calculateOptimalRegions(numTactics)

        tacticNodes.forEach((tactic, index) => {
          const region = regions[index]
          const singleTechniques = singleTacticTechniques.get(tactic) || []
          const multiTechniques = multiTacticTechniques.filter(mt => mt.tactics.includes(tactic))

          // 估算该tactic需要的空间
          const estimatedWidth = Math.max(400, Math.sqrt(singleTechniques.length + multiTechniques.length) * 150)
          const estimatedHeight = estimatedWidth

          // 在分配的区域内选择一个合适的位置
          const tacticX = region.x + region.width * 0.5
          const tacticY = region.y + region.height * 0.5

          preliminaryPositions.set(tactic, { x: tacticX, y: tacticY })
        })

        // 优化tactic位置 - 让它们更好地分布在画布上
        const optimizedPositions = optimizeTacticPositions(preliminaryPositions, singleTacticTechniques, multiTacticTechniques)
        optimizedPositions.forEach((pos, tactic) => {
          tacticPositions.set(tactic, pos)
        })

        // 设置最终的tactic位置
        tacticPositions.forEach((pos, tactic) => {
          nodePositions.value[tactic.id] = pos

          // 布局该tactic的单techniques
          const singleTechniques = singleTacticTechniques.get(tactic) || []
          layoutSingleTechniquesAroundTactic(singleTechniques, pos.x, pos.y)
        })
      }

      // 6. 布局多tactic techniques - 放在相关tactics的中心位置
      multiTacticTechniques.forEach(({ technique, tactics }) => {
        if (tactics.length === 0) return

        // 计算相关tactics的中心位置
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

        // 在中心位置附近找一个合适的位置，避免与其他节点重叠
        const optimalPos = findOptimalPositionForTechnique(centerX, centerY, technique)
        nodePositions.value[technique.id] = optimalPos
      })

      // 7. 布局其他类型节点
      layoutOtherNodes(otherNodes)

      // 辅助函数：计算画布的最佳区域划分
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

      // 辅助函数：优化tactic位置，让它们更好地分布
      function optimizeTacticPositions(preliminaryPositions, singleTacticTechniques, multiTacticTechniques) {
        const optimized = new Map(preliminaryPositions)
        const maxIterations = 50
        const minDistance = 300 // tactic之间的最小距离

        for (let iteration = 0; iteration < maxIterations; iteration++) {
          let hasMovement = false

          // 为每个tactic计算吸引力（来自其techniques的拉力）
          const forces = new Map()

          preliminaryPositions.forEach((pos, tactic) => {
            let forceX = 0
            let forceY = 0

            // 单tactic techniques的吸引力
            const singleTechniques = singleTacticTechniques.get(tactic) || []
            singleTechniques.forEach(technique => {
              if (nodePositions.value[technique.id]) {
                const techPos = nodePositions.value[technique.id]
                const distance = Math.sqrt(Math.pow(techPos.x - pos.x, 2) + Math.pow(techPos.y - pos.y, 2))
                if (distance > techniqueRadius * 0.8) {
                  // 如果technique离tactic太远，拉近一点
                  forceX += (techPos.x - pos.x) * 0.1
                  forceY += (techPos.y - pos.y) * 0.1
                }
              }
            })

            // 多tactic techniques的吸引力（较弱）
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

            // 排斥力（与其他tactic的距离）
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

          // 应用力并更新位置
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

      // 辅助函数：布局单个tactic周围的techniques
      function layoutSingleTechniquesAroundTactic(techniques, tacticX, tacticY) {
        if (techniques.length === 0) return

        const totalNodes = techniques.length
        const angleStep = (2 * Math.PI) / Math.max(totalNodes, 8) // 至少8个位置，更均匀分布

        techniques.forEach((technique, index) => {
          const angle = index * angleStep
          const radius = techniqueRadius + (Math.floor(index / 8) * 100) // 多层分布，层间距更大
          const x = tacticX + radius * Math.cos(angle)
          const y = tacticY + radius * Math.sin(angle)

          nodePositions.value[technique.id] = { x, y }
        })
      }

      // 辅助函数：为多tactic technique找最优位置
      function findOptimalPositionForTechnique(centerX, centerY, technique) {
        const candidates = []

        // 生成候选位置：在中心周围的多个位置，使用更大的间距
        for (let i = 0; i < 12; i++) {
          const angle = (i / 12) * 2 * Math.PI
          const radius = 150 + Math.floor(i / 4) * 100 // 三层半径，更大间距
          const x = centerX + radius * Math.cos(angle)
          const y = centerY + radius * Math.sin(angle)
          candidates.push({ x, y })
        }

        // 选择与现有节点重叠最少的位置
        let bestPos = candidates[0]
        let minOverlaps = Infinity

        candidates.forEach(pos => {
          let overlaps = 0
          Object.values(nodePositions.value).forEach(existingPos => {
            const distance = Math.sqrt(
              Math.pow(pos.x - existingPos.x, 2) + Math.pow(pos.y - existingPos.y, 2)
            )
            if (distance < 180) { // 增大节点间最小距离
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

      // 辅助函数：布局其他节点
      function layoutOtherNodes(otherNodes) {
        if (otherNodes.length === 0) return

        // 将其他节点放在画布底部，网格布局，使用更大的间距
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
      // 卡片式节点尺寸调整
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
      return `${node.label || node.id}\n` +
             `类型: ${node.type}\n` +
             `连接数: ${connections.length}\n` +
             `ID: ${node.id}`
    }
    
    // 获取边透明度
    const getEdgeOpacity = (edge) => {
      let opacity = 0.6
      
      if (selectedNode.value) {
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
    }
    
    // 清除选择
    const clearSelection = () => {
      selectedNode.value = null
      selectedEdge.value = null
      highlightedType.value = null
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
    
    // 监听布局类型变化
    watch(layoutType, () => {
      initNodePositions()
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
      layoutType,
      zoom,
      showNodeLabels,
      highlightedType,
      
      // 计算属性
      typeDistribution,
      
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
      autoLayout
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

.select-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #2d3748;
  font-size: 14px;
  transition: all 0.2s;
}

.select-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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

/* 边 */
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
  stroke-width: 4px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
}

.edge-label {
  font-size: 11px;
  fill: #4a5568;
  font-weight: 600;
  pointer-events: none;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.1);
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

.icon-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
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

.type-distribution-chart {
  margin-bottom: 24px;
}

.type-bar {
  height: 32px;
  margin-bottom: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.type-bar:hover {
  transform: translateX(4px);
}

.type-bar-label {
  color: white;
  font-size: 13px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.stats-overview {
  display: grid;
  gap: 12px;
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
</style>