import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from core.llm_client import TourismAssistant
from core.memory_manager import SessionManager, CacheManager
from core.agents import MultiAgentOrchestrator
from utils.pdf_generator import generate_pdf
from utils.database import UserDatabase

# === FASTAPI APP ===
app = FastAPI(title="SmartTour Assistant")
templates = Jinja2Templates(directory="templates")

# === GLOBAL MANAGERS ===
session_manager = SessionManager()
cache_manager = CacheManager(expiry_seconds=1800)
agent_orchestrator = MultiAgentOrchestrator()
db = UserDatabase()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Ana sayfa"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    """Chat endpoint - streaming yanıt"""
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()
        user_location = data.get("location")
        
        # Kullanıcı ID'si oluştur (IP bazlı)
        client_ip = request.client.host
        user_id = session_manager.generate_user_id(client_ip)
        
        # Kullanıcı oturumunu al
        memory = session_manager.get_session(user_id)
        assistant = TourismAssistant(memory=memory)

        # === LOCATION ENRICHMENT ===
        if user_location:
            lat, lon = user_location["lat"], user_location["lon"]
            cache_key = f"geo:{lat}:{lon}"
            
            city = cache_manager.get(cache_key)
            if not city:
                try:
                    geo_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
                    geo_resp = requests.get(geo_url, headers={"User-Agent": "SmartTour"}, timeout=5)
                    if geo_resp.status_code == 200:
                        geo_data = geo_resp.json()
                        city = (geo_data.get("address", {}).get("city") or
                               geo_data.get("address", {}).get("town") or
                               geo_data.get("address", {}).get("village") or "your location")
                        cache_manager.set(cache_key, city)
                except Exception as e:
                    print(f"Geocoding error: {e}")
                    city = "your location"
            
            if "around me" in user_input.lower() or "near me" in user_input.lower():
                user_input = f"I'm currently in {city}. {user_input}"

        # === STREAMING RESPONSE ===
        async def generate_stream():
            full_response = ""
            try:
                for chunk in assistant.chat_stream(user_input):
                    full_response += chunk
                    yield f"data: {json.dumps({'token': chunk})}\n\n"
                
                # Veritabanına kaydet
                session_manager.save_message(user_id, user_input, full_response)
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(generate_stream(), media_type="text/event-stream")
    
    except Exception as e:
        print(f"Chat error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/generate_pdf")
async def generate_pdf_route(request: Request):
    """PDF oluştur"""
    try:
        data = await request.json()
        
        # Varsayılan değerler ekle
        if "title" not in data:
            data["title"] = "My Travel Plan"
        if "city" not in data:
            data["city"] = "Unknown"
        if "date" not in data:
            data["date"] = "Not specified"
        if "plan" not in data:
            data["plan"] = ["No itinerary provided"]
        if "recommendations" not in data:
            data["recommendations"] = ["No recommendations provided"]
        
        filename = f"travel_plan_{data.get('city', 'plan')}_{os.urandom(4).hex()}.pdf"
        output_path = generate_pdf(data, filename)
        
        # Kullanıcı planını kaydet
        client_ip = request.client.host
        user_id = session_manager.generate_user_id(client_ip)
        db.save_travel_plan(
            user_id=user_id,
            title=data.get("title", "Travel Plan"),
            city=data.get("city", "Unknown"),
            date_range=data.get("date", ""),
            plan_data=data
        )
        
        return FileResponse(
            output_path,
            media_type='application/pdf',
            filename=filename
        )
    except Exception as e:
        print(f"PDF ERROR: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/create_plan")
async def create_plan(request: Request):
    """Multi-agent ile otomatik plan oluştur"""
    try:
        data = await request.json()
        city = data.get("city", "Paris")
        days = data.get("days", 3)
        interests = data.get("interests", [])
        
        # Cache kontrolü
        cache_key = f"plan:{city}:{days}:{'-'.join(interests)}"
        cached_plan = cache_manager.get(cache_key)
        
        if cached_plan:
            return JSONResponse(cached_plan)
        
        # Multi-agent ile plan oluştur
        plan = agent_orchestrator.create_complete_plan(city, days, interests)
        
        # Cache'e kaydet
        cache_manager.set(cache_key, plan)
        
        # Veritabanına kaydet
        client_ip = request.client.host
        user_id = session_manager.generate_user_id(client_ip)
        db.save_travel_plan(
            user_id=user_id,
            title=f"{city} - {days} Days",
            city=city,
            date_range=f"{days} days",
            plan_data=plan
        )
        
        return JSONResponse(plan)
    
    except Exception as e:
        print(f"Plan creation error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/user/history")
async def get_user_history(request: Request):
    """Kullanıcı geçmişini getir"""
    try:
        client_ip = request.client.host
        user_id = session_manager.generate_user_id(client_ip)
        
        history = db.get_chat_history(user_id, limit=20)
        plans = db.get_travel_plans(user_id)
        favorites = db.get_favorites(user_id)
        stats = session_manager.get_user_stats(user_id)
        
        return JSONResponse({
            "success": True,
            "history": history,
            "plans": plans,
            "favorites": favorites,
            "stats": stats
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/user/favorite")
async def add_favorite(request: Request):
    """Favori ekle"""
    try:
        data = await request.json()
        client_ip = request.client.host
        user_id = session_manager.generate_user_id(client_ip)
        
        success = db.add_favorite(
            user_id=user_id,
            city=data.get("city", ""),
            category=data.get("category", "destination"),
            notes=data.get("notes", "")
        )
        
        return JSONResponse({"success": success})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/health")
async def health():
    """Sağlık kontrolü"""
    return {"status": "healthy", "service": "SmartTour Assistant"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)



