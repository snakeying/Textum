from __future__ import annotations

from typing import Any


SUPPORTED_LANGS = ("zh", "en")


def resolve_render_lang(lang: str, prd_pack: dict[str, Any]) -> str:
    normalized = (lang or "").strip().lower()
    if normalized in ("auto", ""):
        return detect_pack_lang(prd_pack)
    if normalized not in SUPPORTED_LANGS:
        raise ValueError(f"unsupported lang: {lang!r} (expected: auto/zh/en)")
    return normalized


def detect_pack_lang(prd_pack: dict[str, Any]) -> str:
    strings: list[str] = []

    def walk(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str):
            strings.append(value)
            return
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(k, str) and k.lower() == "id":
                    continue
                walk(v)
            return
        if isinstance(value, list):
            for item in value:
                walk(item)
            return

    walk(prd_pack)

    cjk = 0
    latin = 0
    for text in strings:
        for ch in text:
            code = ord(ch)
            if 0x4E00 <= code <= 0x9FFF or 0x3400 <= code <= 0x4DBF:
                cjk += 1
                continue
            if ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
                latin += 1

    if cjk == 0 and latin == 0:
        return "zh"

    total = cjk + latin
    if cjk >= 50 and (cjk / total) >= 0.2:
        return "zh"
    return "en"


def prd_render_labels(lang: str) -> dict[str, Any]:
    if lang not in SUPPORTED_LANGS:
        raise ValueError(f"unsupported lang: {lang!r}")

    if lang == "zh":
        return {
            "text": {"none": "无"},
            "sections": {
                "1": "## 1. 项目概述",
                "1.1": "### 1.1 一句话简介",
                "1.2": "### 1.2 目标（Goals）",
                "1.3": "### 1.3 非目标（Non-goals）",
                "2": "## 2. 范围与假设",
                "2.1": "### 2.1 交付范围（In Scope）",
                "2.2": "### 2.2 不在范围（Out of Scope）",
                "2.3": "### 2.3 关键假设与约束",
                "3": "## 3. 目标用户与角色",
                "3.1": "### 3.1 用户角色",
                "4": "## 4. 权限矩阵（必填）",
                "5": "## 5. 核心功能",
                "5.1": "### 5.1 功能清单（必填）",
                "5.2": "### 5.2 功能规格（按模块填写）",
                "5.3": "### 5.3 页面/路由（可选）",
                "6": "## 6. 业务规则（必填）",
                "7": "## 7. 状态与枚举（可选；无则写 N/A）",
                "7.1": "### 7.1 枚举值",
                "7.2": "### 7.2 状态机（如适用；无则写 N/A）",
                "7.3": "### 7.3 命名规范（如适用；否则写 N/A）",
                "8": "## 8. 数据模型（如适用；否则 N/A）",
                "8.0": "### 8.0 功能点→落点映射（必填）",
                "8.1": "### 8.1 表清单（可选）",
                "8.2": "### 8.2 表定义（逐表填写，便于按 `TBL-###` 定位；无则写 N/A）",
                "8.3": "### 8.3 表关系（可选；无则写 N/A）",
                "9": "## 9. 接口设计（如适用；无 API 则 N/A）",
                "9.1": "### 9.1 通用约定（有 API 时填写；无则 N/A）",
                "9.2": "### 9.2 接口清单（有 API 时填写；无则 N/A）",
                "9.3": "### 9.3 接口详情（逐个填写，便于按 `API-###` 定位）",
                "10": "## 10. 非功能需求（可选；无则写 N/A）",
            },
            "blocks": {
                "feature_points": "**功能点（必填）**",
                "scenarios": "**关键场景/验收（必填）**",
                "table_constraints": "**关键约束（可选；无则写 N/A）**",
                "table_indexes": "**关键索引（可选；无则写 N/A）**",
                "request": "**请求（可选；无则写 N/A）**",
                "response": "**响应（可选；无则写 N/A）**",
                "failure": "**失败/边界（可选；无则写 N/A）**",
            },
            "tables": {
                "assumptions": ["ID", "假设/约束", "影响"],
                "roles": ["角色", "描述", "典型场景"],
                "permission_matrix": ["操作", "权限（role=A/D/O）", "说明"],
                "modules": ["模块ID", "模块名", "一句话说明", "优先级", "依赖"],
                "feature_points": ["FP", "描述"],
                "scenarios": ["场景ID", "参与者", "前置条件（Given）", "用户操作（When）", "系统响应（Then）", "失败/边界", "备注"],
                "routes": ["路由", "页面/入口说明", "关联模块"],
                "business_rules": ["规则ID", "规则描述", "适用范围（模块/对象）", "例外/备注"],
                "enums": ["字段（表.字段/上下文）", "可选值", "默认值", "说明"],
                "state_machines": ["当前状态", "触发事件", "下一状态", "权限/条件", "备注"],
                "fp_landing": ["FP", "落点", "说明"],
                "table_list": ["表ID", "表名", "用途", "主要字段（摘要）"],
                "table_columns": ["字段", "类型", "可空", "默认值", "约束/索引", "说明"],
                "table_constraints": ["ID", "约束", "说明"],
                "table_indexes": ["ID", "索引", "用途"],
                "endpoints": ["接口ID", "名称", "方法", "路径", "模块", "权限", "说明"],
                "request_fields": ["位置", "字段", "类型", "必填", "约束", "说明"],
                "response_fields": ["字段", "类型", "说明"],
                "failure_cases": ["状态码", "触发条件", "对用户的提示（如有）"],
                "nfr": ["类别", "需求", "验收口径"],
            },
            "api": {
                "auth": "认证方式",
                "authorization": "权限校验",
                "authorization_note": "按第 4 节权限矩阵执行",
                "pagination": "分页/排序/筛选",
                "response_wrapper": "响应包装",
                "error_codes": "错误码",
                "method": "方法",
                "path": "路径",
                "module": "模块",
                "permission": "权限",
            },
            "table": {"purpose_one_liner": "**用途（一句话；可选）**"},
        }

    return {
        "text": {"none": "None"},
        "sections": {
            "1": "## 1. Project Overview",
            "1.1": "### 1.1 One-liner",
            "1.2": "### 1.2 Goals",
            "1.3": "### 1.3 Non-goals",
            "2": "## 2. Scope & Assumptions",
            "2.1": "### 2.1 In Scope",
            "2.2": "### 2.2 Out of Scope",
            "2.3": "### 2.3 Assumptions & Constraints",
            "3": "## 3. Users & Roles",
            "3.1": "### 3.1 Roles",
            "4": "## 4. Permission Matrix (Required)",
            "5": "## 5. Core Features",
            "5.1": "### 5.1 Feature List (Required)",
            "5.2": "### 5.2 Feature Specs (by module)",
            "5.3": "### 5.3 Pages / Routes (Optional)",
            "6": "## 6. Business Rules (Required)",
            "7": "## 7. States & Enums (Optional; otherwise N/A)",
            "7.1": "### 7.1 Enums",
            "7.2": "### 7.2 State Machines (If applicable; otherwise N/A)",
            "7.3": "### 7.3 Naming Conventions (Optional; otherwise N/A)",
            "8": "## 8. Data Model (If applicable; otherwise N/A)",
            "8.0": "### 8.0 Feature → Landing Mapping (Required)",
            "8.1": "### 8.1 Table List (Optional)",
            "8.2": "### 8.2 Table Definitions (one by one; locate via `TBL-###`; otherwise N/A)",
            "8.3": "### 8.3 Table Relations (Optional; otherwise N/A)",
            "9": "## 9. API Design (If api.has_api=true; otherwise N/A)",
            "9.1": "### 9.1 Common Conventions (If api.has_api=true)",
            "9.2": "### 9.2 Endpoint List (If api.has_api=true)",
            "9.3": "### 9.3 Endpoint Details (one by one; locate via `API-###`)",
            "10": "## 10. Non-functional Requirements (Optional; otherwise N/A)",
        },
        "blocks": {
            "feature_points": "**Feature Points (Required)**",
            "scenarios": "**Scenarios / Acceptance (Required)**",
            "table_constraints": "**Key Constraints (Optional; otherwise N/A)**",
            "table_indexes": "**Key Indexes (Optional; otherwise N/A)**",
            "request": "**Request (Optional; otherwise N/A)**",
            "response": "**Response (Optional; otherwise N/A)**",
            "failure": "**Failure / Edge Cases (Optional; otherwise N/A)**",
        },
        "tables": {
            "assumptions": ["ID", "Assumption/Constraint", "Impact"],
            "roles": ["Role", "Description", "Typical Scenarios"],
            "permission_matrix": ["Operation", "Permissions (role=A/D/O)", "Note"],
            "modules": ["Module ID", "Module", "Summary", "Priority", "Dependencies"],
            "feature_points": ["FP", "Description"],
            "scenarios": ["Scenario ID", "Actor", "Given", "When", "Then", "Failure/Edge", "Note"],
            "routes": ["Route", "Page/Entry", "Module"],
            "business_rules": ["Rule ID", "Description", "Scope (module/object)", "Exception/Note"],
            "enums": ["Field (table.field/context)", "Values", "Default", "Note"],
            "state_machines": ["State", "Event", "Next State", "Permission/Condition", "Note"],
            "fp_landing": ["FP", "Landing", "Note"],
            "table_list": ["Table ID", "Table", "Purpose", "Key Fields (summary)"],
            "table_columns": ["Column", "Type", "Nullable", "Default", "Constraints/Indexes", "Note"],
            "table_constraints": ["ID", "Constraint", "Note"],
            "table_indexes": ["ID", "Index", "Purpose"],
            "endpoints": ["Endpoint ID", "Name", "Method", "Path", "Module", "Permission", "Summary"],
            "request_fields": ["Location", "Field", "Type", "Required", "Constraints", "Note"],
            "response_fields": ["Field", "Type", "Note"],
            "failure_cases": ["Status Code", "Condition", "User Message (if any)"],
            "nfr": ["Category", "Requirement", "Acceptance"],
        },
        "api": {
            "auth": "Authentication",
            "authorization": "Authorization",
            "authorization_note": "Follow Section 4 Permission Matrix",
            "pagination": "Pagination/Sort/Filter",
            "response_wrapper": "Response Wrapper",
            "error_codes": "Error Codes",
            "method": "Method",
            "path": "Path",
            "module": "Module",
            "permission": "Permission",
        },
        "table": {"purpose_one_liner": "**Purpose (Optional; one sentence)**"},
    }
