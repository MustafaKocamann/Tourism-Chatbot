from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

class PlannerAgent:
    """🧭 Rota planlama ajanı"""
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.llm = ChatOllama(model=model_name)
    
    def create_itinerary(self, city: str, days: int, interests: list = None) -> str:
        """Günlük gezilir yer planı oluştur"""
        interests_str = ", ".join(interests) if interests else "general sightseeing"
        
        prompt = f"""You are a travel planner. Create a detailed {days}-day itinerary for {city}.
User interests: {interests_str}

Format:
Day 1:
- Morning: [activity]
- Afternoon: [activity]
- Evening: [activity]

Day 2:
...

Be specific with places, times, and practical tips."""

        messages = [
            SystemMessage(content="You are a professional travel planner."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class ExperienceAgent:
    """🍽️ Yemek ve kültür deneyimi ajanı"""
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.llm = ChatOllama(model=model_name)
    
    def recommend_experiences(self, city: str, cuisine: bool = True, culture: bool = True) -> str:
        """Yemek ve kültür önerileri"""
        prompt_parts = []
        
        if cuisine:
            prompt_parts.append(
                f"Recommend 5 must-try local dishes and best restaurants in {city}. "
                "Include dish names, descriptions, and where to find them."
            )
        
        if culture:
            prompt_parts.append(
                f"Suggest 5 cultural experiences in {city} (museums, theaters, festivals, traditions). "
                "Include practical details."
            )
        
        prompt = "\n\n".join(prompt_parts)
        
        messages = [
            SystemMessage(content="You are a local food and culture expert."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class SummaryAgent:
    """🧠 Özet ve analiz ajanı"""
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.llm = ChatOllama(model=model_name)
    
    def summarize_plan(self, itinerary: str, experiences: str) -> str:
        """Planı özetle ve kilit noktaları çıkar"""
        prompt = f"""Summarize this travel plan concisely:

ITINERARY:
{itinerary}

EXPERIENCES:
{experiences}

Provide:
1. Overview (2-3 sentences)
2. Key highlights (3-5 bullet points)
3. Budget estimate
4. Best time to visit
5. Pro tips (2-3 practical advice)"""

        messages = [
            SystemMessage(content="You are a travel summarization expert."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class MultiAgentOrchestrator:
    """🎭 Tüm ajanları koordine eden orkestratör"""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.experience = ExperienceAgent()
        self.summary = SummaryAgent()
    
    def create_complete_plan(self, city: str, days: int, interests: list = None) -> dict:
        """Komple seyahat planı oluştur"""
        print("🧭 Planner Agent: Creating itinerary...")
        itinerary = self.planner.create_itinerary(city, days, interests)
        
        print("🍽️ Experience Agent: Finding best experiences...")
        experiences = self.experience.recommend_experiences(city, cuisine=True, culture=True)
        
        print("🧠 Summary Agent: Generating summary...")
        summary = self.summary.summarize_plan(itinerary, experiences)
        
        return {
            "city": city,
            "days": days,
            "interests": interests or [],
            "itinerary": itinerary,
            "experiences": experiences,
            "summary": summary,
            "full_text": f"# {city} Travel Plan ({days} Days)\n\n{summary}\n\n## Itinerary\n{itinerary}\n\n## Experiences\n{experiences}"
        }