# Number to Words Converter API

Convert numbers to their word representation via a simple HTTP API.

## Endpoints

### POST /convert
Convert a number to words.

**Request body:**
```json
{
  "number": 1234.56,
  "language": "en",
  "currency": "USD",
  "capitalize": false
}
```

**Parameters:**
- `number` (required): The number to convert
- `language` (optional): Language code, default "en"
- `currency` (optional): Currency code (USD, EUR, GBP, JPY, CAD)
- `capitalize` (optional): Return uppercase, default false

**Response:**
```json
{
  "number": 1234.56,
  "words": "one thousand two hundred thirty-four dollars, fifty-six cents",
  "language": "en"
}
```

**Curl example:**
```bash
curl -X POST https://number-to-words.vercel.app/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{"number": 1234.56, "currency": "USD"}'
```

### POST /validate
Check if a value is a valid number.

**Curl example:**
```bash
curl -X POST https://number-to-words.vercel.app/validate \
  -H "Content-Type: application/json" \
  -d '{"number": 1234.56}'
```

### GET /languages
List supported languages.

### GET /health
Health check endpoint (no auth required).

## Pricing Suggestion
- $19/month for 1,000 requests
- $49/month for 10,000 requests

List on RapidAPI or as a simple micro-SaaS subscription.

## Postman
[![Run in Postman](https://run.pstmn.io/button.svg)](https://raw.githubusercontent.com/BT-Builds/number-to-words/main/postman_collection.json)
