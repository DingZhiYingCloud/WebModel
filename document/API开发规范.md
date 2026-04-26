# WebGPT API 开发规范

> 本文档是项目 API 开发的**唯一权威规范**，所有 AI 参与开发时必须严格遵循。
> 任何新增或修改 API 的行为均需符合本规范。

---

## 目录

- [一、目录结构规范](#一目录结构规范)
- [二、文件职责说明](#二文件职责说明)
- [三、代码编写规范](#三代码编写规范)
- [四、状态码规范](#四状态码规范)
- [五、API 文档规范（docs/）](#五api-文档规范docs)
- [六、日志规范（logs.md）](#六日志规范logspd)
- [七、版本管理规范](#七版本管理规范)
- [八、修改已有 API 的规则](#八修改已有-api-的规则)
- [九、检查清单](#九检查清单)

---

## 一、目录结构规范

每个业务模块必须在 `DZY_API/apis/` 下创建独立目录，结构**必须**如下：

```
DZY_API/apis/
└── {模块名}/              # 例：article、user、category...
    ├── __init__.py        # 包标识文件（必须）
    ├── request.py         # 视图层 —— HTTP 请求处理入口
    ├── urls.py            # 路由配置
    ├── utils.py           # 通用工具函数（统一响应、参数获取等）
    ├── service.py         # 业务逻辑层（纯业务处理，不含 HTTP）
    ├── status_codes.py    # 模块专属状态码定义
    ├── logs.md            # 开发日志（供其他 AI 快速上手）
    └── docs/              # 每个接口一份请求文档
        ├── {接口名}.md
        └── ...
```

### 强制要求

1. **所有上述文件和目录都必须创建**，不允许省略任何一个
2. 模块名使用 **英文小写 + 下划线** 命名（如 `user_profile`）
3. `docs/` 目录下每个接口一个 `.md` 文件

### 路由注册

创建模块后，**必须**在 `DZY_API/apis/urls.py` 中注册路由：

```python
from django.urls import path, include

urlpatterns = [
    path("", include("DZY_API/apis.{模块名}.urls")),
]
```

---

## 二、文件职责说明

| 文件 | 职责 | 不允许做的事 |
|------|------|-------------|
| **request.py** | 视图层：拦截方法 → 取参 → 校验 → 调 service → 返回响应 | 写业务逻辑、操作数据库 |
| **service.py** | 业务层：纯数据处理与业务逻辑 | 引用 Django request/response 对象 |
| **utils.py** | 工具层：统一响应封装、参数获取辅助等通用函数 | 写业务相关代码 |
| **status_codes.py** | 状态码常量定义：仅存放该模块的专属状态码 | 存放全局状态码（全局的在 `documents/状态码.md`） |
| **urls.py** | 路由映射：URL → view function | 写任何业务代码 |
| **logs.md** | 开发日志：记录架构、决策、变更历史 | 省略不写 |
| **docs/\*.md** | 接口文档：请求参数、响应示例、状态码对照 | 含糊描述 |

---

## 三、代码编写规范

### 3.1 视图函数标准模板（五步流程）

**所有接口视图函数必须严格遵循以下顺序**：

```python
@csrf_exempt                          # ① 装饰器：关闭 CSRF
def xxx(request):                     # ② 函数签名：接收 request
    
    # 第一步：限制请求方法
    if request.method != "POST":
        return method_not_allowed_response()
    
    # 第二步：获取参数（使用 utils.get_param）
    param1, err = get_param(request, "key1", required=True)
    if err:
        return err
    param2, _ = get_param(request, "key2", required=False, default="默认值")
    
    # 第三步：参数合法性校验（可选，复杂校验放 service 层）
    
    # 第四步：调用业务层
    res = service.xxx(param1, param2)
    
    # 第五步：结果判断 & 统一返回
    if res["code"] != 0:
        return error_response(res["code"], res["message"])
    return success_response(res["data"], "成功提示")
```

### 3.2 编写原则

| 原则 | 说明 |
|------|------|
| **线性短路** | 从上到下依次校验，不合法立即 return |
| **视图轻量** | request.py 只做 HTTP 层处理，零业务逻辑 |
| **无嵌套判断** | 避免多层 if-else，保持扁平 |
| **统一取参** | 必须使用 `utils.get_param()` 获取参数，禁止直接 `request.POST.get()` |

### 3.3 请求方式

- 所有接口**只允许 POST 方法**
- 统一使用 `application/x-www-form-urlencoded` 格式传参
- 使用 `@csrf_exempt` 装饰器关闭 CSRF 校验

### 3.4 统一响应格式

```json
{
    "code": 0,
    "message": "成功",
    "data": {...}
}
```

| 场景 | code | message | data |
|------|------|---------|------|
| 成功 | `0` | 描述信息 | 实际数据 / `{}` |
| 参数错误 | `1001`~`1004` | 错误描述 | `None` |
| 业务错误 | 模块专属码 | 错误描述 | `None` |
| 方法错误 | `405` | 请求方式不允许 | `None` |

### 3.5 导入规范

```python
# request.py 中使用 utils 时：
from .utils import success_response, error_response, method_not_allowed_response, get_param
from .service import xxx, yyy

# service.py 中导入模型时：
from ..models import XxxModel
from .status_codes import XXX_ERROR_CODE
```

---

## 四、状态码规范

### 4.1 全局状态码（见 `documents/状态码.md`）

| 范围 | 用途 | 示例 |
|------|------|------|
| `0` | 成功 | - |
| `400` ~ `499` | HTTP 客户端错误 | 400=参数错误, 401=未授权 |
| `500` ~ `599` | 服务端错误 | 500=内部异常 |
| `1001` ~ `1004` | 业务通用（跨模块复用） | 1001=参数缺失, 1002=参数不合法 |

### 4.2 模块专属状态码（在 `status_codes.py` 中定义）

**分配规则**：每模块独占一个 **100 的区间段**，避免冲突：

| 模块建议 | code 区间 | 说明 |
|----------|-----------|------|
| article（文章） | 2000 ~ 2099 | 已占用 |
| user（用户） | 2100 ~ 2199 | 预留 |
| category（分类） | 2200 ~ 2299 | 预留 |
| ... | ... | 新模块按需申请 |

**命名规则**：全大写 + 下划线，语义清晰：

```python
# ✅ 正确
ARTICLE_NOT_FOUND = 2001
ARTICLE_CREATE_FAILED = 2004
PAGE_PARAM_INVALID = 2101

# ❌ 错误
error1 = 2001
ERR = 2001
```

### 4.3 定义状态码时的强制要求

1. 每个状态码常量**必须**有清晰的注释说明用途
2. 在同模块内**禁止重复定义**相同含义的状态码
3. 如果需要用到全局已有的状态码（如 1001），**直接从 utils 导入使用即可**，不要在 status_codes.py 中重复定义

---

## 五、API 文档规范（docs/）

`docs/` 目录下**每个接口必须对应一个 `.md` 文件**。

### 5.1 文档模板

```markdown
# {接口功能名称}

## 接口信息
- **URL**: `/api/{模块}/{接口}/`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| param1 | string | 是 | - | 参数说明 |
| param2 | int | 否 | 10 | 可选参数说明 |

## 响应示例

### 成功 (code=0)
```json
{...}
```

### 失败示例
```json
{...}
```

## 状态码说明

| code | 说明 |
|------|------|
| 0 | 成功 |
| ... | ... |
```

### 5.2 文档编写要求

| 要求 | 说明 |
|------|------|
| URL 路径 | 从 `/api/` 开始，不含域名 |
| 参数表格 | 必须包含：类型、是否必填、默认值（可选参数）、详细说明 |
| 响应示例 | 至少提供**成功**和**一种失败**两种示例 |
| data 字段说明 | 列表类接口需单独列出 data 内各字段的类型和含义 |
| 状态码对照 | 仅列出本接口可能用到的状态码 |

---

## 六、日志规范（logs.md）

**每个模块必须有 `logs.md`**。这是其他 AI 快速了解该模块的核心参考文件。

### 6.1 日志必须包含的章节

```markdown
# {模块名} API 开发日志

## 项目概述                    # 一句话描述模块功能

## 目录结构                    # 完整列出模块的文件树

## 设计决策与约定               # 关键设计选择及其原因

## 已实现接口清单               # 表格列出所有接口及路径

## 注意事项                    # 已知限制、待改进点等

## 版本历史                    # ⭐ 必须！每次修改都追加记录（见第七章）

## 后续待办（供参考）           # TODO 列表
```

### 6.2 内容要求

- **目录结构**：必须与实际文件一一对应
- **已实现接口清单**：以表格形式列出，包含 接口名 / URL / 功能 三列
- **注意事项**：如实记录当前实现的已知限制（如"未做权限控制"、"物理删除非软删除"等）

---

## 七、版本管理规范

### 7.1 版本号格式

采用 **语义化版本**：`v{主版本}.{次版本}.{修订号}`

- **主版本**：架构级变更（如重构分层、更换数据库）
- **次版本**：新增接口、新增字段、行为变化
- **修订号**：Bug 修复、文档更新、微调

初始版本为 `v1.0.0`。

### 7.2 logs.md 中的版本历史区

每次修改模块后，**必须在 `logs.md` 的「版本历史」区域追加一条记录**，格式如下：

```markdown
## 版本历史

### v1.0.0 (2026-04-25)
- [新增] 创建文章 CRUD 模块（create/detail/update/delete/list）
- [新增] 建立 utils / service 分层架构
- [作者] AI-Assistant

### v1.1.0 (2026-xx-xx)          ← 下一次修改时追加
- [修改] update 接口增加权限校验
- [修复] list 接口分页边界问题
- [作者] AI-B
```

### 7.3 变更类型标签

| 标签 | 用途 |
|------|------|
| `[新增]` | 新增接口、新功能、新文件 |
| `[修改]` | 修改已有接口的行为或逻辑 |
| `[修复]` | 修复 Bug |
| `[重构]` | 重构代码但不改变行为 |
| `[删除]` | 移除接口或功能 |
| `[文档]` | 更新文档但未改代码 |

### 7.4 版本号递增规则

| 变更内容 | 版本号变化 |
|---------|-----------|
| 新增接口 | 次版本 +1，修订号归 0 |
| 修改已有接口行为 | 次版本 +1，修订号归 0 |
| Bug 修复 | 修订号 +1 |
| 仅更新文档/注释 | 修订号 +1 |
| 架构重构 | 主版本 +1，其余归 0 |

---

## 八、修改已有 API 的规则

当需要**修改他人（或其他 AI）编写的已有接口**时，必须遵循以下流程：

### 8.1 修改前

1. **阅读 `logs.md`**：充分理解当前模块的设计意图和上下文
2. **阅读对应 `docs/*.md`**：确认当前接口的契约（参数、返回值、状态码）
3. **确认影响范围**：评估修改对调用方的影响

### 8.2 修改中

1. **优先兼容**：如果可能，保持向后兼容；无法兼容时必须在 docs 中标注 breaking change
2. **同步更新以下文件**（**缺一不可**）：
   - `request.py` 或 `service.py` — 代码修改
   - `docs/{接口名}.md` — 同步更新接口文档
   - `status_codes.py` — 如新增了状态码
   - `logs.md` — **必须**追加版本记录

### 8.3 修改后

1. 在 `logs.md` 的「版本历史」中**追加**新的版本条目
2. **更新版本号**（按 7.4 规则递增）
3. 在版本记录中清晰说明**改了什么、为什么改**

### 8.4 禁止事项

| 禁止项 | 原因 |
|--------|------|
| 只改代码不改文档 | 其他 AI 无法追踪变更 |
| 删除状态码而不更新文档 | 导致状态码混乱 |
| 修改后不更新版本号 | 无法追溯变更历史 |
| 直接覆盖重写整个文件 | 应做精确的最小化改动 |

---

## 九、检查清单

完成 API 开发后，按此表逐项确认：

### 新建模块时

- [ ] 模块目录下所有 7 个必要文件均已创建（`__init__.py`, `request.py`, `urls.py`, `utils.py`, `service.py`, `status_codes.py`）
- [ ] `docs/` 目录已创建，且**每个接口都有对应的 .md 文档**，以及一个 `logs.md`
- [ ] 主 `apis/urls.py` 已注册新模块的路由
- [ ] `status_codes.py` 中的状态码区间**不与其他模块冲突**
- [ ] `logs.md` 包含完整的章节：项目概述、目录结构、设计决策、接口清单、注意事项、版本历史（v1.0.0）、后续待办
- [ ] 视图函数严格遵循**五步流程**，使用 `utils.py` 封装的方法
- [ ] 所有接口文档中的参数表包含：类型、必填/可选、默认值、说明

### 修改已有模块时

- [ ] 已阅读目标模块的 `logs.md` 和相关 `docs/*.md`
- [ ] 代码修改已完成
- [ ] 相关的 `docs/*.md` 已同步更新
- [ ] `logs.md` 的「版本历史」已追加新记录
- [ ] 版本号已按规则正确递增
- [ ] 记录中注明了修改内容和原因

---

## 附录：快速参考

### 常用导入速查

```python
# === request.py ===
from django.views.decorators.csrf import csrf_exempt
from .utils import success_response, error_response, method_not_allowed_response, get_param
from .service import your_func

# === service.py ===
from ..models import YourModel
from .status_codes import YOUR_CUSTOM_CODE

# === status_codes.py ===
# 仅定义常量，无需额外导入

# === urls.py ===
from django.urls import path
from . import request
```

### utils.py 方法速查

```python
success_response(data=None, message="成功")       # 成功响应
error_response(code, message, data=None)           # 错误响应
method_not_allowed_response()                       # 405
param_missing_response(param_name)                  # 1001
param_invalid_response(param_name, reason="")       # 1002
get_param(request, key, required=True, default=None) # 获取POST参数
```

---

*最后更新：2026-04-25*
*维护者：AI-Assistant*
