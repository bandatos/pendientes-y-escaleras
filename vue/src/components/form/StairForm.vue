<script setup>

import {computed, ref} from "vue";
import UploadImage from "@/components/UploadImage.vue";
import ConnectionPoints from "@/components/form/ConnectionPoints.vue";
import {useSurveyStore} from "@/stores/surveyStore.js";

import rulesMixin from "@/composables/rulesMixin.js";
const { rules } = rulesMixin;

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


const is_accessible = ref(null);
const errors = ref(null);
const save_errors = ref([]);
const stairForm = ref(null);

const emits = defineEmits(
  ["add-new-code", "show-warning", "mark-complete"]
);

const has_codes_rule = computed(() => {
  if (props.stair.without_codes)
    return true;
  return (
    props.stair.code_identifiers &&
    props.stair.code_identifiers.length > 0
    || "⬆️ Agrega al menos un código de identificación o marca que no hay códigos visibles"
  );
});

const accessible_rule = computed(() => {
  return is_accessible.value === null || is_accessible.value === undefined
    ? "Selecciona si se puede acceder a la escalera"
    : true;
});

const is_working_rule = computed(() => {
  return props.stair.is_working === null || props.stair.is_working === undefined
    ? "Selecciona si la escalera funciona"
    : true;
});

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

const accessible_options = [
  { label: "Sí", value: true, key: "yes", color: "green" },
  { label: "No", value: false, key: "no", color: "red" },
];

const new_codes = ref("");

function changeIsAccessible(value) {
  is_accessible.value = value;
  if (value === false) {
    props.stair.code_identifiers = [];
    props.stair.without_codes = false;
    props.stair.is_working = false;
  }
  if (value === true) {
    props.stair.status_maintenance = null;
    props.stair.other_status_maintenance = "";
  }
}

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
async function markStairComplete() {
  const { valid } = await stairForm.value.validate()
  errors.value = null
  if (!valid){
    save_errors.value = [{
      field: 'todo el formulario',
      errors: 'Hay errores con algunos campos, scrolea y revísalos.'
    }]
    return
  }

  save_errors.value = []

  props.stair.status = 'completed'
  emits("mark-complete");
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
          <v-form
            ref="stairForm"
          >
            <!-- En qué dirección funciona -->
            <div class="mb-4">
              <v-alert
                v-if="false"
                type="info"
                variant="tonal"
                density="compact"
                class="mb-4"
                icon-size="small"
              >
                Indica si se puede llegar a la escalera libremente
                (sin importar si funciona o no)
              </v-alert>

              <label class="text-subtitle-1">
                ¿Se puede acceder a la escalera?
              </label>
              <v-spacer></v-spacer>
              <v-input
                :rules="[accessible_rule]"
                hide-details="auto"
              >
                <v-btn-toggle
                  divided
                  v-model="is_accessible"
                  density="comfortable"
                  :rules="[rules.defined]"
                  @update:model-value="changeIsAccessible"
                >
                  <v-btn
                    v-for="option in accessible_options"
                    :key="option.key"
                    :value="option.value"
                    :color="option.color"
                    hide-details
                    :variant="is_accessible === option.value ? 'elevated' : 'outlined'"
                    min-width="80"
                  >
                    {{ option.label }}
                  </v-btn>
                </v-btn-toggle>
              </v-input>
            </div>

            <template v-if="is_accessible === false">
              <div class="mb-4">
                <label class="text-subtitle-2 mb-2 d-block">
                  Estado de mantenimiento
                  <v-icon size="small" class="ml-1">
                    help_outline
                    <v-tooltip activator="parent" location="top">
                      Indica el nivel de deterioro o estado general
                    </v-tooltip>
                  </v-icon>
                </label>
                <v-select
                  v-model="stair.status_maintenance"
                  :items="[
                    { title: 'Menor (funcional, desgaste leve | sin tablas)', value: 'minor' },
                    { title: 'Mayor (requiere atención pronto | con tablas)', value: 'medium' },
                    { title: 'Crítico | Reconstrucción completa (requiere atención urgente)', value: 'full' },
                    { title: 'Otro (especificar)', value: 'other' }
                  ]"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="compact"
                  placeholder="Selecciona el estado"
                  hide-details="auto"
                ></v-select>
              </div>

              <!-- Otro estado de mantenimiento (solo si eligió 'other') -->
              <v-expand-transition>
                <div v-if="stair.status_maintenance === 'other'" class="mb-4">
                  <label class="text-subtitle-2 mb-2 d-block">
                    Especifica el estado de mantenimiento
                  </label>
                  <v-text-field
                    v-model="stair.other_status_maintenance"
                    :rules="[rules.required]"
                    variant="outlined"
                    density="compact"
                    placeholder="Ej: Escalones sueltos en la parte superior"
                    hide-details
                  ></v-text-field>
                </div>
              </v-expand-transition>


              <!-- Si es crítico, mostrar alerta y permitir guardar directamente -->
              <v-alert
                v-if="stair.status_maintenance === 'full'"
                type="warning"
                variant="tonal"
                density="compact"
                class="mb-4"
              >
                ⚠️ Estado crítico detectado. Puedes guardar sin completar los demás campos. Si es necesario agrega fotos del estado.
            </v-alert>
            </template>
            <!-- Códigos de identificación -->
            <v-input
              v-else-if="is_accessible === true"
              :rules="[has_codes_rule]"
              hide-details="auto"
              class="mb-4"
            >
              <div>
                <label class="text-subtitle-2 mb-2 d-block">
                  Códigos de identificación
                  <v-icon size="small" class="ml-1">
                    help_outline
                    <v-tooltip activator="parent" location="left">
                      Por ejemplo: KSG3-43, ALT-01, etc.
                    </v-tooltip>
                  </v-icon>
                </label>

                <v-expand-transition>
                  <div v-if="stair.without_codes === false">
                    <v-alert
                      type="info"
                      variant="tonal"
                      density="compact"
                      class="mb-4"
                      icon-size="small"

                    >
                      Cada escalera puede tener varios identificadores
                    </v-alert>

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
                        class="ml-2"
                      >
                        <v-icon size="large"> add </v-icon>
                      </v-btn>
                    </div>
                  </div>
                </v-expand-transition>

                <v-checkbox
                  v-if="
                    !stair.code_identifiers ||
                    stair.code_identifiers.length === 0
                  "
                  v-model="stair.without_codes"
                  color="error"
                  variant="text"
                  size="small"
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
            </v-input>

            <ConnectionPoints
              v-if="is_accessible !== null && is_accessible !== undefined"
              :stair="stair"
              :is_accessible="is_accessible"
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

            <template v-if="is_accessible === true">

              <!-- ¿Funciona? -->
              <div class="mb-4" v-if="is_accessible === true">
                <label class="text-subtitle-2 mb-2 d-block">
                  ¿Funciona la escalera?
                </label>
                <v-input
                  :rules="[is_working_rule]"
                  hide-details="auto"
                >
                  <v-btn-toggle
                    divided
                    v-model="stair.is_working"
                    density="comfortable"
                    :rules="[rules.defined]"
                  >
                    <v-btn
                      v-for="option in accessible_options"
                      :key="option.key"
                      :value="option.value"
                      :color="option.color"
                      :variant="
                        stair.is_working === option.value
                          ? 'elevated'
                          : 'outlined'
                      "
                      min-width="80"
                    >
                      {{ option.label }}
                    </v-btn>
                  </v-btn-toggle>
                </v-input>
              </div>

              <!-- En qué dirección funciona -->
              <div v-if="stair.is_working === true" class="mb-4">
                <label class="text-subtitle-2 mb-2 d-block">
                  ¿En qué dirección opera la escalera?
                </label>
                <v-item-group
                  v-model="stair.direction_observed"
                >
                  <v-row>
                    <v-col
                      v-for="direction in directions"
                      :key="direction.key"
                      cols="6"
                    >
                      <v-item
                        v-slot="{ isSelected, toggle }"
                        :value="direction.value"
                      >
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
            </template>

            <!-- Fotos -->
            <div class="mb-4">
              <label class="text-subtitle-2 mb-2 d-block">
                Adjunta fotos de la escalera
                <span v-if="is_accessible === true">
                  y sus identificadores
                </span>
                <span v-else-if="is_accessible === false">
                  o de su entorno (letreros, reparaciones, etc.)
                </span>
              </label>
              <UploadImage
                :title="'Subir fotos'"
                :typeFiles="'image/*'"
                :stairId="stair.id"
              />
            </div>
            <v-row v-if="save_errors.length > 0">
              <v-col
                v-for="(error, index) in save_errors"
                :key="index"
                cols="12"
                class="d-flex justify-end px-6 py-1"
              >
                <v-alert
                  type="error"
                >
                  Error al guardar {{ error.field }}: {{ error.errors }}
                </v-alert>
              </v-col>
            </v-row>
            <!-- Botón confirmar escalera -->
            <v-btn
              color="primary"
              block
              @click="markStairComplete"
              xvariant="
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
          </v-form>
        </v-card-text>
      </v-card>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<style scoped>

</style>