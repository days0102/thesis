<!--
 * @Author       : Outsider
 * @Date         : 2023-11-30 19:19:55
 * @LastEditors  : Outsider
 * @LastEditTime : 2024-03-13 17:42:58
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\views\HierarchyView.vue
-->
<template>
  <div
    id="tree-box"
    ref="divRef"
    style="margin: 3px; border: 1px solid black"
  >
    <svg ref="svgRef"></svg>
  </div>
</template>

<script>
import { onMounted, ref, toRaw, watch } from "vue";
import axios from "axios";
import { useWindowSize, useResizeObserver } from "@vueuse/core";

import {
  select,
  tree,
  stratify,
  scaleLinear,
  max,
  min,
  interpolateHcl,
} from "d3";

export default {
  name: "hierarchy",
  setup() {
    const divRef = ref(null);
    let nodes = ref([]);
    let wrapperRef = ref();
    let svgRef = ref(null);
    let nodeColor = "epsilon";
    let dimension = useWindowSize();
    let height = document.body.clientHeight*0.8;
    let dimensions = {
      width: ref(dimension.width.value),
      height: ref(dimension.height.value),
    };
    let nodesInUse = [];
    console.log(useWindowSize().width.value);

    const createNodeLookUpTable = (data) => {
      let table = {};
      for (let i in data) {
        const node_index = data[i].index;
        table[node_index] = data[i];
      }
      return table;
    };

    useResizeObserver(divRef, (entries) => {
      const entry = entries[0];
      const { width, height } = entry.contentRect;
      dimensions.width.value = width;
      dimensions.height.value = height;
    });

    onMounted(async () => {
      const response = await fetch("/api/hierarchy", {
        method: "GET",
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        headers: new Headers({
          "Content-Type": "application/json",
        }),
        redirect: "follow",
      });

      const data = await response.json();
      //   console.log(data.nodes);
      nodes.value = data.nodes;
    });

    // 监视nodes的变化
    watch(
      [nodes, dimensions.width, dimensions.height],
      (newValue, oldValue) => {
        // 当nodes更新时执行的代码
        // console.log("TreeChart-nodeColor");
        // Return if chart wrapper has no dimension
        // if (!dimensions) return;
        console.log(dimensions);

        // Do nothing while the data loads
        if (nodes.length < 1) return;
        console.log(nodes);

        let arrs = toRaw(nodes.value);
        console.log("arrs");
        console.log(arrs);
        if (arrs.length < 1) return;

        // Adjusting the container for cleaner visual
        select("#tree-box").style("padding", `20px 20px 20px 20px`);

        // Drawing canvas- set height
        const svg = select(svgRef.value).attr("height", height);

        // We will use this scale to level our nodes
        const yScale = scaleLinear()
          .domain([0, max(arrs.map((d) => d.y))])
          .range([0, height]);

        const xScale = scaleLinear()
          .domain([0, max(arrs.map((d) => d.x))])
          .range([0, dimensions.width.value]);
        // .range([0, dimensions.width - 45]);
        // console.log(yScale);
        // console.log(xScale);

        const colorScale = scaleLinear();
        if (arrs[0].averages.hasOwnProperty(nodeColor)) {
          colorScale.domain([
            min(arrs.map((d) => d.averages[nodeColor])),
            max(arrs.map((d) => d.averages[nodeColor])),
          ]);
        } else {
          colorScale.domain([
            min(arrs.map((d) => (nodeColor !== "epsilon" ? d.size : d.y))),
            max(arrs.map((d) => (nodeColor !== "epsilon" ? d.size : d.y))),
          ]);
        }
        colorScale.range(["blue", "red"]).interpolate(interpolateHcl);

        // Initialize a tree layout scaler
        const treeLayout = tree().size([dimensions.width, height]);
        // const treeLayout = tree().size([dimensions.width - 45, height]);

        // Let d3 transform the data in to a hierarchical form
        const root = stratify()
          .id((d) => d.index)
          .parentId((d) => d.parent)(arrs);

        // Let d3 compute the x and y cordinates of the nodes
        treeLayout(root);
        // console.log(root);

        // Draw tree node connections
        const node_table = createNodeLookUpTable(arrs); // Temp solution
        console.log("node_table");
        console.log(node_table);
        const pathGenerator = (node) => {
          let parent = node_table[node.data.parent];
          if (parent == null) return;

          // Cubic curve:
          //return `M${xScale(node.data.x)},${height - yScale(node.data.y)}
          //C ${xScale(parent.x)},${height - yScale(node.data.y)}
          //${xScale(parent.x)},${height - yScale(parent.y)}
          //${xScale(parent.x)},${height - yScale(parent.y)}
          //`;
          // console.log(node);
          // console.log(`M${xScale(node.data.x)},${height - yScale(node.data.y)}
          //     Q ${xScale(node.data.x)},${height - yScale(parent.y)}
          //       ${xScale(parent.x)},${height - yScale(parent.y)}
          //     `);
          // Quadratic curve, starting horizonally:
          return `M${xScale(node.data.x)},${height - yScale(node.data.y)}
            Q ${xScale(node.data.x)},${height - yScale(parent.y)}
              ${xScale(parent.x)},${height - yScale(parent.y)}
            `;

          // Piecewise linear curve, starting horizonally:
          //return `M${xScale(node.data.x)},${height - yScale(node.data.y)}
          //V ${height - yScale(parent.y)}
          //H ${xScale(parent.x)}
          //`;
        };

        svg
          .selectAll(".link")
          .data(root.descendants())
          .join("path")
          .attr("class", "link")
          .attr("d", (node) => pathGenerator(node))
          .style("stroke-width", function (d) {
            // Increase the weight of the link based on these break points
            if (d.data.size > 80000) {
              return 16;
            } else if (d.data.size > 70000) {
              return 11;
            } else if (d.data.size > 50000) {
              return 8;
            } else if (d.data.size > 10000) {
              return 6;
            } else {
              return 3;
            }
          });

        // Draw tree nodes
        svg
          .selectAll(".node")
          .data(root.descendants())
          .join("circle")
          .attr("class", (node) => {
            for (let e in nodesInUse) {
              if (nodesInUse[e].index === node.data.index) {
                return `node ${nodesInUse[e].name}`;
              } else {
                continue;
              }
            }
            return "node";
          })
          .attr("fill", (node) => {
            if (nodeColor !== "epsilon") {
              if (nodeColor !== "size") {
                if (arrs[0].averages.hasOwnProperty(nodeColor)) {
                  return colorScale(node.data.averages[nodeColor]);
                } else {
                  if (
                    node.data.users.includes(nodeColor) ||
                    node.data.apps.includes(nodeColor)
                  ) {
                    return "#900";
                  } else {
                    return "#ADA9B7";
                  }
                }
              } else {
                return colorScale(node.data.size);
              }
            } else {
              return colorScale(node.data.y);
            }
          })
          .attr(
            "r",
            (node) =>
              Math.log10(node.data.size) * 1.5 + Math.sqrt(node.data.size) / 30
          )
          .attr("cx", (node) => xScale(node.data.x))
          .attr("cy", (node) => height - yScale(node.data.y));

        // TODO - When the chart re-renders/resizes, we will update/style the this.nodes that are selected
        //   svg.select(".Alpha");
        //   svg.select(".Beta");
        //   svg.select(".Gamma");
        //   svg.select(".Delta");

        //   var defs = svg.selectAll(defs).data([""]).join("defs");

        //   var gradient = defs
        //     .append("linearGradient")
        //     .attr("id", "svgGradient")
        //     .attr("x1", "0%")
        //     .attr("x2", "0%")
        //     .attr("y1", "0%")
        //     .attr("y2", "100%");

        //   gradient
        //     .append("stop")
        //     .attr("class", "start")
        //     .attr("offset", "0%")
        //     .attr("stop-color", "red")
        //     .attr("stop-opacity", 1);

        //   gradient
        //     .append("stop")
        //     .attr("class", "end")
        //     .attr("offset", "100%")
        //     .attr("stop-color", "blue")
        //     .attr("stop-opacity", 1);
      }
    );
    // console.log(nodes);

    return { nodes, wrapperRef, svgRef, nodeColor, divRef };
  },
  computed: {},
  mounted() {},
};
</script>

<style scoped>
/* The CSS in this file are for the graph components */

/* DEFAULTS */
svg {
  overflow: visible !important;
  display: block;
  width: 100%;
}

svg circle {
  /* fill: #005073; */
  stroke: black;
  cursor: pointer;
}

svg circle:hover {
  fill: #1ebbd7;
}

svg text {
  pointer-events: none;
  font-size: 16px;
}

svg .tooltip {
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

svg .tooltipText {
  font-size: 18px;
  fill: white;
}
svg .tooltipText2 {
  font-size: 18px;
  fill: white;
}

svg .dot {
  fill: #005073;
  stroke: none;
}

/* SELECTED NODES */
.Alpha,
.Alpha-text {
  fill: red;
  /* transition: all 1s; */
  r: 20;
  stroke-width: 3;
}
.Beta,
.Beta-text {
  fill: blue;
  /* transition: all 1s; */
  r: 20;
  stroke-width: 3;
}
.Gamma,
.Gamma-text {
  fill: purple;
  /* transition: all 1s; */
  r: 20;
  stroke-width: 3;
}
.Delta,
.Delta-text {
  fill: green;
  /* transition: all 1s; */
  r: 20;
  stroke-width: 3;
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

#group-bar-chart .x-axis text {
  transform: rotate(-45deg) translate(-15px, 10px);
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
