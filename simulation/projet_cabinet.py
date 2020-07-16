from mesa import Agent, Model
from mesa.time import RandomActivation
import datetime
import time
import random
from faker import Faker
import networkx as nx
import random as rd
from . import data_source
# import data_source

data = data_source.create_test_data()
graph = nx.Graph()

# Creation of disease graph with symptoms
def create_disease_graph():
    #adding nodes and edges
    for i in data.values():
        for j in i:
            graph.add_node(j)
            
    symptoms = list(graph.nodes)
    illnesses = list(data.keys())

    for i in data.keys():
        graph.add_node(i)

    for (illness, symptoms) in data.items():
        for i in symptoms:
            graph.add_edge(i, illness)
    
    return [symptoms, illnesses]


#doctor's diagnosis function
def diagnose(symptoms):
    output = {}
    for symp in symptoms:
        ills = graph.neighbors(symp)
        for i in ills:
            if i in output:
                output[i] += 1
            else:
                output[i] = 1
    for ill in output:
        output[ill] = int((output[ill]/graph.degree(ill))*100*100)/100
    return sorted(output.items(), key=lambda item: item[1], reverse=True)


#patient symptoms generation
def generate_symptoms():
    symptoms, illnesses = create_disease_graph()
    output = []
    nbrm = random.randint(2, 5)
    for i in range(nbrm):
        numm = rd.randint(0, len(illnesses)-1)
        output += list(graph.neighbors(illnesses[numm]))
    
    nbrs = rd.randint(2, 6)
    return rd.sample(output, nbrs)


# generation of dates for rendezvous
def generate_dates(number):
    start_date = datetime.datetime(2020, 8, 1)
    end_date = datetime.datetime(2020, 10, 31)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days

    random_dates = []

    counter=3
    while len(random_dates)< number+5:
        random_date = start_date + datetime.timedelta(days=counter)
        for hour in [8,10,12,14]:
            hour_date = random_date.replace(hour=hour)
            random_dates.append(hour_date)
        counter +=3

    random_dates.sort(reverse=True)
    return random_dates

# Implementation of agents
class Patient(Agent):
    def __init__(self, p_id, model):
        super().__init__(p_id,model)
        self.p_id = p_id
        self.arrival_time = None
        self.ticket = None
        self.symptoms = generate_symptoms()
        self.diagnostics = None
        self.state = 0
        fake = Faker()
        self.info = {
            "id": self.p_id,
            "name": fake.name(),
            "birthday": str(fake.date_of_birth().ctime()),
            "address": fake.address()
        }
        
    def send_informations(self, secretary):
        self.arrival_time = str(datetime.datetime.now())
        secretary.receive_informations(self.p_id, self.info) 
        
    def receive_ticket(self, ticket):
        self.ticket = ticket
    
    def receive_diagnostics(self, diagnostics):
        self.diagnostics = diagnostics
        
    def step(self):
        pass
    
    def get_info(self, exiting=False):
        self.info['ticket_id'] = self.ticket['order_num']
        self.info['arrival_date'] = self.arrival_time
        if exiting:
            self.info['patient_state'] = "Exiting"
        elif self.diagnostics:
            self.info['patient_state'] = "Consultating"
        else:
            self.info['patient_state'] = "Waiting"
        return self.info
    
    def get_waiting(self):
        data = {
                "name": self.info['name'],
                "arrival_date": self.arrival_time,
                "ticket_id": self.ticket['order_num'],
            }
        return data
    
    def get_consulting(self):
        data = {
                "name": self.info['name'],
                "symptoms": self.symptoms,
                "ticket_id": self.ticket['order_num'],
                "doctor_name": self.ticket['doctor'].name
            }
        return data
    
    def get_exit(self):
        data = {
                "name": self.info['name'],
                "diagnosis": self.diagnostics,
                "symptoms": self.symptoms,
                "ticket_id": self.ticket['order_num'],
            }
        return data
        

class Secretary(Agent):
    def __init__(self, s_id, model):
        super().__init__(s_id, model)
        self.id = s_id
        self.doctor_list = []
        self.patient_list = {}
        self.count =1000
        self.add_doctor(None)
    
    def receive_informations(self, p_id ,informations) :
        self.patient_list[p_id] = informations
        
    def add_doctor(self, doctor):
        fake = Faker()
        doctor1 = Doctor(random.randint(20,60), fake.name(), self.model)
        doctor2 = Doctor(random.randint(20,60), fake.name(), self.model)
        self.doctor_list.append(doctor1)
        self.doctor_list.append(doctor2)
    
    def create_patient_ticket(self, patient, date):
        rand = random.randint(0, len(self.doctor_list)-1)
        ticket = {'order_num' : self.count,
                    'patient' : patient.p_id ,
                   'doctor' : self.doctor_list[rand],
                  'date_consultation' : date
                 }
        self.doctor_list[rand].waiting_list.append(patient)
        self.count+=1
        return ticket
    
    
class Doctor(Agent):
    def __init__(self, m_id,name, model):
        super().__init__(m_id, model)
        self.id = m_id
        self.name = name
        self.knowledge_base = []
        self.waiting_list = []
        self.outgoing = []
        
    def step(self):
        if len(self.waiting_list)<1:
            return None
        patient = self.waiting_list.pop()
        diagnostics = diagnose(patient.symptoms)
        patient.receive_diagnostics(diagnostics)
        self.outgoing.append(patient)
        return patient

    def get_waiting_patients(self):
        pats = []
        for pat in self.waiting_list:
            if not pat.diagnostics:
                pats.append(pat)
        return pats
    
    def release_patient(self):
        if len(self.outgoing)>0:
            return self.outgoing.pop()
        else:
            return None

class Scheduler(RandomActivation):
    def __init__(self, model, secretary):
        super().__init__(model)
        self.secretary = secretary
        self.random_dates = generate_dates(self.model.num_pats*2)
        self.agent_list = None
        
    def step(self):
        if not self.agent_list:
            agent_list = [agent for agent in self.agent_buffer(shuffled=True)]
        stats = {
            'incoming': [],
            'consulting': [],
            'outgoing': [],
            'waiting': []
        }
        
        random.shuffle(agent_list)
        operation = (random.randrange(100))%2
        if operation == 0 and len(agent_list)>0:
            agent = agent_list.pop()
            stats['incoming'].append(agent)
            agent.send_informations(self.secretary)
            agent.receive_ticket(self.secretary.create_patient_ticket(agent, self.random_dates.pop()))
        elif operation == 1:
            doc = random.randrange(2)
            doctor = self.secretary.doctor_list[doc]
            doctor.step()
        
        doc = random.randrange(2)
        doctor = self.secretary.doctor_list[doc]
        pat = doctor.release_patient()
        if pat:
            stats['outgoing'].append(pat)
        pat = doctor.step()
        if pat:
            stats['consulting'].append(pat)
        
        stats['waiting'] += self.secretary.doctor_list[0].get_waiting_patients()
        stats['waiting'] += self.secretary.doctor_list[1].get_waiting_patients()
        self.steps += 1
        self.time += 1
        if len(stats['incoming'])<1 and len(stats['outgoing'])<1 and len(stats['consulting'])<1 and len(stats['outgoing'])<1:
            return self.step()
        else:
            return stats


# Sample Cabinet management model
class CabinetModel(Model):
    def __init__(self, N):
        self.num_pats= N
        self.secretary = Secretary(100, self)
        self.schedule = Scheduler(self,self.secretary)
        
        for i in range(self.num_pats):
            pat = Patient(i,self)
            self.schedule.add(pat)
            
    def step(self):
        return self.schedule.step()


''' model = CabinetModel(35)
print(model.step())
print(model.step())
print(model.step())
print(model.step())
print(model.step())
print(model.step())
print(model.step())
print(model.step())
print(model.step())
print(model.step())
print(model.step())
print(model.step()) '''
