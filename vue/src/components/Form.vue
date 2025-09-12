<script setup>
import TextField from "./TextField.vue";
import Button from "./Button.vue";
import { ref, onMounted, computed } from "vue";
import { useSyncStore } from "../stores/syncStore.js";

/* Estado del formulario -> Equivalente al data dentro de OptionsAPI */

// Form data
/* const line = ref("");
const station = ref("");
const typeElevation = ref(""); //Stair, Elevator or Stair Lift
const isWorking = ref(true);
const evidenceImage = ref(""); */

const isSubmitting = ref(false);
const submitMessage = ref("");

/* Connectar con el uso del store para su uso con los componentes*/
// Store
const syncStore = useSyncStore();

// Computed properties para mostrar estado
const connectionStatus = computed(
  () => (syncStore.isOnline ? "🟢 Conectado" : "🔴 Sin conexión") //Acceso al state
);

const pendingCount = computed(() => syncStore.syncStats.pending);

// Inicializar store cuando se monta el componente
onMounted(() => {
  syncStore.init(); //Acceso a una action
});

// Manejar envío del formulario
const handleSubmit = async () => {
  if (isSubmitting.value) return;

  // Validación básica
  if (!syncStore.report.line.trim() || !syncStore.report.station.trim()) {
    submitMessage.value = "❌ Por favor completa los campos obligatorios";
    setTimeout(() => (submitMessage.value = ""), 3000);
    return;
  }

  isSubmitting.value = true;
  submitMessage.value = "";

  try {
    const formData = {
      line: syncStore.report.line.trim(),
      station: syncStore.report.station.trim(),
      typeElevation: syncStore.report.typeElevation.trim(),
      isWorking: syncStore.report.isWorking,
      evidenceImage: syncStore.report.evidenceImage,
    };

    console.log("📋 Enviando formulario:", formData);

    // Guardar usando el store (maneja local + sync automático)
    await syncStore.saveFormData(formData);

    // Mostrar mensaje de éxito
    if (syncStore.isOnline) {
      submitMessage.value = "✅ Datos enviados y sincronizados";
    } else {
      submitMessage.value =
        "💾 Datos guardados localmente - Se sincronizarán cuando haya conexión";
    }

    cleanForm();
  } catch (error) {
    console.error("❌ Error al enviar formulario:", error);
    submitMessage.value = "❌ Error al guardar los datos";
  } finally {
    isSubmitting.value = false;

    // Limpiar mensaje después de 5 segundos
    setTimeout(() => (submitMessage.value = ""), 5000);
  }

  // Limpiar formulario
  function cleanForm() {
    /* Cuando hacemos esto y es declarando arriba
      const line = ref(''); Aquí no estamos reasignado que sería el papel que uno observa
      dentro de JS cuando tienes una const, más bien estamos mutando el contenido, no la
      referencia.
    */
    syncStore.report.line = "";
    syncStore.report.station = "";
    syncStore.report.typeElevation = "";
    syncStore.report.isWorking = true;
    syncStore.report.evidenceImage = "";
  }
};
</script>

<template>
  <div class="greetings" pb-5>
    <h2>Subir Evidencia</h2>

    <!-- Status bar -->
    <v-card class="mb-4 pa-2" variant="outlined">
      <div class="d-flex justify-space-between align-center">
        <span class="text-body-2">{{ connectionStatus }}</span>
        <span v-if="pendingCount > 0" class="text-warning text-body-2">
          📋 {{ pendingCount }} pendientes
        </span>
        <v-btn
          v-if="pendingCount > 0 && syncStore.isOnline"
          size="small"
          color="primary"
          @click="syncStore.forceSync()"
          :loading="syncStore.isSyncing"
        >
          Sincronizar
        </v-btn>
      </div>
    </v-card>
  </div>
  <v-container>
    <v-form>
      <!-- Sin embargo, no se requiere acceder a line.value en el template
          esto nos los brindará un unwrapped de la variable.
        -->
      <v-autocomplete
        v-model="syncStore.report.line"
        :items="syncStore.lines"
        label="Número de Línea"
        item-title="line"
      >
        <template v-slot:chip="{ props, item }">
          <v-chip v-bind="props" :color="item?.raw?.color">
            {{ item.raw.name }}
          </v-chip>
        </template>
        <template v-slot:item="{ props, item }">
          <v-list-item
            v-bind="props"
            :title="item?.raw?.name"
            :subtitle="item?.raw?.line"
            :value="item?.raw?.line"
          >
            <template v-slot:append>
              <v-chip :color="item?.raw?.color">{{ item?.raw?.name }}</v-chip>
            </template>
          </v-list-item>
        </template>
      </v-autocomplete>
      <TextField
        v-model="syncStore.report.station"
        :label="'Estación'"
      ></TextField>
      <TextField
        v-model="syncStore.report.typeElevation"
        :label="'Número de Escalera'"
      ></TextField>
      <v-radio-group
        v-model="syncStore.report.isWorking"
        label="¿Funciona?"
        inline
      >
        <v-radio label="Sí" value="true"></v-radio>
        <v-radio label="No" value="false"></v-radio>
      </v-radio-group>
      <v-file-input
        v-if="syncStore.report.isWorking === 'false'"
        v-model="syncStore.report.evidenceImage"
        :label="'Subir Evidencia'"
      ></v-file-input>

      <!-- Submit button with loading state -->
      <Button
        :label="isSubmitting ? 'Enviando...' : 'Enviar'"
        color="primary"
        :disabled="isSubmitting"
        @click="handleSubmit"
      ></Button>

      <!-- Feedback message -->
      <v-alert
        v-if="submitMessage"
        :type="submitMessage.includes('❌') ? 'error' : 'success'"
        class="mt-3"
        closable
        @click:close="submitMessage = ''"
      >
        {{ submitMessage }}
      </v-alert>
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
