# Text Similarity Analysis by Matthew Keeran
# runs via python textanalysis.py 
# I personally pipe the output to a text file, then enter the file names one by one followed by enter.	python textanalysis.py > output.txt
# written in python 3.5.4 on Windows 8.1, produces all desired output all in correct format.		shake-src.txt
# tested with python 3.6 on Ubuntu 16, produces all desired output all in correct format.		shake-tgt.txt

#--------------------------------------------------------------------------------------------------------------------------------#
def readtokens(f):
	f = open(f, 'r')
	tokens = []
	for line in f:
		words = line.split()
		for i in range(len(words)):
			tokens.append(words[i])
	
	return tokens
#--------------------------------------------------------------------------------------------------------------------------------#
def normalize(l):
	normed = []
	for i in range(len(l)):
		token = l[i].lower()																							# lowercase
		alnum, nalnum, index, flag = "", "", -1, 0
		
		if(not(token[0].isalnum())):																					# non alphanumeric prefix
			nalnum += token[0]
			for j in range(1,len(token)):
				if(not(token[j].isalnum()) and not(token[j - 1].isalnum())):
					nalnum += token[j]
				else:
					alnum += token[j]
			
			normed.append(nalnum)
		
		else:
			alnum = token
		
		if(len(alnum) > 0 and not(alnum[len(alnum) - 1].isalnum())):													# non alpha numeric suffix
			nalnum, newalnum = "", ""
			nalnum += alnum[len(alnum) - 1]
			
			for j in range(2,len(alnum)):
				if(not(alnum[len(alnum) - j].isalnum()) and not(alnum[len(alnum) - j + 1].isalnum())):
					nalnum += alnum[len(alnum) - j]
				else:
					newalnum += alnum[len(alnum) - j]
			
			newalnum += alnum[0]
			nalnum, alnum = nalnum[::-1], newalnum[::-1]
			index = 1
				
		if(len(alnum) > 1 and alnum[len(alnum) - 2] == '\'' and alnum[len(alnum) - 1] == 's'):
			s = alnum[:(len(alnum) - 2)]
			normed.append(s)
			normed.append('\'s')
			flag = 1
			
		elif(len(alnum) > 2 and alnum[len(alnum) - 3] == 'n' and alnum[len(alnum) - 2] == '\'' and alnum[len(alnum) - 1] == 't'):
			s = alnum[:(len(alnum) - 3)]
			normed.append(s)
			normed.append('not')
			flag = 1
		
		elif(len(alnum) > 1 and alnum[len(alnum) - 2] == '\'' and alnum[len(alnum) - 1] == 'm'):
			s = ""
			for j in range(len(alnum) - 2):
				s += alnum[j]
			normed.append(s)
			normed.append('am')
			flag = 1
		
		if(index > 0 and flag == 0):																# if non alphanumeric suffix and not special case
			normed.append(alnum)
			[normed.append(nalnum[i]) for i in range(len(nalnum))]
		elif(index > 0 and flag != 0):																# if non alphanumeric suffix and special case
			normed.append(nalnum)
		
		if(flag == 0 and index == -1 and len(alnum) > 0):											# none of the above
			normed.append(alnum)
	
	return normed
#--------------------------------------------------------------------------------------------------------------------------------#	
def editdistance(s,t):
	maxim = float("-inf")
	for i in range(1, len(s) + 1):
		for j in range(1, len(t) + 1):
			delete = edits[i-1][j] - 1
			insert = edits[i][j-1] - 1
			match = edits[i-1][j-1] + (2 if(s[i-1] == t[j-1]) else -1)								# or substitution
			back = ""
			edits[i][j] = max(0, insert, delete, match)
			if(edits[i][j] > maxim):
				maxim = edits[i][j]
			
			if(edits[i][j] == delete and delete != 0):
				back = "UP"
			elif(edits[i][j] == insert and insert != 0):
				back = "LT"
			elif(edits[i][j] == match and match != 0):
				back = "DI"
				
			backtrace[i][j] = back
			
	[index.append([i,j]) for i in range(n+1) for j in range(m+1) if edits[i][j] == maxim]
	
	return maxim	
#--------------------------------------------------------------------------------------------------------------------------------#
def alignments(tokens1, tokens2, edits, backtrace, index):
	for i in range(len(tokens2)):
		if(len(tokens2[i]) < 4):
			tokens2[i] = tokens2[i] + "   "
	
	for i in range(len(index)):
		actions.append([])
		source.append([])
		target.append([])
		while(backtrace[index[i][0]][index[i][1]] != ""):
			if(backtrace[index[i][0]][index[i][1]] == "DI"):
				if(tokens1[index[i][0] - 1] == tokens2[index[i][1] - 1]):
					if(len(tokens1[index[i][0] - 1]) < 8 and len(tokens2[index[i][1] - 1]) < 8):
						actions[i].insert(0, "    ")
						source[i].insert(0, tokens1[index[i][0] - 1])
						target[i].insert(0, tokens2[index[i][1] - 1])
						
					elif(len(tokens1[index[i][0] - 1]) > 7 and len(tokens2[index[i][1] - 1]) < 8):
						actions[i].insert(0,"        ")
						source[i].insert(0, tokens1[index[i][0] - 1])
						target[i].insert(0, tokens2[index[i][1] - 1] + "\t")
					elif(len(tokens2[index[i][1] - 1]) > 7 and len(tokens1[index[i][0] - 1]) < 8):
						actions[i].insert(0,"        ")
						source[i].insert(0, tokens1[index[i][0] - 1] + "\t")
						target[i].insert(0, tokens2[index[i][1] - 1])
					elif(len(tokens2[index[i][1] - 1]) > 7 and len(tokens1[index[i][0] - 1]) > 7):
						actions[i].insert(0,"        ")
						source[i].insert(0, tokens1[index[i][0] - 1])
						target[i].insert(0, tokens2[index[i][1] - 1])
						
				else:
					if(len(tokens1[index[i][0] - 1]) > 7 and len(tokens2[index[i][1] - 1]) < 8):
						actions[i].insert(0, " s  \t")
						source[i].insert(0, tokens1[index[i][0] - 1])
						target[i].insert(0, tokens2[index[i][1] - 1] + "\t")
					elif(len(tokens2[index[i][1] - 1]) > 7 and len(tokens1[index[i][0] - 1]) < 8):
						actions[i].insert(0, " s  \t")
						source[i].insert(0, tokens1[index[i][0] - 1] + "\t")
						target[i].insert(0, tokens2[index[i][1] - 1])
					elif(len(tokens2[index[i][1] - 1]) > 7 and len(tokens1[index[i][0] - 1]) > 7):
						actions[i].insert(0, " s  \t")
						source[i].insert(0, tokens1[index[i][0] - 1])
						target[i].insert(0, tokens2[index[i][1] - 1])
					else:
						actions[i].insert(0, " s  ")
						source[i].insert(0, tokens1[index[i][0]- 1])
						target[i].insert(0, tokens2[index[i][1]- 1])
				index[i][0] -= 1
				index[i][1] -= 1
			
			elif(backtrace[index[i][0]][index[i][1]] == "UP"):
				if(len(tokens1[index[i][0] - 1]) < 8):
					actions[i].insert(0, " d  ")
					target[i].insert(0, " -  ")
					source[i].insert(0, tokens1[index[i][0] - 1])
				elif(len(tokens1[index[i][0] - 1]) > 7):
					actions[i].insert(0, " d  \t")
					source[i].insert(0, tokens1[index[i][0] - 1])
					target[i].insert(0, " -  \t")					
				index[i][0] -= 1
			
			elif(backtrace[index[i][0]][index[i][1]] == "LT"):
				if(len(tokens2[index[i][1] - 1]) < 8):
					actions[i].insert(0, " i  ")
					target[i].insert(0, tokens2[index[i][1]- 1])
					source[i].insert(0, " -  ")
				elif(len(tokens2[index[i][1] - 1]) > 7):
					actions[i].insert(0, " i  \t")
					source[i].insert(0, " -  \t")
					target[i].insert(0, tokens2[index[i][1] - 1])	
				index[i][1] -= 1
#--------------------------------------------------------------------------------------------------------------------------------#				

if __name__ == "__main__":
	f1 = input("\nPlease enter the name of the source file:\n").strip()
	f2 = input("\nPlease enter the name of the target file:\n").strip()
	print("--------------------------------------------------------------------------------------------------------------------------------------------")
	
	print("\nSource file: " + f1)
	print("Target file: " + f2)
	tokens1, tokens2 = readtokens(f1), readtokens(f2)
	
	print("\nRaw Tokens:")
	print("\tSource > " + " ".join(tokens1))
	print("\tTarget > " + " ".join(tokens2))
	
	tokens1, tokens2 = normalize(tokens1), normalize(tokens2)
	
	print("\nNormalized Tokens:")
	print("\tSource > " + " ".join(tokens1))
	print("\tTarget > " + " ".join(tokens2))
	
	print("\n--------------------------------------------------------------------------------------------------------------------------------------------")
	
	n, m = len(tokens1), len(tokens2)
	edits, backtrace = [], []
	for i in range(n+2):
		row1, row2 = [], []
		for j in range(m+2):
			row1.append(0)
			row2.append("")
		edits.append(row1)
		backtrace.append(row2)
	
	
	index = []
	maxim = editdistance(tokens1,tokens2)
	
	print("\nEdit Distance Table:")
	print("\t\t" + "\t".join([str(x) for x in range(m+1)]))
	print("\t\t#\t" + "\t".join([tokens2[x][:3] for x in range(len(tokens2))]))
	for i in range(n + 1):
		if(i == 0):
			print(str(i) + "\t# \t" + "\t".join([str(edits[i][j]) for j in range(m + 1)]))
		else:
			if(len(tokens1[i-1]) < 4):
				tokens1[i-1] = tokens1[i-1] + "   "
			print(str(i) + "\t" + tokens1[i-1][:3] + "\t" + "\t".join([str(edits[i][j]) for j in range(m + 1)]))
	
	print("\n--------------------------------------------------------------------------------------------------------------------------------------------")
	
	print("\nBacktrace Table:")
	print("\t\t" + "\t".join([str(x) for x in range(m+1)]))
	print("\t\t#\t" + "\t".join([tokens2[x][:3] for x in range(len(tokens2))]))
	for i in range(n + 1):
		if(i == 0):
			print(str(i) + "\t# \t" + "\t".join([backtrace[i][j] for j in range(m + 1)]))
		else:
			if(len(tokens1[i-1]) < 4):
				tokens1[i-1] += "   "
			print(str(i) + "\t" + tokens1[i-1][:3] + "\t" + "\t".join([backtrace[i][j] for j in range(m + 1)]))
	
	print("\n--------------------------------------------------------------------------------------------------------------------------------------------")
	
	print("\nMaximum value in the distance table: " + str(maxim))
	print("\nMaxima:\n\t" + str(index))
	print("\nMaximal-similarity alignments:\n\t")
	
	actions, source, target = [], [], []
	alignments(tokens1,tokens2,edits,backtrace,index)
	
	for i in range(len(index)):
		print("\tAlignment " + str(i) + " (length " + str(len(actions[i])) + "):")
		print("\t\tSource at\t" + str(index[i][0]) + ":\t" + "\t".join(source[i]))
		print("\t\tTarget at\t" + str(index[i][1]) + ":\t" + "\t".join(target[i]))
		print("\t\tEdit action\t :\t" + "\t".join(actions[i]) + "\n\n")
	
	print("\n--------------------------------------------------------------------------------------------------------------------------------------------\n")
	
