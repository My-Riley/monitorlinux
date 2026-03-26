<template>
  <div class="app-container">
    <div class="chart-content">
      <div class="chart-left">
        <div id="overall" v-loading="loadingOverall"></div>
      </div>
      <div class="chart-right">
        <div class="trend">
          <div class="search-container">
            <el-form
              :model="queryParamsTrend"
              ref="queryFormTrend"
              size="small"
              :inline="true"
              v-show="showSearch"
              label-width="68px"
              style="margin-left: -10px; margin-top: 30px;"
            >
              <el-form-item label="日期 ">
                <el-date-picker
                  v-model="dateRangeTrend"
                  style="width: 240px"
                  value-format="yyyy-MM-dd HH:mm:ss"
                  type="daterange"
                  range-separator="-"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  :default-time="['00:00:00', '23:59:59']"
                ></el-date-picker>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  icon="el-icon-search"
                  size="mini"
                  @click="handleQuery('Trend')"
                >搜索</el-button>
                <el-button
                  icon="el-icon-refresh"
                  size="mini"
                  @click="resetQuery('Trend')"
                >重置</el-button>
              </el-form-item>
            </el-form>
          </div>
          <div id="trend" v-loading="loadingTrend"></div>
        </div>
        <div class="mood">
          <div class="search-container">
            <el-form
              :model="queryParamsMood"
              ref="queryFormMood"
              size="small"
              :inline="true"
              v-show="showSearch"
              label-width="68px"
              style="margin-left: -10px; margin-top: 30px;"
            >
              <el-form-item label="日期 ">
                <el-date-picker
                  v-model="dateRangeMood"
                  style="width: 240px"
                  value-format="yyyy-MM-dd HH:mm:ss"
                  type="daterange"
                  range-separator="-"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  :default-time="['00:00:00', '23:59:59']"
                ></el-date-picker>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  icon="el-icon-search"
                  size="mini"
                  @click="handleQuery('Mood')"
                >搜索</el-button>
                <el-button
                  icon="el-icon-refresh"
                  size="mini"
                  @click="resetQuery('Mood')"
                >重置</el-button>
              </el-form-item>
            </el-form>
          </div>
          <div id="mood" v-loading="loadingMood"></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import * as echarts from "echarts";
import request from "@/utils/request";
import { getOverallTrend } from '@/api/index';
import websocketMixin from "@/utils/mixins/websocketMixin";

export default {
  mixins: [websocketMixin],
  data() {
    return {
      showSearch: true,
      // 加载状态
      loadingOverall: false,
      loadingTrend: false,
      loadingMood: false,
      searchForm: { studentId: '' },
      // 左侧趋势图的查询参数和日期范围
      dateRangeTrend: [],
      queryParamsTrend: {},
      // 右侧情绪图的查询参数和日期范围
      dateRangeMood: [],
      queryParamsMood: {},
      // 图表数据
      overallData: null,
      trendData: null,
      moodData: null,
      // 图表实例
      overallChart: null,
      trendChart: null,
      moodChartInstance: null,
    };
  },
  mounted() {
    const isOpened = this.$store.state.app.sidebar.opened;
    if (isOpened) {
      this.$store.dispatch("app/toggleSideBar");
    }
    this.initCharts();
    this.loadAllData();
  },
  beforeDestroy() {
    if (this.overallChart) this.overallChart.dispose();
    if (this.trendChart) this.trendChart.dispose();
    if (this.moodChartInstance) this.moodChartInstance.dispose();
    window.removeEventListener("resize", this.handleResize);
  },
  methods: {
    initCharts() {
      this.overallChart = echarts.init(document.getElementById("overall"));
      this.trendChart = echarts.init(document.getElementById("trend"));
      this.moodChartInstance = echarts.init(document.getElementById("mood"));
      window.addEventListener("resize", this.handleResize);
    },
    handleResize() {
      if (this.overallChart) this.overallChart.resize();
      if (this.trendChart) this.trendChart.resize();
      if (this.moodChartInstance) this.moodChartInstance.resize();
    },
    async loadAllData() {
      await Promise.all([
        this.loadOverallData(),
        this.loadTrendData(),
        this.loadMoodData(),
      ]);
    },
    // 加载总体趋势图数据
    async loadOverallData() {
      this.loadingOverall = true;
      try {
        const studentId = this.searchForm?.studentId?.trim() || '';
        const params = studentId ? { studentId } : {};
        const res = await getOverallTrend(params);
        if (res.code === 200 && res.data) {
          this.overallData = res.data;
          this.renderOverallChart();
        }
      } catch (error) {
        console.error("获取总体趋势数据失败:", error);
        this.$message.error("获取总体趋势数据失败");
      } finally {
        this.loadingOverall = false;
      }
    },
    // 加载焦虑趋势饼图数据
    async loadTrendData(params = {}) {
      this.loadingTrend = true;
      try {
        const res = await request({
          url: "/system/results/dashboard/trend",
          method: "get",
          params,
        });
        if (res.code === 200 && res.data) {
          this.trendData = res.data;
          this.renderTrendChart();
        }
      } catch (error) {
        console.error("获取焦虑趋势数据失败:", error);
        this.$message.error("获取焦虑趋势数据失败");
      } finally {
        this.loadingTrend = false;
      }
    },
    // 加载情绪分布饼图数据
    async loadMoodData(params = {}) {
      this.loadingMood = true;
      try {
        const res = await request({
          url: "/system/results/dashboard/mood",
          method: "get",
          params,
        });
        if (res.code === 200 && res.data) {
          this.moodData = res.data;
          this.renderMoodChart();
        }
      } catch (error) {
        console.error("获取情绪分布数据失败:", error);
        this.$message.error("获取情绪分布数据失败");
      } finally {
        this.loadingMood = false;
      }
    },
    // 统一查询处理
    handleQuery(type) {
      const dateRange = this[`dateRange${type}`];
      if (!dateRange || dateRange.length !== 2) {
        this.$message.warning("请选择日期范围");
        return;
      }
      const params = {
        beginTime: dateRange[0],
        endTime: dateRange[1],
      };
      if (type === 'Trend') {
        this.loadTrendData(params);
      } else {
        this.loadMoodData(params);
      }
    },
    // 统一重置处理
    resetQuery(type) {
      this[`dateRange${type}`] = [];
      if (type === 'Trend') {
        this.loadTrendData();
      } else {
        this.loadMoodData();
      }
    },
    // 渲染总体趋势图
    renderOverallChart() {
      if (!this.overallData) return;
      const { dates, noAnxiety, lowAnxiety, midAnxiety, highAnxiety } = this.overallData;
      
      // 计算每日总数及高度焦虑占比
      const totalData = [];
      const highAnxietyRate = [];
      
      dates.forEach((_, index) => {
        const total = (noAnxiety[index] || 0) + 
                      (lowAnxiety[index] || 0) + 
                      (midAnxiety[index] || 0) + 
                      (highAnxiety[index] || 0);
        totalData.push(total);
        
        // 计算高度焦虑占比 (保留1位小数)
        const rate = total > 0 ? ((highAnxiety[index] || 0) / total * 100).toFixed(1) : 0;
        highAnxietyRate.push(rate);
      });

      // 优化：使用堆叠柱状图 (stack: 'total')，可以更直观地看到每天的总量及各焦虑等级的占比
      const baseBarConfig = { 
        type: "bar", 
        barWidth: 30, 
        stack: 'total',
        // 统一设置圆角，但只在每根柱子的最后一段显示顶部圆角
        // 这里通过在 itemStyle 中动态计算来实现比较复杂
        // 简单的方案是只给堆叠的最后一段（通常是高度焦虑）加圆角
        // 但由于数据可能为0，所以最好统一加小圆角或者全加
        // 尝试给所有段加微小圆角，看起来更柔和
        itemStyle: {
          borderRadius: [4, 4, 4, 4], // 全圆角
          borderColor: '#fff', // 增加白色描边区分堆叠层
          borderWidth: 1
        }
      };
      const option = {
        title: {
          text: "最近七天焦虑状态趋势图",
          left: "30",
          top: 20,
          textStyle: { fontSize: 18, fontWeight: "bold", color: "#333" },
        },
        color: ["#00cc99", "#ffcc66", "#6666ff", "#ff4d4d", "#ff4d4d"], // 最后红色给折线
        tooltip: { 
          trigger: "axis", 
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#eee',
          borderWidth: 1,
          textStyle: { color: '#333' },
          extraCssText: 'box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);',
          axisPointer: { type: "shadow" },
          formatter: function(params) {
            let res = '<div style="font-weight:bold;margin-bottom:5px;">' + params[0].name + '</div>';
            params.forEach(item => {
              if (item.seriesName === '总数') return; // 跳过总数辅助柱
              let value = item.value;
              if (item.seriesName === '高度焦虑占比') {
                value += '%';
              }
              res += '<div style="display:flex;justify-content:space-between;min-width:150px;">' +
                     '<span>' + item.marker + item.seriesName + '</span>' +
                     '<span style="font-weight:bold;">' + value + '</span>' +
                     '</div>';
            });
            return res;
          }
        },
        legend: {
          itemWidth: 32, itemHeight: 14, itemGap: 20,
          left: "center", top: "50",
          data: [
            { name: "无焦虑", icon: "circle" },
            { name: "低度焦虑", icon: "circle" },
            { name: "中度焦虑", icon: "circle" },
            { name: "高度焦虑", icon: "circle" },
            { name: "高度焦虑占比" } // 不指定 icon，默认使用 series 的图例样式（折线+点）
          ],
          textStyle: { color: '#666' }
        },
        grid: { left: "40", right: "60", bottom: "50", top: "100", containLabel: true },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            show: false,
            type: 'slider',
            bottom: 10,
            height: 20,
            start: 0,
            end: 100
          }
        ],
        xAxis: [{
          name: "日期", nameGap: 5,
          splitLine: { show: false }, splitArea: { show: false },
          axisLine: { show: true, lineStyle: { color: "#979797", width: 0.6 } },
          axisTick: { show: false },
          axisLabel: { color: "#393C40", rotate: -10, interval: 'auto' },
          data: dates,
        }],
        yAxis: [
          {
            type: 'value',
            name: "数量", nameGap: 10,
            splitLine: { show: true, lineStyle: { type: 'dashed' } }, splitArea: { show: false },
            axisLine: { show: true, lineStyle: { color: "#979797", width: 0.6 } },
            axisTick: { show: false },
            axisLabel: { color: "#393C40" },
          },
          {
            type: 'value',
            name: "占比",
            min: 0,
            max: 100,
            interval: 20,
            axisLabel: { 
              formatter: function(value) {
                return value === 0 ? '' : value + ' %';
              }, 
              color: "#393C40" 
            },
            splitLine: { show: false },
            axisLine: { show: false }, // 隐藏右侧轴线保持简洁
            axisTick: { show: false }
          }
        ],
        series: [
          { ...baseBarConfig, name: "无焦虑", data: noAnxiety },
          { ...baseBarConfig, name: "低度焦虑", data: lowAnxiety },
          { ...baseBarConfig, name: "中度焦虑", data: midAnxiety },
          { ...baseBarConfig, name: "高度焦虑", data: highAnxiety },
          {
            name: "高度焦虑占比",
            type: "line",
            yAxisIndex: 1, // 使用右侧 Y 轴
            data: highAnxietyRate,
            symbol: "emptyCircle", // 空心圆
            symbolSize: 8,
            itemStyle: {
              color: "#ff4d4d", // 与高度焦虑同色
              borderWidth: 2,
            },
            lineStyle: {
              width: 2,
              type: "solid" // 实线
            },
            label: {
              show: true,
              position: 'top',
              formatter: '{c}%',
              color: '#333',
              fontWeight: 'bold'
            }
          },
          {
            name: "总数",
            type: "bar",
            data: totalData,
            barWidth: 30,
            barGap: "-100%",
            z: -10,
            itemStyle: {
              color: "rgba(0,0,0,0)"
            },
            label: {
              show: true,
              position: "top",
              color: "#333",
              fontSize: 12,
              fontWeight: "bold",
              formatter: "{c}"
            },
            tooltip: { show: false } // 不在 tooltip 中显示，避免重复或混淆
          }
        ],
      };
      this.overallChart.setOption(option);
    },
    // 渲染焦虑趋势饼图
    renderTrendChart() {
      if (!this.trendData) return;
      const { data, total } = this.trendData;
      const colors = ["#457244", "#00cc99", "#ffcc66", "#ff4d4d"];
      const m2R2Data = data.map((item, index) => ({
        ...item,
        itemStyle: { color: colors[index] },
      }));

      // 保存数据到实例，供 tooltip 使用
      this.currentTrendData = m2R2Data;

      const option = {
        title: [{
          text: "总体焦虑状态统计",
          left: "7%",
          top: "7%",
          textStyle: { fontSize: 16, color: "black" },
        },
        {
          text: total + "",
          subtext: "总次数",
          x: "39.5%", y: "45%",
          textAlign: "center",
          textStyle: { fontSize: 28, fontWeight: "bold", color: "#333" },
          subtextStyle: { fontSize: 16, color: "#666" },
        }],
        tooltip: {
          trigger: "item",
          formatter: (params) => {
            // 通过 chart 实例获取 legend 选中状态
            const chart = this.trendChart;
            if (!chart) return '';

            const legendSelected = chart.getOption().legend[0].selected || {};
            let visibleTotal = 0;

            // 计算当前可见项的总和
            this.currentTrendData.forEach(item => {
              const isSelected = legendSelected[item.name] !== false; // 默认 true
              if (isSelected) {
                visibleTotal += item.value;
              }
            });

            const percent = visibleTotal > 0
              ? (params.value / visibleTotal * 100).toFixed(2)
              : 0;

            return `${params.name}<br/>次数：${params.value}<br/>占比：${percent}%`;
          }
        },
        legend: {
          right: "5%", top: "center", orient: "vertical",
          textStyle: { color: "#333" },
          formatter: (name) => {
            const item = m2R2Data.find(d => d.name === name);
            return item ? `${name} | ${item.value}次` : '';
          }
        },
        series: [{
          name: "焦虑类型",
          type: "pie",
          radius: ["40%", "65%"],
          center: ["40%", "50%"],
          data: m2R2Data,
          label: { show: false },
          labelLine: { show: false },
          itemStyle: {
            borderRadius: 5,
            borderColor: '#fff',
            borderWidth: 2
          }
        }],
      };

      this.trendChart.setOption(option);
    },
    // 渲染情绪分布饼图
    renderMoodChart() {
      if (!this.moodData) return;

      const emotionMap = {
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

      // 处理数据，将英文情绪转换为中文
      const processedData = this.moodData.data.map(item => {
        let name = item.name;
        if (typeof name === 'string') {
          const key = name.trim().toLowerCase();
          if (emotionMap[key]) {
            name = emotionMap[key];
          }
        }
        return { ...item, name };
      });

      // 自动分配颜色
      const colors = this.generateDistinctColors(processedData.length);

      // 保存数据到实例，供 tooltip 使用
      this.currentMoodData = processedData;

      const option = {
        title: [{
          text: "总体情绪统计",
          textStyle: { fontSize: 16, color: "black" },
          left: "7%", top: "10%",
        }],
        tooltip: {
          trigger: "item",
          formatter: (params) => {
            // 获取图表实例
            const chart = this.moodChartInstance;
            if (!chart) return '';

            // 获取 legend 的选中状态
            const legendOption = chart.getOption().legend[0];
            const legendSelected = legendOption.selected || {};

            let visibleTotal = 0;

            // 计算当前可见项的总和
            this.currentMoodData.forEach(item => {
              const isSelected = legendSelected[item.name] !== false; // 默认 true
              if (isSelected) {
                visibleTotal += item.value;
              }
            });

            // 如果没有可见的数据项，则避免除以零
            const percent = visibleTotal > 0
              ? (params.value / visibleTotal * 100).toFixed(2)
              : 0;

            return `${params.name}<br/>数量：${params.value}<br/>占比：${percent}%`;
          }
        },
        color: colors,
        legend: {
          type: "scroll",
          orient: "vertical",
          left: "75%",
          align: "left",
          bottom: "80",
          textStyle: { color: "#8C8C8C" },
          height: 250,
          formatter: (name) => {
            const item = processedData.find(d => d.name === name);
            return `${name} (${item?.value || 0})`;
          }
        },
        series: [{
          name: "情绪",
          type: "pie",
          radius: [20, 100], // 玫瑰图半径
          center: ["45%", "55%"],
          roseType: 'radius', // 启用南丁格尔玫瑰图
          itemStyle: {
            borderRadius: 5
          },
          data: processedData,
          label: { show: false },
          labelLine: { show: false },
        }]
      };

      this.moodChartInstance.setOption(option);
    },

    // 辅助函数：生成足够多的颜色
    generateDistinctColors(count) {
      if (count <= 0) return [];
      const colors = [];
      const hueStep = 360 / Math.max(count, 8); // 至少8色避免太相近
      for (let i = 0; i < count; i++) {
        // 使用 HSL 生成鲜艳且区分度高的颜色
        colors.push(`hsl(${i * hueStep}, 70%, 55%)`);
      }
      return colors;
    },
    // 处理WebSocket更新通知
    handleWebSocketUpdate() {
      this.loadAllData();
    },
  },
};
</script>
<style lang="scss" scoped>
.app-container {
  padding: 10px !important;
  height: 100vh;
  width: 100vw;

  .chart-content {
    display: flex;
    height: 100%;

    .chart-left {
      width: calc(60% - 20px);
      height: 100%;
      margin-right: 20px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
      border-radius: 10px;
      display: flex;
      #overall {
        width: 100%;
        height: 100%;
      }
    }
    .chart-right {
      width: 40%;
      height: 100%;
      .search-container {
        width: 100%;
        height: 30px;
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 15px;
        margin-bottom: 10px;
      }
      .trend {
        height: 50%;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
        margin-right: 60px;
        border-radius: 10px;
      }
      #trend {
        width: 100%;
        height: 100%;
      }
      .mood {
        height: calc(50% - 10px);
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
        margin-right: 60px;
        margin-top: 10px;
        border-radius: 10px;
      }
      #mood {
        width: 100%;
        height: 100%;
      }
    }
  }
}
</style>
