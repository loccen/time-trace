import { http } from './request'

// 工时记录相关API
export const timeRecordApi = {
  // 获取工时记录列表
  getTimeRecords(params = {}) {
    return http.get('/v1/time-records/', params)
  },

  // 根据ID获取工时记录
  getTimeRecord(id) {
    return http.get(`/v1/time-records/${id}`)
  },

  // 根据日期获取工时记录
  getTimeRecordByDate(date) {
    return http.get(`/v1/time-records/date/${date}`)
  },

  // 创建工时记录
  createTimeRecord(data) {
    return http.post('/v1/time-records/', data)
  },

  // 更新工时记录
  updateTimeRecord(id, data) {
    return http.put(`/v1/time-records/${id}`, data)
  },

  // 删除工时记录
  deleteTimeRecord(id) {
    return http.delete(`/v1/time-records/${id}`)
  },

  // 获取日期范围统计摘要
  getRangeSummary(params) {
    return http.get('/v1/time-records/range/summary', params)
  }
}
