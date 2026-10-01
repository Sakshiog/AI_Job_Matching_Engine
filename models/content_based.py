import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class ContentBasedMatcher:

    def __init__(self):
        self.candidates = pd.read_csv(DATA_DIR / "candidates.csv")
        self.jobs = pd.read_csv(DATA_DIR / "jobs.csv")

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english"
        )

        self.job_vectors = None
        self._prepare_job_vectors()

    def _prepare_job_vectors(self):
        job_text = (
            self.jobs["job_title"].fillna("") + " " +
            self.jobs["required_skills"].fillna("").str.replace("|", " ", regex=False) + " " +
            self.jobs["education"].fillna("") + " " +
            self.jobs["category"].fillna("") + " " +
            self.jobs["location"].fillna("") + " " +
            self.jobs["work_mode"].fillna("")
        )

        self.job_vectors = self.vectorizer.fit_transform(job_text)

    def _create_candidate_text(self, candidate):
        return (
            str(candidate["preferred_role"]) + " " +
            str(candidate["skills"]).replace("|", " ") + " " +
            str(candidate["education"]) + " " +
            str(candidate["location"]) + " " +
            str(candidate["work_mode"])
        )

    def get_candidate(self, candidate_id):
        candidate = self.candidates[
            self.candidates["candidate_id"] == candidate_id
        ]

        if candidate.empty:
            raise ValueError(
                f"Candidate ID '{candidate_id}' not found."
            )

        return candidate.iloc[0]

    def recommend_jobs(self, candidate_id, top_n=10):

        candidate = self.get_candidate(candidate_id)

        candidate_text = self._create_candidate_text(candidate)

        candidate_vector = self.vectorizer.transform(
            [candidate_text]
        )

        similarity_scores = cosine_similarity(
            candidate_vector,
            self.job_vectors
        )[0]

        results = self.jobs.copy()

        results["content_score"] = similarity_scores

        results["match_score"] = (
            results["content_score"] * 100
        ).round(2)

        results = results.sort_values(
            by="match_score",
            ascending=False
        )

        return results.head(top_n)[
            [
                "job_id",
                "job_title",
                "company",
                "location",
                "work_mode",
                "salary",
                "category",
                "match_score"
            ]
        ].reset_index(drop=True)


def main():

    print("\n" + "=" * 65)
    print("        AI JOB MATCHING ENGINE - CONTENT BASED MODEL")
    print("=" * 65)

    matcher = ContentBasedMatcher()

    candidate_id = "C001"

    print(f"\nCandidate: {candidate_id}")

    candidate = matcher.get_candidate(candidate_id)

    print(f"Name           : {candidate['name']}")
    print(f"Preferred Role : {candidate['preferred_role']}")
    print(f"Skills         : {candidate['skills']}")
    print(f"Location       : {candidate['location']}")
    print(f"Work Mode      : {candidate['work_mode']}")

    recommendations = matcher.recommend_jobs(
        candidate_id,
        top_n=10
    )

    print("\nTop 10 Job Recommendations:\n")

    for index, row in recommendations.iterrows():

        print(
            f"{index + 1}. "
            f"{row['job_title']} | "
            f"{row['company']} | "
            f"{row['location']} | "
            f"Match: {row['match_score']}%"
        )

    print("\n" + "=" * 65)
    print("✅ CONTENT-BASED MATCHING TEST COMPLETED")
    print("=" * 65)


if __name__ == "__main__":
    main()