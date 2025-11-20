<script setup>
import lineas from "@/assets/datos/lineas-vis.csv";
import _debounce from "lodash/debounce.js";

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
const tt_data = ref({});
const is_tooltip_active = ref(false);
const posX = ref(-200);
const posY = ref(-200);
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
    .attr("height", ancho.value);

  const empty_drawn = svg.value.select("g.g-contenedor-vis").empty()
  console.log("empty_drawn ", empty_drawn);
  // if (!already_drawn.empty()){
  //   already_drawn.remove();
  // }
  if (!empty_drawn){
    console.log("Mapa ya dibujado, no se dibuja de nuevo.");
    return;
  }
  console.log("Dibujando mapa de metroo...");
  svg.value
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
        `translate(${escala * d.x_position},${escala * d.y_position})`);
    // .attr("class", (d) => "estacion " + d.class);

  estaciones_g.value
    .append("circle")
    .attr("r", (d) =>
        d.total_stairs ? 2 + escala * Math.sqrt(d.total_stairs / 12) : 1.5)
    .style("stroke", (d) => d.total_stairs
        ? d.stairs_with_report
          ? 'none'
          : d.line_color
        : 'none'
    )
    .attr("fill", (d) => d.total_stairs ? d.line_color : 'black')
    .style("fill-opacity", (d) =>
        d.total_stairs ?
            d.stairs_with_report
                ? (d.stairs_working / d.total_stairs)
                : 0.1
            : 0.7
    );

  estaciones_g.value
    .append("circle")
    .attr("r",  2 + escala * 2)
    .style("stroke", 'none')
    .attr("fill", "#fff")
    .style("fill-opacity", 0);

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
      tt_data.value = {
        name: d.name,
        total_stairs: d.total_stairs,
        stairs_not_working: d.stairs_not_working || 0,
        stairs_working: d.stairs_working || 0,
      };
      // console.log("is_tooltip_active", is_tooltip_active.value);
      // is_tooltip_active.value = true;
      d3.select(this).select("text").style("fill-opacity", "1");
      d3.select(this).select("circle").style("stroke", "#fff");
    })
    .on("mouseout", function (e, d) {
      // console.log("mouseout", d);
      // console.log("event", e);
      tt_data.value = {};
      debounceCloseTooltip();
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

const debounceCloseTooltip = _debounce(() => {
  console.log("Intentando cerrar tooltip...");
  if (!tt_data.value.name && is_tooltip_active.value) {
    console.log("No hay datos en tooltip, cerrando.");
    tt_data.value = {};
    is_tooltip_active.value = false;
  }
  else {
    console.log("Hay datos en tooltip, no se cierra.");
    // debounceCloseTooltip.call()
  }

}, 2000)

</script>

<template>
  <v-card
    class="contenedor-svg"

  >
    <div
      v-if="false"
      class="tooltip"
      :class="{ activo: tooltipActivo }"
      ref="divTooltip"
    >
      <span class="text-subtitle-1">{{tt.name}}</span>
      <br/>
      <b>Total de escaleras:</b>
        {{tt.total_stairs}}
      <br/>
      <b>Inoperativa:</b>
      {{tt.stairs_not_working || 0}}
      <br/>
      <b>Sí funcionan:</b>
      {{tt.stairs_working || 0}}
      <br/>
      <b>Último reporte:</b>
      dd-mm-yyyy
      <br/>

    </div>

    <v-tooltip
      location="bottom"
      v-model="is_tooltip_active"
      target="cursor"
      open-on-click
      class="pa-0 mt-3"
      :open-on-hover="false"
    >
      <template v-slot:activator="{ props: activatorProps }">
        <svg
          id="mapa-metro"
          v-bind="activatorProps"
          @mouseout="debounceCloseTooltip()"
        ></svg>
      </template>
      <v-card
        class="py-3 ma-0"
        v-if="tt_data && tt_data.name"
      >
        <v-card-title xclass="text-h6">
          {{tt_data.name}}
        </v-card-title>
        <br/>
        <b>Total de escaleras:</b>
          {{tt_data.total_stairs}}
        <br/>
        <b>Inoperativa:</b>
        {{tt_data.stairs_not_working || 0}}
        <br/>
        <b>Sí funcionan:</b>
        {{tt_data.stairs_working || 0}}
        <br/>
        <b>Último reporte:</b>
        dd-mm-yyyy

        <br/>
      </v-card>
    </v-tooltip>
  </v-card>
</template>

<style lang="scss">
div.contenedor-svg {
  position: relative;
  //div.tooltip {
  //  opacity: 0;
  //  visibility: hidden;
  //  transition: opacity 0.2s ease, visibility 0.2s ease;
  //  position: absolute;
  //  border-radius: 8px;
  //  background: #c8c8c898;
  //  color: black;
  //  font-size: 14px;
  //  backdrop-filter: blur(5px);
  //  padding: 5px;
  //  width: 200px;
  //  height: auto;
  //  &.activo {
  //    opacity: 1;
  //    visibility: visible;
  //  }
  //}
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
