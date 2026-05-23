# API 接口约定

**Base URL:** http://localhost:8000/api
**Auth:** Bearer Token (JWT)

## 认证 (A 已实现)
| 方法 | 路径 | 说明 | 需要认证 |
|------|------|------|----------|
| POST | /auth/register/ | 注册 | 否 |
| POST | /auth/login/ | 登录，返回 access + refresh token | 否 |
| POST | /auth/refresh/ | 刷新 Token | 否 |
| GET | /auth/me/ | 当前用户信息 | 是 |

## 数据管理 (B 实现)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /datasets/upload/ | 上传文件 |
| GET | /datasets/ | 数据集列表 |
| GET | /datasets/{id}/ | 数据集详情 |
| GET | /datasets/{id}/preview/ | 预览(分页) |
| DELETE | /datasets/{id}/ | 删除 |
| GET | /datasets/{id}/export/ | 导出 |

## 清洗+分析 (C 实现)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /analysis/clean/{id}/ | 执行清洗 |
| GET | /analysis/stats/{id}/ | 数据概览 |
| POST | /analysis/kmeans/ | K-Means 聚类 |
| POST | /analysis/regression/ | 线性回归 |
| GET | /analysis/tasks/ | 分析历史 |
| POST | /charts/generate/ | 生成图表数据 |

## 注册示例
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

## 登录示例
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

## 认证使用
所有需要认证的接口在请求头添加：
`Authorization: Bearer <access_token>`
