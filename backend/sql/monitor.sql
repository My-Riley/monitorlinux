set names utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- 情绪识别监控系统数据表（自定义表）
-- ----------------------------

-- ----------------------------
-- 1、班级学生表
-- ----------------------------
drop table if exists sys_class_student;
create table sys_class_student (
  id                bigint(20)      not null auto_increment    comment '主键',
  student_id        varchar(50)     not null                   comment '学号',
  student_name      varchar(30)     not null                   comment '学生姓名',
  classes           varchar(30)     not null                   comment '班级',
  email             varchar(50)     default null               comment '邮箱',
  grade             varchar(50)     default null               comment '年级',
  phonenumber       varchar(11)     default null               comment '手机号码',
  sex               char(1)         default '2'                comment '性别 （0男 1女 2未知）',
  age               int(11)         default null               comment '年龄',
  face_image        varchar(255)    default null               comment '人脸图像路径',
  status            char(1)         default '0'                comment '状态 （0正常 1停用）',
  del_flag          char(1)         default '0'                comment '是否删除 （0存在  2删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (id)
) engine=innodb auto_increment=1 comment = '班级学生信息表';

-- ----------------------------
-- 2、课程表
-- ----------------------------
drop table if exists sys_course;
create table sys_course (
  course_id         bigint(20)      not null auto_increment    comment '课程id',
  course_name       varchar(50)     not null                   comment '课程名称(第几节课)',
  subject_name      varchar(50)     default null               comment '学科名称',
  class_name        varchar(50)     default null               comment '班级',
  course_date       date            default null               comment '日期',
  start_time        time            default null               comment '开始时间',
  end_time          time            default null               comment '结束时间',
  order_num         int(4)          default 0                  comment '排序',
  status            char(1)         default '0'                comment '状态(0正常 1停用)',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (course_id)
) engine=innodb auto_increment=1 comment = '课程表';

-- ----------------------------
-- 3、学期表
-- ----------------------------
drop table if exists sys_semester;
create table sys_semester (
  id                varchar(32)     not null                   comment '学期ID',
  name              varchar(128)    not null                   comment '学期名称',
  start_date        date            not null                   comment '开始日期',
  end_date          date            not null                   comment '结束日期',
  weeks             int(11)         not null                   comment '总周数',
  status            char(1)         not null                   comment '状态(0正常 1停用)',
  order_num         int(4)          not null                   comment '排序',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (id)
) engine=innodb comment = '学期表';

-- ----------------------------
-- 4、学期周期表
-- ----------------------------
drop table if exists sys_semester_cycle;
create table sys_semester_cycle (
  cycle_id          bigint(20)      not null auto_increment    comment '周期ID',
  semester_id       varchar(32)     not null                   comment '学期ID',
  week_num          int(11)         not null                   comment '周次',
  name              varchar(128)    not null                   comment '周期名称',
  start_date        date            not null                   comment '开始日期',
  end_date          date            not null                   comment '结束日期',
  status            char(1)         not null                   comment '状态(0正常 1停用)',
  order_num         int(4)          not null                   comment '排序',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (cycle_id)
) engine=innodb comment = '学期周期表';

-- ----------------------------
-- 5、摄像头表
-- ----------------------------
drop table if exists sys_camera;
create table sys_camera (
  camera_id         bigint(20)      not null auto_increment    comment '摄像头ID',
  camera_name       varchar(100)    not null                   comment '摄像头名称',
  region_id         bigint(20)      default null               comment '区域ID',
  status            char(1)         default '0'                comment '状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  username          varchar(50)     default null               comment '登录用户名',
  password          varchar(50)     default null               comment '登录密码',
  ip_addr           varchar(50)     default null               comment 'IP地址',
  port              varchar(50)     default null               comment '端口',
  rtsp_port         varchar(50)     default null               comment 'RTSP端口',
  protocol          varchar(50)     default null               comment '协议',
  brand             varchar(50)     default null               comment '品牌',
  line              varchar(2)      default '0'                comment '线路',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (camera_id)
) engine=innodb auto_increment=1 comment = '摄像头表';

-- ----------------------------
-- 6、摄像头区域表
-- ----------------------------
drop table if exists sys_camera_region;
create table sys_camera_region (
  region_id         bigint(20)      not null auto_increment    comment '区域id',
  parent_id         bigint(20)      default 0                  comment '父区域id',
  ancestors         varchar(50)     default ''                 comment '祖级列表',
  region_name       varchar(30)     default ''                 comment '区域名称',
  order_num         int(4)          default 0                  comment '显示顺序',
  address           varchar(255)    default null               comment '区域地址',
  status            char(1)         default '0'                comment '区域状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  primary key (region_id)
) engine=innodb auto_increment=200 comment = '摄像头区域表';

-- ----------------------------
-- 7、摄像头预警表
-- ----------------------------
drop table if exists sys_camera_warn;
create table sys_camera_warn (
  warn_id           bigint(20)      not null auto_increment    comment '预警id',
  warn_name         varchar(50)     not null                   comment '预警名称',
  warn_level        char(1)         default '1'                comment '预警级别(1:低, 2:中, 3:高)',
  warn_content      varchar(255)    default ''                 comment '预警内容',
  warn_time         datetime                                   comment '预警时间',
  camera_id         bigint(20)      default null               comment '摄像头ID',
  camera_name       varchar(50)     default ''                 comment '摄像头名称',
  status            char(1)         default '0'                comment '状态(0:未处理, 1:已处理)',
  handle_result     varchar(255)    default ''                 comment '处理结果',
  handle_time       datetime                                   comment '处理时间',
  handle_by         varchar(64)     default ''                 comment '处理人',
  remark            varchar(500)    default ''                 comment '备注',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  primary key (warn_id)
) engine=innodb auto_increment=100 comment = '摄像头预警表';

-- ----------------------------
-- 8、情绪分析结果表
-- ----------------------------
drop table if exists sys_emotion_result;
create table sys_emotion_result (
  result_id         bigint(20)      not null auto_increment    comment '结果ID',
  student_id        varchar(50)     default null               comment '学号',
  student_name      varchar(50)     default null               comment '学生姓名',
  emotion           varchar(50)     not null                   comment '情绪',
  camera_ip         varchar(50)     default null               comment '摄像头IP',
  image_base64      mediumtext                                 comment '图片Base64',
  image_path        varchar(255)    default null               comment '图片路径',
  url               varchar(255)    default null               comment 'URL',
  statistics        text                                       comment '统计信息',
  create_time       datetime                                   comment '创建时间',
  primary key (result_id)
) engine=innodb auto_increment=1 comment = '情绪分析结果表';

-- ----------------------------
-- 9、情绪焦虑映射表
-- ----------------------------
drop table if exists sys_emotion_anxiety_mapping;
create table sys_emotion_anxiety_mapping (
  mapping_id        int(11)         not null auto_increment    comment '主键ID',
  emotion_en        varchar(50)     not null                   comment '情绪英文名称',
  emotion_cn        varchar(50)     not null                   comment '情绪中文名称',
  anxiety_level     int(11)         not null                   comment '焦虑程度(0:无焦虑, 1:低度焦虑, 2:中度焦虑, 3:高度焦虑)',
  anxiety_name      varchar(50)     not null                   comment '焦虑程度名称',
  create_time       datetime        default current_timestamp  comment '创建时间',
  primary key (mapping_id),
  unique key uk_emotion_en (emotion_en)
) engine=innodb auto_increment=1 comment = '情绪焦虑映射表';

-- ----------------------------
-- 初始化-情绪焦虑映射表数据
-- ----------------------------
insert into sys_emotion_anxiety_mapping values (1,  'happiness', '喜悦', 0, '无焦虑情绪', sysdate());
insert into sys_emotion_anxiety_mapping values (2,  'neutral',   '正常', 0, '无焦虑情绪', sysdate());
insert into sys_emotion_anxiety_mapping values (3,  'contempt',  '藐视', 1, '低度焦虑',   sysdate());
insert into sys_emotion_anxiety_mapping values (4,  'surprise',  '惊讶', 1, '低度焦虑',   sysdate());
insert into sys_emotion_anxiety_mapping values (5,  'anger',     '愤怒', 2, '中度焦虑',   sysdate());
insert into sys_emotion_anxiety_mapping values (6,  'disgust',   '厌恶', 2, '中度焦虑',   sysdate());
insert into sys_emotion_anxiety_mapping values (7,  'fear',      '恐惧', 3, '高度焦虑',   sysdate());
insert into sys_emotion_anxiety_mapping values (8,  'sadness',   '悲伤', 3, '高度焦虑',   sysdate());


-- ===========================================================================================
-- 系统核心表 (Aligned with RuoYi-Vue-FastAPI)
-- ===========================================================================================

-- ----------------------------
-- 1、部门表
-- ----------------------------
drop table if exists sys_dept;
create table sys_dept (
  dept_id           bigint(20)      not null auto_increment    comment '部门id',
  parent_id         bigint(20)      default 0                  comment '父部门id',
  ancestors         varchar(50)     default ''                 comment '祖级列表',
  dept_name         varchar(30)     default ''                 comment '部门名称',
  order_num         int(11)         default 0                  comment '显示顺序',
  leader            varchar(20)     default null               comment '负责人',
  phone             varchar(11)     default null               comment '联系电话',
  email             varchar(50)     default null               comment '邮箱',
  status            char(1)         default '0'                comment '部门状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  primary key (dept_id)
) engine=innodb auto_increment=200 comment = '部门表';

-- 初始化-部门表数据
insert into sys_dept values(100,  0,   '0',          '育才实验中学', 0, '校长', '15888888888', 'school@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(101,  100, '0,100',      '教学部',       1, '主任', '15888888888', 'teach@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(102,  100, '0,100',      '政教处',       2, '主任', '15888888888', 'politic@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(103,  100, '0,100',      '后勤部',       3, '主任', '15888888888', 'logistic@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(104,  101, '0,100,101',  '一年级',       1, '组长', '15888888888', 'grade1@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(105,  101, '0,100,101',  '二年级',       2, '组长', '15888888888', 'grade2@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(106,  101, '0,100,101',  '三年级',       3, '组长', '15888888888', 'grade3@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(107,  102, '0,100,102',  '心理咨询室',   1, '老师', '15888888888', 'psy@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(108,  102, '0,100,102',  '保卫科',       2, '科长', '15888888888', 'security@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(109,  103, '0,100,103',  '食堂管理',     1, '经理', '15888888888', 'canteen@qq.com', '0', '0', 'admin', sysdate(), '', null);

-- ----------------------------
-- 2、用户信息表
-- ----------------------------
drop table if exists sys_user;
create table sys_user (
  user_id           bigint(20)      not null auto_increment    comment '用户ID',
  dept_id           bigint(20)      default null               comment '部门ID',
  user_name         varchar(30)     not null                   comment '用户账号',
  nick_name         varchar(30)     not null                   comment '用户昵称',
  user_type         varchar(2)      default '00'               comment '用户类型（00系统用户）',
  email             varchar(50)     default ''                 comment '用户邮箱',
  phonenumber       varchar(11)     default ''                 comment '手机号码',
  sex               char(1)         default '0'                comment '用户性别（0男 1女 2未知）',
  avatar            varchar(100)    default ''                 comment '头像地址',
  password          varchar(100)    default ''                 comment '密码',
  status            char(1)         default '0'                comment '帐号状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  login_ip          varchar(128)    default ''                 comment '最后登录IP',
  login_date        datetime                                   comment '最后登录时间',
  pwd_update_date   datetime                                   comment '密码最后更新时间',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (user_id)
) engine=innodb auto_increment=100 comment = '用户信息表';

-- 初始化-用户信息表数据
insert into sys_user values(1,  100, 'admin',   '超级管理员', '00', 'admin@163.com', '15888888888', '1', '', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', '0', '0', '127.0.0.1', sysdate(), sysdate(), 'admin', sysdate(), '', null, '管理员');
insert into sys_user values(2,  101, 'lanbu',   '蓝布', 		 '00', 'lanbu@qq.com',  '15666666666', '1', '', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', '0', '0', '127.0.0.1', sysdate(), sysdate(), 'admin', sysdate(), '', null, '测试员');


-- ----------------------------
-- 3、岗位信息表
-- ----------------------------
drop table if exists sys_post;
create table sys_post(
  post_id       bigint(20)      not null auto_increment    comment '岗位ID',
  post_code     varchar(64)     not null                   comment '岗位编码',
  post_name     varchar(50)     not null                   comment '岗位名称',
  post_sort     int(4)          not null                   comment '显示顺序',
  status        char(1)         not null                   comment '状态（0正常 1停用）',
  create_by     varchar(64)     default ''                 comment '创建者',
  create_time   datetime                                   comment '创建时间',
  update_by     varchar(64)     default ''                 comment '更新者',
  update_time   datetime                                   comment '更新时间',
  remark        varchar(500)    default null               comment '备注',
  primary key (post_id)
) engine=innodb comment = '岗位信息表';

-- 初始化-岗位信息表数据
insert into sys_post values(1, 'principal',  '校长',    1, '0', 'admin', sysdate(), '', null, '');
insert into sys_post values(2, 'teacher',    '教师',    2, '0', 'admin', sysdate(), '', null, '');
insert into sys_post values(3, 'staff',      '职工',    3, '0', 'admin', sysdate(), '', null, '');
insert into sys_post values(4, 'student',    '学生',    4, '0', 'admin', sysdate(), '', null, '');

-- ----------------------------
-- 4、角色信息表
-- ----------------------------
drop table if exists sys_role;
create table sys_role (
  role_id              bigint(20)      not null auto_increment    comment '角色ID',
  role_name            varchar(30)     not null                   comment '角色名称',
  role_key             varchar(100)    not null                   comment '角色权限字符串',
  role_sort            int(4)          not null                   comment '显示顺序',
  data_scope           char(1)         default '1'                comment '数据范围（1：全部数据权限 2：自定数据权限 3：本部门数据权限 4：本部门及以下数据权限）',
  menu_check_strictly  tinyint(1)      default 1                  comment '菜单树选择项是否关联显示',
  dept_check_strictly  tinyint(1)      default 1                  comment '部门树选择项是否关联显示',
  status               char(1)         not null                   comment '角色状态（0正常 1停用）',
  del_flag             char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by            varchar(64)     default ''                 comment '创建者',
  create_time          datetime                                   comment '创建时间',
  update_by            varchar(64)     default ''                 comment '更新者',
  update_time          datetime                                   comment '更新时间',
  remark               varchar(500)    default null               comment '备注',
  primary key (role_id)
) engine=innodb auto_increment=100 comment = '角色信息表';

-- 初始化-角色信息表数据
insert into sys_role values('1', '超级管理员',  'admin',  1, 1, 1, 1, '0', '0', 'admin', sysdate(), '', null, '超级管理员');
insert into sys_role values('2', '普通角色',    'common', 2, 2, 1, 1, '0', '0', 'admin', sysdate(), '', null, '普通角色');

-- ----------------------------
-- 5、菜单权限表
-- ----------------------------
drop table if exists sys_menu;
create table sys_menu (
  menu_id           bigint(20)      not null auto_increment    comment '菜单ID',
  menu_name         varchar(50)     not null                   comment '菜单名称',
  parent_id         bigint(20)      default 0                  comment '父菜单ID',
  order_num         int(4)          default 0                  comment '显示顺序',
  path              varchar(200)    default ''                 comment '路由地址',
  component         varchar(255)    default null               comment '组件路径',
  query             varchar(255)    default null               comment '路由参数',
  route_name        varchar(50)     default ''                 comment '路由名称',
  is_frame          int(1)          default 1                  comment '是否为外链（0是 1否）',
  is_cache          int(1)          default 0                  comment '是否缓存（0缓存 1不缓存）',
  menu_type         char(1)         default ''                 comment '菜单类型（M目录 C菜单 F按钮）',
  visible           char(1)         default 0                  comment '菜单状态（0显示 1隐藏）',
  status            char(1)         default 0                  comment '菜单状态（0正常 1停用）',
  perms             varchar(100)    default null               comment '权限标识',
  icon              varchar(100)    default '#'                comment '菜单图标',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default ''                 comment '备注',
  primary key (menu_id)
) engine=innodb auto_increment=2000 comment = '菜单权限表';

-- ----------------------------
-- 初始化-菜单信息表数据
-- ----------------------------
-- 一级菜单
insert into sys_menu values(1, '情绪分析', '0', '1', 'emotion', null, null, '', 1, 0, 'M', '0', '0', '', 'chart', 'admin', sysdate(), '', null, '');
insert into sys_menu values(2, '检测记录', '0', '2', 'allLook', 'system/allLook/index', null, '', 1, 0, 'C', '0', '0', 'system:allLook:list', 'monitor', 'admin', sysdate(), '', null, '');
insert into sys_menu values(3, '班级学生', '0', '3', 'class/student', 'system/class/index', '', '', 1, 0, 'C', '0', '0', 'system:user:list', 'user', 'admin', sysdate(), '', null, '');
insert into sys_menu values(4, '课程管理', '0', '4', 'course', 'course/index/index', null, '', 1, 0, 'C', '0', '0', 'cell:course:list', 'time-range', 'admin', sysdate(), '', null, '');
insert into sys_menu values(5, '摄像头管理', '0', '5', 'cellManagement', null, null, '', 1, 0, 'M', '0', '0', '', 'switch', 'admin', sysdate(), '', null, '');
insert into sys_menu values(6, '系统管理', '0', '6', 'system', null, '', '', 1, 0, 'M', '0', '0', '', 'system', 'admin', sysdate(), '', null, '');
insert into sys_menu values(7, '系统监控', '0', '7', 'monitor', null, '', '', 1, 0, 'M', '0', '0', '', 'redis-list', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(8, '系统工具', '0', '8', 'tool', null, '', '', 1, 0, 'M', '0', '0', '', 'tool', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(9, '重点人员监测', '0', '9', 'aberrantEmotions', 'emotion/aberrantEmotions/index', null, '', 1, 0, 'C', '0', '0', '', 'component', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(10, '陌生人员监测', '0', '10', 'stranger', 'emotion/stranger/index', null, '', 1, 0, 'C', '0', '0', '', 'question', 'admin', sysdate(), '', null, '');
-- 二级菜单
insert into sys_menu values(100, '学生情绪状态', '1', '1', 'studentEmotion', 'emotion/studentEmotion/index', null, '', 1, 0, 'C', '0', '0', '', 'education', 'admin', sysdate(), '', null, '');
insert into sys_menu values(101, '学生各周情绪状态', '1', '2', 'dailyEmotion', 'emotion/dailyEmotion/index', null, '', 1, 0, 'C', '0', '0', '', 'date', 'admin', sysdate(), '', null, '');
insert into sys_menu values(102, '班级情绪状态', '1', '3', 'classEmotion', 'emotion/classEmotion/index', null, '', 1, 0, 'C', '0', '0', '', 'peoples', 'admin', sysdate(), '', null, '');
insert into sys_menu values(103, '摄像头区域管理', '5', '1', 'region', 'cellManagement/region/index', null, '', 1, 0, 'C', '0', '0', '', 'tree', 'admin', sysdate(), '', null, '');
insert into sys_menu values(104, '摄像头信息管理', '5', '2', 'camera', 'cellManagement/camera/index', null, '', 1, 0, 'C', '0', '0', '', 'eye-open', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(105, '摄像头预警管理', '5', '3', 'warn', 'cellManagement/warn/index', null, '', 1, 0, 'C', '0', '0', '', 'eye', 'admin', sysdate(), '', null, '');
insert into sys_menu values(106, '用户管理', '6', '1', 'user', 'system/user/index', '', '', 1, 0, 'C', '0', '0', 'system:user:list', 'user', 'admin', sysdate(), '', null, '');
insert into sys_menu values(107, '角色管理', '6', '2', 'role', 'system/role/index', '', '', 1, 0, 'C', '0', '0', 'system:role:list', 'peoples', 'admin', sysdate(), '', null, '');
insert into sys_menu values(108, '菜单管理', '6', '3', 'menu', 'system/menu/index', '', '', 1, 0, 'C', '0', '0', 'system:menu:list', 'tree-table', 'admin', sysdate(), '', null, '');
insert into sys_menu values(109, '部门管理', '6', '4', 'dept', 'system/dept/index', '', '', 1, 0, 'C', '0', '0', 'system:dept:list', 'tree', 'admin', sysdate(), '', null, '');
insert into sys_menu values(110, '岗位管理', '6', '5', 'post', 'system/post/index', '', '', 1, 0, 'C', '0', '0', 'system:post:list', 'post', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(111, '字典管理', '6', '6', 'dict', 'system/dict/index', '', '', 1, 0, 'C', '0', '0', 'system:dict:list', 'dict', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(112, '参数设置', '6', '7', 'config', 'system/config/index', '', '', 1, 0, 'C', '0', '0', 'system:config:list', 'edit', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(113, '通知公告', '6', '8', 'notice', 'system/notice/index', '', '', 1, 0, 'C', '0', '0', 'system:notice:list', 'message', 'admin', sysdate(), '', null, '');
insert into sys_menu values(114, '日志管理', '6', '9', 'log', '', '', '', 1, 0, 'M', '0', '0', '', 'log', 'admin', sysdate(), '', null, '');
insert into sys_menu values(115, '在线用户', '7', '1', 'online', 'monitor/online/index', '', '', 1, 0, 'C', '0', '0', 'monitor:online:list', 'online', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(116, '定时任务', '7', '2', 'job', 'monitor/job/index', '', '', 1, 0, 'C', '0', '0', 'monitor:job:list', 'job', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(117, '数据监控', '7', '3', 'druid', 'monitor/druid/index', '', '', 1, 0, 'C', '0', '0', 'monitor:druid:list', 'druid', 'admin', sysdate(), '', null, '');
insert into sys_menu values(118, '服务监控', '7', '4', 'server', 'monitor/server/index', '', '', 1, 0, 'C', '0', '0', 'monitor:server:list', 'server', 'admin', sysdate(), '', null, '');
insert into sys_menu values(119, '缓存监控', '7', '5', 'cache', 'monitor/cache/index', '', '', 1, 0, 'C', '0', '0', 'monitor:cache:list', 'redis', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(120, '缓存列表', '7', '6', 'cacheList', 'monitor/cache/list', '', '', 1, 0, 'C', '0', '0', 'monitor:cache:list', 'redis-list', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(121, '表单构建', '8', '1', 'build', 'tool/build/index', '', '', 1, 0, 'C', '0', '0', 'tool:build:list', 'build', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(122, '代码生成', '8', '2', 'gen', 'tool/gen/index', '', '', 1, 0, 'C', '0', '0', 'tool:gen:list', 'code', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(123, '系统接口', '8', '3', 'swagger', 'tool/swagger/index', '', '', 1, 0, 'C', '0', '0', 'tool:swagger:list', 'swagger', 'admin', sysdate(), '', null, '');
-- 三级菜单
insert into sys_menu values(500, '操作日志', '114', '1', 'operlog', 'monitor/operlog/index', '', '', 1, 0, 'C', '0', '0', 'monitor:operlog:list', 'form', 'admin', sysdate(), '', null, '');
insert into sys_menu values(501, '登录日志', '114', '2', 'logininfor', 'monitor/logininfor/index', '', '', 1, 0, 'C', '0', '0', 'monitor:logininfor:list', 'logininfor', 'admin', sysdate(), '', null, '');
-- 用户管理按钮
insert into sys_menu values(1000, '用户查询', '106', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1001, '用户新增', '106', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1002, '用户修改', '106', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1003, '用户删除', '106', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:remove',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1004, '用户导出', '106', '5',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:export',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1005, '用户导入', '106', '6',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:import',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1006, '重置密码', '106', '7',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:resetPwd',       '#', 'admin', sysdate(), '', null, '');
-- 角色管理按钮
insert into sys_menu values(1007, '角色查询', '107', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1008, '角色新增', '107', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1009, '角色修改', '107', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1010, '角色删除', '107', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:remove',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1011, '角色导出', '107', '5',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:export',         '#', 'admin', sysdate(), '', null, '');
-- 菜单管理按钮
insert into sys_menu values(1012, '菜单查询', '108', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1013, '菜单新增', '108', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1014, '菜单修改', '108', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1015, '菜单删除', '108', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:remove',         '#', 'admin', sysdate(), '', null, '');
-- 部门管理按钮
insert into sys_menu values(1016, '部门查询', '109', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1017, '部门新增', '109', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1018, '部门修改', '109', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1019, '部门删除', '109', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:remove',         '#', 'admin', sysdate(), '', null, '');
-- 岗位管理按钮
insert into sys_menu values(1020, '岗位查询', '110', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1021, '岗位新增', '110', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1022, '岗位修改', '110', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1023, '岗位删除', '110', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:remove',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1024, '岗位导出', '110', '5',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:export',         '#', 'admin', sysdate(), '', null, '');
-- 字典管理按钮
-- insert into sys_menu values(1025, '字典查询', '111', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:query',          '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1026, '字典新增', '111', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:add',            '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1027, '字典修改', '111', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:edit',           '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1028, '字典删除', '111', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:remove',         '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1029, '字典导出', '111', '5', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:export',         '#', 'admin', sysdate(), '', null, '');
-- 参数设置按钮
-- insert into sys_menu values(1030, '参数查询', '112', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:query',        '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1031, '参数新增', '112', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:add',          '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1032, '参数修改', '112', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:edit',         '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1033, '参数删除', '112', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:remove',       '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1034, '参数导出', '112', '5', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:export',       '#', 'admin', sysdate(), '', null, '');
-- 通知公告按钮
-- insert into sys_menu values(1035, '公告查询', '113', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:query',        '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1036, '公告新增', '113', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:add',          '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1037, '公告修改', '113', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:edit',         '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1038, '公告删除', '113', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:remove',       '#', 'admin', sysdate(), '', null, '');
-- 操作日志按钮
insert into sys_menu values(1039, '操作查询', '500', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:query',      '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1040, '操作删除', '500', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:remove',     '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1041, '日志导出', '500', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:export',     '#', 'admin', sysdate(), '', null, '');
-- 登录日志按钮
insert into sys_menu values(1042, '登录查询', '501', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:query',   '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1043, '登录删除', '501', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:remove',  '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1044, '日志导出', '501', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:export',  '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1045, '账户解锁', '501', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:unlock',  '#', 'admin', sysdate(), '', null, '');
-- 在线用户按钮
insert into sys_menu values(1046, '在线查询', '115', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:query',       '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1047, '批量强退', '115', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:batchLogout', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(1048, '单条强退', '115', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:forceLogout', '#', 'admin', sysdate(), '', null, '');
-- 定时任务按钮
-- insert into sys_menu values(1049, '任务查询', '116', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:query',          '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1050, '任务新增', '116', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:add',            '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1051, '任务修改', '116', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:edit',           '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1052, '任务删除', '116', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:remove',         '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1053, '状态修改', '116', '5', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:changeStatus',   '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1054, '任务导出', '116', '6', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:export',         '#', 'admin', sysdate(), '', null, '');
-- 代码生成按钮
-- insert into sys_menu values(1055, '生成查询', '122', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:query',             '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1056, '生成修改', '122', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:edit',              '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1057, '生成删除', '122', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:remove',            '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1058, '导入代码', '122', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:import',            '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1059, '预览代码', '122', '5', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:preview',           '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(1060, '生成代码', '122', '6', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:code',              '#', 'admin', sysdate(), '', null, '');
-- 摄像头按钮
insert into sys_menu values(2004, '摄像头查询', '104', '1', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:camera:query', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(2005, '摄像头新增', '104', '2', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:camera:add', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(2006, '摄像头修改', '104', '3', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:camera:edit', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(2007, '摄像头删除', '104', '4', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:camera:remove', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values(2008, '摄像头导出', '104', '5', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:camera:export', '#', 'admin', sysdate(), '', null, '');
-- 摄像头预警按钮
-- insert into sys_menu values(2014, '摄像头预警查询', '105', '1', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:warn:query', '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(2015, '摄像头预警新增', '105', '2', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:warn:add', '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(2016, '摄像头预警修改', '105', '3', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:warn:edit', '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(2017, '摄像头预警删除', '105', '4', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:warn:remove', '#', 'admin', sysdate(), '', null, '');
-- insert into sys_menu values(2018, '摄像头预警导出', '105', '5', '#', '', null, '', 1, 0, 'F', '0', '0', 'camera:warn:export', '#', 'admin', sysdate(), '', null, '');


-- ----------------------------
-- 6、用户和角色关联表
-- ----------------------------
drop table if exists sys_user_role;
create table sys_user_role (
  user_id   bigint(20) not null comment '用户ID',
  role_id   bigint(20) not null comment '角色ID',
  primary key(user_id, role_id)
) engine=innodb comment = '用户和角色关联表';

-- ----------------------------
-- 初始化-用户和角色关联表数据
-- ----------------------------
insert into sys_user_role values ('1', '1');
insert into sys_user_role values ('2', '2');


-- ----------------------------
-- 7、角色和菜单关联表
-- ----------------------------
drop table if exists sys_role_menu;
create table sys_role_menu (
  role_id   bigint(20) not null comment '角色ID',
  menu_id   bigint(20) not null comment '菜单ID',
  primary key(role_id, menu_id)
) engine=innodb comment = '角色和菜单关联表';

-- ----------------------------
-- 初始化-角色和菜单关联表数据
-- ----------------------------
insert into sys_role_menu select 1, menu_id from sys_menu;
insert into sys_role_menu values (2, 1);
insert into sys_role_menu values (2, 2);
insert into sys_role_menu values (2, 3);
insert into sys_role_menu values (2, 4);
insert into sys_role_menu values (2, 5);
insert into sys_role_menu values (2, 100);
insert into sys_role_menu values (2, 101);
insert into sys_role_menu values (2, 102);
insert into sys_role_menu values (2, 103);
insert into sys_role_menu values (2, 104);
insert into sys_role_menu values (2, 105);


-- ----------------------------
-- 8、角色和部门关联表
-- ----------------------------
drop table if exists sys_role_dept;
create table sys_role_dept (
  role_id   bigint(20) not null comment '角色ID',
  dept_id   bigint(20) not null comment '部门ID',
  primary key(role_id, dept_id)
) engine=innodb comment = '角色和部门关联表';

-- ----------------------------
-- 初始化-角色和部门关联表数据
-- ----------------------------
insert into sys_role_dept values ('2', '100');
insert into sys_role_dept values ('2', '101');
insert into sys_role_dept values ('2', '105');


-- ----------------------------
-- 9、用户与岗位关联表
-- ----------------------------
drop table if exists sys_user_post;
create table sys_user_post
(
  user_id   bigint(20) not null comment '用户ID',
  post_id   bigint(20) not null comment '岗位ID',
  primary key (user_id, post_id)
) engine=innodb comment = '用户与岗位关联表';

-- ----------------------------
-- 初始化-用户与岗位关联表数据
-- ----------------------------
insert into sys_user_post values ('1', '1');
insert into sys_user_post values ('2', '2');


-- ----------------------------
-- 10、操作日志记录
-- ----------------------------
drop table if exists sys_oper_log;
create table sys_oper_log (
  oper_id           bigint(20)      not null auto_increment    comment '日志主键',
  title             varchar(50)     default ''                 comment '模块标题',
  business_type     int(2)          default 0                  comment '业务类型（0其它 1新增 2修改 3删除）',
  method            varchar(100)    default ''                 comment '方法名称',
  request_method    varchar(10)     default ''                 comment '请求方式',
  operator_type     int(1)          default 0                  comment '操作类别（0其它 1后台用户 2手机端用户）',
  oper_name         varchar(50)     default ''                 comment '操作人员',
  dept_name         varchar(50)     default ''                 comment '部门名称',
  oper_url          varchar(255)    default ''                 comment '请求URL',
  oper_ip           varchar(128)    default ''                 comment '主机地址',
  oper_location     varchar(255)    default ''                 comment '操作地点',
  oper_param        varchar(2000)   default ''                 comment '请求参数',
  json_result       varchar(2000)   default ''                 comment '返回参数',
  status            int(1)          default 0                  comment '操作状态（0正常 1异常）',
  error_msg         varchar(2000)   default ''                 comment '错误消息',
  oper_time         datetime                                   comment '操作时间',
  cost_time         bigint(20)      default 0                  comment '消耗时间',
  primary key (oper_id),
  key idx_sys_oper_log_bt (business_type),
  key idx_sys_oper_log_s  (status),
  key idx_sys_oper_log_ot (oper_time)
) engine=innodb auto_increment=100 comment = '操作日志记录';

-- ----------------------------
-- 11、字典类型表
-- ----------------------------
drop table if exists sys_dict_type;
create table sys_dict_type
(
  dict_id          bigint(20)      not null auto_increment    comment '字典主键',
  dict_name        varchar(100)    default ''                 comment '字典名称',
  dict_type        varchar(100)    default ''                 comment '字典类型',
  status           char(1)         default '0'                comment '状态（0正常 1停用）',
  create_by        varchar(64)     default ''                 comment '创建者',
  create_time      datetime                                   comment '创建时间',
  update_by        varchar(64)     default ''                 comment '更新者',
  update_time      datetime                                   comment '更新时间',
  remark           varchar(500)    default null               comment '备注',
  primary key (dict_id),
  unique (dict_type)
) engine=innodb auto_increment=100 comment = '字典类型表';

-- ----------------------------
-- 初始化-字典类型表数据
-- ----------------------------
insert into sys_dict_type values(1,  '用户性别',     'sys_user_sex',        '0', 'admin', sysdate(), '', null, '用户性别列表');
insert into sys_dict_type values(2,  '菜单状态',     'sys_show_hide',       '0', 'admin', sysdate(), '', null, '菜单状态列表');
insert into sys_dict_type values(3,  '系统开关',     'sys_normal_disable',  '0', 'admin', sysdate(), '', null, '系统开关列表');
insert into sys_dict_type values(4,  '任务状态',     'sys_job_status',      '0', 'admin', sysdate(), '', null, '任务状态列表');
insert into sys_dict_type values(5,  '任务分组',     'sys_job_group',       '0', 'admin', sysdate(), '', null, '任务分组列表');
insert into sys_dict_type values(6,  '任务执行器',   'sys_job_executor',    '0', 'admin', sysdate(), '', null, '任务执行器列表');
insert into sys_dict_type values(7,  '系统是否',     'sys_yes_no',          '0', 'admin', sysdate(), '', null, '系统是否列表');
insert into sys_dict_type values(8,  '通知类型',     'sys_notice_type',     '0', 'admin', sysdate(), '', null, '通知类型列表');
insert into sys_dict_type values(9,  '通知状态', 	   'sys_notice_status',   '0', 'admin', sysdate(), '', null, '通知状态列表');
insert into sys_dict_type values(10, '操作类型', 	   'sys_oper_type',       '0', 'admin', sysdate(), '', null, '操作类型列表');
insert into sys_dict_type values(11, '系统状态',     'sys_common_status',   '0', 'admin', sysdate(), '', null, '登录状态列表');


-- ----------------------------
-- 12、字典数据表
-- ----------------------------
drop table if exists sys_dict_data;
create table sys_dict_data
(
  dict_code        bigint(20)      not null auto_increment    comment '字典编码',
  dict_sort        int(4)          default 0                  comment '字典排序',
  dict_label       varchar(100)    default ''                 comment '字典标签',
  dict_value       varchar(100)    default ''                 comment '字典键值',
  dict_type        varchar(100)    default ''                 comment '字典类型',
  css_class        varchar(100)    default null               comment '样式属性（其他样式扩展）',
  list_class       varchar(100)    default null               comment '表格回显样式',
  is_default       char(1)         default 'N'                comment '是否默认（Y是 N否）',
  status           char(1)         default '0'                comment '状态（0正常 1停用）',
  create_by        varchar(64)     default ''                 comment '创建者',
  create_time      datetime                                   comment '创建时间',
  update_by        varchar(64)     default ''                 comment '更新者',
  update_time      datetime                                   comment '更新时间',
  remark           varchar(500)    default null               comment '备注',
  primary key (dict_code)
) engine=innodb auto_increment=100 comment = '字典数据表';

-- ----------------------------
-- 初始化-字典类型数据表数据
-- ----------------------------
insert into sys_dict_data values(1,  1,  '男',             '0',                'sys_user_sex',        '',   '',        'Y', '0', 'admin', sysdate(), '', null, '性别男');
insert into sys_dict_data values(2,  2,  '女',             '1',                'sys_user_sex',        '',   '',        'N', '0', 'admin', sysdate(), '', null, '性别女');
insert into sys_dict_data values(3,  3,  '未知',            '2',                'sys_user_sex',        '',   '',        'N', '0', 'admin', sysdate(), '', null, '性别未知');
insert into sys_dict_data values(4,  1,  '显示',            '0',                'sys_show_hide',       '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, '显示菜单');
insert into sys_dict_data values(5,  2,  '隐藏',            '1',                'sys_show_hide',       '',   'danger',  'N', '0', 'admin', sysdate(), '', null, '隐藏菜单');
insert into sys_dict_data values(6,  1,  '正常',            '0',                'sys_normal_disable',  '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, '正常状态');
insert into sys_dict_data values(7,  2,  '停用',            '1',                'sys_normal_disable',  '',   'danger',  'N', '0', 'admin', sysdate(), '', null, '停用状态');
insert into sys_dict_data values(8,  1,  '正常',            '0',                'sys_job_status',      '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, '正常状态');
insert into sys_dict_data values(9,  2,  '暂停',            '1',                'sys_job_status',      '',   'danger',  'N', '0', 'admin', sysdate(), '', null, '停用状态');
insert into sys_dict_data values(10, 1,  '默认',            'default',          'sys_job_group',       '',   '',        'Y', '0', 'admin', sysdate(), '', null, '默认分组');
insert into sys_dict_data values(11, 2,  '数据库',          'sqlalchemy',       'sys_job_group',       '',   '',        'N', '0', 'admin', sysdate(), '', null, '数据库分组');
insert into sys_dict_data values(12, 3,  'redis',          'redis',  			     'sys_job_group',       '',   '',        'N', '0', 'admin', sysdate(), '', null, 'reids分组');
insert into sys_dict_data values(13, 1,  '默认',            'default',  		    'sys_job_executor',    '',   '',        'N', '0', 'admin', sysdate(), '', null, '线程池');
insert into sys_dict_data values(14, 2,  '进程池',          'processpool',      'sys_job_executor',    '',   '',        'N', '0', 'admin', sysdate(), '', null, '进程池');
insert into sys_dict_data values(15, 1,  '是',              'Y',       		      'sys_yes_no',          '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, '系统默认是');
insert into sys_dict_data values(16, 2,  '否',              'N',       		      'sys_yes_no',          '',   'danger',  'N', '0', 'admin', sysdate(), '', null, '系统默认否');
insert into sys_dict_data values(17, 1,  '通知',            '1',       		      'sys_notice_type',     '',   'warning', 'Y', '0', 'admin', sysdate(), '', null, '通知');
insert into sys_dict_data values(18, 2,  '公告',            '2',       		      'sys_notice_type',     '',   'success', 'N', '0', 'admin', sysdate(), '', null, '公告');
insert into sys_dict_data values(19, 1,  '正常',            '0',       		      'sys_notice_status',   '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, '正常状态');
insert into sys_dict_data values(20, 2,  '关闭',            '1',       		      'sys_notice_status',   '',   'danger',  'N', '0', 'admin', sysdate(), '', null, '关闭状态');
insert into sys_dict_data values(21, 99, '其他',            '0',       		      'sys_oper_type',       '',   'info',    'N', '0', 'admin', sysdate(), '', null, '其他操作');
insert into sys_dict_data values(22, 1,  '新增',            '1',       		      'sys_oper_type',       '',   'info',    'N', '0', 'admin', sysdate(), '', null, '新增操作');
insert into sys_dict_data values(23, 2,  '修改',            '2',       		      'sys_oper_type',       '',   'info',    'N', '0', 'admin', sysdate(), '', null, '修改操作');
insert into sys_dict_data values(24, 3,  '删除',            '3',       		      'sys_oper_type',       '',   'danger',  'N', '0', 'admin', sysdate(), '', null, '删除操作');
insert into sys_dict_data values(25, 4,  '授权',            '4',       		      'sys_oper_type',       '',   'primary', 'N', '0', 'admin', sysdate(), '', null, '授权操作');
insert into sys_dict_data values(26, 5,  '导出',            '5',       		      'sys_oper_type',       '',   'warning', 'N', '0', 'admin', sysdate(), '', null, '导出操作');
insert into sys_dict_data values(27, 6,  '导入',            '6',       		      'sys_oper_type',       '',   'warning', 'N', '0', 'admin', sysdate(), '', null, '导入操作');
insert into sys_dict_data values(28, 7,  '强退',            '7',       		      'sys_oper_type',       '',   'danger',  'N', '0', 'admin', sysdate(), '', null, '强退操作');
insert into sys_dict_data values(29, 8,  '生成代码',         '8',       		     'sys_oper_type',       '',   'warning', 'N', '0', 'admin', sysdate(), '', null, '生成操作');
insert into sys_dict_data values(30, 9,  '清空数据',         '9',       		     'sys_oper_type',       '',   'danger',  'N', '0', 'admin', sysdate(), '', null, '清空操作');
insert into sys_dict_data values(31, 1,  '成功',            '0',       		       'sys_common_status',   '',   'primary', 'N', '0', 'admin', sysdate(), '', null, '正常状态');
insert into sys_dict_data values(32, 2,  '失败',            '1',       		       'sys_common_status',   '',   'danger',  'N', '0', 'admin', sysdate(), '', null, '停用状态');


-- ----------------------------
-- 13、参数配置表
-- ----------------------------
drop table if exists sys_config;
create table sys_config (
  config_id         int(5)          not null auto_increment    comment '参数主键',
  config_name       varchar(100)    default ''                 comment '参数名称',
  config_key        varchar(100)    default ''                 comment '参数键名',
  config_value      varchar(500)    default ''                 comment '参数键值',
  config_type       char(1)         default 'N'                comment '系统内置（Y是 N否）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (config_id)
) engine=innodb auto_increment=100 comment = '参数配置表';

-- ----------------------------
-- 初始化-参数配置表数据
-- ----------------------------
insert into sys_config values(1, '主框架页-默认皮肤样式名称',     'sys.index.skinName',            'skin-blue',     'Y', 'admin', sysdate(), '', null, '蓝色 skin-blue、绿色 skin-green、紫色 skin-purple、红色 skin-red、黄色 skin-yellow' );
insert into sys_config values(2, '用户管理-账号初始密码',         'sys.user.initPassword',         '123456',        'Y', 'admin', sysdate(), '', null, '初始化密码 123456' );
insert into sys_config values(3, '主框架页-侧边栏主题',           'sys.index.sideTheme',           'theme-dark',    'Y', 'admin', sysdate(), '', null, '深色主题theme-dark，浅色主题theme-light' );
insert into sys_config values(4, '账号自助-验证码开关',           'sys.account.captchaEnabled',    'true',          'Y', 'admin', sysdate(), '', null, '是否开启验证码功能（true开启，false关闭）');
insert into sys_config values(5, '账号自助-是否开启用户注册功能', 'sys.account.registerUser',      'false',         'Y', 'admin', sysdate(), '', null, '是否开启注册用户功能（true开启，false关闭）');
insert into sys_config values(6, '用户登录-黑名单列表',           'sys.login.blackIPList',         '',              'Y', 'admin', sysdate(), '', null, '设置登录IP黑名单限制，多个匹配项以;分隔，支持匹配（*通配、网段）');
insert into sys_config values(7, '用户管理-初始密码修改策略',     'sys.account.initPasswordModify',  '1',             'Y', 'admin', sysdate(), '', null, '0：初始密码修改策略关闭，没有任何提示，1：提醒用户，如果未修改初始密码，则在登录时就会提醒修改密码对话框');
insert into sys_config values(8, '用户管理-账号密码更新周期',     'sys.account.passwordValidateDays', '0',             'Y', 'admin', sysdate(), '', null, '密码更新周期（填写数字，数据初始化值为0不限制，若修改必须为大于0小于365的正整数），如果超过这个周期登录系统时，则在登录时就会提醒修改密码对话框');


-- ----------------------------
-- 14、系统访问记录
-- ----------------------------
drop table if exists sys_logininfor;
create table sys_logininfor (
  info_id        bigint(20)     not null auto_increment   comment '访问ID',
  user_name      varchar(50)    default ''                comment '用户账号',
  ipaddr         varchar(128)   default ''                comment '登录IP地址',
  login_location varchar(255)   default ''                comment '登录地点',
  browser        varchar(50)    default ''                comment '浏览器类型',
  os             varchar(50)    default ''                comment '操作系统',
  status         char(1)        default '0'               comment '登录状态（0成功 1失败）',
  msg            varchar(255)   default ''                comment '提示消息',
  login_time     datetime                                 comment '访问时间',
  primary key (info_id),
  key idx_sys_logininfor_s  (status),
  key idx_sys_logininfor_lt (login_time)
) engine=innodb auto_increment=100 comment = '系统访问记录';

-- ----------------------------
-- 15、定时任务调度表
-- ----------------------------
drop table if exists sys_job;
create table sys_job (
  job_id              bigint(20)    not null auto_increment    comment '任务ID',
  job_name            varchar(64)   default ''                 comment '任务名称',
  job_group           varchar(64)   default 'default'          comment '任务组名',
  job_executor        varchar(64)   default 'default'          comment '任务执行器',
  invoke_target       varchar(500)  not null                   comment '调用目标字符串',
  job_args            varchar(255)  default ''                 comment '位置参数',
  job_kwargs          varchar(255)  default ''                 comment '关键字参数',
  cron_expression     varchar(255)  default ''                 comment 'cron执行表达式',
  misfire_policy      varchar(20)   default '3'                comment '计划执行错误策略（1立即执行 2执行一次 3放弃执行）',
  concurrent          char(1)       default '1'                comment '是否并发执行（0允许 1禁止）',
  status              char(1)       default '0'                comment '状态（0正常 1暂停）',
  create_by           varchar(64)   default ''                 comment '创建者',
  create_time         datetime                                 comment '创建时间',
  update_by           varchar(64)   default ''                 comment '更新者',
  update_time         datetime                                 comment '更新时间',
  remark              varchar(500)  default ''                 comment '备注信息',
  primary key (job_id, job_name, job_group)
) engine=innodb auto_increment=100 comment = '定时任务调度表';

-- ----------------------------
-- 初始化-定时任务调度表数据
-- ----------------------------
insert into sys_job values(1, '系统默认（无参）', 'default', 'default', 'module_task.scheduler_test.job', NULL,   NULL, '0/10 * * * * ?', '3', '1', '1', 'admin', sysdate(), '', null, '');
insert into sys_job values(2, '系统默认（有参）', 'default', 'default', 'module_task.scheduler_test.job', 'test', NULL, '0/15 * * * * ?', '3', '1', '1', 'admin', sysdate(), '', null, '');
insert into sys_job values(3, '系统默认（多参）', 'default', 'default', 'module_task.scheduler_test.job', 'new',  '{\"test\": 111}', '0/20 * * * * ?', '3', '1', '1', 'admin', sysdate(), '', null, '');


-- ----------------------------
-- 16、定时任务调度日志表
-- ----------------------------
drop table if exists sys_job_log;
create table sys_job_log (
  job_log_id          bigint(20)     not null auto_increment    comment '任务日志ID',
  job_name            varchar(64)    not null                   comment '任务名称',
  job_group           varchar(64)    not null                   comment '任务组名',
  job_executor        varchar(64)    not null                   comment '任务执行器',
  invoke_target       varchar(500)   not null                   comment '调用目标字符串',
  job_args            varchar(255)   default ''                 comment '位置参数',
  job_kwargs          varchar(255)   default ''                 comment '关键字参数',
  job_trigger         varchar(255)   default ''                 comment '任务触发器',
  job_message         varchar(500)                              comment '日志信息',
  status              char(1)        default '0'                comment '执行状态（0正常 1失败）',
  exception_info      varchar(2000)  default ''                 comment '异常信息',
  create_time         datetime                                  comment '创建时间',
  primary key (job_log_id)
) engine=innodb comment = '定时任务调度日志表';

-- ----------------------------
-- 17、通知公告表
-- ----------------------------
drop table if exists sys_notice;
create table sys_notice (
  notice_id         int(4)          not null auto_increment    comment '公告ID',
  notice_title      varchar(50)     not null                   comment '公告标题',
  notice_type       char(1)         not null                   comment '公告类型（1通知 2公告）',
  notice_content    longblob        default null               comment '公告内容',
  status            char(1)         default '0'                comment '公告状态（0正常 1关闭）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(255)    default null               comment '备注',
  primary key (notice_id)
) engine=innodb auto_increment=10 comment = '通知公告表';

-- ----------------------------
-- 初始化-通知公告表数据
-- ----------------------------
insert into sys_notice values('1', '温馨提醒：2026-02-01 vfadmin新版本发布啦', '2', '新版本内容', '0', 'admin', sysdate(), '', null, '管理员');
insert into sys_notice values('2', '维护通知：2026-02-01 vfadmin系统凌晨维护', '1', '维护内容',   '0', 'admin', sysdate(), '', null, '管理员');


-- ----------------------------
-- 18、代码生成业务表
-- ----------------------------
drop table if exists gen_table;
create table gen_table (
  table_id          bigint(20)      not null auto_increment    comment '编号',
  table_name        varchar(200)    default ''                 comment '表名称',
  table_comment     varchar(500)    default ''                 comment '表描述',
  sub_table_name    varchar(64)     default null               comment '关联子表的表名',
  sub_table_fk_name varchar(64)     default null               comment '子表关联的外键名',
  class_name        varchar(100)    default ''                 comment '实体类名称',
  tpl_category      varchar(200)    default 'crud'             comment '使用的模板（crud单表操作 tree树表操作）',
  tpl_web_type      varchar(30)     default ''                 comment '前端模板类型（element-ui模版 element-plus模版）',
  package_name      varchar(100)                               comment '生成包路径',
  module_name       varchar(30)                                comment '生成模块名',
  business_name     varchar(30)                                comment '生成业务名',
  function_name     varchar(50)                                comment '生成功能名',
  function_author   varchar(50)                                comment '生成功能作者',
  gen_type          char(1)         default '0'                comment '生成代码方式（0zip压缩包 1自定义路径）',
  gen_path          varchar(200)    default '/'                comment '生成路径（不填默认项目路径）',
  options           varchar(1000)                              comment '其它生成选项',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time 	    datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default null               comment '备注',
  primary key (table_id)
) engine=innodb auto_increment=1 comment = '代码生成业务表';

-- ----------------------------
-- 19、代码生成业务表字段
-- ----------------------------
drop table if exists gen_table_column;
create table gen_table_column (
  column_id         bigint(20)      not null auto_increment    comment '编号',
  table_id          bigint(20)                                 comment '归属表编号',
  column_name       varchar(200)                               comment '列名称',
  column_comment    varchar(500)                               comment '列描述',
  column_type       varchar(100)                               comment '列类型',
  python_type       varchar(500)                               comment 'PYTHON类型',
  python_field      varchar(200)                               comment 'PYTHON字段名',
  is_pk             char(1)                                    comment '是否主键（1是）',
  is_increment      char(1)                                    comment '是否自增（1是）',
  is_required       char(1)                                    comment '是否必填（1是）',
  is_unique         char(1)                                    comment '是否唯一（1是）',
  is_insert         char(1)                                    comment '是否为插入字段（1是）',
  is_edit           char(1)                                    comment '是否编辑字段（1是）',
  is_list           char(1)                                    comment '是否列表字段（1是）',
  is_query          char(1)                                    comment '是否查询字段（1是）',
  query_type        varchar(200)    default 'EQ'               comment '查询方式（等于、不等于、大于、小于、范围）',
  html_type         varchar(200)                               comment '显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）',
  dict_type         varchar(200)    default ''                 comment '字典类型',
  sort              int                                        comment '排序',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time 	    datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  primary key (column_id)
) engine=innodb auto_increment=1 comment = '代码生成业务表字段';

SET FOREIGN_KEY_CHECKS=1;
