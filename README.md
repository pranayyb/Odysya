# Odysya

![Python](https://img.shields.io/badge/python-v3.13+-blue.svg)
![LangChain](https://img.shields.io/badge/langchain-v0.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Odysya** is an AI-powered travel planning system that creates personalized travel itineraries. Built with LangGraph and served via FastAPI, it uses a multi-agent architecture to coordinate hotels, restaurants, transportation, events, attractions, and weather data — then synthesizes everything into a detailed day-by-day itinerary.

## Features

### Multi-Agent Orchestration
Six specialized domain agents run **in parallel** via a LangGraph StateGraph, each handling a different aspect of trip planning:

- **Hotel Agent** — Searches accommodations by location, dates, budget, and amenities. Integrates with Booking.com (RapidAPI).
- **Transport Agent** — Finds flights, trains, and buses to the destination with pricing and schedules.
- **Restaurant Agent** — Discovers dining options matching cuisine preferences and budget. Integrates with Yelp.
- **Weather Agent** — Provides day-by-day weather forecasts to plan weather-appropriate activities. Integrates with OpenWeatherMap.
- **Event Agent** — Finds local events, festivals, and activities happening during the travel dates.
- **Attraction Agent** — Discovers tourist attractions, monuments, temples, beaches, parks, and museums at the destination.

A seventh agent, the **Itinerary Agent**, synthesizes all collected data into a detailed day-by-day schedule with specific timings, costs, and backup plans.

### Intelligent Replanning
- **LLM-Powered ReAct Analysis** — The ReplanAgent uses a **Think → Act → Decide** methodology to evaluate all agent results against the trip requirements.
- **Selective Retry** — Only failed or inadequate agents are re-run, successful agents are skipped on retry loops.
- **Issue Tracking** — The replanner identifies specific issues (e.g. "hotels exceed budget") and logs them for traceability.
- **Graceful Degradation** — If agents still fail after retries, the aggregator substitutes fallback data and the itinerary is generated with whatever is available.

### Grounded Itinerary Generation
- **Data-Driven Output** — The itinerary prompt explicitly forbids the LLM from hallucinating venue names, prices, or events. It may only reference data returned by the agents.

### Model Context Protocol (MCP)
- **Full MCP Implementation** — Each domain has its own MCP server and client, communicating over stdio transport.
- **Dynamic Tool Discovery** — Clients auto-discover available tools from the server on connection.
- **LLM-Based Tool Selection** — The MCP client uses the LLM to pick the best tool and extract parameters from a natural language query, with full schema awareness.
- **3-Step Query Pipeline** — (1) LLM selects tool + extracts params → (2) MCP tool executed directly → (3) LLM summarizes the raw output into a clean response.
- **Structured Output Parsing** — Raw tool results are parsed into typed Pydantic models (e.g. `Hotels`, `Weather`, `Transport`) via LLM structured output.

### Dual-Mode Data (Mock & Live APIs)
- **Independent Mock Toggles** — Each domain has its own `*_MOCK` environment variable, so you can mix mock and real data per service.
- **Realistic Mock Data** — Multi-city coverage with real hotel/restaurant names, plausible prices, ratings, and facilities for development without API keys.
- **Mock Indicator Tagging** — Responses include "(MOCK DATA)" labels when mock mode is active.
- **Real API Integrations** — Pre-configured for Booking.com (RapidAPI), Yelp, and OpenWeatherMap(Not implemented though); event and transport APIs are ready to plug in.

### Resilience & Error Handling
- **Typed Error Hierarchy** — Domain-specific exceptions (`AgentError`, `ToolError`, `ClientError`, `ServerError`) with auto-logging and HTTP-style error codes.
- **HTTP Retry with Exponential Backoff** — External API calls retry up to 3 times with 1.5× backoff delays and latency logging.
- **Per-Agent Failure Isolation** — A single agent failure never crashes the graph; other agents continue independently.
- **Async Throughout** — All agent execution, MCP communication, and HTTP calls are non-blocking.


### API & Interface Design
- **FastAPI REST Endpoint** — `POST /plan` accepts a `TripRequest` and returns a structured JSON response with the itinerary, recommendations, retry count, and notes.
- **Input Validation** — Pydantic-based validation of destination, dates, preferences, and budget with clear error messages.
- **Health Check** — `GET /health` for monitoring and load balancer readiness.
- **ABC-Based Contracts** — `MCPServer`, `MCPClient`, and `AgentToolInterface` abstract base classes ensure consistent patterns across all 6 domains, making it easy to add new agents.

## Architecture

### Graph Flow

```mermaid
graph TD
    A[POST /plan] --> B[Coordinator]

    B --> C[Hotel Agent]
    B --> D[Transport Agent]
    B --> E[Restaurant Agent]
    B --> F[Weather Agent]
    B --> G[Event Agent]
    B --> H[Attraction Agent]

    C --> I[Replanner]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I

    I -->|Retries needed & under limit| B
    I -->|All done or max retries| J[Aggregator]

    J --> K[Itinerary Agent]
    K --> L[Final Itinerary]
```

### Data Flow

```
TripRequest → Coordinator → Agents (parallel) → MCP Clients → MCP Servers (stdio)
                                                      ↓
                                               Tool Results
                                                      ↓
                                          Structured Pydantic Models
                                                      ↓
                                    Replanner (retry or proceed)
                                                      ↓
                                         Aggregator (assemble Itinerary)
                                                      ↓
                                    Itinerary Agent (LLM generates day-by-day plan)
                                                      ↓
                                              JSON Response
```

### Layered Architecture

| Layer | Components |
|-------|-----------|
| **API** | FastAPI app (`main.py`) — `/health`, `/plan` endpoints |
| **Orchestration** | LangGraph StateGraph (`planner_agent.py`) — coordinator, replanner, aggregator, itinerary nodes |
| **Agents** | Domain agents (`hotel_agent.py`, etc.) — query tools, format results via LLM |
| **Tools** | Tool wrappers (`hotel_tools.py`, etc.) — connect to MCP clients |
| **MCP Clients** | Client interfaces (`hotel_mcp_client.py`, etc.) — connect to servers via stdio, use LLM for tool selection |
| **MCP Servers** | Server implementations (`hotel_mcp_server.py`, etc.) — expose tools, fetch data (mock or API) |
| **Infrastructure** | Logger, error handler, HTTP client with retry, validator |

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pranayyb/odysya.git
   cd odysya
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Add your API keys to `.env`:
   ```env
   GROQ_API_KEY=your_groq_api_key_here

   # Optional — external service keys (mock mode is used if not set)
   RAPIDAPI_KEY=
   YELP_API_KEY=
   OPENWEATHER_API_KEY=
   EVENTS_API_KEY=
   TRANSPORT_API_KEY=
   ATTRACTION_API_KEY=
   ```

### Running

```bash
uv run main.py
```

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Plan a Trip

```bash
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Mumbai",
    "start_date": "2025-06-01",
    "end_date": "2025-06-05",
    "preferences": ["food", "culture"],
    "budget": 2000.0
  }'
```

**Response:**
```json
{
  "success": true,
  "destination": "Mumbai",
  "detailed_itinerary": "This is the proposed itinerary for a 5-day trip to Mumbai from 2025-06-01 to 2025-06-05, focused on local food experiences and key city attractions. It provides a day-by-day plan while accounting for preferences, weather conditions, and practical travel considerations...",
  "key_recommendations": [
    "Check weather updates before outdoor activities",
    "Stay within $2000 budget",
    "Focus on food activities",
    "Book accommodations and transport in advance",
    "Keep backup plans for weather-dependent activities"
  ],
  "retry_count": 3,
  "notes": "The system expanded the search by increasing the budget to $2500 and retried hotel and event discovery to improve overall results."
}

```

### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `destination` | string | Yes | Travel destination |
| `start_date` | string | Yes | Trip start date (YYYY-MM-DD) |
| `end_date` | string | Yes | Trip end date (YYYY-MM-DD) |
| `preferences` | list[string] | No | Interests (e.g. `["food", "adventure"]`) |
| `budget` | float | No | Total trip budget in USD |

## Configuration

All configuration is in `config.py` and can be overridden with environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `llama-3.3-70b-versatile` | Groq LLM model |
| `GROQ_API_KEY` | — | Required. Groq API key |
| `MAX_AGENT_RETRIES` | `3` | Max replanner retry cycles |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `HOTEL_MOCK` | `True` | Use mock hotel data |
| `TRANSPORT_MOCK` | `True` | Use mock transport data |
| `RESTAURANT_MOCK` | `True` | Use mock restaurant data |
| `WEATHER_MOCK` | `True` | Use mock weather data |
| `EVENT_MOCK` | `True` | Use mock event data |
| `ATTRACTION_MOCK` | `True` | Use mock attraction data |

## Project Structure

```
odysya/
├── main.py                 # FastAPI app — /health, /plan endpoints
├── config.py               # Configuration and environment variables
├── test_workflow.py        # Workflow testing script
├── agents/                 # AI agents
│   ├── planner_agent.py    # LangGraph StateGraph orchestration
│   ├── replanner_agent.py  # ReplanAgent — retry logic
│   ├── itinerary_agent.py  # Generates final itinerary via LLM
│   ├── hotel_agent.py      # Hotel search + structured output
│   ├── restaurant_agent.py # Restaurant search + structured output
│   ├── transport_agent.py  # Transport search + structured output
│   ├── weather_agent.py    # Weather forecast + structured output
│   ├── event_agent.py      # Event search + structured output
│   └── attraction_agent.py # Attraction search + structured output
├── clients/                # MCP clients (connect to servers via stdio)
│   ├── hotel_mcp_client.py
│   ├── restaurant_mcp_client.py
│   ├── transport_mcp_client.py
│   ├── weather_mcp_client.py
│   ├── event_mcp_client.py
│   └── attraction_mcp_client.py
├── servers/                # MCP servers (expose tools, fetch data)
│   ├── hotel_mcp_server.py
│   ├── restaurant_mcp_server.py
│   ├── transport_mcp_server.py
│   ├── weather_mcp_server.py
│   ├── event_mcp_server.py
│   └── attraction_mcp_server.py
├── tools/                  # Tool wrappers connecting agents to MCP clients
│   ├── hotel_tools.py
│   ├── restaurant_tools.py
│   ├── transport_tools.py
│   ├── weather_tools.py
│   ├── event_tools.py
│   └── attraction_tools.py
├── models/                 # Pydantic data models
│   ├── trip_request.py     # Input request schema
│   ├── planner_state.py    # LangGraph state definition
│   ├── itinerary.py        # Aggregated plan model
│   ├── agent_response.py   # Standardized agent result wrapper
│   ├── replanner.py        # ReplanDecision model
│   ├── hotel.py            # Hotel/HotelItem models
│   ├── restaurant.py       # Restaurant/RestaurantItem models
│   ├── transport.py        # Transport/TransportItem models
│   ├── weather.py          # Weather/WeatherItem models
│   ├── event.py            # Event/EventItem models
│   └── attraction.py       # Attraction/AttractionItem models
├── interfaces/             # Abstract base classes
│   ├── mcp_client_interface.py  # Base MCP client with LLM tool selection
│   ├── mcp_server_interface.py  # Base MCP server interface
│   └── tool_interface.py        # Base tool interface
├── prompts/                # LLM prompt templates
│   ├── itinerary_prompts.py     # Itinerary generation prompts
│   └── replanner_prompts.py     # Replanner analysis prompts
├── utils/                  # Utilities
│   ├── logger.py           # Structured file + console logging
│   ├── error_handler.py    # Typed error classes (AgentError, ToolError, etc.)
│   ├── http_client.py      # HTTP client with retry + exponential backoff
│   ├── validator.py        # Trip request validation
│   └── get_personal_details.py  # User profile loading
├── data/                   # Mock data
│   ├── hotel_data.py
│   ├── restaurant_data.py
│   ├── transport_data.py
│   ├── weather_data.py
│   ├── events_data.py
│   └── attractions_data.py
└── logs/                   # Application logs (gitignored)
```

## Development

### Adding a New Agent

1. Create the data model in `models/` (Pydantic `BaseModel`)
2. Add mock data in `data/`
3. Create the MCP server in `servers/` (inherit `MCPServerInterface`)
4. Create the MCP client in `clients/` (inherit `MCPClient`)
5. Create the tool wrapper in `tools/` (inherit `ToolInterface`)
6. Create the agent in `agents/`
7. Register the node and edges in `planner_agent.py`

### Mock Mode

All servers run in mock mode by default, returning sample data without needing external API keys. Set the `*_MOCK` environment variables to `False` to use real APIs.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangChain](https://langchain.com/) — AI framework
- [LangGraph](https://langgraph.com/) — Multi-agent orchestration
- [Groq](https://groq.com/) — Fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) — HTTP API framework
- [Model Context Protocol](https://modelcontextprotocol.io/) — Service integration standard

---

**Made with ❤️ for travelers by a traveler**