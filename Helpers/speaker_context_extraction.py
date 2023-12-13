# Credit: Daniel Chung

#----

# helper function to extract full article text, useful for debugging cases where the context extraction function fails
def content_of(art_id):
  """Inputs:
     - art_id: id of the article to get the full text of
     Outputs:
     - str: the full article content as a string"""
  just_id = arts[arts["Article ID"] == art_id]["Content"]
  if len(just_id) > 0:
    return arts[arts["Article ID"] == art_id]["Content"].iloc[0]
  else: 
    return ""

#----

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
  last_name = name.split()[-1]
  name_len = len(name.split())
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

#----

# hardcoded list of names that are so recognizable that they often lack context.
# we will search for them manually so as not to confuse the algorithm with noisy context
household_names = ['donald trump','barack obama','ayatollah ali khameni',
                   'vladimir putin','kim jong un', 'joe biden', 'joseph biden', 
                   'george bush', 'benjamin netanyahu', "mitt romney"]

#----

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
  content = content_of(art_id)
  # standardize article content and name to make searching easier
  content = content.lower()
  content = content.replace("-"," ")
  content = re.sub(' \w\. ',' ',content) # remove middle initials
  content = content.replace("'","")
  name = name.lower()
  name = name.replace("-", " ")
  name = name.replace("'", "")
  # initial hardcoded check for household names, since these names often don't
  # have any context and will only confuse the algorithm
  if name in household_names:
    if verbose:
      print("HOUSEHOLD NAME PATTERN")
    return name
  last_name = name.split()[-1]

  # split the full text into a list of paragraphs
  paragraphs =  re.split(r"\n", content)
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
    if verbose:
      print("RERAN CONTEXT EXTRACTION ON LAST NAME")
    return fancy_context(art_id, last_name)
  else:
    context = "# NO CONTEXT FOUND #"
    if verbose:
      print("NO PATTERN FOUND FOR " + str(art_id) + ", " + name)
    return context