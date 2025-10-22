<script setup>
import { computed } from 'vue'

const props = defineProps({
  colors: {
    type: Array,
    required: true,
    validator: (value) => value.length >= 1 && value.length <= 4
  },
  line_text: {
    type: String,
    default: '◯'
  }
})

const squareStyle = computed(() => {
  const gradient = generateGradient(props.colors)
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
  <v-avatar class="stripe-square" :style="squareStyle">
    <span class="text-white text-caption">
      {{ line_text }}
    </span>

  </v-avatar>
</template>

<style scoped>

</style>