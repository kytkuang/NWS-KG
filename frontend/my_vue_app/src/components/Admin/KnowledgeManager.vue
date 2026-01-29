<template>
  <div class="knowledge-manager">
    <div class="section-header">
      <h2>学习管理</h2>
    </div>

    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <ul class="nav-list">
        <li>
          <button 
            class="nav-item" 
            :class="{ active: activeNav === 'knowledge-graph' }"
            @click="switchNav('knowledge-graph')"
          >
            <span>知识图谱</span>
          </button>
        </li>
        <li>
          <button 
            class="nav-item" 
            :class="{ active: activeNav === 'add-content' }"
            @click="switchNav('add-content')"
          >
            <span>添加内容</span>
          </button>
        </li>
        <li>
          <button 
            class="nav-item" 
            :class="{ active: activeNav === 'learning-stats' }"
            @click="switchNav('learning-stats')"
          >
            <span>学习统计</span>
          </button>
        </li>
      </ul>
    </nav>

    <main class="content">
      <!-- 知识图谱页面 -->
      <section v-if="activeNav === 'knowledge-graph'" class="knowledge-graph-view">
        <AdminKnowledgeGraph />
      </section>

      <!-- 添加内容页面 -->
      <section v-else-if="activeNav === 'add-content'" class="add-content-view">
        <AddContentManager />
      </section>

      <!-- 学习统计页面 -->
      <section v-else-if="activeNav === 'learning-stats'" class="empty-view">
        <div class="empty-state">
          <h3>学习统计</h3>
          <p>该功能正在开发中，敬请期待</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import { ref } from 'vue'
import AdminKnowledgeGraph from '../Graph/AdminKnowledgeGraph.vue'
import AddContentManager from './AddContentManager.vue'

export default {
  name: 'KnowledgeManager',
  components: {
    AdminKnowledgeGraph,
    AddContentManager
  },
  setup() {
    const activeNav = ref('knowledge-graph')

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
.knowledge-manager {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section-header {
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

/* 顶部导航栏样式 */
.top-nav {
  margin-bottom: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 8px 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
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

/* 主内容区域 */
.content {
  flex: 1;
  overflow: hidden;
}

/* 知识图谱页面样式 */
.knowledge-graph-view {
  height: 100%;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

/* 空页面样式 */
.empty-view {
  height: 100%;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
}

/* 添加内容页面样式 */
.add-content-view {
  height: 100%;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.empty-state {
  text-align: center;
  color: #6b7280;
}

.empty-state h3 {
  font-size: 20px;
  margin-bottom: 8px;
  color: #374151;
}

.empty-state p {
  font-size: 14px;
}
</style>
