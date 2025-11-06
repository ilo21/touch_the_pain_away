import serial
import time,sys,threading,argparse; 


parser= argparse.ArgumentParser(); 
parser.add_argument("--port", default="COM7" , help="Serial port name") ;
parser.add_argument("--baud", default=115200 , help="Baudrate") ;
args = parser.parse_args();
print(args.port) ; 

if "__main__" == __name__ : 
    #dev_addr = f"/dev/{args.port}"
    dev_addr=f"{args.port}"
    print(f"using port : {dev_addr}")
    
    ser =serial.Serial(dev_addr, int(args.baud)) ; 
    
    def discon(): 
        global ser;
        ser.close();

    def recon(): 
        global ser ;
        discon();
        ser =serial.Serial(dev_addr, int(args.baud)) ; 


    def print_thread_function() : 
      while(1) : 
        try: 
          print(ser.readline().decode()[:-1]) ;
        except :
          time.sleep(1);
    
    print_thread = threading.Thread(target = print_thread_function) ; 
    print_thread.start()
    
    def send(w) : 
      if(w[-1]!='\n')  : w+='\n' ;
      ser.write(w.encode()) ;
   
    def file(fn) : 
        w = open(fn,"r").read();
        send(w);

    def file_line_by_line(fn , delay = 0.01) :  
        w = open(fn,"r").read().split('\n');
        for iw in w : 
            send(iw);
            time.sleep(delay)
    
    
    def send_command(cmd,index= 0 , value =0.0) : 
      ser.write(f"{cmd}/{index}:{value}\n\r".encode()); 
    
    def temp(idx =0 , value = 0 ) : 
      send_command("Target" ,idx, value); 



    
