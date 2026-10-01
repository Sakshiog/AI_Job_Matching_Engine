import pandas as pd
from pathlib import Path


DATA_DIR = Path("data")


def validate_candidates():
    file = DATA_DIR / "candidates.csv"
    df = pd.read_csv(file)

    required_columns = [
        "candidate_id",
        "name",
        "education",
        "skills",
        "experience",
        "preferred_role",
        "location",
        "work_mode",
        "expected_salary"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        print("❌ Candidates: Missing columns:", missing_columns)
        return False

    if df["candidate_id"].duplicated().any():
        print("❌ Candidates: Duplicate candidate IDs found")
        return False

    if df["candidate_id"].isnull().any():
        print("❌ Candidates: Missing candidate IDs found")
        return False

    print(f"✅ Candidates validated: {len(df)} records")
    return True


def validate_jobs():
    file = DATA_DIR / "jobs.csv"
    df = pd.read_csv(file)

    required_columns = [
        "job_id",
        "job_title",
        "company",
        "required_skills",
        "education",
        "experience",
        "location",
        "work_mode",
        "salary",
        "category"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        print("❌ Jobs: Missing columns:", missing_columns)
        return False

    if df["job_id"].duplicated().any():
        print("❌ Jobs: Duplicate job IDs found")
        return False

    if df["job_id"].isnull().any():
        print("❌ Jobs: Missing job IDs found")
        return False

    print(f"✅ Jobs validated: {len(df)} records")
    return True


def validate_applications():
    file = DATA_DIR / "applications.csv"
    df = pd.read_csv(file)

    candidates = pd.read_csv(DATA_DIR / "candidates.csv")
    jobs = pd.read_csv(DATA_DIR / "jobs.csv")

    valid_candidates = set(candidates["candidate_id"])
    valid_jobs = set(jobs["job_id"])

    invalid_candidates = ~df["candidate_id"].isin(valid_candidates)
    invalid_jobs = ~df["job_id"].isin(valid_jobs)

    if invalid_candidates.any():
        print("❌ Applications: Invalid candidate IDs found")
        return False

    if invalid_jobs.any():
        print("❌ Applications: Invalid job IDs found")
        return False

    print(f"✅ Applications validated: {len(df)} records")
    return True


def validate_ratings():
    file = DATA_DIR / "ratings.csv"
    df = pd.read_csv(file)

    candidates = pd.read_csv(DATA_DIR / "candidates.csv")
    jobs = pd.read_csv(DATA_DIR / "jobs.csv")

    valid_candidates = set(candidates["candidate_id"])
    valid_jobs = set(jobs["job_id"])

    if not df["candidate_id"].isin(valid_candidates).all():
        print("❌ Ratings: Invalid candidate IDs found")
        return False

    if not df["job_id"].isin(valid_jobs).all():
        print("❌ Ratings: Invalid job IDs found")
        return False

    if not df["rating"].between(1, 5).all():
        print("❌ Ratings: Rating must be between 1 and 5")
        return False

    print(f"✅ Ratings validated: {len(df)} records")
    return True


def validate_feedback():
    file = DATA_DIR / "feedback.csv"
    df = pd.read_csv(file)

    candidates = pd.read_csv(DATA_DIR / "candidates.csv")
    jobs = pd.read_csv(DATA_DIR / "jobs.csv")

    valid_candidates = set(candidates["candidate_id"])
    valid_jobs = set(jobs["job_id"])

    valid_feedback = {
        "interested",
        "not_interested",
        "applied"
    }

    if not df["candidate_id"].isin(valid_candidates).all():
        print("❌ Feedback: Invalid candidate IDs found")
        return False

    if not df["job_id"].isin(valid_jobs).all():
        print("❌ Feedback: Invalid job IDs found")
        return False

    if not df["feedback"].isin(valid_feedback).all():
        print("❌ Feedback: Invalid feedback values found")
        return False

    print(f"✅ Feedback validated: {len(df)} records")
    return True


def main():
    print("\n" + "=" * 55)
    print("       AI JOB MATCHING ENGINE - DATA VALIDATION")
    print("=" * 55)

    results = [
        validate_candidates(),
        validate_jobs(),
        validate_applications(),
        validate_ratings(),
        validate_feedback()
    ]

    print("\n" + "=" * 55)

    if all(results):
        print("✅ ALL DATASETS ARE VALID")
    else:
        print("❌ DATA VALIDATION FAILED")

    print("=" * 55)


if __name__ == "__main__":
    main()