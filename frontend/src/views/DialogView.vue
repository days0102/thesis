<script>
import { defineComponent, onMounted, ref, watch } from "vue";
import BarChart from "../components/BarChart.vue";
import BarChartContainer from "../components/BarChartContainer.vue";
import ScaleLineChart from "../components/ScaleLineChart.vue";
import LogarithmicLineChart from "../components/LogarithmicLineChart.vue";
import RWChart from "../components/RWChart.vue";
import { select, scaleOrdinal, schemeSet1 } from "d3";

export default defineComponent({
  props: {
    cid: null,
  },
  components: {
    BarChart,
    BarChartContainer,
    ScaleLineChart,
    LogarithmicLineChart,
    RWChart,
  },
  setup(props) {
    // console.log("props", props.cid);

    const structAppAndUserData = (data) => {
      // Structure the user or app data to the specification of the BarChart
      // Our BarChart will have catagorical data on the left axis and linear data on the bottom axis
      let structData = [];
      for (let i in data) {
        structData.push({ key: i, value: data[i] });
      }
      structData.sort((a, b) => b.value - a.value);
      // console.log(structData);

      // Here we are limiting the user data to only 5 entries. The rest will be in a manual computed field named "other"
      let fixedData = [];
      if (structData.length > 5) {
        fixedData = structData.slice(0, 4); // Top 4 entries
        // console.log('fix', fixedData)
        // console.log('s', structData)
        let temp = structData.slice(4, structData.length);
        // console.log('temp',temp)
        let sum = temp.reduce(function (a, b) {
          return typeof a != "object" ? a + b.value : a.value + b.value;
        }, 0);
        temp = [];
        fixedData.push({ key: "other", value: sum }); // add the agregated "other" field to the data
        // console.log('push',fixedData)
      } else {
        fixedData = structData;
      }
      return fixedData;
    };

    const structParallelPerc = (data) => {
      let structData = [];
      for (let v in data) {
        structData.push({
          "Read ratio (by access)": data[v][0],
          "Read-only files (by file #)": data[v][1],
          "Read-write files (by file #)": data[v][2],
          "Write-only files (by file #)": data[v][3],
          "Unique files (by file #)": data[v][4],
          user: String(data[v][5]),
          app: data[v][7],
        });
      }
      return structData;
    };

    const structParallelLog = (data) => {
      let structData = [];
      // console.log(data)
      for (let v in data) {
        // console.log(data[v][0]===0)
        structData.push({
          "I/O throughput [MiB/s]": data[v][0],
          "I/O volume [GiB]": data[v][1] / 1024 ** 3,
          "Runtime [s]": data[v][2],
          "R/W accesses (in 1000s)": data[v][3],
          "App size (nprocs)": data[v][4],
          "Files (count)": data[v][5],
          user: String(data[v][6]),
          app: data[v][8],
        });
      }
      // console.log(structData)
      return structData;
    };

    const structAverageAccess = (reads, writes) => {
      let reads_avgs = [];
      for (let i = 0; i < 10; i++) {
        let sum = reads.reduce(function (prev, cur) {
          return prev + cur[i] * 100;
        }, 0);
        reads_avgs.push(sum / reads.length);
      }

      let writes_avgs = [];
      for (let i = 0; i < 10; i++) {
        let sum = writes.reduce(function (prev, cur) {
          return prev + cur[i] * 100;
        }, 0);
        writes_avgs.push(sum / writes.length);
      }

      return [
        {
          group: "0-100",
          reads: reads_avgs[0],
          writes: writes_avgs[0],
        },
        {
          group: "101-1k",
          reads: reads_avgs[1],
          writes: writes_avgs[1],
        },
        {
          group: "1k-10k",
          reads: reads_avgs[2],
          writes: writes_avgs[2],
        },
        {
          group: "10k-100k",
          reads: reads_avgs[3],
          writes: writes_avgs[3],
        },
        {
          group: "100k-1M",
          reads: reads_avgs[4],
          writes: writes_avgs[4],
        },
        {
          group: "1M-4M",
          reads: reads_avgs[5],
          writes: writes_avgs[5],
        },
        {
          group: "4M-10M",
          reads: reads_avgs[6],
          writes: writes_avgs[6],
        },
        {
          group: "10M-100M",
          reads: reads_avgs[7],
          writes: writes_avgs[7],
        },
        {
          group: "100M-1G",
          reads: reads_avgs[8],
          writes: writes_avgs[8],
        },
        {
          group: "1G+",
          reads: reads_avgs[9],
          writes: writes_avgs[9],
        },
      ];
    };

    let data = ref([]);
    let node = ref(null);
    let userColorScale = ref(null);
    let appColorScale = ref(null);

    let ready = ref(false);

    onMounted(async () => {
      // const response = await fetch(`/api/cluster/${props.cid}/users`, {
      //   method: "GET",
      //   mode: "cors",
      //   cache: "no-cache",
      //   credentials: "same-origin",
      //   headers: new Headers({
      //     "Content-Type": "application/json",
      //   }),
      //   redirect: "follow",
      // });

      // data.value = structAppAndUserData(await response.json());
      // // console.log(data);

      const urls = [
        `/api/cluster/${props.cid}/users`,
        `/api/cluster/${props.cid}/apps`,
        `/api/cluster/${props.cid}/percentage`,
        `/api/cluster/${props.cid}/logarithmic`,
        `/api/cluster/${props.cid}/reads`,
        `/api/cluster/${props.cid}/writes`,
      ];

      const requests = urls.map((url) => fetch(url));

      Promise.all(requests)
        .then((responses) => {
          return Promise.all(responses.map((response) => response.json()));
        })
        .then((data) => {
          const users = data[0];
          const apps = data[1];
          const pfeatures = data[2];
          const lfeatures = data[3];
          const reads = data[4];
          const writes = data[5];

          // console.log("users", users);
          // console.log("apps", apps);
          // console.log("pf", pfeatures);
          // console.log("lf", lfeatures);
          // console.log("rs", reads);
          // console.log("ws", writes);
          // console.log(lfeatures)

          let obj = {
            index: props.cid,
            users: structAppAndUserData(users),
            apps: structAppAndUserData(apps),
            pfeatures: structParallelPerc(pfeatures.data),
            lfeatures: structParallelLog(lfeatures.data),
            rw_access: structAverageAccess(reads,writes),
          };

          userColorScale.value = scaleOrdinal()
            .domain(
              obj.users.map((d) => {
                return d.key;
              })
            )
            .range(schemeSet1);
          // console.log(userColorScale);

          appColorScale.value = scaleOrdinal()
            .domain(
              obj.apps.map((d) => {
                return d.key;
              })
            )
            .range(schemeSet1);

          node.value = obj;

          // Lets create the color scale here so we can pass them to the dependent charts
          // This way, the colors are properly synchronized
          // const colors = ["E63946", "457B9D", "47A025", "C04ABC", "ADA9B7"]
          console.log("node", node.value);
          ready.value = true;
          // console.log("w", userColorScale.value("410575"));
        })
        .catch((error) => {
          console.error("Error fetching data:", error);
        });
    });

    const colorBy = "user";
    // console.log("uc", userColorScale);

    watch(userColorScale, (n, o) => {
      // console.log("w", userColorScale.value(410575));
    });

    return { data, node, userColorScale, appColorScale, colorBy, ready };
  },
});
</script>

<template>
  <div v-if="ready">
    <BarChartContainer
      :userData="node.users"
      :appData="node.apps"
      :node="node"
      :userColorScale="userColorScale"
      :appColorScale="appColorScale"
    ></BarChartContainer>
    <h1 class="h1Style">Percentage Features</h1>
    <ScaleLineChart
      :data="node.pfeatures"
      :colorScale="colorBy === 'user' ? userColorScale : appColorScale"
      :height="200"
    />
    <h1 class="h1Style">Logarithmic Features</h1>
    <LogarithmicLineChart
      :data="node.lfeatures"
      :height="200"
      :colorScale="colorBy === 'user' ? userColorScale : appColorScale"
    />
    <h1 class="h1Style">Read/Write Access</h1>
    <RWChart
      :data="node.rw_access"
      :height="100"
      :colorScale="colorBy === 'user' ? userColorScale : appColorScale"
    />
  </div>
  <div v-else>
    <el-skeleton :rows="5" animated />
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

