import requests
from bs4 import BeautifulSoup

def scrape_sub_pages(base_url):
    # Fetch the content of the main page
    response = requests.get(base_url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements with class 'trending_item_title' and extract 'href'
    links = soup.find_all("div", class_="trending_item_title")

    # Extract the href attribute and create full URLs
    sub_pages = [base_url + link.a['href'] for link in links if link.a and 'href' in link.a.attrs]

    return sub_pages

# URL of the main page
base_url = "https://www.factslides.com/"

# Get the list of sub-pages
sub_pages = scrape_sub_pages(base_url)
print(sub_pages)

import requests
from bs4 import BeautifulSoup
import json
import spacy

# Load the English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_md")

def scrape_description(sub_page_url):
    response = requests.get(sub_page_url)
    if response.status_code != 200:
        print(f"Failed to retrieve {sub_page_url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', type='application/ld+json')

    if not script_tag:
        return []
    
    try:
        # Parse JSON data
        data = json.loads(script_tag.string)
            # Parse JSON data
        data = json.loads(script_tag.string)
        description = data.get('articleBody', '')

        # Process the text
        doc = nlp(description)

        # Extract sentences
        facts = [sent.text.strip() for sent in doc.sents]
        # Post-process to merge sentences that are too short
        merged_facts = []
        for fact in facts:
            words = fact.split()
            if merged_facts and len(words) <= 5:
                merged_facts[-1] += ' ' + fact
            else:
                merged_facts.append(fact)

        return merged_facts, description
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from {sub_page_url}: {e}")
        return [] , ""

def scrape_all_facts(sub_pages):
    all_facts = []
    all_desc = []
    for sub_page in sub_pages:
        print(f"Scraping {sub_page}")
        facts, desc = scrape_description(sub_page)
        all_facts.extend(facts)
        all_desc.extend(desc)
    return all_facts, "".join(all_desc)

# Scrape all facts from sub-pages
all_facts, all_desc = scrape_all_facts(sub_pages)

from bs4 import BeautifulSoup

def scrape_description_from_div(sub_page_url):
    response = requests.get(sub_page_url)
    if response.status_code != 200:
        print(f"Failed to retrieve {sub_page_url}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')

    # List to store the texts of each div
    div_texts = []

    # Start with the first div
    i = 1

    # Use a while loop to find each div
    while True:
        div_id = f'i{i}'
        div = soup.find('div', id=div_id)
        if div is None:
            # If the div is not found, break the loop
            break
        else:
            # Extract text and add it to the list
            text = div.get_text(separator=' ', strip=True)
            div_texts.append(text)
        i += 1  # Increment to the next div

    return div_texts

def scrape_all_facts(sub_pages):
    all_facts = []
    for sub_page in sub_pages:
        print(f"Scraping {sub_page}")
        facts_list = scrape_description_from_div(sub_page)
        all_facts.extend(facts_list)
    return all_facts


fact_list_from_div = scrape_all_facts(sub_pages)

def remove_specific_text_from_list(strings, text_to_remove):
    updated_strings = []
    for string in strings:
        if string.endswith(text_to_remove):
            string = string[:-len(text_to_remove)]
        updated_strings.append(string)
    return updated_strings

text_to_remove = " ♦ SOURCE ♺ SHARE"

fact_list_from_div_trimed = remove_specific_text_from_list(fact_list_from_div, text_to_remove)

import random

unique_fun_facts = list(set(fact_list_from_div_trimed))
print(len(unique_fun_facts))


shuffled_unique_fun_facts = unique_fun_facts.copy()
random.shuffle(shuffled_unique_fun_facts)

for index, fact in enumerate(shuffled_unique_fun_facts):
    if len(fact) > 280:
        print(f"Line {index + 1} has more than 280 characters: {fact}")

with open('fun_facts.txt', 'w') as file:
    # Iterate over the list
    for item in shuffled_unique_fun_facts:
        file.write(item + '\n')

