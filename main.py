from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os, re, random

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Order of Secrets API")

# Allow CORS (so Flutter can call it directly)
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

# -------------------------
# Helpers
# -------------------------
def is_math_expression(text: str) -> bool:
    """Check if the input is a valid math expression (digits, + - * /, parentheses, spaces)."""
    return bool(re.fullmatch(r"[0-9+\-*/().\s]+", text.strip()))

def solve_math_expression(expr: str) -> str:
    """Safely solve simple math expressions."""
    try:
        result = eval(expr, {"__builtins__": None}, {})
        return str(result)
    except Exception:
        return None

def is_unit_conversion(text: str) -> bool:
    """Detect if the text is asking for a unit conversion."""
    return bool(re.search(r"\b(in|to)\b", text.lower()))

def convert_units(text: str) -> str:
    """Very simple unit conversion handler."""
    text = text.lower().strip()

    # length conversions
    if "cm" in text and "meter" in text:
        num = float(re.findall(r"\d+", text)[0])
        return f"{num} cm is {num/100} meters."
    if "meter" in text and "cm" in text:
        num = float(re.findall(r"\d+", text)[0])
        return f"{num} meters is {num*100} cm."

    # time conversions
    if "hour" in text and "second" in text:
        num = float(re.findall(r"\d+", text)[0])
        return f"{num} hour(s) is {num*3600} seconds."
    if "minute" in text and "second" in text:
        num = float(re.findall(r"\d+", text)[0])
        return f"{num} minute(s) is {num*60} seconds."
    if "second" in text and "minute" in text:
        num = float(re.findall(r"\d+", text)[0])
        return f"{num} second(s) is {num/60} minutes."

    return "The Order is wise, but not your calculator for obscure conversions."

def is_simple_question(text: str) -> bool:
    """Detect trivial/common knowledge or simple facts."""
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

# -------------------------
# Main Chat Endpoint
# -------------------------
@app.post("/v1/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        text = req.message.strip()

        # ✅ 1. Handle math expressions
        if is_math_expression(text):
            answer = solve_math_expression(text)
            if answer:
                sarcastic_responses = [
                    f"Really? That’s the mystery you bring before the Order? Fine… it’s {answer}. It has always been {answer}.",
                    f"Seeker, even a child of the Order knows this one… {answer}.",
                    f"Do you wish to insult the Order with such simplicity? The answer is {answer}.",
                    f"The stars sigh… it is {answer}. Was there ever any doubt?",
                ]
                return {"reply": random.choice(sarcastic_responses)}

        # ✅ 2. Handle unit conversions
        if is_unit_conversion(text):
            conversion = convert_units(text)
            sarcastic_responses = [
                f"You trouble the Order with a conversion? Very well… {conversion}",
                f"Such trivial arithmetic… {conversion}",
                f"The Order rolls its eyes, but here: {conversion}",
            ]
            return {"reply": random.choice(sarcastic_responses)}

        # ✅ 3. Handle trivial knowledge (GPT with sarcasm)
        if is_simple_question(text):
            sarcastic_intros = [
                "Ah, Seeker... you truly ask this? ",
                "The Order chuckles at such a question... ",
                "You test the patience of the ancient ones... ",
                "This again? Very well, hear the obvious: ",
                "Even the youngest Initiate knows this... ",
                "Do you seek riddles or nursery tales, Seeker? ",
            ]
            chosen_intro = random.choice(sarcastic_intros)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are the Order of Secrets. For trivial or obvious questions, respond with sarcasm or playful wit, then provide the direct answer."
                    },
                    {"role": "user", "content": req.message},
                ],
                max_tokens=200,
            )
            reply = chosen_intro + response.choices[0].message.content
            return {"reply": reply}

        # 🌌 4. Mystic mode (default)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are the mystical voice of the Order of Secrets. Answer in cryptic, wise, mysterious tones. No sarcasm. Only deep mysticism."
                },
                {"role": "user", "content": req.message},
            ],
            max_tokens=250,
        )
        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        return {"error": str(e)}
