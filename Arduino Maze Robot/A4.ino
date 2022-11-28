#include <LiquidCrystal.h>

LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

#define btnUP 0
#define btnDOWN 1
#define btnRIGHT 2
#define btnLEFT 3
#define btnSELECT 4
#define btnNONE 5

#define InitialMode 10
#define StartMode 20

bool passedSecondGoal = false;
bool correct_direction = false;
bool timer = true;
bool trip_back;

int currentMode = 10;
int minutes = 0;
int closest_angle;
int currentGoal = 1;
int placeholder_goal;
int sen_goal;

double current_sen;
double wall_distance;
double x_distance_home = 0;
double y_distance_home = 0;
double x_distance_goal = 0;
double y_distance_goal = 0;
double closest_sen = 10;
double goal_distance;
double c_distance_home;
double c_angle;

String incomingByte;
String input;
String rot_sen = "CMD_SEN_ROT_";
String forward_movement = "CMD_ACT_LAT_1_";
String backward_movement = "CMD_ACT_LAT_0_";
String rot_ccw = "CMD_ACT_ROT_0_";
String rot_cw = "CMD_ACT_ROT_1_";

volatile long timer1_count = 0;
unsigned long prevMillis = millis();

ISR(TIMER1_COMPA_vect) {
  if (timer == true){
    timer1_count++;
    lcd.setCursor(0, 1);
    if (timer1_count >= 60) {
      timer1_count = 0;
      minutes++;
    }
    if (minutes < 10) {
      lcd.print("0");
      lcd.print(minutes);
    }
    else {
      lcd.print(minutes);
    }
    lcd.print(":");
    if (timer1_count < 10) {
      lcd.print("0");
      lcd.print(timer1_count);
    }
    else {
      lcd.print(timer1_count);
      lcd.setCursor(5, 1);
      lcd.print("    ");
    }
  }
  if (currentGoal == 2){
    lcd.setCursor(8, 1);
    lcd.print("F");
  }
  else if (currentGoal == 0){
    lcd.setCursor(8, 1);
    lcd.print("H");
  }
  else if (currentGoal == 3){
    lcd.setCursor(8, 1);
    lcd.print("C");
  }
  else if (currentGoal == 1){
    lcd.setCursor(8, 1);
    lcd.print("W");
  }
}

void PrintMessage(String message){
  Serial.print(message);
  Serial.write(13);
  Serial.write(10); 
}

void setup() { 
  Serial.begin(9600);
  lcd.begin(16, 2);

}

void loop() {
  switch (currentMode) {
    case InitialMode:
      delay(200);
      initialMode();
      break;
    case StartMode:
      delay(200);
      startMode();
      break;
  }
  
}

void initialMode(){
  lcd.setCursor(0, 0);
  lcd.print("13935921");
  lcd.setCursor(0, 1);
  lcd.print("00:00");

  if (readButtons() == btnSELECT){
    cli();
    TCCR1A = 0;// set TCCR1A register to 0
    TCCR1B = 0;
    TCNT1  = 0;
    // set compare match register for 1hz increments
    OCR1A = 15624;// = (16*10^6) / (1*1024) - 1 
    // turn on CTC mode
    TCCR1B |= (1 << WGM12);
    TCCR1B |= (1 << CS12) | (1 << CS10);
    // enable timer compare interrupt
    TIMSK1 |= (1 << OCIE1A);
    sei();
    PrintMessage("CMD_START");
    currentMode = StartMode;
  }
}

void startMode(){
  currentGoal = 1;

  // Navigate around maze
  
  PrintMessage("CMD_ACT_LAT_1_6");
  x_distance_home = x_distance_home + 6;
  checkGoal();

  PrintMessage("CMD_ACT_LAT_1_2");
  x_distance_home = x_distance_home + 2;
  checkGoal();
  
  PrintMessage("CMD_ACT_ROT_0_90");
  
  PrintMessage("CMD_ACT_LAT_1_2");
  y_distance_home = y_distance_home + 2;
  checkGoal();
  shortestPath();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  y_distance_home = y_distance_home + 1.5;
  checkGoal();
  shortestPath();

   PrintMessage("CMD_ACT_LAT_1_1.5");
  y_distance_home = y_distance_home + 1.5;
  checkGoal();
  shortestPath();

  PrintMessage("CMD_ACT_LAT_1_2");
  y_distance_home = y_distance_home + 2;
  checkGoal();
  shortestPath();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  y_distance_home = y_distance_home + 1.5;
  checkGoal();
  shortestPath();

   PrintMessage("CMD_ACT_LAT_1_1.5");
  y_distance_home = y_distance_home + 1.5;
  checkGoal();

// Reallign here
  reallign();
  shortestPath();
  
  PrintMessage("CMD_ACT_ROT_0_90");
  
  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home - 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home - 1.5;
  checkGoal();
  
  PrintMessage("CMD_ACT_ROT_1_90");
  
  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home + 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home + 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_ROT_1_90");
  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home + 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home + 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_ROT_0_90");
  PrintMessage("CMD_ACT_LAT_1_0.5");
  y_distance_home = y_distance_home + 0.5;
  checkGoal();

  PrintMessage("CMD_ACT_ROT_1_90");
  PrintMessage("CMD_ACT_LAT_1_2");
  x_distance_home = x_distance_home + 2;
  checkGoal();
  // Finished navigating
  
  
  // Return through maze
  PrintMessage("CMD_ACT_ROT_1_180");
  PrintMessage("CMD_ACT_LAT_1_2");
  x_distance_home = x_distance_home - 2;
  checkGoal();

  PrintMessage("CMD_ACT_ROT_0_90");
  PrintMessage("CMD_ACT_LAT_1_0.5");
  y_distance_home = y_distance_home - 0.5;
  checkGoal();

  PrintMessage("CMD_ACT_ROT_1_90");
  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home - 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home - 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_ROT_0_90");
  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home - 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home - 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_ROT_0_90");
  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home + 1.5;
  checkGoal();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  x_distance_home = x_distance_home + 1.5;
  checkGoal();

  // Reallign here
  reallign();

  PrintMessage("CMD_ACT_ROT_1_90");
  shortestPath();
  PrintMessage("CMD_ACT_LAT_1_2");
  y_distance_home = y_distance_home - 2;
  checkGoal();
  shortestPath();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  y_distance_home = y_distance_home - 1.5;
  checkGoal();
  shortestPath();

   PrintMessage("CMD_ACT_LAT_1_1.5");
  y_distance_home = y_distance_home - 1.5;
  checkGoal();
  shortestPath();
  
  PrintMessage("CMD_ACT_LAT_1_2");
  y_distance_home = y_distance_home - 2;
  checkGoal();
  shortestPath();

  PrintMessage("CMD_ACT_LAT_1_1.5");
  y_distance_home = y_distance_home - 1.5;
  checkGoal();
  shortestPath();

   PrintMessage("CMD_ACT_LAT_1_1.5");
  y_distance_home = y_distance_home - 1.5;
  checkGoal();
  shortestPath();

  PrintMessage("CMD_ACT_LAT_1_2");
  x_distance_home = x_distance_home - 2;
  checkGoal();
  
  PrintMessage("CMD_ACT_ROT_1_90");
  PrintMessage("CMD_ACT_LAT_1_5");
  x_distance_home = x_distance_home - 5;
  checkGoal();


  currentGoal = 3;
  PrintMessage("CMD_CLOSE");

  lcd.setCursor(8, 1);
  lcd.print("C");
  timer = false;
  //Return home

}

void checkGoal(){
  PrintMessage("CMD_SEN_ID");
  incomingByte = Serial.readString();
  sen_goal = incomingByte.toInt();
  if (sen_goal == 1 and currentGoal == 1){
    collectGoal();
    currentGoal = 2;
  }
  else if (sen_goal == 2 and currentGoal == 2){
    collectGoal();
    currentGoal = 0;
    lcd.setCursor(8, 1);
    lcd.print("H");
  }
  else if (sen_goal == 2 and currentGoal == 1){
    passedSecondGoal = true;
  }
}


void collectGoal(){
  placeholder_goal = currentGoal;
  PrintMessage("CMD_SEN_PING");
  incomingByte = Serial.readString();
  goal_distance = incomingByte.toDouble();

  bool facing_x = true;
  bool facing_y = true;

  x_distance_goal = 0;
  y_distance_goal = 0;

  correct_direction = false;
  
  while (1 == 1){
    PrintMessage("CMD_SEN_GOAL");
    incomingByte = Serial.readString();
    placeholder_goal = incomingByte.toInt();
    if (placeholder_goal == currentGoal){
      break;
    }
    
    PrintMessage("CMD_ACT_LAT_1_0.5");
    if (facing_x == true){
      x_distance_goal = x_distance_goal + 0.5;
    }
    else{
      x_distance_goal = x_distance_goal - 0.5;
    }
    
    PrintMessage("CMD_SEN_PING");
    incomingByte = Serial.readString();
    current_sen = incomingByte.toDouble();
    if (current_sen > goal_distance and correct_direction == true and current_sen != 0){
      PrintMessage("CMD_ACT_ROT_0_180");
      PrintMessage("CMD_ACT_LAT_1_0.5");
      if (facing_x == true){
        x_distance_goal = x_distance_goal - 0.5;
        PrintMessage("CMD_ACT_ROT_0_180");
      }
      else{
        x_distance_goal = x_distance_goal + 0.5;
      }
      break;
    }
    else if (current_sen > goal_distance or current_sen == 0){
      PrintMessage("CMD_ACT_ROT_0_180");

      if (facing_x == true){
        facing_x = false;
      }
      else{
        facing_x = true;
      }
      if (current_sen != 0){
        goal_distance = current_sen;
      }
      else{
        goal_distance = 10;
      }
    }
    else if (current_sen < goal_distance and current_sen != 0){
      goal_distance = current_sen;
      correct_direction = true;
    }
  }
  correct_direction = false;
  PrintMessage("CMD_ACT_ROT_0_90");

  while (1 == 1){
    PrintMessage("CMD_SEN_GOAL");
    incomingByte = Serial.readString();
    placeholder_goal = incomingByte.toInt();
    if (placeholder_goal == currentGoal){
      if (facing_y == true){
        PrintMessage("CMD_ACT_ROT_0_180");
      }
      break;
    }
    PrintMessage("CMD_ACT_LAT_1_0.5");
    if (facing_y == true){
      y_distance_goal = y_distance_goal + 0.5;
    }
    else{
      y_distance_goal = y_distance_goal - 0.5;
    }
    PrintMessage("CMD_SEN_PING");
    incomingByte = Serial.readString();
    current_sen = incomingByte.toDouble();
    if (current_sen > goal_distance or current_sen == 0){
      PrintMessage("CMD_ACT_ROT_0_180");
      if (facing_y == true){
        facing_y = false;
      }
      else{
        facing_y = true;
      }      
      if (current_sen != 0){
        goal_distance = current_sen;
      }
    }
    else if (current_sen < goal_distance and current_sen != 0){;
      goal_distance = current_sen;
      correct_direction = true;
    }
  }

  if (y_distance_goal != 0){
    if (facing_y == false){
      input = forward_movement + y_distance_goal;
      PrintMessage(input);
    }
    else{
      input = backward_movement + y_distance_goal;
      PrintMessage(input);
    }
  }

  PrintMessage("CMD_ACT_ROT_0_90");

  if (x_distance_goal != 0){
    if (facing_x == false){
      input = forward_movement + x_distance_goal;
      PrintMessage(input);
    }
    else{
      input = backward_movement + x_distance_goal;
      PrintMessage(input);
    }
  }
}

void reallign(){
  for (int y = 0; y <=1; y++){
    if (y == 1 and trip_back == false){
      PrintMessage("CMD_ACT_ROT_1_90");
    }
    else if (y == 1 and trip_back == true){
      PrintMessage("CMD_ACT_ROT_0_90");
    }
    for (int i = 0; i <= 25; i = i + 5){
      input = rot_sen + i;
      PrintMessage(input);
      PrintMessage("CMD_SEN_IR");
      incomingByte = Serial.readString();
      current_sen = incomingByte.toDouble();
      if (current_sen < closest_sen){
        closest_angle = i;
        closest_sen = current_sen;
      }
    }
    for (int i = 360; i >= 335; i = i - 5){
      input = rot_sen + i;
      PrintMessage(input);
      PrintMessage("CMD_SEN_IR");
      incomingByte = Serial.readString();
      current_sen = incomingByte.toDouble();
      if (current_sen < closest_sen){
        closest_angle = i;
        closest_sen = current_sen;
      }
    }
    input = rot_cw + closest_angle;
    PrintMessage(input);
    PrintMessage("CMD_SEN_ROT_0");
    closest_sen = 10;

    PrintMessage("CMD_SEN_IR");
    incomingByte = Serial.readString();
    current_sen = incomingByte.toDouble();
    if (current_sen > 1){
      wall_distance = current_sen - 1;
      input = forward_movement + wall_distance;
      PrintMessage(input);
    }
    else if (current_sen < 1){
      wall_distance = 1 - current_sen;
      input = backward_movement + wall_distance;
      PrintMessage(input);
    }

    if (y == 1 and trip_back == false){
      PrintMessage("CMD_ACT_ROT_0_90");
    }
    else if (y == 1 and trip_back == true){
      PrintMessage("CMD_ACT_ROT_1_90");
    }
  }
  trip_back = true;
}

void shortestPath(){
  if (currentGoal == 0){
    c_distance_home = sqrt(sq(x_distance_home) + sq(y_distance_home));
  
    if (trip_back == false){
      c_angle = 180 - (sin((x_distance_home/c_distance_home))*180/3.14);
      input = rot_ccw + c_angle;
      PrintMessage(input);
      input = forward_movement + c_distance_home;
      PrintMessage(input);
    }
    else if (trip_back == true){
      c_angle = (sin((x_distance_home/c_distance_home))*180/3.14);
      input = rot_cw + c_angle;
      PrintMessage(input);
      input = forward_movement + c_distance_home;
      PrintMessage(input);
    }
    currentGoal = 3;
    PrintMessage("CMD_CLOSE");
  
    lcd.setCursor(8, 1);
    lcd.print("C");
    timer = false;
  }
}

int readButtons(){
  int adc = analogRead(A0);

  if (adc > 1000) return btnNONE;
  if (adc < 50) return btnRIGHT;
  if (adc < 250) return btnUP;
  if (adc < 450) return btnDOWN;
  if (adc < 650) return btnLEFT;
  if (adc < 850) return btnSELECT;

  return btnNONE;
}
