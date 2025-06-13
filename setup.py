#!/usr/bin/env python3
"""
Setup script for the voting application
This script will:
1. Initialize the database
2. Create sample data
3. Test the system
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} successful")
            if result.stdout.strip():
                print(result.stdout.strip())
        else:
            print(f"✗ {description} failed")
            if result.stderr.strip():
                print("Error:", result.stderr.strip())
            return False
        return True
    except Exception as e:
        print(f"✗ {description} failed with exception: {e}")
        return False

def main():
    print("=== NVIAS Voting System Setup ===")
    print("This script will initialize the database and create sample data.")
    
    # Check if we're in the correct directory
    if not os.path.exists('server.py'):
        print("Error: Please run this script from the project root directory.")
        sys.exit(1)
    
    # Initialize database
    if not run_command("python init_db.py", "Initializing database"):
        print("Database initialization failed. Please check your database configuration.")
        sys.exit(1)
    
    # Create sample data
    response = input("\nCreate sample 'Nase firmy 2025' session? (y/N): ")
    if response.lower() in ['y', 'yes']:
        if not run_command("python init_db.py --sample", "Creating sample data"):
            print("Sample data creation failed.")
            sys.exit(1)
    
    # Test database connection
    if not run_command("python test_db.py", "Testing database connection"):
        print("Database test failed.")
        sys.exit(1)
    
    print("\n=== Setup Complete ===")
    print("Your voting system is now ready!")
    print("\nTo start the application:")
    print("  python server.py")
    print("\nOr with Docker:")
    print("  docker-compose up -d")
    print("\nAdmin interface: http://localhost:5000")
    
    # Show sample session info if created
    if response.lower() in ['y', 'yes']:
        print("\nSample 'Nase firmy 2025' session:")
        print("  Voting URL: http://localhost:5000/hlasovani/655662")
        print("  QR Code: http://localhost:5000/presentation/655662")

if __name__ == '__main__':
    main()
