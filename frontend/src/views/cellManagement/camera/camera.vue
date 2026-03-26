<template>
  <div :id="hkvInfo.cameraId" class="xxx"></div>
</template>
<script>
import { WebVideo } from "./webVideo.js";

export default {
  name: "Camera",
  props: {
    hkvInfo: {
      type: Object,
      required: true
    },
  },
  data () {
    return {
      WebVideo: "",
      camera: null,
    };
  },
  mounted () {
    this.webVideo = new WebVideo();
    this.$nextTick(() => {
      this.webVideo.init(
        this.hkvInfo.cameraIp,
        this.hkvInfo.cameraName,
        this.hkvInfo.cameraPassword,
        this.hkvInfo.cameraId
      );
      window.setTimeout(() => {
        this.webVideo.clickLogin();
      }, 1000);
    });
  },
  // 销毁
  beforeDestroy () {
    this.webVideo.clickStopRealPlay();
    this.webVideo.clickLogout();
    this.webVideo.close_JSVideoPlugin();
  },
};
</script>
<style lang="scss" scoped>
.xxx {
  width: 400px;
  height: 300px;
  background-color: red;
}
</style>
