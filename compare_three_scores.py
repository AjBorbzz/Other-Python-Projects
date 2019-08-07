if __name__ == '__main__':
	a = [5,6,7]
	b = [3,6,10]

	""" comparison:
	    if a > b , a += 1
	    if a < b , b += 1
	    if a == b, a=a, b=b
	"""
	point_a = 0
	point_b = 0
	l = zip(a,b)
	for x,y in l:
		if x > y:
			print("a is greater than b")
			point_a += 1
		elif x < y:
			print("b is greater than a")
			point_b += 1
		elif x == y:
			point_a = point_a
			point_b = point_b
	print([point_a,point_b])
	print("total points :\na\tb\n{}\t{}".format(point_a, point_b))