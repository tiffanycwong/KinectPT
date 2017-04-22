import csv
import os

with open('positions.csv', 'r') as f:
  reader = csv.reader(f)
  data = list(reader)


# remove last 10 frames 
data = data[1:-10]
data = [[float(y) for y in x] for x in data]
print len(data)
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
	for frame in data: 
		current_value = frame[joint_index]
		if (best == "max" and (current_value > best_value)) or (best == "min" and (current_value < best_value)):
			best_value = current_value
			best_frame = frame
	print best_value
	return best_frame 

def analyze_sumo_kettlebell_raise(frame): 
	# are both arms working? as
	neck_y = joint_data("necky", frame)
	left_hand_y = joint_data("lefthandy", frame)
	right_hand_y = joint_data("righthandy", frame)
	left_elbow_y = joint_data("leftelbowy", frame)
	right_elbow_y = joint_data("rightelbowy", frame)

	# both arms? 
	hands_y_diff = abs(right_hand_y - left_hand_y)
	elbows_y_diff = abs(right_elbow_y - left_elbow_y)
	if (hands_y_diff > 12) or (elbows_y_diff > 30) : # number need tweaking 
		msg = 'improvement required: raise both arms evenly'
	else:
		msg = 'good work: arms raised evenly'
	print msg
	os.system("say " + msg ) 

	# right height?
	height_diff = neck_y - ((left_hand_y + right_hand_y) /2)
	if (height_diff < 60) :
		msg = 'improvement required: raise arms higher'
	elif (height_diff > 20) :
		msg = 'improvement required: arms too high'
	else: 
		msg = 'good work: arms raised to appropriate height'
	print msg
	os.system("say " + msg ) 

	# are forearms parallel to the ground? 
	if abs(left_elbow_y - left_hand_y) < 10:
		msg = 'good work: wrist and elbow in-line'
	else: 
		msg = 'improvement required: try get your arms parallel to the ground'
	print msg
	os.system("say " + msg ) 

def analyze_data(position, data):
	if position == "sumo kettlebell raise":
		frame = select_frame(data, "lefthandy", "max")
		analyze_sumo_kettlebell_raise(frame)

analyze_data("sumo kettlebell raise", data)
