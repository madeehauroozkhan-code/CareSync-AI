# Citizen Intake Agent

**Owner:** Frontend Dev

## Responsibility
Understands symptoms via voice/text in any language; converts free-form conversation into structured data (symptoms, duration, age, location).

## Input Contract
```json
{
  "text": "Mujhe halka bukhaar hai, do din se",
  "audio_base64": null,
  "language": "hi",
  "latitude": 25.594,
  "longitude": 85.137
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| text | string | No* | Raw text from the patient |
| audio_base64 | string | No* | Base64-encoded audio |
| language | string | Yes | ISO language code (default: "hi") |
| latitude | float | No | GPS latitude |
| longitude | float | No | GPS longitude |

*At least one of `text` or `audio_base64` must be provided.

## Output Contract
```json
{
  "symptoms": ["fever", "headache"],
  "duration": "2 days",
  "age": 35,
  "gender": "male",
  "location": {"lat": 25.594, "lng": 85.137},
  "raw_text_translated": "I have mild fever since 2 days",
  "confidence": 0.85
}
```

## Downstream Consumer
→ **Clinical Triage Agent** (uses `symptoms`, `duration`, `age`)
