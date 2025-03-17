#!/home/ai/YGHC/bin/python3.12
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import tkinter as tk
from tkinter import ttk
from transformers import pipeline
import difflib

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

def recommend_sentences_ml(text, top_keywords):
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)
    sentences = re.split(r'(?<=[.!?]) +', text)
    recommendations = []
    for sentence in sentences:
        for keyword, _ in top_keywords:
            if keyword not in sentence.lower():
                input_length = len(sentence.split()) + len(keyword.split())
                max_length = min(50, input_length)
                min_length = min(max_length, max(25, input_length // 2))
                summary = summarizer(f"{sentence} {keyword}", max_length=max_length, min_length=min_length, do_sample=False)
                recommendations.append(summary[0]['summary_text'])
                break
    return recommendations

def highlight_differences(current_sentence, recommended_sentence, current_text_widget, recommended_text_widget):
    differ = difflib.Differ()
    diff = list(differ.compare(current_sentence.split(), recommended_sentence.split()))
    for word in diff:
        if word.startswith('- '):
            current_text_widget.insert(tk.END, word[2:] + ' ', 'old')
        elif word.startswith('+ '):
            recommended_text_widget.insert(tk.END, word[2:] + ' ', 'new')
        else:
            current_text_widget.insert(tk.END, word[2:] + ' ')
            recommended_text_widget.insert(tk.END, word[2:] + ' ')
    current_text_widget.insert(tk.END, "\n\n")
    recommended_text_widget.insert(tk.END, "\n\n")

def analyze_url(url, current_text, recommended_text):
    html_content = fetch_website_content(url)
    text_content = extract_text_from_html(html_content)
    words = clean_and_tokenize_text(text_content)
    keyword_weights = analyze_keywords(words)
    top_keywords = recommend_keywords(keyword_weights)
    sentences = re.split(r'(?<=[.!?]) +', text_content)
    sentence_recommendations = recommend_sentences_ml(text_content, top_keywords)

    current_text.delete(1.0, tk.END)
    recommended_text.delete(1.0, tk.END)

    for current_sentence, recommended_sentence in zip(sentences, sentence_recommendations):
        highlight_differences(current_sentence, recommended_sentence, current_text, recommended_text)

def main():
    root = tk.Tk()
    root.title("Keyword Analyzer")
    root.geometry("1200x600")

    tk.Label(root, text="Enter the website URL:").pack(pady=5)
    url_entry = tk.Entry(root, width=50)
    url_entry.pack(pady=5)

    frame = tk.Frame(root)
    frame.pack(pady=10, fill=tk.BOTH, expand=True)

    current_text = tk.Text(frame, wrap=tk.WORD, width=60, height=20)
    current_text.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
    current_text.tag_config('old', foreground='red')

    recommended_text = tk.Text(frame, wrap=tk.WORD, width=60, height=20)
    recommended_text.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)
    recommended_text.tag_config('new', foreground='green')

    analyze_button = tk.Button(root, text="Analyze", command=lambda: analyze_url(url_entry.get(), current_text, recommended_text))
    analyze_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
