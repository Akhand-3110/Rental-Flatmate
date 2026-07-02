# Rent & Flatmate Finder Platform Backend 🚀

This project implements an AI-powered compatibility engine for linking property listings and room-seeking tenants, featuring fallback structures, real-time message rooms, and email alerts[cite: 1].

## 📋 System Design Highlights

1. **Compatibility Engine & Fallback Architecture:** Calculations run asynchronously during search queries and are stored in the database to prevent duplicate computations[cite: 1]. If an external AI provider fails or tracking tokens are missing, the system automatically redirects traffic into an engineered fallback logic structure[cite: 1].
2. **Real-Time Encapsulation:** WebSocket channels use a room key structure derived from the expression variables (`listingId_tenantId`)[cite: 1]. Only matched users with an explicit `ACCEPTED` interest status are granted connection paths[cite: 1].

## ⚙️ Quick Start Installation

Ensure you have Python 3.10+ installed. Follow these steps to spin up the local server context layers:

```bash
# 1. Clone repository structures and direct to directory
cd rent_flatmate_finder

# 2. Setup your isolated runtime environment sandbox layers
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Complete system package dependency tree updates
pip install -r requirements.txt

# 4. Initialize environment variables
cp .env.example .env

# 5. Boot the live server instance loop lines
uvicorn app.main:app --reload --port 8080