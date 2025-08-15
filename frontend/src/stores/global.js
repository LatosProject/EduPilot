// stores/global.js

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGlobalStore = defineStore('global', () => {
    const homeBadge = ref(Number(localStorage.getItem('homeBadge') || 0))
    const classUuids = ref((localStorage.getItem('classUuids') || '').split(',').filter(Boolean))

    function setBadgeCount(count) {
        homeBadge.value = count
        localStorage.setItem('homeBadge', count)
    }

    function setClassUuids(uuids) {
        classUuids.value = uuids
        localStorage.setItem('classUuids', uuids)
    }


    return { homeBadge, classUuids, setBadgeCount, setClassUuids }
})
