<template>
  <div class="app-container">
    <el-form
      :model="queryParams"
      ref="queryForm"
      size="small"
      :inline="true"
      v-show="showSearch"
      label-width="68px"
    >
      <el-form-item label="姓名" prop="studentName">
        <el-input
          v-model="queryParams.studentName"
          placeholder="请输入姓名"
          clearable
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
          type="danger"
          plain
          icon="el-icon-delete"
          size="mini"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['system:results:remove']"
        >删除</el-button>
      </el-col>

      <right-toolbar
        :showSearch.sync="showSearch"
        @queryTable="getList"
      ></right-toolbar>
    </el-row>

    <el-table
      v-loading="loading"
      :data="resultsList"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" align="center" />

      <el-table-column label="姓名" align="center" prop="studentName" />
      <el-table-column label="学号" align="center" prop="studentId" />
      <el-table-column label="年级" align="center" prop="grade" />
      <el-table-column label="班级" align="center" prop="classes" />
      <el-table-column label="摄像头编号" align="center" prop="cameraName" />
      <el-table-column label="情绪" align="center" prop="emotion" width="120px">
        <template slot-scope="scope">
          <el-tag :style="scope.row.emotion">
            <!-- {{ gscope.row.emotion }} -->
            {{ getEmotionLabel(scope.row.emotion) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="地点" align="center" prop="address" />
      <el-table-column label="情绪图片" align="center" prop="url" width="120">
        <template #default="{ row }">
          <div v-if="row.url">
            <div v-for="(v, i) in row.url.split(',')" :key="i">
              <el-image
                :src="baseUrl + v"
                :preview-src-list="row.url.split(',').map((v1) => baseUrl + v1)"
              ></el-image>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        label="创建时间"
        align="center"
        prop="createTime"
        width="180"
      >
        <template slot-scope="scope">
          <span>
            <!-- {{
            parseTime(scope.row.createTime, "{y}-{m}-{d} {h}:{m}:{s}")
          }} -->
            {{ scope.row.createTime }}
          </span>
        </template>
      </el-table-column>

      <el-table-column
        label="操作"
        align="center"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['system:results:remove']"
          >删除</el-button>
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

    <!-- 添加或修改情绪情对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="情绪" prop="emotion">
          <el-input v-model="form.emotion" placeholder="请输入情绪" />
        </el-form-item>
        <el-form-item label="姓名" prop="studentName">
          <el-input v-model="form.studentName" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item label="创建时间" prop="createTime">
          <el-date-picker
            clearable
            v-model="form.createTime"
            type="date"
            value-format="yyyy-MM-dd"
            placeholder="请选择创建时间"
          >
          </el-date-picker>
        </el-form-item>
        <el-form-item label="图片" prop="url">
          <el-input v-model="form.url" placeholder="请输入图片" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  listFocus,
  getResults,
  delResults,
  addResults,
  updateResults,
} from "@/api/aberrantEmotions";

export default {
  name: "Results",
  data() {
    return {
      baseUrl: process.env.VUE_APP_BASE_API,
      // 遮罩层
      loading: true,
      // 选中数组
      ids: [],
      // 非单个禁用
      single: true,
      // 非多个禁用
      multiple: true,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // 情绪情表格数据
      resultsList: [],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        status: null,
        message: null,
        imageId: null,
        emotion: null,
        studentName: null,
        studentId: null,
        imageData: null,
        createTime: null,
        url: null,
      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        status: [
          { required: true, message: "状态不能为空", trigger: "change" },
        ],
        imageId: [
          { required: true, message: "用户id不能为空", trigger: "blur" },
        ],
        emotion: [{ required: true, message: "情绪不能为空", trigger: "blur" }],
        imageName: [
          { required: true, message: "姓名不能为空", trigger: "blur" },
        ],
        personNumber: [
          { required: true, message: "版本不能为空", trigger: "blur" },
        ],
      },
    };
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询情绪情列表 */
    getList() {
      this.loading = true;
      listFocus(this.queryParams).then((response) => {
        this.resultsList = response.rows;
        this.total = response.total;
        this.loading = false;
      });
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    // 表单重置
    reset() {
      this.form = {
        id: null,
        status: null,
        message: null,
        imageId: null,
        emotion: null,
        studentName: null,
        studentId: null,
        imageData: null,
        createTime: null,
        url: null,
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
    // 多选框选中数据
    handleSelectionChange(selection) {
      this.ids = selection.map((item) => item.id);
      this.single = selection.length !== 1;
      this.multiple = !selection.length;
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加情绪情";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const id = row.id || this.ids;
      getResults(id).then((response) => {
        this.form = response.data;
        this.open = true;
        this.title = "修改情绪情";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate((valid) => {
        if (valid) {
          if (this.form.id != null) {
            updateResults(this.form).then((response) => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addResults(this.form).then((response) => {
              this.$modal.msgSuccess("新增成功");
              this.open = false;
              this.getList();
            });
          }
        }
      });
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const ids = row.id || this.ids;
      this.$modal
        .confirm('是否确认删除情绪情编号为"' + ids + '"的数据项？')
        .then(function () {
          return delResults(ids);
        })
        .then(() => {
          this.getList();
          this.$modal.msgSuccess("删除成功");
        })
        .catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download(
        "system/results/export",
        {
          ...this.queryParams,
        },
        `results_${new Date().getTime()}.xlsx`
      );
    },
    getTagStyle(emotion) {
      const emotionStyles = {
        neutral: { backgroundColor: "#e0e0e0", color: "#000" },
        happiness: { backgroundColor: "#64b5f6", color: "#fff" },
        surprise: { backgroundColor: "#ffeb3b", color: "#000" },
        sadness: { backgroundColor: "#90caf9", color: "#000" },
        anger: { backgroundColor: "#e57373", color: "#fff" },
        disgust: { backgroundColor: "#f44336", color: "#fff" },
        fear: { backgroundColor: "#ff9800", color: "#fff" },
        contempt: { backgroundColor: "#9e9e9e", color: "#fff" },
        unknown: { backgroundColor: "#9c27b0", color: "#fff" },
      };
      return emotionStyles[emotion] || {};
    },
    // 根据情绪类型返回对应的标签文本
    getEmotionLabel(emotion) {
      const emotionLabels = {
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
      return emotionLabels[emotion] || "未知";
    },
  },
};
</script>
<style scoped>
::v-deep .el-image__preview {
  cursor: s-resize;
  width: 50px;
  height: 50px;
}
</style>
