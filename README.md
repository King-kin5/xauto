# XAuto: Advanced X (Twitter) Automation Bot

> **⚠️ Disclaimer:**
> This tool is for responsible, moderate use only. Excessive or aggressive automation may result in your X (Twitter) account being restricted or banned. Always comply with X's terms of service and use the bot in a way that does not spam, harass, or violate platform rules. Monitor your account regularly and use at your own risk.

## Overview
XAuto is a sophisticated X (Twitter) automation bot that provides intelligent support for the Anoma project. It combines automated replies to mentions with AI-powered content generation for maximum engagement and community building.

## 🚀 Key Features

> **Customizable Target**: You can change the bot to support any X (Twitter) account or keyword, not just Anoma. Simply update the `TARGET_ACCOUNT` and `SEARCH_QUERY` settings in the configuration (see below) to use the bot for any project or topic you like.

### Core Automation
- **Smart Reply System**: Automatically replies to @anoma mentions with engaging, human-like responses
- **AI-Powered Content Generation**: Uses Google Gemini AI to create creative, authentic hype tweets
- **Intelligent Batching**: Processes tweets in optimized batches with natural delays
- **Duplicate Prevention**: Tracks replied tweets to avoid spam and maintain quality

### Advanced Capabilities
- **Stealth Browser Automation**: Uses undetected-chromedriver for anti-detection
- **Human-like Behavior**: Random delays, mouse movements, and typing patterns
- **Rate Limiting**: Configurable daily limits and safety delays
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Statistics Tracking**: Daily stats for replies sent, tweets processed, and errors

### Content Strategy
- **Dual Content Approach**: 
  - Replies to community mentions (engagement)
  - AI-generated hype tweets (content creation)
- **Creative AI Prompts**: Generates authentic, exciting content about Anoma
- **Template Variety**: 30+ pre-written reply templates for diverse responses

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Chrome browser
- X (Twitter) account
- Google Gemini API key (optional, for AI content generation)

### 1. Clone & Install
```bash
git clone <repository-url>
cd xauto
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file with your credentials:
```env
# X Account Credentials
X_USERNAME=your_username_here
X_PASSWORD=your_password_here
X_EMAIL_OR_PHONE=your_email_or_phone_here

# AI Configuration (Optional)
GEMINI_API_KEY=your_gemini_api_key_here

# Bot Configuration
TARGET_ACCOUNT=anoma           # Change this to any account you want to support
SEARCH_QUERY=@anoma -from:anoma # Change this to any search query you want
MAX_CYCLES_PER_RUN=10  # Set to None for infinite
```

### 3. Run the Bot
```bash
python main.py
```

## ⚙️ Configuration Options

### Rate Limiting
- `MAX_REPLIES_PER_DAY`: Daily reply limit (default: 50)
- `MIN_DELAY_BETWEEN_REPLIES`: Minimum delay between replies (default: 60s)
- `MAX_DELAY_BETWEEN_REPLIES`: Maximum delay between replies (default: 150s)

### Search & Content
- `TARGET_ACCOUNT`: Target account to support (default: "anoma")
- `SEARCH_QUERY`: Search query for mentions (default: "@anoma -from:anoma")
- `SEARCH_REFRESH_INTERVAL`: How often to refresh search (default: 100s)

### Browser Settings
- `HEADLESS`: Run browser in headless mode (default: False for debugging)
- Multiple user agents for rotation and stealth

## 🔄 How It Works

### 1. Content Generation Cycle
The bot runs in cycles, each consisting of:
- **Hype Tweet Phase**: Posts 3 AI-generated creative tweets about the target account or topic (default: Anoma)
- **Reply Phase**: Processes up to 20 mentions in batches of 5
- **Cooldown**: Natural delays between cycles for human-like behavior

### 2. AI Content Generation
- Uses Google Gemini 1.5 Flash for creative tweet generation
- Generates authentic, exciting content about the configured target account or topic
- Ensures the target account (e.g., @anoma) is mentioned but not at the start of tweets
- Creates content that feels like genuine community excitement

### 3. Smart Reply System
- Searches for mentions of the configured target account (default: @anoma, but customizable)
- Filters for original tweets (not replies)
- Avoids duplicate replies using tweet ID tracking
- Uses 30+ pre-written templates for variety (customizable)

### 4. Anti-Detection Features
- Undetected Chrome driver
- Random user agent rotation
- Human-like mouse movements and typing
- Natural delays and scrolling
- Window size and position randomization

## 📊 Data & Tracking

### Files Generated
- `data/replied_tweets.json`: Tracks replied tweet IDs
- `data/daily_stats.json`: Daily statistics and metrics
- `data/bot.log`: Comprehensive logging

### Statistics Tracked
- Replies sent per day
- Tweets processed
- Posts made (AI-generated content)
- Errors encountered
- User agent information

## 🎯 Content Strategy

### Reply Templates
30+ engaging templates including:
- "Absolutely loving what Anoma is building! 💖✨"
- "This is so inspiring! Go Anoma! 🌸🙌"
- "Anoma is absolutely crushing it! 🔥💪"
- And many more...

### AI-Generated Content
Creative, authentic tweets that:
- Use casual, energetic language
- Feel like insider knowledge
- Include natural emojis and hashtags
- Reference building, innovation, community, future
- Maintain excitement and authenticity

## 🔒 Safety & Best Practices

### Rate Limiting
- Configurable daily limits
- Natural delays between actions
- Batch processing to avoid overwhelming

### Anti-Detection
- Stealth browser automation
- Human-like behavior patterns
- User agent rotation
- Window randomization

### Error Handling
- Comprehensive exception handling
- Graceful failure recovery
- Detailed logging for debugging

## 📁 Project Structure
```
xauto/
├── main.py               # Main bot logic and entry point
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .env                 # Environment variables (create this)
└── data/                # Generated data files
    ├── replied_tweets.json
    ├── daily_stats.json
    └── bot.log
```

## 🚨 Important Notes

### Security
- Never share your `.env` file or credentials
- Keep your API keys secure
- Use environment variables for all sensitive data

### Responsible Use
- Respect X (Twitter) terms of service
- Use reasonable rate limits
- Monitor bot behavior regularly
- Don't spam or engage in harmful automation

### Monitoring
- Check logs regularly for errors
- Monitor daily statistics
- Adjust rate limits if needed
- Verify bot behavior is natural

## 🔧 Troubleshooting

### Common Issues
1. **Login Failures**: Check credentials and 2FA settings
2. **Chrome Driver Issues**: Ensure Chrome is up to date
3. **Rate Limiting**: Adjust delays if hitting limits
4. **AI Generation Failures**: Verify Gemini API key is set

### Debug Mode
Set `HEADLESS=False` in the config to see browser actions in real-time.

## 📈 Future Enhancements

Potential improvements:
- Multi-account support
- Advanced content scheduling
- Sentiment analysis for replies
- Integration with other social platforms
- Advanced analytics dashboard

---

**Disclaimer**: This tool is for educational and legitimate community support purposes. Use responsibly and in accordance with platform terms of service. 