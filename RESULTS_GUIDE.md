# NVIAS Voting System - Results Functionality Guide

The results functionality has been fixed and enhanced. Here's how to test and use it.

## What Was Fixed

### 1. **Results API Endpoint**
- Added `/api/v1/voting/<voting_id>/results` endpoint
- Returns proper data format for frontend consumption
- Handles different question types (rating, team_selection, multiple_choice)
- Includes total voters and detailed statistics

### 2. **Enhanced Admin Results**
- Improved `displayResults` function with better formatting
- Added visual progress bars for vote counts
- Better error handling and loading states
- Enhanced styling for results display

### 3. **Standalone Results Page**
- Fixed `/vysledky` route (http://localhost:5000/vysledky)
- Enhanced results.html with charts and tables
- Added export functionality (CSV/JSON)
- Better responsive design

## How to Test Results

### Method 1: Quick Test Script
```bash
# Test all results functionality
python test_results.py
```

### Method 2: Manual Testing

#### Step 1: Ensure you have votes in the system
```bash
# Start the application
python startup.py

# Vote as multiple teams using different browsers/incognito windows
# Visit: http://localhost:5000/hlasovani/655662
```

#### Step 2: Test Admin Panel Results
1. Go to http://localhost:5000
2. Click "Výsledky" in the sidebar
3. It should show: "Vyberte hlasování z historie pro zobrazení výsledků"
4. Go back to "Historie hlasování"
5. Click "Výsledky" button next to "Nase firmy 2025"
6. Should display detailed results with charts and vote counts

#### Step 3: Test Standalone Results Page
1. Go to http://localhost:5000/vysledky
2. Select "Nase firmy 2025" from the dropdown
3. Should display:
   - Statistics cards (voters, votes, questions, participation)
   - Charts for each question/category
   - Detailed results table
   - Export buttons

#### Step 4: Test API Directly
```bash
# Test the API endpoint directly
curl http://localhost:5000/api/v1/voting/655662/results
```

## Results Display Features

### 1. **Statistics Overview**
- Total voters count
- Total votes cast
- Number of questions
- Participation rate

### 2. **Question Results**
For each question (MASKA, KOLA, SKELET, PLAKAT, MARKETING):
- Visual progress bars showing relative vote counts
- Team names with vote counts
- Color-coded display (teams with votes highlighted)

### 3. **Charts and Visualizations**
- Interactive charts for each category
- Different chart types based on question type
- Responsive design for mobile devices

### 4. **Export Functionality**
- Export to CSV format
- Export to JSON format
- Includes all voting data and statistics

## Data Format

The results API returns data in this format:
```json
{
  "session_id": "655662",
  "session_name": "Nase firmy 2025",
  "total_voters": 2,
  "results": [
    {
      "question_id": 1,
      "question_text": "MASKA",
      "question_type": "team_selection",
      "teams": {
        "Tym Alpha": {
          "vote_count": 1,
          "average_rating": 0,
          "option_counts": {"Tym Alpha": 1}
        },
        "Tym Beta": {
          "vote_count": 1,
          "average_rating": 0,
          "option_counts": {"Tym Beta": 1}
        }
      }
    }
  ]
}
```

## Troubleshooting

### Issue: "No results found"
**Solution**: Make sure votes have been cast in the system
```bash
# Check if votes exist in database
python test_db.py
```

### Issue: "API endpoint not found"
**Solution**: Ensure the server is running and endpoints are registered
```bash
# Test API health
curl http://localhost:5000/api/v1/health
```

### Issue: "Charts not displaying"
**Solution**: Make sure Chart.js is loaded properly
- Check browser console for JavaScript errors
- Verify internet connection for CDN resources

### Issue: "Results show 0 votes but voting worked"
**Solution**: Check database connection and vote counting logic
```bash
# Test vote counting
python test_results.py
```

## Advanced Usage

### 1. **Creating Custom Reports**
You can access the raw data via API and create custom reports:
```javascript
fetch('/api/v1/voting/655662/results')
  .then(response => response.json())
  .then(data => {
    // Process data for custom reports
    console.log(data);
  });
```

### 2. **Exporting Data**
Multiple export formats available:
- **CSV**: For spreadsheet analysis
- **JSON**: For programmatic processing
- **API**: For real-time integration

### 3. **Real-time Updates**
The results can be refreshed in real-time:
```javascript
// Auto-refresh every 10 seconds
setInterval(() => {
  loadResults();
}, 10000);
```

## URL References

| Page | URL | Description |
|------|-----|-------------|
| Admin Results | http://localhost:5000 → Výsledky | Results in admin panel |
| Standalone Results | http://localhost:5000/vysledky | Dedicated results page |
| Results API | http://localhost:5000/api/v1/voting/655662/results | Raw JSON data |
| Voting List API | http://localhost:5000/get_votings | List of all voting sessions |

## Next Steps

1. **Test the functionality** using the methods above
2. **Cast some votes** if you haven't already
3. **Check both admin and standalone results** pages
4. **Verify the data** matches what was voted
5. **Try the export features** to download results

## Expected Results for "Nase firmy 2025"

After voting as 2 teams, you should see:
- ✅ 2 voters total
- ✅ 10 votes total (5 categories × 2 teams)
- ✅ 5 questions (MASKA, KOLA, SKELET, PLAKAT, MARKETING)
- ✅ Vote counts for each team in each category
- ✅ Visual progress bars showing vote distribution
- ✅ Export functionality working

The results functionality is now fully operational! 🎉
