import json
import time
from channels.generic.websocket import WebsocketConsumer

from simulation.projet_cabinet import CabinetModel

class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = True
        
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        params = json.loads(text_data)
        if params['status'] !=1:
            self.active = False
        
        model = CabinetModel(int(params['patients']))
        data = model.step()
        old_data = None
        
        while old_data==None or len(data['incoming'])>0 or len(data['outgoing'])>0 or len(data['consulting'])>0 or len(data['outgoing'])>0:
            stats = {
                'waiting_number': len(data['waiting']),
                'waiting_arrivals': len(data['incoming']),
                'waiting_exits': len(data['consulting']),
                'consult_number': len(data['consulting']),
                'consult_arrivals': len(data['consulting']),
                'consult_exits': len(data['outgoing']),
                'patient_number': len(data['incoming']) + len(data['consulting']),
                'patient_arrivals': len(data['incoming']),
                'patient_exits': 0 if old_data==None else len(old_data['outgoing']),
            }
            
            resp = {
                'stats': stats, 
                'patients': [pat.get_info() for pat in data['incoming']], 
                'waiting': [pat.get_waiting() for pat in data['waiting']],
                'consult': [pat.get_consulting() for pat in data['consulting']],
                'diagnosed': [pat.get_exit() for pat in data['outgoing']]
            }
            self.send(text_data=json.dumps({'status':1, 'values':resp}))
            time.sleep(2)
            old_data = data
            data = model.step()