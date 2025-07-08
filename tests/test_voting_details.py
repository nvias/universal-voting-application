#!/usr/bin/env python3
"""
Test script to verify detailed voting information (which team voted for which team)
"""

import os
import sys
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5000"

def test_detailed_voting_info():
    """Test that we can see which team voted for which team"""
    print("Testing detailed voting information...")
    
    # Test with the sample session
    voting_id = "655662"
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/voting/{voting_id}/results", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Detailed voting API working")
            print(f"  Session: {data.get('session_name', 'Unknown')}")
            print(f"  Total Voters: {data.get('total_voters', 0)}")
            print()
            
            # Check if we have voting details
            has_voting_details = False
            for result in data.get('results', []):
                if 'voting_details' in result and result['voting_details']:
                    has_voting_details = True
                    break
            
            if has_voting_details:
                print("✓ Detailed voting information available!")
                print()
                print("📊 DETAILED VOTING BREAKDOWN:")
                print("=" * 50)
                
                for result in data.get('results', []):
                    question_text = result.get('question_text', 'Unknown')
                    voting_details = result.get('voting_details', {})
                    
                    if voting_details:
                        print(f"\n🏆 {question_text}:")
                        for team_name, details in voting_details.items():
                            vote_count = details.get('total_votes', 0)
                            voters = details.get('voters', [])
                            
                            if vote_count > 0:
                                voter_teams = [v.get('voter_team', 'Unknown') for v in voters]
                                voter_teams = [t for t in voter_teams if t != 'Unknown']
                                
                                print(f"  → {team_name}: {vote_count} hlasů")
                                if voter_teams:
                                    print(f"    Hlasovali: {', '.join(voter_teams)}")
                                else:
                                    print(f"    Hlasovali: Neznámí voliči")
                print()
                return True
            else:
                print("⚠️  Detailed voting information not available")
                print("   This might mean:")
                print("   - No votes have been cast yet")
                print("   - The voting details feature needs more data")
                print("   - There might be an issue with the voter_team_id field")
                return False
                
        else:
            print(f"✗ Detailed voting API failed with status: {response.status_code}")
            if response.content:
                print(f"    Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Detailed voting API test failed: {e}")
        return False

def show_example_voting_pattern():
    """Show what the detailed voting should look like"""
    print("\n" + "=" * 60)
    print("           EXAMPLE DETAILED VOTING RESULTS")
    print("=" * 60)
    print()
    print("This is what you should see when detailed voting is working:")
    print()
    print("📊 MASKA:")
    print("  → Tym Alpha: 1 hlas")
    print("    Hlasovali: Tym Beta")
    print("  → Tym Beta: 1 hlas")  
    print("    Hlasovali: Tym Alpha")
    print()
    print("📊 KOLA:")
    print("  → Tym Gamma: 2 hlasy")
    print("    Hlasovali: Tym Alpha, Tym Beta")
    print()
    print("📊 SKELET:")
    print("  → Tym Delta: 1 hlas")
    print("    Hlasovali: Tym Alpha")
    print("  → Tym Alpha: 1 hlas")
    print("    Hlasovali: Tym Beta")
    print()
    print("This shows:")
    print("- Which team received votes (→)")
    print("- How many votes they got")
    print("- Which teams gave them those votes")
    print()

def test_database_voter_team_data():
    """Test if we have voter_team_id data in the database"""
    print("Testing database voter team data...")
    
    try:
        from server import create_app
        from models import db, Vote, Team
        
        app = create_app()
        with app.app_context():
            # Check if we have votes with voter_team_id
            votes_with_voter_team = Vote.query.filter(Vote.voter_team_id.isnot(None)).count()
            total_votes = Vote.query.count()
            
            print(f"  Total votes in database: {total_votes}")
            print(f"  Votes with voter team info: {votes_with_voter_team}")
            
            if votes_with_voter_team > 0:
                print("✓ Database has voter team information")
                
                # Show sample vote data
                sample_vote = Vote.query.filter(Vote.voter_team_id.isnot(None)).first()
                if sample_vote:
                    voted_team = Team.query.get(sample_vote.team_id)
                    voter_team = Team.query.get(sample_vote.voter_team_id)
                    
                    print(f"  Example: {voter_team.name if voter_team else 'Unknown'} → {voted_team.name if voted_team else 'Unknown'}")
                
                return True
            else:
                print("⚠️  No voter team information in database")
                print("   This means votes were cast before the voter team tracking was implemented")
                print("   Cast some new votes to see the detailed information")
                return False
                
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def run_voting_details_tests():
    """Run all voting details tests"""
    print("=" * 60)
    print("    NVIAS VOTING SYSTEM - DETAILED VOTING TEST")
    print("=" * 60)
    print()
    
    tests = [
        ("Database Voter Team Data", test_database_voter_team_data),
        ("Detailed Voting API", test_detailed_voting_info)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("              VOTING DETAILS TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Detailed voting information is working!")
        print("\nHow to see detailed voting results:")
        print("1. Admin Panel: http://localhost:5000 → Výsledky → Select voting")
        print("2. Results Page: http://localhost:5000/vysledky → Select voting")
        print("3. Look for 'Hlasovali: Team Name' under each result")
    else:
        print("❌ Detailed voting information needs attention.")
        print("\nTo fix this:")
        print("1. Cast some new votes (the old ones don't have voter team info)")
        print("2. Make sure to select a team when voting")
        print("3. Check that the voter_team_id is being saved correctly")
    
    show_example_voting_pattern()
    
    return passed == total

if __name__ == '__main__':
    print("Testing detailed voting information (which team voted for which team)...")
    print("Make sure the application is running on http://localhost:5000")
    print()
    
    # Wait for user confirmation
    input("Press Enter to continue with detailed voting testing...")
    
    success = run_voting_details_tests()
    
    sys.exit(0 if success else 1)
