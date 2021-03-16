const notify = require('./sendNotify') ;
var title = process.argv[2];
var content = process.argv[3];

notify.sendNotify(`${title}`, `${content}`);

