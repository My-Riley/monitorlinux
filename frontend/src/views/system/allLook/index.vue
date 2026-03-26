<template>
  <div class="app-container">
    <el-form
      :model="queryParams"
      ref="queryForm"
      size="small"
      :inline="true"
      v-show="showSearch"
      label-width="50px"
      class="search-form"
    >
      <el-form-item label="姓名" prop="studentName">
        <el-input
          v-model="queryParams.studentName"
          placeholder="请输入学生姓名"
          clearable
          style="width: 150px"
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="学号" prop="Student">
        <el-input
          v-model="queryParams.Student"
          placeholder="请输入学号"
          clearable
          style="width: 150px"
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="班级" prop="className">
        <el-select
          v-model="queryParams.className"
          placeholder="请选择班级"
          clearable
          filterable
          style="width: 150px"
          @change="handleQuery"
        >
          <el-option
            v-for="item in classOptions"
            :key="item.classId"
            :label="item.className"
            :value="item.className"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="检测时间" label-width="68px">
        <el-date-picker
          v-model="dateRange"
          style="width: 210px"
          value-format="yyyy-MM-dd"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
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
          @click="handleBatchDelete"
          v-hasPermi="['system:results:remove']"
        >批量删除</el-button>
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
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table
      v-loading="loading"
      :data="resultsList"
      @selection-change="handleSelectionChange"
      style="width: 100%"
    >
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="姓名" align="center" prop="studentName" min-width="50" />
      <el-table-column label="学号" align="center" prop="studentId" min-width="50" />
      <el-table-column label="班级" align="center" prop="className" min-width="50" />
      <el-table-column label="设备ID号" align="center" prop="cameraIp" min-width="70" show-overflow-tooltip />
      <el-table-column label="情绪" align="center" prop="emotion" min-width="50">
        <template slot-scope="scope">
          <el-tag :style="getTagStyle(scope.row.emotion)">
            {{ getEmotionLabel(scope.row.emotion) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="抓拍人脸图片" align="center" width="240">
        <template slot-scope="scope">
          <el-image
            v-if="scope.row.imageBase64"
            :src="getImageSrc(scope.row.imageBase64)"
            :preview-src-list="[getImageSrc(scope.row.imageBase64)]"
            style="width: 80px; height: 80px; border-radius: 4px;"
            fit="cover"
            lazy
          />
          <span v-else style="color: #909399; font-size: 12px">无图片</span>
        </template>
      </el-table-column>
      <el-table-column label="检测时间" align="center" prop="createTime" width="240">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
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
  </div>
</template>

<script>
import { listResults, delResults, exportResults } from "@/api/aberrantEmotions";
import { getClassList } from "@/api/system/student";
import websocketMixin from "@/utils/mixins/websocketMixin";

export default {
  name: "AllLook",
  mixins: [websocketMixin],
  data() {
    return {
      // 遮罩层
      loading: true,
      // 选中数组
      ids: [],
      // 非多个禁用
      multiple: true,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // 表格数据
      resultsList: [],
      // 班级选项
      classOptions: [],
      // 日期范围
      dateRange: [],
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        studentName: undefined,
        studentId: undefined,
        className: undefined,
      },
    };
  },
  created() {
    this.getList();
    this.loadClassList();
  },
  methods: {
    /** 查询检测记录列表 */
    getList() {
      this.loading = true;

      const params = {
        ...this.queryParams,
        beginTime: this.dateRange && this.dateRange[0],
        endTime: this.dateRange && this.dateRange[1],
      };

      listResults(params).then((response) => {
        this.resultsList = response.rows || [];
        this.total = response.total || 0;
        this.loading = false;
      }).catch(() => {
        this.loading = false;
      });
    },
    /** 获取班级列表 */
    async loadClassList() {
      try {
        const response = await getClassList();
        this.classOptions = (response.data || []).filter(
          (i) => i && i.className
        ).sort((a, b) =>
          String(a.className).localeCompare(String(b.className), 'zh-Hans-CN')
        );
      } catch (e) {
        console.error("获取班级列表失败", e);
      }
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.getList();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.dateRange = [];
      this.resetForm("queryForm");
      this.handleQuery();
    },
    /** 多选框选中数据 */
    handleSelectionChange(selection) {
      this.ids = selection.map((item) => item.resultId);
      this.multiple = !selection.length;
    },
    /** 批量删除操作 */
    handleBatchDelete() {
      const ids = this.ids;
      this.$modal.confirm('是否确认删除检测记录编号为"' + ids + '"的数据项？').then(function() {
        return delResults(ids.join(","));
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      const params = {
        ...this.queryParams,
        beginTime: this.dateRange && this.dateRange[0],
        endTime: this.dateRange && this.dateRange[1],
      };
      exportResults(params).then(response => {
        const blob = new Blob([response], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `检测记录_${new Date().getTime()}.xlsx`;
        link.click();
        URL.revokeObjectURL(link.href);
      }).catch(() => {
        this.$message.error('导出失败');
      });
    },
    // 图片处理
    getImageSrc(imageBase64) {
      if (!imageBase64) return '';
      if (imageBase64.startsWith('data:image')) return imageBase64;
      return `data:image/jpeg;base64,${imageBase64}`;
    },
    // 情绪标签样式
    getTagStyle(emotion) {
      const emotionStyles = {
        neutral: { backgroundColor: "#e0e0e0", color: "#000", border: "1px solid #dcdfe6" },
        happiness: { backgroundColor: "#67C23A", color: "#fff", border: "none" },
        surprise: { backgroundColor: "#E6A23C", color: "#fff", border: "none" },
        sadness: { backgroundColor: "#909399", color: "#fff", border: "none" },
        anger: { backgroundColor: "#F56C6C", color: "#fff", border: "none" },
        disgust: { backgroundColor: "#F56C6C", color: "#fff", border: "none" },
        fear: { backgroundColor: "#E6A23C", color: "#fff", border: "none" },
        contempt: { backgroundColor: "#909399", color: "#fff", border: "none" },
        unknown: { backgroundColor: "#909399", color: "#fff", border: "none" },
      };
      return emotionStyles[emotion] || {};
    },
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
  }
};
</script>

<style scoped>
.search-form .el-form-item {
  margin-right: 1fr0fr0px;
}
.table-toolbar {
  margin-bottom: 8px;
}
</style>
