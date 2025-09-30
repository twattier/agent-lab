# Frontend Installation Guide

## Prerequisites

- Node.js 18.17.0
- npm 9.x+

## Installation Order

Follow this exact order to avoid dependency conflicts:

### 1. Next.js and React Core
```bash
npm install next@13.4.19 react@18.2.0 react-dom@18.2.0
```

### 2. TypeScript and Build Tools
```bash
npm install --save-dev typescript@5.1.6 @types/react@18.3.11 @types/react-dom@18.3.1 @types/node@20.14.0
```

### 3. Tailwind CSS and shadcn/ui Dependencies
```bash
npm install tailwindcss@3.3.3 postcss@8.4.27 autoprefixer@10.4.14
npm install clsx tailwind-merge class-variance-authority @radix-ui/react-slot lucide-react
```

### 4. State Management
```bash
npm install @tanstack/react-query@5.59.0 zustand@4.5.0
npm install --save-dev @tanstack/react-query-devtools@5.59.0
```

### 5. Development Tools
```bash
npm install --save-dev eslint@8.45.0 eslint-config-next@13.4.19
```

## Quick Install

For a fresh installation, run:
```bash
npm install
```

## Validation

Run the installation validation script:
```bash
node scripts/validate-install.js
```

## Common Issues

### Issue: React types conflict
**Symptom**: TypeScript errors about ReactNode types
**Solution**: Ensure @types/react and @types/react-dom are at compatible versions (18.3.x)

### Issue: Next.js babel module not found
**Symptom**: ESLint parsing errors
**Solution**: This is expected with Next.js 13.4.19 and can be ignored for JS config files

### Issue: Peer dependency warnings
**Symptom**: npm warnings about unmet peer dependencies
**Solution**: These are warnings only and won't affect functionality

## Troubleshooting

If installation fails:

1. Clear cache and reinstall:
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

2. Verify Node.js version:
```bash
node --version  # Should be 18.17.0
```

3. Check for conflicting global packages:
```bash
npm list -g --depth=0
```

## Development Server

Start the development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000 (or next available port).

## Build

Build for production:
```bash
npm run build
```

## Type Checking

Run TypeScript type checking:
```bash
npm run type-check
```
