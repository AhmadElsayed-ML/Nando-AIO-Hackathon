# test_person2.py
import unittest

from Modules.content_analyzer import analyze_content_rule_based, Issue
from Modules.ai_optimizer import optimize_content_rule_based
from Data.sample_data import BAD_BRAND_CONTENT, GOOD_BRAND_CONTENT


class TestContentAnalyzerAndOptimizer(unittest.TestCase):
    def test_analyzer_bad_content_has_issues_and_low_score(self):
        result = analyze_content_rule_based(BAD_BRAND_CONTENT)
        self.assertIsInstance(result.clarity_score, int)
        self.assertGreaterEqual(result.clarity_score, 0)
        self.assertLess(result.clarity_score, 90)
        self.assertGreater(len(result.issues), 0)

        types = {issue.type for issue in result.issues}
        self.assertIn("vague_language", types)

    def test_analyzer_good_content_has_higher_score(self):
        bad_result = analyze_content_rule_based(BAD_BRAND_CONTENT)
        good_result = analyze_content_rule_based(GOOD_BRAND_CONTENT)
        self.assertGreaterEqual(good_result.clarity_score, bad_result.clarity_score)

    def test_optimizer_rule_based_reduces_vague_terms(self):
        # Find vague issues first
        analysis = analyze_content_rule_based(BAD_BRAND_CONTENT)
        vague_issues = [i for i in analysis.issues if i.type == "vague_language"]
        improved = optimize_content_rule_based(BAD_BRAND_CONTENT, vague_issues)

        self.assertTrue(improved.strip())
        self.assertNotIn("stuff", improved.lower())
        # At least content changed
        self.assertNotEqual(improved, BAD_BRAND_CONTENT)


if __name__ == "__main__":
    unittest.main()