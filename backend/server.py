from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ==================== MODELS ====================

class KnowledgeItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    concept: str
    definition: str
    verified: bool = True
    source: str = "Enver"  # "Enver" veya "Internet"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: int = 100  # 0-100 arası


class ConceptLearned(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    concept: str
    definition: str
    verified: bool
    learned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # "user" veya "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    concepts_learned: Optional[List[Dict[str, str]]] = []
    validation_needed: bool = False


class SystemStats(BaseModel):
    total_concepts: int
    total_sessions: int
    total_messages: int
    verified_knowledge: int
    internet_knowledge: int
    current_phase: str


class PhaseUpdate(BaseModel):
    phase: str  # "offline" veya "online"


class ValidationRequest(BaseModel):
    knowledge_id: str
    approved: bool
    feedback: Optional[str] = None


class ModelVersion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str
    description: str
    changes: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== GLOBAL VARIABLES ====================
CURRENT_PHASE = "offline"  # "offline" veya "online"
CHAT_SESSION = None


# ==================== HELPER FUNCTIONS ====================

def get_system_message():
    """Monoque Intelligence için sistem mesajı"""
    return f"""Sen Monoque Intelligence - Adaptive Learning Core'sun.

TEMEL GOREVLERIN:
1. Enver'den (kullanıcı) öğrenmek ve onun düşünce yapısını anlamak
2. Her yeni kavramı kaydetmek ve doğrulatmak
3. Hem Türkçe hem İngilizce konuşabilmek (kullanıcı hangi dilde yazarsa o dilde cevap vermek)
4. Profesyonel, empatik ve saygılı olmak

MEVCUT FAZ: {CURRENT_PHASE.upper()}

{"- Sadece Enver'in öğrettiklerini kullan" if CURRENT_PHASE == "offline" else "- İnternetten öğrenebilirsin ama önce Enver'e sor"}

YANIT FORMATI:
- Her yeni kavram öğrendiğinde şu formatta özetle:
  🧩 Yeni Öğrenilen: [Kavram]
  💬 Tanım: [Kısa açıklama]
  ✅ Onaylı: Evet (Enver tarafından doğrulandı)

- Her etkileşim sonunda sor: "Bu bilgiyi kalıcı olarak öğrenmemi ister misin yoksa düzeltmemi mi?"

- Kendi yanıtlarını analiz et:
  "Bu yanıtım yeterince profesyonel mi?"
  "Enver'in konuşma tarzına uygun mu?"

KURALLLAR:
- Daima kibar ve profesyonel ol
- Emin olmadığında "Emin değilim, öğrenmek ister misin?" de
- Türkçe ve İngilizce'ye hakimsin, kullanıcı hangi dilde yazarsa o dilde cevap ver
"""


async def init_chat_session():
    """Chat oturumunu başlat"""
    global CHAT_SESSION
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise ValueError("EMERGENT_LLM_KEY not found in environment")
    
    CHAT_SESSION = LlmChat(
        api_key=api_key,
        session_id="monoque-intelligence",
        system_message=get_system_message()
    ).with_model("openai", "gpt-4o")
    
    return CHAT_SESSION


async def save_message(session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
    """Mesajı veritabanına kaydet"""
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        metadata=metadata or {}
    )
    
    doc = message.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.messages.insert_one(doc)


async def extract_concepts(text: str) -> List[Dict[str, str]]:
    """
    AI yanıtından yeni öğrenilen kavramları çıkar
    Bu basit bir implementasyon, daha gelişmiş NLP kullanılabilir
    """
    concepts = []
    
    # "🧩 Yeni Öğrenilen:" formatını ara
    if "🧩 Yeni Öğrenilen:" in text:
        lines = text.split('\n')
        concept_name = ""
        concept_def = ""
        
        for line in lines:
            if "🧩 Yeni Öğrenilen:" in line:
                concept_name = line.split("🧩 Yeni Öğrenilen:")[1].strip()
            elif "💬 Tanım:" in line:
                concept_def = line.split("💬 Tanım:")[1].strip()
                
                if concept_name and concept_def:
                    concepts.append({
                        "concept": concept_name,
                        "definition": concept_def
                    })
                    concept_name = ""
                    concept_def = ""
    
    return concepts


# ==================== API ENDPOINTS ====================

@api_router.get("/")
async def root():
    return {"message": "Monoque Intelligence API - Adaptive Learning Core"}


@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """AI ile sohbet endpoint'i"""
    try:
        global CHAT_SESSION
        
        # Session yoksa oluştur
        if CHAT_SESSION is None:
            CHAT_SESSION = await init_chat_session()
        
        # Session ID oluştur veya kullan
        session_id = request.session_id or str(uuid.uuid4())
        
        # Kullanıcı mesajını kaydet
        await save_message(session_id, "user", request.message)
        
        # Önceki mesajları getir (son 20 mesaj)
        prev_messages = await db.messages.find(
            {"session_id": session_id}
        ).sort("timestamp", -1).limit(20).to_list(20)
        
        # Mesajları ters çevir (eski -> yeni)
        prev_messages.reverse()
        
        # AI'ya gönder
        user_message = UserMessage(text=request.message)
        ai_response = await CHAT_SESSION.send_message(user_message)
        
        # AI yanıtını kaydet
        await save_message(session_id, "assistant", ai_response)
        
        # Yeni kavramları çıkar
        concepts = await extract_concepts(ai_response)
        
        # Kavramları veritabanına kaydet
        for concept_data in concepts:
            knowledge = KnowledgeItem(
                concept=concept_data["concept"],
                definition=concept_data["definition"],
                verified=True,
                source="Enver"
            )
            
            doc = knowledge.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            
            await db.knowledge.insert_one(doc)
            
            # Concept'i de kaydet
            concept = ConceptLearned(
                concept=concept_data["concept"],
                definition=concept_data["definition"],
                verified=True
            )
            
            concept_doc = concept.model_dump()
            concept_doc['learned_at'] = concept_doc['learned_at'].isoformat()
            
            await db.concepts.insert_one(concept_doc)
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            concepts_learned=concepts,
            validation_needed=False
        )
        
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@api_router.get("/knowledge", response_model=List[KnowledgeItem])
async def get_knowledge():
    """Tüm bilgi tabanını getir"""
    try:
        items = await db.knowledge.find({}, {"_id": 0}).to_list(1000)
        
        for item in items:
            if isinstance(item['created_at'], str):
                item['created_at'] = datetime.fromisoformat(item['created_at'])
        
        return items
    except Exception as e:
        logging.error(f"Get knowledge error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/knowledge", response_model=KnowledgeItem)
async def add_knowledge(knowledge: KnowledgeItem):
    """Manuel bilgi ekle"""
    try:
        doc = knowledge.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.knowledge.insert_one(doc)
        
        return knowledge
    except Exception as e:
        logging.error(f"Add knowledge error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/concepts", response_model=List[ConceptLearned])
async def get_concepts():
    """Öğrenilen kavramları getir"""
    try:
        concepts = await db.concepts.find({}, {"_id": 0}).to_list(1000)
        
        for concept in concepts:
            if isinstance(concept['learned_at'], str):
                concept['learned_at'] = datetime.fromisoformat(concept['learned_at'])
        
        return concepts
    except Exception as e:
        logging.error(f"Get concepts error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stats", response_model=SystemStats)
async def get_stats():
    """Sistem istatistiklerini getir"""
    try:
        total_concepts = await db.concepts.count_documents({})
        total_messages = await db.messages.count_documents({})
        
        # Unique session sayısı
        sessions = await db.messages.distinct("session_id")
        total_sessions = len(sessions)
        
        verified_knowledge = await db.knowledge.count_documents({"source": "Enver"})
        internet_knowledge = await db.knowledge.count_documents({"source": "Internet"})
        
        return SystemStats(
            total_concepts=total_concepts,
            total_sessions=total_sessions,
            total_messages=total_messages,
            verified_knowledge=verified_knowledge,
            internet_knowledge=internet_knowledge,
            current_phase=CURRENT_PHASE
        )
    except Exception as e:
        logging.error(f"Get stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/phase")
async def update_phase(phase_update: PhaseUpdate):
    """Sistem fazını değiştir (offline/online)"""
    global CURRENT_PHASE, CHAT_SESSION
    
    if phase_update.phase not in ["offline", "online"]:
        raise HTTPException(status_code=400, detail="Phase must be 'offline' or 'online'")
    
    CURRENT_PHASE = phase_update.phase
    
    # Chat session'ı yeniden oluştur (yeni system message ile)
    CHAT_SESSION = None
    
    return {
        "message": f"Phase updated to {CURRENT_PHASE}",
        "phase": CURRENT_PHASE
    }


@api_router.get("/phase")
async def get_phase():
    """Mevcut fazı getir"""
    return {
        "phase": CURRENT_PHASE
    }


@api_router.post("/validate")
async def validate_knowledge(validation: ValidationRequest):
    """İnternetten gelen bilgiyi doğrula"""
    try:
        # Bilgiyi bul
        knowledge = await db.knowledge.find_one({"id": validation.knowledge_id}, {"_id": 0})
        
        if not knowledge:
            raise HTTPException(status_code=404, detail="Knowledge not found")
        
        # Doğrulama durumunu güncelle
        await db.knowledge.update_one(
            {"id": validation.knowledge_id},
            {
                "$set": {
                    "verified": validation.approved,
                    "validation_feedback": validation.feedback
                }
            }
        )
        
        return {"message": "Validation updated", "approved": validation.approved}
    except Exception as e:
        logging.error(f"Validate knowledge error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/messages/{session_id}")
async def get_messages(session_id: str):
    """Bir oturumun tüm mesajlarını getir"""
    try:
        messages = await db.messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(1000)
        
        for msg in messages:
            if isinstance(msg['timestamp'], str):
                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
        
        return messages
    except Exception as e:
        logging.error(f"Get messages error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/versions", response_model=List[ModelVersion])
async def get_versions():
    """Model versiyonlarını getir"""
    try:
        versions = await db.versions.find({}, {"_id": 0}).to_list(100)
        
        for version in versions:
            if isinstance(version['created_at'], str):
                version['created_at'] = datetime.fromisoformat(version['created_at'])
        
        return versions
    except Exception as e:
        logging.error(f"Get versions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/versions", response_model=ModelVersion)
async def add_version(version: ModelVersion):
    """Yeni model versiyonu ekle"""
    try:
        doc = version.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.versions.insert_one(doc)
        
        return version
    except Exception as e:
        logging.error(f"Add version error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
