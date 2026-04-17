"""
Mock LLM for Day 12 production lab.
Returns deterministic-like demo responses without external API keys.
"""
import random
import time


MOCK_RESPONSES = {
    "default": [
        "Day 12 agent is running with mock response mode.",
        "Mock AI response: deployment pipeline is healthy.",
        "Your request was processed by the production-ready mock agent.",
    ],
    "docker": [
        "Docker packages app and dependencies so it runs consistently across environments.",
    ],
    "deploy": [
        "Deployment publishes your app to a public runtime so others can call your API.",
    ],
    "health": [
        "Health check is OK. Service is operational.",
    ],
}


def ask(question: str, delay: float = 0.1) -> str:
    """Return a mock answer with small artificial latency."""
    time.sleep(delay + random.uniform(0, 0.05))

    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)

    return random.choice(MOCK_RESPONSES["default"])


def ask_stream(question: str):
    """Yield response tokens to simulate streaming output."""
    response = ask(question)
    for word in response.split():
        time.sleep(0.05)
        yield word + " "
