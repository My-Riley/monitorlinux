<template>
  <div class="main">
    <div class="top">
      <div class="time">
        <span>{{ currentTime }} </span>
        <span>星期{{ currentDay }}</span>
      </div>
      <span class="headline"> 情绪识别系统 </span>
      <div class="quit">
        <button class="logOut" @click="logout">退出登录</button>
        <button class="logOut" @click="enterInto">进入后台管理系统</button>
      </div>
    </div>
    <div class="videoRegion">
      <camera v-for="v in cameraList" :hkvInfo="v" :key="v.id"></camera>
    </div>
    <div class="formArea">
      <div class="listTop">七日内报警信息</div>
      <div class="list">
        <div class="toptitle">
          <div class="item">报警信息</div>
          <div class="item">报警截图</div>
          <div class="item">时间</div>
        </div>
        <vue-seamless-scroll
          :data="warnList"
          :class-option="optionHover"
          class="seamless-warp"
        >
          <el-table :data="warnList" border :show-header="status">
            <el-table-column
              label=" 报警信息"
              align="center"
              prop="warnInformation"
            />
            <el-table-column
              label="报警截图"
              align="center"
              prop="warnPicture"
              width="120"
            >
              <template #default="scope">
                <div v-if="scope.row.warnPicture" style="display: flex">
                  <div
                    v-for="(v, i) in scope.row.warnPicture.split(',')"
                    :key="i"
                  >
                    <img
                      :src="baseUrl + v"
                      :preview-src-list="
                        scope.row.warnPicture
                          .split(',')
                          .map((v1) => baseUrl + v1)
                      "
                      style="width: 100px; height: 80px"
                    />
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column
              label="时间"
              align="center"
              prop="createTime"
              width="160"
            >
              <template slot-scope="scope">
                <span>{{ parseTime(scope.row.createTime) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </vue-seamless-scroll>
      </div>
    </div>
  </div>
</template>

<script>
// import VueSeamlessScroll from "VueSeamlessScroll";
import { listWarn, listWarnNo } from "@/api/camera/warn.js";
import { listCamera } from "@/api/camera/camera";
import camera from "@/views/cellManagement/camera/camera.vue";
export default {
  name: "Screen",
  components: {
    camera,
  },
  data() {
    return {
      baseUrl: process.env.VUE_APP_BASE_API,
      warnList: [],
      loading: false,
      status: false,

      currentDay: "",
    };
  },
  created() {
    this.getList();
    this.updateDay();

    this.updateTime(); // 初始化时立即更新时间
    // 每秒更新一次时间
    this.timer = setInterval(() => {
      this.updateTime();
    }, 1000);
    this.cameraList();
  },
  computed: {
    optionHover() {
      return {
        step: 1, // 数值越大速度滚动越快
        limitMoveNum: 2, // 开始无缝滚动的数据量 this.dataList.length
        hoverStop: true, // 是否开启鼠标悬停stop
        direction: 1, // 0向下 1向上 2向左 3向右
        openWatch: true, // 开启数据实时监控刷新dom
        singleHeight: 0, // 单步运动停止的高度(默认值0是无缝不停止的滚动) direction => 0/1
        singleWidth: 0, // 单步运动停止的宽度(默认值0是无缝不停止的滚动) direction => 2/3
        waitTime: 1000, // 单步运动停止的时间(默认值1000ms)
      };
    },
  },
  methods: {
    // 退出登录
    async logout() {
      this.$confirm("确定注销并退出系统吗？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          this.$store.dispatch("LogOut").then(() => {
            location.href = "/index";
          });
        })
        .catch(() => {});
    },
    // 进入后台管理系统
    enterInto() {
      this.$router.push({ path: "/index" });
    },
    //获取实时时间
    updateTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, "0");
      const day = String(now.getDate()).padStart(2, "0");
      const hours = String(now.getHours()).padStart(2, "0");
      const minutes = String(now.getMinutes()).padStart(2, "0");
      const seconds = String(now.getSeconds()).padStart(2, "0");
      this.currentTime = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    },
    //获取实时星期
    updateDay() {
      const now = new Date();
      const days = ["日", "一", "二", "三", "四", "五", "六"];
      const dayOfWeek = days[now.getDay()];
      this.currentDay = dayOfWeek;
    },
    /** 查询摄像头预警列表 */
    getList() {
      this.loading = true;
      // 获取当前时间和7天前的时间
      const currentTime = new Date();
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(currentTime.getDate() - 3);

      // 发送请求，获取7天内的报警信息
      listWarnNo(sevenDaysAgo, currentTime).then((response) => {
        this.warnList = response.data;
        this.loading = false;
      });
    },
    cameraList() {
      listCamera().then((response) => {
        this.cameraList = response.rows;
        this.cameraList = this.cameraList.map((item) => {
          item.cameraId =
            "cameraId" +
            item.cameraIp.split(".")[2] +
            item.cameraIp.split(".")[3];
          return item;
        });
      });
    },
    scroll() {
      if (this.$refs.wgzp && this.$refs.wgzp.$el) {
        let maxHeight =
          this.$refs.wgzp.$el.querySelectorAll(".el-table__body")[0]
            .offsetHeight;
        let clientHeight = this.$refs.wgzp.bodyWrapper.clientHeight;
        if (
          Math.abs(
            this.$refs.wgzp.bodyWrapper.scrollTop - (maxHeight - clientHeight)
          ) < 5
        ) {
          //预留5像素误差
          this.$refs.wgzp.bodyWrapper.scrollTop = 0; // 滚动到列表开头
        } else {
          this.$refs.wgzp.bodyWrapper.scrollTop += 18;
        }
      }
    },
    MouseEnter() {
      //鼠标移入停止滚动
      clearInterval(this.interval);
    },
    MouseLeave() {
      //鼠标离开继续滚动
      this.interval = setInterval(this.scroll, 1000);
    },
  },
  mounted() {
    this.interval = setInterval(this.scroll, 1000);
  },
  beforeDestroy() {
    clearInterval(this.interval);
    clearInterval(this.timer); // 组件销毁前清除定时器
  },
};
</script>

<style scoped lang="scss">
.main {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-wrap: wrap;
  .videoRegion {
    width: 75%;
    float: left;
    height: calc(100vh - 50px);
    // .aa {
    //   background-color: red;
    //   width: 33%;
    //   height: 33%;
    //   float: left;
    //   margin-top: 1px;
    //   margin-left: 2px;
    // }
  }
  .formArea {
    width: 25%;
    height: calc(100vh - 81px);
    .list {
      height: calc(100% - 50px);
    }
    .listTop {
      width: 100%;
      height: 50px;
      background-color: #303133;
      font-size: 20px;
      text-align: center;
      line-height: 50px;
      color: #fff;
    }
  }
  .top {
    background-color: rgb(13, 14, 14);
    width: 100%;
    height: 50px;
    display: flex;
    .time {
      display: flex;
      flex-direction: column;
      width: 10%;
      text-align: center;
      height: 100%;
      line-height: 25px;
      font-size: 13px;
      color: #fff;
    }
    .headline {
      width: 70%;
      font-size: 30px;
      text-align: center;
      color: #fff;
    }
    .quit {
      width: 20%;
      height: 100%;
      text-align: right;
      .logOut {
        margin-top: 15px;
        margin-right: 20px;
        border: none;
        background-color: #000;
        color: #fff;
      }
      .logOut:hover {
        color: cyan;
        border-bottom: 1px solid cyan;
      }
    }
  }
}

.seamless-warp {
  height: 100%;
  overflow: auto;
}
.el-table .cell {
  text-align: center;
}
.toptitle {
  width: 100%;
  display: flex;
  margin-bottom: 10px;
  background-color: transparent;
  color: #000;
}
.item {
  width: 33.3%;
  text-align: center;
}
::v-deep.el-table--medium .el-table__cell {
  padding: 0;
}
::v-deep.el-table th.el-table__cell.is-leaf,
.el-table td.el-table__cell {
  border: none;
}
::v-deep.el-table--medium .el-table__cell {
  border: none;
}
::v-deep.el-table--group,
.el-table--border {
  border: none;
}
::v-deep .el-table__body-wrapper::-webkit-scrollbar {
  /*width: 0;宽度为0隐藏*/
  width: 0px;
}

::v-deep .el-table__body-wrapper::-webkit-scrollbar-thumb {
  border-radius: 2px;
  height: 50px;
  background: #eee;
}
::v-deep .el-table__body-wrapper::-webkit-scrollbar-track {
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
  border-radius: 2px;
  background: rgba(0, 0, 0, 0.4);
}

::v-deep .el-table--scrollable-y .el-table__body-wrapper {
  overflow: hidden !important;
}

::v-deep .el-table--scrollable-x .el-table__body-wrapper {
  overflow: hidden !important;
}
::v-deep .el-table tr {
  background-color: #e8eef8;
}
</style>
