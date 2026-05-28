def build_echarts_option(chart_type, data, config):
    """根据图表类型和数据生成 ECharts option JSON"""
    title = config.get('title', '')
    x_column = config.get('x_column', 'X')
    y_column = config.get('y_column', 'Y')
    color = config.get('color', '#5470c6')

    builders = {
        'scatter': _build_scatter,
        'line': _build_line,
        'bar': _build_bar,
        'heatmap': _build_heatmap,
        'boxplot': _build_boxplot,
        'pie': _build_pie,
    }

    builder = builders.get(chart_type)
    if builder is None:
        raise ValueError(f'不支持的图表类型: {chart_type}')

    option = builder(data, title, x_column, y_column, color)
    option['tooltip'] = {'trigger': 'item' if chart_type == 'pie' else 'axis'}
    option['animation'] = True

    return option


def _build_scatter(data, title, x_column, y_column, color):
    points = data.get('points', [])
    series_data = [[p[0], p[1]] for p in points]
    return {
        'title': {'text': title, 'left': 'center'},
        'xAxis': {'name': x_column, 'type': 'value'},
        'yAxis': {'name': y_column, 'type': 'value'},
        'series': [{
            'type': 'scatter',
            'data': series_data,
            'itemStyle': {'color': color},
            'symbolSize': 8,
        }],
    }


def _build_line(data, title, x_column, y_column, color):
    values = data.get('values', [])
    labels = data.get('labels', [])
    if labels and len(labels) == len(values):
        series_data = [[labels[i], v] for i, v in enumerate(values)]
    else:
        series_data = [[i, v] for i, v in enumerate(values)]
    return {
        'title': {'text': title, 'left': 'center'},
        'xAxis': {'name': x_column, 'type': 'value'},
        'yAxis': {'name': y_column, 'type': 'value'},
        'series': [{
            'type': 'line',
            'data': series_data,
            'lineStyle': {'color': color},
            'itemStyle': {'color': color},
            'smooth': True,
        }],
    }


def _build_bar(data, title, x_column, y_column, color):
    labels = data.get('labels', [])
    values = data.get('values', [])
    return {
        'title': {'text': title, 'left': 'center'},
        'xAxis': {
            'name': x_column,
            'type': 'category',
            'data': [str(l) for l in labels],
            'axisLabel': {'rotate': 30},
        },
        'yAxis': {'name': y_column, 'type': 'value'},
        'series': [{
            'type': 'bar',
            'data': values,
            'itemStyle': {'color': color},
        }],
    }


def _build_heatmap(data, title, x_column, y_column, color):
    matrix = data.get('matrix', [])
    # matrix: [[x_idx, y_idx, val], ...]
    if len(matrix) == 0:
        return {
            'title': {'text': title, 'left': 'center'},
            'xAxis': {'type': 'category', 'data': []},
            'yAxis': {'type': 'category', 'data': []},
            'series': [{'type': 'heatmap', 'data': []}],
        }

    x_indices = sorted(set(int(m[0]) for m in matrix))
    y_indices = sorted(set(int(m[1]) for m in matrix))
    x_labels = [str(i) for i in x_indices]
    y_labels = [str(i) for i in y_indices]

    max_val = max(abs(m[2]) for m in matrix) if matrix else 1

    return {
        'title': {'text': title, 'left': 'center'},
        'xAxis': {'name': x_column, 'type': 'category', 'data': x_labels, 'splitArea': {'show': True}},
        'yAxis': {'name': y_column, 'type': 'category', 'data': y_labels, 'splitArea': {'show': True}},
        'visualMap': {
            'min': -max_val,
            'max': max_val,
            'calculable': True,
            'orient': 'horizontal',
            'left': 'center',
            'bottom': 0,
        },
        'series': [{
            'type': 'heatmap',
            'data': matrix,
            'label': {'show': False},
        }],
    }


def _build_boxplot(data, title, x_column, y_column, color):
    box_data = data.get('box_data', [])
    if not box_data:
        return {
            'title': {'text': title, 'left': 'center'},
            'xAxis': {'type': 'category', 'data': []},
            'yAxis': {'type': 'value'},
            'series': [{'type': 'boxplot', 'data': []}],
        }

    x_labels = [str(i) for i in range(len(box_data))]
    series_data = []
    for bd in box_data:
        if isinstance(bd, dict):
            series_data.append([
                bd.get('min', 0), bd.get('Q1', 0), bd.get('median', 0),
                bd.get('Q3', 0), bd.get('max', 0),
            ])
        elif isinstance(bd, (list, tuple)):
            series_data.append(list(bd[:5]))

    return {
        'title': {'text': title, 'left': 'center'},
        'xAxis': {'name': x_column, 'type': 'category', 'data': x_labels},
        'yAxis': {'name': y_column, 'type': 'value'},
        'series': [{
            'type': 'boxplot',
            'data': series_data,
            'itemStyle': {'color': color, 'borderColor': color},
        }],
    }


def _build_pie(data, title, x_column, y_column, color):
    items = data.get('items', [])
    series_data = [{'name': str(it.get('name', '')), 'value': it.get('value', 0)} for it in items]

    colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272',
              '#fc8452', '#9a60b4', '#ea7ccc', '#546570']

    return {
        'title': {'text': title, 'left': 'center'},
        'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
        'series': [{
            'type': 'pie',
            'data': series_data,
            'radius': ['30%', '70%'],
            'center': ['50%', '55%'],
            'itemStyle': {
                'borderRadius': 4,
                'borderColor': '#fff',
                'borderWidth': 2,
            },
            'label': {'show': True, 'formatter': '{b}: {d}%'},
            'emphasis': {
                'label': {'show': True, 'fontSize': 16, 'fontWeight': 'bold'},
                'itemStyle': {'shadowBlur': 10, 'shadowOffsetX': 0, 'shadowColor': 'rgba(0, 0, 0, 0.5)'},
            },
        }],
    }
