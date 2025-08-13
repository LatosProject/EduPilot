// stores/global.js

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGlobalStore = defineStore('global', () => {
    const homeBadge = ref(Number(localStorage.getItem('homeBadge') || 0))
    const classUuid = ref(localStorage.getItem('classUuid') || '')

    function setBadgeCount(count) {
        homeBadge.value = count
        localStorage.setItem('homeBadge', count)
    }

    function setClassUuid(uuid) {
        classUuid.value = uuid
        localStorage.setItem('classUuid', uuid)
    }

    return { homeBadge, classUuid, setBadgeCount, setClassUuid }
})