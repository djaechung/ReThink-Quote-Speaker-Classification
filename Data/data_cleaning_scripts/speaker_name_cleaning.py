# Credit: Lana Elauria

def remove_prefix(text):
    for prefix in prefixes:
      if text.lower().startswith(prefix):
        slicer = len(prefix)
        return text[slicer:]
    return text

def remove_suffix(text):
    for suffix in suffixes:
      if text.endswith(suffix):
        slicer = len(suffix)
        return text[:-slicer]
    return text

def regex_trim(rx_list, column, df, replace_value=""):
    '''Takes a list of regex patterns, and joins the patterns with an OR (|) separator. 
    Searches the specified column/df for the pattern and replaces it with value specified (default value-nothing)'''
    df[column] = df[column].replace(to_replace="|".join(rx_list), value=replace_value, regex=True)
    return df

def remove_accents(txt):
    """Certain outlets (CTV News) do not use accented characters in person names.
       Others (CBC News and Global news), always use accented characters in names.
       To help normalize these names and get accurate counts of sources, we replace 
       accented characters with their regular English equivalents.
       Example names that are normalized across different outlets using this method:
        * François Legault <-> Francois Legault
        * Valérie Plante <-> Valerie Plante
        * Jean Chrétien <-> Jean Chretien 
    """
    txt = re.sub("[àáâãäå]", 'a', txt)
    txt = re.sub("[èéêë]", 'e', txt)
    txt = re.sub("[ìíîïı]", 'i', txt)
    txt = re.sub("[òóôõö]", 'o', txt)
    txt = re.sub("[ùúûü]", 'u', txt)
    txt = re.sub("[ýÿ]", 'y', txt)
    txt = re.sub("ç", 'c', txt)
    txt = re.sub("ğ", 'g', txt)
    txt = re.sub("ñ", 'n', txt)
    txt = re.sub("ş", 's', txt)

    # Capitals
    txt = re.sub("[ÀÁÂÃÄÅ]", 'A', txt)
    txt = re.sub("[ÈÉÊË]", 'E', txt)
    txt = re.sub("[ÌÍÎÏİ]", 'I', txt)
    txt = re.sub("[ÒÓÔÕÖ]", 'O', txt)
    txt = re.sub("[ÙÚÛÜ]", 'U', txt)
    txt = re.sub("[ÝŸ]", 'Y', txt)
    txt = re.sub("Ç", 'C', txt)
    txt = re.sub("Ğ", 'G', txt)
    txt = re.sub("Ñ", 'N', txt)
    txt = re.sub("Ş", 'S', txt)
    return txt

def remove_titles(txt):
    """Method to clean special titles that appear as prefixes or suffixes to
       people's names (common especially in articles from British/European sources).
       The words that are marked as titles are chosen such that they can never appear
       in any form as a person's name (e.g., "Mr", "MBE" or "Headteacher").
    """
    honorifics = ["Dr", "Sir", "Dame", "Professor", "Prof", "Rev"]
    titles = ["QC", "CBE", "MBE", "BM", "MD", "DM", "BHB", "CBC", "Rep", "Rep.",
              "Reverend", "Recorder", "Headteacher", "Councillor", "Cllr", "Father", "Fr",
              "Mother", "Grandmother", "Grandfather", "Creator", "U.S. Rep", "Senator", "Sen", "Rabbi", "Imam"] # could add "Judge" but that could also be someone's name
    extras = ["et al", "www", "href", "http", "https", "Ref"]
    banned_words = r'|'.join(honorifics + titles + extras)
    # Ensure only whole words are replaced (\b is word boundary)
    pattern = re.compile(r'\b({})\b'.format(banned_words)) 
    txt = pattern.sub('', txt)
    txt = re.sub("^\.","",txt)
    return txt.strip()

def lnfn_parse(txt):
    """Converts names with "Last, First" pattern to "First Last" pattern.
       Works with multiple "Last, First" names, returns "First Last, First Last, ..."
    """
    lnfn_split = txt.split(", ")
    fnln_split = lnfn_split[::-1]
    fnln = ", ".join([" ".join(x) for x in zip(fnln_split[0::2], fnln_split[1::2])])
    return fnln

#looks for phone number and optional leading spaces/punctuation
phonenum_regex = '((?: |, |; |\. |\| )?\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}(?: |, |; |\. |\| )?)'
#looks for email address and optional leading spaces/punctuation
email_regex = "((?: |, |; |\. |\| )?[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?: |, |; |\. |\| )?)"
#looks for title words (case insensitive) and optional leading spaces/punctuation
title_regex = '((?: |, |; |\. |\| | - )?(?i)(?:Staff Writers?|Editor\-in\-Chief|Managing Editor|Political Editor|Editor\-at\-large|Columnist|Correspondent|Opinion contributors?|special.*|Capital Bureau)(?: |, |; |\. |\| )?)'
#capture -, anything after | 
symbol_regex = ' -|\|.*$'
#capture firstname.lastinitial pattern at end of AJC bylines, "; .. is . ." pattern with bios 
specialpatterns_regex = "(?: \w{4,}\.\w$)|(?i); .*(?:\.$| is.*)"
#capture non-name entries including anything after 'from,' and anything containing 'editorial', 'readers', or 'editors' 
non_name_regex = ".*(?:staff$|staff ).*|Letters to the Editor|from.*|(?i).*editorial.*|(?i).*editors.*|No by-line,|(?i).*readers.*"
#look for news outlets, case insensitive, including optional leading 'the'/connectors/punctuation
#For CNN captures anything that comes after
outlet_regex = '(?i)(?:, |; | and | for | ?The )?(?i)(?:CNN.*$|Associated Press|New York Times|Washington Times|USA Today|AJC|Green Bay Press-Gazette|Daily Beast|Nation|Houston Chronicle|Sarasota Herald-Tribune|Augusta Chronicle|Arizona Republic|Texas Tribune|Chicago Tribune)'
#capture non-comma connectors ('and', ';and', ';', '\n', '&')
connector_regex = '((?i)(?: ;and | and |; *|\\n * | & *))'
#capture double comma patterns
dbl_comma_regex = ', *,+ *'
#capture last name, first name pattern
# edited to capture names with punctuation (ie. hyphenated names, or names with middle initial)
lnfn_regex = "(^(?:[\w\.\'-])*, (?:[\w\.\'-])*|(?:[\w\.\'-] [\w\.])*$)"
#looks for "The" preceded and followed by a space, with optional leading comma
the_regex = ',? The .*'
#looks for "The" preceded and followed by a space, with optional leading comma
start_the_regex = '^The .*'

rx_patterns = [phonenum_regex,
               email_regex,
               title_regex, 
               symbol_regex, 
               specialpatterns_regex, 
               outlet_regex, 
               non_name_regex,
               the_regex,
               start_the_regex]

state_list = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District ", "of Columbia", 
              "Delaware", "Florida", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", 
              "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", 
              "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", 
              "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virgin Islands", "Vermont", "Wisconsin", 
              "West Virginia", "Wyoming"]

#Patterns of non-name Source Name entries
notname_regex = r"unnamed|editorial|\bthe\b|\bof\b|opponents|election|vote|liberal |conservatives?| for |documents?|expert|citizens|research|voting|financial|journal|reuters|cnn|bulletin| and |newswire| memo|\bpoll\b|spokesperson|[0-9]|\busa\b"
org_regex= "statement|committee|institute|report|groups?|association|university|college|center|coalition|advocate|national|league|associated|american|daily"
govt_regex = "^gop |federal|u\.s\.|supreme court|officials?|administration|department|office|congress|campaign|census|white house|democrat|republican|senate |registrar|secretary|commission|agency|us police|government"
court_regex = "appeals|circuit|lawyer|attorney|records|\bcourts?\b|lawsuit"
long_regex = "\S+\s\S+\s\S+\s\S+\s\S+"

#Look for strings that do not contain this
short_regex = "\S+\s+\S+"

# regex for one-letter first names
one_letter_regex = "^(\w\.)\W(\w+)"

notname_regex_list = [notname_regex, org_regex, govt_regex, court_regex, long_regex]

test_strings = ['Mark', 'By Mark', 'No by-line', 'Opinion by Mark', 'Analysis by Mark']

#for test in df.head()['author']:
#  print(author_cleaning(test))

prefixes = ['letter to the editor by ', 'by ', 'opinion by ', 'analysis by ', 'compiled by ', 'por ']

suffixes = [';Editor', ' Florida Times-Union', ' Jacksonville Florida Times-Union', ' Milwaukee Journal Sentinel',
            ' Capitol Media Services', ' -- Times Staff Writer', 'Appleton Post-Crescent',  
            '; Richmond Times-Dispatch', ' SUN STAFF WRITER', ' News Service Of Florida',
            ', Palm Beach Post', '; Editor', '; WPR NEWS', 
            ' Richmond Times-Dispatch', ' -- Times/Herald Tallahassee Bureau', ', RealClearWire', 
            '  -- Times Political Editor', '; Austin Bureau', ' Tribune News Service', ' Guest Columnist', 
            '; LA CROSSE TRIBUNE', ', Omaha World-Herald', ' USA TODAY NETWORK',  
            ' InsideSources.com', ' Yuma Sun Editor', ', Capitol Beat News Service', ' South Florida Sun Sentinel',
            ' Orlando Sentinel', '; Murphy teaches writing at Virginia Tech', " Washington Bureau", '; Contributing Writer', '  -- Times/Herald',  
            ' Capitol Beat News Service', ' -- PolitiFact', '; Now News Group', ' Tribune Content Agency', 
            '; WISCONSIN STATE JOURNAL', '; Washington Bureau Chief', ' The Heritage Foundation',
            ', Associated Press; The New York Times contributed.', ', Los Angeles Times', ' Atlanta Journal-Constitution', 
            ' of Capital News Service', 'Por']


################################################################### 
# How to apply name-cleaning functions to a df 
################################################################### 


# Drop "OLD" labels from name strings
qtes["Source Name"] = qtes["Source Name"].str.split(" OLD", expand =True)[0]
qtes["Source Name"] = qtes["Source Name"].str.split(r" \(OLD\)", expand =True)[0]

#Remove any names labelled "Organization"
qtes['cleaned_name'] = np.where(qtes['Source Gender'] == "Organization", "not_name", qtes['Source Name']) 

#Fill empty cells
qtes["cleaned_name"] = qtes["Source Name"].replace(np.nan, "none").apply(remove_prefix).apply(remove_suffix).str.title()

# replace " , " with ", " to fix some HuffPost author formats
qtes["cleaned_name"] = qtes["cleaned_name"].replace(" , ", ", ")

# removing stray "Por" prefixes
qtes["cleaned_name"] = qtes["cleaned_name"].replace("Por ", "")

#Remove rx pattern matches
qtes = regex_trim(rx_patterns, column="cleaned_name", df=qtes)

#find non-comma connectors and convert to comma
qtes = regex_trim([connector_regex], "cleaned_name", df=qtes, replace_value=", ")

#after comma conversion, check for multiple commas together and convert to single comma
qtes = regex_trim([dbl_comma_regex], "cleaned_name", df=qtes, replace_value=", ")

#strip trailing commas, and leading and trailing whitespace, then check for trailing commas again
qtes['cleaned_name'] = qtes['cleaned_name'].str.rstrip(",").str.strip().str.rstrip(",")

#Format names with last name, first name pattern
qtes['cleaned_name'] = np.where(qtes['cleaned_name'].str.match(lnfn_regex), 
                                  qtes['cleaned_name'].apply(lnfn_parse),
                                  qtes['cleaned_name'])

#Re-run searches to strip out names starting with 'The'
qtes = regex_trim([the_regex, start_the_regex], "cleaned_name", df=qtes)

#Remove accents and titles
qtes['cleaned_name'] = qtes['cleaned_name'].apply(remove_accents).apply(remove_titles)

#Remove non-name regex matches
qtes['cleaned_name'] = np.where(qtes['cleaned_name'].str.lower().str.contains(
    "|".join(notname_regex_list), regex=True), 
    "not_name", qtes['cleaned_name'])

#Remove state matches
qtes['cleaned_name'] = np.where(qtes['cleaned_name'].str.contains("|".join(state_list), regex=True), 
                                  "not_name", qtes['cleaned_name']) 

#Remove one word names
qtes['cleaned_name'] = np.where(qtes['cleaned_name'].str.contains(short_regex, regex=True), 
                                  qtes['cleaned_name'], "not_name")

# remove one letter (abbreviated) first names
qtes['cleaned_name'] = np.where(qtes['cleaned_name'].str.contains(one_letter_regex, regex=True),
                                  "not_name", qtes['cleaned_name'])