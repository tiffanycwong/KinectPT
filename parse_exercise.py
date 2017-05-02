import os

exercise_num = sys.argv[1]
exercises = ["sumo kettlebell raise", "bent-over dumbbell raise"]
try:
	exercises[int(exercise_num)-1]
except ValueError:
	msg = "That was not a valid option. Restart programme and try again."
	os.system("say " + msg ) 
	