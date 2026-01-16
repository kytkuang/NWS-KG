<template>
  <div class="admin-page">
    <header class="top-bar">
      <div>
        <h1>知识管理</h1>
        <p>维护网络安全知识点及其关系，支撑学习路线与测验设计。</p>
      </div>
    </header>

    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <ul class="nav-list">
        <li>
          <button 
            class="nav-item" 
            :class="{ active: activeNav === 'knowledge-graph' }"
            @click="switchNav('knowledge-graph')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l5.553 2.776A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
            </svg>
            <span>知识图谱</span>
          </button>
        </li>
        <li>
          <button 
            class="nav-item" 
            :class="{ active: activeNav === 'add-content' }"
            @click="switchNav('add-content')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            <span>添加内容</span>
          </button>
        </li>
        <li>
          <button 
            class="nav-item" 
            :class="{ active: activeNav === 'learning-stats' }"
            @click="switchNav('learning-stats')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            <span>学习统计</span>
          </button>
        </li>
      </ul>
    </nav>

    <main class="content">
      <!-- 知识图谱页面 -->
      <section v-if="activeNav === 'knowledge-graph'" class="knowledge-graph-view">
        <!-- 调用AdminKnowledgeGraph组件 -->
        <AdminKnowledgeGraph />
      </section>

      <!-- 添加内容页面 -->
      <section v-else-if="activeNav === 'add-content'" class="empty-view">
        <div class="empty-state">
          <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"/>
          </svg>
          <h2>添加内容</h2>
          <p>该功能正在开发中，敬请期待</p>
        </div>
      </section>

      <!-- 学习统计页面 -->
      <section v-else-if="activeNav === 'learning-stats'" class="empty-view">
        <div class="empty-state">
          <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          <h2>学习统计</h2>
          <p>该功能正在开发中，敬请期待</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import { ref } from 'vue'
// 导入AdminKnowledgeGraph组件
import AdminKnowledgeGraph from '../components/Graph/AdminKnowledgeGraph.vue'

export default {
  name: 'AdminKnowledgeView',
  components: {
    AdminKnowledgeGraph
  },
  setup() {
    const activeNav = ref('knowledge-graph') // 默认显示知识图谱页面

    // 切换导航
    const switchNav = (nav) => {
      activeNav.value = nav
    }

    return {
      activeNav,
      switchNav
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

/* 顶部导航栏样式 */
.top-nav {
  margin-top: 20px;
  margin-bottom: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 8px 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: none;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: #f9fafb;
  color: #374151;
}

.nav-item.active {
  background-color: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* 主内容区域 */
.content {
  margin-top: 0;
}

/* 知识图谱页面样式 */
.knowledge-graph-view {
  height: calc(100vh - 180px);
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  overflow: hidden;
}

/* 空页面样式 */
.empty-view {
  height: calc(100vh - 180px);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.empty-state {
  text-align: center;
  color: #6b7280;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  color: #d1d5db;
}

.empty-state h2 {
  font-size: 20px;
  margin-bottom: 8px;
  color: #374151;
}

.empty-state p {
  font-size: 14px;
}
</style>