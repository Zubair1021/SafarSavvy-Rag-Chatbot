import os
import uuid
import logging
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from dotenv import load_dotenv
import json
from fastapi.middleware.cors import CORSMiddleware

# Configure real-time logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
from app import models, schemas, database
from app.vector_store import VectorStore
from app.grok_integration import DeepSeekIntegration
from app.data_loader import seed_transport_knowledge_if_needed

frontend_urls = os.getenv("FRONTEND_URLS")
if isinstance(frontend_urls, str) and frontend_urls.strip():
    allowed_origins = [u.strip() for u in frontend_urls.split(",") if u.strip()]
else:
    # Default to permissive for local dev; adjust in production via .env
    allowed_origins = ["*"]

app = FastAPI(
    title="SafarSavvy University Transport RAG",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # React dev server or same-origin
    allow_credentials=True,
    allow_methods=["*"],   # allow all HTTP methods
    allow_headers=["*"],   # allow all headers (Content-Type, Authorization, etc.)
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize vector store and AI integration
vector_store = VectorStore()
deepseek_integration = DeepSeekIntegration()

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database tables...")
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Database tables initialized!")
    
    # Automatically load SafarSavvy transport knowledge on startup
    logger.info("Loading SafarSavvy transport knowledge base...")
    try:
        seed_transport_knowledge_if_needed(vector_store)
        logger.info("✅ SafarSavvy knowledge base loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to load transport knowledge: {e}")
        logger.warning("Application will continue but may not have full knowledge base")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    messages = db.query(models.Conversation).filter(
        models.Conversation.conversation_id == conversation_id
    ).order_by(models.Conversation.timestamp).all()
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "message": msg.message,
                "is_user": msg.is_user,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/query/")
async def query_document(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        body = await request.json()
        question = body.get("question", "").strip()
        conversation_id = body.get("conversation_id")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        logger.info(f"Processing question: {question}")
        
        # Search for relevant context in vector store
        try:
            search_results = vector_store.search(question, top_k=5)
            logger.info(f"Found {len(search_results)} relevant chunks")
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to search document content")
        
        # Prepare context from search results
        if search_results and search_results[0][0] != "Knowledge base is empty. Please contact administrator.":
            # Extract chunks from the new tuple format (chunk, similarity, metadata)
            context = "\n\n".join([chunk for chunk, _, _ in search_results])
            logger.info(f"Context length: {len(context)} characters")
        else:
            context = "No relevant information found in the knowledge base."
            logger.info("No documents available for context")
        
        # Generate response using Grok AI
        try:
            # Prepare conversation history
            history = []
            if conversation_id:
                db_messages = db.query(models.Conversation).filter(
                    models.Conversation.conversation_id == conversation_id
                ).order_by(models.Conversation.timestamp).limit(10).all()
                
                for msg in db_messages:
                    role = "user" if msg.is_user else "assistant"
                    history.append({"role": role, "content": msg.message})
            
            response = deepseek_integration.generate_response(question, context, history)
            logger.info(f"Generated response: {len(response)} characters")
            
        except Exception as e:
            logger.error(f"Grok AI generation failed: {str(e)}")
            response = "I apologize, but I'm having trouble generating a response right now. Please try again later."
        
        # Store conversation in database
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        try:
            # Store user question
            user_msg = models.Conversation(
                conversation_id=conversation_id,
                message=question,
                is_user=True,
                timestamp=datetime.utcnow()
            )
            db.add(user_msg)
            
            # Store AI response
            ai_msg = models.Conversation(
                conversation_id=conversation_id,
                message=response,
                is_user=False,
                timestamp=datetime.utcnow()
            )
            db.add(ai_msg)
            
            db.commit()
            logger.info(f"Conversation stored with ID: {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {str(e)}")
            # Don't fail the request if conversation storage fails
        
        return JSONResponse(
            status_code=200,
            content={
                "response": response,
                "conversation_id": conversation_id,
                "context_used": len(context) if context != "No relevant information found in the knowledge base." else 0
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/query-stream/")
async def query_document_stream(
    request: Request,
    db: Session = Depends(get_db)
):
    """Streaming endpoint for real-time chat responses with typing effect"""
    try:
        body = await request.json()
        question = body.get("question", "").strip()
        conversation_id = body.get("conversation_id")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        logger.info(f"Processing streaming question: {question}")
        
        # Search for relevant context in vector store
        try:
            search_results = vector_store.search(question, top_k=5)
            logger.info(f"Found {len(search_results)} relevant chunks")
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to search document content")
        
        # Prepare context from search results
        if search_results and search_results[0][0] != "Knowledge base is empty. Please contact administrator.":
            context = "\n\n".join([chunk for chunk, _, _ in search_results])
            logger.info(f"Context length: {len(context)} characters")
        else:
            context = "No relevant information found in the knowledge base."
            logger.info("No documents available for context")
        
        # Store conversation in database
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        try:
            # Store user question
            user_msg = models.Conversation(
                conversation_id=conversation_id,
                message=question,
                is_user=True,
                timestamp=datetime.utcnow()
            )
            db.add(user_msg)
            db.commit()
            logger.info(f"User question stored with ID: {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to store user question: {str(e)}")
        
        async def generate_stream():
            """Generate streaming response with real-time typing effect"""
            # Send conversation ID first
            yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation_id})}\n\n"
            
            # Send typing indicator
            yield f"data: {json.dumps({'type': 'typing', 'status': 'start'})}\n\n"
            
            # Simulate thinking delay
            await asyncio.sleep(0.3)
            
            try:
                # Generate response using Grok AI
                history = []
                if conversation_id:
                    db_messages = db.query(models.Conversation).filter(
                        models.Conversation.conversation_id == conversation_id
                    ).order_by(models.Conversation.timestamp).limit(10).all()
                    
                    for msg in db_messages:
                        role = "user" if msg.is_user else "assistant"
                        history.append({"role": role, "content": msg.message})
                
                response = await deepseek_integration.generate_response_async(question, context, history)
                logger.info(f"Generated streaming response: {len(response)} characters")
                
                # Split response into words for smooth typing
                words = response.split()
                
                # Send words one by one for realistic typing effect
                for i, word in enumerate(words):
                    # Add space after each word except the last one
                    if i < len(words) - 1:
                        chunk = word + " "
                    else:
                        chunk = word
                    
                    yield f"data: {json.dumps({'type': 'content', 'chunk': chunk})}\n\n"
                    
                    # Smooth typing speed - faster for better UX
                    await asyncio.sleep(0.05)  # 50ms between words
                
                # Send typing end
                yield f"data: {json.dumps({'type': 'typing', 'status': 'end'})}\n\n"
                
                # Send complete response
                yield f"data: {json.dumps({'type': 'complete', 'response': response})}\n\n"
                
                # Store AI response in database
                try:
                    ai_msg = models.Conversation(
                        conversation_id=conversation_id,
                        message=response,
                        is_user=False,
                        timestamp=datetime.utcnow()
                    )
                    db.add(ai_msg)
                    db.commit()
                    logger.info(f"AI response stored for conversation: {conversation_id}")
                except Exception as e:
                    logger.error(f"Failed to store AI response: {str(e)}")
                
            except Exception as e:
                logger.error(f"Grok AI generation failed: {str(e)}")
                error_response = "I apologize, but I'm having trouble generating a response right now. Please try again later."
                
                # Send error response
                yield f"data: {json.dumps({'type': 'content', 'chunk': error_response})}\n\n"
                yield f"data: {json.dumps({'type': 'typing', 'status': 'end'})}\n\n"
                yield f"data: {json.dumps({'type': 'complete', 'response': error_response})}\n\n"
                
                # Store error response in database
                try:
                    ai_msg = models.Conversation(
                        conversation_id=conversation_id,
                        message=error_response,
                        is_user=False,
                        timestamp=datetime.utcnow()
                    )
                    db.add(ai_msg)
                    db.commit()
                except Exception as db_error:
                    logger.error(f"Failed to store error response: {str(db_error)}")
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in streaming query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)