# API quick reference

## Health
`GET /health`

## Predict
`POST /api/predict`

```json
{"text":"example comment"}
```

## History
`GET /api/history?limit=50`

Optional:
`toxic_only=true`
or
`toxic_only=false`

## Stats
`GET /api/stats`

## Model
`GET /api/model`

## Feedback
`POST /api/feedback`

```json
{
  "request_id": "prediction-request-id",
  "correct": true,
  "note": "Looks correct"
}
```

## Export
`GET /api/export`


## Batch prediction

`POST /api/predict/batch`

```json
{
  "texts": [
    "First comment",
    "Second comment"
  ]
}
```

Returns the classification for every supplied comment.
