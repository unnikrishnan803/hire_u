# HireU

HireU is an AI-Powered Adaptive Placement Preparation and Career Management Platform for colleges.

## Features
- **Adaptive Assessment:** Evaluate technical, aptitude, and communication skills dynamically.
- **Skill Passport:** Visual representation of student skill levels and masteries.
- **Personalized Training:** Daily adaptive tasks tailored to skill gaps and target companies.
- **Target Companies:** Company-oriented preparation and readiness mapping.
- **Opportunity Hub:** Matching students with relevant campus and off-campus opportunities.
- **Placement Officer Dashboard:** Comprehensive analytics and student management.

## Setup Instructions

1. **Clone the repository and create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Copy `.env.example` to `.env` and fill in the necessary values:
   ```bash
   cp .env.example .env
   ```

4. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Load Sample Data (Optional but recommended for demo)**
   ```bash
   python manage.py seed_data
   ```

6. **Create a Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```
   Access the app at `http://127.0.0.1:8000`.

## Architecture & Scalability
This project follows a clean Django architecture designed for future expansion, especially for implementing ML readiness prediction and LLM RAG pipelines.
