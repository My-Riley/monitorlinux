<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch">
      <el-form-item label="班级" prop="className">
        <el-select
          v-model="queryParams.className"
          filterable
          allow-create
          default-first-option
          placeholder="请选择或输入班级"
          clearable
          style="width: 100%"
          @change="loadChartData"
        >
          <el-option
            v-for="cls in classList"
            :key="cls.classId"
            :label="cls.className"
            :value="cls.classId"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="学期" prop="semesterId">
        <el-select v-model="queryParams.semesterId" placeholder="请选择学期" clearable @change="loadChartData">
          <el-option v-for="item in semesterList" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="周次" prop="weekNum">
        <el-select v-model="queryParams.weekNum" placeholder="请选择周次" clearable @change="loadChartData">
          <el-option label="全部周次" value="全部周次" />
          <el-option v-for="(week, index) in weeks" :key="index" :label="week" :value="week" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">班级学生焦虑类型总人次数分布</div>
          <div ref="pieChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">班级学生各科目焦虑人次数分布</div>
          <div ref="barChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="24">
        <el-card class="chart-card">
          <div slot="header">班级每周情绪状态统计</div>
          <div ref="weekChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import request from '@/utils/request'
import { getClassList } from "@/api/system/student"
import websocketMixin from "@/utils/mixins/websocketMixin";

export default {
  name: 'ClassEmotion',
  mixins: [websocketMixin],
  data() {
    return {
      showSearch: true,
      classList: [],
      queryParams: {
        className: undefined,
        weekNum: '全部周次',
        semesterId: undefined
      },
      semesterList: [],
      pieChart: null,
      barChart: null,
      weekChart: null,
      emotionData: []
    }
  },
  computed: {
    weeks() {
      return Array.from({ length: 20 }, (_, i) => `第 ${i + 1} 周`);
    }
  },
  async created() {
    this.emotionData = []
    // 先加载基础下拉数据
    await Promise.all([
      this.loadSemesterList(),
      this.loadClassList()
    ])
    // 等待 DOM 挂载完成后再加载图表数据（确保 mounted 已执行）
    this.$nextTick(() => {
      this.loadChartData()
    })
  },
  mounted() {
    // 必须在 mounted 中初始化 ECharts 实例（此时 $refs 才有效）
    this.pieChart = echarts.init(this.$refs.pieChart)
    this.barChart = echarts.init(this.$refs.barChart)
    this.weekChart = echarts.init(this.$refs.weekChart)
  },
  beforeDestroy() {
    if (this.pieChart) this.pieChart.dispose()
    if (this.barChart) this.barChart.dispose()
    if (this.weekChart) this.weekChart.dispose()
  },
  methods: {
    handleQuery() {
      this.loadChartData()
    },
    resetQuery() {
      this.resetForm('queryForm')
      this.handleQuery()
    },
    async loadClassList() {
      const res = await getClassList()
      if (res.code === 200) {
        const list = Array.isArray(res.data) ? res.data : []
        this.classList = list
          .filter(i => i && i.classId != null && i.className != null)
          .slice()
          .sort((a, b) => String(a.className).localeCompare(String(b.className), 'zh-Hans-CN'))
      }
    },
    async loadSemesterList() {
      try {
        const res = await request({
          url: '/cell/semester/list',
          method: 'get'
        })
        if (res.code === 200 && res.data) {
          this.semesterList = res.data.semesters || []
          if (!this.queryParams.semesterId) {
            this.queryParams.semesterId = res.data.currentSemesterId
          }
        }
      } catch (e) {
        console.error('获取学期列表失败', e)
      }
    },
    async loadChartData() {
      try {
        // 饼图：焦虑类型分布
        const stures = await request({
          url: '/system/results/classAnxietyTypeStats',
          method: 'get',
          params: {
            className: this.queryParams.className,
            weekNum:
              this.queryParams.weekNum === '全部周次'
                ? null
                : parseInt(this.queryParams.weekNum.replace('第 ', '').replace(' 周', '')),
            semesterId: this.queryParams.semesterId
          }
        })

        if (stures.code === 200) {
          const anxietyData = stures.data.map(item => {
            const colorMap = {
              0: '#52c41a', // 无焦虑
              1: '#1890ff', // 低度
              2: '#faad14', // 中度
              3: '#f5222d' // 高度
            }
            return {
              name: item.name,
              value: item.count,
              itemStyle: {
                color: colorMap[item.level] || '#bfbfbf'
              }
            };
          });

          this.currentAnxietyData = anxietyData;

          const pieOption = {
            tooltip: {
              trigger: 'item',
              formatter: (params) => {
                const chart = this.pieChart;
                if (!chart || !this.currentAnxietyData) return '';
                const selected = (chart.getOption().legend[0]?.selected) || {};
                let total = 0;
                this.currentAnxietyData.forEach(d => {
                  if (selected[d.name] !== false) total += d.value;
                });
                const p = total > 0 ? (params.value / total * 100).toFixed(1) : 0;
                return `${params.name}: ${params.value}人次 (${p}%)`;
              }
            },
            legend: {
              bottom: 10,
              left: 'center'
            },
            series: [{
              type: 'pie',
              radius: ['20%', '80%'],
              center: ['50%', '45%'],
              roseType: 'area',
              avoidLabelOverlap: true,
              itemStyle: {
                borderRadius: 5,
                borderColor: '#fff',
                borderWidth: 2
              },
              label: {
                show: true,
                position: 'outside',
                formatter: (params) => {
                  const chart = this.pieChart;
                  if (!chart || !this.currentAnxietyData) return '';
                  const selected = (chart.getOption().legend[0]?.selected) || {};
                  let total = 0;
                  this.currentAnxietyData.forEach(d => {
                    if (selected[d.name] !== false) total += d.value;
                  });
                  const p = total > 0 ? (params.value / total * 100).toFixed(1) : 0;
                  return `${params.name}\n${params.value}人次 (${p}%)`;
                }
              },
              labelLine: {
                show: true,
                length: 20,
                length2: 30
              },
              data: anxietyData
            }]
          }
          this.pieChart.setOption(pieOption, true) // 使用 true 覆盖而非合并
        }

        // 柱状图：各科目焦虑人数
        const res = await request({
          url: '/system/results/classSubjectAnxietyStats',
          method: 'get',
          params: {
            className: this.queryParams.className,
            weekNum:
              this.queryParams.weekNum === '全部周次'
                ? null
                : parseInt(this.queryParams.weekNum.replace('第 ', '').replace(' 周', '')),
            semesterId: this.queryParams.semesterId
          }
        })

        if (res.code === 200) {
          const data = res.data
          const barOption = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            legend: { data: ['无焦虑', '低焦虑', '中焦虑', '高焦虑'], bottom: 0 },
            grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
            xAxis: { type: 'category', data: data.subjects },
            yAxis: { type: 'value', name: '人次' },
            series: [
              { name: '无焦虑', type: 'bar', data: data.no_anxiety, itemStyle: { color: '#52c41a' } },
              { name: '低焦虑', type: 'bar', data: data.low_anxiety, itemStyle: { color: '#1890ff' } },
              { name: '中焦虑', type: 'bar', data: data.mid_anxiety, itemStyle: { color: '#faad14' } },
              { name: '高焦虑', type: 'bar', data: data.high_anxiety, itemStyle: { color: '#f5222d' } }
            ]
          }
          this.barChart.setOption(barOption, true)
        }

        // 折线/柱状图：每周情绪状态
        const weekRes = await request({
          url: '/system/results/allWeeksStats',
          method: 'get',
          params: {
            className: this.queryParams.className,
            weekNum: this.queryParams.weekNum === '全部周次' ? null : parseInt(this.queryParams.weekNum.replace('第 ', '').replace(' 周', '')),
            semesterId: this.queryParams.semesterId
          }
        })

        if (weekRes.code === 200 && weekRes.data) {
          this.emotionData = weekRes.data
        }
      } catch (error) {
        console.error('获取数据失败:', error)
      } finally {
        this.renderWeekChart()
      }
    },
    renderWeekChart() {
      const colors = ['#52c41a', '#1890ff', '#faad14', '#f5222d']
      const emotionLabels = ['无焦虑', '低度焦虑', '中度焦虑', '高度焦虑']

      if (this.emotionData && this.emotionData.weeks) {
        const weeks = this.emotionData.weeks || []
        const noAnxiety = this.emotionData.noAnxiety || []
        const lowAnxiety = this.emotionData.lowAnxiety || []
        const midAnxiety = this.emotionData.midAnxiety || []
        const highAnxiety = this.emotionData.highAnxiety || []

        let targetWeeks = weeks
        let targetNoAnxiety = noAnxiety
        let targetLowAnxiety = lowAnxiety
        let targetMidAnxiety = midAnxiety
        let targetHighAnxiety = highAnxiety

        if (this.queryParams.weekNum && this.queryParams.weekNum !== '全部周次') {
          const weekNumStr = this.queryParams.weekNum.replace(/\s+/g, '')
          const weekIndex = weeks.findIndex(w => w.replace(/\s+/g, '') === weekNumStr)
          if (weekIndex !== -1) {
            targetWeeks = [this.queryParams.weekNum]
            targetNoAnxiety = [noAnxiety[weekIndex]]
            targetLowAnxiety = [lowAnxiety[weekIndex]]
            targetMidAnxiety = [midAnxiety[weekIndex]]
            targetHighAnxiety = [highAnxiety[weekIndex]]
          } else {
            targetWeeks = []
            targetNoAnxiety = []
            targetLowAnxiety = []
            targetMidAnxiety = []
            targetHighAnxiety = []
          }
        }

        const series = [
          { name: emotionLabels[0], type: 'bar', barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '20%', data: targetNoAnxiety },
          { name: emotionLabels[1], type: 'bar', barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '20%', data: targetLowAnxiety },
          { name: emotionLabels[2], type: 'bar', barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '20%', data: targetMidAnxiety },
          { name: emotionLabels[3], type: 'bar', barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '20%', data: targetHighAnxiety }
        ]

        const option = {
          color: colors,
          tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
          legend: { top: '2%', data: emotionLabels, align: 'right', right: 10 },
          grid: { left: '2%', right: '2%', bottom: '7%', top: '10%', containLabel: true },
          dataZoom: this.queryParams.weekNum === '全部周次' ? [{ type: 'slider', start: 0, end: 80 }] : [],
          xAxis: {
            type: 'category',
            data: targetWeeks,
            axisTick: { alignWithLabel: true },
            axisLabel: { rotate: 45 }
          },
          yAxis: { type: 'value' },
          series: series
        }

        this.weekChart.setOption(option, true)
        this.weekChart.resize()
      } else {
        // 兼容旧格式（如有需要）
        let filteredData = Array.isArray(this.emotionData) ? this.emotionData : []
        if (this.queryParams.className) {
          filteredData = filteredData.filter(item =>
            item.classID && item.classID.toString().includes(this.queryParams.className)
          )
        }

        let targetWeeks = this.weeks
        let selectedWeekIndex = -1
        if (this.queryParams.weekNum && this.queryParams.weekNum !== '全部周次') {
          selectedWeekIndex = this.weeks.indexOf(this.queryParams.weekNum)
          targetWeeks = [this.queryParams.weekNum]
        }

        const aggregatedData = {
          '无焦虑': Array(targetWeeks.length).fill(0),
          '低度焦虑': Array(targetWeeks.length).fill(0),
          '中度焦虑': Array(targetWeeks.length).fill(0),
          '高焦虑情绪': Array(targetWeeks.length).fill(0)
        }

        filteredData.forEach(item => {
          emotionLabels.forEach(label => {
            if (item[label] && Array.isArray(item[label])) {
              item[label].forEach((value, weekIndex) => {
                if (this.queryParams.weekNum === '全部周次' && weekIndex < this.weeks.length) {
                  aggregatedData[label][weekIndex] += value
                } else if (selectedWeekIndex === weekIndex) {
                  aggregatedData[label][0] += value
                }
              })
            }
          })
        })

        const series = emotionLabels.map((label, index) => ({
          name: label,
          type: 'bar',
          barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '50%',
          data: aggregatedData[label]
        }))

        const option = {
          color: colors,
          tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
          legend: { top: '2%', data: emotionLabels, align: 'right', right: 10 },
          grid: { left: '2%', right: '2%', bottom: '7%', top: '10%', containLabel: true },
          dataZoom: this.queryParams.weekNum === '全部周次' ? [{ type: 'slider', start: 0, end: 80 }] : [],
          xAxis: {
            type: 'category',
            data: targetWeeks,
            axisTick: { alignWithLabel: true },
            axisLabel: { rotate: 45 }
          },
          yAxis: { type: 'value' },
          series: series
        }

        this.weekChart.setOption(option, true)
        this.weekChart.resize()
      }
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
.chart-container { height: 400px; }
</style>
