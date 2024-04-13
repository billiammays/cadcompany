#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import socket, time

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # instantiate client socket 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 56789
        serv = '127.0.0.1'
        # connect to server - server must already be running
        s.connect((serv, port))
        ui.messageBox('[CADGPT-ClIENT] Successfully connected to server at ' \
                      + serv + ' ' + str(port))
        # main recieving loop
        while True:
            message_in = s.recv(8192).decode()
            # execute code (god save me)
            if message_in != 'no code sent':
                try:
                    exec(message_in)     
                    adsk.doEvents()
                except:
                    # continue or exit
                    button_press = ui.messageBox('haiz, that didnt work, continue?', 'Code Failure', 3, 0)
                    if button_press == 2:
                        continue
                    else:
                        break    
            else:
                continue
        s.close()
        ui.messageBox('[CADGPT-CLIENT] Program shut')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
