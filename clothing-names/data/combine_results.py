import os

targets = ['ssense_result.txt', 'ssense1_result.txt', 'ssense2_result.txt', 'ssense3_result.txt', 'ssense4_result.txt']
renamed = 'ssense_results_combined.txt'

curr_dir = os.getcwd()

results = []
for tar in targets:
    with open(os.path.join(curr_dir, tar), 'r') as f:
        for line in f.readlines():
            if line not in results:
                results.append(line)

with open(os.path.join(curr_dir, renamed), 'w') as f:
    for line in results:
        f.write(line)
