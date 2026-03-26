<template>
  <div id="divPlugin" class="shexiangtou"></div>
</template>
<script>
import { WebVideo } from "./webVideo.js";
export default {
  name: "CameraDiv",
  props: {
    cameraList: [Array],
  },
  data() {
    return {
      webVideo: null,
    };
  },
  methods: {},
  mounted() {
    // 页面加载后立即刷新
    this.webVideo = new WebVideo();
    this.$nextTick(() => {
    //   // this.webVideo.init("192.168.2.89", "admin", "lanbu@2024", "divPlugin");
      this.webVideo.init("divPlugin");

      this.cameraList.forEach((v, i) => {
        window.setTimeout(() => {
          this.webVideo.clickLogin(
            v.cameraIp,
            v.cameraName,
            v.cameraPassword,
            i
          );
        }, 1000);
      });
      // let a = this.webVideo.getDeviceInfo("192.168.1.89");
      // console.log(a);
    });
  },
};
</script>
<style lang="scss" scoped>
.shexiangtou {
  height: 95vh;
  width: 100vw;
}
</style>
