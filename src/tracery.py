# https://www.tracery.io/ parser

# get current directory

import json, re, random, sys, time

# mods implemented from https://github.com/galaxykate/tracery/blob/8baa6ec53271ce7526e14b0ae3069a7469c6f035/js/tracery/mods-eng-basic.js
def Mod_IsVowel(letter):
    letter = letter.lower()
    return (letter == "a" or letter == "e" or letter == "i" or letter == "o" or letter == "u")

def Mod_IsAlphaNumeric(letter):
    return (letter.isalnum() or letter == " ")

def Mod_A(s):
    if len(s) > 0:
        if s[0].lower() == "u":
            if len(s) > 2:
                if s[2].lower() == "i":
                    return "a " + s
        if Mod_IsVowel(s[0]):
            return "an " + s
    return "a " + s

def Mod_FirstS(s):
    s2 = s.split(" ")
    finished = Mod_S(s2[0]) + " " + " ".join(s2[1:])
    return finished

def Mod_S(s):
    if len(s) > 0:
        if s[-1] == "s" or s[-1] == "h" or s[-1] == "x":
            return s + "es"
        elif s[-1] == "y":
            if not Mod_IsVowel(s[-2]):
                return s[:-1] + "ies"
            else:
                return s + "s"
        else:
            return s + "s"
    return s

def Mod_Ed(s):
    if len(s) > 0:
        if s[-1] == "s" or s[-1] == "h" or s[-1] == "x":
            return s + "ed"
        elif s[-1] == "e":
            return s + "d"
        elif s[-1] == "y":
            if not Mod_IsVowel(s[-2]):
                return s[:-1] + "ied"
            else:
                return s + "d"
        else:
            return s + "ed"
    return s

class Tracery():
    def __init__(self, rules):
        # load file 
        try:
            self.rules = json.load(open(rules))
        except:
            print("Error loading file: " + rules + "\nTry checking https://jsonlint.com/ to find your problem.")
            sys.exit(1)

    def ParseTraceryString(self, rule, isStored=False, isStoredBoolean=False):
        """# can include .lower/capitalize
        rulemod = rule.split(".")
        rule = rulemod[0]
        # modifiers is everything after the first . (can be multiple)
        modifiers = rulemod[1:]"""

        # new seed every time
        random.seed(time.time())
        # example: #animal# -> dog, can include spaces and punctuation (like .,!?)
        # example: #animal names!#
        # or, #animal names.capitalizeAll#
        #[a-zA-Z0-9 ]+!?
        while re.search(r"#([a-zA-Z0-9 ]+!?)+.?#", rule):
            match = re.search(r"#([a-zA-Z0-9 ]+!?)+.?#", rule)
            choice = random.choice(self.rules[match.group(1)])
            # get all rules in the match (seperated with ., first one is the rule)
            """modifiers = match.group(0).split(".")[1:]
            if "lower" in modifiers:
                choice = choice.lower()
            elif "capitalize" in modifiers:
                choice = choice.title()
            elif "capitalizeAll" in modifiers:
                choice = choice.upper()
            elif "a" in modifiers:
                choice = Mod_A(choice)
            elif "s" in modifiers:
                choice = Mod_S(choice)
            elif "firstS" in modifiers:
                choice = Mod_FirstS(choice)
            elif "ed" in modifiers:
                choice = Mod_Ed(choice)"""
            # TODO: Figure out why this doesn't work

            rule = rule.replace(match.group(0), self.ParseTraceryString(choice, isStored=isStored, isStoredBoolean=isStoredBoolean))

            if isStored and not isStoredBoolean: # if the rule is stored, add it to the enviroment, remove img/vid
                # remove the {img, {vid, etc. from the rule
                for img in re.findall(r"{img \S+}", rule):
                    rule = rule.replace(img, "")
                for vid in re.findall(r"{vid \S+}", rule):
                    rule = rule.replace(vid, "")
            
        return rule
    
    def GetMainRule(self):
        return self.ParseTraceryString("#origin#")
    
    def GetRule(self, rule, isStored=False, isStoredBoolean=False):
        return self.ParseTraceryString(rule, isStored=isStored, isStoredBoolean=isStoredBoolean)