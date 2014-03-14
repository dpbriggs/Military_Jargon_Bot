import csv
import praw
import configparser
from itertools import groupby

class Military_Jargon(object):
    def __init__(self):
        #read config file
        self._read_config('config.ini')
        
        #Get information from config file
        self.user_agent = self.config['info']['user_agent']
        self.user_name = self.config['info']['username']
        self.password = self.config['info']['password']
        
        #Setup praw
        self.setup_praw(self.user_agent, self.user_name, self.password)

        #Pull up military jargon
        self.jargon = self.readDict('military_jargon.csv')
        global c
        c = self.jargon
        #Get previously submitted comments
        self.submitted = self._read_wiki()
        print(self.submitted)
        
        #Get top threads from /r/military stories
        self.stories = self.get_threads()

        self.matched_jargon = self.jargon_finder()
        global k
        k = self.matched_jargon
        
    def _read_wiki(self):
        #Convert string of numbers seperated by commas and spaces into a list of str-type numbers
        wiki_page = self.r.get_wiki_page('BotHeaven', 'index').content_md.replace(' ', '').split(',')
        return wiki_page
    
    def _write_wiki(self, ref_num):
        #Convert list of numbers into a string
        full_list = self.wiki_page
        full_list.append(ref_num)
        join_list = ', '.join(full_list)
        self.r.edit_wiki_page('BotHeaven', 'index', join_list)

    def jargon_finder(self):
        matches = []
        #We will now look for jargon
        for i in range(0, len(self.stories)):
            for k in self.stories[i][1]:
                if k in self.jargon and k != '':
                    #Append post_id, the jargon, and the explaination
                    matches.append((self.stories[i][0], k, self.jargon[k]))
        matches = [list(v) for i, v in groupby(matches, key=lambda t: t[0])]
        return matches
    
    def get_threads(self):
        #Get top threads and break text up for iterating later
        hold = []
        subreddit = self.r.get_subreddit('militarystories')
        for posts in subreddit.get_hot(limit=15):
            if posts.id not in self.submitted:
                op_text = posts.selftext.upper() #all uppercase
                op_text = ''.join([x for x in op_text if x.isalpha() or x.isspace()]) #Kill puncuation
                op_text = op_text.split(' ')
                hold.append((posts.id, op_text))
        return hold
    
    def _read_config(self, file):
        self.config = configparser.ConfigParser()
        self.config.read(file)
    
    def setup_praw(self, user_agent, user_name, password):
        self.r = praw.Reddit(user_agent=user_agent)
        self.r.login(user_name, password)
        
    def readDict(self, file):
        h = []
        with open(file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                    if row != []:
                            h.append(row)
            return dict(h)
        
Military_Jargon()
