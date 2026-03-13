/**
 * 主题管理器
 */

import { Theme } from './types';

export class ThemeManager {
  private static instance: ThemeManager;
  private currentTheme: Theme;
  private listeners: Set<(theme: Theme) => void> = new Set();

  // 内置主题
  private themes: Map<string, Theme> = new Map([
    ['dark', {
      name: 'dark',
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
        background: '#0f172a',
        surface: '#1e293b',
        text: '#f8fafc',
        textSecondary: '#94a3b8',
        border: '#334155',
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6'
      }
    }],
    ['light', {
      name: 'light',
      colors: {
        primary: '#2563eb',
        secondary: '#7c3aed',
        background: '#ffffff',
        surface: '#f1f5f9',
        text: '#0f172a',
        textSecondary: '#64748b',
        border: '#e2e8f0',
        success: '#16a34a',
        warning: '#d97706',
        error: '#dc2626',
        info: '#2563eb'
      }
    }]
  ]);

  private constructor() {
    this.currentTheme = this.themes.get('dark')!;
  }

  static getInstance(): ThemeManager {
    if (!ThemeManager.instance) {
      ThemeManager.instance = new ThemeManager();
    }
    return ThemeManager.instance;
  }

  getTheme(name: string): Theme | undefined {
    return this.themes.get(name);
  }

  setTheme(name: string): void {
    const theme = this.themes.get(name);
    if (theme) {
      this.currentTheme = theme;
      this.notifyListeners();
    }
  }

  getCurrentTheme(): Theme {
    return this.currentTheme;
  }

  addListener(callback: (theme: Theme) => void): void {
    this.listeners.add(callback);
  }

  removeListener(callback: (theme: Theme) => void): void {
    this.listeners.delete(callback);
  }

  private notifyListeners(): void {
    this.listeners.forEach(callback => callback(this.currentTheme));
  }

  getAllThemes(): Theme[] {
    return Array.from(this.themes.values());
  }
}

export const themeManager = ThemeManager.getInstance();
