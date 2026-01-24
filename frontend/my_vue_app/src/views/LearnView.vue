<template>
  <div class="learn-page">
    <KnowledgeGraph />
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
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>