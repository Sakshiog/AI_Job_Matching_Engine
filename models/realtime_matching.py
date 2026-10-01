import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from models.hybrid import HybridMatcher


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class RealtimeMatcher:

    def __init__(self):

        self.matcher = HybridMatcher()

        self.feedback_file = DATA_DIR / "feedback.csv"
        self.ratings_file = DATA_DIR / "ratings.csv"

        self.feedback = pd.read_csv(
            self.feedback_file
        )

        self.ratings = pd.read_csv(
            self.ratings_file
        )

    # --------------------------------------------------
    # SAVE FEEDBACK
    # --------------------------------------------------

    def record_feedback(
        self,
        candidate_id,
        job_id,
        feedback,
        rating=None
    ):

        feedback = feedback.lower().strip()

        valid_feedback = {
            "interested",
            "not_interested",
            "applied"
        }

        if feedback not in valid_feedback:
            raise ValueError(
                "Feedback must be: "
                "interested, not_interested, or applied"
            )

        # Generate new feedback ID
        if self.feedback.empty:
            next_id = 1
        else:
            next_id = len(self.feedback) + 1

        new_feedback = pd.DataFrame([{
            "feedback_id": f"F{next_id:03d}",
            "candidate_id": candidate_id,
            "job_id": job_id,
            "feedback": feedback
        }])

        self.feedback = pd.concat(
            [self.feedback, new_feedback],
            ignore_index=True
        )

        self.feedback.to_csv(
            self.feedback_file,
            index=False
        )

        # Save rating if provided
        if rating is not None:

            rating = float(rating)

            if rating < 1 or rating > 5:
                raise ValueError(
                    "Rating must be between 1 and 5."
                )

            if self.ratings.empty:
                next_rating_id = 1
            else:
                next_rating_id = len(self.ratings) + 1

            new_rating = pd.DataFrame([{
                "rating_id": f"R{next_rating_id:03d}",
                "candidate_id": candidate_id,
                "job_id": job_id,
                "rating": rating
            }])

            self.ratings = pd.concat(
                [self.ratings, new_rating],
                ignore_index=True
            )

            self.ratings.to_csv(
                self.ratings_file,
                index=False
            )

        print(
            f"\n? Feedback recorded successfully:"
            f"\nCandidate : {candidate_id}"
            f"\nJob       : {job_id}"
            f"\nFeedback  : {feedback}"
            f"\nRating    : {rating if rating is not None else 'Not provided'}"
        )

    # --------------------------------------------------
    # GET FEEDBACK SCORE
    # --------------------------------------------------

    def get_feedback_score(
        self,
        candidate_id,
        job_id
    ):

        feedback_rows = self.feedback[
            (self.feedback["candidate_id"] == candidate_id)
            &
            (self.feedback["job_id"] == job_id)
        ]

        if feedback_rows.empty:
            return 0.0

        latest_feedback = feedback_rows.iloc[-1]["feedback"]

        if latest_feedback == "interested":
            return 10.0

        if latest_feedback == "applied":
            return 15.0

        if latest_feedback == "not_interested":
            return -20.0

        return 0.0

    # --------------------------------------------------
    # REAL-TIME RECOMMENDATIONS
    # --------------------------------------------------

    def get_recommendations(
        self,
        candidate_id,
        top_n=10
    ):

        recommendations = self.matcher.recommend_jobs(
            candidate_id,
            top_n=len(self.matcher.jobs)
        )

        adjusted_scores = []

        for _, row in recommendations.iterrows():

            feedback_score = self.get_feedback_score(
                candidate_id,
                row["job_id"]
            )

            adjusted_score = (
                row["hybrid_score"]
                + feedback_score
            )

            adjusted_score = max(
                0,
                min(100, adjusted_score)
            )

            adjusted_scores.append(
                adjusted_score
            )

        recommendations["feedback_adjustment"] = [
            round(
                self.get_feedback_score(
                    candidate_id,
                    job_id
                ),
                2
            )
            for job_id in recommendations["job_id"]
        ]

        recommendations["realtime_score"] = np.round(
            adjusted_scores,
            2
        )

        recommendations = recommendations.sort_values(
            by="realtime_score",
            ascending=False
        )

        return recommendations.head(
            top_n
        ).reset_index(drop=True)

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    def display_recommendations(
        self,
        candidate_id,
        top_n=10
    ):

        recommendations = self.get_recommendations(
            candidate_id,
            top_n
        )

        print(
            "\nTop Real-Time Job Recommendations:\n"
        )

        for index, row in recommendations.iterrows():

            print(
                f"{index + 1}. "
                f"{row['job_title']} | "
                f"{row['company']} | "
                f"Hybrid: {row['hybrid_score']}% | "
                f"Feedback: "
                f"{row['feedback_adjustment']} | "
                f"Real-Time: "
                f"{row['realtime_score']}%"
            )


# ------------------------------------------------------
# TEST
# ------------------------------------------------------

def main():

    print("\n" + "=" * 75)
    print("        AI JOB MATCHING ENGINE - REAL-TIME MATCHING")
    print("=" * 75)

    candidate_id = "C001"

    realtime = RealtimeMatcher()

    candidate = realtime.matcher.get_candidate(
        candidate_id
    )

    print(f"\nCandidate: {candidate_id}")
    print(f"Name           : {candidate['name']}")
    print(f"Preferred Role : {candidate['preferred_role']}")
    print(f"Skills         : {candidate['skills']}")

    print(
        "\nInitial Recommendations:"
    )

    realtime.display_recommendations(
        candidate_id,
        top_n=5
    )

    # Test feedback
    print(
        "\n" + "-" * 75
    )
    print(
        "TESTING REAL-TIME FEEDBACK"
    )
    print(
        "-" * 75
    )

    test_job_id = "J001"

    realtime.record_feedback(
        candidate_id=candidate_id,
        job_id=test_job_id,
        feedback="interested",
        rating=5
    )

    print(
        "\nUpdated Recommendations After Feedback:"
    )

    realtime.display_recommendations(
        candidate_id,
        top_n=5
    )

    print(
        "\n" + "=" * 75
    )
    print(
        "? REAL-TIME MATCHING TEST COMPLETED"
    )
    print(
        "=" * 75
    )


if __name__ == "__main__":
    main()
