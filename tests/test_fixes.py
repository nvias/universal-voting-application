#!/usr/bin/env python3
"""
Test script to verify all fixes are working correctly
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5000"

def test_api_endpoint(url, method='GET', data=None):
    """Test an API endpoint"""
    full_url = f"{BASE_URL}{url}"
    try:
        if method == 'GET':
            response = requests.get(full_url, timeout=10)
        elif method == 'POST':
            response = requests.post(full_url, json=data, timeout=10)
        
        return response.status_code, response.json() if response.content else {}
    except Exception as e:
        return None, str(e)

def test_database_endpoints():
    """Test database-related endpoints"""
    print("Testing database endpoints...")
    
    # Test health check
    status, data = test_api_endpoint("/api/v1/health")
    if status == 200:
        print("✓ Health check endpoint working")
    else:
        print(f"✗ Health check failed: {status}")
        return False
    
    # Test voting sessions list
    status, data = test_api_endpoint("/get_votings")
    if status == 200:
        print(f"✓ Voting sessions endpoint working ({len(data)} sessions found)")
    else:
        print(f"✗ Voting sessions endpoint failed: {status}")
        return False
    
    return True

def test_nase_firmy_session():
    """Test the Nase firmy 2025 session specifically"""
    print("Testing Nase firmy 2025 session...")
    
    # Test session data
    status, data = test_api_endpoint("/api/voting-data/655662")
    if status == 200:
        session = data.get('session', {})
        questions = data.get('questions', [])
        teams = data.get('teams', [])
        
        print(f"✓ Session data loaded: {session.get('name')}")
        print(f"  - Teams: {len(teams)}")
        print(f"  - Questions: {len(questions)}")
        
        # Check if it's properly configured as Nase firmy
        team_selection_questions = [q for q in questions if q.get('question_type') == 'team_selection']
        if team_selection_questions:
            print(f"✓ Naše firmy template detected ({len(team_selection_questions)} team selection questions)")
        else:
            print("! Warning: Naše firmy template not properly detected")
        
        return True
    else:
        print(f"✗ Session data loading failed: {status}")
        return False

def test_statistics_endpoint():
    """Test the statistics endpoint"""
    print("Testing statistics endpoint...")
    
    status, data = test_api_endpoint("/api/v1/voting-stats/655662")
    if status == 200:
        print("✓ Statistics endpoint working")
        print(f"  - Teams: {data.get('team_count', 0)}")
        print(f"  - Questions: {data.get('question_count', 0)}")
        print(f"  - Votes: {data.get('vote_count', 0)}")
        print(f"  - Voters: {data.get('voter_count', 0)}")
        return True
    else:
        print(f"✗ Statistics endpoint failed: {status}")
        return False

def test_vote_submission():
    """Test vote submission functionality"""
    print("Testing vote submission...")
    
    # First get session data to construct proper vote
    status, session_data = test_api_endpoint("/api/voting-data/655662")
    if status != 200:
        print("✗ Cannot get session data for vote test")
        return False
    
    questions = session_data.get('questions', [])
    teams = session_data.get('teams', [])
    
    if not questions or not teams:
        print("✗ No questions or teams found for vote test")
        return False
    
    # Create a test vote
    test_votes = []
    for i, question in enumerate(questions[:2]):  # Test first 2 questions only
        if i < len(teams):
            test_votes.append({
                "question_id": question['id'],
                "team_id": teams[i]['id'],
                "voter_team_id": teams[0]['id'],  # Voting as first team
                "option_selected": teams[i]['name'],
                "numeric_value": None
            })
    
    vote_data = {"votes": test_votes}
    
    # Submit vote
    status, response = test_api_endpoint("/api/submit-vote/655662", method='POST', data=vote_data)
    if status == 201:
        print(f"✓ Vote submission successful ({response.get('votes_submitted', 0)} votes)")
        return True
    else:
        print(f"✗ Vote submission failed: {status} - {response}")
        return False

def test_webpage_accessibility():
    """Test that key web pages are accessible"""
    print("Testing webpage accessibility...")
    
    pages = [
        "/",
        "/hlasovani/655662",
        "/presentation/655662"
    ]
    
    all_accessible = True
    for page in pages:
        try:
            response = requests.get(f"{BASE_URL}{page}", timeout=10)
            if response.status_code == 200:
                print(f"✓ Page {page} accessible")
            else:
                print(f"✗ Page {page} returned status {response.status_code}")
                all_accessible = False
        except Exception as e:
            print(f"✗ Page {page} failed: {e}")
            all_accessible = False
    
    return all_accessible

def run_comprehensive_test():
    """Run comprehensive test of all fixes"""
    print("=" * 60)
    print("       NVIAS VOTING SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    print()
    
    print("Testing all fixes and functionality...\n")
    
    tests = [
        ("Database Endpoints", test_database_endpoints),
        ("Nase Firmy Session", test_nase_firmy_session),
        ("Statistics Endpoint", test_statistics_endpoint),
        ("Vote Submission", test_vote_submission),
        ("Webpage Accessibility", test_webpage_accessibility)
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
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("                    TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The voting system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == '__main__':
    print("Starting comprehensive test...")
    print("Make sure the application is running on http://localhost:5000")
    print()
    
    # Wait for user confirmation
    input("Press Enter to continue with testing...")
    
    success = run_comprehensive_test()
    
    if success:
        print("\n✅ All fixes verified successfully!")
        print("The voting system is ready for use.")
    else:
        print("\n❌ Some issues remain. Please check the test output above.")
    
    sys.exit(0 if success else 1)
