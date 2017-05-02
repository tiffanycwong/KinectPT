import csv
import os
import sys
import math
import random

filename = sys.argv[1]
exercise_num = sys.argv[2]
exercises = ["sumo kettlebell raise", "bent-over dumbbell raise"]
exercise = exercises[int(exercise_num) - 1]


POSITIVE_WORDS = ["Good job!", "Killed it!", "Congrats!","Baller status!"]

sayYN = True
if len(sys.argv) > 2: 
	if sys.argv[2] == 'no':
		sayYN = False
print 'Processing: ' + filename

with open(filename, 'r') as f:
  reader = csv.reader(f)
  data = list(reader)


# remove last 10 frames 
data = data[1:-10]
data = [[float(y) for y in x] for x in data]
# print len(data)
# get frame w/ max wrist 

jointIndexDict = {
	"user" : 0,
	"timestamp" : 1,
	"comx" : 2,
	"comy" : 3,
	"comz" : 4,
	"headx" : 5,
	"heady" : 6,
	"headz" : 7,
	"neckx" : 8,
	"necky" : 9,
	"neckz" : 10,
	"leftshoulderx" : 11,
	"leftshouldery" : 12,
	"leftshoulderz" : 13,
	"leftelbowx" : 14,
	"leftelbowy" : 15,
	"leftelbowz" : 16,
	"lefthandx" : 17,
	"lefthandy" : 18,
	"lefthandz" : 19,
	"rightshoulderx" : 20,
	"rightshouldery" : 21,
	"rightshoulderz" : 22,
	"rightelbowx" : 23,
	"rightelbowy" : 24,
	"rightelbowz" : 25,
	"righthandx" : 26,
	"righthandy" : 27,
	"righthandz" : 28,
	"torsox" : 29,
	"torsoy" : 30,
	"torsoz" : 31,
	"lefthipx" : 32,
	"lefthipy" : 33,
	"lefthipz" : 34,
	"leftkneex" : 35,
	"leftkneey" : 36,
	"leftkneez" : 37,
	"leftfootx" : 38,
	"leftfooty" : 39,
	"leftfootz" : 40,
	"righthipx" : 41,
	"righthipy" : 42,
	"righthipz" : 43,
	"rightkneex" : 44,
	"rightkneey" : 45,
	"rightkneez" : 46,
	"rightfootx" : 47,
	"rightfooty" : 48,
	"rightfootz" : 49
}

def joint_data(joint_name, frame):
	jointIndex = jointIndexDict[joint_name]
	return frame[jointIndex]

# best: "max" or "min"
# joint: should specify x, y or z
def select_frame(data, joint, best):
	best_frame = None
	best_value = -10000 if best == "max" else 10000
	joint_index = jointIndexDict[joint]

	frame_number = -1
	frame_count = 0
	for frame in data:
		frame_count += 1
		current_value = frame[joint_index]
		if (best == "max" and (current_value > best_value)) or (best == "min" and (current_value < best_value)):
			best_value = current_value
			best_frame = frame
			frame_number = frame_count
	# print best_value	
	# print 'Looking at frame: ' + str(frame_number+1)
	# print best_frame[1]
	return best_frame 

##################################################
# CONSTANTS TO USE FOR THE SUMO KETTLEBELL RAISE #
##################################################
# Originals
	# HANDS_Y_DIFF = 12
	# ELBOWS_Y_DIFF = 30
	# HEIGHT_DIFF_1 = 60
	# HEIGHT_DIFF_2 = 20
	# PARALLEL_TO_GROUND_DIFF = 10

def normalization_forearm_length_data_in_frame(frame):
	## Grab the length of the elbow to hand for both left and right and determine the length
	left_hand_x = joint_data("lefthandx", frame)
	right_hand_x = joint_data("righthandx", frame)
	left_elbow_x = joint_data("leftelbowx", frame)
	right_elbow_x = joint_data("rightelbowx", frame)
	left_hand_y = joint_data("lefthandy", frame)
	right_hand_y = joint_data("righthandy", frame)
	left_elbow_y = joint_data("leftelbowy", frame)
	right_elbow_y = joint_data("rightelbowy", frame)

	rightForearmLength = math.sqrt((right_hand_x - right_elbow_x)**2 + (right_hand_y - right_elbow_y)**2)
	leftForearmLength = math.sqrt((left_hand_x - left_elbow_x)**2 + (left_hand_y - left_elbow_y)**2)

	return (rightForearmLength+leftForearmLength)/2

def updated_analyzer_sumo_kettlebell_raise(frame, constants):
	PASSED = [True, True, True]

	messageToUser = ''

	AVG_FOREARM_LENGTH = normalization_forearm_length_data_in_frame(frame)

	# Constants that are used for the tests
	ELBOW_HAND_Y_DIFF_AVG = constants["ELBOW_HAND_Y_DIFF_AVG"]
	HANDS_MIN_DIST_FROM_NECK_X = constants["HANDS_MIN_DIST_FROM_NECK_X"]
	HANDS_MIN_DIST_FROM_NECK_Y_TOO_LOW = constants["HANDS_MIN_DIST_FROM_NECK_Y_TOO_LOW"]
	HANDS_MIN_DIST_FROM_NECK_Y_TOO_HIGH = constants["HANDS_MIN_DIST_FROM_NECK_Y_TOO_HIGH"]

	DIFFERENCE_BETWEEN_ELBOWS = constants["DIFFERENCE_BETWEEN_ELBOWS"]


	## Get the values that we are interested in
	neck_x = joint_data("neckx", frame)
	left_hand_x = joint_data("lefthandx", frame)
	right_hand_x = joint_data("righthandx", frame)
	left_elbow_x = joint_data("leftelbowx", frame)
	right_elbow_x = joint_data("rightelbowx", frame)
	neck_y = joint_data("necky", frame)
	left_hand_y = joint_data("lefthandy", frame)
	right_hand_y = joint_data("righthandy", frame)
	left_elbow_y = joint_data("leftelbowy", frame)
	right_elbow_y = joint_data("rightelbowy", frame)

	## First feedback is going to be whether or not they are doing the right pose.
	## To determine this, look at the positions of joints to one another in both x and y plane
	## There will be 3 tests:
	##	(1) Joint order in x goes left elbow, left hand, right hand, right elbow
	##	(2) Are the elbows and hands roughly at the same height
	##	(3) Are the hands a min distance from the neck x direction (y direction will be left for feedback)
	## Test 1:
	if not (left_elbow_x < left_hand_x and left_hand_x < right_hand_x and right_hand_x < right_elbow_x):
		## Failed the first test
		messageToUser = 'It looks like you are doing the wrong exercise. Make sure your elbows don\'t move as your hands move straight up towards your head.'
		# print messageToUser
		PASSED[0] = False

	## Test 2: many ways to do this. For now, find the difference of all points relative to one another
	test2yDists = {}
	yKeys = ["lefthandy","righthandy","leftelbowy","rightelbowy"]
	for i in yKeys:
		for j in yKeys:
			test2yDists[i,j] = abs(joint_data(i, frame) - joint_data(j, frame))

	## Calculate the average distance. Iteration is only on the diagonal matrix
	totalDiff = 0
	numKeys = len(yKeys)
	for i in xrange(numKeys):
		iKey = yKeys[i]
		for j in xrange(i+1, numKeys):
			jKey = yKeys[j]
			totalDiff += test2yDists[iKey, jKey]

	## Check if that's below a threshold
	if (((1.0*totalDiff)/numKeys)/AVG_FOREARM_LENGTH) > (1.0*ELBOW_HAND_Y_DIFF_AVG / AVG_FOREARM_LENGTH):
		## Failed second test
		messageToUser = 'It looks like you are doing the wrong exercise.'
		PASSED[1] = False

	## Test 3:
	totalDistanceFromNeckInX = abs(left_hand_x - neck_x) + abs(right_hand_x - neck_x)
	# print totalDistanceFromNeckInX
	if totalDistanceFromNeckInX/AVG_FOREARM_LENGTH > HANDS_MIN_DIST_FROM_NECK_X/AVG_FOREARM_LENGTH:
		messageToUser = 'It looks like you are doing the wrong exercise.'
		PASSED[2] = False

	##### Now time for feedback! 3 types of feedback possible:
	## (1) Make sure your arms are raised high enough but now too high. 
	##This is based on the distance between your hands and your neck
	## (2) Make sure your arms are raised evenly
	## (3) Make sure your arms are parrallel to the ground

	FEEDBACK = 'J'

	## Feedback 1
	## Too high would be too close to or above the neck Y and too low would be to far from the neck Y
	totalDistanceFromNeckInY = (left_hand_y - neck_y) + (right_hand_y - neck_y)

	avgDistanceFromNeckInY = totalDistanceFromNeckInX/2

	# print 'Dist from neck: ' + str(avgDistanceFromNeckInY)
	# print 'Too low cut: ' + str(HANDS_MIN_DIST_FROM_NECK_Y_TOO_LOW)
	# print 'Too high cut: ' + str(HANDS_MIN_DIST_FROM_NECK_Y_TOO_HIGH)

	if (avgDistanceFromNeckInY/AVG_FOREARM_LENGTH) < HANDS_MIN_DIST_FROM_NECK_Y_TOO_HIGH/AVG_FOREARM_LENGTH:
		## Arms are too high!
		messageToUser = 'You are raising your arms too high'
		FEEDBACK='H'
		# print messageToUser
	elif (avgDistanceFromNeckInY/AVG_FOREARM_LENGTH) > HANDS_MIN_DIST_FROM_NECK_Y_TOO_LOW/AVG_FOREARM_LENGTH:
		messageToUser = 'You are raising your arms too low'
		FEEDBACK='L'
		# print messageToUser
	else:
		positive_word = random.choice(POSITIVE_WORDS)
		messageToUser = 'You are raising your arms to the right height '+ positive_word


	distanceBetweenElbows = abs(left_hand_y - right_hand_y)
	if distanceBetweenElbows/AVG_FOREARM_LENGTH > DIFFERENCE_BETWEEN_ELBOWS/AVG_FOREARM_LENGTH:
		messageToUser = 'Raise your arms evenly next time!'
		FEEDBACK2 = 'NE'
	else:
		positive_word = random.choice(POSITIVE_WORDS)
		messageToUser = positive_word + ' You raised your arms evenly you are so smart!'
		FEEDBACK2 = 'E'

	return {
		'PASSED': PASSED,
		'FEEDBACK': FEEDBACK,
		'FEEDBACK2': FEEDBACK2
	}



# Gives feedback on based on the data that was collected
# Arguments:
# 	position: what exercise is being done (as a string)
# 	data: all of the data collected in the run
# 	constants: the constants for the classifier (refer to that function to know what they mean)
def analyze_data(position, data, constants):
	## For sumo kettlebell raise, we look at the frame where the lefthandy is max right now and consider
	## that frame
	finalResults = {
		'PASSED':[False, False, False],
		'FEEDBACK': [],
		'FEEDBACK2': []
	}
	if position == "sumo kettlebell raise":
		toCheck = ["lefthandy", "righthandy"]
		# toCheck = ["lefthandy"]
		# toCheck = ["righthandy"]
		for val in toCheck:
			frame = select_frame(data, val, "max")
			currResults = updated_analyzer_sumo_kettlebell_raise(frame,constants)
			for i in xrange(len(currResults['PASSED'])):
				if currResults['PASSED'][i]:
					finalResults['PASSED'][i] = True
			finalResults['FEEDBACK'].append(currResults['FEEDBACK'])
			finalResults['FEEDBACK2'].append(currResults['FEEDBACK2'])

	### Now give feedback!
	print("---------------------------------------------------------------------------")
	for key in ['PASSED','FEEDBACK','FEEDBACK2']:
		messageToUser = ""
		if key == "PASSED":
			if not finalResults[key][0]:
				messageToUser = 'It looks like you are doing the wrong exercise. Make sure your elbows dont move as your hands move straight up towards your head.'
				print messageToUser
				os.system("say " + messageToUser)
				break
			elif not finalResults[key][1]: 
				messageToUser = 'It looks like you are doing the wrong exercise.'
				print messageToUser
				os.system("say " + messageToUser)
				break
			elif not finalResults[key][2]:
				messageToUser = 'It looks like you are doing the wrong exercise.'
				print messageToUser
				os.system("say " + messageToUser)
				break

		if key == 'FEEDBACK':
			key = finalResults[key][0] + finalResults[key][0]
			if key == 'LL':
				messageToUser = 'You need to raise your arms higher'
				print messageToUser
				os.system("say " + messageToUser)
			elif key == 'HH':
				messageToUser = 'You are raising your arms too high!'
				print messageToUser
				os.system("say " + messageToUser)
			else:
				messageToUser = 'You are raising your arms to the right height good job!'
				print messageToUser
				os.system("say " + messageToUser )

		if key == 'FEEDBACK2':
			key = finalResults[key][0] + finalResults[key][0]
			if key == 'NENE':
				messageToUser = 'Raise your arms evenly next time!'
				print messageToUser
				os.system("say " + messageToUser )
			else:
				messageToUser = 'Congrats! You raised your arms evenly you are so smart!'
				print messageToUser
				os.system("say " + messageToUser )

	return finalResults

CONSTS = {
	'ELBOW_HAND_Y_DIFF_AVG': 220,
	'HANDS_MIN_DIST_FROM_NECK_X': 200,
	'HANDS_MIN_DIST_FROM_NECK_Y_TOO_LOW': 170,
	'HANDS_MIN_DIST_FROM_NECK_Y_TOO_HIGH': 20,
	'DIFFERENCE_BETWEEN_ELBOWS': 40
}



res = analyze_data(exercise, data, CONSTS)

####### TESTING BELOW


# resultsCorrectPos = {
# 	'000':0,
# 	'001':0,
# 	'010':0,
# 	'011':0,
# 	'100':0,
# 	'101':0,
# 	'110':0,
# 	'111':0,
# 	'twoCorrect': 0
# }

# feedbackGiven = {
# 	'HH': 0,
# 	'HL': 0,
# 	'HJ':0,
# 	'JH': 0,
# 	'JL': 0,
# 	'JJ':0,
# 	'LH': 0,
# 	'LL': 0,
# 	'LJ':0
# }

# printed1 = False
# tt = 150
# # for c1 in xrange(100, 200, 10):
# for c1 in [170]:
# 	# print c1
# 	# for c2 in xrange(0, 80, 10):
# 	for c2 in [20]:
# 		CONSTS = {
# 			'ELBOW_HAND_Y_DIFF_AVG': 220,
# 			'HANDS_MIN_DIST_FROM_NECK_X': 200,
# 			'HANDS_MIN_DIST_FROM_NECK_Y_TOO_LOW': c1,
# 			'HANDS_MIN_DIST_FROM_NECK_Y_TOO_HIGH': c2,

# 		}
# 		res = analyze_data("sumo kettlebell raise", data, CONSTS)
# 		fullresultsCorrectPos = res['PASSED']
# 		if fullresultsCorrectPos[0]:
# 			if fullresultsCorrectPos[1]:
# 				if fullresultsCorrectPos[2]:
# 					resultsCorrectPos['111'] += 1
# 					resultsCorrectPos['twoCorrect'] += 1
# 				else:
# 					resultsCorrectPos['110'] += 1
# 					resultsCorrectPos['twoCorrect'] += 1
# 			else:
# 				if fullresultsCorrectPos[2]:
# 					resultsCorrectPos['101'] += 1
# 					resultsCorrectPos['twoCorrect'] += 1
# 				else:
# 					resultsCorrectPos['100'] += 1
# 		else:
# 			if fullresultsCorrectPos[1]:
# 				if fullresultsCorrectPos[2]:
# 					resultsCorrectPos['011'] += 1
# 					resultsCorrectPos['twoCorrect'] += 1
# 				else:
# 					resultsCorrectPos['010'] += 1
# 			else:
# 				if fullresultsCorrectPos[2]:
# 					resultsCorrectPos['001'] += 1
# 				else:
# 					resultsCorrectPos['000'] += 1

# 		feedbackRes = res['FEEDBACK']
# 		key = feedbackRes[0] + feedbackRes[1]
# 		if key == 'JJ':
# 			if not printed1:
# 				print 'These are the constants: ' + str((c1, c2))
# 				printed1 = True

# 		feedbackGiven[key] += 1

# print results
# print feedbackGiven
# print 'JJ: ' + str(feedbackGiven['JJ'])
# print 'JL: ' + str(feedbackGiven['JL'])
# print 'LJ: ' + str(feedbackGiven['LJ'])
# print 'LL: ' + str(feedbackGiven['LL'])






