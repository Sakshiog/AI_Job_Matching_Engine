import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class HybridMatcher:

    def __init__(self):
        self.candidates = pd.read_csv(DATA_DIR / "candidates.csv")
        self.jobs = pd.read_csv(DATA_DIR / "jobs.csv")
        self.ratings = pd.read_csv(DATA_DIR / "ratings.csv")

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english"
        )

        self.job_vectors = self._prepare_job_vectors()
        self.rating_matrix = self._prepare_rating_matrix()

    def _prepare_job_vectors(self):

        job_text = (
            self.jobs["job_title"].fillna("") + " " +
            self.jobs["required_skills"]
            .fillna("")
            .str.replace("|", " ", regex=False) + " " +
            self.jobs["education"].fillna("") + " " +
            self.jobs["category"].fillna("") + " " +
            self.jobs["location"].fillna("") + " " +
            self.jobs["work_mode"].fillna("")
        )

        return self.vectorizer.fit_transform(job_text)

    def _prepare_rating_matrix(self):

        return self.ratings.pivot_table(
            index="candidate_id",
            columns="job_id",
            values="rating",
            fill_value=0
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

    def calculate_content_scores(self, candidate_id):

        candidate = self.get_candidate(candidate_id)

        candidate_text = (
            str(candidate["preferred_role"]) + " " +
            str(candidate["skills"]).replace("|", " ") + " " +
            str(candidate["education"]) + " " +
            str(candidate["location"]) + " " +
            str(candidate["work_mode"])
        )

        candidate_vector = self.vectorizer.transform(
            [candidate_text]
        )

        return cosine_similarity(
            candidate_vector,
            self.job_vectors
        )[0]

    def calculate_collaborative_scores(self, candidate_id):

        if candidate_id not in self.rating_matrix.index:
            return np.zeros(len(self.jobs))

        candidate_vector = self.rating_matrix.loc[
            candidate_id
        ].values.reshape(1, -1)

        similarities = cosine_similarity(
            candidate_vector,
            self.rating_matrix.values
        )[0]

        similarity_series = pd.Series(
            similarities,
            index=self.rating_matrix.index
        )

        similarity_series = similarity_series.drop(
            candidate_id
        )

        scores = {}

        for job_id in self.rating_matrix.columns:

            weighted_sum = 0
            similarity_sum = 0

            for similar_id, similarity in similarity_series.items():

                rating = self.rating_matrix.loc[
                    similar_id,
                    job_id
                ]

                if rating > 0:

                    weighted_sum += similarity * rating
                    similarity_sum += abs(similarity)

            if similarity_sum > 0:
                scores[job_id] = (
                    weighted_sum / similarity_sum
                )
            else:
                scores[job_id] = 0

        return np.array([
            scores.get(job_id, 0)
            for job_id in self.jobs["job_id"]
        ])

    def recommend_jobs(
        self,
        candidate_id,
        top_n=10,
        content_weight=0.6,
        collaborative_weight=0.4
    ):

        content_scores = self.calculate_content_scores(
            candidate_id
        )

        collaborative_scores = self.calculate_collaborative_scores(
            candidate_id
        )

        collaborative_normalized = (
            collaborative_scores / 5
        )

        hybrid_scores = (
            content_scores * content_weight +
            collaborative_normalized * collaborative_weight
        )

        results = self.jobs.copy()

        results["content_score"] = (
            content_scores * 100
        ).round(2)

        results["collaborative_score"] = (
            collaborative_normalized * 100
        ).round(2)

        results["hybrid_score"] = (
            hybrid_scores * 100
        ).round(2)

        results = results.sort_values(
            by="hybrid_score",
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
                "content_score",
                "collaborative_score",
                "hybrid_score"
            ]
        ].reset_index(drop=True)


def main():

    print("\n" + "=" * 75)
    print("             AI JOB MATCHING ENGINE - HYBRID MODEL")
    print("=" * 75)

    matcher = HybridMatcher()

    candidate_id = "C001"

    candidate = matcher.get_candidate(candidate_id)

    print(f"\nCandidate: {candidate_id}")
    print(f"Name           : {candidate['name']}")
    print(f"Preferred Role : {candidate['preferred_role']}")
    print(f"Skills         : {candidate['skills']}")
    print(f"Location       : {candidate['location']}")
    print(f"Work Mode      : {candidate['work_mode']}")

    recommendations = matcher.recommend_jobs(
        candidate_id,
        top_n=10
    )

    print("\nTop 10 Hybrid Recommendations:\n")

    for index, row in recommendations.iterrows():

        print(
            f"{index + 1}. "
            f"{row['job_title']} | "
            f"{row['company']} | "
            f"Content: {row['content_score']}% | "
            f"Collaborative: {row['collaborative_score']}% | "
            f"Hybrid: {row['hybrid_score']}%"
        )

    print("\n" + "=" * 75)
    print("✅ HYBRID MATCHING TEST COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()
