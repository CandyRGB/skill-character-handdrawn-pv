import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "character-handdrawn-pv"
SPEC = importlib.util.spec_from_file_location("pv_project", SKILL / "scripts" / "project.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ProjectChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        (self.base / "a.png").write_bytes(b"test asset, not a real image")
        (self.base / "mix.wav").write_bytes(b"test audio, not a real waveform")
        self.data = {
            "schema_version": 1,
            "revision": "r2",
            "route": "adaptation",
            "output": {"width": 2560, "height": 1440, "fps": "30000/1001", "total_frames": 100},
            "timeline_policy": "contiguous",
            "assets": [{"id": "a", "path": "a.png"}],
            "audio": [{"id": "mix", "role": "mix", "path": "mix.wav", "offset_frames": -2}],
            "scenes": [
                {"id": "intro", "order": 1, "asset_id": "a", "start_frame": 0, "end_frame": 40},
                {"id": "answer-B", "order": 2, "asset_id": "a", "start_frame": 40, "end_frame": 100}
            ],
            "export_authorization": {"allowed": True, "evidence": "用户要求导出整片", "revision": None}
        }

    def tearDown(self):
        self.temp.cleanup()

    def check(self, **kwargs):
        return MODULE.validate(self.data, self.base, **kwargs)

    def test_ready_export_without_individual_approvals(self):
        self.assertTrue(self.check(for_export=True, files=True)["ok"])

    def test_draft_template_can_remain_untimed(self):
        self.data = json.loads((SKILL / "assets" / "project-template.json").read_text(encoding="utf-8"))
        result = self.check()
        self.assertTrue(result["ok"])
        self.assertTrue(result["warnings"])
        self.assertFalse(self.check(for_export=True)["ok"])

    def test_gap(self):
        self.data["scenes"][1]["start_frame"] = 41
        self.assertFalse(self.check()["ok"])

    def test_partial_draft_does_not_fabricate_missing_timings(self):
        self.data["scenes"][0]["start_frame"] = None
        self.data["scenes"][0]["end_frame"] = None
        self.assertTrue(self.check()["ok"])
        self.assertFalse(self.check(for_export=True)["ok"])

    def test_overlap_rejected_for_contiguous(self):
        self.data["scenes"][1]["start_frame"] = 39
        self.assertFalse(self.check()["ok"])

    def test_overlap_allowed_for_composited(self):
        self.data["timeline_policy"] = "composited"
        self.data["scenes"][1]["start_frame"] = 39
        self.assertTrue(self.check()["ok"])

    def test_composited_gap_still_fails(self):
        self.data["timeline_policy"] = "composited"
        self.data["scenes"][1]["start_frame"] = 41
        self.assertFalse(self.check()["ok"])

    def test_order_must_match_playback(self):
        self.data["scenes"][0]["order"] = 2
        self.data["scenes"][1]["order"] = 1
        self.assertFalse(self.check()["ok"])

    def test_duplicate_ids_and_order(self):
        self.data["scenes"][1].update(id="intro", order=1)
        result = self.check()
        self.assertFalse(result["ok"])
        self.assertGreaterEqual(len(result["errors"]), 2)

    def test_unknown_selected_asset(self):
        self.data["scenes"][0]["asset_id"] = "old-deleted-version"
        self.assertFalse(self.check()["ok"])

    def test_unused_candidate_need_not_exist(self):
        self.data["assets"].append({"id": "unused", "path": "missing-old-candidate.png"})
        self.assertTrue(self.check(for_export=True, files=True)["ok"])

    def test_bad_hash_catches_stale_file(self):
        self.data["assets"][0]["sha256"] = "0" * 64
        self.assertFalse(self.check(files=True)["ok"])
        self.data["assets"][0]["sha256"] = hashlib.sha256((self.base / "a.png").read_bytes()).hexdigest()
        self.assertTrue(self.check(files=True)["ok"])

    def test_missing_audio_file(self):
        self.data["audio"][0]["path"] = "not-present.wav"
        self.assertFalse(self.check(files=True)["ok"])

    def test_boolean_not_a_frame(self):
        self.data["scenes"][0]["start_frame"] = False
        self.assertFalse(self.check()["ok"])

    def test_invalid_rate(self):
        self.data["output"]["fps"] = "1/0"
        self.assertFalse(self.check()["ok"])

    def test_preview_only_cannot_export(self):
        self.data["export_authorization"]["allowed"] = False
        self.assertFalse(self.check(for_export=True)["ok"])
        self.assertTrue(self.check()["ok"])

    def test_old_revision_authorization(self):
        self.data["export_authorization"]["revision"] = "r1"
        self.assertFalse(self.check(for_export=True)["ok"])

    def test_no_authorization_evidence(self):
        self.data["export_authorization"]["evidence"] = ""
        self.assertFalse(self.check(for_export=True)["ok"])

    def test_read_only_and_cli_no_overwrite(self):
        init = [sys.executable, str(SKILL / "scripts" / "project.py"), "init", str(self.base), "--name", "测试项目"]
        first = subprocess.run(init, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(first.returncode, 0, first.stderr)
        manifest = self.base / "project.json"
        before = manifest.read_bytes()
        second = subprocess.run(init, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(second.returncode, 1)
        self.assertEqual(before, manifest.read_bytes())
        inspected = subprocess.run([sys.executable, str(SKILL / "scripts" / "project.py"), "check", str(manifest)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(inspected.returncode, 0, inspected.stdout)
        self.assertTrue(json.loads(inspected.stdout)["ok"])
        self.assertEqual(before, manifest.read_bytes())

    def test_malformed_input_is_reported(self):
        self.assertFalse(MODULE.validate([], self.base)["ok"])
        self.data["scenes"][0]["asset_id"] = []
        self.assertFalse(self.check()["ok"])

    def run_init(self):
        return subprocess.run(
            [sys.executable, str(SKILL / "scripts" / "project.py"), "init", str(self.base), "--name", "文档目录测试"],
            capture_output=True, text=True, encoding="utf-8"
        )

    def test_init_scaffolds_docs_and_generation_without_fake_content(self):
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stdout)
        manifest = json.loads((self.base / "project.json").read_text(encoding="utf-8"))
        self.assertTrue((self.base / manifest["directories"]["docs"] / "README.md").is_file())
        self.assertTrue((self.base / manifest["directories"]["generation"]).is_dir())
        self.assertIsNone(manifest["brief"]["lyrics_file"])
        self.assertIsNone(manifest["brief"]["storyboard_file"])
        self.assertEqual(len(list((self.base / "docs").iterdir())), 1)
        self.assertNotIn("{{", (self.base / "docs" / "README.md").read_text(encoding="utf-8"))

    def test_init_preserves_existing_document_index(self):
        (self.base / "docs").mkdir()
        index = self.base / "docs" / "README.md"
        index.write_text("用户已写好的文档索引\n", encoding="utf-8")
        before = index.read_bytes()
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(index.read_bytes(), before)

    def test_existing_manifest_does_not_trigger_folder_migration(self):
        manifest = self.base / "project.json"
        manifest.write_text(json.dumps(self.data), encoding="utf-8")
        before = manifest.read_bytes()
        result = self.run_init()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(manifest.read_bytes(), before)
        self.assertFalse((self.base / "docs").exists())
        self.assertFalse((self.base / "generation").exists())

    def test_document_paths_are_relative_to_manifest(self):
        (self.base / "docs").mkdir()
        (self.base / "docs" / "lyrics.md").write_text("歌词", encoding="utf-8")
        self.data["directories"] = {"docs": "docs", "generation": "generation"}
        self.data["brief"] = {"lyrics_file": "docs/lyrics.md", "storyboard_file": None}
        self.assertTrue(self.check(files=True, for_export=True)["ok"])
        self.data["brief"]["lyrics_file"] = "lyrics.md"
        self.assertFalse(self.check(files=True)["ok"])

    def test_missing_document_fails_only_when_checking_files(self):
        self.data["brief"] = {"storyboard_file": "docs/missing.md"}
        self.assertTrue(self.check()["ok"])
        self.assertFalse(self.check(files=True)["ok"])

    def test_legacy_manifest_and_custom_document_folder(self):
        self.assertTrue(self.check(files=True, for_export=True)["ok"])
        (self.base / "notes").mkdir()
        (self.base / "notes" / "storyboard.md").write_text("分镜", encoding="utf-8")
        self.data["directories"] = {"docs": "notes"}
        self.data["brief"] = {"storyboard_file": "notes/storyboard.md"}
        self.assertTrue(self.check(files=True, for_export=True)["ok"])

    def test_invalid_document_pointer_type(self):
        self.data["brief"] = {"lyrics_file": []}
        self.assertFalse(self.check()["ok"])

    def test_scaffold_directory_cannot_escape_project(self):
        for value in ("../outside", "/outside", "C:\\outside", "", None):
            with self.subTest(value=value):
                self.data["directories"] = {"docs": value}
                self.assertFalse(self.check()["ok"])

    def test_directory_conflict_fails_before_manifest_creation(self):
        (self.base / "docs").write_text("用户文件", encoding="utf-8")
        result = self.run_init()
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.base / "project.json").exists())
        self.assertEqual((self.base / "docs").read_text(encoding="utf-8"), "用户文件")


if __name__ == "__main__":
    unittest.main(verbosity=2)
