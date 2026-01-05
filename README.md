# Adversarial Agentic Workflow
[screen-capture 1.11.55 PM.webm](https://github.com/user-attachments/assets/1637e330-577c-45e6-aa90-94f8e8576514)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Stateful_Agents-orange?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?style=for-the-badge)
![Llama 3](https://img.shields.io/badge/Model-Llama_3.3_70B-green?style=for-the-badge)

This is an autonomous agentic pipeline designed to bypass AI detection algorithms through adversarial reinforcement. It utilizes a **Directed Cyclic Graph (DCG)** where a Generator agent and a Forensic Judge agent lock into a feedback loop, iteratively refining text until it meets strict standards.

---

## System Architecture

The core of this project is built on **LangGraph**, utilizing a stateful graph architecture to manage the lifecycle of a text transformation.

```mermaid
graph LR
    A[Input Text] --> B(Generator Node)
    B --> C(Humanizer Node)
    C --> D{Judge Node}
    D -- "Score > 0.25 (Fail)" --> B
    D -- "Score < 0.25 (Pass)" --> E[Final Output]
```
---

## The Agentic Loop

1.  **Generator:** An LLM instructed in "University-Level Academic Register." It employs specific linguistic strategies like **Nominalization** (turning verbs into nouns to increase density) and **Sentence Burstiness** to mimic human variance.
2.  **Humanizer:** To break the consistent patterns of LLMs, the text undergoes **Semantic Round-Tripping**:
    * *English $\to$ Japanese $\to$ German $\to$ English*
    * This exploits translation imperfections to introduce natural syntactic variation.
3.  **Judge:** A separate LLM instance acting as a forensic linguist. It analyzes the text for:
    * AI indicator words
    * Sentence length consistency
    * Logic errors introduced by the Humanizer

---

## Key Features

* **Adversarial Feedback Loop:** The generator receives specific, actionable feedback from the Judge (e.g., *"Text is too verbose, use Nominalization"* or *"Translation artifacts detected"*).
* **Semantic Round-Tripping:** Uses `deep-translator` to physically break AI sentence structures via multi-hop translation.
* **Strict Typing:** Implemented using Python's `TypedDict` for robust state management across graph nodes.
* **Forensic Guardrails:** Hard-coded logic to detect and penalize high-frequency AI tokens ("AI Hallucinations").

---

## Installation & Setup

### Prerequisites
* Python 3.9+
* A [Groq API Key](https://console.groq.com/) (Free tier available)

### Steps

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/GhostWriter.git](https://github.com/YOUR_USERNAME/GhostWriter.git)
    cd GhostWriter
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=gsk_your_api_key_here
    ```

4.  **Run the Application**
    ```bash
    streamlit run main.py
    ```

## License
MIT.
