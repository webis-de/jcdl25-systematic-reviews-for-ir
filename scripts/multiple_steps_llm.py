import ollama


# First construct sub-topics
topic = 'Fairness, Accountability, Transparency and Ethics in Information Retrieval'
prompt = f'You are an information specialist who develops Boolean queries for systematic reviews. \
    You have extensive experience developing highly effective queries for searching information retrieval literature. \
    Your specialty is developing queries that retrieve as few irrelevant documents as possible and retrieve all relevant documents \
    for your information need. \
    Now you have your information need to conduct research on the topic of {topic}. \
    First, please disassemble the topic into multiple relevant subtopics and return a list of these sub-topics. \
    Do not answer with anything else than the list of sub-topics (like explanations)!'
response = ollama.generate(model='gemma2:2b', prompt=prompt)
print(response['response'])
sub_topics = response['response']

# Then construct lists of synonyms of the returned sub-topics
prompt = f'You are an information specialist who develops Boolean queries for systematic reviews. \
    You have extensive experience developing highly effective queries for searching information retrieval literature. \
    Your specialty is developing queries that retrieve as few irrelevant documents as possible and retrieve all relevant documents \
    for your information need. \
    Now you have your information need to conduct research on the topic of {topic}. \
    Given is a list of sub-topics for this topic: {sub_topics}. \
    Please find relevant synonyms for each of these sub-topics and return them as a list. \
    Do not answer with anything else than the list of synonyms for each sub-topic (like explanations)!'
response = ollama.generate(model='gemma2:2b', prompt=prompt)
print(response['response'])
synonyms = response['response']

# Construct a first boolean query with these synonyms
prompt = f'You are an information specialist who develops Boolean queries for systematic reviews. \
    You have extensive experience developing highly effective queries for searching information retrieval literature. \
    Your specialty is developing queries that retrieve as few irrelevant documents as possible and retrieve all relevant documents \
    for your information need. \
    Now you have your information need to conduct research on the topic of {topic}. \
    Given is a list of sub-topics with corresponding synonyms for this topic: {synonyms}. \
    Please construct a highly effective systematic review Boolean query that can best serve your information need and that uses the given list of synonyms. \
    The Boolean query should be designed for the IR Anthology, a collection containing all papers related to information retrieval research. \
    The IR Anthology contains the following searchable index fields: full_text (standard searched field), year, title, author, editor, doi. \
    Do not answer with anything else than the Boolean query (like explanations)!'
response = ollama.generate(model='gemma2:2b', prompt=prompt)
print(response['response'])
query = response['response']
