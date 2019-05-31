'use strict';
        var name = null

        var socket = io();
        $('form').submit(function(){
          name = $('#m').val()//$('#m').val('');
          return false;
        });

        var url = 'localhost:1111'
        // url = "10.90.93.186:1111"
        // url = '35.187.235.125:1111'

        document.getElementById('openForConnect').onclick = openForConnect
        document.getElementById('startVideo').onclick = startMedia
        document.getElementById('endVideo').onclick = endVideo
        document.getElementById('call').onclick = call
        document.getElementById('checkConnections').onclick = callFakeConnection//checkConnections//checkConnections

        //basics for getting the key data here

        //get the video stream  
        var localVideo = document.getElementById("localVideo")
        var localstream = null
        var remoteVideo = document.getElementById("remoteVideo")
        var remotestream = null
        var canvasStream = document.getElementById("canvasStream")
        var constraints = {video:true}


        var configuration = 
        { 
            iceServers: [
              //stun server
              { "urls": "stun:35.187.235.125:3478" },
              //turn server
              { urls: 'turn:35.187.235.125', username:'prouser', credential:'3TptDG7cAfz5TaXsda' }
            ] 
         };
        var pc = null;//new RTCPeerConnection(configuration)

        // pc.addEventListener('icecandidate', e =>{console.log("ice",e);});
        let pc2 = null;


        var offerOptions = {
          offerToReceiveAudio: 1,
          offerToReceiveVideo: 1
        };


        function send(message){
          switch(message.type){
            case "offer":
              // onOffer(message.offer)
              var test = JSON.stringify(message)
              socket.emit("offer broadcast", test)
              break;
            case "answer":
              // onAnswer(message.answer)
              var test = JSON.stringify(message)
              socket.emit("answer broadcast",test)
              break;
            case "candidate":
              var test = JSON.stringify(message)
              socket.emit("candidate", test)
              break;
            case "trigger2":
              var test = JSON.stringify(message)
              socket.emit("trigger2", test)
            default:
              break; 
          } 
        }


        socket.on("offer broadcast", function(msg){//somebody send remotedescription, we ignore
            msg = JSON.parse(msg)
            if(msg.name!=name){
              //do the connection
              console.log(name," receiving offer broadcast from ",msg.name )
              var offer = msg.offer
              onOffer(offer, msg.name)
            }
            else{
              return;
            } 
        }) 


        socket.on("answer broadcast", function(msg){ //somebody sent local description, we set it as remote 
            msg = JSON.parse(msg)
            if(msg.name!=name){
              console.log(name," receiving answer broadcast from ",msg.name )
              var answer = msg.answer
              onAnswer(answer)
            }
        })


        socket.on("candidate", function(msg){
           msg = JSON.parse(msg)
           if(msg.name!=name){

              console.log(name," receiving candidate from ",msg.name )
              var candidate = msg.candidate
              onCandidate(candidate)
           }
        })

        socket.on("trigger2", function(msg){
          console.log("trigger2")
          msg = JSON.parse(msg)
          if(msg.name!=name){
            startSimpleRTC()
          }
        })


        //get all the documents elements


        function startMedia(){
          getMediaStream()
        }

        function getMediaStream(){
          //get the incoming stream
          navigator.getUserMedia(constraints, successStreamCallback, errorStreamCallback)
        }

        function successStreamCallback(stream){
          localstream = stream
          localVideo.srcObject = stream
          //attach stream to rtcpeerconnection
          // pc.addStream(localstream)
        }

        function errorStreamCallback(){
          console.log("error getting stream")
        }
        //get the audio stream
        function getAudioStream(stream){
          var audioContext = new AudioContext()
          var mediaStreamSource = audioContext.createMediaStreamSource(stream);
          mediaStreamSource.connect(audioContext.destination)
        }

        function connectAudioStream(){
          navigator.getUserMedia({audio:true}, gotAudioStream)
        }
          

        function startSimpleRTC(){
          pc = new RTCPeerConnection(configuration)
          pc.addEventListener('icecandidate', e=>onIceCandidate(pc, e))
          pc.addEventListener('iceconnectionstatechange', e=>onIceStateChange(pc, e));
          pc.addEventListener('track', gotRemoteStream);
        }



        function call(){
          const videoTracks = localstream.getVideoTracks()
          const audioTracks = localstream.getAudioTracks()

          pc = new RTCPeerConnection(configuration);

          localstream.getTracks().forEach(function(track){
            pc.addTrack(track, localstream)
          })

          return negotiate();
        }


        


        function callFakeConnection(){
            pc = new RTCPeerConnection(configuration)
            var stream = canvasStream.captureStream()
            console.log("the stream is", stream)
            stream.getTracks().forEach(function(track){
              pc.addTrack(track, stream)
            })

            pc.addEventListener('track', gotRemoteStream);

            return pc.createOffer().then(function(desc) {
              console.log("the desc is", desc)
                return pc.setLocalDescription(desc);
            }).then(function() {
                return new Promise(function(resolve) {
                    if (pc.iceGatheringState === 'complete') {
                        resolve();
                    } else {
                        function checkState() {
                            if (pc.iceGatheringState === 'complete') {
                                pc.removeEventListener('icegatheringstatechange', checkState);
                                resolve();
                            }
                        }
                        pc.addEventListener('icegatheringstatechange', checkState);
                    }
                });
            }).then(function(){
              var offer = pc.localDescription;
              var codec;

              return $.post('http://'+url+'/give_me_an_answer',
                          JSON.stringify({
                            sdp: offer.sdp,
                            type: offer.type,
                            video_transform: "none"
                          })).then(function(res){
                            console.log("the res", res)
                            pc.setRemoteDescription(new RTCSessionDescription(res), function(offer2){
                              console.log("set answer success")
                            }, function(err){
                              console.log("set answer failed")
                            })
                        })
            }).then(function(response){
              console.log("the response", response)
              return response
            }).then(function(answer){
              // pc.setRemoteDescription(answer)
            })
            .catch(function(e) {
                alert(e);
            });

        }

        function negotiate() {
          pc.addEventListener('track', gotRemoteStream);
          return pc.createOffer().then(function(desc) {
              return pc.setLocalDescription(desc);
          }).then(function() {
              // wait for ICE gathering to complete
              return new Promise(function(resolve) {
                  if (pc.iceGatheringState === 'complete') {
                      resolve();
                  } else {
                      function checkState() {
                          if (pc.iceGatheringState === 'complete') {
                              pc.removeEventListener('icegatheringstatechange', checkState);
                              resolve();
                          }
                      }
                      pc.addEventListener('icegatheringstatechange', checkState);
                  }
              });
          }).then(function() {
              var offer = pc.localDescription;
              var codec;

              return $.post('http://'+url+'/offer', 
                  JSON.stringify({
                      sdp: offer.sdp,
                      type: offer.type,
                      video_transform: "edges"
                  //     video_transform: document.getElementById('video-transform').value
                  })
              )
          }).then(function(response) {
            console.log("the response", response)
              return response
          }).then(function(answer) {
              // document.getElementById('answer-sdp').textContent = answer.sdp;
              pc.setRemoteDescription(answer);
          }).catch(function(e) {
              alert(e);
          });
        }

        function onCreateSessionDescriptionError(error) {
          console.log(`Failed to create session description: ${error.toString()}`);
        }


        async function onCreateOfferSuccess(desc){
          console.log("Offer from pc1", desc)

          try {
            pc.setLocalDescription(desc)
            onSetLocalSuccess(pc);
          }
          catch (e){
            onSetSessionDescriptionError(e)
          }

          var offer = desc
          offer.sdp = sdpFilterCodec('video', "H264/90000", offer.sdp);
          return $.post('http://'+url+'/offer', 
              JSON.stringify({
                  sdp: offer.sdp,
                  type: offer.type,
                  video_transform: "none"
              //     video_transform: document.getElementById('video-transform').value
              }),
              function(re){
                console.log("re", re)
                // re.json().then(function(answer){
                  setTimeout(function(){
                    pc.setRemoteDescription(re)  
                  }, 2000)
                  
                // })
              }
          )
        }

        function onSetLocalSuccess(pc) {
          console.log(`setLocalDescription complete`);
        }

        function onSetRemoteSuccess(pc) {
          console.log(`setRemoteDescription complete`);
        }

        function onSetSessionDescriptionError(error) {
          console.log(`Failed to set session description: ${error.toString()}`);
        }

        async function onIceCandidate(pc, event) {
          try {
            console.log("the event candidate is ", event)
            // await (getOtherPc(pc).addIceCandidate(event.candidate));
            //send my ice candidate over
            send({
              type:"candidate",
              candidate: event.candidate,
              name: name
            })

            onAddIceCandidateSuccess(pc);
          } catch (e) {
            onAddIceCandidateError(pc, e);
          }
          console.log(`${getName(pc)} ICE candidate:\n${event.candidate ? event.candidate.candidate : '(null)'}`);
        }

        function getName(){
          return name
        }
        function onAddIceCandidateSuccess(pc) {
          console.log(`${getName(pc)} addIceCandidate success`);
        }

        function onAddIceCandidateError(pc, error) {
          console.log(`${getName(pc)} failed to add ICE Candidate: ${error.toString()}`);
        }

        function onIceStateChange(pc, event) {
          if (pc) {
            console.log(`${getName(pc)} ICE state: ${pc.iceConnectionState}`);
            console.log('ICE state change event: ', event);
          }
        }

        //we need to do the connection here

        //RTC connection sample
        function openForConnect(){

          if(name==undefined){
            alert("please type name")
            return
          }
          // var configuration = { 
          //   "iceServers": [{ "url": "stun:stun2.1.google.com:19302" }] 
          // }; 


          // pc.onaddstream = gotRemoteStream
            pc.createOffer(function(offer){
              send({
                type: "offer",
                offer: offer,
                name: name
              })

              pc.setLocalDescription(offer);
            }, function(error){
              console.log("the error", error)
            })

            pc.onicecandidate = function(event){
              if(event.candidate){
                send({
                    type:"candidate",
                    candidate: event.candidate,
                    name: name
                });
              }
            }
            pc.onaddstream = function(e){
              console.log("added stream")
              remoteVideo.srcObject = e.stream
            }

        }


        function onOffer(offer, name2){
          console.log(name, "received an offer from", name2)
          pc.setRemoteDescription(new RTCSessionDescription(offer))
          console.log(name, "set remote with offer", name2, offer)
          pc.createAnswer(function(answer){
            pc.setLocalDescription(answer);
            console.log(name,"set local")
            send({
              type: "answer",
              answer: answer,
              name: name
            }); 
          }, function(error){
            console.log("error creating an answer")
          })
        }



        function onAnswer(answer){
          console.log(name, "received an answer", answer)
          pc.setRemoteDescription(answer)
          console.log(name, "set remote descript", pc)
        }


        function onCandidate(candidate){
          pc.addIceCandidate(new RTCIceCandidate(candidate))
          console.log(name, "set ice candidate")
        }


        function checkStream(){
          console.log("checking stream", pc)
          pc.onaddstream = function(e){
            remoteVideo.src = window.URL.createObjectURL(e.stream); 
          }
        }

        function sdpFilterCodec(kind, codec, realSdp) {
            var allowed = []
            var rtxRegex = new RegExp('a=fmtp:(\\d+) apt=(\\d+)\r$');
            var codecRegex = new RegExp('a=rtpmap:([0-9]+) ' + escapeRegExp(codec))
            var videoRegex = new RegExp('(m=' + kind + ' .*?)( ([0-9]+))*\\s*$')
            
            var lines = realSdp.split('\n');

            var isKind = false;
            for (var i = 0; i < lines.length; i++) {
                if (lines[i].startsWith('m=' + kind + ' ')) {
                    isKind = true;
                } else if (lines[i].startsWith('m=')) {
                    isKind = false;
                }

                if (isKind) {
                    var match = lines[i].match(codecRegex);
                    if (match) {
                        allowed.push(parseInt(match[1]));
                    }

                    match = lines[i].match(rtxRegex);
                    if (match && allowed.includes(parseInt(match[2]))) {
                        allowed.push(parseInt(match[1]));
                    }
                }
            }

            var skipRegex = 'a=(fmtp|rtcp-fb|rtpmap):([0-9]+)';
            var sdp = '';

            isKind = false;
            for (var i = 0; i < lines.length; i++) {
                if (lines[i].startsWith('m=' + kind + ' ')) {
                    isKind = true;
                } else if (lines[i].startsWith('m=')) {
                    isKind = false;
                }

                if (isKind) {
                    var skipMatch = lines[i].match(skipRegex);
                    if (skipMatch && !allowed.includes(parseInt(skipMatch[2]))) {
                        continue;
                    } else if (lines[i].match(videoRegex)) {
                        sdp += lines[i].replace(videoRegex, '$1 ' + allowed.join(' ')) + '\n';
                    } else {
                        sdp += lines[i] + '\n';
                    }
                } else {
                    sdp += lines[i] + '\n';
                }
            }

            return sdp;
        }


        

        function checkConnections(){
          console.log("start")
          pc = new RTCPeerConnection(configuration)
          pc.addEventListener('track', gotRemoteStream);

          var stream = canvasStream.captureStream()
          stream.getTracks().forEach(function(track){
            pc.addTrack(track, localstream)
          })
          var answerToSend = null
          //send a http request to receive an offer
          $.post('http://'+url+'/i_want_an_offer')
            .then(function(offer){
              pc.setRemoteDescription(offer, 
                function(offer2){
                  console.log("the offer", offer)

                  pc.createAnswer(
                    function(answer){

                      pc.setLocalDescription(new RTCSessionDescription(answer), 
                        function(success){
                          console.log("success", answer)

                           $.post('http://'+url+'/give_back_answer',
                            JSON.stringify({
                                sdp: answer.sdp,
                                type: answer.type,
                                video_transform: "none"
                            })).then(function(res){
                              console.log("done")
                           })
                        }, 
                        function(err){
                          console.log("set local ", err)
                        })
                    }, 
                    function(err){
                      console.log("crate answer ", err)
                    })
                }, 
                function(err){
                  console.log("lernfer", err)
                })//set the remote here
          })
        }
        


        function escapeRegExp(string) {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
        }

        function gotRemoteStream(e) {
          console.log('we fo', e)
          if (remoteVideo.srcObject !== e.streams[0]) {
            remoteVideo.srcObject = e.streams[0];
            console.log('pc2 received remote stream', e);
          }
        }

        function gotRemoteStream2(e) {
          console.log('we fo', e)
          if (remoteVideo.srcObject !== e.streams[0]) {
            remoteVideo.srcObject = e.streams[1];
            console.log('pc2 received remote stream', e);
          }
        }

