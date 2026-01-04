import os
import time
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from deep_translator import GoogleTranslator
from detector import detect_ai_text 

load_dotenv()

class AgentState(TypedDict):
    original_text: str
    current_text: str
    iteration_count: int
    current_score: float
    history: List[dict]
    feedback: str

llm = ChatGroq(
    temperature=0.85, 
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def generator_node(state: AgentState):
    iteration = state['iteration_count']
    current_text = state['current_text']
    original_text = state['original_text']
    feedback = state.get('feedback', "")
    
    print(f"\n--- GENERATOR (Iter {iteration}) ---")

    system_instruction = (
        "Role: You are a ruthless Senior Academic Editor. Your goal is to rewrite the text to be **sophisticated yet deliberate in word choice**.\n"
        "You must eliminate 'AI-sounding' patterns while maintaining a university-level academic register.\n\n"
        
        "### I. THE CORE STRATEGY: DENSITY OVER VOLUME\n"
        "1. **Nominalization (The Academic Secret):** Turn actions into nouns to *shorten* sentences. \n"
        "   - *Bad (Wordy):* 'The participants were confused, which made them perform poorly.'\n"
        "   - *Good (Dense):* 'Participant confusion resulted in suboptimal performance.'\n"
        "2. **No Fluff/Flowery Language:** Do not use decorative adjectives ('wonderful', 'intricate', 'amazing'). If a word does not add meaning, delete it.\n\n"

        "### II. TONE & MECHANICS\n"
        "1. **Objective Authority:** Use third-person exclusively. No 'I', 'We', or 'You'.\n"
        "2. **Epistemic Hedging:** Use 'suggests', 'indicates', 'may', or 'plausibly' instead of absolute claims. (e.g., 'This proves' -> 'This indicates').\n"
        "3. **Latinate Vocabulary:** Use 'investigate' instead of 'check out'. Use 'constitutes' instead of 'makes up'.\n\n"

        "### III. ANTI-ROBOT PROTOCOLS (Strict)\n"
        "1. **Sentence Burstiness:** AI writes sentences of equal length. You must NOT. \n"
        "   - Write one VERY short, direct sentence (<10 words). Follow it with a long, complex sentence (30+ words).\n"
        "2. **The 'Banned' List:** NEVER use these words (they trigger AI detectors):\n"
        "   - 'Delve', 'tapestry', 'landscape', 'symphony', 'leverage', 'underscore', 'multifaceted', 'testament', 'game-changer', 'crucial', 'vital', 'pivotal', 'interplay', 'meticulous', 'realm', 'foster'.\n"
        "3. **Banned Transitions:** Do not start sentences with 'Moreover', 'Furthermore', 'In conclusion', or 'Additionally'. Use 'Conversely', 'Notably', 'Hence', or 'Thus'.\n\n"

        "### IV. LENGTH CONSTRAINT\n"
        "   - The output must be **roughly the same length** as the input. Do not expand, do not cut too much. \n"
        "   - If you add complex words, remove simple ones to compensate."
        "### V. FORMATTING (CRITICAL)\n"
        "   - **OUTPUT ONLY THE REWRITTEN TEXT.**\n"
        "   - Do not include 'Here is the text:', 'Rewritten version:', or any explanations.\n"
        "   - Do not use Markdown quotes (> text) or code blocks."
    )

    if iteration == 0:
        prompt = (
            f"{system_instruction}\n\n"
            f"Input Text:\n{original_text}\n\n"
            "Task: Rewrite this text. Make it dense, academic, and human. STRICTLY ADHERE to the Banned Word list."
        )
    else:
        prompt = (
            f"{system_instruction}\n\n"
            f"### FEEDBACK FROM JUDGE:\n{feedback}\n\n"
            f"Current Draft:\n{current_text}\n\n"
            "Task: Rewrite again. You failed the previous check. \n"
            "Focus specifically on the feedback above. \n"
            "If the feedback says 'Too Long', cut words aggressively while keeping the academic tone."
        )

    response = llm.invoke([HumanMessage(content=prompt)])
    new_text = response.content
    
    if ":" in new_text[:20] and len(new_text.split(":", 1)[1]) > 50:
        new_text = new_text.split(":", 1)[1].strip()

    return {
        "current_text": new_text,
        "iteration_count": iteration + 1
    }

def humanizer_node(state: AgentState):
    """
    Implements Semantic Round-Tripping: Eng -> Jap -> Ger -> Eng
    """
    text = state['current_text']
    feedback = state.get('feedback', "").lower()
    iteration = state['iteration_count']
    
    should_scramble = (iteration == 1) or ("reads like ai" in feedback)
    
    if not should_scramble:
        print("--- HUMANIZER: Skipped (Preserving Generator's grammar fixes) ---")
        return {"current_text": text}

    print(f"--- HUMANIZER: Running Semantic Round-Trip ---")
    
    try:
        # Eng to Japanese to break sentence structure
        ja_text = GoogleTranslator(source='auto', target='ja').translate(text)
        time.sleep(0.5) 
        
        # jp to ger to realign grammar
        de_text = GoogleTranslator(source='ja', target='de').translate(ja_text)
        time.sleep(0.5)

        final_text = GoogleTranslator(source='de', target='en').translate(de_text)
        
        print(f"--- HUMANIZER: Complete. ---")
        return {"current_text": final_text}
        
    except Exception as e:
        print(f"--- HUMANIZER ERROR: {e} (Passing original text) ---")
        return {"current_text": text}

def judge_node(state: AgentState):
    text = state['current_text']
    original_text = state['original_text']
    
    ai_score = detect_ai_text(text)
    
    orig_len = len(original_text.split())
    new_len = len(text.split())
    is_too_long = new_len > (orig_len * 1.10)
    is_too_short = new_len < (orig_len * 0.85)
    
    forbidden_words = [" I ", " we ", " you ", " don't ", " can't ", " it's "]
    lower_text = text.lower()
    
    banned_list = ['delve', 'tapestry', 'leverage', 'underscore', 'crucial', 'meticulous', 'realm', 'interplay']
    has_banned_words = any(w in lower_text for w in banned_list)

    feedback = []
    
    if ai_score > 0.30:
        feedback.append("Text still reads like AI. Vary your sentence structure more.")

    if is_too_long:
        feedback.append(f"Text is too verbose ({new_len} words vs {orig_len} orig). Use 'Nominalization'.")
        if ai_score < 0.5: ai_score += 0.1 

    if is_too_short:
        feedback.append(f"Text is too short ({new_len} words vs {orig_len} orig). Use 'Expansion'.")
        if ai_score < 0.5: ai_score += 0.1 

    if has_banned_words:
        feedback.append(f"You used banned AI words ({', '.join([w for w in banned_list if w in lower_text])}). Remove them.")
        if ai_score < 0.5: ai_score += 0.2 

    # check for translation artifacts
    if " picture calculation " in text or " logic box " in text:
        feedback.append("Translation artifacts detected. Fix awkward phrasing.")

    feedback_str = " ".join(feedback) if feedback else "Good."

    print(f"--- JUDGE: Score {ai_score:.2f} | Word Count: {new_len}/{orig_len} | Feedback: {feedback_str} ---")

    return {
        "current_score": ai_score,
        "history": [{"iteration": state['iteration_count'], "text": text, "score": ai_score}],
        "feedback": feedback_str
    }

def should_continue(state: AgentState):
    score = state['current_score']
    iteration = state['iteration_count']
    MAX_RETRIES = 6
    
    if score < 0.25 and not "Too verbose" in state['feedback']:
        return "end"
    
    if iteration >= MAX_RETRIES:
        return "end"
        
    return "continue"

workflow = StateGraph(AgentState)
workflow.add_node("generator", generator_node)
workflow.add_node("humanizer", humanizer_node)
workflow.add_node("judge", judge_node)

workflow.set_entry_point("generator")
workflow.add_edge("generator", "humanizer")
workflow.add_edge("humanizer", "judge")
workflow.add_conditional_edges("judge", should_continue, {"continue": "generator", "end": END})

app = workflow.compile()