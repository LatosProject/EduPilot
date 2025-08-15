import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getAssignments } from '../api/assignment'

export function useAssignments(classList) {
    const route = useRoute()
    const router = useRouter()
    const assignments = ref([])
    const selectedId = ref(null)
    const currentStatus = ref('pending')

    const currentAssignment = computed(() =>
        assignments.value.find(a => a.uuid === selectedId.value)
    )

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
                selectedId.value = route.params.id
            } else if (assignments.value.length > 0) {
                selectedId.value = assignments.value[0].uuid
                router.replace({ name: 'AssignmentDetail', params: { id: selectedId.value } })
            } else {
                selectedId.value = null
                router.replace({ name: 'AssignmentDetail', params: { id: null } })
            }
        } catch (e) {
            console.error('获取作业失败', e)
        }
    }

    watch(() => route.params.id, (newId) => {
        if (newId) selectedId.value = newId
    })

    return {
        assignments,
        selectedId,
        currentStatus,
        currentAssignment,
        fetchAssignments,
        router
    }
}
