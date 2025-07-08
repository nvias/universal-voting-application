#!/usr/bin/env python3
"""
Test script specifically for results functionality
"""

import os
import sys
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5000"

def test_results_api():
    """Test the results API endpoint"""
    print("Testing results API endpoint...")
    
    # Test with the sample session
    voting_id = "655662"
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/voting/{voting_id}/results", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Results API endpoint working")
            print(f"  Session: {data.get('session_name', 'Unknown')}")
            print(f"  Total Voters: {data.get('total_voters', 0)}")
            print(f"  Questions: {len(data.get('results', []))}")
            
            # Show sample results
            for result in data.get('results', [])[:2]:  # Show first 2 questions
                print(f"  Question: {result.get('question_text', 'Unknown')}")
                print(f"    Type: {result.get('question_type', 'Unknown')}")
                for team_name, team_data in result.get('teams', {}).items():
                    vote_count = team_data.get('vote_count', 0)
                    if vote_count > 0:
                        print(f"    {team_name}: {vote_count} votes")
            
            return True
        else:
            print(f"✗ Results API failed with status: {response.status_code}")
            if response.content:
                print(f"    Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Results API test failed: {e}")
        return False

def test_voting_list_api():
    """Test the voting list endpoint used by results page"""
    print("Testing voting list API...")
    
    try:
        response = requests.get(f"{BASE_URL}/get_votings", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Voting list API working ({len(data)} sessions found)")
            
            # Show session info
            for session_id, session_data in list(data.items())[:3]:  # Show first 3 sessions
                print(f"  {session_id}: {session_data.get('name', 'Unknown')}")
                teams = session_data.get('teams', [])
                team_names = []
                for team in teams:
                    if isinstance(team, dict):
                        team_names.extend(team.keys())
                print(f"    Teams: {', '.join(team_names[:4])}")  # Show first 4 teams
            
            return True
        else:
            print(f"✗ Voting list API failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Voting list API test failed: {e}")
        return False

def test_results_page():
    """Test that the results page loads"""
    print("Testing results page accessibility...")
    
    try:
        response = requests.get(f"{BASE_URL}/vysledky", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            if "Výsledky hlasování" in content and "voting-select" in content:
                print("✓ Results page loads correctly")
                return True
            else:
                print("✗ Results page content seems incomplete")
                return False
        else:
            print(f"✗ Results page failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Results page test failed: {e}")
        return False

def test_admin_results():
    """Test admin results functionality"""
    print("Testing admin results section...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            if "results-section" in content and "displayResults" in content:
                print("✓ Admin results section present")
                return True
            else:
                print("✗ Admin results section missing or incomplete")
                return False
        else:
            print(f"✗ Admin page failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Admin results test failed: {e}")
        return False

def run_results_tests():
    """Run all results-related tests"""
    print("=" * 60)
    print("       NVIAS VOTING SYSTEM - RESULTS TESTING")
    print("=" * 60)
    print()
    
    tests = [
        ("Results API Endpoint", test_results_api),
        ("Voting List API", test_voting_list_api),
        ("Results Page", test_results_page),
        ("Admin Results", test_admin_results)
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
    print("                 RESULTS TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All results tests passed! Results functionality is working.")
        print("\nHow to access results:")
        print("1. Admin Panel: http://localhost:5000 → Click 'Výsledky' → Select voting session")
        print("2. Results Page: http://localhost:5000/vysledky → Select voting session")
        print("3. API Direct: http://localhost:5000/api/v1/voting/655662/results")
        return True
    else:
        print("❌ Some results tests failed. Please check the issues above.")
        return False

if __name__ == '__main__':
    print("Testing results functionality...")
    print("Make sure the application is running on http://localhost:5000")
    print("And that you have some votes cast in the system.")
    print()
    
    # Wait for user confirmation
    input("Press Enter to continue with results testing...")
    
    success = run_results_tests()
    
    sys.exit(0 if success else 1)
