# https://www.tracery.io/ parser

# get current directory

import json, re, random, sys, time

class Tracery():
    def __init__(self, rules):
        # load file 
        try:
            self.rules = json.load(open(rules))
        except:
            print("Error loading file: " + rules + "\nTry checking https://jsonlint.com/ to find your problem.")
            sys.exit(1)

    def ParseTraceryString(self, rule):
        # new seed every time
        random.seed(time.time())
        # example: #animal# -> dog, can include spaces and punctuation
        # example: #animal names!#
        #[a-zA-Z0-9 ]+!?#
        while re.search(r"#([a-zA-Z0-9 ]+!?)#", rule):
            match = re.search(r"#([a-zA-Z0-9 ]+!?)#", rule)
            rule = rule.replace(match.group(0), self.ParseTraceryString(random.choice(self.rules[match.group(1)])))
        return rule
    
    def GetMainRule(self):
        return self.ParseTraceryString("#origin#")
    
    def GetRule(self, rule):
        return self.ParseTraceryString(rule)