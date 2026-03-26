<template>
  <!-- @refresh-header-search="refreshData" -->
  <div :class="{ show: show }" class="header-search">
    <!-- <el-button type="text" icon="el-icon-d-arrow-left" size="mini" @click="toScreen">返回大屏</el-button> -->
    <!-- <svg-icon class-name="search-icon" icon-class="remind" /> -->
    <el-popover placement="top" width="400" trigger="click">
      <el-table :data="gridData" height="300px">
        <el-table-column
          label="报警信息"
          align="center"
          prop="warnAddress"
          width="120"
          :show-overflow-tooltip="true"
        />
        <el-table-column
          label="时间"
          align="center"
          prop="createTime"
          width="120"
        >
          <template slot-scope="scope">
            <span>{{ parseTime(scope.row.createTime) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          align="center"
          class-name="small-padding fixed-width"
        >
          <template slot-scope="scope">
            <!-- <el-button size="mini" type="text" icon="el-icon-edit" @click="handleUpdate(scope.row)" v-hasPermi="['camera:warn:edit']">修改</el-button> -->
            <el-button
              v-if="scope.row.warnHandle == '1'"
              size="mini"
              type="text"
              icon="el-icon-view"
              @click="examine(scope.row)"
            >查看</el-button>
            <el-button
              v-else
              size="mini"
              type="text"
              icon="el-icon-thumb"
              @click="examine(scope.row)"
            >处理</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 信息铃铛 -->
      <!-- <el-badge slot="reference" :value="alertCount" class="item">
        <svg-icon class-name="search-icon" icon-class="remind" style="font-size: 25px" @click="unpack" />
      </el-badge> -->
    </el-popover>

    <!-- 添加或修改摄像头预警对话框 -->
    <!-- 处理框 -->
    <el-dialog
      title="处理预警信息"
      :visible.sync="open"
      width="500px"
      append-to-body
      :close-on-click-modal="false"
      :show-close="false"
    >
      <el-form ref="form" :model="form" :rules="rules">
        <el-form-item label="上传图片" prop="handlePicture" label-width="110px">
          <el-upload
            :action="uploadImgUrl"
            list-type="picture-card"
            :show-file-list="true"
            :file-list="fileList"
            :limit="1"
            :multiple="true"
            :headers="headers"
            :on-error="handleUploadError"
            :on-success="handleUploadSuccess"
            :on-preview="handlePictureCardPreview"
          >
            <i class="el-icon-plus"></i>
          </el-upload>
          <el-dialog :visible.sync="dialogVisible" append-to-body>
            <img width="100%" :src="dialogImageUrl" />
          </el-dialog>
        </el-form-item>

        <el-form-item label="处理经过" prop="handleDescribe">
          <el-input
            type="textarea"
            v-model="form.handleDescribe"
            placeholder="请输入处理经过"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="manage">确 定</el-button>
        <el-button @click="cancel">取消</el-button>
      </div>
    </el-dialog>
    <svg-icon
      class-name="search-icon"
      icon-class="search"
      @click.stop="click"
    />
    <el-select
      ref="headerSearchSelect"
      v-model="search"
      :remote-method="querySearch"
      filterable
      default-first-option
      remote
      placeholder="Search"
      class="header-search-select"
      @change="change"
    >
      <el-option
        v-for="option in options"
        :key="option.item.path"
        :value="option.item"
        :label="option.item.title.join(' > ')"
      />
    </el-select>
  </div>
</template>

<script>
// fuse is a lightweight fuzzy-search module
// make search results more in line with expectations
import {
  getWarnCount,
  handleWarn,
  updateWarn,
  getWarnById,
  listWarnNo,
} from "@/api/camera/warn.js";
import Fuse from "fuse.js/dist/fuse.min.js";
import path from "path";
// import { getToken } from "../../../utils/auth";
import { getToken } from "@/utils/auth";
import Stomp from "stompjs";
import { bus } from "@/main";
import { mapActions, mapState } from "vuex";

export default {
  name: "HeaderSearch",
  data() {
    return {
      baseUrl: process.env.VUE_APP_BASE_API,
      uploadImgUrl: process.env.VUE_APP_BASE_API + "/common/upload", // 上传的图片服务器地址
      baseUrl: process.env.VUE_APP_BASE_API,
      search: "",
      options: [],
      searchPool: [],
      dialogImageUrl: "",
      show: false,
      fuse: undefined,
      fileList: [],
      dialogVisible: false,
      headers: {
        Authorization: "Bearer " + getToken(),
      },
      // data: this.$store.state.user.alarmNum,
      gridData: [],
      // 是否显示弹出层
      open: false,
      form: {},
      client: null,
      rules: {
        handleDescribe: [
          { required: true, message: "请输入处理经过", trigger: "blur" },
          {
            min: 2,
            max: 200,
            message: "长度在 2 到 200 个字符",
            trigger: "blur",
          },
        ],
      },
    };
  },
  computed: {
    routes() {
      return this.$store.getters.permission_routes;
    },
    ...mapState({
      alertCount: (state) => state.user.alarmNum,
    }),
  },
  watch: {
    routes() {
      this.searchPool = this.generateRoutes(this.routes);
    },
    searchPool(list) {
      this.initFuse(list);
    },
    show(value) {
      if (value) {
        document.body.addEventListener("click", this.close);
      } else {
        document.body.removeEventListener("click", this.close);
      }
    },
    alertCount() {
      this.getList();
      this.$root.$emit("data-changed"); // 触发自定义事件
    },
  },
  mounted() {
    this.searchPool = this.generateRoutes(this.routes);
    // this.connect()
  },
  created() {
    // this.getAmount();
    this.getList();
    // this.fetchAlertCount();
    // bus.$on('refresh-header-search', () => {
    //   this.refreshData();
    // });
  },
  methods: {
    //返回大屏
    // toScreen () {
    //   this.$router.push('/screen')
    // },
    unpack() {
      this.getList();
    },
    // 显示图片
    handlePictureCardPreview(file) {
      this.dialogImageUrl = file.url;
      this.dialogVisible = true;
    },
    // 上传成功
    handleUploadSuccess(response, file, fileList) {
      this.form.handlePicture = fileList
        .map((f) => {
          if (f.response) {
            return f.response.fileName;
          }
          return f.url;
        })
        .join(",");
    },
    handleUploadError() {
      this.$message("图片上传失败，请重试");
    },
    // updateData(newValue) {
    //   this.data = newValue;
    //   this.$emit("data-changed", newValue); // 触发自定义事件
    // },
    // refreshData() {
    //   this.getList();
    //   this.getAmount();
    // },
    // connect() {
    //   //这里填你rabbitMQ的连接ip地址直接替换localhost:15674就好其它的不用改
    //   this.client = Stomp.client("ws://192.168.2.51:15674/ws");
    //   this.client.debug = function (str) {};
    //   this.client.connect(
    //     "lanbu",
    //     "123456",
    //     () => {
    //       console.log("登录成功");
    //       this.client.subscribe("camera_lanbu", (res) => {
    //         this.data = res.body;
    //       });
    //     },
    //     (err) => {
    //       console.log(err, "登录失败");
    //     },
    //     "/"
    //   );
    // },
    // 获取告警列表
    getList() {
      // 默认参数对象
      const defaultParams = {
        warnHandle: "0 ",
      };
      // 获取告警列表(不分页)
      listWarnNo({ ...defaultParams }).then((res) => {
        this.gridData = res.data;
      });
      // bus.$emit("refreshList");
    },
    // 获取告警数量
    getAmount() {
      getWarnCount().then((res) => {
        this.$store.commit("SET_ALARM_NUM", res.data);
      });
    },
    // 处理按钮
    manage() {
      this.form.warnHandle = 1;
      this.open = false;
      // 调用更新预警信息的接口
      updateWarn(this.form)
        .then((response) => {
          this.open = false;
          // const currentTime = new Date();
          // this.form.updateTime = currentTime;
          this.$message.success("摄像头预警信息处理成功");
          // 刷新预警列表
          this.getList();
        })
        .catch((error) => {
          console.error("摄像头预警信息修改失败", error);
          this.$message.error("摄像头预警信息修改失败，请重试");
        });
    },
    // 查看按钮
    examine(row) {
      const id = row.id || this.ids;
      getWarnById(id).then((response) => {
        this.form = response.data;
        this.alarmAddress = this.form.warnAddress.split(" ")[0];
        this.alarmCamera = this.form.warnAddress.split(" ")[1];
        // if (response.data.warnPicture) {
        //   this.fileList = response.data.warnPicture.split(",").map((v) => {
        //     return {
        //       name: v,
        //       url: this.baseUrl + v,
        //     };
        //   });
        // };
        if (response.data.handlePicture) {
          this.fileList = response.data.handlePicture.split(",").map((v) => {
            return {
              name: v,
              url: this.baseUrl + v,
            };
          });
        }
        this.form.warnHandle == 0
          ? (this.form.warnHandle = "未处理")
          : (this.form.warnHandle = "已处理");
        this.open = true;
        this.title = "查看摄像头预警";
      });
    },
    cancel() {
      this.open = false;
      // this.getList();
    },
    click() {
      this.show = !this.show;
      if (this.show) {
        this.$refs.headerSearchSelect && this.$refs.headerSearchSelect.focus();
      }
    },
    close() {
      this.$refs.headerSearchSelect && this.$refs.headerSearchSelect.blur();
      this.options = [];
      this.show = false;
    },
    change(val) {
      const path = val.path;
      if (this.ishttp(val.path)) {
        // http(s):// 路径新窗口打开
        const pindex = path.indexOf("http");
        window.open(path.substr(pindex, path.length), "_blank");
      } else {
        this.$router.push(val.path);
      }
      this.search = "";
      this.options = [];
      this.$nextTick(() => {
        this.show = false;
      });
    },
    initFuse(list) {
      this.fuse = new Fuse(list, {
        shouldSort: true,
        threshold: 0.4,
        location: 0,
        distance: 100,
        minMatchCharLength: 1,
        keys: [
          {
            name: "title",
            weight: 0.7,
          },
          {
            name: "path",
            weight: 0.3,
          },
        ],
      });
    },
    // Filter out the routes that can be displayed in the sidebar
    // And generate the internationalized title
    generateRoutes(routes, basePath = "/", prefixTitle = []) {
      let res = [];

      for (const router of routes) {
        // skip hidden router
        if (router.hidden) {
          continue;
        }

        const data = {
          path: !this.ishttp(router.path)
            ? path.resolve(basePath, router.path)
            : router.path,
          title: [...prefixTitle],
        };

        if (router.meta && router.meta.title) {
          data.title = [...data.title, router.meta.title];
          if (router.redirect !== "noRedirect") {
            // only push the routes with title
            // special case: need to exclude parent router without redirect
            res.push(data);
          }
        }

        // recursive child routes
        if (router.children) {
          const tempRoutes = this.generateRoutes(
            router.children,
            data.path,
            data.title
          );
          if (tempRoutes.length >= 1) {
            res = [...res, ...tempRoutes];
          }
        }
      }
      return res;
    },
    querySearch(query) {
      if (query !== "") {
        this.options = this.fuse.search(query);
      } else {
        this.options = [];
      }
    },
    ishttp(url) {
      return url.indexOf("http://") !== -1 || url.indexOf("https://") !== -1;
    },
  },
};
</script>

<style lang="scss" scoped>
::v-deep.item {
  /* margin-top: -4px; */
  margin-right: 20px;
  /* padding: 0px !important; */
  height: 30px;
  // background-color: red;
  width: 20px;
  line-height: 30px;
}

.header-search {
  font-size: 0 !important;

  .search-icon {
    cursor: pointer;
    font-size: 18px;
    vertical-align: middle;
  }

  .header-search-select {
    font-size: 18px;
    transition: width 0.2s;
    width: 0;
    overflow: hidden;
    background: transparent;
    border-radius: 0;
    display: inline-block;
    vertical-align: middle;

    ::v-deep .el-input__inner {
      border-radius: 0;
      border: 0;
      padding-left: 0;
      padding-right: 0;
      box-shadow: none !important;
      border-bottom: 1px solid #d9d9d9;
      vertical-align: middle;
    }
  }

  &.show {
    .header-search-select {
      width: 210px;
      margin-left: 10px;
    }
  }
}
.el-button--text {
  border-color: transparent;
  color: #1890ff;
  background: transparent;
  padding-left: 0;
  padding-right: 0;
  position: relative;
  top: 4px;
  font-size: 14px;
  margin-right: 10px;
}
</style>
