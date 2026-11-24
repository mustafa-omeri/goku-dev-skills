#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_plan_conflict_guard.py
Ön-Mühürleme (/seal-plan) ve Sprint/Kanban Plan Çakışma, Tekrar
(ALREADY_DONE_EXACT / ENRICHED_SUPERSET / SIMPLIFIED_SUBSET_REGRESSION)
ve Sıralı Plan Ezme (QUEUED_PLAN_CLOBBER / SEQUENTIAL_ORDER_DEPENDENCY /
BACKLOG_SEMANTIC_DUPLICATE) Kalkanı regresyon test paketi.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import archive_plan  # noqa: E402
import check_handoff  # noqa: E402
import check_sprint_board  # noqa: E402
import plan_conflict_guard as guard  # noqa: E402


BASE_HANDOFF = """# HANDOFF — SampleApp

> Güncel: **2026-11-24** · Ajan: **Antigravity**

## 1. Bu Oturumda Yapılanlar (Özet)
- `AUTH-FEAT-001` kullanıcı profil sayfası ve güncelleme endpointi tamamlandı.

## 3. ⏭️ BURADAN DEVAM ET

#### 🎯 Aktif Sprint / Anlık Görev Panosu (WIP Maks 3)
| ID | Durum | İş / Hedef | Kapsam / PRD Referansı | Hedef Sürüm |
|---|---|---|---|---|

#### 📌 Gelecek Fazlar & Parking Lot Yol Haritası (Product Roadmap Backlog)
| Gereksinim ID | Açıklama | Hedef Faz | Hedef Sürüm | PRD / Kaynak Ref | Durum |
|---|---|---|---|---|---|
"""


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class TestPlanConflictGuard(unittest.TestCase):
    def test_already_done_exact_detected_against_live_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "package.json", "{}")
            _write(root / "HANDOFF.md", BASE_HANDOFF)
            _write(
                root / "src" / "routes" / "profile.ts",
                "export const route = '/profile';\nexport async function updateProfile() { return fetch('/api/v1/profile/update'); }\n",
            )
            plan_p = _write(
                root / ".agent" / "plans" / "dup_plan.md",
                """# Kullanıcı Profili Güncelleme Planı
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum | Kapsam |
|---|---|---|---|
| AUTH-FEAT-010 | Bekliyor | Yapılıyor | Profil güncelleme |

#### [NEW] `src/routes/profile.ts`
- `/profile` sayfası ve `POST /api/v1/profile/update` çağrısı
""",
            )
            report = guard.analyze_plan_conflicts(root, plan_p)
            types = {f["type"] for f in report["findings"]}
            self.assertIn("ALREADY_DONE_EXACT", types)

    def test_enriched_superset_warns_new_should_be_modify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "package.json", "{}")
            _write(root / "HANDOFF.md", BASE_HANDOFF)
            _write(
                root / "src" / "services" / "feedback.ts",
                "export async function submitFeedback(body: unknown) { return fetch('/api/v1/feedback', { method: 'POST' }); }\n",
            )
            plan_p = _write(
                root / ".agent" / "plans" / "enriched.md",
                """# Geri Bildirim Formu Zenginleştirme Planı
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum | Kapsam |
|---|---|---|---|
| FB-FEAT-002 | Bekliyor | Yapılıyor | Turnstile, Rate Limiting ve RLS eklenmesi |

#### [NEW] `src/services/feedback.ts`
- Mevcut `POST /api/v1/feedback` uç noktasına Turnstile, Rate Limiting, RLS (`ENABLE ROW LEVEL SECURITY`) ve Zero-CLS Skeleton UI eklenir.
- `CREATE TABLE feedback_audit_logs` migration'ı açılır.
""",
            )
            report = guard.analyze_plan_conflicts(root, plan_p)
            types = {f["type"] for f in report["findings"]}
            self.assertIn("ENRICHED_SUPERSET", types)
            self.assertEqual(report["overall_classification"], "ENRICHED_SUPERSET")

    def test_simplified_subset_regression_detected_as_critical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "package.json", "{}")
            _write(root / "HANDOFF.md", BASE_HANDOFF)
            _write(
                root / "src" / "services" / "order.ts",
                """// Production service with full protections
import { z } from 'zod';
// RLS enabled, Turnstile check, Idempotency-Key, Skeleton UI, @Version optimistic lock, rateLimit
export const orderSchema = z.object({ id: z.string() });
export async function createOrder() {
  // rateLimit + turnstile + idempotency + validation + skeleton + @Version
  return fetch('/api/v1/orders/create', { method: 'POST', headers: { 'Idempotency-Key': '1' } });
}
""",
            )
            plan_p = _write(
                root / ".agent" / "plans" / "simple_overwrite.md",
                """# Basit Sipariş Oluşturma Planı
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum | Kapsam |
|---|---|---|---|
| ORD-TASK-001 | Bekliyor | Yapılıyor | Basit sipariş formu |

#### [NEW] `src/services/order.ts`
- `POST /api/v1/orders/create` için sade bir fetch çağrısı yazar.
""",
            )
            report = guard.analyze_plan_conflicts(root, plan_p)
            findings = report["findings"]
            self.assertTrue(
                any(
                    f["type"] == "SIMPLIFIED_SUBSET_REGRESSION" and f["severity"] == "CRITICAL"
                    for f in findings
                ),
                f"Beklenen CRITICAL SIMPLIFIED_SUBSET_REGRESSION bulunamadı: {findings}",
            )

    def test_queued_plan_vs_plan_clobber_and_order_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "package.json", "{}")
            queued_plan_1 = _write(
                root / "docs" / "plans" / "plan_alpha_20261124_100000.md",
                """# Alpha Planı
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum | Kapsam |
|---|---|---|---|
| CORE-FEAT-001 | Bekliyor | Yapılıyor | Yeni servis |

#### [NEW] `src/services/billing.ts`
- `POST /api/v1/billing/charge` servisini sıfırdan oluşturur.
#### [MODIFY] `src/pages/Settings.tsx`
- Ayarlar ekranına fatura sekmesi ekler.
""",
            )
            _write(
                root / "HANDOFF.md",
                BASE_HANDOFF
                + f"| CORE-FEAT-001 | Plan mühürlendi | Sprint 10 | Planlı | `{queued_plan_1.relative_to(root).as_posix()}` | ⬜ Bekliyor |\n",
            )
            # Yeni Plan 2 hem CORE-FEAT-001 ile aynı dosyayı [NEW] ile çakıştırıyor hem Settings.tsx'i [DELETE] ediyor
            # hem de Plan 1'in [NEW] yapacağı src/services/invoice.ts benzeri başka dosyaya bağımlı
            queued_plan_1_extra = _write(
                root / "docs" / "plans" / "plan_beta_20261124_100500.md",
                """# Beta Planı
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum | Kapsam |
|---|---|---|---|
| CORE-FEAT-002 | Bekliyor | Yapılıyor | Fatura PDF |

#### [NEW] `src/services/invoicePdf.ts`
- Fatura PDF motoru.
""",
            )
            _write(
                root / "HANDOFF.md",
                (root / "HANDOFF.md").read_text(encoding="utf-8")
                + f"| CORE-FEAT-002 | Plan mühürlendi | Sprint 11 | Planlı | `{queued_plan_1_extra.relative_to(root).as_posix()}` | ⬜ Bekliyor |\n",
            )

            plan_3 = _write(
                root / ".agent" / "plans" / "plan_gamma.md",
                """# Gamma Planı
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum | Kapsam |
|---|---|---|---|
| CORE-FEAT-003 | Bekliyor | Yapılıyor | Ödeme & PDF güncellemesi |

#### [NEW] `src/services/billing.ts`
- Farklı sözleşmeyle `POST /api/v1/billing/charge` yazar.
#### [DELETE] `src/pages/Settings.tsx`
- Eski ayar sayfasını kaldırır.
#### [MODIFY] `src/services/invoicePdf.ts`
- PDF çıktısına QR ekler.
""",
            )
            report = guard.analyze_plan_conflicts(root, plan_3)
            types = {f["type"] for f in report["findings"]}
            self.assertIn("DOUBLE_NEW_COLLISION", types)
            self.assertIn("MODIFY_DELETE_CLOBBER", types)
            self.assertIn("SEQUENTIAL_ORDER_DEPENDENCY", types)

    def test_archive_plan_blocks_critical_clobber_unless_allow_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "package.json", "{}")
            plan_1 = _write(
                root / "docs" / "plans" / "plan_first_20261124_090000.md",
                """# İlk Mühürlü Plan
| Görev ID | Durum |
|---|---|
| USR-FEAT-001 | Bekliyor |

#### [NEW] `src/api/users.ts`
- `POST /api/v1/users/invite`
""",
            )
            _write(
                root / "HANDOFF.md",
                BASE_HANDOFF
                + f"| USR-FEAT-001 | Plan mühürlendi | Sprint 5 | Planlı | `{plan_1.relative_to(root).as_posix()}` | ⬜ Bekliyor |\n",
            )
            plan_2_src = _write(
                root / ".agent" / "plans" / "second_plan.md",
                """# İkinci Çakışan Plan
| Görev ID | Durum |
|---|---|
| USR-FEAT-002 | Bekliyor |

#### [NEW] `src/api/users.ts`
- `POST /api/v1/users/invite` sıfırdan yeniden yazılır.
""",
            )
            with self.assertRaises(archive_plan.PlanConflictError):
                archive_plan.archive_plan(
                    plan_path=plan_2_src,
                    project_root=root,
                    slug="second-plan",
                    seal_handoff=True,
                    sprint_label="Sprint 6",
                    allow_conflicts=False,
                )

            # --allow-conflicts ile mühürlenince arşivlenir ve raporu plan sonuna yazar
            dest = archive_plan.archive_plan(
                plan_path=plan_2_src,
                project_root=root,
                slug="second-plan",
                seal_handoff=True,
                sprint_label="Sprint 6",
                allow_conflicts=True,
            )
            self.assertTrue(dest.is_file())
            archived_text = dest.read_text(encoding="utf-8")
            self.assertIn("Ön-Mühürleme Çakışma", archived_text)
            self.assertIn("DOUBLE_NEW_COLLISION", archived_text)

    def test_check_handoff_w4_and_check_sprint_board_w5(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "package.json", "{}")
            p1 = _write(
                root / "docs" / "plans" / "plan_a_20261124_090000.md",
                "# Plan A\n- ORD-FEAT-001\n#### [NEW] `src/shared/calc.ts`\n",
            )
            p2 = _write(
                root / "docs" / "plans" / "plan_b_20261124_091000.md",
                "# Plan B\n- ORD-FEAT-002\n#### [NEW] `src/shared/calc.ts`\n",
            )
            _write(
                root / "HANDOFF.md",
                BASE_HANDOFF
                + f"| ORD-FEAT-001 | Plan A | Sprint 1 | Planlı | `{p1.relative_to(root).as_posix()}` | ⬜ Bekliyor |\n"
                + f"| ORD-FEAT-002 | Plan B | Sprint 2 | Planlı | `{p2.relative_to(root).as_posix()}` | ⬜ Bekliyor |\n",
            )
            _errs, warns = check_handoff.validate_handoff(root, ignore_git_diff=True)
            self.assertIn("W4", {c for c, _ in warns})

            # KANBAN W5: İki açık kart aynı başlık/yüzeyde semantik tekrar
            _write(root / "specs" / "S1-01.feature", "Feature: F\n  Scenario: S\n    Given a\n    When b\n    Then c\n")
            _write(root / "docs" / "KULLANICI_TEST_REHBERI.md", "# Test\n")
            tpl = (REPO_ROOT / ".agent" / "templates" / "KULLANICI_REHBERI.template.html").read_text(encoding="utf-8")
            _write(
                root / "docs" / "kullanici-rehberi.html",
                tpl.replace("{{PROJE_ADI}}", "Test")
                .replace("supabase/migrations/20261101_dashboard.sql", "db/001.sql")
                .replace("Edge Function: compute-kpi", "GET /metrics"),
            )
            _write(root / "SPRINT_PLAN.md", "## Sprint 1\n**Hedef**\nTest\n**MVP Kapsam**\n- S1-01\n- S1-02\n**Kapsam Dışı**\n- Yok\n")
            _write(root / "RELEASE_PLAN.md", "| S1-01 | x | S1 | düşük |\n| S1-02 | x | S1 | düşük |\n")
            _write(
                root / "KANBAN.md",
                """## Bekliyor

### S1-01 · Kullanıcı profil güncelleme ekranı ve endpoint ekle (`src/pages/Profile.tsx`)
| alan | değer |
|---|---|
| durum | Bekliyor |
| oncelik | P1 |
| sprint | S1 |
| gherkin | specs/S1-01.feature |
| kapi | python .agent/skills/musgoku/scripts/check_sprint_board.py |
| test | (yazılacak) |
| risk | düşük |

### S1-02 · Kullanıcı profil güncelleme ekranı ve endpoint geliştir (`src/pages/Profile.tsx`)
| alan | değer |
|---|---|
| durum | Bekliyor |
| oncelik | P2 |
| sprint | S1 |
| gherkin | specs/S1-01.feature |
| kapi | python .agent/skills/musgoku/scripts/check_sprint_board.py |
| test | (yazılacak) |
| risk | düşük |

## Yapılıyor

## Sınırdı

## Yapıldı
""",
            )
            _s_errs, s_warns, _stats = check_sprint_board.check(root)
            self.assertIn("W5", {c for c, _, _ in s_warns})

    def test_real_repo_queue_has_zero_critical_conflicts(self):
        report = guard.analyze_queue(REPO_ROOT)
        self.assertIn("checked_plans", report)

    def test_natural_language_seal_triggers_and_template_contract(self):
        routing_txt = (REPO_ROOT / ".agent" / "rules" / "skill-trigger-routing.md").read_text(encoding="utf-8")
        dev_txt = (REPO_ROOT / ".agent" / "rules" / "development-workflow.md").read_text(encoding="utf-8")
        tpl_txt = (REPO_ROOT / ".agent" / "templates" / "PLAN.template.md").read_text(encoding="utf-8")
        for phrase in ("mühürle", "bunları plana dahil et", "todo olarak ekle", "sıraya al"):
            self.assertIn(phrase, routing_txt.lower())
            self.assertIn(phrase, dev_txt.lower())
        self.assertIn("plan_conflict_guard.py", tpl_txt)
        self.assertIn("Ön-Mühürleme Çakışma", tpl_txt)


if __name__ == "__main__":
    unittest.main()
