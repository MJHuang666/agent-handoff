import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "shared/.agents/skills/agent-relay"
LEGACY_IN_TEMPLATE = ROOT / "shared/.agents/skills/project-role-workflow"
COMPATIBILITY_SHIM = ROOT / "compat/project-role-workflow/SKILL.md"


class AgentRelayContractTests(unittest.TestCase):
    def test_canonical_skill_identity(self):
        skill = CANONICAL / "SKILL.md"
        self.assertTrue(skill.is_file())
        self.assertIn("name: agent-relay", skill.read_text(encoding="utf-8"))
        self.assertFalse(LEGACY_IN_TEMPLATE.exists())

    def test_legacy_compatibility_is_thin(self):
        self.assertTrue(COMPATIBILITY_SHIM.is_file())
        self.assertFalse((COMPATIBILITY_SHIM.parent / "assets").exists())
        self.assertFalse((COMPATIBILITY_SHIM.parent / "references").exists())
        self.assertFalse((COMPATIBILITY_SHIM.parent / "scripts").exists())

    def test_public_documents_use_canonical_command(self):
        public_documents = (
            ROOT / "README.md",
            ROOT / "README.zh-CN.md",
            ROOT / "docs/AGENT_RELAY_USAGE.md",
            ROOT / "docs/AGENT_RELAY_USAGE.en-US.md",
        )
        for document in public_documents:
            text = document.read_text(encoding="utf-8")
            self.assertIn("$agent-relay", text, document)
            self.assertNotIn("$project-role-workflow", text, document)

    def test_knowledge_index_is_present_in_all_template_variants(self):
        documents = (
            ROOT / "shared/docs/agent/knowledge-index.md",
            CANONICAL
            / "assets/project-template/shared/docs/agent/knowledge-index.md",
            CANONICAL
            / "assets/project-template/locales/zh-CN/docs/agent/knowledge-index.md",
            CANONICAL
            / "assets/project-template/locales/en-US/docs/agent/knowledge-index.md",
        )
        for document in documents:
            text = document.read_text(encoding="utf-8")
            self.assertIn("| ID |", text, document)
            self.assertIn("ACTIVE", text, document)
            self.assertIn("SUPERSEDED", text, document)
            self.assertIn("RETIRED", text, document)

    def test_public_brand_and_migration_material_are_present(self):
        self.assertIn("lightweight multi-Agent collaboration framework", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("轻量级多 Agent 接力协作框架", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        migration = (ROOT / "docs/migration-v1.5.md").read_text(encoding="utf-8")
        self.assertIn("Uncommitted-state handoff package", migration)
        self.assertIn("未提交状态交接包", migration)


if __name__ == "__main__":
    unittest.main()
