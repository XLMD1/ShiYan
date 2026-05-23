# 交互式数据分析系统 — 设计规格说明

**日期：** 2026-05-23
**团队：** 4 人
**项目类型：** 课程实验（Python 数据分析系统开发）

---

## 1. 项目概述

开发一个基于 Web 的交互式数据分析系统，完整覆盖数据管道：上传 → 清洗 → 分析 → 可视化 → 导出。

### 1.1 核心目标
- 用户可通过 Web 页面上传 CSV/Excel 文件
- 系统自动检测缺失值和异常值，提供清洗选项
- 支持 K-Means 聚类和线性回归两种分析方法
- 动态生成 6 种以上可配置图表
- 多用户注册/登录，独立数据空间，历史记录可检索

---

## 2. 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 后端框架 | Django 5.x + Django REST Framework | 全栈框架，内置 ORM、认证、Admin |
| 前端框架 | Vue 3 + Vite + Pinia + Vue Router | SPA 单页应用 |
| 图表库 | ECharts 5.x | 中文本地化好，图表类型丰富 |
| 数据分析 | Pandas + scikit-learn | 数据清洗、K-Means、线性回归 |
| 认证 | djangorestframework-simplejwt | JWT Token 认证 |
| 数据库 | SQLite（开发）/ MySQL（可选扩展） | 教学场景 SQLite 足够 |
| 数据集 | Mall Customers + California Housing | 双数据集切换演示 |

---

## 3. 架构设计

### 3.1 前后端分离架构

```
┌─────────────┐     REST API (JSON)     ┌──────────────┐
│  Vue 3 SPA  │ ◄──────────────────────► │  Django DRF  │
│  (Port 5173 │    JWT Authentication    │  (Port 8000) │
│   dev mode) │                          │              │
└─────────────┘                          └──────┬───────┘
                                                │
                                    ┌───────────┴───────────┐
                                    │   Pandas / sklearn    │
                                    │   (数据分析引擎)       │
                                    └───────────────────────┘
```

- **开发阶段：** Vue dev server (5173) + Django (8000)，CORS 配置
- **部署阶段：** Vue build → Django static/，统一端口服务

### 3.2 数据流

```
用户上传文件 → 后端解析(Pandas) → 存为 Dataset 记录
       ↓
前端请求预览 → 后端分页返回 DataFrame 前 N 行
       ↓
用户触发清洗 → 后端执行缺失值/异常值处理 → 返回清洗报告
       ↓
用户选择算法+参数 → 后端执行 K-Means/回归 → 结果存 AnalysisTask
       ↓
前端配置图表 → 后端生成 ECharts option JSON → 前端渲染
       ↓
用户导出 → 后端生成 CSV/Excel 文件下载
```

---

## 4. 项目目录结构

```
project/
├── backend/                    # Django 后端
│   ├── config/                 # 项目配置
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/           # 用户模块
│   │   │   ├── models.py       # User 扩展（如有）
│   │   │   ├── views.py        # 注册/登录 API
│   │   │   └── serializers.py
│   │   ├── datafile/           # 数据文件管理（角色 B）
│   │   │   ├── models.py       # Dataset 模型
│   │   │   ├── views.py        # 上传/预览/导出 API
│   │   │   └── serializers.py
│   │   └── analysis/           # 清洗+分析引擎（角色 C）
│   │       ├── models.py       # AnalysisTask, ChartConfig
│   │       ├── views.py        # 清洗/分析/图表 API
│   │       ├── serializers.py
│   │       ├── cleaning.py     # 缺失值/异常值处理
│   │       ├── clustering.py   # K-Means
│   │       ├── regression.py   # 线性回归
│   │       └── visualization.py # 图表数据生成
│   ├── media/                  # 用户上传文件
│   ├── static/                 # Vue build 产物（部署时）
│   └── requirements.txt
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── UploadView.vue
│   │   │   ├── CleanView.vue
│   │   │   ├── AnalysisView.vue
│   │   │   ├── VisualizeView.vue
│   │   │   └── HistoryView.vue
│   │   ├── components/         # 可复用组件
│   │   │   ├── NavBar.vue
│   │   │   ├── FileUploader.vue
│   │   │   ├── DataTable.vue
│   │   │   ├── ChartPanel.vue
│   │   │   ├── ChartConfig.vue
│   │   │   ├── AnalysisParams.vue
│   │   │   └── StatsCard.vue
│   │   ├── router/index.js
│   │   ├── stores/             # Pinia
│   │   │   ├── auth.js
│   │   │   ├── dataset.js
│   │   │   ├── analysis.js
│   │   │   └── chart.js
│   │   └── api/                # Axios 封装
│   │       └── index.js
│   ├── package.json
│   └── vite.config.js
└── docs/
    └── superpowers/specs/      # 设计文档
```

---

## 5. 数据模型

### 5.1 Dataset（数据集）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | PK | 主键 |
| user | FK → User | 所属用户 |
| name | CharField | 数据集名称 |
| file | FileField | 上传的文件 |
| file_type | CharField | CSV / Excel |
| rows | IntegerField | 行数 |
| columns | JSONField | 列名列表 |
| uploaded_at | DateTimeField | 上传时间 |
| is_cleaned | BooleanField | 是否已清洗 |

### 5.2 AnalysisTask（分析任务）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | PK | 主键 |
| user | FK → User | 所属用户 |
| dataset | FK → Dataset | 关联数据集 |
| task_type | CharField | KMeans / Regression |
| parameters | JSONField | 算法参数（K值、特征列等） |
| result_data | JSONField | 分析结果数据 |
| metrics | JSONField | 评估指标（R², 轮廓系数等） |
| status | CharField | pending / running / done / error |
| created_at | DateTimeField | 创建时间 |

### 5.3 ChartConfig（图表配置）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | PK | 主键 |
| user | FK → User | 所属用户 |
| analysis_task | FK → AnalysisTask | 关联分析任务 |
| chart_type | CharField | scatter / line / bar / heatmap / boxplot / pie |
| x_column | CharField | X 轴字段 |
| y_column | CharField | Y 轴字段 |
| color_column | CharField | 颜色映射字段（可选） |
| title | CharField | 图表标题 |
| config | JSONField | ECharts 额外配置 |
| created_at | DateTimeField | 创建时间 |

---

## 6. API 设计

### 6.1 认证（accounts）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/auth/register/ | 注册 | 否 |
| POST | /api/auth/login/ | 登录，返回 JWT Token | 否 |
| GET | /api/auth/me/ | 当前用户信息 | 是 |

### 6.2 数据管理（datafile）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/datasets/upload/ | 上传文件 + 解析元信息 | 是 |
| GET | /api/datasets/ | 我的数据集列表 | 是 |
| GET | /api/datasets/{id}/ | 数据集详情 | 是 |
| GET | /api/datasets/{id}/preview/ | 前 100 行预览（支持分页） | 是 |
| DELETE | /api/datasets/{id}/ | 删除数据集 | 是 |

### 6.3 数据导出（datafile）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/datasets/{id}/export/ | 导出清洗后数据 | 是 |

### 6.4 数据清洗（analysis）

### 6.4 数据清洗（analysis）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/analysis/clean/{dataset_id}/ | 执行清洗，返回报告 | 是 |
| GET  | /api/analysis/stats/{dataset_id}/  | 数据概览：缺失值/异常值/分布 | 是 |

### 6.5 分析算法（analysis）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/analysis/kmeans/ | 执行 K-Means | 是 |
| POST | /api/analysis/regression/ | 执行线性回归 | 是 |
| GET | /api/analysis/tasks/ | 分析历史记录 | 是 |
| GET | /api/analysis/tasks/{id}/ | 单次分析详情+结果 | 是 |

### 6.6 可视化（analysis/charts）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/charts/generate/ | 按配置生成图表 JSON | 是 |
| GET | /api/charts/configs/ | 用户保存的图表配置 | 是 |

---

## 7. 前端设计

### 7.1 路由表
| 路径 | 组件 | 说明 |
|------|------|------|
| /login | LoginView | 登录 |
| /register | RegisterView | 注册 |
| / | DashboardView | 工作台（需登录） |
| /upload | UploadView | 文件上传 |
| /clean/:id | CleanView | 数据清洗 |
| /analysis/:id | AnalysisView | 算法分析 |
| /visualize/:taskId | VisualizeView | 图表可视化 |
| /history | HistoryView | 历史记录 |

### 7.2 组件树
```
App.vue
├── NavBar.vue (全局)
└── <router-view>
    ├── LoginView / RegisterView
    ├── DashboardView
    │   └── DataTable.vue
    ├── UploadView
    │   ├── FileUploader.vue
    │   └── DataTable.vue
    ├── CleanView
    │   ├── StatsCard.vue
    │   └── DataTable.vue
    ├── AnalysisView
    │   ├── AnalysisParams.vue
    │   └── ChartPanel.vue
    ├── VisualizeView
    │   ├── ChartConfig.vue
    │   └── ChartPanel.vue
    └── HistoryView
        └── DataTable.vue
```

### 7.3 Pinia Stores
- **authStore** — Token 管理、自动刷新、登录状态
- **datasetStore** — 当前数据集、预览数据、清洗状态
- **analysisStore** — 分析任务状态、结果缓存
- **chartStore** — 图表配置、ECharts option 生成

### 7.4 支持的图表类型（6 种）
1. 散点图（scatter）— 聚类结果展示
2. 折线图（line）— 回归线 + 预测值
3. 柱状图（bar）— 数据分布对比
4. 热力图（heatmap）— 相关性矩阵
5. 箱线图（boxplot）— 异常值检测
6. 饼图（pie）— 分类占比

---

## 8. 数据分析功能

### 8.1 数据清洗
- **缺失值处理：** 删除 / 均值填充 / 中位数填充 / 众数填充（用户可选）
- **异常值检测：** IQR 方法（箱线图识别）+ Z-score 方法
- **清洗报告：** 返回处理前后对比（缺失数量、异常值数量、处理方式）

### 8.2 K-Means 聚类
- **参数：** 聚类数 K（2-10）、特征列选择
- **评估：** 肘部法则（Elbow Method）+ 轮廓系数（Silhouette Score）
- **输出：** 每个样本的簇标签、聚类中心坐标、评估指标

### 8.3 线性回归
- **参数：** 自变量 X（支持多列）、因变量 y
- **评估：** R² 决定系数、MSE 均方误差、回归系数
- **输出：** 回归方程、预测值 vs 实际值对比数据

---

## 9. 数据集

### 9.1 Mall Customer Segmentation
- **来源：** Kaggle
- **规模：** 200 行 × 5 列
- **字段：** CustomerID, Gender, Age, Annual Income (k$), Spending Score (1-100)
- **用途：** 入门演示，快速跑通全流程

### 9.2 California Housing
- **来源：** scikit-learn 内置数据集
- **规模：** 20,640 行 × 10 列
- **字段：** MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude, MedHouseVal
- **用途：** 深度分析，展示大规模清洗和复杂建模

---

## 10. 团队分工（4 人 · 独立模块 · 可独立 MR）

### 10.1 分工原则
- **一人一模块：** 每个 Django App 只由一人修改，Vue 页面/组件不共享
- **接口先约定：** A 先交付基础骨架，B/C/D 基于约定接口并行开发
- **Git 分支策略：** A 在 main 搭骨架 → B/C/D 各自开 feature 分支 → 分别 MR 合入
- **Store 也分人：** auth(A)、dataset(B)、analysis(C)、chart(D)

### 10.2 角色分配

| 角色 | 阶段 | Django App | Vue 页面 | Vue 组件 | 关键交付 |
|------|------|------------|----------|----------|----------|
| A：基础+认证 | 1（先行） | accounts | LoginView, RegisterView | NavBar | Django/Vue 项目骨架 + JWT 认证 |
| B：数据管理 | 2（并行） | datafile | DashboardView, UploadView | FileUploader, DataTable | 上传/预览/导出 完整流程 |
| C：清洗+分析 | 2（并行） | analysis | CleanView, AnalysisView | AnalysisParams, StatsCard | K-Means + 回归 + 清洗报告 |
| D：可视化+历史 | 2（并行） | 无（纯前端） | VisualizeView, HistoryView | ChartPanel, ChartConfig | 6 种可配置图表 + 响应式 |

### 10.3 开发阶段
1. **A 搭骨架：** Django 项目 + Vue 项目 + JWT + 路由守卫 + Axios 封装
2. **B/C/D 并行（A 交付后）：**
   - B：Dataset 模型 + 数据管理 API + Dashboard/Upload 页面
   - C：AnalysisTask/ChartConfig 模型 + 清洗 + K-Means + 回归 + Clean/Analysis 页面
   - D：ECharts 集成 + ChartPanel/ChartConfig 组件 + Visualize/History 页面
3. **集成联调：** 全流程测试 + 部署 + 报告

---

## 11. 非功能需求
- 响应式布局（桌面 + 平板）
- 文件上传限制 < 20MB
- 分析任务异步处理（避免请求超时）
- 前端路由守卫（未登录重定向）
- 所有 API 错误统一返回格式：`{"error": "message", "code": 400}`
