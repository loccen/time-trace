import { http } from './request'

// 统计分析相关API
export const statisticsApi = {
  // 获取日统计
  getDailyStatistics(date) {
    return http.get(`/v1/statistics/daily/${date}`)
  },

  // 获取周统计
  getWeeklyStatistics(date) {
    return http.get(`/v1/statistics/weekly/${date}`)
  },

  // 获取月统计
  getMonthlyStatistics(year, month) {
    return http.get(`/v1/statistics/monthly/${year}/${month}`)
  },

  // 获取范围统计摘要
  getRangeSummary(params) {
    return http.get('/v1/statistics/range/summary', params)
  },

  // 获取周趋势数据
  getWeeklyTrends(weeks = 12) {
    return http.get('/v1/statistics/trends/weekly', { weeks })
  },

  // 获取仪表板概览
  getDashboardOverview() {
    return http.get('/v1/statistics/overview/dashboard')
  }
}
