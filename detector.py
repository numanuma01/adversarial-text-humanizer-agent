import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# separate instance for the judge for clean separation
judge_llm = ChatGroq(
    temperature=0.0,
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def detect_ai_text(text):
    """
    Uses Llama-3-70B to analyze text for AI patterns.
    Returns: float (0.0 = Human, 1.0 = AI)
    """
    system_prompt = (
        "You are a Forensic Linguist specializing in AI detection. "
        "Your task is to analyze the following text and determine if it was written by an AI (like ChatGPT/Llama) or a Human.\n\n"
        "INDICATORS OF AI TEXT:\n"
        "1. Structure: Perfectly balanced paragraphs, predictable sentence length.\n"
        "2. Vocabulary: Overuse of 'crucial', 'foster', 'tapestry', 'delve', 'leverage', 'landscape'.\n"
        "3. Tone: Overly neutral, lack of strong opinion, generic 'preaching'.\n"
        "4. Fluff: Sentences that sound nice but say little.\n\n"
        "INDICATORS OF HUMAN TEXT:\n"
        "1. Imperfection: Sentence fragments, slight awkwardness, varied rhythm.\n"
        "2. Specificity: Concrete examples, strong opinions, colloquialisms.\n\n"
        "OUTPUT FORMAT: Return ONLY a raw JSON object (no markdown) with two keys:\n"
        "- 'score': A float between 0.0 (Human) and 1.0 (AI).\n"
        "- 'reason': A short, biting explanation of why."
    )

    try:
        response = judge_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"TEXT TO ANALYZE:\n{text}")
        ])
        
        # parse the JSON response
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        
        result = json.loads(content)
        
        # reasoning for debugging 
        print(f" >>> JUDGE REASONING: {result['reason']}")
        
        return result['score']

    except Exception as e:
        print(f"Judge Error: {e}")
        return 0.5  

if __name__ == "__main__":
    test_text = "In the rapidly evolving landscape of technology, it is crucial to foster innovation to leverage new opportunities."
    
    print("Analyzing text...")
    score = detect_ai_text(test_text)
    print(f"AI Score: {score}")