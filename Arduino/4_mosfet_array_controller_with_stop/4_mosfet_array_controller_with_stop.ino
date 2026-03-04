const int dataPin=10;
const int latchPin=11;
const int clockPin=12;
uint32_t switch_state; 

//#define verbose
#define seq_size 200
#define state_mem 6*seq_size 

size_t len_code = 0; 
char code_sequence[state_mem];


static bool parseUint32(const String & s, uint32_t & out) {
  out=0; size_t l =  s.length(); 
  if(0 == l ) return false ;
  if(s.startsWith("0x")) { 
    for(size_t i =2 ; i < l ; ++i) {
      char c = s[i];
      uint8_t d = 0 ; 
      if(c >= '0' && c <= '9' ) { d = (uint8_t) (c - '0') ; } 
      else if(c>='a' && c <='f'){ d = (uint8_t)( c - 'a' ) + 10 ; }
      else return false ;
      out = ((out<<4) + d); 
    }
  } else {
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
  write32bits(0);
}

void execute_command(String command) {
  uint32_t nss; // new switch state
  int sub_idx = command.indexOf(':');
  bool maj_mnr;
  String cmd_MAJ,cmd_mnr;
	if(-1 == sub_idx)  { 
    maj_mnr = false;
	  cmd_MAJ = command ; 
	  cmd_mnr = "" ; 
  }	 else { 
    maj_mnr = true;
	  cmd_MAJ = command.substring(0,sub_idx) ; 
	  cmd_mnr = command.substring(sub_idx+1) ; 
  }

	if(maj_mnr && cmd_MAJ.equals("setstate") && parseUint32(cmd_mnr , nss)) {  
    write32bits(nss) ;
    #ifdef verbose
		  Serial.print( "command : " ); 
		  Serial.print( cmd_MAJ ); 
		  Serial.print( "new state: " ); 
		  Serial.println( nss); 
    #endif
  } else if( (!maj_mnr) &  cmd_MAJ.equals("clearcode"))   { 
    len_code=0;
    #ifdef verbose
		  Serial.println( "code is cleared " ); 
    #endif
  } else if(maj_mnr && cmd_MAJ.equals("addcode")) {
    size_t slash_idx  = cmd_mnr.indexOf('/') ;
    String cmd_state = cmd_mnr.substring(0, slash_idx) ;
    String cmd_delay = cmd_mnr.substring(slash_idx + 1) ;
    uint32_t t1,t2 ; 
    if(parseUint32(cmd_state , t1) && parseUint32(cmd_delay , t2 )) {
      if(6  *(len_code+1) < state_mem) {
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
  } else if((!maj_mnr) && cmd_MAJ.equals("printcode")) {
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
  } else if((!maj_mnr) && cmd_MAJ.equals("exec") ) {
    #ifdef verbose
		Serial.println("Execution of sequence : " ); 
    #endif
    for(size_t i =0 ;  i < len_code ; ++i ) {
      uint32_t * s  = ( uint32_t * ) (code_sequence + 6*i ) ;
      uint16_t * d  = ( uint16_t * ) (code_sequence + 6*i + 4  ) ;
      write32bits(s[0]) ;
      



      //delay(d[0]) ; //delay in mills
      //#ifdef verbose
      //  Serial.print("state:0x");
      //  Serial.print(s[0], HEX) ;
      //  Serial.print(" delay:");
      //  Serial.print(d[0]) ;
      //  Serial.println("") ;
      //#endif
      ////interruption of execution if anything comes from serial
      //if(Serial.available() ) { 
      //  Serial.println("Execution Interrupted!");
      //  break;
      //}
      //

      //  Arbitary stop  by serial availability
      
      unsigned long del_start = millis();
      while( millis()  - del_start  <  d[0] )  {
        if(Serial.available() ) { 
          Serial.println("Execution Interrupted!");
          break;
        }
      }
    }
    write32bits(0);
  }

}


void loop(){
	if(Serial.available()) {
		String msg = Serial.readStringUntil('\n') ; 
		if( msg.length() >  0)  execute_command(msg); 
	}
}
