# EduGuideBot - Educational Guidance Tool for Cambodian Students

## Project Overview

EduGuideBot is a Telegram bot that helps Cambodian students find suitable university recommendations based on their preferences, career goals, and academic profile. The bot provides personalized recommendations, allows exploration of university information, and offers insights into different career paths.

## Features

- **Student DNA Analysis**: Personalized university recommendations based on student preferences
- **University Catalog Browser**: Explore universities, their faculties, and majors
- **Education Cost Calculator**: Calculate estimated costs of studying at different universities
- **Career Path Explorer**: Learn about career opportunities in different fields
- **ML-powered Admission Predictor**: Predict admission chances based on student profile

## Project Structure

```
EduGuideBot_FINAL/
├── app.py                     # Main bot application entry point
├── data/                      # Data files
│   ├── data.json              # University dataset
│   └── synthetic_admissions_data.csv  # ML training data
├── models/                    # Machine learning models
├── scripts/                   # Utility scripts
│   ├── build_web_apps.py      # Builds web applications with data injection
│   ├── generate_synthetic_data.py  # Generates synthetic data for ML
│   └── train_admission_model.py    # Trains the admission prediction model
├── src/                       # Source code
│   ├── bot/                   # Telegram bot implementation
│   ├── core/                  # Core recommendation logic
│   │   ├── data_loader.py     # University data loading
│   │   ├── ml_models/         # ML model files
│   │   └── recommender.py     # Recommendation engine
│   └── web/                   # Web interfaces
└── static/                    # Web assets and templates
    ├── browser/               # University catalog web app
    ├── calculator/            # Cost calculator web app
    ├── quiz/                  # Student DNA quiz web app
    ├── css/                   # Shared CSS files
    ├── js/                    # Shared JavaScript files
    └── templates/             # HTML templates
```

## Technology Stack

- **Backend**: Python with python-telegram-bot
- **Frontend**: HTML, CSS, JavaScript, Telegram Web Apps API
- **Data Storage**: JSON, CSV
- **Machine Learning**: scikit-learn

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get from @BotFather)
- A GitHub Pages site for hosting web apps (optional)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.template` to `.env` and configure:
   ```
   cp .env.template .env
   ```
4. Configure your Telegram bot token and GitHub Pages URL in `.env`

### Running the Bot

```
python app.py
```

### Preparing Data and Models

1. Generate synthetic data:
   ```
   python scripts/generate_synthetic_data.py
   ```
2. Train the ML model:
   ```
   python scripts/train_admission_model.py
   ```
3. Build the web apps:
   ```
   python scripts/build_web_apps.py
   ```

## Web Applications

The project includes three web applications that are integrated with the Telegram bot:

1. **Student DNA Quiz**: Collects student preferences and generates recommendations
2. **University Catalog**: Allows browsing and exploration of universities
3. **Cost Calculator**: Helps estimate education costs

## License

This project is created for educational purposes.

## Acknowledgments

- Telegram for their Bot API and Web App platform
- Educational institutions of Cambodia for inspiration 