<template>
  <div
    style="
      height: calc(-40px + 100vh);
      margin-left: 20px;
      margin-top: 20px;
      width: 100%;
      background: linear-gradient(
        to bottom right,
        rgba(213, 231, 250),
        rgba(170, 213, 244)
      );
    "
    v-hasPermi="['homePage:message:list']"
  >
    <div class="main">
      <div class="currentDevice">
        <div class="currentDeviceText">
          <div class="currentDeviceTextTop">
            <div
              style="width: 100%; line-height: 220%; margin-left: 10px"
              class="title"
            >
              <i v-if="cameraSelectValue" style="font-size: 1vw">{{ cameraSelectValue }} 摄像头</i>
              <i v-else style="font-size: 1vw">全部摄像头</i>
              <el-select
                v-model="cameraSelectValue"
                placeholder="选择"
                style="margin-left: 5%; width: 30%"
                size="mini"
              >
                <el-option
                  v-for="item in cameraOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                </el-option>
              </el-select>
            </div>
            <span
              style="
                width: 100%;
                text-align: right;
                line-height: 200%;
                margin-right: 10px;
              "
            ><i style="font-size: 1vw;">累计监测人数：58 人</i></span>
          </div>
          <div class="currentDeviceTextBottom">
            <span style="margin-right: 15px; margin-left: 10px"><b style="font-size: 1vw;">通道监测总人数:{{
              studentTop.length || 0 }}人</b></span>
            <span><b style="font-size: 1vw;">今日检测人数{{ studentTop.length || 0 }}人</b></span>
          </div>
        </div>
        <!-- 显示区域 -->
        <!-- <vue-seamless-scroll :data="student2" class="seamless-warp2" :class-option="classOption2"> -->

        <div class="currentDeviceMessage">
          <div v-for="(item, index) in cameraData" :key="index"
               style="width: calc(50% - 10px);margin-left: 10px;margin-bottom: 10px;border: solid 1px #5cacf5; border-radius: 5px;"
          >
            <CardComponent :student="item" />
          </div>
        </div>

      </div>
      <!-- 摄像头 start -->

      <div class="frames">
        <cameraBox :cameraList="currentCameraInfo" />

      </div>

      <!-- 摄像头 end-->

    </div>
    <div class="framesButtom">
      <div class="framesButtomText">
        <i style="margin-left: 10px"><b>最近监测</b></i>
      </div>
      <!-- 底部 -->
      <div class="framesButtomContent">
        <vue-seamless-scroll ref="seamlessScroll" :data="studentTop" class="seamless-warp"
                             :class-option="classOptionBottom"
        >
          <div class="bottom_box">
            <!-- 中间内容 -->
            <div v-for="(item, index) in studentTop" :key="index" style="border: solid 1px #5cacf5;">
              <CardComponent :student="item" />
            </div>
          </div>
        </vue-seamless-scroll>
      </div>
    </div>
  </div>
</template>

<script>
import CardComponent from "@/components/Card/CardComponent.vue";
// 引入摄像头
import { WebVideo } from "@/views/cellManagement/camera/webVideo.js";
import camera from "@/views/cellManagement/camera/camera.vue";
import cameraBox from "@/views/cellManagement/camera/cameraDiv.vue";
import { getStudentData } from "@/api/student/singleStudent.js";

export default {
  components: {
    CardComponent,
    camera,
    cameraBox,
  },
  data() {
    return {
      scoreList: [21, 65, 89, 78, 45, 34, 78, 45, 78, 45, 89, 87,43,56,22,90,76,34,55, 88,67],
      emoNumList: [0, 1, 3, 2, 5, 4, 3, 6, 0, 2, 4, 6, 5, 4, 1, 3, 3, 2, 5, 3, 4, 2, 3, 0, 5, 3, 0, 2, 4],
      dataList: [
        "2024-11-18 08:23:45",
        "2024-11-19 14:59:01",
        "2024-11-20 06:34:22",
        "2024-11-21 19:47:33",
        "2024-11-22 11:05:58",
        "2024-11-23 16:20:49",
        "2024-11-24 09:15:30",
        "2024-11-18 21:37:12",
        "2024-11-19 07:02:46",
        "2024-11-20 12:48:59",
        "2024-11-21 18:31:04",
        "2024-11-22 13:27:56",
        "2024-11-23 02:19:38",
        "2024-11-24 17:08:25",
        "2024-11-18 15:09:32",
        "2024-11-19 22:45:07",
        "2024-11-20 03:51:14",
        "2024-11-21 10:36:28",
        "2024-11-22 05:22:41",
        "2024-11-23 20:11:59",
        "2024-11-24 14:43:06"
      ],
      baseUrl: process.env.VUE_APP_BASE_API, // 基础地址
      // 摄像头数据 start
      cameraOptions: [
        {
          value: 1,
          label: '1号'
        }],
      cameraSelectValue: 1, // 选择的摄像头
      WebVideo: "",
      currentCameraInfo: [],
      row: {
        cameraId: "cameraId189",
        ipAddr: "192.168.1.89",
        username: "admin",
        password: "lanbu@2024",
        port: "80",
        status: "0",
        createBy: null,
        createTime: "2024-03-12 17:46:52",
        del: null,
        regionId: "111",
        id: "12345678-338d-4a47-b13d-f84967f4b9d5",
        cameraName: "一单元一栋101号",
        remark: null,
        updateBy: null,
        updateTime: "2024-06-06 15:40:38",
      },
      // 摄像头数据 end

      scrollStep: 400, // 每次滚动的像素
      isLeftDisabled: true, // 禁用左箭头的状态
      isRightDisabled: false, // 禁用右箭头的状态
      studentBottom: [
        {
          name: "及你太美阿阿萨阿萨威威萨方法",
          img: require("@/assets/images/card/1.png"),
          gender: "男",
          score: 98,
          studentId: "C0020",
          className: "初一3班",
          count: "232",
          emoNum: 6,
          camera: 4,
          createTime: "2024-01-13 11:34:33",
        },
        {
          name: "小华",
          img: require("@/assets/images/card/3.png"),
          gender: "女",
          score: 92,
          studentId: "C0018",
          className: "初一2班",
          count: "245",
          emoNum: 5,
          camera: 3,
          createTime: "2024-01-11 14:32:11",
        },
        {
          name: "小丽",
          img: require("@/assets/images/card/2.png"),
          gender: "女",
          score: 88,
          studentId: "C0022",
          className: "初二2班",
          count: "200",
          emoNum: 4,
          camera: 1,
          createTime: "2024-01-10 10:15:55",
        },
        {
          name: "小丽",
          img: require("@/assets/images/card/2.png"),
          gender: "女",
          score: 88,
          studentId: "C0022",
          className: "初二2班",
          count: "200",
          emoNum: 4,
          camera: 1,
          createTime: "2024-01-10 10:15:55",
        },
        {
          name: "小丽",
          img: require("@/assets/images/card/2.png"),
          gender: "女",
          score: 88,
          studentId: "C0022",
          className: "初二2班",
          count: "200",
          emoNum: 4,
          camera: 1,
          createTime: "2024-01-10 10:15:55",
        },
        {
          name: "小丽",
          img: require("@/assets/images/card/2.png"),
          gender: "女",
          score: 88,
          studentId: "C0022",
          className: "初二2班",
          count: "200",
          emoNum: 4,
          camera: 1,
          createTime: "2024-01-10 10:15:55",
        },
        {
          name: "小丽",
          img: require("@/assets/images/card/2.png"),
          gender: "女",
          score: 88,
          studentId: "C0022",
          className: "初二2班",
          count: "200",
          emoNum: 4,
          camera: 1,
          createTime: "2024-01-10 10:15:55",
        },
      ],
      studentTop: [],
      // studentTop: [
      //   {
      //     name: "李华",
      //     img: require("@/assets/images/card/2.png"),
      //     gender: "男",
      //     score: 87,
      //     id: "C0011",
      //     className: "初一1班",
      //     count: "120",
      //     emoNum: 5,
      //     camera: 2,
      //     timestamp: "2024-01-13 09:24:10"
      //   },
      //   {
      //     name: "王小明",
      //     img: require("@/assets/images/card/3.png"),
      //     gender: "女",
      //     score: 92,
      //     id: "C0012",
      //     className: "初二2班",
      //     count: "145",
      //     emoNum: 7,
      //     camera: 3,
      //     timestamp: "2024-01-12 10:15:20"
      //   },
      //   {
      //     name: "赵丽",
      //     img: require("@/assets/images/card/4.png"),
      //     gender: "女",
      //     score: 78,
      //     id: "C0013",
      //     className: "初三5班",
      //     count: "134",
      //     emoNum: 3,
      //     camera: 1,
      //     timestamp: "2024-01-14 11:20:30"
      //   },
      //   {
      //     name: "钱多多",
      //     img: require("@/assets/images/card/5.png"),
      //     gender: "男",
      //     score: 95,
      //     id: "C0014",
      //     className: "初二4班",
      //     count: "90",
      //     emoNum: 8,
      //     camera: 2,
      //     timestamp: "2024-01-13 12:30:45"
      //   },
      //   {
      //     name: "孙大圣",
      //     img: require("@/assets/images/card/6.png"),
      //     gender: "男",
      //     score: 85,
      //     id: "C0015",
      //     className: "初一2班",
      //     count: "150",
      //     emoNum: 4,
      //     camera: 3,
      //     timestamp: "2024-01-14 15:50:25"
      //   },
      //   {
      //     name: "张美丽",
      //     img: require("@/assets/images/card/7.png"),
      //     gender: "女",
      //     score: 88,
      //     id: "C0016",
      //     className: "初三1班",
      //     count: "210",
      //     emoNum: 9,
      //     camera: 2,
      //     timestamp: "2024-01-12 14:45:30"
      //   },
      //   {
      //     name: "李阳阳",
      //     img: require("@/assets/images/card/8.png"),
      //     gender: "男",
      //     score: 91,
      //     id: "C0017",
      //     className: "初二3班",
      //     count: "180",
      //     emoNum: 2,
      //     camera: 1,
      //     timestamp: "2024-01-15 16:20:10"
      //   },
      //   {
      //     name: "王晴",
      //     img: require("@/assets/images/card/9.png"),
      //     gender: "女",
      //     score: 83,
      //     id: "C0018",
      //     className: "初二1班",
      //     count: "170",
      //     emoNum: 6,
      //     camera: 3,
      //     timestamp: "2024-01-13 08:40:15"
      //   },
      //   {
      //     name: "林小雨",
      //     img: require("@/assets/images/card/10.png"),
      //     gender: "女",
      //     score: 86,
      //     id: "C0019",
      //     className: "初一4班",
      //     count: "125",
      //     emoNum: 5,
      //     camera: 2,
      //     timestamp: "2024-01-11 13:10:00"
      //   },
      //   {
      //     name: "陈阳光",
      //     img: require("@/assets/images/card/11.png"),
      //     gender: "男",
      //     score: 89,
      //     id: "C0020",
      //     className: "初三6班",
      //     count: "190",
      //     emoNum: 7,
      //     camera: 1,
      //     timestamp: "2024-01-14 18:15:30"
      //   },
      //   {
      //     name: "刘梦",
      //     img: require("@/assets/images/card/12.png"),
      //     gender: "女",
      //     score: 94,
      //     id: "C0021",
      //     className: "初二5班",
      //     count: "110",
      //     emoNum: 6,
      //     camera: 3,
      //     timestamp: "2024-01-10 17:00:45"
      //   },
      //   {
      //     name: "马飞",
      //     img: require("@/assets/images/card/13.png"),
      //     gender: "男",
      //     score: 77,
      //     id: "C0022",
      //     className: "初三3班",
      //     count: "135",
      //     emoNum: 4,
      //     camera: 2,
      //     timestamp: "2024-01-12 16:20:30"
      //   },
      //   {
      //     name: "周小宝",
      //     img: require("@/assets/images/card/14.png"),
      //     gender: "男",
      //     score: 93,
      //     id: "C0023",
      //     className: "初一5班",
      //     count: "220",
      //     emoNum: 8,
      //     camera: 1,
      //     timestamp: "2024-01-13 07:35:20"
      //   },
      //   {
      //     name: "杨雪",
      //     img: require("@/assets/images/card/15.png"),
      //     gender: "女",
      //     score: 84,
      //     id: "C0024",
      //     className: "初二2班",
      //     count: "115",
      //     emoNum: 5,
      //     camera: 2,
      //     timestamp: "2024-01-12 11:55:10"
      //   },
      //   {
      //     name: "朱星星",
      //     img: require("@/assets/images/card/16.png"),
      //     gender: "男",
      //     score: 90,
      //     id: "C0025",
      //     className: "初三4班",
      //     count: "145",
      //     emoNum: 7,
      //     camera: 3,
      //     timestamp: "2024-01-11 10:40:30"
      //   },
      //   {
      //     name: "及你太美阿阿萨阿萨威威萨方法",
      //     img: require("@/assets/images/card/1.png"),
      //     gender: "男",
      //     score: 98,
      //     id: "C0020",
      //     className: "初一3班",
      //     count: "232",
      //     emoNum: 6,
      //     camera: 1,
      //     timestamp: "2024-01-13 11:34:33"
      //   }, {
      //     name: "及你太美阿阿萨阿萨威威萨方法",
      //     img: require("@/assets/images/card/1.png"),
      //     gender: "男",
      //     score: 98,
      //     id: "C0020",
      //     className: "初一3班",
      //     count: "232",
      //     emoNum: 6,
      //     camera: 4,
      //     timestamp: "2024-01-13 11:34:33",
      //   },
      //   {
      //     name: "小华",
      //     img: require("@/assets/images/card/3.png"),
      //     gender: "女",
      //     score: 92,
      //     id: "C0018",
      //     className: "初一2班",
      //     count: "245",
      //     emoNum: 5,
      //     camera: 3,
      //     timestamp: "2024-01-11 14:32:11",
      //   },
      //   {
      //     name: "小丽",
      //     img: require("@/assets/images/card/2.png"),
      //     gender: "女",
      //     score: 88,
      //     id: "C0022",
      //     className: "初二2班",
      //     count: "200",
      //     emoNum: 4,
      //     camera: 4,
      //     timestamp: "2024-01-10 10:15:55"
      //   },
      //   {
      //     name: "小丽",
      //     img: require("@/assets/images/card/2.png"),
      //     gender: "女",
      //     score: 88,
      //     id: "C0022",
      //     className: "初二2班",
      //     count: "200",
      //     emoNum: 4,
      //     camera: 2,
      //     timestamp: "2024-01-10 10:15:55"
      //   },
      //   {
      //     name: "小丽",
      //     img: require("@/assets/images/card/2.png"),
      //     gender: "女",
      //     score: 88,
      //     id: "C0022",
      //     className: "初二2班",
      //     count: "200",
      //     emoNum: 4,
      //     camera: 2,
      //     timestamp: "2024-01-10 10:15:55"
      //   },
      //   {
      //     name: "小丽",
      //     img: require("@/assets/images/card/2.png"),
      //     gender: "女",
      //     score: 88,
      //     id: "C0022",
      //     className: "初二2班",
      //     count: "200",
      //     emoNum: 4,
      //     camera: 1,
      //     timestamp: "2024-01-10 10:15:55",
      //   },
      //   {
      //     name: "小丽",
      //     img: require("@/assets/images/card/2.png"),
      //     gender: "女",
      //     score: 88,
      //     id: "C0022",
      //     className: "初二2班",
      //     count: "200",
      //     emoNum: 4,
      //     camera: 1,
      //     timestamp: "2024-01-10 10:15:55",
      //   },
      // ],
    };
  },
  beforeDestroy() {
    this.closeCamera();
    this.clickLogin(this.row);
    window.removeEventListener("resize", this.handleResize); // 组件销毁时移除监听器
  },

  computed: {
    // 摄像头选择，更换数据
    cameraData() {
      if (this.cameraSelectValue == null) {
        return this.studentTop;
      }
      // 从 studentTop 里面筛选出 camera 属性等于  的数据
      return this.studentTop.filter(
        (item) => item.camera === this.cameraSelectValue
      );
    },
    classOptionBottom() {
      //配置项
      return {
        step: 3, // 数值越大速度滚动越快
        limitMoveNum: this.studentTop.length, // 开始无缝滚动的数据量 this.tableList
        hoverStop: true, // 是否开启鼠标悬停stop
        direction: 2, // 0向下 1向上 2向左 3向右
        openWatch: true, // 开启数据实时监控刷新dom
        singleHeight: 0, // 单步运动停止的高度(默认值0是无缝不停止的滚动) direction => 0/1
        singleWidth: 0, // 单步运动停止的宽度(默认值0是无缝不停止的滚动) direction => 2/3
        waitTime: 1000, // 单步运动停止的时间(默认值1000ms)
      };
    },
  },
  created() {
    // 从后台数据库拿学生数据
    this.getStudent();

    try {
      this.webVideo = new WebVideo();
    } catch (error) {
      // 忽略错误
    }
  },
  methods: {
    // 获取学生数据
    getStudent() {
      getStudentData().then(response => {
        this.studentTop = response.rows.map((item, index) => {
          return {
            name: item.studentName,
            img: this.baseUrl + item.faceImage,
            gender: item.sex === '1' ? '女' : '男',
            score: this.scoreList[index],
            id: item.studentId,
            className: item.classes,
            count: index + 1,
            emoNum: this.emoNumList[index] || this.emoNumList[0],
            camera: 1,
            createTime: this.dataList[index] || this.dataList[0],
          }
        })
      })
    },
    handleResize() {
      // 强制重新初始化 vue-seamless-scroll
      const seamlessScroll = this.$refs.seamlessScroll;
      if (seamlessScroll && seamlessScroll.reset) {
        seamlessScroll.reset(); // 使用插件的 `reset` 方法重新初始化
      }
    },
    // 摄像头 start
    closeCamera() {
      this.webVideo.clickStopRealPlay(0);
      this.webVideo.clickLogout(this.currentCameraInfo[0].cameraIp);
      window.setTimeout(() => {
        this.webVideo.close_JSVideoPlugin();
        this.currentCameraInfo = [];
      }, 100);
    },

    clickLogin(obj) {
      if (obj?.cameraIp == "192.168.1.64") {
        this.webVideo.clickLogin(
          obj.cameraIp,
          obj.cameraName,
          obj.cameraPassword
        );
      }
    },
    showPreview() {
      this.currentCameraInfo = [this.row];
      // this.formSwitch = true;
    },
    // 摄像头 end
  },
  mounted() {
    // 调用摄像头

    try {
      this.showPreview();
    } catch (error) {
      // 忽略错误
    }
    this.handleResize(); // 初次启动时调用一次
    window.addEventListener("resize", this.handleResize); // 监听窗口尺寸变化

    if (this.$store.state.app.sidebar.opened == true) {
      this.$store.dispatch("app/toggleSideBar");
    }
  },
};
</script>
<style scoped lang="scss">
.main {
  width: calc(100% - 40px);
  height: calc(60% - 20px);
  // background: linear-gradient(to bottom right,
  //     rgba(213, 231, 250),
  //     rgba(170, 213, 244));
  display: flex;
  margin-bottom: 20px;

  .frames {
    width: calc(65% - 20px);
    height: 100%;
    // border: solid 2px red;
    background-color: #d6e7fa;
    padding: 1ch;
    margin-left: 1ch;
    // margin-right: 20px;
    display: flex;
    justify-content: center;
    border-radius: 1ch;

    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
  }

  // 右侧列表大小
  .currentDevice {
    width: 35%;
    height: 100%;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
    /* 多层次阴影 */
    transition: box-shadow 0.3s ease-in-out;
    // padding-right: 1%;
    /* 增加动态效果 */

    &.seamless-warp2 {
      width: 100%;
      // height: 100%;
      overflow: hidden;
    }

    .currentDeviceText {
      background: linear-gradient(
        to bottom right,
        rgba(170, 213, 244),
        rgba(213, 231, 250)
      );
      width: 100%;
      height: 20%;
      border-top-left-radius: 10px;
      border-top-right-radius: 10px;

      .currentDeviceTextTop {
        width: 100%;
        height: 60%;
        display: flex;
        font-size: 20px;
        font-weight: 1000;
        color: #094b88;

        .title {
          display: flex;
          align-items: center;
        }
      }

      .currentDeviceTextBottom {
        width: 100%;
        height: 40%;
        color: #094b88;
        display: block;
        word-wrap: break-word;
      }
    }

    .currentDeviceMessage {
      //隐藏滚动条
      width: 100%;
      height: 86%;
      scrollbar-width: none;
      /* Firefox */
      -ms-overflow-style: none;
      /* IE 10+ */

      background-color: #d6e7fa;
      width: 100%;
      overflow: auto;
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      // justify-content: center !important;
      padding-right: 1ch;

      .centerBox {
        height: auto;
        width: 100%;
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        background-color: #d6e7fa;
      }
    }
  }
}

// 下面框架高度
.framesButtom {
  width: calc(100% - 40px);
  height: 55%;
  // background-color: aqua;
  border-radius: 15px;
  // border: solid 1px red;
  box-sizing: border-box;
  overflow: hidden;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);

  // 中间内容区域
  .framesButtomText {
    width: 100%;
    height: 15%;
    background: linear-gradient(
      to bottom right,
      rgba(170, 213, 244),
      rgba(213, 231, 250)
    );
    font-size: 18px;
    text-align: left;
    line-height: 448%;
    color: #094b88;
    border-bottom: solid 1px #5cacf5;
    margin-bottom: 1px;
    display: flex;
    align-items: center;
  }

  .framesButtomContent {
    width: 100%;

    .seamless-war {
      width: 100vw;
      border: solid 1px green;
      background-color: red;
    }
  }

  .bottom_box {
    // 左侧
    // width: 100%;
    display: flex;
    background-color: #d6e7fa;
  }
}

.back {
  width: 7px;
  height: 7px;
  background-color: #fb926e;
  border-radius: 50px;
  position: absolute;
  z-index: 9;
}

.header_box {
  margin-left: 3%;
  display: flex;

  .list_box {
    text-align: center;
    width: 200px;
    padding: 10px 0;
    margin-left: 30px;
    border-radius: 10px;
    background-color: #1dbff7;
    color: #fff;

    .list_title {
      line-height: 30px;
    }
  }

  .list_box2 {
    background-color: #599afe;
  }

  .list_box3 {
    background-color: #22bfb6;
  }
}

.table_header {
  margin-top: 20px;
  display: flex;
  flex-direction: row-reverse;

  .select_box {
    margin-right: 20px;
  }
}

.fault {
  width: 80px;
  background-color: #fb926e;
  color: #fff;
  border-radius: 7px;
}

.fault2 {
  background-color: #17a4ff;
}

.table_conten {
  margin-top: 20px;
  width: 100%;
  height: 100%;
}

.first {
  ::v-deep .el-collapse-item__content {
    padding-bottom: 0;
  }
}

::v-deep .el-collapse {
  border: none;
}

::v-deep .el-collapse-item__header {
  // background-color: #296689;
  border: none;
  color: #b8def8;
}

::v-deep .el-collapse-item__header.is-active {
  // background-color: #296689;
  border: none;
  color: #b8def8;
}

::v-deep .el-collapse-item__wrap {
  // background-color: #296689;
}

::v-deep .el-textarea__inner {
  min-height: 105px !important;
}

::v-deep .el-collapse-item__arrow {
  margin: 0;
  margin-left: 10px;
}
</style>
