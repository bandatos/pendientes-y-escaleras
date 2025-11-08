<script setup>
import estaciones from "@/assets/datos/estaciones-match-stops.csv";
import lineas from "@/assets/datos/lineas-vis.csv";

import * as d3 from "d3";
import { ref, onMounted, onUpdated, watch } from "vue";
import {useStationStore} from "@/stores/index.js";
const svg = ref(null);
const estaciones_g = ref(null);
const lineas_g = ref(null);
const tooltipActivo = ref(false);
const ancho = ref();
const divTooltip = ref();
let escala = 1;

const stationStore = useStationStore()
const mounted_map = ref(false);
// const { fullStations } = stationStore

onMounted(() => {
  console.log("Montando mapa de metro...");
  startMap();
});

onUpdated(() => {
  console.log("Actualizando mapa de metro...");
  startMap();
});

watch(
  () => stationStore.fullStations,
  (newVal) => {
    if (newVal.length > 0) {
      // console.log("mounted_map", mounted_map.value);
      if (mounted_map.value)
        loadMapaData();
    }
  },
  { immediate: true }
);

function startMap(){
  ancho.value = document.querySelector("div.contenedor-svg").clientWidth;
  escala = ancho.value / 120;
  svg.value = d3
    .select("svg#mapa-metro")
    .attr("width", ancho.value)
    .attr("height", ancho.value)
    .append("g")
    .attr("class", "g-contenedor-vis");
  lineas_g.value = svg.value
    .selectAll("line")
    .data(lineas)
    .enter()
    .append("line")
    .style("stroke-width", escala * 0.3)
    .attr("x1", (d) => escala * d.x1)
    .attr("y1", (d) => escala * d.y1)
    .attr("x2", (d) => escala * d.x2)
    .attr("y2", (d) => escala * d.y2)
    .attr("class", (d) => d.class);
  mounted_map.value = true;
  if (stationStore.fullStations.length > 0){
    loadMapaData();
  }
}

function loadMapaData() {
  estaciones_g.value = svg.value
    .selectAll("g.estacion")
    .data(stationStore.fullStations)
    .enter()
    .append("g")
    .style("cursor", "pointer")
    .attr("transform", (d) =>
        `translate(${escala * d.x_position},${escala * d.y_position})`)
    // .attr("class", (d) => "estacion " + d.class);
    .attr("fill", (d) => d.total_stairs ? d.line_color : 'black');
  estaciones_g.value
    .append("circle")
    // .attr("r", (d) => escala * (0.2 + Math.sqrt(1 * Math.random())))
    .attr("r", (d) =>
        d.total_stairs ? 2 + escala * Math.sqrt(d.total_stairs / 12) : 1.5)
    .style("stroke", (d) => d.total_stairs
        ? d.stairs_with_report
          ? 'none'
          : d.line_color
        : 'none'
    )
    .style("fill-opacity", (d) =>
        d.total_stairs ?
            d.stairs_with_report
                ? (d.stairs_working / d.total_stairs)
                : 0.1
            : 0.7
    );
        // d.total_stairs ? 0.2 + Math.random() : 0.7
  estaciones_g.value
    .append("text")
    .attr(
      "transform",
      (d) =>
        `translate(${escala * (d.x_name - d.x_position)} , ${
          escala * (d.y_name - d.y_position)
        }) rotate(${d.rotation || 0})`
    )
    .style("dominant-baseline", "middle")
    .style("font-size", `${escala * 1.2}px`)

    .attr("text-anchor", (d) => d.end_anchor ? 'end' : null)
    .text((d) => d.name)
    .style("fill", "#000")
    .style("fill-opacity", "0.5");
  estaciones_g.value
    .on("mouseover", function (e, d) {
      tooltipActivo.value = true;
      divTooltip.value.style.left = escala * +d.x_position - 100 + "px";
      divTooltip.value.style.top = escala * +d.y_position + 10 + "px";

      divTooltip.value.innerHTML = `
      <span class="text-subtitle-1">${d.name}</span>
      <br/>
      <b>Total de escaleras:</b>
      ${d.total_stairs}
      <br/>
      <b>Inoperativa:</b>
      ${d.stairs_not_working || 0}
      <br/>
      <b>Sí funcionan:</b>
      ${d.stairs_working || 0}
      <br/>
      <b>Último reporte:</b>
      dd-mm-yyyy
      <br/>
      `;

      d3.select(this).select("text").style("fill-opacity", "1");
      d3.select(this).select("circle").style("stroke", "#fff");
    })
    .on("mouseout", function (e, d) {
      tooltipActivo.value = false;

      console.log(e, d);
      d3.select(this).select("text").style("fill-opacity", "0.5");
      d3.select(this).select("circle").style("stroke", d =>
        d.total_stairs
          ? d.stairs_with_report
            ? 'none'
            : d.line_color
          : 'none'
      );
    });
}


</script>
<template>
  <div class="contenedor-svg">
    <div
      class="tooltip"
      :class="{ activo: tooltipActivo }"
      ref="divTooltip"
    ></div>
    <svg id="mapa-metro"></svg>
  </div>
</template>

<style lang="scss">
div.contenedor-svg {
  position: relative;
  div.tooltip {
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.2s ease, visibility 0.2s ease;
    position: absolute;
    border-radius: 8px;
    background: #c8c8c898;
    color: black;
    font-size: 14px;
    backdrop-filter: blur(5px);
    padding: 5px;
    width: 200px;
    height: auto;
    &.activo {
      opacity: 1;
      visibility: visible;
    }
  }
  svg#mapa-metro {
    line {
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    .c1 {
      stroke: #005fff;
    }
    .c2 {
      stroke: #ff9cce;
    }
    .c3 {
      stroke: #ff0800;
    }
    .c4 {
      stroke: #ff8300;
    }
    .c5 {
      stroke: #92535d;
    }
    .c6 {
      stroke: #fff0b5;
    }
    .c7 {
      stroke: #fff200;
    }
    .c8 {
      stroke: #00be00;
    }
    .c9 {
      stroke: #d6297d;
    }
    .c10 {
      stroke: #a4a5a7;
    }
    .c11 {
      stroke: #a0c965;
    }
    .c12 {
      stroke: #8ae5bf;
    }
    //.c13 {
    //  stroke: #ffb700;
    //}
    g {
      &.linea2 {
        circle {
          fill: #005fff;
        }
      }
      &.linea9 {
        circle {
          fill: #92535d;
        }
      }
      &.linea6 {
        circle {
          fill: #ff0800;
        }
      }
      &.linea7 {
        circle {
          fill: #ff8300;
        }
      }
      &.linea12 {
        circle {
          fill: #fff0b5;
        }
      }
      &.linea1 {
        circle {
          fill: #ff9cce;
        }
      }
      &.lineaB {
        circle {
          fill: #a4a5a7;
        }
      }
      &.linea5 {
        circle {
          fill: #fff200;
        }
      }
      &.linea3 {
        circle {
          fill: #a0c965;
        }
      }
      &.linea8 {
        circle {
          fill: #00be00;
        }
      }
      &.linea4 {
        circle {
          fill: #8ae5bf;
        }
      }
      &.lineaA {
        circle {
          fill: #d6297d;
        }
      }
    }
  }
}
</style>
