<script name="PaperExtract" setup>
/**
 * 摘要结构化信息组件
 * 
 * 用于显示论文的结构化摘要信息，包括背景、方法、结果和结论等内容
 * 支持通过props传入摘要结构信息，以及通过事件触发抽取操作
 * 
 * @props {Object} abstractStructure - 抽取的摘要结构信息
 * @props {Boolean} loading - 加载状态
 * @props {String|Number} paperId - 论文ID
 * 
 * @emits {extract} - 开始抽取事件，参数为论文ID
 */
import { ref, watch, inject, computed, onMounted } from 'vue'
import { formatDate, formatJSON } from '@/utils/paperUtils'
import { abstractStructureApi, llmModelApi, paperApi } from '@/api/literature'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  // 抽取结构信息
  abstractStructure: {
    type: Object,
    default: null
  },
  // 加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 当前论文ID
  paperId: {
    type: [String, Number],
    default: null
  }
})

// 定义emit事件
const emit = defineEmits(['extract'])
const proxy = inject('proxy')

// 添加抽取中状态
const extracting = ref(false)
const localLoading = ref(false)
const structureData = ref(null)
// 是否处于编辑状态
const isEditing = ref(false)
// 可用的LLM模型列表
const modelList = ref([])
// 选择的模型ID
const selectedModelId = ref('')
// 临时编辑的结构数据
const editData = ref({
  background: '',
  methods: '',
  results: '',
  conclusion: '',
  content: null
})

// 获取LLM模型列表
const getModelList = async () => {
  try {
    const res = await llmModelApi.getLlmModelList()
    if (res.code === 0 || res.code === 200) {
      modelList.value = res.data || []
      if (modelList.value.length > 0) {
        selectedModelId.value = modelList.value[0].id
      }
    }
  } catch (error) {
    console.error('获取模型列表失败', error)
  }
}

// 检查是否已抽取
const isExtracted = computed(() => {
  return props.abstractStructure && props.abstractStructure.data && props.abstractStructure.isExtracted
})

// 开始抽取方法
const startExtract = async () => {
  if (!props.paperId) {
    ElMessage.error('论文ID不能为空')
    return
  }
  
  if (!selectedModelId.value && modelList.value.length > 0) {
    selectedModelId.value = modelList.value[0].id
  }
  
  // 设置抽取中状态为true
  extracting.value = true
  
  try {
    if (selectedModelId.value) {
      // 使用选择的模型抽取
      await llmModelApi.extractStructureWithLlm({
        paper_id: props.paperId,
        model_id: selectedModelId.value
      })
    } else {
      // 使用默认方式抽取
      await paperApi.extractPaperAbstract(props.paperId)
    }
    // 触发父组件的抽取事件
    emit('extract', props.paperId)
  } catch (error) {
    console.error('抽取失败', error)
    ElMessage.error('抽取失败: ' + (error.message || '未知错误'))
    extracting.value = false
  }
}

// 进入编辑状态
const enterEditMode = () => {
  if (structureData.value) {
    editData.value = {
      background: structureData.value.background || '',
      methods: structureData.value.methods || '',
      results: structureData.value.results || '',
      conclusion: structureData.value.conclusion || '',
      content: structureData.value.content || null
    }
    isEditing.value = true
  }
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
}

// 提交结构化数据
const submitStructure = async () => {
  if (!props.paperId) {
    ElMessage.warning('论文ID不能为空')
    return
  }
  
  // 如果是编辑状态，使用编辑的数据
  const dataToSubmit = isEditing.value ? editData.value : structureData.value
  
  if (!dataToSubmit) {
    ElMessage.warning('无可提交的数据')
    return
  }
  
  localLoading.value = true
  try {
    const res = await abstractStructureApi.submitAbstractStructure(props.paperId, dataToSubmit)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('提交成功')
      if (isEditing.value) {
        // 更新本地数据
        structureData.value = { ...dataToSubmit }
        isEditing.value = false
      }
    } else {
      ElMessage.error('提交失败：' + (res.msg || '未知错误'))
    }
  } catch (error) {
    console.error('提交失败', error)
    ElMessage.error('提交失败: ' + (error.message || '未知错误'))
  } finally {
    localLoading.value = false
  }
}

// 重新抽取确认
const confirmReExtract = () => {
  ElMessageBox.confirm('重新抽取将覆盖现有结构，确定继续吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    startExtract()
  }).catch(() => {
    // 取消操作
  })
}

// 监听props中的loading属性变化，当loading变为false时，重置extracting状态
watch(() => props.loading, (newVal) => {
  if (!newVal && extracting.value) {
    // 延迟一点关闭extracting状态，以确保结果显示平滑
    setTimeout(() => {
      extracting.value = false
    }, 500)
  }
})

// 监听abstractStructure属性变化
watch(() => props.abstractStructure, (newVal) => {
  if (newVal && newVal.data) {
    structureData.value = { ...newVal.data }
  } else {
    structureData.value = null
  }
}, { immediate: true, deep: true })

// 组件挂载时获取模型列表
onMounted(() => {
  getModelList()
})
</script>

<template>
  <div v-loading="loading || localLoading">
    <div v-if="props.abstractStructure && props.abstractStructure.isExtracted" class="abstract-structure">
      <div class="extract-meta">
        <p><strong>抽取日期</strong> {{ formatDate(props.abstractStructure.data?.extraction_date) }}</p>
        <p><strong>抽取状态</strong> {{ props.abstractStructure.data?.extraction_status || '未知' }}</p>
        <p v-if="props.abstractStructure.data?.model_name"><strong>使用模型</strong> {{ props.abstractStructure.data?.model_name }}</p>
      </div>
      
      <el-tabs type="border-card">
        <!-- 非编辑状态下显示 -->
        <template v-if="!isEditing">
          <el-tab-pane label="背景">
            <div class="extract-content">{{ props.abstractStructure.data?.background || '无背景信息' }}</div>
          </el-tab-pane>
          <el-tab-pane label="方法">
            <div class="extract-content">{{ props.abstractStructure.data?.methods || '无方法信息' }}</div>
          </el-tab-pane>
          <el-tab-pane label="结果">
            <div class="extract-content">{{ props.abstractStructure.data?.results || '无结果信息' }}</div>
          </el-tab-pane>
          <el-tab-pane label="结论">
            <div class="extract-content">{{ props.abstractStructure.data?.conclusion || '无结论信息' }}</div>
          </el-tab-pane>
          <el-tab-pane label="结构化内容" v-if="props.abstractStructure.data?.content">
            <pre class="extract-content">{{ formatJSON(props.abstractStructure.data?.content) }}</pre>
          </el-tab-pane>
        </template>
        
        <!-- 编辑状态下显示 -->
        <template v-else>
          <el-tab-pane label="背景">
            <el-input 
              v-model="editData.background" 
              type="textarea" 
              :rows="6" 
              placeholder="请输入背景信息"
              class="edit-textarea"
            ></el-input>
          </el-tab-pane>
          <el-tab-pane label="方法">
            <el-input 
              v-model="editData.methods" 
              type="textarea" 
              :rows="6" 
              placeholder="请输入方法信息"
              class="edit-textarea"
            ></el-input>
          </el-tab-pane>
          <el-tab-pane label="结果">
            <el-input 
              v-model="editData.results" 
              type="textarea" 
              :rows="6" 
              placeholder="请输入结果信息"
              class="edit-textarea"
            ></el-input>
          </el-tab-pane>
          <el-tab-pane label="结论">
            <el-input 
              v-model="editData.conclusion" 
              type="textarea" 
              :rows="6" 
              placeholder="请输入结论信息"
              class="edit-textarea"
            ></el-input>
          </el-tab-pane>
        </template>
      </el-tabs>
      
      <!-- 添加编辑和提交按钮 -->
      <div class="actions-container">
        <template v-if="!isEditing">
          <el-button type="primary" @click="enterEditMode">编辑结构</el-button>
          <el-button type="warning" @click="confirmReExtract">重新抽取</el-button>
        </template>
        <template v-else>
          <el-button type="success" @click="submitStructure">保存修改</el-button>
          <el-button @click="cancelEdit">取消编辑</el-button>
        </template>
      </div>
    </div>
    <div v-else-if="extracting" class="extracting-container">
      <div class="extracting-content">
        <el-progress type="circle" :percentage="100" status="warning" indeterminate />
        <div class="extracting-text">
          <h3>正在进行摘要抽取...</h3>
          <p>系统正在使用大语言模型处理论文摘要，请耐心等待</p>
          <p class="small-text">抽取过程可能需要10-30秒</p>
        </div>
      </div>
    </div>
    <div v-else class="no-extract">
      <el-empty description="暂无抽取信息">
        <div class="extract-options">
          <div v-if="modelList.length > 0" class="model-select">
            <p>选择使用的模型：</p>
            <el-select v-model="selectedModelId" placeholder="选择模型" style="width: 100%;">
              <el-option
                v-for="model in modelList"
                :key="model.id"
                :label="model.name"
                :value="model.id"
              >
                <div class="model-option">
                  <span>{{ model.name }}</span>
                  <span class="model-desc">{{ model.description }}</span>
                </div>
              </el-option>
            </el-select>
          </div>
          <el-button type="primary" @click="startExtract" class="extract-button">开始抽取</el-button>
        </div>
      </el-empty>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.abstract-structure {
  margin-bottom: 20px;
}

.extract-meta {
  margin-bottom: 20px;
  background: linear-gradient(145deg, #f9fbff, #f0f7ff);
  padding: 16px 20px;
  border-radius: 10px;
  border-left: 4px solid #409EFF;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
  }
  
  p {
    margin: 8px 0;
    color: #2c3e50;
    font-size: 14px;
    display: flex;
    align-items: center;
    line-height: 1.6;
    
    strong {
      color: #409EFF;
      margin-right: 10px;
      font-weight: 600;
      min-width: 80px;
      position: relative;
      
      &:after {
        content: ":";
        position: absolute;
        right: 0;
        color: #909399;
      }
    }
  }
}

.extract-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.8;
  color: #2c3e50;
  padding: 20px;
  background: linear-gradient(145deg, #f9fbff, #f5f7fd);
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  margin-bottom: 4px;
  font-size: 14px;
  letter-spacing: 0.2px;
  border-left: 3px solid rgba(64, 158, 255, 0.5);
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    transform: translateY(-2px);
  }
  
  &:empty::before {
    color: #909399;
    font-style: italic;
    opacity: 0.7;
  }
  
  &:before {
    position: absolute;
    top: -15px;
    left: 16px;
    font-size: 60px;
    color: rgba(64, 158, 255, 0.08);
    font-family: serif;
  }
}

.edit-textarea {
  width: 100%;
  margin-bottom: 10px;
  
  :deep(.el-textarea__inner) {
    background: linear-gradient(145deg, #f9fbff, #f5f7fd);
    border: 1px solid rgba(64, 158, 255, 0.3);
    border-radius: 8px;
    padding: 15px;
    font-size: 14px;
    line-height: 1.8;
    color: #2c3e50;
    transition: all 0.3s;
    
    &:focus {
      border-color: #409EFF;
      box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
    }
  }
}

.actions-container {
  margin-top: 20px;
  text-align: right;
  
  .el-button {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 10px rgba(64, 158, 255, 0.2);
    margin-left: 12px;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 12px rgba(64, 158, 255, 0.25);
    }
    
    &.el-button--warning {
      box-shadow: 0 4px 10px rgba(230, 162, 60, 0.2);
      
      &:hover {
        box-shadow: 0 6px 12px rgba(230, 162, 60, 0.25);
      }
    }
    
    &.el-button--success {
      box-shadow: 0 4px 10px rgba(103, 194, 58, 0.2);
      
      &:hover {
        box-shadow: 0 6px 12px rgba(103, 194, 58, 0.25);
      }
    }
  }
}

pre.extract-content {
  font-family: "Monaco", "Menlo", "Consolas", monospace;
  background: linear-gradient(145deg, #f5f7fa, #f0f3f9);
  padding: 20px;
  border-radius: 10px;
  font-size: 13px;
  overflow-x: auto;
  line-height: 1.6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  border-left: 3px solid #7c64ff;
  
  &:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    transform: translateY(-2px);
  }
  
  &:before {
    position: absolute;
    top: -15px;
    left: 16px;
    font-size: 36px;
    color: rgba(124, 100, 255, 0.1);
    font-family: Monaco, monospace;
  }
}

.no-extract {
  padding: 50px 0;
  text-align: center;
  
  .el-empty {
    padding: 30px;
    background: linear-gradient(145deg, #f9fbff, #f5f7fd);
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    
    &:before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #409EFF, #7c64ff);
      opacity: 0.5;
    }
    
    &:hover {
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
      transform: translateY(-3px);
      
      &:before {
          opacity: 1;
      }
      
      .el-button {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 6px 12px rgba(64, 158, 255, 0.25);
      }
    }
    
    .el-empty__image {
      filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.1));
    }
    
    .el-empty__description {
      margin-top: 20px;
      font-size: 14px;
      color: #606266;
    }
    
    .extract-options {
      margin-top: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 15px;
      width: 80%;
      max-width: 400px;
      margin-left: auto;
      margin-right: auto;
      
      .model-select {
        width: 100%;
        text-align: left;
        
        p {
          font-size: 14px;
          color: #606266;
          margin-bottom: 8px;
        }
      }
      
      .extract-button {
        width: 100%;
        padding: 12px 20px;
        font-weight: 500;
        background: linear-gradient(145deg, #409EFF, #3b97ff);
        border: none;
        border-radius: 8px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 10px rgba(64, 158, 255, 0.2);
        
        &:hover {
          background: linear-gradient(145deg, #4aa3ff, #409EFF);
          box-shadow: 0 6px 12px rgba(64, 158, 255, 0.25);
          transform: translateY(-2px);
        }
      }
    }
  }
}

.model-option {
  display: flex;
  flex-direction: column;
  
  .model-desc {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}

.extracting-container {
  padding: 50px 0;
  text-align: center;
  
  .extracting-content {
    padding: 40px;
    background: linear-gradient(145deg, #f9fbff, #f5f7fd);
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    
    &:before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #e6a23c, #f56c6c);
      animation: gradient-flow 3s ease infinite;
      background-size: 200% 200%;
    }
    
    .extracting-text {
      margin-top: 24px;
      
      h3 {
        margin: 0 0 12px;
        color: #e6a23c;
        font-size: 18px;
      }
      
      p {
        margin: 8px 0;
        color: #606266;
        font-size: 14px;
      }
      
      .small-text {
        font-size: 12px;
        color: #909399;
        font-style: italic;
        margin-top: 16px;
      }
    }
  }
}

@keyframes gradient-flow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

// 透明度过渡效果
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 