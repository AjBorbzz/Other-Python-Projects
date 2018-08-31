""" An anti-Lychrel number is a number that forms a palindrome through the iterative process of repeatedly
    reversing its digits and adding the resulting numbers. For example, 56 becomes palindromic after one iteration: 56+65 = 121.
    If the number doesn't become palindromic after 30 iterations, then it is not an anti-Lychrel number. 

    examples:
    Input = 12
    Output = true (12 +21 = 33, a palindrome)

    Input = 57
    Output = true (57+75 = 132, 132 + 231 = 363, palindrome)

    input = 10911
    output = false(10911 takes 55 iterations to reach a palindrome)
"""

#Write a program to check if the user input is an anti-Lychel number or not.

def anti_Lychrel(number):
	pass

def reverse(s):
	return s[::-1]

def sum(s,l):
	x = int(s) + int(l)
	return str(x)

def isPalindrome(s):
	rev = reverse(s)
	if(s == rev):
		return True
	return False

user_num = input("Enter a number: ")
rev_num = reverse(user_num) #user_num : 12
NumSum = sum(rev_num,user_num) #NumSum : 33
counter = 1
#write loops
while True:
	ans = isPalindrome(NumSum)
	if (ans == 1) and (counter <= 30):
		print("True, " + str(NumSum) + " is a Palindrome, Attempted: " + str(counter) + " time/s")
		break
	else:
		if(counter > 500):
			print("False, takes " + str(counter) + " iterations to reach a palindrome")
			break
		else:
			rev_ans = reverse(NumSum)
			NumSum = sum(NumSum,rev_ans)
			NumSum = str(NumSum)
	counter += 1
	if (counter == 1000): break
