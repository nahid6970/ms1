# Bengali Synonyms MCQ Quiz Application - Project Overview

## 📋 Project Summary

This is a **dynamic MCQ (Multiple Choice Question) test application** built with Flask that generates random quizzes based on Bengali synonym words. The application intelligently creates questions by selecting words from synonym groups and generates contextually appropriate answer options.

## 🎯 Core Concept

The application uses a **smart question generation algorithm**:
1. **Question Word**: Randomly selected from a synonym group
2. **Correct Answer**: Another word from the same synonym group
3. **Wrong Options**: 3 random words from different synonym groups
4. **Dynamic Generation**: Each quiz session creates completely new questions

## 🏗️ Architecture

### Backend (Flask - Python)
- **File**: `app.py`
- **Port**: 4421
- **Main Functions**:
  - `generate_quiz(num_questions)`: Creates random quiz questions
  - `/api/generate-quiz`: API endpoint for quiz generation
  - `/api/check-answer`: API endpoint for answer validation

### Frontend (HTML/CSS/JavaScript)
- **File**: `templates/index.html`
- **Features**:
  - Responsive design (mobile + desktop)
  - Real-time scoring
  - Question counter
  - Color-coded feedback (green=correct, red=wrong)
  - Customizable quiz length (5-50 questions)

### Data Structure
- **File**: `questions.json`
- **Format**: Synonym groups with related words
- **Total Groups**: 39 categories
- **Total Words**: 200+ Bengali synonym words

## 📊 Data Organization

The `questions.json` contains synonym groups like:
```json
{
  "synonym_groups": [
    {
      "group": "পানি",
      "words": ["পানি", "জল", "অম্বু", "অপ", "নীর", "সলিল", "বারি", "উদক"]
    },
    {
      "group": "চাঁদ", 
      "words": ["চাঁদ", "চন্দ্র", "ইন্দু", "সুধাংসু", "বিধু", "নিশাকর"]
    }
  ]
}
```

## 🔄 Quiz Generation Logic

```python
def generate_quiz(num_questions):
    for each question:
        1. Select random synonym group
        2. Pick random word from group (question word)
        3. Pick different word from same group (correct answer)
        4. Select 3 random words from other groups (wrong options)
        5. Shuffle all options
        6. Return question with shuffled options
```

## 🎮 User Flow

1. **Setup**: User selects number of questions (5-50)
2. **Loading**: App generates random quiz questions
3. **Quiz**: User answers questions one by one
4. **Feedback**: Immediate visual feedback (correct/wrong)
5. **Results**: Final score with percentage
6. **Restart**: Option to take new quiz

## 📁 File Structure

```
├── app.py                 # Flask backend application
├── questions.json         # Synonym groups data
├── templates/
│   └── index.html        # Frontend UI
├── requirements.txt      # Python dependencies
├── README.md            # User documentation
└── PROJECT_OVERVIEW.md  # This technical overview
```

## 🛠️ Technical Features

### Smart Question Generation
- **Contextual Answers**: Correct answer always from same semantic group
- **Realistic Distractors**: Wrong options from different groups to avoid obvious answers
- **No Repetition**: Each quiz session generates unique questions

### Responsive Design
- **Mobile-First**: Works on all screen sizes
- **Modern UI**: Gradient backgrounds, smooth animations
- **Bengali Typography**: Proper font support for Bengali text

### Real-time Interaction
- **Instant Feedback**: Color changes on answer selection
- **Progress Tracking**: Question counter and live scoring
- **Smooth Transitions**: Loading states and animations

## 🔧 Configuration Options

### Quiz Customization
- **Question Count**: 5-50 questions per quiz
- **Port Configuration**: Currently set to 4421
- **Debug Mode**: Enabled for development

### Data Expansion
To add new synonym groups:
```json
{
  "group": "new_category_name",
  "words": ["word1", "word2", "word3", "word4"]
}
```

## 🚀 Deployment

### Local Development
```bash
python app.py
# Access: http://localhost:4421
```

### Production Considerations
- Change `debug=False` in app.py
- Use production WSGI server (gunicorn, uwsgi)
- Add proper error handling
- Implement session management for multiple users

## 📚 Educational Context

Based on **"বাংলা সমার্থক শব্দ: চূড়ান্ত স্টাডি নোট"** covering:
- Confusing/similar words
- Water & nature related terms
- Sky & celestial objects
- Earth & land features
- Flora & fauna
- Human & family relations
- Miscellaneous important synonyms

## 🎯 Key Benefits

1. **Dynamic Content**: Never the same quiz twice
2. **Educational Value**: Reinforces Bengali synonym learning
3. **Engaging UX**: Interactive and visually appealing
4. **Scalable**: Easy to add more synonym groups
5. **Accessible**: Works on any device with a browser

## 🔮 Future Enhancements

- **Difficulty Levels**: Easy/Medium/Hard based on word complexity
- **Category Selection**: Let users choose specific synonym categories
- **Progress Tracking**: Save user performance over time
- **Multiplayer Mode**: Compete with other users
- **Audio Support**: Pronunciation of Bengali words
- **Explanation Mode**: Show word meanings and usage examples