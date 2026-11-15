/* Bulk planner DOM test; API and upload mocked, no real account or publication. */
const fs=require('fs'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const dom=new JSDOM(fs.readFileSync('studio/static/index.html','utf8'),{url:'http://localhost:8511/#publications',runScripts:'outside-only'}),w=dom.window,$=id=>w.document.getElementById(id),calls=[];
w.setInterval=()=>0;
const metadata={title:'Une idée à partager',description:'Une description précise suffisamment longue.',hashtags:['#Video','#Partage','#Exemple'],thumbnail_text:'Une idée claire'};
let failRead=false;
let library=[{id:'a'.repeat(32),title:'<img src=x onerror=alert(1)>',format:'reel',source:'studio',metadata},{id:'b'.repeat(32),title:'Deuxième vidéo',format:'reel',source:'studio',metadata}],plans=[];
w.fetch=async(url,options={})=>{if(url==='/api/publications'&&failRead)throw new Error('Connexion de test interrompue');const body=options.body?JSON.parse(options.body):null;calls.push({url,method:options.method,body});if(options.method==='POST'){plans=body.items.map((item,i)=>({id:String(i),job_id:item.job_id,title:item.metadata.title,platforms:body.platforms,at:new Date(item.at).getTime()/1000,status:'waiting',message:'Planifiée'}));return{ok:true,json:async()=>({plans})};}if(options.method==='DELETE'){plans[0].status='cancelled';return{ok:true,json:async()=>plans[0]};}return{ok:true,json:async()=>({library,plans})};};
w.XMLHttpRequest=class {constructor(){this.upload={};}open(method,url){this.url=url;}setRequestHeader(){}send(file){assert.equal(file.name,'externe.mp4');this.status=201;this.responseText=JSON.stringify({id:'c'.repeat(32),title:'externe',source:'import',format:'reel'});setImmediate(()=>this.onload());}};
const settle=async()=>{for(let i=0;i<10;i++)await new Promise(r=>setImmediate(r));};
(async()=>{
 w.eval(fs.readFileSync('studio/static/planner.js','utf8'));await settle();assert.equal($('bulk-library').querySelectorAll('input').length,2);assert.equal(w.document.querySelector('[onerror]'),null);
 failRead=true;$('planner-reload').click();await settle();assert.match($('bulk-feedback').textContent,/interrompue/);failRead=false;$('planner-reload').click();await settle();assert.match($('bulk-feedback').textContent,/rétablie/);
 $('bulk-select-all').click();assert.equal($('bulk-editors').children.length,2);$('bulk-start').value='2030-01-10T09:00';$('bulk-spacing').value='60';$('bulk-apply-dates').click();
 const dates=[...$('bulk-editors').querySelectorAll('input[type=datetime-local]')].map(e=>new Date(e.value).getTime());assert.equal(dates[1]-dates[0],3600000);
 $('bulk-youtube').checked=true;$('bulk-publication-form').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));await settle();const post=calls.find(c=>c.method==='POST');assert.equal(post.body.items.length,2);assert.deepEqual(post.body.platforms,['youtube']);assert.equal($('bulk-editors').children.length,0);assert.equal($('calendar-agenda').children.length,2);assert($('calendar-grid').querySelector('.calendar-event'));
 $('calendar-agenda').querySelector('button:last-child').click();await settle();assert(calls.some(c=>c.method==='DELETE'));
 Object.defineProperty($('bulk-files'),'files',{value:[{name:'externe.mp4',size:128}],configurable:true});$('bulk-files').dispatchEvent(new w.Event('change'));await settle();assert.equal($('bulk-editors').children.length,1);assert.match($('bulk-import-progress').textContent,/1 import/);assert(!calls.some(c=>c.url.includes('/social/publish')));
 dom.window.close();console.log('OK: bulk selection, safe titles, staggered dates, calendar, cancellation and external import without automatic posting.');
})().catch(e=>{console.error(e);dom.window.close();process.exitCode=1;});
