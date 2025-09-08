# Order of Secrets Backend

This is the backend for the **Order of Secrets** AI app.  
It connects to OpenAI and exposes a `/v1/chat` endpoint.

## 🚀 Deployment (Render)

1. Fork or upload this repo to GitHub.
2. Go to [Render](https://render.com) → New → Web Service.
3. Connect your GitHub repo.
4. Add environment variable:
   - `OPENAI_API_KEY=your_api_key`
5. Deploy 🚀
6. Your API will be live at:
   ```
   https://your-app-name.onrender.com/v1/chat
   ```

## 📦 API Usage

POST `/v1/chat`  
Body JSON:
```json
{
  "message": "What is the secret of the Order?",
  "tone": "order"
}
```

Response:
```json
{
  "reply": "The Order whispers: Knowledge is the path to power."
}
```
