<script setup>

import { ref } from 'vue';

const props = defineProps({
  connectionPoints: {
    type: Object,
    required: true,
  },
});

const same_start_as_route = ref(false);
const same_end_as_route = ref(false);

</script>

<template>
  <v-card
    class="mb-4 px-2 py-3"
    variant="tonal"
    color="deep-purple"
  >
    <v-card-title
      class="text-subtitle-2 mb-2 d-block px-0 py-1 text-primary"
    >
      ¿Qué puntos comunica la escalera?
      <v-tooltip location="top">
        <template v-slot:activator="{ props }">
          <v-icon v-bind="props" size="small" class="ml-1">
            help_outline
          </v-icon>
        </template>
        Ejemplo: anden línea 7 dirección barranca
      </v-tooltip>
    </v-card-title>

    <div class="pb-2">
      <label class="text-body-2">
        <b>Origen:</b> Dónde comenzó el recorrido
      </label>
      <v-text-field
        v-model="connectionPoints.route_start"
        variant="outlined"
        density="comfortable"
        placeholder="Ej: Andén dirección barranca"
        hide-details
        prepend-inner-icon="trip_origin"
      ></v-text-field>
    </div>
    <v-expand-transition>
      <div v-if="!same_start_as_route" class="ml-4">
        <label class="text-body-2">
          <b>Inicio:</b> En qué punto inicia la escalera
        </label>
        <v-text-field
          v-model="connectionPoints.path_start"
          variant="outlined"
          density="comfortable"
          placeholder="Ej: Mezanine nivel 1"
          hide-details
          prepend-inner-icon="airline_stops"
        ></v-text-field>
      </div>
    </v-expand-transition>
    <div class="ml-4 mb-2">
      <v-checkbox
        v-model="same_start_as_route"
        label="El inicio es el mismo punto de Origen"
        color="deep-purple"
        hide-details
        density="compact"
      ></v-checkbox>
    </div>

    <div class="mt-6 pb-2">
      <label class="text-body-2 text-purple">
        <b>Final:</b> En qué punto termina la escalera
      </label>
      <v-text-field
        v-model="connectionPoints.path_end"
        variant="outlined"
        density="comfortable"
        placeholder="Ej: Torniquetes"
        hide-details
        color="purple"
        prepend-inner-icon="add_road"
        follow_the_signs
        class="text-purple"
      ></v-text-field>
    </div>

    <v-expand-transition>
      <div v-if="!same_end_as_route" class="ml-4">
        <label class="text-body-2 text-purple">
          <b>Destino:</b> Dónde termina el recorrido
        </label>
        <v-text-field
          v-model="connectionPoints.route_end"
          variant="outlined"
          class="text-purple"
          color="purple"
          density="comfortable"
          placeholder="Ej: Torniquetes"
          hide-details
          prepend-inner-icon="outlined_flag"
        ></v-text-field>
      </div>
    </v-expand-transition>
    <div class="ml-4 mb-2">
      <v-checkbox
        v-model="same_end_as_route"
        label="El destino el mismo que Final"
        class="text-purple"
        hide-details
        density="compact"
      ></v-checkbox>
    </div>
  </v-card>
</template>

<style scoped>

</style>