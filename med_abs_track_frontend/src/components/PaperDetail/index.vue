<template>
  <div class="paper-details-container">
    <div class="paper-header">
      <h2 class="paper-title">{{ paper.title }}</h2>
      <div class="paper-journal" v-if="paper.journal || paper.journalName">
        <el-tag size="small" type="info" effect="plain">{{ paper.journal || paper.journalName }}</el-tag>
        <span class="publish-date" v-if="paper.publishedDate">{{ formatDate(paper.publishedDate) }}</span>
      </div>
    </div>
    
    <el-divider content-position="left">
      <div class="divider-content">
        <el-icon><Document /></el-icon>
        <span>基本信息</span>
      </div>
    </el-divider>
    
    <div class="paper-meta">
      <div class="meta-item">
        <div class="meta-label">
          <el-icon><Link /></el-icon>
          <span>PubMed ID</span>
        </div>
        <div class="meta-value">
          <el-link type="primary" :underline="false" v-if="paper.pmid" :href="`https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}`" target="_blank">
            {{ paper.pmid }}
            <el-icon><Position /></el-icon>
          </el-link>
          <span v-else>无</span>
        </div>
      </div>
      
      <div class="meta-item" v-if="paper.doi">
        <div class="meta-label">
          <el-icon><Link /></el-icon>
          <span>DOI</span>
        </div>
        <div class="meta-value">
          <el-link type="primary" :underline="false" :href="`https://doi.org/${paper.doi}`" target="_blank">
            {{ paper.doi }}
            <el-icon><Position /></el-icon>
          </el-link>
        </div>
      </div>
      
      <div class="meta-item">
        <div class="meta-label">
          <el-icon><Reading /></el-icon>
          <span>期刊</span>
        </div>
        <div class="meta-value">{{ paper.journal || paper.journalName || '无' }}</div>
      </div>
      
      <div class="meta-item" v-if="paper.publishStatus">
        <div class="meta-label">
          <el-icon><Notebook /></el-icon>
          <span>发表状态</span>
        </div>
        <div class="meta-value">
          <el-tag size="small" :type="getPublishStatusType(paper.publishStatus)">
            {{ paper.publishStatus }}
          </el-tag>
        </div>
      </div>
      
      <div class="meta-item">
        <div class="meta-label">
          <el-icon><Calendar /></el-icon>
          <span>发表日期</span>
        </div>
        <div class="meta-value">{{ formatDate(paper.publishedDate) || '无' }}</div>
      </div>
      
      <div class="meta-item" v-if="paper.createTime">
        <div class="meta-label">
          <el-icon><Timer /></el-icon>
          <span>创建时间</span>
        </div>
        <div class="meta-value">{{ formatDate(paper.createTime) || '无' }}</div>
      </div>
    </div>
    
    <el-divider content-position="left">
      <div class="divider-content">
        <el-icon><DocumentCopy /></el-icon>
        <span>摘要</span>
      </div>
    </el-divider>
    
    <div class="paper-section abstract-section">
      <!-- 结构化摘要 -->
      <div v-if="hasStructuredAbstract">
        <el-tabs type="border-card">
          <el-tab-pane label="背景">
            <div class="abstract-content">{{ paper.background || '无背景信息' }}</div>
          </el-tab-pane>
          <el-tab-pane label="方法">
            <div class="abstract-content">{{ paper.methods || '无方法信息' }}</div>
          </el-tab-pane>
          <el-tab-pane label="结果">
            <div class="abstract-content">{{ paper.results || '无结果信息' }}</div>
          </el-tab-pane>
          <el-tab-pane label="结论">
            <div class="abstract-content">{{ paper.conclusion || '无结论信息' }}</div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <!-- 非结构化摘要 -->
      <div v-else>
        <div class="abstract-content">{{ paper.abstract || '无摘要信息' }}</div>
      </div>
      
      <div class="abstract-actions" v-if="paper.abstract">
        <el-button size="small" type="primary" plain @click="handleCopy(paper.abstract)">
          <el-icon><CopyDocument /></el-icon>
          <span>复制摘要</span>
        </el-button>
      </div>
    </div>
    
    <el-divider content-position="left">
      <div class="divider-content">
        <el-icon><User /></el-icon>
        <span>作者</span>
      </div>
    </el-divider>
    
    <div class="paper-section" v-if="hasAuthors">
      <div class="authors-grid">
        <div class="author-item" v-for="(author, index) in getAuthors" :key="index">
          <el-card shadow="hover" class="author-card" :body-style="{ padding: '0' }">
            <div class="author-info">
              <div class="author-name">{{ author.name }}</div>
              <div class="author-affiliation" v-if="author.affiliation">{{ author.affiliation }}</div>
              <div class="author-order">
                <el-tag size="small" effect="plain" type="info">排序: {{ author.authorOrder || (index + 1) }}</el-tag>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
    <div v-else class="no-data-section">暂无作者信息</div>
    
    <el-divider content-position="left" v-if="hasKeywords">
      <div class="divider-content">
        <el-icon><Collection /></el-icon>
        <span>关键词</span>
      </div>
    </el-divider>
    
    <div class="paper-section" v-if="hasKeywords">
      <div class="keywords-container">
        <el-tag
          v-for="(keyword, index) in getKeywords"
          :key="index"
          class="keyword-tag"
          effect="light"
          round
          type="success"
        >
          <el-icon><PriceTag /></el-icon>
          <span>{{ keyword }}</span>
        </el-tag>
      </div>
    </div>
    
    <div class="paper-footer" v-if="paper.remark">
      <div class="remark-section">
        <el-divider content-position="left">
          <div class="divider-content">
            <el-icon><InfoFilled /></el-icon>
            <span>备注</span>
          </div>
        </el-divider>
        <div class="remark-content">{{ paper.remark }}</div>
      </div>
    </div>
    
    <slot name="footer"></slot>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { 
  Document, DocumentCopy, Link, Reading, Notebook, Calendar, Timer, 
  User, Collection, InfoFilled, Position, PriceTag, CopyDocument 
} from '@element-plus/icons-vue'
import { formatDate, copyText, getPublishStatusType } from '@/utils/paperUtils'

const proxy = inject('proxy')

// 定义组件属性
const props = defineProps({
  paper: {
    type: Object,
    required: true,
  }
})

// 判断是否有结构化摘要
const hasStructuredAbstract = computed(() => {
  return (
    props.paper.background ||
    props.paper.methods ||
    props.paper.results ||
    props.paper.conclusion
  )
})

// 判断是否有作者信息
const hasAuthors = computed(() => {
  return props.paper.authors && props.paper.authors.length > 0
})

// 获取格式化后的作者列表
const getAuthors = computed(() => {
  if (!props.paper.authors) return []
  return Array.isArray(props.paper.authors) ? props.paper.authors : []
})

// 判断是否有关键词
const hasKeywords = computed(() => {
  return props.paper.keywords && props.paper.keywords.length > 0
})

// 获取格式化后的关键词列表
const getKeywords = computed(() => {
  if (!props.paper.keywords) return []
  
  // 支持新的关键词数据结构
  if (Array.isArray(props.paper.keywords)) {
    // 如果是对象数组且含有term属性，说明是从API获取的新格式
    if (props.paper.keywords.length > 0 && typeof props.paper.keywords[0] === 'object' && 'term' in props.paper.keywords[0]) {
      return props.paper.keywords.map(k => k.term);
    }
    // 如果是对象数组且含有keyword属性，说明是从数据库获取的格式
    else if (props.paper.keywords.length > 0 && typeof props.paper.keywords[0] === 'object' && 'keyword' in props.paper.keywords[0]) {
      return props.paper.keywords.map(k => k.keyword);
    }
    // 如果是字符串数组，直接返回
    else {
      return props.paper.keywords;
    }
  }
  
  return [];
})

// 复制文本方法
const handleCopy = (text) => {
  copyText(text, proxy)
}
</script>

<style lang="scss" scoped>
.paper-details-container {
  width: 100%;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  position: relative;
  overflow: hidden;
  
  &:before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 6px;
    background: linear-gradient(90deg, #4a9bff, #7c64ff, #3bc1a8);
  }
  
  .paper-header {
    margin-bottom: 25px;
    
    .paper-title {
      font-size: 22px;
      font-weight: 700;
      color: #2c3e50;
      margin-bottom: 14px;
      line-height: 1.4;
      letter-spacing: -0.01em;
      padding-bottom: 10px;
      border-bottom: 2px solid rgba(64, 158, 255, 0.15);
      position: relative;
      
      &:after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 80px;
        height: 2px;
        background: linear-gradient(90deg, #409EFF, #7c64ff);
      }
    }
    
    .paper-journal {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .publish-date {
        color: #606266;
        font-size: 14px;
        font-weight: 500;
        position: relative;
        padding-left: 10px;
        
        &:before {
          content: '•';
          position: absolute;
          left: 0;
          color: #409EFF;
        }
      }
    }
  }
  
  .divider-content {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #409EFF;
    font-weight: 600;
    font-size: 15px;
    
    .el-icon {
      background-color: rgba(64, 158, 255, 0.12);
      padding: 5px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 5px rgba(64, 158, 255, 0.15);
    }
  }
  
  .paper-meta {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 12px;
    margin-bottom: 30px;
    
    .meta-item {
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      padding: 10px 14px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      background-color: #f7faff;
      border: 1px solid rgba(64, 158, 255, 0.08);
      
      &:hover {
        background-color: #f0f7ff;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(64, 158, 255, 0.1);
      }
      
      .meta-label {
        display: flex;
        align-items: center;
        font-size: 14px;
        color: #606266;
        font-weight: 600;
        width: 100px;
        flex-shrink: 0;
        
        .el-icon {
          margin-right: 8px;
          color: #409EFF;
          background-color: rgba(64, 158, 255, 0.12);
          padding: 5px;
          border-radius: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
      
      .meta-value {
        font-size: 14px;
        color: #2c3e50;
        word-break: break-word;
        line-height: 1.4;
        flex: 1;
        font-weight: 500;
      }
    }
  }
  
  .abstract-section {
    background: linear-gradient(145deg, #f9fbff, #f0f7ff);
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 28px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    border-left: 5px solid #409EFF;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:hover {
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.09);
      transform: translateY(-3px);
    }
    
    &:before {
      content: "";
      position: absolute;
      top: -20px;
      left: 16px;
      font-size: 80px;
      color: rgba(64, 158, 255, 0.08);
      font-family: serif;
    }
    
    .abstract-content {
      font-size: 15px;
      line-height: 1.8;
      color: #2c3e50;
      white-space: pre-wrap;
      letter-spacing: 0.2px;
      padding: 6px 0;
    }
    
    .abstract-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 20px;
      
      .el-button {
        border-radius: 8px;
        box-shadow: 0 3px 6px rgba(64, 158, 255, 0.15);
        transition: all 0.3s ease;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 10px rgba(64, 158, 255, 0.25);
        }
      }
    }
    
    :deep(.el-tabs--border-card) {
      border: none;
      background: transparent;
      box-shadow: none;
      
      .el-tabs__header {
        background: rgba(255, 255, 255, 0.7);
        border: none;
        border-radius: 8px;
        margin-bottom: 16px;
      }
      
      .el-tabs__nav {
        border: none;
      }
      
      .el-tabs__item {
        border: none;
        font-weight: 600;
        position: relative;
        
        &.is-active {
          color: #409EFF;
          background: rgba(64, 158, 255, 0.08);
          
          &:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 20px;
            height: 2px;
            background: #409EFF;
            border-radius: 2px;
          }
        }
      }
      
      .el-tabs__content {
        padding: 5px;
      }
    }
  }
  
  .authors-grid {
    margin-bottom: 20px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
    
    .author-card {
      height: 100%;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border-radius: 10px;
      overflow: hidden;
      border: none;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
      background: linear-gradient(145deg, #ffffff, #f8faff);
      padding: 16px;
      border-left: 4px solid #409EFF;
      position: relative;
      
      &:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.09);
        
        &:before {
          transform: scaleX(1);
        }
      }
      
      &:before {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #409EFF, #7c64ff);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      }
      
      .author-info {
        overflow: hidden;
        
        .author-name {
          font-size: 15px;
          font-weight: 700;
          color: #2c3e50;
          margin-bottom: 6px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          display: flex;
          align-items: center;
          
          &:before {
            content: "";
            display: inline-block;
            width: 10px;
            height: 10px;
            background: linear-gradient(135deg, #409EFF, #7c64ff);
            border-radius: 50%;
            margin-right: 8px;
          }
        }
        
        .author-affiliation {
          font-size: 13px;
          color: #606266;
          margin-bottom: 8px;
          line-height: 1.4;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          padding-left: 18px;
          position: relative;
          
          &:before {
            content: '📍';
            position: absolute;
            left: 0;
            font-size: 12px;
            opacity: 0.7;
          }
        }
        
        .author-order {
          padding-left: 18px;
          
          .el-tag {
            border-radius: 6px;
            background-color: rgba(144, 147, 153, 0.08);
            border: 1px solid rgba(144, 147, 153, 0.1);
            color: #606266;
            font-weight: 600;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
          }
        }
      }
    }
  }
  
  .keywords-container {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 24px;
    
    .keyword-tag {
      font-size: 13px;
      padding: 0 14px;
      height: 32px;
      line-height: 30px;
      transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
      border-radius: 16px;
      background-color: rgba(103, 194, 58, 0.08);
      border: 1px solid rgba(103, 194, 58, 0.2);
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
      
      .el-icon {
        margin-right: 5px;
        font-size: 12px;
        color: #67c23a;
      }
      
      &:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 6px 12px rgba(103, 194, 58, 0.15);
        background-color: rgba(103, 194, 58, 0.12);
      }
    }
  }
  
  .no-data-section {
    text-align: center;
    color: #909399;
    padding: 36px 0;
    font-size: 14px;
    background: linear-gradient(145deg, #fbfcff, #f5f7fc);
    border-radius: 12px;
    box-shadow: inset 0 1px 8px rgba(0, 0, 0, 0.04);
    position: relative;
    overflow: hidden;
    
    &:before, &:after {
      content: '';
      position: absolute;
      width: 200px;
      height: 200px;
      border-radius: 50%;
      background: rgba(64, 158, 255, 0.03);
      z-index: 0;
    }
    
    &:before {
      top: -100px;
      left: -100px;
    }
    
    &:after {
      bottom: -100px;
      right: -100px;
    }
  }
  
  .remark-section {
    margin-top: 28px;
    
    .remark-content {
      padding: 20px 24px;
      background: linear-gradient(145deg, #f9fff7, #f0f9eb);
      border-radius: 12px;
      color: #606266;
      line-height: 1.7;
      border-left: 4px solid #67c23a;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
      position: relative;
      
      &:before {
        content: '"';
        position: absolute;
        top: 5px;
        left: 14px;
        font-size: 40px;
        color: rgba(103, 194, 58, 0.15);
        font-family: serif;
      }
    }
  }
}

@media (max-width: 768px) {
  .paper-details-container {
    padding: 1.5rem;
    
    .paper-meta {
      grid-template-columns: 1fr;
    }
    
    .abstract-section {
      padding: 20px;
    }
  }
}
</style>