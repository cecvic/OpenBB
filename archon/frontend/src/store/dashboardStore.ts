import { create } from 'zustand';
import { v4 as uuid } from 'uuid';
import type { WidgetData, WidgetLayout, WidgetType, DashboardState } from './types';

interface ArtifactData {
  type: 'table' | 'chart' | 'text';
  name: string;
  description?: string;
  data: unknown;
}

interface DashboardActions {
  addWidget: (type: WidgetType, title: string) => string;
  addWidgetFromArtifact: (artifact: ArtifactData) => string;
  removeWidget: (id: string) => void;
  updateWidgetData: (id: string, data: unknown) => void;
  updateWidgetLoading: (id: string, loading: boolean) => void;
  updateWidgetError: (id: string, error: string | null) => void;
  updateWidgetParameter: (id: string, paramName: string, value: string | number) => void;
  setGlobalTicker: (ticker: string) => void;
  updateLayouts: (layouts: WidgetLayout[]) => void;
  toggleEditMode: () => void;
  getWidgetContext: () => WidgetContextItem[];
}

export interface WidgetContextItem {
  id: string;
  type: WidgetType;
  title: string;
  parameters: Record<string, unknown>;
  dataSummary: string;
}

const defaultLayouts: WidgetLayout[] = [];

const getDefaultWidget = (type: WidgetType, title: string): Omit<WidgetData, 'id'> => {
  const baseParams = {
    ticker: { name: 'ticker', type: 'string' as const, value: 'NVDA', linked: true },
  };

  switch (type) {
    case 'agent-analysis':
      return {
        type,
        title,
        description: 'AI agent analysis with glass-box reasoning',
        parameters: { ...baseParams },
        data: null,
        loading: false,
        error: null,
        lastUpdated: null,
      };
    case 'price-chart':
      return {
        type,
        title,
        description: 'Historical price chart',
        parameters: {
          ...baseParams,
          period: { name: 'period', type: 'select', value: '1M', options: ['1D', '1W', '1M', '3M', '1Y'] },
        },
        data: null,
        loading: false,
        error: null,
        lastUpdated: null,
      };
    case 'data-table':
      return {
        type,
        title,
        description: 'Financial data table',
        parameters: { ...baseParams },
        data: null,
        loading: false,
        error: null,
        lastUpdated: null,
      };
    case 'news-feed':
      return {
        type,
        title,
        description: 'Latest news and sentiment',
        parameters: { ...baseParams },
        data: null,
        loading: false,
        error: null,
        lastUpdated: null,
      };
    case 'metrics':
      return {
        type,
        title,
        description: 'Key financial metrics',
        parameters: { ...baseParams },
        data: null,
        loading: false,
        error: null,
        lastUpdated: null,
      };
    case 'consensus':
      return {
        type,
        title,
        description: 'Multi-agent consensus view',
        parameters: { ...baseParams },
        data: null,
        loading: false,
        error: null,
        lastUpdated: null,
      };
    default:
      return {
        type,
        title,
        parameters: baseParams,
        data: null,
        loading: false,
        error: null,
        lastUpdated: null,
      };
  }
};

const GRID_COLS = 3;

const widgetSizes: Record<WidgetType, { w: number; h: number }> = {
  'agent-analysis': { w: 1, h: 2 },
  'price-chart': { w: 2, h: 2 },
  'data-table': { w: 1, h: 2 },
  'news-feed': { w: 1, h: 2 },
  'metrics': { w: 1, h: 1 },
  'consensus': { w: 3, h: 2 },
};

const findNextAvailablePosition = (
  existingLayouts: WidgetLayout[],
  width: number,
  height: number
): { x: number; y: number } => {
  if (existingLayouts.length === 0) {
    return { x: 0, y: 0 };
  }

  // Build a grid map of occupied cells
  const maxY = Math.max(...existingLayouts.map(l => l.y + l.h), 0);
  const gridHeight = maxY + height + 10; // Extra buffer for new widget
  const grid: boolean[][] = Array.from({ length: gridHeight }, () =>
    Array(GRID_COLS).fill(false)
  );

  // Mark occupied cells
  for (const layout of existingLayouts) {
    for (let row = layout.y; row < layout.y + layout.h; row++) {
      for (let col = layout.x; col < layout.x + layout.w; col++) {
        if (row < gridHeight && col < GRID_COLS) {
          grid[row][col] = true;
        }
      }
    }
  }

  // Find first position where widget fits (scan row by row, left to right)
  for (let y = 0; y < gridHeight; y++) {
    for (let x = 0; x <= GRID_COLS - width; x++) {
      let fits = true;

      // Check if all required cells are free
      for (let dy = 0; dy < height && fits; dy++) {
        for (let dx = 0; dx < width && fits; dx++) {
          if (y + dy >= gridHeight || grid[y + dy][x + dx]) {
            fits = false;
          }
        }
      }

      if (fits) {
        return { x, y };
      }
    }
  }

  // Fallback: place at bottom
  return { x: 0, y: maxY };
};

const getDefaultLayoutForType = (
  type: WidgetType,
  id: string,
  existingLayouts: WidgetLayout[]
): WidgetLayout => {
  const size = widgetSizes[type] || { w: 1, h: 1 };
  const position = findNextAvailablePosition(existingLayouts, size.w, size.h);

  return {
    i: id,
    x: position.x,
    y: position.y,
    w: size.w,
    h: size.h,
    minW: 1,
    minH: 1,
  };
};

export const useDashboardStore = create<DashboardState & DashboardActions>((set, get) => ({
  widgets: {},
  layouts: defaultLayouts,
  globalTicker: 'NVDA',
  isEditMode: false,

  addWidget: (type, title) => {
    const id = uuid();
    const widget: WidgetData = {
      id,
      ...getDefaultWidget(type, title),
    };

    const layout = getDefaultLayoutForType(type, id, get().layouts);

    set((state) => ({
      widgets: { ...state.widgets, [id]: widget },
      layouts: [...state.layouts, layout],
    }));

    return id;
  },

  addWidgetFromArtifact: (artifact) => {
    const id = uuid();
    const widgetType: WidgetType = artifact.type === 'table' ? 'data-table' :
                                    artifact.type === 'chart' ? 'price-chart' : 'data-table';

    const widget: WidgetData = {
      id,
      type: widgetType,
      title: artifact.name,
      description: artifact.description,
      parameters: {
        ticker: { name: 'ticker', type: 'string', value: get().globalTicker, linked: false },
      },
      data: artifact.data,
      loading: false,
      error: null,
      lastUpdated: new Date().toISOString(),
    };

    const layout = getDefaultLayoutForType(widgetType, id, get().layouts);

    set((state) => ({
      widgets: { ...state.widgets, [id]: widget },
      layouts: [...state.layouts, layout],
    }));

    return id;
  },

  removeWidget: (id) => {
    set((state) => {
      const { [id]: _, ...remainingWidgets } = state.widgets;
      return {
        widgets: remainingWidgets,
        layouts: state.layouts.filter((l) => l.i !== id),
      };
    });
  },

  updateWidgetData: (id, data) => {
    set((state) => ({
      widgets: {
        ...state.widgets,
        [id]: {
          ...state.widgets[id],
          data,
          lastUpdated: new Date().toISOString(),
        },
      },
    }));
  },

  updateWidgetLoading: (id, loading) => {
    set((state) => ({
      widgets: {
        ...state.widgets,
        [id]: { ...state.widgets[id], loading },
      },
    }));
  },

  updateWidgetError: (id, error) => {
    set((state) => ({
      widgets: {
        ...state.widgets,
        [id]: { ...state.widgets[id], error, loading: false },
      },
    }));
  },

  updateWidgetParameter: (id, paramName, value) => {
    const state = get();
    const widget = state.widgets[id];
    if (!widget) return;

    const param = widget.parameters[paramName];
    if (!param) return;

    if (param.linked && paramName === 'ticker') {
      set({ globalTicker: value as string });
      Object.keys(state.widgets).forEach((wid) => {
        const w = state.widgets[wid];
        if (w.parameters.ticker?.linked) {
          set((s) => ({
            widgets: {
              ...s.widgets,
              [wid]: {
                ...s.widgets[wid],
                parameters: {
                  ...s.widgets[wid].parameters,
                  ticker: { ...s.widgets[wid].parameters.ticker, value },
                },
              },
            },
          }));
        }
      });
    } else {
      set((s) => ({
        widgets: {
          ...s.widgets,
          [id]: {
            ...s.widgets[id],
            parameters: {
              ...s.widgets[id].parameters,
              [paramName]: { ...param, value },
            },
          },
        },
      }));
    }
  },

  setGlobalTicker: (ticker) => {
    const state = get();
    set({ globalTicker: ticker });
    
    Object.keys(state.widgets).forEach((id) => {
      const widget = state.widgets[id];
      if (widget.parameters.ticker?.linked) {
        set((s) => ({
          widgets: {
            ...s.widgets,
            [id]: {
              ...s.widgets[id],
              parameters: {
                ...s.widgets[id].parameters,
                ticker: { ...s.widgets[id].parameters.ticker, value: ticker },
              },
            },
          },
        }));
      }
    });
  },

  updateLayouts: (layouts) => {
    set({ layouts });
  },

  toggleEditMode: () => {
    set((state) => ({ isEditMode: !state.isEditMode }));
  },

  getWidgetContext: () => {
    const state = get();
    return Object.values(state.widgets).map((widget) => ({
      id: widget.id,
      type: widget.type,
      title: widget.title,
      parameters: Object.fromEntries(
        Object.entries(widget.parameters).map(([k, v]) => [k, v.value])
      ),
      dataSummary: widget.data 
        ? JSON.stringify(widget.data).slice(0, 500) 
        : 'No data loaded',
    }));
  },
}));
