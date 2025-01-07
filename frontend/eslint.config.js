import tsParser from '@typescript-eslint/parser'
import tsPlugin from '@typescript-eslint/eslint-plugin'
import reactRefreshPlugin from 'eslint-plugin-react-refresh'
import reactHooksPlugin from 'eslint-plugin-react-hooks'

export default [
  // Config for Node.js files
  {
    files: ['**/*.js'],
    ignores: ['**/dist/**', '**/build/**', '**/node_modules/**'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        // Node.js globals
        process: true,
        console: true,
        module: true,
        require: true,
        __dirname: true,
        error: true
      }
    },
    rules: {
      'no-unused-vars': ['warn', { 
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
      }],
    }
  },
  
  // Config for React/TypeScript files
  {
    files: ['**/*.{ts,tsx}'],
    ignores: [
      '**/dist/**',
      '**/build/**',
      '**/node_modules/**',
      'vite.config.ts',
      '.eslintrc.cjs',
    ],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        window: true,
        document: true,
        console: true,
        process: true,
        setTimeout: true,
        clearTimeout: true,
        setInterval: true,
        clearInterval: true,
        fetch: true,
        Promise: true,
        navigator: true,
        location: true,
        localStorage: true,
        sessionStorage: true,
        MutationObserver: true,
        performance: true,
        MessageChannel: true,
        reportError: true,
        queueMicrotask: true,
        AbortController: true,
        MSApp: true,
        __REACT_DEVTOOLS_GLOBAL_HOOK__: true
      },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      'react-refresh': reactRefreshPlugin,
      'react-hooks': reactHooksPlugin,
    },
    rules: {
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      'no-unused-vars': ['warn', { 
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
      }],
      'no-console': 'off',
      'no-empty': 'warn',
      'no-prototype-builtins': 'off',
      'no-constant-condition': 'warn',
      'no-case-declarations': 'off',
      'no-control-regex': 'off',
      'no-useless-escape': 'warn',
      'no-fallthrough': 'warn',
      'getter-return': 'warn',
      'no-func-assign': 'warn',
      'valid-typeof': 'warn',
      'no-cond-assign': ['warn', 'except-parens'],
    }
  }
];
