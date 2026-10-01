# 🤖 AI Job Matching Engine
### 🎯 AI-Powered Job Recommendations for Your Career
A machine learning-based job recommendation system that matches candidates with suitable job opportunities based on their skills, experience, preferences, location, work mode, and expected salary.
The system uses NLP, TF-IDF, Scikit-learn, and multiple recommendation techniques to calculate candidate-job compatibility and generate personalized job recommendations.

---
## ✨ Features
* Candidate registration and login
* Candidate profile management
* AI-based job matching
* NLP and TF-IDF-based text matching
* Content-based recommendation
* Collaborative filtering
* Hybrid recommendation
* Deep learning-based matching
* Real-time matching
* Personalized job recommendations
* Job compatibility scores
* Location and work-mode matching
* Expected salary matching
* Interactive Streamlit dashboard

---

## 🧠 How It Works

```text
Candidate Profile
       |
       v
Profile Processing
       |
       v
NLP & TF-IDF
       |
       +-------------------+
       |                   |
       v                   v
Content-Based       Collaborative
Matching             Filtering
       |                   |
       +---------+---------+
                 |
                 v
          Hybrid Matching
                 |
                 v
          Match Score
                 |
                 v
       Recommended Jobs
```

The system analyzes candidate and job information and generates a compatibility score for each available job.

---

## 🔬 AI & Recommendation Techniques
### Content-Based Matching
Compares candidate information with job requirements to identify suitable opportunities.
The matching process considers:
* Skills
* Preferred role
* Education
* Experience
* Location
* Work mode
* Expected salary

### NLP & TF-IDF
TF-IDF converts textual information such as skills and job descriptions into numerical features that can be compared using similarity techniques.

### Collaborative Filtering
Uses historical applications, ratings, and feedback to identify recommendation patterns.

### Hybrid Recommendation
Combines multiple recommendation approaches to generate the final job recommendations.

### Deep Learning
Includes a deep-learning-based recommendation module for experimenting with advanced matching techniques.

### Real-Time Matching
Generates updated recommendations based on the candidate's current profile information.

---

## 📊 Sample Results

```text
Job Recommendations

TechNova        100.00% Match
InnovateAI       91.06% Match
SmartAI          84.11% Match
DeepTech         77.55% Match
AI Labs          72.69% Match
```
The match percentage represents the compatibility calculated by the recommendation system using the available candidate and job data.

---

## 👤 Candidate Profile
Candidates can create and manage their profile with:
```text
Candidate ID
Name
Education
Skills
Experience
Preferred Role
Location
Work Mode
Expected Salary
```
This information is used by the matching engine to generate personalized recommendations.

---

## 🔐 Authentication
The application provides a registration and login system.
```text
Home
  |
  +---- Register
  |       |
  |       v
  |   Create Profile
  |
  +---- Sign In
          |
          v
       Dashboard
          |
          v
    Job Recommendations
```
Passwords are stored using **PBKDF2 password hashing** rather than plain-text storage.

---

## 🛠️ Technology Stack

| Category         | Technologies                         |
| ---------------- | ------------------------------------ |
| Programming      | Python 3.10                          |
| Machine Learning | Scikit-learn                         |
| NLP              | TF-IDF, Text Similarity              |
| Data Processing  | Pandas, NumPy                        |
| Recommendation   | Content-Based, Collaborative, Hybrid |
| Interface        | Streamlit, HTML, CSS                 |
| Data Storage     | CSV, JSON                            |

---

## 📁 Project Structure

```text
AI_Job_Matching_Engine/
│
├── app.py
├── matching_engine.py
│
├── content_based.py
├── collaborative.py
├── hybrid.py
├── deep_learning.py
├── realtime_matching.py
│
├── candidates.csv
├── jobs.csv
├── applications.csv
├── ratings.csv
├── feedback.csv
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 📈 Dataset
The project currently uses:
| Dataset      | Records |
| ------------ | ------: |
| Candidates   |      50 |
| Jobs         |     100 |
| Applications |     100 |
| Ratings      |     100 |
| Feedback     |     100 |

The datasets are used to develop and test different job recommendation approaches.

---
## 🔄 Project Workflow
```text
Registration
     ↓
Candidate Profile
     ↓
Profile Processing
     ↓
Feature Extraction
     ↓
Job Matching
     ↓
Recommendation
     ↓
Match Score
```

---

## 🚀 Future Enhancements
* Resume PDF parsing
* Real-time job API integration
* PostgreSQL or MySQL database
* Transformer-based NLP models
* Explainable AI for match scores
* Recruiter dashboard
* Job application tracking
* Email notifications
* Cloud deployment

---

## 🎯 Project Objective
The objective of this project is to develop an AI-based recruitment recommendation system that analyzes candidate profiles and job requirements to provide relevant and personalized job opportunities.

The project demonstrates the practical use of **Machine Learning, NLP, recommendation systems, and Streamlit application development** in recruitment automation.

---

## 👩‍💻 Developer
**Sakshi Yadav**
B.Tech Computer Science & Engineering
Specialization: Data Science & AI
**Technologies:** Python · Machine Learning · NLP · TF-IDF · Scikit-learn · Pandas · NumPy · Streamlit · HTML · CSS

---

# 🙏 Thank You
Thank you for visiting this project and exploring the **AI Job Matching Engine**.
If you found this project interesting, feel free to explore the repository and share your feedback.

