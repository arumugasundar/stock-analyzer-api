# Time-Series Stock Analyzer (Backend)

This is a fastAPI based backend application responsible for processing excel file along with parameters to perform computations on time-series data

## 🛠️ Technology Stack

* **Backend:** FastAPI (Python)

* **Containerization:** Docker

* **Cloud Infrastructure:** AWS (EC2, ECR, CloudFront)

* **CI/CD:** GitHub Actions

## 🛡️ Security Measures

* **Origin Protection:** API access is restricted to whitelisted domains via CORS.

* **Resource Management:** File uploads are size-limited to ensure system stability and prevent high memory usage

* **Format Validation:** Strict support for `.csv` and `.xlsx` files only.

* **Data Integrity:** Header and data validation with user-friendly error feedback.

## 🏗️ Deployment Architecture

* **Dockerized Backend:** FastAPI app is containerized and hosted on AWS ECR.

* **Compute:** Hosted on an AWS EC2 instance that pulls and runs the latest Docker images.

* **Global Delivery:** AWS CloudFront serves as a secure entry point, providing HTTPS and optimized routing.

## 🚀 Getting Started

Follow the instructions below to get the application up and running on your local machine.

---

### 1. Prerequisites
Before starting, ensure you have **Python** and **pip** installed on your system. You can verify this by running the following commands in your terminal:

```bash
python --version
pip --version
```

## 2. Installation
Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/arumugasundar/stock-analyzer-api.git
cd stock-analyzer-api
```
Install the required dependencies in a virtual environment:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1 # for windows
pip install -r ./requirements.txt
```

## 3. Running the App
To start the development server with hot-reloading:

```bash
fastapi dev .\main.py
```