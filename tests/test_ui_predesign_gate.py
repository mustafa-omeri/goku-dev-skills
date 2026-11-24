#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/UX On-Tasarim Onizleme, Wireframe ve --ui-preview (--ui-ux) Birim Testleri."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
MUSGOKU_SCRIPTS = PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
if str(MUSGOKU_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MUSGOKU_SCRIPTS))

import archive_plan  # noqa: E402
import sync_sibling_handoff  # noqa: E402


BACKEND_ONLY_PLAN = """# Salt Backend API Plani
## 7. Tema ve Bileşen İskeleti Sözleşmesi
- Salt Backend / UI Kapsam Dışı
## 9. Proposed Changes
#### [MODIFY] `src/main/java/com/app/OrderService.java`
- Hesaplama mantığı güncellenir.
"""

UI_PLAN_NO_WIREFRAME = """# Siparis Filtre Plani
## 9. Proposed Changes
#### [MODIFY] `src/pages/OrdersPage.tsx`
- Yeni filtre barı ve detay çekmecesi eklenir.
"""

UI_PLAN_WITH_WIREFRAME = """# Siparis Filtre Plani
## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi
### 7.1 🖼️ UI/UX Ön-Tasarım Önizlemesi
```text
[BEFORE: OrdersPage (/orders)]
+--------------------------------------+
| Siparisler                           |
+--------------------------------------+

[AFTER: OrdersPage (/orders)]
+--------------------------------------+
| Siparisler      [Durum v] [+ Yeni]   |
+--------------------------------------+
```
## 9. Proposed Changes
#### [MODIFY] `src/pages/OrdersPage.tsx`
- Yeni filtre barı eklenir.
"""

UI_PREVIEW_LOCKED_PLAN = """# Gercek Ekran Onizleme Plani (--ui-preview)
## 7.1 🖼️ UI/UX Ön-Tasarım Önizlemesi
- Mod: `--ui-preview` (`--ui-ux`)
- UI-PREVIEW-LOCK:
  - Gerçek Kaynak Ekran Dosyası: `src/pages/OrdersPage.tsx`
  - Üretilen Önizleme HTML Yolu: `docs/plans/wireframes/ui_preview_orders.html`
  - Kilitlenen DOM/Layout İmzası: `grid-cols-12, FilterBar + Table + DetailDrawer`
  - Kilitlenen DESIGN.md Tokenları: `--surface-ground, --primary`
## 9. Proposed Changes
#### [MODIFY] `src/pages/OrdersPage.tsx`
- Onaylanan önizleme ile birebir 1:1 uygulanır.
"""


class TestUiPredesignGate(unittest.TestCase):
    def test_backend_only_plan_triggers_no_ui_warning(self):
        res = archive_plan.check_ui_predesign_plan(BACKEND_ONLY_PLAN)
        self.assertFalse(res["ui_detected"])
        self.assertEqual(res["warnings"], [])

    def test_ui_plan_without_wireframe_emits_warning(self):
        res = archive_plan.check_ui_predesign_plan(UI_PLAN_NO_WIREFRAME)
        self.assertTrue(res["ui_detected"])
        self.assertFalse(res["has_wireframe"])
        codes = [w["code"] for w in res["warnings"]]
        self.assertIn("UI-WIREFRAME-MISSING", codes)

    def test_ui_plan_with_ascii_before_after_wireframe_passes_clean(self):
        res = archive_plan.check_ui_predesign_plan(UI_PLAN_WITH_WIREFRAME)
        self.assertTrue(res["ui_detected"])
        self.assertTrue(res["has_wireframe"])
        self.assertEqual(res["warnings"], [])

    def test_ui_preview_lock_contract_detection(self):
        res = archive_plan.check_ui_predesign_plan(UI_PREVIEW_LOCKED_PLAN)
        self.assertTrue(res["ui_detected"])
        self.assertTrue(res["has_preview_lock"])
        self.assertEqual(res["warnings"], [])

    def test_archive_plan_allow_no_wireframe_suppresses_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_src = root / "draft_plan.md"
            plan_src.write_text(UI_PLAN_NO_WIREFRAME, encoding="utf-8")

            err_warn = io.StringIO()
            with contextlib.redirect_stderr(err_warn):
                archive_plan.archive_plan(
                    plan_src,
                    root,
                    slug="no-wf-warn",
                    skip_conflict_check=True,
                    allow_no_wireframe=False,
                )
            self.assertIn("UI-WIREFRAME-MISSING", err_warn.getvalue())

            err_silent = io.StringIO()
            with contextlib.redirect_stderr(err_silent):
                archive_plan.archive_plan(
                    plan_src,
                    root,
                    slug="no-wf-allow",
                    skip_conflict_check=True,
                    allow_no_wireframe=True,
                )
            self.assertNotIn("UI-WIREFRAME-MISSING", err_silent.getvalue())

    def test_sync_sibling_handoff_ui_wireframe_expected_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            backend = ws / "backend-repo"
            frontend = ws / "frontend-repo"
            backend.mkdir()
            frontend.mkdir()
            (frontend / ".git").mkdir()
            (frontend / "KANBAN.md").write_text("# KANBAN\n\n## Bekliyor\n", encoding="utf-8")
            (frontend / "SPRINT_PLAN.md").write_text("# SPRINT\n\n### MVP Kapsam\n", encoding="utf-8")

            res = sync_sibling_handoff.sync_sibling_handoff(
                sibling_root=frontend,
                source_root=backend,
                plan_ref="docs/plans/plan_api_filter.md",
                task_id="FE-UI-012",
                task_title="Siparis filtre drawer UI uyumu",
                summary="GET /api/orders filtre parametreleri eklendi.",
                template_path=PROJECT_ROOT / ".agent" / "templates" / "HANDOFF.template.md",
                ui_wireframe_expected=True,
            )
            self.assertTrue(res["ui_wireframe_expected"])
            handoff_txt = (frontend / "HANDOFF.md").read_text(encoding="utf-8")
            kanban_txt = (frontend / "KANBAN.md").read_text(encoding="utf-8")
            sprint_txt = (frontend / "SPRINT_PLAN.md").read_text(encoding="utf-8")
            self.assertIn("UI-ÖN-TASARIM ZORUNLU", handoff_txt)
            self.assertIn("DESIGN.md", handoff_txt)
            self.assertIn("UI-ÖN-TASARIM ZORUNLU", kanban_txt)
            self.assertIn("UI-ÖN-TASARIM ZORUNLU", sprint_txt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
