<script setup>


import {useSurveyStore} from "@/stores/index.js";

const surveyStore = useSurveyStore()
// const props = defineProps({
//   surveyStore: {
//     type: Object,
//     required: true,
//   },
// })
const {stats} = surveyStore

</script>

<template>
  <v-card
    class="rounded-0"
    variant="tonal"
    color="grey lighten-4"
  >
    <v-card-text class="py-3">
      <div class="d-flex justify-space-around text-center">
        <div>
          <div class="text-h6">{{ surveyStore.total_stairs }}</div>
          <div class="text-caption text-medium-emphasis">
            escaleras
          </div>
        </div>
        <v-divider vertical></v-divider>
        <div>
          <div class="text-h6 text-success">
            {{ stats.working }}
          </div>
          <div class="text-caption text-medium-emphasis">funcionan</div>
        </div>
        <v-divider vertical></v-divider>
        <div>
          <div class="text-h6 text-error">
            {{ stats.notWorking }}
          </div>
          <div class="text-caption text-medium-emphasis">
            no funcionan
          </div>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<style scoped>

</style>