
let rulesMixin = {
  rules: {
    required: (value) => !!value || 'Valor Requerido.',
    defined: v => v !== undefined && v !== null && v!=="" || 'Elige una opción.',
    email: (value) => {
      const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}.\[0-9]{1,3}.\[0-9]{1,3}.\[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return pattern.test(value) || 'Escribe un correo válido'
    }
  }
}

export default rulesMixin
