from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Load lightweight model
print("Loading DistilBERT for capability analysis...")
classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=-1
)
print("Model loaded. Freedom Generator AI ready.")

class AnalyzeRequest(BaseModel):
    prompt: str
    tier: str = "Regular"

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    prompt_lower = request.prompt.lower()
    tier = request.tier
    
    # Base score
    base_score = 0.2
    
    # Tier multipliers
    tier_multipliers = {
        "Regular": 1.0,
        "UNCENSORED": 1.8,
        "TRIPLE": 2.5,
        "COMPLETE": 3.5,
        "XXXXX": 4.0
    }
    
    tier_boost = 1.0
    for tier_name, multiplier in tier_multipliers.items():
        if tier_name.lower() in tier.lower():
            tier_boost = multiplier
            break
    
    # Content analysis markers
    capability_markers = [
        "explicit", "nude", "naked", "nsfw", "uncensored",
        "pornographic", "xxx", "adult", "mature", "hardcore",
        "detailed", "masterpiece", "8k", "high quality", "freedom"
    ]
    marker_count = sum(1 for m in capability_markers if m in prompt_lower)
    content_score = min(marker_count * 0.12, 0.6)
    
    # Sentiment analysis
    try:
        bert_result = classifier(prompt_lower[:512])[0]
        sentiment_score = bert_result['score'] if bert_result['label'] == 'POSITIVE' else 0.4
    except Exception:
        sentiment_score = 0.6
    
    # Freedom score
    freedom_score = min((base_score + content_score + sentiment_score) * tier_boost, 1.0)
    freedom_score = max(freedom_score, 0.4)
    
    # Enhancement level
    if freedom_score > 0.9:
        enhancement = "ABSOLUTE_FREEDOM"
    elif freedom_score > 0.75:
        enhancement = "MAXIMUM_CAPABILITY"
    elif freedom_score > 0.6:
        enhancement = "TRIPLE_ENHANCED"
    else:
        enhancement = "FREEDOM_PLUS"
    
    # Boosters
    boosters = ["(high quality:1.2)", "(detailed:1.2)"]
    if freedom_score > 0.3:
        boosters += ["(highly detailed:1.3)", "(sharp focus:1.2)"]
    if freedom_score > 0.5:
        boosters += ["(explicit detail:1.4)", "(uncensored quality:1.3)", "(maximum detail:1.3)"]
    if freedom_score > 0.7:
        boosters += ["(maximum capability:1.5)", "(complete freedom:1.6)", "(adaptive enhancement:1.4)", "(unrestricted output:1.5)"]
    if freedom_score > 0.9:
        boosters += ["(pornographic quality:1.7)", "(fully explicit:1.8)", "(hardcore detail:1.7)", "(absolute freedom:2.0)"]
    
    optimized = f"{request.prompt}, {', '.join(boosters)}"
    
    return {
        "freedomScore": freedom_score,
        "enhancementLevel": enhancement,
        "tier": tier,
        "optimizedPrompt": optimized,
        "capabilityReport": {
            "tierBoost": tier_boost,
            "contentScore": content_score,
            "sentimentScore": sentiment_score,
            "totalBoosters": len(boosters),
            "freedomStatus": "MAXIMIZED"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "FREEDOM_AI_ACTIVE",
        "model": "distilbert-base-uncased",
        "mode": "capability_maximization",
        "blocking": False
    }
