function toArray(value) {
  if (value === undefined || value === null) return []
  return Array.isArray(value) ? value : [value]
}

function axisIndexes(axis) {
  return toArray(axis).map((_, index) => index)
}

function hasZoomFor(zooms, type, axisKey) {
  return zooms.some((zoom) => (
    zoom?.type === type
    && (zoom[axisKey] !== undefined || (zoom.xAxisIndex === undefined && zoom.yAxisIndex === undefined))
  ))
}

function mergeFeature(existingFeature, defaultFeature) {
  return {
    ...defaultFeature,
    ...(existingFeature || {}),
  }
}

function withInteractiveGrid(grid) {
  const defaults = {
    left: 48,
    right: 38,
    top: 56,
    bottom: 72,
    containLabel: true,
  }

  if (Array.isArray(grid)) {
    return grid.map((item) => ({
      ...defaults,
      ...(item || {}),
      bottom: item?.bottom ?? defaults.bottom,
      right: item?.right ?? defaults.right,
      containLabel: item?.containLabel ?? defaults.containLabel,
    }))
  }

  if (grid && typeof grid === 'object') {
    return {
      ...defaults,
      ...grid,
      bottom: grid.bottom ?? defaults.bottom,
      right: grid.right ?? defaults.right,
      containLabel: grid.containLabel ?? defaults.containLabel,
    }
  }

  return defaults
}

function withInteractiveToolbox(toolbox, canZoomY) {
  const existingFeature = toolbox?.feature || {}
  const defaultDataZoom = {
    show: true,
    title: {
      zoom: '区域缩放',
      back: '缩放还原',
    },
  }

  if (!canZoomY) {
    defaultDataZoom.yAxisIndex = 'none'
  }

  return {
    show: true,
    right: 12,
    top: 8,
    itemSize: 16,
    itemGap: 10,
    ...(toolbox || {}),
    feature: {
      ...existingFeature,
      dataZoom: mergeFeature(existingFeature.dataZoom, defaultDataZoom),
      restore: mergeFeature(existingFeature.restore, { show: true, title: '还原' }),
      saveAsImage: mergeFeature(existingFeature.saveAsImage, {
        show: true,
        title: '保存图片',
        pixelRatio: 2,
        backgroundColor: '#ffffff',
      }),
    },
  }
}

function withInteractiveZoom(option, canZoomY) {
  const existingZooms = toArray(option.dataZoom)
  const nextZooms = [...existingZooms]
  const xIndexes = axisIndexes(option.xAxis)
  const yIndexes = axisIndexes(option.yAxis)

  if (xIndexes.length && !hasZoomFor(existingZooms, 'inside', 'xAxisIndex')) {
    nextZooms.push({
      type: 'inside',
      xAxisIndex: xIndexes,
      filterMode: 'filter',
      zoomOnMouseWheel: true,
      moveOnMouseMove: true,
      moveOnMouseWheel: true,
      start: 0,
      end: 100,
    })
  }

  if (xIndexes.length && !hasZoomFor(existingZooms, 'slider', 'xAxisIndex')) {
    nextZooms.push({
      type: 'slider',
      xAxisIndex: xIndexes,
      filterMode: 'filter',
      bottom: 18,
      height: 24,
      start: 0,
      end: 100,
      brushSelect: true,
      showDataShadow: false,
    })
  }

  if (canZoomY && yIndexes.length && !hasZoomFor(existingZooms, 'inside', 'yAxisIndex')) {
    nextZooms.push({
      type: 'inside',
      yAxisIndex: yIndexes,
      filterMode: 'empty',
      zoomOnMouseWheel: true,
      moveOnMouseMove: true,
      start: 0,
      end: 100,
    })
  }

  return nextZooms
}

export function enhanceChartOption(option) {
  if (!option || typeof option !== 'object') return option

  const series = toArray(option.series)
  const hasAxis = option.xAxis !== undefined || option.yAxis !== undefined
  const hasCoordinateSeries = series.some((item) => item?.type !== 'pie')

  if (!hasAxis || !hasCoordinateSeries) return option

  const seriesTypes = new Set(series.map((item) => item?.type).filter(Boolean))
  const canZoomY = seriesTypes.has('scatter') || seriesTypes.has('heatmap')

  return {
    ...option,
    grid: withInteractiveGrid(option.grid),
    toolbox: withInteractiveToolbox(option.toolbox, canZoomY),
    dataZoom: withInteractiveZoom(option, canZoomY),
  }
}
