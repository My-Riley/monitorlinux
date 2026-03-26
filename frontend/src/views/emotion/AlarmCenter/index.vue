<template>
  <div class="main">
    <div class="rightBox">
      <div class="section section-small">
        <div class="section-header">
          <i><b>告警统计</b></i>
        </div>
        <div class="section-body">
          <div id="alert"></div>
        </div>
      </div>
      <div class="section section-large">
        <div class="section-header">
          <i><b>情绪异常报告排名</b></i>
        </div>
        <div class="section-body">
          <div id="ranking"></div>
        </div>
      </div>
      <div class="section section-large section-last">
        <div class="section-header">
          <i><b>近期告警趋势</b></i>
        </div>
        <div class="section-body">
          <div id="trend"></div>
        </div>
      </div>
    </div>
    <div class="leftBox">
      <div class="searchBox">
        <el-form
          ref="queryForm"
          :inline="true"
          @submit.native.prevent
          class="box"
        >
          <el-form-item prop="userName" label="名称">
            <el-input
              placeholder="请输入"
              v-model="inputValue"
              @keydown.enter="handleEnter"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" size="mini" @click="search">搜索</el-button>
          </el-form-item>
        </el-form>
      </div>
      <div class="tableBox">
        <div
          class="tableBox-mini"
          v-for="(item, index) in userData"
          :key="index"
        >
          <!--  @click="toManagement(item)" -->
          <div class="tableBox-user">
            <div class="tableBox-userBox">
              <div class="tableBox-user-imgBox">
                <img :src="item.faceImage" alt="" />
              </div>
            </div>

            <div class="user-Information">
              <div style="height: 20%; font-size: 20px; color: #62aff5">
                <b><i>{{ item.userName }}</i></b>
              </div>
              <div style="height: 20%">学号：{{ item.studentId }}</div>
              <div style="height: 20%">
                班级：{{ item.grade }}{{ item.classes }}
              </div>
              <div style="height: 20%">告警：情绪异常</div>
              <div style="height: 20%">时间：{{ item.sj }}</div>
            </div>
          </div>

          <div class="tableBox-img">
            <div
              :id="'personalData-' + index"
              style="width: 100%; height: 100%"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import * as echarts from "echarts";
import AlarmCenter from "@/api/AlarmCenter.json";
import { getUserInfo } from "@/api/aberrantEmotions";
export default {
  data() {
    return {
      useUserData: [],
      baseUrl: process.env.VUE_APP_BASE_API,
      options: [
        {
          value: "轻微告警",
          label: "轻微告警",
        },
        {
          value: "注意告警",
          label: "注意告警",
        },
        {
          value: "严重告警",
          label: "严重告警",
        },
        {
          value: "愤怒告警",
          label: "愤怒告警",
        },
      ],
      value: "",
      // userData: AlarmCenter,
      inputValue: "",
      userData: [
        {
          name: "张三", // 姓名
          tx: "http://121.37.224.213:12590/static/img/logo.bc5fe698.png", // 头像
          bh: 20241121, // 编号
          bj: "高一5班", // 班级
          jg: "愤怒告警", // 告警
          age: 18, // 年龄
          sex: "男", // 性别
          img: "http://121.37.224.213:9000/box-im/image/20241008/1728368668906.jpg", // 图片
          // 历史检测记录
          history: [
            {
              address: "教学楼", // 地址
              sj: "2024-11-18", // 时间
              qx: "愤怒", // 情绪
              score: 75, // 分数
            },
            {
              address: "图书馆", // 地址
              sj: "2024-11-18", // 时间
              qx: "喜悦", // 情绪
              score: 85, // 分数
            },
            {
              address: "校门口", // 地址
              sj: "2024-11-19", // 时间
              qx: "惊讶", // 情绪
              score: 70, // 分数
            },
            {
              address: "操场", // 地址
              sj: "2024-11-19", // 时间
              qx: "厌恶", // 情绪
              score: 60, // 分数
            },
            {
              address: "操场", // 地址
              sj: "2024-11-19", // 时间
              qx: "恐惧", // 情绪
              score: 55, // 分数
            },
            {
              address: "体育馆", // 地址
              sj: "2024-11-20", // 时间
              qx: "悲伤", // 情绪
              score: 50, // 分数
            },
            {
              address: "田径场", // 地址
              sj: "2024-11-20", // 时间
              qx: "藐视", // 情绪
              score: 65, // 分数
            },
            {
              address: "教学楼", // 地址
              sj: "2024-11-20", // 时间
              qx: "喜悦", // 情绪
              score: 90, // 分数
            },
            {
              address: "图书馆", // 地址
              sj: "2024-11-21", // 时间
              qx: "惊讶", // 情绪
              score: 80, // 分数
            },
            {
              address: "操场", // 地址
              sj: "2024-11-21", // 时间
              qx: "悲伤", // 情绪
              score: 40, // 分数
            },
            {
              address: "教学楼", // 地址
              sj: "2024-11-22", // 时间
              qx: "愤怒", // 情绪
              score: 20, // 分数
            },
            {
              address: "图书馆", // 地址
              sj: "2024-11-22", // 时间
              qx: "藐视", // 情绪
              score: 67, // 分数
            },
            {
              address: "校门口", // 地址
              sj: "2024-11-23", // 时间
              qx: "惊讶", // 情绪
              score: 45, // 分数
            },
            {
              address: "操场", // 地址
              sj: "2024-11-23", // 时间
              qx: "厌恶", // 情绪
              score: 80, // 分数
            },
            {
              address: "体育馆", // 地址
              sj: "2024-11-24", // 时间
              qx: "恐惧", // 情绪
              score: 56, // 分数
            },
            {
              address: "田径场", // 地址
              sj: "2024-11-24", // 时间
              qx: "悲伤", // 情绪
              score: 78, // 分数
            },
          ],
        },
        {
          name: "小妹", // 姓名
          tx: "http://121.37.224.213:12590/static/img/logo.bc5fe698.png", // 头像
          bh: 20241125, // 编号
          bj: "高一5班", // 班级
          jg: "愤怒告警", // 告警
          age: 19, // 年龄
          sex: "女", // 性别
          img: "http://121.37.224.213:9000/box-im/image/20241008/1728368668906.jpg", // 图片
          history: [
            {
              address: "教学楼",
              sj: "2024-11-18",
              qx: "愤怒",
              score: 75,
            },
            {
              address: "图书馆",
              sj: "2024-11-18",
              qx: "藐视",
              score: 55,
            },
            {
              address: "校门口",
              sj: "2024-11-18",
              qx: "惊讶",
              score: 60,
            },
            {
              address: "操场",
              sj: "2024-11-18",
              qx: "厌恶",
              score: 45,
            },
            {
              address: "体育馆",
              sj: "2024-11-18",
              qx: "恐惧",
              score: 80,
            },
            {
              address: "田径场",
              sj: "2024-11-18",
              qx: "悲伤",
              score: 30,
            },
            {
              address: "教学楼",
              sj: "2024-11-19",
              qx: "愤怒",
              score: 70,
            },
            {
              address: "图书馆",
              sj: "2024-11-19",
              qx: "藐视",
              score: 50,
            },
            {
              address: "校门口",
              sj: "2024-11-19",
              qx: "惊讶",
              score: 65,
            },
            {
              address: "操场",
              sj: "2024-11-19",
              qx: "厌恶",
              score: 40,
            },
            {
              address: "体育馆",
              sj: "2024-11-19",
              qx: "恐惧",
              score: 85,
            },
            {
              address: "田径场",
              sj: "2024-11-19",
              qx: "悲伤",
              score: 25,
            },
            {
              address: "教学楼",
              sj: "2024-11-20",
              qx: "愤怒",
              score: 78,
            },
            {
              address: "图书馆",
              sj: "2024-11-20",
              qx: "藐视",
              score: 58,
            },
            {
              address: "校门口",
              sj: "2024-11-20",
              qx: "惊讶",
              score: 62,
            },
            {
              address: "操场",
              sj: "2024-11-20",
              qx: "厌恶",
              score: 43,
            },
            {
              address: "体育馆",
              sj: "2024-11-20",
              qx: "恐惧",
              score: 82,
            },
            {
              address: "田径场",
              sj: "2024-11-20",
              qx: "悲伤",
              score: 31,
            },
            {
              address: "教学楼",
              sj: "2024-11-21",
              qx: "愤怒",
              score: 72,
            },
            {
              address: "图书馆",
              sj: "2024-11-21",
              qx: "藐视",
              score: 52,
            },
            {
              address: "校门口",
              sj: "2024-11-21",
              qx: "惊讶",
              score: 68,
            },
            {
              address: "操场",
              sj: "2024-11-21",
              qx: "厌恶",
              score: 47,
            },
            {
              address: "体育馆",
              sj: "2024-11-21",
              qx: "恐惧",
              score: 87,
            },
            {
              address: "田径场",
              sj: "2024-11-21",
              qx: "悲伤",
              score: 28,
            },
            {
              address: "教学楼",
              sj: "2024-11-22",
              qx: "愤怒",
              score: 76,
            },
            {
              address: "图书馆",
              sj: "2024-11-22",
              qx: "藐视",
              score: 54,
            },
            {
              address: "校门口",
              sj: "2024-11-22",
              qx: "惊讶",
              score: 63,
            },
            {
              address: "操场",
              sj: "2024-11-22",
              qx: "厌恶",
              score: 42,
            },
            {
              address: "体育馆",
              sj: "2024-11-22",
              qx: "恐惧",
              score: 81,
            },
            {
              address: "田径场",
              sj: "2024-11-22",
              qx: "悲伤",
              score: 29,
            },
            {
              address: "教学楼",
              sj: "2024-11-23",
              qx: "愤怒",
              score: 74,
            },
            {
              address: "图书馆",
              sj: "2024-11-23",
              qx: "藐视",
              score: 51,
            },
            {
              address: "校门口",
              sj: "2024-11-23",
              qx: "惊讶",
              score: 67,
            },
            {
              address: "操场",
              sj: "2024-11-23",
              qx: "厌恶",
              score: 46,
            },
            {
              address: "体育馆",
              sj: "2024-11-23",
              qx: "恐惧",
              score: 83,
            },
            {
              address: "田径场",
              sj: "2024-11-23",
              qx: "悲伤",
              score: 27,
            },
            {
              address: "教学楼",
              sj: "2024-11-24",
              qx: "愤怒",
              score: 79,
            },
            {
              address: "图书馆",
              sj: "2024-11-24",
              qx: "藐视",
              score: 53,
            },
            {
              address: "校门口",
              sj: "2024-11-24",
              qx: "惊讶",
              score: 61,
            },
            {
              address: "操场",
              sj: "2024-11-24",
              qx: "厌恶",
              score: 41,
            },
            {
              address: "体育馆",
              sj: "2024-11-24",
              qx: "恐惧",
              score: 84,
            },
            {
              address: "田径场",
              sj: "2024-11-24",
              qx: "悲伤",
              score: 26,
            },
          ],
        },
      ],
      charts: {
        unit: "次数",
        names: ["愤怒", "悲伤", "厌恶", "恐惧"],
        lineX: this.generateDateArray(),
        value: [
          // [9, 6, 3, 8, 5, 2, 2],
          // [1, 4, 1, 4, 7, 8, 5],
          // [8, 5, 2, 0, 1, 7, 4],
          // [7, 5, 3, 9, 5, 1, 4],
        ],
      },
      color: [
        "rgba(192,44,56",
        "rgba(169, 169, 169",
        "rgba(0, 100, 0",
        "rgba(0, 0, 139",
      ],
    };
  },
  mounted() {
    if (this.$store.state.app.sidebar.opened == true) {
      this.$store.dispatch("app/toggleSideBar");
    }
    this.generateDateArray();
    this.alertChart();

    this.$nextTick(() => {
      this.rankingChart(); // 确保 DOM 渲染完成后再执行
    });
    this.trendChart();
    this.generateRandomValues();
    // 确保index已正确传递
    this.renderCharts();
    this.getUserInfo();
    // this.useUserData = this.userData;
  },
  updated() {
    this.renderCharts();
  },

  methods: {
    handleEnter(event) {
      event.preventDefault(); // 阻止默认行为

      this.search();
    },
    //获取用户信息
    getUserInfo() {
      getUserInfo().then((res) => {
        this.userData = res.rows;
        this.userData.forEach((item) => {
          item.faceImage = this.baseUrl + item.faceImage;
        });

        this.useUserData = this.userData;
      });
    },
    generateDateArray() {
      const today = new Date();
      const lineX = [];
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        const day = date.getDate().toString().padStart(2, "0");
        lineX.push(`${month}-${day}`);
      }
      return lineX;
    },
    generateRandomArray(length, min, max) {
      const array = [];
      for (let i = 0; i < length; i++) {
        array.push(Math.floor(Math.random() * (max - min + 1)) + min);
      }
      return array;
    },
    // 为每个图生成随机数据
    generateRandomValues(length, min, max) {
      const data = [];
      for (let i = 0; i < length; i++) {
        data.push(Math.floor(Math.random() * (max - min + 1)) + min);
      }
      return data; // 返回一组随机数
    },
    // 告警统计echarts图
    alertChart() {
      let alertChart = echarts.init(document.getElementById("alert"));
      let startAngle = 180;
      let endAngle = 0;
      let min = 0;
      let max = 100;
      let radius = "100%";
      let pointer = { show: false }; // 是否显示指针
      let axisLine = {
        lineStyle: {
          width: 15,
          color: [[1, "#f4f4f4"]],
        },
      };
      let axisTick = { show: false };
      let splitLine = { show: false };
      let axisLabel = {
        distance: 5,
        color: "#666",
        fontSize: 10,
        formatter: function (value) {
          return;
        },
      };
      let anchor = {
        show: false,
        showAbove: false,
        size: 10,
        itemStyle: {
          borderWidth: 20,
        },
      };
      let title = {
        show: true,
        offsetCenter: [0, "33%"],
        fontSize: 14,
      };
      let detail = {
        valueAnimation: true,
        fontSize: 16,
        lineHeight: 0,
        color: "#106ae7",
        fontWeight: "bold",
        offsetCenter: [0, "-20%"],
        formatter: function (value) {
          return "\n" + value + "{a|%}";
        },
        rich: {
          a: {
            color: "#333",
            fontSize: 16,
            lineHeight: 10,
          },
        },
      };
      let option = {
        title: [
          {
            text: "总数{a|97}人",
            left: 170,
            top: 0,
            textStyle: {
              fontWeight: "bold",
              fontSize: "12",
              color: "#333",
              rich: {
                a: {
                  color: "#319fff",
                  fontSize: 16,
                  lineHeight: 10,
                  padding: [0, 10],
                },
              },
            },
          },
        ],
        grid: {
          left: "10%",
          right: "10%",
          top: 0,
          containLabel: true, // 确保标签不会溢出容器
        },
        series: [
          {
            type: "gauge",
            startAngle: startAngle,
            center: ["15%", "70%"],
            endAngle: endAngle,
            min: min,
            max: max,
            radius: radius,
            progress: {
              show: true,
              width: 15,
              itemStyle: {
                color: "#ff42a4",
              },
            },
            pointer: pointer,
            axisLine: axisLine,
            axisTick: axisTick,
            splitLine: splitLine,
            axisLabel: axisLabel,
            anchor: anchor,
            title: title,
            detail: detail,
            data: [
              {
                value: 27.8,
                name: "愤怒告警",
              },
            ],
          },
          {
            type: "gauge",
            startAngle: startAngle,
            center: ["50%", "70%"], // 中心调整
            radius: radius,
            endAngle: endAngle,
            min: min,
            max: max,
            progress: {
              show: true,
              width: 15,
              itemStyle: {
                color: "#1ac9f6",
              },
            },
            pointer: pointer,
            axisLine: axisLine,
            axisTick: axisTick,
            splitLine: splitLine,
            axisLabel: axisLabel,
            anchor: anchor,
            title: title,
            detail: detail,
            data: [
              {
                value: 53.4,
                name: "悲伤告警",
              },
            ],
          },
          {
            type: "gauge",
            startAngle: startAngle,
            center: ["85%", "70%"], // 中心调整
            radius: radius,
            endAngle: endAngle,
            min: min,
            max: max,
            progress: {
              show: true,
              width: 15,
              itemStyle: {
                color: "#12d891",
              },
            },
            pointer: pointer,
            axisLine: axisLine,
            axisTick: axisTick,
            splitLine: splitLine,
            axisLabel: axisLabel,
            anchor: anchor,
            title: title,
            detail: detail,
            data: [
              {
                value: 28.3,
                name: "综合告警",
              },
            ],
          },
        ],
      };

      // 监听窗口缩放事件，根据窗口宽度重新调整每个仪表盘的中心位置
      window.addEventListener("resize", () => {
        alertChart.resize();

        // 动态调整图表中心位置，避免重叠
        const chartWidth = document.getElementById("alert").offsetWidth;
        const centerPositions = [
          ["15%", "70%"],
          ["50%", "70%"],
          ["85%", "70%"],
        ];

        if (chartWidth < 1200) {
          centerPositions[0] = ["20%", "70%"];
          centerPositions[1] = ["50%", "70%"];
          centerPositions[2] = ["80%", "70%"];
        }

        alertChart.setOption({
          series: [
            {
              center: centerPositions[0],
            },
            {
              center: centerPositions[1],
            },
            {
              center: centerPositions[2],
            },
          ],
        });
      });

      alertChart.setOption(option);
    },

    //情绪异常告警排名echarts图
    rankingChart() {
      const rankingChart = echarts.init(document.getElementById("ranking"));
      let salvProName = [
        "校门口",
        "食堂",
        "教学楼",
        "田径场",
        "操场",
        "图书馆",
        "体育馆",
      ];
      let salvProValue = [5, 10, 30, 6, 24, 7, 17];
      let salvProMax = []; //背景按最大值
      for (let i = 0; i < salvProValue.length; i++) {
        salvProMax.push(salvProValue[0]);
      }
      let option = {
        // backgroundColor:"#003366",
        grid: {
          left: "2%",
          right: "2%",
          bottom: "2%",
          top: "2%",
          containLabel: true,
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "none",
          },
          formatter: function (params) {
            return params[0].name + " : " + params[0].value;
          },
        },
        xAxis: {
          show: false,
          type: "value",
        },
        yAxis: [
          {
            type: "category",
            inverse: true,
            axisLabel: {
              show: true,
              textStyle: {
                color: "#0a4c89",
              },
            },
            splitLine: {
              show: false,
            },
            axisTick: {
              show: false,
            },
            axisLine: {
              show: false,
            },
            data: salvProName,
          },
          {
            type: "category",
            inverse: true,
            axisTick: "none",
            axisLine: "none",
            show: true,
            axisLabel: {
              textStyle: {
                color: "#0a4c89",
                fontSize: "12",
              },
            },
            data: salvProValue,
          },
        ],
        series: [
          {
            name: "值",
            type: "bar",
            zlevel: 1,
            itemStyle: {
              normal: {
                borderRadius: 30,
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                  {
                    offset: 0,
                    color: "rgb(57,89,255,1)",
                  },
                  {
                    offset: 1,
                    color: "rgb(46,200,207,1)",
                  },
                ]),
              },
            },
            barWidth: 20,
            data: salvProValue,
          },
          {
            name: "背景",
            type: "bar",
            barWidth: 20,
            barGap: "-100%",
            data: salvProMax,
            itemStyle: {
              normal: {
                color: "rgba(24,31,68,1)",
                borderRadius: 30,
              },
            },
          },
        ],
      };
      window.addEventListener("resize", () => {
        rankingChart.resize();
      });
      rankingChart.setOption(option);
    },
    //近期告警趋势echarts图
    trendChart() {
      let trendChart = echarts.init(document.getElementById("trend"));
      let data_val = [7, 12, 16, 17, 6, 4, 35];
      let xAxis_val = this.generateDateArray();
      // let  data_val1 = [0, 0, 0, 0, 0, 0, 0];
      let option = {
        grid: {
          left: 10,
          top: "10%",
          bottom: 20,
          right: 20,
          containLabel: true,
        },
        tooltip: {
          show: true,
          borderColor: "rgb(26, 201, 246)",
          backgroundColor: "rgb(196, 211, 248)",
          //字体颜色
          textStyle: {
            color: "#000",
          },
          borderWidth: 1,
          formatter: "{b}:{c}",
          extraCssText: "box-shadow: 0 0 5px rgba(0, 0, 0, 1)",
        },

        xAxis: {
          data: xAxis_val,
          boundaryGap: false,
          axisLine: {
            show: true, //是否显示坐标轴轴线
          },
          axisLabel: {
            textStyle: {
              color: "#5c6076",
            },
          },
          axisTick: {
            show: false,
          },
        },
        yAxis: {
          ayisLine: {
            show: true, //是否显示坐标轴轴线
          },
          axisLabel: {
            textStyle: {
              color: "#5c6076",
            },
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: "#bbb",
              type: "dashed", // 设置为虚线
            },
          },
          axisLine: {
            lineStyle: {
              color: "#384157",
            },
          },
        },

        series: [
          {
            type: "bar",
            name: "linedemo",

            tooltip: {
              show: false,
            },
            animation: false,
            barWidth: 1.4,
            hoverAnimation: false,
            data: data_val,
            itemStyle: {
              normal: {
                color: "rgb(26, 201, 246)",
                opacity: 0.6,
                label: {
                  show: false, //是否显示数值
                },
              },
            },
          },
          // {
          //   type: "line",
          //   name: "距离",

          //   animation: false,
          //   symbol: "circle",

          //   hoverAnimation: false,
          //   data: data_val1,
          //   itemStyle: {
          //     normal: {
          //       color: "#00ff00", // 修改为绿色
          //       opacity: 0,
          //     },
          //   },
          //   lineStyle: {
          //     normal: {
          //       width: 1,
          //       color: "#000", // 修改为绿色
          //       opacity: 1,
          //     },
          //   },
          // },
          {
            type: "line",
            name: "linedemo",
            smooth: true,
            symbolSize: 10,
            animation: false,
            lineWidth: 1.2,
            hoverAnimation: false,
            data: data_val,
            symbol: "circle",
            itemStyle: {
              normal: {
                color: "rgb(26, 201, 246)", // 修改为蓝色
                shadowBlur: 40,
                label: {
                  show: true,
                  position: "top",
                  textStyle: {
                    color: "rgb(26, 201, 246)", // 修改为蓝色
                  },
                },
              },
            },
            areaStyle: {
              normal: {
                color: "#0000ff", // 修改为蓝色
                opacity: 0.08,
              },
            },
          },
        ],
      };
      window.addEventListener("resize", () => {
        trendChart.resize();
      });
      trendChart.setOption(option);
    },
    //个人情绪次数统计echarts图
    renderCharts() {
      this.$nextTick(() => {
        this.useUserData.forEach((item, index) => {
          const chartElement = document.getElementById(`personalData-${index}`);
          const myChart = echarts.init(chartElement); // 初始化图表实例

          const lineY = [];
          // 为每个图表分配独立数据
          for (let i = 0; i < this.charts.names.length; i++) {
            const x = i < this.color.length ? i : this.color.length - 1;

            const randomData = this.generateRandomValues(7, 0, 10); // 为每条线生成独立数据

            const data = {
              name: this.charts.names[i],
              type: "line",
              color: this.color[x] + ")",
              smooth: true,
              areaStyle: {
                normal: {
                  color: new echarts.graphic.LinearGradient(
                    0,
                    0,
                    0,
                    1,
                    [
                      { offset: 0, color: this.color[x] + ", 0.3)" },
                      { offset: 0.8, color: this.color[x] + ", 0)" },
                    ],
                    false
                  ),
                  shadowColor: "rgba(0, 0, 0, 0.1)",
                  shadowBlur: 10,
                },
              },
              symbol: "circle",
              symbolSize: 5,
              data: randomData, // 确保每条线的随机数据不同
            };
            lineY.push(data);
          }

          const option = {
            tooltip: { trigger: "axis" },
            legend: {
              data: this.charts.names,
              textStyle: { fontSize: 12, color: "rgb(0,253,255,0.6)" },
              right: "4%",
            },
            grid: {
              top: "14%",
              left: "10px",
              right: "10px",
              bottom: "12%",
              containLabel: true,
            },
            xAxis: {
              type: "category",
              boundaryGap: false,
              data: this.charts.lineX,
              axisLabel: {
                textStyle: { color: "rgb(0,253,255,0.6)" },
                formatter: (params) => params.split(" ")[0],
              },
            },
            yAxis: {
              name: this.charts.unit,
              type: "value",
              axisLabel: {
                formatter: "{value}",
                textStyle: { color: "rgb(0,253,255,0.6)" },
              },
              splitLine: { lineStyle: { color: "rgb(23,255,243,0.3)" } },
              axisLine: { lineStyle: { color: "rgb(0,253,255,0.6)" } },
            },
            series: lineY,
          };
          window.addEventListener("resize", () => {
            myChart.resize();
          });
          window.addEventListener("resize", () => {
            myChart.resize(); // 使用 myChart 而不是 renderCharts
          });
          myChart.setOption(option);
        });
      });
    },
    //跳转到人员详情/management
    // toManagement(item) {
    //   console.log(item);
    //   // this.$router.push("/management");
    //   this.$router.push({
    //     path: "/management",
    //     query: { value: item },
    //   });
    // },
    search() {
      // 查询全部数据
      if (this.inputValue.trim() == "") {
        this.userData = this.useUserData;
        return;
      }

      //  名称不为空
      if (this.inputValue != "" && this.value == "") {
        this.userData = [
          ...this.useUserData.filter((item) =>
            item.userName.includes(this.inputValue)
          ),
        ];
        return;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.main {
  #alert {
    width: 100%;
    height: 100%;
  }

  #ranking {
    width: 100%;
    height: 100%;
  }

  #trend {
    width: 100%;
    height: 100%;
  }

  /* width: 100vw; */
  height: calc(-40px + 100vh);
  margin-left: 20px;
  margin-top: 20px;
  margin-right: 20px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;

  .leftBox {
    width: calc(70% - 20px);
    height: 100%;
    // background-color: red;
    margin-left: 20px;
    border-radius: 15px;

    .searchBox {
      width: 100%;
      height: 50px;
      display: flex;
      align-items: center;
      // background-color: blanchedalmond;
      position: relative;

      .box {
        display: flex;
        align-items: center;
      }
    }

    .tableBox {
      width: 100%;
      height: calc(100% - 50px);
      border-radius: 10px;
      overflow: auto;
      display: flex;
      padding-top: 10px;
      border: 1px solid #9dd0fe;
      scrollbar-width: none;
      /* Firefox */
      -ms-overflow-style: none;
      /* IE 10+ */
      //隐藏滚动条

      /* flex-direction: row; */
      flex-wrap: wrap;

      .tableBox-mini {
        width: calc(33% - 10px);
        height: calc(50% - 10px);
        display: flex;
        flex-direction: column;
        margin-left: 10px;
        margin-bottom: 10px;
        background-color: #ecf5ff;
        border: 1px solid #9dd0fe;

        border-radius: 10px;

        .tableBox-user {
          display: flex;
          width: 100%;
          height: 50%;
          align-items: center;

          .tableBox-userBox {
            width: 50%;
            /* height: 80%; */
            padding: 10px;

            .tableBox-user-imgBox {
              width: 100%;
              height: 100%;
              padding: 15px;

              img {
                width: 90%;
                height: 100%;
                padding: 10px;
                //等比缩放
                object-fit: cover;
              }
            }
          }
        }

        .tableBox-img {
          display: flex;
          width: 100%;
          height: 50%;
          #personalData {
            width: 100%;
            height: 100%;
          }
        }
      }

      .user-Information {
        display: flex;
        flex-direction: column;
        // padding-left: 14px;
        font-size: 14px;
        color: #a4a7ac;
        width: 50%;

        div {
          width: 100%;
          line-height: 200%;
        }
      }
    }
  }
}

.rightBox {
  width: 30%;
  height: 100%;
  border-radius: 15px;

  .section {
    width: 100%;
    background-color: #d6e7fa;
    border-radius: 10px;
    border: #9dd0fe 2px solid;

    &.section-small {
      height: calc(20% - 10px);
      margin-bottom: 10px;
    }

    &.section-large {
      height: calc(40% - 5px);
    }

    &.section-last {
      margin-top: 10px;
    }

    .section-header {
      width: 100%;
      height: 40px;
      background: linear-gradient(
        to bottom right,
        rgba(170, 213, 244),
        rgba(213, 231, 250)
      );
      color: #094b88;
      display: flex;
      align-items: center;
      padding-left: 5px;
      font-weight: bold;
      border-radius: 5px 5px 0 0;
    }

    .section-body {
      flex: 1;
      width: 100%;
      height: calc(100% - 40px);
    }
  }
}

::v-deep .el-input--small .el-input__inner {
  height: 25px;
  line-height: 25px;
}

::v-deep.el-select {
  width: 150px;
  margin-top: 11px;
  position: absolute;
  top: 0;
  right: 85px;
}

::v-deep .el-input--medium .el-input__inner {
  height: 25px;
  line-height: 25px;
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
  background: #409efe;
  color: #fff;
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
</style>
