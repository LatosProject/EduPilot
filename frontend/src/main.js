import "mdui/mdui.css";
import "mdui"; // 全量导入所有组件

import App from "./App.vue";
import { createApp } from "vue";
import router from "./router";

createApp(App).use(router).mount("#app");

