# Sentiment Analyzer using BOW and a feedforward NN by Matthew Keeran
# runs via python NN_Final.py 
# written in python 3.5.4 on Windows 8.1.															
# tested with python 3.6 on Ubuntu 16

import glob
import numpy as np
import tensorflow as tf
from collections import Counter
import os, nltk, random, pickle, time
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

classes = 2
batch = 100
nodes = 1000
lemmatizer = WordNetLemmatizer()

def lex(pos,neg):
	lexicon, positive, negative = [], [], []
	indx = 0
	start = time.time()
	for f in os.listdir(pos):	
		words = open(pos + f,'r', encoding="utf8").readlines()
		words = words[0].split()
		positive.append([])
		for w in words:
			word = word_tokenize(w.lower())
			[positive[indx].append(i) for i in word]
			lexicon += word
		indx += 1
	
	indx = 0
	for f in os.listdir(neg):	
		words = open(neg + f,'r', encoding="utf8").readlines()
		words = words[0].split()
		negative.append([])
		for w in words:
			word = word_tokenize(w.lower())
			[negative[indx].append(i) for i in word]
			lexicon += word
		indx += 1

	lexicon = [lemmatizer.lemmatize(w) for w in lexicon]
	counts = Counter(lexicon)	
	
	l2, indx = {}, 0
	for w in counts:
		if(1000 > counts[w] > 75):
			l2[w] = indx
			indx += 1	
	
	print("Lexicon size = ",len(l2))
	print("Creating lexicon took %.2f seconds" % (time.time()-start))
	return l2, positive, negative


def vectorize_train(review, lexicon, clas):
	vector = []
	features = np.zeros(len(lexicon))
	
	review = [lemmatizer.lemmatize(w) for w in review]
				
	for w in review:
		if(w in lexicon):
			features[lexicon[w]] += 1
		
	features = list(features)
	vector.append([features, clas])
	
	return vector
	
def vectorize_test(review, lexicon, clas):
	vector = []
	features = np.zeros(len(lexicon))
	review = open(review, 'r', encoding="utf8").readlines()
	review = word_tokenize(review[0].lower())
	review = [lemmatizer.lemmatize(w) for w in review]
				
	for w in review:
		if(w in lexicon):
			features[lexicon[w]] += 1
		
	features = list(features)
	vector.append([features, clas])
	
	return vector
	

def prep_data(pos,neg, testpos,testneg):
	start = time.time()
	lexicon, positive, negative = lex(pos,neg)
	
	t2 = time.time()
	vectors = []
	for i in range(len(positive)):	
		vectors += vectorize_train(positive[i],lexicon,[1,0])
	
	t1 = time.time()
	print("Adding positive training data took %.2f seconds" % (t1-t2))
	
	for i in range(len(negative)):	
		vectors += vectorize_train(negative[i],lexicon,[0,1])
	
	t2 = time.time()	
	print("Adding negative training data took %.2f seconds" % (t2-t1))
	
	random.shuffle(vectors)
	vectors = np.array(vectors)
	train_x = list(vectors[:,0])
	train_y = list(vectors[:,1])
		
	t2 = time.time()
	vectors = []
	for f in glob.iglob(testpos + "*.txt"):	
		vectors += vectorize_test(f,lexicon,[1,0])
	t1 = time.time()
	print("Adding positive test data took %.2f seconds" % (t1-t2))
	
	for f in glob.iglob(testneg + "*.txt"):	
		vectors += vectorize_test(f,lexicon,[0,1])
	t2 = time.time()
	print("Adding negative test data took %.2f seconds" % (t2-t1))
	
	random.shuffle(vectors)
	vectors = np.array(vectors)
	test_x = list(vectors[:,0])
	test_y = list(vectors[:,1])

	print("Creating Sets and Labels took %.2f seconds" % (time.time()-start))
	return train_x,train_y, test_x,test_y
	

def NN(data,train_x):

    layer1 = {'weights':tf.Variable(tf.random_normal([len(train_x[0]), nodes])),'biases':tf.Variable(tf.random_normal([nodes]))}

    output = {'weights':tf.Variable(tf.random_normal([nodes, classes])),'biases':tf.Variable(tf.random_normal([classes])),}

    layer1 = tf.add(tf.matmul(data,layer1['weights']), layer1['biases'])
    layer1 = tf.nn.relu(layer1)

    output = tf.matmul(layer1,output['weights']) + output['biases']
    return output


def Train_NN(x, train_x, train_y,test_x,test_y,y):
	start2 = time.time()
	model = NN(x,train_x)
	cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=model, labels=y))
	optimizer = tf.train.AdamOptimizer().minimize(cost)
    
	epochs = 10
	with tf.Session() as sess:
		sess.run(tf.global_variables_initializer())

		for epoch in range(epochs):
			loss = 0

			i = 0			
			while i < len(train_x):
				start = i
				end = i + batch
				
				batch_x = np.array(train_x[start:end])
				batch_y = np.array(train_y[start:end])

				z, l = sess.run([optimizer, cost], feed_dict={x: batch_x, y: batch_y})
				loss += l
				i += batch

			print('Epoch', epoch+1,'loss: %.4f' % loss)

		correct = tf.equal(tf.argmax(model, 1), tf.argmax(y, 1))
		accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
		
		print('Accuracy:',accuracy.eval({x:test_x, y:test_y}))
	print("Training NN took %.4f seconds" % (time.time()-start2))
	


if __name__ == '__main__':
	begin = time.time()
	pos, neg, testpos, testneg = "C:\\Users\\Matt\\Desktop\\aclImdb\\train\\pos\\", "C:\\Users\\Matt\\Desktop\\aclImdb\\train\\neg\\","C:\\Users\\Matt\\Desktop\\aclImdb\\test\\pos\\", "C:\\Users\\Matt\\Desktop\\aclImdb\\test\\neg\\"

	train_x, train_y, test_x, test_y = prep_data(pos,neg,testpos,testneg)	

	x = tf.placeholder('float', [None, len(train_x[0])])
	y = tf.placeholder('float')

	model = Train_NN(x,train_x,train_y,test_x,test_y,y)
		
	print("Total Elapsed Time = %.2f seconds" % (time.time()-begin))

