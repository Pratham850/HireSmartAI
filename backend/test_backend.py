import asyncio
import os
import sys
import logging
import httpx

# Ensure backend folder is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_hiresmart")


async def run_async_tests():
    logger.info("Starting HireSmart AI Async Test Suite for MySQL...")
    logger.info("Initializing MySQL Database tables...")
    await init_db()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Healthcheck
        logger.info("Testing GET / ...")
        res = await client.get("/")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        logger.info(f"Health check response: {res.json()}")

        # 2. Authentication
        logger.info("Testing Auth module...")
        reg_payload = {
            "email": "recruiter@hiresmart.ai",
            "password": "TestPassword123!",
            "full_name": "Senior Campus Recruiter"
        }
        res = await client.post("/auth/register", json=reg_payload)
        if res.status_code != 201:
            logger.warning(f"Registration status {res.status_code}: {res.text}")
        else:
            logger.info("Recruiter registration successful!")

        # Login
        login_payload = {
            "email": "recruiter@hiresmart.ai",
            "password": "TestPassword123!"
        }
        res = await client.post("/auth/login", json=login_payload)
        assert res.status_code == 200, f"Login failed: {res.text}"
        token_data = res.json()
        access_token = token_data.get("access_token")
        assert access_token, "No access token returned"
        logger.info("Recruiter login successful!")

        headers = {"Authorization": f"Bearer {access_token}"}
        res = await client.get("/auth/me", headers=headers)
        assert res.status_code == 200, f"Get /auth/me failed: {res.text}"
        logger.info(f"Recruiter profile: {res.json()}")

        # 3. Create Job Description
        logger.info("Testing Job Description API...")
        jd_payload = {"role": "Backend Developer"}
        res = await client.post("/job-description", json=jd_payload)
        assert res.status_code == 201, f"Job description creation failed: {res.text}"
        jd_data = res.json()
        jd_id = jd_data["id"]
        logger.info(f"Created Job Description ID {jd_id}: {jd_data['role']}")

        res = await client.get("/job-descriptions")
        assert res.status_code == 200, f"Get job descriptions failed: {res.text}"

        # 4. Mock PDF Resume Upload
        logger.info("Testing Resume Upload API...")
        pdf_filename = "test_candidate_resume.pdf"
        pdf_path = os.path.join(os.path.dirname(__file__), pdf_filename)
        
        pdf_bytes = (
            b"%PDF-1.4\n"
            b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            b"2 0 obj << /Type /Pages /Kinds [ /Page ] /Count 1 /Kids [ 3 0 R ] >> endobj\n"
            b"3 0 obj << /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
            b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
            b"5 0 obj << /Length 120 >> stream\n"
            b"BT\n/F1 12 Tf\n72 712 Td\n(John Doe - Backend Developer Resume) Tj\n"
            b"(Email: john.doe@example.com Phone: +1234567890) Tj\n"
            b"(Skills: Python, FastAPI, PostgreSQL, Docker, Git, REST APIs) Tj\nET\n"
            b"endstream\nendobj\n"
            b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000130 00000 n \n0000000243 00000 n \n0000000312 00000 n \n"
            b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n484\n%%EOF"
        )
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_filename, f, "application/pdf")}
            res = await client.post("/upload-resume", files=files)
        
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        assert res.status_code == 201, f"Upload resume failed: {res.text}"
        cand_data = res.json()
        candidate_id = cand_data["id"]
        logger.info(f"Uploaded Candidate Profile ID {candidate_id}: {cand_data['name']}")

        # 5. Candidate List & Single Retrieval
        logger.info("Testing Candidate Retrieval APIs...")
        res = await client.get("/candidates")
        assert res.status_code == 200, f"Get candidates failed: {res.text}"

        res = await client.get(f"/candidate/{candidate_id}")
        assert res.status_code == 200, f"Get candidate by ID failed: {res.text}"

        # 6. AI Candidate Ranking Engine (/analyze)
        logger.info("Testing AI Candidate Ranking (/analyze)...")
        analyze_payload = {"job_description_id": jd_id}
        res = await client.post("/analyze", json=analyze_payload)
        assert res.status_code == 200, f"/analyze failed: {res.text}"
        ranking_data = res.json()
        logger.info(f"AI Ranking complete! Analyzed {ranking_data['total_candidates_analyzed']} candidates.")

        # 7. Recruitment Analytics
        logger.info("Testing Analytics API (/analytics)...")
        res = await client.get("/analytics")
        assert res.status_code == 200, f"Get analytics failed: {res.text}"
        analytics_data = res.json()
        logger.info(f"Analytics metrics: Total candidates: {analytics_data['total_candidates']}, Avg Score: {analytics_data['average_match_score']}")

        # 8. Report Generation (Excel, CSV, JSON)
        logger.info("Testing Report Generation APIs...")
        report_req = {"job_description_id": jd_id}

        res = await client.post("/reports/excel", json=report_req)
        assert res.status_code == 200, f"Excel report failed: {res.text}"
        excel_info = res.json()
        logger.info(f"Excel report generated: {excel_info['download_url']}")

        res = await client.post("/reports/csv", json=report_req)
        assert res.status_code == 200, f"CSV report failed: {res.text}"

        res = await client.post("/reports/json", json=report_req)
        assert res.status_code == 200, f"JSON report failed: {res.text}"

        filename = excel_info["download_url"].rsplit("/", 1)[-1]
        res = await client.get(f"/reports/download/{filename}")
        assert res.status_code == 200, f"Report download failed: {res.text}"

        # 9. Email Dispatch
        logger.info("Testing SMTP Email endpoint...")
        email_payload = {
            "job_description_id": jd_id,
            "candidate_ids": [candidate_id]
        }
        res = await client.post("/email/send-shortlisted", json=email_payload)
        assert res.status_code == 200, f"Email dispatch failed: {res.text}"
        logger.info(f"Email results: {res.json()}")

        logger.info("🎉 All HireSmart AI Async Backend Suite Tests Passed on MySQL! 🚀")


if __name__ == "__main__":
    asyncio.run(run_async_tests())
