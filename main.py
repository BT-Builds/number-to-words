import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import mangum

app = FastAPI(title="Number to Words Converter API", version="1.0.0")
# === BT Builds Standard Middleware (auto-injected) ===
from fastapi.middleware.cors import CORSMiddleware as _BTCors
app.add_middleware(_BTCors, allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], expose_headers=["X-RateLimit-Limit","X-RateLimit-Remaining","X-RateLimit-Reset"])

@app.middleware("http")
async def _bt_add_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Powered-By"] = "btbuilds"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


API_KEY_HEADER = "X-API-Key"
VALID_API_KEYS = set(os.environ.get("API_KEYS", "dev-key-12345,test-key-67890").split(","))

class NumberRequest(BaseModel):
    number: float
    language: str = "en"
    currency: Optional[str] = None
    capitalize: bool = False

class WordsResponse(BaseModel):
    number: float
    words: str
    language: str

def get_api_key(api_key: str = None):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

def require_api_key(api_key: str = Depends(lambda: None)):
    if os.environ.get("REQUIRE_AUTH", "false").lower() == "true":
        get_api_key(api_key)
    return

ONES = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
TEENS = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
THOUSANDS = ["", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion"]

CURRENCY_SYMBOLS = {
    "USD": ("dollar", "dollars", "cent", "cents"),
    "EUR": ("euro", "euros", "cent", "cents"),
    "GBP": ("pound", "pounds", "penny", "pence"),
    "JPY": ("yen", "yen", "", ""),
    "CAD": ("dollar", "dollars", "cent", "cents"),
}

def convert_below_100(n: int) -> str:
    if n < 10:
        return ONES[n]
    elif n < 20:
        return TEENS[n - 10]
    else:
        ten = TENS[n // 10]
        one = ONES[n % 10]
        return f"{ten}-{one}" if one else ten

def convert_below_1000(n: int) -> str:
    if n < 100:
        return convert_below_100(n)
    hundred = ONES[n // 100]
    rest = convert_below_100(n % 100)
    if rest:
        return f"{hundred} hundred {rest}"
    return f"{hundred} hundred"

def number_to_words(n: int) -> str:
    if n == 0:
        return "zero"
    parts = []
    group_index = 0
    while n > 0:
        group = n % 1000
        if group > 0:
            part = convert_below_1000(group)
            if THOUSANDS[group_index]:
                part += f" {THOUSANDS[group_index]}"
            parts.append(part)
        n //= 1000
        group_index += 1
    return " ".join(reversed(parts))

def number_to_currency(amount: float, currency: str) -> str:
    if currency not in CURRENCY_SYMBOLS:
        raise HTTPException(status_code=400, detail=f"Unsupported currency: {currency}")
    
    singular, plural, cent_singular, cent_plural = CURRENCY_SYMBOLS[currency]
    whole = int(abs(amount))
    decimal = round(abs(amount) % 1 * 100)
    
    words = number_to_words(whole)
    if whole != 1 and whole != 0:
        words += f" {plural}"
    elif whole == 1:
        words += f" {singular}"
    
    if cent_singular and cent_plural:
        if decimal > 0:
            if decimal == 1:
                words += f", {number_to_words(decimal)} {cent_singular}"
            else:
                words += f", {number_to_words(decimal)} {cent_plural}"
    
    if amount < 0:
        words = f"negative {words}"
    
    return words

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/convert")
async def convert(req: NumberRequest, _api_key: str = Depends(require_api_key)):
    if req.number < 0 and not req.capitalize:
        number = abs(req.number)
    else:
        number = req.number
    
    if req.currency:
        words = number_to_currency(number, req.currency)
    else:
        if number == int(number):
            words = number_to_words(int(number))
        else:
            int_part = int(number)
            decimal_part = int(round((number - int_part) * 100))
            words = number_to_words(int_part)
            if decimal_part > 0:
                words += f" point {number_to_words(decimal_part)}"
    
    if req.capitalize:
        words = words.upper()
    
    return WordsResponse(number=req.number, words=words, language=req.language)

@app.post("/validate")
async def validate(req: NumberRequest, _api_key: str = Depends(require_api_key)):
    try:
        float(req.number)
        return {"valid": True, "number": req.number}
    except (ValueError, TypeError):
        return {"valid": False, "number": req.number}

@app.get("/languages")
async def languages():
    return {"languages": ["en"], "message": "English only currently supported"}

handler = mangum.Mangum(app)