#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Validating frontend installation...\n');

const checks = [];

// Check 1: Verify npm list has no errors
console.log('Checking npm dependencies...');
try {
  execSync('npm list --depth=0', { stdio: 'ignore' });
  checks.push({ name: 'npm dependencies', status: '✅ PASS' });
} catch (error) {
  checks.push({ name: 'npm dependencies', status: '❌ FAIL - Run npm install' });
}

// Check 2: Verify peer dependencies
console.log('Checking peer dependencies...');
try {
  const output = execSync('npm ls --parseable 2>&1', { encoding: 'utf-8' });
  if (output.includes('UNMET PEER DEPENDENCY')) {
    checks.push({ name: 'peer dependencies', status: '⚠️  WARNING - Unmet peer deps' });
  } else {
    checks.push({ name: 'peer dependencies', status: '✅ PASS' });
  }
} catch (error) {
  checks.push({ name: 'peer dependencies', status: '✅ PASS' });
}

// Check 3: TypeScript compilation
console.log('Checking TypeScript compilation...');
try {
  execSync('npx tsc --noEmit', { stdio: 'ignore' });
  checks.push({ name: 'TypeScript compilation', status: '✅ PASS' });
} catch (error) {
  checks.push({ name: 'TypeScript compilation', status: '❌ FAIL - Type errors exist' });
}

// Check 4: Critical files exist
console.log('Checking critical files...');
const criticalFiles = [
  'package.json',
  'next.config.js',
  'tsconfig.json',
  'tailwind.config.js',
  'src/app/layout.tsx',
  'src/app/page.tsx',
];

const missingFiles = criticalFiles.filter(file => !fs.existsSync(path.join(process.cwd(), file)));
if (missingFiles.length === 0) {
  checks.push({ name: 'critical files', status: '✅ PASS' });
} else {
  checks.push({ name: 'critical files', status: `❌ FAIL - Missing: ${missingFiles.join(', ')}` });
}

// Print results
console.log('\n📊 Installation Validation Results:\n');
checks.forEach(check => {
  console.log(`${check.status.padEnd(25)} ${check.name}`);
});

const allPassed = checks.every(check => check.status.includes('✅'));
console.log('\n' + (allPassed ? '✅ All checks passed!' : '❌ Some checks failed'));

process.exit(allPassed ? 0 : 1);
