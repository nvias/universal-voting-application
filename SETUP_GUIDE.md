# 🚀 Complete Setup Guide - Voting System

This guide will help you fix all issues and get the updated voting system running with the new features.

## 🔧 Step 1: Fix Database Issues

The database problems are likely due to schema changes. Let's fix this:

### Option A: Using the Fix Script (Recommended)
```bash
# Run the interactive database fix script
python fix_database.py

# Select option 1 to reset the database
# This will delete existing data but fix all schema issues
```

### Option B: Manual Reset
```bash
# If you're using Docker
docker-compose down
docker-compose up -d

# Wait for PostgreSQL to start, then:
docker-compose exec voting-app python fix_database.py
```

### Option C: Direct Database Reset
```bash
# Connect to your PostgreSQL and drop/recreate the database
psql -U your_username -h your_host
DROP DATABASE voting_db;
CREATE DATABASE voting_db;

# Then run:
python init_db.py
```

## 🎨 Step 2: Verify New UI is Working

The new modern UI should now be active. If you still see the old design:

### Clear Browser Cache
1. Press `Ctrl+F5` (or `Cmd+Shift+R` on Mac) to hard refresh
2. Or clear browser cache manually
3. Try in an incognito/private window

### Verify Files
Check that the new voting.html is in place:
```bash
# The file should contain modern CSS with Inter font and CSS variables
head -20 site/voting.html
```

You should see modern CSS with variables like `--primary-color: #2563eb;`

## 🗳️ Step 3: Test the New Features

### Create Sample Voting Sessions
```bash
python fix_database.py
# Select option 3 for regular voting
# Select option 4 for "Naše firmy" voting
```

### Test Features:
1. **Team Selection**: Go to voting URL, you should first select your team
2. **Modern UI**: Should see gradient background, modern cards, progress bars
3. **Stop Voting**: Admin interface should have stop buttons
4. **QR Codes**: Should show proper URLs from APP_URL config

## ⚙️ Step 4: Environment Configuration

### Create/Update .env file:
```bash
cp .env.example .env
```

Edit `.env`:
```env
# Database (use your actual credentials)
DATABASE_URL=postgresql://username:password@localhost:5432/voting_db

# Application URL for QR codes
APP_URL=http://localhost:5000

# Security
SECRET_KEY=your-very-secure-secret-key-here

# Environment
FLASK_ENV=development
```

### For Docker deployment:
```env
DATABASE_URL=postgresql://postgres:password@db:5432/voting_db
APP_URL=https://yourdomain.com
FLASK_ENV=docker
```

## 🐳 Step 5: Docker Setup

### Update docker-compose.yml:
The file should include `APP_URL` environment variable:
```yaml
environment:
  APP_URL: http://localhost:5000  # or your domain
```

### Start with Docker:
```bash
docker-compose up -d
docker-compose exec voting-app python fix_database.py
```

## 🧪 Step 6: Testing Checklist

### ✅ Basic Functionality
- [ ] Admin interface loads at `http://localhost:5000`
- [ ] Can create new voting sessions
- [ ] Can start/stop voting sessions
- [ ] QR codes display with correct URLs

### ✅ New UI Features
- [ ] Voting page shows modern design with gradient background
- [ ] Team selection screen appears first
- [ ] Progress bar shows completion
- [ ] Responsive design works on mobile

### ✅ "Naše firmy" Features
- [ ] Can create Naše firmy voting with 5 categories
- [ ] Teams can't vote for themselves
- [ ] Special results API returns winners by category
- [ ] Shows voting teams for each winner

### ✅ API Integration
- [ ] Health check: `GET /api/v1/health`
- [ ] Create voting: `POST /api/v1/voting`
- [ ] Special results: `GET /api/v1/voting/{id}/results/nase-firmy`

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check connection string
echo $DATABASE_URL

# Test connection
python -c "from server import create_app; app=create_app(); app.app_context().push(); from models import db; print('DB OK' if db.engine.execute('SELECT 1') else 'DB Error')"
```

### Still Seeing Old UI?
```bash
# Force browser cache clear
# Check that voting.html was updated correctly
grep -n "Inter" site/voting.html  # Should find the Inter font

# Check for file permissions
ls -la site/voting.html

# Restart the server
python server.py
```

### Import Errors
```bash
# Check all dependencies are installed
pip install -r requirements.txt

# Verify models can be imported
python -c "from models import db, VotingSession; print('Models OK')"
```

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill if needed
kill -9 <PID>

# Or use different port
python server.py --port 5001
```

## 📱 Step 7: Quick Test Scenarios

### Test 1: Basic Voting
```bash
# 1. Create sample voting
python fix_database.py  # option 3

# 2. Go to admin, start the voting
# 3. Visit voting URL, select team, vote
# 4. Check results work
```

### Test 2: Naše firmy
```bash
# 1. Create Naše firmy sample
python fix_database.py  # option 4

# 2. Start voting in admin
# 3. Test that teams can't vote for themselves
# 4. Check special results API
curl http://localhost:5000/api/v1/voting/{ID}/results/nase-firmy
```

### Test 3: API Integration
```bash
# Test creating voting via API
curl -X POST http://localhost:5000/api/v1/voting \
  -H "Content-Type: application/json" \
  -d '{"name":"API Test","questions":[{"text":"Test Q","question_type":"rating","options":["1","2","3"]}],"teams":[{"name":"Team A"}]}'
```

## 🎯 Expected Results

After following this guide, you should have:

### ✅ Modern UI
- Gradient backgrounds with Inter font
- Team selection before voting
- Progress indicators and animations
- Mobile-responsive design

### ✅ Enhanced Functionality
- Team-based voting with attribution
- Stop voting capability
- QR codes with configurable URLs
- "Naše firmy" template support

### ✅ Robust Backend
- PostgreSQL with proper schema
- RESTful API endpoints
- Flexible result aggregation
- Docker deployment ready

## 📞 Still Having Issues?

If you're still experiencing problems:

1. **Check the logs**: Look for error messages in the console
2. **Verify environment**: Ensure all environment variables are set
3. **Test step by step**: Use the fix script options individually
4. **Check file permissions**: Ensure Python can read/write all files
5. **Database access**: Verify PostgreSQL credentials and access

### Common Error Solutions:

**"No module named X"**: Run `pip install -r requirements.txt`

**"Database connection error"**: Check DATABASE_URL and PostgreSQL service

**"Old UI still showing"**: Clear browser cache, check voting.html content

**"Import error"**: Check that all Python files are in the correct location

Run `python fix_database.py` and select option 2 to check database health.

The system should now work with all the modern features you requested! 🎉
