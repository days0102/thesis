<script>
import { defineComponent, ref } from "vue";
import BarChart from "./BarChart.vue";

export default defineComponent({
  components: {
    BarChart,
  },
  props: {
    userData: null,
    appData: null,
    node: {},
    userColorScale: null,
    appColorScale: null,
  },
  setup(props) {
    console.log("BarChartContainer", props);
  },
});
</script>

<template>
  <div style="display: flex; flexdirection: row">
    <div style="flex: 1">
      <h3 class="h1Style">User Details</h3>
      <BarChart
        :data="userData"
        :node="node"
        height="100"
        :colorScale="userColorScale"
      />
    </div>

    <div style="flex: 1">
      <h3 class="h1Style">App Details</h3>
      <BarChart
        :data="userData"
        :node="node"
        height="100"
        :colorScale="appColorScale"
      />
    </div>
  </div>
</template>

<style scoped>
.h1Style {
  display: block;
  margin-top: 10px;
  color: #707070;
  text-align: center;
  font-size: 1em;
}
</style>
