/**
 * 网络拓扑组件
 */

import React, { useEffect, useRef, useCallback } from 'react';
import { NetworkData, NetworkNode, themeManager } from '@stork-viz/core';

interface StorkNetworkTopologyProps {
  data: NetworkData;
  width?: number;
  height?: number;
  onNodeClick?: (node: NetworkNode) => void;
}

export const StorkNetworkTopology: React.FC<StorkNetworkTopologyProps> = ({
  data,
  width = 800,
  height = 600,
  onNodeClick
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const theme = themeManager.getCurrentTheme();

    // 清空画布
    ctx.fillStyle = theme.colors.background;
    ctx.fillRect(0, 0, width, height);

    // 绘制连接线
    ctx.strokeStyle = theme.colors.border;
    ctx.lineWidth = 1;
    data.edges.forEach(edge => {
      const source = data.nodes.find(n => n.id === edge.source);
      const target = data.nodes.find(n => n.id === edge.target);
      if (source && target) {
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();
      }
    });

    // 绘制节点
    data.nodes.forEach(node => {
      // 节点圆形
      ctx.beginPath();
      ctx.arc(node.x, node.y, 20, 0, Math.PI * 2);
      
      // 根据状态设置颜色
      switch (node.status) {
        case 'online':
          ctx.fillStyle = theme.colors.success;
          break;
        case 'busy':
          ctx.fillStyle = theme.colors.warning;
          break;
        default:
          ctx.fillStyle = theme.colors.error;
      }
      ctx.fill();

      // 节点边框
      ctx.strokeStyle = theme.colors.text;
      ctx.lineWidth = 2;
      ctx.stroke();

      // 节点标签
      ctx.fillStyle = theme.colors.text;
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(node.label, node.x, node.y + 35);
    });
  }, [data, width, height]);

  useEffect(() => {
    const animate = () => {
      draw();
      animationRef.current = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [draw]);

  const handleClick = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !onNodeClick) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // 检查点击的节点
    const clickedNode = data.nodes.find(node => {
      const dx = node.x - x;
      const dy = node.y - y;
      return Math.sqrt(dx * dx + dy * dy) <= 20;
    });

    if (clickedNode) {
      onNodeClick(clickedNode);
    }
  }, [data.nodes, onNodeClick]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      onClick={handleClick}
      style={{ cursor: 'pointer' }}
    />
  );
};
