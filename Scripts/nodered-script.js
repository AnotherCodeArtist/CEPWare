var count = context.get('count')||0;
count++;
context.set('count',count);
if (count <= 20) {msg.payload = "t|20";}
else if (count <= 50) {msg.payload = "t|" + count;}
else {msg.payload = "t|" + Math.floor(Math.random()*(90-30)+30);}
msg.url = "http://172.17.0.8:7896/iot/d?k=4jggokgpepnvsb2uv4s40d59ov&i=IoT-R" + Math.floor(Math.random()*(6-1)+1);
msg.headers = {};
msg.headers['Fiware-Service'] = 'cepware';
msg.headers['Fiware-ServicePath'] = '/rooms';
msg.headers['Content-Type'] = 'text/plain';
node.warn(msg.payload);
return msg;