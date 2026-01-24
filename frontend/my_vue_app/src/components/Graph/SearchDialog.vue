<template>
  <div class="search-dialog-overlay" @click.self="handleClose">
    <div class="search-dialog">
      <div class="search-dialog-header">
        <h2>节点搜索</h2>
        <button @click="handleClose" class="close-btn">关闭</button>
      </div>
      
      <div class="search-dialog-body">
        <!-- 搜索输入框 -->
        <div class="search-input-section">
          <input
            v-model="searchQuery"
            @input="handleSearch"
            type="text"
            class="search-input-large"
            placeholder="输入节点名称、ID或类型进行搜索..."
            autofocus
          />
          <div v-if="searchQuery" class="search-stats">
            找到 {{ filteredNodes.length }} 个匹配的节点
          </div>
        </div>
        
        <!-- 标签筛选区域 -->
        <div class="tags-section">
          <div class="tags-header">
            <h3>节点类型筛选</h3>
            <button 
              @click="toggleTagsExpanded"
              class="toggle-tags-btn"
            >
              {{ tagsExpanded ? '收起' : '展开' }}
            </button>
          </div>
          
          <div class="tags-container" :class="{ collapsed: !tagsExpanded }">
            <div 
              v-for="tag in availableTags" 
              :key="tag.type"
              class="tag-item"
              :class="{ active: selectedTags.includes(tag.type) }"
              @click="toggleTag(tag.type)"
            >
              <span class="tag-color" :style="{ backgroundColor: getTagColor(tag.type) }"></span>
              <span class="tag-label">{{ tag.type }}</span>
              <span class="tag-count">({{ tag.count }})</span>
            </div>
          </div>
        </div>
        
        <!-- 搜索结果列表 -->
        <div class="results-section">
          <div v-if="filteredNodes.length === 0 && searchQuery" class="no-results">
            未找到匹配的节点
          </div>
          
          <div v-else-if="filteredNodes.length > 0" class="results-list">
            <div 
              v-for="node in filteredNodes" 
              :key="node.id"
              class="result-item"
              @click="selectNode(node)"
              :class="{ selected: selectedNodeId === node.id }"
            >
              <div class="result-item-header">
                <div class="result-type-badge" :style="{ backgroundColor: getTagColor(node.type) }">
                  {{ node.type }}
                </div>
                <div class="result-name">
                  <span v-html="highlightMatch(node.label || node.id, searchQuery)"></span>
                </div>
              </div>
              <div class="result-item-meta">
                <span class="result-id">ID: {{ node.id }}</span>
                <span v-if="node.properties && node.properties.description" class="result-description">
                  {{ truncateText(node.properties.description, 100) }}
                </span>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <p>输入关键词开始搜索，或选择标签进行筛选</p>
          </div>
        </div>
      </div>
      
      <div class="search-dialog-footer">
        <button @click="handleClose" class="btn-cancel">取消</button>
        <button 
          v-if="selectedNodeId"
          @click="confirmSelection"
          class="btn-confirm"
        >
          定位到选中节点
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

export default {
  name: 'SearchDialog',
  props: {
    nodes: {
      type: Array,
      default: () => []
    },
    nodePositions: {
      type: Object,
      default: () => ({})
    },
    getTypeColor: {
      type: Function,
      required: true
    }
  },
  emits: ['close', 'select-node'],
  setup(props, { emit }) {
    const searchQuery = ref('')
    const selectedTags = ref([])
    const tagsExpanded = ref(true)
    const selectedNodeId = ref(null)
    
    // 获取所有可用的标签（节点类型）
    const availableTags = computed(() => {
      const tagCounts = {}
      props.nodes.forEach(node => {
        const type = node.type || 'Unknown'
        tagCounts[type] = (tagCounts[type] || 0) + 1
      })
      
      return Object.entries(tagCounts)
        .map(([type, count]) => ({ type, count }))
        .sort((a, b) => b.count - a.count)
    })
    
    // 过滤节点
    const filteredNodes = computed(() => {
      let results = props.nodes
      
      // 按标签筛选
      if (selectedTags.value.length > 0) {
        results = results.filter(node => 
          selectedTags.value.includes(node.type)
        )
      }
      
      // 按搜索关键词筛选
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.trim().toLowerCase()
        results = results.filter(node => {
          const label = (node.label || '').toLowerCase()
          const id = (node.id || '').toLowerCase()
          const type = (node.type || '').toLowerCase()
          const description = (node.properties?.description || '').toLowerCase()
          
          return label.includes(query) || 
                 id.includes(query) || 
                 type.includes(query) ||
                 description.includes(query)
        })
        
        // 按匹配度排序
        results.sort((a, b) => {
          const query = searchQuery.value.trim().toLowerCase()
          const aLabel = (a.label || '').toLowerCase()
          const bLabel = (b.label || '').toLowerCase()
          const aId = (a.id || '').toLowerCase()
          const bId = (b.id || '').toLowerCase()
          
          const aLabelMatch = aLabel.includes(query) ? 1 : 0
          const bLabelMatch = bLabel.includes(query) ? 1 : 0
          const aIdMatch = aId.includes(query) ? 1 : 0
          const bIdMatch = bId.includes(query) ? 1 : 0
          
          if (aLabelMatch !== bLabelMatch) return bLabelMatch - aLabelMatch
          if (aIdMatch !== bIdMatch) return bIdMatch - aIdMatch
          return aLabel.localeCompare(bLabel)
        })
      }
      
      return results.slice(0, 100) // 最多显示100个结果
    })
    
    // 高亮匹配文本
    const highlightMatch = (text, query) => {
      if (!query || !text) return text
      const regex = new RegExp(`(${query})`, 'gi')
      return String(text).replace(regex, '<mark>$1</mark>')
    }
    
    // 截断文本
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }
    
    // 获取标签颜色
    const getTagColor = (type) => {
      return props.getTypeColor(type)
    }
    
    // 切换标签选择
    const toggleTag = (tagType) => {
      const index = selectedTags.value.indexOf(tagType)
      if (index > -1) {
        selectedTags.value.splice(index, 1)
      } else {
        selectedTags.value.push(tagType)
      }
    }
    
    // 切换标签展开/收起
    const toggleTagsExpanded = () => {
      tagsExpanded.value = !tagsExpanded.value
    }
    
    // 处理搜索
    const handleSearch = () => {
      // 搜索逻辑在 computed 中处理
    }
    
    // 选择节点
    const selectNode = (node) => {
      selectedNodeId.value = node.id
    }
    
    // 确认选择
    const confirmSelection = () => {
      if (selectedNodeId.value) {
        const node = props.nodes.find(n => n.id === selectedNodeId.value)
        if (node) {
          emit('select-node', node)
          handleClose()
        }
      }
    }
    
    // 关闭对话框
    const handleClose = () => {
      emit('close')
    }
    
    // 监听键盘事件
    const handleKeydown = (e) => {
      if (e.key === 'Escape') {
        handleClose()
      }
    }
    
    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
    })
    
    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
    })
    
    return {
      searchQuery,
      selectedTags,
      tagsExpanded,
      selectedNodeId,
      availableTags,
      filteredNodes,
      highlightMatch,
      truncateText,
      getTagColor,
      toggleTag,
      toggleTagsExpanded,
      handleSearch,
      selectNode,
      confirmSelection,
      handleClose
    }
  }
}
</script>

<style scoped>
.search-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.search-dialog {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.search-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eaeaea;
}

.search-dialog-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
}

.close-btn {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.search-dialog-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 24px;
}

.search-input-section {
  margin-bottom: 24px;
}

.search-input-large {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  color: #2d3748;
  background: white;
  transition: all 0.2s;
  box-sizing: border-box;
}

.search-input-large:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-stats {
  margin-top: 8px;
  font-size: 14px;
  color: #718096;
}

.tags-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #eaeaea;
}

.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tags-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.toggle-tags-btn {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 13px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-tags-btn:hover {
  background: #edf2f7;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  transition: max-height 0.3s ease;
}

.tags-container.collapsed {
  max-height: 0;
  overflow: hidden;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
}

.tag-item:hover {
  border-color: #cbd5e0;
  background: #f7fafc;
}

.tag-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
}

.tag-item.active .tag-label,
.tag-item.active .tag-count {
  color: white;
}

.tag-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-label {
  font-weight: 500;
  color: #2c3e50;
}

.tag-count {
  font-size: 12px;
  color: #718096;
}

.results-section {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
}

.results-section::-webkit-scrollbar {
  width: 6px;
}

.results-section::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.results-section::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.results-section::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.no-results,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #718096;
  font-size: 14px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  padding: 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.result-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.result-item.selected {
  border-color: #667eea;
  border-width: 2px;
  background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.result-item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.result-type-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.result-name {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  flex: 1;
}

.result-name mark {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 700;
}

.result-item-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: #718096;
}

.result-id {
  font-family: 'Courier New', monospace;
  color: #a0aec0;
}

.result-description {
  color: #4a5568;
  line-height: 1.5;
}

.search-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eaeaea;
  background: #f8fafc;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: white;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.btn-cancel:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
</style>
