#!/usr/bin/env python3
"""
Script to create a "Naše firmy" voting session with predefined categories
"""

import requests
import json
import sys

def create_nase_firmy_voting(app_url, session_name, teams):
    """
    Create a "Naše firmy" voting session
    
    Args:
        app_url (str): Base URL of the voting application
        session_name (str): Name for the voting session
        teams (list): List of team names
    """
    
    # Predefined categories for "Naše firmy"
    categories = ["MASKA", "KOLA", "SKELET", "PLAKÁT", "MARKETING"]
    
    # Create questions for each category
    questions = []
    for category in categories:
        questions.append({
            "text": category,
            "question_type": "team_selection",
            "options": [],  # Teams will be the options
            "template_id": None  # Will use "Naše firmy" template
        })
    
    # Create teams data
    teams_data = []
    for team_name in teams:
        teams_data.append({
            "name": team_name,
            "external_id": team_name.lower().replace(" ", "_"),
            "description": f"Tým {team_name}"
        })
    
    # Payload for creating voting session
    payload = {
        "name": session_name,
        "description": "Soutěž Naše firmy - hlasování v kategoriích MASKA, KOLA, SKELET, PLAKÁT, MARKETING",
        "questions": questions,
        "teams": teams_data
    }
    
    try:
        # Create voting session
        response = requests.post(
            f"{app_url}/api/v1/voting",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 201:
            result = response.json()
            voting_id = result['id']
            print(f"✅ Hlasování '{session_name}' bylo úspěšně vytvořeno!")
            print(f"🆔 ID hlasování: {voting_id}")
            print(f"🗳️  URL pro hlasování: {app_url}/hlasovani/{voting_id}")
            print(f"📱 QR kód: {app_url}/presentation/{voting_id}")
            print("\n📋 Kategorie:")
            for category in categories:
                print(f"   • {category}")
            print(f"\n👥 Týmy ({len(teams)}):")
            for team in teams:
                print(f"   • {team}")
            
            return voting_id
        else:
            print(f"❌ Chyba při vytváření hlasování: {response.status_code}")
            print(f"   {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Chyba při připojení: {e}")
        return None

def main():
    """Main function"""
    print("🏆 Vytváření hlasování 'Naše firmy'\n")
    
    # Configuration
    app_url = input("URL aplikace (např. http://localhost:5000): ").strip()
    if not app_url:
        app_url = "http://localhost:5000"
    
    session_name = input("Název hlasování (např. 'Naše firmy 2025'): ").strip()
    if not session_name:
        session_name = "Naše firmy"
    
    print("\n👥 Zadejte názvy týmů (prázdný řádek pro ukončení):")
    teams = []
    while True:
        team = input(f"Tým {len(teams) + 1}: ").strip()
        if not team:
            break
        teams.append(team)
    
    if not teams:
        print("❌ Musíte zadat alespoň jeden tým!")
        return
    
    if len(teams) < 2:
        print("⚠️  Doporučujeme alespoň 2 týmy pro smysluplné hlasování.")
    
    print(f"\n📝 Souhrn:")
    print(f"   Název: {session_name}")
    print(f"   Týmů: {len(teams)}")
    print(f"   Kategorií: 5 (MASKA, KOLA, SKELET, PLAKÁT, MARKETING)")
    
    confirm = input("\nPokračovat? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes', 'ano', 'a']:
        print("Zrušeno.")
        return
    
    # Create voting session
    voting_id = create_nase_firmy_voting(app_url, session_name, teams)
    
    if voting_id:
        print(f"\n🎉 Hlasování je připraveno!")
        print(f"\n📋 Další kroky:")
        print(f"   1. Otevřete administraci: {app_url}")
        print(f"   2. Spusťte hlasování v historii")
        print(f"   3. Zobrazte QR kód: {app_url}/presentation/{voting_id}")
        print(f"   4. Účastníci mohou hlasovat: {app_url}/hlasovani/{voting_id}")
        print(f"\n💡 Tip: Každý tým vybere jeden tým v každé kategorii (nemohou hlasovat sami pro sebe)")

if __name__ == "__main__":
    main()
