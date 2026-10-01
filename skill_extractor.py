import re


SKILL_LIST = [
    "python",
    "java",
    "c++",
    "c",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "react.js",
    "node.js",
    "nodejs",
    "express",
    "flask",
    "django",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "pandas",
    "numpy",
    "scikit-learn",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "nlp",
    "tensorflow",
    "pytorch",
    "keras",
    "opencv",
    "data science",
    "data analysis",
    "power bi",
    "tableau",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
]


def extract_skills(resume_text):
    if not resume_text:
        return []

    text = resume_text.lower()

    # Normalize common variations
    text = text.replace("scikit learn", "scikit-learn")
    text = text.replace("machine-learning", "machine learning")
    text = text.replace("deep-learning", "deep learning")
    text = text.replace("powerbi", "power bi")
    text = text.replace("node js", "node.js")

    found_skills = []

    for skill in SKILL_LIST:
        pattern = r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills