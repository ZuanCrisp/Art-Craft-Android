import os
import tempfile
import unittest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))
from craft_suite.gitsync import AppGitSync, discover_default_branch, sanitizable_entries, parse_symref, select_tags, compare_natural  # noqa
from craft_suite.common import SyncError  # noqa
from craft_suite.common import git_auth_env, clean_env  # noqa
import gitfix
from gitfix import g


def app(slug, url):
    return {"slug": slug, "name": slug.title(), "repository": f"o/{slug}", "upstream_url": url,
            "destination_branch": slug, "sync_tags": True}


class GitEngine(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp()
        self.up = os.path.join(self.td, "up")
        self.c1, self.c2 = gitfix.make_upstream(self.up)
        self.dest = gitfix.bare(os.path.join(self.td, "dest.git"))

    def run_sync(self, slug="photocraft", up=None, overlay=None, dry=False):
        up = up or self.up
        gs = AppGitSync(app(slug, up), os.path.join(tempfile.mkdtemp(dir=self.td), "w.git"), self.dest, None, dry, overlay)
        gs.init_workspace()
        br = discover_default_branch(up, f"o/{slug}", None, None)
        gs.fetch(br)
        return gs, br, gs.sync_branch(), gs.sync_tags(True, "1-ALL", set())

    def test_default_branch_detected_not_assumed(self):
        self.assertEqual(discover_default_branch(self.up, "o/x", None, None), "trunk")
        self.assertEqual(parse_symref("ref: refs/heads/dev\tHEAD\nabc\tHEAD"), "dev")

    def test_branch_renamed_sanitised_and_only_default_branch_pushed(self):
        gs, br, b, t = self.run_sync()
        refs = g(self.dest, "for-each-ref", "--format=%(refname)")
        self.assertIn("refs/heads/photocraft", refs)
        self.assertNotIn("refs/heads/side", refs)           # other upstream branches are not mirrored
        self.assertNotIn("refs/heads/trunk", refs)
        tip = g(self.dest, "rev-parse", "refs/heads/photocraft")
        self.assertEqual(tip, self.c2)   # tip has no workflows => upstream commit pushed untouched (history preserved)
        self.assertEqual(b["status"], "created")

    def test_workflow_files_archived_on_tag_and_original_kept_as_parent(self):
        gs, br, b, t = self.run_sync()
        tag = g(self.dest, "rev-parse", "refs/tags/photocraft--v1.0.0")
        self.assertNotEqual(tag, self.c1)
        self.assertEqual(g(self.dest, "rev-parse", tag + "^"), self.c1)
        names = g(self.dest, "ls-tree", "-r", "--name-only", tag).splitlines()
        self.assertNotIn(".github/workflows/ci.yml", names)
        self.assertIn(".upstream-archive/workflows/ci.yml", names)
        self.assertIn(".upstream-archive/github/dependabot.yml", names)
        self.assertTrue(any(n.startswith(".upstream-archive/tag-metadata/") for n in names))
        self.assertEqual(t["sanitized"], 1)

    def test_annotated_tag_object_preserved_verbatim(self):
        gs, br, b, t = self.run_sync()
        src = g(self.up, "rev-parse", "v2.0.0")
        self.assertEqual(g(self.dest, "rev-parse", "refs/tags/photocraft--v2.0.0"), src)
        self.assertEqual(g(self.dest, "cat-file", "-t", "refs/tags/photocraft--v2.0.0"), "tag")

    def test_idempotent_second_run_pushes_nothing(self):
        self.run_sync()
        before = g(self.dest, "for-each-ref", "--format=%(refname) %(objectname)")
        gs, br, b, t = self.run_sync()
        self.assertEqual(b["status"], "unchanged")
        self.assertEqual((t["created"], t["updated"], t["unchanged"]), (0, 0, 2))
        self.assertEqual(before, g(self.dest, "for-each-ref", "--format=%(refname) %(objectname)"))

    def test_moved_upstream_tag_updates_and_deleted_tag_is_only_reported(self):
        self.run_sync()
        g(self.up, "tag", "-f", "v1.0.0", self.c2)
        g(self.up, "tag", "-d", "v2.0.0")
        gs, br, b, t = self.run_sync()
        self.assertEqual(t["updated"], 1)
        self.assertEqual(g(self.dest, "rev-parse", "refs/tags/photocraft--v1.0.0"), self.c2)
        self.assertEqual(t["stale"], ["photocraft--v2.0.0"])
        self.assertIn("photocraft--v2.0.0", g(self.dest, "tag"))   # never pruned

    def test_two_apps_same_tag_names_do_not_collide(self):
        up2 = os.path.join(self.td, "up2")
        gitfix.make_upstream(up2, branch="main", seed="2")
        gitfix.write(up2, "other.txt", "different\n"); g(up2, "add", "-A"); g(up2, "commit", "-qm", "other")
        self.run_sync("photocraft")
        self.run_sync("vectorcraft", up=up2)
        tags = g(self.dest, "tag").splitlines()
        self.assertEqual(sorted(tags), ["photocraft--v1.0.0", "photocraft--v2.0.0", "vectorcraft--v1.0.0", "vectorcraft--v2.0.0"])
        branches = g(self.dest, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
        self.assertEqual(sorted(branches), ["photocraft", "vectorcraft"])
        # independent histories: no shared root between the two branches
        self.assertEqual(g(self.dest, "merge-base", "photocraft", "vectorcraft", check=False), "")

    def test_craft_overlay_installs_controller_and_archives_upstream_workflows(self):
        g(self.up, "checkout", "-q", "-b", "wf")
        gitfix.write(self.up, ".github/workflows/release.yml", "on: push\n")
        g(self.up, "add", "-A"); g(self.up, "commit", "-qm", "wf")
        g(self.up, "checkout", "-q", "trunk"); g(self.up, "merge", "-q", "wf")
        overlay = {".github/workflows/sync-craft.yml": b"name: x\n", "SYNC-INFO.md": b"hi\n"}
        gs, br, b, t = self.run_sync("craft", overlay=overlay)
        tip = g(self.dest, "rev-parse", "refs/heads/craft")
        names = g(self.dest, "ls-tree", "-r", "--name-only", tip).splitlines()
        self.assertEqual([n for n in names if n.startswith(".github/")], [".github/workflows/sync-craft.yml"])
        self.assertIn(".upstream-archive/workflows/release.yml", names)
        gs2, _, b2, _ = self.run_sync("craft", overlay=overlay)
        self.assertEqual(b2["status"], "unchanged")

    def test_dry_run_changes_nothing(self):
        gs, br, b, t = self.run_sync(dry=True)
        self.assertEqual(g(self.dest, "for-each-ref"), "")
        self.assertEqual(b["status"], "planned")

    def _fresh(self, slug="photocraft"):
        gs = AppGitSync(app(slug, self.up), os.path.join(tempfile.mkdtemp(dir=self.td), "w.git"), self.dest, None, False, None)
        gs.init_workspace()
        gs.fetch(discover_default_branch(self.up, f"o/{slug}", None, None))
        return gs

    def test_tag_range_keeps_newest_n_and_release_tags_always_included(self):
        t = self._fresh().sync_tags(True, "1-1", set())
        self.assertEqual(sorted(g(self.dest, "tag").splitlines()), ["photocraft--v2.0.0"])
        self.assertEqual((t["selected"], t["upstream_total"]), (1, 2))
        t = self._fresh().sync_tags(True, "1-1", {"v1.0.0"})           # a mirrored release needs v1.0.0
        self.assertEqual(sorted(g(self.dest, "tag").splitlines()), ["photocraft--v1.0.0", "photocraft--v2.0.0"])
        self.assertEqual(t["stale"], [])                                  # still exists upstream: not stale

    def test_tags_disabled_mirrors_only_release_tags_and_deletes_nothing(self):
        self._fresh().sync_tags(True, "1-ALL", set())
        t = self._fresh().sync_tags(False, "1-ALL", {"v2.0.0"})
        self.assertEqual(sorted(g(self.dest, "tag").splitlines()), ["photocraft--v1.0.0", "photocraft--v2.0.0"])
        dest2 = gitfix.bare(os.path.join(self.td, "dest2.git"))
        gs = AppGitSync(app("photocraft", self.up), os.path.join(self.td, "w2.git"), dest2, None, False, None)
        gs.init_workspace(); gs.fetch("trunk")
        gs.sync_tags(False, "1-ALL", {"v2.0.0"})
        self.assertEqual(g(dest2, "tag"), "photocraft--v2.0.0")

    def test_auth_header_scoped_to_destination_url_only(self):
        env = git_auth_env("https://github.com/me/dest.git", "SECRET")
        self.assertEqual(env["GIT_CONFIG_KEY_0"], "http.https://github.com/me/dest.git.extraheader")
        self.assertNotIn("SECRET", " ".join(f"{k}={v}" for k, v in env.items() if k != "GIT_CONFIG_VALUE_0"))
        self.assertNotIn("GIT_CONFIG_COUNT", git_auth_env("/local/path", "SECRET"))
        self.assertNotIn("GIT_CONFIG_COUNT", clean_env())


class TagSelection(unittest.TestCase):
    NAMES = ["v1.2.0", "v1.10.0", "v1.9.0", "v10.0.0", "v2.0.0"]

    def test_natural_not_lexical_order(self):
        self.assertEqual(select_tags(self.NAMES, "1-ALL"), ["v10.0.0", "v2.0.0", "v1.10.0", "v1.9.0", "v1.2.0"])
        self.assertGreater(compare_natural("v1.10.0", "v1.9.0"), 0)

    def test_range_n_and_case_insensitive_all(self):
        self.assertEqual(select_tags(self.NAMES, "1-2"), ["v10.0.0", "v2.0.0"])
        self.assertEqual(len(select_tags(self.NAMES, "1-all")), 5)
        self.assertEqual(len(select_tags(self.NAMES, "1-1000")), 5)

    def test_invalid_ranges_rejected(self):
        for bad in ("2-5", "1-0", "abc", "1-", "1-10000000"):
            with self.assertRaises(SyncError):
                select_tags(self.NAMES, bad)


if __name__ == "__main__":
    unittest.main()
