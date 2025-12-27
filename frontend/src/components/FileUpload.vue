<template>
  <div class="upload-container">
    <el-upload
      class="upload-demo"
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      :show-file-list="false"
      accept=".txt,.md,.jpg,.jpeg,.png,.bmp"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持文本文件 (.txt, .md) 和图片 (.jpg, .png)
        </div>
      </template>
    </el-upload>
    
    <el-button 
      v-if="selectedFile" 
      type="primary" 
      @click="uploadFile"
      :loading="uploading"
      class="upload-btn"
      size="large"
    >
      开始学习
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../services/api'

const emit = defineEmits(['upload-success'])

const selectedFile = ref(null)
const uploading = ref(false)

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  uploading.value = true
  
  try {
    const response = await api.uploadFile(selectedFile.value)
    ElMessage.success('文件上传成功！')
    emit('upload-success', response.data)
  } catch (error) {
    ElMessage.error('上传失败：' + error.message)
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-container {
  padding: 40px 20px;
  text-align: center;
}

.upload-demo {
  margin: 0 auto;
  max-width: 600px;
}

.upload-btn {
  margin-top: 30px;
  width: 200px;
  font-size: 16px;
}

.el-icon--upload {
  font-size: 67px;
  color: #409eff;
  margin-bottom: 16px;
}

.el-upload__text {
  font-size: 16px;
  color: #606266;
}

.el-upload__text em {
  color: #409eff;
  font-style: normal;
}

.el-upload__tip {
  margin-top: 12px;
  font-size: 14px;
  color: #909399;
}
</style>
