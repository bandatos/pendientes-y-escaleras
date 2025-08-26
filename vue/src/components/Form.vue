<script setup>
import TextField from "./TextField.vue";
import Button from "./Button.vue";
import { ref, onMounted, computed } from "vue";
import { useSyncStore } from "../stores/syncStore.js";

// Form data
let line = ref("");
let station = ref("");
let typeElevation = ref(""); //Stair, Elevator or...
let isWorking = ref(true);
let evidenceImage = ref("");

// Store
const syncStore = useSyncStore();

// Estado del formulario
const isSubmitting = ref(false);
const submitMessage = ref("");

// Computed properties para mostrar estado
const connectionStatus = computed(() => 
  syncStore.isOnline ? "🟢 Conectado" : "🔴 Sin conexión"
);

const pendingCount = computed(() => syncStore.syncStats.pending);

// Inicializar store cuando se monta el componente
onMounted(() => {
  syncStore.init();
});

// Manejar envío del formulario
const handleSubmit = async () => {
  if (isSubmitting.value) return;
  
  // Validación básica
  if (!line.value.trim() || !station.value.trim()) {
    submitMessage.value = "❌ Por favor completa los campos obligatorios";
    setTimeout(() => submitMessage.value = "", 3000);
    return;
  }
  
  isSubmitting.value = true;
  submitMessage.value = "";
  
  try {
    const formData = {
      line: line.value.trim(),
      station: station.value.trim(),
      typeElevation: typeElevation.value.trim(),
      isWorking: isWorking.value,
      evidenceImage: evidenceImage.value.trim()
    };
    
    console.log("📋 Enviando formulario:", formData);
    
    // Guardar usando el store (maneja local + sync automático)
    await syncStore.saveFormData(formData);
    
    // Mostrar mensaje de éxito
    if (syncStore.isOnline) {
      submitMessage.value = "✅ Datos enviados y sincronizados";
    } else {
      submitMessage.value = "💾 Datos guardados localmente - Se sincronizarán cuando haya conexión";
    }
    
    // Limpiar formulario
    line.value = "";
    station.value = "";
    typeElevation.value = "";
    isWorking.value = true;
    evidenceImage.value = "";
    
  } catch (error) {
    console.error("❌ Error al enviar formulario:", error);
    submitMessage.value = "❌ Error al guardar los datos";
  } finally {
    isSubmitting.value = false;
    
    // Limpiar mensaje después de 5 segundos
    setTimeout(() => submitMessage.value = "", 5000);
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
        v-if="!isWorking"
        v-model="evidenceImage"
        :label="'Subir Evidencia'"
      ></TextField>
      
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
