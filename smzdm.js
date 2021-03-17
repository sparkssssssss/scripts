/**
 * nodejs的request模块模拟登陆开源中国
 */
//密码加密模块
const notify = require('./sendNotify') ;
const xpath = require('xpath')
const dom = require('xmldom').DOMParser
const request = require('request');
const fs = require("fs");
let url = 'https://zhiyou.smzdm.com/member/9687682701/baoliao/';
let headers = {
  'User-Agent': `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36`,
};
 
let opts = {
  url: url,
  method: 'GET',
  headers: headers,
};
 
request(opts, (e, r, b) => {
  let doc = new dom({
	      locator: {},
	      errorHandler: { warning: function (w) { }, 
		          error: function (e) { }, 
		          fatalError: function (e) { console.error(e) } }
  }).parseFromString(b)
  let nodes = xpath.select("//div[@class='pandect-content-stuff']", doc)
  content = ''
  const result=fs.readFileSync('./smzdm.txt','utf8');
  nodes.forEach(function (info, index) {
    let url = xpath.select("string(./div[1]/a/@href)", info);
    let title = xpath.select("string(./div[1]/a)", info);
    let time = xpath.select("string(./div[@class='pandect-content-type']/span)", info);
    //console.log(fd.toString())
    if(result.indexOf(url) == -1){
      content = content + title.trim() + "\n" + url +"\n\n" 
      fs.appendFile('./smzdm.txt', url, err => {
        if (err) {
          console.error(err)
          return
        }
      })
    }
  });
    notify.sendNotify('smzdm', content);
    console.log(content)
});

