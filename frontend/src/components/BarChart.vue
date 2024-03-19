<!--
 * @Author       : Outsider
 * @Date         : 2024-03-16 09:06:49
 * @LastEditors  : Outsider
 * @LastEditTime : 2024-03-19 14:41:44
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
    node: {},
    colorScale: null,
  },
  setup(props) {
    const data = props.data;
    const node = props.node;
    const colorScale = props.colorScale;
    console.log("BarChart", props);

    const divRef = ref(null);

    // const userColorScale = scaleOrdinal()
    //   .domain(
    //     node.users.map((d) => {
    //       return d.key;
    //     })
    //   )
    //   .range(schemeSet1);

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
      if (data.length < 1) return;

      // shotening names that are too large from the node
      // shortenName(data);

      // Adjusting the container to fit the svg
      // let leftPadding = max(data.map((d) => calcWidthOfName(d.key)));
      let leftPadding = 50;
      select("#dialog-box").style("padding", `0 20px 30px ${leftPadding}px`);

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
  <div id="dialog-box" ref="divRef">
    <svg ref="svgRef">
      <g class="x-axis"></g>
      <g class="y-axis"></g>
    </svg>
  </div>
</template>

<style scoped>
/* The CSS in this file are for the graph components */

/* DEFAULTS */
svg {
  overflow: visible !important;
  display: block;
  width: 100%;
}

svg text {
  pointer-events: none;
  font-size: 16px;
}

svg :deep(.tooltip) {
  display: block;
  font-weight: bold;
  opacity: 1 !important;
}

/* TREE COMPONENT STYLES*/
svg :deep(.link) {
  fill: none;
  stroke: gray;
}

svg /deep/ .name {
  font-size: 12px;
  fill: white;
}

/* Parallel Plot */
svg {
  font: 10px sans-serif;
}

.background path {
  fill: none;
  stroke: #ddd;
  shape-rendering: crispEdges;
}

.foreground path {
  fill: none;
  stroke: steelblue;
}

.brush .extent {
  fill-opacity: 0.3;
  stroke: #fff;
  shape-rendering: crispEdges;
}

.axis line,
.axis path {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.axis text {
  text-shadow:
    0 1px 0 #fff,
    1px 0 0 #fff,
    0 -1px 0 #fff,
    -1px 0 0 #fff;
  cursor: move;
}

/* GLOBALS */
ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

body {
  height: 100%;
  position: relative;
  overflow-y: scroll;
}

.row-fix {
  /* This will overwrite the margins bootstrap has on the row component*/
  margin: 0 !important;
  width: 100%;
}

#root {
  height: 100%;
}
/* App.js Styles */
.sidebar,
.main-content {
  padding: 0 !important;
}

.sidebar {
  background-color: #141414;
}

/* Navbar.js Styles */
#navbar {
  width: 100%;
  height: 75px;
  background-color: #141414;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 50px;
}

#headerLogo {
  height: 50px;
}

#viewMenu {
  height: 50px;
  color: rgb(106, 130, 255);
  z-index: 1001;
  display: flex;
  width: 75px;
  justify-content: space-around;
}

.grow {
  z-index: 10;
}
/* Sidemenu.js Styles */
#sidemenu {
  width: 100%;
  height: 100vh;
  background-color: #141414;
  color: #fff;
}

#sidemenu .side-menu-title {
  margin: 0;
  padding: 10px 0;
  display: block;
  width: 100%;
  text-align: center;
  text-transform: uppercase;
  font-size: 1.5em;
  letter-spacing: 4px;
  border-bottom: 1px solid #545454;
  font-weight: 400;
}

#sidemenu nav {
  margin: 0 20px;
}

#sidemenu ul li {
  font-size: 1em;
  height: 40px;
  margin-top: 5px;
  padding-left: 40px;
  cursor: pointer;
  line-height: 2.3;
  font-weight: 100;
  letter-spacing: 1px;
}

#sidemenu i {
  margin-right: 10px;
  line-height: 1.5;
  font-size: 1.2em;
}

#sidemenu ul li:hover {
  display: block;
  background-color: teal;
}

/* Dashboard.js Styles */
.title {
  margin: 0 20px;
  font-size: 1.5em;
  display: block;
  width: 100%;
  text-transform: uppercase;
  padding: 5px 10px;
  color: #a1a1a1;
  font-weight: 100;
  border-bottom: 1px solid#858585;
}

.chart-box {
  margin-top: 15px !important;
  flex-wrap: nowrap !important;
}
.dash-menu {
  padding: 0 !important;
  max-width: 60px !important;
  margin: 0 5px;
  float: left;
}
.dash-menu ul li {
  text-align: center;
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #141414;
  cursor: pointer;
}

/* .dash-menu ul {
	position: absolute;
} */

.dash-menu ul li i {
  font-size: 2em;
}

.tree-icon ul {
  margin-top: 10px;
}

/* DashColumn.js Styles */
.col-dash-head {
  background-color: #141414;
  width: 100%;
  height: 30px;
  color: #fff;
}

.col-dash-head i {
  line-height: 1.8;
  float: right;
  margin-right: 15px;
  cursor: pointer;
}

.col-title {
  color: 141414;
  font-size: 1.5em;
  margin-left: 15px;
  /* background-color: rgb(106, 130, 255); */
}

.form-row {
  /* overwrite bootstrap rules */
  margin: 0 !important;
  padding: 0 10px;
}

.form-check {
  /* overwrite bootstrap rules */
  padding-left: 2.5rem !important;
}

/* GraphGrid.js Styles */
.graph-grid {
  margin-bottom: 30px;
}

/* Material-UI Overwrite */
.MuiInputBase-root {
  display: block !important;
}

h3 {
  text-align: center;
}

.MuiAutocomplete-inputRoot[class*="MuiOutlinedInput-root"]
  .MuiAutocomplete-input:first-child {
  width: 100%;
}

.parcoords {
  display: block;
}

.parcoords svg,
.parcoords canvas {
  font: 10px sans-serif;
  position: absolute;
  display: block;
  width: 100%;
}

.parcoords canvas {
  opacity: 0.9;
  pointer-events: none;
}

.axis .title {
  font-size: 10px;
  transform: rotate(-45deg) translate(-85px, -25px);
  fill: #222;
}

#parChart2 .axis .title {
  transform: rotate(-45deg) translate(-70px, -20px) !important;
}

.axis line,
.axis path {
  stroke: #ccc;
  stroke-width: 1px;
}

.axis .tick text {
  fill: #222;
  pointer-events: none;
  z-index: 10000;
}

.axis.manufac_name .tick text,
.axis.food_group .tick text {
  opacity: 1;
}

.axis.active .title {
  font-weight: bold;
}

.axis.active .tick text {
  opacity: 1;
  font-weight: bold;
}

.brush .extent {
  fill-opacity: 0.3;
  stroke: #fff;
  stroke-width: 1px;
}

pre {
  width: 100%;
  height: 300px;
  margin: 6px 12px;
  tab-size: 40;
  font-size: 10px;
  overflow: auto;
}

/* hide axes except main axis */
.hide-axis .tick text,
.hide-axis .tick {
  opacity: 0;
}
</style>
