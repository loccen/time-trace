<template>
  <div class="sidebar">
    <div class="sidebar-logo">
      <router-link to="/" class="sidebar-logo-link">
        <img v-if="logo" :src="logo" class="sidebar-logo-img" alt="logo">
        <h1 v-if="showTitle" class="sidebar-title">{{ title }}</h1>
      </router-link>
    </div>
    
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="false"
        :collapse-transition="false"
        mode="vertical"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <SidebarItem
          v-for="route in routes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import SidebarItem from './SidebarItem.vue'

const route = useRoute()
const appStore = useAppStore()

// 计算属性
const sidebar = computed(() => appStore.sidebar)
const isCollapse = computed(() => !sidebar.value.opened)
const activeMenu = computed(() => route.path)

// 菜单路由配置
const routes = computed(() => [
  {
    path: '/dashboard',
    meta: { title: '仪表板', icon: 'DataBoard' },
    name: 'Dashboard'
  },
  {
    path: '/time-records',
    meta: { title: '工时记录', icon: 'Clock' },
    name: 'TimeRecords'
  },
  {
    path: '/statistics',
    meta: { title: '统计分析', icon: 'DataAnalysis' },
    name: 'Statistics'
  },
  {
    path: '/system-events',
    meta: { title: '系统事件', icon: 'Bell' },
    name: 'SystemEvents'
  },
  {
    path: '/settings',
    meta: { title: '系统设置', icon: 'Setting' },
    name: 'Settings'
  }
])

// Logo和标题
const logo = computed(() => appStore.settings.logo)
const title = computed(() => appStore.settings.title)
const showTitle = computed(() => appStore.settings.showSidebarLogo && !isCollapse.value)
</script>

<style lang="scss" scoped>
.sidebar {
  height: 100%;
  background-color: #304156;
}

.sidebar-logo {
  width: 100%;
  height: 50px;
  line-height: 50px;
  background: #2b2f3a;
  text-align: center;
  overflow: hidden;
  
  .sidebar-logo-link {
    height: 100%;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    
    .sidebar-logo-img {
      width: 32px;
      height: 32px;
      vertical-align: middle;
      margin-right: 12px;
    }
    
    .sidebar-title {
      display: inline-block;
      margin: 0;
      color: #fff;
      font-weight: 600;
      line-height: 50px;
      font-size: 14px;
      font-family: Avenir, Helvetica Neue, Arial, Helvetica, sans-serif;
      vertical-align: middle;
    }
  }
}

.scrollbar-wrapper {
  overflow-x: hidden !important;
}

:deep(.el-scrollbar__bar.is-vertical) {
  right: 0px;
}

:deep(.el-scrollbar) {
  height: calc(100% - 50px);
}

:deep(.el-menu) {
  border: none;
  height: 100%;
  width: 100% !important;
}

// 折叠状态下隐藏标题
.el-menu--collapse .sidebar-title {
  display: none;
}
</style>
