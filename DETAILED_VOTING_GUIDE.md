# 🗳️ Detailed Voting Information - See Which Team Voted for Which Team

Yes! You can now see which team gave each vote. This is especially useful for "Naše firmy" competitions to understand voting patterns and preferences.

## 🎯 What You'll See

### **Before** (Old Results):
```
MASKA:
├── Tym Alpha: 2 hlasy
├── Tym Beta: 1 hlas
└── Tym Gamma: 0 hlasů
```

### **After** (New Detailed Results):
```
MASKA:
├── Tym Alpha: 2 hlasy
│   ← Hlasovali: Tym Beta, Tym Gamma
├── Tym Beta: 1 hlas  
│   ← Hlasovali: Tym Alpha
└── Tym Gamma: 0 hlasů
```

## 🔍 How to See Detailed Voting Results

### **Method 1: Admin Panel**
1. Go to http://localhost:5000
2. Click "Historie hlasování" in sidebar
3. Click "Výsledky" button next to any voting session
4. You'll see results like:
   ```
   Tym Alpha: 2 hlasy
   ← Hlasovali: Tym Beta, Tym Gamma
   ```

### **Method 2: Standalone Results Page**
1. Go to http://localhost:5000/vysledky
2. Select a voting session from dropdown
3. Look at the results table with "Hlasovali" column
4. Export to CSV to analyze voting patterns

### **Method 3: Direct API**
```bash
curl http://localhost:5000/api/v1/voting/655662/results
```
Returns detailed JSON with `voting_details` showing which teams voted for each team.

## 🧪 Testing the Feature

### **Quick Test:**
```bash
# Test the detailed voting functionality
python test_voting_details.py
```

### **Manual Test:**
1. **Cast votes as different teams:**
   - Open http://localhost:5000/hlasovani/655662 in regular browser
   - Select "Tym Alpha", vote for different teams in each category
   - Open same URL in incognito window
   - Select "Tym Beta", vote for different teams
   - Repeat for more teams if desired

2. **Check results:**
   - Go to results page and verify you see "Hlasovali: [team names]"

## 📊 Data Structure

The API now returns detailed voting information:

```json
{
  "results": [
    {
      "question_text": "MASKA",
      "voting_details": {
        "Tym Alpha": {
          "total_votes": 2,
          "voters": [
            {"voter_team": "Tym Beta", "option_selected": "Tym Alpha"},
            {"voter_team": "Tym Gamma", "option_selected": "Tym Alpha"}
          ]
        },
        "Tym Beta": {
          "total_votes": 1,
          "voters": [
            {"voter_team": "Tym Alpha", "option_selected": "Tym Beta"}
          ]
        }
      }
    }
  ]
}
```

## 💡 Use Cases

### **1. Voting Pattern Analysis**
- See which teams tend to vote for each other
- Identify voting alliances or preferences
- Understand competition dynamics

### **2. Fairness Verification**
- Ensure teams are voting fairly
- Check for potential bias or strategic voting
- Verify voting distribution

### **3. Team Insights**
- Understand how teams perceive each other
- See which teams are most popular
- Analyze voting behavior patterns

## 🎨 Visual Examples

### **Admin Panel Display:**
```
🏆 MASKA:
  → Tym Alpha: 2 hlasy
    Hlasovali: Tym Beta, Tym Gamma
  → Tym Beta: 1 hlas
    Hlasovali: Tym Alpha

🏆 KOLA:
  → Tym Gamma: 3 hlasy
    Hlasovali: Tym Alpha, Tym Beta, Tym Delta
```

### **Results Table:**
| Otázka | Tým | Hlasů | Hlasovali |
|--------|-----|-------|-----------|
| MASKA | Tym Alpha | 2 | Tym Beta, Tym Gamma |
| MASKA | Tym Beta | 1 | Tym Alpha |
| KOLA | Tym Gamma | 3 | Tym Alpha, Tym Beta, Tym Delta |

## 🚨 Important Notes

### **For Existing Votes:**
- Votes cast **before** this update won't show voter team information
- You'll see "Neznámí voliči" (Unknown voters) for old votes
- Cast new votes to see the detailed information

### **For New Votes:**
- All new votes automatically track which team cast them
- Detailed information appears immediately in results
- Works for all question types (rating, team_selection, multiple_choice)

## 🔧 Troubleshooting

### **Issue: "Neznámí voliči" shown**
**Cause:** Votes were cast before detailed tracking was implemented
**Solution:** Cast some new votes to see the feature working

### **Issue: No detailed information shown**
**Cause:** Database might not have voter_team_id data
**Solution:** 
```bash
# Check database
python test_voting_details.py

# If needed, cast new votes
```

### **Issue: Results not updating**
**Cause:** Cache or API issues
**Solution:**
- Refresh the page
- Clear browser cache
- Restart the application

## 📈 Export Features

### **CSV Export with Voter Info:**
```csv
Otazka,Tym,Pocet_hlasu,Hlasovali
MASKA,Tym Alpha,2,"Tym Beta;Tym Gamma"
MASKA,Tym Beta,1,"Tym Alpha"
KOLA,Tym Gamma,3,"Tym Alpha;Tym Beta;Tym Delta"
```

### **JSON Export:**
Complete voting details in JSON format for advanced analysis.

## 🎯 Next Steps

1. **Test the feature** with your existing votes
2. **Cast new votes** if you don't see detailed information
3. **Analyze voting patterns** to gain insights
4. **Export data** for further analysis
5. **Share results** with participants

## 🚀 Advanced Usage

### **Custom Analysis:**
```javascript
// Fetch detailed voting data
fetch('/api/v1/voting/655662/results')
  .then(response => response.json())
  .then(data => {
    // Analyze voting patterns
    data.results.forEach(question => {
      const details = question.voting_details;
      // Your custom analysis here
    });
  });
```

### **Voting Pattern Detection:**
- Which teams vote for each other most often?
- Are there consistent voting alliances?
- Which teams receive the most cross-votes?

The detailed voting information is now fully functional! You can see exactly which team voted for which team in every category. This gives you complete transparency and insights into the voting process. 🎉

**Ready to explore the voting patterns? Cast some votes and check the results!**
