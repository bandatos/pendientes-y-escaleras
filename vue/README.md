# Sistema de Relevamiento


## Project Setup

```sh
yarn || yarn install
```

### Dependencies
- Vue
- Pinia
- Vite
- Vuetify

### Dev Dependencies
- unplugin-auto-import (AutoImport)

### Compile and Hot-Reload for Development

```sh
yarn dev
```

### Compile and Minify for Production

```sh
yarn build
```



### Considerations
The system only load the stair from the Sistema Metro (Incluir nombre del Sistema), because there stations cases where looks
have more stairs, however in those cases their stairs don't belong to the station could be from part of a mall.
Examples:
- Rosario Station