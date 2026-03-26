<template>
  <div class="main app-container">
    <div class="topQuery search-container">
      <el-form
        :model="queryParams"
        ref="queryForm"
        size="small"
        :inline="true"
        v-show="showSearch"
        label-width="68px"
        style="margin-left: 20px"
      >
        <el-form-item label="学生">
          <el-input
            v-model="queryParams.name"
            placeholder="请输入学生姓名"
            clearable
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            icon="el-icon-search"
            size="mini"
            @click="handleQuery"
          >搜索</el-button>
          <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div class="leftChart">
      <div id="student"></div>
    </div>
    <div class="rightChart">
      <div id="discipline"></div>
    </div>
  </div>
</template>
<script>
import * as echarts from "echarts";
import classData from "./classEmotionData.json";

export default {
  data() {
    return {
      showSearch: true,
      dateRange: [],
      queryParams: {
        name: null,
      },
      value1: null,
      weatherData: {
        city: "",
        weather: "",
        temperature: "",
      },
      classData: [],
      studentChartInstance: null,
      disciplineChartInstance: null,
    };
  },

  created() {
    this.classData = classData.classData;
  },

  mounted() {
    this.studentChartInstance = echarts.init(
      document.getElementById("student")
    );
    this.disciplineChartInstance = echarts.init(
      document.getElementById("discipline")
    );
    this.refreshCharts();
    this.bindResize(this.studentChartInstance);
    this.bindResize(this.disciplineChartInstance);
  },

  methods: {
    // 自动适配窗口大小
    bindResize(chart) {
      window.addEventListener("resize", () => {
        chart.resize();
      });
    },

    handleQuery() {
      this.refreshCharts();
    },

    resetQuery() {
      this.queryParams.name = null;
      this.refreshCharts();
    },

    refreshCharts() {
      const selectedClass = this.queryParams.name;
      const filtered = selectedClass
        ? this.classData.filter((item) => item.name.includes(selectedClass))
        : this.classData;

      const emotionCounts = {
        无焦虑: 0,
        低度焦虑: 0,
        中度焦虑: 0,
        高度焦虑: 0,
      };

      const subjects = [
        "语文",
        "数学",
        "英语",
        "道法",
        "历史",
        "物理",
        "化学",
        "地理",
        "生物",
      ];

      const subjectEmotionCounts = {
        无焦虑: Array(subjects.length).fill(0),
        低度焦虑: Array(subjects.length).fill(0),
        中度焦虑: Array(subjects.length).fill(0),
        高度焦虑: Array(subjects.length).fill(0),
      };

      // 遍历筛选后的所有班级数据
      filtered.forEach((item) => {
        // 遍历每个学科的索引
        subjects.forEach((subj, index) => {
          // 遍历每个情绪类别
          for (let emotion in subjectEmotionCounts) {
            const values = item[emotion]; // 获取当前item该情绪的数组
            if (Array.isArray(values)) {
              subjectEmotionCounts[emotion][index] += values[index] || 0;
              emotionCounts[emotion] += values[index] || 0; // 统计总体情绪次数
            }
          }
        });
      });

      this.updateStudentChart(emotionCounts);
      this.updateDisciplineChart(subjects, subjectEmotionCounts);
    },

    updateStudentChart(emotionCounts) {
      const data = [
        {
          value: emotionCounts["无焦虑"],
          itemStyle: { color: "#1F78B4" },
        },
        {
          value: emotionCounts["低度焦虑"],
          itemStyle: { color: "#A6CEE3" },
        },
        {
          value: emotionCounts["中度焦虑"],
          itemStyle: { color: "#B2DF8A" },
        },
        {
          value: emotionCounts["高度焦虑"],
          itemStyle: { color: "#33A02C" },
        },
      ];

      const option = {
        title: {
          text: "学生情绪状态统计图",
          top: "2%",
          left: "center",
          textStyle: { fontSize: 16 },
        },
        tooltip: {
          trigger: "axis",
          axisPointer: { type: "shadow" },
        },
        grid: {
          left: "4%",
          right: "4%",
          bottom: "8%",
          containLabel: true,
        },
        xAxis: [
          {
            type: "category",
            axisTick: { show: false },
            axisLabel: {
              textStyle: { fontSize: 14, color: "#4D4D4D" },
            },
            axisLine: {
              lineStyle: { color: "#707070" },
            },
            data: ["无焦虑", "低度焦虑", "中度焦虑", "高度焦虑"],
          },
        ],
        yAxis: {
          type: "value",
          name: "次数",
          nameTextStyle: { fontSize: 14, color: "#4D4D4D" },
          axisLabel: {
            textStyle: { fontSize: 12, color: "#4D4D4D" },
          },
          axisLine: {
            lineStyle: { color: "#707070" },
          },
        },
        series: [
          {
            name: "次数",
            type: "bar",
            barWidth: "60%",
            data,
          },
        ],
      };

      this.studentChartInstance.setOption(option);
    },

    updateDisciplineChart(subjects, subjectEmotionCounts) {
      const emotionTemplate = [
        {
          name: "无焦虑",
          colorFrom: "#8BDCFF",
          colorTo: "#4594E8",
        },
        {
          name: "低度焦虑",
          colorFrom: "#FFB2B2",
          colorTo: "#F45353",
        },
        {
          name: "中焦虑情绪",
          colorFrom: "#59FFB7",
          colorTo: "#37BDFF",
        },
        {
          name: "高焦虑情绪",
          colorFrom: "#59FF85",
          colorTo: "#37BD41",
        },
      ];

      const series = emotionTemplate.map((item) => ({
        name: item.name,
        type: "bar",
        barWidth: 15,
        barGap: "40%",
        data: subjectEmotionCounts[item.name],
        itemStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 1,
            x2: 0,
            y2: 0,
            colorStops: [
              { offset: 0, color: item.colorFrom },
              { offset: 1, color: item.colorTo },
            ],
            global: false,
          },
        },
      }));

      const option = {
        tooltip: {
          trigger: "axis",
          axisPointer: { type: "shadow" },
        },
        legend: {
          top: "bottom",
          data: emotionTemplate.map((item) => item.name),
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "8%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          data: subjects,
          axisLine: { lineStyle: { color: "#D2E6F9" } },
          axisTick: { show: false },
          axisLabel: { color: "#000" },
        },
        yAxis: {
          type: "value",
          splitLine: {
            show: true,
            lineStyle: {
              color: "#D2E6F9",
              type: "dashed",
            },
          },
          axisLine: { lineStyle: { color: "#D2E6F9" } },
          axisTick: { show: false },
          axisLabel: { color: "#000" },
        },
        series,
      };

      this.disciplineChartInstance.setOption(option);
    },
  },
};
</script>
<style lang="scss" scoped>
.main {
  height: calc(100vh - 85px);
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  .topQuery {
    width: 100%;
    height: calc(8% - 10px);
    margin-bottom: 10px;
    //阴影
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }
  .leftChart {
    width: calc(50% - 10px);
    height: 90%;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-right: 10px;
    border-radius: 10px;
    #student {
      width: 100%;
      height: 100%;
    }
  }
  .rightChart {
    width: calc(50% - 10px);
    height: 90%;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-left: 10px;
    border-radius: 10px;
    #discipline {
      width: 100%;
      height: 100%;
    }
  }
  .search-container {
    width: 100%;
    height: 9%;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-pack: center;
    -ms-flex-pack: center;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: flex-end;
    align-content: stretch;
    justify-content: center;
  }
}
</style>
