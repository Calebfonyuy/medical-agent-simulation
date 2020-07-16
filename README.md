# medical-agent-simulation

Simple simulation of a multiagent system in the context of a medical center. The project was modeled using the PASSI aproach.

### Environment
The medical center

### Agents
* Secretary
* Doctor
* Patient

### Scenario description
* Patient arrives center and is signals his presence
* The patient's information is received by the secretary and a ticket offered to the patient containing the time to see a particular doctor chosen by the secretary 
* The patient meets with the doctor at a particular date and gives his symptoms to doctor.
* Doctor performs a diagnosis and communicates it to patient

### Technologies used
* Programming language: Python (Django server)
* Agent simulation library: mesa
* Websockets are used to update the real time display on the page
* Django Dependencies can be found in the _python-packages.txt_ file
* Other libraries used: faker(for generation of random data)

### Usage
* Install the requirements in your virtual environment
* Start the django server
* Enter the number of patients