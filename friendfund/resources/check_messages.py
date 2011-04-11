import os, re

FOLDERS = [".", "../messages_de_de", "../messages_es_es"]
NAMES = re.compile("\['([^']+)'\]")


superset = set()
results = {}
for name in os.listdir("."):
	if name[-4:] == ".txt":
		for folder in FOLDERS:
			subname = os.path.join(folder, name)
			try:
				f = open(name, "r")
				content = f.read()
				f.close()
				results[folder] = set(re.findall(NAMES, content))
				superset = superset.union(results[folder])
			except Exception, e:
				print "MISSING", subname, e
		
		print "SUPERSET", name, '='*100
		print sorted(results[FOLDERS[0]])
		for folder in FOLDERS[1:]:
			if results.get(folder):
				missing = results[FOLDERS[0]] - results[folder]
				additional =  results[folder] - results[FOLDERS[0]]
				if not (missing or additional):
					print folder, "ALLOK"
				else:
					print "SUBSET", folder, '-'*40
				if missing:
					print "m:", missing
				if additional:
					print "a:", additional
			


print "="*120
print sorted(superset)