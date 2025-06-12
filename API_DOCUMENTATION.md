# Voting System API Documentation

## Base URL
- Development: `http://localhost:5000/api/v1`
- Production: `https://yourdomain.com/api/v1`

## Authentication
Currently, the API does not require authentication. Consider implementing API keys or JWT tokens for production use.

## Endpoints

### Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-11T10:30:00.000Z",
  "version": "1.0"
}
```

---

### Question Templates

#### Get All Templates
**GET** `/templates`

Retrieve all available question templates.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Rating Scale 1-5",
    "description": "Rate from 1 (worst) to 5 (best)",
    "question_type": "rating",
    "options": ["1", "2", "3", "4", "5"]
  }
]
```

#### Create Template
**POST** `/templates`

Create a new question template.

**Request Body:**
```json
{
  "name": "Custom Rating",
  "description": "Custom rating scale",
  "question_type": "rating",
  "options": ["1", "2", "3", "4", "5"]
}
```

**Response:**
```json
{
  "id": 2,
  "message": "Template created successfully"
}
```

---

### Voting Sessions

#### Get All Voting Sessions
**GET** `/voting`

Retrieve all voting sessions with summary information.

**Response:**
```json
[
  {
    "id": "123456",
    "name": "Team Performance Review",
    "started": true,
    "ended": false,
    "created_at": "2025-06-11T10:00:00.000Z",
    "question_count": 3,
    "team_count": 4,
    "vote_count": 12
  }
]
```

#### Create Voting Session
**POST** `/voting`

Create a new voting session from external application.

**Request Body:**
```json
{
  "name": "Team Performance Review",
  "description": "Q2 team performance evaluation",
  "questions": [
    {
      "text": "How would you rate the team's communication?",
      "question_type": "rating",
      "options": ["1", "2", "3", "4", "5"],
      "template_id": 1
    },
    {
      "text": "Did the team meet project deadlines?",
      "question_type": "multiple_choice",
      "options": ["Yes", "No", "Partially"]
    }
  ],
  "teams": [
    {
      "name": "Development Team",
      "external_id": "dev_001",
      "description": "Frontend and backend developers"
    },
    {
      "name": "Design Team",
      "external_id": "design_001",
      "description": "UX/UI designers"
    }
  ]
}
```

**Response:**
```json
{
  "id": "123456",
  "message": "Voting session created successfully",
  "voting_url": "/hlasovani/123456",
  "qr_url": "/presentation/123456"
}
```

#### Get Voting Session
**GET** `/voting/{voting_id}`

Get detailed information about a specific voting session.

**Response:**
```json
{
  "id": "123456",
  "name": "Team Performance Review",
  "description": "Q2 team performance evaluation",
  "started": true,
  "ended": false,
  "created_at": "2025-06-11T10:00:00.000Z",
  "questions": [
    {
      "id": 1,
      "text": "How would you rate the team's communication?",
      "question_type": "rating",
      "options": ["1", "2", "3", "4", "5"],
      "order_index": 0
    }
  ],
  "teams": [
    {
      "id": 1,
      "name": "Development Team",
      "external_id": "dev_001",
      "description": "Frontend and backend developers"
    }
  ]
}
```

#### Update Teams
**POST** `/voting/{voting_id}/teams`

Update teams for a voting session (useful when teams are managed externally).

**Request Body:**
```json
{
  "teams": [
    {
      "name": "Updated Team Name",
      "external_id": "team_001",
      "description": "Updated description"
    }
  ]
}
```

#### Start Voting Session
**POST** `/voting/{voting_id}/start`

Start a voting session to allow votes.

**Response:**
```json
{
  "message": "Voting session 123456 started successfully"
}
```

#### End Voting Session
**POST** `/voting/{voting_id}/end`

End a voting session to prevent further votes.

**Response:**
```json
{
  "message": "Voting session 123456 ended successfully"
}
```

---

### Voting

#### Submit Vote
**POST** `/voting/{voting_id}/vote`

Submit a single vote (typically used by the web interface).

**Request Body:**
```json
{
  "question_id": 1,
  "team_id": 1,
  "voter_identifier": "user_12345",
  "option_selected": "4",
  "numeric_value": 4
}
```

**Response:**
```json
{
  "message": "Vote submitted successfully"
}
```

#### Get Voting Results
**GET** `/voting/{voting_id}/results`

Get comprehensive voting results with flexible aggregation.

**Response:**
```json
{
  "session_id": "123456",
  "session_name": "Team Performance Review",
  "total_voters": 25,
  "results": [
    {
      "question_id": 1,
      "question_text": "How would you rate the team's communication?",
      "question_type": "rating",
      "teams": {
        "Development Team": {
          "vote_count": 12,
          "average_rating": 4.2
        },
        "Design Team": {
          "vote_count": 13,
          "average_rating": 3.8
        }
      }
    },
    {
      "question_id": 2,
      "question_text": "Did the team meet project deadlines?",
      "question_type": "multiple_choice",
      "teams": {
        "Development Team": {
          "vote_count": 12,
          "option_counts": {
            "Yes": 8,
            "No": 2,
            "Partially": 2
          }
        }
      }
    }
  ]
}
```

---

## Advanced SQL Queries for Results

The abstract database schema allows for complex result analysis through SQL queries. Here are some examples:

### Average Rating by Team
```sql
SELECT 
    t.name as team_name,
    q.text as question,
    AVG(v.numeric_value) as average_rating,
    COUNT(v.id) as vote_count
FROM votes v
JOIN teams t ON v.team_id = t.id
JOIN questions q ON v.question_id = q.id
WHERE v.session_id = :session_id AND q.question_type = 'rating'
GROUP BY t.name, q.text
ORDER BY average_rating DESC;
```

### Vote Distribution by Option
```sql
SELECT 
    t.name as team_name,
    q.text as question,
    v.option_selected,
    COUNT(v.id) as vote_count,
    ROUND(COUNT(v.id) * 100.0 / SUM(COUNT(v.id)) OVER (PARTITION BY q.id, t.id), 2) as percentage
FROM votes v
JOIN teams t ON v.team_id = t.id
JOIN questions q ON v.question_id = q.id
WHERE v.session_id = :session_id
GROUP BY t.name, q.text, v.option_selected
ORDER BY t.name, q.text, vote_count DESC;
```

### Top Performing Teams
```sql
SELECT 
    t.name as team_name,
    AVG(v.numeric_value) as overall_average,
    COUNT(DISTINCT q.id) as questions_answered,
    COUNT(v.id) as total_votes
FROM votes v
JOIN teams t ON v.team_id = t.id
JOIN questions q ON v.question_id = q.id
WHERE v.session_id = :session_id AND v.numeric_value IS NOT NULL
GROUP BY t.name
HAVING COUNT(DISTINCT q.id) >= (SELECT COUNT(*) FROM questions WHERE session_id = :session_id) * 0.8
ORDER BY overall_average DESC;
```

---

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

**400 Bad Request:**
```json
{
  "error": "Missing required fields: name, question_type"
}
```

**404 Not Found:**
```json
{
  "error": "Voting session not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error"
}
```

---

## Integration Examples

### Creating a Voting Session from External App
```python
import requests

# Create voting session
response = requests.post('http://localhost:5000/api/v1/voting', json={
    "name": "Monthly Team Review",
    "questions": [
        {
            "text": "Rate team collaboration",
            "question_type": "rating",
            "options": ["1", "2", "3", "4", "5"]
        }
    ],
    "teams": [
        {"name": "Team Alpha", "external_id": "alpha_01"},
        {"name": "Team Beta", "external_id": "beta_01"}
    ]
})

voting_id = response.json()['id']

# Start voting
requests.post(f'http://localhost:5000/api/v1/voting/{voting_id}/start')

# Get results later
results = requests.get(f'http://localhost:5000/api/v1/voting/{voting_id}/results')
print(results.json())
```

### Updating Teams from External System
```python
# Update teams when your external system changes
requests.post(f'http://localhost:5000/api/v1/voting/{voting_id}/teams', json={
    "teams": [
        {"name": "Team Alpha (Updated)", "external_id": "alpha_01"},
        {"name": "Team Gamma", "external_id": "gamma_01"}  # New team
    ]
})
```
