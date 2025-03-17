#!/home/ai/YGHC/bin/python3.12
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import tkinter as tk
from tkinter import ttk

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
                recommendations.append(sentence.strip())
                break
    return recommendations

def analyze_url(url, tree):
    html_content = fetch_website_content(url)
    text_content = extract_text_from_html(html_content)
    words = clean_and_tokenize_text(text_content)
    keyword_weights = analyze_keywords(words)
    top_keywords = recommend_keywords(keyword_weights)
    sentence_recommendations = recommend_sentences(text_content, top_keywords)

    for i in tree.get_children():
        tree.delete(i)

    for sentence in sentence_recommendations:
        tree.insert("", "end", values=(sentence, sentence))

def main():
    root = tk.Tk()
    root.title("Keyword Analyzer")
    root.geometry("1200x600")

    tk.Label(root, text="Enter the website URL:").pack(pady=5)
    url_entry = tk.Entry(root, width=50)
    url_entry.pack(pady=5)

    columns = ("Current Sentence", "Recommended Sentence")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.heading("Current Sentence", text="Current Sentence")
    tree.heading("Recommended Sentence", text="Recommended Sentence")
    tree.column("Current Sentence", width=600, anchor="w")
    tree.column("Recommended Sentence", width=600, anchor="w")
    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    analyze_button = tk.Button(root, text="Analyze", command=lambda: analyze_url(url_entry.get(), tree))
    analyze_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
