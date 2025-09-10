<script setup>
import Form from "./components/Form.vue";
import MapaMetro from "./components/vis/MapaMetro.vue";
</script>

<template>
  <v-container>
    <v-row justify="center" class="fill-height" align="center">
      <v-col cols="12" sm="10" md="6" lg="4" xl="4">
        <Form />
      </v-col>
    </v-row>
  </v-container>
  <v-container>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="12" md="10" lg="10" xl="10">
        <MapaMetro></MapaMetro>
      </v-col>
    </v-row>
  </v-container>
</template>
