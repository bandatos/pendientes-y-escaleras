<script setup>
import { computed } from 'vue'

const props = defineProps({
  stationData: {
    type: Object,
    required: true
  },
})

const squareStyle = computed(() => {
  const gradient = generateGradient(props.stationData.line_colors)
  return {
    background: gradient
  }
})

const generateGradient = (colors) => {
  // Si solo hay un color, retornar ese color sólido
  if (colors.length === 1) {
    return colors[0]
  }

  // Calcular el porcentaje de cada franja
  const percentage = 100 / colors.length
  let gradientStops = []

  // Crear las franjas con bordes definidos (sin difuminado)
  colors.forEach((color, index) => {
    const start = percentage * index
    const end = percentage * (index + 1)
    gradientStops.push(`${color} ${start}%`)
    gradientStops.push(`${color} ${end}%`)
  })

  return `linear-gradient(135deg, ${gradientStops.join(', ')})`
}
</script>

<template>
  <v-avatar
    v-if="stationData.line_colors"
    class="stripe-square"
    :style="squareStyle"
  >
    <span class="text-white text-caption">
      {{ stationData.lines }}
    </span>
  </v-avatar>
  <v-avatar
    v-else
    :style="{ backgroundColor: stationData.line_color }"
    size="40"
    class="stripe-square"
  >
    <span class="text-white text-h6s">
      {{stationData.first_route.route_short_name || '?'}}
    </span>
  </v-avatar>

</template>

<style scoped>

</style>