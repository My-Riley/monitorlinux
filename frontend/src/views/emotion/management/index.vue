<template>
  <div class="main">
    <div class="right-panel">
      <div class="right-section right-section-top">
        <div class="exponent-header">情绪数量</div>
        <div id="exponent"></div>
      </div>
      <div class="right-section right-section-bottom">
        <div class="exponent-bottom-header">
          <div class="text">
            <i><b>检测记录</b></i>
          </div>
          <div style="margin-right: 20px">
            <el-form
              :model="queryParams"
              ref="queryForm"
              size="small"
              :inline="true"
              v-show="showSearch"
              label-width="68px"
              @submit.native.prevent
            >
              <el-form-item label="学生姓名" prop="studentName">
                <el-input
                  v-model="queryParams.studentName"
                  placeholder="请输入学生姓名"
                  clearable
                  style="width: 240px"
                  @keyup.enter.native="handleQuery"
                />
              </el-form-item>
              <el-form-item label="检测时间">
                <el-date-picker
                  v-model="dateRange"
                  style="width: 240px"
                  value-format="yyyy-MM-dd"
                  type="daterange"
                  range-separator="-"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                ></el-date-picker>
              </el-form-item>
              <el-form-item>
                <el-button
                  style="margin-left: 0px; height: 32px"
                  icon="el-icon-search"
                  circle
                  @click="handleQuery"
                ></el-button>
                <el-button
                  icon="el-icon-refresh-right"
                  circle
                  @click="resetQuery"
                ></el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
        <div style="width: 100%; height: 90%; padding: 10px">
          <el-table
            stripe
            :data="resultsList"
            style="width: 100%; scrollbar-width: none"
            :row-class-name="tableRowClassName"
            :header-cell-style="{ background: '#c1e0ff', color: '#606266' }"
            height="90%"
          >
            <el-table-column label="姓名" align="center" prop="studentName" />
            <el-table-column label="学号" align="center" prop="studentId" />
            <el-table-column label="年级" align="center" prop="grade" />
            <el-table-column label="班级" align="center" prop="classes" />
            <el-table-column
              label="设备ID号"
              align="center"
              prop="cameraIp"
            />
            <el-table-column
              label="情绪"
              align="center"
              prop="emotion"
              width="120px"
            >
              <template slot-scope="scope">
                <el-tag :style="scope.row.emotion">
                  {{ scope.row.emotion }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="地点" align="center" prop="address" />
            <el-table-column
              label="检测时间"
              align="center"
              prop="createTime"
              width="180"
            >
              <template slot-scope="scope">
                <span>{{
                  parseTime(scope.row.createTime, "{y}-{m}-{d} {h}:{m}:{s}")
                }}</span>
              </template>
            </el-table-column>
          </el-table>
          <pagination
            v-show="total > 0"
            :total="total"
            :page.sync="queryParams.pageNum"
            :limit.sync="queryParams.pageSize"
            @pagination="getList"
          />
        </div>
      </div>
    </div>
    <div class="left-panel">
      <div class="left-section left-section-medium">
        <div class="section-header">
          <i><b>情绪统计</b></i>
        </div>
        <div class="section-body">
          <div id="positionBox"></div>
        </div>
      </div>
      <div class="left-section left-section-small left-section-last">
        <div class="section-header">
          <i><b>活跃场所</b></i>
        </div>
        <div class="section-body">
          <div id="place"></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import * as echarts from "echarts";
import { listResults } from "@/api/aberrantEmotions";
import { getEmotionCount } from "@/api/management";
export default {
  data() {
    return {
      baseUrl: process.env.VUE_APP_BASE_API, // 基础地址
      student: null, // 学生信息
      resultsList: [],
      // 总条数
      total: 0,
      showSearch: true,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        studentName: undefined,
      },
      // 日期范围
      dateRange: [],
      emotionCountData: [],
      chartData: [
        { name: "图书馆", value: 3 },
        { name: "体育馆", value: 1 },
        { name: "食堂", value: 2 },
        { name: "教学楼", value: 6 },
        { name: "田径场", value: 1 },
        { name: "校门口", value: 2 },
        { name: "操场", value: 7 },
      ],
    };
  },
  created() {
    this.student = this.$route.query.value;
  },
  mounted() {
    if (this.$store.state.app.sidebar.opened == true) {
      this.$store.dispatch("app/toggleSideBar");
    }
    this.generateDateArray();
    this.exponentChat();
    this.positionBoxChart();
    this.placeChat();
    this.getList();
    this.getEmotionCount();
  },
  computed: {
    imgUrl() {
      return this.student?.faceImage || "";
    },
  },

  methods: {
    //查询检测记录列表
    getList() {
      this.loading = true;

      listResults(this.queryParams, this.dateRange).then((response) => {
        this.resultsList = response.rows;
        this.total = response.total;
        this.loading = false;
      });
    },
    getTagStyle(emotion) {
      const emotionStyles = {
        neutral: { backgroundColor: "#e0e0e0", color: "#000" },
        happiness: { backgroundColor: "#64b5f6", color: "#fff" },
        surprise: { backgroundColor: "#ffeb3b", color: "#000" },
        sadness: { backgroundColor: "#90caf9", color: "#000" },
        anger: { backgroundColor: "#e57373", color: "#fff" },
        disgust: { backgroundColor: "#f44336", color: "#fff" },
        fear: { backgroundColor: "#ff9800", color: "#fff" },
        contempt: { backgroundColor: "#9e9e9e", color: "#fff" },
        unknown: { backgroundColor: "#9c27b0", color: "#fff" },
      };
      return emotionStyles[emotion] || {};
    },
    // 根据情绪类型返回对应的标签文本
    getEmotionLabel(emotion) {
      const emotionLabels = {
        neutral: "正常",
        happiness: "喜悦",
        surprise: "惊讶",
        sadness: "悲伤",
        anger: "愤怒",
        disgust: "厌恶",
        fear: "恐惧",
        contempt: "藐视",
        unknown: "未知",
      };
      return emotionLabels[emotion] || "未知";
    },
    //查询情绪数量Echarts数据
    getEmotionCount() {
      getEmotionCount(this.queryParams, this.dateRange).then((response) => {
        this.emotionCountData = response.rows;
        this.exponentChat();
      });
    },
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.getList();
      this.getEmotionCount();
    },
    resetQuery() {
      this.dateRange = [];
      this.resetForm("queryForm");
      this.queryParams.deptId = undefined;
      this.handleQuery();
    },
    generateDateArray() {
      const today = new Date();
      const lineX = [];
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        const day = date.getDate().toString().padStart(2, "0");
        lineX.push(`${year}-${month}-${day}`);
      }
      return lineX;
    },
    // 情绪数量Echarts
    exponentChat() {
      let exponentChat = echarts.init(document.getElementById("exponent"));
      const emotions = [
        { name: "愤怒", color: "#4ca273", data: [] },
        { name: "藐视", color: "#2b8ec9", data: [] },
        { name: "惊讶", color: "#a87057", data: [] },
        { name: "厌恶", color: "#964264", data: [] },
        { name: "恐惧", color: "#61766c", data: [] },
        { name: "悲伤", color: "#2bae85", data: [] },
        { name: "喜悦", color: "#b7d07a", data: [] },
        { name: "正常", color: "#ccc", data: [] },
      ];

      const dates = this.emotionCountData.map((item) => item.date);
      dates.forEach((date) => {
        emotions.forEach((emotion) => {
          const item = this.emotionCountData.find(
            (item) =>
              item.date === date &&
              this.emotionMap(item.emotion) === emotion.name
          );
          emotion.data.push(item ? item.count : 0); // 如果没有找到数据，填充为 0
        });
      });

      const series = emotions.map((emotion) => ({
        name: emotion.name,
        type: "line",
        smooth: true,
        lineStyle: {
          normal: {
            width: 3,
            color: emotion.color,
          },
        },
        itemStyle: {
          color: emotion.color,
          borderColor: "#fff",
          borderWidth: 2,
        },
        data: emotion.data,
      }));

      const option = {
        backgroundColor: "#e1f1ff",
        grid: {
          top: "15%",
          bottom: "10%",
          left: "4%",
          right: "4%",
        },
        tooltip: {
          trigger: "axis",
          position: (point, params, dom, rect, size) => [point[0], 20],
        },
        legend: {
          data: emotions.map((emotion) => emotion.name),
          top: 20,
          icon: "circle",
          textStyle: {
            fontSize: 12,
            color: "#c8c8c8",
          },
        },
        toolbox: {
          show: true,
        },
        calculable: true,
        xAxis: [
          {
            type: "category",
            boundaryGap: false,
            data: dates, // 使用后端返回的日期
          },
        ],
        yAxis: [
          {
            type: "value",
          },
        ],
        series: series, // 动态生成的系列数据
      };

      window.addEventListener("resize", () => {
        exponentChat.resize();
      });

      exponentChat.setOption(option);
    },
    emotionMap(emotion) {
      const map = {
        neutral: "正常",
        fear: "恐惧",
        anger: "愤怒",
        contempt: "藐视",
        surprise: "惊讶",
        disgust: "厌恶",
        sadness: "悲伤",
        joy: "喜悦",
      };
      return map[emotion] || emotion; // 如果没有匹配则返回原始情感
    },
    // 情绪统计Echarts
    positionBoxChart() {
      let positionBoxChart = echarts.init(
        document.getElementById("positionBox")
      );
      let option = {
        animation: true,
        grid: {
          top: "5%",
          bottom: "10%",
          left: "8%",
          right: "2%",
        },
        xAxis: {
          type: "category",
          data: [
            "教学楼",
            "图书馆",
            "校门口",
            "操场",
            "食堂",
            "体育馆",
            "田径场",
          ],
          boundaryGap: ["10", "10"], // 设置为 false，去除两端的空白
          axisLine: {
            show: true, // 去掉 X 轴的坐标轴线
          },
          axisTick: {
            show: false, // 去掉 X 轴的刻度线
          },
          splitLine: {
            show: false, // 去掉网格分隔线
          },
          axisLabel: {
            show: true,
            margin: 14,
            fontSize: 10,
            textStyle: {
              color: "#094b88", // X 轴文字颜色
            },
          },
        },
        yAxis: {
          type: "value",
          min: 0, // 从 0 开始，避免下方的空白
          max: 100,
          interval: 25,
          splitLine: {
            show: false, // 去掉 Y 轴的网格分隔线
          },
          axisTick: {
            show: false, // 去掉 Y 轴的刻度线
          },
          axisLine: {
            show: true, // 去掉 Y 轴的坐标轴线
          },
          axisLabel: {
            show: true,
            margin: 5,
            fontSize: 12,
            textStyle: {
              color: "#094b88", // Y 轴文字颜色
            },
          },
        },
        series: [
          {
            type: "bar",
            barWidth: 16,
            itemStyle: {
              normal: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: "rgba(146, 225, 255, 1)" },
                  { offset: 1, color: "rgba(0, 151, 251, 1)" },
                ]),
              },
            },
            data: [70, 50, 80, 86, 78, 64, 57],
            z: 10,
            zlevel: 0,
            label: {
              show: true, // 显示标签
              position: "top", // 设置标签显示在柱子上方
              textStyle: {
                color: "#094b88", // 设置标签字体颜色为 #094b88
                fontSize: 12, // 设置字体大小
              },
            },
          },

          {
            name: "背影",
            type: "line",
            smooth: true, // 平滑曲线显示
            showAllSymbol: false, // 显示所有图形
            symbolSize: 0,
            lineStyle: {
              width: 0,
            },
            areaStyle: {
              color: "rgba(0, 151, 251, 0.1)",
            },
            data: [70, 50, 80, 86, 78, 64, 57],
            z: 5,
          },
        ],
        dataZoom: [
          {
            type: "slider",
            show: false,
            xAxisIndex: [0],
            endValue: 0,
            startValue: 100,
          },
        ],
      };
      window.addEventListener("resize", () => {
        positionBoxChart.resize();
      });
      positionBoxChart.setOption(option);
    },
    //活跃场所Echarts

    placeChat() {
      // 确保 placeChat 在 Vue 的上下文中初始化
      this.placeChat = echarts.init(document.getElementById("place"));
      this.updateChart(); // 进行初始化
    },

    updateChart() {
      const colorList = this.chartData.map((item) =>
        this.getDynamicColor(item.value)
      );

      const option = {
        title: {
          show: true,
          x: "center",
          y: "bottom",
          backgroundColor: "rgba(0,0,0,0)",
          borderColor: "#ccc",
          borderWidth: 0,
          padding: 0,
          itemGap: 10,
          textStyle: {
            fontSize: 18,
            fontWeight: "bolder",
            color: "#333",
          },
          subtextStyle: {
            color: "#aaa",
          },
        },
        backgroundColor: "#fff",
        tooltip: {},
        animationDurationUpdate: function (idx) {
          return idx * 100;
        },
        animationEasingUpdate: "bounceIn",
        color: ["#fff", "#fff", "#fff"],
        series: [
          {
            type: "graph",
            layout: "force",
            force: {
              repulsion: 150,
              edgeLength: 10,
            },
            roam: true,
            data: this.chartData.map((item, index) => ({
              name: item.name,
              value: item.value,
              symbolSize: 48,
              draggable: true,
              itemStyle: {
                normal: {
                  shadowBlur: 100,
                  shadowColor: colorList[index * 2],
                  color: colorList[index],
                },
              },
              label: {
                normal: {
                  show: true,
                  color: "#fff",
                },
              },
            })),
          },
        ],
      };

      // 确保 `placeChat` 是正确的 ECharts 实例
      if (this.placeChat) {
        this.placeChat.setOption(option);
      }

      // 在窗口调整大小时自动适应
      window.addEventListener("resize", () => {
        if (this.placeChat) {
          this.placeChat.resize();
        }
      });
    },

    getDynamicColor() {
      const colorList = [
        "#ff7f50",
        "#87cefa",
        "#da70d6",
        "#32cd32",
        "#6495ed",
        "#ff69b4",
        "#ba55d3",
        "#cd5c5c",
        "#ffa500",
        "#40e0d0",
        "#1e90ff",
        "#ff6347",
        "#7b68ee",
        "#d0648a",
        "#ffd700",
        "#6b8e23",
        "#4ea397",
        "#3cb371",
        "#b8860b",
        "#7bd9a5",
        "#ff7f50",
        "#87cefa",
        "#da70d6",
        "#32cd32",
        "#6495ed",
        "#ff69b4",
        "#ba55d3",
        "#cd5c5c",
        "#ffa500",
        "#40e0d0",
        "#1e90ff",
        "#ff6347",
        "#7b68ee",
        "#00fa9a",
        "#ffd700",
        "#6b8e23",
        "#ff00ff",
        "#3cb371",
        "#b8860b",
        "#30e0e0",
        "#929fff",
        "#9de0ff",
        "#ffa897",
        "#af87fe",
        "#7dc3fe",
        "#bb60b2",
        "#433e7c",
        "#f47a75",
        "#009db2",
        "#024b51",
        "#0780cf",
        "#765005",
        "#e75840",
        "#26ccd8",
        "#3685fe",
        "#9977ef",
        "#f5616f",
        "#f7b13f",
        "#f9e264",
        "#50c48f",
      ];

      // 从颜色数组中随机选取一个颜色
      const randomIndex = Math.floor(Math.random() * colorList.length);
      return colorList[randomIndex];
    },
    tableRowClassName({ row, rowIndex }) {
      if (rowIndex === 1) {
        return "warning-row";
      } else if (rowIndex === 3) {
        return "success-row";
      }
      return "";
    },
  },
  watch: {
    // 当 chartData 改变时，更新图表
    chartData: "updateChart",
  },
};
</script>
<style lang="scss" scoped>
.el-table .warning-row {
  background: oldlace;
}

.el-table .success-row {
  background: #f0f9eb;
}

#exponent {
  width: 100%;
  height: 90%;
}

.main {
  width: calc(100vw - 40px);
  height: calc(100vh - 40px);
  margin: 20px 20px 20px 20px;
  display: flex;
}

#positionBox {
  width: 99%;
  height: 100%;
}

#place {
  width: 100%;
  height: 100%;
}

.left-panel {
  width: 25%;
  height: 100%;
  border-radius: 15px;

  .left-section {
    width: 100%;
    background-color: #ecf6ff;
    border-radius: 10px;

    &.left-section-top-small {
      height: calc(20% - 10px);
      margin-bottom: 10px;
      display: flex;
      border: 1px solid #0e9efc;

      div {
        width: 50%;
        height: 100%;

        img {
          width: 100%;
          height: 100%;
        }
      }

      .user-Information {
        display: flex;
        flex-direction: column;
        padding-left: 14px;
        font-size: 14px;
        color: #a4a7ac;

        div {
          width: 100%;
          line-height: 200%;
        }
      }
    }

    &.left-section-small {
      height: calc(50% - 10px);
      margin-bottom: 10px;
      border: 1px solid #0e9efc;
    }

    &.left-section-medium {
      border: 1px solid #0e9efc;
      height: 50%;
    }

    &.left-section-last {
      margin-top: 10px;
    }

    .section-header {
      width: 100%;
      height: 10%;
      background: linear-gradient(
        to bottom right,
        rgba(213, 231, 250),
        rgba(170, 213, 244)
      );
      color: #094b88;
      display: flex;
      align-items: center;
      padding-left: 5px;
      font-weight: bold;
      border-radius: 10px 10px 0 0;
    }

    .section-body {
      width: 100%;
      height: 90%;
      /* 可根据需要添加具体样式 */
    }
  }
}

.right-panel {
  width: calc(75% - 70px);
  height: 100%;
  margin-right: 20px;
  border-radius: 15px;

  .right-section {
    width: 100%;
    background-color: #ecf6ff;
    border-radius: 10px;
    border: 1px solid #0e9efc;

    &.right-section-top {
      height: 29%;
    }

    &.right-section-bottom {
      height: calc(71% - 10px);
      margin-top: 10px;
    }
  }

  .exponent-header {
    width: 100%;
    height: 10%;
    color: rgb(9, 75, 136);
    display: flex;
    padding-left: 5px;
    font-weight: bold;
    border-radius: 10px 10px 0px 0px;
    text-align: center;
    align-items: center;
    justify-content: center;
    background: linear-gradient(
      to bottom right,
      rgba(213, 231, 250),
      rgba(170, 213, 244)
    );
  }

  .exponent-bottom-header {
    width: 100%;
    height: 10%;
    color: #094b88;
    display: flex;
    padding-left: 5px;
    background: linear-gradient(to bottom right, #d5e7fa, #aad5f4);
    align-items: center;
    border-radius: 10px 10px 0 0;
    justify-content: space-between;
    .text {
      width: 30%;
      margin-left: 10px;
    }
  }
  //搜索框
  .searchBox {
    width: 50%;
  }
}

::v-deep .el-input__suffix {
  position: absolute;
  height: 100%;
  right: 5px;
  top: 6px;
  text-align: center;
  color: #c0c4cc;
  -webkit-transition: all 0.3s;
  transition: all 0.3s;
  pointer-events: none;
}

::v-deep .el-button:hover,
.el-button:focus {
  color: #fff !important;
  border-color: #409efe;
  background-color: #409efe;
}

::v-deep .el-button {
  background: #0c5a8c;
  color: #a2d6f9;
  display: inline-block;
  line-height: 6px;
  white-space: nowrap;
  cursor: pointer;
  border: 1px solid transparent;
  font-family: "PingFang SC";
  -webkit-appearance: none;
  text-align: center;
  -webkit-box-sizing: border-box;
  box-sizing: border-box;
  outline: none;
  margin: 0;
  -webkit-transition: 0.1s;
  transition: 0.1s;
  font-weight: 400;
  -moz-user-select: none;
  -webkit-user-select: none;
  -ms-user-select: none;
  padding: 9px 16px;
  font-size: 13px;
  margin-top: 10px;
  border-radius: 4px;
  margin-left: 20px;
}

::v-deep .el-form-item__content {
  line-height: 40px;
  position: static;
  font-size: 14px;
}

::v-deep .el-form-item--medium .el-form-item__label {
  line-height: 40px;
}

::v-deep .pagination-container[data-v-72233bcd] {
  /* background: #fff; */
  padding: 32px 16px;
}

::v-deep .el-table--striped .el-table__body tr.el-table__row--striped td {
  background: #fff;
}

/* 非斑马纹颜色 */
::v-deep .el-table tr {
  background: #e1f1ff;
}

/* 斑马纹颜色定义完之后会显示自带的边框颜色，这里要重置 */
::v-deep .el-table td,
.building-top .el-table th.is-leaf {
  border: none;
  color: #000;
}

/* 这里是滑过斑马纹滑过时的颜色 */
::v-deep .el-table--enable-row-hover .el-table__body tr:hover > td {
  background-color: #e1f1ff;
}

::v-deep .pagination-container[data-v-72233bcd] {
  /* background: #fff; */
  padding: 32px 16px;
}
::v-deep .el-table__body-wrapper {
  overflow-y: auto;
  scrollbar-width: none;
}
::v-deep .pagination-container[data-v-72233bcd] {
  background: none;
  padding: 32px 16px;
}
::v-deep .el-form-item--small.el-form-item {
  margin-bottom: 5px;
}
::v-deep .el-form--inline .el-form-item {
  display: inline-block;
  margin-right: 10px;
  vertical-align: bottom;
}
::v-deep .el-input--small .el-input__inner {
  height: 32px;
  line-height: 32px;
}
::v-deep .el-form-item--small .el-form-item__label {
  line-height: 42px;
}
::v-deep [data-v-2cf3b854] .el-form-item__content {
  line-height: 40px;
  position: static;
  font-size: 14px;
  margin-bottom: 5px;
}
</style>
