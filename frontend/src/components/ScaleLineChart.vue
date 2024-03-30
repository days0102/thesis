<script>
import { defineComponent, ref, watch } from "vue";
import { useWindowSize, useResizeObserver } from "@vueuse/core";
import * as d3 from "d3";
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
    height: 200,
  },
  setup(props) {
    const data = props.data;
    // console.log("data", props.data);
    // console.log("coclor", props.colorScale);
    const colorScale = props.colorScale;

    let dimension = useWindowSize();
    let height = props.height;
    let comDimensions = {
      width: ref(dimension.width.value),
      height: ref(dimension.height.value),
    };

    const colorBy = "user";
    let box = ref(null);
    let wrapperRef = ref(null);
    let canvasRef = ref(null);

    useResizeObserver(wrapperRef, (entries) => {
      const entry = entries[0];
      const { width, height } = entry.contentRect;
      comDimensions.width.value = width;
      comDimensions.height.value = height;
      // console.log("scaleLine", width, height);
    });

    watch(
      [comDimensions.width, comDimensions.height, () => props.data],
      (newValue, oldValue) => {
        select(box.value).selectAll("*").remove();
        // box.clear()
        // Return if chart wrapper has no dimension
        if (!comDimensions) return;
        // console.log("slchart-watch");

        let width = comDimensions.width.value;
        let margin = { top: 10, left: 80, right: 20, bottom: 70 };
        let innerWidth = width - margin.left - margin.right;
        let innerHeight = height - margin.top - margin.bottom;
        let devicePixelRatio = window.devicePixelRatio || 1;

        var types = {
          Number: {
            key: "Number",
            coerce: function (d) {
              return +d;
            },
            extent: d3.extent,
            within: function (d, extent, dim) {
              return (
                extent[0] <= dim.scale(d) && dim.scale(d) <= extent[1]
                // d3.scaleLinear().range([0, innerHeight])
              );
            },
            defaultScale: d3.scaleLinear().range([innerHeight, 0]),
          },
        };
        // console.log("types", types);

        const renderQueue = function (func) {
          var _queue = [], // data to be rendered
            _rate = 1000, // number of calls per frame
            _invalidate = function () {}, // invalidate last render queue
            _clear = function () {}; // clearing function

          var rq = function (data) {
            if (data) rq.data(data);
            _invalidate();
            _clear();
            rq.render();
          };

          rq.render = function () {
            var valid = true;
            _invalidate = rq.invalidate = function () {
              valid = false;
            };

            function doFrame() {
              if (!valid) return true;
              var chunk = _queue.splice(0, _rate);
              chunk.map(func);
              timer_frame(doFrame);
            }

            doFrame();
          };

          rq.data = function (data) {
            _invalidate();
            _queue = data.slice(0); // creates a copy of the data
            return rq;
          };

          rq.add = function (data) {
            _queue = _queue.concat(data);
          };

          rq.rate = function (value) {
            if (!arguments.length) return _rate;
            _rate = value;
            return rq;
          };

          rq.remaining = function () {
            return _queue.length;
          };

          // clear the canvas
          rq.clear = function (func) {
            if (!arguments.length) {
              _clear();
              return rq;
            }
            _clear = func;
            return rq;
          };

          rq.invalidate = _invalidate;

          var timer_frame =
            window.requestAnimationFrame ||
            window.webkitRequestAnimationFrame ||
            window.mozRequestAnimationFrame ||
            window.oRequestAnimationFrame ||
            window.msRequestAnimationFrame ||
            function (callback) {
              setTimeout(callback, 1);
            };

          return rq;
        };

        var dimensions = [
          {
            key: "Read ratio (by access)",
            type: types["Number"],
            scale: d3.scaleLinear().range([innerHeight, 0]),
          },
          {
            key: "Read-only files (by file #)",
            type: types["Number"],
            scale: d3.scaleLinear().range([innerHeight, 0]),
          },
          {
            key: "Read-write files (by file #)",
            type: types["Number"],
            scale: d3.scaleLinear().range([innerHeight, 0]),
          },
          {
            key: "Write-only files (by file #)",
            type: types["Number"],
            scale: d3.scaleLinear().range([innerHeight, 0]),
          },
          {
            key: "Unique files (by file #)",
            type: types["Number"],
            scale: d3.scaleLinear().range([innerHeight, 0]),
          },
        ];

        var xscale = d3
          .scalePoint()
          .domain(d3.range(dimensions.length))
          .range([0, innerWidth]);

        // console.log(xscale)
        // console.log(innerWidth)
        // console.log('sc',xscale(1));

        var yAxis = d3.axisLeft().tickFormat(d3.format("1.0%")).ticks(4);

        function make_y_gridlines() {
          return d3
            .axisLeft(dimensions[0].scale)
            .tickValues([0, 0.25, 0.5, 0.75, 1]);
        }

        const wrapper = d3
          .select(wrapperRef.value)
          .style("width", width + "px")
          .style("height", height + "px")
          .attr("class", "parcoords");

        var svg = d3
          .select(box.value)
          .style("width", width + "px")
          .style("height", height + "px")
          .append("g")
          .attr(
            "transform",
            "translate(" + margin.left + "," + margin.top + ")"
          );

        var canvas = d3
          .select(canvasRef.value)
          .attr("width", innerWidth * devicePixelRatio)
          .attr("height", innerHeight * devicePixelRatio)
          .style("width", innerWidth + "px")
          .style("height", innerHeight + "px")
          .style("margin-top", margin.top + "px")
          .style("margin-left", margin.left + "px");

        var ctx = canvas.node().getContext("2d");
        ctx.globalCompositeOperation = "darken";
        ctx.globalAlpha = 0.15;
        ctx.lineWidth = 1.5;
        ctx.scale(devicePixelRatio, devicePixelRatio);
        ctx.clearRect(0, 0, width, height);

        var axes = svg
          .selectAll(".axis")
          .data(dimensions)
          .enter()
          .append("g")
          .attr("class", function (d) {
            return "axis " + d.key.replace(/ /g, "_");
          })
          .attr("transform", function (d, i) {
            return "translate(" + xscale(i) + ")";
          });

        data.forEach(function (d) {
          dimensions.forEach(function (p) {
            d[p.key] = !d[p.key] ? null : p.type.coerce(Number(d[p.key]));
          });
        });

        // add the X gridlines
        // svg.append("g")
        // 	.attr("class", "grid")
        // 	.attr("transform", "translate(0," + innerHeight + ")")
        // 	.call(make_x_gridlines().tickSize(-innerHeight).tickFormat(""));

        // add the Y gridlines
        svg
          .append("g")
          .attr("class", "axis grid")
          .call(make_y_gridlines().tickSize(-innerWidth).tickFormat(""));

        // type/dimension default setting happens here
        dimensions.forEach(function (dim) {
          if (!("domain" in dim)) {
            // detect domain using dimension type's extent function
            // dim.domain = d3_functor(dim.type.extent)(
            // 	data.map(function (d) {
            // 		return d[dim.key];
            // 	})
            // );
            dim.domain = [0, 1];
          }
          if (!("scale" in dim)) {
            // use type's default scale for dimension
            dim.scale = dim.type.defaultScale.copy();
          }
          dim.scale.domain(dim.domain);
        });

        var render = renderQueue(draw).rate(200);

        ctx.clearRect(0, 0, width, height);
        ctx.globalAlpha = d3.min([0.85 / Math.pow(data.length, 0.3), 1]);
        render(data);

        axes
          .append("g")
          .each(function (d, i) {
            // console.log("d i", d, i);
            // debugger;
            var renderAxis = yAxis
              .scale(d.scale)
              .tickValues([0, 0.25, 0.5, 0.75, 1]);
            if (i != 0) {
              d3.select(this).attr("class", "hide-axis").call(renderAxis);
            }
            d3.select(this).call(renderAxis);
          })
          .append("text")
          .attr("class", "title")
          .attr("x", function (d) {
            yAxis.scale(d.scale);
          })
          .attr("y", innerHeight)
          .html(function (d) {
            let word = d.key.split("(");
            if (word.length < 2) {
              let word = d.key.split("[");
              return `<tspan>${word[0]}</tspan>
				<tspan x="0" dx="0" dy="10">[${word[1]}</tspan>`;
            } else {
              return `<tspan>${word[0]}</tspan>
					<tspan x="0" dx="0" dy="10">(${word[1]}</tspan>`;
            }
            // return "description" in d ? d.description : d.key;
          });
        // console.log(axes);

        // Add and store a brush for each axis.
        axes
          .append("g")
          .attr("class", "brush")
          .each(function (d) {
            d3.select(this).call(
              (d.brush = d3
                .brushY()
                .extent([
                  [-10, 0],
                  [10, innerHeight],
                ])
                .on("start", brushstart)
                .on("brush", brush)
                .on("end", brush))
                // .on("start brush end", () => {
                //   if (d3.event.selection) {
                //     const indexSelection = d3.event.selection.map(
                //       d.scale.invert
                //     );
                //     // console.log(indexSelection);
                //   }
                // })) // added )
            );
          })
          .selectAll("rect")
          .attr("x", -8)
          .attr("width", 16);

        function project(d) {
          return dimensions.map(function (p, i) {
            // check if data element has property and contains a value
            // I am remocing this check because of the null values in the data
            // For some reason, javascript is converting 0 to null in the object
            // if (!(p.key in d) || d[p.key] === null) return ;
            return [xscale(i), p.scale(Number(d[p.key]))];
          });
        }

        function draw(d) {
          // console.log('d',d)
          ctx.strokeStyle = colorScale.domain().includes(d[colorBy])
            ? colorScale(d[colorBy])
            : "#DEDEDE";
          // console.log("strokestyle",ctx.strokeStyle)
          // console.log("d-color",d[colorBy])
          // console.log("d",d)
          ctx.beginPath();
          var coords = project(d);
          coords.forEach(function (p, i) {
            // this tricky bit avoids rendering null values as 0
            if (p === null) {
              // this bit renders horizontal lines on the previous/next
              // dimensions, so that sandwiched null values are visible
              if (i > 0) {
                var prev = coords[i - 1];
                if (prev !== null) {
                  ctx.moveTo(prev[0], prev[1]);
                  ctx.lineTo(prev[0] + 6, prev[1]);
                }
              }
              if (i < coords.length - 1) {
                var next = coords[i + 1];
                if (next !== null) {
                  ctx.moveTo(next[0] - 6, next[1]);
                }
              }
              return;
            }

            if (i === 0) {
              ctx.moveTo(p[0], p[1]);
              return;
            }

            ctx.lineTo(p[0], p[1]);
          });
          ctx.stroke();
        }

        function brushstart(event) {
          event.sourceEvent.stopPropagation();
        }

        // Handles a brush event, toggling the display of foreground lines.
        function brush() {
          render.invalidate();

          var actives = [];
          svg
            .selectAll(".axis .brush")
            .filter(function (d) {
              return d3.brushSelection(this);
            })
            .each(function (d) {
              actives.push({
                dimension: d,
                extent: d3.brushSelection(this),
              });
            });

          var selected = data.filter(function (d) {
            if (
              actives.every(function (active) {
                var dim = active.dimension;
                // console.log(d);
                // test if point is within extents for each active brush
                return dim.type.within(Number(d[dim.key]), active.extent, dim);
              })
            ) {
              return true;
            }
          });

          ctx.clearRect(0, 0, width, height);
          ctx.globalAlpha = d3.min([0.85 / Math.pow(selected.length, 0.3), 1]);
          render(selected);
        }

        function d3_functor(v) {
          return typeof v === "function"
            ? v
            : function () {
                return v;
              };
        }
      }
    );
    return { wrapperRef, box, canvasRef };
  },
});
</script>

<template>
  <div ref="wrapperRef">
    <svg ref="box"></svg>
    <canvas ref="canvasRef"></canvas>
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

<style>
/* hide axes except main axis */
.hide-axis .tick text,
.hide-axis .tick {
  opacity: 0;
}

.axis .title {
  font-size: 10px;
  transform: rotate(-45deg) translate(-85px, -25px);
  fill: #222;
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

.parcoords {
  display: block;
  position: relative;
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
/* 
.axis line,
.axis path {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
} */

.axis text {
  text-shadow:
    0 1px 0 #fff,
    1px 0 0 #fff,
    0 -1px 0 #fff,
    -1px 0 0 #fff;
  cursor: move;
}
</style>
