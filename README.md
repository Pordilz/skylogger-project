# ✈️ SkyLogger: Live Aviation Telemetry Dashboard

![Python](https://img.shields.io/badge/Python-3.9-blue?style=flat&logo=python)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat&logo=postgresql)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-FF4B4B?style=flat&logo=streamlit)
![Status](https://img.shields.io/badge/Status-Completed-success)

> **Academic Project:** Software Development (DLBSEPPSD01_E)  
> **Institution:** IU International University of Applied Sciences

---

## 📖 Project Overview

**SkyLogger** is a full-stack, containerized application designed to log and visualize real-time aviation data. 

While public flight trackers (like FlightRadar24) show live traffic, they do not allow users to easily store historical telemetry for custom analysis. This project solves that problem by implementing a **Microservices Architecture** that automatically:
1.  **Ingests** live flight data (Position, Altitude, Velocity) from the OpenSky Network API.
2.  **Stores** the data in a persistent relational database (PostgreSQL).
3.  **Visualizes** the traffic on an interactive map and dashboard for historical analysis.

---

## 🏗️ Technical Architecture

The system is composed of three decoupled services orchestrated via **Docker Compose**.

```mermaid
graph TD;
    subgraph Docker Network
        A[Ingestor Service] -->|Writes Data| B[(PostgreSQL DB)];
        C[Dashboard Service] -->|Reads Data| B;
    end
    D[OpenSky API] -->|JSON Stream| A;
    E[User Browser] -->|HTTP Request| C;
