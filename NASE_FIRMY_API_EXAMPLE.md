# Naše firmy - API Integration Guide

This guide shows how to integrate with the "Naše firmy" voting template through the API.

## Overview

The "Naše firmy" template is a special voting system where:
- Teams vote for other teams in specific categories
- Categories: MASKA, KOLA, SKELET, PLAKÁT, MARKETING
- Teams cannot vote for themselves
- Results show which team won each category and which teams voted for them

## 1. Creating a "Naše firmy" Voting Session

### API Call
```bash
curl -X POST http://localhost:5000/api/v1/voting \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Naše firmy 2025",
    "description": "Annual company competition",
    "questions": [
      {
        "text": "MASKA",
        "question_type": "team_selection",
        "options": []
      },
      {
        "text": "KOLA", 
        "question_type": "team_selection",
        "options": []
      },
      {
        "text": "SKELET",
        "question_type": "team_selection", 
        "options": []
      },
      {
        "text": "PLAKÁT",
        "question_type": "team_selection",
        "options": []
      },
      {
        "text": "MARKETING",
        "question_type": "team_selection",
        "options": []
      }
    ],
    "teams": [
      {"name": "Tým Alpha", "external_id": "alpha"},
      {"name": "Tým Beta", "external_id": "beta"}, 
      {"name": "Tým Gamma", "external_id": "gamma"},
      {"name": "Tým Delta", "external_id": "delta"}
    ]
  }'
```

### Response
```json
{
  "id": "123456",
  "message": "Voting session created successfully",
  "voting_url": "/hlasovani/123456",
  "qr_url": "/presentation/123456"
}
```

## 2. Starting the Voting Session

```bash
curl -X POST http://localhost:5000/api/v1/voting/123456/start
```

## 3. Submitting Votes

When a team votes, they select one team for each category:

```bash
curl -X POST http://localhost:5000/api/v1/voting/123456/vote \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": 1,
    "team_id": 2,
    "voter_identifier": "team_alpha_voter",
    "voter_team_id": 1,
    "option_selected": "Tým Beta"
  }'
```

### Parameters:
- `question_id`: Category question ID (MASKA, KOLA, etc.)
- `team_id`: ID of team being voted FOR
- `voter_team_id`: ID of team that is voting
- `voter_identifier`: Unique identifier for the voter
- `option_selected`: Name of the team being voted for

## 4. Getting "Naše firmy" Results

### Special Results Endpoint
```bash
curl http://localhost:5000/api/v1/voting/123456/results/nase-firmy
```

### Response Format
```json
{
  "session_id": "123456",
  "session_name": "Naše firmy 2025", 
  "template": "Naše firmy",
  "results": {
    "MASKA": {
      "winning_team": "Tým Beta",
      "votes_received": 3,
      "voting_teams": ["Tým Alpha", "Tým Gamma", "Tým Delta"]
    },
    "KOLA": {
      "winning_team": "Tým Alpha", 
      "votes_received": 2,
      "voting_teams": ["Tým Beta", "Tým Gamma"]
    },
    "SKELET": {
      "winning_team": "Tým Delta",
      "votes_received": 2, 
      "voting_teams": ["Tým Alpha", "Tým Beta"]
    },
    "PLAKÁT": {
      "winning_team": "Tým Gamma",
      "votes_received": 3,
      "voting_teams": ["Tým Alpha", "Tým Beta", "Tým Delta"]
    },
    "MARKETING": {
      "winning_team": "Tým Beta",
      "votes_received": 2,
      "voting_teams": ["Tým Alpha", "Tým Delta"]
    }
  }
}
```

## 5. Stopping the Voting

```bash
curl -X POST http://localhost:5000/api/v1/voting/123456/stop
```

## 6. Python Integration Example

```python
import requests
import json

class NaseFirmyAPI:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
    
    def create_voting(self, session_name, teams):
        """Create a new Naše firmy voting session"""
        categories = ["MASKA", "KOLA", "SKELET", "PLAKÁT", "MARKETING"]
        
        questions = [
            {
                "text": category,
                "question_type": "team_selection",
                "options": []
            } for category in categories
        ]
        
        teams_data = [
            {
                "name": team,
                "external_id": team.lower().replace(" ", "_")
            } for team in teams
        ]
        
        payload = {
            "name": session_name,
            "questions": questions,
            "teams": teams_data
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/voting",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        return response.json() if response.status_code == 201 else None
    
    def start_voting(self, voting_id):
        """Start the voting session"""
        response = requests.post(f"{self.base_url}/api/v1/voting/{voting_id}/start")
        return response.status_code == 200
    
    def stop_voting(self, voting_id):
        """Stop the voting session"""
        response = requests.post(f"{self.base_url}/api/v1/voting/{voting_id}/stop")
        return response.status_code == 200
    
    def get_results(self, voting_id):
        """Get Naše firmy results"""
        response = requests.get(f"{self.base_url}/api/v1/voting/{voting_id}/results/nase-firmy")
        return response.json() if response.status_code == 200 else None
    
    def update_teams(self, voting_id, teams):
        """Update teams from external system"""
        teams_data = [
            {
                "name": team,
                "external_id": team.lower().replace(" ", "_")
            } for team in teams
        ]
        
        response = requests.post(
            f"{self.base_url}/api/v1/voting/{voting_id}/teams",
            headers={"Content-Type": "application/json"},
            json={"teams": teams_data}
        )
        
        return response.status_code == 200

# Usage example
api = NaseFirmyAPI("http://localhost:5000")

# Create voting session
teams = ["Tým Alpha", "Tým Beta", "Tým Gamma", "Tým Delta"]
result = api.create_voting("Naše firmy 2025", teams)

if result:
    voting_id = result['id']
    print(f"Created voting session: {voting_id}")
    
    # Start voting
    if api.start_voting(voting_id):
        print("Voting started successfully")
        
        # Later... get results
        results = api.get_results(voting_id)
        if results:
            print("\nResults:")
            for category, data in results['results'].items():
                winner = data['winning_team']
                votes = data['votes_received']
                voters = ', '.join(data['voting_teams'])
                print(f"{category}: {winner} ({votes} votes from {voters})")
        
        # Stop voting
        api.stop_voting(voting_id)
        print("Voting stopped")
```

## 7. JavaScript Frontend Integration

```javascript
class NaseFirmyAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }
    
    async createVoting(sessionName, teams) {
        const categories = ["MASKA", "KOLA", "SKELET", "PLAKÁT", "MARKETING"];
        
        const questions = categories.map(category => ({
            text: category,
            question_type: "team_selection",
            options: []
        }));
        
        const teamsData = teams.map(team => ({
            name: team,
            external_id: team.toLowerCase().replace(/\s+/g, '_')
        }));
        
        const response = await fetch(`${this.baseUrl}/api/v1/voting`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: sessionName,
                questions: questions,
                teams: teamsData
            })
        });
        
        return response.ok ? await response.json() : null;
    }
    
    async getResults(votingId) {
        const response = await fetch(`${this.baseUrl}/api/v1/voting/${votingId}/results/nase-firmy`);
        return response.ok ? await response.json() : null;
    }
    
    async startVoting(votingId) {
        const response = await fetch(`${this.baseUrl}/api/v1/voting/${votingId}/start`, {
            method: 'POST'
        });
        return response.ok;
    }
    
    async stopVoting(votingId) {
        const response = await fetch(`${this.baseUrl}/api/v1/voting/${votingId}/stop`, {
            method: 'POST'
        });
        return response.ok;
    }
}

// Usage
const api = new NaseFirmyAPI('http://localhost:5000');

// Create and manage voting
async function runNaseFirmyVoting() {
    const teams = ['Tým Alpha', 'Tým Beta', 'Tým Gamma', 'Tým Delta'];
    
    // Create voting
    const result = await api.createVoting('Naše firmy 2025', teams);
    if (!result) return;
    
    const votingId = result.id;
    console.log(`Created voting: ${votingId}`);
    console.log(`Voting URL: ${result.voting_url}`);
    console.log(`QR URL: ${result.qr_url}`);
    
    // Start voting
    await api.startVoting(votingId);
    console.log('Voting started');
    
    // Later... get results
    const results = await api.getResults(votingId);
    if (results) {
        console.log('\nResults:');
        Object.entries(results.results).forEach(([category, data]) => {
            console.log(`${category}: ${data.winning_team} (${data.votes_received} votes)`);
            console.log(`  Voted by: ${data.voting_teams.join(', ')}`);
        });
    }
    
    // Stop voting
    await api.stopVoting(votingId);
    console.log('Voting stopped');
}
```

## 8. Database Queries for Custom Analysis

For advanced analytics, you can query the database directly:

```sql
-- Get detailed vote breakdown for Naše firmy
SELECT 
    q.text as category,
    t_voted.name as winning_team,
    t_voter.name as voting_team,
    COUNT(v.id) as vote_count
FROM votes v
JOIN questions q ON v.question_id = q.id
JOIN teams t_voted ON v.team_id = t_voted.id  -- Team that received the vote
JOIN teams t_voter ON v.voter_team_id = t_voter.id  -- Team that gave the vote
WHERE v.session_id = :session_id 
    AND q.question_type = 'team_selection'
GROUP BY q.text, t_voted.name, t_voter.name
ORDER BY q.text, vote_count DESC;

-- Get winners for each category
SELECT 
    q.text as category,
    t.name as winning_team,
    COUNT(v.id) as total_votes,
    RANK() OVER (PARTITION BY q.text ORDER BY COUNT(v.id) DESC) as rank
FROM votes v
JOIN questions q ON v.question_id = q.id
JOIN teams t ON v.team_id = t.id
WHERE v.session_id = :session_id 
    AND q.question_type = 'team_selection'
GROUP BY q.text, t.name
HAVING RANK() OVER (PARTITION BY q.text ORDER BY COUNT(v.id) DESC) = 1;
```

## 9. Command Line Usage

Use the provided script to quickly create a "Naše firmy" session:

```bash
python create_nase_firmy.py
```

The script will guide you through:
1. Setting the application URL
2. Naming the voting session  
3. Adding team names
4. Creating the voting session with all 5 categories

## Summary

The "Naše firmy" template provides:
- ✅ Predefined categories (MASKA, KOLA, SKELET, PLAKÁT, MARKETING)
- ✅ Team-vs-team voting (teams can't vote for themselves)
- ✅ Specialized results API showing winners and voting teams
- ✅ Modern, responsive voting interface
- ✅ QR code generation for easy access
- ✅ Complete API for external integration
- ✅ Database support for complex analytics

Perfect for company competitions, team evaluations, and similar voting scenarios where teams evaluate each other across multiple categories.
