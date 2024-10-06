import PySimpleGUI as ps
import cv2
from Client import Server
from Experiment import Experiment

server = Server('./Mass/')
experiment = Experiment('./Pressure/')
experiment.sync(server)

swidth, sheight = server.get_size()
cwidth, cheight = experiment.get_size()

layout = [[ps.Graph(canvas_size=(cwidth, cheight), graph_bottom_left=(0, 0), graph_top_right=(cwidth, cheight), key='mvideo'),
           ps.Graph(canvas_size=(swidth, sheight), graph_bottom_left=(0, 0), graph_top_right=(swidth, sheight), key='ovideo')],
          [ps.Button('Start Experiment', key='start'),
           ps.Button('Stop Experiment', key='stop', disabled=True)
              ]]

window = ps.Window("Super Awesome Experimental Setup", layout)
running = False

while True:
    event, values = window.read(timeout=20)
    
    if event == ps.WINDOW_CLOSED or event == 'EXIT':
        if not running:
            break
        else:
            value = ps.popup_ok_cancel("Are you sure you want to exit while an experiment is running?")
            if value == "OK":
                break

    if event == 'start':
        experiment.start()
        window['start'].update(disabled=True)
        window['stop'].update(disabled=False)
        running = True

    if event == 'stop':
        window['start'].update(disabled=False)
        window['stop'].update(disabled=True)
        experiment.stop()
        running = False

    data = server.read_cur()
    if data is not None:
        encoded_data = cv2.imencode('.png', data[1])[1].tobytes()
        my_graph = window['ovideo']
        my_graph.erase()
        my_graph.draw_image(data=encoded_data, location=(0, sheight))

    data = experiment.read_cur()      
    if data is not None:
        encoded_data = cv2.imencode('.png', data[1])[1].tobytes()
        my_graph = window['mvideo']
        my_graph.erase()
        my_graph.draw_image(data=encoded_data, location=(0, cheight))
        pass

    window['mvideo']
