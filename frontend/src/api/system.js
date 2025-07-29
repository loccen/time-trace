import { http } from './request'

// 系统相关API
export const systemApi = {
  // 健康检查
  health() {
    return http.get('/health')
  },

  // 获取系统信息
  getSystemInfo() {
    return http.get('/system/info')
  },

  // 获取系统配置
  getSystemConfig() {
    return http.get('/system/config')
  }
}
