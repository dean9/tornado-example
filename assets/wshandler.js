var ws = new WebSocket('ws://' + window.location.host + '/ws')
var message = document.getElementById("message")

ws.onopen = function(){
    message.textContent = 'open'
};
ws.onmessage = function(ev){
    message.textContent = 'received message'
    var json = JSON.parse(ev.data)
    console.log(json);
    document.getElementById(json.name).textContent = json.value
};
ws.onclose = function(ev){
  message.textContent = 'closed'
};
ws.onerror = function(ev){
  message.textContent = 'error occurred'
};
