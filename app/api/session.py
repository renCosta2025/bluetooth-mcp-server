from fastapi import APIRouter
import uuid
from app.models.session import SessionResponse, bluetooth_scan_tool

# Création du router FastAPI
router = APIRouter()

@router.post("/mcp/v1/session", response_model=SessionResponse)
async def create_session():
    """
    Endpoint pour initialiser une session MCP
    
    Returns:
        Informations sur la session créée et les outils disponibles
    """
    # Génération d'un ID de session unique
    session_id = f"bluetooth-session-{uuid.uuid4()}"
    
    # Création de la réponse avec les outils disponibles
    return SessionResponse(
        session={"id": session_id},
        tools=[bluetooth_scan_tool]
    )