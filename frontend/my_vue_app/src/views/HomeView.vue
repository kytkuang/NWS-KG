<template>
  <div class="home-page">
    <header class="hero">
      <div class="hero-content">
        <h1>网络安全知识图谱学习平台</h1>
        <p>
          基于 ATT&CK / CAPEC 等威胁情报构建的知识图谱，可视化掌握攻击技术、APT 组织与防御策略。
        </p>
        <div class="hero-actions">
          <router-link class="btn primary" to="/login">立即登录</router-link>
          <router-link class="btn ghost" to="/register">注册新账号</router-link>
        </div>
      </div>
    </header>

    <main class="home-main">
      <section class="features">
        <div class="feature-card">
          <h3>知识图谱可视化</h3>
          <p>从攻击技术、恶意软件到攻击组织，直观探索网络威胁实体与关系。</p>
        </div>
        <div class="feature-card">
          <h3>学习进度跟踪</h3>
          <p>记录你的学习进度与登录情况，帮助你系统性掌握安全知识。</p>
        </div>
        <div class="feature-card">
          <h3>结构化数据支撑</h3>
          <p>基于 Neo4j 图数据库存储 CTI 数据，保证查询高效与关系清晰。</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: #ffffff;
  color: #333333;
}

.hero {
  padding: 80px 20px 40px;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.hero h1 {
  font-size: 34px;
  font-weight: 800;
  margin-bottom: 16px;
  color: #333333;
}

.hero p {
  font-size: 16px;
  color: #666666;
  max-width: 640px;
  margin: 0 auto 28px;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease, box-shadow 0.1s ease;
}

.btn.primary {
  background-color: #007bff;
  color: #ffffff;
}

.btn.primary:hover {
  background-color: #0056b3;
}

.btn.ghost {
  background-color: #f8f9fa;
  color: #333333;
  border: 1px solid #ddd;
}

.btn.ghost:hover {
  background-color: #e9ecef;
}

.home-main {
  padding: 20px 20px 40px;
}

.features {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.feature-card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 20px 18px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
  font-size: 18px;
  margin-bottom: 8px;
  color: #333333;
}

.feature-card p {
  font-size: 14px;
  color: #666666;
  line-height: 1.6;
}
</style>