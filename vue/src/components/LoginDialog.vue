<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '../stores/authStore'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  stationName: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'login-success', 'login-cancel'])

const authStore = useAuthStore()

// Estado local
const email = ref('')
const emailRules = [
  v => !!v || 'El correo es requerido',
  v => /.+@.+\..+/.test(v) || 'Debe ser un correo válido'
]
const formValid = ref(false)

// Computed para el diálogo
const dialog = ref(props.modelValue)

watch(() => props.modelValue, (newVal) => {
  dialog.value = newVal
})

watch(dialog, (newVal) => {
  emit('update:modelValue', newVal)
})

// Métodos
const handleLogin = async () => {
  if (!formValid.value) return

  const result = await authStore.login(email.value)

  if (result.success) {
    emit('login-success', result.data)
    closeDialog()
  }
}

const closeDialog = () => {
  dialog.value = false
  email.value = ''
}

const handleCancel = () => {
  emit('login-cancel')
  closeDialog()
}
</script>

<template>
  <v-dialog
    v-model="dialog"
    max-width="500px"
    persistent
  >
    <v-card>
      <v-card-title class="text-h5 pa-4">
        <v-icon class="mr-2" color="primary">login</v-icon>
        Autenticación requerida
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text class="pa-4">
        <p class="text-body-1 mb-4">
          Para realizar el relevamiento de <strong>{{ stationName }}</strong>,
          por favor ingresa tu correo electrónico.
        </p>

        <v-form v-model="formValid" @submit.prevent="handleLogin">
          <v-text-field
            v-model="email"
            label="Correo electrónico"
            type="email"
            variant="outlined"
            prepend-inner-icon="email"
            :rules="emailRules"
            :disabled="authStore.isLoading"
            autofocus
            @keyup.enter="handleLogin"
          ></v-text-field>
        </v-form>

        <v-alert
          v-if="!authStore.isAuthenticated"
          type="info"
          variant="tonal"
          density="compact"
          class="mt-2"
        >
          Solo usuarios autorizados pueden realizar relevamientos
        </v-alert>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="pa-4">
        <v-btn
          variant="text"
          @click="handleCancel"
          :disabled="authStore.isLoading"
        >
          Cancelar
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="elevated"
          :disabled="!formValid"
          :loading="authStore.isLoading"
          @click="handleLogin"
        >
          Ingresar
          <v-icon end>arrow_forward</v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
strong {
  color: rgb(var(--v-theme-primary));
}
</style>
