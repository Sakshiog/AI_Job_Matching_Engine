import pandas as pd
import numpy as np
from pathlib import Path

from models.content_based import ContentBasedMatcher
from models.collaborative import CollaborativeMatcher
from models.hybrid import HybridMatcher
from models.deep_learning import DeepLearningMatcher
from models.realtime_matching import RealtimeMatcher

from resume_parser import extract_resume_text
from skill_extractor import extract_skills


DATA_DIR = Path(__file__).resolve().parent / "data"


class JobMatchingEngine:

    def __init__(self):

        print("\nInitializing AI Job Matching Engine...")

        self.candidates_file = DATA_DIR / "candidates.csv"
        self.jobs_file = DATA_DIR / "jobs.csv"

        self.candidates = pd.read_csv(
            self.candidates_file
        )

        self.jobs = pd.read_csv(
            self.jobs_file
        )

        self.load_models()

        print("All recommendation models loaded successfully.")

    # ==================================================
    # LOAD / REFRESH RECOMMENDATION MODELS
    # ==================================================

    def load_models(self):

        self.content_model = ContentBasedMatcher()
        self.collaborative_model = CollaborativeMatcher()
        self.hybrid_model = HybridMatcher()
        self.deep_learning_model = DeepLearningMatcher()
        self.realtime_model = RealtimeMatcher()

    # ==================================================
    # REFRESH CANDIDATE DATA
    # ==================================================

    def refresh_candidates(self):

        self.candidates = pd.read_csv(
            self.candidates_file
        )

    # ==================================================
    # CHECK CANDIDATE ID
    # ==================================================

    def candidate_exists(self, candidate_id):

        candidate_id = str(candidate_id).strip()

        return (
            self.candidates["candidate_id"]
            .astype(str)
            .str.strip()
            .eq(candidate_id)
            .any()
        )

    # ==================================================
    # SAVE NEW CANDIDATE
    # ==================================================

    def save_candidate(
        self,
        candidate_id,
        name,
        education,
        skills,
        experience,
        preferred_role,
        location,
        work_mode,
        expected_salary
    ):

        candidate_id = str(candidate_id).strip()

        if not candidate_id:

            raise ValueError(
                "Candidate ID cannot be empty."
            )

        if self.candidate_exists(candidate_id):

            raise ValueError(
                f"Candidate ID '{candidate_id}' already exists. "
                "Please use a different Candidate ID."
            )

        new_candidate = {

            "candidate_id": candidate_id,

            "name": str(name).strip(),

            "education": str(
                education
            ).strip(),

            "skills": str(
                skills
            ).strip(),

            "experience": float(
                experience
            ),

            "preferred_role": str(
                preferred_role
            ).strip(),

            "location": str(
                location
            ).strip(),

            "work_mode": str(
                work_mode
            ).strip(),

            "expected_salary": float(
                expected_salary
            )
        }

        new_candidate_df = pd.DataFrame(
            [new_candidate]
        )

        new_candidate_df.to_csv(
            self.candidates_file,
            mode="a",
            header=False,
            index=False
        )

        self.refresh_candidates()

        self.load_models()

        return True

    # ==================================================
    # GET CANDIDATE PROFILE
    # ==================================================

    def get_candidate_profile(
        self,
        candidate_id
    ):

        candidate_id = str(
            candidate_id
        ).strip()

        candidate = self.candidates[
            self.candidates["candidate_id"]
            .astype(str)
            .str.strip()
            == candidate_id
        ]

        if candidate.empty:

            raise ValueError(
                f"Candidate ID '{candidate_id}' not found."
            )

        return candidate.iloc[0]

    # ==================================================
    # GET CANDIDATE
    # ==================================================

    def get_candidate(
        self,
        candidate_id
    ):

        candidate_id = str(
            candidate_id
        ).strip()

        candidate = self.candidates[
            self.candidates["candidate_id"]
            .astype(str)
            .str.strip()
            == candidate_id
        ]

        if candidate.empty:
            return None

        return candidate.iloc[0]

    # ==================================================
    # UPDATE SKILLS FROM RESUME
    # ==================================================

    def update_skills_from_resume(
        self,
        candidate_id,
        resume_path
    ):

        candidate_id = str(
            candidate_id
        ).strip()

        candidate_index = self.candidates.index[
            self.candidates["candidate_id"]
            .astype(str)
            .str.strip()
            .eq(candidate_id)
        ]

        if len(candidate_index) == 0:

            raise ValueError(
                f"Candidate ID '{candidate_id}' not found."
            )

        resume_text = extract_resume_text(
            resume_path
        )

        if not resume_text:
            return []

        extracted_skills = extract_skills(
            resume_text
        )

        if not extracted_skills:
            return []

        existing_skills = str(
            self.candidates.loc[
                candidate_index[0],
                "skills"
            ]
        )

        existing_skills = existing_skills.replace(
            "|",
            ","
        )

        manual_skills = {
            skill.strip().lower()
            for skill in existing_skills.split(",")
            if skill.strip()
        }

        resume_skills = {
            skill.strip().lower()
            for skill in extracted_skills
            if skill.strip()
        }

        merged_skills = (
            manual_skills.union(
                resume_skills
            )
        )

        final_skills = sorted(
            merged_skills
        )

        final_skill_text = ", ".join(
            final_skills
        )

        self.candidates.loc[
            candidate_index[0],
            "skills"
        ] = final_skill_text

        self.candidates.to_csv(
            self.candidates_file,
            index=False
        )

        self.refresh_candidates()

        self.load_models()

        return final_skills

    # ==================================================
    # SKILL GAP ANALYSIS
    # ==================================================

    def skill_gap_analysis(
        self,
        candidate_id,
        job_id
    ):

        candidate = self.get_candidate_profile(
            candidate_id
        )

        job = self.jobs[
            self.jobs["job_id"]
            .astype(str)
            .str.strip()
            == str(job_id).strip()
        ]

        if job.empty:

            raise ValueError(
                f"Job ID '{job_id}' not found."
            )

        job = job.iloc[0]

        # ----------------------------------------------
        # CANDIDATE SKILLS
        # ----------------------------------------------

        candidate_skill_text = str(
            candidate["skills"]
        )

        candidate_skill_text = (
            candidate_skill_text.replace(
                "|",
                ","
            )
        )

        candidate_skills = {
            skill.strip().lower()
            for skill in candidate_skill_text.split(",")
            if skill.strip()
        }

        # ----------------------------------------------
        # JOB REQUIRED SKILLS
        # ----------------------------------------------

        job_skill_text = str(
            job["required_skills"]
        )

        job_skills = {
            skill.strip().lower()
            for skill in job_skill_text.split("|")
            if skill.strip()
        }

        # ----------------------------------------------
        # MATCHED SKILLS
        # ----------------------------------------------

        matched_skills = sorted(
            candidate_skills.intersection(
                job_skills
            )
        )

        # ----------------------------------------------
        # MISSING SKILLS
        # ----------------------------------------------

        missing_skills = sorted(
            job_skills.difference(
                candidate_skills
            )
        )

        # ----------------------------------------------
        # SKILL MATCH PERCENTAGE
        # ----------------------------------------------

        if len(job_skills) > 0:

            skill_match_percentage = (
                len(matched_skills)
                / len(job_skills)
            ) * 100

        else:

            skill_match_percentage = 0

        return {

            "job_id": str(
                job["job_id"]
            ),

            "job_title": str(
                job["job_title"]
            ),

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "skill_match_percentage": round(
                skill_match_percentage,
                2
            )
        }

    # ==================================================
    # CANDIDATE RANKING FOR A JOB
    # ==================================================

    def rank_candidates_for_job(
        self,
        job_id,
        top_n=10
    ):

        job_id = str(
            job_id
        ).strip()

        job = self.jobs[
            self.jobs["job_id"]
            .astype(str)
            .str.strip()
            .eq(job_id)
        ]

        if job.empty:

            raise ValueError(
                f"Job ID '{job_id}' not found."
            )

        job = job.iloc[0]

        required_skills = {
            skill.strip().lower()
            for skill in str(
                job["required_skills"]
            ).split("|")
            if skill.strip()
        }

        results = []

        for _, candidate in self.candidates.iterrows():

            candidate_skills = str(
                candidate["skills"]
            ).replace(
                "|",
                ","
            )

            candidate_skills = {
                skill.strip().lower()
                for skill in candidate_skills.split(",")
                if skill.strip()
            }

            matched_skills = (
                candidate_skills
                .intersection(
                    required_skills
                )
            )

            if required_skills:

                skill_score = (
                    len(matched_skills)
                    / len(required_skills)
                ) * 100

            else:

                skill_score = 0

            results.append({

                "candidate_id": str(
                    candidate["candidate_id"]
                ),

                "name": str(
                    candidate["name"]
                ),

                "preferred_role": str(
                    candidate["preferred_role"]
                ),

                "skills": str(
                    candidate["skills"]
                ),

                "matched_skills": ", ".join(
                    sorted(
                        matched_skills
                    )
                ),

                "match_score": round(
                    skill_score,
                    2
                )
            })

        ranking = pd.DataFrame(
            results
        )

        ranking = ranking.sort_values(
            by="match_score",
            ascending=False
        ).reset_index(
            drop=True
        )

        ranking["rank"] = (
            ranking.index + 1
        )

        return ranking.head(
            top_n
        )

    # ==================================================
    # CONTENT-BASED RECOMMENDATIONS
    # ==================================================

    def content_recommendations(
        self,
        candidate_id,
        top_n=10
    ):

        return self.content_model.recommend_jobs(
            candidate_id,
            top_n=top_n
        )

    # ==================================================
    # COLLABORATIVE RECOMMENDATIONS
    # ==================================================

    def collaborative_recommendations(
        self,
        candidate_id,
        top_n=10
    ):

        return self.collaborative_model.recommend_jobs(
            candidate_id,
            top_n=top_n
        )

    # ==================================================
    # HYBRID RECOMMENDATIONS
    # ==================================================

    def hybrid_recommendations(
        self,
        candidate_id,
        top_n=10
    ):

        return self.hybrid_model.recommend_jobs(
            candidate_id,
            top_n=top_n
        )

    # ==================================================
    # NEURAL NETWORK RECOMMENDATIONS
    # ==================================================

    def neural_network_recommendations(
        self,
        candidate_id,
        top_n=10
    ):

        return self.deep_learning_model.recommend_jobs(
            candidate_id,
            top_n=top_n
        )

    # ==================================================
    # REAL-TIME RECOMMENDATIONS
    # ==================================================

    def realtime_recommendations(
        self,
        candidate_id,
        top_n=10
    ):

        return self.realtime_model.get_recommendations(
            candidate_id,
            top_n=top_n
        )

    # ==================================================
    # FINAL RECOMMENDATIONS
    # ==================================================

    def get_recommendations(
        self,
        candidate_id,
        top_n=10
    ):

        recommendations = (
            self.realtime_recommendations(
                candidate_id,
                top_n=top_n
            )
        )

        return recommendations

    # ==================================================
    # RECORD USER FEEDBACK
    # ==================================================

    def record_feedback(
        self,
        candidate_id,
        job_id,
        feedback,
        rating=None
    ):

        self.realtime_model.record_feedback(
            candidate_id=candidate_id,
            job_id=job_id,
            feedback=feedback,
            rating=rating
        )

        self.hybrid_model = HybridMatcher()

        self.realtime_model.matcher = (
            self.hybrid_model
        )

        self.deep_learning_model = (
            DeepLearningMatcher()
        )

        print(
            "\nRecommendation models refreshed "
            "after user feedback."
        )

    # ==================================================
    # DISPLAY FINAL RESULTS
    # ==================================================

    def display_recommendations(
        self,
        candidate_id,
        top_n=10
    ):

        candidate = self.get_candidate_profile(
            candidate_id
        )

        print("\n" + "=" * 80)

        print(
            "             AI JOB MATCHING ENGINE"
        )

        print("=" * 80)

        print(
            f"\nCandidate ID   : {candidate_id}"
        )

        print(
            f"Name           : {candidate['name']}"
        )

        print(
            f"Preferred Role : {candidate['preferred_role']}"
        )

        print(
            f"Skills         : {candidate['skills']}"
        )

        print(
            f"Location       : {candidate['location']}"
        )

        print(
            f"Work Mode      : {candidate['work_mode']}"
        )

        recommendations = (
            self.get_recommendations(
                candidate_id,
                top_n=top_n
            )
        )

        print(
            "\nFinal Real-Time Job Recommendations:\n"
        )

        for index, row in recommendations.iterrows():

            score = row.get(
                "realtime_score",
                row.get(
                    "match_score",
                    row.get(
                        "score",
                        0
                    )
                )
            )

            print(
                f"{index + 1}. "
                f"{row['job_title']} | "
                f"{row['company']} | "
                f"Location: {row['location']} | "
                f"Mode: {row['work_mode']} | "
                f"Score: {score}%"
            )

        print(
            "\n" + "=" * 80
        )


# ======================================================
# TEST
# ======================================================

def main():

    engine = JobMatchingEngine()

    candidate_id = "C001"

    # ----------------------------------------------
    # TEST RECOMMENDATIONS
    # ----------------------------------------------

    engine.display_recommendations(
        candidate_id,
        top_n=10
    )

    # ----------------------------------------------
    # TEST SKILL GAP ANALYSIS
    # ----------------------------------------------

    skill_gap = engine.skill_gap_analysis(
        candidate_id,
        "J001"
    )

    print("\n" + "=" * 80)

    print(
        "             SKILL GAP ANALYSIS"
    )

    print("=" * 80)

    print(
        f"\nJob: "
        f"{skill_gap['job_title']}"
    )

    print(
        f"Matched Skills: "
        f"{', '.join(skill_gap['matched_skills'])}"
    )

    print(
        f"Missing Skills: "
        f"{', '.join(skill_gap['missing_skills'])}"
    )

    print(
        f"Skill Match: "
        f"{skill_gap['skill_match_percentage']}%"
    )

    print(
        "\n" + "=" * 80
    )

    print(
        "\nMAIN JOB MATCHING ENGINE TEST COMPLETED"
    )


if __name__ == "__main__":

    main()