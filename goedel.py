import praw
import archiveis
import time
from random import choice
import logging
import re
import gcredentials

# TODO add command line args

def parse_quotes():
    with open('quotes.txt', 'r') as f:
        lines = f.readlines()
    

    quotes = []
    for n in range(len(lines) / 2):
        quotes.append((lines[2 * n].strip(), lines[2 * n + 1].strip()))

    return quotes

def get_urls(body_markdown):
    regex = r"(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*)"
    links = re.findall(regex, body_markdown)
   
    return links

def generate_text(quote, submission):
    text =  quote[0].decode('string-escape') # in case quote has \n in it
    text += '\n\n'
    text += '[Here\'s]('
    text += archiveis.capture(submission.url)
    text += ') an archived version of '
    

    urls = None
    if submission.is_self and submission.selftext:
        urls = get_urls(submission.selftext)
        archive_urls = map(archiveis.capture, urls)
    
    if submission.is_self:
        text += 'this thread'
        if urls:
            text += '[,' if quote[1] else ','
        else:
            text += '[.' if quote[1] else '.'
    else:
        text += 'the linked post'
        text += '[.' if quote[1] else '.' 

    if quote[1]:
        text += ']('
        text += quote[1]
        text += ')'

    if urls:
        text += ' and the links:'

        for link in zip(urls, archive_urls):
            text += '\n\n'
            text += '[' + link[0] + '](' + link[1] + ')'

    return text


def login():
    return praw.Reddit(user_agent='Goedel\'s Vortex v2',
                       client_id=gcredentials.client_id,
                       client_secret=gcredentials.client_secret,
                       username=gcredentials.username,
                       password=gcredentials.password)

def main():
    logger.info('Bot Initiated')
    r = login()

    sub = r.subreddit('badmathematics')
    
    start_time = time.time()

    quotes = parse_quotes()
    
    logger.info('Bot Ready')
    for submission in sub.stream.submissions():
        # Only comment on new submissions
        if submission.created_utc < start_time:
            continue

        # Select random quote
        rand_quote = choice(quotes)

        text = generate_text(rand_quote, submission)
        try:
            submission.reply(text)
            logger.info('replied to ' + submission.id)
        except praw.exceptions.APIException as err:
            logger.error(err)



if __name__ == '__main__':
    # Logging Configuration
    logging.basicConfig(filename='goedel.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('goedel')
##    logger.addHandler(logging.StreamHandler()) # adds stderr as output stream
    
    main()

    logging.shutdown()
