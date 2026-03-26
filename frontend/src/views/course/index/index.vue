<template>
  <div class="app-container">
    <el-form
      :model="queryParams"
      ref="queryForm"
      size="small"
      :inline="true"
      v-show="showSearch"
      label-width="68px"
      class="course-search-form"
    >
      <el-form-item label="学科" prop="subjectName">
        <el-select
          v-model="queryParams.subjectName"
          placeholder="请选择学科"
          clearable
          filterable
          style="width: 240px"
          @change="handleQuery"
        >
          <el-option label="全部学科" :value="null" />
          <el-option v-for="item in subjectOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item label="班级" prop="className">
        <el-select
          v-model="queryParams.className"
          placeholder="请选择班级"
          clearable
          filterable
          style="width: 240px"
          @change="handleQuery"
        >
          <el-option label="全部班级" :value="null" />
          <el-option v-for="item in classOptions" :key="item.classId" :label="item.className" :value="item.classId" />
        </el-select>
      </el-form-item>
      <el-form-item label="日期" prop="courseDate">
        <el-date-picker
          v-model="queryParams.courseDate"
          type="date"
          placeholder="请选择日期"
          value-format="yyyy-MM-dd"
          clearable
          style="width: 240px"
          @change="handleCourseDateChange"
        />
      </el-form-item>
      <div class="course-search-break"></div>
      <el-form-item label="学期" prop="semesterId">
        <el-select
          v-model="queryParams.semesterId"
          placeholder="请选择学期"
          clearable
          style="width: 240px"
          @change="handleSemesterChange"
        >
          <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="周次" prop="weekNum">
        <el-select
          v-model="queryParams.weekNum"
          placeholder="请选择周次"
          clearable
          style="width: 240px"
          :disabled="!queryParams.semesterId"
          @change="handleWeekChange"
        >
          <el-option label="全部周次" :value="null" />
          <el-option v-for="item in weekOptions" :key="item.weekNum" :label="item.name" :value="item.weekNum" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="el-icon-plus" size="mini" @click="handleAdd">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="el-icon-delete" size="mini" :disabled="multiple" @click="handleDelete">删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="el-icon-setting" size="mini" @click="openSemesterManage">学期维护</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="warning" plain icon="el-icon-date" size="mini" @click="openCycleManage">周期维护</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="info" plain icon="el-icon-upload2" size="mini" @click="handleImport">导入</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="courseList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="序号" width="60" align="center">
        <template slot-scope="scope">
          <span>{{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}</span>
        </template>
      </el-table-column>
      <el-table-column label="课节" align="center" prop="courseName" min-width="140" />
      <el-table-column label="学科" align="center" prop="subjectName" min-width="120" />
      <el-table-column label="班级" align="center" prop="className" min-width="120" />
      <el-table-column label="日期" align="center" prop="courseDate" min-width="120" />
      <el-table-column label="课节开始时间" align="center" prop="startTime" min-width="110" />
      <el-table-column label="课节结束时间" align="center" prop="endTime" min-width="110" />
      <el-table-column label="操作" align="center" width="150">
        <template slot-scope="scope">
          <el-button size="mini" type="text" icon="el-icon-edit" @click="handleUpdate(scope.row)">修改</el-button>
          <el-button size="mini" type="text" icon="el-icon-delete" @click="handleDelete(scope.row)">删除</el-button>
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

    <!-- 添加或修改课程对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="110px">
        <el-form-item label="课节" prop="courseName">
          <el-select
            v-model="form.courseName"
            placeholder="请选择或输入课节"
            filterable
            allow-create
            default-first-option
            style="width: 100%"
            @change="handleCourseNameChange"
          >
            <el-option
              v-for="item in courseOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学科" prop="subjectName">
          <el-select
            v-model="form.subjectName"
            placeholder="请选择或输入学科"
            filterable
            allow-create
            default-first-option
            clearable
            style="width: 100%"
          >
            <el-option v-for="item in subjectOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级" prop="className">
          <el-select v-model="form.className" placeholder="请选择班级" filterable clearable style="width: 100%">
            <el-option v-for="item in classOptions" :key="item.classId" :label="item.className" :value="item.classId" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" prop="courseDate">
          <el-date-picker
            v-model="form.courseDate"
            type="date"
            placeholder="请选择日期"
            value-format="yyyy-MM-dd"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="课节开始时间" prop="startTime">
          <el-time-picker
            v-model="form.startTime"
            placeholder="请选择课节开始时间"
            value-format="HH:mm"
            format="HH:mm"
            style="width: 100%"
            @change="handleStartTimeChange"
          />
        </el-form-item>
        <el-form-item label="课节结束时间" prop="endTime">
          <el-time-picker
            v-model="form.endTime"
            placeholder="请选择课节结束时间"
            value-format="HH:mm"
            format="HH:mm"
            style="width: 100%"
            @change="handleEndTimeChange"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="0">正常</el-radio>
            <el-radio label="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>

    <el-dialog title="学期维护" :visible.sync="semesterManageOpen" width="820px" append-to-body>
      <div style="margin-bottom: 12px; display: flex; gap: 8px;">
        <el-button type="primary" size="mini" icon="el-icon-plus" @click="handleSemesterAdd">新增</el-button>
        <el-button size="mini" icon="el-icon-refresh" @click="loadSemesterManageList">刷新</el-button>
      </div>
      <el-table v-loading="semesterManageLoading" :data="semesterManageList">
        <el-table-column label="名称" prop="name" min-width="180" />
        <el-table-column label="开始日期" prop="start" min-width="120" />
        <el-table-column label="结束日期" prop="end" min-width="120" />
        <el-table-column label="周数" prop="weeks" width="80" align="center" />
        <el-table-column label="操作" width="160" align="center">
          <template slot-scope="scope">
            <el-button size="mini" type="text" icon="el-icon-edit" @click="handleSemesterEdit(scope.row)">修改</el-button>
            <el-button size="mini" type="text" icon="el-icon-delete" @click="handleSemesterDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog :title="semesterFormTitle" :visible.sync="semesterFormOpen" width="520px" append-to-body>
      <el-form ref="semesterFormRef" :model="semesterForm" label-width="100px">
        <el-form-item label="学期名称">
          <el-input v-model="semesterForm.name" placeholder="例如：2025-2026学年上学期" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="semesterForm.start" type="date" value-format="yyyy-MM-dd" placeholder="请选择开始日期" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="semesterForm.end" type="date" value-format="yyyy-MM-dd" placeholder="请选择结束日期" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="周数">
          <el-input-number v-model="semesterForm.weeks" :min="1" :max="60" controls-position="right" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="semesterForm.remark" type="textarea" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitSemesterForm">确 定</el-button>
        <el-button @click="semesterFormOpen = false">取 消</el-button>
      </div>
    </el-dialog>

    <el-dialog title="周期维护" :visible.sync="cycleManageOpen" width="980px" append-to-body>
      <el-form :inline="true" size="small">
        <el-form-item label="学期">
          <el-select v-model="cycleManageSemesterId" placeholder="请选择学期" clearable style="width: 260px" @change="loadCycleManageList">
            <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="mini" icon="el-icon-plus" @click="handleCycleAdd">新增一周</el-button>
        </el-form-item>
      </el-form>
      <el-table v-loading="cycleManageLoading" :data="cycleManagePagedList">
        <el-table-column label="周次" prop="weekNum" width="90" />
        <el-table-column label="名称" prop="name" min-width="160" />
        <el-table-column label="开始日期" prop="startDate" width="120" />
        <el-table-column label="结束日期" prop="endDate" width="120" />
        <el-table-column label="备注" prop="remark" min-width="140" />
        <el-table-column label="操作" width="160">
          <template slot-scope="scope">
            <template v-if="scope.row.cycleId">
              <el-button size="mini" type="text" icon="el-icon-edit" @click="handleCycleEdit(scope.row)">修改</el-button>
              <el-button size="mini" type="text" icon="el-icon-delete" @click="handleCycleDelete(scope.row)">删除</el-button>
            </template>
            <template v-else>
              <el-button size="mini" type="text" icon="el-icon-plus" @click="handleCycleMaintain(scope.row)">维护</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
      <div class="course-pagination-wrapper">
        <pagination
          v-show="cycleManageTotal > 0"
          :total="cycleManageTotal"
          :page.sync="cycleManagePageNum"
          :limit.sync="cycleManagePageSize"
          @pagination="handleCycleManagePagination"
        />
      </div>
    </el-dialog>

    <el-dialog :title="cycleFormTitle" :visible.sync="cycleFormOpen" width="540px" append-to-body>
      <el-form ref="cycleFormRef" :model="cycleForm" label-width="100px">
        <el-form-item label="学期">
          <el-select v-model="cycleForm.semesterId" placeholder="请选择学期" style="width: 100%;" :disabled="cycleFormMode === 'edit'">
            <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="周次">
          <el-input-number v-model="cycleForm.weekNum" :min="1" :max="60" controls-position="right" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="cycleForm.name" placeholder="例如：第1周" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="cycleForm.startDate" type="date" value-format="yyyy-MM-dd" placeholder="请选择开始日期" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="cycleForm.endDate" type="date" value-format="yyyy-MM-dd" placeholder="请选择结束日期" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="cycleForm.remark" type="textarea" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitCycleForm">确 定</el-button>
        <el-button @click="cycleFormOpen = false">取 消</el-button>
      </div>
    </el-dialog>

    <el-dialog :title="upload.title" :visible.sync="upload.open" width="400px" append-to-body>
      <el-upload
        ref="upload"
        :limit="1"
        accept=".xlsx, .xls"
        :headers="upload.headers"
        :action="upload.url + '?updateSupport=0'"
        :disabled="upload.isUploading"
        :on-progress="handleFileUploadProgress"
        :on-success="handleFileSuccess"
        :auto-upload="false"
        drag
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip text-center" slot="tip">
          <span>仅允许导入xls、xlsx格式文件。</span>
          <el-link type="primary" :underline="false" style="font-size: 12px; vertical-align: baseline" @click="importTemplate">下载模板</el-link>
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
  listCourse,
  listCourseClasses,
  listCourseSubjects,
  listCourseWeeks,
  getCourse,
  addCourse,
  updateCourse,
  delCourse,
  listSemesters,
  addSemester,
  updateSemester,
  delSemester,
  listSemesterWeeks,
  addCycle,
  updateCycle,
  delCycle,
  importCourseTemplate
  } from '@/api/cell/course'
import { getToken } from '@/utils/auth'

export default {
  name: 'Course',
  data() {
    return {
      loading: true,
      ids: [],
      multiple: true,
      showSearch: true,
      courseList: [],
      total: 0,
      title: '',
      open: false,
      classOptions: [],
      subjectOptions: [],
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        subjectName: null,
        className: null,
        status: null,
        courseDate: null,
        semesterId: null,
        weekNum: null
      },
      semesterOptions: [],
      weekOptions: [],
      semesterManageOpen: false,
      semesterManageLoading: false,
      semesterManageList: [],
      semesterFormOpen: false,
      semesterFormTitle: '',
      semesterFormMode: 'add',
      semesterForm: {
        id: '',
        name: '',
        start: '',
        end: '',
        weeks: 20,
        status: '0',
        remark: ''
      },
      cycleManageOpen: false,
      cycleManageLoading: false,
      cycleManageSemesterId: null,
      cycleManageDate: null,
      cycleManageFullList: [],
      cycleManageList: [],
      cycleManageTotal: 0,
      cycleManagePageNum: 1,
      cycleManagePageSize: 10,
      cycleFormOpen: false,
      cycleFormTitle: '',
      cycleFormMode: 'add',
      cycleForm: {
        cycleId: null,
        semesterId: '',
        weekNum: 1,
        name: '',
        startDate: '',
        endDate: '',
        status: '0',
        orderNum: 0,
        remark: ''
      },
      form: {},
      // 课程导入参数
      upload: {
        // 是否显示弹出层（课程导入）
        open: false,
        // 弹出层标题（课程导入）
        title: '',
        // 是否禁用上传
        isUploading: false,
        // 是否更新已经存在的课程数据
        updateSupport: 0,
        // 设置上传的请求头部
        headers: { Authorization: 'Bearer ' + getToken() },
        // 上传的地址
        url: process.env.VUE_APP_BASE_API + '/cell/course/upload'
      },
      // 九节课选项
      courseOptions: [
        { value: '第1节', label: '第1节', startTime: '08:00', endTime: '08:45', orderNum: 1 },
        { value: '第2节', label: '第2节', startTime: '08:55', endTime: '09:40', orderNum: 2 },
        { value: '第3节', label: '第3节', startTime: '10:00', endTime: '10:45', orderNum: 3 },
        { value: '第4节', label: '第4节', startTime: '10:55', endTime: '11:40', orderNum: 4 },
        { value: '第5节', label: '第5节', startTime: '14:00', endTime: '14:45', orderNum: 5 },
        { value: '第6节', label: '第6节', startTime: '14:55', endTime: '15:40', orderNum: 6 },
        { value: '第7节', label: '第7节', startTime: '16:00', endTime: '16:45', orderNum: 7 },
        { value: '第8节', label: '第8节', startTime: '16:55', endTime: '17:40', orderNum: 8 },
        { value: '第9节', label: '第9节', startTime: '19:00', endTime: '19:45', orderNum: 9 }
      ],
      rules: {
        courseName: [{ required: true, message: '课节不能为空', trigger: 'change' }],
        subjectName: [{ required: true, message: '学科不能为空', trigger: 'blur' }],
        className: [{ required: true, message: '班级不能为空', trigger: 'change' }],
        courseDate: [{ required: true, message: '日期不能为空', trigger: 'change' }],
        startTime: [{ required: true, message: '课节开始时间不能为空', trigger: 'change' }],
        endTime: [{ required: true, message: '课节结束时间不能为空', trigger: 'change' }]
      }
    }
  },
  created() {
    this.getList()
    this.getSemesterOptions()
    this.loadClassOptions()
    this.loadSubjectOptions()
    this.rules.courseName.push({ validator: this.validateCourseNameFormat, trigger: 'change' })
    this.rules.startTime.push({ validator: this.validateCourseTimeRange, trigger: 'change' })
    this.rules.endTime.push({ validator: this.validateCourseTimeRange, trigger: 'change' })
  },
  computed: {
    cycleManagePagedList() {
      const list = Array.isArray(this.cycleManageList) ? this.cycleManageList : []
      const pageSize = Number(this.cycleManagePageSize || 10)
      const pageNum = Number(this.cycleManagePageNum || 1)
      const safePageSize = Number.isFinite(pageSize) && pageSize > 0 ? pageSize : 10
      const safePageNum = Number.isFinite(pageNum) && pageNum > 0 ? pageNum : 1
      const startIndex = (safePageNum - 1) * safePageSize
      return list.slice(startIndex, startIndex + safePageSize)
    }
  },
  methods: {
    formatDate(date) {
      if (!(date instanceof Date) || !Number.isFinite(date.getTime())) return ''
      const y = date.getFullYear()
      const m = String(date.getMonth() + 1).padStart(2, '0')
      const d = String(date.getDate()).padStart(2, '0')
      return `${y}-${m}-${d}`
    },
    addDays(dateStr, days) {
      const s = dateStr != null ? String(dateStr).trim() : ''
      if (!s) return ''
      const dt = new Date(`${s}T00:00:00`)
      if (!Number.isFinite(dt.getTime())) return ''
      dt.setDate(dt.getDate() + Number(days || 0))
      return this.formatDate(dt)
    },
    validateCourseNameFormat(rule, value, callback) {
      const s = value != null ? String(value).trim() : ''
      if (!s) {
        callback()
        return
      }
      const ok = /^第[0-9一二三四五六七八九十百零〇两]+节$/.test(s)
      if (!ok) {
        callback(new Error('课节格式必须为：第X节（例如：第1节、第11节）'))
        return
      }
      callback()
    },
    timeToMinutes(value) {
      if (!value) return null
      if (typeof value === 'string') {
        const s = value.trim()
        const parts = s.split(':')
        if (parts.length < 2) return null
        const h = Number(parts[0])
        const m = Number(parts[1])
        if (!Number.isFinite(h) || !Number.isFinite(m)) return null
        return h * 60 + m
      }
      if (value instanceof Date) {
        return value.getHours() * 60 + value.getMinutes()
      }
      return null
    },
    validateCourseTimeRange(rule, value, callback) {
      const startTime = this.form && this.form.startTime
      const endTime = this.form && this.form.endTime
      if (!startTime || !endTime) {
        callback()
        return
      }
      const startMin = this.timeToMinutes(startTime)
      const endMin = this.timeToMinutes(endTime)
      if (startMin == null || endMin == null) {
        callback()
        return
      }
      if (startMin > endMin) {
        callback(new Error('课节开始时间不能晚于结束时间'))
        return
      }
      callback()
    },
    handleStartTimeChange() {
      this.$nextTick(() => {
        if (this.$refs.form && this.$refs.form.validateField) {
          this.$refs.form.validateField(['startTime', 'endTime'])
        }
      })
    },
    handleEndTimeChange() {
      this.$nextTick(() => {
        if (this.$refs.form && this.$refs.form.validateField) {
          this.$refs.form.validateField(['startTime', 'endTime'])
        }
      })
    },
    loadClassOptions() {
      listCourseClasses()
        .then(response => {
          const list = Array.isArray(response.data) ? response.data : []
          this.classOptions = list
            .filter(i => i && i.classId != null && i.className != null)
            .slice()
            .sort((a, b) => String(a.className).localeCompare(String(b.className), 'zh-Hans-CN'))
        })
        .catch(() => {
          this.classOptions = []
        })
    },
    loadSubjectOptions() {
      listCourseSubjects()
        .then(response => {
          this.subjectOptions = response.data || []
        })
        .catch(() => {
          this.subjectOptions = []
        })
    },
    ensureClassOption(value) {
      if (!value) return
      const exists = this.classOptions.some(i => String(i.classId) === String(value))
      if (exists) return
      this.classOptions = [
        ...this.classOptions,
        { classId: value, className: value }
      ].sort((a, b) => String(a.className).localeCompare(String(b.className), 'zh-Hans-CN'))
    },
    getList() {
      this.loading = true
      listCourse(this.queryParams).then(response => {
        if (Array.isArray(response.rows)) {
          this.courseList = response.rows
          this.total = Number(response.total || 0)
        } else if (Array.isArray(response.data)) {
          this.courseList = response.data
          this.total = response.data.length
        } else {
          this.courseList = []
          this.total = 0
        }
        this.loading = false
      })
    },
    cancel() {
      this.open = false
      this.reset()
    },
    reset() {
      this.form = {
        courseId: null,
        courseName: null,
        subjectName: null,
        className: null,
        courseDate: null,
        startTime: null,
        endTime: null,
        orderNum: 0,
        status: '0'
      }
      this.resetForm('form')
    },
    handleQuery() {
      this.queryParams.pageNum = 1
      this.getList()
    },
    handleCourseDateChange() {
      if (this.queryParams.courseDate) {
        this.queryParams.weekNum = null
      }
      this.handleQuery()
    },
    resetQuery() {
      this.resetForm('queryForm')
      this.handleQuery()
    },
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.courseId)
      this.multiple = !selection.length
    },
    handleCourseNameChange(val) {
      const normalized = val != null ? String(val).trim() : val
      if (this.form && typeof this.form.courseName === 'string') {
        this.form.courseName = normalized
      }
      const course = this.courseOptions.find(item => item.value === normalized)
      if (!course) return
      this.form.orderNum = course.orderNum
      if (!this.form.startTime) {
        this.form.startTime = course.startTime
      }
      if (!this.form.endTime) {
        this.form.endTime = course.endTime
      }
      this.handleStartTimeChange()
    },
    handleAdd() {
      this.reset()
      this.open = true
      this.title = '添加课程'
    },
    handleUpdate(row) {
      this.reset()
      const courseId = row.courseId || this.ids
      getCourse(courseId).then(response => {
        this.form = response.data
        this.ensureClassOption(this.form.className)
        this.open = true
        this.title = '修改课程'
      })
    },
    submitForm() {
      this.$refs['form'].validate(valid => {
        if (valid) {
          const { remark, ...payload } = this.form || {}
          if (this.form.courseId != null) {
            updateCourse(payload).then(response => {
              this.$modal.msgSuccess('修改成功')
              this.open = false
              this.getList()
            })
          } else {
            addCourse(payload).then(response => {
              this.$modal.msgSuccess('新增成功')
              this.open = false
              this.getList()
            })
          }
        }
      })
    },
    handleDelete(row) {
      const courseIds = row.courseId || this.ids
      this.$modal.confirm('是否确认删除课程编号为"' + courseIds + '"的数据项？').then(() => {
        return delCourse(courseIds)
      }).then(() => {
        this.getList()
        this.$modal.msgSuccess('删除成功')
      }).catch(() => {})
    },
    getSemesterOptions() {
      listSemesters().then(res => {
        const data = res.data || {}
        this.semesterOptions = data.semesters || []
        if (data.currentSemesterId) {
          this.queryParams.semesterId = data.currentSemesterId
          this.handleSemesterChange(this.queryParams.semesterId)
        }
      })
    },
    handleSemesterChange(semesterId) {
      this.queryParams.weekNum = null
      this.weekOptions = []
      if (this.queryParams.courseDate) {
        this.queryParams.courseDate = null
      }
      if (!semesterId) return
      listCourseWeeks(semesterId).then(res => {
        const weekNums = Array.isArray(res.data) ? res.data : []
        this.weekOptions = weekNums.map(n => ({
          weekNum: Number(n),
          name: `第${Number(n)}周`
        })).filter(w => Number.isFinite(w.weekNum))
      })
      this.handleQuery()
    },
    openSemesterManage() {
      this.semesterManageOpen = true
      this.loadSemesterManageList()
    },
    loadSemesterManageList() {
      this.semesterManageLoading = true
      listSemesters()
        .then(res => {
          const data = res.data || {}
          this.semesterManageList = data.semesters || []
        })
        .finally(() => {
          this.semesterManageLoading = false
        })
    },
    handleSemesterAdd() {
      this.semesterFormMode = 'add'
      this.semesterFormTitle = '新增学期'
      this.semesterForm = {
        id: '',
        name: '',
        start: '',
        end: '',
        weeks: 20,
        status: '0',
        remark: ''
      }
      this.semesterFormOpen = true
    },
    handleSemesterEdit(row) {
      this.semesterFormMode = 'edit'
      this.semesterFormTitle = '修改学期'
      this.semesterForm = {
        id: row.id,
        name: row.name,
        start: row.start,
        end: row.end,
        weeks: row.weeks != null ? Number(row.weeks) : 20,
        status: row.status != null ? String(row.status) : '0',
        remark: row.remark || ''
      }
      this.semesterFormOpen = true
    },
    submitSemesterForm() {
      if (!this.semesterForm.name || !this.semesterForm.start || !this.semesterForm.end) {
        this.$message.error('学期名称、开始日期、结束日期不能为空')
        return
      }
      if (this.semesterForm.start > this.semesterForm.end) {
        this.$message.error('学期开始日期不能晚于结束日期')
        return
      }
      const weeks = Number(this.semesterForm.weeks || 0)
      if (!Number.isFinite(weeks) || weeks < 1) {
        this.$message.error('学期周数必须大于0')
        return
      }
      const start = new Date(`${this.semesterForm.start}T00:00:00`)
      const end = new Date(`${this.semesterForm.end}T00:00:00`)
      if (!Number.isFinite(start.getTime()) || !Number.isFinite(end.getTime())) {
        this.$message.error('学期日期格式不正确')
        return
      }
      const days = Math.floor((end.getTime() - start.getTime()) / 86400000) + 1
      if (days < weeks * 7) {
        this.$message.error('学期结束日期需覆盖周数范围')
        return
      }
      const payload = {
        name: this.semesterForm.name,
        start: this.semesterForm.start,
        end: this.semesterForm.end,
        weeks: this.semesterForm.weeks,
        remark: this.semesterForm.remark
      }
      if (this.semesterFormMode === 'edit') {
        payload.id = this.semesterForm.id
      }
      const req = this.semesterFormMode === 'edit' ? updateSemester(payload) : addSemester(payload)
      req.then(() => {
        this.$modal.msgSuccess(this.semesterFormMode === 'edit' ? '修改成功' : '新增成功')
        this.semesterFormOpen = false
        this.loadSemesterManageList()
        this.getSemesterOptions()
      })
    },
    handleSemesterDelete(row) {
      this.$modal
        .confirm('是否确认删除学期"' + row.name + '"？')
        .then(() => delSemester(row.id))
        .then(() => {
          this.$modal.msgSuccess('删除成功')
          this.loadSemesterManageList()
          this.getSemesterOptions()
        })
        .catch(() => {})
    },
    openCycleManage() {
      this.cycleManageOpen = true
      this.cycleManageSemesterId = this.queryParams.semesterId || (this.semesterOptions[0] && this.semesterOptions[0].id) || null
      this.cycleManageDate = this.queryParams.courseDate || null
      this.cycleManagePageNum = 1
      this.loadCycleManageList()
    },
    applyCycleManageDateFilter() {
      const dateStr = this.cycleManageDate != null ? String(this.cycleManageDate).trim() : ''
      const list = Array.isArray(this.cycleManageFullList) ? this.cycleManageFullList : []
      if (!dateStr) {
        this.cycleManageList = list
        this.cycleManageTotal = this.cycleManageList.length
        return
      }
      const row = list.find(item => {
        const start = item && item.startDate ? String(item.startDate) : ''
        const end = item && item.endDate ? String(item.endDate) : ''
        return start && end && start <= dateStr && dateStr <= end
      })
      this.cycleManageList = row ? [row] : []
      this.cycleManageTotal = this.cycleManageList.length
      this.cycleManagePageNum = 1
    },
    handleCycleManagePagination() {},
    loadCycleManageList() {
      const semesterId = this.cycleManageSemesterId
      if (!semesterId) {
        this.cycleManageFullList = []
        this.cycleManageList = []
        this.cycleManageTotal = 0
        return
      }
      this.cycleManageLoading = true
      listSemesterWeeks(semesterId)
        .then(res => {
          const data = res.data || []
          this.cycleManageFullList = Array.isArray(data) ? data : []
          this.applyCycleManageDateFilter()
        })
        .finally(() => {
          this.cycleManageLoading = false
        })
    },
    handleCycleAdd() {
      const semesterId = this.cycleManageSemesterId || this.queryParams.semesterId
      const list = Array.isArray(this.cycleManageFullList) ? this.cycleManageFullList : []
      const last = list.length ? list[list.length - 1] : null
      const nextWeekNum = last && last.weekNum != null ? Number(last.weekNum) + 1 : 1
      const defaultStart = last && last.endDate ? this.addDays(last.endDate, 1) : ''
      const semester = this.semesterOptions.find(s => s.id === semesterId)
      const computedStart = semester && semester.start ? this.addDays(semester.start, (nextWeekNum - 1) * 7) : ''
      const startDate = defaultStart || computedStart
      const endDate = startDate ? this.addDays(startDate, 6) : ''
      this.cycleFormMode = 'add'
      this.cycleFormTitle = '新增一周'
      this.cycleForm = {
        cycleId: null,
        semesterId: semesterId || '',
        weekNum: Number.isFinite(nextWeekNum) && nextWeekNum > 0 ? nextWeekNum : 1,
        name: `第${Number.isFinite(nextWeekNum) && nextWeekNum > 0 ? nextWeekNum : 1}周`,
        startDate: startDate,
        endDate: endDate,
        status: '0',
        orderNum: 0,
        remark: ''
      }
      this.cycleFormOpen = true
    },
    handleCycleMaintain(row) {
      this.cycleFormMode = 'add'
      this.cycleFormTitle = '维护周期'
      this.cycleForm = {
        cycleId: null,
        semesterId: row.semesterId || this.cycleManageSemesterId || '',
        weekNum: row.weekNum != null ? Number(row.weekNum) : 1,
        name: row.name || '',
        startDate: row.startDate || '',
        endDate: row.endDate || '',
        status: row.status != null ? String(row.status) : '0',
        orderNum: row.orderNum != null ? Number(row.orderNum) : 0,
        remark: row.remark || ''
      }
      this.cycleFormOpen = true
    },
    handleCycleEdit(row) {
      if (!row.cycleId) {
        this.handleCycleMaintain(row)
        return
      }
      this.cycleFormMode = 'edit'
      this.cycleFormTitle = '修改周期'
      this.cycleForm = {
        cycleId: row.cycleId != null ? Number(row.cycleId) : null,
        semesterId: row.semesterId || this.cycleManageSemesterId || '',
        weekNum: row.weekNum != null ? Number(row.weekNum) : 1,
        name: row.name || '',
        startDate: row.startDate || '',
        endDate: row.endDate || '',
        status: row.status != null ? String(row.status) : '0',
        orderNum: row.orderNum != null ? Number(row.orderNum) : 0,
        remark: row.remark || ''
      }
      this.cycleFormOpen = true
    },
    submitCycleForm() {
      if (!this.cycleForm.semesterId) {
        this.$message.error('请选择学期')
        return
      }
      const weekNum = Number(this.cycleForm.weekNum || 0)
      if (!Number.isFinite(weekNum) || weekNum < 1) {
        this.$message.error('周次必须大于0')
        return
      }
      if (!this.cycleForm.startDate || !this.cycleForm.endDate) {
        this.$message.error('周期开始日期、结束日期不能为空')
        return
      }
      if (this.cycleForm.startDate > this.cycleForm.endDate) {
        this.$message.error('周期开始日期不能晚于结束日期')
        return
      }
      const payload = {
        cycleId: this.cycleForm.cycleId,
        semesterId: this.cycleForm.semesterId,
        weekNum: this.cycleForm.weekNum,
        name: this.cycleForm.name,
        startDate: this.cycleForm.startDate,
        endDate: this.cycleForm.endDate,
        remark: this.cycleForm.remark
      }
      const req = this.cycleFormMode === 'edit' ? updateCycle(payload) : addCycle(payload)
      req.then(() => {
        this.$modal.msgSuccess(this.cycleFormMode === 'edit' ? '修改成功' : '新增成功')
        this.cycleFormOpen = false
        this.loadCycleManageList()
        this.getSemesterOptions()
        if (this.semesterManageOpen) {
          this.loadSemesterManageList()
        }
        if (this.queryParams.semesterId) {
          this.handleSemesterChange(this.queryParams.semesterId)
        }
      })
    },
    handleCycleDelete(row) {
      const cycleId = row.cycleId
      this.$modal
        .confirm('是否确认删除周期"' + (row.name || '') + '"？')
        .then(() => delCycle(cycleId))
        .then(() => {
          this.$modal.msgSuccess('删除成功')
          this.loadCycleManageList()
          this.getSemesterOptions()
          if (this.semesterManageOpen) {
            this.loadSemesterManageList()
          }
          if (this.queryParams.semesterId) {
            this.handleSemesterChange(this.queryParams.semesterId)
          }
        })
        .catch(() => {})
    },
    handleWeekChange() {
      if (this.queryParams.weekNum) {
        this.queryParams.courseDate = null
      }
      this.handleQuery()
    },
    handleImport() {
      this.upload.title = '课程导入'
      this.upload.open = true
    },
    importTemplate() {
      importCourseTemplate()
        .then(response => {
          const blob = new Blob([response], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          })
          const fileName = '课程导入模板.xlsx'
          if (window.navigator.msSaveOrOpenBlob) {
            navigator.msSaveBlob(blob, fileName)
            return
          }
          const link = document.createElement('a')
          link.href = window.URL.createObjectURL(blob)
          link.download = fileName
          link.click()
          window.URL.revokeObjectURL(link.href)
        })
        .catch(() => {
          this.$message.error('下载模板失败')
        })
    },
    handleFileUploadProgress() {
      this.upload.isUploading = true
    },
    handleFileSuccess(response) {
      this.upload.open = false
      this.upload.isUploading = false
      this.$refs.upload.clearFiles()
      this.$alert("<div style='overflow: auto;overflow-x: hidden;max-height: 70vh;padding: 10px 20px 0;'>" + (response && response.msg ? response.msg : '') + '</div>', '导入结果', { dangerouslyUseHTMLString: true })
      this.getList()
    },
    submitFileForm() {
      this.$refs.upload.submit()
    }
  }
}
</script>

<style scoped>
.course-search-form {
  margin-bottom: 12px;
}

.course-search-form ::v-deep.el-form--inline .el-form-item {
  margin-right: 16px;
  margin-bottom: 10px;
}

.course-search-break {
  display: block;
  width: 100%;
  height: 0;
}

.course-pagination-wrapper {
  display: flex;
  justify-content: center;
}

.course-pagination-wrapper ::v-deep .pagination-container {
  background: transparent;
  padding: 16px 0 0;
}

::v-deep .el-table {
  margin-top: 12px;
}

::v-deep .el-table th > .cell,
::v-deep .el-table td > .cell {
  padding-left: 16px;
  padding-right: 16px;
}
</style>
