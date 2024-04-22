<!--
 * @Author       : Outsider
 * @Date         : 2023-11-24 09:39:25
 * @LastEditors  : Outsider
 * @LastEditTime : 2024-04-22 11:54:53
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\App.vue
-->
<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <el-config-provider namespace="ep">
    <BaseHeader />
    <div class="flex main-container">
      <!-- <BaseSide /> -->
      <div w="full" py="4" style="overflow:auto">
        <!--        <Logos my="4" />-->
        <!--        <HelloWorld msg="Hello Vue 3 + Element Plus + Vite" />-->
        <RouterView />
      </div>
    </div>
  </el-config-provider>
</template>

<style>
#app {
  text-align: center;
  color: var(--ep-text-color-primary);
}
.main-container {
  height: calc(100vh - var(--ep-menu-item-height) - 5px);
}
</style>
