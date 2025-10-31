// === Shift Register Control Sketch ===
// Controls up to 32 outputs via 4 daisy-chained shift registers
// Commands are received via Serial to set output states or run stored sequences.

// --- Pin definitions ---
const int dataPin=10;    // shift-register data input
const int latchPin=11;   // latch pin (stores shifted bits to outputs)
const int clockPin=12;   // clock pin (pulsed to shift bits)

// --- Global state variables ---
uint32_t switch_state;  // holds current 32-bit output pattern



#define verbose                 // enable serial feedback, to mute serial printing just undefine it
#define seq_size 200            // maximum number of steps in a stored sequence
#define state_mem 6*seq_size    // each step uses 6 bytes (4 for state + 2 for delay)

// --- Sequence memory ---
size_t len_code = 0;            // how many steps are currently stored
char code_sequence[state_mem];  // raw byte buffer to store all steps

// ============================================================================
// Helper: parseUint32()
// Converts a String (decimal or 0x-prefixed hex) to uint32_t value
// Returns true if valid, false if parsing failed.
// ============================================================================
static bool parseUint32(const String & s, uint32_t & out) {
  out=0; size_t l =  s.length(); 
  if(0 == l ) return false ;
  // we should use hex to avoid confucion
  if(s.startsWith("0x")) {   // --- Hexadecimal format ---
    for(size_t i =2 ; i < l ; ++i) {
      char c = s[i];
      uint8_t d = 0 ; 
      if(c >= '0' && c <= '9' ) { d = (uint8_t) (c - '0') ; } 
      else if(c>='a' && c <='f'){ d = (uint8_t)( c - 'a' ) + 10 ; }
      else return false ;
      out = ((out<<4) + d); 
    }
  } else { // --- Decimal format ---
    for(size_t i =0 ; i < l ; ++i) {
      char c = s[i];
      uint8_t d = 0 ; 
      if(c >= '0' && c <= '9' ) { d= (uint8_t) (c - '0') ; } 
      else return false ;
      out = out*10UL + d; 
    }
  }
  return true ;
}

// ============================================================================
// write32bits()
// Sends a 32-bit pattern to the shift registers (LSB first).
// Four 8-bit values are shifted out, then latched to outputs.
// ============================================================================
void write32bits(uint32_t st){
  digitalWrite(latchPin, LOW);
  shiftOut(dataPin, clockPin, LSBFIRST , st & 0xff ); 
  shiftOut(dataPin, clockPin, LSBFIRST , (st>> 8 ) & 0xff ); 
  shiftOut(dataPin, clockPin, LSBFIRST , (st>> 16 ) & 0xff ); 
  shiftOut(dataPin, clockPin, LSBFIRST , (st>> 24 ) & 0xff ); 
  digitalWrite(latchPin, HIGH);
}


void setup() {
  // setup serial
	Serial.begin(115200) ; 

  // seting up the data pins for the mosfets 
  pinMode(latchPin, OUTPUT) ; 
  pinMode(clockPin, OUTPUT) ; 
  pinMode(dataPin, OUTPUT) ; 
  write32bits(0); // set all states to 0
}

// ============================================================================
// execute_command()
// Parses and executes text commands from the serial interface.
// Supported commands:
//   setstate:<value>        -> set outputs immediately
//   clearcode               -> clear stored sequence
//   addcode:<state>/<delay> -> add state+delay pair
//   printcode               -> list stored sequence
//   exec                    -> run sequence
// ============================================================================
void execute_command(String command) {
  uint32_t nss; // new switch state
  int sub_idx = command.indexOf(':');
  bool maj_mnr; // whether the command has a colon part
  String cmd_MAJ,cmd_mnr; // main command and argument

  // --- split main:sub ---
	if(-1 == sub_idx)  { 
    maj_mnr = false;
	  cmd_MAJ = command ; 
	  cmd_mnr = "" ; 
  }	 else { 
    maj_mnr = true;
	  cmd_MAJ = command.substring(0,sub_idx) ; 
	  cmd_mnr = command.substring(sub_idx+1) ; 
  }

    // ----------------------------------------------------------
  // 1. setstate:<value> → directly write to outputs
  // ----------------------------------------------------------
	if(maj_mnr && cmd_MAJ.equals("setstate") && parseUint32(cmd_mnr , nss)) {  
    write32bits(nss) ;
    #ifdef verbose
		  Serial.print( "command : " ); 
		  Serial.print( cmd_MAJ ); 
		  Serial.print( "new state: " ); 
		  Serial.println( nss); 
    #endif
  } 
  // ----------------------------------------------------------
  // 2. clearcode → reset sequence buffer
  // ----------------------------------------------------------
  else if( (!maj_mnr) &  cmd_MAJ.equals("clearcode"))   { 
    len_code=0;
	write32bits(0);
    #ifdef verbose
		  Serial.println( "code is cleared " ); 
    #endif
  } 
    // ----------------------------------------------------------
  // 3. addcode:<state>/<delay> → append step to sequence
  // ----------------------------------------------------------
  else if(maj_mnr && cmd_MAJ.equals("addcode")) {
    size_t slash_idx  = cmd_mnr.indexOf('/') ;
    String cmd_state = cmd_mnr.substring(0, slash_idx) ;
    String cmd_delay = cmd_mnr.substring(slash_idx + 1) ;
    uint32_t t1,t2 ; 
    // parse both numbers
    if(parseUint32(cmd_state , t1) && parseUint32(cmd_delay , t2 )) {
      if(6  *(len_code+1) < state_mem) {
        // memory layout: [uint32_t state][uint16_t delay]
        uint32_t * s  = ( uint32_t * ) (code_sequence + 6*len_code ) ;
        uint16_t * d  = ( uint16_t * ) (code_sequence + 6*len_code + 4  ) ;
        s[0] = t1;
        d[0] = (uint16_t)t2; 
        len_code+=1;
        #ifdef verbose
		      Serial.print( "code add success : " ); 
		      Serial.print( "new state: " ); 
		      Serial.println( s[0]); 
		      Serial.print( "new delay: " ); 
		      Serial.println( d[0]); 
        #endif
      } else {
        Serial.print("add code failed, memory overflow") ; 
      }
    } else {
      #ifdef verbose
		    Serial.print( "code added failed: " ); 
		    Serial.print( "cmd_state: " ); 
		    Serial.println( cmd_state); 
		    Serial.print( "cmd_delay: " ); 
		    Serial.println( cmd_delay); 
      #endif
    } 
  } 
  // ----------------------------------------------------------
  // 4. printcode → display all stored steps
  // ----------------------------------------------------------
  else if((!maj_mnr) && cmd_MAJ.equals("printcode")) {
    Serial.println("current code : "); 
    for(size_t i =0 ;  i < len_code ; ++i ) {
      uint32_t * s  = ( uint32_t * ) (code_sequence + 6*i ) ;
      uint16_t * d  = ( uint16_t * ) (code_sequence + 6*i + 4  ) ;
      Serial.print("state:0x");
      Serial.print(s[0], HEX) ;
      Serial.print(" delay:");
      Serial.print(d[0]) ;
      Serial.println("") ;
    }
  } 
   // ----------------------------------------------------------
  // 5. exec → execute stored sequence
  // ----------------------------------------------------------
  else if((!maj_mnr) && cmd_MAJ.equals("exec") ) {
    #ifdef verbose
		Serial.println("Execution of sequence : " ); 
    #endif
    for(size_t i =0 ;  i < len_code ; ++i ) {
      uint32_t * s  = ( uint32_t * ) (code_sequence + 6*i ) ;
      uint16_t * d  = ( uint16_t * ) (code_sequence + 6*i + 4  ) ;
      // apply output state and wait its delay
      write32bits(s[0]) ;
      delay(d[0]) ;
      #ifdef verbose
        Serial.print("state:0x");
        Serial.print(s[0], HEX) ;
        Serial.print(" delay:");
        Serial.print(d[0]) ;
        Serial.println("") ;
      #endif
      //interruption of execution if anything comes from serial
      if(Serial.available() ) { 
        Serial.println("Execution Interrupted!");
        break;
      }
    }
    write32bits(0);
  }

}

// ============================================================================
// loop()
// Waits for serial input and executes one command per line.
// ============================================================================
void loop(){
	if(Serial.available()) {
		String msg = Serial.readStringUntil('\n') ; 
		if( msg.length() >  0)  execute_command(msg); 
	}
}
