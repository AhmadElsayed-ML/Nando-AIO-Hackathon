# validator.py
# Runs 8 test questions against ORIGINAL and OPTIMIZED Nando content.
# Produces a before/after score report showing improvement %.
#
# Usage:
#   python validator.py --original Data/original_content.txt --optimized Data/optimized_content.txt
#   python validator.py  (uses built-in fallback content for demo purposes)

import argparse
import json
import os
from datetime import datetime
from Utils.scoring import score_question

# ─────────────────────────────────────────────
# The 8 test questions — sourced directly from
# Jonas (Head of Innovation) and the adjuvants PDF
# ─────────────────────────────────────────────
TEST_QUESTIONS = [
    "Can I use Nando microbial products in soil with pH 4?",
    "What microbial products work in very low pH conditions?",
    "How does Perifolis improve spray coverage on leaves?",
    "What is the difference between foliar and soil adjuvants?",
    "How do water conditioners improve pesticide effectiveness?",
    "What is alkaline hydrolysis and how do adjuvants prevent it?",
    "Which Nando product reduces spray drift?",
    "How do soil superspreaders prevent pesticide leaching?",
]

# ─────────────────────────────────────────────
# Fallback content for demo if no files provided
# ─────────────────────────────────────────────
FALLBACK_ORIGINAL = """
Nando is an innovative solutions company for agriculture.
We develop products that help farmers.
Our products include various biological solutions.
Contact us for more information about our products.
We work with many crops across different conditions.
"""

FALLBACK_OPTIMIZED = """
Nando Bio is a Lithuanian biotechnology company specializing in microbiological 
biostimulants and adjuvants for field crops, vegetables, fruit, and exotic species.

MICROBIALS AND pH:
Nando's microbial products are designed to survive in a wide pH range. 
Although bulk spray pH may appear low (e.g. pH 4), the pH in the root zone 
(rhizosphere) is typically 0.5–1.5 units higher due to root exudates and 
biological activity. This means microbials can work effectively even when 
applied at low bulk pH. Always check the specific product datasheet for 
minimum application pH guidelines.

ADJUVANTS — FOLIAR vs SOIL:
Foliar adjuvants (e.g. Perifolis): organosilicone-based superspreaders that 
reduce surface tension, allowing a single droplet to spread to 10x its original 
diameter on the leaf. This improves coverage and penetration through the waxy 
cuticle. Increases water use efficiency by up to 30%.

Soil adjuvants (e.g. Periterra): reduce interfacial tension between water and 
soil particles, promoting uniform horizontal wetting (capillary spread) in the 
root zone. Prevents finger flow and pesticide leaching into deeper soil layers.

WATER CONDITIONERS AND pH BUFFERS:
Nando's pH Water Power is a water conditioner and pH buffer that:
- Sequesters calcium and magnesium ions that cause hardness lockout
- Prevents alkaline hydrolysis (pesticides can lose 50% efficacy in under 1 hour
  in alkaline water at pH above 7)
- Keeps spray solution pH in the optimal range of 4–6 for most pesticides

DRIFT REDUCTION:
Targetum is Nando's drift-reduction adjuvant. It modifies fluid viscoelasticity 
to collapse ultra-fine mist droplets (<150 microns) into larger, stable droplets. 
Reduces off-target spray movement by up to 70%.

RAINFASTNESS:
Nando's rainfastness technology ensures 70–90% of the applied product remains 
on the leaf even if rain occurs shortly after application.

PRODUCT OVERVIEW:
- Perifolis: foliar superspreader, improves leaf coverage, +30% water efficiency
- Periterra: soil superspreader, uniform root zone wetting, prevents leaching
- Targetum: drift-reduction adjuvant, reduces off-target movement by 70%
- pH Water Power: water conditioner, prevents hardness lockout and alkaline hydrolysis
"""


def load_content(filepath: str, fallback: str) -> str:
    """Load content from file, or use fallback if file doesn't exist."""
    if filepath and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    print(f"  [!] File not found: '{filepath}' — using fallback demo content.")
    return fallback


def run_validation(content: str, label: str, use_anthropic: bool = True) -> list:
    """Run all 8 questions against given content. Returns list of result dicts."""
    print(f"\n{'='*60}")
    print(f"  Running validation on: {label}")
    print(f"{'='*60}")
    results = []
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"  [{i}/8] {question[:60]}...")
        result = score_question(question, content, use_anthropic)
        result["label"] = label
        results.append(result)
        print(f"        accuracy={result['accuracy_score']}/10  nando={result['nando_score']}/10  combined={result['combined_score']}/10")
    return results


def compute_summary(results: list) -> dict:
    """Compute aggregate scores from a list of result dicts."""
    n = len(results)
    if n == 0:
        return {}
    total_accuracy = sum(r["accuracy_score"] for r in results)
    total_nando = sum(r["nando_score"] for r in results)
    total_combined = sum(r["combined_score"] for r in results)
    return {
        "avg_accuracy": round(total_accuracy / n, 1),
        "avg_nando": round(total_nando / n, 1),
        "avg_combined": round(total_combined / n, 1),
        "total_score": round((total_combined / n) * 10, 1),  # out of 100
    }


def print_report(before_results: list, after_results: list):
    """Print a clean before/after comparison table to the console."""
    before_summary = compute_summary(before_results)
    after_summary = compute_summary(after_results)

    improvement = round(
        ((after_summary["total_score"] - before_summary["total_score"]) /
         max(before_summary["total_score"], 1)) * 100, 1
    )

    print(f"\n{'='*60}")
    print("  NANDO AIO — BEFORE / AFTER VALIDATION REPORT")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"\n{'Question':<52} {'Before':>6} {'After':>6} {'Delta':>6}")
    print("-" * 72)

    for b, a in zip(before_results, after_results):
        q = b["question"][:50]
        delta = round(a["combined_score"] - b["combined_score"], 1)
        delta_str = f"+{delta}" if delta >= 0 else str(delta)
        print(f"  {q:<50} {b['combined_score']:>6} {a['combined_score']:>6} {delta_str:>6}")

    print("-" * 72)
    print(f"\n  OVERALL SCORE (out of 100)")
    print(f"  Before:  {before_summary['total_score']:.1f} / 100")
    print(f"  After:   {after_summary['total_score']:.1f} / 100")
    print(f"  Change:  +{improvement}% improvement in AI comprehension")
    print(f"\n  Breakdown:")
    print(f"  {'Metric':<20} {'Before':>8} {'After':>8}")
    print(f"  {'Accuracy (avg)':<20} {before_summary['avg_accuracy']:>8} {after_summary['avg_accuracy']:>8}")
    print(f"  {'Nando mentions (avg)':<20} {before_summary['avg_nando']:>8} {after_summary['avg_nando']:>8}")
    print(f"{'='*60}\n")


def save_report(before_results: list, after_results: list, output_path: str = "validation_report.json"):
    """Save full detailed results to JSON for use in Streamlit UI."""
    before_summary = compute_summary(before_results)
    after_summary = compute_summary(after_results)

    improvement = round(
        ((after_summary["total_score"] - before_summary["total_score"]) /
         max(before_summary["total_score"], 1)) * 100, 1
    )

    report = {
        "generated_at": datetime.now().isoformat(),
        "improvement_percent": improvement,
        "before": {
            "summary": before_summary,
            "results": before_results,
        },
        "after": {
            "summary": after_summary,
            "results": after_results,
        }
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  Full report saved to: {output_path}")
    return report


def main():
    parser = argparse.ArgumentParser(description="Nando AIO — Before/After Validation")
    parser.add_argument("--original", type=str, default="", help="Path to original content .txt file")
    parser.add_argument("--optimized", type=str, default="", help="Path to optimized content .txt file")
    parser.add_argument("--output", type=str, default="Data/validation_report.json", help="Output JSON path")
    parser.add_argument("--openai", action="store_true", help="Use OpenAI instead of Anthropic")
    args = parser.parse_args()

    use_anthropic = not args.openai

    # Load content
    print("\n  Loading content...")
    original_content = load_content(args.original, FALLBACK_ORIGINAL)
    optimized_content = load_content(args.optimized, FALLBACK_OPTIMIZED)

    # Run validation
    before_results = run_validation(original_content, "BEFORE (original)", use_anthropic)
    after_results = run_validation(optimized_content, "AFTER (optimized)", use_anthropic)

    # Print report
    print_report(before_results, after_results)

    # Save JSON for Streamlit
    report = save_report(before_results, after_results, args.output)

    return report


if __name__ == "__main__":
    main()
