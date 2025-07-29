import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    // 用户信息
    userInfo: {
      id: 'system',
      username: 'system',
      nickname: '系统用户',
      avatar: '',
      email: '',
      roles: ['admin']
    },
    // 认证token
    token: '',
    // 权限列表
    permissions: [],
    // 登录状态
    isLoggedIn: false
  }),

  getters: {
    // 用户名
    username: (state) => state.userInfo.username,
    
    // 用户昵称
    nickname: (state) => state.userInfo.nickname || state.userInfo.username,
    
    // 用户头像
    avatar: (state) => state.userInfo.avatar || '/default-avatar.png',
    
    // 是否为管理员
    isAdmin: (state) => state.userInfo.roles.includes('admin'),
    
    // 是否已登录
    loggedIn: (state) => state.isLoggedIn && !!state.token
  },

  actions: {
    // 设置用户信息
    setUserInfo(userInfo) {
      this.userInfo = { ...this.userInfo, ...userInfo }
    },

    // 设置token
    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('access_token', token)
      } else {
        localStorage.removeItem('access_token')
      }
    },

    // 设置权限
    setPermissions(permissions) {
      this.permissions = permissions
    },

    // 设置登录状态
    setLoginStatus(status) {
      this.isLoggedIn = status
    },

    // 登录
    async login(credentials) {
      try {
        // TODO: 实现真实的登录逻辑
        // const response = await api.login(credentials)
        // const { token, userInfo } = response.data
        
        // 模拟登录成功
        const token = 'mock-token-' + Date.now()
        const userInfo = {
          id: 'user001',
          username: credentials.username,
          nickname: credentials.username,
          avatar: '',
          email: credentials.username + '@example.com',
          roles: ['user']
        }

        this.setToken(token)
        this.setUserInfo(userInfo)
        this.setLoginStatus(true)

        return { success: true, message: '登录成功' }
      } catch (error) {
        console.error('登录失败:', error)
        return { success: false, message: '登录失败' }
      }
    },

    // 登出
    async logout() {
      try {
        // TODO: 调用登出API
        // await api.logout()
        
        this.setToken('')
        this.setUserInfo({
          id: '',
          username: '',
          nickname: '',
          avatar: '',
          email: '',
          roles: []
        })
        this.setPermissions([])
        this.setLoginStatus(false)

        return { success: true, message: '登出成功' }
      } catch (error) {
        console.error('登出失败:', error)
        return { success: false, message: '登出失败' }
      }
    },

    // 获取用户信息
    async fetchUserInfo() {
      try {
        if (!this.token) {
          throw new Error('未找到访问令牌')
        }

        // TODO: 调用API获取用户信息
        // const response = await api.getUserInfo()
        // this.setUserInfo(response.data)
        // this.setPermissions(response.data.permissions || [])

        return { success: true }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 清除无效token
        this.logout()
        return { success: false, message: '获取用户信息失败' }
      }
    },

    // 更新用户信息
    async updateUserInfo(userInfo) {
      try {
        // TODO: 调用API更新用户信息
        // const response = await api.updateUserInfo(userInfo)
        // this.setUserInfo(response.data)

        this.setUserInfo(userInfo)
        return { success: true, message: '更新成功' }
      } catch (error) {
        console.error('更新用户信息失败:', error)
        return { success: false, message: '更新失败' }
      }
    },

    // 修改密码
    async changePassword(passwordData) {
      try {
        // TODO: 调用API修改密码
        // await api.changePassword(passwordData)

        return { success: true, message: '密码修改成功' }
      } catch (error) {
        console.error('修改密码失败:', error)
        return { success: false, message: '修改密码失败' }
      }
    },

    // 检查权限
    hasPermission(permission) {
      return this.permissions.includes(permission) || this.isAdmin
    },

    // 检查角色
    hasRole(role) {
      return this.userInfo.roles.includes(role)
    },

    // 初始化用户状态
    async initUser() {
      try {
        // 从localStorage恢复token
        const token = localStorage.getItem('access_token')
        if (token) {
          this.setToken(token)
          this.setLoginStatus(true)
          
          // 获取用户信息
          const result = await this.fetchUserInfo()
          if (!result.success) {
            // 如果获取用户信息失败，清除登录状态
            this.logout()
          }
        }
      } catch (error) {
        console.error('初始化用户状态失败:', error)
        this.logout()
      }
    }
  }
})
