// 格式化截止日期
export function formatDeadline(deadline) {
    if (!deadline) return '无截止日期'
    return new Date(deadline).toLocaleString()
}