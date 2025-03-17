#!/home/ai/YGHC/bin/python3.12
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

# Custom stopwords list
STOPWORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was',
    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and',
    'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
    'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
    'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
])

def fetch_website_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch the website content: {response.status_code}")

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()  # Remove JavaScript and CSS
    text = soup.get_text()
    return text

def clean_and_tokenize_text(text):
    words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in STOPWORDS]
    return filtered_words

def analyze_keywords(words):
    word_counts = Counter(words)
    total_words = sum(word_counts.values())
    keyword_weights = {word: count / total_words for word, count in word_counts.items()}
    return keyword_weights

def recommend_keywords(keyword_weights, top_n=10):
    sorted_keywords = sorted(keyword_weights.items(), key=lambda item: item[1], reverse=True)
    return sorted_keywords[:top_n]

def recommend_sentences(text, top_keywords):
    sentences = re.split(r'(?<=[.!?]) +', text)
    recommendations = []
    for sentence in sentences:
        for keyword, _ in top_keywords:
            if keyword in sentence.lower():
                recommendations.append(sentence)
                break
    return recommendations

def main(url):
    html_content = fetch_website_content(url)
    text_content = extract_text_from_html(html_content)
    words = clean_and_tokenize_text(text_content)
    keyword_weights = analyze_keywords(words)
    top_keywords = recommend_keywords(keyword_weights)

    print("Keyword Weights:")
    for keyword, weight in keyword_weights.items():
        print(f"{keyword}: {weight:.4f}")

    print("\nKeyword Recommendations:")
    for keyword, weight in top_keywords:
        print(f"{keyword}: {weight:.4f}")

    print("\nSentence Recommendations:")
    sentence_recommendations = recommend_sentences(text_content, top_keywords)
    for sentence in sentence_recommendations:
        print(f"- {sentence}")

if __name__ == "__main__":
    url = input("Enter the website URL: ")
    main(url)
