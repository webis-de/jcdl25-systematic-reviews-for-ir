import ollama


topic = 'Fairness, Accountability, Transparency and Ethics in Information Retrieval'
prompt = f'You are an information specialist who develops Boolean queries for systematic reviews. \
    You have extensive experience developing highly effective queries for searching information retrieval literature. \
    Your specialty is developing queries that retrieve as few irrelevant documents as possible and retrieve all relevant documents \
    for your information need. \
    Now you have your information need to conduct research on the topic of {topic}. \
    Please construct a highly effective systematic review Boolean query that can best serve your information need. \
    The Boolean query should be designed for the IR Anthology, a collection containing all papers related to information retrieval research. \
    Do not answer with anything else than the Boolean query (like explanations)!'
response = ollama.generate(model='gemma2:2b', prompt=prompt)
print(response['response'])
