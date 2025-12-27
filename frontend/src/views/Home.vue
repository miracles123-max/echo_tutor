<template>
  <div class="home-container">
    <div class="header">
      <h1>
        <el-icon class="logo-icon"><Headset /></el-icon>
        Echo Tutor
      </h1>
      <p class="subtitle">AI 驱动的智能语言学习助手</p>
    </div>
    
    <!-- Upload Section -->
    <div v-if="!sessionId" class="upload-section">
      <FileUpload @upload-success="handleUploadSuccess" />
    </div>
    
    <!-- Learning Section -->
    <div v-else class="learning-section">
      <el-card class="content-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="section-info">
              <el-icon><Document /></el-icon>
              学习内容 ({{ currentData?.section }})
            </span>
            <el-button @click="resetSession" type="danger" :icon="RefreshLeft">
              重新开始
            </el-button>
          </div>
        </template>
        
        <!-- Text Display -->
        <div class="text-content">
          <el-icon class="content-icon"><Reading /></el-icon>
          <p>{{ currentData?.text }}</p>
        </div>
        
        <!-- Audio Player -->
        <div v-if="currentData?.audio_path" class="audio-section">
          <div class="audio-header">
            <el-icon><Microphone /></el-icon>
            <span>发音练习</span>
          </div>
          <audio 
            controls 
            :src="getAudioUrl(currentData.audio_path)"
            class="audio-player"
          >
          </audio>
        </div>
        
        <!-- Questions -->
        <div v-if="currentData?.questions && currentData.questions.length > 0" class="questions-section">
          <div class="questions-header">
            <el-icon><QuestionFilled /></el-icon>
            <h3>练习题</h3>
          </div>
          
          <div 
            v-for="(question, index) in currentData?.questions" 
            :key="index"
            class="question-item"
          >
            <p class="question-text">
              <span class="question-number">{{ index + 1 }}</span>
              {{ question.question }}
            </p>
            
            <el-radio-group v-model="answers[index]" class="options">
              <el-radio 
                v-for="(option, optIdx) in question.options" 
                :key="optIdx"
                :label="option"
                class="option-item"
                border
              >
                {{ option }}
              </el-radio>
            </el-radio-group>
            
            <el-button 
              @click="submitAnswer(index)" 
              type="primary"
              :icon="Select"
              :disabled="!answers[index]"
              class="submit-btn"
            >
              提交答案
            </el-button>
            
            <!-- Feedback -->
            <el-alert
              v-if="feedback[index]"
              :title="feedback[index].is_correct ? '✓ 回答正确！' : '✗ 回答错误'"
              :type="feedback[index].is_correct ? 'success' : 'error'"
              :description="feedback[index].explanation"
              show-icon
              class="feedback-alert"
            />
          </div>
        </div>
        
        <!-- Navigation -->
        <div class="navigation">
          <el-button 
            @click="goToNextSection" 
            type="primary" 
            size="large"
            :icon="DArrowRight"
          >
            下一段内容
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import FileUpload from '../components/FileUpload.vue'
import api from '../services/api'
import { ElMessage } from 'element-plus'
import { 
  Headset, 
  Document, 
  Reading, 
  Microphone, 
  QuestionFilled, 
  Select,
  DArrowRight,
  RefreshLeft
} from '@element-plus/icons-vue'

const sessionId = ref(null)
const currentData = ref(null)
const answers = reactive({})
const feedback = reactive({})

const handleUploadSuccess = async (data) => {
  sessionId.value = data.file_id
  await loadCurrentSection()
}

const loadCurrentSection = async () => {
  try {
    const response = await api.getCurrentSection(sessionId.value)
    currentData.value = response.data
    
    if (response.data.completed) {
      ElMessage.success('恭喜！所有内容已学习完成！')
    }
  } catch (error) {
    ElMessage.error('加载内容失败：' + error.message)
  }
}

const getAudioUrl = (audioPath) => {
  const filename = audioPath.split('/').pop()
  return api.getAudioUrl(filename)
}

const submitAnswer = async (questionIndex) => {
  try {
    const response = await api.submitAnswer(
      sessionId.value,
      questionIndex.toString(),
      answers[questionIndex]
    )
    feedback[questionIndex] = response.data
    
    if (response.data.is_correct) {
      ElMessage.success('回答正确！')
    }
  } catch (error) {
    ElMessage.error('提交失败：' + error.message)
  }
}

const goToNextSection = async () => {
  try {
    await api.nextSection(sessionId.value)
    // Clear previous answers and feedback
    Object.keys(answers).forEach(key => delete answers[key])
    Object.keys(feedback).forEach(key => delete feedback[key])
    await loadCurrentSection()
    ElMessage.success('已切换到下一段')
  } catch (error) {
    ElMessage.error('切换失败：' + error.message)
  }
}

const resetSession = () => {
  sessionId.value = null
  currentData.value = null
  Object.keys(answers).forEach(key => delete answers[key])
  Object.keys(feedback).forEach(key => delete feedback[key])
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
  padding: 40px 20px;
}

.header h1 {
  font-size: 48px;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.logo-icon {
  font-size: 52px;
}

.subtitle {
  font-size: 20px;
  margin-top: 10px;
  opacity: 0.9;
}

.upload-section {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.learning-section {
  max-width: 1000px;
  margin: 0 auto;
}

.content-card {
  border-radius: 16px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
}

.section-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-content {
  font-size: 20px;
  line-height: 2;
  margin-bottom: 30px;
  padding: 30px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  position: relative;
}

.content-icon {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 24px;
  color: #909399;
}

.audio-section {
  text-align: center;
  margin: 40px 0;
  padding: 30px;
  background: #f0f9ff;
  border-radius: 12px;
}

.audio-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 20px;
}

.audio-player {
  width: 100%;
  max-width: 600px;
  margin-top: 10px;
}

.questions-section {
  margin-top: 40px;
}

.questions-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 25px;
  color: #303133;
}

.questions-header h3 {
  margin: 0;
  font-size: 22px;
}

.question-item {
  margin-bottom: 35px;
  padding: 25px;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  background: white;
  transition: all 0.3s;
}

.question-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
}

.question-text {
  font-weight: 600;
  font-size: 18px;
  margin-bottom: 20px;
  color: #303133;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.question-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  font-size: 16px;
  flex-shrink: 0;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.option-item {
  width: 100%;
  margin: 0;
  padding: 12px;
}

.submit-btn {
  margin-top: 10px;
}

.feedback-alert {
  margin-top: 20px;
  border-radius: 8px;
}

.navigation {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid #e4e7ed;
  text-align: center;
}
</style>
