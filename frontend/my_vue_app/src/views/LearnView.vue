<template>
  <div class="learn-page">
    <header class="top-bar">
      <h1>知识学习</h1>
      <p>从知识图谱中探索攻击技术与战术关系。</p>
    </header>

    <main class="content">
      <KnowledgeGraph />
    </main>
  </div>
</template>

<script>
import KnowledgeGraph from '@/components/Graph/KnowledgeGraph.vue'

export default {
  name: 'LearnView',
  components: {
    KnowledgeGraph
  }
}
</script>

<style scoped>
.learn-page {
  min-height: 100vh;
  background-color: #ffffff;
  padding: 24px 16px;
}

.top-bar h1 {
  font-size: 24px;
  margin-bottom: 6px;
}

.top-bar p {
  font-size: 14px;
  color: #6b7280;
}

.content {
  margin-top: 18px;
}
</style>