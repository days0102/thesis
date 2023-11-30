<!--
 * @Author       : Outsider
 * @Date         : 2023-11-24 10:01:52
 * @LastEditors  : Outsider
 * @LastEditTime : 2023-11-30 10:17:15
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\components\layout\BaseHeader.vue
-->
<script lang="ts" setup>
// @ts-ignore
import { toggleDark } from "~/composables";
</script>

<template>
  <el-menu class="el-menu-demo" mode="horizontal">
    <div class="box">
    <p class="logo">HPC I/O Analysis</p>
    </div>
    <el-menu-item index="1">
      <router-link to="/" style="text-decoration: none">
        Cluster Analysis
      </router-link>
    </el-menu-item>
    <el-sub-menu index="2">
      <template #title>Workspace</template>
      <el-menu-item index="2-1">item one</el-menu-item>
      <el-menu-item index="2-2">item two</el-menu-item>
      <el-menu-item index="2-3">item three</el-menu-item>
      <el-sub-menu index="2-4">
        <template #title>item four</template>
        <el-menu-item index="2-4-1">item one</el-menu-item>
        <el-menu-item index="2-4-2">item two</el-menu-item>
        <el-menu-item index="2-4-3">item three</el-menu-item>
      </el-sub-menu>
    </el-sub-menu>
    <!-- <el-menu-item index="3" disabled>Info</el-menu-item> -->
    <el-menu-item index="3">
      <router-link to="/analysis" style="text-decoration: none">
        Log Analysis
      </router-link>
    </el-menu-item>
    <el-menu-item index="4">
      
      <router-link to="/bank" style="text-decoration: none">
        Info
      </router-link>
    </el-menu-item>
    <el-menu-item h="full" @click="toggleDark()">
      <button
        class="border-none w-full bg-transparent cursor-pointer"
        style="height: var(--ep-menu-item-height)"
      >
        <i inline-flex i="dark:ep-moon ep-sunny" />
      </button>
    </el-menu-item>
  </el-menu>
</template>

<style lang="scss" scoped>
.logo{
  font: bolder;
  font-size: 1.6vw;
  text-align: center;
  font-family: "STXingkai";
  border: 2px;
}
.box{
  display:flex;
	align-items: center ;
  margin: 0 1vw;
}
</style>