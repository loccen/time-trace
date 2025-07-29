import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 侧边栏状态
    sidebar: {
      opened: true,
      withoutAnimation: false
    },
    // 设备类型
    device: 'desktop',
    // 主题设置
    theme: {
      mode: 'light', // light | dark
      primaryColor: '#409EFF',
      size: 'default' // large | default | small
    },
    // 系统设置
    settings: {
      title: '时迹工时追踪系统',
      logo: '',
      fixedHeader: true,
      showLogo: true,
      showTagsView: true,
      showSidebarLogo: true,
      errorLog: 'production'
    },
    // 加载状态
    loading: false,
    // 系统信息
    systemInfo: null
  }),

  getters: {
    // 侧边栏是否打开
    sidebarOpened: (state) => state.sidebar.opened,
    
    // 是否为移动设备
    isMobile: (state) => state.device === 'mobile',
    
    // 当前主题
    currentTheme: (state) => state.theme.mode,
    
    // 应用标题
    appTitle: (state) => state.settings.title
  },

  actions: {
    // 切换侧边栏
    toggleSidebar() {
      this.sidebar.opened = !this.sidebar.opened
      this.sidebar.withoutAnimation = false
    },

    // 关闭侧边栏
    closeSidebar(withoutAnimation = false) {
      this.sidebar.opened = false
      this.sidebar.withoutAnimation = withoutAnimation
    },

    // 设置设备类型
    setDevice(device) {
      this.device = device
    },

    // 切换主题
    toggleTheme() {
      this.theme.mode = this.theme.mode === 'light' ? 'dark' : 'light'
      this.applyTheme()
    },

    // 设置主题
    setTheme(mode) {
      this.theme.mode = mode
      this.applyTheme()
    },

    // 应用主题
    applyTheme() {
      const html = document.documentElement
      if (this.theme.mode === 'dark') {
        html.classList.add('dark')
      } else {
        html.classList.remove('dark')
      }
    },

    // 设置主色调
    setPrimaryColor(color) {
      this.theme.primaryColor = color
      // TODO: 动态设置CSS变量
    },

    // 设置组件尺寸
    setSize(size) {
      this.theme.size = size
    },

    // 设置加载状态
    setLoading(loading) {
      this.loading = loading
    },

    // 更新系统设置
    updateSettings(settings) {
      this.settings = { ...this.settings, ...settings }
    },

    // 设置系统信息
    setSystemInfo(info) {
      this.systemInfo = info
    },

    // 初始化应用
    async initApp() {
      try {
        this.setLoading(true)
        
        // 从localStorage恢复设置
        this.restoreSettings()
        
        // 应用主题
        this.applyTheme()
        
        // 获取系统信息
        await this.fetchSystemInfo()
        
      } catch (error) {
        console.error('应用初始化失败:', error)
      } finally {
        this.setLoading(false)
      }
    },

    // 恢复设置
    restoreSettings() {
      try {
        const savedSettings = localStorage.getItem('app-settings')
        if (savedSettings) {
          const settings = JSON.parse(savedSettings)
          this.theme = { ...this.theme, ...settings.theme }
          this.sidebar = { ...this.sidebar, ...settings.sidebar }
          this.settings = { ...this.settings, ...settings.settings }
        }
      } catch (error) {
        console.error('恢复设置失败:', error)
      }
    },

    // 保存设置
    saveSettings() {
      try {
        const settings = {
          theme: this.theme,
          sidebar: this.sidebar,
          settings: this.settings
        }
        localStorage.setItem('app-settings', JSON.stringify(settings))
      } catch (error) {
        console.error('保存设置失败:', error)
      }
    },

    // 获取系统信息
    async fetchSystemInfo() {
      try {
        // TODO: 调用API获取系统信息
        // const response = await api.getSystemInfo()
        // this.setSystemInfo(response.data)
      } catch (error) {
        console.error('获取系统信息失败:', error)
      }
    }
  }
})
