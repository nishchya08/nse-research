# lamnda function = A small function for a long time use (throw away function)
#  They can take any number of arguments, but only have one expression.
# Helps keep the namespace clean and is useful with higher order functions
# sorted(), filter(), map()

double = lambda x: x * 2
add = lambda x,y : x + y
max = lambda x, y: x if x>y else y
full_name = lambda first, last: first + ' ' + last
is_even = lambda num: num % 2 == 0
age_check = lambda age: True if age >= 18 else False
#print(age_check(18))
#print(is_even(78))
#print(full_name('Nishchya', 'Kataria'))
#print(max(5,10))
#print(add(5,7))
#print(double(7))

# map() = Applies a given function to all items in a collection

#def c_to_f(temp):
#    return ((9/5) *  temp) + 32

celsius_temp = [0.0, 10.0, 20.0, 34.5]
farenheit_temp = list(map(lambda temp: ((9/5) *  temp) + 32, celsius_temp))
for temp in farenheit_temp:
    print(temp)