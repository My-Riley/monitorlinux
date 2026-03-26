<template>
  <div class="app-container">
    <el-row :gutter="20">
      <el-col :span="4" :xs="24">
        <div class="head-container">
          <el-input
            v-model="regionLabel"
            placeholder="请输入区域名称"
            clearable
            size="small"
            prefix-icon="el-icon-search"
            style="margin-bottom: 20px"
          />
        </div>
        <div class="head-container">
          <el-tree
            :data="regionOptions"
            :props="defaultProps"
            :expand-on-click-node="false"
            :filter-node-method="filterNode"
            ref="tree"
            node-key="id"
            default-expand-all
            highlight-current
            @node-click="handleNodeClick"
          />
        </div>
      </el-col>
      <el-col :span="20" :xs="24">
        <el-form
          :model="queryParams"
          ref="queryForm"
          size="small"
          :inline="true"
          v-show="showSearch"
          label-width="68px"
        >
          <el-form-item label="摄像头名称" prop="cameraName" label-width="100px">
            <el-input
              v-model="queryParams.cameraName"
              placeholder="请输入摄像头名称"
              clearable
              style="width: 240px"
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

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button
              type="primary"
              plain
              icon="el-icon-plus"
              size="mini"
              @click="handleAdd"
              v-hasPermi="['camera:camera:add']"
            >新增</el-button>
          </el-col>

          <el-col :span="1.5">
            <el-button
              type="danger"
              plain
              icon="el-icon-delete"
              size="mini"
              :disabled="multiple"
              @click="handleDelete"
              v-hasPermi="['camera:camera:remove']"
            >删除</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button
              type="info"
              plain
              icon="el-icon-upload2"
              size="mini"
              @click="handleImport"
              v-hasPermi="['camera:camera:import']"
            >导入</el-button>
          </el-col>

          <right-toolbar
            :showSearch.sync="showSearch"
            @queryTable="getList"
          ></right-toolbar>
        </el-row>

        <el-table
          v-loading="loading"
          :data="cameraList"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="摄像头名称" align="center" prop="cameraName" />
          <!-- <el-table-column
            label="摄像头状态"
            align="center"
            prop="cameraStatus"
          >
            <template slot-scope="scope">
              <el-tag
                :type="scope.row.cameraStatus == 0 ? 'success' : 'danger'"
              >{{ scope.row.cameraStatus == 0 ? "开启" : "关闭" }}</el-tag>
            </template>
          </el-table-column> -->

          <el-table-column
            label="摄像头IP"
            align="center"
            prop="ipAddr"
          ></el-table-column>
          <el-table-column
            label="摄像头端口"
            align="center"
            prop="port"
          ></el-table-column>
          <el-table-column
            label="RTSP端口"
            align="center"
            prop="rtspPort"
          ></el-table-column>
          <el-table-column
            label="摄像头登录名"
            align="center"
            prop="username"
          ></el-table-column>

          <el-table-column
            label="操作"
            align="center"
            class-name="small-padding fixed-width"
          >
            <template slot-scope="scope">
              <el-button
                size="mini"
                type="text"
                icon="el-icon-edit"
                @click="handleUpdate(scope.row)"
                v-hasPermi="['camera:camera:edit']"
              >修改</el-button>
              <el-button
                size="mini"
                type="text"
                icon="el-icon-delete"
                @click="handleDelete(scope.row)"
                v-hasPermi="['camera:camera:remove']"
              >删除</el-button>
              <el-button
                size="mini"
                type="text"
                icon="el-icon-view"
                @click="text(scope.row)"
              >预览</el-button>
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
        <el-dialog
          :title="upload.title"
          :visible.sync="upload.open"
          width="400px"
          append-to-body
        >
          <el-upload
            ref="upload"
            :limit="1"
            accept=".xlsx, .xls"
            :headers="headers"
            :action="upload.url + '?updateSupport=' + (upload.updateSupport ? 1 : 0)"
            :disabled="upload.isUploading"
            :on-progress="handleFileUploadProgress"
            :on-success="handleFileSuccess"
            :auto-upload="false"
            drag
          >
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <div class="el-upload__tip text-center" slot="tip">
              <div class="el-upload__tip">
                <el-checkbox v-model="upload.updateSupport" />
                是否更新已经存在的摄像头数据
              </div>
              <span>仅允许导入 xls、xlsx 格式文件。</span>
              <el-link
                type="primary"
                :underline="false"
                style="font-size: 12px; vertical-align: baseline"
                @click="downloadTemplate"
              >下载模板</el-link>
            </div>
          </el-upload>
          <div slot="footer" class="dialog-footer">
            <el-button type="primary" @click="submitFileForm">确 定</el-button>
            <el-button @click="upload.open = false">取 消</el-button>
          </div>
        </el-dialog>
      </el-col>
    </el-row>

    <el-dialog :title="title" :visible.sync="open" width="680px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="110px">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="区域" prop="regionId">
              <treeselect
                v-model="form.regionId"
                :options="communityOptions"
                :show-count="true"
                placeholder="请选择区域"
                @input="riskPersonDeptChangeValue"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="摄像头名称" prop="cameraName">
              <el-input v-model="form.cameraName" placeholder="请输入摄像头名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="登录账号" prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入摄像头登录名"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              label="登录密码"
              prop="password"
            >
              <el-input
                v-model="form.password"
                placeholder="请输入登录密码"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="摄像头IP" prop="ipAddr">
              <el-input v-model="form.ipAddr" placeholder="请输入摄像头IP" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              label="RTSP端口"
              prop="rtspPort"
            >
              <el-input
                v-model="form.rtspPort"
                placeholder="请输入RTSP端口"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="摄像头端口" prop="port">
              <el-input v-model="form.port" placeholder="请输入摄像头端口" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="摄像头品牌" prop="brand">
              <el-select v-model="form.brand" placeholder="请选择摄像头品牌" @change="onBrandChange" style="width: 100%">
                <el-option label="海康" value="海康" />
                <el-option label="大华" value="大华" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="24">
            <el-form-item label="RTSP协议路径" prop="protocol">
              <el-input v-model="form.protocol" placeholder="如: /Streaming/Channels/1" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>
    <el-dialog
      title="监控画面"
      :visible.sync="formSwitch"
      width="1080px"
      append-to-body
      @close="stopStream"
    >
      <div style="height: 535px;">
        <img v-if="videoSrc" :src="videoSrc" alt="Camera Stream" style="width: 100%; height: 100%;" />
        <div v-else style="text-align: center; padding: 50px; color: #999;">
          正在加载视频流...
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  listCamera,
  getCamera,
  delCamera,
  addCamera,
  updateCamera,
  getCameraByRegionId,
  importTemplate
} from "@/api/camera/camera";
import { treeRegion } from "@/api/camera/region";
import { WebVideo } from "./webVideo.js";
import Treeselect from "@riophae/vue-treeselect";
import "@riophae/vue-treeselect/dist/vue-treeselect.css";
import config, { pythonIP } from "@/config/index.js";
import { getToken } from "@/utils/auth";
export default {
  name: "CameraIndex",
  components: {
    Treeselect,
  },

  data() {
    return {
      upload: {
        open: false,
        title: "摄像头导入",
        isUploading: false,
        updateSupport: false,
        url: process.env.VUE_APP_BASE_API + "/camera/camera/upload",
      },
      headers: {
        Authorization: "Bearer " + getToken()
      },
      pythonIP: config.pythonIP,
      videoSrc: "",
      loading: true,
      ids: [],
      formSwitch: false,
      single: true,
      multiple: true,
      showSearch: true,
      total: 0,
      cameraList: [],
      title: "",
      open: false,
      communityOptions: [],
      regionOptions: [],
      defaultProps: {
        children: "children",
        label: "label",
      },
      regionLabel: "",
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        liftName: null,
        regionId: null,
        status: null,
        cameraRtsp: null,
        del: null,
        port: 80,
        password: null,
        cameraName: null,
        cameraIP: null,
      },
      form: {},
      rules: {
        deptId: [
          { required: true, message: "请选择区域", trigger: "change" },
        ],
        cameraName: [
          { required: true, message: "摄像头登录名不能为空", trigger: "blur" },
        ],
        password: [
          { required: true, message: "登录密码不能为空", trigger: "blur" },
        ],
        port: [
          { required: true, message: "摄像头端口不能为空", trigger: "blur" },
        ],
        liftName: [
          { required: true, message: "摄像头名称不能为空", trigger: "blur" },
        ],
        status: [
          { required: true, message: "摄像头状态不能为空", trigger: "change" },
        ],
        createTime: [
          { required: true, message: "创建时间不能为空", trigger: "blur" },
        ],
        ipAddr: [
          { required: true, message: "摄像头IP不能为空", trigger: "blur" },
        ],
        cameraRtspPort: [
          { required: true, message: "RTSP端口不能为空", trigger: "blur" },
        ],
      },
    };
  },

  created() {
    this.webVideo = new WebVideo();
    this.getList();
    this.getRegionTreeData();
  },

  watch: {
    /** 根据名称筛选小区树 */
    regionLabel(val) {
      this.$refs.tree.filter(val);
    },
  },

  methods: {
    /** 预览摄像头视频流 */
    text(row) {
      this.videoSrc = "";
      this.formSwitch = true;
      this.loading = true;

      const protocol = row.protocol || '/Streaming/Channels/1';
      const rtspUrl = `rtsp://${row.username}:${row.password}@${row.ipAddr}:${row.rtspPort}${protocol}`;

      // 这样可以确保在局域网访问时，视频流请求也指向正确的服务器 IP
      const hostname = window.location.hostname;
      const currentPythonIP = `${hostname}:5001`;
          
      this.videoSrc = `http://${currentPythonIP}/video_feed?url=${encodeURIComponent(rtspUrl)}&t=${Date.now()}`;
      this.loading = false;
    },

    /** 停止视频流 */
    stopStream() {
      this.videoSrc = "";
    },

    /** 区域选择变化时触发表单校验 */
    riskPersonDeptChangeValue() {
      this.$refs["form"].validateField("deptId");
    },

    /** 摄像头品牌变化时自动填充RTSP协议路径 */
    onBrandChange(brand) {
      if (brand === '海康') {
        this.form.protocol = '/Streaming/Channels/1';
      } else if (brand === '大华') {
        this.form.protocol = '/cam/realmonitor?channel=1&subtype=0';
      } else if (brand === '其他') {
        this.form.protocol = '';
      }
    },
    /** 查询摄像头列表 */
    getList() {
      this.loading = true;
      listCamera(this.queryParams).then((response) => {
        this.cameraList = response.rows.map((item) => {
          item.rtspUrl =
            "rtsp://" +
            item.username +
            ":" +
            item.password +
            "@" +
            item.ipAddr +
            ":" +
            item.rtspPort +
            "/h264/ch1/main/av_stream";
          item.videoUrl = "";
          if (item.ipAddr) {
            const ipParts = item.ipAddr.split(".");
            if (ipParts.length >= 4) {
              item.videoUrl =
                "http://" +
                this.pythonIP +
                ":8083/stream/" +
                ipParts[2] +
                ipParts[3];
            }
          }
          return item;
        });
        this.total = response.total;
        this.loading = false;
      });
    },
    /** 获取区域树结构数据 */
    getRegionTreeData() {
      treeRegion().then((response) => {
        this.regionOptions = response.data;
        this.communityOptions = response.data;
      });
    },
    /** 筛选树节点 */
    filterNode(value, data) {
      if (!value) return true;
      return data.label.indexOf(value) !== -1;
    },
    /** 处理树节点点击事件，根据选择的区域查询摄像头 */
    handleNodeClick(node) {
      const regionId = node.id;
      getCameraByRegionId(regionId).then((response) => {
        this.cameraList = response.data;
      });
    },

    /** 取消按钮操作 */
    cancel() {
      this.open = false;
      this.reset();
    },
    /** 表单重置 */
    reset() {
      this.form = {
        cameraId: null,
        cameraName: null,
        regionId: null,
        status: null,
        cameraRtsp: null,
        createTime: null,
        updateTime: null,
        del: null,
        port: 80,
        password: null,
        username: "",
        ipAddr: null,
        rtspPort: 554,
        brand: null,
        protocol: null,
      };
      this.resetForm("form");
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.getList();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.resetForm("queryForm");
      this.handleQuery();
    },
    /** 多选框选中数据变化 */
    handleSelectionChange(selection) {
      this.ids = selection.map((item) => item.cameraId);
      this.single = selection.length !== 1;
      this.multiple = !selection.length;
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加摄像头";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const id = row.cameraId || this.ids;
      getCamera(id).then((response) => {
        this.form = response.data;
        this.open = true;
        this.title = "修改摄像头";
      });
    },
    /** 提交表单 */
    submitForm() {
      this.$refs["form"].validate((valid) => {
        if (valid) {
          if (this.form.cameraId != null) {
            updateCamera(this.form).then((response) => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addCamera(this.form).then((response) => {
              this.$modal.msgSuccess("新增成功");
              this.open = false;
              this.getList();
            });
          }
        }
      });
    },
    /** 下载导入模板 */
    downloadTemplate() {
      importTemplate().then((response) => {
        const blob = new Blob([response], {
          type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        });
        const fileName = "摄像头导入模板.xlsx";
        if (window.navigator.msSaveOrOpenBlob) {
          navigator.msSaveBlob(blob, fileName);
        } else {
          const link = document.createElement("a");
          link.href = window.URL.createObjectURL(blob);
          link.download = fileName;
          link.click();
          window.URL.revokeObjectURL(link.href);
        }
      }).catch(() => {
        this.$message.error("下载模板失败");
      });
    },
    /** 文件上传进度处理 */
    handleFileUploadProgress(event, file, fileList) {
      this.upload.isUploading = true;
    },
    /** 文件上传成功处理 */
    handleFileSuccess(response, file, fileList) {
      this.upload.open = false;
      this.upload.isUploading = false;
      this.$refs.upload.clearFiles();
      this.$alert(
        "<div style='overflow: auto;overflow-x: hidden;max-height: 70vh;padding: 10px 20px 0;'>" +
          response.msg +
          "</div>",
        "导入结果",
        { dangerouslyUseHTMLString: true }
      );
      this.getList();
    },
    /** 提交上传文件 */
    submitFileForm() {
      this.$refs.upload.submit();
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const ids = row.cameraId || this.ids;
      this.$modal
        .confirm('是否确认删除电梯/摄像头编号为"' + ids + '"的数据项？')
        .then(function () {
          return delCamera(ids);
        })
        .then(() => {
          this.getList();
          this.$modal.msgSuccess("删除成功");
        })
        .catch(() => {});
    },
    /** 导入按钮操作 */
    handleImport() {
      this.upload.title = "摄像头导入";
      this.upload.open = true;
    },
  },
};
</script>
<style lang="scss" scoped>
.shexiangtou {
  height: 700px;
  width: 100%;
}

.cameraDiv {
  height: 100%;
  display: flex;
  justify-content: space-between;
}
video {
  width: 100%;
  height: 100%;
  object-fit: fill;
}
img {
  width: 100%;
  height: 100%;
}
::v-deep .el-dialog__body {
  padding: 30px 20px;
  color: #606266;
  font-size: 14px;
  word-break: break-all;
}
</style>
