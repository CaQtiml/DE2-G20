# analytics.py
import json
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import os
import traceback

# Configuration
DATA_FILES = {
    "commits": "data_commits.jsonl",
    "tdd": "data_tdd.jsonl",
    "lang": "data_lang.jsonl",
    "tdd_cicd": "data_tdd_cicd.jsonl"
}
OUTPUT_DIR = "results"
ERROR_FILE = "result.txt"

def setup():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    # Clear previous error file
    with open(ERROR_FILE, "w") as f:
        pass

def log_error(error_msg):
    """Write errors to result.txt"""
    with open(ERROR_FILE, "a") as f:
        f.write(f"ERROR: {error_msg}\n")

def load_data(file_path):
    """Load and validate data from JSONL files"""
    data = []
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        data.append(entry)
                    except json.JSONDecodeError as e:
                        log_error(f"Invalid JSON in {file_path}: {e}")
        return data
    except Exception as e:
        log_error(f"Failed to load {file_path}: {e}")
        return []

def analyze_q1_languages():
    """Q1: Top 10 programming languages by project count"""
    try:
        lang_data = load_data(DATA_FILES["lang"])
        lang_counts = Counter()
        
        for entry in lang_data:
            if isinstance(entry, dict):
                lang_counts.update(entry)

        # Optional: filter out Unknown if undesired
        if "Unknown" in lang_counts:
            del lang_counts["Unknown"]

        top10 = lang_counts.most_common(10)
        
        # Plot
        plt.figure(figsize=(12, 6))
        languages, counts = zip(*top10)
        plt.bar(languages, counts, color='skyblue')
        plt.title("Top 10 Programming Languages by Project Count")
        plt.xlabel("Language")
        plt.ylabel("Number of Projects")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/q1_top_languages.png")
        plt.close()
        
        return top10
    except Exception as e:
        log_error(f"Q1 Analysis failed: {traceback.format_exc()}")
        return []

def analyze_q2_commits():
    """Q2: Top 10 most active repos by commits"""
    try:
        commit_data = load_data(DATA_FILES["commits"])
        repo_commits = Counter()
        
        for entry in commit_data:
            if isinstance(entry, dict):
                repo = entry.get("repo", "Unknown")
                count = entry.get("commit_count", 0)
                repo_commits[repo] += count

            if count == 1000:
                log_error(f"Possible 1000-result GitHub API cap hit for repo: {repo}")

        
        top10 = repo_commits.most_common(10)
        
        # Plot
        plt.figure(figsize=(12, 6))
        repos, counts = zip(*top10)
        plt.barh(repos, counts, color='lightgreen')
        plt.title("Top 10 Most Active Repositories by Commits")
        plt.xlabel("Number of Commits")
        plt.ylabel("Repository")
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/q2_top_commits.png")
        plt.close()
        
        return top10
    except Exception as e:
        log_error(f"Q2 Analysis failed: {traceback.format_exc()}")
        return []

def analyze_q3_tdd():
    """Q3: Top 10 languages with test-driven development"""
    try:
        tdd_data = load_data(DATA_FILES["tdd"])
        tdd_counts = Counter()
        
        for entry in tdd_data:
            if isinstance(entry, dict):
                lang = entry.get("language", "Unknown")
                count = entry.get("project_count", 0)
                if lang != "Unknown":
                    tdd_counts[lang] += count

        
        top10 = tdd_counts.most_common(10)
        
        # Plot
        plt.figure(figsize=(12, 6))
        languages, counts = zip(*top10)
        plt.pie(counts, labels=languages, autopct='%1.1f%%', startangle=140)
        plt.title("Top 10 Languages with Test-Driven Development")
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/q3_tdd_adoption.png")
        plt.close()
        
        return top10
    except Exception as e:
        log_error(f"Q3 Analysis failed: {traceback.format_exc()}")
        return []

def analyze_q4_tdd_cicd():
    try:
        cicd_data = load_data(DATA_FILES["tdd_cicd"])
        cicd_counts = Counter()

        for entry in cicd_data:
            if isinstance(entry, dict):
                cicd_counts.update(entry)

        # Optional: remove Unknown
        if "Unknown" in cicd_counts:
            del cicd_counts["Unknown"]

        top10 = cicd_counts.most_common(10)

        # Plotting
        plt.figure(figsize=(12, 6))
        languages, counts = zip(*top10)
        plt.bar(languages, counts, color='salmon')
        plt.title("Top 10 Languages with TDD and CI/CD Adoption")
        plt.xlabel("Language")
        plt.ylabel("Number of Projects")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/q4_tdd_cicd.png")
        plt.close()

        return top10

    except Exception as e:
        log_error(f"Q4 Analysis failed: {traceback.format_exc()}")
        return []


def generate_report(results):
    """Generate a text report of all results"""
    report = []
    for q, data in results.items():
        report.append(f"\n=== {q} ===")
        if not data:
            report.append("No data available or error occurred")
            continue
            
        for i, (item, count) in enumerate(data, 1):
            report.append(f"{i:>2}. {item:<20} {count}")
    
    with open(f"{OUTPUT_DIR}/report.txt", "w") as f:
        f.write("\n".join(report))

def main():
    setup()
    
    try:
        results = {
            "Q1: Top 10 Languages by Project Count": analyze_q1_languages(),
            "Q2: Top 10 Most Active Repos by Commits": analyze_q2_commits(),
            "Q3: Top 10 Languages with TDD": analyze_q3_tdd(),
            "Q4: Top 10 Languages with TDD+CI/CD": analyze_q4_tdd_cicd()
        }
        
        generate_report(results)
        
        # Check if any errors occurred
        with open(ERROR_FILE, "r") as f:
            errors = f.read()
        
        if not errors:
            with open(ERROR_FILE, "w") as f:
                f.write("No error... everything ran successfully")
                
        print("Analysis completed. Results saved in 'results/' directory.")
        
    except Exception as e:
        log_error(f"Main analysis failed: {traceback.format_exc()}")
        print(f"Analysis failed. Check {ERROR_FILE} for details.")

if __name__ == "__main__":
    main()
