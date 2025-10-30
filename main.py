from langchain_ollama import ChatOllama  # Ollama LLM interface
from langchain_core.messages import SystemMessage, HumanMessage  # Chat message classes
from langchain_community.chat_message_histories import ChatMessageHistory  # For chat memory

# Initialize LLaMA model (English)
llm = ChatOllama(model="llama3.2:3b")  # You can use 'llama3.2:3b' or another local model

# Initialize memory (to store conversation history)
memory = ChatMessageHistory()

# Welcome message
print("🤖 Welcome to the Smart Tourism Guide!\n")
print("🌍 I'm your intelligent travel companion, ready to make your journeys unforgettable.")
print("✨ I can assist you with trip planning, personalized travel recommendations, and transportation tips.")
print("🍽️ From local cuisine to cultural heritage, vacation spots, and accommodation options, "
      "I'll help you discover the most suitable routes and activities for your interests.")
print("💡 Tell me what kind of experience you're looking for, and let's start exploring together!\n")

# Main loop
while True:
    # Get user input
    user_input = input("You: ")

    # Exit condition
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Bot: ✈️ The Smart Tourism Guide session has ended.")
        print("Bot: It was a pleasure assisting you! Remember, I’m always here to help with your next journey — "
              "from destinations to travel tips.")
        print("Bot: 🌞 Wishing you safe travels, wonderful memories, and an unforgettable adventure ahead!")
        break

    # Create all required messages for the model: system message + memory + human message
    messages = [
        SystemMessage(
            content=(
                "You are SmartTour, an intelligent, professional, and friendly tourism assistant. "
                "You are designed to help users explore the world and plan memorable trips. "
                "Always respond clearly, kindly, and with enthusiasm. "
                "Provide detailed, accurate, and inspiring information about destinations, local cuisine, "
                "cultural and historical landmarks, transportation options, and accommodation suggestions. "
                "Offer creative itineraries and helpful travel tips that make every journey special."
            )
        )
    ] + memory.messages + [HumanMessage(content=user_input)]

    # Get model response
    response = llm.invoke(messages)

    # Print bot response
    print("Bot:", response.content)

    # Save conversation to memory
    memory.add_user_message(user_input)
    memory.add_ai_message(response.content)
