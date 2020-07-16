let count = 0;
let patient_table = $('#patient-table').DataTable({
	searching: false,
	paging: false,
	columns: [
		{data: 'id'},
		{data: 'name'},
		{data: 'birthday'},
		{data: 'arrival_date'},
		{data: 'ticket_id'},
		{data: 'patient_state'}
	],
	order: [
		[0, 'desc']
	]
});

let waiting_table = $('#waiting-table').DataTable({
	searching: false,
	paging: false,
	columns: [
		{data: 'ticket_id'},
		{data: 'name'},
		{data: 'arrival_date'},
	],
	order: [
		[0, 'desc']
	]
});

let consult_table = $('#consult-table').DataTable({
	searching: false,
	paging: false,
	columns: [
		{data: 'ticket_id'},
		{data: 'name'},
		{data: 'doctor_name'},
		{data: 'symptoms'},
	],
	order: [
		[0, 'desc']
	]
});

let diagnosed_table = $('#diagnosed-table').DataTable({
	searching: false,
	paging: false,
	columns: [
		{data: 'ticket_id'},
		{data: 'name'},
		{data: 'symptoms'},
		{data: 'diagnosis'},
	],
	order: [
		[0, 'desc']
	]
});

var simulating = false;
var patient_count = 0;

var dataSocket =null;

function start_simulation (form) {
	let params = {
		status: 1,
		patients: $('#patients').val()
	}
	simulating = true;

	reset_values();

	if(dataSocket!=null && (dataSocket.readyState == dataSocket.OPEN)){
		dataSocket.close();
	}

	dataSocket = new WebSocket('ws://'+window.location.host+'/data');

	send_data = function (){
		if(dataSocket.readyState!=1){
			setTimeout(send_data, 1000)
		}else{
			create_socket();
			dataSocket.send(JSON.stringify(params));

			$("#start-btn").attr('hidden','hidden');
			$("#stop-btn").removeAttr("hidden");
		}
	}
	setTimeout(send_data, 1000)
}

function create_socket(){
	dataSocket.onmessage = function (msg) {
		console.log(msg);
	    data = JSON.parse(msg.data);
	    if(data.status==1){
	    	update_values(data.values);
	    }else{
	    	alert("Server Error: "+data.message);
	    }
	}

	dataSocket.onclose = function (e) {
		$("#stop-btn").attr('hidden','hidden');
		$("#start-btn").removeAttr("hidden");
		simulating = false;
	    alert('Server connection closed');
	}
}


function stop_simulation () {
	dataSocket.close();
}

function reset_values () {
	$('#waiting-number').text("0");
	$('#waiting-arrivals').text("0");
	$('#waiting-exits').text("0");

	$('#consult-number').text("0");
	$('#consult-arrivals').text("0");
	$('#consult-exits').text("0");

	$('#patient-number').text("0");
	$('#patient-arrivals').text("0");
	$('#patient-exits').text("0");

	patient_table.clear().draw();
	waiting_table.clear().draw();
	consult_table.clear().draw();
	diagnosed_table.clear().draw();
}

function update_values(values){
	let stats = values.stats;
	$('#waiting-number').text(stats.waiting_number);
	$('#waiting-arrivals').text(stats.waiting_arrivals);
	$('#waiting-exits').text(stats.waiting_exits);

	$('#consult-number').text(stats.consult_number);
	$('#consult-arrivals').text(stats.consult_arrivals);
	$('#consult-exits').text(stats.consult_exits);

	$('#patient-number').text(stats.patient_number);
	$('#patient-arrivals').text(stats.patient_arrivals);
	$('#patient-exits').text(stats.patient_exits);

	waiting_table.clear();
	consult_table.clear();
	diagnosed_table.clear();
	patient_table.rows.add(values.patients).draw();
	waiting_table.rows.add(values.waiting).draw();
	consult_table.rows.add(values.consult).draw();
	diagnosed_table.rows.add(values.diagnosed).draw();
}

function sendMessage(message) {
    dataSocket.send(JSON.stringify({
        'message': message
    }));
}