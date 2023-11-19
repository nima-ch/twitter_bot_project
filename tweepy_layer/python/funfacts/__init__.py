fun_facts = []
with open('/opt/python/funfacts/fun_facts.txt', 'r') as file:
   for line in file:
       fun_facts.append(line.strip())
