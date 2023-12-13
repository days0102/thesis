<!--
 * @Author       : Outsider
 * @Date         : 2023-11-24 10:01:52
 * @LastEditors  : Outsider
 * @LastEditTime : 2023-12-09 20:10:25
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\components\layout\BaseHeader.vue
-->
<script lang="ts" setup>
// @ts-ignore
import { toggleDark } from "~/composables";
import { ref } from "vue";
import { ElMessageBox } from "element-plus";
import router from "../../router";

const drawer = ref(false);

function choose() {}

const direction = ref("ttb");

interface Tree {
  label: string;
  children?: Tree[];
}

const handleNodeClick = (data: Tree) => {
//   console.log(data.label);
  router.push({ name: 'analysis', query: { select: data.label }});
  drawer.value = false;
};

const data = ref([
  {
    label: "Level one 1",
    children: [
      {
        label: "Level two 1-1",
        children: [
          {
            label: "Level three 1-1-1",
          },
        ],
      },
    ],
  },
  {
    label: "Level one 2",
    children: [
      {
        label: "Level two 2-1",
        children: [
          {
            label: "Level three 2-1-1",
          },
        ],
      },
      {
        label: "Level two 2-2",
        children: [
          {
            label: "Level three 2-2-1",
          },
        ],
      },
    ],
  },
  {
    label: "Level one 3",
    children: [
      {
        label: "Level two 3-1",
        children: [
          {
            label: "Level three 3-1-1",
          },
        ],
      },
      {
        label: "Level two 3-2",
        children: [
          {
            label: "Level three 3-2-1",
          },
        ],
      },
    ],
  },
]);
const defaultProps = {
  children: "children",
  label: "label",
};

function open() {
  fetch("/api/getdirent", {
    method: "get",
    mode: "cors",
    cache: "no-cache",
    credentials: "same-origin",
    headers: new Headers({
      "Content-Type": "application/json",
    }),
    redirect: "follow",
  })
    .then((v) => {
      return v.json();
    })
    .then((v) => {
      // console.log(v);
      data.value = v;
    });
}
</script>

<template>
  <el-drawer
    v-model="drawer"
    title="Choose Darshan Log"
    :direction="direction"
    size="60%"
    @open="open"
  >
    <div class="view">
      <el-tree
        class="tree"
        :data="data"
        :props="defaultProps"
        @node-click="handleNodeClick"
      />
    </div>
  </el-drawer>
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
      <template #title>Log Analysis</template>
      <el-menu-item index="2-1" @click="drawer = true"
        >choose darshan</el-menu-item
      >
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
        Workspace
      </router-link>
    </el-menu-item>
    <el-menu-item index="4">
      <router-link to="/cluster" style="text-decoration: none">
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
.logo {
  font: bolder;
  font-size: 1.6vw;
  text-align: center;
  font-family: "STXingkai";
  border: 2px;
}
.box {
  display: flex;
  align-items: center;
  margin: 0 1vw;
}
.view {
  overflow: auto;
  height: 100%;
  text-align: center;
}
.tree {
  text-align: center;
  font-size: 1vw;
  margin: 1vw;
  padding-left: 2vw;
}

:deep(.ep-tree-node__expand-icon.ep-icon-caret-right:before) {
  color: #646a73;
  font-size: 15px;
}

:deep(.is-leaf.ep-tree-node__expand-icon.ep-icon-caret-right:before) {
  color: transparent;
}

.ep-tree-node__content > .ep-tree-node__expand-icon {
  padding: 9px 6px 6px 6px;
}

:deep(.ep-tree-node__content) {
  height: 5vh;
  font-size: 1.5vw;
}

:deep(.ep-tree-node__content:hover) {
  border-radius: 4px;
}
</style>
