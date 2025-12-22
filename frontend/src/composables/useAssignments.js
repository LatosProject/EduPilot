import { getAssignment, getAssignments } from "../api/assignment";
import { ref, watch, unref } from "vue";
import { useRoute, useRouter } from "vue-router";

/**
 * 自定义组合函数：管理作业列表、选中状态和路由同步
 * @param {Array|Ref<Array>} classListOrRef 班级 UUID 列表（支持响应式引用）
 */
export function useAssignments(classListOrRef) {
  const route = useRoute(); // 获取当前路由信息
  const router = useRouter(); // 路由跳转工具

  // 所有作业列表
  const assignments = ref([]);

  // 当前选中作业 UUID
  const selectedId = ref(null);

  // 当前过滤状态（pending / done / expired）
  const currentStatus = ref("pending");

  // 当前选中的作业对象
  const currentAssignment = ref(null);

  /**
   * 获取作业列表
   * @param {String} status 过滤状态，默认 'pending'
   */
  async function fetchAssignments(status = "pending") {
    // 获取当前的班级列表（支持响应式引用）
    const classList = unref(classListOrRef);

    // 如果班级列表为空，不请求
    if (!classList || classList.length === 0) {
      assignments.value = [];
      selectedId.value = null;
      currentAssignment.value = null;
      return;
    }

    try {
      const allHomework = [];

      // 顺序获取每个班级作业
      for (const cls of classList) {
        const res = await getAssignments(
          cls,
          1,
          10,
          "created_at",
          "asc",
          status
        );
        // 为每个作业添加 class_uuid，便于后续提交时使用
        res.items.forEach((item) => {
          item.class_uuid = cls;
        });
        allHomework.push(...res.items);
      }

      assignments.value = allHomework;

      // 判断路由中 id 是否在作业列表中
      const idInList =
        route.params.id &&
        assignments.value.some((a) => a.uuid === route.params.id);

      if (idInList) {
        // 如果路由 id 存在，选中对应作业
        selectAssignment(route.params.id);
      } else if (assignments.value.length > 0) {
        // 否则默认选中第一个作业
        selectAssignment(assignments.value[0].uuid);
      } else {
        // 作业列表为空，清空选中状态并路由跳转到首页
        selectedId.value = null;
        currentAssignment.value = null;
        router.replace({ name: "Home" });
      }
    } catch (e) {
      console.error("获取作业失败", e);
    }
  }

  /**
   * 选中作业
   * @param {String} uuid 作业 UUID
   */
  async function selectAssignment(uuid) {
    selectedId.value = uuid;
    // 先从当前列表中找到 class_uuid（如果存在）
    const fromList = assignments.value.find((a) => a.uuid === uuid) || null;
    if (fromList && fromList.class_uuid) {
      try {
        const detail = await getAssignment(fromList.class_uuid, uuid);
        // 将返回的详情替换 currentAssignment，确保包含最新的 submitted 标识
        currentAssignment.value = { ...fromList, ...detail };
        return;
      } catch (e) {
        console.warn("获取作业详情失败，使用列表数据回退", e);
      }
    }

    // 回退到使用列表中的数据或 null
    currentAssignment.value = fromList || null;
  }

  // 监听路由 id 变化，保持选中作业同步
  watch(
    () => route.params.id,
    (newId) => {
      if (newId) selectAssignment(newId);
    }
  );

  return {
    assignments, // 作业列表
    selectedId, // 当前选中作业 UUID
    currentStatus, // 当前过滤状态
    currentAssignment, // 当前选中作业对象
    fetchAssignments, // 获取作业列表函数
    selectAssignment, // 选中作业函数
    router, // 路由实例
  };
}
