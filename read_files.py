# Python reading files (.txt, .csv, .json, .csv)

file_path = '/Users/nishchyakataria/Desktop/mop.rtfs'
try:
    with open(file_path, 'r') as file:
        content = file.read()
        print(content)
except FileNotFoundError:
    print("That file was not found.")
