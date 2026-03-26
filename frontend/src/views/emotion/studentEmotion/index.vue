<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch">
      <el-form-item label="学生姓名" prop="studentName">
        <el-autocomplete
          v-model="queryParams.studentName"
          :fetch-suggestions="querySearch"
          placeholder="输入姓名关键词（如：小明）"
          clearable
          @select="handleSelectStudent"
          style="width: 220px"
          :trigger-on-focus="false"
          :debounce="300"
        >
          <template #default="{ item }">
            <div class="student-suggestion">
              <span>{{ item.studentName }}</span>
              <!-- 可选：显示用户名 -->
              <!-- <small style="color: #999; margin-left: 8px">{{ item.userName }}</small> -->
            </div>
          </template>
        </el-autocomplete>
      </el-form-item>
      <el-form-item label="学号" prop="studentId">
        <el-autocomplete
          v-model="queryParams.studentId"
          :fetch-suggestions="querySearchStudentId"
          placeholder="输入学号关键词（如：2023）"
          clearable
          @select="handleSelectStudentId"
          style="width: 220px"
          :trigger-on-focus="false"
          :debounce="300"
        >
          <template #default="{ item }">
            <div class="student-suggestion">
              <span>{{ item.studentId }} - {{ item.studentName }}</span>
            </div>
          </template>
        </el-autocomplete>
      </el-form-item>
      <el-form-item label="学期" prop="semesterId">
        <el-select v-model="queryParams.semesterId" placeholder="请选择学期" clearable>
          <el-option v-for="item in semesterList" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="周次" prop="weekNum">
        <el-select v-model="queryParams.weekNum" placeholder="请选择周次" clearable>
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
          <div slot="header">学生情绪状态统计图</div>
          <div ref="barChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header">学生各科目情绪分布</div>
          <div ref="subjectChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="24">
        <el-card class="chart-card">
          <div slot="header">学生每周情绪状态统计</div>
          <div ref="weekChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import request from '@/utils/request'
import { getWeek } from "date-fns"
import { searchStudents, searchStudentIds } from "@/api/system/student";
import websocketMixin from "@/utils/mixins/websocketMixin";

export default {
  name: 'StudentEmotion',
  mixins: [websocketMixin],
  data() {
    return {
      showSearch: true,
      autoCompleteOptions: [], // 存储下拉建议列表
      autoCompleteLoading: false, // 加载状态
      queryParams: {
        studentName: undefined,
        studentId: undefined,
        weekNum: '全部周次',
        semesterId: undefined
      },
      barChart: null,
      subjectChart: null,
      weekChart: null,
      loading: false,
      emotionData: [],
      semesterList: []
    }
  },
  computed: {
    // 获取当前选中的学期对象
    currentSemester() {
      if (!this.queryParams.semesterId) return null;
      return this.semesterList.find(s => s.id === this.queryParams.semesterId);
    },
    // 动态生成周次列表
    weeks() {
      const totalWeeks = this.currentSemester?.weeks || 20; // 默认兜底 20
      return Array.from({ length: totalWeeks }, (_, i) => `第 ${i + 1} 周`);
    }
  },
  watch: {
    'queryParams.semesterId'(newId) {
      // 切换学期时，重置周次为“全部周次”
      this.queryParams.weekNum = '全部周次';
      // 可选：自动重新查询
      this.handleQuery();
    },
    'queryParams.weekNum'() {
      this.handleQuery(); // 选中周次后自动刷新图表
    }
  },
  mounted() {
    this.initCharts()
  },
  created() {
    this.emotionData = [];
    this.loadSemesterList();
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.barChart) this.barChart.dispose()
    if (this.subjectChart) this.subjectChart.dispose()
    if (this.weekChart) this.weekChart.dispose()
  },
  methods: {
    handleQuery() {
      this.loadChartData()
    },
    resetForm(formName) {
      if (this.$refs[formName]) {
        this.$refs[formName].resetFields();
      }
    },
    resetQuery() {
      this.resetForm('queryForm')
      this.queryParams.weekNum = '全部周次'
      this.handleQuery()
    },
    initCharts() {
      this.barChart = echarts.init(this.$refs.barChart)
      this.subjectChart = echarts.init(this.$refs.subjectChart)
      this.weekChart = echarts.init(this.$refs.weekChart)
      this.loadChartData()
      
      window.addEventListener('resize', this.handleResize)
    },
    handleResize() {
      this.barChart && this.barChart.resize()
      this.subjectChart && this.subjectChart.resize()
      this.weekChart && this.weekChart.resize()
    },
    /** 搜索建议回调 */
    querySearch(queryString, cb) {
      if (!queryString || queryString.trim().length === 0) {
        cb([]);
        return;
      }
      this.autoCompleteLoading = true;
      searchStudents(queryString.trim())
        .then(response => {
          const list = response.data || [];
          // 转换为 autocomplete 需要的格式：{ value, ...rest }
          const suggestions = list.map(item => ({
            value: item.studentName, // 显示值
            ...item // 保留 userId 等信息
          }));
          cb(suggestions);
          this.autoCompleteLoading = false;
        })
        .catch(() => {
          cb([]);
          this.autoCompleteLoading = false;
        });
    },

    /** 选中学生后的回调 */
    handleSelectStudent(item) {
      // 可选：自动触发主列表查询
      this.handleQuery();
    },
    cleanClassInput() {
      if (this.form.classes) {
        // 移除所有空白字符（包括空格、全角空格、换行等）
        this.form.classes = this.form.classes.replace(/\s+/g, '');
      }
    },
    /** 学号搜索建议 */
    async querySearchStudentId(queryString, cb) {
      if (!queryString?.trim()) {
        cb([]);
        return;
      }
      try {
        const response = await searchStudentIds(queryString.trim());
        if (response.code === 200) {
          const list = response.data || [];
          const suggestions = list.map(item => ({
            value: item.studentId, // 输入框显示的值（学号）
            ...item
          }));
          cb(suggestions);
        } else {
          cb([]);
        }
      } catch (e) {
        console.error('学号搜索失败', e);
        cb([]);
      }
    },
    /** 选中学号后的回调 */
    handleSelectStudentId(item) {
      // 自动填充学生姓名
      this.queryParams.studentName = item.studentName;
      // 自动触发查询
      this.handleQuery();
    },

    // 获取学期列表
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
      this.loading = true
      try {
        // 获取学生情绪统计数据
        const statsRes = await request({
          url: '/system/results/studentStats',
          method: 'get',
          params: {
            //studentName: this.queryParams.studentName,
            studentName: this.queryParams.studentName,
            studentId: this.queryParams.studentId,
            semesterId: this.queryParams.semesterId,
            weekNum: this.queryParams.weekNum === '全部周次' ? null : parseInt(this.queryParams.weekNum.replace('第 ', '').replace(' 周', ''))
          }
        })

        if (statsRes.code === 200 && statsRes.data) {
          const anxietyStats = statsRes.data.anxietyStats || []
          this.renderBarChart(anxietyStats)
        }

        // 获取各科目情绪统计数据
        const subjectRes = await request({
          url: '/system/results/subjectStats',
          method: 'get',
          params: {
            //studentName: this.queryParams.studentName,
            studentName: this.queryParams.studentName,
            semesterId: this.queryParams.semesterId,
            studentId: this.queryParams.studentId,
            weekNum: this.queryParams.weekNum === '全部周次' ? null : parseInt(this.queryParams.weekNum.replace('第 ', '').replace(' 周', ''))
          }
        })

        if (subjectRes.code === 200 && subjectRes.data) {
          this.renderSubjectChart(subjectRes.data)
        }

        // 获取每周情绪数据
        const weekRes = await request({
          url: '/system/results/allWeeksStats',
          method: 'get',
          params: {
            //studentName: this.queryParams.studentName,
            studentName: this.queryParams.studentName,
            studentId: this.queryParams.studentId,
            semesterId: this.queryParams.semesterId,
            weekNum: this.queryParams.weekNum === '全部周次' ? null : parseInt(this.queryParams.weekNum.replace('第 ', '').replace(' 周', ''))
          }
        })

        if (weekRes.code === 200 && weekRes.data) {
          this.emotionData = weekRes.data
        }
      } catch (error) {
        console.error('获取数据失败:', error)
        // 使用默认数据
        this.renderDefaultCharts()
      } finally {
        this.loading = false
        // 渲染每周情绪图表
        this.renderWeekChart()
      }
    },
    renderBarChart(anxietyStats) {
      const colors = ['#52c41a', '#1890ff', '#faad14', '#f5222d']
      const barOption = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        toolbox: {
          feature: {
            saveAsImage: { show: true, name: '学生情绪状态统计图' }
          }
        },
        xAxis: {
          type: 'category',
          data: anxietyStats.map(item => item.name),
          axisTick: { alignWithLabel: true }
        },
        yAxis: { type: 'value', name: '次数' },
        series: [{
          type: 'bar',
          data: anxietyStats.map((item, index) => ({
            value: item.count,
            itemStyle: { 
              color: colors[index],
              borderRadius: [5, 5, 0, 0] // 圆角效果
            }
          })),
          barWidth: '40%',
          label: {
            show: true,
            position: 'top'
          }
        }]
      }
      this.barChart.setOption(barOption)
    },
    renderSubjectChart(data) {
      const subjects = data.subjects || []
      const subjectData = data.data || {}
      const colors = ['#52c41a', '#1890ff', '#faad14', '#f5222d']
      const names = ['无焦虑', '低度焦虑', '中度焦虑', '高度焦虑']

      const series = [0, 1, 2, 3].map((level, index) => ({
        name: names[index],
        type: 'bar',
        data: subjects.map(s => (subjectData[s] && subjectData[s][level]) || 0),
        itemStyle: { 
          color: colors[index],
          borderRadius: [4, 4, 0, 0] // 圆角
        },
        barWidth: '15%' // 稍微加宽
      }))

      const subjectOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderColor: '#ccc',
          borderWidth: 1,
          textStyle: { color: '#333' },
          confine: true,
          formatter: function(params) {
            let total = 0;
            let res = params[0].name + '<br/>';
            params.forEach(item => {
              res += item.marker + item.seriesName + ': ' + item.value + '<br/>';
              total += item.value ? Number(item.value) : 0;
            });
            res += '<div style="margin-top:5px;border-top:1px solid #eee;padding-top:5px;"><strong>总数量: ' + total + '</strong></div>';
            return res;
          }
        },
        legend: { data: names, top: '2%', left: 'center' }, // 统一放到顶部居中
        toolbox: {
          show: true,
          feature: {
            magicType: { show: true, type: ['line', 'bar', 'stack'] },
            saveAsImage: { show: true, name: '学生各科目情绪分布' }
          },
          right: 20
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%', // 底部空间可以减小，因为图例移到了顶部
          containLabel: true
        },
        xAxis: { type: 'category', data: subjects, axisLabel: { interval: 0, rotate: -30 } },
        yAxis: { type: 'value' },
        series: series
      }
      this.subjectChart.setOption(subjectOption)
    },
    renderWeekChart() {
      const colors = ['#52c41a', '#1890ff', '#faad14', '#f5222d']
      const emotionLabels = ['无焦虑', '低度焦虑', '中度焦虑', '高度焦虑']

      // 检查数据是否为后端返回的格式
      if (this.emotionData && this.emotionData.weeks) {
        // 后端返回的数据格式
        const weeks = this.emotionData.weeks || []
        const noAnxiety = this.emotionData.noAnxiety || []
        const lowAnxiety = this.emotionData.lowAnxiety || []
        const midAnxiety = this.emotionData.midAnxiety || []
        const highAnxiety = this.emotionData.highAnxiety || []

        // 处理周次选择
        let targetWeeks = weeks
        let targetNoAnxiety = noAnxiety
        let targetLowAnxiety = lowAnxiety
        let targetMidAnxiety = midAnxiety
        let targetHighAnxiety = highAnxiety

        if (this.queryParams.weekNum && this.queryParams.weekNum !== '全部周次') {
          const weekNumStr = this.queryParams.weekNum.replace(/\s+/g, '')
          const weekIndex = weeks.findIndex(week => week.replace(/\s+/g, '') === weekNumStr)
          if (weekIndex !== -1) {
            targetWeeks = [this.queryParams.weekNum]
            targetNoAnxiety = [noAnxiety[weekIndex]]
            targetLowAnxiety = [lowAnxiety[weekIndex]]
            targetMidAnxiety = [midAnxiety[weekIndex]]
            targetHighAnxiety = [highAnxiety[weekIndex]]
          } else {
            // 如果未找到对应周次，使用空数组
            targetWeeks = []
            targetNoAnxiety = []
            targetLowAnxiety = []
            targetMidAnxiety = []
            targetHighAnxiety = []
          }
        }

        // 构建 series
        const series = [
          {
            name: emotionLabels[0],
            type: 'bar',
            barWidth: this.queryParams.weekNum === '全部周次' ? '15%' : '20%', // 稍微加宽
            data: targetNoAnxiety,
            itemStyle: { 
              color: colors[0],
              borderRadius: [4, 4, 0, 0], // 圆角
              borderColor: '#fff',
              borderWidth: 1
            }
          },
          {
            name: emotionLabels[1],
            type: 'bar',
            barWidth: this.queryParams.weekNum === '全部周次' ? '15%' : '20%',
            data: targetLowAnxiety,
            itemStyle: { 
              color: colors[1],
              borderRadius: [4, 4, 0, 0],
              borderColor: '#fff',
              borderWidth: 1
            }
          },
          {
            name: emotionLabels[2],
            type: 'bar',
            barWidth: this.queryParams.weekNum === '全部周次' ? '15%' : '20%',
            data: targetMidAnxiety,
            itemStyle: { 
              color: colors[2],
              borderRadius: [4, 4, 0, 0],
              borderColor: '#fff',
              borderWidth: 1
            }
          },
          {
            name: emotionLabels[3],
            type: 'bar',
            barWidth: this.queryParams.weekNum === '全部周次' ? '15%' : '20%',
            data: targetHighAnxiety,
            itemStyle: { 
              color: colors[3],
              borderRadius: [4, 4, 0, 0],
              borderColor: '#fff',
              borderWidth: 1
            }
          }
        ]

        const option = {
          color: colors,
          toolbox: {
            show: true,
            feature: {
              dataView: { 
                readOnly: true,
                optionToContent: function(opt) {
                  var axisData = opt.xAxis[0].data;
                  var series = opt.series;
                  var table = '<div style="width:100%;height:100%;overflow-y:scroll;"><table style="width:100%;text-align:center;border-collapse:collapse;border:1px solid #ddd;"><tbody><tr>'
                               + '<td style="border:1px solid #ddd;padding:8px;font-weight:bold;background:#f5f7fa;">周次</td>';
                  for (var i = 0; i < series.length; i++) {
                    table += '<td style="border:1px solid #ddd;padding:8px;font-weight:bold;background:#f5f7fa;">' + series[i].name + '</td>';
                  }
                  table += '</tr>';
                  for (var i = 0, l = axisData.length; i < l; i++) {
                    table += '<tr>'
                             + '<td style="border:1px solid #ddd;padding:8px;">' + axisData[i] + '</td>';
                    for (var j = 0; j < series.length; j++) {
                      table += '<td style="border:1px solid #ddd;padding:8px;">' + series[j].data[i] + '</td>';
                    }
                    table += '</tr>';
                  }
                  table += '</tbody></table></div>';
                  return table;
                }
              },
              magicType: { type: ['line', 'bar', 'stack'] },
              restore: { show: true }, // 启用还原配置
              saveAsImage: { name: '学生每周情绪状态统计' }
            },
            right: 20
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            },
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            borderColor: '#ccc',
            borderWidth: 1,
            textStyle: { color: '#333' },
            confine: true,
            formatter: function(params) {
              let total = 0;
              let res = params[0].name + '<br/>';
              params.forEach(item => {
                res += item.marker + item.seriesName + ': ' + item.value + '<br/>';
                total += item.value ? Number(item.value) : 0;
              });
              res += '<div style="margin-top:5px;border-top:1px solid #eee;padding-top:5px;"><strong>总数量: ' + total + '</strong></div>';
              return res;
            }
          },
          legend: {
            top: '2%',
            data: emotionLabels,
            left: 'center' // 居中显示，避免与工具栏重叠
          },
          grid: {
            left: '2%',
            right: '2%',
            bottom: '7%',
            top: '15%', // 增加顶部空间
            containLabel: true
          },
          dataZoom: this.queryParams.weekNum === '全部周次' ? [
            {
              type: 'slider',
              show: true,
              xAxisIndex: 0,
              start: 0,
              end: 100, // 默认显示全部数据
              bottom: 10
            },
            {
              type: 'inside', // 支持鼠标滚轮缩放和拖拽
              xAxisIndex: 0,
              start: 0,
              end: 100
            }
          ] : [],
          xAxis: [
            {
              type: 'category',
              data: targetWeeks,
              axisTick: { alignWithLabel: true },
              axisLabel: { rotate: 45 }
            }
          ],
          yAxis: [
            {
              type: 'value'
            }
          ],
          series
        }

        this.weekChart.setOption(option)
        // 确保图表能够正确显示
        this.weekChart.resize()
      } else {
        // 兼容旧的数据格式（如果需要）
        let filteredData = Array.isArray(this.emotionData) ? this.emotionData : []
        if (this.queryParams.studentName) {
          filteredData = filteredData.filter(item =>
            item.name && item.name.includes(this.queryParams.studentName)
          )
        }

        // 处理周次选择
        let targetWeeks = this.weeks
        let selectedWeekIndex = -1
        if (this.queryParams.weekNum && this.queryParams.weekNum !== '全部周次') {
          selectedWeekIndex = this.weeks.indexOf(this.queryParams.weekNum)
          targetWeeks = [this.queryParams.weekNum]
        }

        // 聚合情绪数据
        const weeksCount = targetWeeks.length
        const aggregatedEmotionData = emotionLabels.map(() =>
          Array(weeksCount).fill(0)
        )

        filteredData.forEach(item => {
          emotionLabels.forEach((label, labelIndex) => {
            if (item[label] && Array.isArray(item[label])) {
              item[label].forEach((val, weekIndex) => {
                if (this.queryParams.weekNum === '全部周次') {
                  // 显示全部周次
                  if (weekIndex < this.weeks.length) {
                    aggregatedEmotionData[labelIndex][weekIndex] += val
                  }
                } else if (selectedWeekIndex === weekIndex) {
                  // 显示特定周次
                  aggregatedEmotionData[labelIndex][0] += val
                }
              })
            }
          })
        })

        // 构建 series
        const series = emotionLabels.map((label, index) => ({
          name: label,
          type: 'bar',
          barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '50%',
          data: aggregatedEmotionData[index]
        }))

        const option = {
          color: colors,
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            top: '2%',
            data: emotionLabels,
            left: 'center'
          },
          grid: {
            left: '2%',
            right: '2%',
            bottom: '7%',
            top: '15%',
            containLabel: true
          },
          dataZoom: this.queryParams.weekNum === '全部周次' ? [
            {
              type: 'slider',
              start: 0,
              end: 80
            }
          ] : [],
          xAxis: [
            {
              type: 'category',
              data: targetWeeks,
              axisTick: { alignWithLabel: true },
              axisLabel: { rotate: 45 }
            }
          ],
          yAxis: [
            {
              type: 'value'
            }
          ],
          series
        }

        this.weekChart.setOption(option)
        // 确保图表能够正确显示
        this.weekChart.resize()
      }
    },
    renderDefaultCharts() {
      // 默认数据
      const defaultAnxiety = [
        { name: '无焦虑', count: 0 },
        { name: '低度焦虑', count: 0 },
        { name: '中度焦虑', count: 0 },
        { name: '高焦虑情绪', count: 0 }
      ]
      this.renderBarChart(defaultAnxiety)

      const defaultSubject = {
        subjects: [],
        data: {}
      }
      this.renderSubjectChart(defaultSubject)
    },
    // 处理WebSocket更新通知
    handleWebSocketUpdate() {
      this.handleQuery();
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
