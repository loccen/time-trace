import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '仪表板',
          icon: 'DataBoard'
        }
      },
      {
        path: '/time-records',
        name: 'TimeRecords',
        component: () => import('@/views/TimeRecords.vue'),
        meta: {
          title: '工时记录',
          icon: 'Clock'
        }
      },
      {
        path: '/statistics',
        name: 'Statistics',
        component: () => import('@/views/Statistics.vue'),
        meta: {
          title: '统计分析',
          icon: 'DataAnalysis'
        }
      },
      {
        path: '/system-events',
        name: 'SystemEvents',
        component: () => import('@/views/SystemEvents.vue'),
        meta: {
          title: '系统事件',
          icon: 'Bell'
        }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: {
          title: '系统设置',
          icon: 'Setting'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面不存在',
      hideInMenu: true
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 时迹工时追踪系统`
  }

  // TODO: 添加权限验证逻辑
  next()
})

export default router
