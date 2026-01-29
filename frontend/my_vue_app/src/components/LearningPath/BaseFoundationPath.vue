<template>
  <div class="learning-path-wrapper">
    <div class="content-container">
      <!-- 左侧路径图 -->
      <div class="path-container">
        <h2 class="section-title">网络安全基础学习路径图</h2>

        <!-- 学习路径图 -->
        <div class="path-diagram">
          <!-- 第一层：网络基础 -->
          <div class="path-layer">
            <div class="layer-label">起点阶段</div>
            <div class="node-container">
              <div 
                class="learning-node start-node"
                :class="{ 'selected': selectedNode === 'network-basics' }"
                @click="selectNode('network-basics')"
              >
                <div class="node-header">
                  <div class="node-tag start-tag">起点</div>
                  <div class="node-title">网络基础</div>
                </div>
                <div class="node-body">
                  <div class="node-desc">建立网络通信基础认知</div>
                  <div class="node-features">
                    <span class="feature">TCP/IP协议</span>
                    <span class="feature">HTTP/DNS</span>
                    <span class="feature">网络模型</span>
                  </div>
                </div>
                <div class="node-arrow">
                  <div class="arrow-down"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 连接线1 -->
          <div class="connection-line line-1">
            <div class="line"></div>
            <div class="line-label">前置依赖</div>
          </div>

          <!-- 第二层：操作系统 -->
          <div class="path-layer">
            <div class="layer-label">基础环境阶段</div>
            <div class="parallel-container">
              <!-- 并行学习提示 -->
              <div class="parallel-label">
                <div class="parallel-line"></div>
                <div class="parallel-text">建议并行学习</div>
                <div class="parallel-line"></div>
              </div>

              <!-- Linux节点 -->
              <div 
                class="learning-node parallel-node linux-node"
                :class="{ 'selected': selectedNode === 'linux-basics' }"
                @click="selectNode('linux-basics')"
              >
                <div class="node-header">
                  <div class="node-tag parallel-tag">基础</div>
                  <div class="node-title">Linux基础</div>
                </div>
                <div class="node-body">
                  <div class="node-desc">服务器与运维核心环境</div>
                  <div class="node-features">
                    <span class="feature">文件权限</span>
                    <span class="feature">Shell命令</span>
                    <span class="feature">服务配置</span>
                  </div>
                </div>
                <div class="node-arrow">
                  <div class="arrow-down-right"></div>
                </div>
              </div>

              <!-- Windows节点 -->
              <div 
                class="learning-node parallel-node windows-node"
                :class="{ 'selected': selectedNode === 'windows-basics' }"
                @click="selectNode('windows-basics')"
              >
                <div class="node-header">
                  <div class="node-tag parallel-tag">基础</div>
                  <div class="node-title">Windows基础</div>
                </div>
                <div class="node-body">
                  <div class="node-desc">企业环境与桌面安全</div>
                  <div class="node-features">
                    <span class="feature">用户权限</span>
                    <span class="feature">系统服务</span>
                    <span class="feature">日志审计</span>
                  </div>
                </div>
                <div class="node-arrow">
                  <div class="arrow-down-left"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 连接线2 -->
          <div class="connection-line line-2">
            <div class="line merge-line"></div>
            <div class="line-label">知识融合</div>
          </div>

          <!-- 第三层：安全概念 -->
          <div class="path-layer">
            <div class="layer-label">综合应用阶段</div>
            <div class="node-container">
              <div 
                class="learning-node end-node"
                :class="{ 'selected': selectedNode === 'security-concepts' }"
                @click="selectNode('security-concepts')"
              >
                <div class="node-header">
                  <div class="node-tag end-tag">综合</div>
                  <div class="node-title">安全基本概念</div>
                </div>
                <div class="node-body">
                  <div class="node-desc">构建完整安全认知框架</div>
                  <div class="node-features">
                    <span class="feature">CIA三要素</span>
                    <span class="feature">加密技术</span>
                    <span class="feature">攻击类型</span>
                  </div>
                </div>
                <div class="node-complete">完成基础阶段</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 图例说明 -->
        <div class="legend-container">
          <div class="legend-item">
            <div class="legend-color start-legend"></div>
            <div class="legend-text">起点模块</div>
          </div>
          <div class="legend-item">
            <div class="legend-color parallel-legend"></div>
            <div class="legend-text">并行学习模块</div>
          </div>
          <div class="legend-item">
            <div class="legend-color end-legend"></div>
            <div class="legend-text">综合应用模块</div>
          </div>
          <div class="legend-item">
            <div class="legend-line"></div>
            <div class="legend-text">依赖关系</div>
          </div>
        </div>
      </div>

      <!-- 右侧详情面板 -->
      <div class="detail-container" :class="{ 'visible': selectedNode !== null }">
        <div class="detail-header">
          <div class="detail-title">
            <h3>{{ selectedBlock?.title || '学习模块详情' }}</h3>
            <div class="detail-stage" v-if="selectedBlock">{{ selectedBlock.stage }}</div>
          </div>
          <button class="close-btn" @click="closeDetail">×</button>
        </div>

        <div class="detail-content" v-if="selectedBlock">
          <!-- 模块概览 -->
          <div class="detail-section">
            <h4 class="section-title-small">模块概述</h4>
            <p class="section-text">{{ selectedBlock.description }}</p>
            
            <div class="meta-grid">
              <div class="meta-item">
                <div class="meta-label">学习难度</div>
                <div class="meta-value">{{ getDifficulty(selectedBlock.id) }}</div>
              </div>
              <div class="meta-item">
                <div class="meta-label">建议时间</div>
                <div class="meta-value">{{ getStudyTime(selectedBlock.id) }}</div>
              </div>
              <div class="meta-item">
                <div class="meta-label">依赖模块</div>
                <div class="meta-value">{{ selectedBlock.prerequisites.length || '无' }}</div>
              </div>
            </div>
          </div>

          <!-- 核心知识点 -->
          <div class="detail-section">
            <h4 class="section-title-small">核心知识点</h4>
            <div class="knowledge-list">
              <div 
                v-for="(topic, index) in selectedBlock.topics" 
                :key="index"
                class="knowledge-item"
              >
                <div class="knowledge-number">{{ index + 1 }}</div>
                <div class="knowledge-text">{{ topic }}</div>
              </div>
            </div>
          </div>

          <!-- 学习路径 -->
          <div class="detail-section">
            <h4 class="section-title-small">学习路径</h4>
            <div class="learning-steps">
              <!-- 前置依赖 -->
              <div class="step" v-if="selectedBlock.prerequisites.length > 0">
                <div class="step-header">
                  <div class="step-number">1</div>
                  <div class="step-title">先决条件</div>
                </div>
                <div class="step-content">
                  <div class="prereq-list">
                    <div 
                      v-for="(pre, idx) in selectedBlock.prerequisites" 
                      :key="idx"
                      class="prereq-item"
                      @click="selectPrerequisite(pre)"
                    >
                      {{ pre }}
                    </div>
                  </div>
                  <div class="step-note">需要先掌握这些前置知识</div>
                </div>
              </div>

              <!-- 学习顺序 -->
              <div class="step">
                <div class="step-header">
                  <div class="step-number">{{ selectedBlock.prerequisites.length > 0 ? '2' : '1' }}</div>
                  <div class="step-title">学习顺序</div>
                </div>
                <div class="step-content">
                  <div class="order-text">{{ selectedBlock.orderHint }}</div>
                </div>
              </div>

              <!-- 后续应用 -->
              <div class="step">
                <div class="step-header">
                  <div class="step-number">{{ selectedBlock.prerequisites.length > 0 ? '3' : '2' }}</div>
                  <div class="step-title">后续应用</div>
                </div>
                <div class="step-content">
                  <div class="application-list">
                    <div 
                      v-for="(app, idx) in getApplications(selectedBlock.id)" 
                      :key="idx"
                      class="application-item"
                    >
                      {{ app }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 学习建议 -->
          <div class="detail-section">
            <h4 class="section-title-small">学习建议</h4>
            <ul class="suggestion-list">
              <li v-for="(suggestion, idx) in getSuggestions(selectedBlock.id)" :key="idx">
                {{ suggestion }}
              </li>
            </ul>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button class="btn-primary" @click="startLearning">开始学习</button>
            <button class="btn-secondary" @click="viewMaterials">查看资料</button>
          </div>
        </div>

        <!-- 空状态 -->
        <div class="empty-state" v-else>
          <div class="empty-icon">📚</div>
          <h4>选择学习模块</h4>
          <p>点击左侧路径图中的任意模块，查看详细内容和学习建议</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LearningPathDiagram',
  data() {
    return {
      blocks: [
        {
          id: 'network-basics',
          title: '网络基础',
          stage: '起步阶段',
          description: '从零构建对计算机网络的整体认知，理解数据如何在不同主机与网络之间传输，是后续所有安全学习的必备基础。',
          topics: [
            '计算机网络分层模型（OSI 七层模型、TCP/IP 四层模型）',
            'TCP / UDP 协议及端口、连接状态（SYN/ACK、三次握手与四次挥手）',
            'IP 地址、子网掩码与子网划分，路由与转发基本概念',
            '常见应用层协议：HTTP/HTTPS、DNS、SMTP、FTP 等',
            'DNS 解析过程与缓存、HTTP 请求/响应报文结构'
          ],
          prerequisites: [],
          orderHint: '建议从网络模型 → TCP/IP 协议 → IP/路由 → 常见应用层协议的顺序逐步学习。'
        },
        {
          id: 'linux-basics',
          title: 'Linux 操作系统基础',
          stage: '基础环境',
          description: '掌握 Linux 的基本使用方法和系统管理能力，是进行渗透测试、服务器加固和安全运维的核心技能之一。',
          topics: [
            'Linux 文件系统层次结构（/etc、/var、/home、/var/log 等）',
            '用户与用户组、文件权限与所有者（rwx、chmod、chown）',
            '常用命令：文件/目录操作、进程管理、网络调试（ls、ps、netstat、ss、tcpdump 等）',
            'Shell 基础与简单脚本编写（变量、条件判断、循环）',
            '常见服务的安装与基础配置（SSH、Web 服务等）'
          ],
          prerequisites: ['网络基础'],
          orderHint: '在掌握网络基础后，通过命令行练习文件管理 → 权限控制 → 服务部署，逐步熟悉 Linux 环境。'
        },
        {
          id: 'windows-basics',
          title: 'Windows 基础',
          stage: '基础环境',
          description: '了解 Windows 的账户体系、服务机制和管理工具，为后续的域渗透、安全审计和蓝队防护打下基础。',
          topics: [
            '本地用户与用户组管理、权限模型（ACL）',
            'Windows 注册表结构与常见关键位置',
            '系统服务与启动项管理，任务计划程序的基本使用',
            '事件查看器与日志基础，安全相关日志的定位',
            'Active Directory / 域的基础概念与典型结构（只需理解，不必深入实现细节）'
          ],
          prerequisites: ['网络基础'],
          orderHint: '在理解网络基础后，先熟悉本地账号与权限，再了解服务、日志和 AD 基本架构。'
        },
        {
          id: 'security-concepts',
          title: '安全基本概念',
          stage: '安全入门',
          description: '在具备网络与操作系统认知后，从宏观层面理解信息安全的目标、威胁类型以及常见防护思路，是进入各类安全分支前的必修课。',
          topics: [
            'CIA 三要素：机密性（Confidentiality）、完整性（Integrity）、可用性（Availability）',
            '安全策略、最小权限原则、纵深防御等安全设计原则',
            '对称加密与非对称加密的基本原理与典型算法（AES、RSA 等）',
            '哈希算法与完整性校验（MD5、SHA 系列），消息认证码（MAC）的基本思想',
            '常见攻击类型概览：SQL 注入、XSS、CSRF、暴力破解、社工、拒绝服务等'
          ],
          prerequisites: ['网络基础', 'Linux 操作系统基础', 'Windows 基础'],
          orderHint: '在掌握网络与操作系统基础后，再系统性学习安全三要素、加密与攻击类型，从"为什么要防""防什么"两个角度建立安全思维。'
        }
      ],
      selectedNode: 'network-basics'
    }
  },
  computed: {
    selectedBlock() {
      return this.blocks.find(block => block.id === this.selectedNode)
    }
  },
  methods: {
    selectNode(nodeId) {
      this.selectedNode = nodeId
    },
    
    closeDetail() {
      this.selectedNode = null
    },
    
    getDifficulty(nodeId) {
      const difficulties = {
        'network-basics': '初级',
        'linux-basics': '初级',
        'windows-basics': '初级',
        'security-concepts': '中级'
      }
      return difficulties[nodeId] || '初级'
    },
    
    getStudyTime(nodeId) {
      const times = {
        'network-basics': '2-3周',
        'linux-basics': '2-3周',
        'windows-basics': '1-2周',
        'security-concepts': '2-3周'
      }
      return times[nodeId] || '1-2周'
    },
    
    getApplications(nodeId) {
      const applications = {
        'network-basics': ['网络协议分析', '流量监控', '网络拓扑设计'],
        'linux-basics': ['服务器管理', '脚本自动化', '服务部署'],
        'windows-basics': ['系统审计', '日志分析', '权限管理'],
        'security-concepts': ['风险评估', '安全策略制定', '渗透测试基础']
      }
      return applications[nodeId] || []
    },
    
    getSuggestions(nodeId) {
      const suggestions = {
        'network-basics': [
          '使用 Wireshark 抓包分析实际网络流量',
          '搭建小型局域网实验环境',
          '逐个学习 TCP/IP 协议族中的核心协议'
        ],
        'linux-basics': [
          '在虚拟机中安装 Linux 系统进行实操',
          '每天练习常用命令，形成肌肉记忆',
          '尝试编写简单的 Shell 脚本解决实际问题'
        ],
        'windows-basics': [
          '在自己的 Windows 电脑上实践管理操作',
          '关注 Windows 事件查看器中的安全日志',
          '了解域环境的基本概念和架构'
        ],
        'security-concepts': [
          '结合已学网络和系统知识理解安全概念',
          '查阅 OWASP Top 10 了解常见 Web 漏洞',
          '思考如何将 CIA 三要素应用到实际场景'
        ]
      }
      return suggestions[nodeId] || []
    },
    
    selectPrerequisite(preName) {
      const preNode = this.blocks.find(block => block.title === preName)
      if (preNode) {
        this.selectNode(preNode.id)
      }
    },
    
    startLearning() {
      alert(`开始学习：${this.selectedBlock.title}`)
    },
    
    viewMaterials() {
      // 跳转到资料页面，并传递组件名称作为查询参数
      this.$router.push({
        name: 'Materials',
        query: {
          component: this.selectedNode
        }
      })
    }
  }
}
</script>

<style scoped>
.learning-path-wrapper {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 20px;
  box-sizing: border-box;
}

.content-container {
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  gap: 20px;
  height: calc(100vh - 40px);
}

/* 左侧路径图容器 */
.path-container {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow-y: auto;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 700;
  color: #1a202c;
  text-align: center;
}

.section-intro {
  margin: 0 0 32px 0;
  font-size: 14px;
  color: #4a5568;
  line-height: 1.6;
  text-align: center;
}

.section-intro b {
  color: #2c5282;
  font-weight: 600;
}

/* 路径图 */
.path-diagram {
  position: relative;
  padding: 20px 0;
}

.path-layer {
  margin-bottom: 40px;
  position: relative;
}

.layer-label {
  font-size: 12px;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
  text-align: center;
}

/* 节点样式 */
.node-container {
  display: flex;
  justify-content: center;
}

.parallel-container {
  display: flex;
  justify-content: space-around;
  align-items: flex-start;
  position: relative;
  min-height: 200px;
}

.learning-node {
  background: white;
  border-radius: 10px;
  padding: 16px;
  width: 220px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.learning-node:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.learning-node.selected {
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.start-node {
  border-top: 4px solid #48bb78;
}

.parallel-node {
  border-top: 4px solid #ed8936;
}

.linux-node {
  margin-right: 10px;
}

.windows-node {
  margin-left: 10px;
}

.end-node {
  border-top: 4px solid #805ad5;
}

.node-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.node-tag {
  font-size: 11px;
  font-weight: 700;
  color: white;
  padding: 2px 8px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.start-tag {
  background: #48bb78;
}

.parallel-tag {
  background: #ed8936;
}

.end-tag {
  background: #805ad5;
}

.node-title {
  font-size: 16px;
  font-weight: 700;
  color: #2d3748;
  flex: 1;
}

.node-body {
  margin-bottom: 12px;
}

.node-desc {
  font-size: 12px;
  color: #718096;
  margin-bottom: 10px;
  line-height: 1.4;
}

.node-features {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.feature {
  font-size: 11px;
  padding: 2px 6px;
  background: #e2e8f0;
  color: #4a5568;
  border-radius: 4px;
  font-weight: 500;
}

.node-arrow {
  display: flex;
  justify-content: center;
  padding-top: 8px;
  border-top: 1px dashed #e2e8f0;
}

.arrow-down {
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 10px solid #a0aec0;
}

.arrow-down-right {
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 10px solid #a0aec0;
  transform: rotate(45deg);
}

.arrow-down-left {
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 10px solid #a0aec0;
  transform: rotate(-45deg);
}

.node-complete {
  font-size: 11px;
  font-weight: 600;
  color: #805ad5;
  text-align: center;
  padding-top: 8px;
  border-top: 1px dashed #e2e8f0;
}

/* 连接线 */
.connection-line {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 40px;
  position: relative;
}

.line {
  height: 2px;
  width: 80%;
  background: linear-gradient(90deg, #cbd5e0, #a0aec0);
  position: relative;
}

.line::before,
.line::after {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  background: #a0aec0;
  border-radius: 50%;
  top: -3px;
}

.line::before {
  left: 0;
}

.line::after {
  right: 0;
}

.merge-line {
  background: linear-gradient(90deg, 
    transparent 0%, 
    transparent 15%, 
    #a0aec0 15%, 
    #a0aec0 85%, 
    transparent 85%, 
    transparent 100%
  );
}

.line-label {
  position: absolute;
  font-size: 11px;
  color: #718096;
  background: white;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

/* 并行标签 */
.parallel-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
}

.parallel-line {
  width: 60px;
  height: 1px;
  background: #ed8936;
}

.parallel-text {
  font-size: 11px;
  color: #ed8936;
  font-weight: 600;
  white-space: nowrap;
}

/* 图例 */
.legend-container {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 32px;
  padding: 16px;
  background: #f7fafc;
  border-radius: 8px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.start-legend {
  background: #48bb78;
}

.parallel-legend {
  background: #ed8936;
}

.end-legend {
  background: #805ad5;
}

.legend-line {
  width: 20px;
  height: 2px;
  background: #a0aec0;
}

.legend-text {
  font-size: 12px;
  color: #4a5568;
}

/* 右侧详情面板 */
.detail-container {
  width: 380px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  opacity: 0;
  transform: translateX(20px);
  transition: all 0.3s ease;
  overflow: hidden;
}

.detail-container.visible {
  opacity: 1;
  transform: translateX(0);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.detail-title {
  flex: 1;
}

.detail-title h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 700;
  color: #2d3748;
}

.detail-stage {
  font-size: 11px;
  font-weight: 600;
  color: white;
  padding: 2px 8px;
  background: #805ad5;
  border-radius: 999px;
  display: inline-block;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #718096;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #edf2f7;
  color: #4a5568;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  text-align: center;
  flex: 1;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-state h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: #718096;
  line-height: 1.5;
}

/* 详情内容样式 */
.detail-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.detail-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title-small {
  font-size: 14px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 12px 0;
}

.section-text {
  font-size: 13px;
  color: #4a5568;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.meta-item {
  background: #f7fafc;
  border-radius: 6px;
  padding: 8px;
  text-align: center;
}

.meta-label {
  font-size: 11px;
  color: #718096;
  margin-bottom: 4px;
}

.meta-value {
  font-size: 13px;
  color: #2d3748;
  font-weight: 600;
}

/* 知识点列表 */
.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.knowledge-item {
  display: flex;
  gap: 12px;
  padding: 10px;
  background: #f7fafc;
  border-radius: 6px;
  border-left: 3px solid #4299e1;
}

.knowledge-number {
  font-size: 12px;
  font-weight: 700;
  color: #4299e1;
  min-width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
}

.knowledge-text {
  font-size: 13px;
  color: #4a5568;
  line-height: 1.4;
  flex: 1;
}

/* 学习步骤 */
.learning-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step {
  background: #f7fafc;
  border-radius: 8px;
  padding: 12px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.step-number {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #805ad5;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
}

.step-title {
  font-size: 13px;
  font-weight: 600;
  color: #2d3748;
}

.prereq-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.prereq-item {
  font-size: 12px;
  padding: 4px 8px;
  background: #e9d8fd;
  color: #553c9a;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.prereq-item:hover {
  background: #d6bcfa;
}

.step-note {
  font-size: 11px;
  color: #718096;
  font-style: italic;
}

.order-text {
  font-size: 13px;
  color: #4a5568;
  line-height: 1.5;
}

.application-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.application-item {
  font-size: 12px;
  padding: 4px 8px;
  background: #bee3f8;
  color: #2c5282;
  border-radius: 4px;
}

/* 学习建议 */
.suggestion-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-list li {
  font-size: 13px;
  color: #4a5568;
  padding: 6px 0;
  padding-left: 16px;
  position: relative;
  line-height: 1.4;
}

.suggestion-list li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: #48bb78;
  font-weight: bold;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary, .btn-secondary {
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.btn-primary {
  background: #805ad5;
  color: white;
}

.btn-primary:hover {
  background: #6b46c1;
}

.btn-secondary {
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #edf2f7;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .content-container {
    flex-direction: column;
    height: auto;
  }
  
  .detail-container {
    width: 100%;
    margin-top: 20px;
  }
  
  .parallel-container {
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }
  
  .linux-node, .windows-node {
    margin: 0;
  }
  
  .parallel-label {
    top: -10px;
  }
}

@media (max-width: 768px) {
  .content-container {
    gap: 16px;
  }
  
  .path-container, .detail-container {
    padding: 16px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .learning-node {
    width: 100%;
    max-width: 280px;
  }
  
  .legend-container {
    gap: 16px;
  }
  
  .meta-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>