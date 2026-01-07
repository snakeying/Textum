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
      fp_ids: ["FP-001"]
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
    fp_ids: ["FP-001"]
    gc_br_ids: ["BR-001"]
    prd_api_ids: ["API-001"]
    prd_tbl_ids: ["TBL-001"]
    prd_br_ids: ["BR-002"]
