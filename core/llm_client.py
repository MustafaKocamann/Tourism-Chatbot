from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from utils.api_clients import WeatherAPI, AviationAPI, CurrencyAPI
import re

class TourismAssistant:
    """SmartTour: Gelişmiş özelliklere sahip seyahat asistanı."""

    def __init__(self, model_name: str = "llama3.2:3b", memory: ChatMessageHistory = None):
        self.llm = ChatOllama(model=model_name)
        self.memory = memory or ChatMessageHistory()
        self.interest_summary = ""
        
        # API clients
        self.weather_api = WeatherAPI()
        self.aviation_api = AviationAPI()
        self.currency_api = CurrencyAPI()

    def _build_prompt(self, user_input: str):
        """Sistem promptunu oluştur"""
        system_content = (
            "You are SmartTour, a professional, friendly, and knowledgeable tourism assistant. "
            "You help users explore destinations, plan trips, and discover cultural and culinary highlights. "
            "You have access to real-time weather, flight, and currency data. "
            "Provide concise yet inspiring answers with practical travel tips and local insights."
        )

        if self.interest_summary:
            system_content += (
                f"\n\nThe user is particularly interested in: {self.interest_summary}. "
                "You should tailor your responses with this context in mind."
            )

        system_msg = SystemMessage(content=system_content)
        return [system_msg] + self.memory.messages + [HumanMessage(content=user_input)]

    def _check_tool_usage(self, user_input: str) -> tuple:
        """Kullanıcının hangi aracı kullanmak istediğini tespit et"""
        lower_input = user_input.lower()
        
        # Weather kontrolü
        if any(word in lower_input for word in ["weather", "temperature", "forecast", "climate"]):
            city_match = re.search(r'\b(?:in|for|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', user_input)
            if city_match:
                return ("weather", city_match.group(1))
        
        # Flight kontrolü
        if any(word in lower_input for word in ["flight", "flights", "plane", "fly"]):
            # "flights from IST to FCO" pattern
            flight_match = re.search(r'from\s+([A-Z]{3})\s+to\s+([A-Z]{3})', user_input.upper())
            if flight_match:
                return ("flight", (flight_match.group(1), flight_match.group(2)))
        
        # Currency kontrolü
        if any(word in lower_input for word in ["convert", "currency", "exchange", "rate"]):
            # "convert 100 USD to EUR" pattern
            currency_match = re.search(r'(\d+\.?\d*)\s+([A-Z]{3})\s+to\s+([A-Z]{3})', user_input.upper())
            if currency_match:
                amount = float(currency_match.group(1))
                from_curr = currency_match.group(2)
                to_curr = currency_match.group(3)
                return ("currency", (amount, from_curr, to_curr))
        
        return (None, None)

    def _update_interest_summary(self):
        """İlgi alanlarını güncelle"""
        recent_history = self.memory.messages[-6:]
        history_text = "\n".join(
            f"{msg.type.upper()}: {msg.content}" for msg in recent_history 
            if isinstance(msg, (HumanMessage, AIMessage))
        )

        summarization_prompt = ChatPromptTemplate.from_messages([
            ("system", "You summarize user's travel interests from conversation history."),
            ("human", "Given this chat:\n\n{history}\n\nWhat are the user's travel preferences?")
        ])

        chain = summarization_prompt | self.llm
        result = chain.invoke({"history": history_text})
        self.interest_summary = result.content.strip()

    def chat_stream(self, user_input: str):
        """Streaming yanıt döner"""
        # Tool kullanımını kontrol et
        tool_type, tool_params = self._check_tool_usage(user_input)
        
        # Eğer bir tool kullanılacaksa, önce API'den veri al
        if tool_type == "weather" and tool_params:
            weather_data = self.weather_api.get_weather(tool_params)
            if weather_data["success"]:
                user_input = f"{user_input}\n\n[Weather Data: {weather_data['formatted']}]"
        
        elif tool_type == "flight" and tool_params:
            dep, arr = tool_params
            flights = self.aviation_api.get_flights(dep, arr)
            if flights["success"]:
                flight_info = self.aviation_api.format_flights(flights)
                user_input = f"{user_input}\n\n[Flight Data:\n{flight_info}]"
        
        elif tool_type == "currency" and tool_params:
            amount, from_curr, to_curr = tool_params
            conversion = self.currency_api.convert(amount, from_curr, to_curr)
            if conversion["success"]:
                user_input = f"{user_input}\n\n[Currency: {conversion['formatted']}]"
        
        # LLM ile yanıt üret
        messages = self._build_prompt(user_input)
        full_response = ""

        for chunk in self.llm.stream(messages):
            if hasattr(chunk, "content"):
                token = chunk.content
                full_response += token
                yield token

        # Hafızayı güncelle
        self.memory.add_user_message(user_input)
        self.memory.add_ai_message(full_response)
        self._update_interest_summary()

    def chat(self, user_input: str) -> str:
        """Streaming olmayan versiyon"""
        messages = self._build_prompt(user_input)
        response = self.llm.invoke(messages)
        self.memory.add_user_message(user_input)
        self.memory.add_ai_message(response.content)
        self._update_interest_summary()
        return response.content