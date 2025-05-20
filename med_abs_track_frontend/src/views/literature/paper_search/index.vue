<template>
  <div class="app-container search-page">
    <!-- 搜索表单 -->
    <el-card>
      <template #header>
        <span>PubMed文献搜索</span>
      </template>
      <el-form
        ref="searchFormRef"
        :model="searchForm"
        :rules="rules"
        label-width="120px"
        @submit.prevent="handleSearch"
      >
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="搜索关键词" prop="query">
              <el-input
                v-model="searchForm.query"
                placeholder="请输入搜索关键词"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="排序方式" prop="sortBy">
              <el-select
                v-model="searchForm.sortBy"
                placeholder="请选择排序方式"
                style="width: 100%"
              >
                <el-option label="相关性" value="relevance" />
                <el-option label="发布日期" value="pub_date" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="发布日期" prop="dateRange">
              <el-date-picker
                v-model="searchForm.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY/MM/DD"
                value-format="YYYY/MM/DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="search-buttons">
          <el-button
            type="primary"
            @click="handleSearch"
            :loading="loading"
            :icon="Search"
            v-hasPermi="[permission.search]"
          >
            搜索
          </el-button>
          <el-button @click="resetForm" :icon="Refresh">重置</el-button>
        </div>
      </el-form>
    </el-card>

    <!-- 使用说明 -->
    <el-card v-if="!searchResults.length && !loading">
      <template #header>
        <span>文献检索使用说明</span>
      </template>
      <el-descriptions :column="1" border title="检索流程">
        <el-descriptions-item>
          <template #label>步骤1: 输入关键词</template>
          <el-tag size="small">在搜索框中输入您想要查找的医学文献关键词</el-tag>
        </el-descriptions-item>
        <el-descriptions-item>
          <template #label>步骤2: 设置过滤条件</template>
          <el-tag size="small">选择排序方式和发布日期范围来缩小搜索范围</el-tag>
        </el-descriptions-item>
        <el-descriptions-item>
          <template #label>步骤3: 浏览结果</template>
          <el-tag size="small">查看搜索结果，点击"预览"可查看详细信息</el-tag>
        </el-descriptions-item>
        <el-descriptions-item>
          <template #label>步骤4: 收藏文献</template>
          <el-tag size="small"
            >点击"收藏"按钮将文献保存到系统中，以便后续查阅和分析</el-tag
          >
        </el-descriptions-item>
      </el-descriptions>

      <el-descriptions :column="1" border title="数据来源" class="mt-20">
        <el-descriptions-item>
          <template #label>PubMed</template>
          <el-tag size="small"
            >美国国立医学图书馆的生物医学文献数据库，包含超过3000万篇文献引用</el-tag
          >
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 搜索结果 -->
    <el-card v-if="searchResults.length > 0 || loading" class="mt-20">
      <template #header>
        <span>搜索结果 (共 {{ total }} 条)</span>
      </template>

      <el-table
        v-loading="loading"
        :data="searchResults"
        border
        style="width: 100%"
        max-height="650"
      >
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column
          prop="title"
          label="标题"
          min-width="300"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <div>{{ row.title }}</div>
            <div class="paper-authors" v-if="row.authors && row.authors.length">
              <el-tag
                size="small"
                type="info"
                v-for="(author, index) in row.authors.slice(0, 3)"
                :key="index"
                class="mr-5 mt-5"
              >
                {{ author.name }}
              </el-tag>
              <span v-if="row.authors.length > 3"
                >等{{ row.authors.length }}人</span
              >
            </div>
            <div
              class="paper-keywords"
              v-if="row.keywords && row.keywords.length"
            >
              <el-tag
                size="small"
                type="success"
                v-for="(keyword, index) in row.keywords.slice(0, 3)"
                :key="index"
                class="mr-5 mt-5"
                effect="light"
              >
                {{ keyword.term }}
              </el-tag>
              <span v-if="row.keywords.length > 3" class="more-keywords">
                <el-tooltip
                  placement="top"
                  :content="
                    row.keywords
                      .slice(3)
                      .map((k) => k.term)
                      .join(', ')
                  "
                >
                  <span>+{{ row.keywords.length - 3 }}</span>
                </el-tooltip>
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="journal"
          label="期刊"
          min-width="150"
          show-overflow-tooltip
        />
        <el-table-column
          prop="publishedDate"
          label="发布日期"
          width="120"
          align="center"
        />
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <div class="operation-btns">
              <el-button
                type="primary"
                size="small"
                @click="handlePreview(row)"
                :icon="View"
                v-hasPermi="[permission.detail]"
              >
                预览
              </el-button>
              <el-button
                v-if="!row.isSaved"
                type="success"
                size="small"
                @click="handleCollect(row)"
                :loading="row.loading"
                :icon="Collection"
                v-hasPermi="['literature:paper:add']"
              >
                收藏
              </el-button>
              <el-button
                v-else
                type="info"
                size="small"
                disabled
                :icon="Select"
              >
                已收藏
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        class="mt-20"
        background
        :current-page="searchForm.pageNum"
        :page-sizes="[10, 20, 30, 50]"
        :page-size="searchForm.pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 预览对话框 - 使用统一组件 -->
    <el-dialog
      v-model="previewVisible"
      title="文献预览"
      width="850px"
      destroy-on-close
      class="paper-details-dialog"
      top="5vh"
    >
      <div v-loading="previewLoading">
        <paper-detail v-if="previewData.title" :paper="previewData">
          <template #footer>
            <!-- 这里可以添加特定于搜索页面的按钮或操作 -->
          </template>
        </paper-detail>
        <div v-else class="no-data-container">
          <el-empty description="暂无论文详情数据">
            <template #image>
              <el-icon :size="60"><DocumentDelete /></el-icon>
            </template>
          </el-empty>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="previewVisible = false">关闭</el-button>
          <el-button
            v-if="!previewData.isSaved"
            type="primary"
            @click="handleCollect(previewData)"
            :loading="previewData.loading"
            v-hasPermi="['literature:paper:add']"
          >
            <el-icon><Collection /></el-icon> 收藏
          </el-button>
          <el-button v-else type="success" disabled>
            <el-icon><Select /></el-icon> 已收藏
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="LiteratureSearch">
import { ref, reactive, inject } from 'vue'
import {
  Search,
  Refresh,
  Collection,
  View,
  Select,
  DocumentDelete,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  searchPubMedPapers,
  getPubMedPaperDetail,
} from '@/api/literature/paper_search'
import { addPaper } from '@/api/literature/paper'
import { addAuthor, addBatchAuthor } from '@/api/literature/author'
import { addJournal } from '@/api/literature/journal'
import { addKeyword, addBatchKeyword } from '@/api/literature/keyword'
import { copyText } from '@/utils/paperUtils'
import PaperDetail from '@/components/PaperDetail'

const proxy = inject('proxy')

// 权限设置
const permission = ref({
  search: 'literature:paper:search',
  detail: 'literature:paper:detail'
})

// 搜索表单
const searchFormRef = ref(null)
const searchForm = reactive({
  query: '',
  sortBy: 'relevance',
  dateRange: null,
  pageNum: 1,
  pageSize: 10,
})

// 表单验证规则
const rules = {
  query: [{ required: true, message: '请输入搜索关键词', trigger: 'blur' }],
}

// 搜索结果
const searchResults = ref([])
const total = ref(0)
const loading = ref(false)

// 预览对话框
const previewVisible = ref(false)
const previewLoading = ref(false)
const previewData = ref({})

// 搜索
const handleSearch = async () => {
  if (!searchForm.query.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  await searchFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true

      try {
        // 构建请求参数
        const params = {
          query: searchForm.query,
          page_num: searchForm.pageNum,
          page_size: searchForm.pageSize,
          sort_by: searchForm.sortBy,
        }

        // 添加日期范围参数
        if (searchForm.dateRange && searchForm.dateRange.length === 2) {
          params.min_date = searchForm.dateRange[0]
          params.max_date = searchForm.dateRange[1]
        }

        // 发送请求
        const res = await searchPubMedPapers(params)

        if (res.code === 0 || res.code === 200) {
          // 适配后端返回的数据结构
          searchResults.value = res.data?.rows || []
          total.value = res.data?.total || 0
          
          // 如果后端返回了分页信息，更新前端分页状态
          if (res.data?.pageNum !== undefined) {
            searchForm.pageNum = res.data.pageNum
          }
          if (res.data?.pageSize !== undefined) {
            searchForm.pageSize = res.data.pageSize
          }
        } else {
          ElMessage.error('搜索失败：' + (res.msg || '未知错误'))
        }
      } catch (error) {
        console.error('搜索出错', error)
        ElMessage.error('搜索请求失败：' + (error.message || '未知错误'))
      } finally {
        loading.value = false
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  searchFormRef.value.resetFields()
  searchResults.value = []
  total.value = 0
}

// 分页大小变化
const handleSizeChange = (size) => {
  searchForm.pageSize = size
  searchForm.pageNum = 1
  handleSearch()
}

// 页码变化
const handleCurrentChange = (page) => {
  searchForm.pageNum = page
  handleSearch()
}

// 预览论文
const handlePreview = async (row) => {
  previewVisible.value = true
  previewLoading.value = true
  previewData.value = { ...row }
  
  try {
    // 获取详细信息
    const res = await getPubMedPaperDetail(row.pmid)
    if (res.code === 0 || res.code === 200) {
      // 适配后端返回的数据结构
      previewData.value = { ...(res.data || {}), isSaved: row.isSaved }
    } else {
      ElMessage.warning('获取论文详情失败：' + (res.msg || '未知错误'))
    }
  } catch (error) {
    console.error('获取论文详情失败', error)
    ElMessage.error('获取论文详情请求失败：' + (error.message || '未知错误'))
  } finally {
    previewLoading.value = false
  }
}

// 收藏论文
const handleCollect = async (paper) => {
  // 防止重复点击
  if (paper.loading) return

  try {
    // 设置加载状态
    paper.loading = true

    // 检查论文是否已收藏 - 使用后端提供的信息，不需要再次请求
    if (paper.isSaved) {
      ElMessage.warning('该论文已收藏')
      return
    }

    // 统一计数器
    const stats = {
      author: { success: 0, fail: 0 },
      journal: { success: 0, fail: 0 },
      keyword: { success: 0, fail: 0 }
    }
    
    // 用于收集ID的数组
    const authorIds = []
    let journalId = null
    const keywordIds = []

    // 1. 批量保存作者信息
    if (paper.authors && paper.authors.length > 0) {
      try {
        const authorsList = paper.authors.map(author => ({
          name: author.name,
          remark: `PMID: ${paper.pmid}的作者`
        }))
        
        const res = await addBatchAuthor(authorsList)
        
        if (res.code === 0 || res.code === 200) {
          // 处理返回结果
          const data = res.data || []
          stats.author.success = data.filter(item => !item.error).length
          stats.author.fail = data.filter(item => item.error).length
          
          // 收集成功添加的作者ID
          data.forEach(item => {
            if (item.author_id) {
              authorIds.push(item.author_id)
            }
          })
        } else {
          ElMessage.warning('批量保存作者信息失败：' + (res.msg || '未知错误'))
          stats.author.fail = paper.authors.length
        }
      } catch (error) {
        console.warn('批量保存作者信息失败:', error)
        stats.author.fail = paper.authors.length
      }
    }

    // 2. 保存期刊信息
    if (paper.journal) {
      try {
        const res = await addJournal({
          journalName: paper.journal,
          issn: paper.issn || '',
          remark: `PMID: ${paper.pmid}的期刊`
        })
        stats.journal.success++
        // 捕获返回的ID
        if (res.code === 0 || res.code === 200) {
          journalId = res.data?.journal_id
        }
      } catch (error) {
        console.warn('保存期刊信息失败:', paper.journal, error)
        stats.journal.fail++
      }
    }

    // 3. 批量保存关键词信息
    if (paper.keywords && paper.keywords.length > 0) {
      try {
        const keywordsList = paper.keywords.map(keyword => ({
          keyword: typeof keyword === 'string' ? keyword : keyword.term,
          remark: `PMID: ${paper.pmid}的关键词`
        }))
        
        const res = await addBatchKeyword(keywordsList)
        
        if (res.code === 0 || res.code === 200) {
          // 处理返回结果
          const data = res.data || []
          stats.keyword.success = data.filter(item => !item.error).length
          stats.keyword.fail = data.filter(item => item.error).length
          
          // 收集成功添加的关键词ID
          data.forEach(item => {
            if (item.keyword_id) {
              keywordIds.push(item.keyword_id)
            }
          })
        } else {
          ElMessage.warning('批量保存关键词信息失败：' + (res.msg || '未知错误'))
          stats.keyword.fail = paper.keywords.length
        }
      } catch (error) {
        console.warn('批量保存关键词信息失败:', error)
        stats.keyword.fail = paper.keywords.length
      }
    }

    // 统一显示通知
    let successMsg = []
    if (stats.author.success > 0) {
      successMsg.push(`${stats.author.success}位作者信息`)
    }
    if (stats.journal.success > 0) {
      successMsg.push(`期刊信息`)
    }
    if (stats.keyword.success > 0) {
      successMsg.push(`${stats.keyword.success}个关键词`)
    }
    
    if (successMsg.length > 0) {
      ElMessage.success(`成功添加${successMsg.join('、')}`)
    }
    
    let failMsg = []
    if (stats.author.fail > 0) {
      failMsg.push(`${stats.author.fail}位作者信息`)
    }
    if (stats.journal.fail > 0) {
      failMsg.push(`期刊信息`)
    }
    if (stats.keyword.fail > 0) {
      failMsg.push(`${stats.keyword.fail}个关键词`)
    }
    
    if (failMsg.length > 0) {
      ElMessage.warning(`${failMsg.join('、')}添加失败`)
    }

    // 4. 准备保存文章数据
    const saveData = {
      pmid: paper.pmid,
      doi: paper.doi,
      title: paper.title,
      abstract: paper.abstract,
      publishedDate: paper.publishedDate,
      journal: paper.journal,
      // 添加从后端获取的ID
      authorIds: authorIds.filter(id => id !== undefined && id !== null),
      keywordIds: keywordIds.filter(id => id !== undefined && id !== null),
      journalId: journalId
    }

    // 5. 保存论文
    const saveRes = await addPaper(saveData)
    if (saveRes.code === 0 || saveRes.code === 200) {
      ElMessage.success('收藏成功')
      paper.isSaved = true

      // 更新预览数据
      if (previewData.value && previewData.value.pmid === paper.pmid) {
        previewData.value.isSaved = true
      }

      // 如果在搜索结果中，同步更新状态
      const index = searchResults.value.findIndex(
        (item) => item.pmid === paper.pmid
      )
      if (index !== -1) {
        searchResults.value[index].isSaved = true
      }
    } else {
      ElMessage.error('收藏失败：' + (saveRes.msg || '未知错误'))
    }
  } catch (error) {
    console.error('收藏出错', error)
    ElMessage.error('收藏请求失败：' + (error.message || '未知错误'))
  } finally {
    paper.loading = false
  }
}

// 复制文本的代理方法，调用工具函数
const handleCopyText = (text) => {
  copyText(text, proxy)
}
</script>

<style lang="scss" scoped>
.search-page {
  margin: var(--ba-main-space);

  :deep(.el-card) {
    margin-bottom: 15px;
  }
}

.mt-20 {
  margin-top: 20px;
}

.mt-10 {
  margin-top: 10px;
}

.mr-5 {
  margin-right: 5px;
}

.mb-5 {
  margin-bottom: 5px;
}

.mt-5 {
  margin-top: 5px;
}

.paper-abstract {
  white-space: pre-line;
  line-height: 1.6;
}

.paper-authors {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

.paper-keywords {
  margin-top: 5px;
  font-size: 12px;
  color: #606266;
}

.more-keywords {
  margin-left: 5px;
  font-size: 12px;
  color: #909399;
}

// 对话框样式
:deep(.paper-details-dialog) {
  .el-dialog__body {
    padding: 24px 28px;
    max-height: 70vh;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-thumb {
      background-color: #c0c4cc;
      border-radius: 10px;
    }

    &::-webkit-scrollbar-track {
      background-color: #f5f7fa;
    }
  }

  .el-dialog__footer {
    border-top: 1px solid #ebeef5;
    padding: 16px 24px;
    background-color: #f8f9fd;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.02);
    z-index: 10;
    position: relative;
    border-radius: 0 0 8px 8px;
  }
}

.no-data-container {
  padding: 40px 0;

  :deep(.el-empty__image) {
    display: flex;
    justify-content: center;
    align-items: center;

    .el-icon {
      color: #c0c4cc;
      filter: drop-shadow(0 2px 5px rgba(0, 0, 0, 0.1));
    }
  }
}

.dialog-footer {
  text-align: right;
  background: transparent;
  border-top: none;
  margin-top: 0;
  padding-top: 0;
}

.search-buttons {
  text-align: center;
  margin-top: 10px;
}

.operation-btns {
  text-align: center;
  margin-top: 10px;
}
</style>
