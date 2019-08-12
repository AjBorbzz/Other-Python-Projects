from collections import Counter
""" returns an integer matching a pair in a list """

def sockMerchant(num, ar):
	sockList = []
	sum = 0
	for values in Counter(ar).values():
		sum += values // 2
	return sum


num = 9
ar = [10,20,20,10,10,30,50,10,20]

print(sockMerchant(num,ar))
