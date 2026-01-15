import antfu from '@antfu/eslint-config'

export default antfu({
  react: true,
  ignores: [
    '**/components/ui',
    '**/hooks/use-mobile.tsx',
  ],
})
