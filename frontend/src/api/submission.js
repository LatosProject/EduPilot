import instance from '.'

/**
 * 上传单个文件，后端应返回 { filename, url } 或类似结构
 * @param {File} file
 */
export async function uploadFile(file) {
  const form = new FormData()
  form.append('file', file)

  // 假设后端会在该路由接收单文件并返回上传后的信息
  const res = await instance.post('/api/v1/files/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  // 期望返回 data.data 为 { filename, url }
  return res.data?.data || null
}

/**
 * 提交作业：先上传文件（如果有），再调用提交接口
 * @param {string} classUuid
 * @param {string} assignmentUuid
 * @param {string} content
 * @param {File[]|Object[]} attachments - File 对象数组或已上传的 {filename,url} 对象数组
 */
export async function submitAssignment(classUuid, assignmentUuid, content, attachments = []) {
  // attachments 可能是 File，也可能是 {filename, url}
  const uploaded = []

  for (const a of attachments || []) {
    if (!a) continue
    // 已有 url 的对象直接使用
    if (typeof a === 'object' && a.url) {
      uploaded.push({ filename: a.filename || a.name || '', url: a.url })
      continue
    }

    // 否则视为 File 并上传
    try {
      console.log('Uploading file:', a.name, 'size:', a.size, 'type:', a.type)
      const info = await uploadFile(a)
      if (info) uploaded.push(info)
    } catch (e) {
      // 如果上传某个文件失败，记录详细错误信息
      const errorDetail = e.response?.data?.detail || e.message || '未知错误'
      console.error('uploadFile failed:', errorDetail, e)
      throw new Error(`文件 "${a.name}" 上传失败: ${errorDetail}`)
    }
  }

  // 调用后端提交接口，按照后端期望格式发送 attachments（对象数组）
  const payload = {
    content: content || '',
    attachments: uploaded,
  }

  const url = `/api/v1/classes/${classUuid}/${assignmentUuid}/submissions`
  const res = await instance.post(url, payload)
  return res.data
}

export default {
  uploadFile,
  submitAssignment,
}
