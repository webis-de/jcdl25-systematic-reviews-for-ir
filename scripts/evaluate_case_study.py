# This file calculates the metrics
total_relevants = 30

def print_metrics(total, relevants, total_relevants):
    print(f'#Retrieved: {total}')
    print(f'#Relevant: {relevants}')
    recall = relevants/total_relevants
    precision = relevants/total
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')
    print(f'F1: {2*((precision*recall)/(precision+recall))}')
    print(f'F3: {(((1+3**2)*precision*recall)/((3**2 * precision)+recall))}\n')

def get_total_retrieved_and_relevants_from_file(f):
    total = 0
    relevants = 0
    while True:
        line = f.readline()
        if not line or line.startswith('#'):
            break
        if line.startswith('R') and not line.startswith('Results'):
            total += 1
            relevants += 1
        if line.startswith('N'):
            total += 1
    return total, relevants


# Read in evaluation file
f = open("./case-study/evaluation-notes.txt", 'r', encoding='utf-8')
while True:
    line = f.readline()
    if line.startswith('-'):
        break


print('Results for the query from the systematic review paper:')
total, relevants = get_total_retrieved_and_relevants_from_file(f)
print_metrics(total, relevants, total_relevants)

print('Results for the Single Prompt LLM-generated query:')
total, relevants = get_total_retrieved_and_relevants_from_file(f)
print_metrics(total, relevants, total_relevants)


print('Results for the Multi-Step LLM-generated query:')
total, relevants = get_total_retrieved_and_relevants_from_file(f)
print_metrics(total, relevants, total_relevants)

f.close()
