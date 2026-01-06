# 阶段1a: 需求澄清

输出 1 个可复制的 `PRD_INPUT_PACK`（YAML 代码块）；不写文件。

## 输入

- 用户需求描述（自由文本），或
- `PRD_CLARIFY_PACK`（可选）

## `PRD_CLARIFY_PACK` 处理（必须）

当用户粘贴 `PRD_CLARIFY_PACK` 时：

1. 只围绕 `blockers` 提问（每轮最多 4 个）
2. 收集答案后，回填到**本窗口上一次已确认的需求信息/上一版 `PRD_INPUT_PACK`**
3. 输出更新后的完整 `PRD_INPUT_PACK`（只输出 1 个代码块）

## 对话规则（必须遵守）

- 全程中文（必要技术词可用英文）
- 每轮最多提 4 个问题；优先问会阻塞 PRD 落盘的缺失信息
- 未确认的信息不得写入 `PRD_INPUT_PACK`；未知必须继续追问
- 每完成一个主题块，输出 1-3 行「当前需求小结」并让用户确认/补充

## 收敛门禁（输出 pack 前必须满足）

- `modules` 至少 1 个，且至少 1 个模块 `priority = P0`
- 每个模块至少 1 个 `feature_points[]`，且每个 `feature_points[].landing` 非空（允许 `N/A`）
- `business_rules` 至少 1 条且非空
- `permission_matrix.operations` 至少 1 行

## 输出规则（必须遵守）

- 信息不足：继续提问（不输出 pack）
- 信息足够或用户确认收敛：先输出「当前需求小结」，再输出且仅输出 1 个 `PRD_INPUT_PACK` 代码块

## `PRD_INPUT_PACK`（必须严格按此结构输出）

```yaml
PRD_INPUT_PACK: v1
project:
  name: ""
  one_liner: ""

goals:
  - ""
non_goals:
  - ""

scope:
  in:
    - ""
  out:
    - ""
assumptions_constraints:
  - assumption: ""
    impact: ""

roles:
  - role: ""
    description: ""
    typical_scenarios:
      - ""

permission_matrix:
  legend: "A=允许, D=禁止, O=仅自己的/所属范围"
  operations:
    - operation: ""
      per_role:
        "<role>": "A/D/O"
      note: ""

modules:
  - name: ""
    priority: "P0/P1/P2"
    deps: ["无"]
    summary: ""
    feature_points:
      - desc: ""
        landing: "N/A" # N/A 或逗号分隔：DB:<table> / FILE:<path/glob> / CFG:<key> / EXT:<system>
        note: ""
    scenarios:
      - actor: ""
        given: ""
        when: ""
        then: ""
        fail_or_edge: ""
        note: ""

ui_routes:
  - route: ""
    desc: ""

business_rules:
  - rule: ""
    scope: ""
    note: ""

states_enums:
  enums:
    - field: ""
      values: ""
      default: ""
      note: ""
  state_machines:
    - entity: ""
      flow: ""
      transitions:
        - from: ""
          event: ""
          to: ""
          auth_or_condition: ""
          note: ""

data_model:
  persistence:
    has_durable_artifacts: true
    notes: ""
  tables:
    - table: ""
      purpose: ""
      fields:
        - name: ""
          type: ""
          nullable: "Y/N"
          default: ""
          constraints_or_index: ""
          note: ""
      constraints:
        - ""
      indexes:
        - ""
  relations: ""

api:
  has_api: true
  base_url: "/api"
  auth: "无登录/N/A 或 说明具体方式"
  pagination_sort_filter: "如有则说明；无则 N/A"
  response_wrapper: "如有则给一个极简例子；无则 N/A"
  extra_error_codes:
    - ""
  endpoints:
    - name: ""
      method: "GET/POST/PUT/PATCH/DELETE"
      path: ""
      module: ""
      permission: "Role/Operation（需能映射到权限矩阵）"
      summary: ""
      request_fields:
        - in: "path/query/body"
          field: ""
          type: ""
          required: "Y/N"
          constraints: ""
          note: ""
      response_fields:
        - field: ""
          type: ""
          note: ""
      failures:
        - status: 400
          condition: ""
          user_message: ""

nfr:
  security: ""
  audit: ""
  performance: ""
  observability: ""
```

## 开始

请用 1-3 句话描述你要做的应用：给谁用、主要解决什么问题？
