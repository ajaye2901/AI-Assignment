import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template
import openai
import re
from nltk.tokenize import word_tokenize

# Set up OpenAI API
api_key = "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"
openai.api_key = api_key

app = Flask(__name__)

# Scrape course information
def scrape_course_info():
    url = "https://brainlox.com/courses/category/technical"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        courses = []

        course_cards = soup.find_all("div", class_="course-card")

        for card in course_cards:
            title = card.find("h2").text.strip()
            description = card.find("p", class_="description").text.strip()
            course_url = card.find("a")["href"].strip()

            courses.append({
                "title": title,
                "description": description,
                "url": course_url
            })

        return courses
    else:
        return []

# Preprocess text
def clean_text(text):
    # Remove HTML tags using regex
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)
    return cleantext

def tokenize_text(text):
    tokens = word_tokenize(text)
    return tokens

def lowercase_text(text):
    return text.lower()

# Initialize GPT-3 chat
def chat_with_gpt3(user_message):
    conversation_history = []
    conversation_history.append("Hello, I'm your course recommendation chatbot. How can I assist you today?")
    conversation_history.append(user_message)


    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="\n".join(conversation_history),
        max_tokens=50
    )

    bot_response = response.choices[0].text
    conversation_history.append(bot_response)

    return bot_response

# Recommend courses based on user input
def recommend_courses(user_query, courses):
    matching_courses = []

    for course in courses:
        if user_query.lower() in course["title"].lower() or user_query.lower() in course["description"].lower():
            matching_courses.append(course)

    return matching_courses

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("user_message")
    
    courses = scrape_course_info()
    recommended_courses = recommend_courses(user_message, courses)

    bot_response = chat_with_gpt3(user_message)

    if recommended_courses:
        bot_response += "\n\nRecommended Courses:\n"
        for course in recommended_courses:
            bot_response += f"- {course['title']}\n  {course['description']}\n  URL: {course['url']}\n"

    return render_template("index.html", user_message=user_message, bot_response=bot_response)

if __name__ == "__main__":
    app.run(debug=True)
