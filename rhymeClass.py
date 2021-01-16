#Luke De Vos
#Lyric Analyzer

'''

move Word methods to global scope so there's not that messy Word() nonsense in splitSylls

Data Sources:
	note- "office" o sound is AO, "top" o sound is AA
	there's some weirdness with the vowel sound in words like "war" too

Features:
	Find 15 distinct colors for the phonemes.
		assign the most distinct/brightest colors to more common phonemes

Rhyme Finding:
	
'''


'''
#=======================================
'''

import re
from sty import fg, rs, bg
import nltk


class Word:
	# constructor
	def __init__(self, passedText):
		self.text = passedText
		self.phos = []
		self.phos2 = []
		self.sylls = []
		self.emphs = []
		self.rNos = []
		self.multi = []
		self.lineNo = 0
		self.hasConG = False #true if the word has a contracted 'g' like "sayin'"
		self.numSylls = 0
		self.pos = ''
		self.isPruneable=True
		
	#returns stripped, g-fixed, and lowered text to fit phDict
	def fit(self):
		newWord=""
		x = re.search('[A-Za-z0-9\']+', self.text)	#strip non-word punc
		if x!=None:
			newWord = x.group(0)
		if newWord[-3:] == "in\'":		#fix G
			self.hasConG = True
			newWord = newWord[0:-1] + 'g'
		return newWord.lower()

	#returns text without preceding or following punctuation (ignoring apostraphes)
	def strip(self):
		x = re.search('[A-Za-z0-9\']+', self.text)
		if str(x)=='None':
			return self.text
		else:
			return x.group(0)

	#return punctuation to left of dict word
	def getLeftPunc(self):
		i=0
		for character in self.text:
			if character in PUNCT:
				i+=1
			else:
				return self.text[0:i]

	#return punctuation to right of dict word
	def getRightPunc(self):
		i = len(self.text) - 1
		while (self.text[i] in PUNCT):
			i -= 1
		i += 1
		return self.text[i:]

	#prints word with colors for rhymes
	def cPrint(self):
		if self.numSylls == 0:	#unrecognized word
			print(bg(40,40,40) + self.strip() + bg.rs, end='')
		elif len(self.phos) != len(self.sylls):	
			print(bg(140,140,40) + self.strip() + bg.rs, end='')
		else:
			for i in range(self.numSylls):
				if self.rNos[i] != 0:
					print(colorDict[self.phos[i]], end='')	
				#shade emphasized sylls
				if self.emphs[i] !=0:
					print(bg(70,70,50),end='')
				print(self.sylls[i] + fg.rs + bg.rs, end='')

	#prints word with highlights multi syllable rhymes
	def mPrint(self):
		if self.numSylls == 0:	#unrecognized word
			print(bg.rs+fg(170,230,170) + self.strip()+fg.rs, end='')
		elif len(self.phos) != len(self.sylls):	
			print(bg.rs+fg(255,150,150) + self.strip() + fg.rs, end='')
		else:
			for i in range(self.numSylls):
				if self.multi[i] != lastMulti[0]:
					print(bg.rs,end='')
				if self.multi[i]!=0:
					print(bgList[self.multi[i]%len(bgList)],end='')
				lastMulti[0]=self.multi[i]
				print(self.sylls[i], end='')


class Syllable:

	def __init__(self, passedText):
		self.syll=passedText
		self.pho=''
		self.emph=''
		self.oneSyll=''
		self.lineNo=''
		self.wholeWord=''
		self.textUnit=''
		self.isWord=False
		self.multi=0 #overwritten in .markMultiRhymes
		self.rNo=0 #overwritten in .markSyllRhymes
		self.isRecog=True	#set to false when syllList is created if corresponding word is not in phDict
		self.multiPho='0' #if this syll closeMatched with a similar pho in a multirhyme, store that pho here for correct color printing
		self.partOfMulti=False

	#toString
	def __str__(self):
		return self.syll + " " + self.pho


	#prints syllable with colors for rhymes
	def cPrint(self):
		if not self.isRecog:	#unrecognized word
			print(bg(40,40,40) + self.syll + bg.rs, end='')
		else:
			if self.rNo != 0:
				#print(bg(20,20,20),end='')
				if self.multiPho=='0':
					print(colorDict[self.pho], end='')	
				else:
					print(colorDict[self.multiPho], end='')	
			print(self.syll + fg.rs + bg.rs, end='')

	#prints syllable with highlighted multi rhymes
	def mPrint(self):
		if not self.isRecog:	#unrecognized word
			print(bg(40,40,40) + self.syll + bg.rs, end='')
		else:
			if self.multi != 0:
				print(bgList[self.multi%len(bgList)], end='')
			print(self.syll + bg.rs, end='')

	#prints syllable with colors for rhymes
	def ePrint(self):
		if not self.isRecog:	#unrecognized word
			print(bg(240,240,240) + self.syll + bg.rs, end='')
		else:	
			#shade emphasized sylls
			if self.emph !=0:
				print(bg(70,60,50),end='')
			print(self.syll + fg.rs + bg.rs, end='')
		
	#return punctuation to left of dict word
	def getLeftPunc(self):
		i=0
		for character in self.textUnit:
			if character in PUNCT:
				i+=1
			else:
				return self.textUnit[0:i]

	#return punctuation to right of 
	def getRightPunc(self):
		i = len(self.textUnit) - 1
		while (self.textUnit[i] in PUNCT):
			i -= 1
		i += 1
		return self.textUnit[i:]

#SPLIT SYLLS
#passed a Word object, return list of the word's individual syllables =================================================
#returns whole word if it is not in phDict
def splitSylls(word):	#(Word)
	if word.fit() in phDict:
		word.numSylls = len(phDict[word.fit()])
	if word.numSylls == 1 or word.fit() not in phDict:		
		return [word.strip()]

	numSylls = word.numSylls
	fitWord = word.fit()
	stripWord = word.strip()

	#check syllable dictionary text file first
	if fitWord in syllDict and len(syllDict[fitWord]) == word.numSylls:
		newList = syllDict[fitWord]
		if stripWord[0].isupper():
			newList[0] = newList[0].capitalize()
		if word.hasConG:
			newList[-1] = newList[-1][0:-1] + '\''
		return newList

	#SUFFIX CHECK
	#NOTE: a word with one of these endings will continue past the if
	# 		statement if it does not affect syllable count
	if fitWord[-2:] == "es" or fitWord[-2:] == "ed":
		if fitWord[0:-1] in phDict and len(phDict[fitWord[0:-1]]) == numSylls-1:
			newList=splitSylls(Word(stripWord[0:-1]))
			newList[numSylls-2]=newList[numSylls-2][0:-1]	#chop off trailing 'e'
			if fitWord[-1] == 's': newList.append("es")
			elif fitWord[-1] == 'd': newList.append("ed")
			return newList
		elif fitWord[0:-2] in phDict and len(phDict[fitWord[0:-2]]) == numSylls-1:
			newList=splitSylls(Word(stripWord[0:-2]))
			if fitWord[-1] == 's': newList.append("es")
			elif fitWord[-1] == 'd': newList.append("ed")
			return newList
	elif fitWord[-3:] == "ing":
		eAdded = fitWord[0:-3] + 'e'
		if fitWord[0:-3] in phDict and len(phDict[fitWord[0:-3]]) == numSylls-1:
			newList = splitSylls(Word(fitWord[0:-3]))
			if word.hasConG:
				newList.append('in\'')
			else:
				newList.append("ing")
			return newList
		elif eAdded in phDict and len(phDict[eAdded]) == numSylls-1:
			newList = splitSylls(Word(eAdded))
			newList[-1]=newList[-1][0:-1] #clip trailing e; "ing" will be appended
			if word.hasConG:
				newList.append('in\'')
			else:
				newList.append("ing")
			return newList
	elif fitWord[-4:] == "ment":
		if fitWord[0:-4] in phDict and len(phDict[fitWord[0:-4]]) == numSylls-1:
			newList = splitSylls(Word(fitWord[0:-4]))
			newList.append("ment")
			return newList
	elif fitWord[-4:] == "tion":
		noSuffix = fitWord[0:-3]+'e'
		if noSuffix in phDict and len(phDict[noSuffix]) == numSylls-1:
			newList = splitSylls(Word(noSuffix))
			newList[-1] = newList[-1][0:-2]
			newList.append("tion")
			return newList
	#advanced splitting
	phos=phDict2[fitWord]
	newList=[]
	vf1=0
	vf2=False
	i1=0
	i2=0
	j2=0
	while i1 < len(phos):	
		if len(newList)==numSylls-1:
			newList.append(stripWord[i2:])
			return newList
		#vowel pho found
		if phos[i1][-1] in VOWELNOS:
			vf1+=1
		#non vowel pho found
		else:	
			#if a single vowel pho came before this
			if vf1==1:
				#look through original for [c]*[v]+[c]+ match as one syllable
				vf2=False
				cf2=False
				while j2 < len(stripWord):
					if stripWord[j2] in VOWELS:
						vf2=True
					else:
						if vf2:
							if stripWord[j2+1] in VOWELS:
								newList.append(stripWord[i2:j2])	
								i2=j2
							else:
								newList.append(stripWord[i2:j2+1])	
								i2=j2+1
							break
					j2+=1
				vf1=0
			#if two vowel phos came before this
			elif vf1==2:
				#look through original stripWord add [c]*[v] and [v][c] matches
				complete=False
				while j2 < len(stripWord):
					if stripWord[j2] in VOWELS:
						newList.append(stripWord[i2:j2+1])
						i2=j2+1	
						for x2 in range(i2, len(stripWord)):
							if stripWord[x2] not in VOWELS:
								if stripWord[x2+1] not in VOWELS:
									newList.append(stripWord[i2:x2+1])
									i2=x2+1
								else:
									newList.append(stripWord[i2:x2])
									i2=x2
								complete=True
								break
					if complete:
						break
					j2+=1
				vf1=0
		i1+=1
	return newList


#emphasis pruning
def prune():
	for i in range(0, len(syllList)):
		if syllList[i].oneSyll:	#one syllable
			if syllList[i].pos in softPOS:
				syllList[i].emph == 0
		
'''
	for i in range(1, len(wordList)):
		try:
			#only consider single syllable, non-DT/IN/CC, non-handstressed words for pruning
			if wordList[i].numSylls==1 and wordList[i].isPruneable:
				#remove stress
				#if phonetically simple..
				if len(wordList[i].phos2) < 4:
					#prune if following word is multisyllable and begins with stress
					if wordList[i+1].numSylls>1 and wordList[i+1].emphs[0]!=0:
						wordList[i].emphs[0]=0
					#prune if previous syll was emphasized
					elif wordList[i-1].emphs[-1] == 1:
						wordList[i].emphs[0]=0
				#add stress
				#followed by punct
				if wordList[i].text[-1] in PUNCT:
					wordList[i].emphs[0]=1
					#newly stressed word has simple word behind it, unstress prev word
					if wordList[i-1].numSylls==1 and len(wordList[i].phos2) < 4 and wordList[i-1].emph:
						wordList[i-1].emphs[0]=0
				#followed by multisyllabic word that does not start with stress
				if wordList[i+1].numSylls>1 and wordList[i+1].emphs[0]==0:
					wordList[i].emphs[0]=1
		except:
			continue
'''
'''
		#special case emphasis fixing
				if syllList[-1].oneSyll:	#is one syllable word
					if syllList[-1].pos in softPOS and syllList[-1].fit() not in EXCEPTIONS:
						syllList[-1].emphs[0]=0
						syllList[-1].isPruneable=False
					elif syllList[-1].fit() in ILIST:
						syllList[-1].emphs[0]=0 
						syllList[-1].isPruneable=False
					elif syllList[-1].pos[0:2] in hardPOS:
						syllList[-1].emphs[0]=3
						syllList[-1].isPruneable=False
					if i==len(line.split())-1: #last word in line
						syllList[-1].emphs[0]=3
						syllList[-1].isPruneable=False
'''


#passed a list of entries from syllList
#returns true if a phoneme already has a multi rhyme ID and thus is unavailable for multi ID assignment
def syllTaken(sylls): #(list of Syllable objects)
	for thisSyll in sylls:
		if thisSyll.multi != 0:
			return True
	return False

#determines if two syllables are close enough to rhyming for multi rhyme purposes
def isCloseMatch(syll1, syll2): #(Syllabe, Syllable)
	#if phonemes match
	if syll1.pho==syll2.pho:
		return True
	#if phonemes are the weak/vague sounds
	if syll1.emph==0 or syll2.emph==0:
		if syll1.pho in SIMSYLLS1 and syll2.pho in SIMSYLLS1:
			return True
		elif syll1.pho in SIMSYLLS2 and syll2.pho in SIMSYLLS2:
			return True
		#elif syll1.pho in SIMSYLLS3 and syll2.pho in SIMSYLLS3:
		#	return True
		
	return False

#passed entries of syllList
def isMultiMatch(sylls1, sylls2, approx): #(list of syllList entries, list of syllList entries)
	if len(sylls1)==2:
		if sylls1[0].wordNo!=sylls1[1].wordNo:
			return False
		if sylls2[0].wordNo!=sylls2[1].wordNo:
			return False
	if approx:
		for i in range(len(sylls1)):
			if not isCloseMatch(sylls1[i], sylls2[i]):
				return False
			else:
				#for correct color printing
				if sylls1[i].pho!=sylls2[i].pho:
					sylls2[i].multiPho=sylls1[i].pho
	else:
		for i in range(len(sylls1)):
			if sylls1[i].pho != sylls2[i].pho:
				return False
			#if sylls1[i].emph != sylls2[i].emph:
			#	return False
	return True

#returns True if over half of the passed syllables are identical and also part of the same word
#used for pruning lame multi-rhymes
def isRepetitive(sylls1, sylls2): #(list of Syllable objects, list of Syllable objects)
	matches=0
	for i in range(len(sylls1)):
		if sylls1[i].syll == sylls2[i].syll:
			if sylls1[i].wholeWord == sylls2[i].wholeWord:
				matches+=1
	if matches > len(sylls1)/2:
		return True
	return False

#returns true if all passed syllables are on the same line
def allSameLine(sylls1): #(list of Syllable objects)
	for i in range(len(sylls1)-1):
		if sylls1[i].lineNo!=sylls1[i+1].lineNo:
			return False
	return True

#returns true if passed syllables are all unemphasized
def allUnemph(sylls1): #(list of Syllable objects)
	for i in range(len(sylls1)):
		if sylls1.emph!=0:
			return False
	return True

#MULTI SYLL RHYME MARKING
def markMultiRhymes(exclusive, multiLen): #(boolean, int)
	multiNo=1
	multDist=16
	multCountList.append(0)
	multiFound=False
	#for each entry of syllList (each syllable)...
	for i in range(len(syllList)-(2*multiLen)+1):
		iList = syllList[i:i+multiLen]
		dist=0
		alreadyAdded=False #set to true when a multi rhyme match is found
		if not allSameLine(iList): continue	#no multis across lines
		#skip if this group of phonemes already has a multiNo assigned to it
		if exclusive:
			if syllTaken(iList): continue
		#for every other syllable ahead of syllable i (plus multiLen sylls)
		for j in range(i+multiLen, len(syllList)-multiLen+1):
			jList = syllList[j:j+multiLen]
			if dist>multDist: break
			dist+=1
			if not allSameLine(jList): continue
			#first only find perfectly matched multis
			if exclusive:
				if syllTaken(jList): continue
			if isMultiMatch(iList, jList, False):
				if isRepetitive(iList, jList): continue #repetitive phrase
				if not alreadyAdded:
					multCountList[-1]+=1
					alreadyAdded=True
				multCountList[-1]+=1
				#assign multi rhyme numbers
				for k in range(multiLen):
					syllList[i+k].multi = multiNo
					syllList[i+k].partOfMulti=True
					syllList[j+k].multi = multiNo
					syllList[j+k].partOfMulti=True
				dist=0
				multiFound=True
			'''
			THIS SHOULD BE MOVED. RN JUST HAPPENS IMMEDIATELY AFTER ABOVE CODE EACH LOOP
			#then check for approximate multis, ignoring any set of sylls with a multiNo already
			if exclusive:
				if syllTaken(syllList[j:j+multiLen]):continue
			if isMultiMatch(syllList[i:i+multiLen], syllList[j:j+multiLen], True):
				if isRepetitive(syllList[i:i+multiLen], syllList[j:j+multiLen]):
					continue
				if alreadyAdded==False:
					multCountList[-1]+=1
					alreadyAdded=True
				multCountList[-1]+=1
				#assign multi rhyme numbers
				for k in range(multiLen):
					syllList[i+k].multi = multiNo
					syllList[i+k].partOfMulti=True
					syllList[j+k].multi = multiNo
					syllList[j+k].partOfMulti=True
				dist=0
				multiFound=True
			'''
		if multiFound:
			multiNo+=1
			multiFound=False

#clear all Syllable objects' multi values
def clearMultis():
	for i in range(len(syllList)):
		syllList[i].multi=0

#mark wordList for syll rhymes appropriately
def addRhyme(x,y, rhymeNo):
	if syllList[x].rNo!=0:
		syllList[y].rNo=syllList[x].rNo
	else:
		syllList[x].rNo=rhymeNo
		syllList[y].rNo=rhymeNo
	

#SINGLE SYLLABLE RHYME DETECTION
def markSyllRhymes():
	rhymeNo=1
	maxDist=16
	dist=0
	#for every syll..
	for i in range(len(syllList)-1):
		rhymeFound=False
		#if syllList[i].rNo!=0: continue
		#for every syll ahead of syllList[i]..
		dist=0
		for j in range(i+1, len(syllList)):
			#if syllList[j].rNo!=0: continue
			if dist>maxDist: break
			dist+=1
			#if the sylls are part of corresponding nonzero multis
			if syllList[i].multi==syllList[j].multi and syllList[i].multi!=0:
				if isCloseMatch(syllList[i], syllList[j]):
					addRhyme(i,j,rhymeNo)
					rhymeFound=True
					dist=0
			#sylls have different multiNos
			else:
				#if the sylls are identical sets of characters and the word they are a part of is the same word (not Word object), ignore
				if syllList[i].syll == syllList[j].syll:
					if syllList[i].wholeWord == syllList[j].wholeWord:
						continue
				#if the syllables' vowel sound matches perfectly..
				if syllList[i].pho == syllList[j].pho:
					#and if both emphasized, add rhyme
					if syllList[i].emph in EMPHNOS and syllList[j].emph in EMPHNOS:
						addRhyme(i,j,rhymeNo)
						rhymeFound=True
						dist=0
		if rhymeFound: 
			rhymeNo+=1

#counts number of syllabes that rhyme
def countSyllRhymes():
	count=0
	for i in range(len(syllList)):
		if syllList[i].rNo!=0:
			count+=1
	return count

#print
#PRINT LYRICS with colored rhymes
def printOut(x): #(string)
	wordNo=0
	syllNo=0
	with open(filePath) as file:
		for line in file:
			for word in line.split():
				for textUnit in re.findall('[^\s\-]+\-?', word):
					print(syllList[syllNo].getLeftPunc(), end='')
					while syllList[syllNo].wordNo == wordNo:
						if x == 'rhymes':
							syllList[syllNo].cPrint()
						elif x == 'multis':
							syllList[syllNo].mPrint()
						elif x == 'emphs':
							syllList[syllNo].ePrint()
						if syllNo == len(syllList)-1 or syllList[syllNo].wordNo != syllList[syllNo+1].wordNo:
							print(syllList[syllNo].getRightPunc(), end='')
						syllNo+=1
						if syllNo > len(syllList)-1: break #all lyrics read
					wordNo+=1
					if textUnit[-1] != '-':
						print(" ", end='')
			print()

#STATS
def printStats():
	totRhymeSylls = countSyllRhymes()
	totWords = len(wordList)
	totSylls = len(syllList)
	print("Words: "+str(totWords))
	print("Percentage of words unique: "+str((len(uniqDict)/totWords)*100)[0:4]+"%")
	print("Syllables: "+str(totSylls))
	print("Avg syllables per word: "+str(totSylls/totWords)[0:4])
	print("Percentage of syllables that rhyme: "+str((totRhymeSylls/totSylls)*100)[0:4]+"%")
	multCount=0
	for i in range(len(syllList)):
		if syllList[i].partOfMulti:
			multCount+=1
	print("Percentage of syllables that are part of a multi: "+str((multCount/totSylls)*100)[0:4]+"%")
	#multCountList
	for i in range(len(multCountList)):
		if multCountList[i]!=0:
			print(str(len(multCountList)-i+1)+"-syllable multi rhymes: "+str(multCountList[i]))

#INFO DISPLAY
def printInfo():
	for syll in syllList:
		print(syll.syll+"\t",end='')
		print(syll.pho+"\t",end='')
		print(syll.pos+"\t",end='')
		print('wordNo: '+str(syll.wordNo)+"\t",end='')
		print('lineNo: '+str(syll.lineNo)+"\t",end='')
		print('emph: '+str(syll.emph)+"\t",end='')
		print('rNo: '+str(syll.rNo)+"\t",end='')
		print('multi: '+str(syll.multi)+"\t",end='')
		print(syll.wholeWord+"\t",end='')
		print(syll.textUnit+"\t",end='')
		print()









'''
MAIN=================================================================
'''

filePath="lyrics.txt"


VOWELNOS=['0','1','2'] #in phonetic.txt, vowel phonemes end in one of these ints
EMPHNOS=[1,2,3] #1 and 2 from phnonetic.txt, 3 from specially placed stress
VOWELS=['A','E','I','O','U','Y','a','e','i','o','u','y']
PUNCT=['.',',','!','?',':',';','\"','(',')','[',']','*','^','~', '-']

phDict={}		#dict- {word: vowel phonemes} from phonetic.txt
phDict2={} 		#dict- {word: all phonemes} from phonetic.txt
syllDict={}		#dict- {word: syllables} from hyph.txt
wordList=[] 	#list- Word objects representing each lyric in lyrics.txt
syllList=[] 	#list of lists. Each inner list holds a syllable's characters, its vowel phoneme, its emphasis, the number of the word it came from, and its multi rhyme ID
multCountList=[]#used in markMultRhymes() to represent how many of each length of multi syll rhyme was found
uniqDict={} 	#dictionary used to count number of unique words, after .fit()
lastMulti=[0] 
totRhymeSylls=0 


softPOS=['DT','IN','CC','TO','PRP']
hardPOS=['NN','VB']
SIMSYLLS1=['AH','IH','ER']
SIMSYLLS2=['AA','AO']
SIMSYLLS3=['IH','IY']
EXCEPTIONS=['all','both']
ILIST=['i','i\'m','i\'d','i\'ma','i\'ll']

colorList=[fg(230,0,0),fg(0,175,0),fg(0,128,255),
			fg(230,230,0),fg(255,0,255),fg(0,255,255),
			fg(255,128,0),fg(150,255,150),fg(150,20,255),
			fg(245,174,220), fg(150,150,0), fg(155,84,130),
			fg(128,255,50), fg(165,35,0), fg(255,150,100)]

bgList=[bg(100,0,0),bg(0,100,0),bg(20,20,100),
			bg(100,100,0),bg(100,0,100),bg(0,100,100),
			bg(100,150,0),bg(100,0,150),bg(0,100,150),
			bg(150,100,0), bg(150,0,100), bg(0,150,100)]

colorDict={'AA': colorList[1], 'AE': colorList[0], 'AH': colorList[2], 
			'AW': colorList[3], 'AY': colorList[4], 'EH': colorList[5], 
			'ER': colorList[9], 'EY': colorList[7], 'IH': colorList[8], 
			'IY': colorList[6], 'OW': colorList[10], 'OY': colorList[13], 
			'UH': colorList[12], 'UW': colorList[11], 'AO': colorList[14]}


#build phDict and phDict2
tempList=[]
with open("phonetic.txt") as file:
	for line in file:
		phDict2.update({line.split()[0].lower(): line.split()[1:]})	#add all phonemes
		for word in line.split():
			if word[-1] in VOWELNOS and len(word)>1:	#only add vowel phonemes
				tempList.append(word)		#len(word)>1 to ignore the "1" and "2" entries
		phDict.update({line.split()[0].lower(): tempList})
		tempList=[]

#build syllDict
thisWord = ""
with open("hyph.txt") as file:
	for line in file:
		for syllable in line[0:-1].split('_'):	#line[0:-1] to clip trailing \n
			thisWord = thisWord + syllable
		syllDict.update({thisWord.lower(): line[0:-1].split('_')})
		thisWord=""


#CONSTRUCTION
# build syllList
# build uniqDict
with open(filePath) as file:
	lineNo=-1
	wordNo=-1
	for line in file:
		lineNo+=1
		for i in range(len(line.split())):
			for textUnit in re.findall('[^\s\-]+\-?', line.split()[i]):	#handle hyphenated words
				wordNo+=1
				thisPos = nltk.pos_tag([textUnit])[0][1]
				theseSylls = splitSylls(Word(textUnit))	#does not split if word is not in phDict
				if Word(textUnit).fit() in phDict:
					phoList = phDict[Word(textUnit).fit()]
				else:
					phoList = ['x']
				for i in range(len(phoList)):	#for each syllable of this word..
					syllList.append(Syllable(theseSylls[i]))
					syllList[-1].pho = phoList[i][0:-1]
					syllList[-1].pos = thisPos
					syllList[-1].lineNo = lineNo
					syllList[-1].wordNo = wordNo
					syllList[-1].wholeWord = Word(textUnit).fit()
					syllList[-1].textUnit = textUnit
					if phoList[i][-1] == 'x':
						syllList[-1].emph = 0
					else:
						syllList[-1].emph = int(phoList[i][-1])
					if len(phoList) == 1:
						syllList[-1].oneSyll = True

				#add to uniqDict
				if Word(textUnit).fit() not in uniqDict:
					uniqDict.update({Word(textUnit).fit():0})


#GENERATION
prune()
print("First Pass:")
printOut("emphs")
markSyllRhymes()
printOut("rhymes")
print()
for i in range(10, 1, -1):
	markMultiRhymes(exclusive=True, multiLen=i)
	markSyllRhymes()
	for syll in syllList:
		if syll.multi != 0:
			print(i)
			printOut('multis')
			printOut('rhymes')
			print()
			break
	clearMultis()


#printInfo()
#printStats()












