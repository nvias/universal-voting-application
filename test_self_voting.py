#!/usr/bin/env python3
"""
Test script to demonstrate self-voting capability in Naše firmy template
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def create_nase_firmy_session():
    """Create a new Naše firmy voting session"""
    data = {
        "name": "Naše firmy 2025 - Self Voting Test",
        "description": "Testing self-voting capability",
        "questions": [
            {"text": "MASKA", "question_type": "team_selection", "options": []},
            {"text": "KOLA", "question_type": "team_selection", "options": []},
            {"text": "SKELET", "question_type": "team_selection", "options": []},
            {"text": "PLAKÁT", "question_type": "team_selection", "options": []},
            {"text": "MARKETING", "question_type": "team_selection", "options": []}
        ],
        "teams": [
            {"name": "Tým Alpha", "external_id": "alpha"},
            {"name": "Tým Beta", "external_id": "beta"},
            {"name": "Tým Gamma", "external_id": "gamma"},
            {"name": "Tým Delta", "external_id": "delta"}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/voting", json=data)
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Created voting session: {result['id']}")
        print(f"   Voting URL: {BASE_URL}{result['voting_url']}")
        print(f"   QR URL: {BASE_URL}{result['qr_url']}")
        return result['id']
    else:
        print(f"❌ Failed to create session: {response.text}")
        return None

def start_voting_session(session_id):
    """Start the voting session"""
    response = requests.post(f"{BASE_URL}/api/v1/voting/{session_id}/start")
    if response.status_code == 200:
        print(f"✅ Started voting session: {session_id}")
        return True
    else:
        print(f"❌ Failed to start session: {response.text}")
        return False

def simulate_self_voting(session_id):
    """Simulate teams voting for themselves"""
    # Get session details
    response = requests.get(f"{BASE_URL}/api/v1/voting/{session_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get session details: {response.text}")
        return
    
    session_data = response.json()
    teams = session_data['teams']
    questions = session_data['questions']
    
    print(f"\n🗳️  Simulating self-voting:")
    
    for team in teams:
        for question in questions:
            # Each team votes for itself in each category
            vote_data = {
                "votes": [{
                    "question_id": question['id'],
                    "team_id": team['id'],  # Voting FOR this team
                    "voter_team_id": team['id'],  # Voting AS this team (self-vote)
                    "option_selected": team['name']
                }]
            }
            
            response = requests.post(
                f"{BASE_URL}/api/submit-vote/{session_id}",
                json=vote_data
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ {team['name']} voted for themselves in {question['text']}")
            else:
                print(f"   ❌ Failed vote: {team['name']} -> {question['text']}: {response.text}")

def get_results(session_id):
    """Get and display results"""
    response = requests.get(f"{BASE_URL}/api/v1/voting/{session_id}/results/nase-firmy")
    if response.status_code == 200:
        results = response.json()
        print(f"\n📊 Results for {results['session_name']}:")
        print("=" * 50)
        
        for category, data in results['results'].items():
            winner = data['winning_team']
            votes = data['votes_received']
            self_votes = data.get('self_votes', 0)
            
            print(f"\n🏆 {category}:")
            print(f"   Winner: {winner if winner else 'No votes'}")
            print(f"   Total votes: {votes}")
            print(f"   Self-votes: {self_votes}")
            print(f"   Voting teams: {', '.join(data['voting_teams'])}")
    else:
        print(f"❌ Failed to get results: {response.text}")

def main():
    print("🚀 Testing Naše firmy Self-Voting Capability")
    print("=" * 50)
    
    # Create session
    session_id = create_nase_firmy_session()
    if not session_id:
        return
    
    # Start session
    if not start_voting_session(session_id):
        return
    
    # Simulate self-voting
    simulate_self_voting(session_id)
    
    # Get results
    get_results(session_id)
    
    print(f"\n✅ Test completed! Visit {BASE_URL}/vysledky to see visual results.")
    print(f"   Session ID: {session_id}")

if __name__ == "__main__":
    main()
