<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
});

const model = defineModel();
</script>

<template>
  <v-text-field :label="label" v-model="model"></v-text-field>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
