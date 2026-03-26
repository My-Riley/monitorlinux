<template>
  <div class="app-container">
    <!-- 搜索表单 -->
    <el-form
      :model="queryParams"
      ref="queryForm"
      size="small"
      :inline="true"
      v-show="showSearch"
      label-width="68px"
    >
      <el-form-item label="班级" prop="classes">
        <el-select
          v-model="queryParams.classes"
          placeholder="请选择班级"
          filterable
          clearable
          style="width: 240px"
          @change="handleQuery"
        >
          <el-option
            v-for="item in classOptions"
            :key="item.classId"
            :label="item.className"
            :value="item.classId"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="学号" prop="studentId">
        <el-autocomplete
          v-model="queryParams.studentId"
          :fetch-suggestions="querySearchStudentId"
          placeholder="输入学号关键词（如：2025）"
          clearable
          style="width: 240px"
          @keyup.enter.native="handleQuery"
          @select="handleSelectStudentId"
          :trigger-on-focus="false"
          :debounce="300"
          popper-class="student-id-suggestion-popper"
        >
          <template #default="{ item }">
            <div class="student-suggestion">
              <span>{{ item.studentId }}</span>
              <small style="color: #999; margin-left: 8px">{{ item.studentName }}</small>
            </div>
          </template>
        </el-autocomplete>
      </el-form-item>
      <el-form-item label="学生姓名" prop="studentName">
        <el-autocomplete
          v-model="queryParams.studentName"
          :fetch-suggestions="querySearch"
          placeholder="输入姓名关键词（如：小明）"
          clearable
          @select="handleSelectStudent"
          style="width: 240px"
          :trigger-on-focus="false"
          :debounce="300"
        >
          <template #default="{ item }">
            <div class="student-suggestion">
              <span>{{ item.studentName }}</span>
            </div>
          </template>
        </el-autocomplete>
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

    <!-- 工具栏 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="el-icon-plus"
          size="mini"
          @click="handleAdd"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="el-icon-delete"
          size="mini"
          :disabled="multiple"
          @click="handleDelete()"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="el-icon-upload2"
          size="mini"
          @click="handleImport"
        >导入</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="el-icon-download"
          size="mini"
          @click="handleExport"
        >导出</el-button>
      </el-col>
      <right-toolbar
        :showSearch.sync="showSearch"
        @queryTable="getList"
      ></right-toolbar>
    </el-row>

    <!-- 学生列表表格 -->
    <el-table
      v-loading="loading"
      :data="studentList"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="50" align="center" />

      <el-table-column label="年级" align="center" prop="grade" />
      <el-table-column label="班级" align="center" prop="classes" />
      <el-table-column
        label="学生姓名"
        align="center"
        prop="studentName"
        :show-overflow-tooltip="true"
      />
      <el-table-column label="性别" align="center" prop="sex">
        <template slot-scope="scope">
          <span>{{ scope.row.sex === '0' ? '男' : scope.row.sex === '1' ? '女' : '未知' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="年龄" align="center" prop="age" />
      <el-table-column label="学号" align="center" prop="studentId" />
      <el-table-column
        label="人脸图片"
        align="center"
        prop="faceImage"
        width="120"
      >
        <template #default="{ row }">
          <div v-if="row.faceImage">
            <div v-for="(v, i) in row.faceImage.split(',')" :key="i">
              <el-image
                :src="baseUrl + v"
                :preview-src-list="
                  row.faceImage.split(',').map((v1) => baseUrl + v1)
                "
              >
                <div slot="error" class="image-slot">
                  <i class="el-icon-picture-outline" style="font-size: 20px; color: #909399;"></i>
                </div>
              </el-image>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column
        label="创建时间"
        align="center"
        prop="createTime"
        width="160"
      >
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column
        label="操作"
        align="center"
        width="160"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-edit"
            @click="handleUpdate(scope.row)"
          >修改</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="queryParams.pageNum"
      :limit.sync="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改学生对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="600px" append-to-body class="user-edit-dialog">
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="学生姓名" prop="studentName">
              <el-input
                v-model="form.studentName"
                placeholder="请输入学生姓名"
                maxlength="10"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学生年龄" prop="age">
              <el-input-number v-model="form.age" :min="1" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="学生性别" prop="sex">
              <el-select v-model="form.sex" placeholder="请选择性别" style="width: 100%">
                <el-option label="男" value="0"></el-option>
                <el-option label="女" value="1"></el-option>
                <el-option label="未知" value="2"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学生年级" prop="grade">
              <el-input v-model="form.grade" placeholder="请输入学生年级" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="学生班级" prop="classes">
              <el-input v-model="form.classes" placeholder="请输入班级（如：2501班）" @blur="cleanClassInput" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学生学号" prop="studentId">
              <el-input
                v-model="form.studentId"
                placeholder="请输入学生学号"
                maxlength="20"
                @keypress="onlyNumber"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="人脸图片" prop="faceImage">
              <el-upload
                :action="computedUploadUrl"
                list-type="picture-card"
                :show-file-list="true"
                :file-list="fileList"
                :limit="1"
                :multiple="false"
                :headers="headers"
                :on-error="handleUploadError"
                :on-success="handleUploadSuccess"
                :on-preview="handlePictureCardPreview"
                :before-upload="beforeUpload"
              >
                <i class="el-icon-plus"></i>
              </el-upload>
              <el-dialog :visible.sync="dialogVisible" append-to-body>
                <img width="100%" :src="dialogImageUrl" />
              </el-dialog>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>

    <!-- 导入对话框 -->
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
          <div class="el-upload__tip" slot="tip">
            <el-checkbox v-model="upload.updateSupport" />
            是否更新已经存在的学生数据
          </div>
          <span>仅允许导入xls、xlsx格式文件。</span>
          <el-link
            type="primary"
            :underline="false"
            style="font-size: 12px; vertical-align: baseline"
            @click="importTemplate"
          >下载模板</el-link>
        </div>
      </el-upload>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitFileForm">确 定</el-button>
        <el-button @click="upload.open = false">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  listStudent,
  getClassList,
  searchStudents,
  searchStudentIds,
  addStudent,
  updateStudent,
  delStudent,
  exportStudent,
  importTemplate as downloadImportTemplate,
} from "@/api/system/student";
import { getToken } from "@/utils/auth";
import request from "@/utils/request";

export default {
  name: "Student",
  data() {
    return {
      // 基础配置
      baseUrl: process.env.VUE_APP_BASE_API,
      loading: true,
      showSearch: true,
      total: 0,
      studentList: [],
      ids: [],
      single: true,
      multiple: true,

      // 班级选项
      classOptions: [],

      // 表单相关
      open: false,
      title: "",
      form: {},
      rules: {
        studentName: [
          { required: true, message: "学生姓名不能为空", trigger: "blur" },
          { min: 1, max: 10, message: "长度必须在1～10之间", trigger: "blur" }
        ],
        sex: [{ required: true, message: "学生性别不能为空", trigger: "blur" }],
        age: [{ required: true, message: "学生年龄不能为空", trigger: "blur" }],
        grade: [
          { required: true, message: "学生年级不能为空", trigger: "blur" },
          { max: 10, message: "年级不能超过10个字符", trigger: "blur" }
      ],
        classes: [
          { required: true, message: "学生班级不能为空", trigger: "blur" },
          { pattern: /^\d{4}班$/, message: "格式错误，如：2501班", trigger: "blur" }
        ],
        studentId: [
          { required: true, message: "学生学号不能为空", trigger: "blur" },
          {
            pattern: /^\d{1,20}$/,
            message: "学号必须为1-20位纯数字",
            trigger: "blur"
          }
        ],
        faceImage: [{ required: true, message: "人脸图片不能为空", trigger: "blur" }]
      },

      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        classes: undefined,
        studentId: '',
        studentName: '',
      },

      // 图片上传
      fileList: [],
      dialogVisible: false,
      dialogImageUrl: "",

      // 导入
      upload: {
        open: false,
        title: "",
        isUploading: false,
        updateSupport: false,
        url: process.env.VUE_APP_BASE_API + "/system/student/import"
      },
      headers: { Authorization: "Bearer " + getToken() },
    };
  },
  computed: {
    computedUploadUrl() {
      const baseUrl = process.env.VUE_APP_BASE_API + "/common/upload";
      const params = [];
      if (this.form.studentName) params.push(`userName=${encodeURIComponent(this.form.studentName)}`);
      if (this.form.studentId) params.push(`studentId=${encodeURIComponent(this.form.studentId)}`);
      return params.length ? `${baseUrl}?${params.join('&')}` : baseUrl;
    }
  },
  created() {
    this.getList();
    this.loadClassList();
  },
  methods: {
    // 加载班级
    loadClassList() {
      getClassList().then(response => {
        const list = Array.isArray(response.data) ? response.data : [];
        this.classOptions = list
          .filter(i => i && i.classId != null && i.className != null)
          .slice()
          .sort((a, b) => String(a.className).localeCompare(String(b.className), 'zh-Hans-CN'));
      });
    },

    // 搜索建议
    querySearch(queryString, cb) {
      if (!queryString?.trim()) return cb([]);
      searchStudents(queryString.trim()).then(res => {
        cb((res.data || []).map(item => ({ value: item.studentName, ...item })));
      }).catch(() => cb([]));
    },
    querySearchStudentId(queryString, cb) {
      if (!queryString?.trim()) return cb([]);
      searchStudentIds(queryString.trim()).then(res => {
        cb((res.data || []).map(item => ({ value: String(item.studentId), ...item })));
      }).catch(() => cb([]));
    },

    handleSelectStudent(item) {
      this.handleQuery();
    },
    handleSelectStudentId(item) {
      this.queryParams.studentId = item.studentId;
      this.handleQuery();
    },

    cleanClassInput() {
      if (this.form.classes) {
        this.form.classes = this.form.classes.replace(/\s+/g, '');
      }
    },

    // 数据操作
    getList() {
      this.loading = true;
      listStudent(this.queryParams).then(response => {
        this.studentList = response.rows;
        this.total = response.total;
        this.loading = false;
      });
    },
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.getList();
    },
    resetQuery() {
      this.resetForm("queryForm");
      this.handleQuery();
    },
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.studentId);
      this.single = selection.length !== 1;
      this.multiple = selection.length === 0;
    },

    // 新增/编辑
    handleAdd() {
      this.reset();
      this.fileList = [];
      this.open = true;
      this.title = "添加学生";
    },
    handleUpdate(row) {
      this.open = true;
      this.title = "修改学生信息";
      this.form = { ...row };
      if (row.faceImage) {
        this.fileList = row.faceImage.split(",").map((img, i) => ({
          name: `图片${i + 1}`,
          url: this.baseUrl + img
        }));
      } else {
        this.fileList = [];
      }
    },
    onlyNumber(event) {
    // 允许数字、退格、删除、方向键等
    const keyCode = event.keyCode || event.which;
    if (
      (keyCode >= 48 && keyCode <= 57) || // 主键盘数字
      (keyCode >= 96 && keyCode <= 105) || // 小键盘数字
      [8, 9, 37, 39, 46].includes(keyCode) // 退格、Tab、方向键、删除
    ) {
      return true;
    }
    event.preventDefault();
    return false;
  },
    reset() {
      this.form = {
        id: undefined,
        studentId: '',
        studentName: undefined,
        classes: undefined,
        grade: undefined,
        sex: undefined,
        age: undefined,
        faceImage: undefined,
        status: "0",
        remark: undefined
      };
      this.resetForm("form");
    },
    cancel() {
      // 如果是新增操作（非编辑），且已上传图片，删除未保存的图片
      if (!this.form.id && this.form.faceImage) {
        const imagePaths = this.form.faceImage.split(',').filter(path => path && path.trim());
        imagePaths.forEach(imagePath => {
          if (imagePath) {
            // 调用后端接口删除图片
            request({
              url: '/common/deleteImage',
              method: 'post',
              data: { imagePath: imagePath.trim() }
            }).catch(err => {
              console.warn('删除图片失败:', err);
              // 删除失败不影响取消操作，只记录警告
            });
          }
        });
      }
      // 清空文件列表
      this.fileList = [];
      this.open = false;
      this.reset();
    },
    submitForm() {
      this.$refs.form.validate(valid => {
        if (valid) {
          // const payload = { ...this.form };
          // // 如果 studentId 是字符串，转成数字再提交
          // if (typeof payload.studentId === 'string') {
          //   payload.studentId = parseInt(payload.studentId, 10);
          // }
          const api = this.form.id ? updateStudent : addStudent;
          api(this.form).then(() => {
            this.$modal.msgSuccess(this.form.id ? "修改成功" : "新增成功");
            this.open = false;
            this.getList();
            this.loadClassList();
          });
        }
      });
    },

    // 删除
    handleDelete(row) {
      // 获取原始 ID 列表
      const rawIds = row ? [row.studentId] : this.ids;
      // 过滤掉 null, undefined, 空字符串, 以及非数字值
      const validIds = rawIds.filter(id => id != null && id !== '');

      if (validIds.length === 0) {
        this.$message.warning("请选择有效的学生进行删除");
        return;
      }
      this.$modal.confirm(`是否确认删除学号为 "${validIds.join(', ')}" 的学生？`).then(() => {
        return delStudent(validIds.join(','));
      }).then(() => {
        this.getList();
        this.loadClassList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },

    // 导出
    handleExport() {
      exportStudent().then(response => {
        // 创建 blob 并触发下载
        const blob = new Blob([response], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `student_list_${new Date().getTime()}.xlsx`;
        link.click();
        URL.revokeObjectURL(link.href);
      }).catch(() => {
        this.$message.error('导出失败');
      });
    },

    // 导入
    handleImport() {
      this.upload.title = "学生导入";
      this.upload.open = true;
    },
    importTemplate() {
      downloadImportTemplate().then(response => {
        const blob = new Blob([response], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "学生导入模板.xlsx";
        link.click();
        URL.revokeObjectURL(link.href);
      }).catch(() => {
        this.$message.error("下载模板失败");
      });
    },
    handleFileUploadProgress() {
      this.upload.isUploading = true;
    },
    handleFileSuccess(response) {
      this.upload.open = false;
      this.upload.isUploading = false;
      this.$refs.upload.clearFiles();
      this.$alert(response.msg || "导入完成", "导入结果", { dangerouslyUseHTMLString: true });
      this.loadClassList();
      this.getList();
    },
    submitFileForm() {
      this.$refs.upload.submit();
    },

    // 图片上传
    beforeUpload(file) {
      if (!this.form.studentName) {
        this.$message.warning("请先填写学生姓名");
        return false;
      }
      if (!this.form.studentId) {
        this.$message.warning("请先填写学生学号");
        return false;
      }
      if (!this.form.classes) {
        this.$message.warning("请先填写学生班级");
        return false;
      }
      return true;
    },
    handleUploadSuccess(response, file, fileList) {
      this.form.faceImage = fileList
        .map(f => f.response ? f.response.fileName : f.url)
        .join(",");
    },
    handleUploadError() {
      this.$message.error("图片上传失败，请重试");
    },
    handlePictureCardPreview(file) {
      this.dialogImageUrl = file.url;
      this.dialogVisible = true;
    }
  }
};
</script>

<style scoped>
::v-deep .el-image__preview {
  cursor: s-resize;
  width: 50px;
  height: 50px;
}
.student-suggestion {
  padding: 4px 10px;
  line-height: 1.5;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
::v-deep .student-id-suggestion-popper {
  min-width: 320px !important;
}
::v-deep .student-id-suggestion-popper li {
  white-space: normal;
}
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
}
</style>
