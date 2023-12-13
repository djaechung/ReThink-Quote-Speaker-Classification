# importing libraries
import numpy as np
import pandas as pd
import json
import csv
import regex as re
import seaborn as sns
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
stop_words = set(stopwords.words('english'))


GNI88 = pd.read_csv("/Users/carla/Desktop/internships/rethinkmedia/GNI88_cleaned_data.csv")
GNI88 = GNI88[GNI88['Article Status']=='News']
GNI88 = GNI88[GNI88["source_name_cleaned"].str.contains("Unknown|Unnamed|unknown|unnamed", regex=True)==False]
GNI88 = GNI88[GNI88["Source Gender"]!='Organization']
GNI88 = GNI88.drop(labels=[370772, 370773], axis=0).reset_index(drop=True) # This one is an empty quote


source_groups = {"Foreign Government": ['Foreign Gov/Mil Official', 'Former Soviet Military Officer', 
                                        'South Korean Official', 'EU Official'],
                "Experts": ['Nuke Organization','Non-Profit/NGO','Think Tanks',
                            'Nuke Organization - Other', 'Nuke Organization - Academic',
                            'International Orgs','Academic','Nuclear Scientist',"Analyst/Commentator",
                            'Attorney','Regulator', 'Research Group'],
                "US Congress": ['US Rep. & Staff','US Senate & Staff', 'Partisans/Fmr. Politicians'],
                "US Federal Officials": ['Federal Official','State/Local Official',
                                        'Former Admin. Officials','Judicial Official'],
                "US Defense": ['US Military','Defense Forces','Defense', 'retired US Military', 'Former DIA intelligence'],
                "Media": ["Media/Journalist","Blogger"],
                "Corporate Official": ['Corporate Official'],
                "Other": ['Other','Chairman','Terrorist/Extremist','Information minister',
                          'Religious/Clerical', 'Ambassador', 'Nuclear Official',
                          'Citizen','Public Polling','US Police','Deputy', 'P & S - Former Government', 'Director']}



# Helper function that inverts a dictionary. This will be useful for using speaker groups
# later on in model evaluation
def invert_dict(dictionary):
    """Inputs:
     - dictionary: dict, dictionary we wish to invert
     Outputs:
     - dict, where keys are the initial dictionary's values and values are the initial dictionary's keys"""
  # get a list of all items in all dictionary values
    speaker_types = list(np.concatenate(list(dictionary.values())).flat)
    # each speaker type will become its own key now, and the value will be the speaker group it's a part of
    inverted_dict = {}
    for speaker_type in speaker_types:
        # find the group the speaker_type belongs in
        speaker_group = [key for key, value in dictionary.items() if speaker_type in value][0]
        # update the inverted dictionary such that the key is the speaker type and the value is the speaker group
        inverted_dict[speaker_type] = speaker_group
    return inverted_dict



# lookup dictionary which can convert a speaker type to its classification group in constant time
source_to_group = invert_dict(source_groups)



def assign_source_to_group(source_type):
    """Inputs:
    - source_type: str, source type from quote datafame
    Outputs:
    - str of the bigger speaker category to which source_type belongs"""
    if type(source_type) != str:
        return "Other"
    try:
        return source_to_group[source_type]
    except:
        return "Other"
    

# Listing indicidator features to compare across the speaker categories
experts_ps = ["associate professor",
              "university",
              "studies",
              "scholar",
              "expert",
              "historian",
              "academy",
              "social science",
              "lecturer",
              "physicist",
              "professor",
              "political science",
              "political",
              "scientist",
              "college",
              "education",
              "school",
              "economics",
              "international relations",
              "physics",
              "associate professor",
              "researcher",
              "laboratory",
              "research fellow",
              "graduate school",
              "international affairs",
              "research associate",
              "dr\.",
              "ph\.d\.",
              "institute of technology",
              "economist",
              "analysis",
              "counselor",
              "postdoctoral",
              "fellow",
              "specialist",
              "novelist",
              "founder",
              "council",
              "director",
              "program",
              "think tank",
              "foundation",
              "institute",
              "division",
              "policy",
              "association",
              "center",
              "group",
              "superindendent",
              "international"]
foreign_gov_ps = ["putin|kim jong un|netanyahu|ayatollah|moon jae in",
                  "[nseih] president",
                  "[nseih] foreign",
                  "foreign minister",
                  "foreign ministry",
                  "prime minister",
                  "people's liberation army",
                  "foreign policy",
                  "supreme leader",
                  "prince"] 
corporate_official_ps = ["chief finnancial officer",
                         "managing director",
                         "bank",
                         "chief executive",
                         "general manager",
                         "investment fund",
                         "investment",
                         "employer",
                         "firm",
                         "chief executive officer",
                         "businessman",
                         "businesswoman",
                         "inc\.",
                         "manager",
                         "ltd[ ,\.]",
                         "chairman",
                         "chairwoman",
                         "sales",
                         "managing",
                         "program director",
                         "strategist",
                         "company",
                         "contractor",
                         "consultancy"]
judicial_ps = ["attorney",
               "justice",
               "lawyer",
               "court",
               "judge",
               "magistrate"]
us_congress_ps = [" sen\.",
                  " rep\.",
                  " sens\.",
                  " reps\.",
                  " r ",
                  " d ",
                  "\(r",
                  "\(d",
                  "democrat",
                  "democratic",
                  "republican",
                  "majority leader",
                  "minority leader",
                  "senate",
                  "house",
                  "committee",
                  "frontrunner",
                  "candidate",
                  "committee chairman",
                  "ranking member",
                  " top",
                  "foreign relations committee",
                  "intelligence committee",
                  "hopeful",
                  "house speaker",
                  "campaign"]
us_defense_ps = ["pentagon",
                 "navy",
                 "air force",
                 "army",
                 "marine",
                 "coast gaurd",
                 " capt\.",
                 "captain",
                 " gen\.",
                 "general",
                 " adm\.",
                 "admiral",
                 " col\.",
                 "colonel",
                 " lt\.",
                 "lieutenant",
                 "chief of staff",
                 "joint chiefs of staff",
                 "commander",
                 "norad",
                 "northcom",
                 "special forces",
                 "strategic command",
                 "defense secretary",
                 "nato",
                 "allied",
                 "officer",
                 "corps",
                 " u\.s\.",
                 " us "]
us_fed_officials_ps = ["biden|trump|obama|bush|clinton|reagan",
                        "ambassador",
                        "u\.s\. president",
                        "department",
                        "attorney",
                        "secretary of",
                        "us ambassador",
                        "state department",
                        "national security",
                        "secretary",
                        "secretary of"]
media_ps = ["author\:? ",
            "correspondent",
            "columnist",
            " post",
            " host",
            "editor",
            "times",
            "press",
            "magazine",
            "msnbc|cnn|fox",
            "writer",
            "syndicated columnist",
            "editorial",
            "blog",
            ": .+",
            "i\"m",
            "by\:? ",
            "media_tag"] 
international_officials_ps = ["deputy director general",
                              "international atomic energy agency",
                              "iaea",
                              "inspector",
                              "inspections"]
other_ps = ["hezbollah",
            "taliban",
            "pollster",
            "archbishop",
            "pope",
            "bishop",
            "church",
            "rev\.",
            "reverand",
            "police",
            "commissioner",
            "nypd",
            "resident"]



# Creating dictionary with speaker categories as keys and a list of their corresponding indicators as the value
speaker_dict = {"Experts" : ["associate professor",
              "university",
              "studies",
              "scholar",
              "expert",
              "historian",
              "academy",
              "social science",
              "lecturer",
              "physicist",
              "professor",
              "political science",
              "political",
              "scientist",
              "college",
              "education",
              "school",
              "economics",
              "international relations",
              "physics",
              "associate professor",
              "researcher",
              "laboratory",
              "research fellow",
              "graduate school",
              "international affairs",
              "research associate",
              "dr\.",
              "ph\.d\.",
              "institute of technology",
              "economist",
              "analysis",
              "counselor",
              "postdoctoral",
              "fellow",
              "specialist",
              "novelist",
              "founder",
              "council",
              "director",
              "program",
              "think tank",
              "foundation",
              "institute",
              "division",
              "policy",
              "association",
              "center",
              "group",
              "superindendent",
              "international"], 
"Foreign Government" : ["putin|kim jong un|netanyahu|ayatollah|moon jae in",
                  "[nseih] president",
                  "[nseih] foreign",
                  "foreign minister",
                  "foreign ministry",
                  "prime minister",
                  "people's liberation army",
                  "foreign policy",
                  "supreme leader",
                  "prince"], 
"Corporate Official" : ["chief finnancial officer",
                         "managing director",
                         "bank",
                         "chief executive",
                         "general manager",
                         "investment fund",
                         "investment",
                         "employer",
                         "firm",
                         "chief executive officer",
                         "businessman",
                         "businesswoman",
                         "inc\.",
                         "manager",
                         "ltd[ ,\.]",
                         "chairman",
                         "chairwoman",
                         "sales",
                         "managing",
                         "program director",
                         "strategist",
                         "company",
                         "contractor",
                         "consultancy"],
"Judicial" : ["attorney",
               "justice",
               "lawyer",
               "court",
               "judge",
               "magistrate"],
"US Congress" : [" sen\.",
                  " rep\.",
                  " sens\.",
                  " reps\.",
                  " r ",
                  " d ",
                  "\(r",
                  "\(d",
                  "democrat",
                  "democratic",
                  "republican",
                  "majority leader",
                  "minority leader",
                  "senate",
                  "house",
                  "committee",
                  "frontrunner",
                  "candidate",
                  "committee chairman",
                  "ranking member",
                  " top",
                  "foreign relations committee",
                  "intelligence committee",
                  "hopeful",
                  "house speaker",
                  "campaign"],
"US Defense" : ["pentagon",
                 "navy",
                 "air force",
                 "army",
                 "marine",
                 "coast gaurd",
                 " capt\.",
                 "captain",
                 " gen\.",
                 "general",
                 " adm\.",
                 "admiral",
                 " col\.",
                 "colonel",
                 " lt\.",
                 "lieutenant",
                 "chief of staff",
                 "joint chiefs of staff",
                 "commander",
                 "norad",
                 "northcom",
                 "special forces",
                 "strategic command",
                 "defense secretary",
                 "nato",
                 "allied",
                 "officer",
                 "corps",
                 " u\.s\.",
                 " us "],
"US Federal Officials" : ["biden|trump|obama|bush|clinton|reagan",
                        "ambassador",
                        "u\.s\. president",
                        "department",
                        "attorney",
                        "secretary of",
                        "us ambassador",
                        "state department",
                        "national security",
                        "secretary",
                        "secretary of"],
"Media" : ["author\:? ",
            "correspondent",
            "columnist",
            " post",
            " host",
            "editor",
            "times",
            "press",
            "magazine",
            "msnbc|cnn|fox",
            "writer",
            "syndicated columnist",
            "editorial",
            "blog",
            ": .+",
            "i\"m",
            "by\:? ",
            "media_tag"], 
"International Officials" : ["deputy director general",
                              "international atomic energy agency",
                              "iaea",
                              "inspector",
                              "inspections"],
"Other" : ["hezbollah",
            "taliban",
            "pollster",
            "archbishop",
            "pope",
            "bishop",
            "church",
            "rev\.",
            "reverand",
            "police",
            "commissioner",
            "nypd",
            "resident"]}



indicator_pattern_set  = [experts_ps,
                          foreign_gov_ps,
                          corporate_official_ps,
                          judicial_ps,
                          us_congress_ps,
                          us_defense_ps,
                          us_fed_officials_ps,
                          media_ps,
                          international_officials_ps,
                          other_ps]



indicator_patterns = []
for pattern_group in indicator_pattern_set:
    indicator_patterns += pattern_group
    
    

# A special indicator to try is the existence of a foreign title--that is, any case in which
# a title and a foreign cuntry are mentioned in the same string. Examples are shown below.
def has_foreign_title(context_str):
    """Inputs:
     - context_str: string to find a foreign title in
     Outputs:
     - int, whether or not a foreign title is in the string"""
    country_pattern = "iran|iraq|south korea|north korea|russia|china|france|germany|india|pakistan|libya|britain|u\.k\.|united kingdom|israel|saudi arabia"
    country_s_pattern = "(iran|iraq|south korea|north korea|russia|china|france|germany|india|pakistan|libya|britain|u\.k\.|united kingdom|israel|saudi arabia|south|north|korea).?s"
    country_adj_pattern = "iranian|iraqi|south korean|north koren|russian|chinese|french|german|indian|pakistani|libyan|british|israeli|saudi"
    title_pattern = "foreign|defense|minister|ambassador|leader|president|prince|diplomat|prime minister|spokesman|spokeswoman|gen\.|governor|chief|government"
    country_match = re.search(country_pattern, context_str)
    s_match = re.search(country_s_pattern, context_str)
    adj_match = re.search(country_adj_pattern, context_str)
    title_match = re.search(title_pattern, context_str)
    has_country = False 
    has_title = False
    if s_match or adj_match or country_match:
        has_country = True
    if title_match:
        has_title = True
    return int(has_country and has_title)



# helper function to extract full article text, useful for debugging cases where the context extraction function fails
def fulltext_of(art_id):
    """Inputs:
     - art_id: id of the article to get the full text of
     Outputs:
     - str: the article fulltext as a string"""
    just_id = GNI88[GNI88["Article ID"] == art_id]["fulltext"]
    if type(just_id.iloc[0]) == float:
        return ""
    elif len(just_id) > 0:
        return GNI88[GNI88["Article ID"] == art_id]["fulltext"].iloc[0]
    else: 
        return ""

    

# Helper function to find the context for a speaker if the context follows a prenoun pattern
# Example: "Russian president Vladimir Putin" -- useful context nouns "Russian president" precede Putin's name
def find_prenoun_pattern(name, mentions):
    """Inputs:
     - name: str, name of the speaker we're looking for context for
     - mentions: list of str, all paragraphs in the article where name has appeared
     Outputs:
     - str: the prenoun context preceding a name's mention, if it exists. If no prenoun
            context is found, return an empty string."""
    # listing pos tags we can reference
    nouns = ['NN','NNS','NNP','NNPS']
    verbs = ['VB','VBD','VBG','VBN','VBP','VBZ']
    adverbs = ['RB','RBR','RBS']
    # get last name and name length (num words in name) for reference
    
    last_name = ''
    name_len = len(name.split())
    if name_len > 0:
        last_name = name.split()[-1]
    # for each sentence in the article that name appears in:
    for mention in mentions:
        potential_verb = ""
        # tokenize the sentence and parse it to see what part of speech (pos)
        # every word in it is
        wordsList = nltk.word_tokenize(mention) # note: we're keeping stopwords
        tagged = nltk.pos_tag(wordsList)
        if len(tagged) <= 1:
            return ""
        # now we iterate through the sentence
        sentence_legend = {}
        name_idx = 0
        i = 0
        # for each word in sentence:
        for tag_pair in tagged:
            sentence_legend[i] = tag_pair
            # if we find the last name, save that word index. It'll be handy
            if tag_pair[0] == last_name:
                name_idx = i
            i += 1
      
    # using the word index of the name, go back in the sentence to find the
    # word preceding it. If that preceding word is a noun, we have a prenoun
    # pattern we should extract! (we know it's a noun because of NLTK functionality)
        if name_idx - name_len >= 0:
            preceding_word_pos = sentence_legend[name_idx-name_len][1] 
            if preceding_word_pos in nouns:
                prenoun_pattern = ".*?((?:\w+\W+){1,4})" + name
                matches = re.search(prenoun_pattern, mention)
                if matches:
                    #print(mention)
                    return matches[1]
    return ""



# hardcoded list of names that are so recognizable that they often lack context.
# we will search for them manually so as not to confuse the algorithm with noisy context
household_names = ['donald trump','barack obama', 'ayatollah ali khamenei', 
                   'vladimir putin','kim jong un', 'joe biden', 'joseph biden', 
                   'george bush', 'benjamin netanyahu', "mitt romney"]



# Beefed up context extraction function that searches for many more possible context patterns
def fancy_context(art_id, name, verbose=False):
    """Inputs:
     - art_id: int, id of the article in which name spoke a quote
     - name: str, name of the speaker to search for context for
     - verbose: bool, whether or not to print a log of what patterns
                were found
     Outputs:
     - str: relevant context that can help identify name in article art_id.
            if no patterns could be matched, this string will be NO CONTEXT FOUND.
            if name is a household name, return the name alone. We have an indicator
            to handle it later."""
    fulltext = fulltext_of(art_id)
    # standardize article fulltext and name to make searching easier
    fulltext = fulltext.lower()
    fulltext = fulltext.replace("-"," ")
    fulltext = re.sub(' \w\. ',' ', fulltext) # remove middle initials
    fulltext = fulltext.replace("'","")
    
    name = name.lower()
    name = name.replace("-", " ")
    name = name.replace("'", "")
    # initial hardcoded check for household names, since these names often don't
    # have any context and will only confuse the algorithm
    if name in household_names:
        return name
    
    last_name = name.split()[-1]
    

    # split the full text into a list of paragraphs
    paragraphs =  re.split(r"\n", fulltext)
    # find paragraphs where the name is mentioned
    mentions = []
    for paragraph in paragraphs:
        if name in paragraph:
            mentions.append(paragraph)
  
    # BEGIN PATTERN MATCHING
    #writer_pattern1 = '(author\:? |by\:? )' + name
    writer_pattern1 = '(author\:? )' + name
    #writer_pattern2 = '(\n' + name + '.{0,10}\n)'
    writer_pattern2 = name+'   \r'
    congress_pattern = '(\w{3}. ' + name + ' \([dr]{1} .+\))'
    precontext_pattern = '([,\.!?].+, )' + name
    is_pattern = name + ' (is .+[,\.!?])'
    postcontext_pattern = name + '(,.+[,\.!?])'
    catchall_pattern = '(\W+(?:\w+\W+){0,6}' + name + '\W+(?:\w+\W+){0,12})'
    context = ""

    # try writer pattern (E: 'By: Johnny Harris')
    for mention in mentions:
        matches = re.search(writer_pattern1, mention)
        if matches:
            context = matches[1]
            break
        matches = re.search(writer_pattern2, mention)
        if matches:
            context = "media_tag"
            break
    if context:
        if verbose:
            print("WRITER PATTERN")
        return context


  # try congress pattern (E: 'sen. John McCain (r ariz.))
    for mention in mentions:
        matches = re.search(congress_pattern, mention)
        if matches:
            context += matches[1]
        if context:
            if verbose:
                print("CONGRESS PATTERN")
            return context

  # try prenoun pattern (E: 'Press secretary Jen Psaki')
    prenoun_result = find_prenoun_pattern(name, mentions)
    if prenoun_result:
        if verbose:
            print("PRENOUN PATTERN")
        return prenoun_result

  # try precontext patterns (E: 'Director of international affairs, Rob Black')
    for mention in mentions:
        matches = re.search(precontext_pattern, mention)
        if matches:
              context += matches[1]
    if context:
        if verbose:
            print("PRECONTEXT PATTERN")
        return context

  # try is pattern (E: 'Ezra Klein is a writer for the New York Times')
    for mention in mentions:
        matches = re.search(is_pattern, mention)
        if matches:
            context += matches[1]
    if context:
        if verbose:
            print("IS PATTERN")
        return context

  # try postcontext pattern (E: 'Daniel Chung, a researcher for ReThink media, ...')
    for mention in mentions:
        matches = re.search(postcontext_pattern, mention)
        if matches:
            context += matches[1]
    if context:
        if verbose:
            print("POSTCONTEXT PATTERN")
        return context

  # if all else fails, extract the first few words both preceding and trailing mentions
  # of name in the article. A less surgical extraction, but still an extraction.
    for mention in mentions:
        matches = re.search(catchall_pattern, mention)
        if matches:
            context += matches[1]
            break
    if context:
        if verbose:
            print("CATCHALL FOR " + str(art_id) + ", " + name)
        return context

  # if all else REALLY fails, run the whole function again with just the speaker's
  # last name, since sometimes they are mentioned as "Mr. last_name" or "Mrs. last_name"
    if len(name.split()) > 1:
        return fancy_context(art_id, last_name)
    else:
        context = "# NO CONTEXT FOUND #"
        if verbose:
            print("NO PATTERN FOUND FOR " + str(art_id) + ", " + name)
        return context
    
    
    
def extract_indicators(context_str, indicator_patterns):
    """Inputs:
     - context_str: str, the article fulltext to extract indicator features from
     - indicator_patterns: list, all the patterns to be turned into indicators
     Outputs:
     - array of indicators in the order of indicator_patterns, where a 1 indicates
       that the corresponding pattern from indicator_patterns is present in 
       context_str"""

    # initialize a vector of length len(indicator_patterns)
    feat_vector = np.zeros(len(indicator_patterns))
    # for each pattern in indicator_patterns:
    i = 0
    for pattern in indicator_patterns:
        # search for the pattern in context_str
        match = re.findall(pattern, context_str)
        # if it's there, make that entry in the vector a 1
        # otherwise, leave it a 0
        if match:
            feat_vector[i] = 1
        i += 1
    # return the vector, that's our feature data
    return feat_vector



def extract_speaker_indicators(context_str, speaker_dict):
    """Inputs:
     - context_str: str, the article fulltext to extract indicator features from
     - speaker_dict: dictionary, with keys being speaker types and values being a list of indicator patterns
     Outputs:
     - array of indicators in the order of speaker_dict.keys(), where the number indicates
       the number of indicator patterns that were present in 
       context_str"""

    # initialize a vector of length len(speaker_dict.keys())
    feat_vector = np.zeros(len(speaker_dict.keys()))
    # i keeps track of index in feat_vector
    i = 0
    for speaker_type in speaker_dict.keys():
        count = 0
        for indicator in speaker_dict[speaker_type]:
        # search for the pattern in context_str
            match = re.findall(indicator, context_str)
            if match:
                count += 1
        # if it's there, make that entry in the vector a 1
        # otherwise, leave it a 0
        feat_vector[i] = count
        i += 1
    # return the vector, that's our feature data
    return feat_vector



household_indicators = ['biden|trump|obama|bush|clinton|reagan', 'putin|kim jong un|netanyahu|ayatollah|moon jae in']



def extract_speaker_indicators_binary(context_str, speaker_dict):
    """Inputs:
     - context_str: str, the article fulltext to extract indicator features from
     - speaker_dict: dictionary, with keys being speaker types and values being a list of indicator patterns
     Outputs:
     - array of indicators in the order of speaker_dict.keys(), where a 1 indicates
       that the one or more indicator patterns for that speaker class were present in 
       context_str"""

    # initialize a vector of length len(speaker_dict.keys())
    feat_vector = np.zeros(len(speaker_dict.keys()))
    # i keeps track of index in feat_vector
    i = 0
    for speaker_type in speaker_dict.keys():
        indicator_present = 0
        for indicator in speaker_dict[speaker_type]:
        # search for the pattern in context_str
            match = re.findall(indicator, context_str)
            if match:
                if indicator in household_indicators:
                    feat_vector = np.zeros(len(speaker_dict.keys()))
                    feat_vector[i] = 1
                    return feat_vector
                    
                indicator_present = 1
        # if it's there, make that entry in the vector a 1
        # otherwise, leave it a 0
        
        feat_vector[i] = indicator_present
        i += 1
    # return the vector, that's our feature data
    return feat_vector