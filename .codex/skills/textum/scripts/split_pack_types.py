from __future__ import annotations

import re


SPLIT_PLAN_PACK_FILENAME = "split-plan-pack.json"
SPLIT_PLAN_TEMPLATE_FILENAME = "split-plan-pack.template.json"

STORIES_DIRNAME = "stories"
STORY_FILE_PREFIX = "story-"
STORY_SCHEMA_VERSION = "story@v1"

SPLIT_CHECK_INDEX_PACK_FILENAME = "split-check-index-pack.json"

KEBAB_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STORY_NAME_RE = re.compile(r"^Story (\d+)$")

