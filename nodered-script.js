var jsonCont = msg.payload;

var count = global.get('count')||0;
count++;
global.set('count',count);

jsonCont.id = 1+count;
jsonCont.temperature.value.degrees = Math.floor(Math.random()*(50-18)+18);
msg.payload = jsonCont;
node.warn(jsonCont.temperature.value.degrees);
msg.topic = jsonCont.type + "/" + jsonCont.id;
return msg;