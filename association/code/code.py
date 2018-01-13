import numpy as np
from itertools import combinations

SUPPORT = 0.5
CONFIDENCE = 0.7
global_d = {}
onefreq = []
TOTAL_ITEMS = 0
possible_rules = []
LARGEST_ITEM_SET = []


'''We created a dictionary with keys as the up or down entries and 
the values as the row index in which they occurred.
 This row index also represents the transaction id.
'''
def preprocess(filename):
    inpdata = np.genfromtxt(filename,delimiter = '\t')
    X = np.loadtxt(filename,delimiter = '\t', usecols = range(inpdata.shape[1]-1), dtype = 'S15')
    labels = np.loadtxt(filename,delimiter = '\t', usecols = inpdata.shape[1]-1, dtype = 'S15')
    for i in xrange(0, X.shape[0]):
    	for j in xrange(0, X.shape[1]):
    		X[i][j] = "G" +str(j+1) + "_"+str(X[i][j])
    return X, labels


''' Global dictionary creates key , value pairs of elements occurence '''
def makeGlobalDictionary(X):
	dictstruct = {}
	for i in xrange(X.shape[0]):
		for j in xrange(X.shape[1]):
			if(X[i][j] in dictstruct):
				dictstruct[X[i][j]].append(i+1)
			else:
				dictstruct[X[i][j]] = [i+1]
	return dictstruct


'''
calPruningVol creates a key value table of length one frequent item sets and the transactions where they occurred.
 It also filters the keys which have the no of transaction less than the support value 0.5 initially.
'''
def calPruningVol(X):
	thresh_count = X.shape[0]*SUPPORT
	toremove = []
	for key, val in global_d.iteritems():
		if(len(val) < thresh_count):
			toremove.append(key)
	for i in toremove:
		global_d.pop(i, None)
	'''
	for key, val in global_d.iteritems():
		print(str(key) + " - " + str(val))
	'''
	return thresh_count


def interTrans(transactions):
	if(len(transactions) > 0):
		ans = set(global_d[transactions[0]])
	for i in range(1, len(transactions)):
		ans = ans.intersection(global_d[transactions[i]])
	return list(ans)

'''
function calPruning recursively calls itself with a variable step which increments by one. 
This function creates frequency of length 2,3,4,5 and so on recursively. 
The values are the transactions where keys occur simultaneously.
 This function also filters the keys which do not fulfill the support requirement.

'''

def calPruning(dictionary, thresh_count, freq, step):
	global TOTAL_ITEMS
	global LARGEST_ITEM_SET
	newdict = {}
	newfreq = []

	for i in freq:
		for j in onefreq:
			key = i + j
			key = list(set(key))
			key.sort()
			key_tuple = tuple(key)
			if(len(key) == step and key_tuple not in newdict):
				commonTrans = interTrans(key_tuple)
				newdict[key_tuple] = commonTrans
	toremove = []

	for key, val in newdict.iteritems():
		if(len(val) < thresh_count):
			toremove.append(key)
		else:
			newfreq.append(list(key))
	for i in toremove:
		newdict.pop(i, None)
		'''
	for key, val in newdict.iteritems():
		print(str(key) + " - " + str(val))
		'''
	print("Number of length " + str(step) + " frequent itemsets are : "+ str(len(newfreq)))

	TOTAL_ITEMS += len(newfreq)
	LARGEST_ITEM_SET.append(dictionary.keys())
	if(len(newfreq) == 0):
		return LARGEST_ITEM_SET

	return calPruning(newdict, thresh_count, newfreq, step+1)	


'''
	This function returns a boolean True if transaction fulfills the confidence requirement else returns False.
'''
def fulfil_thresh_confidence(keys, values):
	keys = list(keys)
	values = list(values)
	numerator = len(interTrans(keys+values))
	denominator = len(interTrans(keys))
	if(float(numerator)/denominator >= CONFIDENCE):
		return True
	return False

'''
Once we get all possible key, value pairs starting from length - 2 till the maximum length pairs, 
we generate rules using the function generate_possible_rules. The generate_possible_rules also filters the rules which do not fulfil the confidence requirements.
'''

def generate_possible_rules(largest_item_set):
	possible_rules = []
	for itemset in largest_item_set:
		for frequent_item in itemset:
			for i in range(1, len(frequent_item)):
				comb = list(combinations(frequent_item, i))
				for c in comb:
					keys = c
					values = set(frequent_item)-set(c)
					if(fulfil_thresh_confidence(keys, values) == True):
						possible_rules.append([keys, list(values)])
	return possible_rules

def is_list_common(list1, list2):
	intersection = set(list1).intersection(list2)
	if(len(intersection) == 0):
		return False
	return True

'''
Filters the queries using keywords
'''
def asso_rule_template1(type, param, item):
	print("Keywords are : " + str(type) + " " + str(param) + " " + str(item))
	final_rule = []
	if(type == "RULE"):
		if(param == "ANY"):
			for rule in possible_rules:
				if(is_list_common(item, rule[0]) or is_list_common(item, rule[1])):
					final_rule.append(rule)
		elif(param == "NONE"):
			for rule in possible_rules:
				if(is_list_common(item, rule[0]) == False and is_list_common(item, rule[1]) == False):
					final_rule.append(rule)
		elif(param == "1"):
			for rule in possible_rules:
				if(is_list_common(item, rule[0]) and is_list_common(item, rule[1])):
					pass
				elif(is_list_common(item, rule[0]) or is_list_common(item, rule[1])):
					final_rule.append(rule)
	elif(type == "BODY"):
		if(param == "ANY"):
			for rule in possible_rules:
				if(is_list_common(item, rule[0])):
					final_rule.append(rule)
		elif(param == "NONE"):
			for rule in possible_rules:
				if(is_list_common(item, rule[0]) == False):
					final_rule.append(rule)
		elif(param == "1"):
			for rule in possible_rules:
				if(is_list_common(item, rule[0])):
					final_rule.append(rule)
	elif(type == "HEAD"):
		if(param == "ANY"):
			for rule in possible_rules:
				if(is_list_common(item, rule[1])):
					final_rule.append(rule)
		elif(param == "NONE"):
			for rule in possible_rules:
				if(is_list_common(item, rule[1]) == False):
					final_rule.append(rule)
		elif(param == "1"):
			for rule in possible_rules:
				if(is_list_common(item, rule[1])):
					final_rule.append(rule)

	return final_rule

'''
Filters the queries using keywords
'''

def asso_rule_template2(type, count):
	print("Keywords are : " + str(type) + " " + str(count))
	final_rule = []
	if(type == "RULE"):
		for rule in possible_rules:
			if(len(rule[0]) + len(rule[1]) >= count):
				final_rule.append(rule)
	elif(type == "BODY"):
		for rule in possible_rules:
			if(len(rule[0]) >= count):
				final_rule.append(rule)
	elif(type == "HEAD"):
		for rule in possible_rules:
			if(len(rule[1]) >= count):
				final_rule.append(rule)
	return final_rule

'''
Filters the queries using keywords
'''

def asso_rule_template3(template, *argum):
	print("Keywords are : " + str(template) + " " + str(argum))
	index1 = template[0]
	index2 = template[-1]
	first_rule = []
	second_rule = []
	final_rule = []
	if(index1 == "1"):
		first_rule = asso_rule_template1(argum[0], argum[1], argum[2])
	if(index1 == "2"):
		first_rule = asso_rule_template2(argum[0], int(argum[1]))
	if(index2 == "1"):
		second_rule = asso_rule_template1(argum[-3], argum[-2], argum[-1])
	if(index2 == "2"):
		second_rule = asso_rule_template2(argum[-2], int(argum[-1]))

	if("and" in template):
		for i in first_rule:
			if i in second_rule:
				final_rule.append(i)
	else:
		for i in first_rule:
			final_rule.append(i)
		for j in second_rule:
			if j not in final_rule:
				final_rule.append(j)
	return final_rule

def main():
	global global_d
	global onefreq
	global possible_rules
	global TOTAL_ITEMS
	global LARGEST_ITEM_SET
	largest_item_set = 0
	X, labels = preprocess("associationruletestdata.txt")
	#X = np.array([['A','B','C','D'], ['D', 'E', 'B', 'F'], ['B','A','C','F'], ['A','F', 'D', 'C']])
	labels = labels.reshape(labels.shape[0], 1)
	X = np.concatenate((X, labels), axis=1)
	#print(labels)
	global_d = makeGlobalDictionary(X)
	
	threshhold_count = calPruningVol(X)
	for key, val in global_d.iteritems():
		onefreq.append([key])
	TOTAL_ITEMS += len(onefreq)
	print("*----------------------------------------------------------*")
	print("Number of length 1 frequent itemsets are : "+ str(len(onefreq)))
	largest_item_set = calPruning(global_d, threshhold_count, onefreq, 2)
	print("*----------------------------------------------------------*")
	print("Total frequent item sets are : " + str(TOTAL_ITEMS))
	possible_rules = generate_possible_rules(largest_item_set[1:])

	
	print("*----------------------------------------------------------*")
	print("Total possible rules are : ")
	print(len(possible_rules))
	'''
	for i in possible_rules:
		print(i)
	'''
	print("*----------------------------------------------------------*")
	
	all_results = []
	result11  = asso_rule_template1("RULE", "ANY", ["G59_Up"])
	print("Count of Rule :", len(result11))
	print("*----------------------------------------------------------*")
	result12  = asso_rule_template1("RULE", "NONE", ["G59_Up"])
	print("Count of Rule :", len(result12))
	print("*----------------------------------------------------------*")
	result13  = asso_rule_template1("RULE", "1", ["G59_Up", "G10_Down"])
	print("Count of Rule :", len(result13))
	print("*----------------------------------------------------------*")
	result14  = asso_rule_template1("BODY", "ANY", ["G59_Up"])
	print("Count of Rule :", len(result14))
	print("*----------------------------------------------------------*")
	result15  = asso_rule_template1("BODY", "NONE", ["G59_Up"])
	print("Count of Rule :", len(result15))
	print("*----------------------------------------------------------*")
	result16  = asso_rule_template1("BODY", "1", ["G59_Up", "G10_Down"])
	print("Count of Rule :", len(result16))
	print("*----------------------------------------------------------*")
	result17  = asso_rule_template1("HEAD", "ANY", ["G59_Up"])
	print("Count of Rule :", len(result17))
	print("*----------------------------------------------------------*")
	result18  = asso_rule_template1("HEAD", "NONE", ["G59_Up"])
	print("Count of Rule :", len(result18))
	print("*----------------------------------------------------------*")
	result19  = asso_rule_template1("HEAD", "1", ["G59_Up", "G10_Down"])
	print("Count of Rule :", len(result19))
	print("*----------------------------------------------------------*")

	result21 = asso_rule_template2("RULE", 3)
	print("Count of Rule :", len(result21))
	print("*----------------------------------------------------------*")
	result22 = asso_rule_template2("BODY", 2)
	print("Count of Rule :", len(result22))
	print("*----------------------------------------------------------*")
	result23 = asso_rule_template2("HEAD", 1)
	print("Count of Rule :", len(result23))
	print("*----------------------------------------------------------*")
	result31  = asso_rule_template3("1or1", "BODY", "ANY" ,["G10_Down"], "HEAD", "1", ["G59_Up"])
	print("Count of Rule :", len(result31))
	print("*----------------------------------------------------------*")
	result32  = asso_rule_template3("1and1", "BODY", "ANY" ,["G10_Down"], "HEAD", "1", ["G59_Up"])
	print("Count of Rule :", len(result32))
	print("*----------------------------------------------------------*")
	result33  = asso_rule_template3("1or2", "BODY", "ANY" ,["G10_Down"], "HEAD", 2)
	print("Count of Rule :", len(result33))
	print("*----------------------------------------------------------*")

	result34  = asso_rule_template3("1and2", "BODY", "ANY" ,["G10_Down"], "HEAD", 2)
	print("Count of Rule :", len(result34))
	print("*----------------------------------------------------------*")
	result35  = asso_rule_template3("2or2", "BODY", 1, "HEAD", 2)
	print("Count of Rule :", len(result35))
	print("*----------------------------------------------------------*")
	result36  = asso_rule_template3("2and2", "BODY", 1, "HEAD", 2)
	print("Count of Rule :", len(result36))
	print("*----------------------------------------------------------*")

	'''
	all_results = [result11, result12, result13, result14, result15, result16, result17, result18, result19, result21, result22, result23, result31, result32, result33, result34, result35, result36]
	
	for rule in all_results:
		print("*----------------------------------------------------------*")
		print("Count of Rule :", len(rule))
		print("Selected rules are :")
		
		for i in rule:
			print("Body : ", i[0], "Head : ", i[1])
		
		print("*----------------------------------------------------------*")
	'''
if __name__=='__main__':
	main()