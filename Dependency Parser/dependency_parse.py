# Viterbi Part-of-Speech Tagger by Matthew Keeran
# runs via python textanalysis.py 
# I personally pipe the output to a text file, then enter the file names one by one followed by enter.	python dependency_parser.py > output.txt
# written in python 3.5.4 on Windows 8.1.															piper.txt
# tested with python 3.6 on Ubuntu 16

import time

leftarccounts, rightarccounts = {}, {}														# global arc arrays for oracle to use

#--------------------------------------------------------------------------------------------------------------------------------#
def readtokens(f):
	wordtags = []
	f = open(f, 'r')
	for line in f:
		line = line.split('/')
		wordtags.append((line[0],line[1].strip('\n')))
	
	return wordtags

#--------------------------------------------------------------------------------------------------------------------------------#
def train(c):
	sent, confusion = [], []
	stats, tokens, tags = [0,0,0,0,0,0], {}, {}

	f = open(c, 'r')
	for line in f:
		if(line == '\n'):																	# resolve transitions for sentence
			for i in range(len(sent)):
				if(int(sent[i][0]) > int(sent[i][3])):										# right arc
					if(not((sent[i][2],sent[int(sent[i][3])-1][2]) in rightarccounts) and (sent[i][1] != '.' or sent[i][1] != ',' or sent[i][1] != ':' or sent[i][1] != '\'\'' or sent[i][1] != '-RRB-')):
						rightarccounts[(sent[i][2],sent[int(sent[i][3])-1][2])] = 1
					else:
						rightarccounts[(sent[i][2],sent[int(sent[i][3])-1][2])] += 1
				
				elif(int(sent[i][3]) > int(sent[i][0])):									# left arc 
					if(not((sent[i][2],sent[int(sent[i][3])-1][2]) in leftarccounts)):
						leftarccounts[(sent[i][2],sent[int(sent[i][3])-1][2])] = 1
					else:
						leftarccounts[(sent[i][2],sent[int(sent[i][3])-1][2])] += 1	
			sent = []
			continue
		
		line = line.split()
		if(line[0] == '1'):									# new sentence
			stats[0] += 1
		
		stats[1] += 1										# token count
			
		if(not(line[2] in tags)):							# new POS tag
			tags[line[2]] = 0
			stats[2] += 1
		
		if(line[3] == '0'):									# root arc
			stats[5] += 1
		elif(int(line[0]) > int(line[3])):					# right arc
			stats[4] += 1
		elif(int(line[3]) > int(line[0])):					# left arc 
			stats[3] += 1
		
		sent.append(line)	
			
			
	temp = []												# swapping data structure from dict to list to sort
	for item in leftarccounts:
		temp.append((item, leftarccounts[item]))
	temp.sort()
	left = []
	for i in range(len(temp)):
		if(i == 0):
			left.append([temp[i]])
		elif(temp[i][0][0] == temp[i - 1][0][0]):
			left[len(left) - 1].append(temp[i])
		else:
			left.append([temp[i]])
		
	temp = []												# swapping data structure from dict to list to sort
	for item in rightarccounts:								
		temp.append((item, rightarccounts[item]))
	temp.sort()
	right = []
	for i in range(len(temp)):
		if(i == 0):
			right.append([temp[i]])
		elif(temp[i][0][0] == temp[i - 1][0][0]):
			right[len(right) - 1].append(temp[i])
		else:
			right.append([temp[i]])
	
	confcount = 0			
	for item in leftarccounts:								# creating confusion array
		if(item in rightarccounts):
			confusion.append((item, leftarccounts[item], rightarccounts[item]))
			confcount += 1
	confusion.sort()
	
	conf = []												# reformatting into new data structure
	for i in range(len(confusion)):
		if(i == 0):
			conf.append([confusion[i]])
		elif(confusion[i][0][0] == confusion[i - 1][0][0]):
			conf[len(conf) - 1].append(confusion[i])
		else:
			conf.append([confusion[i]])
	
	pos	= []												# turning tags dict into list to sort
	for item in tags:
		pos.append(item)
	pos.sort()
	
	return stats, left, right, conf, confcount, pos

#--------------------------------------------------------------------------------------------------------------------------------#
def dependparse(buffer):
	stack = []
	while(buffer or len(stack) > 1):
		action = oracle(stack, buffer)
		
		if(action == "SHIFT"):
			print([stack[i][0] + "/" + stack[i][1] for i in range(len(stack))], [buffer[i][0] + "/" + buffer[i][1] for i in range(len(buffer))], action)
			stack.insert(0,buffer.pop(0))
		elif(action == "Left-Arc"):
			print([stack[i][0] + "/" + stack[i][1] for i in range(len(stack))], [buffer[i][0] + "/" + buffer[i][1] for i in range(len(buffer))], action + ": " + stack[1][0] + "/" + stack[1][1] + " <-- " +  stack[0][0] + "/" + stack[0][1])
			stack.pop(1)
		elif(action == "Right-Arc"):
			print([stack[i][0] + "/" + stack[i][1] for i in range(len(stack))], [buffer[i][0] + "/" + buffer[i][1] for i in range(len(buffer))], action + ": " + stack[1][0] + "/" + stack[1][1] + " --> " +  stack[0][0] + "/" + stack[0][1])
			stack.pop(0)
		elif(action == "SWAP"):
			print([stack[i][0] + "/" + stack[i][1] for i in range(len(stack))], [buffer[i][0] + "/" + buffer[i][1] for i in range(len(buffer))], action)
			buffer.insert(0,stack.pop(1))
			
	print("[ " + stack[0][0] + "/" + stack[0][1] + "] [] ROOT --> " + stack[0][0] + "/" + stack[0][1])

#--------------------------------------------------------------------------------------------------------------------------------#
def oracle(stack, buffer):
	if(len(stack) < 2):
		return "SHIFT"
	else:
		if(stack[1][1][0] == 'V' and (stack[0][1][0] == '.' or stack[0][1][0] == 'R')):
			return "Right-Arc"
		elif(len(stack) > 2 and stack[1][1][0] == 'I' and stack[0][1][0] == '.'):
			return "SWAP"
		elif(len(buffer) > 0 and (stack[1][1][0] == 'V' or stack[1][1][0] == 'I') and (stack[0][1][0] == 'D' or stack[0][1][0] == 'I' or stack[0][1][0] == 'J' or stack[0][1][0] == 'P' or stack[0][1][0] == 'R')):
			return "SHIFT"
		elif((stack[1][1],stack[0][1]) in leftarccounts and (stack[1][1],stack[0][1]) in rightarccounts):
			if(leftarccounts[(stack[1][1],stack[0][1])] > rightarccounts[(stack[1][1],stack[0][1])]):
				return "Left-Arc"
			else:
				return "Right-Arc"
		elif((stack[1][1],stack[0][1]) in leftarccounts):
			return "Left-Arc"
		elif((stack[1][1],stack[0][1]) in rightarccounts):
			return "Right-Arc"
	

#--------------------------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":			
	f = input().strip()
	start = time.time()
	corpus = "wsj-clean.txt"
	stats, left, right, conf, cc, tags = train(corpus)
	
	for i in range(len(stats)):
		w = ""
		for j in range(5 - len(str(stats[i]))):
			w += " "
		stats[i] = w + str(stats[i])
	
	print("\nCorpus Statistics:\n")
	
	print("     # sentences  : " + stats[0])
	print("     # tokens     : " + stats[1])
	print("     # POS tags   : " + stats[2])
	print("     # Left-Arcs  : " + stats[3])
	print("     # Right-Arcs : " + stats[4])
	print("     # Root-Arcs  : " + stats[5])

	#--------------------------------------------------------------------------------------------------------------------------------#				
	print("\n\nLeft Arc Array Nonzero Counts:\n")
	
	e = 0
	for i in range(len(tags)):
		w = ""
		for j in range(5 - len(tags[i])):
			w += " "
		w = w + str(tags[i]) + " : "
		if(left[i-e][0][0][0] != tags[i]):
			e += 1
			print(w)
			continue
		for j in range(len(left[i-e])):
			w += "[ "
			for k in range(4 - len(left[i-e][j][0][1])):
				w += " "
			w += str(left[i-e][j][0][1]) + ","
			for k in range(4 - len(str(left[i-e][j][1]))):
				w += " "
			w += str(left[i-e][j][1]) + "] "

		print(w)
			
		
	#--------------------------------------------------------------------------------------------------------------------------------#				
	print("\n\nRight Arc Array Nonzero Counts:\n")
	
	e = 0
	for i in range(len(tags)):
		w = ""
		for j in range(5 - len(tags[i])):
			w += " "
		w = w + str(tags[i]) + " : "
		if(tags[i] != right[i-e][0][0][0]):
			e += 1
			print(w)
			continue
		for j in range(len(right[i-e])):
			if(right[i-e][j][0][1] == '.' or right[i-e][j][0][1] == ',' or right[i-e][j][0][1] == ':' or right[i-e][j][0][1] == '\'\'' or right[i-e][j][0][1] == '-RRB-'):
				continue
			w += "[ "
			for k in range(4 - len(right[i-e][j][0][1])):
				w += " "
			w += str(right[i-e][j][0][1]) + ","
			for k in range(4 - len(str(right[i-e][j][1]))):
				w += " "
			w += str(right[i-e][j][1]) + "] "

		print(w)
	
	#--------------------------------------------------------------------------------------------------------------------------------#				
	print("\n\nArc Confusion Array:\n")
	
	e = 0
	for i in range(len(tags)):
		w = ""
		for j in range(5 - len(tags[i])):
			w += " "
		w = w + str(tags[i]) + " : "
		if(tags[i] != conf[i-e][0][0][0]):
			e += 1
			print(w)
			continue
		for j in range(len(conf[i-e])):
			w += "[ "
			for k in range(4 - len(conf[i-e][j][0][1])):
				w += " "
			w += str(conf[i-e][j][0][1]) + ","
			for k in range(4 - len(str(conf[i-e][j][1]))):
				w += " "
			w += str(conf[i-e][j][1]) + ","
			for k in range(4 - len(str(conf[i-e][j][2]))):
				w += " "
			w += str(conf[i-e][j][2]) + "] "

		print(w)
	
	print("\n      Number of confusing arcs = " + str(cc))
	
	#--------------------------------------------------------------------------------------------------------------------------------#				
	print("\n\nInput Sentence:")
	
	wordtags = readtokens(f)
	w = ""
	for i in range(len(wordtags)):
		w += wordtags[i][0] + "/" + wordtags[i][1] + " "
	print(w)
	
	#--------------------------------------------------------------------------------------------------------------------------------#				
	print("\n\nParsing Actions and Transitions:\n")
	
	dependparse(wordtags)
	
	print("Elapsed Time = %.10f" % (time.time() - start))