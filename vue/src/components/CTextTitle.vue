<script setup>
const props = defineProps({
  title: {
    type: String,
    requiered: true,
  },
  sizeText: {
    type: String,
    default: "text-body-1",
  },
  color: { type: String },
  tooltip: {
    type: String,
  },
  direction: {
    type: String,
    default: "top", //left, right and bottom
  },
  sizeIcon: {
    type: String,
    default: "small",
  },
  icon: {
    type: String,
    default: "help_outline",
  },
});
</script>
<template >
  <div :class="[color, sizeText]" class="py-1 px-0 mb-1">
    {{ title }}
    <v-tooltip v-if="tooltip" :location="direction">
      <template v-slot:activator="{ props }">
        <v-icon v-bind="props" :size="sizeIcon" class="ml-1">
          {{ icon }}
        </v-icon>
      </template>
      {{ tooltip }}
    </v-tooltip>
  </div>
</template>
