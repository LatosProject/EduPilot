// composables/useAssignments.js
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAssignments } from '../api/assignment'

/**
 * 自定义组合式函数，管理作业相关状态和逻辑
 * @param {string} classUuid 课程唯一标识，用于请求作业列表
 * @returns 作业列表及相关状态、方法
 */
export function useAssignments(classUuid) {
    const route = useRoute()    // 获取当前路由对象，响应路由变化
    const router = useRouter()  // 获取路由实例，用于导航跳转
    const assignments = ref([]) // 存储作业列表，响应式数据
    const selectedId = ref(null) // 当前选中的作业 UUID
    const currentStatus = ref('') // 当前作业筛选状态，空字符串代表全部

    // 计算属性，获取当前选中的作业详情对象
    const currentAssignment = computed(() =>
        assignments.value.find(a => a.uuid === selectedId.value)
    )

    /**
     * 异步函数：根据筛选状态拉取作业列表
     * @param {string} status 筛选状态，默认为空，代表全部作业
     */
    async function fetchAssignments(status = '') {
        try {
            // 调用接口获取作业数据
            const res = await getAssignments(classUuid, 1, 10, 'created_at', 'asc', status)
            assignments.value = res.items  // 更新响应式作业列表

            // 路由中带有作业 id 时，优先设置为选中
            if (route.params.id) {
                selectedId.value = route.params.id
            }
            // 否则默认选中第一个作业（若列表非空，且未选中任何作业）
            else if (assignments.value.length > 0 && !selectedId.value) {
                selectedId.value = assignments.value[0].uuid
            }
        } catch (e) {
            console.error('获取任务失败', e)
        }
    }

    // 监听路由参数中的 id 变化，自动更新当前选中作业 id
    watch(() => route.params.id, (newId) => {
        if (newId) selectedId.value = newId
    })

    // 返回暴露给组件使用的响应式变量和方法
    return {
        assignments,       // 作业列表
        selectedId,        // 当前选中作业 id
        currentStatus,     // 当前筛选状态
        currentAssignment, // 当前选中作业的详细对象
        fetchAssignments,  // 拉取作业列表的方法
        router             // 路由实例，供组件使用
    }
}
