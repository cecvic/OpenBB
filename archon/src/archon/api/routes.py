from __future__ import annotations
import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from archon.core.config import ArchonConfig
from archon.core.engine import ConsensusEngine
from archon.core.models import AnalysisResult, Stance


router = APIRouter()


class AnalyzeRequest(BaseModel):
    symbol: str
    include_raw_data: bool = False


class AnalyzeResponse(BaseModel):
    symbol: str
    stance: str
    confidence: float
    suggested_action: str
    glass_box_summary: str
    execution_time_seconds: float
    providers_used: list[str]
    risk_approved: bool
    risk_level: str
    position_size_pct: float
    agent_stances: dict[str, dict[str, Any]]


def result_to_response(result: AnalysisResult, include_raw: bool = False) -> AnalyzeResponse:
    consensus = result.consensus
    agent_stances = {}

    for thought in consensus.agent_thoughts:
        agent_stances[thought.agent_type.value] = {
            "stance": thought.stance.value,
            "confidence": thought.confidence,
            "reasoning": thought.reasoning[:500],
            "key_factors": thought.key_factors,
        }
        if include_raw:
            agent_stances[thought.agent_type.value]["raw_data"] = thought.raw_data

    return AnalyzeResponse(
        symbol=result.symbol,
        stance=consensus.overall_stance.value,
        confidence=consensus.overall_confidence,
        suggested_action=consensus.suggested_action,
        glass_box_summary=result.glass_box_summary,
        execution_time_seconds=result.execution_time_seconds,
        providers_used=result.providers_used,
        risk_approved=consensus.risk_assessment.approved,
        risk_level=consensus.risk_assessment.risk_level.value,
        position_size_pct=consensus.risk_assessment.position_size_pct,
        agent_stances=agent_stances,
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_symbol(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        config = ArchonConfig()
        engine = ConsensusEngine(config)
        result = await engine.analyze(request.symbol.upper())
        return result_to_response(result, request.include_raw_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{symbol}", response_model=AnalyzeResponse)
async def analyze_symbol_get(symbol: str, include_raw_data: bool = False) -> AnalyzeResponse:
    try:
        config = ArchonConfig()
        engine = ConsensusEngine(config)
        result = await engine.analyze(symbol.upper())
        return result_to_response(result, include_raw_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/analyze/{symbol}")
async def websocket_analyze(websocket: WebSocket, symbol: str):
    await websocket.accept()

    try:
        await websocket.send_json(
            {
                "type": "status",
                "message": f"Starting analysis for {symbol.upper()}",
            }
        )

        config = ArchonConfig()
        engine = ConsensusEngine(config)

        await websocket.send_json(
            {
                "type": "status",
                "message": "Agents analyzing in parallel...",
                "agents": ["ORACLE", "QUANT", "PULSE", "SENTINEL"],
            }
        )

        result = await engine.analyze(symbol.upper())

        for thought in result.consensus.agent_thoughts:
            await websocket.send_json(
                {
                    "type": "agent_thought",
                    "agent": thought.agent_type.value.upper(),
                    "stance": thought.stance.value,
                    "confidence": thought.confidence,
                    "reasoning": thought.reasoning,
                    "key_factors": thought.key_factors,
                }
            )
            await asyncio.sleep(0.1)

        risk = result.consensus.risk_assessment
        await websocket.send_json(
            {
                "type": "risk_assessment",
                "approved": risk.approved,
                "veto_reason": risk.veto_reason,
                "risk_level": risk.risk_level.value,
                "position_size_pct": risk.position_size_pct,
                "stop_loss_pct": risk.stop_loss_pct,
            }
        )

        await websocket.send_json(
            {
                "type": "consensus",
                "symbol": result.symbol,
                "stance": result.consensus.overall_stance.value,
                "confidence": result.consensus.overall_confidence,
                "suggested_action": result.consensus.suggested_action,
                "dissenting_opinions": result.consensus.dissenting_opinions,
            }
        )

        await websocket.send_json(
            {
                "type": "complete",
                "execution_time_seconds": result.execution_time_seconds,
                "providers_used": result.providers_used,
            }
        )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json(
            {
                "type": "error",
                "message": str(e),
            }
        )
    finally:
        await websocket.close()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "archon"}
