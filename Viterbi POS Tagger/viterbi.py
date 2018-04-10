# Viterbi Part-of-Speech Tagger by Matthew Keeran
# runs via python viterbi.py 
# I personally pipe the output to a text file, then enter the file names one by one followed by enter.	python viterbi.py > output.txt
# written in python 3.5.4 on Windows 8.1, produces all desired output all in correct format.		pos.train.txt
# tested with python 3.6 on Ubuntu 16, produces all desired output all in correct format.		sample_3.txt

#--------------------------------------------------------------------------------------------------------------------------------#
def readtokens(f):
	# Bi-grams, Lexicals, Sentences
	f = open(f, 'r')
	tokens, tokcounts, startcount = {}, [], []
	wordtags, wordtagcount, l = {}, [], {}
	sentences, flag, k = 0, 0, 0
	prevtag, transitions, transcount = "", {}, []
	
	for line in f:
			
		if(line == '\n'):
			sentences += 1
			flag = 1
			continue	
		
		words = line.split()
		words[0] = words[0].lower()
		
		if((words[0][len(words[0]) - 1] == 's' and words[0][len(words[0]) - 2] == 'e' and words[0][len(words[0]) - 3] == 's' and words[0][len(words[0]) - 4] == 's') or (words[0][len(words[0]) - 1] == 's' and words[0][len(words[0]) - 2] == 'e' and words[0][len(words[0]) - 1] == 'x')):
			words[0] = words[0][0:len(words[0]) - 2]
		elif((words[0][len(words[0]) - 1] == 's' and words[0][len(words[0]) - 2] == 'e' and words[0][len(words[0]) - 3] == 's') or (words[0][len(words[0]) - 1] == 's' and words[0][len(words[0]) - 2] == 'e' and words[0][len(words[0]) - 3] == 'z')):
			words[0] = words[0][0:len(words[0]) - 1]
		elif((words[0][len(words[0]) - 1] == 's' and words[0][len(words[0]) - 2] == 'e' and words[0][len(words[0]) - 3] == 'h' and words[0][len(words[0]) - 4] == 'c') or (words[0][len(words[0]) - 1] == 's' and words[0][len(words[0]) - 2] == 'e' and words[0][len(words[0]) - 3] == 'h' and words[0][len(words[0]) - 4] == 's')):
			words[0] = words[0][0:len(words[0]) - 2]
		elif(words[0][len(words[0]) - 1] == 'n' and words[0][len(words[0]) - 2] == 'e' and words[0][len(words[0]) - 3] == 'm'):
			words[0] = words[0][0:len(words[0]) - 2]
			words[0] += "an"
		elif(words[0][len(words[0]) - 1] == 's' and words[0][len(words[0]) - 2] == 'e' and words[0][len(words[0]) - 3] == 'i'):
			words[0] = words[0][0:len(words[0]) - 3]
			words[0] += "y"
		
		if(not(words[0] in l)):
			l[words[0]] = 1
		
		if(not(words[1] in tokens)):
			tokens[words[1]] = [1, 0]
		elif(words[1] in tokens):
			tokens[words[1]][0] += 1
		
		if(not((words[0],words[1]) in wordtags)):
			wordtags[(words[0],words[1])] = 1
		elif((words[0],words[1]) in wordtags):
			wordtags[(words[0],words[1])] += 1
		
		if(flag == 1):
			tokens[words[1]][1] += 1
		
		if(k == 0):
			tokens[words[1]][1] += 1
			k = 1
		
		if(prevtag != "" and not((words[1],prevtag) in transitions) and flag == 0):
			transitions[(words[1],prevtag)] = 1
		elif(prevtag != "" and (words[1],prevtag) in transitions and flag == 0):
			transitions[(words[1],prevtag)] += 1
		elif(not((words[1],"  ") in transitions) and flag == 1):
			transitions[(words[1],"  ")] = 1
			flag = 0
		elif((words[1],"  ") in transitions and flag == 1):
			transitions[(words[1],"  ")] += 1
			flag = 0
		
		prevtag = words[1]
	
	tokdist, emissions = [], {}
	# initial dist i = # of occurances of \n\n i / # of sentences in corpus
	
	for item in tokens:
		tokens[item].append(float(tokens[item][1] / (sentences + 1)))
	
	# emission i = # of occurances of word i with given tag  / # times tag occurs
	
	for item in wordtags:
		emissions[item] = float(wordtags[item] / tokens[item[1]][0])
	
	emiss = []
	for key, value in emissions.items():
		temp1 = [key,value]
		emiss.append(temp1)
	emiss.sort()
	
	toks = []
	for key, value in tokens.items():
		temp1 = [key,value]
		toks.append(temp1)
	toks.sort()
	
	transit = []
	for key, value in transitions.items():
		temp1 = [key,value]
		transit.append(temp1)
	transit.sort()
	
	# transition probabilities
	
	transitionprobs = []
	
	for i in range(len(toks)):
		row = []
		for j in range(len(transit)):
			if(transit[j][0][1] == toks[i][0]):
				prob = float(transit[j][1] / toks[i][1][0])
				row.append((transit[j][0], prob))
				
		transitionprobs.append(row)

	return toks, emiss, transitionprobs, sentences, len(l)

#--------------------------------------------------------------------------------------------------------------------------------#
def test(f):
	f = open(f, 'r')
	words = []
	for line in f:
		l = line.split()
		for i in range(len(l)):
			words.append(l[i])

	return words

#--------------------------------------------------------------------------------------------------------------------------------#
def findtags(d, e):															# finding emission probabilities of test words
	tags = []																
	for i in range(len(d)):
		tags.append([])
		flag = 0
		for j in range(len(e)):
			if(d[i].lower() == e[j][0][0]):
				tags[i].append((e[j][0][1], e[j][1]))
				flag = 1
		if(flag == 0):
			tags[i].append(("NN", 0))
			
	
	return tags

				
#--------------------------------------------------------------------------------------------------------------------------------#				
def viterbi(tokens, sequence, tags, transprobs):
	path, id, trans = [], [], {}
	
	for i in range(len(tags[0])):											# finding initial probs of first word in sequence
		for j in range(len(tokens)):
			if(tags[0][i][0] == tokens[j][0]):
				id.append(tokens[j][1][2])
	
	for i in range(len(transprobs)):										# converting transition probs from 2D list to dict
		for j in range(len(transprobs[i])):
				trans[transprobs[i][j][0]] = transprobs[i][j][1]
	
	seqprobs, t = [], []
	for i in range(len(sequence)):											# actual start of Viterbi
		some = 0
		seqprobs.append([])
		for j in range(len(tags[i])):										
			if(i == 0):														# tags = [[(VB, 0.3),(NN,0.1)], [(POS, 0.0)]]
				p = float(tags[i][j][1] * id[j])
				seqprobs[i].append(p)										# seqprobs = [[0.4,0.6],[0.2,0.3,0.5],[0.1,0.8,0.1]]
				some += p
			else:
				currprobs = []
				for k in range(len(seqprobs[i-1])):							# for every sub
					if((tags[i][j][0],tags[i-1][k][0]) in trans):
						currprobs.append(float(seqprobs[i-1][k] * trans[(tags[i][j][0],tags[i-1][k][0])] * tags[i][j][1]))
					else:
						currprobs.append(float(0))							# if transition doesn't exist in corpus prob = 0
				p = max(currprobs)
				indx = maxi(currprobs)
				seqprobs[i].append(p)
				some += p				
			
		seqprobs[i] = normaleyes(seqprobs[i], some)
		j = maxi(seqprobs[i])
		path.append(tags[i][j][0])
	
	return path, seqprobs
			
#--------------------------------------------------------------------------------------------------------------------------------#				
def normaleyes(l,s):
	normed = []
	for i in range(len(l)):
		normed.append(float(l[i]/s))
		
	return normed

#--------------------------------------------------------------------------------------------------------------------------------#				
def maxi(l):
	tmp, indx = float("-inf"), 0
	for i in range(len(l)):
		if(l[i] > tmp):
			tmp = l[i]
			indx = i
	return indx

#--------------------------------------------------------------------------------------------------------------------------------#				
def max(l):
	tmp = float("-inf")
	for i in range(len(l)):
		if(l[i] > tmp):
			tmp = l[i]
	return tmp

#--------------------------------------------------------------------------------------------------------------------------------#				

			
if __name__ == "__main__":
	f1 = input().strip()
	f2 = input().strip()
	
	tokens, emiss, transp, sentences, lex = readtokens(f1)
		
	print("\n\nAll Tags Observed:\n")
	for i in range(len(tokens)):
		if(i + 1 < 10):
			print(" " + str(i + 1) + "  " + tokens[i][0])
		else:
			print(str(i + 1) + "  " + tokens[i][0])
	
	
	print("\nInitial Distribution:\n")
	for i in range(len(tokens)):
		if(tokens[i][1][2] > 0.000000):
			print("start [ " + tokens[i][0] + " |  ] %.6f" % tokens[i][1][2])
	
	
	print("\nEmission Probabilities:\n")
		

	for i in range(len(emiss)):
	
		whitespc = 16 - len(emiss[i][0][0])
		w = ""
		for j in range(whitespc):
			w += " "
		w += emiss[i][0][0]
		
		w2 = ""
		for j in range(5 - len(emiss[i][0][1])):
			w2 += " "
		w2 += emiss[i][0][1]
		
		print(w + w2 + " %.6f" % emiss[i][1])
	
	
	print("\nTransition Probabilities:\n")
	
	big, some = 0, 0
	s = ""
	for i in range(len(tokens)):
		if(tokens[i][1][2] > 0.000000):
			s += "  [" + tokens[i][0] + "|] %.6f" % tokens[i][1][2]
			big += 1
			some += tokens[i][1][2]
	print("[ %.6f ] " % some + s) 
	

	for i in range(len(transp)):
		s, sum = "", 0
		for j in range(len(transp[i])):
			sum += transp[i][j][1]
			s += "  [" + transp[i][j][0][0] + "|" + transp[i][j][0][1] + "] %.6f" % transp[i][j][1]
			big += 1
			some += transp[i][j][1]
		
		if(sum < 0.999999):
			print("[ 1.000000 ] " + "  [  |" + transp[i][0][0][1] + "] %.6f" % (1 - sum) + s)
			big += 1
		else:
			print("[ %.6f ] " % sum + s)
	
	
	print("\nCorpus Features:\n")
	print("   Total # tags        : " + str(len(tokens)))
	print("   Total # bigrams     : " + str(big))
	print("   Total # lexicals    : " + str(lex - 7))
	print("   Total # sentences   : " + str(sentences))
	
	sequence = test(f2)
	
	tags = findtags(sequence, emiss)
	
	print("\n\nTest Set Tokens Found in Corpus:\n")
	
	for i in range(len(sequence)):
		whitespc = 16 - len(sequence[i])
		w = ""
		for j in range(whitespc):
			w += " "
		w += sequence[i] + " : "
	
		for j in range(len(tags[i])):
			w2 = ""
			for k in range(4 - len(tags[i][j][0])):
				w2 += " "
			w += w2 + tags[i][j][0] + " (%.6f)" % tags[i][j][1]
		print(w)
	
	path, probs = viterbi(tokens, sequence, tags, transp)
	
	print("\n\nIntermediate Results of Viterbi Algorithm:\n")
	
	for i in range(len(sequence)):
		s = "Iteration  " + str(i+1) + " :"
		whitespc = 13 - len(sequence[i])
		for j in range(whitespc):
			s += " "
		s += sequence[i] + " :" 
		for j in range(len(tags[i])):
			if(i == 0):
				s += " " + tags[i][j][0] + " (%.6f, null)" % probs[i][j]
			else:	
				s += " " + tags[i][j][0] + " (%.6f, " % probs[i][j] + path[i - 1] + ")" 
		print(s)	
	
	
	print("\n\nViterbi Tagger Output:\n")
	
	for i in range(len(sequence)):
		s = ""
		whitespc = 13 - len(sequence[i])
		for j in range(whitespc):
			s += " "
		s += sequence[i] + "     " + path[i]
		print(s)
	print()
	
	
	