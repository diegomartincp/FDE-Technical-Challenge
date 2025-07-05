
# FDE Technical Challenge

This project is a complete, production-ready solution for managing inbound carrier engagement in the logistics and freight industry.
Is designed to automate and streamline the process of handling carrier calls, negotiating loads, and tracking key operational metrics, all while ensuring security and scalability.
Also will save important data regarding the call, negotiation process and sentiment analysis of the caller and store in a database while also prviding important KPIs in a dashboard

## Key Components

-   **Flask REST API:**  
    Serves as the backend for handling all business logic, including carrier verification, load search,  and call logging.
    The API is fully secured with API Key authentication and only accessible via HTTPS.
    [https://happyrobot-challenge.duckdns.org/backend/](https://happyrobot-challenge.duckdns.org/backend/)  
    
-   **PostgreSQL Database:**  
    Stores all persistent data, including loads and call logs.
    The schema is designed to capture all relevant information for each load and call.
    
-   **Apache Superset Dashboard:**  
    Provides interactive data visualization and reporting.
    Users can explore metrics such as call volume, sales closure rates, agent performance, and sentiment analysis through dashboards.
    [Superset Dashboard](https://happyrobot-challenge.duckdns.org/superset/dashboard/p/Gme1yR2rRA7/)  
    [Superset Login](https://happyrobot-challenge.duckdns.org/)  
    
-   **Nginx Reverse Proxy & Certbot (Let's Encrypt):**  
    Ensures all endpoints are served securely over HTTPS. Nginx acts as a reverse proxy, routing requests to the backend services, and Certbot automates SSL certificate management.
    
-   **Containerization with Docker Compose:**  
    All services are containerized for easy deployment, and scalation.
    The solution is currently containerized in a Google Cloud's Debian VM instance.



## Table of Contents

   * [Deployment architecture](#deployment-architecture)
   * [Requirements](#requirements)
      + [Quick install](#quick-install)
      + [Install script for ubuntu/debian](#install-script-for-ubuntudebian)
   * [Environment Variables](#environment-variables)
   * [API Endpoints](#api-endpoints)
      + [Example: Request Body for `/backend/call_logs` (POST)](#example-request-body-for-backendcall_logs-post)
      + [Example: Request Response for `/backend/validate-mc` (POST)](#example-response-body-for-backendvalidate-mc-post)
   * [Deployment Steps](#deployment-steps)
   * [Database schemas](#database-schemas)
      + [Loads table](#loads-table)
      + [Calls logs table](#calls-logs-table)
   * [Accessing Superset Dashboard](#accessing-superset-dashboard)
   * [Security and best practices](#security-and-best-practices)
   * [Important Notes](#important-notes)

---

## Deployment architecture
-   **Production:**  Deployed on Google Cloud using Duck DNS for dynamic DNS and Let's Encrypt for automated SSL certificates.
-   **Testing:**  Local deployments use ngrok and a private VPN to the US to ensure FMCSA API access.
-   **HTTPS:**  All endpoints are secured with HTTPS via Nginx and Let's Encrypt.
-   **API Security:**  All endpoints except the healthcheck require an API Key for access.
-   **Environment Variables:**  All sensitive configuration is injected at runtime via environment variables and never stored in the container images.

## Requirements

- **Docker** and **Docker Compose** must be installed on your server.
-   **US-based server or https proxy:**  The FMCSA API (`mobile.fmcsa.dot.gov`) only accepts requests from US IP addresses. For local testing, a VPN to the US is required.

### Quick install

In the `/install` folder you can find scripts to automate the installation of Docker and Docker Compose.

### Install script for ubuntu/debian
`cd install`
`bash install_docker.sh`  
`bash install_docker_compose.sh`

## Environment Variables
Create a `.env` file in the project root with the following content:
`FMCSA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`  
`INTERNAL_API_KEY=28685360-5443-4812-8182-6b6770221179`  
`POSTGRES_DB=carrier_sales`  
`POSTGRES_USER=postgres`  
`POSTGRES_PASSWORD=S3cret`  
`POSTGRES_HOST=db`  
`SUPERSET_SECRET_KEY=S3cret`  
`ADMIN_USERNAME=admin`
`ADMIN_PASSWORD=admin`
`ADMIN_EMAIL=admin@superset.local`

## API Endpoints
All API endpoints are exposed under the `/backend` path and require authentication via an API Key in the header:
| Endpoint | Method | Description | Request Body / Parameters | Response Format |
|--|--|--|--|--|
| `/validate-mc` | POST | Validates a MC number from a carrier | JSON object `{"mc_number": "123456"}`| JSON array of loads |
| `/backend/loads` | GET | Get a list of available loads | None | JSON array of loads |
| `/backend/loads/<id>` | GET | Get details for a specific load | URL parameter: `id` (integer) | JSON object |
| `/backend/call_logs` | POST | Create a new call log | JSON object (see below) | Created log as JSON |
| `/backend/health` | GET | Health check (no auth required) | None | JSON status |

**Authentication:**  
Add the following header to all requests (except healthcheck):
`Authorization: ApiKey INTERNAL_API_KEY`

### Example: Request Body for `/backend/call_logs` (POST)

`{
"duration": "85",
"agent_name": "Maria",
"negotiation_rounds": "3",
"carrier_id": "987654",
"load_id": "7",
"sale_closed": "deal-closed",
"sentiment": "sentiment-positive",
"notes": "Carrier was satisfied with the offer and agreed to the proposed rate after a brief negotiation. All details were confirmed during the call."
}`
- **duration**: (string/integer) Duration of the call in seconds.
- **agent_name**: (string) Name of the agent.
- **negotiation_rounds**: (string/integer) Number of negotiation rounds.
- **carrier_id**: (string/integer) Carrier identifier.
- **load_id**: (string/integer) Load identifier.
- **sale_closed**: (string) `"deal-closed"` or `"deal-not-closed"`.
- **sentiment**: (string) `"sentiment-positive"`, `"sentiment-neutral"`, or `"sentiment-negative"`.
- -*notes**: (string) AI summary of the call. 

### Example: Response Body for `/backend/validate-mc` (POST)
`{
"allowed_to_operate": "Y",
"dot_number": 3177404,
"is_valid": true,
"legal_name": "B MARRON LOGISTICS LLC",
"mc_number": "123456",
"status_code": "A"
}`
**All data is a direct split from the FMCSA API**

## Deployment Steps
1. **Clone the repository:**
git clone  [https://github.com/diegomartincp/FDE-Technical-Challenge.git](https://github.com/diegomartincp/FDE-Technical-Challenge.git)  
cd FDE-Technical-Challenge
2. **Install Docker and Docker Compose:** Use the scripts in `/install` or install manually.
3. **Set up environment variables:** Create a `.env` file as described above.
4. **Run the deployment script:**
`chmod +x start_containers.sh` 
`./start_containers.sh`
This will install:
	- **Flask API app**
	- **Certbot** container to create Let's encrypt certificates
	- **Nginx Proxy** using the above certificates
	- **PostgreSQL Database** already filled with dummy information
	- **Apache Superset** to create dashboards with the information available on the Postgres database
## Database schemas
### Loads table
| Field | Type | Description |
|--|--|--|
| load_id | integer (PK) | Unique load identifier |
| origin | varchar(100) | Origin city/state |
| destination|varchar(100) | Destination city/state |
| pickup_datetime | timestamp | Pickup date and time |
| delivery_datetime | timestamp | Delivery date and time |
| equipment_type | varchar(50) | Equipment required |
| loadboard_rate | numeric(10,2) | Rate offered on the loadboard |
| notes | text | Additional notes |
| weight | numeric(10,2) | Weight of the load |
| commodity_type | varchar(100) | Type of commodity |
| num_of_pieces | integer | Number of pieces |
| miles | integer | Distance in miles |
| dimensions | varchar(100) | Load dimensions |


### Calls logs table
| Field | Type | Description |
|--|--|--|
| call_id | integer (PK) | Unique call log identifier |
| call_timestamp | timestamp | Timestamp of the call (default: now) |
| carrier_id | integer | Carrier identifier |
| load_id | integer | Associated load identifier |
| sale_closed | boolean | Whether the sale was closed (`true`/`false`) |
| sentiment | varchar(20) | Sentiment: `sentiment-positive`, `sentiment-neutral`, `sentiment-negative` |
| notes | text | Notes or summary of the call |
| duration | integer | Duration of the call in seconds |
| agent_name | varchar(100) | Name of the agent handling the call |
| negotiation_rounds |  integer | Number of negotiation rounds |

## Accessing Superset Dashboard
- **URL:** [Superset Dashboard](https://happyrobot-challenge.duckdns.org/superset/dashboard/p/Gme1yR2rRA7/)  
- **Default credentials:**
	- Username: `admin`
	- Password: `admin`

## Security and best practices
-   **HTTPS enforced:**  All endpoints are only accessible via HTTPS.
-   **API Key protection:**  All endpoints except  `/backend/health`  require a valid API Key in the  `Authorization`  header.
-   **Environment variables:**  All secrets and configuration are injected at runtime and never stored in the container images.
-   **Containerization:**  All components are deployed as Docker containers for portability and reproducibility.

## Important Notes
- **FMCSA API:** The FMCSA API (`mobile.fmcsa.dot.gov`) only works if your server is physically located in the United States.
- **API authentication:** Every protected endpoint requires the `Authorization: ApiKey ...` header.
- **All services are orchestrated via Docker Compose** and are accessible only through the Nginx reverse proxy.
- **Superset dashboards are protected by login by default.** You can make them public by adjusting the `Public` role permissions in Superset. 
-  **API design:**  The  `/loads`  endpoints follow a structure similar to the official Broker API, but only include the fields required by the challenge.
---