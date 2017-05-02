import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import SimpleOpenNI.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class KinectPT extends PApplet {



SimpleOpenNI context;
boolean start = false;
boolean hastracked = false;
Table positions;
String[] skeletonNames = { "head", "neck", "leftshoulder", "leftelbow", "lefthand", "rightshoulder", "rightelbow", "righthand", "torso", "lefthip", "leftknee", "leftfoot", "righthip", "rightknee", "rightfoot" };
HashMap<String, Integer> skeleton = new HashMap<String, Integer>();
PVector com = new PVector();
PVector com2d = new PVector();
int[] skeletonIds;


public void setup() {
  size(640, 480);
  frameRate(25);
  
  context = new SimpleOpenNI(this);
  if (context.isInit() == false) {
    println("Can't init SimpleOpenNI, maybe the camera is not connected!"); 
    exit();
    return;  
  }
  
  // enable depthMap generation 
  context.enableDepth();
  context.enableRGB();
  
  // enable skeleton generation for all joints
  context.enableUser();
  
  stroke(0,0,255);
  strokeWeight(3);
  smooth(); 
  
  setupTable();
  
  // Draw Welcome Message
  textSize(32); // Set text size to 32
  fill(0);
  text("Welcome to Kinect PT !", 100, 100);
  textSize(17);
  text("Wait for the red circle to disappear to start your workout.", 70, 180);
  text("Please press the space bar when you are done or wait for data to save automatically.", 100, 210);
  textSize(24); // Set text size to 32
  text("Click anywhere to begin.", 150, 270);
  
  getSkeletonList();
  
}

// Counter to no how often we save a file
int printcounter = 0;

public void draw() {
  
  printcounter += 1;
  if (start) {
    context.update();
    image(context.userImage(),0,0);
    
    // Affordance for UI to tell user when to start presenting
    if (!hastracked){
      // Draw red circle
      fill(255,0,0);
      ellipse(100,100,100,100);
    }
    
    // get joint position of user
    int[] userList = context.getUsers();
    for (int i=0; i<userList.length; i++) {
      if (context.isTrackingSkeleton(userList[i])){
        // Create new row for table
        TableRow newRow = positions.addRow();
        newRow.setInt("user", userList[i]);
        newRow.setInt("timestamp", millis());
        hastracked = true;
        
        for (int j=0; j<skeletonNames.length; j++){
          PVector jointPos = new PVector();
          context.getJointPositionSkeleton(userList[i],skeleton.get(skeletonNames[j]), jointPos);
          String x = skeletonNames[j] + "x";
          String y = skeletonNames[j] + "y";
          String z = skeletonNames[j] + "z";
          println(x, y, z, jointPos.x, jointPos.y, jointPos.z);
          newRow.setFloat(x, jointPos.x);
          newRow.setFloat(y, jointPos.y);
          newRow.setFloat(z, jointPos.z);
          
          if (context.getCoM(userList[i], com)){
            newRow.setFloat("comx", com.x);
            newRow.setFloat("comy", com.y);
            newRow.setFloat("comz", com.z);
          } 
        }
      }
   }
   
   //Save out table to a file!
   if (printcounter % 50 == 0) {
     saveTableNow(printcounter/200+1);
   }
 }
}

// Setup Necessary Data Structures
public void getSkeletonList(){ 
  int[] kinectIds = {SimpleOpenNI.SKEL_HEAD, SimpleOpenNI.SKEL_NECK, SimpleOpenNI.SKEL_LEFT_SHOULDER,
  SimpleOpenNI.SKEL_LEFT_ELBOW, SimpleOpenNI.SKEL_LEFT_HAND, SimpleOpenNI.SKEL_RIGHT_SHOULDER,
  SimpleOpenNI.SKEL_RIGHT_ELBOW, SimpleOpenNI.SKEL_RIGHT_HAND, SimpleOpenNI.SKEL_TORSO,
  SimpleOpenNI.SKEL_LEFT_HIP, SimpleOpenNI.SKEL_LEFT_KNEE, SimpleOpenNI.SKEL_LEFT_FOOT,
  SimpleOpenNI.SKEL_RIGHT_HIP, SimpleOpenNI.SKEL_RIGHT_KNEE, SimpleOpenNI.SKEL_RIGHT_FOOT};
  skeletonIds = kinectIds.clone();
  for (int i=0; i<skeletonNames.length; i++)
  {
    skeleton.put(skeletonNames[i], skeletonIds[i]);
  } 
}

public void setupTable()
{
  positions = new Table();
  positions.addColumn("user");
  positions.addColumn("timestamp");
  positions.addColumn("comx");
  positions.addColumn("comy");
  positions.addColumn("comz");
  
  for (int i=0; i<skeletonNames.length; i++)
  {
    positions.addColumn(skeletonNames[i] + "x");
    positions.addColumn(skeletonNames[i] + "y");
    positions.addColumn(skeletonNames[i] + "z");
  }
}

// SimpleOpenNI events
public void onNewUser(SimpleOpenNI curContext, int userId)
{
  println("onNewUser - userId: " + userId);
  println("\tstart tracking skeleton");
  
  curContext.startTrackingSkeleton(userId);
}

public void onLostUser(SimpleOpenNI curContext, int userId)
{
  println("onLostUser - userId: " + userId);
}

public void onVisibleUser(SimpleOpenNI curContext, int userId)
{
  //println("onVisibleUser - userId: " + userId);
}

// Save table based on a file number
public void saveTableNow(int filenumber) {
  String tablefilename = "data/positions_" + filenumber + ".csv"; 
  saveTable(positions, tablefilename);
}


// Removed because now it just saves every X amount of times based on a counter variable
public void keyPressed()
{
  switch(key)
  {
  case ' ':
   exit();
 }
}

public void mouseClicked() {
  if (!start) {
    start = true;
    background(0);
  }
}
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "KinectPT" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
