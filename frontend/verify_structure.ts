import * as fs from 'fs'
import * as path from 'path'

function verifyPath(relativePath: string): { status: boolean; message: string } {
  const fullPath = path.resolve(__dirname, relativePath)
  return {
    status: fs.existsSync(fullPath),
    message: `${relativePath}: ${fs.existsSync(fullPath) ? '✅' : '❌'}`
  }
}

function verifyFrontendStructure() {
  const requiredPaths = [
    'src/components',
    'src/pages',
    'src/services',
    'src/hooks',
    'src/utils',
    'src/styles',
    'src/services/api.ts',
    'src/utils/queryClient.ts',
    'src/App.tsx',
    'public',
    'index.html',
    'package.json',
    'vite.config.ts',
    'tailwind.config.js',
    '.env.development',
    'tsconfig.json'
  ]

  console.log('\nVerifying Frontend Structure...\n')

  const results = requiredPaths.map(path => ({
    path,
    ...verifyPath(path)
  }))

  const missingPaths = results.filter(r => !r.status)

  console.log('Directory Structure Check:')
  console.log('-------------------------')
  results.forEach(result => {
    console.log(result.message)
  })

  if (missingPaths.length > 0) {
    console.log('\n❌ Missing Required Files/Directories:')
    missingPaths.forEach(missing => {
      console.log(`  - ${missing.path}`)
    })
    return false
  }

  // Verify package.json dependencies
  try {
    const packageJson = require('./package.json')
    const requiredDependencies = [
      'react',
      'react-dom',
      '@tanstack/react-query',
      'axios',
      'tailwindcss'
    ]

    console.log('\nDependency Check:')
    console.log('----------------')
    const missingDeps = requiredDependencies.filter(
      dep => !packageJson.dependencies?.[dep] && !packageJson.devDependencies?.[dep]
    )

    if (missingDeps.length > 0) {
      console.log('❌ Missing Required Dependencies:')
      missingDeps.forEach(dep => {
        console.log(`  - ${dep}`)
      })
      return false
    }
    console.log('✅ All required dependencies are installed')
  } catch (error) {
    console.log('❌ Error reading package.json')
    return false
  }

  console.log('\n✅ Frontend structure verification complete!')
  console.log('✅ All required files and directories are present!')
  return true
}

// Run verification
const success = verifyFrontendStructure()
process.exit(success ? 0 : 1) 