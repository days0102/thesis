<!--
 * @Author       : Outsider
 * @Date         : 2023-11-30 19:19:55
 * @LastEditors  : Outsider
 * @LastEditTime : 2024-04-22 16:51:19
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\src\views\HierarchyView.vue
-->
<template>
  <div v-loading="loading" id="tree-box" ref="divRef" style="margin: 5px;">
    <svg ref="svgRef"></svg>
  </div>
  <!-- <el-button plain @click="dialogVisible = true">
    Click to open the Dialog
  </el-button>
  <el-dialog
    v-model="dialogVisible"
    title="Tips"
    width="500"
    :before-close="handleClose"
    draggable
  >
    <span>This is a message</span>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogVisible = false">
          Confirm
        </el-button>
      </div>
    </template>
  </el-dialog> -->
  <el-dialog v-for="(dialog, key) in dialogs" v-model="dialog.value" :key="dialog.key" title="Tips" width="600"
    :before-close="() => handleClose(key)" draggable center append-to="#tree-box" :destroy-on-close="true" :modal="false"
    :close-on-click-modal="false" modal-class="el-dialog__wrapper">
    <template #header>
      <div class="dialog-header" style="text-align: center; margin: 5px">
        <h3 style="margin-bottom: 12px">Node-{{ dialog.key }} Size-{{ dialog.size }} ε-{{ dialog.epsilon }}</h3>
      </div>
    </template>
    <!-- <span>This is a message</span> -->
    <DialogView :cid="dialog.cid"></DialogView>
    <template #footer>
      <div style="margin-top: 12px">
        <!-- <el-button type="warning" @click="innerVisible = true">详情</el-button> -->
        <el-button type="warning" @click="train(dialog.cid)">SHAP解释</el-button>
        <el-button type="primary" @click="() => handleClose(key)">
          关闭
        </el-button>
      </div>
    </template>
    <el-dialog v-model="innerVisible" :fullscreen="true" title="HiPlot" center append-to-body>
      <DetailView />
    </el-dialog>
  </el-dialog>
</template>

<script>
import { onMounted, ref, toRaw, watch } from "vue";
import { useWindowSize, useResizeObserver } from "@vueuse/core";
import DialogView from "./DialogView.vue";
import DetailView from "./DetailView.vue";

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
  components: {
    DialogView,
    DetailView,
  },
  setup() {
    const divRef = ref(null);
    let nodes = ref([]);
    let svgRef = ref(null);
    let nodeColor = "epsilon";
    let dimension = useWindowSize();
    let height = document.body.clientHeight * 0.8;
    let dimensions = {
      width: ref(dimension.width.value),
      height: ref(dimension.height.value),
    };
    let nodesInUse = [];

    const dialogs = ref([]);

    const loading = ref(true);

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
      console.log("hierarchy", width, height);
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

      loading.value = false;
    });

    // 监视nodes的变化
    watch(
      [nodes, dimensions.width, dimensions.height],
      (newValue, oldValue) => {
        // 当nodes更新时执行的代码
        // console.log("TreeChart-nodeColor");
        // Return if chart wrapper has no dimension
        // if (!dimensions) return;
        // console.log(dimensions);

        // Do nothing while the data loads
        if (nodes.length < 1) return;
        // console.log(nodes);

        let arrs = toRaw(nodes.value);
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
        // console.log("node_table");
        // console.log(node_table);
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
            // selected
            // for (let e in nodesInUse) {
            //   if (nodesInUse[e].index === node.data.index) {
            //     return `node ${nodesInUse[e].name}`;
            //   } else {
            //     continue;
            //   }
            // }
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
          .attr("cy", (node) => height - yScale(node.data.y))
          // event
          .on("click", function (event, node) {
            // console.log(event);
            // console.log(node);
            // dialogVisible.value = true;
            const keyExists = (key) => {
              // 判断键是否存在于 dialogs 数组中
              return dialogs.value.some((dialog) => dialog.key === key);
            };
            const itemFinds = (key) => {
              return dialogs.value.find((dialog) => dialog.key === key);
            };

            if (keyExists(node.data.index)) {
              // console.log(dialogs);
              // console.log("key find");
              // console.log(itemFinds(node.data.index));
              itemFinds(node.data.index).value = true;
            } else {
              dialogs.value.push({
                key: node.data.index,
                value: true,
                cid: node.id,
                size: node.data.size,
                epsilon: node.data.epsilon.toFixed(2)
              });
              // console.log(node)
              // console.log(dialogs)
            }
          })
          .on("mouseenter", function (event, node) {
            // 鼠标进入时将圆变大
            select(this)
              .transition()
              .duration(200)
              .attr("r", (node) =>
                (Math.log10(node.data.size) * 1.5 + Math.sqrt(node.data.size) / 30) + 10 // 增加半径
              );
          })
          .on("mouseleave", function () {
            select(this)
              .transition()
              .duration(200)
              .attr("r", (node) =>
                Math.log10(node.data.size) * 1.5 + Math.sqrt(node.data.size) / 30
              );
          });
        // .on("mouseenter", (event, node) => {
        //   svg
        //     .selectAll(".tooltip")
        //     .data([node])
        //     .join("circle")
        //     .attr("class", "tooltip")
        //     .attr("fill", (node) => colorScale(node.data.y))
        //     .attr("x", xScale(node.data.x) + 50)
        //     .attr("y", height - yScale(node.data.y) + 30)
        //     .attr("cx", xScale(node.data.x) + 50)
        //     .attr("cy", height - yScale(node.data.y) + 50)
        //     .attr("r", 60)
        //     .text(`Index: ${node.data.index}`)
        //     .attr("x", xScale(node.data.x) + 100)
        //     .attr("y", height - yScale(node.data.y));

        //   svg
        //     .append("text")
        //     .attr("class", "tooltipText")
        //     .text(`Size: ${node.data.size}`)
        //     .attr("x", xScale(node.data.x) + 22)
        //     .attr("y", height - yScale(node.data.y) + 40)
        //     .attr("dx", "-1.25em")
        //     .attr("dy", "0.32em");

        //   svg
        //     .append("text")
        //     .attr("class", "tooltipText2")
        //     .text(`Epsilon: ${node.data.epsilon.toFixed(2)}`)
        //     .attr("x", xScale(node.data.x) + 22)
        //     .attr("y", height - yScale(node.data.y) + 60)
        //     .attr("dx", "-1.25em")
        //     .attr("dy", "0.32em");
        // })
        // .on("mouseleave", () => {
        //   svg.select(".tooltip").remove();
        //   svg.select(".tooltipText").remove();
        //   svg.select(".tooltipText2").remove();
        // });

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
    // const handleClose = (done) => {
    //   ElMessageBox.confirm("Are you sure to close this dialog?")
    //     .then(() => {
    //       done();
    //     })
    //     .catch(() => {
    //       // catch error
    //     });
    // };
    const handleClose = (index) => {
      dialogs.value[index].value = false;
      // dialogs.value = dialogs.value.filter((item, idx) => idx !== index);
    };
    // const dialogVisible = ref(false);
    const innerVisible = ref(false);
    return {
      svgRef,
      divRef,
      handleClose,
      dialogs,
      innerVisible,
      loading,
      // dialogVisible,
    };
  },
  computed: {},
  mounted() { },
  methods: {
    train(cid) {
      this.$router.push({
        path: `/ml/${cid}`
      })
    },
  },
};
</script>

<style scoped>
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

svg :deep(.name) {
  font-size: 12px;
  fill: white;
}

svg :deep(.tooltipText) {
  font-size: 18px;
  fill: white;
}

svg :deep(.tooltipText2) {
  font-size: 18px;
  fill: white;
}

svg :deep(.dot) {
  fill: #005073;
  stroke: none;
}
</style>

<style lang="scss">
.el-dialog__wrapper {
  .ep-dialog__header {
    pointer-events: auto !important;
    padding: 5px;
  }

  .ep-dialog__body {
    pointer-events: auto !important;
    height: 45vh;
    overflow: auto;
    padding: 5px 25px;
  }

  .ep-dialog__footer {
    pointer-events: auto !important;
  }

  pointer-events: none !important;
}
</style>
