import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAppStore } from '../app-store';

describe('useAppStore', () => {
  beforeEach(() => {
    // Reset store to initial state before each test
    const { result } = renderHook(() => useAppStore());
    act(() => {
      result.current.sidebarOpen = true;
      result.current.currentLanguage = 'en';
      result.current.theme = 'light';
    });
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const { result } = renderHook(() => useAppStore());

      expect(result.current.sidebarOpen).toBe(true);
      expect(result.current.currentLanguage).toBe('en');
      expect(result.current.theme).toBe('light');
    });
  });

  describe('toggleSidebar', () => {
    it('should toggle sidebar from true to false', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.sidebarOpen).toBe(false);
    });

    it('should toggle sidebar from false to true', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.toggleSidebar();
        result.current.toggleSidebar();
      });

      expect(result.current.sidebarOpen).toBe(true);
    });

    it('should toggle sidebar multiple times correctly', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.toggleSidebar(); // false
        result.current.toggleSidebar(); // true
        result.current.toggleSidebar(); // false
        result.current.toggleSidebar(); // true
      });

      expect(result.current.sidebarOpen).toBe(true);
    });
  });

  describe('setLanguage', () => {
    it('should set language to French', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.setLanguage('fr');
      });

      expect(result.current.currentLanguage).toBe('fr');
    });

    it('should set language to English', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.setLanguage('fr');
        result.current.setLanguage('en');
      });

      expect(result.current.currentLanguage).toBe('en');
    });

    it('should change language multiple times', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.setLanguage('fr');
      });
      expect(result.current.currentLanguage).toBe('fr');

      act(() => {
        result.current.setLanguage('en');
      });
      expect(result.current.currentLanguage).toBe('en');

      act(() => {
        result.current.setLanguage('fr');
      });
      expect(result.current.currentLanguage).toBe('fr');
    });
  });

  describe('setTheme', () => {
    it('should set theme to dark', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.setTheme('dark');
      });

      expect(result.current.theme).toBe('dark');
    });

    it('should set theme to light', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.setTheme('dark');
        result.current.setTheme('light');
      });

      expect(result.current.theme).toBe('light');
    });

    it('should change theme multiple times', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.setTheme('dark');
      });
      expect(result.current.theme).toBe('dark');

      act(() => {
        result.current.setTheme('light');
      });
      expect(result.current.theme).toBe('light');

      act(() => {
        result.current.setTheme('dark');
      });
      expect(result.current.theme).toBe('dark');
    });
  });

  describe('state independence', () => {
    it('should not affect other state when toggling sidebar', () => {
      const { result } = renderHook(() => useAppStore());

      const initialLanguage = result.current.currentLanguage;
      const initialTheme = result.current.theme;

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.currentLanguage).toBe(initialLanguage);
      expect(result.current.theme).toBe(initialTheme);
    });

    it('should not affect other state when changing language', () => {
      const { result } = renderHook(() => useAppStore());

      const initialSidebarOpen = result.current.sidebarOpen;
      const initialTheme = result.current.theme;

      act(() => {
        result.current.setLanguage('fr');
      });

      expect(result.current.sidebarOpen).toBe(initialSidebarOpen);
      expect(result.current.theme).toBe(initialTheme);
    });

    it('should not affect other state when changing theme', () => {
      const { result } = renderHook(() => useAppStore());

      const initialSidebarOpen = result.current.sidebarOpen;
      const initialLanguage = result.current.currentLanguage;

      act(() => {
        result.current.setTheme('dark');
      });

      expect(result.current.sidebarOpen).toBe(initialSidebarOpen);
      expect(result.current.currentLanguage).toBe(initialLanguage);
    });
  });

  describe('multiple actions', () => {
    it('should handle multiple simultaneous state changes', () => {
      const { result } = renderHook(() => useAppStore());

      act(() => {
        result.current.toggleSidebar();
        result.current.setLanguage('fr');
        result.current.setTheme('dark');
      });

      expect(result.current.sidebarOpen).toBe(false);
      expect(result.current.currentLanguage).toBe('fr');
      expect(result.current.theme).toBe('dark');
    });
  });

  describe('store persistence across multiple hook instances', () => {
    it('should share state between multiple hook instances', () => {
      const { result: result1 } = renderHook(() => useAppStore());
      const { result: result2 } = renderHook(() => useAppStore());

      act(() => {
        result1.current.toggleSidebar();
      });

      expect(result1.current.sidebarOpen).toBe(result2.current.sidebarOpen);
      expect(result2.current.sidebarOpen).toBe(false);
    });

    it('should update all hook instances when state changes', () => {
      const { result: result1 } = renderHook(() => useAppStore());
      const { result: result2 } = renderHook(() => useAppStore());

      act(() => {
        result1.current.setLanguage('fr');
        result2.current.setTheme('dark');
      });

      expect(result1.current.currentLanguage).toBe('fr');
      expect(result2.current.currentLanguage).toBe('fr');
      expect(result1.current.theme).toBe('dark');
      expect(result2.current.theme).toBe('dark');
    });
  });
});
