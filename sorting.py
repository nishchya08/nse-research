# SORTING IN PYTHON .sort() AND sorted()
# Lists[], tuples(), dictionaries{}

# ------------Lists----------------

fruits = ['orange', 'apple', 'banana', 'kiwi', 'pear', 'grape']

#fruits.sort(reverse=True)  # sorts the list in place
#print(fruits)

# ------------Tuples----------------

fruits = ('orange', 'apple', 'banana', 'kiwi', 'pear', 'grape')
#fruits = tuple(sorted(fruits) )
fruits = tuple(sorted(fruits, reverse=True) ) 

#print(fruits)

# ------------Dictionaries----------------

fruits = {'orange': 105,
          'apple': 80,
          'banana': 75,
          'kiwi': 60,
          'pear': 90,
          'grape': 70}

#fruits = dict(sorted(fruits.items(), key=lambda item: item[0], reverse=True) )
fruits = dict(sorted(fruits.items(), key=lambda item: item[1], reverse=True) )


#print(fruits)


# ------------Objects----------------

class Fruit:
    def __init__(self, name, calories):
        self.name = name
        self.calories = calories

    def __repr__(self):
        return f"{self.name}: {self.calories}"
    
fruits = [Fruit('orange', 105),Fruit('apple', 80),Fruit('banana', 75),]

#fruits = sorted(fruits, key=lambda fruit: fruit.name, reverse=True)
fruits = sorted(fruits, key=lambda fruit: fruit.calories, reverse=True)

print(fruits)