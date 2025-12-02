from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import List, Optional
import logging
import traceback
from sqlalchemy.orm import Session
import httpx

from database import engine, get_db
import models
import auth
from ai_service import ai_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DevOps Learning Chat API",
    description="API para chat educacional sobre DevOps com autenticação e múltiplos modelos de IA",
    version="2.0.0"
)

# Configure CORS
cors_env = os.getenv("CORS_ORIGINS", "*")
origins = cors_env.split(",") if cors_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gemini-2.5-flash"
    temperature: Optional[float] = 0.7
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    status: str
    conversation_id: Optional[int] = None

class GoogleAuthRequest(BaseModel):
    google_data: dict

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class ConversationCreate(BaseModel):
    title: Optional[str] = "Nova Conversa"
    model: Optional[str] = "gemini-2.5-flash"

class ConversationResponse(BaseModel):
    id: int
    title: str
    model: str
    created_at: str
    updated_at: str
    message_count: int

class ConversationDetail(BaseModel):
    id: int
    title: str
    model: str
    created_at: str
    updated_at: str
    messages: List[dict]

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    description: str

@app.get("/")
async def root():
    return {
        "message": "DevOps Learning Chat API v2.0",
        "status": "running",
        "version": "2.0.0",
        "features": ["Google OAuth", "OpenRouter", "Conversation History"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/auth/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate user with Google OAuth token"""
    try:
        google_data = request.google_data
        
        if not google_data.get("sub") or not google_data.get("email"):
            raise HTTPException(status_code=400, detail="Dados do Google incompletos")
        
        user = db.query(models.User).filter(
            models.User.google_id == google_data["sub"]
        ).first()
        
        if not user:
            user = models.User(
                google_id=google_data["sub"],
                email=google_data["email"],
                name=google_data.get("name"),
                picture=google_data.get("picture")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.name = google_data.get("name")
            user.picture = google_data.get("picture")
            db.commit()
        
        access_token = auth.create_access_token(
            data={"user_id": user.id, "email": user.email}
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na autenticação Google: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro na autenticação: {str(e)}")

@app.get("/auth/me")
async def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):
    """Get current authenticated user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Send message and get AI response"""
    try:
        logger.info(f"Chat request - Model: {request.model}, Messages: {len(request.messages)}")
        
        conversation = None
        if current_user:
            if request.conversation_id:
                conversation = db.query(models.Conversation).filter(
                    models.Conversation.id == request.conversation_id,
                    models.Conversation.user_id == current_user.id
                ).first()
            else:
                user_first_message = next((msg.content for msg in request.messages if msg.role == "user"), "Nova Conversa")
                conversation = models.Conversation(
                    user_id=current_user.id,
                    title=user_first_message[:50] + "..." if len(user_first_message) > 50 else user_first_message,
                    model=request.model
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
        
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response_text = await ai_service.generate_response(
            messages=messages_dict,
            model=request.model,
            temperature=request.temperature
        )
        
        if current_user and conversation:
            for msg in request.messages[-1:]:
                if msg.role == "user":
                    db_message = models.Message(
                        conversation_id=conversation.id,
                        role=msg.role,
                        content=msg.content
                    )
                    db.add(db_message)
            
            db_message = models.Message(
                conversation_id=conversation.id,
                role="assistant",
                content=response_text
            )
            db.add(db_message)
            db.commit()
        
        return ChatResponse(
            response=response_text,
            status="success",
            conversation_id=conversation.id if conversation else None
        )
    
    except Exception as e:
        logger.error(f"Erro no chat: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao processar mensagem: {str(e)}")

@app.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """List all conversations for current user"""
    conversations = db.query(models.Conversation).filter(
        models.Conversation.user_id == current_user.id
    ).order_by(models.Conversation.updated_at.desc()).all()
    
    return [
        ConversationResponse(
            id=conv.id,
            title=conv.title,
            model=conv.model,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
            message_count=len(conv.messages)
        )
        for conv in conversations
    ]

@app.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation details with all messages"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        model=conversation.model,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        messages=[
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in conversation.messages
        ]
    )

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversa deletada com sucesso"}

@app.get("/models", response_model=List[ModelInfo])
async def list_available_models():
    """List all available AI models"""
    models_list = [
        ModelInfo(
            id="gemini-2.5-flash",
            name="Gemini 2.5 Flash",
            provider="Google",
            description="Rápido e inteligente, ideal para alto volume"
        ),
        ModelInfo(
            id="gemini-2.5-pro",
            name="Gemini 2.5 Pro",
            provider="Google",
            description="Modelo avançado para raciocínio complexo"
        ),
        ModelInfo(
            id="x-ai/grok-4.1-fast:free",
            name="Grok 4.1 Fast",
            provider="xAI via OpenRouter",
            description="Modelo agentic com 2M context window"
        ),
        ModelInfo(
            id="kwaipilot/kat-coder-pro:free",
            name="KAT-Coder-Pro V1",
            provider="KwaiKAT via OpenRouter",
            description="Especializado em coding e engenharia de software"
        ),
        ModelInfo(
            id="openai/gpt-oss-20b:free",
            name="GPT OSS 20B",
            provider="OpenAI via OpenRouter",
            description="Modelo open-source com MoE architecture"
        ),
        ModelInfo(
            id="nvidia/nemotron-nano-9b-v2:free",
            name="Nemotron Nano 9B V2",
            provider="NVIDIA via OpenRouter",
            description="Modelo unificado para reasoning e non-reasoning"
        ),
        ModelInfo(
            id="alibaba/tongyi-deepresearch-30b-a3b:free",
            name="Tongyi DeepResearch 30B",
            provider="Alibaba via OpenRouter",
            description="Otimizado para pesquisa profunda e reasoning"
        ),
        ModelInfo(
            id="meituan/longcat-flash-chat:free",
            name="LongCat Flash Chat",
            provider="Meituan via OpenRouter",
            description="MoE com 560B params, 128K context window"
        ),
    ]
    
    return models_list


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
