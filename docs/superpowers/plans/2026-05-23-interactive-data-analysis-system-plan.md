# 交互式数据分析系统 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建完整的数据分析 Web 系统：上传→清洗→分析→可视化→导出

**Architecture:** Django DRF 后端 (8000) + Vue 3 SPA 前端 (5173)，JWT 认证，前后端完全分离。4 人独立模块并行开发。

**Tech Stack:** Django 5.x + DRF + simplejwt / Vue 3 + Vite + Pinia + Vue Router + ECharts / Pandas + scikit-learn

---

# 阶段 0：项目初始化（角色 A，先行）

## Task 0.1：Git 仓库初始化

- [ ] **Step 1：初始化仓库并创建 .gitignore**

```bash
cd "E:/vs code/code/Python/ShiYan"
git init
```

创建 `E:/vs code/code/Python/ShiYan/.gitignore`：

```gitignore
__pycache__/
*.py[cod]
*.db
*.sqlite3
.env
node_modules/
dist/
.vite/
media/
*.log
.superpowers/
.DS_Store
Thumbs.db
```

- [ ] **Step 2：初始提交**

```bash
git add .gitignore docs/
git commit -m "chore: init repo with gitignore and design specs"
```

---

# 阶段 1：角色 A — Django 后端骨架 + 认证模块

## Task 1.1：Django 项目搭建

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/manage.py`

- [ ] **Step 1：安装依赖**

```bash
cd "E:/vs code/code/Python/ShiYan"
mkdir -p backend/config backend/apps
python -m venv venv
source venv/Scripts/activate  # Windows
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers pandas scikit-learn openpyxl
```

- [ ] **Step 2：创建 requirements.txt**

写入 `backend/requirements.txt`：

```
django>=5.0
djangorestframework>=3.15
djangorestframework-simplejwt>=5.3
django-cors-headers>=4.3
pandas>=2.2
scikit-learn>=1.5
openpyxl>=3.1
```

- [ ] **Step 3：创建项目配置文件**

写入 `backend/config/settings.py`：

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dev-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.accounts',
    'apps.datafile',
    'apps.analysis',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

写入 `backend/config/urls.py`：

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/datasets/', include('apps.datafile.urls')),
    path('api/analysis/', include('apps.analysis.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

写入 `backend/config/wsgi.py`：

```python
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
```

写入 `backend/manage.py`：

```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

- [ ] **Step 4：创建空 __init__.py 文件**

```bash
touch backend/config/__init__.py
mkdir -p backend/apps/accounts
mkdir -p backend/apps/datafile
mkdir -p backend/apps/analysis
touch backend/apps/__init__.py
touch backend/apps/accounts/__init__.py
touch backend/apps/datafile/__init__.py
touch backend/apps/analysis/__init__.py
```

- [ ] **Step 5：运行迁移并启动验证**

```bash
cd backend && python manage.py makemigrations && python manage.py migrate
python manage.py runserver 8000
```

Expected: `Starting development server at http://127.0.0.1:8000/`

- [ ] **Step 6：提交**

```bash
git add backend/
git commit -m "feat(backend): init Django project with DRF + JWT + CORS"
```

---

## Task 1.2：accounts 应用 — 用户认证 API

**Files:**
- Create: `backend/apps/accounts/urls.py`
- Create: `backend/apps/accounts/serializers.py`
- Create: `backend/apps/accounts/views.py`

- [ ] **Step 1：创建序列化器**

写入 `backend/apps/accounts/serializers.py`：

```python
from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined')
```

- [ ] **Step 2：创建视图**

写入 `backend/apps/accounts/views.py`：

```python
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
```

- [ ] **Step 3：创建 URL 路由**

写入 `backend/apps/accounts/urls.py`：

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.MeView.as_view(), name='me'),
]
```

- [ ] **Step 4：测试认证 API**

```bash
# 启动服务器后测试
# 注册
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","email":"test@test.com"}'

# 登录
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# 用返回的 access token 测试 me
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

Expected: 注册返回用户数据，登录返回 access+refresh token，me 返回当前用户信息。

- [ ] **Step 5：提交**

```bash
git add backend/apps/accounts/
git commit -m "feat(accounts): add register/login/me API with JWT"
```

---

## Task 1.3：创建空占位 App（给 B/C 用）

- [ ] **Step 1：创建 datafile 和 analysis app 的基础文件**

写入 `backend/apps/datafile/urls.py`：

```python
urlpatterns = []
```

写入 `backend/apps/analysis/urls.py`：

```python
urlpatterns = []
```

创建空的 models.py（使 Django 能识别 app）：

```bash
echo "" > backend/apps/datafile/models.py
echo "" > backend/apps/analysis/models.py
```

- [ ] **Step 2：验证所有 app 可加载**

```bash
cd backend && python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 3：提交**

```bash
git add backend/apps/datafile/ backend/apps/analysis/
git commit -m "feat: add placeholder apps for datafile and analysis"
```

---

# 阶段 2：角色 A — Vue 3 前端骨架 + 认证页面

## Task 2.1：Vue 3 项目搭建

**Files:**
- Create: `frontend/` (Vite 脚手架)
- Modify: `frontend/vite.config.js`
- Create: `frontend/src/api/index.js`

- [ ] **Step 1：创建 Vue 项目**

```bash
cd "E:/vs code/code/Python/ShiYan"
npm create vite@latest frontend -- --template vue
cd frontend
npm install
npm install vue-router@4 pinia axios
```

- [ ] **Step 2：配置 Vite 代理**

修改 `frontend/vite.config.js`：

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

- [ ] **Step 3：Axios 封装**

写入 `frontend/src/api/index.js`：

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

- [ ] **Step 4：提交**

```bash
git add frontend/
git commit -m "feat(frontend): init Vue 3 project with Vite + Axios"
```

---

## Task 2.2：路由 + 路由守卫

**Files:**
- Create: `frontend/src/router/index.js`
- Modify: `frontend/src/main.js`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1：创建路由**

写入 `frontend/src/router/index.js`：

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('../views/UploadView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/clean/:id',
    name: 'Clean',
    component: () => import('../views/CleanView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/analysis/:id',
    name: 'Analysis',
    component: () => import('../views/AnalysisView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/visualize/:taskId',
    name: 'Visualize',
    component: () => import('../views/VisualizeView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/HistoryView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guest && token) {
    next('/')
  } else {
    next()
  }
})

export default router
```

- [ ] **Step 2：更新 main.js**

修改 `frontend/src/main.js`：

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 3：更新 App.vue**

修改 `frontend/src/App.vue`：

```vue
<template>
  <div id="app">
    <NavBar v-if="isLoggedIn" />
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from './components/NavBar.vue'

const router = useRouter()
const isLoggedIn = computed(() => !!localStorage.getItem('access_token'))
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
.container { max-width: 1200px; margin: 0 auto; padding: 1.5rem; }
</style>
```

- [ ] **Step 4：提交**

```bash
git add frontend/src/router/ frontend/src/main.js frontend/src/App.vue
git commit -m "feat(frontend): add Vue Router with auth guards and 8 routes"
```

---

## Task 2.3：Pinia auth Store

**Files:**
- Create: `frontend/src/stores/auth.js`

- [ ] **Step 1：创建 auth store**

写入 `frontend/src/stores/auth.js`：

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  async function register(username, password, email) {
    const { data } = await api.post('/auth/register/', { username, password, email })
    return data
  }

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    isAuthenticated.value = true
    await fetchUser()
    return data
  }

  async function fetchUser() {
    try {
      const { data } = await api.get('/auth/me/')
      user.value = data
      isAuthenticated.value = true
    } catch {
      logout()
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    isAuthenticated.value = false
  }

  return { user, isAuthenticated, register, login, fetchUser, logout }
})
```

- [ ] **Step 2：提交**

```bash
git add frontend/src/stores/
git commit -m "feat(frontend): add Pinia auth store with JWT login/logout/register"
```

---

## Task 2.4：NavBar 组件

**Files:**
- Create: `frontend/src/components/NavBar.vue`

- [ ] **Step 1：创建导航栏**

写入 `frontend/src/components/NavBar.vue`：

```vue
<template>
  <nav class="navbar">
    <div class="nav-left">
      <router-link to="/" class="logo">数据分析系统</router-link>
      <router-link to="/upload">上传数据</router-link>
      <router-link to="/history">历史记录</router-link>
    </div>
    <div class="nav-right">
      <span class="username">{{ user?.username }}</span>
      <button @click="handleLogout" class="btn-logout">退出</button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.5rem;
  height: 56px;
  background: #1a1a2e;
  color: #fff;
}
.nav-left { display: flex; gap: 1.5rem; align-items: center; }
.nav-left a { color: #ccc; text-decoration: none; font-size: 0.9rem; }
.nav-left a:hover { color: #fff; }
.nav-left .logo { color: #fff; font-weight: 700; font-size: 1.1rem; }
.nav-right { display: flex; gap: 1rem; align-items: center; }
.username { font-size: 0.85rem; color: #aaa; }
.btn-logout {
  padding: 0.3rem 0.8rem;
  border: 1px solid #555;
  border-radius: 4px;
  background: transparent;
  color: #ccc;
  cursor: pointer;
  font-size: 0.8rem;
}
.btn-logout:hover { background: #333; }
</style>
```

- [ ] **Step 2：提交**

```bash
git add frontend/src/components/NavBar.vue
git commit -m "feat(frontend): add NavBar component with user info and logout"
```

---

## Task 2.5：Login + Register 页面

**Files:**
- Create: `frontend/src/views/LoginView.vue`
- Create: `frontend/src/views/RegisterView.vue`

- [ ] **Step 1：创建登录页面**

写入 `frontend/src/views/LoginView.vue`：

```vue
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <label>用户名</label>
        <input v-model="username" type="text" required placeholder="请输入用户名" />
        <label>密码</label>
        <input v-model="password" type="password" required placeholder="请输入密码" />
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="switch">
        没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
.auth-card {
  background: #fff;
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  width: 400px;
}
.auth-card h2 { margin-bottom: 1.5rem; text-align: center; }
.auth-card label { display: block; margin-bottom: 0.3rem; font-size: 0.9rem; color: #333; }
.auth-card input {
  width: 100%; padding: 0.6rem; margin-bottom: 1rem;
  border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem;
}
.auth-card button {
  width: 100%; padding: 0.7rem;
  background: #1a1a2e; color: #fff; border: none;
  border-radius: 4px; font-size: 1rem; cursor: pointer;
  margin-top: 0.5rem;
}
.auth-card button:hover { background: #16213e; }
.auth-card button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #e74c3c; font-size: 0.85rem; margin-bottom: 0.5rem; }
.switch { margin-top: 1rem; text-align: center; font-size: 0.9rem; color: #666; }
.switch a { color: #1a1a2e; }
</style>
```

- [ ] **Step 2：创建注册页面**

写入 `frontend/src/views/RegisterView.vue`：

```vue
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <label>用户名</label>
        <input v-model="username" type="text" required placeholder="请输入用户名" />
        <label>邮箱</label>
        <input v-model="email" type="email" placeholder="请输入邮箱（可选）" />
        <label>密码</label>
        <input v-model="password" type="password" required placeholder="至少6位密码" />
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="switch">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await authStore.register(username.value, password.value, email.value)
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    const data = e.response?.data
    error.value = typeof data === 'object' ? Object.values(data).flat().join(', ') : '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
.auth-card {
  background: #fff;
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  width: 400px;
}
.auth-card h2 { margin-bottom: 1.5rem; text-align: center; }
.auth-card label { display: block; margin-bottom: 0.3rem; font-size: 0.9rem; color: #333; }
.auth-card input {
  width: 100%; padding: 0.6rem; margin-bottom: 1rem;
  border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem;
}
.auth-card button {
  width: 100%; padding: 0.7rem;
  background: #1a1a2e; color: #fff; border: none;
  border-radius: 4px; font-size: 1rem; cursor: pointer;
  margin-top: 0.5rem;
}
.auth-card button:hover { background: #16213e; }
.auth-card button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #e74c3c; font-size: 0.85rem; margin-bottom: 0.5rem; }
.switch { margin-top: 1rem; text-align: center; font-size: 0.9rem; color: #666; }
.switch a { color: #1a1a2e; }
</style>
```

- [ ] **Step 3：启动前端验证**

```bash
cd frontend && npm run dev
```

Expected: 访问 http://localhost:5173，重定向到 /login，可注册/登录，登录后跳转到 Dashboard。

- [ ] **Step 4：提交**

```bash
git add frontend/src/views/LoginView.vue frontend/src/views/RegisterView.vue
git commit -m "feat(frontend): add Login and Register pages with auth flow"
```

---

## Task 2.6：创建占位页面（给 B/C/D 填充）

**Files:**
- Create: `frontend/src/views/DashboardView.vue`
- Create: `frontend/src/views/UploadView.vue`
- Create: `frontend/src/views/CleanView.vue`
- Create: `frontend/src/views/AnalysisView.vue`
- Create: `frontend/src/views/VisualizeView.vue`
- Create: `frontend/src/views/HistoryView.vue`

- [ ] **Step 1：创建所有占位页面**

每个占位页面结构相同（以 DashboardView 为例），写入 `frontend/src/views/DashboardView.vue`：

```vue
<template>
  <div class="page">
    <h2>工作台</h2>
    <p>此处由角色 B 实现</p>
  </div>
</template>

<script setup>
</script>
```

同样为 UploadView、CleanView、AnalysisView、VisualizeView、HistoryView 创建占位文件，替换标题和描述文字：
- UploadView → "上传数据" / "此处由角色 B 实现"
- CleanView → "数据清洗" / "此处由角色 C 实现"
- AnalysisView → "分析任务" / "此处由角色 C 实现"
- VisualizeView → "图表可视化" / "此处由角色 D 实现"
- HistoryView → "历史记录" / "此处由角色 D 实现"

- [ ] **Step 2：提交**

```bash
git add frontend/src/views/
git commit -m "feat(frontend): add placeholder pages for roles B/C/D"
```

---

## Task 2.7：基础 CSS + 响应式布局

**Files:**
- Modify: `frontend/src/style.css`

- [ ] **Step 1：写入全局样式**

写入 `frontend/src/style.css`：

```css
:root {
  --primary: #1a1a2e;
  --bg: #f5f6fa;
  --card-bg: #fff;
  --text: #333;
  --text-muted: #888;
  --border: #e0e0e0;
  --success: #27ae60;
  --danger: #e74c3c;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}

.page { padding: 1.5rem 0; }
.page h2 { margin-bottom: 1rem; font-size: 1.5rem; }

.card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.btn {
  display: inline-block;
  padding: 0.5rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: opacity 0.2s;
}
.btn:hover { opacity: 0.85; }
.btn-primary { background: var(--primary); color: #fff; }
.btn-danger { background: var(--danger); color: #fff; }
.btn-success { background: var(--success); color: #fff; }

input, select, textarea {
  padding: 0.5rem 0.7rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 0.9rem;
  width: 100%;
}
input:focus, select:focus { outline: none; border-color: var(--primary); }

table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  padding: 0.6rem 0.8rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
  font-size: 0.85rem;
}
th { background: #f8f9fa; font-weight: 600; }

@media (max-width: 768px) {
  .container { padding: 0.8rem; }
  .page h2 { font-size: 1.2rem; }
}
```

- [ ] **Step 2：提交**

```bash
git add frontend/src/style.css
git commit -m "feat(frontend): add global CSS with responsive layout and design tokens"
```

---

## Task 2.8：角色 A 整体验证 + 交付

- [ ] **Step 1：全链路测试**

```bash
# 终端 1：启动后端
cd backend && python manage.py runserver 8000

# 终端 2：启动前端
cd frontend && npm run dev
```

验证清单：
1. 访问 http://localhost:5173 → 重定向到 /login
2. 点击注册 → 输入用户名+密码 → 注册成功自动跳转工作台
3. NavBar 显示用户名，点击退出回到登录页
4. 再次登录 → 进入工作台（占位页面）
5. 访问 /upload /history 等 → 显示占位内容
6. 手动清除 localStorage access_token → 刷新 → 重定向到 /login

- [ ] **Step 2：最终提交**

```bash
git status
git add -A
git commit -m "feat: complete Role A skeleton — Django + Vue + JWT auth ready"
```

- [ ] **Step 3：生成 API 文档给团队**

创建 `docs/api-reference.md`，汇总所有 API 端点约定：

```markdown
# API 接口约定

**Base URL:** http://localhost:8000/api
**Auth:** Bearer Token (JWT)

## 认证 (A 已实现)
- POST /auth/register/ — 注册
- POST /auth/login/ — 登录
- GET /auth/me/ — 当前用户

## 数据管理 (B 实现)
- POST /datasets/upload/ — 上传文件
- GET /datasets/ — 数据集列表
- GET /datasets/{id}/preview/ — 预览(分页)
- DELETE /datasets/{id}/ — 删除
- GET /datasets/{id}/export/ — 导出

## 清洗+分析 (C 实现)
- POST /analysis/clean/{id}/ — 执行清洗
- GET /analysis/stats/{id}/ — 数据概览
- POST /analysis/kmeans/ — K-Means
- POST /analysis/regression/ — 线性回归
- GET /analysis/tasks/ — 历史记录
- POST /charts/generate/ — 生成图表数据
```

---

# 阶段 3：角色 B — 数据管理模块（独立分支 feature/datafile）

## Task 3.1-3.5：Dataset 模型 + CRUD API + 上传/预览/导出视图 + DataTable 组件 + Dashboard/Upload 页面

（角色 B 详细任务将在角色 A 交付后展开，此处预留章节。B 仅修改 `backend/apps/datafile/` 和 `frontend/src/views/DashboardView.vue`、`frontend/src/views/UploadView.vue`、`frontend/src/components/DataTable.vue`、`frontend/src/components/FileUploader.vue`、`frontend/src/stores/dataset.js`，不触碰 A/C/D 的文件。）

---

# 阶段 4：角色 C — 清洗+分析模块（独立分支 feature/analysis）

## Task 4.1-4.7：AnalysisTask/ChartConfig 模型 + cleaning.py + clustering.py + regression.py + visualization.py + CleanView + AnalysisView

（角色 C 详细任务预留。C 仅修改 `backend/apps/analysis/` 和 `frontend/src/views/CleanView.vue`、`frontend/src/views/AnalysisView.vue`、`frontend/src/components/AnalysisParams.vue`、`frontend/src/components/StatsCard.vue`、`frontend/src/stores/analysis.js`。）

---

# 阶段 5：角色 D — 可视化+历史模块（独立分支 feature/visualize）

## Task 5.1-5.5：ChartPanel + ChartConfig 组件 + VisualizeView + HistoryView + chart store

（角色 D 详细任务预留。D 仅修改 `frontend/src/views/VisualizeView.vue`、`frontend/src/views/HistoryView.vue`、`frontend/src/components/ChartPanel.vue`、`frontend/src/components/ChartConfig.vue`、`frontend/src/stores/chart.js`。）

---

# 阶段 6：集成测试 + 部署

## Task 6.1：全流程联调

- [ ] 启动 Django + Vue，从注册到可视化跑通完整管线
- [ ] 验证文件上传→预览→清洗→K-Means→散点图 流程
- [ ] 验证文件上传→预览→清洗→线性回归→折线图 流程
- [ ] 验证历史记录查询
- [ ] 验证导出 CSV 功能

## Task 6.2：部署配置

```bash
# 前端构建
cd frontend && npm run build

# 复制到 Django static
cp -r dist/* ../backend/static/

# 配置 Django 服务静态文件
cd ../backend
python manage.py collectstatic --noinput
python manage.py runserver 8000
```

## Task 6.3：实验报告

（由角色 D 负责撰写。）
