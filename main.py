import mimetypes
import os
from pathlib import Path
import smtplib
import time
from email.message import EmailMessage
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Configuration
CSV_FILE = BASE_DIR / "company_emails (1).csv"
RESUME_FILE = BASE_DIR / "Hariharan_Jaganathan (2).pdf"  # Update with your resume filename
SLEEP_BETWEEN_EMAILS = 2  # Seconds to wait between sends (keeps Gmail safe)


def send_applications():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV file not found at: {CSV_FILE}")

    # Read CSV
    df = pd.read_csv(CSV_FILE)
    total_companies = len(df)

    print(f"Connecting to Gmail SMTP server for {SENDER_EMAIL}...")
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    print("Authentication successful! Starting dispatch...\n")

    try:
        for idx, row in df.iterrows():
            company = str(row["Company Name"]).strip()
            hr_email = str(row["HR Email"]).strip()
            career_email = str(row["Career Email"]).strip()

            # Determine primary recipient and optional CC
            to_recipient = (
                hr_email
                if hr_email and hr_email.lower() != "nan"
                else career_email
            )
            cc_recipient = (
                career_email
                if career_email
                and career_email.lower() != "nan"
                and career_email != to_recipient
                else None
            )

            if not to_recipient or to_recipient.lower() == "nan":
                print(
                    f"[{idx + 1}/{total_companies}] Skipping {company}: No valid email found."
                )
                continue

            # Compose Email
            msg = EmailMessage()
            msg["Subject"] = (
                f"Application for Generative AI Engineer | Python, RAG, LangGraph & AWS Bedrock - {company} - Hariharan"
            )
            msg["From"] = SENDER_EMAIL
            msg["To"] = to_recipient
            if cc_recipient:
                msg["Cc"] = cc_recipient

            body = f"""Dear Hiring Team at {company},


I am writing to express my interest in Generative AI Engineer / AI Engineer / LLM Engineer opportunities at [Company Name].

I have **3 years and 2 months of overall professional experience** across Python application development, AI-assisted workflow automation, and Generative AI engineering.

Currently, I work as an AI Engineer at Equitas Small Finance Bank, where I contribute to LLM-powered applications and enterprise knowledge retrieval solutions. My experience includes developing RAG pipeline components involving PDF and CSV ingestion, text extraction, chunking, metadata enrichment, embedding generation, vector indexing, hybrid retrieval, and context-grounded response generation.

My technical experience aligns with several key areas of Generative AI development:

- **Programming & Backend:** Python, SQL, FastAPI, REST APIs and API integration.
- **Generative AI:** LLM integration, Amazon Bedrock (Nova Pro), prompt engineering and document-based question answering.
- **RAG & Retrieval:** LangChain, LangGraph, Sentence Transformers, BM25, cosine similarity, Reciprocal Rank Fusion (RRF) and Amazon OpenSearch.
- **Cloud & Infrastructure:** AWS S3, Lambda, API Gateway, Step Functions and PostgreSQL.
- **Engineering Practices:** Workflow orchestration, request validation, logging, monitoring, retrieval evaluation and token-cost awareness.

Previously, I also contributed to Python-based AI-assisted IT ticket classification, prioritization, routing and automated email communication workflows.

I am looking for an opportunity where I can apply my existing experience in Generative AI, RAG systems, LLM application development and Python backend engineering while contributing to real-world AI solutions.

I have attached my resume for your consideration. I would appreciate the opportunity to discuss any relevant openings that align with my experience.

Thank you for your time and consideration.

Best regards,  
Hariharan Jaganathan  
Generative AI Engineer  
Phone: 9344030851  
Email: hariharanjaganathan10@gmail.com  
LinkedIn: https://linkedin.com/in/hariharan-jaganathan
"""
            msg.set_content(body)

            # Attach Resume if it exists
            if RESUME_FILE.exists():
                ctype, encoding = mimetypes.guess_type(str(RESUME_FILE))
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)

                with open(RESUME_FILE, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=RESUME_FILE.name,
                    )

            # Send Email
            try:
                server.send_message(msg)
                print(
                    f"[{idx + 1}/{total_companies}] Sent to {company} -> To: {to_recipient}"
                    + (f" | Cc: {cc_recipient}" if cc_recipient else "")
                )
            except Exception as e:
                print(f"[{idx + 1}/{total_companies}] Failed to send to {company}: {e}")

            time.sleep(SLEEP_BETWEEN_EMAILS)

    finally:
        server.quit()
        print("\nAll emails processed and connection closed.")


if __name__ == "__main__":
    send_applications()