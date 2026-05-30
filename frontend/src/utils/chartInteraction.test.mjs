import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { enhanceChartOption } from './chartInteraction.js'

describe('enhanceChartOption', () => {
  it('adds inside zoom, slider zoom, and toolbox controls to axis charts', () => {
    const option = {
      xAxis: { type: 'category' },
      yAxis: { type: 'value' },
      series: [{ type: 'line', data: [1, 2, 3] }],
    }

    const enhanced = enhanceChartOption(option)

    assert.equal(enhanced.dataZoom.length, 2)
    assert.equal(enhanced.dataZoom[0].type, 'inside')
    assert.equal(enhanced.dataZoom[1].type, 'slider')
    assert.deepEqual(enhanced.toolbox.feature.restore, { show: true, title: '还原' })
    assert.equal(enhanced.toolbox.feature.saveAsImage.show, true)
    assert.equal(enhanced.toolbox.feature.dataZoom.show, true)
    assert.equal(enhanced.grid.bottom, 72)
  })

  it('does not add zoom controls to pie charts without axes', () => {
    const option = {
      series: [{ type: 'pie', data: [{ name: 'A', value: 1 }] }],
    }

    const enhanced = enhanceChartOption(option)

    assert.equal(enhanced, option)
  })

  it('keeps existing zoom configuration and only adds missing controls', () => {
    const option = {
      xAxis: {},
      yAxis: {},
      dataZoom: [{ type: 'slider', start: 20, end: 80 }],
      toolbox: { feature: { saveAsImage: { show: false } } },
      series: [{ type: 'bar', data: [1, 2, 3] }],
    }

    const enhanced = enhanceChartOption(option)

    assert.equal(enhanced.dataZoom.length, 2)
    assert.deepEqual(enhanced.dataZoom[0], { type: 'slider', start: 20, end: 80 })
    assert.equal(enhanced.dataZoom[1].type, 'inside')
    assert.equal(enhanced.toolbox.feature.saveAsImage.show, false)
  })
})
