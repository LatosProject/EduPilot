import "mdui/mdui.css";
import "mdui"; // 全量导入所有组件

import App from "./App.vue";
import Vue3Lottie from 'vue3-lottie';
import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";

const pinia = createPinia();
const app = createApp(App);

app.use(pinia);
app.use(router);
// 全局注册 Lottie 组件
app.use(Vue3Lottie, { name: "LottieAnimation" }); // 指定组件名为 <LottieAnimation />
app.mount("#app");
