var jsonCont = msg.payload;

var count = context.get('count')||0;
count++;
context.set('count',count);

jsonCont.id = 1+count;
jsonCont.temperature.value.degrees = Math.floor(Math.random()*(50-18)+18);
msg.payload = jsonCont;
node.warn(jsonCont.temperature.value.degrees);
return msg;