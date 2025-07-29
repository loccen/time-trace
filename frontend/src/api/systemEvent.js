import { http } from './request'

// 系统事件相关API
export const systemEventApi = {
  // 获取系统事件列表
  getSystemEvents(params = {}) {
    return http.get('/v1/system-events/', params)
  },

  // 根据ID获取系统事件
  getSystemEvent(id) {
    return http.get(`/v1/system-events/${id}`)
  },

  // 创建系统事件
  createSystemEvent(data) {
    return http.post('/v1/system-events/', data)
  },

  // 标记事件为已处理
  markEventProcessed(id) {
    return http.put(`/v1/system-events/${id}/process`)
  },

  // 批量标记事件为已处理
  markEventsProcessedBatch(eventIds) {
    return http.put('/v1/system-events/batch/process', eventIds)
  },

  // 获取未处理事件
  getUnprocessedEvents(limit = 50) {
    return http.get('/v1/system-events/unprocessed/list', { limit })
  },

  // 获取最近事件
  getRecentEvents(limit = 20) {
    return http.get('/v1/system-events/recent/list', { limit })
  },

  // 获取事件统计
  getEventStatistics(params = {}) {
    return http.get('/v1/system-events/statistics/summary', params)
  }
}
