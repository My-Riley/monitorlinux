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
        <el-form-item label="班级">
          <el-input
            v-model="queryParams.classID"
            placeholder="请输入班级"
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
// 这里导入你的emotionData.json
import emotionData from "./emotionData.json";

export default {
  data() {
    return {
      showSearch: true,
      emotionData: [], // 所有班级数据
      combinedData: null, // 合并总数据
      currentData: null, // 当前显示数据
      queryParams: {
        classID: "", // 搜索用班级ID
      },
      studentChartInstance: null,
      disciplineChartInstance: null,
    };
  },

  mounted() {
    this.emotionData = emotionData.data;
    this.combinedData = this.mergeAllData(this.emotionData);
    this.currentData = this.combinedData;

    this.initCharts();
    this.renderCharts();
  },

  methods: {
    // 合并所有班级数据
    mergeAllData(dataArray) {
      if (!dataArray || dataArray.length === 0) return null;

      const anxietyTypes = Object.keys(dataArray[0].all);
      const subjectCount = dataArray[0].all[anxietyTypes[0]].length;

      const result = {};
      anxietyTypes.forEach((type) => {
        result[type] = new Array(subjectCount).fill(0);
      });

      dataArray.forEach((classItem) => {
        anxietyTypes.forEach((type) => {
          classItem.all[type].forEach((val, idx) => {
            result[type][idx] += val;
          });
        });
      });

      return result;
    },

    // 根据班级ID过滤
    filterByClassID(classID) {
      const found = this.emotionData.find((item) => item.classID == classID);
      if (found) {
        this.currentData = found.all;
      } else {
        this.currentData = this.combinedData;
      }
    },

    // 搜索输入处理
    handleQuery() {
      if (!this.queryParams.classID) {
        this.currentData = this.combinedData;
      } else {
        this.filterByClassID(this.queryParams.classID);
      }
      this.renderCharts();
    },
    resetQuery() {
      this.queryParams.classID = "";
      this.handleQuery();
    },

    // 初始化echarts实例
    initCharts() {
      this.studentChartInstance = echarts.init(
        document.getElementById("student")
      );
      this.disciplineChartInstance = echarts.init(
        document.getElementById("discipline")
      );
    },

    // 渲染两个图表
    renderCharts() {
      this.renderStudentChart();
      this.renderDisciplineChart();
    },

    // 学生情绪饼图
    renderStudentChart() {
      const data = this.currentData;
      if (!data) return;

      const anxietyTypes = Object.keys(data);
      const values = anxietyTypes.map((type) =>
        data[type].reduce((a, b) => a + b, 0)
      );

      const colorList = ["#507AFF", "#51D9A2", "#FFC371", "#797AFF"];

      const syjgdata = anxietyTypes.map((name, i) => ({
        name,
        value: values[i],
      }));

      const option = {
        title: {
          text: "学生焦虑类型总人数分布",
          left: "center",
        },
        tooltip: {
          trigger: "item",
        },
        legend: {
          bottom: 10,
          left: "center",
          data: anxietyTypes,
        },
        color: colorList,
        series: [
          {
            name: "人数",
            type: "pie",
            radius: "50%",
            data: syjgdata,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
            label: {
              formatter: "{b}: {c}人 ({d}%)",
            },
          },
        ],
      };
      window.addEventListener("resize", () => {
        this.studentChartInstance.resize();
      });
      this.studentChartInstance.setOption(option);
    },

    // 各科目焦虑柱状图
    renderDisciplineChart() {
      const data = this.currentData;
      if (!data) return;

      const anxietyTypes = Object.keys(data);
      const xLabels = [
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
      const barColors = [
        "rgba(80, 122, 255, 0.8)",
        "rgba(81, 217, 162, 0.8)",
        "rgba(255, 195, 113, 0.8)",
        "rgba(121, 122, 255, 0.8)",
      ];

      const series = anxietyTypes.map((type, index) => ({
        name: type,
        type: "bar",
        data: data[type],
        itemStyle: {
          color: barColors[index % barColors.length],
        },
      }));

      const option = {
        title: {
          text: "各科目焦虑人数分布",
          left: "center",
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        legend: {
          top: 30,
          data: anxietyTypes,
        },
        xAxis: {
          type: "category",
          data: xLabels,
        },
        yAxis: {
          type: "value",
          name: "人数",
        },
        series,
      };
      window.addEventListener("resize", () => {
        this.disciplineChartInstance.resize();
      });
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
