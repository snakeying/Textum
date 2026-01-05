# split-check 索引pack（用于两阶段拆分校验交接）

目标：把 `docs/split-plan.md` 与 `docs/story-*-*.md` 的“可解析索引”抽取成一个小而稳定的 YAML，供后续对齐校验使用，避免复读所有 Story 文件。

约束：
- 只做抽取与机械计数：不得新增任何 PRD/GC 中不存在的信息
- 所有列表去重并按编号升序
- 不得残留占位符（如 `[...]`、`###`）

输出文件：`docs/split-check-index-pack.yaml`（纯 YAML；不包含 ```）

```yaml
SPLIT_CHECK_INDEX_PACK: v1
source:
  split_plan: "docs/split-plan.md"
  stories_glob: "docs/story-*-*.md"

split_plan:
  stories:
    - story: "Story 1"
      n: 1
      slug: "kebab-case"
      modules: ["M-01"]
      prereq_stories: [] # ["Story 2"]
  api_assignments:
    - api: "API-001"
      story: "Story 1"

stories:
  - file: "docs/story-1-kebab-case.md"
    story: "Story 1"
    n: 1
    slug: "kebab-case"
    modules: ["M-01"]
    prereq_stories: []
    refs:
      gc_br_ids: ["BR-001"]
      prd_api_ids: ["API-001"]
      prd_tbl_ids: ["TBL-001"]
      prd_br_ids: ["BR-002"]
    metrics:
      api_refs: 1
      tbl_refs: 1
      feature_points: 3
      acceptance_items: 5

summary:
  story_count: 1
  api_assignment_count: 1
  refs:
    gc_br_ids: ["BR-001"]
    prd_api_ids: ["API-001"]
    prd_tbl_ids: ["TBL-001"]
    prd_br_ids: ["BR-002"]
```
