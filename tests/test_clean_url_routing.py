import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / ".agent" / "skills" / "react-best-practices" / "SKILL.md"
REFERENCE_DOC = ROOT / ".agent" / "skills" / "react-best-practices" / "references" / "clean-url-routing-standard.md"

class TestCleanUrlRoutingStandard(unittest.TestCase):
    def test_01_reference_document_exists(self):
        self.assertTrue(
            REFERENCE_DOC.is_file(),
            f"Eksik referans dokümanı: {REFERENCE_DOC}"
        )

    def test_02_reference_doc_contains_both_scenarios(self):
        self.assertTrue(REFERENCE_DOC.is_file())
        content = REFERENCE_DOC.read_text(encoding="utf-8")
        self.assertIn("/portal/haberler/:newsSlug", content)
        self.assertIn("slugify", content)
        self.assertIn("/portal/profil-ayarlari", content)
        self.assertIn("useNavigate", content)
        self.assertIn("useLocation", content)
        self.assertIn("location.state", content)

    def test_03_reference_doc_contains_f5_fallback_and_error_boundary(self):
        self.assertTrue(REFERENCE_DOC.is_file())
        content = REFERENCE_DOC.read_text(encoding="utf-8")
        self.assertIn("F5", content)
        self.assertIn("Fallback", content)
        self.assertIn("createBrowserRouter", content)
        self.assertIn("RouterProvider", content)

    def test_04_skill_md_links_clean_url_standard(self):
        self.assertTrue(SKILL_MD.is_file())
        content = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("clean-url-routing-standard.md", content)
        self.assertIn("Clean URL", content)

    def test_05_turkish_slugify_logic_contract(self):
        self.assertTrue(REFERENCE_DOC.is_file())
        content = REFERENCE_DOC.read_text(encoding="utf-8")
        self.assertIn("trMap", content)
        self.assertIn("replace(/[çÇğĞıIİöÖşŞüÜ]/g", content)

if __name__ == "__main__":
    unittest.main()
