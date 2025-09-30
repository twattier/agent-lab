/**
 * Test utilities for AgentLab frontend tests
 *
 * This file provides custom render functions and utilities for testing
 * React components with all necessary providers and context.
 */
import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import type { RenderResult } from '@testing-library/react';

/**
 * Custom render function that wraps components with necessary providers
 *
 * @example
 * ```tsx
 * import { renderWithProviders } from '@/__tests__/test-utils'
 *
 * test('renders with providers', () => {
 *   const { getByText } = renderWithProviders(<MyComponent />)
 *   expect(getByText('Hello')).toBeInTheDocument()
 * })
 * ```
 */
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
): RenderResult {
  // Add providers here as they are implemented
  // Example: QueryClientProvider, ThemeProvider, etc.
  const Wrapper = ({ children }: { children: React.ReactNode }) => {
    return <>{children}</>;
  };

  return render(ui, { wrapper: Wrapper, ...options });
}

/**
 * Re-export everything from React Testing Library
 */
export * from '@testing-library/react';

/**
 * Custom matchers and utilities
 */
export { default as userEvent } from '@testing-library/user-event';
