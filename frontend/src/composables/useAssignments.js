import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getAssignments } from '../api/assignment'

export function useAssignments(classList) {
    const route = useRoute()
    const router = useRouter()

    const assignments = ref([])
    const selectedId = ref(null)
    const currentStatus = ref('pending')
    const currentAssignment = ref(null) // 改成 ref

    async function fetchAssignments(status = 'pending') {
        try {
            const allHomework = []
            for (const cls of classList) {
                const res = await getAssignments(cls, 1, 10, 'created_at', 'asc', status)
                allHomework.push(...res.items)
            }

            assignments.value = allHomework

            const idInList = route.params.id && assignments.value.some(a => a.uuid === route.params.id)
            if (idInList) {
                selectAssignment(route.params.id)
            } else if (assignments.value.length > 0) {
                selectAssignment(assignments.value[0].uuid)
            } else {
                selectedId.value = null
                currentAssignment.value = null
                router.replace({ name: 'AssignmentDetail', params: { id: null } })
            }
        } catch (e) {
            console.error('获取作业失败', e)
        }
    }

    function selectAssignment(uuid) {
        selectedId.value = uuid
        currentAssignment.value = assignments.value.find(a => a.uuid === uuid) || null
    }

    watch(() => route.params.id, (newId) => {
        if (newId) selectAssignment(newId)
    })

    return {
        assignments,
        selectedId,
        currentStatus,
        currentAssignment,
        fetchAssignments,
        selectAssignment, // 暴露出来
        router
    }
}
