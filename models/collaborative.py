import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class CollaborativeMatcher:

    def __init__(self):
        self.candidates = pd.read_csv(DATA_DIR / "candidates.csv")
        self.jobs = pd.read_csv(DATA_DIR / "jobs.csv")
        self.ratings = pd.read_csv(DATA_DIR / "ratings.csv")

        self.rating_matrix = self._create_rating_matrix()

    def _create_rating_matrix(self):

        matrix = self.ratings.pivot_table(
            index="candidate_id",
            columns="job_id",
            values="rating",
            fill_value=0
        )

        return matrix

    def get_candidate(self, candidate_id):

        candidate = self.candidates[
            self.candidates["candidate_id"] == candidate_id
        ]

        if candidate.empty:
            raise ValueError(
                f"Candidate ID '{candidate_id}' not found."
            )

        return candidate.iloc[0]

    def find_similar_candidates(self, candidate_id):

        if candidate_id not in self.rating_matrix.index:
            raise ValueError(
                f"No rating history found for {candidate_id}"
            )

        candidate_vector = self.rating_matrix.loc[
            candidate_id
        ].values.reshape(1, -1)

        similarity = cosine_similarity(
            candidate_vector,
            self.rating_matrix.values
        )[0]

        similarity_scores = pd.Series(
            similarity,
            index=self.rating_matrix.index
        )

        similarity_scores = similarity_scores.drop(
            candidate_id
        )

        return similarity_scores.sort_values(
            ascending=False
        )

    def recommend_jobs(self, candidate_id, top_n=10):

        similar_candidates = self.find_similar_candidates(
            candidate_id
        )

        candidate_ratings = self.rating_matrix.loc[
            candidate_id
        ]

        unrated_jobs = candidate_ratings[
            candidate_ratings == 0
        ].index.tolist()

        if not unrated_jobs:
            unrated_jobs = list(self.rating_matrix.columns)

        job_scores = {}

        for job_id in unrated_jobs:

            weighted_sum = 0
            similarity_sum = 0

            for similar_id, similarity in similar_candidates.items():

                rating = self.rating_matrix.loc[
                    similar_id,
                    job_id
                ]

                if rating > 0:

                    weighted_sum += similarity * rating
                    similarity_sum += abs(similarity)

            if similarity_sum > 0:

                predicted_rating = (
                    weighted_sum / similarity_sum
                )

            else:

                predicted_rating = 0

            job_scores[job_id] = predicted_rating

        recommendations = pd.DataFrame(
            list(job_scores.items()),
            columns=[
                "job_id",
                "predicted_rating"
            ]
        )

        recommendations = recommendations.sort_values(
            by="predicted_rating",
            ascending=False
        )

        recommendations["match_score"] = (
            recommendations["predicted_rating"] / 5 * 100
        ).round(2)

        recommendations = recommendations.merge(
            self.jobs,
            on="job_id",
            how="left"
        )

        return recommendations.head(top_n)[
            [
                "job_id",
                "job_title",
                "company",
                "location",
                "work_mode",
                "salary",
                "category",
                "predicted_rating",
                "match_score"
            ]
        ].reset_index(drop=True)


def main():

    print("\n" + "=" * 70)
    print("       AI JOB MATCHING ENGINE - COLLABORATIVE FILTERING")
    print("=" * 70)

    matcher = CollaborativeMatcher()

    candidate_id = "C001"

    candidate = matcher.get_candidate(candidate_id)

    print(f"\nCandidate: {candidate_id}")
    print(f"Name: {candidate['name']}")

    similar_candidates = matcher.find_similar_candidates(
        candidate_id
    )

    print("\nMost Similar Candidates:")

    for candidate, score in similar_candidates.head(5).items():

        print(
            f"{candidate} → Similarity: {score:.4f}"
        )

    recommendations = matcher.recommend_jobs(
        candidate_id,
        top_n=10
    )

    print("\nTop 10 Collaborative Recommendations:\n")

    for index, row in recommendations.iterrows():

        print(
            f"{index + 1}. "
            f"{row['job_title']} | "
            f"{row['company']} | "
            f"Predicted Rating: "
            f"{row['predicted_rating']:.2f}/5 | "
            f"Match: {row['match_score']}%"
        )

    print("\n" + "=" * 70)
    print("✅ COLLABORATIVE FILTERING TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()