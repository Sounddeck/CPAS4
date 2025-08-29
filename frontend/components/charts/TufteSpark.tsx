
/**
 * Tufte-Style Sparkline Component
 * Implements Edward Tufte's principles for elegant data visualization
 */

import React, { useMemo } from 'react';

interface TufteSparkProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  strokeWidth?: number;
  showDots?: boolean;
  showMinMax?: boolean;
  showLast?: boolean;
  className?: string;
}

export const TufteSpark: React.FC<TufteSparkProps> = ({
  data,
  width = 200,
  height = 40,
  color = '#3B82F6',
  strokeWidth = 1.5,
  showDots = false,
  showMinMax = false,
  showLast = true,
  className = ''
}) => {
  const { pathData, minPoint, maxPoint, lastPoint, minValue, maxValue } = useMemo(() => {
    if (!data || data.length === 0) {
      return { pathData: '', minPoint: null, maxPoint: null, lastPoint: null, minValue: 0, maxValue: 0 };
    }

    const minValue = Math.min(...data);
    const maxValue = Math.max(...data);
    const range = maxValue - minValue || 1;

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - minValue) / range) * height;
      return { x, y, value, index };
    });

    const pathData = points
      .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
      .join(' ');

    const minPoint = points.find(p => p.value === minValue);
    const maxPoint = points.find(p => p.value === maxValue);
    const lastPoint = points[points.length - 1];

    return { pathData, minPoint, maxPoint, lastPoint, minValue, maxValue };
  }, [data, width, height]);

  if (!data || data.length === 0) {
    return (
      <div 
        className={`flex items-center justify-center text-gray-400 ${className}`}
        style={{ width, height }}
      >
        <span className="text-xs">No data</span>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`} style={{ width, height }}>
      <svg
        width={width}
        height={height}
        className="overflow-visible"
        style={{ filter: 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))' }}
      >
        {/* Main sparkline */}
        <path
          d={pathData}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
          className="transition-all duration-300"
        />

        {/* Fill area (subtle) */}
        <path
          d={`${pathData} L ${width} ${height} L 0 ${height} Z`}
          fill={color}
          fillOpacity={0.1}
          className="transition-all duration-300"
        />

        {/* Data points */}
        {showDots && data.map((value, index) => {
          const x = (index / (data.length - 1)) * width;
          const y = height - ((value - minValue) / (maxValue - minValue || 1)) * height;
          
          return (
            <circle
              key={index}
              cx={x}
              cy={y}
              r={1}
              fill={color}
              className="transition-all duration-300"
            />
          );
        })}

        {/* Min/Max indicators */}
        {showMinMax && minPoint && maxPoint && minValue !== maxValue && (
          <>
            {/* Min point */}
            <circle
              cx={minPoint.x}
              cy={minPoint.y}
              r={2}
              fill="#EF4444"
              stroke="white"
              strokeWidth={1}
            />
            
            {/* Max point */}
            <circle
              cx={maxPoint.x}
              cy={maxPoint.y}
              r={2}
              fill="#10B981"
              stroke="white"
              strokeWidth={1}
            />
          </>
        )}

        {/* Last value indicator */}
        {showLast && lastPoint && (
          <circle
            cx={lastPoint.x}
            cy={lastPoint.y}
            r={2}
            fill={color}
            stroke="white"
            strokeWidth={1}
            className="transition-all duration-300"
          />
        )}
      </svg>

      {/* Value labels (Tufte style - minimal) */}
      {showMinMax && minValue !== maxValue && (
        <>
          {minPoint && (
            <div
              className="absolute text-xs text-red-600 font-mono"
              style={{
                left: minPoint.x - 10,
                top: minPoint.y + 8,
                fontSize: '10px'
              }}
            >
              {minValue.toFixed(0)}
            </div>
          )}
          {maxPoint && (
            <div
              className="absolute text-xs text-green-600 font-mono"
              style={{
                left: maxPoint.x - 10,
                top: maxPoint.y - 16,
                fontSize: '10px'
              }}
            >
              {maxValue.toFixed(0)}
            </div>
          )}
        </>
      )}

      {/* Last value */}
      {showLast && lastPoint && (
        <div
          className="absolute text-xs text-gray-700 dark:text-gray-300 font-mono font-semibold"
          style={{
            left: lastPoint.x + 8,
            top: lastPoint.y - 6,
            fontSize: '11px'
          }}
        >
          {lastPoint.value.toFixed(1)}
        </div>
      )}
    </div>
  );
};

// Multi-series sparkline for comparative analysis
interface TufteMultiSparkProps {
  series: Array<{
    name: string;
    data: number[];
    color: string;
  }>;
  width?: number;
  height?: number;
  className?: string;
}

export const TufteMultiSpark: React.FC<TufteMultiSparkProps> = ({
  series,
  width = 200,
  height = 40,
  className = ''
}) => {
  const { globalMin, globalMax } = useMemo(() => {
    const allValues = series.flatMap(s => s.data);
    return {
      globalMin: Math.min(...allValues),
      globalMax: Math.max(...allValues)
    };
  }, [series]);

  return (
    <div className={`relative ${className}`} style={{ width, height }}>
      <svg width={width} height={height} className="overflow-visible">
        {series.map((serie, serieIndex) => {
          const pathData = serie.data
            .map((value, index) => {
              const x = (index / (serie.data.length - 1)) * width;
              const y = height - ((value - globalMin) / (globalMax - globalMin || 1)) * height;
              return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
            })
            .join(' ');

          return (
            <g key={serieIndex}>
              <path
                d={pathData}
                fill="none"
                stroke={serie.color}
                strokeWidth={1.5}
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeOpacity={0.8}
                className="transition-all duration-300"
              />
              
              {/* Last point */}
              {serie.data.length > 0 && (
                <circle
                  cx={(serie.data.length - 1) / (serie.data.length - 1) * width}
                  cy={height - ((serie.data[serie.data.length - 1] - globalMin) / (globalMax - globalMin || 1)) * height}
                  r={1.5}
                  fill={serie.color}
                  className="transition-all duration-300"
                />
              )}
            </g>
          );
        })}
      </svg>
      
      {/* Legend */}
      <div className="absolute -bottom-6 left-0 flex space-x-4">
        {series.map((serie, index) => (
          <div key={index} className="flex items-center space-x-1">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: serie.color }}
            />
            <span className="text-xs text-gray-600 dark:text-gray-400">
              {serie.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Small multiples component for comparative analysis
interface TufteSmallMultiplesProps {
  datasets: Array<{
    title: string;
    data: number[];
    color?: string;
  }>;
  width?: number;
  height?: number;
  columns?: number;
  className?: string;
}

export const TufteSmallMultiples: React.FC<TufteSmallMultiplesProps> = ({
  datasets,
  width = 120,
  height = 60,
  columns = 3,
  className = ''
}) => {
  return (
    <div className={`grid gap-4 ${className}`} style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
      {datasets.map((dataset, index) => (
        <div key={index} className="text-center">
          <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
            {dataset.title}
          </div>
          <TufteSpark
            data={dataset.data}
            width={width}
            height={height}
            color={dataset.color || '#3B82F6'}
            showLast={true}
            showMinMax={false}
          />
        </div>
      ))}
    </div>
  );
};
