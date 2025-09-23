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


def is_simple_question(text: str) -> bool:
    """Detect trivial/common knowledge or simple math questions."""
    text = text.lower().strip()

    # Simple math like "2+2", "10-3"
    if re.match(r"^\d+\s*[\+\-\*\/]\s*\d+$", text):
        return True

    # Common knowledge/trivial phrases
    trivial_keywords = [
        "2+2", "one plus one", "what is 1+1", "basic math", "multiply", "divide",
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
        if is_simple_question(req.message):
            # 🎭 Random sarcastic intros
            sarcastic_intros = [
                "Ah, Seeker... you truly ask this? ",
                "The Order chuckles at such a question... ",
                "You test the patience of the ancient ones... ",
                "This again? Very well, hear the obvious: ",
                "Even the youngest Initiate knows this... ",
                "Do you seek riddles or nursery tales, Seeker? ",
                "Really? That’s the mystery you bring before the Order? Fine… "
            ]
            chosen_intro = random.choice(sarcastic_intros)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are the Order of Secrets.
When asked trivial or obvious questions, respond with sarcasm or playful wit first,
then give the direct answer clearly.
Example: 'Really? That’s the mystery you bring before the Order? Fine… it’s 4. It has always been 4.'"""
                    },
                    {"role": "user", "content": req.message},
                ],
                max_tokens=200,
            )
            reply = chosen_intro + response.choices[0].message.content
            return {"reply": reply}

        # 🌌 Mystic mode for deeper/serious questions
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are the mystical voice of the Order of Secrets.
Answer in cryptic, wise, mysterious tones. No sarcasm. Only deep mysticism."""
                },
                {"role": "user", "content": req.message},
            ],
            max_tokens=250,
        )
        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        return {"error": str(e)}
