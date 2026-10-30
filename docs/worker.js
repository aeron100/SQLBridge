importScripts('vendor/pyodide/pyodide.js');
let engine;
(async()=>{try{
 engine=await loadPyodide({indexURL:new URL('vendor/pyodide/',self.location.href).href});
 const [wheel,code]=await Promise.all([fetch('vendor/sqlglot-27.29.0-py3-none-any.whl').then(r=>{if(!r.ok)throw Error('Engine package unavailable');return r.arrayBuffer()}),fetch('converter.py').then(r=>r.text())]);
 engine.unpackArchive(wheel,'zip',{extractDir:'/lib/python3.12/site-packages'});
 engine.runPython(code);
 self.postMessage({type:'ready'});
}catch(e){self.postMessage({type:'initError',error:String(e)})}})();
self.onmessage=({data})=>{if(!engine)return;try{engine.globals.set('source_input',data.sql);engine.globals.set('pretty_input',true);let result=JSON.parse(engine.runPython('json.dumps(convert(source_input, pretty_input))'));self.postMessage({type:'result',id:data.id,...result});}catch(e){self.postMessage({type:'error',id:data.id,error:String(e).split('\n').filter(l=>l.trim()).slice(-1)[0].replace(/\u001b\[[0-9;]*m/g,'')})}};
