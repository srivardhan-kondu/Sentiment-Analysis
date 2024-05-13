import re
import os
import nltk
import joblib
import requests
import numpy as np
import urllib.request as urllib
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
import streamlit as st

def extract_all_reviews(url, clean_reviews, org_reviews, customernames, commentheads, ratings):
    with urllib.urlopen(url) as u:
        page = u.read()
        page_html = BeautifulSoup(page, "html.parser")
    reviews = page_html.find_all('div', {'class': 't-ZTKy'})
    commentheads_ = page_html.find_all('p', {'class': '_2-N8zT'})
    customernames_ = page_html.find_all('p', {'class': '_2sc7ZR _2V5EHH'})
    ratings_ = page_html.find_all('div', {'class': ['_3LWZlK _1BLPMq', '_3LWZlK _32lA32 _1BLPMq', '_3LWZlK _1rdVr6 _1BLPMq']})

    for review in reviews:
        x = review.get_text()
        org_reviews.append(re.sub(r'READ MORE', '', x))
        clean_reviews.append(re.sub(r'[^a-zA-Z ]', ' ', x).lower())

    for cn in customernames_:
        customernames.append('~' + cn.get_text())

    for ch in commentheads_:
        commentheads.append(ch.get_text())

    ra = []
    for r in ratings_:
        try:
            if int(r.get_text()) in [1, 2, 3, 4, 5]:
                ra.append(int(r.get_text()))
            else:
                ra.append(0)
        except:
            ra.append(r.get_text())

    ratings += ra
    print(ratings)

def main():
    st.title(" Sentiment Analysis")

    url = st.text_input("Enter the Flipkart product URL:")
    num_reviews = st.number_input("Enter the number of reviews to extract:", min_value=1, step=1)
    if st.button("Extract Reviews"):
        clean_reviews = []
        org_reviews = []
        customernames = []
        commentheads = []
        ratings = []

        with urllib.urlopen(url) as u:
            page = u.read()
            page_html = BeautifulSoup(page, "html.parser")

        proname_elements = page_html.find_all('span', {'class': 'B_NuCI'})
        if proname_elements:  # Check if any elements are found
            proname = proname_elements[0].get_text()
        else:
            proname = "Product Name Not Found"  # Set a default value if not found

        price_elements = page_html.find_all('div', {'class': '_30jeq3 _16Jk6d'})
        if price_elements:  # Check if any elements are found
            price = price_elements[0].get_text()
        else:
            price = "Price Not Found"  # Set a default value if not found

        # Getting the link of see all reviews button
        all_reviews_url = page_html.find_all('div', {'class': 'col JOpGWq'})
        if all_reviews_url:  # Check if any elements are found
            all_reviews_url = all_reviews_url[0].find_all('a')[-1]
            all_reviews_url = 'https://www.flipkart.com' + all_reviews_url.get('href')
            url2 = all_reviews_url + '&page=1'
        else:
            st.error("See all reviews button not found.")
            return

        # Start reading reviews and go to the next page after all reviews are read
        while True:
            x = len(clean_reviews)
            # Extracting the reviews
            extract_all_reviews(url2, clean_reviews, org_reviews, customernames, commentheads, ratings)
            url2 = url2[:-1] + str(int(url2[-1]) + 1)
            if x == len(clean_reviews) or len(clean_reviews) >= num_reviews:
                break

        org_reviews = org_reviews[:num_reviews]
        clean_reviews = clean_reviews[:num_reviews]
        customernames = customernames[:num_reviews]
        commentheads = commentheads[:num_reviews]
        ratings = ratings[:num_reviews]

        # Building wordcloud
        for_wc = ' '.join(clean_reviews)
        wcstops = set(STOPWORDS)
        wc = WordCloud(width=1400, height=800, stopwords=wcstops, background_color='white').generate(for_wc)
        plt.figure(figsize=(20, 10), facecolor='k', edgecolor='k')
        plt.imshow(wc, interpolation='bicubic')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('woc.png')
        st.image('woc.png')

        
        st.write(f"Product Name: {proname}")
        st.write(f"Price: {price}")
        st.write("Reviews:")
        for i in range(len(org_reviews)):
            st.write(f"Review {i+1}:")
            st.write(f"Original Review: {org_reviews[i]}")
            st.write(f"Cleaned Review: {clean_reviews[i]}")
            st.write(f"Customer Name: {customernames[i]}")
            st.write(f"Comment Head: {commentheads[i]}")
            st.write(f"Rating: {ratings[i]}")

if __name__ == '__main__':
    main()
