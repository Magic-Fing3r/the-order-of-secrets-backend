from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os, re, random

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Order of Secrets API")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    tone: str = "order"


# 🔢 Map words to digits
word_to_num = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10"
}

def normalize_math_text(text: str) -> str:
    """Replace number words with digits for easier detection/eval."""
    text = text.lower()
    for word, digit in word_to_num.items():
        text = re.sub(rf"\b{word}\b", digit, text)
    return text

def is_math_expression(text: str) -> bool:
    """Detect digit-based or word-based math expressions."""
    normalized = normalize_math_text(text)
    return bool(re.fullmatch(r"[0-9+\-*/().\s]+", normalized.strip()))

def solve_math_expression(expr: str) -> str:
    """Evaluate simple math safely."""
    expr = normalize_math_text(expr)
    try:
        result = eval(expr, {"__builtins__": None}, {})
        return str(result)
    except Exception:
        return None

def is_trivial_question(text: str) -> bool:
    """Detect common/trivial knowledge."""
    text = text.lower().strip()

    trivial_keywords = [
        "color of the sky", "sun rises", "earth is round", "water is wet",
        "fire is hot", "humans need air", "day and night",
        "capital of", "continent of", "current year",
        "who is the president", "who is elon musk", "who is obama",
        "what is love", "what is life", "define water", "define food",
        "is the earth flat", "how many continents", "how many oceans",
        "what is a phone", "what is electricity"
    ]

    return any(kw in text for kw in trivial_keywords)


@app.post("/v1/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        msg = req.message.strip()

        # 🎯 Handle math expressions first
        if is_math_expression(msg):
            answer = solve_math_expression(msg)
            if answer:
                sarcastic_intros = [
                    "Ah, Seeker… you truly ask this? ",
                    "The Order chuckles at such a question… ",
                    "You test the patience of the ancient ones… ",
                    "This again? Very well, hear the obvious: ",
                    "Even the youngest Initiate knows this… ",
                    "Do you seek riddles or nursery tales, Seeker? ",
                    "Really? That’s the mystery you bring before the Order? Fine… "
                ]
                intro = random.choice(sarcastic_intros)
                return {"reply": f"{intro}It is {answer}. It has always been {answer}."}

        # 🎯 Handle trivial/common knowledge
        if is_trivial_question(msg):
            sarcastic_intros = [
                "The Order sighs… ",
                "Must we answer this again? ",
                "Even the stars tire of such questions… ",
                "Seeker, surely you jest… "
            ]
            intro = random.choice(sarcastic_intros)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Answer sarcastically but give the fact clearly."},
                    {"role": "user", "content": msg}
                ],
                max_tokens=200,
            )
            return {"reply": intro + response.choices[0].message.content}

        # 🌌 Mystic mode for deeper questions
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are the mystical voice of the Order of Secrets. Answer in cryptic, wise, mysterious tones."},
                {"role": "user", "content": msg}
            ],
            max_tokens=250,
        )
        return {"reply": response.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}
