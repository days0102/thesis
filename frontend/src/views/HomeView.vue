<!--
 * @Author       : Outsider
 * @Date         : 2023-11-24 09:39:25
 * @LastEditors  : Outsider
 * @LastEditTime : 2023-11-28 16:01:04
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\views\HomeView.vue
-->
<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "HomeView",
  //用户绑定的事件在methods中定义
  //methods中定义的方法this始终指向vue实列
  methods: {
    call() {
      fetch("/api", {
        method: "GET",
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        headers: new Headers({
          "Content-Type": "application/json",
        }),
        redirect: "follow",
      }) //.then()为异步方法，保证前面执行完后再开始，可以避免数据没有获取到
        .then((v) => {
          console.log(v);
          return v.json();
        })
        .then((v) => {
          console.log(v);
        });
    },
  },
});
</script>

<template>
  <main>Hello World</main>
  <el-button type="primary" @click="call">登录</el-button>
</template>
