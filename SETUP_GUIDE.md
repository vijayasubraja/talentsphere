# TalentSphere Project — Student-Friendly Setup and Deployment Guide

**GitHub Project:** [https://github.com/MASTER-SVS/PROJECT-DEMO-TALENT-MANAGE](https://github.com/MASTER-SVS/PROJECT-DEMO-TALENT-MANAGE)  
**Project Type:** Python + Streamlit Career Growth Application  

---

## 1. What is TalentSphere?

TalentSphere is a career development application that helps users understand their skills, improve their professional profile, and plan their career growth.

### Main Features:
1. **User registration and login** — Account creation, credential validation, and authentication.
2. **Professional profile management** — Contact details, work experience, education, and credentials.
3. **Resume upload and PDF export** — Resume parsing and profile export.
4. **Skills management and self-assessment** — Skills inventory, category filtering, proficiency levels, and self-assessments.
5. **Career direction and target role selection** — Benchmark enterprise roles and target horizons.
6. **Role matching and skill-gap analysis** — Deterministic gap calculations and proficiency benchmarks.
7. **Career recommendations** — Prioritized advice based on identified competency gaps.
8. **Career growth progress tracking** — Short-term and long-term milestones with status tracking.
9. **Career report generation** — Multi-page PDF career reports created via ReportLab.
10. **Personal data export** — Structured JSON personal data backup.

The application uses Python and Streamlit for its interface and SQLite to store user information.

---

## 2. Technologies Used

- **Python** — Main programming language
- **Streamlit** — Web application interface
- **SQLite** — Database
- **Pandas** — Data processing
- **Plotly** — Charts and visualizations
- **ReportLab** — PDF report generation
- **pypdf** — Reading PDF files
- **python-docx** — Reading Word documents
- **python-dotenv** — Environment configuration
- **pytest** — Automated testing framework

---

## 3. Current GitHub Repository Status

**GitHub repository:**  
[https://github.com/MASTER-SVS/PROJECT-DEMO-TALENT-MANAGE](https://github.com/MASTER-SVS/PROJECT-DEMO-TALENT-MANAGE)

The repository contains these core files:
- `app.py`
- `requirements.txt`
- `README.md`
- `.gitignore`
- `.env.example`
- `LICENSE`

The `app.py` file imports these modules:
- `services/core.py`
- `services/reports.py`

> [!IMPORTANT]
> Do not assume the project is ready for deployment just because `app.py` exists. The `services/` modules must be present alongside `app.py` before the application can start successfully.

---

## 4. Required Project Structure

The repository must have the following structure:

```text
PROJECT-DEMO-TALENT-MANAGE/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── LICENSE
│
├── .streamlit/
│   └── config.toml
│
├── services/
│   ├── __init__.py
│   ├── core.py
│   └── reports.py
│
└── tests/
    ├── test_core.py
    └── test_ui_views.py
```

### Important Notes on Structure:
- The `services` folder must be at the same level as `app.py`.
- `services/core.py` contains database persistence, authentication, and career-management logic.
- `services/reports.py` generates career reports via ReportLab.
- `.streamlit/config.toml` stores application theme and configuration settings.
- The `tests` folder is used to verify that the application works correctly.
- Do not create empty replacement files for missing modules; maintain the actual source code.

---

## 5. How to Run the Application on Windows

### STEP 1: Open PowerShell.

### STEP 2: Navigate to your project folder:
```powershell
cd "d:\infosys\talentsphere_elevate"
```

### STEP 3: Create a virtual environment:
```powershell
py -m venv .venv
```

### STEP 4: Activate the virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```
*If script execution is blocked on Windows, use the virtual environment's Python executable directly:*
```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### STEP 5: Install the required packages:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### STEP 6: Start the application:
```powershell
streamlit run app.py
```

### STEP 7: Open the local URL shown in PowerShell:
Usually:
```
http://localhost:8501
```
The application will open in your browser once all required files and dependencies are available.

---

## 6. How to Fix the Import Error

### Possible Error:
```text
ModuleNotFoundError: No module named 'services.core'
```

### Why does this happen?
The application imports:
```python
from services.core import ...
from services.reports import create_report
```
Python needs to find the `services` package folder and its `core.py` and `reports.py` files at the same root level as `app.py`.

### How to fix it:
1. **Step 1:** Open your project folder on your computer.
2. **Step 2:** Locate the `services` folder.
3. **Step 3:** Confirm that these files exist:
   - `services/core.py`
   - `services/reports.py`
4. **Step 4:** Check whether `services/__init__.py` exists. Adding this file ensures Python treats the folder as a package.
5. **Step 5:** Upload the actual files to the GitHub repository, preserving their folder locations.
6. **Step 6:** Commit the changes to the `main` branch.
7. **Step 7:** Test the application again locally using PowerShell:
   ```powershell
   python -c "from services.core import init_db; from services.reports import create_report; print('Imports successful')"
   ```
   If imports succeed, PowerShell prints `Imports successful`.

---

## 7. Check `requirements.txt`

The repository's `requirements.txt` includes:
```text
streamlit>=1.35
pandas>=2.0
numpy>=1.24
plotly>=5.18
reportlab>=4.0
pypdf>=4.0
python-docx>=1.1
python-dotenv>=1.0
scikit-learn>=1.3
pytest>=8.0
```

Install them using:
```powershell
pip install -r requirements.txt
```

> [!NOTE]
> Do not remove required packages without checking whether the application uses them.

---

## 8. How to Deploy on Streamlit Community Cloud

**Website:** [https://share.streamlit.io/](https://share.streamlit.io/)

- **STEP 1:** Sign in using the GitHub account that can access your repository.
- **STEP 2:** Choose **Create App**.
- **STEP 3:** Select the repository: `MASTER-SVS/PROJECT-DEMO-TALENT-MANAGE`
- **STEP 4:** Select the branch: `main` (where the completed project is stored).
- **STEP 5:** Set the main application file path to: `app.py`
- **STEP 6:** Deploy the application.
- **STEP 7:** Check the deployment logs if startup fails.

Streamlit Community Cloud installs dependencies from `requirements.txt`. After a successful deployment, you will receive a shareable web link.

---

## 9. Database and Security

TalentSphere uses **SQLite**. The database is created automatically at:
```text
data/talentsphere.db
```
The application stores user profiles, skills, assessments, and progress information.

### Important Security Rules:
1. **Never upload passwords or API keys.**
2. **Never upload your real `.env` file** (keep `.env.example` with placeholders).
3. **Do not upload the `.venv` folder.**
4. **Do not upload your local SQLite database** (`data/talentsphere.db`).
5. **Use fictional sample information** when testing a public demo.
6. **Do not use temporary hosted SQLite storage as a permanent employee database.** A hosted application may reset local database information when its container is rebuilt.
7. Before organizational use, arrange persistent database storage and review authentication, privacy, and access control.
8. Current career recommendations use sample role requirements and rule-based logic; they should not be treated as binding HR decisions.

---

## 10. Final Checklist

- [x] Python is installed.
- [x] `requirements.txt` packages are installed.
- [x] `app.py` exists in the repository root.
- [x] `services/core.py` is present.
- [x] `services/reports.py` is present.
- [x] `services/__init__.py` is present.
- [x] All required source files are committed to GitHub.
- [x] The application runs locally (`streamlit run app.py`).
- [x] The correct GitHub repository (`MASTER-SVS/PROJECT-DEMO-TALENT-MANAGE`) and branch (`main`) are selected.
- [x] The deployment entrypoint is `app.py`.
- [x] Deployment logs show no unresolved errors.
- [x] No secrets or private database files are uploaded.

---

## Final Note

First, restore the missing services source files to the GitHub repository. Then test the application locally, commit the complete project, and deploy it using Streamlit Community Cloud.

**Repository:**  
[https://github.com/MASTER-SVS/PROJECT-DEMO-TALENT-MANAGE](https://github.com/MASTER-SVS/PROJECT-DEMO-TALENT-MANAGE)
