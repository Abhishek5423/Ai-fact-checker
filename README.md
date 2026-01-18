AI Fact Checker: Report Verification Tool
AI Fact Checker is a Streamlit application that extracts and verifies factual claims from PDF reports using Google Gemini Flash and Tavily Web Search. It streamlines the process of auditing structured reports by cross-referencing claims with real-time web evidence.

Core Features
PDF Claim Extraction: Automatically identifies key factual claims from uploaded documents.

Live Verification: Cross-references claims against live web data via Tavily API.

Automated Verdicts: Classifies claims as Verified, Inaccurate, or False with brief reasoning.

Transparent Sourcing: Provides direct source links for every verified claim.

Tech Stack
LLM: Google Gemini Flash

Search: Tavily API

Frontend: Streamlit

Parsing: PyPDF

Quick Start
Install: pip install -r requirements.txt

Configure: Add GEMINI_API_KEY and TAVILY_API_KEY to .streamlit/secrets.toml.

Run: streamlit run app.py
