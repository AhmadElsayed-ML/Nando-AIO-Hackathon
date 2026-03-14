# demo.py
from Data.sample_data import BAD_BRAND_CONTENT
from Modules.content_analyzer import analyze_content_rule_based
from Modules.ai_optimizer import optimize_content_rule_based

def main():
    print("=== ORIGINAL CONTENT ===")
    print(BAD_BRAND_CONTENT)

    analysis = analyze_content_rule_based(BAD_BRAND_CONTENT)
    print("\n=== ANALYSIS RESULT ===")
    print(f"Clarity score: {analysis.clarity_score}")
    for i, issue in enumerate(analysis.issues, start=1):
        print(f"{i}. [{issue.type}] {issue.message}")
        if issue.excerpt:
            print(f"   Excerpt: {issue.excerpt}")
        if issue.suggestion:
            print(f"   Suggestion: {issue.suggestion}")

    improved = optimize_content_rule_based(BAD_BRAND_CONTENT, analysis.issues)
    print("\n=== OPTIMIZED CONTENT (RULE-BASED) ===")
    print(improved)

if __name__ == "__main__":
    main()