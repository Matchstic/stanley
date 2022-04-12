/* eslint-disable no-undef */
module.exports = {
  root: true,
  parser: "vue-eslint-parser",
  plugins: [
    '@typescript-eslint',
  ],
  extends: [
    'plugin:vue/recommended',
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
  ],
  settings: {
    'import/parsers': {
      '@typescript-eslint/parser': ['.ts', '.tsx'],
    },
    'import/resolver': {
      typescript: {},
    }
  },
  parserOptions: {
    parser: require.resolve('@typescript-eslint/parser'),
    ecmaFeatures: {
      jsx: true
    }
  },
  rules: {
    'semi': ["error", "never"],
    "indent": ["error", 2],
    '@typescript-eslint/no-explicit-any': 'off',
    'no-async-promise-executor': 'off',
    '@typescript-eslint/ban-ts-comment': 'off',
    'no-useless-escape': 'off',
    "@typescript-eslint/explicit-function-return-type": 0,
    "@typescript-eslint/explicit-module-boundary-types": 'off'
  },
}