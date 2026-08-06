<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  color: {
    type: String,
    default: "primary",
  },
  variant: {
    type: String,
    default: "elevated",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});
// This should emit a 'click' event when the button is pressed
// Use defineEmits to create the event emitter
defineEmits({
  event: "click",
});
</script>

<template>
  <v-btn :color="color" :variant="variant" :disabled="disabled" class="mt-4">
    {{ label }}
  </v-btn>
</template>

<style scoped>
/* Custom button styles can be added here if needed */
</style>