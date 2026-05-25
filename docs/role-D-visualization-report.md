# 角色 D 实验报告：可视化、历史与部署

## 实现内容

本次完成角色 D 的前端可视化模块，实现了图表渲染、图表配置、分析历史查看和前端静态资源部署。

- `frontend/src/components/ChartPanel.vue`：封装 ECharts 渲染容器，支持散点图、折线图、柱状图、热力图、箱线图和饼图，并处理窗口尺寸变化与组件销毁。
- `frontend/src/components/ChartConfig.vue`：提供图表类型、X/Y 字段、标题和颜色配置，点击生成后向父页面提交配置。
- `frontend/src/stores/chart.js`：新增 Pinia store，维护当前图表 option、历史图表配置、分析任务列表和当前任务，并封装图表生成与历史任务接口。
- `frontend/src/views/VisualizeView.vue`：展示当前分析任务摘要、参数与指标，根据任务结果构造图表数据并调用图表生成接口渲染。
- `frontend/src/views/HistoryView.vue`：调用分析任务历史接口展示任务类型、参数、指标、状态和时间，支持跳转到可视化页面。

## 接口对接

前端通过统一 `api` 实例访问后端。

- 分析历史：`GET /api/analysis/tasks/`
- 分析详情：`GET /api/analysis/tasks/{id}/`
- 图表生成：优先请求 `POST /api/charts/generate/`，若返回 404，则回退到 `POST /api/analysis/charts/generate/`
- 图表配置：优先请求 `GET /api/charts/configs/`，若返回 404，则回退到 `GET /api/analysis/charts/configs/`

加入回退逻辑是为了兼容计划中图表接口路径与现有 Django `api/analysis/` 挂载方式之间的不一致。

## 部署验证

已完成前端构建、静态资源复制和 Django 静态资源收集。

```bash
cd frontend
npm run build
```

构建成功后，将 `frontend/dist` 内容复制到 `backend/static`，再执行：

```bash
cd backend
py -3.13 manage.py collectstatic --noinput
```

`collectstatic` 已成功复制静态资源到 `backend/staticfiles`。

## 注意事项

角色 D 需要 ECharts 渲染图表，因此新增了前端依赖 `echarts`。当前后端分析 API 仍依赖角色 E 的接口实现，若接口未合入，可视化页面会显示接口错误状态。
