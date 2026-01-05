# Task Plan: Build Archon - Glass-Box Trading Intelligence Platform

## Goal
Build a multi-agent AI trading intelligence system as a wrapper around OpenBB that provides transparent, explainable analysis with specialized agents for Risk, Fundamentals, Technicals, and Sentiment.

## Phases

### Phase 1: Foundation & Core Architecture
- [x] 1.1 Create project structure and package setup
- [x] 1.2 Build core Agent base class with OpenBB MCP integration
- [x] 1.3 Create AgentThought and reasoning data models
- [x] 1.4 Implement basic LLM integration layer (Anthropic/OpenAI)
- [x] 1.5 Build configuration system for API keys and settings

### Phase 2: Specialized Agents
- [x] 2.1 SENTINEL Agent (Risk Management) - with VETO power
- [x] 2.2 ORACLE Agent (Fundamentals & Macro)
- [x] 2.3 QUANT Agent (Technical Analysis)
- [x] 2.4 PULSE Agent (Sentiment & News)
- [x] 2.5 Agent tool definitions for OpenBB data access

### Phase 3: Orchestration & Consensus
- [x] 3.1 ConsensusEngine - orchestrate multi-agent analysis
- [x] 3.2 Confidence scoring system
- [x] 3.3 Agent debate/synthesis logic
- [x] 3.4 Glass-box reasoning chain formatter
- [ ] 3.5 Strategy compilation from natural language

### Phase 4: API & Interface Layer
- [x] 4.1 FastAPI REST endpoints
- [x] 4.2 WebSocket for real-time reasoning streams
- [x] 4.3 CLI interface for quick analysis
- [ ] 4.4 Basic web UI (React) for glass-box visualization (future)

### Phase 5: Integration & Polish
- [ ] 5.1 OpenBB Desktop integration (future)
- [ ] 5.2 Telegram/Discord bot for alerts (future)
- [x] 5.3 Testing suite
- [x] 5.4 Documentation
- [x] 5.5 Example scripts

## Key Technical Decisions
- **LLM Provider**: Support both Anthropic Claude and OpenAI GPT-4 (configurable)
- **Data Layer**: Use OpenBB's existing MCP server and Python SDK directly
- **Agent Framework**: Custom lightweight implementation (not LangChain - too heavy)
- **Async First**: All agents run async for parallel analysis
- **Pydantic Models**: Type-safe data structures throughout

## Dependencies
- openbb (existing platform)
- anthropic / openai (LLM clients)
- fastapi + uvicorn (API)
- pydantic (data models)
- rich (CLI output)
- websockets (real-time)

## Errors Encountered
(Will be logged as encountered)

## Status
**MVP COMPLETE** - Core platform, API, CLI, and tests built. Ready for production use.
