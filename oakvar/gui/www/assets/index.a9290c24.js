(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))r(s);new MutationObserver(s=>{for(const i of s)if(i.type==="childList")for(const o of i.addedNodes)o.tagName==="LINK"&&o.rel==="modulepreload"&&r(o)}).observe(document,{childList:!0,subtree:!0});function n(s){const i={};return s.integrity&&(i.integrity=s.integrity),s.referrerpolicy&&(i.referrerPolicy=s.referrerpolicy),s.crossorigin==="use-credentials"?i.credentials="include":s.crossorigin==="anonymous"?i.credentials="omit":i.credentials="same-origin",i}function r(s){if(s.ep)return;s.ep=!0;const i=n(s);fetch(s.href,i)}})();const G={};function Vo(t){G.context=t}const Wo=(t,e)=>t===e,be=Symbol("solid-proxy"),qn=Symbol("solid-track"),Vt={equals:Wo};let Qs=ri;const _e=1,Wt=2,Zs={owned:null,cleanups:null,context:null,owner:null},On={};var X=null;let je=null,H=null,Y=null,me=null,ur=0;function ee(t,e){const n=H,r=X,s=t.length===0,i=s?Zs:{owned:null,cleanups:null,context:null,owner:e||r},o=s?t:()=>t(()=>Ce(()=>fr(i)));X=i,H=null;try{return Ae(o,!0)}finally{H=n,X=r}}function _(t,e){e=e?Object.assign({},Vt,e):Vt;const n={value:t,observers:null,observerSlots:null,comparator:e.equals||void 0},r=s=>(typeof s=="function"&&(s=s(n.value)),ni(n,s));return[ti.bind(n),r]}function Gr(t,e,n){const r=sn(t,e,!0,_e);Qe(r)}function $(t,e,n){const r=sn(t,e,!1,_e);Qe(r)}function Oe(t,e,n){Qs=Yo;const r=sn(t,e,!1,_e);r.user=!0,me?me.push(r):Qe(r)}function ve(t,e,n){n=n?Object.assign({},Vt,n):Vt;const r=sn(t,e,!0,0);return r.observers=null,r.observerSlots=null,r.comparator=n.equals||void 0,Qe(r),ti.bind(r)}function dr(t,e,n){let r,s,i;arguments.length===2&&typeof e=="object"||arguments.length===1?(r=!0,s=t,i=e||{}):(r=t,s=e,i=n||{});let o=null,a=On,c=null,l=!1,u="initialValue"in i,d=typeof r=="function"&&ve(r);const v=new Set,[m,g]=(i.storage||_)(i.initialValue),[b,w]=_(void 0),[x,S]=_(void 0,{equals:!1}),[T,P]=_(u?"ready":"unresolved");if(G.context){c=`${G.context.id}${G.context.count++}`;let C;i.ssrLoadFrom==="initial"?a=i.initialValue:G.load&&(C=G.load(c))&&(a=C[0])}function U(C,L,O,K){return o===C&&(o=null,u=!0,(C===a||L===a)&&i.onHydrated&&queueMicrotask(()=>i.onHydrated(K,{value:L})),a=On,k(L,O)),L}function k(C,L){Ae(()=>{L||g(()=>C),P(L?"errored":"ready"),w(L);for(const O of v.keys())O.decrement();v.clear()},!1)}function W(){const C=Go,L=m(),O=b();if(O&&!o)throw O;return H&&!H.user&&C&&Gr(()=>{x(),o&&(C.resolved||v.has(C)||(C.increment(),v.add(C)))}),L}function z(C=!0){if(C!==!1&&l)return;l=!1;const L=d?d():r;if(L==null||L===!1){U(o,Ce(m));return}const O=a!==On?a:Ce(()=>s(L,{value:m(),refetching:C}));return typeof O!="object"||!(O&&"then"in O)?(U(o,O),O):(o=O,l=!0,queueMicrotask(()=>l=!1),Ae(()=>{P(u?"refreshing":"pending"),S()},!1),O.then(K=>U(O,K,void 0,L),K=>U(O,void 0,ii(K))))}return Object.defineProperties(W,{state:{get:()=>T()},error:{get:()=>b()},loading:{get(){const C=T();return C==="pending"||C==="refreshing"}},latest:{get(){if(!u)return W();const C=b();if(C&&!o)throw C;return m()}}}),d?Gr(()=>z(!1)):z(!1),[W,{refetch:z,mutate:g}]}function Jo(t){return Ae(t,!1)}function Ce(t){const e=H;H=null;try{return t()}finally{H=e}}function Jt(t){return X===null||(X.cleanups===null?X.cleanups=[t]:X.cleanups.push(t)),t}function ei(){return H}function qo(t){const e=ve(t),n=ve(()=>Gn(e()));return n.toArray=()=>{const r=n();return Array.isArray(r)?r:r!=null?[r]:[]},n}let Go;function ti(){const t=je;if(this.sources&&(this.state||t))if(this.state===_e||t)Qe(this);else{const e=Y;Y=null,Ae(()=>Gt(this),!1),Y=e}if(H){const e=this.observers?this.observers.length:0;H.sources?(H.sources.push(this),H.sourceSlots.push(e)):(H.sources=[this],H.sourceSlots=[e]),this.observers?(this.observers.push(H),this.observerSlots.push(H.sources.length-1)):(this.observers=[H],this.observerSlots=[H.sources.length-1])}return this.value}function ni(t,e,n){let r=t.value;return(!t.comparator||!t.comparator(r,e))&&(t.value=e,t.observers&&t.observers.length&&Ae(()=>{for(let s=0;s<t.observers.length;s+=1){const i=t.observers[s],o=je&&je.running;o&&je.disposed.has(i),(o&&!i.tState||!o&&!i.state)&&(i.pure?Y.push(i):me.push(i),i.observers&&si(i)),o||(i.state=_e)}if(Y.length>1e6)throw Y=[],new Error},!1)),e}function Qe(t){if(!t.fn)return;fr(t);const e=X,n=H,r=ur;H=X=t,Ko(t,t.value,r),H=n,X=e}function Ko(t,e,n){let r;try{r=t.fn(e)}catch(s){t.pure&&(t.state=_e),oi(s)}(!t.updatedAt||t.updatedAt<=n)&&(t.updatedAt!=null&&"observers"in t?ni(t,r):t.value=r,t.updatedAt=n)}function sn(t,e,n,r=_e,s){const i={fn:t,state:r,updatedAt:null,owned:null,sources:null,sourceSlots:null,cleanups:null,value:e,owner:X,context:null,pure:n};return X===null||X!==Zs&&(X.owned?X.owned.push(i):X.owned=[i]),i}function qt(t){const e=je;if(t.state===0||e)return;if(t.state===Wt||e)return Gt(t);if(t.suspense&&Ce(t.suspense.inFallback))return t.suspense.effects.push(t);const n=[t];for(;(t=t.owner)&&(!t.updatedAt||t.updatedAt<ur);)(t.state||e)&&n.push(t);for(let r=n.length-1;r>=0;r--)if(t=n[r],t.state===_e||e)Qe(t);else if(t.state===Wt||e){const s=Y;Y=null,Ae(()=>Gt(t,n[0]),!1),Y=s}}function Ae(t,e){if(Y)return t();let n=!1;e||(Y=[]),me?n=!0:me=[],ur++;try{const r=t();return Xo(n),r}catch(r){Y||(me=null),oi(r)}}function Xo(t){if(Y&&(ri(Y),Y=null),t)return;const e=me;me=null,e.length&&Ae(()=>Qs(e),!1)}function ri(t){for(let e=0;e<t.length;e++)qt(t[e])}function Yo(t){let e,n=0;for(e=0;e<t.length;e++){const r=t[e];r.user?t[n++]=r:qt(r)}for(G.context&&Vo(),e=0;e<n;e++)qt(t[e])}function Gt(t,e){const n=je;t.state=0;for(let r=0;r<t.sources.length;r+=1){const s=t.sources[r];s.sources&&(s.state===_e||n?s!==e&&qt(s):(s.state===Wt||n)&&Gt(s,e))}}function si(t){const e=je;for(let n=0;n<t.observers.length;n+=1){const r=t.observers[n];(!r.state||e)&&(r.state=Wt,r.pure?Y.push(r):me.push(r),r.observers&&si(r))}}function fr(t){let e;if(t.sources)for(;t.sources.length;){const n=t.sources.pop(),r=t.sourceSlots.pop(),s=n.observers;if(s&&s.length){const i=s.pop(),o=n.observerSlots.pop();r<s.length&&(i.sourceSlots[o]=r,s[r]=i,n.observerSlots[r]=o)}}if(t.owned){for(e=0;e<t.owned.length;e++)fr(t.owned[e]);t.owned=null}if(t.cleanups){for(e=0;e<t.cleanups.length;e++)t.cleanups[e]();t.cleanups=null}t.state=0,t.context=null}function ii(t){return t instanceof Error||typeof t=="string"?t:new Error("Unknown error")}function oi(t){throw t=ii(t),t}function Gn(t){if(typeof t=="function"&&!t.length)return Gn(t());if(Array.isArray(t)){const e=[];for(let n=0;n<t.length;n++){const r=Gn(t[n]);Array.isArray(r)?e.push.apply(e,r):e.push(r)}return e}return t}const Qo=Symbol("fallback");function Kr(t){for(let e=0;e<t.length;e++)t[e]()}function Zo(t,e,n={}){let r=[],s=[],i=[],o=0,a=e.length>1?[]:null;return Jt(()=>Kr(i)),()=>{let c=t()||[],l,u;return c[qn],Ce(()=>{let v=c.length,m,g,b,w,x,S,T,P,U;if(v===0)o!==0&&(Kr(i),i=[],r=[],s=[],o=0,a&&(a=[])),n.fallback&&(r=[Qo],s[0]=ee(k=>(i[0]=k,n.fallback())),o=1);else if(o===0){for(s=new Array(v),u=0;u<v;u++)r[u]=c[u],s[u]=ee(d);o=v}else{for(b=new Array(v),w=new Array(v),a&&(x=new Array(v)),S=0,T=Math.min(o,v);S<T&&r[S]===c[S];S++);for(T=o-1,P=v-1;T>=S&&P>=S&&r[T]===c[P];T--,P--)b[P]=s[T],w[P]=i[T],a&&(x[P]=a[T]);for(m=new Map,g=new Array(P+1),u=P;u>=S;u--)U=c[u],l=m.get(U),g[u]=l===void 0?-1:l,m.set(U,u);for(l=S;l<=T;l++)U=r[l],u=m.get(U),u!==void 0&&u!==-1?(b[u]=s[l],w[u]=i[l],a&&(x[u]=a[l]),u=g[u],m.set(U,u)):i[l]();for(u=S;u<v;u++)u in b?(s[u]=b[u],i[u]=w[u],a&&(a[u]=x[u],a[u](u))):s[u]=ee(d);s=s.slice(0,o=v),r=c.slice(0)}return s});function d(v){if(i[u]=v,a){const[m,g]=_(u);return a[u]=g,e(c[u],m)}return e(c[u])}}}function h(t,e){return Ce(()=>t(e||{}))}function Rt(){return!0}const ea={get(t,e,n){return e===be?n:t.get(e)},has(t,e){return t.has(e)},set:Rt,deleteProperty:Rt,getOwnPropertyDescriptor(t,e){return{configurable:!0,enumerable:!0,get(){return t.get(e)},set:Rt,deleteProperty:Rt}},ownKeys(t){return t.keys()}};function Nn(t){return(t=typeof t=="function"?t():t)?t:{}}function ta(...t){if(t.some(n=>n&&(be in n||typeof n=="function")))return new Proxy({get(n){for(let r=t.length-1;r>=0;r--){const s=Nn(t[r])[n];if(s!==void 0)return s}},has(n){for(let r=t.length-1;r>=0;r--)if(n in Nn(t[r]))return!0;return!1},keys(){const n=[];for(let r=0;r<t.length;r++)n.push(...Object.keys(Nn(t[r])));return[...new Set(n)]}},ea);const e={};for(let n=t.length-1;n>=0;n--)if(t[n]){const r=Object.getOwnPropertyDescriptors(t[n]);for(const s in r)s in e||Object.defineProperty(e,s,{enumerable:!0,get(){for(let i=t.length-1;i>=0;i--){const o=(t[i]||{})[s];if(o!==void 0)return o}}})}return e}function ce(t){const e="fallback"in t&&{fallback:()=>t.fallback};return ve(Zo(()=>t.each,t.children,e||void 0))}function ie(t){let e=!1;const n=t.keyed,r=ve(()=>t.when,void 0,{equals:(s,i)=>e?s===i:!s==!i});return ve(()=>{const s=r();if(s){const i=t.children,o=typeof i=="function"&&i.length>0;return e=n||o,o?Ce(()=>i(s)):i}return t.fallback})}function ai(t){let e=!1,n=!1;const r=qo(()=>t.children),s=ve(()=>{let i=r();Array.isArray(i)||(i=[i]);for(let o=0;o<i.length;o++){const a=i[o].when;if(a)return n=!!i[o].keyed,[o,a,i[o]]}return[-1]},void 0,{equals:(i,o)=>i[0]===o[0]&&(e?i[1]===o[1]:!i[1]==!o[1])&&i[2]===o[2]});return ve(()=>{const[i,o,a]=s();if(i<0)return t.fallback;const c=a.children,l=typeof c=="function"&&c.length>0;return e=n||l,l?Ce(()=>c(o)):c})}function Kt(t){return t}const na=["allowfullscreen","async","autofocus","autoplay","checked","controls","default","disabled","formnovalidate","hidden","indeterminate","ismap","loop","multiple","muted","nomodule","novalidate","open","playsinline","readonly","required","reversed","seamless","selected"],ra=new Set(["className","value","readOnly","formNoValidate","isMap","noModule","playsInline",...na]),sa=new Set(["innerHTML","textContent","innerText","children"]),ia=Object.assign(Object.create(null),{className:"class",htmlFor:"for"}),Xr=Object.assign(Object.create(null),{class:"className",formnovalidate:"formNoValidate",ismap:"isMap",nomodule:"noModule",playsinline:"playsInline",readonly:"readOnly"}),oa=new Set(["beforeinput","click","dblclick","contextmenu","focusin","focusout","input","keydown","keyup","mousedown","mousemove","mouseout","mouseover","mouseup","pointerdown","pointermove","pointerout","pointerover","pointerup","touchend","touchmove","touchstart"]),aa={xlink:"http://www.w3.org/1999/xlink",xml:"http://www.w3.org/XML/1998/namespace"};function la(t,e,n){let r=n.length,s=e.length,i=r,o=0,a=0,c=e[s-1].nextSibling,l=null;for(;o<s||a<i;){if(e[o]===n[a]){o++,a++;continue}for(;e[s-1]===n[i-1];)s--,i--;if(s===o){const u=i<r?a?n[a-1].nextSibling:n[i-a]:c;for(;a<i;)t.insertBefore(n[a++],u)}else if(i===a)for(;o<s;)(!l||!l.has(e[o]))&&e[o].remove(),o++;else if(e[o]===n[i-1]&&n[a]===e[s-1]){const u=e[--s].nextSibling;t.insertBefore(n[a++],e[o++].nextSibling),t.insertBefore(n[--i],u),e[s]=n[i]}else{if(!l){l=new Map;let d=a;for(;d<i;)l.set(n[d],d++)}const u=l.get(e[o]);if(u!=null)if(a<u&&u<i){let d=o,v=1,m;for(;++d<s&&d<i&&!((m=l.get(e[d]))==null||m!==u+v);)v++;if(v>u-a){const g=e[o];for(;a<u;)t.insertBefore(n[a++],g)}else t.replaceChild(n[a++],e[o++])}else o++;else e[o++].remove()}}}const Yr="_$DX_DELEGATE";function ca(t,e,n,r={}){let s;return ee(i=>{s=i,e===document?t():f(e,t(),e.firstChild?null:void 0,n)},r.owner),()=>{s(),e.textContent=""}}function y(t,e,n){const r=document.createElement("template");r.innerHTML=t;let s=r.content.firstChild;return n&&(s=s.firstChild),s}function R(t,e=window.document){const n=e[Yr]||(e[Yr]=new Set);for(let r=0,s=t.length;r<s;r++){const i=t[r];n.has(i)||(n.add(i),e.addEventListener(i,ga))}}function V(t,e,n){n==null?t.removeAttribute(e):t.setAttribute(e,n)}function ua(t,e,n,r){r==null?t.removeAttributeNS(e,n):t.setAttributeNS(e,n,r)}function li(t,e){e==null?t.removeAttribute("class"):t.className=e}function on(t,e,n,r){if(r)Array.isArray(n)?(t[`$$${e}`]=n[0],t[`$$${e}Data`]=n[1]):t[`$$${e}`]=n;else if(Array.isArray(n)){const s=n[0];t.addEventListener(e,n[0]=i=>s.call(t,n[1],i))}else t.addEventListener(e,n)}function Mt(t,e,n={}){const r=Object.keys(e||{}),s=Object.keys(n);let i,o;for(i=0,o=s.length;i<o;i++){const a=s[i];!a||a==="undefined"||e[a]||(Qr(t,a,!1),delete n[a])}for(i=0,o=r.length;i<o;i++){const a=r[i],c=!!e[a];!a||a==="undefined"||n[a]===c||!c||(Qr(t,a,!0),n[a]=c)}return n}function ci(t,e,n){if(!e)return n?V(t,"style"):e;const r=t.style;if(typeof e=="string")return r.cssText=e;typeof n=="string"&&(r.cssText=n=void 0),n||(n={}),e||(e={});let s,i;for(i in n)e[i]==null&&r.removeProperty(i),delete n[i];for(i in e)s=e[i],s!==n[i]&&(r.setProperty(i,s),n[i]=s);return n}function da(t,e={},n,r){const s={};return r||$(()=>s.children=Ke(t,e.children,s.children)),$(()=>e.ref&&e.ref(t)),$(()=>fa(t,e,n,!0,s,!0)),s}function f(t,e,n,r){if(n!==void 0&&!r&&(r=[]),typeof e!="function")return Ke(t,e,r,n);$(s=>Ke(t,e(),s,n),r)}function fa(t,e,n,r,s={},i=!1){e||(e={});for(const o in s)if(!(o in e)){if(o==="children")continue;s[o]=Zr(t,o,null,s[o],n,i)}for(const o in e){if(o==="children"){r||Ke(t,e.children);continue}const a=e[o];s[o]=Zr(t,o,a,s[o],n,i)}}function ha(t){return t.toLowerCase().replace(/-([a-z])/g,(e,n)=>n.toUpperCase())}function Qr(t,e,n){const r=e.trim().split(/\s+/);for(let s=0,i=r.length;s<i;s++)t.classList.toggle(r[s],n)}function Zr(t,e,n,r,s,i){let o,a,c;if(e==="style")return ci(t,n,r);if(e==="classList")return Mt(t,n,r);if(n===r)return r;if(e==="ref")i||n(t);else if(e.slice(0,3)==="on:"){const l=e.slice(3);r&&t.removeEventListener(l,r),n&&t.addEventListener(l,n)}else if(e.slice(0,10)==="oncapture:"){const l=e.slice(10);r&&t.removeEventListener(l,r,!0),n&&t.addEventListener(l,n,!0)}else if(e.slice(0,2)==="on"){const l=e.slice(2).toLowerCase(),u=oa.has(l);if(!u&&r){const d=Array.isArray(r)?r[0]:r;t.removeEventListener(l,d)}(u||n)&&(on(t,l,n,u),u&&R([l]))}else if((c=sa.has(e))||!s&&(Xr[e]||(a=ra.has(e)))||(o=t.nodeName.includes("-")))e==="class"||e==="className"?li(t,n):o&&!a&&!c?t[ha(e)]=n:t[Xr[e]||e]=n;else{const l=s&&e.indexOf(":")>-1&&aa[e.split(":")[0]];l?ua(t,l,e,n):V(t,ia[e]||e,n)}return n}function ga(t){const e=`$$${t.type}`;let n=t.composedPath&&t.composedPath()[0]||t.target;for(t.target!==n&&Object.defineProperty(t,"target",{configurable:!0,value:n}),Object.defineProperty(t,"currentTarget",{configurable:!0,get(){return n||document}}),G.registry&&!G.done&&(G.done=!0,document.querySelectorAll("[id^=pl-]").forEach(r=>r.remove()));n!==null;){const r=n[e];if(r&&!n.disabled){const s=n[`${e}Data`];if(s!==void 0?r.call(n,s,t):r.call(n,t),t.cancelBubble)return}n=n.host&&n.host!==n&&n.host instanceof Node?n.host:n.parentNode}}function Ke(t,e,n,r,s){for(G.context&&!n&&(n=[...t.childNodes]);typeof n=="function";)n=n();if(e===n)return n;const i=typeof e,o=r!==void 0;if(t=o&&n[0]&&n[0].parentNode||t,i==="string"||i==="number"){if(G.context)return n;if(i==="number"&&(e=e.toString()),o){let a=n[0];a&&a.nodeType===3?a.data=e:a=document.createTextNode(e),n=We(t,n,r,a)}else n!==""&&typeof n=="string"?n=t.firstChild.data=e:n=t.textContent=e}else if(e==null||i==="boolean"){if(G.context)return n;n=We(t,n,r)}else{if(i==="function")return $(()=>{let a=e();for(;typeof a=="function";)a=a();n=Ke(t,a,n,r)}),()=>n;if(Array.isArray(e)){const a=[],c=n&&Array.isArray(n);if(Kn(a,e,n,s))return $(()=>n=Ke(t,a,n,r,!0)),()=>n;if(G.context){if(!a.length)return n;for(let l=0;l<a.length;l++)if(a[l].parentNode)return n=a}if(a.length===0){if(n=We(t,n,r),o)return n}else c?n.length===0?es(t,a,r):la(t,n,a):(n&&We(t),es(t,a));n=a}else if(e instanceof Node){if(G.context&&e.parentNode)return n=o?[e]:e;if(Array.isArray(n)){if(o)return n=We(t,n,r,e);We(t,n,null,e)}else n==null||n===""||!t.firstChild?t.appendChild(e):t.replaceChild(e,t.firstChild);n=e}}return n}function Kn(t,e,n,r){let s=!1;for(let i=0,o=e.length;i<o;i++){let a=e[i],c=n&&n[i];if(a instanceof Node)t.push(a);else if(!(a==null||a===!0||a===!1))if(Array.isArray(a))s=Kn(t,a,c)||s;else if(typeof a=="function")if(r){for(;typeof a=="function";)a=a();s=Kn(t,Array.isArray(a)?a:[a],Array.isArray(c)?c:[c])||s}else t.push(a),s=!0;else{const l=String(a);c&&c.nodeType===3&&c.data===l?t.push(c):t.push(document.createTextNode(l))}}return s}function es(t,e,n=null){for(let r=0,s=e.length;r<s;r++)t.insertBefore(e[r],n)}function We(t,e,n,r){if(n===void 0)return t.textContent="";const s=r||document.createTextNode("");if(e.length){let i=!1;for(let o=e.length-1;o>=0;o--){const a=e[o];if(s!==a){const c=a.parentNode===t;!i&&!o?c?t.replaceChild(s,a):t.insertBefore(s,n):c&&a.remove()}else i=!0}}else t.insertBefore(s,n);return[s]}const ma=!1,pa="http://www.w3.org/2000/svg";function ba(t,e=!1){return e?document.createElementNS(pa,t):document.createElement(t)}function va(t){const{useShadow:e}=t,n=document.createTextNode(""),r=t.mount||document.body;function s(){if(G.context){const[i,o]=_(!1);return queueMicrotask(()=>o(!0)),()=>i()&&t.children}else return()=>t.children}if(r instanceof HTMLHeadElement){const[i,o]=_(!1),a=()=>o(!0);ee(c=>f(r,()=>i()?c():s()(),null)),Jt(()=>{G.context?queueMicrotask(a):a()})}else{const i=ba(t.isSVG?"g":"div",t.isSVG),o=e&&i.attachShadow?i.attachShadow({mode:"open"}):i;Object.defineProperty(i,"host",{get(){return n.parentNode},configurable:!0}),f(o,s()),r.appendChild(i),t.ref&&t.ref(i),Jt(()=>r.removeChild(i))}return n}function ui(t,e){return function(){return t.apply(e,arguments)}}const{toString:di}=Object.prototype,{getPrototypeOf:hr}=Object,gr=(t=>e=>{const n=di.call(e);return t[n]||(t[n]=n.slice(8,-1).toLowerCase())})(Object.create(null)),we=t=>(t=t.toLowerCase(),e=>gr(e)===t),an=t=>e=>typeof e===t,{isArray:xt}=Array,Xn=an("undefined");function ya(t){return t!==null&&!Xn(t)&&t.constructor!==null&&!Xn(t.constructor)&&Ze(t.constructor.isBuffer)&&t.constructor.isBuffer(t)}const fi=we("ArrayBuffer");function _a(t){let e;return typeof ArrayBuffer<"u"&&ArrayBuffer.isView?e=ArrayBuffer.isView(t):e=t&&t.buffer&&fi(t.buffer),e}const wa=an("string"),Ze=an("function"),hi=an("number"),gi=t=>t!==null&&typeof t=="object",xa=t=>t===!0||t===!1,Ut=t=>{if(gr(t)!=="object")return!1;const e=hr(t);return(e===null||e===Object.prototype||Object.getPrototypeOf(e)===null)&&!(Symbol.toStringTag in t)&&!(Symbol.iterator in t)},Ea=we("Date"),Ia=we("File"),Sa=we("Blob"),$a=we("FileList"),ka=t=>gi(t)&&Ze(t.pipe),Ta=t=>{const e="[object FormData]";return t&&(typeof FormData=="function"&&t instanceof FormData||di.call(t)===e||Ze(t.toString)&&t.toString()===e)},Ca=we("URLSearchParams"),Aa=t=>t.trim?t.trim():t.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g,"");function ln(t,e,{allOwnKeys:n=!1}={}){if(t===null||typeof t>"u")return;let r,s;if(typeof t!="object"&&(t=[t]),xt(t))for(r=0,s=t.length;r<s;r++)e.call(null,t[r],r,t);else{const i=n?Object.getOwnPropertyNames(t):Object.keys(t),o=i.length;let a;for(r=0;r<o;r++)a=i[r],e.call(null,t[a],a,t)}}function Yn(){const t={},e=(n,r)=>{Ut(t[r])&&Ut(n)?t[r]=Yn(t[r],n):Ut(n)?t[r]=Yn({},n):xt(n)?t[r]=n.slice():t[r]=n};for(let n=0,r=arguments.length;n<r;n++)arguments[n]&&ln(arguments[n],e);return t}const Oa=(t,e,n,{allOwnKeys:r}={})=>(ln(e,(s,i)=>{n&&Ze(s)?t[i]=ui(s,n):t[i]=s},{allOwnKeys:r}),t),Na=t=>(t.charCodeAt(0)===65279&&(t=t.slice(1)),t),Ra=(t,e,n,r)=>{t.prototype=Object.create(e.prototype,r),t.prototype.constructor=t,Object.defineProperty(t,"super",{value:e.prototype}),n&&Object.assign(t.prototype,n)},Da=(t,e,n,r)=>{let s,i,o;const a={};if(e=e||{},t==null)return e;do{for(s=Object.getOwnPropertyNames(t),i=s.length;i-- >0;)o=s[i],(!r||r(o,t,e))&&!a[o]&&(e[o]=t[o],a[o]=!0);t=n!==!1&&hr(t)}while(t&&(!n||n(t,e))&&t!==Object.prototype);return e},Pa=(t,e,n)=>{t=String(t),(n===void 0||n>t.length)&&(n=t.length),n-=e.length;const r=t.indexOf(e,n);return r!==-1&&r===n},La=t=>{if(!t)return null;if(xt(t))return t;let e=t.length;if(!hi(e))return null;const n=new Array(e);for(;e-- >0;)n[e]=t[e];return n},Ma=(t=>e=>t&&e instanceof t)(typeof Uint8Array<"u"&&hr(Uint8Array)),Ua=(t,e)=>{const r=(t&&t[Symbol.iterator]).call(t);let s;for(;(s=r.next())&&!s.done;){const i=s.value;e.call(t,i[0],i[1])}},ja=(t,e)=>{let n;const r=[];for(;(n=t.exec(e))!==null;)r.push(n);return r},Fa=we("HTMLFormElement"),Ba=t=>t.toLowerCase().replace(/[_-\s]([a-z\d])(\w*)/g,function(n,r,s){return r.toUpperCase()+s}),ts=(({hasOwnProperty:t})=>(e,n)=>t.call(e,n))(Object.prototype),Ha=we("RegExp"),mi=(t,e)=>{const n=Object.getOwnPropertyDescriptors(t),r={};ln(n,(s,i)=>{e(s,i,t)!==!1&&(r[i]=s)}),Object.defineProperties(t,r)},za=t=>{mi(t,(e,n)=>{const r=t[n];if(!!Ze(r)){if(e.enumerable=!1,"writable"in e){e.writable=!1;return}e.set||(e.set=()=>{throw Error("Can not read-only method '"+n+"'")})}})},Va=(t,e)=>{const n={},r=s=>{s.forEach(i=>{n[i]=!0})};return xt(t)?r(t):r(String(t).split(e)),n},Wa=()=>{},Ja=(t,e)=>(t=+t,Number.isFinite(t)?t:e),p={isArray:xt,isArrayBuffer:fi,isBuffer:ya,isFormData:Ta,isArrayBufferView:_a,isString:wa,isNumber:hi,isBoolean:xa,isObject:gi,isPlainObject:Ut,isUndefined:Xn,isDate:Ea,isFile:Ia,isBlob:Sa,isRegExp:Ha,isFunction:Ze,isStream:ka,isURLSearchParams:Ca,isTypedArray:Ma,isFileList:$a,forEach:ln,merge:Yn,extend:Oa,trim:Aa,stripBOM:Na,inherits:Ra,toFlatObject:Da,kindOf:gr,kindOfTest:we,endsWith:Pa,toArray:La,forEachEntry:Ua,matchAll:ja,isHTMLForm:Fa,hasOwnProperty:ts,hasOwnProp:ts,reduceDescriptors:mi,freezeMethods:za,toObjectSet:Va,toCamelCase:Ba,noop:Wa,toFiniteNumber:Ja};function N(t,e,n,r,s){Error.call(this),Error.captureStackTrace?Error.captureStackTrace(this,this.constructor):this.stack=new Error().stack,this.message=t,this.name="AxiosError",e&&(this.code=e),n&&(this.config=n),r&&(this.request=r),s&&(this.response=s)}p.inherits(N,Error,{toJSON:function(){return{message:this.message,name:this.name,description:this.description,number:this.number,fileName:this.fileName,lineNumber:this.lineNumber,columnNumber:this.columnNumber,stack:this.stack,config:this.config,code:this.code,status:this.response&&this.response.status?this.response.status:null}}});const pi=N.prototype,bi={};["ERR_BAD_OPTION_VALUE","ERR_BAD_OPTION","ECONNABORTED","ETIMEDOUT","ERR_NETWORK","ERR_FR_TOO_MANY_REDIRECTS","ERR_DEPRECATED","ERR_BAD_RESPONSE","ERR_BAD_REQUEST","ERR_CANCELED","ERR_NOT_SUPPORT","ERR_INVALID_URL"].forEach(t=>{bi[t]={value:t}});Object.defineProperties(N,bi);Object.defineProperty(pi,"isAxiosError",{value:!0});N.from=(t,e,n,r,s,i)=>{const o=Object.create(pi);return p.toFlatObject(t,o,function(c){return c!==Error.prototype},a=>a!=="isAxiosError"),N.call(o,t.message,e,n,r,s),o.cause=t,o.name=t.name,i&&Object.assign(o,i),o};var qa=typeof self=="object"?self.FormData:window.FormData;function Qn(t){return p.isPlainObject(t)||p.isArray(t)}function vi(t){return p.endsWith(t,"[]")?t.slice(0,-2):t}function ns(t,e,n){return t?t.concat(e).map(function(s,i){return s=vi(s),!n&&i?"["+s+"]":s}).join(n?".":""):e}function Ga(t){return p.isArray(t)&&!t.some(Qn)}const Ka=p.toFlatObject(p,{},null,function(e){return/^is[A-Z]/.test(e)});function Xa(t){return t&&p.isFunction(t.append)&&t[Symbol.toStringTag]==="FormData"&&t[Symbol.iterator]}function cn(t,e,n){if(!p.isObject(t))throw new TypeError("target must be an object");e=e||new(qa||FormData),n=p.toFlatObject(n,{metaTokens:!0,dots:!1,indexes:!1},!1,function(b,w){return!p.isUndefined(w[b])});const r=n.metaTokens,s=n.visitor||u,i=n.dots,o=n.indexes,c=(n.Blob||typeof Blob<"u"&&Blob)&&Xa(e);if(!p.isFunction(s))throw new TypeError("visitor must be a function");function l(g){if(g===null)return"";if(p.isDate(g))return g.toISOString();if(!c&&p.isBlob(g))throw new N("Blob is not supported. Use a Buffer instead.");return p.isArrayBuffer(g)||p.isTypedArray(g)?c&&typeof Blob=="function"?new Blob([g]):Buffer.from(g):g}function u(g,b,w){let x=g;if(g&&!w&&typeof g=="object"){if(p.endsWith(b,"{}"))b=r?b:b.slice(0,-2),g=JSON.stringify(g);else if(p.isArray(g)&&Ga(g)||p.isFileList(g)||p.endsWith(b,"[]")&&(x=p.toArray(g)))return b=vi(b),x.forEach(function(T,P){!(p.isUndefined(T)||T===null)&&e.append(o===!0?ns([b],P,i):o===null?b:b+"[]",l(T))}),!1}return Qn(g)?!0:(e.append(ns(w,b,i),l(g)),!1)}const d=[],v=Object.assign(Ka,{defaultVisitor:u,convertValue:l,isVisitable:Qn});function m(g,b){if(!p.isUndefined(g)){if(d.indexOf(g)!==-1)throw Error("Circular reference detected in "+b.join("."));d.push(g),p.forEach(g,function(x,S){(!(p.isUndefined(x)||x===null)&&s.call(e,x,p.isString(S)?S.trim():S,b,v))===!0&&m(x,b?b.concat(S):[S])}),d.pop()}}if(!p.isObject(t))throw new TypeError("data must be an object");return m(t),e}function rs(t){const e={"!":"%21","'":"%27","(":"%28",")":"%29","~":"%7E","%20":"+","%00":"\0"};return encodeURIComponent(t).replace(/[!'()~]|%20|%00/g,function(r){return e[r]})}function mr(t,e){this._pairs=[],t&&cn(t,this,e)}const yi=mr.prototype;yi.append=function(e,n){this._pairs.push([e,n])};yi.toString=function(e){const n=e?function(r){return e.call(this,r,rs)}:rs;return this._pairs.map(function(s){return n(s[0])+"="+n(s[1])},"").join("&")};function Ya(t){return encodeURIComponent(t).replace(/%3A/gi,":").replace(/%24/g,"$").replace(/%2C/gi,",").replace(/%20/g,"+").replace(/%5B/gi,"[").replace(/%5D/gi,"]")}function _i(t,e,n){if(!e)return t;const r=n&&n.encode||Ya,s=n&&n.serialize;let i;if(s?i=s(e,n):i=p.isURLSearchParams(e)?e.toString():new mr(e,n).toString(r),i){const o=t.indexOf("#");o!==-1&&(t=t.slice(0,o)),t+=(t.indexOf("?")===-1?"?":"&")+i}return t}class ss{constructor(){this.handlers=[]}use(e,n,r){return this.handlers.push({fulfilled:e,rejected:n,synchronous:r?r.synchronous:!1,runWhen:r?r.runWhen:null}),this.handlers.length-1}eject(e){this.handlers[e]&&(this.handlers[e]=null)}clear(){this.handlers&&(this.handlers=[])}forEach(e){p.forEach(this.handlers,function(r){r!==null&&e(r)})}}const wi={silentJSONParsing:!0,forcedJSONParsing:!0,clarifyTimeoutError:!1},Qa=typeof URLSearchParams<"u"?URLSearchParams:mr,Za=FormData,el=(()=>{let t;return typeof navigator<"u"&&((t=navigator.product)==="ReactNative"||t==="NativeScript"||t==="NS")?!1:typeof window<"u"&&typeof document<"u"})(),pe={isBrowser:!0,classes:{URLSearchParams:Qa,FormData:Za,Blob},isStandardBrowserEnv:el,protocols:["http","https","file","blob","url","data"]};function tl(t,e){return cn(t,new pe.classes.URLSearchParams,Object.assign({visitor:function(n,r,s,i){return pe.isNode&&p.isBuffer(n)?(this.append(r,n.toString("base64")),!1):i.defaultVisitor.apply(this,arguments)}},e))}function nl(t){return p.matchAll(/\w+|\[(\w*)]/g,t).map(e=>e[0]==="[]"?"":e[1]||e[0])}function rl(t){const e={},n=Object.keys(t);let r;const s=n.length;let i;for(r=0;r<s;r++)i=n[r],e[i]=t[i];return e}function xi(t){function e(n,r,s,i){let o=n[i++];const a=Number.isFinite(+o),c=i>=n.length;return o=!o&&p.isArray(s)?s.length:o,c?(p.hasOwnProp(s,o)?s[o]=[s[o],r]:s[o]=r,!a):((!s[o]||!p.isObject(s[o]))&&(s[o]=[]),e(n,r,s[o],i)&&p.isArray(s[o])&&(s[o]=rl(s[o])),!a)}if(p.isFormData(t)&&p.isFunction(t.entries)){const n={};return p.forEachEntry(t,(r,s)=>{e(nl(r),s,n,0)}),n}return null}function sl(t,e,n){const r=n.config.validateStatus;!n.status||!r||r(n.status)?t(n):e(new N("Request failed with status code "+n.status,[N.ERR_BAD_REQUEST,N.ERR_BAD_RESPONSE][Math.floor(n.status/100)-4],n.config,n.request,n))}const il=pe.isStandardBrowserEnv?function(){return{write:function(n,r,s,i,o,a){const c=[];c.push(n+"="+encodeURIComponent(r)),p.isNumber(s)&&c.push("expires="+new Date(s).toGMTString()),p.isString(i)&&c.push("path="+i),p.isString(o)&&c.push("domain="+o),a===!0&&c.push("secure"),document.cookie=c.join("; ")},read:function(n){const r=document.cookie.match(new RegExp("(^|;\\s*)("+n+")=([^;]*)"));return r?decodeURIComponent(r[3]):null},remove:function(n){this.write(n,"",Date.now()-864e5)}}}():function(){return{write:function(){},read:function(){return null},remove:function(){}}}();function ol(t){return/^([a-z][a-z\d+\-.]*:)?\/\//i.test(t)}function al(t,e){return e?t.replace(/\/+$/,"")+"/"+e.replace(/^\/+/,""):t}function Ei(t,e){return t&&!ol(e)?al(t,e):e}const ll=pe.isStandardBrowserEnv?function(){const e=/(msie|trident)/i.test(navigator.userAgent),n=document.createElement("a");let r;function s(i){let o=i;return e&&(n.setAttribute("href",o),o=n.href),n.setAttribute("href",o),{href:n.href,protocol:n.protocol?n.protocol.replace(/:$/,""):"",host:n.host,search:n.search?n.search.replace(/^\?/,""):"",hash:n.hash?n.hash.replace(/^#/,""):"",hostname:n.hostname,port:n.port,pathname:n.pathname.charAt(0)==="/"?n.pathname:"/"+n.pathname}}return r=s(window.location.href),function(o){const a=p.isString(o)?s(o):o;return a.protocol===r.protocol&&a.host===r.host}}():function(){return function(){return!0}}();function Et(t,e,n){N.call(this,t??"canceled",N.ERR_CANCELED,e,n),this.name="CanceledError"}p.inherits(Et,N,{__CANCEL__:!0});function cl(t){const e=/^([-+\w]{1,25})(:?\/\/|:)/.exec(t);return e&&e[1]||""}const ul=p.toObjectSet(["age","authorization","content-length","content-type","etag","expires","from","host","if-modified-since","if-unmodified-since","last-modified","location","max-forwards","proxy-authorization","referer","retry-after","user-agent"]),dl=t=>{const e={};let n,r,s;return t&&t.split(`
`).forEach(function(o){s=o.indexOf(":"),n=o.substring(0,s).trim().toLowerCase(),r=o.substring(s+1).trim(),!(!n||e[n]&&ul[n])&&(n==="set-cookie"?e[n]?e[n].push(r):e[n]=[r]:e[n]=e[n]?e[n]+", "+r:r)}),e},is=Symbol("internals"),Ii=Symbol("defaults");function ct(t){return t&&String(t).trim().toLowerCase()}function jt(t){return t===!1||t==null?t:p.isArray(t)?t.map(jt):String(t)}function fl(t){const e=Object.create(null),n=/([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;let r;for(;r=n.exec(t);)e[r[1]]=r[2];return e}function os(t,e,n,r){if(p.isFunction(r))return r.call(this,e,n);if(!!p.isString(e)){if(p.isString(r))return e.indexOf(r)!==-1;if(p.isRegExp(r))return r.test(e)}}function hl(t){return t.trim().toLowerCase().replace(/([a-z\d])(\w*)/g,(e,n,r)=>n.toUpperCase()+r)}function gl(t,e){const n=p.toCamelCase(" "+e);["get","set","has"].forEach(r=>{Object.defineProperty(t,r+n,{value:function(s,i,o){return this[r].call(this,e,s,i,o)},configurable:!0})})}function at(t,e){e=e.toLowerCase();const n=Object.keys(t);let r=n.length,s;for(;r-- >0;)if(s=n[r],e===s.toLowerCase())return s;return null}function re(t,e){t&&this.set(t),this[Ii]=e||null}Object.assign(re.prototype,{set:function(t,e,n){const r=this;function s(i,o,a){const c=ct(o);if(!c)throw new Error("header name must be a non-empty string");const l=at(r,c);l&&a!==!0&&(r[l]===!1||a===!1)||(r[l||o]=jt(i))}return p.isPlainObject(t)?p.forEach(t,(i,o)=>{s(i,o,e)}):s(e,t,n),this},get:function(t,e){if(t=ct(t),!t)return;const n=at(this,t);if(n){const r=this[n];if(!e)return r;if(e===!0)return fl(r);if(p.isFunction(e))return e.call(this,r,n);if(p.isRegExp(e))return e.exec(r);throw new TypeError("parser must be boolean|regexp|function")}},has:function(t,e){if(t=ct(t),t){const n=at(this,t);return!!(n&&(!e||os(this,this[n],n,e)))}return!1},delete:function(t,e){const n=this;let r=!1;function s(i){if(i=ct(i),i){const o=at(n,i);o&&(!e||os(n,n[o],o,e))&&(delete n[o],r=!0)}}return p.isArray(t)?t.forEach(s):s(t),r},clear:function(){return Object.keys(this).forEach(this.delete.bind(this))},normalize:function(t){const e=this,n={};return p.forEach(this,(r,s)=>{const i=at(n,s);if(i){e[i]=jt(r),delete e[s];return}const o=t?hl(s):String(s).trim();o!==s&&delete e[s],e[o]=jt(r),n[o]=!0}),this},toJSON:function(t){const e=Object.create(null);return p.forEach(Object.assign({},this[Ii]||null,this),(n,r)=>{n==null||n===!1||(e[r]=t&&p.isArray(n)?n.join(", "):n)}),e}});Object.assign(re,{from:function(t){return p.isString(t)?new this(dl(t)):t instanceof this?t:new this(t)},accessor:function(t){const n=(this[is]=this[is]={accessors:{}}).accessors,r=this.prototype;function s(i){const o=ct(i);n[o]||(gl(r,i),n[o]=!0)}return p.isArray(t)?t.forEach(s):s(t),this}});re.accessor(["Content-Type","Content-Length","Accept","Accept-Encoding","User-Agent"]);p.freezeMethods(re.prototype);p.freezeMethods(re);function ml(t,e){t=t||10;const n=new Array(t),r=new Array(t);let s=0,i=0,o;return e=e!==void 0?e:1e3,function(c){const l=Date.now(),u=r[i];o||(o=l),n[s]=c,r[s]=l;let d=i,v=0;for(;d!==s;)v+=n[d++],d=d%t;if(s=(s+1)%t,s===i&&(i=(i+1)%t),l-o<e)return;const m=u&&l-u;return m?Math.round(v*1e3/m):void 0}}function as(t,e){let n=0;const r=ml(50,250);return s=>{const i=s.loaded,o=s.lengthComputable?s.total:void 0,a=i-n,c=r(a),l=i<=o;n=i;const u={loaded:i,total:o,progress:o?i/o:void 0,bytes:a,rate:c||void 0,estimated:c&&o&&l?(o-i)/c:void 0};u[e?"download":"upload"]=!0,t(u)}}function ls(t){return new Promise(function(n,r){let s=t.data;const i=re.from(t.headers).normalize(),o=t.responseType;let a;function c(){t.cancelToken&&t.cancelToken.unsubscribe(a),t.signal&&t.signal.removeEventListener("abort",a)}p.isFormData(s)&&pe.isStandardBrowserEnv&&i.setContentType(!1);let l=new XMLHttpRequest;if(t.auth){const m=t.auth.username||"",g=t.auth.password?unescape(encodeURIComponent(t.auth.password)):"";i.set("Authorization","Basic "+btoa(m+":"+g))}const u=Ei(t.baseURL,t.url);l.open(t.method.toUpperCase(),_i(u,t.params,t.paramsSerializer),!0),l.timeout=t.timeout;function d(){if(!l)return;const m=re.from("getAllResponseHeaders"in l&&l.getAllResponseHeaders()),b={data:!o||o==="text"||o==="json"?l.responseText:l.response,status:l.status,statusText:l.statusText,headers:m,config:t,request:l};sl(function(x){n(x),c()},function(x){r(x),c()},b),l=null}if("onloadend"in l?l.onloadend=d:l.onreadystatechange=function(){!l||l.readyState!==4||l.status===0&&!(l.responseURL&&l.responseURL.indexOf("file:")===0)||setTimeout(d)},l.onabort=function(){!l||(r(new N("Request aborted",N.ECONNABORTED,t,l)),l=null)},l.onerror=function(){r(new N("Network Error",N.ERR_NETWORK,t,l)),l=null},l.ontimeout=function(){let g=t.timeout?"timeout of "+t.timeout+"ms exceeded":"timeout exceeded";const b=t.transitional||wi;t.timeoutErrorMessage&&(g=t.timeoutErrorMessage),r(new N(g,b.clarifyTimeoutError?N.ETIMEDOUT:N.ECONNABORTED,t,l)),l=null},pe.isStandardBrowserEnv){const m=(t.withCredentials||ll(u))&&t.xsrfCookieName&&il.read(t.xsrfCookieName);m&&i.set(t.xsrfHeaderName,m)}s===void 0&&i.setContentType(null),"setRequestHeader"in l&&p.forEach(i.toJSON(),function(g,b){l.setRequestHeader(b,g)}),p.isUndefined(t.withCredentials)||(l.withCredentials=!!t.withCredentials),o&&o!=="json"&&(l.responseType=t.responseType),typeof t.onDownloadProgress=="function"&&l.addEventListener("progress",as(t.onDownloadProgress,!0)),typeof t.onUploadProgress=="function"&&l.upload&&l.upload.addEventListener("progress",as(t.onUploadProgress)),(t.cancelToken||t.signal)&&(a=m=>{!l||(r(!m||m.type?new Et(null,t,l):m),l.abort(),l=null)},t.cancelToken&&t.cancelToken.subscribe(a),t.signal&&(t.signal.aborted?a():t.signal.addEventListener("abort",a)));const v=cl(u);if(v&&pe.protocols.indexOf(v)===-1){r(new N("Unsupported protocol "+v+":",N.ERR_BAD_REQUEST,t));return}l.send(s||null)})}const cs={http:ls,xhr:ls},us={getAdapter:t=>{if(p.isString(t)){const e=cs[t];if(!t)throw Error(p.hasOwnProp(t)?`Adapter '${t}' is not available in the build`:`Can not resolve adapter '${t}'`);return e}if(!p.isFunction(t))throw new TypeError("adapter is not a function");return t},adapters:cs},pl={"Content-Type":"application/x-www-form-urlencoded"};function bl(){let t;return typeof XMLHttpRequest<"u"?t=us.getAdapter("xhr"):typeof process<"u"&&p.kindOf(process)==="process"&&(t=us.getAdapter("http")),t}function vl(t,e,n){if(p.isString(t))try{return(e||JSON.parse)(t),p.trim(t)}catch(r){if(r.name!=="SyntaxError")throw r}return(n||JSON.stringify)(t)}const et={transitional:wi,adapter:bl(),transformRequest:[function(e,n){const r=n.getContentType()||"",s=r.indexOf("application/json")>-1,i=p.isObject(e);if(i&&p.isHTMLForm(e)&&(e=new FormData(e)),p.isFormData(e))return s&&s?JSON.stringify(xi(e)):e;if(p.isArrayBuffer(e)||p.isBuffer(e)||p.isStream(e)||p.isFile(e)||p.isBlob(e))return e;if(p.isArrayBufferView(e))return e.buffer;if(p.isURLSearchParams(e))return n.setContentType("application/x-www-form-urlencoded;charset=utf-8",!1),e.toString();let a;if(i){if(r.indexOf("application/x-www-form-urlencoded")>-1)return tl(e,this.formSerializer).toString();if((a=p.isFileList(e))||r.indexOf("multipart/form-data")>-1){const c=this.env&&this.env.FormData;return cn(a?{"files[]":e}:e,c&&new c,this.formSerializer)}}return i||s?(n.setContentType("application/json",!1),vl(e)):e}],transformResponse:[function(e){const n=this.transitional||et.transitional,r=n&&n.forcedJSONParsing,s=this.responseType==="json";if(e&&p.isString(e)&&(r&&!this.responseType||s)){const o=!(n&&n.silentJSONParsing)&&s;try{return JSON.parse(e)}catch(a){if(o)throw a.name==="SyntaxError"?N.from(a,N.ERR_BAD_RESPONSE,this,null,this.response):a}}return e}],timeout:0,xsrfCookieName:"XSRF-TOKEN",xsrfHeaderName:"X-XSRF-TOKEN",maxContentLength:-1,maxBodyLength:-1,env:{FormData:pe.classes.FormData,Blob:pe.classes.Blob},validateStatus:function(e){return e>=200&&e<300},headers:{common:{Accept:"application/json, text/plain, */*"}}};p.forEach(["delete","get","head"],function(e){et.headers[e]={}});p.forEach(["post","put","patch"],function(e){et.headers[e]=p.merge(pl)});function Rn(t,e){const n=this||et,r=e||n,s=re.from(r.headers);let i=r.data;return p.forEach(t,function(a){i=a.call(n,i,s.normalize(),e?e.status:void 0)}),s.normalize(),i}function Si(t){return!!(t&&t.__CANCEL__)}function Dn(t){if(t.cancelToken&&t.cancelToken.throwIfRequested(),t.signal&&t.signal.aborted)throw new Et}function ds(t){return Dn(t),t.headers=re.from(t.headers),t.data=Rn.call(t,t.transformRequest),(t.adapter||et.adapter)(t).then(function(r){return Dn(t),r.data=Rn.call(t,t.transformResponse,r),r.headers=re.from(r.headers),r},function(r){return Si(r)||(Dn(t),r&&r.response&&(r.response.data=Rn.call(t,t.transformResponse,r.response),r.response.headers=re.from(r.response.headers))),Promise.reject(r)})}function gt(t,e){e=e||{};const n={};function r(l,u){return p.isPlainObject(l)&&p.isPlainObject(u)?p.merge(l,u):p.isPlainObject(u)?p.merge({},u):p.isArray(u)?u.slice():u}function s(l){if(p.isUndefined(e[l])){if(!p.isUndefined(t[l]))return r(void 0,t[l])}else return r(t[l],e[l])}function i(l){if(!p.isUndefined(e[l]))return r(void 0,e[l])}function o(l){if(p.isUndefined(e[l])){if(!p.isUndefined(t[l]))return r(void 0,t[l])}else return r(void 0,e[l])}function a(l){if(l in e)return r(t[l],e[l]);if(l in t)return r(void 0,t[l])}const c={url:i,method:i,data:i,baseURL:o,transformRequest:o,transformResponse:o,paramsSerializer:o,timeout:o,timeoutMessage:o,withCredentials:o,adapter:o,responseType:o,xsrfCookieName:o,xsrfHeaderName:o,onUploadProgress:o,onDownloadProgress:o,decompress:o,maxContentLength:o,maxBodyLength:o,beforeRedirect:o,transport:o,httpAgent:o,httpsAgent:o,cancelToken:o,socketPath:o,responseEncoding:o,validateStatus:a};return p.forEach(Object.keys(t).concat(Object.keys(e)),function(u){const d=c[u]||s,v=d(u);p.isUndefined(v)&&d!==a||(n[u]=v)}),n}const $i="1.1.3",pr={};["object","boolean","number","function","string","symbol"].forEach((t,e)=>{pr[t]=function(r){return typeof r===t||"a"+(e<1?"n ":" ")+t}});const fs={};pr.transitional=function(e,n,r){function s(i,o){return"[Axios v"+$i+"] Transitional option '"+i+"'"+o+(r?". "+r:"")}return(i,o,a)=>{if(e===!1)throw new N(s(o," has been removed"+(n?" in "+n:"")),N.ERR_DEPRECATED);return n&&!fs[o]&&(fs[o]=!0,console.warn(s(o," has been deprecated since v"+n+" and will be removed in the near future"))),e?e(i,o,a):!0}};function yl(t,e,n){if(typeof t!="object")throw new N("options must be an object",N.ERR_BAD_OPTION_VALUE);const r=Object.keys(t);let s=r.length;for(;s-- >0;){const i=r[s],o=e[i];if(o){const a=t[i],c=a===void 0||o(a,i,t);if(c!==!0)throw new N("option "+i+" must be "+c,N.ERR_BAD_OPTION_VALUE);continue}if(n!==!0)throw new N("Unknown option "+i,N.ERR_BAD_OPTION)}}const Zn={assertOptions:yl,validators:pr},Ee=Zn.validators;class Fe{constructor(e){this.defaults=e,this.interceptors={request:new ss,response:new ss}}request(e,n){typeof e=="string"?(n=n||{},n.url=e):n=e||{},n=gt(this.defaults,n);const{transitional:r,paramsSerializer:s}=n;r!==void 0&&Zn.assertOptions(r,{silentJSONParsing:Ee.transitional(Ee.boolean),forcedJSONParsing:Ee.transitional(Ee.boolean),clarifyTimeoutError:Ee.transitional(Ee.boolean)},!1),s!==void 0&&Zn.assertOptions(s,{encode:Ee.function,serialize:Ee.function},!0),n.method=(n.method||this.defaults.method||"get").toLowerCase();const i=n.headers&&p.merge(n.headers.common,n.headers[n.method]);i&&p.forEach(["delete","get","head","post","put","patch","common"],function(g){delete n.headers[g]}),n.headers=new re(n.headers,i);const o=[];let a=!0;this.interceptors.request.forEach(function(g){typeof g.runWhen=="function"&&g.runWhen(n)===!1||(a=a&&g.synchronous,o.unshift(g.fulfilled,g.rejected))});const c=[];this.interceptors.response.forEach(function(g){c.push(g.fulfilled,g.rejected)});let l,u=0,d;if(!a){const m=[ds.bind(this),void 0];for(m.unshift.apply(m,o),m.push.apply(m,c),d=m.length,l=Promise.resolve(n);u<d;)l=l.then(m[u++],m[u++]);return l}d=o.length;let v=n;for(u=0;u<d;){const m=o[u++],g=o[u++];try{v=m(v)}catch(b){g.call(this,b);break}}try{l=ds.call(this,v)}catch(m){return Promise.reject(m)}for(u=0,d=c.length;u<d;)l=l.then(c[u++],c[u++]);return l}getUri(e){e=gt(this.defaults,e);const n=Ei(e.baseURL,e.url);return _i(n,e.params,e.paramsSerializer)}}p.forEach(["delete","get","head","options"],function(e){Fe.prototype[e]=function(n,r){return this.request(gt(r||{},{method:e,url:n,data:(r||{}).data}))}});p.forEach(["post","put","patch"],function(e){function n(r){return function(i,o,a){return this.request(gt(a||{},{method:e,headers:r?{"Content-Type":"multipart/form-data"}:{},url:i,data:o}))}}Fe.prototype[e]=n(),Fe.prototype[e+"Form"]=n(!0)});class br{constructor(e){if(typeof e!="function")throw new TypeError("executor must be a function.");let n;this.promise=new Promise(function(i){n=i});const r=this;this.promise.then(s=>{if(!r._listeners)return;let i=r._listeners.length;for(;i-- >0;)r._listeners[i](s);r._listeners=null}),this.promise.then=s=>{let i;const o=new Promise(a=>{r.subscribe(a),i=a}).then(s);return o.cancel=function(){r.unsubscribe(i)},o},e(function(i,o,a){r.reason||(r.reason=new Et(i,o,a),n(r.reason))})}throwIfRequested(){if(this.reason)throw this.reason}subscribe(e){if(this.reason){e(this.reason);return}this._listeners?this._listeners.push(e):this._listeners=[e]}unsubscribe(e){if(!this._listeners)return;const n=this._listeners.indexOf(e);n!==-1&&this._listeners.splice(n,1)}static source(){let e;return{token:new br(function(s){e=s}),cancel:e}}}function _l(t){return function(n){return t.apply(null,n)}}function wl(t){return p.isObject(t)&&t.isAxiosError===!0}function ki(t){const e=new Fe(t),n=ui(Fe.prototype.request,e);return p.extend(n,Fe.prototype,e,{allOwnKeys:!0}),p.extend(n,e,null,{allOwnKeys:!0}),n.create=function(s){return ki(gt(t,s))},n}const F=ki(et);F.Axios=Fe;F.CanceledError=Et;F.CancelToken=br;F.isCancel=Si;F.VERSION=$i;F.toFormData=cn;F.AxiosError=N;F.Cancel=F.CanceledError;F.all=function(e){return Promise.all(e)};F.spread=_l;F.isAxiosError=wl;F.formToJSON=t=>xi(p.isHTMLForm(t)?new FormData(t):t);const hs="http://0.0.0.0:3000",xl="http://0.0.0.0:8080",gs=window.location.origin;function El(){let t;gs==hs?t=xl:t="";const[e,n]=_(t),r=gs==hs;return{serverUrl:e,setServerUrl:n,withCredentials:r}}const te=ee(El);function Il(){const[t,e]=_("submit");return{tabName:t,setTabName:e}}const tt=ee(Il),Sl=y('<a id="tabhead_{props.tabName}" href="#" class="tabhead"></a>');function un(t){const{tabName:e,setTabName:n}=tt;return(()=>{const r=Sl.cloneNode(!0);return r.$$click=()=>n(t.tabName),f(r,()=>t.svg,null),f(r,()=>t.title,null),$(()=>r.classList.toggle("selected",e()==t.tabName)),r})()}R(["click"]);const $l=y('<svg fill="currentColor" stroke-width="0" xmlns="http://www.w3.org/2000/svg"></svg>'),kl=y("<title></title>");function ne(t,e){const n=ta(t.a,e);return(()=>{const r=$l.cloneNode(!0);return da(r,n,!0,!0),f(r,()=>ma,null),f(r,(()=>{const s=ve(()=>!!e.title,!0);return()=>s()&&(()=>{const i=kl.cloneNode(!0);return f(i,()=>e.title),i})()})(),null),$(s=>{const i=t.a.stroke,o={...e.style,overflow:"visible",color:e.color||"currentColor"},a=e.size||"1em",c=e.size||"1em",l=t.c;return i!==s._v$&&V(r,"stroke",s._v$=i),s._v$2=ci(r,o,s._v$2),a!==s._v$3&&V(r,"height",s._v$3=a),c!==s._v$4&&V(r,"width",s._v$4=c),l!==s._v$5&&(r.innerHTML=s._v$5=l),s},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0}),r})()}function Tl(t){return ne({a:{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",viewBox:"0 0 24 24"},c:'<path stroke="none" d="M0 0h24v24H0z"/><path d="M9 13L5 9l4-4M5 9h11a4 4 0 010 8h-1"/>'},t)}function Cl(t){return ne({a:{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",viewBox:"0 0 24 24"},c:'<path stroke="none" d="M0 0h24v24H0z"/><path d="M14 3v4a1 1 0 001 1h4"/><path d="M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2zM12 11v6"/><path d="M9.5 13.5L12 11l2.5 2.5"/>'},t)}function Al(){const t=h(Cl,{class:"tabheadicon",color:"rgb(156 163 175)"});return h(un,{tabName:"submit",title:"Submit",svg:t})}function Ol(t){return ne({a:{viewBox:"0 0 1024 1024"},c:'<path d="M518.3 459a8 8 0 00-12.6 0l-112 141.7a7.98 7.98 0 006.3 12.9h73.9V856c0 4.4 3.6 8 8 8h60c4.4 0 8-3.6 8-8V613.7H624c6.7 0 10.4-7.7 6.3-12.9L518.3 459z"/><path d="M811.4 366.7C765.6 245.9 648.9 160 512.2 160S258.8 245.8 213 366.6C127.3 389.1 64 467.2 64 560c0 110.5 89.5 200 199.9 200H304c4.4 0 8-3.6 8-8v-60c0-4.4-3.6-8-8-8h-40.1c-33.7 0-65.4-13.4-89-37.7-23.5-24.2-36-56.8-34.9-90.6.9-26.4 9.9-51.2 26.2-72.1 16.7-21.3 40.1-36.8 66.1-43.7l37.9-9.9 13.9-36.6c8.6-22.8 20.6-44.1 35.7-63.4a245.6 245.6 0 0152.4-49.9c41.1-28.9 89.5-44.2 140-44.2s98.9 15.3 140 44.2c19.9 14 37.5 30.8 52.4 49.9 15.1 19.3 27.1 40.7 35.7 63.4l13.8 36.5 37.8 10C846.1 454.5 884 503.8 884 560c0 33.1-12.9 64.3-36.3 87.7a123.07 123.07 0 01-87.6 36.3H720c-4.4 0-8 3.6-8 8v60c0 4.4 3.6 8 8 8h40.1C870.5 760 960 670.5 960 560c0-92.7-63.1-170.7-148.6-193.3z"/>'},t)}function Nl(t){return ne({a:{viewBox:"0 0 1024 1024"},c:'<path d="M920 760H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0-568H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0 284H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM216 712H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h72.4v20.5h-35.7c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h35.7V838H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4V716c0-2.2-1.8-4-4-4zM100 188h38v120c0 2.2 1.8 4 4 4h40c2.2 0 4-1.8 4-4V152c0-4.4-3.6-8-8-8h-78c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4zm116 240H100c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4h68.4l-70.3 77.7a8.3 8.3 0 00-2.1 5.4V592c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4v-36c0-2.2-1.8-4-4-4h-68.4l70.3-77.7a8.3 8.3 0 002.1-5.4V432c0-2.2-1.8-4-4-4z"/>'},t)}function Rl(){const t=h(Nl,{class:"tabheadicon",color:"rgb(156 163 175)"});return h(un,{tabName:"jobs",title:"Jobs",svg:t})}const Dl=y('<svg class="tabheadicon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"></path></svg>');function Pl(){const t=Dl.cloneNode(!0);return h(un,{tabName:"system",title:"System",svg:t})}function Ll(t){return ne({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>'},t)}function Ml(t){return ne({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>'},t)}function Ul(t){return ne({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>'},t)}function vr(t){return ne({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>'},t)}function jl(t){return ne({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>'},t)}function Fl(t){return ne({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>'},t)}function Bl(t){return ne({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>'},t)}function Hl(t){return ne({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>'},t)}function zl(){const t=h(Hl,{class:"tabheadicon",color:"rgb(156 163 175)"});return h(un,{tabName:"account",title:"Account",svg:t})}const Vl=y('<div id="verdiv" class="text-xs absolute left-4 bottom-2 text-gray-400"><span class="text-xs">v</span><span class="curverspan text-xs"></span></div>');function Wl(){return Vl.cloneNode(!0)}function Jl(){const[t,e]=_(!1);return{multiuser:t,setMultiuser:e}}const Ne=ee(Jl),ql=y('<div id="sidebar_static" class="md:flex md:w-36 md:flex-col md:fixed md:inset-y-0"><div class="flex-1 flex flex-col min-h-0 border-r border-gray-200"><div class="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto"><div class="flex items-center flex-shrink-0 px-4"><img class="h-16 w-auto" alt="Logo"></div><nav class="mt-5 flex-1 px-2 space-y-1"></nav></div></div></div>'),{serverUrl:Gl,setServerUrl:Tm,withCredentials:Cm}=te,{multiuser:Kl,setMultiuser:Am}=Ne;function Xl(){return(()=>{const t=ql.cloneNode(!0),e=t.firstChild,n=e.firstChild,r=n.firstChild,s=r.firstChild,i=r.nextSibling;return f(i,h(Al,{}),null),f(i,h(Rl,{}),null),f(i,h(Pl,{}),null),f(i,h(ie,{get when(){return Kl()==!0},get children(){return h(zl,{})}}),null),f(n,h(Wl,{}),null),$(()=>V(s,"src",Gl()+"/submit/images/logo_transparent_bw.png")),t})()}function Yl(t){return ne({a:{fill:"currentColor",viewBox:"0 0 16 16"},c:'<path d="M11.42 2l3.428 6-3.428 6H4.58L1.152 8 4.58 2h6.84zM4.58 1a1 1 0 00-.868.504l-3.428 6a1 1 0 000 .992l3.428 6A1 1 0 004.58 15h6.84a1 1 0 00.868-.504l3.429-6a1 1 0 000-.992l-3.429-6A1 1 0 0011.42 1H4.58z"/><path d="M6.848 5.933a2.5 2.5 0 102.5 4.33 2.5 2.5 0 00-2.5-4.33zm-1.78 3.915a3.5 3.5 0 116.061-3.5 3.5 3.5 0 01-6.062 3.5z"/>'},t)}async function Ti(t){const{serverUrl:e,setServerUrl:n}=te;return(await fetch(e()+t)).json()}const Ql="module_option_file__";function Zl(){const[t,e]=_({}),[n,r]=_({});function s(d){return d in t()?t()[d]:null}function i(d){var v=t();v[d.name]=d}function o(){Ti("/store/local").then(function(d){e(d)})}function a(d){return d in n()?n()[d]:h(Yl,{})}function c(d,v,m){const b=t()[d];b.module_options==null&&(b.module_options={}),v.type=="int"?m=parseInt(m):v.type=="float"&&(m=parseFloat(m));const w={value:m,method:v.method,type:v.type};console.log("@ vd=",w,v),b.module_options[v.name]=w}function l(d,v){console.log("@ modules=",d);let m={};for(const g in d){console.log("@ moduleName=",g);const b=d[g];if(b.module_options){m[g]={};for(const w in b.module_options){const x=b.module_options[w];if(console.log("@ d=",x),x.method=="file"){const S=Ql+g+"__"+w;console.log("@ key=",S,"value=",x.value),v.append(S,x.value)}else m[g][w]=x.value}Object.keys(m[g]).length==0&&delete m[g]}}return m}function u(d,v){const m=t()[d];if(m&&m.module_options){const g=m.module_options[v];return g||null}else return null}return{localModules:t,setLocalModules:e,getLocalModule:s,addLocalModule:i,loadAllModules:o,localModuleLogos:n,setLocalModuleLogos:r,getLocalModuleLogo:a,setModuleOption:c,getModuleOptions:l,getModuleOption:u}}const It=ee(Zl),ec=y('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function Dt(t){function e(){t.setAssembly(t.value),t.setShow(!1)}return(()=>{const n=ec.cloneNode(!0);return n.$$click=e,f(n,()=>t.title),n})()}R(["click"]);const tc=y('<div id="assembly-select" class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabindex="-1"><div class="py-1" role="none"></div></div>');function nc(t){return(()=>{const e=tc.cloneNode(!0),n=e.firstChild;return f(n,h(Dt,{value:"auto",title:"Auto",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),f(n,h(Dt,{value:"hg38",title:"GRCh38/hg38",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),f(n,h(Dt,{value:"hg19",title:"GRCh37/hg19",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),f(n,h(Dt,{value:"hg18",title:"GRCh36/hg18",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),$(()=>e.classList.toggle("hidden",!t.show)),e})()}const rc=y('<div id="assembly-select-panel" class="select-div relative inline-block text-left" value=""><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="assembly-select-div" title="Genome assembly">Genome assembly: </button></div></div>');function sc(t){const[e,n]=_(!1),r={"":"Auto",hg38:"GRCh38/hg38",hg19:"GRCh37/hg19",hg18:"GRCh36/hg18"};function s(i){n(!e())}return(()=>{const i=rc.cloneNode(!0),o=i.firstChild,a=o.firstChild;return a.firstChild,a.$$click=s,f(a,()=>r[t.assembly],null),f(a,h(vr,{class:"-mr-1 ml-2 h-5 w-5"}),null),f(i,h(nc,{get show(){return e()},get setAssembly(){return t.setAssembly},setShow:n}),null),i})()}R(["click"]);const ic=y('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function ms(t){function e(){t.setInputFormat(t.value),t.setShow(!1)}return(()=>{const n=ic.cloneNode(!0);return n.$$click=e,f(n,()=>t.title),n})()}R(["click"]);function oc(){const[t,e]=_(!1);return{logged:t,setLogged:e}}const Ve=ee(oc),ac=y('<div id="input-format-select" class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabindex="-1"><div class="py-1" role="none"></div></div>'),{multiuser:lc,setMultiuser:Om}=Ne,{logged:cc,setLogged:Nm}=Ve;async function uc(){if(lc()==!1||cc()==!0)return await Ti("/submit/converters")}function dc(t){const[e]=dr(uc);return Oe(()=>{var n={"":"Auto"};if(!!e()){for(var r=0;r<e().length;r++)n[e()[r].format]=e()[r].title;t.setInputFormats(n)}}),(()=>{const n=ac.cloneNode(!0),r=n.firstChild;return f(r,h(ms,{value:"",title:"Auto",get setInputFormat(){return t.setInputFormat},get setShow(){return t.setShow}}),null),f(r,h(ce,{get each(){return e()},children:function(s){return h(ms,{get value(){return s.format},get title(){return s.title},get setInputFormat(){return t.setInputFormat},get setShow(){return t.setShow}})}}),null),$(()=>n.classList.toggle("hidden",!t.show)),n})()}const fc=y('<div id="input-format-select-panel" class="select-div relative inline-block text-left ml-6" value=""><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="input-format-select-div" title="Format">Format: </button></div></div>');function hc(t){const[e,n]=_(!1),[r,s]=_({"":"Auto"});function i(o){n(!e())}return(()=>{const o=fc.cloneNode(!0),a=o.firstChild,c=a.firstChild;return c.firstChild,c.$$click=i,f(c,()=>r()[t.inputFormat],null),f(c,h(vr,{class:"-mr-1 ml-2 h-5 w-5"}),null),f(o,h(dc,{get show(){return e()},get setInputFormat(){return t.setInputFormat},setInputFormats:s,setShow:n}),null),o})()}R(["click"]);const gc=y('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100"><svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v3.75m-9.303 3.376C1.83 19.126 2.914 21 4.645 21h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 4.88c-.866-1.501-3.032-1.501-3.898 0L2.697 17.626zM12 17.25h.007v.008H12v-.008z"></path></svg></div><div class="mt-3 text-center sm:mt-5"><h3 class="text-lg font-medium leading-6 text-gray-900"></h3><div class="mt-2"><p class="text-sm text-gray-500"></p></div></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:text-sm">Dismiss</button></div></div></div></div></div>');function Ci(t){return(()=>{const e=gc.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.nextSibling,l=c.firstChild,u=l.nextSibling,d=u.firstChild,v=o.nextSibling,m=v.firstChild;return f(l,()=>t.title),f(d,()=>t.text),m.$$click=t.setShowDialog,m.$$clickData=!1,e})()}R(["click"]);const mc=y('<div id="input-upload-list-div" class="w-1/2 flex flex-col justify-center items-center p-2 relative h-full bg-gray-50"><button id="clear_inputfilelist_button" class="text-gray-500 bg-neutral-200 hover:bg-neutral-300 p-1 w-16 rounded-md absolute top-1 left-1" onclick="clearInputUploadList()">Clear</button><div id="input-upload-list-wrapper" class="flex w-full overflow-auto h-[13rem] absolute bottom-1 bg-gray-50"><div id="input-upload-list" class="h-full overflow-auto"></div></div></div>'),pc=y('<label id="input-drop-area" for="input-file" class="flex items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-md cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600"><div id="input-drop-box" class="w-1/2"><div class="flex flex-col items-center justify-center pt-5 pb-6"><p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> input files</p><p class="text-gray-500 mb-2"> or </p><button class="mb-2 text-sm text-gray-500 dark:text-gray-400 bg-neutral-200 hover:bg-neutral-300 p-2 rounded-md">Manually enter variants</button></div><input type="file" class="hidden" name="input-file" id="input-file" multiple></div></label>'),bc=y('<span class="pl-2 text-sm text-gray-600 hover:text-gray-400 cursor-pointer round-md inline-block w-5/6" title="Click to remove"></span>');function vc(t){const[e,n]=_(!1),[r,s]=_({title:"Problem",text:"?"});Oe(function(){});function i(a,c){c.preventDefault();for(var l=0;l<t.inputDataDrop.length;l++)if(t.inputDataDrop[l].name==a){t.setInputDataDrop([...t.inputDataDrop.slice(0,l),...t.inputDataDrop.slice(l+1,t.inputDataDrop.length)]);break}}function o(a){const c=a.target.files;for(var l=0;l<c.length;l++)if(c[l].name.indexOf(" ")>=0){s({title:"Problem",text:"Input file names should not have space."}),n(!0);break}t.setInputDataDrop([...t.inputDataDrop,...c])}return(()=>{const a=pc.cloneNode(!0),c=a.firstChild,l=c.firstChild,u=l.firstChild,d=u.nextSibling,v=d.nextSibling,m=l.nextSibling;return f(a,h(ie,{get when(){return t.inputDataDrop.length>0},get children(){const g=mc.cloneNode(!0),b=g.firstChild,w=b.nextSibling,x=w.firstChild;return f(x,h(ce,{get each(){return t.inputDataDrop},children:S=>(()=>{const T=bc.cloneNode(!0);return T.$$click=i,T.$$clickData=S.name,f(T,()=>S.name),T})()})),g}}),c),f(l,h(Ol,{class:"w-10 h-10",color:"#9ca3af"}),u),v.$$click=t.setInputMode,v.$$clickData="paste",m.addEventListener("change",o),f(a,h(va,{get children(){return h(ie,{get when(){return e()},get children(){return h(Ci,{get title(){return r().title},get text(){return r().text},setShowErrorDialog:n})}})}}),null),a})()}R(["click"]);const yc=y(`<div id="input-paste-area" class="relative w-full h-64 border-2 border-gray-300 border-dashed rounded-md"><textarea id="input-text" class="font-mono border-0 bg-gray-50 text-gray-600 p-4 resize-none w-full h-full" placeholder="Copy and paste or type input variants. VCF is supported. A quick and simple format is space-delimited one:

chr1 9384934 + A T

which is chromosome, position, strand, a reference allele, and an alternate allele.

Alternatively, paths to input files in the server can be used as well. For example,

/mnt/oakvar/input/sample/sample_1.vcf
"></textarea><div class="top-2 right-3 absolute cursor-pointer" title="Click to go back"></div><div class="absolute bottom-1 right-1 text-gray-400 text-sm"><button value="cravat" class="p-1 text-gray-500 bg-neutral-200 hover:bg-neutral-300">Try an example</button></div></div>`);function _c(t){function e(r){const{serverUrl:s,setServerUrl:i}=te;t.setAssembly("hg38"),t.setInputFormat("vcf"),fetch(`${s()}/submit/input-examples/${t.inputFormat}.${t.assembly}.txt`).then(o=>o.text()).then(o=>{t.changeInputData("paste",o)})}function n(r){t.changeInputData("paste",r.target.value)}return(()=>{const r=yc.cloneNode(!0),s=r.firstChild,i=s.nextSibling,o=i.nextSibling,a=o.firstChild;return s.$$keyup=n,i.$$click=t.setInputMode,i.$$clickData="drop",f(i,h(Tl,{class:"w-5 h-5 mr-2"})),a.$$click=e,$(()=>s.value=t.inputDataPaste),r})()}R(["keyup","click"]);const wc=y('<div id="job-name-div" class="mt-4 w-full"><textarea id="job-name" class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full " placeholder="(Optional) job name"></textarea></div>');function xc(t){function e(n){t.setJobName(n.target.value)}return(()=>{const n=wc.cloneNode(!0),r=n.firstChild;return r.$$keyup=e,$(()=>n.classList.toggle("hidden",!t.inputExists)),$(()=>r.value=t.jobName),n})()}R(["keyup"]);const Ec=y('<div id="submit-note-div" class="mt-4 w-full"><textarea id="submit-note" class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full" placeholder="(Optional) note for this job"></textarea></div>');function Ic(t){function e(n){t.setJobNote(n.target.value)}return(()=>{const n=Ec.cloneNode(!0),r=n.firstChild;return r.$$keyup=e,$(()=>n.classList.toggle("hidden",!t.inputExists)),$(()=>r.value=t.jobNote),n})()}R(["keyup"]);const Sc=y('<div id="submit-job-button-div" class="mt-4"><button id="submit-job-button" type="button" class="inline-flex items-center h-12 rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Annotate</button></div>');function $c(t){return(()=>{const e=Sc.cloneNode(!0),n=e.firstChild;return on(n,"click",t.submitFn,!0),$(()=>e.classList.toggle("hidden",!t.inputExists)),e})()}R(["click"]);const kc=y('<div id="input-div" class="w-[40rem] items-center flex flex-col" style="height: calc(100vh - 10rem);"><div class="flex"></div><div class="w-full flex items-center justify-center mt-1" ondragenter="onDragEnterInputFiles(event)" ondragover="onDragOverInputFiles(event)" ondragleave="onDragLeaveInputFiles(event)" ondrop="onDropInputFiles(event)"></div></div>');function Tc(t){function e(n,r){t.setInputMode(n),n=="drop"?t.setInputDataDrop(r):n=="paste"&&t.setInputDataPaste(r)}return Oe(function(){t.inputMode=="drop"?t.setInputExists(t.inputDataDrop.length>0):t.inputMode=="paste"&&t.setInputExists(t.inputDataPaste.length>0)}),(()=>{const n=kc.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return f(r,h(sc,{get assembly(){return t.assembly},get setAssembly(){return t.setAssembly}}),null),f(r,h(hc,{get inputFormat(){return t.inputFormat},get setInputFormat(){return t.setInputFormat}}),null),f(s,h(ai,{get children(){return[h(Kt,{get when(){return t.inputMode=="drop"},get children(){return h(vc,{get setInputMode(){return t.setInputMode},get inputDataDrop(){return t.inputDataDrop},get setInputDataDrop(){return t.setInputDataDrop}})}}),h(Kt,{get when(){return t.inputMode=="paste"},get children(){return h(_c,{get setInputMode(){return t.setInputMode},changeInputData:e,get inputDataPaste(){return t.inputDataPaste},get assembly(){return t.assembly},get setAssembly(){return t.setAssembly},get inputFormat(){return t.inputFormat},get setInputFormat(){return t.setInputFormat}})}})]}})),f(n,h(xc,{get inputExists(){return t.inputExists},get jobName(){return t.jobName},get setJobName(){return t.setJobName}}),null),f(n,h(Ic,{get inputExists(){return t.inputExists},get jobNote(){return t.jobNote},get setJobNote(){return t.setJobNote}}),null),f(n,h($c,{get inputExists(){return t.inputExists},get submitFn(){return t.submitFn}}),null),n})()}const Cc=y("<a></a>");function er(t){return(()=>{const e=Cc.cloneNode(!0);return on(e,"click",t.clickFn,!0),f(e,()=>t.children),$(n=>{const r="relative text-sm h-8 inline-flex items-center rounded-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-500 cursor-pointer focus:z-20 "+t.bgColor+" "+t.bgHoverColor,s=t.hrefValue,i=t.targetValue;return r!==n._v$&&li(e,n._v$=r),s!==n._v$2&&V(e,"href",n._v$2=s),i!==n._v$3&&V(e,"target",n._v$3=i),n},{_v$:void 0,_v$2:void 0,_v$3:void 0}),e})()}R(["click"]);const Ac=y('<input class="block w-full text-xs text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" type="file">'),Oc=y('<select class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"></select>'),Nc=y('<div class="flex flex-col mb-4"><span class="mb-2 font-xs"></span></div>'),Rc=y('<input type="text">'),Dc=y("<option></option>"),{setModuleOption:Pc,getModuleOptions:Rm,getModuleOption:Lc}=It;function Mc(t){const[e,n]=_(null);Oe(function(){const s=Lc(t.moduleName,t.option.name);e()==null&&s!=null&&n(s.value)});function r(s){const i=s.target.value;n(s.target.value),Pc(t.moduleName,t.option,i)}return(()=>{const s=Nc.cloneNode(!0),i=s.firstChild;return f(i,()=>t.option.title),f(s,h(ai,{get fallback(){return(()=>{const o=Rc.cloneNode(!0);return o.$$keyup=r,$(()=>o.value=e()),o})()},get children(){return[h(Kt,{get when(){return t.option.method=="file"},get children(){const o=Ac.cloneNode(!0);return o.addEventListener("change",r),o}}),h(Kt,{get when(){return t.option.method=="select"},get children(){const o=Oc.cloneNode(!0);return o.addEventListener("change",r),o.$$click=function(a){a.stopPropagation()},f(o,h(ce,{get each(){return t.option.options},children:a=>(()=>{const c=Dc.cloneNode(!0);return c.value=a,f(c,a),c})()})),$(()=>V(o,"title",t.option.help)),$(()=>o.value=e()),o}})]}}),null),$(()=>V(i,"title",t.option.help)),s})()}R(["click","keyup"]);const Uc=y('<div class="relative modulecard relative items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400 p-2 z-0 mb-2"><div class="absolute left-0 bottom-0 w-full p-2 cursor-default" style="background-color: rgba(68, 64, 60, 0.3);"><a class="relative remove-button text-sm h-8 inline-flex items-center rounded-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-500 cursor-pointer focus:z-20 bg-white hover:bg-gray-100">Remove</a></div><div><div class="float-left w-24 h-24 mr-2 flex justify-center items-center"><img class="w-20 rounded-lg"></div><div class="min-w-0 flex-1" style="min-height: 6rem;"><a class="focus:online-none"><p class="text-md font-semibold text-gray-700"></p><p class="text-sm text-gray-500"></p></a></div></div><div class="w-full"></div></div>'),{serverUrl:jc}=te,{localModules:Fc}=It;function yr(t){const e=Fc()[t.moduleName],n=e.type,[r,s]=_(!1);function i(d){for(const v in d)if(t.moduleName==v)return!0;return!1}function o(){return i(t.annotators)||i(t.postaggregators)||i(t.reporters)}function a(){let d;return n=="annotator"?d={...t.annotators}:n=="postaggregator"?d={...t.postaggregators}:n=="reporter"&&(d={...t.reporters}),d}function c(d){o()?delete d[t.moduleName]:d[t.moduleName]=e}function l(d){n=="annotator"?t.setAnnotators(d):n=="postaggregator"?t.setPostaggregators(d):n=="reporter"&&t.setReporters(d)}function u(d){d.stopPropagation();const v=d.target;if(t.cardType=="selected"){if(v.classList.contains("remove-button")){const m=a();c(m),l(m);return}}else{let m=a();c(m),l(m)}}return(()=>{const d=Uc.cloneNode(!0),v=d.firstChild,m=v.firstChild,g=v.nextSibling,b=g.firstChild,w=b.firstChild,x=b.nextSibling,S=x.firstChild,T=S.firstChild,P=T.nextSibling,U=g.nextSibling;return d.$$click=u,d.addEventListener("mouseleave",k=>s(!1,k)),d.addEventListener("mouseenter",k=>s(!0,k)),f(v,h(er,{class:"details-button w-full text-sm h-8 cursor-pointer",get classList(){return{hidden:t.cardType=="selected"}},bgColor:"bg-white",bgHoverColor:"hover:bg-gray-100",children:"Details"}),m),f(T,()=>e&&e.title),f(P,()=>e&&e.conf.description),f(U,h(ie,{get when(){return(t.cardType=="selected"||e.type=="reporter")&&e.conf.module_options},get children(){return h(ce,{get each(){return e.conf.module_options},children:k=>h(Mc,{get moduleName(){return t.moduleName},option:k})})}})),$(k=>{const W=!!o(),z=t.cardType!="selected",C=t.cardType!="selected",L=!!(t.cardType=="selected"&&e.conf.module_options),O=e&&e.name,K=e&&e.kind,B=!r()||t.cardType!="selected",J=t.cardType!="selected",De=jc()+"/store/locallogo?module="+t.moduleName;return W!==k._v$&&d.classList.toggle("checked",k._v$=W),z!==k._v$2&&d.classList.toggle("cursor-copy",k._v$2=z),C!==k._v$3&&d.classList.toggle("max-h-64",k._v$3=C),L!==k._v$4&&d.classList.toggle("pb-16",k._v$4=L),O!==k._v$5&&V(d,"name",k._v$5=O),K!==k._v$6&&V(d,"kind",k._v$6=K),B!==k._v$7&&v.classList.toggle("hidden",k._v$7=B),J!==k._v$8&&m.classList.toggle("hidden",k._v$8=J),De!==k._v$9&&V(w,"src",k._v$9=De),k},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0,_v$6:void 0,_v$7:void 0,_v$8:void 0,_v$9:void 0}),d})()}R(["click"]);const Bc=y('<div id="report-choice-div" class="w-[36rem] flex flex-col justify-center items-center"><div class="text-md text-gray-600">(Optional) reporters to run</div><div id="report-choice-items" class="w-96 grid gap-2 justify-center overflow-y-auto bg-gray-100 py-4 rounded-md" style="height: calc(100vh - 10rem);"></div></div>'),Hc=async()=>{const{serverUrl:t,setServerUrl:e}=te;return(await(await fetch(t()+"/submit/reporttypes")).json()).valid};function zc(t){const[e]=dr(Hc);return(()=>{const n=Bc.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return f(s,h(ce,{get each(){return e()},children:i=>h(yr,{moduleName:i+"reporter",get reporters(){return t.reporters},get setReporters(){return t.setReporters}})})),n})()}const Vc=y('<div id="cta-analysis-module-choice" class="absolute inset-x-0 bottom-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Click to select analysis modules</span></p></div></div></div></div></div>');function Wc(t){function e(){document.querySelector("#analysis-module-choice-div").scrollIntoView({behavior:"smooth"})}return(()=>{const n=Vc.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild;return n.$$click=e,f(o,h(Ll,{color:"#6b7280"}),a),n})()}R(["click"]);const Jc=y('<button type="button" class="filter-category"></button>');function ps(t){function e(n){t.setFilterCategory(t.value)}return(()=>{const n=Jc.cloneNode(!0);return n.$$click=e,f(n,()=>t.title),$(r=>{const s=t.value==t.filterCategory,i=t.pos=="left",o=t.pos=="right";return s!==r._v$&&n.classList.toggle("pinned",r._v$=s),i!==r._v$2&&n.classList.toggle("rounded-l-lg",r._v$2=i),o!==r._v$3&&n.classList.toggle("rounded-r-md",r._v$3=o),r},{_v$:void 0,_v$2:void 0,_v$3:void 0}),$(()=>n.value=t.value),n})()}R(["click"]);const qc=y('<div class="flex mb-2"><label for="search" class="sr-only">Search</label><input type="text" name="search" class="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm mr-2" placeholder="Search"><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Select all</button><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-2">Deselect all</button></div>');function Ai(t){function e(n){t.setSearchText(n.target.value)}return(()=>{const n=qc.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return s.$$keyup=e,$(()=>V(n,"id",`search-filtered-modules-${t.kind}`)),$(()=>s.value=t.searchText),n})()}R(["keyup"]);const{localModules:Gc}=It;function Oi(t){for(let e in t)return!1;return!0}function Kc(t,e){let n=[];for(const[r,s]of Object.entries(Gc())){let i=!0;r=="tagsampler"||r=="vcfinfo"||r=="varmeta"||s.type!="annotator"&&s.type!="postaggregator"?i=!1:e!=null&&(e=="no tag"?s.tags.length>0&&(i=!1):s.tags.indexOf(e)==-1&&(i=!1)),i&&t!=null&&(i=!1,(r.indexOf(t)>=0||s.title.indexOf(t)>=0||s.description&&s.description.indexOf(t)>=0)&&(i=!0)),i&&n.push(r)}return n.sort(),n}const Xc=y('<div class="filtered-modules-div overflow-auto pr-2" style="height: calc(95vh - 8rem);"></div>');function Ni(t){return(()=>{const e=Xc.cloneNode(!0);return f(e,h(ce,{get each(){return Kc(t.searchText,t.selectedTag)},children:n=>h(yr,{moduleName:n,get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}})})),$(n=>{const r=`filtered-modules-${t.kind}`,s=t.noCols==2,i=t.noCols==1;return r!==n._v$&&V(e,"id",n._v$=r),s!==n._v$2&&e.classList.toggle("grid-cols-2",n._v$2=s),i!==n._v$3&&e.classList.toggle("grid-cols-1",n._v$3=i),n},{_v$:void 0,_v$2:void 0,_v$3:void 0}),e})()}const Yc=y('<div id="analysis-module-filter-panel-all" class="analysis-module-filter-panel w-full mt-4 overflow-auto"></div>');function Qc(t){const[e,n]=_(null);return(()=>{const r=Yc.cloneNode(!0);return f(r,h(Ai,{kind:"all",get searchText(){return e()},setSearchText:n}),null),f(r,h(Ni,{kind:"all",noCols:1,get searchText(){return e()},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),$(()=>r.classList.toggle("hidden",t.filterCategory!="all")),r})()}const Zc=y('<div class="relative flex items-start mb-2"><div class="flex items-center"><input type="radio" name="module-tag" class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"><label class="ml-3 block text-sm font-medium text-gray-600"></label></div></div>');function eu(t){return t.replace(" ","_")}function tu(t){return t.replace(/\w\S*/g,function(e){return e.charAt(0).toUpperCase()+e.substr(1).toLowerCase()})}function nu(t){const e=`module-tag-radio-${eu(t.value)}`;return(()=>{const n=Zc.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.nextSibling;return s.$$click=t.setSelectedTag,s.$$clickData=t.value,V(s,"id",e),V(i,"for",e),f(i,()=>tu(t.value)),$(()=>s.value=t.value),n})()}R(["click"]);const ru=y('<div id="analysis-module-filter-panel-tags" class="analysis-module-filter-panel w-full mt-4 overflow-auto grid grid-cols-3"><div id="analysis-module-filter-items-tags" class="col-span-1 flex flex-col justify-leading pl-1 overflow-y-auto" style="height: calc(95vh - 8rem);"></div><div class="col-span-2"></div></div>'),su=async()=>{const{serverUrl:t,setServerUrl:e}=te;let n=await(await fetch(t()+"/submit/tags_annotators_postaggregators")).json();return n.push("no tag"),n};function iu(t){const[e]=dr(su),[n,r]=_(null),[s,i]=_(null);return(()=>{const o=ru.cloneNode(!0),a=o.firstChild,c=a.nextSibling;return f(a,h(ce,{get each(){return e()},children:l=>h(nu,{value:l,setSelectedTag:r})})),f(c,h(Ai,{kind:"tags",get searchText(){return s()},setSearchText:i}),null),f(c,h(Ni,{kind:"tags",noCols:1,get selectedTag(){return n()},get searchText(){return s()},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),$(()=>o.classList.toggle("hidden",t.filterCategory!="tags")),o})()}const ou=y('<div class="analysis-module-filter-wrapper col-span-7"><div id="analysis-module-filter-kinds" class="w-full"><div class="inline-flex rounded-md shadow-sm" role="group"></div></div></div>');function au(t){const[e,n]=_("all");return(()=>{const r=ou.cloneNode(!0),s=r.firstChild,i=s.firstChild;return f(i,h(ps,{value:"all",title:"All",pos:"left",get filterCategory(){return e()},setFilterCategory:n}),null),f(i,h(ps,{value:"tags",title:"Tags",pos:"right",get filterCategory(){return e()},setFilterCategory:n}),null),f(r,h(Qc,{get filterCategory(){return e()},get localModules(){return t.localModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),f(r,h(iu,{get filterCategory(){return e()},get localModules(){return t.localModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),r})()}const lu=y('<div class="col-span-4"><div class="text-gray-600 bg-gray-100 rounded-md border border-transparent font-medium px-3 py-1.5 h-[34px]">Selected analysis modules</div><div class="flex mb-2 mt-4"><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 h-[38px]">Clear</button></div><div class="relative filtered-modules-div overflow-auto pr-2" style="height: calc(95vh - 8rem);"></div></div>');function cu(t){function e(){let r=[];for(const s in t.annotators)r.push(s);for(const s in t.postaggregators)r.push(s);return r.sort(),r}function n(){t.setAnnotators({}),t.setPostaggregators({})}return(()=>{const r=lu.cloneNode(!0),s=r.firstChild,i=s.nextSibling,o=i.firstChild,a=i.nextSibling;return o.$$click=n,f(a,h(ce,{get each(){return e()},children:function(c){return h(yr,{moduleName:c,get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators},cardType:"selected"})}})),r})()}R(["click"]);const uu=y('<div id="cta-input" class="absolute inset-x-0 top-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Go back to the input panel</span></p></div></div></div></div></div>');function du(t){function e(){document.querySelector("#input-div").scrollIntoView({behavior:"smooth"})}return(()=>{const n=uu.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild;return n.$$click=e,f(o,h(Ul,{color:"#6b7280"}),a),n})()}R(["click"]);const fu=y('<div id="analysis-module-choice-div" class="relative container mt-6 mb-4 snap-center flex justify-center max-w-7xl h-[95vh] max-w-7xl"><div id="analysis-module-filter-div" class="bg-white p-4 rounded-md ml-4 mt-4 overflow-auto flex flex-col gap-8 text-gray-600 h-[95vh] w-full"><div id="analysis-module-div" class="grid grid-cols-12 gap-2 mt-8" style="height: calc(95vh - 20rem);"><div class="col-span-1 flex flex-col justify-center content-center items-center"></div></div></div></div>');function hu(t){return(()=>{const e=fu.cloneNode(!0),n=e.firstChild,r=n.firstChild,s=r.firstChild;return f(e,h(du,{}),n),f(r,h(au,{get localModules(){return t.localModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),s),f(s,h(Ml,{})),f(r,h(cu,{get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),e})()}const gu=y('<li><a href="#" class="block hover:bg-gray-50"><div class="py-4"><div class="flex items-center justify-between"><p class="truncate text-sm font-medium text-indigo-600"></p></div><div class="mt-2 sm:flex sm:justify-between"><div class="mt-2 w-full flex items-center text-sm text-gray-500 sm:mt-0"><div class="w-full bg-gray-200 rounded-full dark:bg-gray-700"><div class="bg-blue-600 text-xs font-medium text-blue-100 text-center p-0.5 leading-none rounded-full">%</div></div></div></div></div></a></li>');function mu(t){return(()=>{const e=gu.cloneNode(!0),n=e.firstChild,r=n.firstChild,s=r.firstChild,i=s.firstChild,o=s.nextSibling,a=o.firstChild,c=a.firstChild,l=c.firstChild,u=l.firstChild;return f(i,()=>t.fileName),f(l,()=>t.progress,u),$(()=>l.style.setProperty("width",t.progress+"%")),e})()}const pu=y('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6"><div><div class="mt-3 text-center sm:mt-5"><ul role="list" class="divide-y divide-gray-200"></ul></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm">Cancel</button></div></div></div></div></div>');function bu(t){function e(){t.controller.abort()}return(()=>{const n=pu.cloneNode(!0),r=n.firstChild,s=r.nextSibling,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.firstChild,l=c.firstChild,u=a.nextSibling,d=u.firstChild;return f(l,h(mu,{fileName:"Uploading...",get progress(){return t.uploadState.progress}})),d.$$click=e,n})()}R(["click"]);const vu=y('<div class="tabcontent p-4 snap-y snap-mandatory h-screen overflow-y-auto"><div class="relative container flex gap-8 snap-center max-w-7xl h-[95vh] justify-center items-start"></div></div>'),yu=y("<div>Loading...</div>"),{tabName:_u}=tt,{localModules:wu,getModuleOptions:xu}=It,{serverUrl:Eu,withCredentials:Iu}=te,{logged:Su}=Ve,{multiuser:$u}=Ne;function ku(t){const[e,n]=_("drop"),[r,s]=_(""),[i,o]=_([]),[a,c]=_(""),[l,u]=_([]),[d,v]=_([]),[m,g]=_([]),[b,w]=_(""),[x,S]=_(!1),[T,P]=_(null),[U,k]=_(null),[W,z]=_(!1),[C,L]=_({});let O=[],K=null,B={},J;Oe(function(){$u()&&!Su()&&De()});function De(){n("drop"),s(""),o([]),c([]),u([]),v([]),g([]),w(""),S(!1),P(null),k(null),z(!1),L({})}function bn(){return a().startsWith("#serverfile")}function vn(){let A=[],D=a().split(`
`);for(var oe=1;oe<D.length;oe++){let Z=D[oe];Z==""||Z.startsWith("#")||A.push(Z.trim())}A.length>0&&(B.inputServerFiles=A)}function yn(){O=[];const A=new Blob([a()],{type:"text/plain"});O.push(new File([A],"input"))}function _n(){bn()?vn():yn()}function st(A){if(A!=null&&(e()=="drop"?O=i():e()=="paste"&&_n(),O.length>0)){for(var D=0;D<O.length;D++)A.append("file_"+D,O[D]),console.log("@ appending",O[D]);console.log("@@ formData=",A)}}function wn(){B.annotators=[];for(const A in l())B.annotators.push(A)}function xe(){B.postaggregators=[];for(const A in d())B.postaggregators.push(A)}function xn(){B.reports=[];for(const A in m())B.reports.push(A.substring(0,A.lastIndexOf("reporter")))}function En(){B.genome=b()}function In(){B.input_format=r()}function it(){B.job_name=T()}function Sn(){B.note=U()}function $n(A){console.log("@ anns=",l(),d(),m());let D={};for(const Z in l())D[Z]=l()[Z];for(const Z in d())D[Z]=d()[Z];for(const Z in m())D[Z]=m()[Z];console.log("@ modules=",D);const oe=xu(D,A);B.module_options=oe}function E(A){console.log("@ submitOption=",B),console.log("@ formData=",A),J=new AbortController,z(!0),L({progress:0}),F({method:"post",url:Eu()+"/submit/submit?"+Math.random(),data:A,transformRequest:()=>A,signal:J.signal,withCredentials:Iu,onUploadProgress:D=>{let oe=Math.round(D.progress*100);L({progress:oe})}}).then(function(D){z(!1),setTimeout(function(){t.setJobsTrigger(!t.jobsTrigger)},500)}).catch(function(D){console.error(D),D.code!="ERR_CANCELED"&&(console.error(D),alert(D)),L({}),z(!1)})}function q(){O={},B={},K=new FormData,st(K),wn(),xe(),xn(),En(),In(),it(),Sn(),$n(K),B.writeadmindb=!0,K.append("options",JSON.stringify(B)),E(K)}return(()=>{const A=vu.cloneNode(!0),D=A.firstChild;return f(D,h(Tc,{get inputMode(){return e()},setInputMode:n,get inputDataDrop(){return i()},setInputDataDrop:o,get inputDataPaste(){return a()},setInputDataPaste:c,get assembly(){return b()},setAssembly:w,get inputFormat(){return r()},setInputFormat:s,get inputExists(){return x()},setInputExists:S,get jobName(){return T()},setJobName:P,get jobNote(){return U()},setJobNote:k,submitFn:q}),null),f(D,h(ie,{get when(){return x()},get children(){return[h(ie,{get when(){return!Oi(wu())},get fallback(){return yu.cloneNode(!0)},get children(){return h(zc,{get reporters(){return m()},setReporters:g})}}),h(Wc,{})]}}),null),f(A,h(ie,{get when(){return x()},get children(){return h(hu,{get annotators(){return l()},setAnnotators:u,get postaggregators(){return d()},setPostaggregators:v})}}),null),f(A,h(ie,{get when(){return W()},get children(){return h(bu,{get uploadState(){return C()},controller:J})}}),null),$(()=>A.classList.toggle("hidden",_u()!="submit")),A})()}const tr=Symbol("store-raw"),mt=Symbol("store-node"),Tu=Symbol("store-name");function Ri(t,e){let n=t[be];if(!n&&(Object.defineProperty(t,be,{value:n=new Proxy(t,Ou)}),!Array.isArray(t))){const r=Object.keys(t),s=Object.getOwnPropertyDescriptors(t);for(let i=0,o=r.length;i<o;i++){const a=r[i];if(s[a].get){const c=s[a].get.bind(n);Object.defineProperty(t,a,{enumerable:s[a].enumerable,get:c})}}}return n}function Xt(t){let e;return t!=null&&typeof t=="object"&&(t[be]||!(e=Object.getPrototypeOf(t))||e===Object.prototype||Array.isArray(t))}function pt(t,e=new Set){let n,r,s,i;if(n=t!=null&&t[tr])return n;if(!Xt(t)||e.has(t))return t;if(Array.isArray(t)){Object.isFrozen(t)?t=t.slice(0):e.add(t);for(let o=0,a=t.length;o<a;o++)s=t[o],(r=pt(s,e))!==s&&(t[o]=r)}else{Object.isFrozen(t)?t=Object.assign({},t):e.add(t);const o=Object.keys(t),a=Object.getOwnPropertyDescriptors(t);for(let c=0,l=o.length;c<l;c++)i=o[c],!a[i].get&&(s=t[i],(r=pt(s,e))!==s&&(t[i]=r))}return t}function _r(t){let e=t[mt];return e||Object.defineProperty(t,mt,{value:e={}}),e}function nr(t,e,n){return t[e]||(t[e]=Pi(n))}function Cu(t,e){const n=Reflect.getOwnPropertyDescriptor(t,e);return!n||n.get||!n.configurable||e===be||e===mt||e===Tu||(delete n.value,delete n.writable,n.get=()=>t[be][e]),n}function Di(t){if(ei()){const e=_r(t);(e._||(e._=Pi()))()}}function Au(t){return Di(t),Reflect.ownKeys(t)}function Pi(t){const[e,n]=_(t,{equals:!1,internal:!0});return e.$=n,e}const Ou={get(t,e,n){if(e===tr)return t;if(e===be)return n;if(e===qn)return Di(t),n;const r=_r(t),s=r.hasOwnProperty(e);let i=s?r[e]():t[e];if(e===mt||e==="__proto__")return i;if(!s){const o=Object.getOwnPropertyDescriptor(t,e);ei()&&(typeof i!="function"||t.hasOwnProperty(e))&&!(o&&o.get)&&(i=nr(r,e,i)())}return Xt(i)?Ri(i):i},has(t,e){return e===tr||e===be||e===qn||e===mt||e==="__proto__"?!0:(this.get(t,e,t),e in t)},set(){return!0},deleteProperty(){return!0},ownKeys:Au,getOwnPropertyDescriptor:Cu};function Yt(t,e,n,r=!1){if(!r&&t[e]===n)return;const s=t[e],i=t.length;n===void 0?delete t[e]:t[e]=n;let o=_r(t),a;(a=nr(o,e,s))&&a.$(()=>n),Array.isArray(t)&&t.length!==i&&(a=nr(o,"length",i))&&a.$(t.length),(a=o._)&&a.$()}function Li(t,e){const n=Object.keys(e);for(let r=0;r<n.length;r+=1){const s=n[r];Yt(t,s,e[s])}}function Nu(t,e){if(typeof e=="function"&&(e=e(t)),e=pt(e),Array.isArray(e)){if(t===e)return;let n=0,r=e.length;for(;n<r;n++){const s=e[n];t[n]!==s&&Yt(t,n,s)}Yt(t,"length",r)}else Li(t,e)}function ut(t,e,n=[]){let r,s=t;if(e.length>1){r=e.shift();const o=typeof r,a=Array.isArray(t);if(Array.isArray(r)){for(let c=0;c<r.length;c++)ut(t,[r[c]].concat(e),n);return}else if(a&&o==="function"){for(let c=0;c<t.length;c++)r(t[c],c)&&ut(t,[c].concat(e),n);return}else if(a&&o==="object"){const{from:c=0,to:l=t.length-1,by:u=1}=r;for(let d=c;d<=l;d+=u)ut(t,[d].concat(e),n);return}else if(e.length>1){ut(t[r],e,[r].concat(n));return}s=t[r],n=[r].concat(n)}let i=e[0];typeof i=="function"&&(i=i(s,n),i===s)||r===void 0&&i==null||(i=pt(i),r===void 0||Xt(s)&&Xt(i)&&!Array.isArray(i)?Li(s,i):Yt(t,r,i))}function Ru(...[t,e]){const n=pt(t||{}),r=Array.isArray(n),s=Ri(n);function i(...o){Jo(()=>{r&&o.length===1?Nu(n,o[0]):ut(n,o)})}return[s,i]}const Du=y('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function Pu(t){function e(){t.setAction(t.optionValue),t.execute(),t.setShow(!1)}return(()=>{const n=Du.cloneNode(!0);return n.$$click=e,f(n,()=>t.optionTitle),n})()}R(["click"]);const Lu=y('<div class="option-list ease-in absolute right-0 z-10 mt-12 w-24 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu"><div class="py-1" role="none"></div></div>');function Mu(t){return(()=>{const e=Lu.cloneNode(!0),n=e.firstChild;return f(n,h(ce,{get each(){return t.options},children:function(r){return h(Pu,{get optionValue(){return r.value},get optionTitle(){return r.title},get execute(){return t.execute},get setAction(){return t.setAction},get setShow(){return t.setShow}})}})),$(()=>e.classList.toggle("hidden",!t.show)),e})()}const Uu=y('<div class="select-div relative inline-flex text-left"><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="assembly-select-div" title="Job action">Action</button></div></div>');function ju(t){const[e,n]=_(!1),[r,s]=_(""),i=[{value:"abort",title:"Abort"},{value:"delete",title:"Delete"}];function o(){t.performJobAction(r())}function a(c){n(!e())}return(()=>{const c=Uu.cloneNode(!0),l=c.firstChild,u=l.firstChild;return u.firstChild,u.$$click=a,f(u,h(vr,{class:"-mr-1 ml-2 h-5 w-5"}),null),f(c,h(Mu,{get show(){return e()},options:i,execute:o,setAction:s,setShow:n}),null),c})()}R(["click"]);const Fu=y('<div class="flex bg-white pb-2 mt-2"><div class="flex"><nav class="isolate inline-flex rounded-md shadow-sm ml-8" aria-label="Pagination"><a href="#" class="jobs-table-page-nav-btn relative inline-flex items-center rounded-l-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span aria-current="page" class="relative z-10 inline-flex items-center border bg-white border-gray-300 text-gray-500 px-4 py-2 text-sm font-medium focus:z-20"></span><a href="#" class="jobs-table-page-nav-btn relative inline-flex items-center rounded-r-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Go to page</span><input type="text" class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">Go</a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Show</span><input type="text" class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">jobs per page</a><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20 ml-4"></a></nav></div></div>');function Bu(t){function e(){let o=t.pageno;o=o-1,o<=0&&(o=1),o!=t.pageno&&t.setPageno(o)}function n(){let o=t.pageno;o=o+1,o!=t.pageno&&t.setPageno(o)}function r(o){let a=o.target.value;try{a=parseInt(a)}catch(c){console.error(c);return}a<1&&(a=1),t.setPageno(a)}function s(o){let a=o.target.value;try{a=parseInt(a)}catch(c){console.error(c);return}t.setPagesize(a)}function i(o){t.setJobsTrigger(!t.jobsTrigger)}return(()=>{const o=Fu.cloneNode(!0),a=o.firstChild,c=a.firstChild,l=c.firstChild,u=l.nextSibling,d=u.nextSibling,v=d.nextSibling,m=v.nextSibling,g=m.nextSibling,b=g.nextSibling,w=b.nextSibling,x=w.nextSibling,S=x.nextSibling;return f(a,h(ju,{get performJobAction(){return t.performJobAction}}),c),l.$$click=e,f(l,h(jl,{class:"w-5 h-5"})),f(u,()=>t.pageno),d.$$click=n,f(d,h(Fl,{class:"w-5 h-5"})),m.addEventListener("change",r),w.addEventListener("change",s),S.$$click=i,f(S,h(Bl,{class:"w-5 h-5"})),$(()=>m.value=t.pageno),$(()=>w.value=t.pagesize),o})()}R(["click"]);const Hu=y('<span class="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800"></span>'),zu=y('<span class="inline-flex rounded-full bg-amber-100 px-2 text-xs font-semibold leading-5 text-amber-800"></span>'),Vu=y('<span class="inline-flex rounded-full bg-red-100 px-2 text-xs font-semibold leading-5 text-red-800"></span>'),Wu=y('<span class="inline-flex text-xs"></span>'),Ju=y('<tr class="text-sm h-16"><td scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8 bg-gray-50"><input type="checkbox" class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></td><td class="jobs-table-td"></td><td class="jobs-table-td bg-gray-50"></td><td class="jobs-table-td"></td><td class="jobs-table-td bg-gray-50"></td><td class="jobs-table-td"></td><td class="jobs-table-td bg-gray-50 text-xs"></td><td class="jobs-table-td"></td></tr>');function qu(t){return t=="Finished"||t=="Error"||t=="Aborted"}function Gu(t){const{serverUrl:e,withCredentials:n}=te,r=1e3;let s=null;Jt(()=>clearInterval(s));function i(){t.changeJobChecked(t.job.uid),t.setAllMarksOn(null)}function o(){F.get(e()+"/submit/jobstatus",{params:{uid:t.job.uid},withCredentials:n}).then(function(g){const b=g.data;qu(b)&&clearInterval(s),t.changeJobStatus(t.job.uid,b)}).catch(function(g){console.error(g)})}function a(){const g=t.job.status;g!="Finished"&&g!="Error"&&g!="Aborted"&&(s=setInterval(function(){o()},r))}function c(){return t.job.status=="Finished"}function l(){return c()?h(er,{children:"View",get hrefValue(){return e()+"/result/nocache/index.html?uid="+t.job.uid},targetValue:"_blank",bgColor:"bg-sky-100",bgHoverColor:"hover:bg-sky-200"}):h(er,{children:"Log",get hrefValue(){return e()+"/submit/joblog?uid="+t.job.uid},targetValue:"_blank",bgColor:"bg-gray-100",bgHoverColor:"hover:bg-gray-200"})}function u(){const g=t.job.status;return g=="Finished"?(()=>{const b=Hu.cloneNode(!0);return f(b,()=>t.job.status),b})():g=="Aborted"?(()=>{const b=zu.cloneNode(!0);return f(b,()=>t.job.status),b})():g=="Error"?(()=>{const b=Vu.cloneNode(!0);return f(b,()=>t.job.status),b})():(()=>{const b=Wu.cloneNode(!0);return f(b,()=>t.job.status),b})()}function d(){return t.job.info_json.orig_input_fname?t.job.info_json.orig_input_fname.join(", "):""}function v(){return(""+new Date(t.job.info_json.submission_time)).split("GMT")[0]}function m(){let g=[];const b=t.job.info_json;if(!b)return"";const w=b.annotators;if(w)for(const S of w)S!="original_input"&&g.push(S);const x=b.postaggregators;if(x)for(const S of x)g.push(S);return g.join(", ")}return a(),(()=>{const g=Ju.cloneNode(!0),b=g.firstChild,w=b.firstChild,x=b.nextSibling,S=x.nextSibling,T=S.nextSibling,P=T.nextSibling,U=P.nextSibling,k=U.nextSibling,W=k.nextSibling;return w.addEventListener("change",i),f(x,()=>t.job.name),f(S,u),f(T,l),f(P,d),f(U,m),f(k,v),f(W,()=>t.job.info_json.note),$(()=>w.checked=t.job.checked),g})()}const Ku=y('<div class="flex flex-col"><div class="relative shadow ring-1 ring-black ring-opacity-5 md:rounded-lg overflow-auto"><table class="table-fixed divide-y divide-gray-300"><thead class="table-header-group bg-gray-50 block"><tr><th scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8"><input type="checkbox" class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></th><th scope="col" class="jobs-table-th min-w-[10rem]">Name</th><th scope="col" class="jobs-table-th min-w-[5rem]">State</th><th scope="col" class="jobs-table-th min-w-[5rem]">View</th><th scope="col" class="jobs-table-th min-w-[20rem]">Input</th><th scope="col" class="jobs-table-th min-w-[10rem]">Modules</th><th scope="col" class="jobs-table-th min-w-[8rem]">Submitted</th><th scope="col" class="jobs-table-th w-full">Note</th></tr></thead><tbody class="table-row-group divide-y divide-gray-200 bg-white block overflow-auto h-[36rem]"></tbody></table></div></div>');function Xu(t){const[e,n]=_(null);function r(){if(e()==!0?n(!1):(e()==null||e()==!1)&&n(!0),e()==!0)for(const s of t.jobs)t.changeJobChecked(s.uid,!0);else if(e()==!1)for(const s of t.jobs)t.changeJobChecked(s.uid,!1)}return(()=>{const s=Ku.cloneNode(!0),i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.firstChild,l=c.firstChild,u=l.firstChild,d=a.nextSibling;return u.$$click=r,f(d,h(ce,{get each(){return t.jobs},children:v=>h(Gu,{job:v,get changeJobStatus(){return t.changeJobStatus},get changeJobChecked(){return t.changeJobChecked},setAllMarksOn:n})})),$(()=>u.value=e()),s})()}R(["click"]);const Yu=y('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="text-center"><p class="text-sm text-gray-500"></p></div></div></div></div></div></div>');function Qu(t){return(()=>{const e=Yu.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.firstChild;return f(c,()=>t.msg),$(()=>e.classList.toggle("hidden",t.msg==null)),e})()}const Zu=y('<div id="tab_jobs" class="tabcontent px-6 mb-4"><div></div></div>'),{serverUrl:bs,withCredentials:vs}=te,{logged:ed,setLogged:td}=Ve,{multiuser:nd}=Ne;function rd(t){const{tabName:e}=tt,[n,r]=Ru([]),[s,i]=_(1),[o,a]=_(10),[c,l]=_(null);Oe(function(){s(),o(),t.jobsTrigger,(nd()==!1||ed()==!0)&&v()});function u(b,w){r(x=>x.uid==b,"status",w)}function d(b,w){w==null?r(x=>x.uid==b,"checked",x=>!x):r(x=>x.uid==b,"checked",w)}function v(){F.post(bs()+"/submit/jobs",{pageno:s(),pagesize:o()},{withCredentials:vs}).then(function(b){if(b.status=="error"){td(!1);return}const w=b.data;r(w)}).catch(function(b){console.error(b),b.response.status==404&&i(s()-1)})}function m(b,w){const x=b.map(S=>S.uid);F.post(bs()+"/submit/delete_jobs",{uids:x,abort_only:w},{withCredentials:vs}).then(function(){t.setJobsTrigger(!t.jobsTrigger),l(null)}).catch(function(S){console.error(S),l(null)})}function g(b){const w=n.filter(x=>x.checked);b=="delete"?(l("Deleting jobs..."),m(w,!1)):b=="abort"&&(l("Aborting jobs..."),m(w,!0))}return(()=>{const b=Zu.cloneNode(!0),w=b.firstChild;return f(w,h(Bu,{get pageno(){return s()},setPageno:i,get pagesize(){return o()},setPagesize:a,get jobsTrigger(){return t.jobsTrigger},get setJobsTrigger(){return t.setJobsTrigger},performJobAction:g}),null),f(w,h(Xu,{jobs:n,changeJobStatus:u,changeJobChecked:d}),null),f(b,h(Qu,{get msg(){return c()}}),null),$(()=>b.classList.toggle("hidden",e()!="jobs")),b})()}const sd=y('<div id="tab_system" class="tabcontent"><div class="p-4"><button type="button" class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 text-sm font-medium leading-4 text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Download system log</button></div></div>'),{serverUrl:id,setServerUrl:Dm,withCredentials:Pm}=te;function od(){const{tabName:t,setTabName:e}=tt;function n(){F({url:id()+"/submit/systemlog",method:"GET",responseType:"blob"}).then(function(r){let s=document.createElement("a");s.href=window.URL.createObjectURL(new Blob([r.data],{type:"text/plain"})),s.download=r.headers["content-disposition"].split("=")[1],document.body.appendChild(s),s.click(),document.body.removeChild(s)}).catch(function(r){console.error(r)})}return(()=>{const r=sd.cloneNode(!0),s=r.firstChild,i=s.firstChild;return i.$$click=n,$(()=>r.classList.toggle("hidden",t()!="system")),r})()}R(["click"]);/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *//**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Mi=function(t){const e=[];let n=0;for(let r=0;r<t.length;r++){let s=t.charCodeAt(r);s<128?e[n++]=s:s<2048?(e[n++]=s>>6|192,e[n++]=s&63|128):(s&64512)===55296&&r+1<t.length&&(t.charCodeAt(r+1)&64512)===56320?(s=65536+((s&1023)<<10)+(t.charCodeAt(++r)&1023),e[n++]=s>>18|240,e[n++]=s>>12&63|128,e[n++]=s>>6&63|128,e[n++]=s&63|128):(e[n++]=s>>12|224,e[n++]=s>>6&63|128,e[n++]=s&63|128)}return e},ad=function(t){const e=[];let n=0,r=0;for(;n<t.length;){const s=t[n++];if(s<128)e[r++]=String.fromCharCode(s);else if(s>191&&s<224){const i=t[n++];e[r++]=String.fromCharCode((s&31)<<6|i&63)}else if(s>239&&s<365){const i=t[n++],o=t[n++],a=t[n++],c=((s&7)<<18|(i&63)<<12|(o&63)<<6|a&63)-65536;e[r++]=String.fromCharCode(55296+(c>>10)),e[r++]=String.fromCharCode(56320+(c&1023))}else{const i=t[n++],o=t[n++];e[r++]=String.fromCharCode((s&15)<<12|(i&63)<<6|o&63)}}return e.join("")},Ui={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(t,e){if(!Array.isArray(t))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let s=0;s<t.length;s+=3){const i=t[s],o=s+1<t.length,a=o?t[s+1]:0,c=s+2<t.length,l=c?t[s+2]:0,u=i>>2,d=(i&3)<<4|a>>4;let v=(a&15)<<2|l>>6,m=l&63;c||(m=64,o||(v=64)),r.push(n[u],n[d],n[v],n[m])}return r.join("")},encodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(t):this.encodeByteArray(Mi(t),e)},decodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(t):ad(this.decodeStringToByteArray(t,e))},decodeStringToByteArray(t,e){this.init_();const n=e?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let s=0;s<t.length;){const i=n[t.charAt(s++)],a=s<t.length?n[t.charAt(s)]:0;++s;const l=s<t.length?n[t.charAt(s)]:64;++s;const d=s<t.length?n[t.charAt(s)]:64;if(++s,i==null||a==null||l==null||d==null)throw Error();const v=i<<2|a>>4;if(r.push(v),l!==64){const m=a<<4&240|l>>2;if(r.push(m),d!==64){const g=l<<6&192|d;r.push(g)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let t=0;t<this.ENCODED_VALS.length;t++)this.byteToCharMap_[t]=this.ENCODED_VALS.charAt(t),this.charToByteMap_[this.byteToCharMap_[t]]=t,this.byteToCharMapWebSafe_[t]=this.ENCODED_VALS_WEBSAFE.charAt(t),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[t]]=t,t>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(t)]=t,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(t)]=t)}}},ld=function(t){const e=Mi(t);return Ui.encodeByteArray(e,!0)},ji=function(t){return ld(t).replace(/\./g,"")},Fi=function(t){try{return Ui.decodeString(t,!0)}catch(e){console.error("base64Decode failed: ",e)}return null};/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Q(){return typeof navigator<"u"&&typeof navigator.userAgent=="string"?navigator.userAgent:""}function cd(){return typeof window<"u"&&!!(window.cordova||window.phonegap||window.PhoneGap)&&/ios|iphone|ipod|ipad|android|blackberry|iemobile/i.test(Q())}function ud(){const t=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof t=="object"&&t.id!==void 0}function dd(){return typeof navigator=="object"&&navigator.product==="ReactNative"}function fd(){const t=Q();return t.indexOf("MSIE ")>=0||t.indexOf("Trident/")>=0}function hd(){return typeof indexedDB=="object"}function gd(){return new Promise((t,e)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(r);s.onsuccess=()=>{s.result.close(),n||self.indexedDB.deleteDatabase(r),t(!0)},s.onupgradeneeded=()=>{n=!1},s.onerror=()=>{var i;e(((i=s.error)===null||i===void 0?void 0:i.message)||"")}}catch(n){e(n)}})}function md(){if(typeof self<"u")return self;if(typeof window<"u")return window;if(typeof global<"u")return global;throw new Error("Unable to locate global object.")}/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const pd=()=>md().__FIREBASE_DEFAULTS__,bd=()=>{if(typeof process>"u"||typeof process.env>"u")return;const t=process.env.__FIREBASE_DEFAULTS__;if(t)return JSON.parse(t)},vd=()=>{if(typeof document>"u")return;let t;try{t=document.cookie.match(/__FIREBASE_DEFAULTS__=([^;]+)/)}catch{return}const e=t&&Fi(t[1]);return e&&JSON.parse(e)},wr=()=>{try{return pd()||bd()||vd()}catch(t){console.info(`Unable to get __FIREBASE_DEFAULTS__ due to: ${t}`);return}},yd=t=>{var e,n;return(n=(e=wr())===null||e===void 0?void 0:e.emulatorHosts)===null||n===void 0?void 0:n[t]},_d=()=>{var t;return(t=wr())===null||t===void 0?void 0:t.config},Bi=t=>{var e;return(e=wr())===null||e===void 0?void 0:e[`_${t}`]};/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class wd{constructor(){this.reject=()=>{},this.resolve=()=>{},this.promise=new Promise((e,n)=>{this.resolve=e,this.reject=n})}wrapCallback(e){return(n,r)=>{n?this.reject(n):this.resolve(r),typeof e=="function"&&(this.promise.catch(()=>{}),e.length===1?e(n):e(n,r))}}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const xd="FirebaseError";class Re extends Error{constructor(e,n,r){super(n),this.code=e,this.customData=r,this.name=xd,Object.setPrototypeOf(this,Re.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,St.prototype.create)}}class St{constructor(e,n,r){this.service=e,this.serviceName=n,this.errors=r}create(e,...n){const r=n[0]||{},s=`${this.service}/${e}`,i=this.errors[e],o=i?Ed(i,r):"Error",a=`${this.serviceName}: ${o} (${s}).`;return new Re(s,a,r)}}function Ed(t,e){return t.replace(Id,(n,r)=>{const s=e[r];return s!=null?String(s):`<${r}?>`})}const Id=/\{\$([^}]+)}/g;function Sd(t){for(const e in t)if(Object.prototype.hasOwnProperty.call(t,e))return!1;return!0}function Qt(t,e){if(t===e)return!0;const n=Object.keys(t),r=Object.keys(e);for(const s of n){if(!r.includes(s))return!1;const i=t[s],o=e[s];if(ys(i)&&ys(o)){if(!Qt(i,o))return!1}else if(i!==o)return!1}for(const s of r)if(!n.includes(s))return!1;return!0}function ys(t){return t!==null&&typeof t=="object"}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function $t(t){const e=[];for(const[n,r]of Object.entries(t))Array.isArray(r)?r.forEach(s=>{e.push(encodeURIComponent(n)+"="+encodeURIComponent(s))}):e.push(encodeURIComponent(n)+"="+encodeURIComponent(r));return e.length?"&"+e.join("&"):""}function dt(t){const e={};return t.replace(/^\?/,"").split("&").forEach(r=>{if(r){const[s,i]=r.split("=");e[decodeURIComponent(s)]=decodeURIComponent(i)}}),e}function ft(t){const e=t.indexOf("?");if(!e)return"";const n=t.indexOf("#",e);return t.substring(e,n>0?n:void 0)}function $d(t,e){const n=new kd(t,e);return n.subscribe.bind(n)}class kd{constructor(e,n){this.observers=[],this.unsubscribes=[],this.observerCount=0,this.task=Promise.resolve(),this.finalized=!1,this.onNoObservers=n,this.task.then(()=>{e(this)}).catch(r=>{this.error(r)})}next(e){this.forEachObserver(n=>{n.next(e)})}error(e){this.forEachObserver(n=>{n.error(e)}),this.close(e)}complete(){this.forEachObserver(e=>{e.complete()}),this.close()}subscribe(e,n,r){let s;if(e===void 0&&n===void 0&&r===void 0)throw new Error("Missing Observer.");Td(e,["next","error","complete"])?s=e:s={next:e,error:n,complete:r},s.next===void 0&&(s.next=Pn),s.error===void 0&&(s.error=Pn),s.complete===void 0&&(s.complete=Pn);const i=this.unsubscribeOne.bind(this,this.observers.length);return this.finalized&&this.task.then(()=>{try{this.finalError?s.error(this.finalError):s.complete()}catch{}}),this.observers.push(s),i}unsubscribeOne(e){this.observers===void 0||this.observers[e]===void 0||(delete this.observers[e],this.observerCount-=1,this.observerCount===0&&this.onNoObservers!==void 0&&this.onNoObservers(this))}forEachObserver(e){if(!this.finalized)for(let n=0;n<this.observers.length;n++)this.sendOne(n,e)}sendOne(e,n){this.task.then(()=>{if(this.observers!==void 0&&this.observers[e]!==void 0)try{n(this.observers[e])}catch(r){typeof console<"u"&&console.error&&console.error(r)}})}close(e){this.finalized||(this.finalized=!0,e!==void 0&&(this.finalError=e),this.task.then(()=>{this.observers=void 0,this.onNoObservers=void 0}))}}function Td(t,e){if(typeof t!="object"||t===null)return!1;for(const n of e)if(n in t&&typeof t[n]=="function")return!0;return!1}function Pn(){}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ue(t){return t&&t._delegate?t._delegate:t}class Xe{constructor(e,n,r){this.name=e,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Me="[DEFAULT]";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Cd{constructor(e,n){this.name=e,this.container=n,this.component=null,this.instances=new Map,this.instancesDeferred=new Map,this.instancesOptions=new Map,this.onInitCallbacks=new Map}get(e){const n=this.normalizeInstanceIdentifier(e);if(!this.instancesDeferred.has(n)){const r=new wd;if(this.instancesDeferred.set(n,r),this.isInitialized(n)||this.shouldAutoInitialize())try{const s=this.getOrInitializeService({instanceIdentifier:n});s&&r.resolve(s)}catch{}}return this.instancesDeferred.get(n).promise}getImmediate(e){var n;const r=this.normalizeInstanceIdentifier(e?.identifier),s=(n=e?.optional)!==null&&n!==void 0?n:!1;if(this.isInitialized(r)||this.shouldAutoInitialize())try{return this.getOrInitializeService({instanceIdentifier:r})}catch(i){if(s)return null;throw i}else{if(s)return null;throw Error(`Service ${this.name} is not available`)}}getComponent(){return this.component}setComponent(e){if(e.name!==this.name)throw Error(`Mismatching Component ${e.name} for Provider ${this.name}.`);if(this.component)throw Error(`Component for ${this.name} has already been provided`);if(this.component=e,!!this.shouldAutoInitialize()){if(Od(e))try{this.getOrInitializeService({instanceIdentifier:Me})}catch{}for(const[n,r]of this.instancesDeferred.entries()){const s=this.normalizeInstanceIdentifier(n);try{const i=this.getOrInitializeService({instanceIdentifier:s});r.resolve(i)}catch{}}}}clearInstance(e=Me){this.instancesDeferred.delete(e),this.instancesOptions.delete(e),this.instances.delete(e)}async delete(){const e=Array.from(this.instances.values());await Promise.all([...e.filter(n=>"INTERNAL"in n).map(n=>n.INTERNAL.delete()),...e.filter(n=>"_delete"in n).map(n=>n._delete())])}isComponentSet(){return this.component!=null}isInitialized(e=Me){return this.instances.has(e)}getOptions(e=Me){return this.instancesOptions.get(e)||{}}initialize(e={}){const{options:n={}}=e,r=this.normalizeInstanceIdentifier(e.instanceIdentifier);if(this.isInitialized(r))throw Error(`${this.name}(${r}) has already been initialized`);if(!this.isComponentSet())throw Error(`Component ${this.name} has not been registered yet`);const s=this.getOrInitializeService({instanceIdentifier:r,options:n});for(const[i,o]of this.instancesDeferred.entries()){const a=this.normalizeInstanceIdentifier(i);r===a&&o.resolve(s)}return s}onInit(e,n){var r;const s=this.normalizeInstanceIdentifier(n),i=(r=this.onInitCallbacks.get(s))!==null&&r!==void 0?r:new Set;i.add(e),this.onInitCallbacks.set(s,i);const o=this.instances.get(s);return o&&e(o,s),()=>{i.delete(e)}}invokeOnInitCallbacks(e,n){const r=this.onInitCallbacks.get(n);if(!!r)for(const s of r)try{s(e,n)}catch{}}getOrInitializeService({instanceIdentifier:e,options:n={}}){let r=this.instances.get(e);if(!r&&this.component&&(r=this.component.instanceFactory(this.container,{instanceIdentifier:Ad(e),options:n}),this.instances.set(e,r),this.instancesOptions.set(e,n),this.invokeOnInitCallbacks(r,e),this.component.onInstanceCreated))try{this.component.onInstanceCreated(this.container,e,r)}catch{}return r||null}normalizeInstanceIdentifier(e=Me){return this.component?this.component.multipleInstances?e:Me:e}shouldAutoInitialize(){return!!this.component&&this.component.instantiationMode!=="EXPLICIT"}}function Ad(t){return t===Me?void 0:t}function Od(t){return t.instantiationMode==="EAGER"}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Nd{constructor(e){this.name=e,this.providers=new Map}addComponent(e){const n=this.getProvider(e.name);if(n.isComponentSet())throw new Error(`Component ${e.name} has already been registered with ${this.name}`);n.setComponent(e)}addOrOverwriteComponent(e){this.getProvider(e.name).isComponentSet()&&this.providers.delete(e.name),this.addComponent(e)}getProvider(e){if(this.providers.has(e))return this.providers.get(e);const n=new Cd(e,this);return this.providers.set(e,n),n}getProviders(){return Array.from(this.providers.values())}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */var j;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(j||(j={}));const Rd={debug:j.DEBUG,verbose:j.VERBOSE,info:j.INFO,warn:j.WARN,error:j.ERROR,silent:j.SILENT},Dd=j.INFO,Pd={[j.DEBUG]:"log",[j.VERBOSE]:"log",[j.INFO]:"info",[j.WARN]:"warn",[j.ERROR]:"error"},Ld=(t,e,...n)=>{if(e<t.logLevel)return;const r=new Date().toISOString(),s=Pd[e];if(s)console[s](`[${r}]  ${t.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class Hi{constructor(e){this.name=e,this._logLevel=Dd,this._logHandler=Ld,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in j))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?Rd[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,j.DEBUG,...e),this._logHandler(this,j.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,j.VERBOSE,...e),this._logHandler(this,j.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,j.INFO,...e),this._logHandler(this,j.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,j.WARN,...e),this._logHandler(this,j.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,j.ERROR,...e),this._logHandler(this,j.ERROR,...e)}}const Md=(t,e)=>e.some(n=>t instanceof n);let _s,ws;function Ud(){return _s||(_s=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function jd(){return ws||(ws=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const zi=new WeakMap,rr=new WeakMap,Vi=new WeakMap,Ln=new WeakMap,xr=new WeakMap;function Fd(t){const e=new Promise((n,r)=>{const s=()=>{t.removeEventListener("success",i),t.removeEventListener("error",o)},i=()=>{n(ke(t.result)),s()},o=()=>{r(t.error),s()};t.addEventListener("success",i),t.addEventListener("error",o)});return e.then(n=>{n instanceof IDBCursor&&zi.set(n,t)}).catch(()=>{}),xr.set(e,t),e}function Bd(t){if(rr.has(t))return;const e=new Promise((n,r)=>{const s=()=>{t.removeEventListener("complete",i),t.removeEventListener("error",o),t.removeEventListener("abort",o)},i=()=>{n(),s()},o=()=>{r(t.error||new DOMException("AbortError","AbortError")),s()};t.addEventListener("complete",i),t.addEventListener("error",o),t.addEventListener("abort",o)});rr.set(t,e)}let sr={get(t,e,n){if(t instanceof IDBTransaction){if(e==="done")return rr.get(t);if(e==="objectStoreNames")return t.objectStoreNames||Vi.get(t);if(e==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return ke(t[e])},set(t,e,n){return t[e]=n,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function Hd(t){sr=t(sr)}function zd(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...n){const r=t.call(Mn(this),e,...n);return Vi.set(r,e.sort?e.sort():[e]),ke(r)}:jd().includes(t)?function(...e){return t.apply(Mn(this),e),ke(zi.get(this))}:function(...e){return ke(t.apply(Mn(this),e))}}function Vd(t){return typeof t=="function"?zd(t):(t instanceof IDBTransaction&&Bd(t),Md(t,Ud())?new Proxy(t,sr):t)}function ke(t){if(t instanceof IDBRequest)return Fd(t);if(Ln.has(t))return Ln.get(t);const e=Vd(t);return e!==t&&(Ln.set(t,e),xr.set(e,t)),e}const Mn=t=>xr.get(t);function Wd(t,e,{blocked:n,upgrade:r,blocking:s,terminated:i}={}){const o=indexedDB.open(t,e),a=ke(o);return r&&o.addEventListener("upgradeneeded",c=>{r(ke(o.result),c.oldVersion,c.newVersion,ke(o.transaction))}),n&&o.addEventListener("blocked",()=>n()),a.then(c=>{i&&c.addEventListener("close",()=>i()),s&&c.addEventListener("versionchange",()=>s())}).catch(()=>{}),a}const Jd=["get","getKey","getAll","getAllKeys","count"],qd=["put","add","delete","clear"],Un=new Map;function xs(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if(Un.get(e))return Un.get(e);const n=e.replace(/FromIndex$/,""),r=e!==n,s=qd.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(s||Jd.includes(n)))return;const i=async function(o,...a){const c=this.transaction(o,s?"readwrite":"readonly");let l=c.store;return r&&(l=l.index(a.shift())),(await Promise.all([l[n](...a),s&&c.done]))[0]};return Un.set(e,i),i}Hd(t=>({...t,get:(e,n,r)=>xs(e,n)||t.get(e,n,r),has:(e,n)=>!!xs(e,n)||t.has(e,n)}));/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Gd{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(Kd(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function Kd(t){const e=t.getComponent();return e?.type==="VERSION"}const ir="@firebase/app",Es="0.8.4";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const He=new Hi("@firebase/app"),Xd="@firebase/app-compat",Yd="@firebase/analytics-compat",Qd="@firebase/analytics",Zd="@firebase/app-check-compat",ef="@firebase/app-check",tf="@firebase/auth",nf="@firebase/auth-compat",rf="@firebase/database",sf="@firebase/database-compat",of="@firebase/functions",af="@firebase/functions-compat",lf="@firebase/installations",cf="@firebase/installations-compat",uf="@firebase/messaging",df="@firebase/messaging-compat",ff="@firebase/performance",hf="@firebase/performance-compat",gf="@firebase/remote-config",mf="@firebase/remote-config-compat",pf="@firebase/storage",bf="@firebase/storage-compat",vf="@firebase/firestore",yf="@firebase/firestore-compat",_f="firebase",wf="9.14.0";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const or="[DEFAULT]",xf={[ir]:"fire-core",[Xd]:"fire-core-compat",[Qd]:"fire-analytics",[Yd]:"fire-analytics-compat",[ef]:"fire-app-check",[Zd]:"fire-app-check-compat",[tf]:"fire-auth",[nf]:"fire-auth-compat",[rf]:"fire-rtdb",[sf]:"fire-rtdb-compat",[of]:"fire-fn",[af]:"fire-fn-compat",[lf]:"fire-iid",[cf]:"fire-iid-compat",[uf]:"fire-fcm",[df]:"fire-fcm-compat",[ff]:"fire-perf",[hf]:"fire-perf-compat",[gf]:"fire-rc",[mf]:"fire-rc-compat",[pf]:"fire-gcs",[bf]:"fire-gcs-compat",[vf]:"fire-fst",[yf]:"fire-fst-compat","fire-js":"fire-js",[_f]:"fire-js-all"};/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Zt=new Map,ar=new Map;function Ef(t,e){try{t.container.addComponent(e)}catch(n){He.debug(`Component ${e.name} failed to register with FirebaseApp ${t.name}`,n)}}function bt(t){const e=t.name;if(ar.has(e))return He.debug(`There were multiple attempts to register component ${e}.`),!1;ar.set(e,t);for(const n of Zt.values())Ef(n,t);return!0}function Wi(t,e){const n=t.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),t.container.getProvider(e)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const If={["no-app"]:"No Firebase App '{$appName}' has been created - call Firebase App.initializeApp()",["bad-app-name"]:"Illegal App name: '{$appName}",["duplicate-app"]:"Firebase App named '{$appName}' already exists with different options or config",["app-deleted"]:"Firebase App named '{$appName}' already deleted",["no-options"]:"Need to provide options, when not being deployed to hosting via source.",["invalid-app-argument"]:"firebase.{$appName}() takes either no argument or a Firebase App instance.",["invalid-log-argument"]:"First argument to `onLog` must be null or a function.",["idb-open"]:"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.",["idb-get"]:"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.",["idb-set"]:"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.",["idb-delete"]:"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}."},Te=new St("app","Firebase",If);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Sf{constructor(e,n,r){this._isDeleted=!1,this._options=Object.assign({},e),this._config=Object.assign({},n),this._name=n.name,this._automaticDataCollectionEnabled=n.automaticDataCollectionEnabled,this._container=r,this.container.addComponent(new Xe("app",()=>this,"PUBLIC"))}get automaticDataCollectionEnabled(){return this.checkDestroyed(),this._automaticDataCollectionEnabled}set automaticDataCollectionEnabled(e){this.checkDestroyed(),this._automaticDataCollectionEnabled=e}get name(){return this.checkDestroyed(),this._name}get options(){return this.checkDestroyed(),this._options}get config(){return this.checkDestroyed(),this._config}get container(){return this._container}get isDeleted(){return this._isDeleted}set isDeleted(e){this._isDeleted=e}checkDestroyed(){if(this.isDeleted)throw Te.create("app-deleted",{appName:this._name})}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const dn=wf;function Ji(t,e={}){let n=t;typeof e!="object"&&(e={name:e});const r=Object.assign({name:or,automaticDataCollectionEnabled:!1},e),s=r.name;if(typeof s!="string"||!s)throw Te.create("bad-app-name",{appName:String(s)});if(n||(n=_d()),!n)throw Te.create("no-options");const i=Zt.get(s);if(i){if(Qt(n,i.options)&&Qt(r,i.config))return i;throw Te.create("duplicate-app",{appName:s})}const o=new Nd(s);for(const c of ar.values())o.addComponent(c);const a=new Sf(n,r,o);return Zt.set(s,a),a}function $f(t=or){const e=Zt.get(t);if(!e&&t===or)return Ji();if(!e)throw Te.create("no-app",{appName:t});return e}function Je(t,e,n){var r;let s=(r=xf[t])!==null&&r!==void 0?r:t;n&&(s+=`-${n}`);const i=s.match(/\s|\//),o=e.match(/\s|\//);if(i||o){const a=[`Unable to register library "${s}" with version "${e}":`];i&&a.push(`library name "${s}" contains illegal characters (whitespace or "/")`),i&&o&&a.push("and"),o&&a.push(`version name "${e}" contains illegal characters (whitespace or "/")`),He.warn(a.join(" "));return}bt(new Xe(`${s}-version`,()=>({library:s,version:e}),"VERSION"))}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const kf="firebase-heartbeat-database",Tf=1,vt="firebase-heartbeat-store";let jn=null;function qi(){return jn||(jn=Wd(kf,Tf,{upgrade:(t,e)=>{switch(e){case 0:t.createObjectStore(vt)}}}).catch(t=>{throw Te.create("idb-open",{originalErrorMessage:t.message})})),jn}async function Cf(t){var e;try{return(await qi()).transaction(vt).objectStore(vt).get(Gi(t))}catch(n){if(n instanceof Re)He.warn(n.message);else{const r=Te.create("idb-get",{originalErrorMessage:(e=n)===null||e===void 0?void 0:e.message});He.warn(r.message)}}}async function Is(t,e){var n;try{const s=(await qi()).transaction(vt,"readwrite");return await s.objectStore(vt).put(e,Gi(t)),s.done}catch(r){if(r instanceof Re)He.warn(r.message);else{const s=Te.create("idb-set",{originalErrorMessage:(n=r)===null||n===void 0?void 0:n.message});He.warn(s.message)}}}function Gi(t){return`${t.name}!${t.options.appId}`}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Af=1024,Of=30*24*60*60*1e3;class Nf{constructor(e){this.container=e,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new Df(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){const n=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),r=Ss();if(this._heartbeatsCache===null&&(this._heartbeatsCache=await this._heartbeatsCachePromise),!(this._heartbeatsCache.lastSentHeartbeatDate===r||this._heartbeatsCache.heartbeats.some(s=>s.date===r)))return this._heartbeatsCache.heartbeats.push({date:r,agent:n}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(s=>{const i=new Date(s.date).valueOf();return Date.now()-i<=Of}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,this._heartbeatsCache===null||this._heartbeatsCache.heartbeats.length===0)return"";const e=Ss(),{heartbeatsToSend:n,unsentEntries:r}=Rf(this._heartbeatsCache.heartbeats),s=ji(JSON.stringify({version:2,heartbeats:n}));return this._heartbeatsCache.lastSentHeartbeatDate=e,r.length>0?(this._heartbeatsCache.heartbeats=r,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}}function Ss(){return new Date().toISOString().substring(0,10)}function Rf(t,e=Af){const n=[];let r=t.slice();for(const s of t){const i=n.find(o=>o.agent===s.agent);if(i){if(i.dates.push(s.date),$s(n)>e){i.dates.pop();break}}else if(n.push({agent:s.agent,dates:[s.date]}),$s(n)>e){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class Df{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return hd()?gd().then(()=>!0).catch(()=>!1):!1}async read(){return await this._canUseIndexedDBPromise?await Cf(this.app)||{heartbeats:[]}:{heartbeats:[]}}async overwrite(e){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return Is(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return Is(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:[...s.heartbeats,...e.heartbeats]})}else return}}function $s(t){return ji(JSON.stringify({version:2,heartbeats:t})).length}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Pf(t){bt(new Xe("platform-logger",e=>new Gd(e),"PRIVATE")),bt(new Xe("heartbeat",e=>new Nf(e),"PRIVATE")),Je(ir,Es,t),Je(ir,Es,"esm2017"),Je("fire-js","")}Pf("");function Er(t,e){var n={};for(var r in t)Object.prototype.hasOwnProperty.call(t,r)&&e.indexOf(r)<0&&(n[r]=t[r]);if(t!=null&&typeof Object.getOwnPropertySymbols=="function")for(var s=0,r=Object.getOwnPropertySymbols(t);s<r.length;s++)e.indexOf(r[s])<0&&Object.prototype.propertyIsEnumerable.call(t,r[s])&&(n[r[s]]=t[r[s]]);return n}function Ki(){return{["dependent-sdk-initialized-before-auth"]:"Another Firebase SDK was initialized and is trying to use Auth before Auth is initialized. Please be sure to call `initializeAuth` or `getAuth` before starting any other Firebase SDK."}}const Lf=Ki,Xi=new St("auth","Firebase",Ki());/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ks=new Hi("@firebase/auth");function Ft(t,...e){ks.logLevel<=j.ERROR&&ks.error(`Auth (${dn}): ${t}`,...e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function se(t,...e){throw Ir(t,...e)}function ae(t,...e){return Ir(t,...e)}function Yi(t,e,n){const r=Object.assign(Object.assign({},Lf()),{[e]:n});return new St("auth","Firebase",r).create(e,{appName:t.name})}function Mf(t,e,n){const r=n;if(!(e instanceof r))throw r.name!==e.constructor.name&&se(t,"argument-error"),Yi(t,"argument-error",`Type of ${e.constructor.name} does not match expected instance.Did you pass a reference from a different Auth SDK?`)}function Ir(t,...e){if(typeof t!="string"){const n=e[0],r=[...e.slice(1)];return r[0]&&(r[0].appName=t.name),t._errorFactory.create(n,...r)}return Xi.create(t,...e)}function I(t,e,...n){if(!t)throw Ir(e,...n)}function he(t){const e="INTERNAL ASSERTION FAILED: "+t;throw Ft(e),new Error(e)}function ye(t,e){t||he(e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ts=new Map;function ge(t){ye(t instanceof Function,"Expected a class definition");let e=Ts.get(t);return e?(ye(e instanceof t,"Instance stored in cache mismatched with class"),e):(e=new t,Ts.set(t,e),e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Uf(t,e){const n=Wi(t,"auth");if(n.isInitialized()){const s=n.getImmediate(),i=n.getOptions();if(Qt(i,e??{}))return s;se(s,"already-initialized")}return n.initialize({options:e})}function jf(t,e){const n=e?.persistence||[],r=(Array.isArray(n)?n:[n]).map(ge);e?.errorMap&&t._updateErrorMap(e.errorMap),t._initializeWithPersistence(r,e?.popupRedirectResolver)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function lr(){var t;return typeof self<"u"&&((t=self.location)===null||t===void 0?void 0:t.href)||""}function Ff(){return Cs()==="http:"||Cs()==="https:"}function Cs(){var t;return typeof self<"u"&&((t=self.location)===null||t===void 0?void 0:t.protocol)||null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Bf(){return typeof navigator<"u"&&navigator&&"onLine"in navigator&&typeof navigator.onLine=="boolean"&&(Ff()||ud()||"connection"in navigator)?navigator.onLine:!0}function Hf(){if(typeof navigator>"u")return null;const t=navigator;return t.languages&&t.languages[0]||t.language||null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class kt{constructor(e,n){this.shortDelay=e,this.longDelay=n,ye(n>e,"Short delay should be less than long delay!"),this.isMobile=cd()||dd()}get(){return Bf()?this.isMobile?this.longDelay:this.shortDelay:Math.min(5e3,this.shortDelay)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Sr(t,e){ye(t.emulator,"Emulator should always be set here");const{url:n}=t.emulator;return e?`${n}${e.startsWith("/")?e.slice(1):e}`:n}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Qi{static initialize(e,n,r){this.fetchImpl=e,n&&(this.headersImpl=n),r&&(this.responseImpl=r)}static fetch(){if(this.fetchImpl)return this.fetchImpl;if(typeof self<"u"&&"fetch"in self)return self.fetch;he("Could not find fetch implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static headers(){if(this.headersImpl)return this.headersImpl;if(typeof self<"u"&&"Headers"in self)return self.Headers;he("Could not find Headers implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static response(){if(this.responseImpl)return this.responseImpl;if(typeof self<"u"&&"Response"in self)return self.Response;he("Could not find Response implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const zf={CREDENTIAL_MISMATCH:"custom-token-mismatch",MISSING_CUSTOM_TOKEN:"internal-error",INVALID_IDENTIFIER:"invalid-email",MISSING_CONTINUE_URI:"internal-error",INVALID_PASSWORD:"wrong-password",MISSING_PASSWORD:"internal-error",EMAIL_EXISTS:"email-already-in-use",PASSWORD_LOGIN_DISABLED:"operation-not-allowed",INVALID_IDP_RESPONSE:"invalid-credential",INVALID_PENDING_TOKEN:"invalid-credential",FEDERATED_USER_ID_ALREADY_LINKED:"credential-already-in-use",MISSING_REQ_TYPE:"internal-error",EMAIL_NOT_FOUND:"user-not-found",RESET_PASSWORD_EXCEED_LIMIT:"too-many-requests",EXPIRED_OOB_CODE:"expired-action-code",INVALID_OOB_CODE:"invalid-action-code",MISSING_OOB_CODE:"internal-error",CREDENTIAL_TOO_OLD_LOGIN_AGAIN:"requires-recent-login",INVALID_ID_TOKEN:"invalid-user-token",TOKEN_EXPIRED:"user-token-expired",USER_NOT_FOUND:"user-token-expired",TOO_MANY_ATTEMPTS_TRY_LATER:"too-many-requests",INVALID_CODE:"invalid-verification-code",INVALID_SESSION_INFO:"invalid-verification-id",INVALID_TEMPORARY_PROOF:"invalid-credential",MISSING_SESSION_INFO:"missing-verification-id",SESSION_EXPIRED:"code-expired",MISSING_ANDROID_PACKAGE_NAME:"missing-android-pkg-name",UNAUTHORIZED_DOMAIN:"unauthorized-continue-uri",INVALID_OAUTH_CLIENT_ID:"invalid-oauth-client-id",ADMIN_ONLY_OPERATION:"admin-restricted-operation",INVALID_MFA_PENDING_CREDENTIAL:"invalid-multi-factor-session",MFA_ENROLLMENT_NOT_FOUND:"multi-factor-info-not-found",MISSING_MFA_ENROLLMENT_ID:"missing-multi-factor-info",MISSING_MFA_PENDING_CREDENTIAL:"missing-multi-factor-session",SECOND_FACTOR_EXISTS:"second-factor-already-in-use",SECOND_FACTOR_LIMIT_EXCEEDED:"maximum-second-factor-count-exceeded",BLOCKING_FUNCTION_ERROR_RESPONSE:"internal-error"};/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Vf=new kt(3e4,6e4);function Tt(t,e){return t.tenantId&&!e.tenantId?Object.assign(Object.assign({},e),{tenantId:t.tenantId}):e}async function nt(t,e,n,r,s={}){return Zi(t,s,async()=>{let i={},o={};r&&(e==="GET"?o=r:i={body:JSON.stringify(r)});const a=$t(Object.assign({key:t.config.apiKey},o)).slice(1),c=await t._getAdditionalHeaders();return c["Content-Type"]="application/json",t.languageCode&&(c["X-Firebase-Locale"]=t.languageCode),Qi.fetch()(eo(t,t.config.apiHost,n,a),Object.assign({method:e,headers:c,referrerPolicy:"no-referrer"},i))})}async function Zi(t,e,n){t._canInitEmulator=!1;const r=Object.assign(Object.assign({},zf),e);try{const s=new Wf(t),i=await Promise.race([n(),s.promise]);s.clearNetworkTimeout();const o=await i.json();if("needConfirmation"in o)throw Pt(t,"account-exists-with-different-credential",o);if(i.ok&&!("errorMessage"in o))return o;{const a=i.ok?o.errorMessage:o.error.message,[c,l]=a.split(" : ");if(c==="FEDERATED_USER_ID_ALREADY_LINKED")throw Pt(t,"credential-already-in-use",o);if(c==="EMAIL_EXISTS")throw Pt(t,"email-already-in-use",o);if(c==="USER_DISABLED")throw Pt(t,"user-disabled",o);const u=r[c]||c.toLowerCase().replace(/[_\s]+/g,"-");if(l)throw Yi(t,u,l);se(t,u)}}catch(s){if(s instanceof Re)throw s;se(t,"network-request-failed")}}async function fn(t,e,n,r,s={}){const i=await nt(t,e,n,r,s);return"mfaPendingCredential"in i&&se(t,"multi-factor-auth-required",{_serverResponse:i}),i}function eo(t,e,n,r){const s=`${e}${n}?${r}`;return t.config.emulator?Sr(t.config,s):`${t.config.apiScheme}://${s}`}class Wf{constructor(e){this.auth=e,this.timer=null,this.promise=new Promise((n,r)=>{this.timer=setTimeout(()=>r(ae(this.auth,"network-request-failed")),Vf.get())})}clearNetworkTimeout(){clearTimeout(this.timer)}}function Pt(t,e,n){const r={appName:t.name};n.email&&(r.email=n.email),n.phoneNumber&&(r.phoneNumber=n.phoneNumber);const s=ae(t,e,r);return s.customData._tokenResponse=n,s}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Jf(t,e){return nt(t,"POST","/v1/accounts:delete",e)}async function qf(t,e){return nt(t,"POST","/v1/accounts:lookup",e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ht(t){if(!!t)try{const e=new Date(Number(t));if(!isNaN(e.getTime()))return e.toUTCString()}catch{}}async function Gf(t,e=!1){const n=ue(t),r=await n.getIdToken(e),s=$r(r);I(s&&s.exp&&s.auth_time&&s.iat,n.auth,"internal-error");const i=typeof s.firebase=="object"?s.firebase:void 0,o=i?.sign_in_provider;return{claims:s,token:r,authTime:ht(Fn(s.auth_time)),issuedAtTime:ht(Fn(s.iat)),expirationTime:ht(Fn(s.exp)),signInProvider:o||null,signInSecondFactor:i?.sign_in_second_factor||null}}function Fn(t){return Number(t)*1e3}function $r(t){var e;const[n,r,s]=t.split(".");if(n===void 0||r===void 0||s===void 0)return Ft("JWT malformed, contained fewer than 3 sections"),null;try{const i=Fi(r);return i?JSON.parse(i):(Ft("Failed to decode base64 JWT payload"),null)}catch(i){return Ft("Caught error parsing JWT payload as JSON",(e=i)===null||e===void 0?void 0:e.toString()),null}}function Kf(t){const e=$r(t);return I(e,"internal-error"),I(typeof e.exp<"u","internal-error"),I(typeof e.iat<"u","internal-error"),Number(e.exp)-Number(e.iat)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function yt(t,e,n=!1){if(n)return e;try{return await e}catch(r){throw r instanceof Re&&Xf(r)&&t.auth.currentUser===t&&await t.auth.signOut(),r}}function Xf({code:t}){return t==="auth/user-disabled"||t==="auth/user-token-expired"}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Yf{constructor(e){this.user=e,this.isRunning=!1,this.timerId=null,this.errorBackoff=3e4}_start(){this.isRunning||(this.isRunning=!0,this.schedule())}_stop(){!this.isRunning||(this.isRunning=!1,this.timerId!==null&&clearTimeout(this.timerId))}getInterval(e){var n;if(e){const r=this.errorBackoff;return this.errorBackoff=Math.min(this.errorBackoff*2,96e4),r}else{this.errorBackoff=3e4;const s=((n=this.user.stsTokenManager.expirationTime)!==null&&n!==void 0?n:0)-Date.now()-3e5;return Math.max(0,s)}}schedule(e=!1){if(!this.isRunning)return;const n=this.getInterval(e);this.timerId=setTimeout(async()=>{await this.iteration()},n)}async iteration(){var e;try{await this.user.getIdToken(!0)}catch(n){((e=n)===null||e===void 0?void 0:e.code)==="auth/network-request-failed"&&this.schedule(!0);return}this.schedule()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class to{constructor(e,n){this.createdAt=e,this.lastLoginAt=n,this._initializeTime()}_initializeTime(){this.lastSignInTime=ht(this.lastLoginAt),this.creationTime=ht(this.createdAt)}_copy(e){this.createdAt=e.createdAt,this.lastLoginAt=e.lastLoginAt,this._initializeTime()}toJSON(){return{createdAt:this.createdAt,lastLoginAt:this.lastLoginAt}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function en(t){var e;const n=t.auth,r=await t.getIdToken(),s=await yt(t,qf(n,{idToken:r}));I(s?.users.length,n,"internal-error");const i=s.users[0];t._notifyReloadListener(i);const o=!((e=i.providerUserInfo)===null||e===void 0)&&e.length?eh(i.providerUserInfo):[],a=Zf(t.providerData,o),c=t.isAnonymous,l=!(t.email&&i.passwordHash)&&!a?.length,u=c?l:!1,d={uid:i.localId,displayName:i.displayName||null,photoURL:i.photoUrl||null,email:i.email||null,emailVerified:i.emailVerified||!1,phoneNumber:i.phoneNumber||null,tenantId:i.tenantId||null,providerData:a,metadata:new to(i.createdAt,i.lastLoginAt),isAnonymous:u};Object.assign(t,d)}async function Qf(t){const e=ue(t);await en(e),await e.auth._persistUserIfCurrent(e),e.auth._notifyListenersIfCurrent(e)}function Zf(t,e){return[...t.filter(r=>!e.some(s=>s.providerId===r.providerId)),...e]}function eh(t){return t.map(e=>{var{providerId:n}=e,r=Er(e,["providerId"]);return{providerId:n,uid:r.rawId||"",displayName:r.displayName||null,email:r.email||null,phoneNumber:r.phoneNumber||null,photoURL:r.photoUrl||null}})}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function th(t,e){const n=await Zi(t,{},async()=>{const r=$t({grant_type:"refresh_token",refresh_token:e}).slice(1),{tokenApiHost:s,apiKey:i}=t.config,o=eo(t,s,"/v1/token",`key=${i}`),a=await t._getAdditionalHeaders();return a["Content-Type"]="application/x-www-form-urlencoded",Qi.fetch()(o,{method:"POST",headers:a,body:r})});return{accessToken:n.access_token,expiresIn:n.expires_in,refreshToken:n.refresh_token}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class _t{constructor(){this.refreshToken=null,this.accessToken=null,this.expirationTime=null}get isExpired(){return!this.expirationTime||Date.now()>this.expirationTime-3e4}updateFromServerResponse(e){I(e.idToken,"internal-error"),I(typeof e.idToken<"u","internal-error"),I(typeof e.refreshToken<"u","internal-error");const n="expiresIn"in e&&typeof e.expiresIn<"u"?Number(e.expiresIn):Kf(e.idToken);this.updateTokensAndExpiration(e.idToken,e.refreshToken,n)}async getToken(e,n=!1){return I(!this.accessToken||this.refreshToken,e,"user-token-expired"),!n&&this.accessToken&&!this.isExpired?this.accessToken:this.refreshToken?(await this.refresh(e,this.refreshToken),this.accessToken):null}clearRefreshToken(){this.refreshToken=null}async refresh(e,n){const{accessToken:r,refreshToken:s,expiresIn:i}=await th(e,n);this.updateTokensAndExpiration(r,s,Number(i))}updateTokensAndExpiration(e,n,r){this.refreshToken=n||null,this.accessToken=e||null,this.expirationTime=Date.now()+r*1e3}static fromJSON(e,n){const{refreshToken:r,accessToken:s,expirationTime:i}=n,o=new _t;return r&&(I(typeof r=="string","internal-error",{appName:e}),o.refreshToken=r),s&&(I(typeof s=="string","internal-error",{appName:e}),o.accessToken=s),i&&(I(typeof i=="number","internal-error",{appName:e}),o.expirationTime=i),o}toJSON(){return{refreshToken:this.refreshToken,accessToken:this.accessToken,expirationTime:this.expirationTime}}_assign(e){this.accessToken=e.accessToken,this.refreshToken=e.refreshToken,this.expirationTime=e.expirationTime}_clone(){return Object.assign(new _t,this.toJSON())}_performRefresh(){return he("not implemented")}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ie(t,e){I(typeof t=="string"||typeof t>"u","internal-error",{appName:e})}class Be{constructor(e){var{uid:n,auth:r,stsTokenManager:s}=e,i=Er(e,["uid","auth","stsTokenManager"]);this.providerId="firebase",this.proactiveRefresh=new Yf(this),this.reloadUserInfo=null,this.reloadListener=null,this.uid=n,this.auth=r,this.stsTokenManager=s,this.accessToken=s.accessToken,this.displayName=i.displayName||null,this.email=i.email||null,this.emailVerified=i.emailVerified||!1,this.phoneNumber=i.phoneNumber||null,this.photoURL=i.photoURL||null,this.isAnonymous=i.isAnonymous||!1,this.tenantId=i.tenantId||null,this.providerData=i.providerData?[...i.providerData]:[],this.metadata=new to(i.createdAt||void 0,i.lastLoginAt||void 0)}async getIdToken(e){const n=await yt(this,this.stsTokenManager.getToken(this.auth,e));return I(n,this.auth,"internal-error"),this.accessToken!==n&&(this.accessToken=n,await this.auth._persistUserIfCurrent(this),this.auth._notifyListenersIfCurrent(this)),n}getIdTokenResult(e){return Gf(this,e)}reload(){return Qf(this)}_assign(e){this!==e&&(I(this.uid===e.uid,this.auth,"internal-error"),this.displayName=e.displayName,this.photoURL=e.photoURL,this.email=e.email,this.emailVerified=e.emailVerified,this.phoneNumber=e.phoneNumber,this.isAnonymous=e.isAnonymous,this.tenantId=e.tenantId,this.providerData=e.providerData.map(n=>Object.assign({},n)),this.metadata._copy(e.metadata),this.stsTokenManager._assign(e.stsTokenManager))}_clone(e){return new Be(Object.assign(Object.assign({},this),{auth:e,stsTokenManager:this.stsTokenManager._clone()}))}_onReload(e){I(!this.reloadListener,this.auth,"internal-error"),this.reloadListener=e,this.reloadUserInfo&&(this._notifyReloadListener(this.reloadUserInfo),this.reloadUserInfo=null)}_notifyReloadListener(e){this.reloadListener?this.reloadListener(e):this.reloadUserInfo=e}_startProactiveRefresh(){this.proactiveRefresh._start()}_stopProactiveRefresh(){this.proactiveRefresh._stop()}async _updateTokensIfNecessary(e,n=!1){let r=!1;e.idToken&&e.idToken!==this.stsTokenManager.accessToken&&(this.stsTokenManager.updateFromServerResponse(e),r=!0),n&&await en(this),await this.auth._persistUserIfCurrent(this),r&&this.auth._notifyListenersIfCurrent(this)}async delete(){const e=await this.getIdToken();return await yt(this,Jf(this.auth,{idToken:e})),this.stsTokenManager.clearRefreshToken(),this.auth.signOut()}toJSON(){return Object.assign(Object.assign({uid:this.uid,email:this.email||void 0,emailVerified:this.emailVerified,displayName:this.displayName||void 0,isAnonymous:this.isAnonymous,photoURL:this.photoURL||void 0,phoneNumber:this.phoneNumber||void 0,tenantId:this.tenantId||void 0,providerData:this.providerData.map(e=>Object.assign({},e)),stsTokenManager:this.stsTokenManager.toJSON(),_redirectEventId:this._redirectEventId},this.metadata.toJSON()),{apiKey:this.auth.config.apiKey,appName:this.auth.name})}get refreshToken(){return this.stsTokenManager.refreshToken||""}static _fromJSON(e,n){var r,s,i,o,a,c,l,u;const d=(r=n.displayName)!==null&&r!==void 0?r:void 0,v=(s=n.email)!==null&&s!==void 0?s:void 0,m=(i=n.phoneNumber)!==null&&i!==void 0?i:void 0,g=(o=n.photoURL)!==null&&o!==void 0?o:void 0,b=(a=n.tenantId)!==null&&a!==void 0?a:void 0,w=(c=n._redirectEventId)!==null&&c!==void 0?c:void 0,x=(l=n.createdAt)!==null&&l!==void 0?l:void 0,S=(u=n.lastLoginAt)!==null&&u!==void 0?u:void 0,{uid:T,emailVerified:P,isAnonymous:U,providerData:k,stsTokenManager:W}=n;I(T&&W,e,"internal-error");const z=_t.fromJSON(this.name,W);I(typeof T=="string",e,"internal-error"),Ie(d,e.name),Ie(v,e.name),I(typeof P=="boolean",e,"internal-error"),I(typeof U=="boolean",e,"internal-error"),Ie(m,e.name),Ie(g,e.name),Ie(b,e.name),Ie(w,e.name),Ie(x,e.name),Ie(S,e.name);const C=new Be({uid:T,auth:e,email:v,emailVerified:P,displayName:d,isAnonymous:U,photoURL:g,phoneNumber:m,tenantId:b,stsTokenManager:z,createdAt:x,lastLoginAt:S});return k&&Array.isArray(k)&&(C.providerData=k.map(L=>Object.assign({},L))),w&&(C._redirectEventId=w),C}static async _fromIdTokenResponse(e,n,r=!1){const s=new _t;s.updateFromServerResponse(n);const i=new Be({uid:n.localId,auth:e,stsTokenManager:s,isAnonymous:r});return await en(i),i}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class no{constructor(){this.type="NONE",this.storage={}}async _isAvailable(){return!0}async _set(e,n){this.storage[e]=n}async _get(e){const n=this.storage[e];return n===void 0?null:n}async _remove(e){delete this.storage[e]}_addListener(e,n){}_removeListener(e,n){}}no.type="NONE";const As=no;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Bt(t,e,n){return`firebase:${t}:${e}:${n}`}class qe{constructor(e,n,r){this.persistence=e,this.auth=n,this.userKey=r;const{config:s,name:i}=this.auth;this.fullUserKey=Bt(this.userKey,s.apiKey,i),this.fullPersistenceKey=Bt("persistence",s.apiKey,i),this.boundEventHandler=n._onStorageEvent.bind(n),this.persistence._addListener(this.fullUserKey,this.boundEventHandler)}setCurrentUser(e){return this.persistence._set(this.fullUserKey,e.toJSON())}async getCurrentUser(){const e=await this.persistence._get(this.fullUserKey);return e?Be._fromJSON(this.auth,e):null}removeCurrentUser(){return this.persistence._remove(this.fullUserKey)}savePersistenceForRedirect(){return this.persistence._set(this.fullPersistenceKey,this.persistence.type)}async setPersistence(e){if(this.persistence===e)return;const n=await this.getCurrentUser();if(await this.removeCurrentUser(),this.persistence=e,n)return this.setCurrentUser(n)}delete(){this.persistence._removeListener(this.fullUserKey,this.boundEventHandler)}static async create(e,n,r="authUser"){if(!n.length)return new qe(ge(As),e,r);const s=(await Promise.all(n.map(async l=>{if(await l._isAvailable())return l}))).filter(l=>l);let i=s[0]||ge(As);const o=Bt(r,e.config.apiKey,e.name);let a=null;for(const l of n)try{const u=await l._get(o);if(u){const d=Be._fromJSON(e,u);l!==i&&(a=d),i=l;break}}catch{}const c=s.filter(l=>l._shouldAllowMigration);return!i._shouldAllowMigration||!c.length?new qe(i,e,r):(i=c[0],a&&await i._set(o,a.toJSON()),await Promise.all(n.map(async l=>{if(l!==i)try{await l._remove(o)}catch{}})),new qe(i,e,r))}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Os(t){const e=t.toLowerCase();if(e.includes("opera/")||e.includes("opr/")||e.includes("opios/"))return"Opera";if(io(e))return"IEMobile";if(e.includes("msie")||e.includes("trident/"))return"IE";if(e.includes("edge/"))return"Edge";if(ro(e))return"Firefox";if(e.includes("silk/"))return"Silk";if(ao(e))return"Blackberry";if(lo(e))return"Webos";if(kr(e))return"Safari";if((e.includes("chrome/")||so(e))&&!e.includes("edge/"))return"Chrome";if(oo(e))return"Android";{const n=/([a-zA-Z\d\.]+)\/[a-zA-Z\d\.]*$/,r=t.match(n);if(r?.length===2)return r[1]}return"Other"}function ro(t=Q()){return/firefox\//i.test(t)}function kr(t=Q()){const e=t.toLowerCase();return e.includes("safari/")&&!e.includes("chrome/")&&!e.includes("crios/")&&!e.includes("android")}function so(t=Q()){return/crios\//i.test(t)}function io(t=Q()){return/iemobile/i.test(t)}function oo(t=Q()){return/android/i.test(t)}function ao(t=Q()){return/blackberry/i.test(t)}function lo(t=Q()){return/webos/i.test(t)}function hn(t=Q()){return/iphone|ipad|ipod/i.test(t)||/macintosh/i.test(t)&&/mobile/i.test(t)}function nh(t=Q()){var e;return hn(t)&&!!(!((e=window.navigator)===null||e===void 0)&&e.standalone)}function rh(){return fd()&&document.documentMode===10}function co(t=Q()){return hn(t)||oo(t)||lo(t)||ao(t)||/windows phone/i.test(t)||io(t)}function sh(){try{return!!(window&&window!==window.top)}catch{return!1}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function uo(t,e=[]){let n;switch(t){case"Browser":n=Os(Q());break;case"Worker":n=`${Os(Q())}-${t}`;break;default:n=t}const r=e.length?e.join(","):"FirebaseCore-web";return`${n}/JsCore/${dn}/${r}`}/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ih{constructor(e){this.auth=e,this.queue=[]}pushCallback(e,n){const r=i=>new Promise((o,a)=>{try{const c=e(i);o(c)}catch(c){a(c)}});r.onAbort=n,this.queue.push(r);const s=this.queue.length-1;return()=>{this.queue[s]=()=>Promise.resolve()}}async runMiddleware(e){var n;if(this.auth.currentUser===e)return;const r=[];try{for(const s of this.queue)await s(e),s.onAbort&&r.push(s.onAbort)}catch(s){r.reverse();for(const i of r)try{i()}catch{}throw this.auth._errorFactory.create("login-blocked",{originalMessage:(n=s)===null||n===void 0?void 0:n.message})}}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class oh{constructor(e,n,r){this.app=e,this.heartbeatServiceProvider=n,this.config=r,this.currentUser=null,this.emulatorConfig=null,this.operations=Promise.resolve(),this.authStateSubscription=new Ns(this),this.idTokenSubscription=new Ns(this),this.beforeStateQueue=new ih(this),this.redirectUser=null,this.isProactiveRefreshEnabled=!1,this._canInitEmulator=!0,this._isInitialized=!1,this._deleted=!1,this._initializationPromise=null,this._popupRedirectResolver=null,this._errorFactory=Xi,this.lastNotifiedUid=void 0,this.languageCode=null,this.tenantId=null,this.settings={appVerificationDisabledForTesting:!1},this.frameworks=[],this.name=e.name,this.clientVersion=r.sdkClientVersion}_initializeWithPersistence(e,n){return n&&(this._popupRedirectResolver=ge(n)),this._initializationPromise=this.queue(async()=>{var r,s;if(!this._deleted&&(this.persistenceManager=await qe.create(this,e),!this._deleted)){if(!((r=this._popupRedirectResolver)===null||r===void 0)&&r._shouldInitProactively)try{await this._popupRedirectResolver._initialize(this)}catch{}await this.initializeCurrentUser(n),this.lastNotifiedUid=((s=this.currentUser)===null||s===void 0?void 0:s.uid)||null,!this._deleted&&(this._isInitialized=!0)}}),this._initializationPromise}async _onStorageEvent(){if(this._deleted)return;const e=await this.assertedPersistence.getCurrentUser();if(!(!this.currentUser&&!e)){if(this.currentUser&&e&&this.currentUser.uid===e.uid){this._currentUser._assign(e),await this.currentUser.getIdToken();return}await this._updateCurrentUser(e,!0)}}async initializeCurrentUser(e){var n;const r=await this.assertedPersistence.getCurrentUser();let s=r,i=!1;if(e&&this.config.authDomain){await this.getOrInitRedirectPersistenceManager();const o=(n=this.redirectUser)===null||n===void 0?void 0:n._redirectEventId,a=s?._redirectEventId,c=await this.tryRedirectSignIn(e);(!o||o===a)&&c?.user&&(s=c.user,i=!0)}if(!s)return this.directlySetCurrentUser(null);if(!s._redirectEventId){if(i)try{await this.beforeStateQueue.runMiddleware(s)}catch(o){s=r,this._popupRedirectResolver._overrideRedirectResult(this,()=>Promise.reject(o))}return s?this.reloadAndSetCurrentUserOrClear(s):this.directlySetCurrentUser(null)}return I(this._popupRedirectResolver,this,"argument-error"),await this.getOrInitRedirectPersistenceManager(),this.redirectUser&&this.redirectUser._redirectEventId===s._redirectEventId?this.directlySetCurrentUser(s):this.reloadAndSetCurrentUserOrClear(s)}async tryRedirectSignIn(e){let n=null;try{n=await this._popupRedirectResolver._completeRedirectFn(this,e,!0)}catch{await this._setRedirectUser(null)}return n}async reloadAndSetCurrentUserOrClear(e){var n;try{await en(e)}catch(r){if(((n=r)===null||n===void 0?void 0:n.code)!=="auth/network-request-failed")return this.directlySetCurrentUser(null)}return this.directlySetCurrentUser(e)}useDeviceLanguage(){this.languageCode=Hf()}async _delete(){this._deleted=!0}async updateCurrentUser(e){const n=e?ue(e):null;return n&&I(n.auth.config.apiKey===this.config.apiKey,this,"invalid-user-token"),this._updateCurrentUser(n&&n._clone(this))}async _updateCurrentUser(e,n=!1){if(!this._deleted)return e&&I(this.tenantId===e.tenantId,this,"tenant-id-mismatch"),n||await this.beforeStateQueue.runMiddleware(e),this.queue(async()=>{await this.directlySetCurrentUser(e),this.notifyAuthListeners()})}async signOut(){return await this.beforeStateQueue.runMiddleware(null),(this.redirectPersistenceManager||this._popupRedirectResolver)&&await this._setRedirectUser(null),this._updateCurrentUser(null,!0)}setPersistence(e){return this.queue(async()=>{await this.assertedPersistence.setPersistence(ge(e))})}_getPersistence(){return this.assertedPersistence.persistence.type}_updateErrorMap(e){this._errorFactory=new St("auth","Firebase",e())}onAuthStateChanged(e,n,r){return this.registerStateListener(this.authStateSubscription,e,n,r)}beforeAuthStateChanged(e,n){return this.beforeStateQueue.pushCallback(e,n)}onIdTokenChanged(e,n,r){return this.registerStateListener(this.idTokenSubscription,e,n,r)}toJSON(){var e;return{apiKey:this.config.apiKey,authDomain:this.config.authDomain,appName:this.name,currentUser:(e=this._currentUser)===null||e===void 0?void 0:e.toJSON()}}async _setRedirectUser(e,n){const r=await this.getOrInitRedirectPersistenceManager(n);return e===null?r.removeCurrentUser():r.setCurrentUser(e)}async getOrInitRedirectPersistenceManager(e){if(!this.redirectPersistenceManager){const n=e&&ge(e)||this._popupRedirectResolver;I(n,this,"argument-error"),this.redirectPersistenceManager=await qe.create(this,[ge(n._redirectPersistence)],"redirectUser"),this.redirectUser=await this.redirectPersistenceManager.getCurrentUser()}return this.redirectPersistenceManager}async _redirectUserForId(e){var n,r;return this._isInitialized&&await this.queue(async()=>{}),((n=this._currentUser)===null||n===void 0?void 0:n._redirectEventId)===e?this._currentUser:((r=this.redirectUser)===null||r===void 0?void 0:r._redirectEventId)===e?this.redirectUser:null}async _persistUserIfCurrent(e){if(e===this.currentUser)return this.queue(async()=>this.directlySetCurrentUser(e))}_notifyListenersIfCurrent(e){e===this.currentUser&&this.notifyAuthListeners()}_key(){return`${this.config.authDomain}:${this.config.apiKey}:${this.name}`}_startProactiveRefresh(){this.isProactiveRefreshEnabled=!0,this.currentUser&&this._currentUser._startProactiveRefresh()}_stopProactiveRefresh(){this.isProactiveRefreshEnabled=!1,this.currentUser&&this._currentUser._stopProactiveRefresh()}get _currentUser(){return this.currentUser}notifyAuthListeners(){var e,n;if(!this._isInitialized)return;this.idTokenSubscription.next(this.currentUser);const r=(n=(e=this.currentUser)===null||e===void 0?void 0:e.uid)!==null&&n!==void 0?n:null;this.lastNotifiedUid!==r&&(this.lastNotifiedUid=r,this.authStateSubscription.next(this.currentUser))}registerStateListener(e,n,r,s){if(this._deleted)return()=>{};const i=typeof n=="function"?n:n.next.bind(n),o=this._isInitialized?Promise.resolve():this._initializationPromise;return I(o,this,"internal-error"),o.then(()=>i(this.currentUser)),typeof n=="function"?e.addObserver(n,r,s):e.addObserver(n)}async directlySetCurrentUser(e){this.currentUser&&this.currentUser!==e&&this._currentUser._stopProactiveRefresh(),e&&this.isProactiveRefreshEnabled&&e._startProactiveRefresh(),this.currentUser=e,e?await this.assertedPersistence.setCurrentUser(e):await this.assertedPersistence.removeCurrentUser()}queue(e){return this.operations=this.operations.then(e,e),this.operations}get assertedPersistence(){return I(this.persistenceManager,this,"internal-error"),this.persistenceManager}_logFramework(e){!e||this.frameworks.includes(e)||(this.frameworks.push(e),this.frameworks.sort(),this.clientVersion=uo(this.config.clientPlatform,this._getFrameworks()))}_getFrameworks(){return this.frameworks}async _getAdditionalHeaders(){var e;const n={["X-Client-Version"]:this.clientVersion};this.app.options.appId&&(n["X-Firebase-gmpid"]=this.app.options.appId);const r=await((e=this.heartbeatServiceProvider.getImmediate({optional:!0}))===null||e===void 0?void 0:e.getHeartbeatsHeader());return r&&(n["X-Firebase-Client"]=r),n}}function Ct(t){return ue(t)}class Ns{constructor(e){this.auth=e,this.observer=null,this.addObserver=$d(n=>this.observer=n)}get next(){return I(this.observer,this.auth,"internal-error"),this.observer.next.bind(this.observer)}}function ah(t,e,n){const r=Ct(t);I(r._canInitEmulator,r,"emulator-config-failed"),I(/^https?:\/\//.test(e),r,"invalid-emulator-scheme");const s=!!n?.disableWarnings,i=fo(e),{host:o,port:a}=lh(e),c=a===null?"":`:${a}`;r.config.emulator={url:`${i}//${o}${c}/`},r.settings.appVerificationDisabledForTesting=!0,r.emulatorConfig=Object.freeze({host:o,port:a,protocol:i.replace(":",""),options:Object.freeze({disableWarnings:s})}),s||ch()}function fo(t){const e=t.indexOf(":");return e<0?"":t.substr(0,e+1)}function lh(t){const e=fo(t),n=/(\/\/)?([^?#/]+)/.exec(t.substr(e.length));if(!n)return{host:"",port:null};const r=n[2].split("@").pop()||"",s=/^(\[[^\]]+\])(:|$)/.exec(r);if(s){const i=s[1];return{host:i,port:Rs(r.substr(i.length+1))}}else{const[i,o]=r.split(":");return{host:i,port:Rs(o)}}}function Rs(t){if(!t)return null;const e=Number(t);return isNaN(e)?null:e}function ch(){function t(){const e=document.createElement("p"),n=e.style;e.innerText="Running in emulator mode. Do not use with production credentials.",n.position="fixed",n.width="100%",n.backgroundColor="#ffffff",n.border=".1em solid #000000",n.color="#b50000",n.bottom="0px",n.left="0px",n.margin="0px",n.zIndex="10000",n.textAlign="center",e.classList.add("firebase-emulator-warning"),document.body.appendChild(e)}typeof console<"u"&&typeof console.info=="function"&&console.info("WARNING: You are using the Auth Emulator, which is intended for local testing only.  Do not use with production credentials."),typeof window<"u"&&typeof document<"u"&&(document.readyState==="loading"?window.addEventListener("DOMContentLoaded",t):t())}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Tr{constructor(e,n){this.providerId=e,this.signInMethod=n}toJSON(){return he("not implemented")}_getIdTokenResponse(e){return he("not implemented")}_linkToIdToken(e,n){return he("not implemented")}_getReauthenticationResolver(e){return he("not implemented")}}async function uh(t,e){return nt(t,"POST","/v1/accounts:update",e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function dh(t,e){return fn(t,"POST","/v1/accounts:signInWithPassword",Tt(t,e))}async function fh(t,e){return nt(t,"POST","/v1/accounts:sendOobCode",Tt(t,e))}async function hh(t,e){return fh(t,e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function gh(t,e){return fn(t,"POST","/v1/accounts:signInWithEmailLink",Tt(t,e))}async function mh(t,e){return fn(t,"POST","/v1/accounts:signInWithEmailLink",Tt(t,e))}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class wt extends Tr{constructor(e,n,r,s=null){super("password",r),this._email=e,this._password=n,this._tenantId=s}static _fromEmailAndPassword(e,n){return new wt(e,n,"password")}static _fromEmailAndCode(e,n,r=null){return new wt(e,n,"emailLink",r)}toJSON(){return{email:this._email,password:this._password,signInMethod:this.signInMethod,tenantId:this._tenantId}}static fromJSON(e){const n=typeof e=="string"?JSON.parse(e):e;if(n?.email&&n?.password){if(n.signInMethod==="password")return this._fromEmailAndPassword(n.email,n.password);if(n.signInMethod==="emailLink")return this._fromEmailAndCode(n.email,n.password,n.tenantId)}return null}async _getIdTokenResponse(e){switch(this.signInMethod){case"password":return dh(e,{returnSecureToken:!0,email:this._email,password:this._password});case"emailLink":return gh(e,{email:this._email,oobCode:this._password});default:se(e,"internal-error")}}async _linkToIdToken(e,n){switch(this.signInMethod){case"password":return uh(e,{idToken:n,returnSecureToken:!0,email:this._email,password:this._password});case"emailLink":return mh(e,{idToken:n,email:this._email,oobCode:this._password});default:se(e,"internal-error")}}_getReauthenticationResolver(e){return this._getIdTokenResponse(e)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Ge(t,e){return fn(t,"POST","/v1/accounts:signInWithIdp",Tt(t,e))}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ph="http://localhost";class ze extends Tr{constructor(){super(...arguments),this.pendingToken=null}static _fromParams(e){const n=new ze(e.providerId,e.signInMethod);return e.idToken||e.accessToken?(e.idToken&&(n.idToken=e.idToken),e.accessToken&&(n.accessToken=e.accessToken),e.nonce&&!e.pendingToken&&(n.nonce=e.nonce),e.pendingToken&&(n.pendingToken=e.pendingToken)):e.oauthToken&&e.oauthTokenSecret?(n.accessToken=e.oauthToken,n.secret=e.oauthTokenSecret):se("argument-error"),n}toJSON(){return{idToken:this.idToken,accessToken:this.accessToken,secret:this.secret,nonce:this.nonce,pendingToken:this.pendingToken,providerId:this.providerId,signInMethod:this.signInMethod}}static fromJSON(e){const n=typeof e=="string"?JSON.parse(e):e,{providerId:r,signInMethod:s}=n,i=Er(n,["providerId","signInMethod"]);if(!r||!s)return null;const o=new ze(r,s);return o.idToken=i.idToken||void 0,o.accessToken=i.accessToken||void 0,o.secret=i.secret,o.nonce=i.nonce,o.pendingToken=i.pendingToken||null,o}_getIdTokenResponse(e){const n=this.buildRequest();return Ge(e,n)}_linkToIdToken(e,n){const r=this.buildRequest();return r.idToken=n,Ge(e,r)}_getReauthenticationResolver(e){const n=this.buildRequest();return n.autoCreate=!1,Ge(e,n)}buildRequest(){const e={requestUri:ph,returnSecureToken:!0};if(this.pendingToken)e.pendingToken=this.pendingToken;else{const n={};this.idToken&&(n.id_token=this.idToken),this.accessToken&&(n.access_token=this.accessToken),this.secret&&(n.oauth_token_secret=this.secret),n.providerId=this.providerId,this.nonce&&!this.pendingToken&&(n.nonce=this.nonce),e.postBody=$t(n)}return e}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function bh(t){switch(t){case"recoverEmail":return"RECOVER_EMAIL";case"resetPassword":return"PASSWORD_RESET";case"signIn":return"EMAIL_SIGNIN";case"verifyEmail":return"VERIFY_EMAIL";case"verifyAndChangeEmail":return"VERIFY_AND_CHANGE_EMAIL";case"revertSecondFactorAddition":return"REVERT_SECOND_FACTOR_ADDITION";default:return null}}function vh(t){const e=dt(ft(t)).link,n=e?dt(ft(e)).deep_link_id:null,r=dt(ft(t)).deep_link_id;return(r?dt(ft(r)).link:null)||r||n||e||t}class Cr{constructor(e){var n,r,s,i,o,a;const c=dt(ft(e)),l=(n=c.apiKey)!==null&&n!==void 0?n:null,u=(r=c.oobCode)!==null&&r!==void 0?r:null,d=bh((s=c.mode)!==null&&s!==void 0?s:null);I(l&&u&&d,"argument-error"),this.apiKey=l,this.operation=d,this.code=u,this.continueUrl=(i=c.continueUrl)!==null&&i!==void 0?i:null,this.languageCode=(o=c.languageCode)!==null&&o!==void 0?o:null,this.tenantId=(a=c.tenantId)!==null&&a!==void 0?a:null}static parseLink(e){const n=vh(e);try{return new Cr(n)}catch{return null}}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class rt{constructor(){this.providerId=rt.PROVIDER_ID}static credential(e,n){return wt._fromEmailAndPassword(e,n)}static credentialWithLink(e,n){const r=Cr.parseLink(n);return I(r,"argument-error"),wt._fromEmailAndCode(e,r.code,r.tenantId)}}rt.PROVIDER_ID="password";rt.EMAIL_PASSWORD_SIGN_IN_METHOD="password";rt.EMAIL_LINK_SIGN_IN_METHOD="emailLink";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Ar{constructor(e){this.providerId=e,this.defaultLanguageCode=null,this.customParameters={}}setDefaultLanguage(e){this.defaultLanguageCode=e}setCustomParameters(e){return this.customParameters=e,this}getCustomParameters(){return this.customParameters}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class At extends Ar{constructor(){super(...arguments),this.scopes=[]}addScope(e){return this.scopes.includes(e)||this.scopes.push(e),this}getScopes(){return[...this.scopes]}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Se extends At{constructor(){super("facebook.com")}static credential(e){return ze._fromParams({providerId:Se.PROVIDER_ID,signInMethod:Se.FACEBOOK_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return Se.credentialFromTaggedObject(e)}static credentialFromError(e){return Se.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return Se.credential(e.oauthAccessToken)}catch{return null}}}Se.FACEBOOK_SIGN_IN_METHOD="facebook.com";Se.PROVIDER_ID="facebook.com";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class de extends At{constructor(){super("google.com"),this.addScope("profile")}static credential(e,n){return ze._fromParams({providerId:de.PROVIDER_ID,signInMethod:de.GOOGLE_SIGN_IN_METHOD,idToken:e,accessToken:n})}static credentialFromResult(e){return de.credentialFromTaggedObject(e)}static credentialFromError(e){return de.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthIdToken:n,oauthAccessToken:r}=e;if(!n&&!r)return null;try{return de.credential(n,r)}catch{return null}}}de.GOOGLE_SIGN_IN_METHOD="google.com";de.PROVIDER_ID="google.com";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class fe extends At{constructor(){super("github.com")}static credential(e){return ze._fromParams({providerId:fe.PROVIDER_ID,signInMethod:fe.GITHUB_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return fe.credentialFromTaggedObject(e)}static credentialFromError(e){return fe.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return fe.credential(e.oauthAccessToken)}catch{return null}}}fe.GITHUB_SIGN_IN_METHOD="github.com";fe.PROVIDER_ID="github.com";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class $e extends At{constructor(){super("twitter.com")}static credential(e,n){return ze._fromParams({providerId:$e.PROVIDER_ID,signInMethod:$e.TWITTER_SIGN_IN_METHOD,oauthToken:e,oauthTokenSecret:n})}static credentialFromResult(e){return $e.credentialFromTaggedObject(e)}static credentialFromError(e){return $e.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthAccessToken:n,oauthTokenSecret:r}=e;if(!n||!r)return null;try{return $e.credential(n,r)}catch{return null}}}$e.TWITTER_SIGN_IN_METHOD="twitter.com";$e.PROVIDER_ID="twitter.com";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Ye{constructor(e){this.user=e.user,this.providerId=e.providerId,this._tokenResponse=e._tokenResponse,this.operationType=e.operationType}static async _fromIdTokenResponse(e,n,r,s=!1){const i=await Be._fromIdTokenResponse(e,r,s),o=Ds(r);return new Ye({user:i,providerId:o,_tokenResponse:r,operationType:n})}static async _forOperation(e,n,r){await e._updateTokensIfNecessary(r,!0);const s=Ds(r);return new Ye({user:e,providerId:s,_tokenResponse:r,operationType:n})}}function Ds(t){return t.providerId?t.providerId:"phoneNumber"in t?"phone":null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class tn extends Re{constructor(e,n,r,s){var i;super(n.code,n.message),this.operationType=r,this.user=s,Object.setPrototypeOf(this,tn.prototype),this.customData={appName:e.name,tenantId:(i=e.tenantId)!==null&&i!==void 0?i:void 0,_serverResponse:n.customData._serverResponse,operationType:r}}static _fromErrorAndOperation(e,n,r,s){return new tn(e,n,r,s)}}function ho(t,e,n,r){return(e==="reauthenticate"?n._getReauthenticationResolver(t):n._getIdTokenResponse(t)).catch(i=>{throw i.code==="auth/multi-factor-auth-required"?tn._fromErrorAndOperation(t,i,e,r):i})}async function yh(t,e,n=!1){const r=await yt(t,e._linkToIdToken(t.auth,await t.getIdToken()),n);return Ye._forOperation(t,"link",r)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function _h(t,e,n=!1){var r;const{auth:s}=t,i="reauthenticate";try{const o=await yt(t,ho(s,i,e,t),n);I(o.idToken,s,"internal-error");const a=$r(o.idToken);I(a,s,"internal-error");const{sub:c}=a;return I(t.uid===c,s,"user-mismatch"),Ye._forOperation(t,i,o)}catch(o){throw((r=o)===null||r===void 0?void 0:r.code)==="auth/user-not-found"&&se(s,"user-mismatch"),o}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function go(t,e,n=!1){const r="signIn",s=await ho(t,r,e),i=await Ye._fromIdTokenResponse(t,r,s);return n||await t._updateCurrentUser(i.user),i}async function wh(t,e){return go(Ct(t),e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function xh(t,e,n){var r;I(((r=n.url)===null||r===void 0?void 0:r.length)>0,t,"invalid-continue-uri"),I(typeof n.dynamicLinkDomain>"u"||n.dynamicLinkDomain.length>0,t,"invalid-dynamic-link-domain"),e.continueUrl=n.url,e.dynamicLinkDomain=n.dynamicLinkDomain,e.canHandleCodeInApp=n.handleCodeInApp,n.iOS&&(I(n.iOS.bundleId.length>0,t,"missing-ios-bundle-id"),e.iOSBundleId=n.iOS.bundleId),n.android&&(I(n.android.packageName.length>0,t,"missing-android-pkg-name"),e.androidInstallApp=n.android.installApp,e.androidMinimumVersionCode=n.android.minimumVersion,e.androidPackageName=n.android.packageName)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Eh(t,e,n){const r=ue(t),s={requestType:"PASSWORD_RESET",email:e};n&&xh(r,s,n),await hh(r,s)}function Ih(t,e,n){return wh(ue(t),rt.credential(e,n))}function Sh(t,e,n,r){return ue(t).onIdTokenChanged(e,n,r)}function $h(t,e,n){return ue(t).beforeAuthStateChanged(e,n)}function kh(t,e,n,r){return ue(t).onAuthStateChanged(e,n,r)}function Th(t){return ue(t).signOut()}const nn="__sak";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class mo{constructor(e,n){this.storageRetriever=e,this.type=n}_isAvailable(){try{return this.storage?(this.storage.setItem(nn,"1"),this.storage.removeItem(nn),Promise.resolve(!0)):Promise.resolve(!1)}catch{return Promise.resolve(!1)}}_set(e,n){return this.storage.setItem(e,JSON.stringify(n)),Promise.resolve()}_get(e){const n=this.storage.getItem(e);return Promise.resolve(n?JSON.parse(n):null)}_remove(e){return this.storage.removeItem(e),Promise.resolve()}get storage(){return this.storageRetriever()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ch(){const t=Q();return kr(t)||hn(t)}const Ah=1e3,Oh=10;class po extends mo{constructor(){super(()=>window.localStorage,"LOCAL"),this.boundEventHandler=(e,n)=>this.onStorageEvent(e,n),this.listeners={},this.localCache={},this.pollTimer=null,this.safariLocalStorageNotSynced=Ch()&&sh(),this.fallbackToPolling=co(),this._shouldAllowMigration=!0}forAllChangedKeys(e){for(const n of Object.keys(this.listeners)){const r=this.storage.getItem(n),s=this.localCache[n];r!==s&&e(n,s,r)}}onStorageEvent(e,n=!1){if(!e.key){this.forAllChangedKeys((o,a,c)=>{this.notifyListeners(o,c)});return}const r=e.key;if(n?this.detachListener():this.stopPolling(),this.safariLocalStorageNotSynced){const o=this.storage.getItem(r);if(e.newValue!==o)e.newValue!==null?this.storage.setItem(r,e.newValue):this.storage.removeItem(r);else if(this.localCache[r]===e.newValue&&!n)return}const s=()=>{const o=this.storage.getItem(r);!n&&this.localCache[r]===o||this.notifyListeners(r,o)},i=this.storage.getItem(r);rh()&&i!==e.newValue&&e.newValue!==e.oldValue?setTimeout(s,Oh):s()}notifyListeners(e,n){this.localCache[e]=n;const r=this.listeners[e];if(r)for(const s of Array.from(r))s(n&&JSON.parse(n))}startPolling(){this.stopPolling(),this.pollTimer=setInterval(()=>{this.forAllChangedKeys((e,n,r)=>{this.onStorageEvent(new StorageEvent("storage",{key:e,oldValue:n,newValue:r}),!0)})},Ah)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}attachListener(){window.addEventListener("storage",this.boundEventHandler)}detachListener(){window.removeEventListener("storage",this.boundEventHandler)}_addListener(e,n){Object.keys(this.listeners).length===0&&(this.fallbackToPolling?this.startPolling():this.attachListener()),this.listeners[e]||(this.listeners[e]=new Set,this.localCache[e]=this.storage.getItem(e)),this.listeners[e].add(n)}_removeListener(e,n){this.listeners[e]&&(this.listeners[e].delete(n),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&(this.detachListener(),this.stopPolling())}async _set(e,n){await super._set(e,n),this.localCache[e]=JSON.stringify(n)}async _get(e){const n=await super._get(e);return this.localCache[e]=JSON.stringify(n),n}async _remove(e){await super._remove(e),delete this.localCache[e]}}po.type="LOCAL";const Nh=po;/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class bo extends mo{constructor(){super(()=>window.sessionStorage,"SESSION")}_addListener(e,n){}_removeListener(e,n){}}bo.type="SESSION";const vo=bo;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Rh(t){return Promise.all(t.map(async e=>{try{return{fulfilled:!0,value:await e}}catch(n){return{fulfilled:!1,reason:n}}}))}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class gn{constructor(e){this.eventTarget=e,this.handlersMap={},this.boundEventHandler=this.handleEvent.bind(this)}static _getInstance(e){const n=this.receivers.find(s=>s.isListeningto(e));if(n)return n;const r=new gn(e);return this.receivers.push(r),r}isListeningto(e){return this.eventTarget===e}async handleEvent(e){const n=e,{eventId:r,eventType:s,data:i}=n.data,o=this.handlersMap[s];if(!o?.size)return;n.ports[0].postMessage({status:"ack",eventId:r,eventType:s});const a=Array.from(o).map(async l=>l(n.origin,i)),c=await Rh(a);n.ports[0].postMessage({status:"done",eventId:r,eventType:s,response:c})}_subscribe(e,n){Object.keys(this.handlersMap).length===0&&this.eventTarget.addEventListener("message",this.boundEventHandler),this.handlersMap[e]||(this.handlersMap[e]=new Set),this.handlersMap[e].add(n)}_unsubscribe(e,n){this.handlersMap[e]&&n&&this.handlersMap[e].delete(n),(!n||this.handlersMap[e].size===0)&&delete this.handlersMap[e],Object.keys(this.handlersMap).length===0&&this.eventTarget.removeEventListener("message",this.boundEventHandler)}}gn.receivers=[];/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Or(t="",e=10){let n="";for(let r=0;r<e;r++)n+=Math.floor(Math.random()*10);return t+n}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Dh{constructor(e){this.target=e,this.handlers=new Set}removeMessageHandler(e){e.messageChannel&&(e.messageChannel.port1.removeEventListener("message",e.onMessage),e.messageChannel.port1.close()),this.handlers.delete(e)}async _send(e,n,r=50){const s=typeof MessageChannel<"u"?new MessageChannel:null;if(!s)throw new Error("connection_unavailable");let i,o;return new Promise((a,c)=>{const l=Or("",20);s.port1.start();const u=setTimeout(()=>{c(new Error("unsupported_event"))},r);o={messageChannel:s,onMessage(d){const v=d;if(v.data.eventId===l)switch(v.data.status){case"ack":clearTimeout(u),i=setTimeout(()=>{c(new Error("timeout"))},3e3);break;case"done":clearTimeout(i),a(v.data.response);break;default:clearTimeout(u),clearTimeout(i),c(new Error("invalid_response"));break}}},this.handlers.add(o),s.port1.addEventListener("message",o.onMessage),this.target.postMessage({eventType:e,eventId:l,data:n},[s.port2])}).finally(()=>{o&&this.removeMessageHandler(o)})}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function le(){return window}function Ph(t){le().location.href=t}/**
 * @license
 * Copyright 2020 Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function yo(){return typeof le().WorkerGlobalScope<"u"&&typeof le().importScripts=="function"}async function Lh(){if(!navigator?.serviceWorker)return null;try{return(await navigator.serviceWorker.ready).active}catch{return null}}function Mh(){var t;return((t=navigator?.serviceWorker)===null||t===void 0?void 0:t.controller)||null}function Uh(){return yo()?self:null}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const _o="firebaseLocalStorageDb",jh=1,rn="firebaseLocalStorage",wo="fbase_key";class Ot{constructor(e){this.request=e}toPromise(){return new Promise((e,n)=>{this.request.addEventListener("success",()=>{e(this.request.result)}),this.request.addEventListener("error",()=>{n(this.request.error)})})}}function mn(t,e){return t.transaction([rn],e?"readwrite":"readonly").objectStore(rn)}function Fh(){const t=indexedDB.deleteDatabase(_o);return new Ot(t).toPromise()}function cr(){const t=indexedDB.open(_o,jh);return new Promise((e,n)=>{t.addEventListener("error",()=>{n(t.error)}),t.addEventListener("upgradeneeded",()=>{const r=t.result;try{r.createObjectStore(rn,{keyPath:wo})}catch(s){n(s)}}),t.addEventListener("success",async()=>{const r=t.result;r.objectStoreNames.contains(rn)?e(r):(r.close(),await Fh(),e(await cr()))})})}async function Ps(t,e,n){const r=mn(t,!0).put({[wo]:e,value:n});return new Ot(r).toPromise()}async function Bh(t,e){const n=mn(t,!1).get(e),r=await new Ot(n).toPromise();return r===void 0?null:r.value}function Ls(t,e){const n=mn(t,!0).delete(e);return new Ot(n).toPromise()}const Hh=800,zh=3;class xo{constructor(){this.type="LOCAL",this._shouldAllowMigration=!0,this.listeners={},this.localCache={},this.pollTimer=null,this.pendingWrites=0,this.receiver=null,this.sender=null,this.serviceWorkerReceiverAvailable=!1,this.activeServiceWorker=null,this._workerInitializationPromise=this.initializeServiceWorkerMessaging().then(()=>{},()=>{})}async _openDb(){return this.db?this.db:(this.db=await cr(),this.db)}async _withRetries(e){let n=0;for(;;)try{const r=await this._openDb();return await e(r)}catch(r){if(n++>zh)throw r;this.db&&(this.db.close(),this.db=void 0)}}async initializeServiceWorkerMessaging(){return yo()?this.initializeReceiver():this.initializeSender()}async initializeReceiver(){this.receiver=gn._getInstance(Uh()),this.receiver._subscribe("keyChanged",async(e,n)=>({keyProcessed:(await this._poll()).includes(n.key)})),this.receiver._subscribe("ping",async(e,n)=>["keyChanged"])}async initializeSender(){var e,n;if(this.activeServiceWorker=await Lh(),!this.activeServiceWorker)return;this.sender=new Dh(this.activeServiceWorker);const r=await this.sender._send("ping",{},800);!r||((e=r[0])===null||e===void 0?void 0:e.fulfilled)&&((n=r[0])===null||n===void 0?void 0:n.value.includes("keyChanged"))&&(this.serviceWorkerReceiverAvailable=!0)}async notifyServiceWorker(e){if(!(!this.sender||!this.activeServiceWorker||Mh()!==this.activeServiceWorker))try{await this.sender._send("keyChanged",{key:e},this.serviceWorkerReceiverAvailable?800:50)}catch{}}async _isAvailable(){try{if(!indexedDB)return!1;const e=await cr();return await Ps(e,nn,"1"),await Ls(e,nn),!0}catch{}return!1}async _withPendingWrite(e){this.pendingWrites++;try{await e()}finally{this.pendingWrites--}}async _set(e,n){return this._withPendingWrite(async()=>(await this._withRetries(r=>Ps(r,e,n)),this.localCache[e]=n,this.notifyServiceWorker(e)))}async _get(e){const n=await this._withRetries(r=>Bh(r,e));return this.localCache[e]=n,n}async _remove(e){return this._withPendingWrite(async()=>(await this._withRetries(n=>Ls(n,e)),delete this.localCache[e],this.notifyServiceWorker(e)))}async _poll(){const e=await this._withRetries(s=>{const i=mn(s,!1).getAll();return new Ot(i).toPromise()});if(!e)return[];if(this.pendingWrites!==0)return[];const n=[],r=new Set;for(const{fbase_key:s,value:i}of e)r.add(s),JSON.stringify(this.localCache[s])!==JSON.stringify(i)&&(this.notifyListeners(s,i),n.push(s));for(const s of Object.keys(this.localCache))this.localCache[s]&&!r.has(s)&&(this.notifyListeners(s,null),n.push(s));return n}notifyListeners(e,n){this.localCache[e]=n;const r=this.listeners[e];if(r)for(const s of Array.from(r))s(n)}startPolling(){this.stopPolling(),this.pollTimer=setInterval(async()=>this._poll(),Hh)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}_addListener(e,n){Object.keys(this.listeners).length===0&&this.startPolling(),this.listeners[e]||(this.listeners[e]=new Set,this._get(e)),this.listeners[e].add(n)}_removeListener(e,n){this.listeners[e]&&(this.listeners[e].delete(n),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&this.stopPolling()}}xo.type="LOCAL";const Vh=xo;/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Wh(){var t,e;return(e=(t=document.getElementsByTagName("head"))===null||t===void 0?void 0:t[0])!==null&&e!==void 0?e:document}function Jh(t){return new Promise((e,n)=>{const r=document.createElement("script");r.setAttribute("src",t),r.onload=e,r.onerror=s=>{const i=ae("internal-error");i.customData=s,n(i)},r.type="text/javascript",r.charset="UTF-8",Wh().appendChild(r)})}function qh(t){return`__${t}${Math.floor(Math.random()*1e6)}`}new kt(3e4,6e4);/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Eo(t,e){return e?ge(e):(I(t._popupRedirectResolver,t,"argument-error"),t._popupRedirectResolver)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Nr extends Tr{constructor(e){super("custom","custom"),this.params=e}_getIdTokenResponse(e){return Ge(e,this._buildIdpRequest())}_linkToIdToken(e,n){return Ge(e,this._buildIdpRequest(n))}_getReauthenticationResolver(e){return Ge(e,this._buildIdpRequest())}_buildIdpRequest(e){const n={requestUri:this.params.requestUri,sessionId:this.params.sessionId,postBody:this.params.postBody,tenantId:this.params.tenantId,pendingToken:this.params.pendingToken,returnSecureToken:!0,returnIdpCredential:!0};return e&&(n.idToken=e),n}}function Gh(t){return go(t.auth,new Nr(t),t.bypassAuthState)}function Kh(t){const{auth:e,user:n}=t;return I(n,e,"internal-error"),_h(n,new Nr(t),t.bypassAuthState)}async function Xh(t){const{auth:e,user:n}=t;return I(n,e,"internal-error"),yh(n,new Nr(t),t.bypassAuthState)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Io{constructor(e,n,r,s,i=!1){this.auth=e,this.resolver=r,this.user=s,this.bypassAuthState=i,this.pendingPromise=null,this.eventManager=null,this.filter=Array.isArray(n)?n:[n]}execute(){return new Promise(async(e,n)=>{this.pendingPromise={resolve:e,reject:n};try{this.eventManager=await this.resolver._initialize(this.auth),await this.onExecution(),this.eventManager.registerConsumer(this)}catch(r){this.reject(r)}})}async onAuthEvent(e){const{urlResponse:n,sessionId:r,postBody:s,tenantId:i,error:o,type:a}=e;if(o){this.reject(o);return}const c={auth:this.auth,requestUri:n,sessionId:r,tenantId:i||void 0,postBody:s||void 0,user:this.user,bypassAuthState:this.bypassAuthState};try{this.resolve(await this.getIdpTask(a)(c))}catch(l){this.reject(l)}}onError(e){this.reject(e)}getIdpTask(e){switch(e){case"signInViaPopup":case"signInViaRedirect":return Gh;case"linkViaPopup":case"linkViaRedirect":return Xh;case"reauthViaPopup":case"reauthViaRedirect":return Kh;default:se(this.auth,"internal-error")}}resolve(e){ye(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.resolve(e),this.unregisterAndCleanUp()}reject(e){ye(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.reject(e),this.unregisterAndCleanUp()}unregisterAndCleanUp(){this.eventManager&&this.eventManager.unregisterConsumer(this),this.pendingPromise=null,this.cleanUp()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Yh=new kt(2e3,1e4);async function Ms(t,e,n){const r=Ct(t);Mf(t,e,Ar);const s=Eo(r,n);return new Ue(r,"signInViaPopup",e,s).executeNotNull()}class Ue extends Io{constructor(e,n,r,s,i){super(e,n,s,i),this.provider=r,this.authWindow=null,this.pollId=null,Ue.currentPopupAction&&Ue.currentPopupAction.cancel(),Ue.currentPopupAction=this}async executeNotNull(){const e=await this.execute();return I(e,this.auth,"internal-error"),e}async onExecution(){ye(this.filter.length===1,"Popup operations only handle one event");const e=Or();this.authWindow=await this.resolver._openPopup(this.auth,this.provider,this.filter[0],e),this.authWindow.associatedEvent=e,this.resolver._originValidation(this.auth).catch(n=>{this.reject(n)}),this.resolver._isIframeWebStorageSupported(this.auth,n=>{n||this.reject(ae(this.auth,"web-storage-unsupported"))}),this.pollUserCancellation()}get eventId(){var e;return((e=this.authWindow)===null||e===void 0?void 0:e.associatedEvent)||null}cancel(){this.reject(ae(this.auth,"cancelled-popup-request"))}cleanUp(){this.authWindow&&this.authWindow.close(),this.pollId&&window.clearTimeout(this.pollId),this.authWindow=null,this.pollId=null,Ue.currentPopupAction=null}pollUserCancellation(){const e=()=>{var n,r;if(!((r=(n=this.authWindow)===null||n===void 0?void 0:n.window)===null||r===void 0)&&r.closed){this.pollId=window.setTimeout(()=>{this.pollId=null,this.reject(ae(this.auth,"popup-closed-by-user"))},2e3);return}this.pollId=window.setTimeout(e,Yh.get())};e()}}Ue.currentPopupAction=null;/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Qh="pendingRedirect",Ht=new Map;class Zh extends Io{constructor(e,n,r=!1){super(e,["signInViaRedirect","linkViaRedirect","reauthViaRedirect","unknown"],n,void 0,r),this.eventId=null}async execute(){let e=Ht.get(this.auth._key());if(!e){try{const r=await eg(this.resolver,this.auth)?await super.execute():null;e=()=>Promise.resolve(r)}catch(n){e=()=>Promise.reject(n)}Ht.set(this.auth._key(),e)}return this.bypassAuthState||Ht.set(this.auth._key(),()=>Promise.resolve(null)),e()}async onAuthEvent(e){if(e.type==="signInViaRedirect")return super.onAuthEvent(e);if(e.type==="unknown"){this.resolve(null);return}if(e.eventId){const n=await this.auth._redirectUserForId(e.eventId);if(n)return this.user=n,super.onAuthEvent(e);this.resolve(null)}}async onExecution(){}cleanUp(){}}async function eg(t,e){const n=rg(e),r=ng(t);if(!await r._isAvailable())return!1;const s=await r._get(n)==="true";return await r._remove(n),s}function tg(t,e){Ht.set(t._key(),e)}function ng(t){return ge(t._redirectPersistence)}function rg(t){return Bt(Qh,t.config.apiKey,t.name)}async function sg(t,e,n=!1){const r=Ct(t),s=Eo(r,e),o=await new Zh(r,s,n).execute();return o&&!n&&(delete o.user._redirectEventId,await r._persistUserIfCurrent(o.user),await r._setRedirectUser(null,e)),o}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ig=10*60*1e3;class og{constructor(e){this.auth=e,this.cachedEventUids=new Set,this.consumers=new Set,this.queuedRedirectEvent=null,this.hasHandledPotentialRedirect=!1,this.lastProcessedEventTime=Date.now()}registerConsumer(e){this.consumers.add(e),this.queuedRedirectEvent&&this.isEventForConsumer(this.queuedRedirectEvent,e)&&(this.sendToConsumer(this.queuedRedirectEvent,e),this.saveEventToCache(this.queuedRedirectEvent),this.queuedRedirectEvent=null)}unregisterConsumer(e){this.consumers.delete(e)}onEvent(e){if(this.hasEventBeenHandled(e))return!1;let n=!1;return this.consumers.forEach(r=>{this.isEventForConsumer(e,r)&&(n=!0,this.sendToConsumer(e,r),this.saveEventToCache(e))}),this.hasHandledPotentialRedirect||!ag(e)||(this.hasHandledPotentialRedirect=!0,n||(this.queuedRedirectEvent=e,n=!0)),n}sendToConsumer(e,n){var r;if(e.error&&!So(e)){const s=((r=e.error.code)===null||r===void 0?void 0:r.split("auth/")[1])||"internal-error";n.onError(ae(this.auth,s))}else n.onAuthEvent(e)}isEventForConsumer(e,n){const r=n.eventId===null||!!e.eventId&&e.eventId===n.eventId;return n.filter.includes(e.type)&&r}hasEventBeenHandled(e){return Date.now()-this.lastProcessedEventTime>=ig&&this.cachedEventUids.clear(),this.cachedEventUids.has(Us(e))}saveEventToCache(e){this.cachedEventUids.add(Us(e)),this.lastProcessedEventTime=Date.now()}}function Us(t){return[t.type,t.eventId,t.sessionId,t.tenantId].filter(e=>e).join("-")}function So({type:t,error:e}){return t==="unknown"&&e?.code==="auth/no-auth-event"}function ag(t){switch(t.type){case"signInViaRedirect":case"linkViaRedirect":case"reauthViaRedirect":return!0;case"unknown":return So(t);default:return!1}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function lg(t,e={}){return nt(t,"GET","/v1/projects",e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const cg=/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,ug=/^https?/;async function dg(t){if(t.config.emulator)return;const{authorizedDomains:e}=await lg(t);for(const n of e)try{if(fg(n))return}catch{}se(t,"unauthorized-domain")}function fg(t){const e=lr(),{protocol:n,hostname:r}=new URL(e);if(t.startsWith("chrome-extension://")){const o=new URL(t);return o.hostname===""&&r===""?n==="chrome-extension:"&&t.replace("chrome-extension://","")===e.replace("chrome-extension://",""):n==="chrome-extension:"&&o.hostname===r}if(!ug.test(n))return!1;if(cg.test(t))return r===t;const s=t.replace(/\./g,"\\.");return new RegExp("^(.+\\."+s+"|"+s+")$","i").test(r)}/**
 * @license
 * Copyright 2020 Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const hg=new kt(3e4,6e4);function js(){const t=le().___jsl;if(t?.H){for(const e of Object.keys(t.H))if(t.H[e].r=t.H[e].r||[],t.H[e].L=t.H[e].L||[],t.H[e].r=[...t.H[e].L],t.CP)for(let n=0;n<t.CP.length;n++)t.CP[n]=null}}function gg(t){return new Promise((e,n)=>{var r,s,i;function o(){js(),gapi.load("gapi.iframes",{callback:()=>{e(gapi.iframes.getContext())},ontimeout:()=>{js(),n(ae(t,"network-request-failed"))},timeout:hg.get()})}if(!((s=(r=le().gapi)===null||r===void 0?void 0:r.iframes)===null||s===void 0)&&s.Iframe)e(gapi.iframes.getContext());else if(!((i=le().gapi)===null||i===void 0)&&i.load)o();else{const a=qh("iframefcb");return le()[a]=()=>{gapi.load?o():n(ae(t,"network-request-failed"))},Jh(`https://apis.google.com/js/api.js?onload=${a}`).catch(c=>n(c))}}).catch(e=>{throw zt=null,e})}let zt=null;function mg(t){return zt=zt||gg(t),zt}/**
 * @license
 * Copyright 2020 Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const pg=new kt(5e3,15e3),bg="__/auth/iframe",vg="emulator/auth/iframe",yg={style:{position:"absolute",top:"-100px",width:"1px",height:"1px"},"aria-hidden":"true",tabindex:"-1"},_g=new Map([["identitytoolkit.googleapis.com","p"],["staging-identitytoolkit.sandbox.googleapis.com","s"],["test-identitytoolkit.sandbox.googleapis.com","t"]]);function wg(t){const e=t.config;I(e.authDomain,t,"auth-domain-config-required");const n=e.emulator?Sr(e,vg):`https://${t.config.authDomain}/${bg}`,r={apiKey:e.apiKey,appName:t.name,v:dn},s=_g.get(t.config.apiHost);s&&(r.eid=s);const i=t._getFrameworks();return i.length&&(r.fw=i.join(",")),`${n}?${$t(r).slice(1)}`}async function xg(t){const e=await mg(t),n=le().gapi;return I(n,t,"internal-error"),e.open({where:document.body,url:wg(t),messageHandlersFilter:n.iframes.CROSS_ORIGIN_IFRAMES_FILTER,attributes:yg,dontclear:!0},r=>new Promise(async(s,i)=>{await r.restyle({setHideOnLeave:!1});const o=ae(t,"network-request-failed"),a=le().setTimeout(()=>{i(o)},pg.get());function c(){le().clearTimeout(a),s(r)}r.ping(c).then(c,()=>{i(o)})}))}/**
 * @license
 * Copyright 2020 Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Eg={location:"yes",resizable:"yes",statusbar:"yes",toolbar:"no"},Ig=500,Sg=600,$g="_blank",kg="http://localhost";class Fs{constructor(e){this.window=e,this.associatedEvent=null}close(){if(this.window)try{this.window.close()}catch{}}}function Tg(t,e,n,r=Ig,s=Sg){const i=Math.max((window.screen.availHeight-s)/2,0).toString(),o=Math.max((window.screen.availWidth-r)/2,0).toString();let a="";const c=Object.assign(Object.assign({},Eg),{width:r.toString(),height:s.toString(),top:i,left:o}),l=Q().toLowerCase();n&&(a=so(l)?$g:n),ro(l)&&(e=e||kg,c.scrollbars="yes");const u=Object.entries(c).reduce((v,[m,g])=>`${v}${m}=${g},`,"");if(nh(l)&&a!=="_self")return Cg(e||"",a),new Fs(null);const d=window.open(e||"",a,u);I(d,t,"popup-blocked");try{d.focus()}catch{}return new Fs(d)}function Cg(t,e){const n=document.createElement("a");n.href=t,n.target=e;const r=document.createEvent("MouseEvent");r.initMouseEvent("click",!0,!0,window,1,0,0,0,0,!1,!1,!1,!1,1,null),n.dispatchEvent(r)}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ag="__/auth/handler",Og="emulator/auth/handler";function Bs(t,e,n,r,s,i){I(t.config.authDomain,t,"auth-domain-config-required"),I(t.config.apiKey,t,"invalid-api-key");const o={apiKey:t.config.apiKey,appName:t.name,authType:n,redirectUrl:r,v:dn,eventId:s};if(e instanceof Ar){e.setDefaultLanguage(t.languageCode),o.providerId=e.providerId||"",Sd(e.getCustomParameters())||(o.customParameters=JSON.stringify(e.getCustomParameters()));for(const[c,l]of Object.entries(i||{}))o[c]=l}if(e instanceof At){const c=e.getScopes().filter(l=>l!=="");c.length>0&&(o.scopes=c.join(","))}t.tenantId&&(o.tid=t.tenantId);const a=o;for(const c of Object.keys(a))a[c]===void 0&&delete a[c];return`${Ng(t)}?${$t(a).slice(1)}`}function Ng({config:t}){return t.emulator?Sr(t,Og):`https://${t.authDomain}/${Ag}`}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Bn="webStorageSupport";class Rg{constructor(){this.eventManagers={},this.iframes={},this.originValidationPromises={},this._redirectPersistence=vo,this._completeRedirectFn=sg,this._overrideRedirectResult=tg}async _openPopup(e,n,r,s){var i;ye((i=this.eventManagers[e._key()])===null||i===void 0?void 0:i.manager,"_initialize() not called before _openPopup()");const o=Bs(e,n,r,lr(),s);return Tg(e,o,Or())}async _openRedirect(e,n,r,s){return await this._originValidation(e),Ph(Bs(e,n,r,lr(),s)),new Promise(()=>{})}_initialize(e){const n=e._key();if(this.eventManagers[n]){const{manager:s,promise:i}=this.eventManagers[n];return s?Promise.resolve(s):(ye(i,"If manager is not set, promise should be"),i)}const r=this.initAndGetManager(e);return this.eventManagers[n]={promise:r},r.catch(()=>{delete this.eventManagers[n]}),r}async initAndGetManager(e){const n=await xg(e),r=new og(e);return n.register("authEvent",s=>(I(s?.authEvent,e,"invalid-auth-event"),{status:r.onEvent(s.authEvent)?"ACK":"ERROR"}),gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER),this.eventManagers[e._key()]={manager:r},this.iframes[e._key()]=n,r}_isIframeWebStorageSupported(e,n){this.iframes[e._key()].send(Bn,{type:Bn},s=>{var i;const o=(i=s?.[0])===null||i===void 0?void 0:i[Bn];o!==void 0&&n(!!o),se(e,"internal-error")},gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER)}_originValidation(e){const n=e._key();return this.originValidationPromises[n]||(this.originValidationPromises[n]=dg(e)),this.originValidationPromises[n]}get _shouldInitProactively(){return co()||kr()||hn()}}const Dg=Rg;var Hs="@firebase/auth",zs="0.20.11";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Pg{constructor(e){this.auth=e,this.internalListeners=new Map}getUid(){var e;return this.assertAuthConfigured(),((e=this.auth.currentUser)===null||e===void 0?void 0:e.uid)||null}async getToken(e){return this.assertAuthConfigured(),await this.auth._initializationPromise,this.auth.currentUser?{accessToken:await this.auth.currentUser.getIdToken(e)}:null}addAuthTokenListener(e){if(this.assertAuthConfigured(),this.internalListeners.has(e))return;const n=this.auth.onIdTokenChanged(r=>{var s;e(((s=r)===null||s===void 0?void 0:s.stsTokenManager.accessToken)||null)});this.internalListeners.set(e,n),this.updateProactiveRefresh()}removeAuthTokenListener(e){this.assertAuthConfigured();const n=this.internalListeners.get(e);!n||(this.internalListeners.delete(e),n(),this.updateProactiveRefresh())}assertAuthConfigured(){I(this.auth._initializationPromise,"dependent-sdk-initialized-before-auth")}updateProactiveRefresh(){this.internalListeners.size>0?this.auth._startProactiveRefresh():this.auth._stopProactiveRefresh()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Lg(t){switch(t){case"Node":return"node";case"ReactNative":return"rn";case"Worker":return"webworker";case"Cordova":return"cordova";default:return}}function Mg(t){bt(new Xe("auth",(e,{options:n})=>{const r=e.getProvider("app").getImmediate(),s=e.getProvider("heartbeat"),{apiKey:i,authDomain:o}=r.options;return((a,c)=>{I(i&&!i.includes(":"),"invalid-api-key",{appName:a.name}),I(!o?.includes(":"),"argument-error",{appName:a.name});const l={apiKey:i,authDomain:o,clientPlatform:t,apiHost:"identitytoolkit.googleapis.com",tokenApiHost:"securetoken.googleapis.com",apiScheme:"https",sdkClientVersion:uo(t)},u=new oh(a,c,l);return jf(u,n),u})(r,s)},"PUBLIC").setInstantiationMode("EXPLICIT").setInstanceCreatedCallback((e,n,r)=>{e.getProvider("auth-internal").initialize()})),bt(new Xe("auth-internal",e=>{const n=Ct(e.getProvider("auth").getImmediate());return(r=>new Pg(r))(n)},"PRIVATE").setInstantiationMode("EXPLICIT")),Je(Hs,zs,Lg(t)),Je(Hs,zs,"esm2017")}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ug=5*60,jg=Bi("authIdTokenMaxAge")||Ug;let Vs=null;const Fg=t=>async e=>{const n=e&&await e.getIdTokenResult(),r=n&&(new Date().getTime()-Date.parse(n.issuedAtTime))/1e3;if(r&&r>jg)return;const s=n?.token;Vs!==s&&(Vs=s,await fetch(t,{method:s?"POST":"DELETE",headers:s?{Authorization:`Bearer ${s}`}:{}}))};function Bg(t=$f()){const e=Wi(t,"auth");if(e.isInitialized())return e.getImmediate();const n=Uf(t,{popupRedirectResolver:Dg,persistence:[Vh,Nh,vo]}),r=Bi("authTokenSyncURL");if(r){const i=Fg(r);$h(n,i,()=>i(n.currentUser)),Sh(n,o=>i(o))}const s=yd("auth");return s&&ah(n,`http://${s}`),n}Mg("Browser");function Hg(){const[t,e]=_(null);return{email:t,setEmail:e}}const $o=ee(Hg);var zg="firebase",Vg="9.14.0";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */Je(zg,Vg,"app");const Wg={apiKey:"AIzaSyAX9a9qLUzLoVFy9YrRprTWuf7lwZ-cEi0",authDomain:"fabled-pivot-305219.firebaseapp.com",projectId:"fabled-pivot-305219",storageBucket:"fabled-pivot-305219.appspot.com",messagingSenderId:"293220208202",appId:"1:293220208202:web:59eabbc4f981ead408e0b3",measurementId:"G-7E7PGPVJ99"},Jg=Ji(Wg);function qg(){const[t,e]=_(null);return e(Bg(Jg)),{auth:t}}const ko=ee(qg),Gg=y('<div id="tab_account" class="tabcontent p-4"><p class="text-gray-600"></p><button type="button" class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 text-sm font-medium leading-4 text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 mt-2">Logout</button></div>'),{tabName:Kg}=tt,{email:Xg}=$o,{auth:Yg}=ko;function Qg(){function t(){Th(Yg()).catch(function(e){console.error(e)})}return(()=>{const e=Gg.cloneNode(!0),n=e.firstChild,r=n.nextSibling;return f(n,Xg),r.$$click=t,$(()=>e.classList.toggle("hidden",Kg()!="account")),e})()}R(["click"]);const Zg=y('<div class="md:pl-36 flex flex-col flex-1"><main class="flex-1"><div class=""><div class="mx-auto"><div></div></div></div></main></div>'),{multiuser:Ws}=Ne,{logged:em}=Ve,{localModules:tm,loadAllModules:nm}=It;function rm(){const[t,e]=_(!1);return Oe(function(){(Ws()==!1||em()==!0)&&Oi(tm())&&nm()}),(()=>{const n=Zg.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild;return f(o,h(ku,{get jobsTrigger(){return t()},setJobsTrigger:e}),null),f(o,h(rd,{get jobsTrigger(){return t()},setJobsTrigger:e}),null),f(o,h(od,{}),null),f(o,h(ie,{get when(){return Ws()==!0},get children(){return h(Qg,{})}}),null),n})()}function sm(){const[t,e]=_(!0);return{systemReady:t,setSystemReady:e}}const im=ee(sm),om=y('<div id="tab_systemnotready" class="tabcontent"><div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-md bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"><div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4"><div class="sm:flex sm:items-start"><div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"><svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v3.75m-9.303 3.376C1.83 19.126 2.914 21 4.645 21h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 4.88c-.866-1.501-3.032-1.501-3.898 0L2.697 17.626zM12 17.25h.007v.008H12v-.008z"></path></svg></div><div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left"><h3 class="text-lg font-medium leading-6 text-gray-900" id="modal-title">System not ready</h3><div class="mt-2"><p class="text-sm text-gray-500">OakVar server is not running or it is having a problem. Please contact your system administrator.</p></div></div></div></div></div></div></div></div></div>');function am(){const{systemReady:t,setSystemReady:e}=im;return(()=>{const n=om.cloneNode(!0);return $(()=>n.classList.toggle("hidden",!!t())),n})()}function lm(){const[t,e]=_(!0);return{appLoading:t,setAppLoading:e}}const pn=ee(lm),cm=y('<div class="h-full"></div>'),{multiuser:um}=Ne,{appLoading:dm}=pn;function fm(){const{logged:t}=Ve;return(()=>{const e=cm.cloneNode(!0);return f(e,h(Xl,{}),null),f(e,h(rm,{}),null),f(e,h(am,{}),null),$(()=>e.classList.toggle("hidden",!!(dm()||um()&&!t()))),e})()}const hm=y('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100"><svg class="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"></path></svg></div><div class="mt-3 text-center sm:mt-5"><h3 class="text-lg font-medium leading-6 text-gray-900"></h3><div class="mt-2"><p class="text-sm text-gray-500"></p></div></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm">Dismiss</button></div></div></div></div></div>');function gm(t){return(()=>{const e=hm.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.nextSibling,l=c.firstChild,u=l.nextSibling,d=u.firstChild,v=o.nextSibling,m=v.firstChild;return f(l,()=>t.title),f(d,()=>t.text),on(m,"click",t.callback,!0),e})()}R(["click"]);const mm=y('<svg class="hide animate-spin ml-1 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>');function Js(t){return(()=>{const e=mm.cloneNode(!0);return $(()=>e.classList.toggle("hidden",!t.show)),e})()}const pm=y('<div class="flex w-screen h-screen items-center justify-center"><div id="container" class="w-[64rem]"><div class="flex min-h-full flex-col justify-center py-12 sm:px-6 lg:px-8"><div class="sm:mx-auto sm:w-full sm:max-w-md"><img class="mx-auto h-16 w-auto" alt="OakVar"><h2 class="mt-4 text-center text-3xl font-bold tracking-tight text-gray-900">Sign in</h2><h2 class="hide mt-4 text-center text-3xl font-bold tracking-tight text-gray-900">Sign up</h2></div><p class="mt-2 text-center text-sm text-gray-600">Or&nbsp;<a href="#" class="font-medium text-indigo-600 hover:text-indigo-500">sign up</a><a href="#" class="hide font-medium text-indigo-600 hover:text-indigo-500">sign in</a></p><div class="mt-6 sm:mx-auto sm:w-full sm:max-w-md"><div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10"><div class="space-y-6" method="POST"><div><label for="email" class="block text-sm font-medium text-gray-700">Email address</label><div class="mt-1"><input id="email" name="email" type="email" autocomplete="email" required class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"><div class="text-xs text-orange-600 mt-2"></div></div></div><div><label for="password" class="block text-sm font-medium text-gray-700">Password</label><div class="mt-1"><input id="password" name="password" type="password" autocomplete="current-password" required class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"><div class="text-xs text-orange-600 mt-2"></div></div></div><div class="flex items-center justify-between"><div class="flex items-center"></div><div class="text-sm"><a href="#" class="font-medium">Forgot your password?</a></div></div><div><button id="signin_btn" type="submit" class="flex w-full justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Sign in</button><button id="signup_btn" type="submit" class="flex w-full justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Sign up</button></div></div></div></div></div></div></div>'),{serverUrl:Lt,withCredentials:Hn}=te,{email:Le,setEmail:qs}=$o,{setTabName:bm}=tt,{auth:lt}=ko,{appLoading:vm,setAppLoading:zn}=pn,{multiuser:ym}=Ne,{logged:_m,setLogged:Vn}=Ve;let Gs=null;function wm(){const[t,e]=_("signin"),[n,r]=_(!1),[s,i]=_(!1),[o,a]=_(null),[c,l]=_(!1),[u,d]=_(null),[v,m]=_(null),[g,b]=_(!1),[w,x]=_(null),[S,T]=_(null),[P,U]=_(""),[k,W]=_(""),[z,C]=_(!0),[L,O]=_(!0),K={"auth/user-not-found":"Account was not found. Please sign up first.","auth/account-exists-with-different-credential":"Account exists with different credential.","auth/wrong-password":"Wrong password. Please check your password or use Forget Your Password? link.","auth/missing-email":"Please provide an email address.","missing-password":"Please provide a password.","account-exists":"Account already exists.","auth/too-many-requests":"Too many failed attempts. Wait for a while and try again, or use Forgot your password? link."};let B=()=>{l(!1)};Gs||(Gs=kh(lt(),function(E){E?(zn(!0),st(E.email)):wn()}));function J(){return!z()&&!L()}function De(){vn(),_n()}function bn(E){qs(E.target.value),De(),E.keyCode==13&&J()&&it("email")}function vn(){if(!Le()||Le().length==0){U("Please enter an email."),C(!0);return}let E=/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9]+)+$/;if(!Le().match(E)){U("Email is invalid."),C(!0);return}U(""),C(!1)}function yn(E){a(E.target.value),De(),E.keyCode==13&&J()&&it("email")}function _n(){if(!o()||o().length==0){W("Please enter a password."),O(!0);return}let E=/^[a-zA-Z0-9.!?#$%&^_@*]+$/;if(!o().match(E)){W("Password is invalid (a-z, A-Z, 0-9, .!?#$%&^_@* allowed)."),O(!0);return}return W(""),O(!1),!0}function st(E){F.post(Lt()+"/server/loginsuccess",{email:E},{withCredentials:Hn}).then(function(q){qs(q.data.email),r(!1),bm("submit"),Vn(!0),zn(!1)}).catch(function(q){xe(q,"Login failed"),r(!1)})}function wn(){F.get(Lt()+"/server/logout",{withCredentials:Hn}).then(function(E){E.status==200&&Vn(!1)}).catch(function(E){console.error(E)}),zn(!1)}function xe(E,q){if(E.response&&(E=E.response.data),E.code=="auth/popup-closed-by-user"){r(!1);return}x(q);let A=K[E.code];A?T(A):(T("Error code: "+E.code),console.error(E)),b(!0)}function xn(){r(!0),Ih(lt(),Le(),o()).catch(function(E){xe(E,"Login failed"),r(!1)})}function En(){r(!0);const E=new de;Ms(lt(),E).then(function(q){st(q)}).catch(function(q){xe(q,"Login failed"),r(!1)})}function In(){r(!0);const E=new fe;Ms(lt(),E).then(function(q){st(q)}).catch(function(q){xe(q,"Login failed"),r(!1)})}function it(E){E=="email"?xn():E=="google"?En():E=="github"&&In()}function Sn(){i(!0),F.post(Lt()+"/server/signup",{email:Le(),password:o()},{withCredentials:Hn}).then(function(E){E.data.code&&(d("Success"),m(E.data.code),B=()=>{i(!1),Vn(!0)},l(!0))}).catch(function(E){xe(E,"Signup failed"),i(!1)})}function $n(){Eh(lt(),Le()).then(function(){d("Success"),m("Please check your email for a password reset link."),l(!0)}).catch(function(E){xe(E,"Password reset failed")})}return(()=>{const E=pm.cloneNode(!0),q=E.firstChild,A=q.firstChild,D=A.firstChild,oe=D.firstChild,Z=oe.nextSibling,To=Z.nextSibling,Rr=D.nextSibling,Co=Rr.firstChild,Nt=Co.nextSibling,kn=Nt.nextSibling,Ao=Rr.nextSibling,Oo=Ao.firstChild,No=Oo.firstChild,Dr=No.firstChild,Ro=Dr.firstChild,Do=Ro.nextSibling,Tn=Do.firstChild,Po=Tn.nextSibling,Pr=Dr.nextSibling,Lo=Pr.firstChild,Mo=Lo.nextSibling,Cn=Mo.firstChild,Uo=Cn.nextSibling,Lr=Pr.nextSibling,jo=Lr.firstChild,Mr=jo.nextSibling,An=Mr.firstChild,Fo=Lr.nextSibling,Pe=Fo.firstChild;Pe.firstChild;const ot=Pe.nextSibling;return ot.firstChild,Nt.$$click=e,Nt.$$clickData="signup",kn.$$click=e,kn.$$clickData="signin",Tn.$$keyup=bn,f(Po,P),Cn.$$keyup=yn,f(Uo,k),An.$$click=$n,Pe.$$click=it,Pe.$$clickData="email",f(Pe,h(Js,{get show(){return n()}}),null),ot.$$click=Sn,f(ot,h(Js,{get show(){return s()}}),null),f(E,h(ie,{get when(){return g()},get children(){return h(Ci,{get title(){return w()},get text(){return S()},setShowDialog:b})}}),null),f(E,h(ie,{get when(){return c()},get children(){return h(gm,{get title(){return u()},get text(){return v()},callback:B})}}),null),$(M=>{const Ur=!!(vm()||!ym()||_m()),jr=Lt()+"/submit/images/logo_only.png",Fr=t()!="signin",Br=t()!="signup",Hr=t()!="signin",zr=t()!="signup",Vr=t()!="signin",Bo={"text-indigo-600":!z(),"hover:text-indigo-500":!z(),"text-gray-500":z(),"cursor-default":z()},Wr=z(),Ho={hidden:t()!="signin","bg-indigo-600":J(),"hover:bg-indigo-700":J(),"bg-gray-500":!J()},Jr=!J(),zo={hidden:t()!="signup","bg-indigo-600":J(),"hover:bg-indigo-700":J(),"bg-gray-500":!J()},qr=!J();return Ur!==M._v$&&E.classList.toggle("hidden",M._v$=Ur),jr!==M._v$2&&V(oe,"src",M._v$2=jr),Fr!==M._v$3&&Z.classList.toggle("hidden",M._v$3=Fr),Br!==M._v$4&&To.classList.toggle("hidden",M._v$4=Br),Hr!==M._v$5&&Nt.classList.toggle("hidden",M._v$5=Hr),zr!==M._v$6&&kn.classList.toggle("hidden",M._v$6=zr),Vr!==M._v$7&&Mr.classList.toggle("hidden",M._v$7=Vr),M._v$8=Mt(An,Bo,M._v$8),Wr!==M._v$9&&(An.disabled=M._v$9=Wr),M._v$10=Mt(Pe,Ho,M._v$10),Jr!==M._v$11&&(Pe.disabled=M._v$11=Jr),M._v$12=Mt(ot,zo,M._v$12),qr!==M._v$13&&(ot.disabled=M._v$13=qr),M},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0,_v$6:void 0,_v$7:void 0,_v$8:void 0,_v$9:void 0,_v$10:void 0,_v$11:void 0,_v$12:void 0,_v$13:void 0}),$(()=>Tn.value=Le()),$(()=>Cn.value=o()),E})()}R(["click","keyup"]);const xm=y('<div class="h-screen w-screen grid place-items-center"><img class="h-96 animate-pulse"></div>'),{serverUrl:Em}=te,{appLoading:Im}=pn;function Sm(){return(()=>{const t=xm.cloneNode(!0),e=t.firstChild;return $(n=>{const r=!Im(),s=Em()+"/submit/images/logo_transparent.png";return r!==n._v$&&t.classList.toggle("hidden",n._v$=r),s!==n._v$2&&V(e,"src",n._v$2=s),n},{_v$:void 0,_v$2:void 0}),t})()}const{serverUrl:Wn}=te,{logged:Ks,setLogged:Xs}=Ve,{multiuser:Jn,setMultiuser:Ys}=Ne,{setAppLoading:$m}=pn;function km(){Ys(null),Xs(null),Oe(function(){Jn()!=null&&Ks()!=null&&$m(!1)});function t(){F.get(Wn()+"/server/deletetoken").then(function(){}).catch(function(r){console.error(r)})}function e(){F.get(Wn()+"/submit/servermode").then(function(r){Ys(r.data.servermode),Jn()||t()}).catch(function(r){console.error(r)})}function n(){F.get(Wn()+"/submit/loginstate").then(function(r){Xs(r.data.loggedin)}).catch(function(r){console.error(r)})}return Jn()==null&&e(),Ks()==null&&n(),[h(Sm,{}),h(wm,{}),h(fm,{})]}ca(()=>h(km,{}),document.getElementById("root"));
