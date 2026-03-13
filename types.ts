/**
 * 类型定义
 */

export interface Theme {
  name: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    success: string;
    warning: string;
    error: string;
    info: string;
  };
}

export interface NetworkNode {
  id: string;
  x: number;
  y: number;
  label: string;
  status: 'online' | 'offline' | 'busy';
  type?: string;
}

export interface NetworkEdge {
  source: string;
  target: string;
  strength: 'strong' | 'medium' | 'weak';
}

export interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}
