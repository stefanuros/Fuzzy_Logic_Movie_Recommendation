import csv
import math
from random import shuffle, choice

################################## IMPORTANT ##################################
# You will need to install numpy using pip ex. "pip install numpy"
import numpy as np

# global movies list
movies = {}

# Function to read CSV files
def readCSV(fn):
	lis = []

	with open(fn, newline='', encoding='utf-8') as f:
		reader = csv.reader(f)
		for row in reader:
			lis.append(row)

	return lis[1:]


# Function that creates a list of id-movie combos into a dict
def createMovieDict():
	global movies

	movieList = [x[:2] for x in readCSV('ml-latest-small/movies.csv')]
	
	for i in movieList:
		# Remove the year from the title
		m = " ".join(i[1].split(" ")[:-1])
		movies[i[0]] = m.lower()


# Function to create a dictionary of users
def parseUsers():
	# Get the user ratings
	userRatings = readCSV('ml-latest-small/ratings.csv')

	# Put them into a dictionary
	users = {}

	for i in userRatings:
		# Get the user variables
		u = i[0] # User id
		m = movies[i[1]] # Movie name
		r = float(i[2]) / 5 # rating limited to range of [0 .. 1]

		# If the user already has a section in the dict, user that
		if u in users:
			# Add the rating for the movie
			users[u][m] = r
		# Otherwise create a new section
		else:
			# Add the rating for the movie
			users[u] = {m: r}


	# Return the new user dictionary
	return users

# Function to read in ratings from standard input
def getInput():
	print("Enter the name of a movie followed by a space then a rating from 0-5 stars, decimals are allowed")
	print("Example: Toy Story 4.5")
	print("The movie title must follow exactly what is in the 'movies.csv' spreadsheet")
	print("Enter as many as you would like and then type 'quit' to quit")

	userData = {}

	userIn = input()

	while userIn.lower() != "quit":	

		try:
			userIn = userIn.split(" ")

			m = " ".join(userIn[:-1]).lower()
			r = float(userIn[-1]) / 5

			# Error checking
			if (r > 1):
				print("Rating too high")
				raise Exception
			elif (r < 0):
				print("Rating too low")
				raise Exception

			if (m not in list(movies.values())):
				print("Movie not in list. Please enter another one")
				raise Exception

			# Add value to dictionary
			userData[m] = r
		except:
			print("You did something wrong. Please try again")
		
		userIn = input()

	print("Here is your membership set:")
	print(userData)
	return userData


# The following 2 functions come from this website
# https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249

# Returns the unit vector of vector
def unit_vector(vector):
	return vector / np.linalg.norm(vector)

# Returns the angle between vector 1 and 2
def angle_between(v1, v2):
	v1_u = unit_vector(v1)
	v2_u = unit_vector(v2)
	return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


# Function to compare similarity of movies
# a is from the list of user ratings
# b is the user entering their movie ratings
def sim(a, b):
	# First get a set of movies that both users have watched
	aMovies = set(list(a.keys()))
	bMovies = set(list(b.keys()))

	# Get the list of movies both users have watched
	both = list(aMovies.intersection(bMovies))

	# They have not watched the same movies, so dont include them
	if(len(both) <= 0):
		return 0
	elif(len(both) == 1):
		# Calculate a specific value when there is a single movie
		return 1 - abs(a[both[0]] - b[both[0]])

	# They have watched all the same movies so there are no new suggestions to be gained
	if(aMovies.issubset(bMovies)):
		return 0


	aFuzz = []
	bFuzz = []

	# Loop through the movies and create a fuzzy set for a and b
	for m in both:
		aFuzz.append(a[m])
		bFuzz.append(b[m])

	# Calculate the similarity
	return math.cos(angle_between(aFuzz, bFuzz))


# Function to compare the list of ratings (ratings) to the ratings the user created (user)
def compareRatings(ratings, user):
	
	# The list of similarty each rater has with the user
	simVal = []

	# Loop through the ratings list
	for k, v in ratings.items():
		simVal.append([k, sim(v, user)])

	# Sort the list based on the similarity
	simVal.sort(key=lambda x: x[1])
	simVal.reverse()

	# Return the 25 people with the highest ratings
	return simVal[:25]


# Function to get a list of movies that a user has rated
def getRatedMovies(ratingList, id):
	return ratingList[id].keys()

# Function that takes a list of raters and suggests movies the user hasn't watched
def suggestMovies(ratingList, matches, user):

	# Get the list of movies the user has watched so we dont suggest those
	watchedMovies = set(list(user.keys()))

	suggested = []

	for i in matches:
		# Add the movies that the rater has rated
		suggested += getRatedMovies(ratingList ,i[0])

	# Get rid of any duplicated
	suggested = set(suggested)
	# Remove the movies the user has already watched
	suggested = list(suggested.difference(watchedMovies))

	shuffle(suggested)

	print("Below are some suggested movies for you based on your ratings:")
	for i in range(15):
		print("\t" + suggested[i])


# Main Function
def main():
	# Create the dictinary of movies
	createMovieDict()

	# Get the list of user ratings
	ratingList = parseUsers()

	print("Press 'y' to use random ratings, or press anything else to create your own movie ratings")
	if(input() == "y"):
		print("Here is the membership set you will be using:")
		# Get a random raters ratings
		randKey = choice(list(ratingList.keys()))
		userRating = ratingList[randKey]
		# Remove that raters ratings from the dictionary
		del ratingList[randKey]
		print(userRating)
	else:
		# Get ratings from user
		userRating = getInput()

	# Compare the ratings from the user to the database of ratings
	highestMatches = compareRatings(ratingList, userRating)

	suggestMovies(ratingList, highestMatches, userRating)

main()
