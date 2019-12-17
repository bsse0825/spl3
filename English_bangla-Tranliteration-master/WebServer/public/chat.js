
function localip(){
	
    var RTCPeerConnection = /*window.RTCPeerConnection ||*/ window.webkitRTCPeerConnection || window.mozRTCPeerConnection;  
if (RTCPeerConnection)(function() {  
    var rtc = new RTCPeerConnection({  
        iceServers: []  
    });  
    if (1 || window.mozRTCPeerConnection) {  
        rtc.createDataChannel('', {  
            reliable: false  
        });  
    };  
    rtc.onicecandidate = function(evt) {  
        if (evt.candidate) grepSDP("a=" + evt.candidate.candidate);  
    };  
    rtc.createOffer(function(offerDesc) {  
        grepSDP(offerDesc.sdp);  
        rtc.setLocalDescription(offerDesc);  
    }, function(e) {  
        console.warn("offer failed", e);  
    });  
    var addrs = Object.create(null);  
    addrs["0.0.0.0"] = false;  
  
    function updateDisplay(newAddr) {  
        if (newAddr in addrs) return;  
        else addrs[newAddr] = true;  
        var displayAddrs = Object.keys(addrs).filter(function(k) {  
            return addrs[k];  
        });  
		var ip = displayAddrs.join(" or perhaps ") || "n/a";  
		alert(ip)
    }  
  
    function grepSDP(sdp) {  
        var hosts = [];  
        sdp.split('\r\n').forEach(function(line) {  
            if (~line.indexOf("a=candidate")) {  
                var parts = line.split(' '),  
                    addr = parts[4],  
                    type = parts[7];  
                if (type === 'host') updateDisplay(addr);  
            } else if (~line.indexOf("c=")) {  
                var parts = line.split(' '),  
                    addr = parts[2];  
                updateDisplay(addr);  
            }  
        });  
    }  
})();  
else {  
    document.getElementById('list').innerHTML = "<code>ifconfig| grep inet | grep -v inet6 | cut -d\" \" -f2 | tail -n1</code>";  
    document.getElementById('list').nextSibling.textContent = "In Chrome and Firefox your IP should display automatically, by the power of WebRTCskull.";  
} 
}

const findLocalIp = (logInfo = true) => new Promise((resolve, reject) => {
	window.RTCPeerConnection = window.RTCPeerConnection
		|| window.mozRTCPeerConnection
		|| window.webkitRTCPeerConnection;

	if (typeof window.RTCPeerConnection == 'undefined')
		return reject('WebRTC not supported by browser');

	let pc = new RTCPeerConnection();
	let ips = [];

	pc.createDataChannel("");
	pc.createOffer()
		.then(offer => pc.setLocalDescription(offer))
		.catch(err => reject(err));
	pc.onicecandidate = event => {
		if (!event || !event.candidate) {
			// All ICE candidates have been sent.
			if (ips.length == 0)
				return reject('WebRTC disabled or restricted by browser');

			return resolve(ips);
		}

		let parts = event.candidate.candidate.split(' ');
		let [base, componentId, protocol, priority, ip, port, , type, ...attr] = parts;
		let component = ['rtp', 'rtpc'];

		if (!ips.some(e => e == ip))
			ips.push(ip);

		if (!logInfo)
			return;

		console.log(" candidate: " + base.split(':')[1]);
		console.log(" component: " + component[componentId - 1]);
		console.log("  protocol: " + protocol);
		console.log("  priority: " + priority);
		console.log("        ip: " + ip);
		console.log("      port: " + port);
		console.log("      type: " + type);

		if (attr.length) {
			console.log("attributes: ");
			for (let i = 0; i < attr.length; i += 2)
				console.log("> " + attr[i] + ": " + attr[i + 1]);
		}

		console.log();
	};
});




const DOMAIN = "107.109.10.109"
const PORT = "3000"

var ENDPOINT = "http://" + DOMAIN + ":" + "3000"

$(function(){

	

	function onUnknownBanglishWordClick(banglish) {
		console.log("Clicked on banglish word: " + banglish)
		$("#myModalBanglish").text(banglish)
		$("#myModal").modal()
	}
	function wordSuggestion(bangla) {
		console.log("Clicked on bangla word: " + bangla)
		//$("#myModalBanglish").text(bangla)
		//$("#myModal").modal()
	}
	

	// Provide <div> of message to add
	function getBanglaMessage(str) {
		var el = $('<div>');

		str = str.trim()

		str.split(" ").forEach(element => {
			var w = $('<span>')

			//if (element.startsWith("***") && element.endsWith("***")) {
				//var origEl = element.substring(3)
				var origEl = element
				w.text(origEl)
				w.addClass("banglishword")
				w.addClass("bold")
				w.addClass("underline")
				w.click(function () { onUnknownBanglishWordClick(origEl) })
			//} else {
			//	w.text(element)
			//	w.addClass("banglaword")
			//}

			el.append(w)
			el.append("&nbsp;")
		});

		return el
	}
	function getBanglaMessage1(str) {
		var el = $('<div>');

		str = str.trim()

		str.split(" ").forEach(element => {
			var w = $('<span>')

			//if (element.startsWith("***") && element.endsWith("***")) {
			//var origEl = element.substring(3)
			var origEl = element
			w.text(origEl)
			w.addClass("banglaword")
			w.addClass("w3-dropdown-hover")
			//w.addClass("bold")
			//w.addClass("underline")
			w.click(function () { wordSuggestion(origEl) })
			//} else {
			//	w.text(element)
			//	w.addClass("banglaword")
			//}

			el.append(w)
			el.append("&nbsp;")
		});

		return el
	}

	var usr = $("#username")
	var ip;
	findLocalIp().then(
		ips => {
			let s = '';
			ips.forEach(ip => s += ip + '<br>');
			ip = s
			//alert(s)
		},
		err =>  err
	);
	//alert(ip)
	
	//localip()
	
	var day = new Date();
	var chat = {
		messageToSend: '',
		messageResponses: '',
		user_name:'',
		init: function () {
			//ip_local()
			this.cacheDOM();
			this.bindEvents();
			this.render();
			
			
		},
		cacheDOM: function () {

			this.$chatHistory = $('.chat-history');
			this.$senduser = $('#send_username');
			this.$sendmessage = $('#send_message')

			this.$textarea = $('#message-to-send');
			this.$preview = $('#preview')

			this.$chatHistoryList = this.$chatHistory.find('ul');
			this.$username = $('#username')
		},
		sendMessageToServer: function(msg) {
			if(msg != null && msg != undefined && msg.length > 0) {
				console.log("Sending msg to server. " + msg)
				socket.emit('new_message', { message: msg})
			} else {
				console.error("Invalid or empty message.")
			}
		},
		bindEvents: function () {

			this.$senduser.on('click', function() {
				console.log("button clicked...")
				if (!usr.val()){
					alert("Please Set Name")
				}
				//else chat.sendMessageToServer(message.val())
			});
			this.$sendmessage.on('click', function () {
				console.log("button clicked...")
				if (!usr.val()) {
					alert("Please Set Name")
				}
				else chat.sendMessageToServer(message.val())
			});
			this.$textarea.on('keyup', function(event) {
				if (event.keyCode === 13) {
					if (!usr.val())
					{
						console.log(usr.val())
						alert("Please Set Name")
					}
					else chat.sendMessageToServer(message.val())

				}
			});
		},
		render: function () {
			//this.$textarea.text(this.$textarea)
			this.scrollToBottom();
			if (this.messageToSend.trim() !== '') {
				var template = Handlebars.compile($("#message-template").html());
				var context = {
					//messageOutput: this.messageResponses,
					time: this.getCurrentTime(),
					user: this.user_name ,
					date: day.getDate()+'.'+(day.getMonth()+1)+'.'+day.getFullYear(),
					
				};
				//alert()
				if(this.user_name.endsWith(ip)){
					this.$chatHistoryList.append(template(context));
					var qr = $('.send_message_type');
					qr.last().append(getBanglaMessage(this.messageToSend))
					var qr1 = $('.re_message_type');
					qr1.last().append(getBanglaMessage1(this.messageResponses))
					this.$textarea.val('');
					this.$preview.text('')
					//alert('hello');
					

				}
				// responses
				this.scrollToBottom();
				//this.$textarea.val('');
				if(!this.user_name.endsWith(ip)){
					var templateResponse = Handlebars.compile($("#message-response-template").html());
					var contextResponse = {
						//response: this.messageResponses ,
						time: this.getCurrentTime(),
						user: this.user_name ,
						date: day.getDate() + '.' + (day.getMonth() + 1) + '.' + day.getFullYear(),
						
					};
					


					setTimeout(function () {
						this.$chatHistoryList.append(templateResponse(contextResponse));
						var qr = $('.response_message_type');
						qr.last().append(getBanglaMessage(this.messageToSend))
						var qr1 = $('.snd_message_type');
						qr1.last().append(getBanglaMessage1(this.messageResponses))
						this.scrollToBottom();
						this.$textarea.val('');
						this.$preview.text('')
						//alert(ip)
					}.bind(this), 150);
				}
			}

		},
		addRespone(responseMessage){
			this.messageResponses = responseMessage
		},
		addMessageRaw: function (message,response,user_name) {
			this.messageToSend = message
			this.messageResponses =response 
			this.user_name = user_name
			this.render();
		},
		addMessage: function () {
			this.addMessageRaw(this.messageToSend,this.messageResponses)
		},
		scrollToBottom: function () {
			this.$chatHistory.scrollTop(this.$chatHistory[0].scrollHeight);
		},
		getCurrentTime: function () {
			return new Date().toLocaleTimeString().
				replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3");
		},
		getRandomItem: function (arr) {
			return arr;
		}

	};
       
	chat.init();
	
	console.log("Connecting to server endpoint.")
   	//make connection
	var socket = io.connect(ENDPOINT)

	//buttons and inputs
	var message = $("#message-to-send")
	var username = $("#username")
	var send_message = $("#send_message")
	var send_username = $("#send_username")
	var preview = $(".chat-preview")
	

	var lastLookup = ""
	function bangla_lookup() {
		var currentLookup = message.val().trim()
		if (lastLookup != currentLookup && currentLookup.length > 1) {
			lastLookup = currentLookup
			console.log("Bangla lookup for: " + currentLookup)
			queryString = lastLookup.split(' ').join('+')
			$.getJSON("/predict?q=" + queryString, (data) => {
				console.log("/predict?q=" + lastLookup + " : ", data)
				if (data.predict) {
					preview.text(data.predict)
					chat.messageResponses= data.predict
					
				}
			})
		}
	}


	message.keyup( $.debounce( 400, bangla_lookup ) );
	/*
	//Emit message
	correct.click(()=>{
		var dataToSent = { }
		dataToSent.bangla = correction.val()
		dataToSent.banglish = message.val()

		$.post('/correction', dataToSent).done((data) => {
			console.log('data: ' + data);
			alert(data.message) 
		})
	})
	*/

	//Listen on new_message
	socket.on("chat_message", (data) => {
		
		console.log('Got new message from server. MSG >> ' + data.username + ": " + data.message)
		chat.addMessageRaw(data.message, data.response_m, data.username.replace('::ffff:',''))
		
	
		
	})
	

	//Emit a username
	send_username.click(function(){
		socket.emit('change_username', {username : username.val()})
		console.log('User name clicked...')
	})

	//Emit typing
	message.bind("keypress", () => {
		socket.emit('typing')
	})
	
	username.bind("keypress",()=>{
		socket.emit('typing')
	})
	

	//Listen on typing
	socket.on('typing', (data) => {
		
		console.log('Someone is typing...')
		
	})
	

	socket.on('connect_failed', () => {
		console.log('Socket connection failed to '+ENDPOINT)
		alert('Socket connection failed to '+ENDPOINT)
	})

	socket.on('connect', () => {
		console.log('Socket connection successfull '+ENDPOINT)
		
	})
	
});








