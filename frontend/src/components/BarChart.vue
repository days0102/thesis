<!--
 * @Author       : Outsider
 * @Date         : 2024-03-16 09:06:49
 * @LastEditors  : Outsider
 * @LastEditTime : 2024-03-19 21:02:45
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\components\BarChart.vue
-->
<script lang="js">
import { watch, ref, defineComponent } from "vue";

import { useWindowSize, useResizeObserver } from "@vueuse/core";

import {
  select,
  scaleLinear,
  scaleBand,
  axisLeft,
  axisBottom,
  max,
  scaleOrdinal,
  schemeSet1,
} from "d3";

export default defineComponent({
  props: {
    data: null,
    colorScale: null,
  },
  setup(props) {
    console.log("barchart", props.data);
    const data = props.data;
    const colorScale = props.colorScale;
    console.log("BarChart", props);

    const divRef = ref(null);

    const svgRef = ref(null);
    const wrapperRef = ref();
    let dimension = useWindowSize();
    let height = 100;
    let dimensions = {
      width: ref(dimension.width.value),
      height: ref(dimension.height.value),
    };
    useResizeObserver(divRef, (entries) => {
      const entry = entries[0];
      const { width, height } = entry.contentRect;
      dimensions.width.value = width;
      dimensions.height.value = height;
      // console.log(width, height);
    });

    watch([dimensions.width, dimensions.height], (newValue, oldValue) => {
      // Return if no data is available
      // select("#dialog-box").selectAll("*").remove();
      // select(svgRef.value).selectAll("*").remove();
      console.log(data);
      if (data.length < 1) return;

      // shotening names that are too large from the node
      // shortenName(data);

      // Adjusting the container to fit the svg
      // let leftPadding = max(data.map((d) => calcWidthOfName(d.key)));
      let leftPadding = 60;
      select(divRef.value).style("padding", `0 20px 30px ${leftPadding}px`);

      // Main drawing canvas
      // console.log("svgRef", svgRef.value);
      const svg = select(svgRef.value).attr("height", height);

      // Define our scales
      const xScale = scaleLinear()
        .domain([0, max(data.map((d) => d.value))])
        .range([0, dimensions.width.value]);

      const yScale = scaleBand()
        .domain(data.map((d) => d.key))
        .range([0, height])
        .padding(0.1);

      // Define and draw our axis
      const xAxis = axisBottom(xScale).ticks(2);
      // svg
      //   .join(".x-axis")
      //   .style("transform", `translateY(${height}px)`)
      //   .call(xAxis);
      svg
        .select(".x-axis")
        .style("transform", `translateY(${height}px)`)
        .call(xAxis);

      const yAxis = axisLeft(yScale);
      // svg.join(".y-axis").call(yAxis);

      svg.select(".y-axis").call(yAxis);

      // Draw the rect to their proper position
      svg
        .selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", (d) => xScale(0))
        .attr("y", (d) => yScale(d.key))
        .attr("width", (d) => xScale(d.value))
        .attr("height", yScale.bandwidth())
        .attr("fill", (d) => {
          if (colorScale != null) {
            if (d.key === "other") {
              return "#DEDEDE";
            } else {
              console.log(colorScale(d.key));
              return colorScale(d.key);
            }
          }
        })
        .on("mouseenter", (event, d) => {
          svg
            .selectAll(".tooltip")
            .data([d])
            .join("text")
            .attr("class", "tooltip")
            .attr("x", xScale(d.value) / 2)
            .attr("y", yScale(d.key) + yScale.bandwidth() / 2)
            .text(d.value)
            .attr("text-anchor", "middle")
            .transition()
            .attr("opacity", 1);
        })
        .on("mouseleave", () => svg.select(".tooltip").remove())
        .transition();
    });
    return { divRef, svgRef };
  },
});
</script>

<template>
  <div ref="divRef">
    <svg ref="svgRef">
      <g class="x-axis"></g>
      <g class="y-axis"></g>
    </svg>
  </div>
</template>

<style scoped>
svg {
  overflow: visible !important;
  display: block;
  width: 100%;
}
svg :deep(text) {
  pointer-events: none;
  font-size: 15px;
}

svg :deep(.tooltip) {
  display: block;
  font-weight: bold;
  opacity: 1 !important;
}
</style>
