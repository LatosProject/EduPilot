// composables/useAssignments.js

import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getAssignments } from '../api/assignment'
import { useGlobalStore } from "/src/stores/global";

/**
 * 自定义组合式函数，管理作业相关状态和逻辑
 * @param {string} classUuid 课程唯一标识，用于请求作业列表
 * @returns 作业列表及相关状态、方法
 */
export function useAssignments(classUuid) {
    const globalStore = useGlobalStore();
    const route = useRoute()    // 获取当前路由对象，响应路由变化
    const router = useRouter()  // 获取路由实例，用于导航跳转
    const assignments = ref([]) // 存储作业列表，响应式数据
    const selectedId = ref(null) // 当前选中的作业 UUID
    const currentStatus = ref() // 当前作业筛选状态，空字符串代表全部

    // 计算属性，获取当前选中的作业详情对象
    const currentAssignment = computed(() =>
        assignments.value.find(a => a.uuid === selectedId.value)
    )

    async function fetchAssignments(status = 'pending') {
        try {
            const res = await getAssignments(classUuid, 1, 10, 'created_at', 'asc', status);
            assignments.value = res.items;

            const idInList = route.params.id && assignments.value.some(a => a.uuid === route.params.id);

            if (idInList) {
                // 路由里的id有效，使用它
                selectedId.value = route.params.id;
            } else if (assignments.value.length > 0) {
                // 路由里的id无效或不存在，默认选中第一个作业
                selectedId.value = assignments.value[0].uuid;
                // 同步路由参数，保证url和状态一致
                router.replace({ name: 'AssignmentDetail', params: { id: selectedId.value } });
            } else {
                // 列表为空，清空选中id
                selectedId.value = null;
                router.replace({ name: 'AssignmentDetail', params: { id: null } });
            }
        } catch (e) {
            console.error('获取任务失败', e);
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
