import { http } from './request'

// 系统配置相关API
export const configApi = {
  // 获取所有配置
  getAllConfig() {
    return http.get('/v1/config/')
  },

  // 按分类获取配置
  getConfigByCategory(category) {
    return http.get(`/v1/config/category/${category}`)
  },

  // 获取单个配置
  getConfigItem(key) {
    return http.get(`/v1/config/key/${key}`)
  },

  // 更新单个配置
  updateConfigItem(key, value) {
    return http.put(`/v1/config/key/${key}`, { value })
  },

  // 批量更新配置
  updateConfigBatch(configUpdates) {
    return http.put('/v1/config/batch', configUpdates)
  },

  // 重新加载配置
  reloadConfig() {
    return http.post('/v1/config/reload')
  },

  // 获取工作配置
  getWorkSettings() {
    return http.get('/v1/config/work/settings')
  },

  // 更新工作配置
  updateWorkSettings(workConfig) {
    return http.put('/v1/config/work/settings', workConfig)
  },

  // 获取事件配置
  getEventSettings() {
    return http.get('/v1/config/event/settings')
  },

  // 更新事件配置
  updateEventSettings(eventConfig) {
    return http.put('/v1/config/event/settings', eventConfig)
  }
}
