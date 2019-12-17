const express = require('express')
const app = express()
const net = require('net')
const fs = require('fs')
const bodyParser = require('body-parser');

const SOCKETFILE = '../uds_socket';
const PORT = 3000

//set the template engine ejs
app.set('view engine', 'ejs')

app.use(bodyParser());

//middlewares
app.use(express.static('public'))

// Chat history of last 10 messages
const MAX_CHAT_HISTORY = 10
var chatHistory = []

//routes
app.get('/', (req, res) => {
	res.render('test', {history: chatHistory})
})

function getBangla(banglishSentance, callback, error) {
    banglishSentance = banglishSentance.split('+').join(' ')
    console.log("Predict >> " + banglishSentance);
    client = net.createConnection(SOCKETFILE)
        .on('connect', ()=>{
            client.write(banglishSentance)
        })
        // Messages are buffers. use toString
        .on('data', function(data) {
            data = data.toString();
            callback(data)
        })
        .on('error', function(data)
        {
            error()
        });
}

app.get('/checkWord', (req, res) => {
    var q = req.query.q
    console.log("Query: " + q)

    getBangla(q, (banglaSen) => {
        // Success callback
        res.setEncoding = 'utf-8'
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ suggestion: banglaSen, error: null }, null, 3));
    },
        () => {
            // Error Callback
            res.setEncoding = 'utf-8'
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify({ predict: '', error: 'Error occurred' }, null, 3));
        })
})



app.get('/predict', (req,res) => {
    var q = req.query.q
    console.log("Query: "+q)

    getBangla(q, (banglaSen) => {
        // Success callback
        res.setEncoding = 'utf-8'
        res.setHeader('Content-Type', 'application/json');
        result = banglaSen.split(" ")
        len = parseInt(result[0])
        result_bangla = ''
        for(i=len+1;i<result.length;i++){
            result_bangla += ' '+result[i];
        }
       // alert(r)
        res.end(JSON.stringify({ predict: result_bangla, error: null }, null, 3));
    },
    () => {
        // Error Callback
        res.setEncoding = 'utf-8'
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ predict: '', error: 'Error occurred' }, null, 3));
    })
})

app.post("/correction", (req, res) => {
    console.log("/correction body: "+ JSON.stringify(req.body))
    console.log("/correction body: "+ JSON.stringify(req.params))

    if (req.body == null || req.body == undefined) {
        res.setEncoding = 'utf-8'
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ message: "No data found!", error: 1 }, null, 3));
        return
    }

    var data = req.body
    var bangla = req.body['bangla']
    var banglish =  req.body['banglish']

    if (bangla == null || bangla == undefined || banglish == null || banglish == undefined) {
        res.setEncoding = 'utf-8'
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ message: "Error occurred!", error: 1 }, null, 3));
        return
    }

    bangla = bangla.trim().split(' ')
    banglish =  banglish.trim().split(' ')

    console.log("Correction: ")
    console.log(bangla)
    console.log(banglish)

    if (bangla.length > 0 && bangla.length == banglish.length) {
        var stream = fs.createWriteStream("correction.txt", {flags:'a'});
        str = ""
        for (var i=0;i<bangla.length;++i) {
            str += bangla[i] + "\t" + banglish[i] + "\n"
        }

        stream.write(str)
        stream.close()

        res.setEncoding = 'utf-8'
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ message: "Correction submitted.", error: 0 }, null, 3));
    } else {
        res.setEncoding ='utf-8'
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ message: "Number of words doesn't match exactly or count: 0.", error: 1 }, null, 3));
    }

})

//Listen on port PORT (3000)
server = app.listen(PORT)

//socket.io instantiation
const io = require("socket.io")(server)


//listen on every connection
io.on('connection', (socket) => {
    console.log('New user connected')
	//default username
	socket.username = "Anonymous"

    //listen on change_username
    socket.on('change_username', (data) => {
        socket.username = data.username
    })

    //listen on new_message
    socket.on('new_message', (data) => {
        //broadcast the new message
      
        console.log('connection :', socket.request.connection.remoteAddress);
        var newMsg = {}
        var newBangla = 'gerbaze'
        getBangla(data.message, (bangla)=>{
           
           newMsg = {username: data.username, bangla: bangla, banglish: data.message, message: data.message + " >>> " + bangla }
           
            result = bangla.split(" ")
            len = parseInt(result[0])
            result_bangla = ''
            for (i = 1; i <= len + 1; i++) {
                result_bangla += ' ' + result[i];
            }
            this.newBangla = result_bangla
            
            io.sockets.emit('chat_message', { message: data.message, username: socket.username + ' , ' + socket.request.connection.remoteAddress, response_m: this.newBangla});

            if (chatHistory.length > MAX_CHAT_HISTORY)
                chatHistory.splice(0, chatHistory.length - MAX_CHAT_HISTORY)
        },
        () => {
            newMsg = { username: data.username, bangla: "Error getting bangla!", banglish: data.message, message: data.message + " >>>  ****** " }

            if (chatHistory.length > MAX_CHAT_HISTORY)
                chatHistory.splice(0, chatHistory.length - MAX_CHAT_HISTORY)
            io.sockets.emit('chat_message', { message: data.message, username: socket.username, response_m: 'Error'});
        })
    })
    
    
    //listen on typing
    socket.on('typing', (data) => {
    	socket.broadcast.emit('typing', {username : socket.username})
    })
})
