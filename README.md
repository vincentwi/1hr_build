# 1hr_build

Ideated through a few things, ultimately decided to build something I would use.

Lately i've been behind on emails, so i've made:

#Daily email digest
A tool leveraging OpenAI's ChatGPT and Gmail API to read all messages received yesterday, summarize them, give a sentiment analysis and urgency rating, then email the digest to read at the top of the inbox at 8:59am.  

Basically
This project is a Python-based utility that automates the task of summarizing and analyzing your Gmail inbox emails from the previous day. The tool leverages Google's Gmail API to fetch email data and uses OpenAI's GPT-4 engine to generate summaries, assess sentiment, and gauge urgency.

Key Features
Summarization: Shortens long emails to their key points.
Sentiment Analysis: Understands the overall tone (e.g., positive, negative) of the email.
Urgency Detection: Assesses how urgent the email is, aiding in prioritization.
Technologies Used
Python: The backend code is written in Python.
Gmail API: Used for fetching emails from your Gmail inbox.
OpenAI's GPT-4: Summarizes the emails, performs sentiment analysis, and detects urgency.
BeautifulSoup: Extracts plain text from HTML email content.
Pandas: Stores and manipulates the email data for easy analysis and CSV export.
Installation & Setup
Clone this repository.

Install the required Python packages.

bash
Copy code
pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 pandas beautifulsoup4 openai
Setup Gmail API and download your credentials.json.

Place credentials.json in the project directory.

Usage
Run the main Python script.

bash
Copy code
python your_script_name.py
The script will create a DataFrame and an output CSV file containing:

Sender
Subject
Summary
Sentiment
Urgency
Code Structure
Authentication
The script begins by authenticating the user using OAuth 2.0.

Gmail API Calls
The get_yesterday_message_ids_and_senders() function fetches the message IDs of emails received the previous day.

Data Processing
The get_subject_from_message() and get_plain_text_from_message() functions extract the subject and the plain text content from each email.

GPT-4 Integration
summarize_email(): Summarizes the email content.
get_email_sentiment(): Performs sentiment analysis.
get_email_urgency(): Assesses the urgency of the email.
Data Storage
All the data is stored in a Pandas DataFrame and saved as a CSV file.

Limitations
The OpenAI GPT-4 engine has a maximum token limit; emails are truncated to fit within this limit.
The Gmail API has its own set of limitations, including rate limits.
Security
Do not share your credentials.json and token.json.
The OpenAI API key is sensitive; ensure it's securely stored and not embedded in the code.
Contributing
Feel free to fork this project, open issues, or submit pull requests.

License
This project is licensed under the MIT License.

By using this tool, you can maintain a more organized and prioritized email workflow, while gaining insightful information about your communications.