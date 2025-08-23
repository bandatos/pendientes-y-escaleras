<script setup>
import TextField from "./TextField.vue";
import Button from "./Button.vue";
let line = defineModel("line");
let station = defineModel("station");
let typeElevation = defineModel("typeElevation"); //Stair, Elevator or...
let isWorking = defineModel("isWorking");
let evidenceImage = defineModel("evidenceImage");

const handleSubmit = () => {
  console.log('Form data:', {
    line: line.value,
    station: station.value,
    typeElevation: typeElevation.value,
    isWorking: isWorking.value,
    evidenceImage: evidenceImage.value
  });
};
</script>

<template>
  <div class="greetings" pb-5>
    <h2>Subir Evidencia</h2>
  </div>
  <v-container>
    <v-form>
      <TextField v-model="line" :label="'Número de Línea'"></TextField>
      <TextField v-model="station" :label="'Estación'"></TextField>
      <TextField
        v-model="typeElevation"
        :label="'Número de Escalera'"
      ></TextField>
      <v-radio-group v-model="isWorking" label="¿Funciona?" inline>
        <v-radio label="Sí" value="true"></v-radio>
        <v-radio label="No" value="false"></v-radio>
      </v-radio-group>
      <TextField
        v-if="isWorking === 'false'"
        v-model="evidenceImage"
        :label="'Subir Evidencia'"
      ></TextField>
      <Button 
        :label="'Enviar'"
        color="primary"
        @click="handleSubmit"
      ></Button>
    </v-form>
  </v-container>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h2 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h2 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h2 {
    text-align: left;
  }
}
</style>
