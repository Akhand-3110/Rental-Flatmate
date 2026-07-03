# 🏠 Rental & Flatmate Finder Platform

An AI-powered rental and flatmate matching platform that connects tenants with property owners and compatible roommates. The system combines intelligent compatibility scoring, real-time communication, and automated matching workflows to help users find the most suitable living arrangements.

---

# ✨ Features

## 🔍 Smart Compatibility Matching

* AI-powered compatibility scoring between tenants and listings.
* Lifestyle, budget, and preference-based recommendations.
* Ranked search results based on compatibility scores.
* Match scores are stored to avoid redundant calculations and improve performance.

## 🛡️ Fallback Matching Engine

* Automatic fallback mechanism when external AI services are unavailable.
* Rule-based compatibility calculation ensures uninterrupted operation.
* Reliable matching experience even during provider outages.

## 🏘️ Property Listing Management

* Create, update, and manage rental property listings.
* Upload property details, rent information, amenities, and preferences.
* Search and filter listings based on location, budget, and requirements.

## 👤 Tenant Profiles

* Create detailed tenant profiles.
* Store lifestyle preferences, budget range, occupation, and housing requirements.
* Improve recommendation quality through profile data.

## ❤️ Interest & Match Workflow

* Tenants can express interest in listings.
* Property owners can accept or reject requests.
* Match status tracking:

  * Pending
  * Accepted
  * Rejected

## 💬 Real-Time Messaging

* WebSocket-based real-time communication.
* Dedicated room generation using:

```text
listingId_tenantId
```

* Only users with an **ACCEPTED** match can access chat rooms.
* Secure and isolated conversations.

## 📧 Email Notifications

Automated email alerts for:

* New match requests
* Accepted interests
* Important platform events

## 🔐 Authentication & Security

* JWT-based authentication.
* Protected API routes.
* User authorization and access control.

---

# 🏗️ System Architecture

## Compatibility Engine

1. User performs a search.
2. Compatibility score is calculated asynchronously.
3. Results are stored in the database.
4. Cached scores prevent duplicate computations.
5. Rankings are generated using compatibility scores.

### Fallback Flow

```text
Search Request
      │
      ▼
AI Compatibility Service
      │
      ├── Success
      │      ▼
      │  Store Score
      │
      └── Failure
             ▼
     Fallback Rule Engine
             ▼
         Store Score
```

### Real-Time Messaging Flow

```text
Accepted Match
       │
       ▼
Create Room Key
(listingId_tenantId)
       │
       ▼
WebSocket Connection
       │
       ▼
Secure Chat Room
```

---

# 🛠️ Tech Stack

## Backend

* Python 3.10+
* FastAPI
* SQLAlchemy
* Pydantic
* WebSockets

## Database

* PostgreSQL / SQLite

## Authentication

* JWT Tokens

## AI & Matching

* Compatibility Scoring Engine
* Fallback Recommendation Logic

## Notifications

* SMTP Email Services

---

# 📂 Project Structure

```text
rental-flatmate-finder/
│
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── websocket/
│   ├── compatibility/
│   └── main.py
│
├── migrations/
├── requirements.txt
├── .env.example
└── README.md
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/Akhand-3110/Rental-Flatmate.git
cd Rental-Flatmate
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

```bash
cp .env.example .env
```

Update the environment variables according to your setup.

## 5. Start Development Server

```bash
uvicorn app.main:app --reload --port 8080
```

Server will start at:

```text
http://localhost:8080
```

API Documentation:

```text
http://localhost:8080/docs
```

---

# 📡 WebSocket Endpoint

```text
/ws/chat/{listing_id}/{tenant_id}
```

Access is granted only when:

* Interest status = ACCEPTED
* User authentication succeeds

---

# 📧 Email Notifications

The platform sends automated notifications for:

* New interest requests
* Accepted matches
* Compatibility recommendations
* System events

Configure SMTP credentials in the `.env` file.

---

# 🚀 Future Enhancements

* Mobile application
* Video calling between matched users
* AI-generated roommate insights
* Fraud detection system
* Property recommendation engine
* Advanced analytics dashboard
* Multi-city support

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch:

```bash
git checkout -b feature-name
```

3. Commit changes:

```bash
git commit -m "Add feature"
```

4. Push branch:

```bash
git push origin feature-name
```

5. Open a Pull Request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Akhand Pratap Singh**
B.Tech CSE (Artificial Intelligence)

