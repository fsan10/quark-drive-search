<template>
  <div>
    <div class="box-card">
      <div class="section-header">打赏捐赠配置</div>
      <MdEditor v-model="content" :style="{ height: '500px' }" language="zh-CN" :onUploadImg="onUploadImg" />
      <div class="mt-16">
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDonation, updateDonation, uploadImage } from '../api'
import { ElMessage } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

const content = ref('')
const saving = ref(false)

onMounted(async () => {
  try {
    const res = await getDonation()
    content.value = res.data.content || ''
  } catch {}
})

const handleSave = async () => {
  saving.value = true
  try {
    await updateDonation({ content: content.value })
    ElMessage.success('保存成功')
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

const onUploadImg = async (files, callback) => {
  const urls = []
  for (const file of files) {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await uploadImage(formData)
      urls.push(res.data.url)
    } catch {
      ElMessage.error(`图片 ${file.name} 上传失败`)
    }
  }
  callback(urls)
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
.mt-16 {
  margin-top: 16px;
}
</style>
