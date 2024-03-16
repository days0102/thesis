<script>
import { defineComponent } from "vue";

export default defineComponent({
  setup() {},
});
</script>

<template>
  <div style="display: flex; flexdirection: row">
    <div style="flex: 1">
      <h3 class="h1Style">User Details</h3>
      <BarChart
        data="{userData}"
        height="{100}"
        colorScale="{userColorScale}"
      />
    </div>

    <div style="flex: 1">
      <h3 class="h1Style">App Details</h3>
      <BarChart data="{appData}" height="{100}" colorScale="{appColorScale}" />
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
