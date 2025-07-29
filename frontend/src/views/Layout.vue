<template>
  <div class="app-wrapper">
    <!-- 顶部导航栏 -->
    <AppHeader />

    <!-- 主内容区域 -->
    <main class="main">
      <router-view />
    </main>

    <!-- 底部状态栏 -->
    <AppFooter />
  </div>
</template>

<script setup>
import AppHeader from '@/components/AppHeader/index.vue'
import AppFooter from '@/components/AppFooter/index.vue'
</script>

<style lang="scss" scoped>
.app-wrapper {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background-color: #f5f7fa;
  color: #303133;
  line-height: 1.5;
  overflow-x: hidden;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.main {
  margin-top: 60px;
  margin-bottom: 40px;
  padding: 20px;
  min-height: calc(100vh - 100px);
  flex: 1;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}
</style>
