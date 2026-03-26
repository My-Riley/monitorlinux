<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="预警名称" prop="warnName">
        <el-input
          v-model="queryParams.warnName"
          placeholder="请输入预警名称"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="预警级别" prop="warnLevel">
        <el-select v-model="queryParams.warnLevel" placeholder="请选择预警级别" clearable>
          <el-option label="低" value="1" />
          <el-option label="中" value="2" />
          <el-option label="高" value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
          <el-option label="未处理" value="0" />
          <el-option label="已处理" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
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
          v-hasPermi="['camera:warn:add']"
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
          v-hasPermi="['camera:warn:remove']"
        >删除</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="warnList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="预警ID" align="center" prop="warnId" />
      <el-table-column label="预警名称" align="center" prop="warnName" />
      <el-table-column label="预警级别" align="center" prop="warnLevel">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.warnLevel == '1'" type="success">低</el-tag>
          <el-tag v-else-if="scope.row.warnLevel == '2'" type="warning">中</el-tag>
          <el-tag v-else-if="scope.row.warnLevel == '3'" type="danger">高</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="预警内容" align="center" prop="warnContent" />
      <el-table-column label="摄像头名称" align="center" prop="cameraName" />
      <el-table-column label="预警时间" align="center" prop="warnTime" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.warnTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" prop="status">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.status == '0'" type="danger">未处理</el-tag>
          <el-tag v-else type="success">已处理</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['camera:warn:edit']"
          >修改/处理</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['camera:warn:remove']"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="queryParams.pageNum"
      :limit.sync="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改预警对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="预警名称" prop="warnName">
          <el-input v-model="form.warnName" placeholder="请输入预警名称" />
        </el-form-item>
        <el-form-item label="预警级别" prop="warnLevel">
          <el-select v-model="form.warnLevel" placeholder="请选择预警级别">
            <el-option label="低" value="1" />
            <el-option label="中" value="2" />
            <el-option label="高" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="预警内容" prop="warnContent">
          <el-input v-model="form.warnContent" type="textarea" placeholder="请输入预警内容" />
        </el-form-item>
        <el-form-item label="摄像头" prop="cameraName">
          <el-input v-model="form.cameraName" placeholder="请输入摄像头名称" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="0">未处理</el-radio>
            <el-radio label="1">已处理</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="处理结果" prop="handleResult" v-if="form.status == '1'">
          <el-input v-model="form.handleResult" type="textarea" placeholder="请输入处理结果" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" />
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
import { listWarn, getWarn, delWarn, addWarn, updateWarn } from "@/api/camera/warn";

export default {
  name: "Warn",
  data() {
    return {
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
      // 预警表格数据
      warnList: [],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        warnName: null,
        status: null,
        warnLevel: null,
      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        warnName: [
          { required: true, message: "预警名称不能为空", trigger: "blur" }
        ],
        warnLevel: [
          { required: true, message: "预警级别不能为空", trigger: "change" }
        ],
      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询预警列表 */
    getList() {
      this.loading = true;
      listWarn(this.queryParams).then(response => {
        this.warnList = response.rows;
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
        warnId: null,
        warnName: null,
        warnLevel: null,
        warnContent: null,
        cameraName: null,
        status: "0",
        handleResult: null,
        remark: null
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
      this.ids = selection.map(item => item.warnId)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加预警";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const warnId = row.warnId || this.ids
      getWarn(warnId).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改预警";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.warnId != null) {
            updateWarn(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addWarn(this.form).then(response => {
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
      const warnIds = row.warnId || this.ids;
      this.$modal.confirm('是否确认删除预警编号为"' + warnIds + '"的数据项？').then(function() {
        return delWarn(warnIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    }
  }
};
</script>
