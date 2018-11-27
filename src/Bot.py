import random as rnd
import wikipedia

from models.nlp import (
    get_named_entities,
    get_nouns,
    summarize_article,
    get_sentiment,
)
from models.logging import log


class Bot:

    def __init__(self, name):
        self.name = name

        self.liked_pages = []
        self.disliked_pages = []
        self.prev_page = []
    
    def get_search_string(self, msg):
        search_string = ' '.join([ent[0] for ent in get_named_entities(msg)])
        search_string += ' '
        search_string += ' '.join([noun for noun in get_nouns(msg)])

        return search_string

    def recommend(self, msg):
        search_string = self.get_search_string(msg)
        log("SEARCHING FOR:", search_string)

        page_titles = wikipedia.search(search_string)
        log("Founded articles:\n", page_titles)

        ### Choose the most appropriate page based on previous activity ###
        log("Loading...")
        loaded = False
        while not loaded:
            try:
                self.prev_page = wikipedia.page(rnd.choice(page_titles))
                loaded = True
            except wikipedia.exceptions.DisambiguationError:
                pass      

        print(self.prev_page.categories)

        log("Summarizing...")
        try:
            summary = summarize_article(self.prev_page.summary)
        except ValueError:
            summary = summarize_article(self.prev_page.content)

        return summary + "<br>More info here: " + str(self.prev_page.url)
        
    def feedback(self, msg):
        sentiment = get_sentiment(msg)[0][1]
        log(msg, ":", sentiment)

        res = "Thanks for the feedback. I recorder the you "

        if sentiment > .5:
            self.liked_pages.append(self.prev_page)
        else:
            self.disliked_pages.append(self.prev_page)
            res += "do not "

        return res + f"like the page: {self.prev_page.title}"

    def response(self, msg):
        if self.get_search_string(msg) == ' ':
            if self.prev_page is not None:
                return self.feedback(msg)
            else:
                return "What would you like to know about?"
        else:
            return self.recommend(msg)