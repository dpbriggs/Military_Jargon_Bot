import csv
import praw
import configparser
from itertools import groupby
from pprint import pprint

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

        #Pull up military jargon from csv
        self.jargon = self.readDict('military_jargon.csv')
        
        #Get previously submitted comments (threads.id)
        self.previously_posted = self._read_wiki()
        print(self.previously_posted)
        
        #Get top threads from /r/military stories
        self.stories = self.get_threads()

        #Find jargon in threads
        self.matched_jargon = self.jargon_finder()
        global k
        k = self.matched_jargon
        #Reply to all threads found with Jargon
        #self.post_comment()
        
    def post_comment(self):
        #Iterate through list and check if it wasn't already replied too
        submitted = []
        for i in self.matched_jargon:
            i[0].add_comment(i[1])
            print(i[0].short_link)
            submitted.append(i[0].id)
        self._write_wiki(submitted)
        
    def _read_wiki(self):
        #Convert string of numbers seperated by commas and spaces into a list of str-type numbers
        wiki_page = self.r.get_wiki_page('BotHeaven', 'index').content_md.replace(' ', '').split(',')
        return wiki_page
    
    def _write_wiki(self, submitted):
        #Convert list of numbers into a string
        full_list = self.previously_posted
        full_list = full_list + submitted
        join_list = ', '.join(full_list)
        self.r.edit_wiki_page('BotHeaven', 'index', join_list)

    def jargon_finder(self):
        matches = []
        #We will now look for jargon
        for i in range(0, len(self.stories)):
            for k in self.stories[i][1]:
                if k in self.jargon and k != '':
                    #Append post, the jargon, and the explaination
                    matches.append((self.stories[i][0], k, self.jargon[k]))
            
        #Structure of list is: [[(post_object1, jargon1, trans1), (post_object1, jargon2, trans2)], ...]
        #Structure is changed very shortly...
        matches = [sorted(x,key=lambda t: t[1]) for x in [list(v) for i, v in groupby(matches, key=lambda t: t[0])]]


        #Comment_bucket list structure is: [[post_object1, comment_1], [post_object2, comment_2], ...]
        comment_bucket = []
        comment_start = '\n\n#This is an automated translation so there may be some errors. [Source](https://github.com/iMultiPlay/Military_Jargon_Bot)\n\n ***** \n\n'
        comment_end = '\n\n ***** \n\n###Please reply or PM if I did something incorrect or missed some jargon \n\nBot by /u/Davess1'
        for threads in matches:
            comment =  'Jargon | Translation \n :----|:----- \n '
            for jargon in threads:
                if jargon[2] not in comment:
                    comment = comment + jargon[1] + '| == ' + jargon[2] + ' \n '
            comment_bucket.append((threads[0][0], comment_start+comment+comment_end))
        return comment_bucket
        
    def get_threads(self):
        #Get top threads and break text up for iterating later
        hold = []
        subreddit = self.r.get_subreddit('militarystories')
        for posts in subreddit.get_hot(limit=15):
            if posts.id not in self.previously_posted:
                op_text = posts.selftext.upper() #all uppercase
                op_text = ''.join([x for x in op_text if x.isalpha() or x.isspace()]) #Kill puncuation
                op_text = op_text.split(' ')
                hold.append((posts, op_text))
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
