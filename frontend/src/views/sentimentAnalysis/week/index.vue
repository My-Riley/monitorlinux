<template>
  <div class="main app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" style="margin-bottom: 20px;">
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
    <div class="leftChart">
      <div id="student"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import { getWeek } from "date-fns";
import request from '@/utils/request';

export default {
  data() {
    return {
      studentChart: null,
      emotionData: [], // 所有学生的情绪数据
      queryParams: {
        weekNum: '全部周次'
      }
    };
  },
  mounted() {
    this.initStudentChart();
    this.loadChartData();
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
    if (this.studentChart) {
      this.studentChart.dispose();
    }
  },
  created() {
    this.emotionData = [];
  },
  computed: {
    weeks() {
      // 显示固定20周的周次选择器，与后端格式保持一致（无空格）
      return Array.from({ length: 20 }, (_, i) => `第${i + 1}周`);
    },
  },
  methods: {
    async loadChartData() {
      try {
        // 获取每周情绪数据
        const weekRes = await request({
          url: '/system/results/allWeeksStats',
          method: 'get',
          params: {
            weekNum: this.queryParams.weekNum === '全部周次' ? null : parseInt(this.queryParams.weekNum.replace('第', '').replace('周', ''))
          }
        })

        if (weekRes.code === 200 && weekRes.data) {
          this.emotionData = weekRes.data
          this.setStudentChartOption();
        }
      } catch (error) {
        console.error('获取数据失败:', error)
      }
    },
    handleQuery() {
      this.setStudentChartOption();
    },
    resetQuery() {
      this.queryParams.weekNum = '全部周次';
      this.setStudentChartOption();
    },
    initStudentChart() {
      this.studentChart = echarts.init(document.getElementById("student"));
    },
    setStudentChartOption() {
      const colors = ["#52c41a", "#1890ff", "#faad14", "#f5222d"];
      const emotionLabels = [
        "无焦虑",
        "低度焦虑",
        "中度焦虑",
        "高焦虑情绪",
      ];

      // 直接使用后端返回的对象格式数据
      const data = this.emotionData || {};
      const weeks = data.weeks || [];

      // 处理周次选择
      let targetWeeks = weeks;
      let noAnxiety = data.noAnxiety || [];
      let lowAnxiety = data.lowAnxiety || [];
      let midAnxiety = data.midAnxiety || [];
      let highAnxiety = data.highAnxiety || [];

      if (this.queryParams.weekNum && this.queryParams.weekNum !== '全部周次') {
        // 查找选中周次在后端数据中的索引
        const selectedWeekIndex = targetWeeks.findIndex(week => week === this.queryParams.weekNum);
        if (selectedWeekIndex !== -1) {
          // 只显示选中的周次数据
          targetWeeks = [this.queryParams.weekNum];
          noAnxiety = [noAnxiety[selectedWeekIndex]];
          lowAnxiety = [lowAnxiety[selectedWeekIndex]];
          midAnxiety = [midAnxiety[selectedWeekIndex]];
          highAnxiety = [highAnxiety[selectedWeekIndex]];
        }
      }

      // 构建 series
      const series = [
        {
          name: emotionLabels[0],
          type: "bar",
          barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '50%',
          data: noAnxiety,
          itemStyle: { color: colors[0] }
        },
        {
          name: emotionLabels[1],
          type: "bar",
          barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '50%',
          data: lowAnxiety,
          itemStyle: { color: colors[1] }
        },
        {
          name: emotionLabels[2],
          type: "bar",
          barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '50%',
          data: midAnxiety,
          itemStyle: { color: colors[2] }
        },
        {
          name: emotionLabels[3],
          type: "bar",
          barWidth: this.queryParams.weekNum === '全部周次' ? '10%' : '50%',
          data: highAnxiety,
          itemStyle: { color: colors[3] }
        }
      ];

      const option = {
        title: {
          text: "各周学生情绪状态统计",
          top: "2%",
        },
        color: colors,
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        legend: {
          top: "2%",
          data: emotionLabels,
          align: "right",
          right: 10,
        },
        grid: {
          left: "2%",
          right: "2%",
          bottom: "7%",
          top: "10%",
          containLabel: true,
        },
        dataZoom: this.queryParams.weekNum === '全部周次' ? [
          {
            type: "slider",
            start: 0,
            end: 80,
          },
        ] : [],
        xAxis: [
          {
            type: "category",
            data: targetWeeks,
            axisTick: { alignWithLabel: true },
            axisLabel: { rotate: 45 },
          },
        ],
        yAxis: [
          {
            type: "value",
          },
        ],
        series,
      };

      this.studentChart.setOption(option);
    },
    handleResize() {
      if (this.studentChart) {
        this.studentChart.resize();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.main {
  height: calc(100vh - 85px);
  width: 100%;
  display: flex;
  .leftChart {
    width: 100%;
    height: 100%;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    border-radius: 10px;
    #student {
      width: 100%;
      height: 100%;
    }
  }
}
</style>
