---
STORY:
story: "Story N"
n: 1
slug: "kebab-case"
title: "功能名称"
modules:
  - "M-xx"
prereq_stories: []
fp_ids:
  - "FP-###"
refs:
  gc_br: []
  prd_br: []
  prd_tbl: []
  prd_api: []
artifacts:
  file: []
  cfg: []
  ext: []
---

# Story N: 功能名称

## 功能点（必填）
- [功能描述（对应 fp_ids 中每个 FP 一条）]

## 依赖（必填）
- 已有资源: [表/接口/组件/代码标识符（如 Service/Controller/函数名/类型名/相对路径）]

## 业务规则（必填；无则写 N/A）
- [规则摘要（与 refs.gc_br / refs.prd_br 对齐）]

## 数据/产物落点（必填；无则写 N/A）
- [职责说明（与 refs.prd_tbl / artifacts.* 对齐）]

## 接口（如无写 N/A）
- [职责说明（与 refs.prd_api 对齐）]

## 验收标准（必填）
- [ ] 技术验收: [可测试的具体场景]
- [ ] 用户验收: [打开页面可以看到xxx / 点击按钮会xxx]（如不需要用户验收写 N/A）

## 测试要求（必填；涉及 API 时不得为 N/A；否则无则写 N/A）
- [ ] 单元测试: [需要单元测试的模块]

## 注意（如无写 N/A）
- [边界情况/人工配置项/外部依赖]
