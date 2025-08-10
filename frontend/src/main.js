import "mdui/mdui.css";
import "mdui"; // 全量导入所有组件

import App from "./App.vue";
import { createApp } from "vue";
import router from "./router";
import { setColorScheme } from 'mdui/functions/setColorScheme.js';

createApp(App).use(router).mount("#app");



// 根据 #0061a4 生成一套配色方案，并将 <html> 设置为该配色方案
setColorScheme('#EEEE00');