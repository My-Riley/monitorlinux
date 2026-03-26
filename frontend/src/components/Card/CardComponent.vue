<template>
  <div class="hello">
    <div class="studentInfo">
      <!-- use -->
      <div class="top">
        <!-- icon表情 -->
        <!-- 一个单个的情绪 -->
        <!-- use -->
        <div class="mood">
          <!-- index == users.emotion  -->
          <div v-for="(item, index) in emotions" :key="index" class="emotion">
            <svg class="icon" aria-hidden="true" :style="index == student.emoNum ? { fill: item.color } : ''">
              <use :xlink:href="'#' + item.icon"></use>
            </svg>
            <span class="text" :style="index == student.emoNum ? { color: item.color } : ''">{{ item.mood }}</span>
          </div>
        </div>
      </div>

      <!-- 线条 -->
      <div class="student_line"></div>

      <!-- 个人信息 -->
      <div class="student_info">
        <!-- 头像 -->
        <div class="img">
          <img :src="student.img" alt="">
        </div>

        <!-- 信息 -->
        <div class="info">
          <div class="name_sex">
            <span class="name">{{ student.name }}</span>
            <!-- <span class="sex">男</span> -->
            <span class="sex">
              <svg v-if="student.gender == '女'" class="icon" aria-hidden="true">
                <use xlink:href="#icon-nvhai"></use>
              </svg>
              <svg v-else class="icon" aria-hidden="true">
                <use xlink:href="#icon-nanhai"></use>
              </svg>
            </span>
          </div>
          <span class="id">编号：{{ student.id }}</span>
          <span class="class_name">{{ student.className }}</span>
          <span class="count">总第{{ student.count }}次检测</span>
        </div>

        <!-- 分数 -->
        <div class="score_box">
          <div class="score">

            <div class="circle">
              <span>{{ student.score }}</span>

            </div>
          </div>
        </div>
      </div>

      <!-- 摄像头 时间 -->
      <div class="camera_box">
        <div class="camera_left">
          <!-- 摄像头图标 -->
          <div>
            <span class="icon_box">
              <svg class="cameraIcon" aria-hidden="true">
                <use xlink:href="#icon-shexiangtou"></use>
              </svg>
            </span>
            <span class="text">{{ student.camera }}# 摄像头</span>
          </div>
        </div>

        <!-- 右侧 -->
        <div class="camera_right">
          <span>
            <svg class="camera_icon" aria-hidden="true">
              <use xlink:href="#icon-shijian"></use>
            </svg>
          </span>
          <span class="time">{{ student.createTime }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import "@/assets/styles/scroll.scss";
export default {
  naem: "CardComponent",
  // props: {
  //   name: {
  //     type: String,
  //     default: "小美",
  //     required: false,
  //   },
  //   img: {
  //     type: String,
  //     default: require("@/assets/images/card/1.png"),
  //   },
  //   gender: { // 性别图标
  //     type: String,
  //     default: "男",
  //     required: false,
  //   },
  //   score: { // 分数
  //     type: Number,
  //     default: 98,
  //     required: false,
  //   },
  //   id: { // 编号
  //     type: String,
  //     default: "C001",
  //     required: false,
  //   },
  //   className: { // 班级名称
  //     type: String,
  //     default: "初一3班",
  //     required: false,
  //   },
  //   count: { // 多少次检测
  //     type: Number,
  //     default: 232,
  //     required: false,
  //   },
  //   emoNum: { // 情绪数字
  //     type: Number,
  //     default: 6,
  //     required: false,
  //   },
  //   camera: { // 几号摄像头
  //     type: Number,
  //     required: false,
  //     default: 4,
  //   },
  //   timestamp: { // 拍照的时间
  //     type: String,
  //     required: false,
  //     default: "2024-01-13 11:34:33",
  //   }
  // },
  props: {
    student: {
      type: Object,
      required: true
    }
  },

  data() {
    return {
      emotions: [
        {
          mood: "愤怒",
          icon: "icon-fennu-",
          color: "red"
        },
        {
          mood: "藐视",
          icon: "icon-bukaixin",
          color: "orange"
        },
        {
          mood: "惊讶",
          icon: "icon-biaoqing-jingya",
          color: "blue"
        },
        {
          mood: "厌恶",
          icon: "icon-yane",
          color: "black"
        },
        {
          mood: "恐惧",
          icon: "icon-kongju-",
          color: "purple"
        },
        {
          mood: "悲伤",
          icon: "icon-confused",
          color: "#aa421b"
        },
        {
          mood: "喜悦",
          icon: "icon-xiyue",
          color: "green"
        }
      ]

    }
  }
}
</script>
<!-- <style scoped lang="scss">
.hello {
  background-color: rgb(206, 228, 251);
  width: 300px;
  height: 190px;
  padding: 10px;
  border-radius: 18px;
  margin: 5px;

  // 学生信息
  .studentInfo {
    width: 100%;
    height: 190px;
    display: flex;
    flex-direction: column;

    .top {
      width: 100%;
      height: 30px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      margin-top: 5px;

      .mood {
        display: flex;
        justify-content: space-between;

        .emotion {
          width: 50px;
          height: 60px;
          display: flex;
          flex-direction: column;
          align-items: center;
          border-bottom: 5px;

          .icon {
            width: 2em;
            vertical-align: -0.15em;
            fill: currentColor;
            overflow: hidden;

          }

          .text {
            font-size: 14px;
            color: gray;
            margin-top: 4px;
            margin-bottom: 4px;
          }
        }
      }
    }

    .student_line {
      width: 100%;
      height: 1px;
      margin-top: 30px;
      border-top: solid 0.1rem gray;
      /* 使用 rem 单位，通常根据根字体大小 */
    }

    // 个人全部的信息
    .student_info {
      display: flex;
      flex-direction: row;

      // 头像
      .img {
        width: 85px;
        height: 90px;
        margin: 10px 0;
        display: flex;

        img {
          width: 100%;
          height: 100%;
          object-fit: contain;
          /* 按比例缩放，内容完全显示 */
        }

      }

      // 个人信息
      .info {
        width: 180px;
        height: 94px;
        margin-top: 5px;
        padding-left: 5px;
        display: flex;
        flex-direction: column;
        color: gray;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;

        .name_sex {
          width: 100%;
          height: 33px;

          .name {
            font-size: 20px;
            color: rgb(55, 156, 250);
            float: left;
          }

          .sex {
            float: right;
            font-size: 14px;
            height: 24px;

            .icon {
              height: 24px;
              width: 30px;
            }
          }
        }

        .id {
          font-size: 14px;
        }

        .class_name {
          font-size: 14px;
          padding-top: 5px;
        }

        .count {
          font-size: 14px;
          padding-top: 5px;
        }
      }

      // 摄像头 时间

      .score_box {
        width: 26%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 20px;

        .score {
          width: 50px;
          height: 50px;
          border: solid 1px rgb(92, 172, 245);
          border-radius: 50%;
          color: rgb(92, 172, 245);
          text-align: center;
          line-height: 50px;

        }
      }
    }

    .camera_box {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;

      .camera_left {
        height: 21px;
        width: 120px;
        display: flex;
        align-items: center;
        position: relative;

        .icon_box {
          .cameraIcon {
            width: 18px;
            height: 20px;
            top: 50%;
            transform: translate(0, -50%);
            left: 7px;
            position: absolute;
            fill: gray;
          }
        }

        .text {
          font-size: 13px;
          color: gray;
          position: absolute;
          // top: 0;
          top: 50%;
          transform: translate(0, -50%);
          left: 32px;

        }
      }

      // 右侧
      .camera_right {
        position: relative;
        width: 180px;
        height: 20px;

        .camera_icon {
          width: 15px;
          height: 20px;
          position: absolute;
          top: 50%;
          transform: translate(0, -50%);
          left: 10px;
          fill: gray;
        }

        .time {
          color: gray;
          font-size: 14px;
          position: absolute;
          top: 50%;
          transform: translate(0, -50%);
          left: 34px;

        }
      }
    }
  }
}
</style> -->

<style scoped lang="scss">
.hello {
  background-color: transparent;
  // border: solid 1px gray;
  width: calc(15.66vw - 10px); // 300px / 1366 * 100vw
  height: 28.74vh; // 190px / 768 * 100vh
  padding: 0.43vw; // 10px / 1366 * 100vw
  border-radius: 1.32vw; // 18px / 1366 * 100vw
  margin: 0.37vw; // 5px / 1366 * 100vw

  // 学生信息
  .studentInfo {
    width: 100%;
    height: 24.74vh; // 190px / 768 * 100vh
    display: flex;
    flex-direction: column;

    .top {
      width: 100%;
      height: 3.91vh; // 30px / 768 * 100vh
      display: flex;
      flex-direction: column;
      justify-content: space-between;

      .mood {
        display: flex;
        justify-content: space-between;

        .emotion {
          width: 3.66vw; // 50px / 1366 * 100vw
          height: 7.81vh; // 60px / 768 * 100vh
          display: flex;
          flex-direction: column;
          align-items: center;
          border-bottom: 0.37vw; // 5px / 1366 * 100vw

          .icon {
            width: 1.46vw; // 20px / 1366 * 100vw
            vertical-align: -0.15em;
            fill: currentColor;
            overflow: hidden;
          }

          .text {
            font-size: 0.9vw; // 1.02vw - 0.12
            color: gray;
            margin-top: 0.52vh; // 4px / 768 * 100vh
            margin-bottom: 0.52vh; // 4px / 768 * 100vh
          }
        }
      }
    }

    .student_line {
      width: 100%;
      height: 0.13vh; // 1px / 768 * 100vh
      margin-top: 3.91vh; // 30px / 768 * 100vh
      border-top: solid 0.1rem gray;
    }

    .student_info {
      display: flex;
      flex-direction: row;

      .img {
        width: 6.22vw; // 85px / 1366 * 100vw
        height: 11.72vh; // 90px / 768 * 100vh
        margin: 0.73vw 0; // 10px / 1366 * 100vw
        display: flex;
        // border: solid 1px red;

        img {
          width: 100%;
          height: 100%;
          object-fit: contain;
        }
      }

      .info {
        width: 10.18vw; // 180px / 1366 * 100vw
        height: 15.24vh; // 94px / 768 * 100vh
        margin-top: 0.65vh; // 5px / 768 * 100vh
        padding-left: 0.37vw; // 5px / 1366 * 100vw
        display: flex;
        flex-direction: column;
        color: gray;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;

        .name_sex {
          width: 100%;
          height: 4.3vh; // 33px / 768 * 100vh

          .name {
            // border: solid 1px red;
            width: 64%;
            overflow: hidden;
            font-size: 1.04vw; // 1.46vw - 0.12
            color: rgb(55, 156, 250);
            float: left;
          }

          .sex {
            float: right;
            font-size: 0.9vw; // 1.02vw - 0.12
            height: 3.13vh; // 24px / 768 * 100vh

            .icon {
              height: 3.13vh; // 24px / 768 * 100vh
              width: 2.19vw; // 30px / 1366 * 100vw
            }
          }
        }

        .id {
          font-size: 0.9vw; // 1.02vw - 0.12
        }

        .class_name {
          font-size: 0.9vw; // 1.02vw - 0.12
          padding-top: 0.65vh; // 5px / 768 * 100vh
        }

        .count {
          font-size: 0.9vw; // 1.02vw - 0.12
          padding-top: 0.65vh; // 5px / 768 * 100vh
        }
      }

      .score_box {
        width: 5.8vw; // 50px / 1366 * 100vw
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.34vw; // 1.46vw - 0.12

        .score {
          // width: 3.2vw; // 50px / 1366 * 100vw
          // // height: 6.51vh; // 50px / 768 * 100vh
          // aspect-ratio: 1;
          // border: solid 1px rgb(92, 172, 245); // 10px / 1366 * 100vw
          // border-radius: 50%;
          // color: rgb(92, 172, 245);
          // text-align: center;
          // line-height: 6.51vh; // 50px / 768 * 100vh

          width: 100%;
          /* 圆形的宽度，等于父元素宽度的 50% */
          position: relative;
          // border: solid 1px red;
          /* 为了更清楚地看到圆形的位置，添加一个边框 */

          &::before {
            content: '';
            display: block;
            padding-top: 100%;
            /* 1:1 的宽高比 */
          }

          .circle {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            // background-color: lightpink;
            border: solid 1px rgb(92, 172, 245);
            text-align: center;
            line-height: 50%;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            color: rgb(92, 172, 245);

            /* 使元素变成圆形 */
          }
        }
      }
    }

    .camera_box {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;

      .camera_left {
        height: 2.73vh; // 21px / 768 * 100vh
        width: 8.78vw; // 120px / 1366 * 100vw
        display: flex;
        align-items: center;
        position: relative;

        .icon_box {
          .cameraIcon {
            width: 1.02vw; // 18px / 1366 * 100vw
            height: 2.6vh; // 20px / 768 * 100vh
            top: 50%;
            transform: translate(0, -50%);
            left: 0.51vw; // 7px / 1366 * 100vw
            position: absolute;
            fill: gray;
          }
        }

        .text {
          font-size: 0.7vw; // 0.95vw - 0.12
          color: gray;
          position: absolute;
          top: 50%;
          transform: translate(0, -50%);
          left: 2vw; // 32px / 1366 * 100vw
        }
      }

      .camera_right {
        position: relative;
        width: 14.18vw; // 180px / 1366 * 100vw
        height: 2.6vh; // 20px / 768 * 100vh

        .camera_icon {
          width: 0.78vw; // 1.1vw - 0.12
          height: 2.6vh; // 20px / 768 * 100vh
          position: absolute;
          top: 50%;
          transform: translate(0, -50%);
          left: 0.73vw; // 10px / 1366 * 100vw
          fill: gray;
        }

        .time {
          color: gray;
          font-size: 0.7vw; // 1.02vw - 0.12
          position: absolute;
          top: 50%;
          transform: translate(0, -50%);
          left: 2.09vw; // 34px / 1366 * 100vw
        }
      }
    }
  }
}
</style>
