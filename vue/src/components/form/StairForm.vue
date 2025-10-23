<script setup>

import {computed, ref} from "vue";
import UploadImage from "@/components/UploadImage.vue";
import ConnectionPoints from "@/components/form/ConnectionPoints.vue";
import {useSurveyStore} from "@/stores/surveyStore.js";

const surveyStore = useSurveyStore()

const { currentSurvey, currentStairs } = surveyStore

const props = defineProps({
  stair: {
    type: Object,
    required: true,
  },
  stair_index: {
    type: Number,
    required: true,
  },
  all_status: {
    type: Array,
    required: true,
  },
});

const emits = defineEmits(
  ["add-new-code", "show-warning", "mark-complete"]
);

const full_status = computed(() => {
  if (props.stair.status === "pending") {
    return props.all_status.find((status) => status.key === "pending");
  }
  return props.stair.is_working
    ? props.all_status.find((status) => status.is_working === true)
    : props.all_status.find((status) => status.key === "not_working");
});

const directions = [
  { label: "Sube", value: "move_up", key: "up" },
  { label: "Baja", value: "move_down", key: "down" },
];

const new_codes = ref("");

function addCode() {
  const code = new_codes.value;
  if (code?.trim()) {
    props.stair.code_identifiers.push(code.trim());
    new_codes.value = "";
  }
}
function removeCode(codeIndex) {
  props.stair.code_identifiers.splice(codeIndex, 1);
}
const markStairComplete = (stairIndex) => {
  const stair = props.stair;
  const hasCodes = stair.code_identifiers && stair.code_identifiers.length > 0;
  const hasCodesEmpty = !stair.code_identifiers || stair.code_identifiers.length === 0
  // Validaciones básicas
  // Solo validar códigos si hasCodes no está explícitamente marcado como true (sin códigos)

  let warningMessage = ''
  if (hasCodes && hasCodesEmpty) {
    warningMessage = 'Agrega al menos un código de identificación o marca que no hay códigos visibles'
  }
  else if (!stair.route_start?.trim()) {
    warningMessage = 'Especifica el punto de inicio'
  }
  else if (stair.is_working === null) {
    warningMessage = 'Indica si la escalera funciona'
  }
  else
    props.stair.status = 'completed'

  if (warningMessage) {
    emits("show-warning", warningMessage);
  }
  else {

    emits("mark-complete", stairIndex);
  }

}


</script>

<template>

  <v-expansion-panel
    :value="stair_index"
  >
    <!-- Panel Title -->
    <v-expansion-panel-title color="grey-lighten-4">
      <div class="d-flex align-center w-100">
        <v-icon :color="full_status?.color || 'grey'" class="mr-3">
          {{ full_status?.icon || "help_outline" }}
        </v-icon>
        <div>
          <div class="font-weight-bold">
            Escalera {{ stair.number }}
          </div>
          <div
            v-if="stair.status === 'completed'"
            class="text-caption text-medium-emphasis"
          >
            {{ stair.is_working ? "Funciona" : "No funciona" }}
            <span v-if="stair.photo_ids?.length > 0">
              • 📷 {{ stair.photo_ids.length }}
            </span>
          </div>
          <div class="text-caption text-warning" v-else>Pendiente</div>
        </div>
      </div>
    </v-expansion-panel-title>

    <!-- Panel Content - Formulario completo -->
    <v-expansion-panel-text>
      <v-card flat>
        <v-card-text class="px-0">
          <!-- Nota informativa -->
          <v-alert
            type="info"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            Toma en cuenta que pueden tener varios identificadores
          </v-alert>

          <!-- Códigos de identificación -->
          <div class="mb-4">
            <label class="text-subtitle-2 mb-2 d-block">
              Códigos de identificación
              <v-icon size="small" class="ml-1">
                help_outline
                <v-tooltip activator="parent" location="left">
                  Por ejemplo: KSG3-43, ALT-01, etc.
                </v-tooltip>
              </v-icon>
            </label>

            <div class="d-flex gap-2 mb-2">
              <v-text-field
                v-model="new_codes"
                variant="outlined"
                density="compact"
                placeholder="Ej: KSG3-43"
                hide-details
                @keyup.enter="addCode()"
              ></v-text-field>
              <v-btn
                color="primary"
                size="small"
                icon
                @click="addCode()"
              >
                <v-icon size="large"> add </v-icon>
              </v-btn>
            </div>

            <v-checkbox
              v-if="
                !stair.code_identifiers ||
                stair.code_identifiers.length === 0
              "
              v-model="stair.hasCodes"
              color="error"
              variant="text"
              size="small"
              class="mb-2"
              hide-details
              label="No hay visible ningún código"
            >
            </v-checkbox>
            <div class="d-flex flex-wrap gap-2">
              <v-chip
                v-for="(code, codeIndex) in stair.code_identifiers"
                :key="codeIndex"
                closable
                @click:close="removeCode(codeIndex)"
                color="primary"
                variant="outlined"
                size="small"
                class="mr-2 mb-2"
              >
                {{ code }}
              </v-chip>
            </div>
          </div>

          <ConnectionPoints
            :stair="stair"
          />

          <!-- Detalles -->
          <div class="mb-4">
            <label class="text-subtitle-2 mb-2 d-block">
              Escribe más detalles para identificar la escalera
            </label>
            <v-textarea
              v-model="stair.details"
              variant="outlined"
              rows="2"
              auto-grow
              placeholder="Está de lado derecho (viendo desde abajo)"
              hide-details
              density="compact"
            ></v-textarea>
          </div>

          <!-- ¿Funciona? -->
          <div class="mb-4">
            <label class="text-subtitle-2 mb-2 d-block">
              ¿Funciona la escalera?
            </label>
            <v-radio-group
              v-model="stair.is_working"
              inline
              hide-details
            >
              <v-radio
                label="Sí"
                :value="true"
                color="success"
                class="mr-3"
              ></v-radio>
              <v-radio label="No" :value="false" color="error">
              </v-radio>
            </v-radio-group>
          </div>

          <!-- En qué dirección funciona -->
          <div class="mb-4">
            <label class="text-subtitle-2 mb-2 d-block">
              ¿En qué dirección opera la escalera?
            </label>
            <v-item-group>

                <v-row>
                  <v-col
                    v-for="direction in directions"
                    :key="direction.key"
                    cols="6"
                  >
                    <v-item v-slot="{ isSelected, toggle }">
                      <v-card
                        :color="isSelected ? 'secondary' : ''"
                        class="d-flex align-center px-3 py-1 align-center justify-center"
                        dark
                        @click="toggle"
                      >
                        <v-icon size="24" class="mr-2">
                          {{ direction.value }}
                        </v-icon>
                        <div class="text-h6">
                          {{ direction.label }}
                        </div>
                      </v-card>
                    </v-item>
                  </v-col>
                </v-row>

            </v-item-group>

          </div>

          <!-- Fotos -->
          <div class="mb-4">
            <label class="text-subtitle-2 mb-2 d-block">
              Adjunta fotos de la escalera y sus identificadores
            </label>
            <UploadImage
              :title="'Subir fotos'"
              :typeFiles="'image/*'"
              :stairId="stair.id"
            />
          </div>

          <!-- Botón confirmar escalera -->
          <v-btn
            color="primary"
            block
            @click="markStairComplete"
            :variant="
              stair.status === 'completed' ? 'outlined' : 'elevated'
            "
          >
            <v-icon start>
              {{
                stair.status === "completed" ? "check_circle" : "check"
              }}
            </v-icon>
            {{
              stair.status === "completed"
                ? "Guardar cambios"
                : "Completar escalera"
            }}
          </v-btn>
        </v-card-text>
      </v-card>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<style scoped>

</style>