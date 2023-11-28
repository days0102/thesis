// import './assets/backup_main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// import "~/styles/element/index.scss";

// import ElementPlus from "element-plus";
// import all element css, uncommented next line
// import "element-plus/dist/index.css";
import "element-plus/theme-chalk/src/message.scss";
//
import "~/styles/index.scss";
import "uno.css";

const app = createApp(App)

app.use(router)
// app.use(ElementPlus)
app.mount('#app')
