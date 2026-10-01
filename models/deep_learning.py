import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class DeepLearningMatcher:

    def __init__(self):

        self.candidates = pd.read_csv(
            DATA_DIR / "candidates.csv"
        )

        self.jobs = pd.read_csv(
            DATA_DIR / "jobs.csv"
        )

        self.ratings = pd.read_csv(
            DATA_DIR / "ratings.csv"
        )

        self.scaler = StandardScaler()

        self.model = MLPRegressor(
            hidden_layer_sizes=(32, 16),
            activation="relu",
            solver="adam",
            learning_rate_init=0.01,
            max_iter=1000,
            random_state=42
        )

        self._prepare_model()

    # --------------------------------------------------
    # TEXT / VALUE HELPERS
    # --------------------------------------------------

    def _split_values(self, value):

        if pd.isna(value):
            return set()

        return {
            item.strip().lower()
            for item in str(value).split("|")
            if item.strip()
        }

    def _skill_overlap(self, candidate_skills, job_skills):

        candidate_set = self._split_values(candidate_skills)
        job_set = self._split_values(job_skills)

        if not job_set:
            return 0.0

        return len(candidate_set & job_set) / len(job_set)

    def _role_match(self, preferred_role, job_title):

        preferred = str(preferred_role).lower()
        title = str(job_title).lower()

        if preferred in title or title in preferred:
            return 1.0

        preferred_words = set(preferred.split())
        title_words = set(title.split())

        if preferred_words & title_words:
            return 0.6

        return 0.0

    def _education_match(self, candidate_education, job_education):

        candidate = str(candidate_education).lower()
        job = str(job_education).lower()

        if candidate == job:
            return 1.0

        if (
            "b.tech" in candidate
            and "b.tech" in job
        ):
            return 1.0

        if (
            "b.e" in candidate
            and "b.e" in job
        ):
            return 1.0

        return 0.5

    def _location_match(self, candidate_location, job_location):

        candidate = str(candidate_location).lower()
        job = str(job_location).lower()

        if candidate == job:
            return 1.0

        return 0.0

    def _work_mode_match(self, candidate_mode, job_mode):

        candidate = str(candidate_mode).lower()
        job = str(job_mode).lower()

        if candidate == job:
            return 1.0

        if candidate == "remote":
            return 1.0 if job == "remote" else 0.5

        if candidate == "hybrid":
            return 1.0 if job == "hybrid" else 0.5

        if candidate == "onsite":
            return 1.0 if job == "onsite" else 0.5

        return 0.5

    def _experience_match(self, candidate_exp, job_exp):

        try:
            candidate_exp = float(candidate_exp)
            job_exp = float(job_exp)
        except (ValueError, TypeError):
            return 0.5

        if candidate_exp >= job_exp:
            return 1.0

        difference = job_exp - candidate_exp

        if difference <= 1:
            return 0.8

        if difference <= 2:
            return 0.5

        return 0.2

    def _salary_match(self, candidate_salary, job_salary):

        try:
            expected = float(candidate_salary)
            salary = float(job_salary)
        except (ValueError, TypeError):
            return 0.5

        if expected <= 0:
            return 0.5

        if salary >= expected:
            return 1.0

        difference = (expected - salary) / expected

        return max(0.0, 1.0 - difference)

    # --------------------------------------------------
    # FEATURE GENERATION
    # --------------------------------------------------

    def _create_features(self, candidate, job, historical_rating=0):

        skill_score = self._skill_overlap(
            candidate["skills"],
            job["required_skills"]
        )

        role_score = self._role_match(
            candidate["preferred_role"],
            job["job_title"]
        )

        education_score = self._education_match(
            candidate["education"],
            job["education"]
        )

        location_score = self._location_match(
            candidate["location"],
            job["location"]
        )

        work_mode_score = self._work_mode_match(
            candidate["work_mode"],
            job["work_mode"]
        )

        experience_score = self._experience_match(
            candidate["experience"],
            job["experience"]
        )

        salary_score = self._salary_match(
            candidate["expected_salary"],
            job["salary"]
        )

        rating_score = historical_rating / 5.0

        return [
            skill_score,
            role_score,
            education_score,
            location_score,
            work_mode_score,
            experience_score,
            salary_score,
            rating_score
        ]

    # --------------------------------------------------
    # TRAINING
    # --------------------------------------------------

    def _prepare_model(self):

        X = []
        y = []

        for _, rating in self.ratings.iterrows():

            candidate_data = self.candidates[
                self.candidates["candidate_id"]
                == rating["candidate_id"]
            ]

            job_data = self.jobs[
                self.jobs["job_id"]
                == rating["job_id"]
            ]

            if candidate_data.empty or job_data.empty:
                continue

            candidate = candidate_data.iloc[0]
            job = job_data.iloc[0]

            features = self._create_features(
                candidate,
                job,
                float(rating["rating"])
            )

            X.append(features)
            y.append(float(rating["rating"]))

        X = np.array(X)
        y = np.array(y)

        X_scaled = self.scaler.fit_transform(X)

        self.model.fit(
            X_scaled,
            y
        )

    # --------------------------------------------------
    # CANDIDATE
    # --------------------------------------------------

    def get_candidate(self, candidate_id):

        candidate = self.candidates[
            self.candidates["candidate_id"]
            == candidate_id
        ]

        if candidate.empty:
            raise ValueError(
                f"Candidate ID '{candidate_id}' not found."
            )

        return candidate.iloc[0]

    # --------------------------------------------------
    # PREDICTION
    # --------------------------------------------------

    def predict_job_scores(self, candidate_id):

        candidate = self.get_candidate(candidate_id)

        features = []

        for _, job in self.jobs.iterrows():

            job_features = self._create_features(
                candidate,
                job,
                historical_rating=0
            )

            features.append(job_features)

        X = np.array(features)

        X_scaled = self.scaler.transform(X)

        predictions = self.model.predict(
            X_scaled
        )

        predictions = np.clip(
            predictions,
            1,
            5
        )

        return predictions

    # --------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------

    def recommend_jobs(self, candidate_id, top_n=10):

        predictions = self.predict_job_scores(
            candidate_id
        )

        results = self.jobs.copy()

        results["predicted_rating"] = np.round(
            predictions,
            2
        )

        results["match_score"] = np.round(
            ((predictions - 1) / 4) * 100,
            2
        )

        results = results.sort_values(
            by="match_score",
            ascending=False
        )

        return results.head(top_n)[[
            "job_id",
            "job_title",
            "company",
            "location",
            "work_mode",
            "salary",
            "category",
            "predicted_rating",
            "match_score"
        ]].reset_index(drop=True)


# ------------------------------------------------------
# MAIN TEST
# ------------------------------------------------------

def main():

    print("\n" + "=" * 75)
    print("       AI JOB MATCHING ENGINE - NEURAL NETWORK MODEL")
    print("=" * 75)

    matcher = DeepLearningMatcher()

    candidate_id = "C001"

    candidate = matcher.get_candidate(
        candidate_id
    )

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

    print(
        "\nTop 10 Neural Network Recommendations:\n"
    )

    for index, row in recommendations.iterrows():

        print(
            f"{index + 1}. "
            f"{row['job_title']} | "
            f"{row['company']} | "
            f"Predicted Rating: "
            f"{row['predicted_rating']}/5 | "
            f"Match: "
            f"{row['match_score']}%"
        )

    print("\n" + "=" * 75)
    print("? NEURAL NETWORK MATCHING TEST COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()
