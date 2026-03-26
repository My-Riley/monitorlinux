<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch">
      <el-form-item label="学期">
        <el-select v-model="queryParams.semesterId" placeholder="请选择学期" clearable style="width: 200px" @change="handleSemesterChange">
          <el-option v-for="item in semesterList" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="周次">
        <el-select v-model="queryParams.weekNum" placeholder="全部周次" clearable style="width: 120px" @change="handleWeekChange">
          <el-option label="全部周次" :value="null" />
          <el-option v-for="item in weekList" :key="item.weekNum" :label="item.name" :value="item.weekNum" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 学期总览图表 -->
    <el-card class="chart-card" v-show="!queryParams.weekNum">
      <div slot="header">
        <span>{{ currentSemesterName }} - 各周学生情绪状态统计</span>
        <!-- <div style="float: right;">
          <span class="legend-item"><span class="legend-color" style="background: #52c41a;"></span>无焦虑</span>
          <span class="legend-item"><span class="legend-color" style="background: #1890ff;"></span>低度焦虑</span>
          <span class="legend-item"><span class="legend-color" style="background: #faad14;"></span>中度焦虑</span>
          <span class="legend-item"><span class="legend-color" style="background: #722ed1;"></span>高度焦虑</span>
        </div> -->
      </div>
      <div ref="semesterChart" class="chart-container"></div>
    </el-card>

    <!-- 周次详情图表 -->
    <el-card class="chart-card" v-show="queryParams.weekNum">
      <div slot="header">
        <span>{{ currentSemesterName }} - 第{{ queryParams.weekNum }}周情绪状态统计</span>
        <span v-if="weekDateRange" style="margin-left: 10px; color: #909399; font-size: 12px;">
          ({{ weekDateRange }})
        </span>
        <!-- <div style="float: right;">
          <span class="legend-item"><span class="legend-color" style="background: #52c41a;"></span>无焦虑</span>
          <span class="legend-item"><span class="legend-color" style="background: #1890ff;"></span>低度焦虑</span>
          <span class="legend-item"><span class="legend-color" style="background: #faad14;"></span>中度焦虑</span>
          <span class="legend-item"><span class="legend-color" style="background: #722ed1;"></span>高度焦虑</span>
        </div> -->
      </div>
      <div ref="weekChart" class="chart-container"></div>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import request from '@/utils/request'
import websocketMixin from "@/utils/mixins/websocketMixin";

export default {
  name: 'SemesterEmotion',
  mixins: [websocketMixin],
  data() {
    return {
      showSearch: true,
      queryParams: {
        semesterId: undefined,
        weekNum: null
      },
      semesterList: [],
      weekList: [],
      currentSemesterName: '',
      weekDateRange: '',
      semesterChart: null,
      weekChart: null,
      loading: false
    }
  },
  mounted() {
    this.loadSemesters()
  },
  beforeDestroy() {
    if (this.semesterChart) this.semesterChart.dispose()
    if (this.weekChart) this.weekChart.dispose()
  },
  methods: {
    async loadSemesters() {
      try {
        const res = await request({
          url: '/cell/semester/list',
          method: 'get'
        })
        if (res.code === 200 && res.data) {
          this.semesterList = res.data.semesters || []
          // 设置默认学期
          if (res.data.currentSemesterId) {
            this.queryParams.semesterId = res.data.currentSemesterId
          } else if (this.semesterList.length > 0) {
            this.queryParams.semesterId = this.semesterList[0].id
          }
          this.handleSemesterChange()
        }
      } catch (error) {
        console.error('获取学期列表失败:', error)
        this.initDefaultSemesters()
      }
    },
    initDefaultSemesters() {
      // 默认学期列表
      this.semesterList = [
        { id: '2025-2026-1', name: '2025-2026学年上学期' },
        { id: '2025-2026-2', name: '2025-2026学年下学期' },
        { id: '2026-2027-1', name: '2026-2027学年上学期' },
        { id: '2026-2027-2', name: '2026-2027学年下学期' }
      ]
      this.queryParams.semesterId = this.semesterList[0].id
      this.handleSemesterChange()
    },
    async handleSemesterChange() {
      if (!this.queryParams.semesterId) return

      // 更新当前学期名称
      const semester = this.semesterList.find(s => s.id === this.queryParams.semesterId)
      this.currentSemesterName = semester ? semester.name : ''

      // 加载周次列表
      try {
        const res = await request({
          url: '/system/results/semesterWeeks',
          method: 'get',
          params: { semesterId: this.queryParams.semesterId }
        })
        if (res.code === 200 && res.data && Array.isArray(res.data) && res.data.length > 0) {
          this.weekList = res.data
        } else {
          // 如果返回数据为空或格式不正确，使用默认20周
          this.weekList = Array.from({ length: 20 }, (_, i) => ({
            weekNum: i + 1,
            name: `第${i + 1}周`
          }))
        }
      } catch (error) {
        console.error('获取周次列表失败:', error)
        // 默认20周
        this.weekList = Array.from({ length: 20 }, (_, i) => ({
          weekNum: i + 1,
          name: `第${i + 1}周`
        }))
      }

      // 重置周次选择
      this.queryParams.weekNum = null
      this.loadSemesterData()
    },
    handleWeekChange() {
      if (this.queryParams.weekNum) {
        this.loadWeekData()
      } else {
        this.loadSemesterData()
      }
    },
    handleQuery() {
      if (this.queryParams.weekNum) {
        this.loadWeekData()
      } else {
        this.loadSemesterData()
      }
    },
    resetQuery() {
      this.queryParams.weekNum = null
      this.handleQuery()
    },
    async loadSemesterData() {
      this.loading = true
      try {
        const res = await request({
          url: '/system/results/allWeeksStats',
          method: 'get',
          params: {
            semesterId: this.queryParams.semesterId
          }
        })

        if (res.code === 200 && res.data) {
          this.$nextTick(() => {
            this.renderSemesterChart(res.data)
          })
        }
      } catch (error) {
        console.error('获取学期数据失败:', error)
        this.renderDefaultSemesterChart()
      } finally {
        this.loading = false
      }
    },
    async loadWeekData() {
      this.loading = true
      try {
        const res = await request({
          url: '/system/results/semesterWeekStats',
          method: 'get',
          params: {
            semesterId: this.queryParams.semesterId,
            weekNum: this.queryParams.weekNum
          }
        })

        if (res.code === 200 && res.data) {
          this.weekDateRange = res.data.startDate && res.data.endDate
            ? `${res.data.startDate} ~ ${res.data.endDate}`
            : ''
          this.$nextTick(() => {
            this.renderWeekChart(res.data)
          })
        }
      } catch (error) {
        console.error('获取周次数据失败:', error)
        this.renderDefaultWeekChart()
      } finally {
        this.loading = false
      }
    },
    renderSemesterChart(data) {
      if (!this.$refs.semesterChart) return
      if (!this.semesterChart) {
        this.semesterChart = echarts.init(this.$refs.semesterChart)
      }

      const weeks = data.weeks || [];
      const option = {
        // 👇 新增 legend
        legend: {
          right: 10,
          top: 10,
          data: ['无焦虑', '低度焦虑', '中度焦虑', '高度焦虑'],
          textStyle: { fontSize: 12, color: '#666' }
        },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: {
          type: 'category',
          data: weeks,
          axisLabel: { interval: 0, rotate: 45, fontSize: 10 }
        },
        yAxis: { type: 'value', name: '次数' },
        dataZoom: [{ type: 'slider', show: true, xAxisIndex: [0], start: 0, end: 100, bottom: 10 }],
        series: [
          { name: '无焦虑', type: 'bar', data: data.noAnxiety || [], itemStyle: { color: '#52c41a' }, barGap: '0%' },
          { name: '低度焦虑', type: 'bar', data: data.lowAnxiety || [], itemStyle: { color: '#1890ff' } },
          { name: '中度焦虑', type: 'bar', data: data.midAnxiety || [], itemStyle: { color: '#faad14' } },
          { name: '高度焦虑', type: 'bar', data: data.highAnxiety || [], itemStyle: { color: '#722ed1' } }
        ]
      };
      this.semesterChart.setOption(option, true);
    },
    renderWeekChart(data) {
      if (!this.$refs.weekChart) return
      if (!this.weekChart) {
        this.weekChart = echarts.init(this.$refs.weekChart)
      }

      const days = data.days || ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      const option = {
        legend: {
          right: 10,
          top: 10,
          data: ['无焦虑', '低度焦虑', '中度焦虑', '高度焦虑'],
          textStyle: { fontSize: 12, color: '#666' }
        },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
        xAxis: { type: 'category', data: days },
        yAxis: { type: 'value', name: '次数' },
        series: [
          { name: '无焦虑', type: 'bar', data: data.noAnxiety || [], itemStyle: { color: '#52c41a' }, barGap: '0%' },
          { name: '低度焦虑', type: 'bar', data: data.lowAnxiety || [], itemStyle: { color: '#1890ff' } },
          { name: '中度焦虑', type: 'bar', data: data.midAnxiety || [], itemStyle: { color: '#faad14' } },
          { name: '高度焦虑', type: 'bar', data: data.highAnxiety || [], itemStyle: { color: '#722ed1' } }
        ]
      }
      this.weekChart.setOption(option, true)
    },
    renderDefaultSemesterChart() {
      const weeks = Array.from({ length: 20 }, (_, i) => `第${i + 1}周`)
      const emptyData = new Array(20).fill(0)
      this.renderSemesterChart({ weeks, noAnxiety: emptyData, lowAnxiety: emptyData, midAnxiety: emptyData, highAnxiety: emptyData })
    },
    renderDefaultWeekChart() {
      const emptyData = new Array(7).fill(0)
      this.renderWeekChart({ days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'], noAnxiety: emptyData, lowAnxiety: emptyData, midAnxiety: emptyData, highAnxiety: emptyData })
    },
    // 处理WebSocket更新通知
    handleWebSocketUpdate() {
      this.handleQuery()
    }
  }
}
</script>

<style scoped>
.chart-card {
  margin-bottom: 20px;
  font-size: 16px;
  color: black;
  font-weight: bold;
  z-index: 10;
}
.chart-container { height: 500px; }
</style>
