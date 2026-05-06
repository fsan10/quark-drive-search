<template>
  <div>
    <div class="box-card">
      <div class="section-header">CSV 批量导入</div>

      <el-alert type="info" :closable="false" show-icon class="mb-16" title="CSV 文件格式要求：第一行为表头，必须包含 title 和 link 列。可选列：link_type、extraction_code、description、file_size。文件编码支持 UTF-8 和 GBK，大小限制 10MB。" />

      <el-button @click="downloadTemplate" plain class="mb-16">
        <el-icon class="mr-1"><Download /></el-icon>
        下载CSV模板
      </el-button>

      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="1"
        accept=".csv,.CSV"
        :on-change="handleFileChange"
        :on-exceed="() => ElMessage.warning('只能上传一个文件')"
        class="mb-16"
      >
        <el-icon class="el-icon--upload" :size="48" color="#c0c4cc"><UploadFilled /></el-icon>
        <div class="el-upload__text">将 CSV 文件拖到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">仅支持 .csv 文件</div>
        </template>
      </el-upload>

      <el-button type="primary" :loading="importing" :disabled="!selectedFile" @click="handleImport">
        <el-icon class="mr-1"><Upload /></el-icon>
        开始导入
      </el-button>

      <div v-if="importResult" class="mt-16">
        <el-result
          :icon="importResult.success_count > 0 ? 'success' : 'error'"
          :title="`成功导入 ${importResult.success_count} 条`"
          :sub-title="importResult.fail_count > 0 ? `失败 ${importResult.fail_count} 条` : ''"
        >
          <template #extra>
            <div v-if="importResult.errors && importResult.errors.length" class="text-left max-w-md mx-auto">
              <el-collapse>
                <el-collapse-item :title="`错误详情 (${importResult.errors.length})`">
                  <div v-for="(err, i) in importResult.errors" :key="i" class="text-xs text-red-500 mb-1">{{ err }}</div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Download, UploadFilled, Upload } from '@element-plus/icons-vue'
import { importCsv } from '../api'
import { ElMessage } from 'element-plus'

const uploadRef = ref(null)
const selectedFile = ref(null)
const importing = ref(false)
const importResult = ref(null)

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleImport = async () => {
  if (!selectedFile.value) return
  importing.value = true
  importResult.value = null
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  try {
    const res = await importCsv(formData)
    importResult.value = res.data
    if (res.data.success_count > 0) {
      ElMessage.success(`成功导入 ${res.data.success_count} 条`)
    }
  } catch {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

const downloadTemplate = () => {
  const csv = 'title,link,link_type,extraction_code,description,file_size\n示例视频,https://pan.quark.cn/s/example,quark,,这是一个示例,1GB\n'
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'import_template.csv'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.box-card {
  background: #fff;
  padding: 20px;
  box-shadow: 4px 4px 40px rgba(0, 0, 0, 0.05);
}

.section-header {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.mb-16 {
  margin-bottom: 16px;
}

.mt-16 {
  margin-top: 16px;
}

.text-left {
  text-align: left;
}

.max-w-md {
  max-width: 28rem;
  margin-left: auto;
  margin-right: auto;
}
</style>
