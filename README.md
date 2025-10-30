# 🧭 SmartTour: AI-Powered Travel Assistant

> Your intelligent AI travel companion — built with **FastAPI**, **LangChain**, and **Ollama**.  
> SmartTour helps users explore destinations, create personalized itineraries, and get real-time travel insights using multi-agent LLM orchestration.

## 🌍 Overview

**SmartTour** is an intelligent tourism assistant that combines the power of local LLMs and real-time data APIs.  
It can generate full travel plans, summarize experiences, suggest local cuisines, and track flights and currencies — all in one place.

The system is designed with a **multi-agent architecture**, where specialized AI agents collaborate to deliver high-quality travel recommendations.

## 🧠 Key Features

✅ **Multi-Agent System** — Planner, Experience, and Summary agents collaborate to build full itineraries.  
✅ **LLM Integration** — Uses local **LLaMA 3.2 (3B)** model via **Ollama**.  
✅ **Real-Time APIs** — Fetches weather, flight, and currency data using OpenWeather, Aviationstack, and CurrencyAPI.  
✅ **Session Memory** — Stores chat history and user preferences in SQLite.  
✅ **Cache System** — Reduces redundant API calls for faster responses.  
✅ **PDF Generator** — Exports personalized travel plans as downloadable PDFs.  
✅ **Modern Web UI** — Built with custom HTML/CSS/JS and animated gradient design.  


## 💡 Example Prompts

* ✈️ Create a 5-day itinerary for Paris focused on art and gastronomy.
* 🌦️ What’s the weather in Tokyo right now?
* 💱 Convert 100 USD to EUR.
* 🗓️ Flights from IST to FCO this week.


| Agent                   | Role                                  | Description                                 |
| ----------------------- | ------------------------------------- | ------------------------------------------- |
| 🧭 **PlannerAgent**     | Generates a day-by-day itinerary      | Uses user interests and trip length         |
| 🍽️ **ExperienceAgent** | Suggests food and culture experiences | Local dishes, events, traditions            |
| 🧠 **SummaryAgent**     | Creates summary reports               | Highlights, best time to visit, budget tips |
| 🎭 **Orchestrator**     | Coordinates all agents                | Merges outputs and finalizes plan           |

| Layer          | Technologies                               |
| -------------- | ------------------------------------------ |
| **Backend**    | FastAPI, Uvicorn                           |
| **AI Engine**  | LangChain, Ollama (LLaMA 3.2 3B)           |
| **Database**   | SQLite3                                    |
| **APIs**       | OpenWeatherMap, Aviationstack, CurrencyAPI |
| **Frontend**   | Vanilla JS, HTML, CSS                      |
| **PDF Export** | FPDF                                       |


