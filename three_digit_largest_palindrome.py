def three_digit_numbers():
	pal_list = []
	for i in range(100,1000):
		for j in range(100,1000):
			product = str(i*j)
			rev = str(product[::-1])
			if product == rev:
				pal_list.append(product)
	return (pal_list)


print(three_digit_numbers())