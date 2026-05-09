import { defineConfig } from 'nitro'

export default defineConfig({
  runtimeConfig: {
    backendEndpoint: 'https://api.fragapi.com/v1',
    sessionPassword: 'SomeVeryHackablePasswordThatIsSomething',
  },
})
