import { createApp } from "vue";
import App from "./App.vue";
import "mdui/mdui.css";
import "mdui"; // 全量导入所有组件
import router from "./router";
createApp(App).use(router).mount("#app");
