<template>
  <div class="app-container">
    <el-card>
      <div slot="header">
        <span><i class="el-icon-warning-outline"></i> 功能说明</span>
      </div>
      <div style="text-align: center; padding: 50px 0;">
        <i class="el-icon-info" style="font-size: 60px; color: #e6a23c; margin-bottom: 20px;"></i>
        <h2 style="color: #606266;">该功能暂不可用</h2>
        <p style="color: #909399; font-size: 16px; line-height: 2;">
          如需监控数据库性能，建议使用数据库自带的监控工具或云厂商提供的监控服务。
        </p>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: "Druid"
};
</script>

<style scoped>
.app-container {
  padding: 20px;
}
</style>
