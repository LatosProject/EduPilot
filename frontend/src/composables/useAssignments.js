import { getAssignment, getAssignments } from "../api/assignment";
import { isRef, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

export function useAssignments(classList) {
  // 核心：必须在 setup 同步执行阶段调用
  const route = useRoute();
  const router = useRouter();

  const assignments = ref([]);
  const selectedId = ref(null);
  const currentStatus = ref("pending");
  const currentAssignment = ref(null);

  const getClassListArray = () =>
    isRef(classList) ? classList.value : classList;

  /**
   * 选中并获取作业详情
   */
  async function selectAssignment(uuid) {
    if (!uuid || !assignments.value.length) return;
    selectedId.value = uuid;

    const fromList = assignments.value.find((a) => a.uuid === uuid);
    if (fromList && fromList.class_uuid) {
      try {
        const detail = await getAssignment(fromList.class_uuid, uuid);
        currentAssignment.value = { ...fromList, ...detail };
        return;
      } catch (e) {
        console.warn("获取详情失败，回退至列表数据", e);
      }
    }
    currentAssignment.value = fromList || null;
  }

  /**
   * 获取作业列表并同步路由
   */
  async function fetchAssignments(status = "pending") {
    const currentList = getClassListArray();
    if (!currentList || currentList.length === 0) {
      assignments.value = [];
      return;
    }

    // 安全检查：如果 route 没注入成功则终止，防止 params of undefined
    if (!route || !route.params) {
      console.error(
        "Vue Router 上下文未找到，请确保在 setup 顶层使用 useAssignments"
      );
      return;
    }

    try {
      const promises = currentList.map(async (cls) => {
        try {
          const res = await getAssignments(
            cls,
            1,
            10,
            "created_at",
            "asc",
            status
          );
          return (res?.items || []).map((item) => ({
            ...item,
            class_uuid: cls,
          }));
        } catch (err) {
          return [];
        }
      });

      const results = await Promise.all(promises);
      const allHomework = results.flat();
      assignments.value = allHomework;

      if (allHomework.length > 0) {
        // 使用 route.params 之前已经过了上面的安全检查
        const routeId = route.params.id;
        const target =
          allHomework.find((a) => a.uuid === routeId) || allHomework[0];

        selectAssignment(target.uuid);

        if (routeId !== target.uuid) {
          router
            .replace({
              name: "AssignmentDetail",
              params: { id: target.uuid },
              query: route.query,
            })
            .catch(() => {});
        }
      } else {
        selectedId.value = null;
        currentAssignment.value = null;
        if (route.params.id) {
          router
            .replace({ name: "AssignmentDetail", params: { id: "" } })
            .catch(() => {});
        }
      }
    } catch (e) {
      console.error("fetchAssignments 异常", e);
    }
  }

  // --- 响应式监听 ---

  // 1. 监听班级列表变化 (只保留这一个)
  watch(
    () => getClassListArray(),
    (newList) => {
      if (newList && newList.length > 0) {
        fetchAssignments(currentStatus.value);
      }
    },
    { immediate: true, deep: true }
  );

  // 2. 监听路由 ID 变化 (当用户点击左侧列表切换时触发)
  watch(
    () => route?.params?.id,
    (newId) => {
      if (newId && newId !== selectedId.value) {
        selectAssignment(newId);
      }
    }
  );

  return {
    assignments,
    selectedId,
    currentStatus,
    currentAssignment,
    fetchAssignments,
    selectAssignment,
  };
}
