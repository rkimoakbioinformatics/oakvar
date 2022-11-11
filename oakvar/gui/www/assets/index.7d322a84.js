(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))r(s);new MutationObserver(s=>{for(const i of s)if(i.type==="childList")for(const o of i.addedNodes)o.tagName==="LINK"&&o.rel==="modulepreload"&&r(o)}).observe(document,{childList:!0,subtree:!0});function n(s){const i={};return s.integrity&&(i.integrity=s.integrity),s.referrerpolicy&&(i.referrerPolicy=s.referrerpolicy),s.crossorigin==="use-credentials"?i.credentials="include":s.crossorigin==="anonymous"?i.credentials="omit":i.credentials="same-origin",i}function r(s){if(s.ep)return;s.ep=!0;const i=n(s);fetch(s.href,i)}})();const J={};function Vo(t){J.context=t}const Wo=(t,e)=>t===e,he=Symbol("solid-proxy"),Jn=Symbol("solid-track"),Ht={equals:Wo};let Qs=ri;const pe=1,zt=2,Zs={owned:null,cleanups:null,context:null,owner:null},An={};var G=null;let Pe=null,H=null,K=null,de=null,cr=0;function Q(t,e){const n=H,r=G,s=t.length===0,i=s?Zs:{owned:null,cleanups:null,context:null,owner:e||r},o=s?t:()=>t(()=>ke(()=>dr(i)));G=i,H=null;try{return Te(o,!0)}finally{H=n,G=r}}function _(t,e){e=e?Object.assign({},Ht,e):Ht;const n={value:t,observers:null,observerSlots:null,comparator:e.equals||void 0},r=s=>(typeof s=="function"&&(s=s(n.value)),ni(n,s));return[ti.bind(n),r]}function Gr(t,e,n){const r=nn(t,e,!0,pe);Xe(r)}function $(t,e,n){const r=nn(t,e,!1,pe);Xe(r)}function Fe(t,e,n){Qs=Yo;const r=nn(t,e,!1,pe);r.user=!0,de?de.push(r):Xe(r)}function ge(t,e,n){n=n?Object.assign({},Ht,n):Ht;const r=nn(t,e,!0,0);return r.observers=null,r.observerSlots=null,r.comparator=n.equals||void 0,Xe(r),ti.bind(r)}function ur(t,e,n){let r,s,i;arguments.length===2&&typeof e=="object"||arguments.length===1?(r=!0,s=t,i=e||{}):(r=t,s=e,i=n||{});let o=null,a=An,l=null,c=!1,u="initialValue"in i,v=typeof r=="function"&&ge(r);const g=new Set,[b,m]=(i.storage||_)(i.initialValue),[p,w]=_(void 0),[x,S]=_(void 0,{equals:!1}),[C,D]=_(u?"ready":"unresolved");if(J.context){l=`${J.context.id}${J.context.count++}`;let A;i.ssrLoadFrom==="initial"?a=i.initialValue:J.load&&(A=J.load(l))&&(a=A[0])}function M(A,P,N,Y){return o===A&&(o=null,u=!0,(A===a||P===a)&&i.onHydrated&&queueMicrotask(()=>i.onHydrated(Y,{value:P})),a=An,k(P,N)),P}function k(A,P){Te(()=>{P||m(()=>A),D(P?"errored":"ready"),w(P);for(const N of g.keys())N.decrement();g.clear()},!1)}function z(){const A=Go,P=b(),N=p();if(N&&!o)throw N;return H&&!H.user&&A&&Gr(()=>{x(),o&&(A.resolved||g.has(A)||(A.increment(),g.add(A)))}),P}function F(A=!0){if(A!==!1&&c)return;c=!1;const P=v?v():r;if(P==null||P===!1){M(o,ke(b));return}const N=a!==An?a:ke(()=>s(P,{value:b(),refetching:A}));return typeof N!="object"||!(N&&"then"in N)?(M(o,N),N):(o=N,c=!0,queueMicrotask(()=>c=!1),Te(()=>{D(u?"refreshing":"pending"),S()},!1),N.then(Y=>M(N,Y,void 0,P),Y=>M(N,void 0,ii(Y))))}return Object.defineProperties(z,{state:{get:()=>C()},error:{get:()=>p()},loading:{get(){const A=C();return A==="pending"||A==="refreshing"}},latest:{get(){if(!u)return z();const A=p();if(A&&!o)throw A;return b()}}}),v?Gr(()=>F(!1)):F(!1),[z,{refetch:F,mutate:m}]}function Jo(t){return Te(t,!1)}function ke(t){const e=H;H=null;try{return t()}finally{H=e}}function Vt(t){return G===null||(G.cleanups===null?G.cleanups=[t]:G.cleanups.push(t)),t}function ei(){return H}function qo(t){const e=ge(t),n=ge(()=>qn(e()));return n.toArray=()=>{const r=n();return Array.isArray(r)?r:r!=null?[r]:[]},n}let Go;function ti(){const t=Pe;if(this.sources&&(this.state||t))if(this.state===pe||t)Xe(this);else{const e=K;K=null,Te(()=>Jt(this),!1),K=e}if(H){const e=this.observers?this.observers.length:0;H.sources?(H.sources.push(this),H.sourceSlots.push(e)):(H.sources=[this],H.sourceSlots=[e]),this.observers?(this.observers.push(H),this.observerSlots.push(H.sources.length-1)):(this.observers=[H],this.observerSlots=[H.sources.length-1])}return this.value}function ni(t,e,n){let r=t.value;return(!t.comparator||!t.comparator(r,e))&&(t.value=e,t.observers&&t.observers.length&&Te(()=>{for(let s=0;s<t.observers.length;s+=1){const i=t.observers[s],o=Pe&&Pe.running;o&&Pe.disposed.has(i),(o&&!i.tState||!o&&!i.state)&&(i.pure?K.push(i):de.push(i),i.observers&&si(i)),o||(i.state=pe)}if(K.length>1e6)throw K=[],new Error},!1)),e}function Xe(t){if(!t.fn)return;dr(t);const e=G,n=H,r=cr;H=G=t,Ko(t,t.value,r),H=n,G=e}function Ko(t,e,n){let r;try{r=t.fn(e)}catch(s){t.pure&&(t.state=pe),oi(s)}(!t.updatedAt||t.updatedAt<=n)&&(t.updatedAt!=null&&"observers"in t?ni(t,r):t.value=r,t.updatedAt=n)}function nn(t,e,n,r=pe,s){const i={fn:t,state:r,updatedAt:null,owned:null,sources:null,sourceSlots:null,cleanups:null,value:e,owner:G,context:null,pure:n};return G===null||G!==Zs&&(G.owned?G.owned.push(i):G.owned=[i]),i}function Wt(t){const e=Pe;if(t.state===0||e)return;if(t.state===zt||e)return Jt(t);if(t.suspense&&ke(t.suspense.inFallback))return t.suspense.effects.push(t);const n=[t];for(;(t=t.owner)&&(!t.updatedAt||t.updatedAt<cr);)(t.state||e)&&n.push(t);for(let r=n.length-1;r>=0;r--)if(t=n[r],t.state===pe||e)Xe(t);else if(t.state===zt||e){const s=K;K=null,Te(()=>Jt(t,n[0]),!1),K=s}}function Te(t,e){if(K)return t();let n=!1;e||(K=[]),de?n=!0:de=[],cr++;try{const r=t();return Xo(n),r}catch(r){K||(de=null),oi(r)}}function Xo(t){if(K&&(ri(K),K=null),t)return;const e=de;de=null,e.length&&Te(()=>Qs(e),!1)}function ri(t){for(let e=0;e<t.length;e++)Wt(t[e])}function Yo(t){let e,n=0;for(e=0;e<t.length;e++){const r=t[e];r.user?t[n++]=r:Wt(r)}for(J.context&&Vo(),e=0;e<n;e++)Wt(t[e])}function Jt(t,e){const n=Pe;t.state=0;for(let r=0;r<t.sources.length;r+=1){const s=t.sources[r];s.sources&&(s.state===pe||n?s!==e&&Wt(s):(s.state===zt||n)&&Jt(s,e))}}function si(t){const e=Pe;for(let n=0;n<t.observers.length;n+=1){const r=t.observers[n];(!r.state||e)&&(r.state=zt,r.pure?K.push(r):de.push(r),r.observers&&si(r))}}function dr(t){let e;if(t.sources)for(;t.sources.length;){const n=t.sources.pop(),r=t.sourceSlots.pop(),s=n.observers;if(s&&s.length){const i=s.pop(),o=n.observerSlots.pop();r<s.length&&(i.sourceSlots[o]=r,s[r]=i,n.observerSlots[r]=o)}}if(t.owned){for(e=0;e<t.owned.length;e++)dr(t.owned[e]);t.owned=null}if(t.cleanups){for(e=0;e<t.cleanups.length;e++)t.cleanups[e]();t.cleanups=null}t.state=0,t.context=null}function ii(t){return t instanceof Error||typeof t=="string"?t:new Error("Unknown error")}function oi(t){throw t=ii(t),t}function qn(t){if(typeof t=="function"&&!t.length)return qn(t());if(Array.isArray(t)){const e=[];for(let n=0;n<t.length;n++){const r=qn(t[n]);Array.isArray(r)?e.push.apply(e,r):e.push(r)}return e}return t}const Qo=Symbol("fallback");function Kr(t){for(let e=0;e<t.length;e++)t[e]()}function Zo(t,e,n={}){let r=[],s=[],i=[],o=0,a=e.length>1?[]:null;return Vt(()=>Kr(i)),()=>{let l=t()||[],c,u;return l[Jn],ke(()=>{let g=l.length,b,m,p,w,x,S,C,D,M;if(g===0)o!==0&&(Kr(i),i=[],r=[],s=[],o=0,a&&(a=[])),n.fallback&&(r=[Qo],s[0]=Q(k=>(i[0]=k,n.fallback())),o=1);else if(o===0){for(s=new Array(g),u=0;u<g;u++)r[u]=l[u],s[u]=Q(v);o=g}else{for(p=new Array(g),w=new Array(g),a&&(x=new Array(g)),S=0,C=Math.min(o,g);S<C&&r[S]===l[S];S++);for(C=o-1,D=g-1;C>=S&&D>=S&&r[C]===l[D];C--,D--)p[D]=s[C],w[D]=i[C],a&&(x[D]=a[C]);for(b=new Map,m=new Array(D+1),u=D;u>=S;u--)M=l[u],c=b.get(M),m[u]=c===void 0?-1:c,b.set(M,u);for(c=S;c<=C;c++)M=r[c],u=b.get(M),u!==void 0&&u!==-1?(p[u]=s[c],w[u]=i[c],a&&(x[u]=a[c]),u=m[u],b.set(M,u)):i[c]();for(u=S;u<g;u++)u in p?(s[u]=p[u],i[u]=w[u],a&&(a[u]=x[u],a[u](u))):s[u]=Q(v);s=s.slice(0,o=g),r=l.slice(0)}return s});function v(g){if(i[u]=g,a){const[b,m]=_(u);return a[u]=m,e(l[u],b)}return e(l[u])}}}function f(t,e){return ke(()=>t(e||{}))}function Ot(){return!0}const ea={get(t,e,n){return e===he?n:t.get(e)},has(t,e){return t.has(e)},set:Ot,deleteProperty:Ot,getOwnPropertyDescriptor(t,e){return{configurable:!0,enumerable:!0,get(){return t.get(e)},set:Ot,deleteProperty:Ot}},ownKeys(t){return t.keys()}};function On(t){return(t=typeof t=="function"?t():t)?t:{}}function ta(...t){if(t.some(n=>n&&(he in n||typeof n=="function")))return new Proxy({get(n){for(let r=t.length-1;r>=0;r--){const s=On(t[r])[n];if(s!==void 0)return s}},has(n){for(let r=t.length-1;r>=0;r--)if(n in On(t[r]))return!0;return!1},keys(){const n=[];for(let r=0;r<t.length;r++)n.push(...Object.keys(On(t[r])));return[...new Set(n)]}},ea);const e={};for(let n=t.length-1;n>=0;n--)if(t[n]){const r=Object.getOwnPropertyDescriptors(t[n]);for(const s in r)s in e||Object.defineProperty(e,s,{enumerable:!0,get(){for(let i=t.length-1;i>=0;i--){const o=(t[i]||{})[s];if(o!==void 0)return o}}})}return e}function be(t){const e="fallback"in t&&{fallback:()=>t.fallback};return ge(Zo(()=>t.each,t.children,e||void 0))}function Z(t){let e=!1;const n=t.keyed,r=ge(()=>t.when,void 0,{equals:(s,i)=>e?s===i:!s==!i});return ge(()=>{const s=r();if(s){const i=t.children,o=typeof i=="function"&&i.length>0;return e=n||o,o?ke(()=>i(s)):i}return t.fallback})}function ai(t){let e=!1,n=!1;const r=qo(()=>t.children),s=ge(()=>{let i=r();Array.isArray(i)||(i=[i]);for(let o=0;o<i.length;o++){const a=i[o].when;if(a)return n=!!i[o].keyed,[o,a,i[o]]}return[-1]},void 0,{equals:(i,o)=>i[0]===o[0]&&(e?i[1]===o[1]:!i[1]==!o[1])&&i[2]===o[2]});return ge(()=>{const[i,o,a]=s();if(i<0)return t.fallback;const l=a.children,c=typeof l=="function"&&l.length>0;return e=n||c,c?ke(()=>l(o)):l})}function Gn(t){return t}const na=["allowfullscreen","async","autofocus","autoplay","checked","controls","default","disabled","formnovalidate","hidden","indeterminate","ismap","loop","multiple","muted","nomodule","novalidate","open","playsinline","readonly","required","reversed","seamless","selected"],ra=new Set(["className","value","readOnly","formNoValidate","isMap","noModule","playsInline",...na]),sa=new Set(["innerHTML","textContent","innerText","children"]),ia=Object.assign(Object.create(null),{className:"class",htmlFor:"for"}),Xr=Object.assign(Object.create(null),{class:"className",formnovalidate:"formNoValidate",ismap:"isMap",nomodule:"noModule",playsinline:"playsInline",readonly:"readOnly"}),oa=new Set(["beforeinput","click","dblclick","contextmenu","focusin","focusout","input","keydown","keyup","mousedown","mousemove","mouseout","mouseover","mouseup","pointerdown","pointermove","pointerout","pointerover","pointerup","touchend","touchmove","touchstart"]),aa={xlink:"http://www.w3.org/1999/xlink",xml:"http://www.w3.org/XML/1998/namespace"};function la(t,e,n){let r=n.length,s=e.length,i=r,o=0,a=0,l=e[s-1].nextSibling,c=null;for(;o<s||a<i;){if(e[o]===n[a]){o++,a++;continue}for(;e[s-1]===n[i-1];)s--,i--;if(s===o){const u=i<r?a?n[a-1].nextSibling:n[i-a]:l;for(;a<i;)t.insertBefore(n[a++],u)}else if(i===a)for(;o<s;)(!c||!c.has(e[o]))&&e[o].remove(),o++;else if(e[o]===n[i-1]&&n[a]===e[s-1]){const u=e[--s].nextSibling;t.insertBefore(n[a++],e[o++].nextSibling),t.insertBefore(n[--i],u),e[s]=n[i]}else{if(!c){c=new Map;let v=a;for(;v<i;)c.set(n[v],v++)}const u=c.get(e[o]);if(u!=null)if(a<u&&u<i){let v=o,g=1,b;for(;++v<s&&v<i&&!((b=c.get(e[v]))==null||b!==u+g);)g++;if(g>u-a){const m=e[o];for(;a<u;)t.insertBefore(n[a++],m)}else t.replaceChild(n[a++],e[o++])}else o++;else e[o++].remove()}}}const Yr="_$DX_DELEGATE";function ca(t,e,n,r={}){let s;return Q(i=>{s=i,e===document?t():d(e,t(),e.firstChild?null:void 0,n)},r.owner),()=>{s(),e.textContent=""}}function y(t,e,n){const r=document.createElement("template");r.innerHTML=t;let s=r.content.firstChild;return n&&(s=s.firstChild),s}function R(t,e=window.document){const n=e[Yr]||(e[Yr]=new Set);for(let r=0,s=t.length;r<s;r++){const i=t[r];n.has(i)||(n.add(i),e.addEventListener(i,ga))}}function q(t,e,n){n==null?t.removeAttribute(e):t.setAttribute(e,n)}function ua(t,e,n,r){r==null?t.removeAttributeNS(e,n):t.setAttributeNS(e,n,r)}function li(t,e){e==null?t.removeAttribute("class"):t.className=e}function rn(t,e,n,r){if(r)Array.isArray(n)?(t[`$$${e}`]=n[0],t[`$$${e}Data`]=n[1]):t[`$$${e}`]=n;else if(Array.isArray(n)){const s=n[0];t.addEventListener(e,n[0]=i=>s.call(t,n[1],i))}else t.addEventListener(e,n)}function Pt(t,e,n={}){const r=Object.keys(e||{}),s=Object.keys(n);let i,o;for(i=0,o=s.length;i<o;i++){const a=s[i];!a||a==="undefined"||e[a]||(Qr(t,a,!1),delete n[a])}for(i=0,o=r.length;i<o;i++){const a=r[i],l=!!e[a];!a||a==="undefined"||n[a]===l||!l||(Qr(t,a,!0),n[a]=l)}return n}function ci(t,e,n){if(!e)return n?q(t,"style"):e;const r=t.style;if(typeof e=="string")return r.cssText=e;typeof n=="string"&&(r.cssText=n=void 0),n||(n={}),e||(e={});let s,i;for(i in n)e[i]==null&&r.removeProperty(i),delete n[i];for(i in e)s=e[i],s!==n[i]&&(r.setProperty(i,s),n[i]=s);return n}function da(t,e={},n,r){const s={};return r||$(()=>s.children=qe(t,e.children,s.children)),$(()=>e.ref&&e.ref(t)),$(()=>fa(t,e,n,!0,s,!0)),s}function d(t,e,n,r){if(n!==void 0&&!r&&(r=[]),typeof e!="function")return qe(t,e,r,n);$(s=>qe(t,e(),s,n),r)}function fa(t,e,n,r,s={},i=!1){e||(e={});for(const o in s)if(!(o in e)){if(o==="children")continue;s[o]=Zr(t,o,null,s[o],n,i)}for(const o in e){if(o==="children"){r||qe(t,e.children);continue}const a=e[o];s[o]=Zr(t,o,a,s[o],n,i)}}function ha(t){return t.toLowerCase().replace(/-([a-z])/g,(e,n)=>n.toUpperCase())}function Qr(t,e,n){const r=e.trim().split(/\s+/);for(let s=0,i=r.length;s<i;s++)t.classList.toggle(r[s],n)}function Zr(t,e,n,r,s,i){let o,a,l;if(e==="style")return ci(t,n,r);if(e==="classList")return Pt(t,n,r);if(n===r)return r;if(e==="ref")i||n(t);else if(e.slice(0,3)==="on:"){const c=e.slice(3);r&&t.removeEventListener(c,r),n&&t.addEventListener(c,n)}else if(e.slice(0,10)==="oncapture:"){const c=e.slice(10);r&&t.removeEventListener(c,r,!0),n&&t.addEventListener(c,n,!0)}else if(e.slice(0,2)==="on"){const c=e.slice(2).toLowerCase(),u=oa.has(c);if(!u&&r){const v=Array.isArray(r)?r[0]:r;t.removeEventListener(c,v)}(u||n)&&(rn(t,c,n,u),u&&R([c]))}else if((l=sa.has(e))||!s&&(Xr[e]||(a=ra.has(e)))||(o=t.nodeName.includes("-")))e==="class"||e==="className"?li(t,n):o&&!a&&!l?t[ha(e)]=n:t[Xr[e]||e]=n;else{const c=s&&e.indexOf(":")>-1&&aa[e.split(":")[0]];c?ua(t,c,e,n):q(t,ia[e]||e,n)}return n}function ga(t){const e=`$$${t.type}`;let n=t.composedPath&&t.composedPath()[0]||t.target;for(t.target!==n&&Object.defineProperty(t,"target",{configurable:!0,value:n}),Object.defineProperty(t,"currentTarget",{configurable:!0,get(){return n||document}}),J.registry&&!J.done&&(J.done=!0,document.querySelectorAll("[id^=pl-]").forEach(r=>r.remove()));n!==null;){const r=n[e];if(r&&!n.disabled){const s=n[`${e}Data`];if(s!==void 0?r.call(n,s,t):r.call(n,t),t.cancelBubble)return}n=n.host&&n.host!==n&&n.host instanceof Node?n.host:n.parentNode}}function qe(t,e,n,r,s){for(J.context&&!n&&(n=[...t.childNodes]);typeof n=="function";)n=n();if(e===n)return n;const i=typeof e,o=r!==void 0;if(t=o&&n[0]&&n[0].parentNode||t,i==="string"||i==="number"){if(J.context)return n;if(i==="number"&&(e=e.toString()),o){let a=n[0];a&&a.nodeType===3?a.data=e:a=document.createTextNode(e),n=ze(t,n,r,a)}else n!==""&&typeof n=="string"?n=t.firstChild.data=e:n=t.textContent=e}else if(e==null||i==="boolean"){if(J.context)return n;n=ze(t,n,r)}else{if(i==="function")return $(()=>{let a=e();for(;typeof a=="function";)a=a();n=qe(t,a,n,r)}),()=>n;if(Array.isArray(e)){const a=[],l=n&&Array.isArray(n);if(Kn(a,e,n,s))return $(()=>n=qe(t,a,n,r,!0)),()=>n;if(J.context){if(!a.length)return n;for(let c=0;c<a.length;c++)if(a[c].parentNode)return n=a}if(a.length===0){if(n=ze(t,n,r),o)return n}else l?n.length===0?es(t,a,r):la(t,n,a):(n&&ze(t),es(t,a));n=a}else if(e instanceof Node){if(J.context&&e.parentNode)return n=o?[e]:e;if(Array.isArray(n)){if(o)return n=ze(t,n,r,e);ze(t,n,null,e)}else n==null||n===""||!t.firstChild?t.appendChild(e):t.replaceChild(e,t.firstChild);n=e}}return n}function Kn(t,e,n,r){let s=!1;for(let i=0,o=e.length;i<o;i++){let a=e[i],l=n&&n[i];if(a instanceof Node)t.push(a);else if(!(a==null||a===!0||a===!1))if(Array.isArray(a))s=Kn(t,a,l)||s;else if(typeof a=="function")if(r){for(;typeof a=="function";)a=a();s=Kn(t,Array.isArray(a)?a:[a],Array.isArray(l)?l:[l])||s}else t.push(a),s=!0;else{const c=String(a);l&&l.nodeType===3&&l.data===c?t.push(l):t.push(document.createTextNode(c))}}return s}function es(t,e,n=null){for(let r=0,s=e.length;r<s;r++)t.insertBefore(e[r],n)}function ze(t,e,n,r){if(n===void 0)return t.textContent="";const s=r||document.createTextNode("");if(e.length){let i=!1;for(let o=e.length-1;o>=0;o--){const a=e[o];if(s!==a){const l=a.parentNode===t;!i&&!o?l?t.replaceChild(s,a):t.insertBefore(s,n):l&&a.remove()}else i=!0}}else t.insertBefore(s,n);return[s]}const ma=!1,pa="http://www.w3.org/2000/svg";function ba(t,e=!1){return e?document.createElementNS(pa,t):document.createElement(t)}function va(t){const{useShadow:e}=t,n=document.createTextNode(""),r=t.mount||document.body;function s(){if(J.context){const[i,o]=_(!1);return queueMicrotask(()=>o(!0)),()=>i()&&t.children}else return()=>t.children}if(r instanceof HTMLHeadElement){const[i,o]=_(!1),a=()=>o(!0);Q(l=>d(r,()=>i()?l():s()(),null)),Vt(()=>{J.context?queueMicrotask(a):a()})}else{const i=ba(t.isSVG?"g":"div",t.isSVG),o=e&&i.attachShadow?i.attachShadow({mode:"open"}):i;Object.defineProperty(i,"host",{get(){return n.parentNode},configurable:!0}),d(o,s()),r.appendChild(i),t.ref&&t.ref(i),Vt(()=>r.removeChild(i))}return n}function ui(t,e){return function(){return t.apply(e,arguments)}}const{toString:di}=Object.prototype,{getPrototypeOf:fr}=Object,hr=(t=>e=>{const n=di.call(e);return t[n]||(t[n]=n.slice(8,-1).toLowerCase())})(Object.create(null)),ve=t=>(t=t.toLowerCase(),e=>hr(e)===t),sn=t=>e=>typeof e===t,{isArray:_t}=Array,Xn=sn("undefined");function ya(t){return t!==null&&!Xn(t)&&t.constructor!==null&&!Xn(t.constructor)&&Ye(t.constructor.isBuffer)&&t.constructor.isBuffer(t)}const fi=ve("ArrayBuffer");function _a(t){let e;return typeof ArrayBuffer<"u"&&ArrayBuffer.isView?e=ArrayBuffer.isView(t):e=t&&t.buffer&&fi(t.buffer),e}const wa=sn("string"),Ye=sn("function"),hi=sn("number"),gi=t=>t!==null&&typeof t=="object",xa=t=>t===!0||t===!1,Lt=t=>{if(hr(t)!=="object")return!1;const e=fr(t);return(e===null||e===Object.prototype||Object.getPrototypeOf(e)===null)&&!(Symbol.toStringTag in t)&&!(Symbol.iterator in t)},Ea=ve("Date"),Ia=ve("File"),Sa=ve("Blob"),$a=ve("FileList"),ka=t=>gi(t)&&Ye(t.pipe),Ta=t=>{const e="[object FormData]";return t&&(typeof FormData=="function"&&t instanceof FormData||di.call(t)===e||Ye(t.toString)&&t.toString()===e)},Ca=ve("URLSearchParams"),Aa=t=>t.trim?t.trim():t.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g,"");function on(t,e,{allOwnKeys:n=!1}={}){if(t===null||typeof t>"u")return;let r,s;if(typeof t!="object"&&(t=[t]),_t(t))for(r=0,s=t.length;r<s;r++)e.call(null,t[r],r,t);else{const i=n?Object.getOwnPropertyNames(t):Object.keys(t),o=i.length;let a;for(r=0;r<o;r++)a=i[r],e.call(null,t[a],a,t)}}function Yn(){const t={},e=(n,r)=>{Lt(t[r])&&Lt(n)?t[r]=Yn(t[r],n):Lt(n)?t[r]=Yn({},n):_t(n)?t[r]=n.slice():t[r]=n};for(let n=0,r=arguments.length;n<r;n++)arguments[n]&&on(arguments[n],e);return t}const Oa=(t,e,n,{allOwnKeys:r}={})=>(on(e,(s,i)=>{n&&Ye(s)?t[i]=ui(s,n):t[i]=s},{allOwnKeys:r}),t),Na=t=>(t.charCodeAt(0)===65279&&(t=t.slice(1)),t),Ra=(t,e,n,r)=>{t.prototype=Object.create(e.prototype,r),t.prototype.constructor=t,Object.defineProperty(t,"super",{value:e.prototype}),n&&Object.assign(t.prototype,n)},Da=(t,e,n,r)=>{let s,i,o;const a={};if(e=e||{},t==null)return e;do{for(s=Object.getOwnPropertyNames(t),i=s.length;i-- >0;)o=s[i],(!r||r(o,t,e))&&!a[o]&&(e[o]=t[o],a[o]=!0);t=n!==!1&&fr(t)}while(t&&(!n||n(t,e))&&t!==Object.prototype);return e},Pa=(t,e,n)=>{t=String(t),(n===void 0||n>t.length)&&(n=t.length),n-=e.length;const r=t.indexOf(e,n);return r!==-1&&r===n},La=t=>{if(!t)return null;if(_t(t))return t;let e=t.length;if(!hi(e))return null;const n=new Array(e);for(;e-- >0;)n[e]=t[e];return n},Ma=(t=>e=>t&&e instanceof t)(typeof Uint8Array<"u"&&fr(Uint8Array)),Ua=(t,e)=>{const r=(t&&t[Symbol.iterator]).call(t);let s;for(;(s=r.next())&&!s.done;){const i=s.value;e.call(t,i[0],i[1])}},ja=(t,e)=>{let n;const r=[];for(;(n=t.exec(e))!==null;)r.push(n);return r},Fa=ve("HTMLFormElement"),Ba=t=>t.toLowerCase().replace(/[_-\s]([a-z\d])(\w*)/g,function(n,r,s){return r.toUpperCase()+s}),ts=(({hasOwnProperty:t})=>(e,n)=>t.call(e,n))(Object.prototype),Ha=ve("RegExp"),mi=(t,e)=>{const n=Object.getOwnPropertyDescriptors(t),r={};on(n,(s,i)=>{e(s,i,t)!==!1&&(r[i]=s)}),Object.defineProperties(t,r)},za=t=>{mi(t,(e,n)=>{const r=t[n];if(!!Ye(r)){if(e.enumerable=!1,"writable"in e){e.writable=!1;return}e.set||(e.set=()=>{throw Error("Can not read-only method '"+n+"'")})}})},Va=(t,e)=>{const n={},r=s=>{s.forEach(i=>{n[i]=!0})};return _t(t)?r(t):r(String(t).split(e)),n},Wa=()=>{},Ja=(t,e)=>(t=+t,Number.isFinite(t)?t:e),h={isArray:_t,isArrayBuffer:fi,isBuffer:ya,isFormData:Ta,isArrayBufferView:_a,isString:wa,isNumber:hi,isBoolean:xa,isObject:gi,isPlainObject:Lt,isUndefined:Xn,isDate:Ea,isFile:Ia,isBlob:Sa,isRegExp:Ha,isFunction:Ye,isStream:ka,isURLSearchParams:Ca,isTypedArray:Ma,isFileList:$a,forEach:on,merge:Yn,extend:Oa,trim:Aa,stripBOM:Na,inherits:Ra,toFlatObject:Da,kindOf:hr,kindOfTest:ve,endsWith:Pa,toArray:La,forEachEntry:Ua,matchAll:ja,isHTMLForm:Fa,hasOwnProperty:ts,hasOwnProp:ts,reduceDescriptors:mi,freezeMethods:za,toObjectSet:Va,toCamelCase:Ba,noop:Wa,toFiniteNumber:Ja};function O(t,e,n,r,s){Error.call(this),Error.captureStackTrace?Error.captureStackTrace(this,this.constructor):this.stack=new Error().stack,this.message=t,this.name="AxiosError",e&&(this.code=e),n&&(this.config=n),r&&(this.request=r),s&&(this.response=s)}h.inherits(O,Error,{toJSON:function(){return{message:this.message,name:this.name,description:this.description,number:this.number,fileName:this.fileName,lineNumber:this.lineNumber,columnNumber:this.columnNumber,stack:this.stack,config:this.config,code:this.code,status:this.response&&this.response.status?this.response.status:null}}});const pi=O.prototype,bi={};["ERR_BAD_OPTION_VALUE","ERR_BAD_OPTION","ECONNABORTED","ETIMEDOUT","ERR_NETWORK","ERR_FR_TOO_MANY_REDIRECTS","ERR_DEPRECATED","ERR_BAD_RESPONSE","ERR_BAD_REQUEST","ERR_CANCELED","ERR_NOT_SUPPORT","ERR_INVALID_URL"].forEach(t=>{bi[t]={value:t}});Object.defineProperties(O,bi);Object.defineProperty(pi,"isAxiosError",{value:!0});O.from=(t,e,n,r,s,i)=>{const o=Object.create(pi);return h.toFlatObject(t,o,function(l){return l!==Error.prototype},a=>a!=="isAxiosError"),O.call(o,t.message,e,n,r,s),o.cause=t,o.name=t.name,i&&Object.assign(o,i),o};var qa=typeof self=="object"?self.FormData:window.FormData;function Qn(t){return h.isPlainObject(t)||h.isArray(t)}function vi(t){return h.endsWith(t,"[]")?t.slice(0,-2):t}function ns(t,e,n){return t?t.concat(e).map(function(s,i){return s=vi(s),!n&&i?"["+s+"]":s}).join(n?".":""):e}function Ga(t){return h.isArray(t)&&!t.some(Qn)}const Ka=h.toFlatObject(h,{},null,function(e){return/^is[A-Z]/.test(e)});function Xa(t){return t&&h.isFunction(t.append)&&t[Symbol.toStringTag]==="FormData"&&t[Symbol.iterator]}function an(t,e,n){if(!h.isObject(t))throw new TypeError("target must be an object");e=e||new(qa||FormData),n=h.toFlatObject(n,{metaTokens:!0,dots:!1,indexes:!1},!1,function(p,w){return!h.isUndefined(w[p])});const r=n.metaTokens,s=n.visitor||u,i=n.dots,o=n.indexes,l=(n.Blob||typeof Blob<"u"&&Blob)&&Xa(e);if(!h.isFunction(s))throw new TypeError("visitor must be a function");function c(m){if(m===null)return"";if(h.isDate(m))return m.toISOString();if(!l&&h.isBlob(m))throw new O("Blob is not supported. Use a Buffer instead.");return h.isArrayBuffer(m)||h.isTypedArray(m)?l&&typeof Blob=="function"?new Blob([m]):Buffer.from(m):m}function u(m,p,w){let x=m;if(m&&!w&&typeof m=="object"){if(h.endsWith(p,"{}"))p=r?p:p.slice(0,-2),m=JSON.stringify(m);else if(h.isArray(m)&&Ga(m)||h.isFileList(m)||h.endsWith(p,"[]")&&(x=h.toArray(m)))return p=vi(p),x.forEach(function(C,D){!(h.isUndefined(C)||C===null)&&e.append(o===!0?ns([p],D,i):o===null?p:p+"[]",c(C))}),!1}return Qn(m)?!0:(e.append(ns(w,p,i),c(m)),!1)}const v=[],g=Object.assign(Ka,{defaultVisitor:u,convertValue:c,isVisitable:Qn});function b(m,p){if(!h.isUndefined(m)){if(v.indexOf(m)!==-1)throw Error("Circular reference detected in "+p.join("."));v.push(m),h.forEach(m,function(x,S){(!(h.isUndefined(x)||x===null)&&s.call(e,x,h.isString(S)?S.trim():S,p,g))===!0&&b(x,p?p.concat(S):[S])}),v.pop()}}if(!h.isObject(t))throw new TypeError("data must be an object");return b(t),e}function rs(t){const e={"!":"%21","'":"%27","(":"%28",")":"%29","~":"%7E","%20":"+","%00":"\0"};return encodeURIComponent(t).replace(/[!'()~]|%20|%00/g,function(r){return e[r]})}function gr(t,e){this._pairs=[],t&&an(t,this,e)}const yi=gr.prototype;yi.append=function(e,n){this._pairs.push([e,n])};yi.toString=function(e){const n=e?function(r){return e.call(this,r,rs)}:rs;return this._pairs.map(function(s){return n(s[0])+"="+n(s[1])},"").join("&")};function Ya(t){return encodeURIComponent(t).replace(/%3A/gi,":").replace(/%24/g,"$").replace(/%2C/gi,",").replace(/%20/g,"+").replace(/%5B/gi,"[").replace(/%5D/gi,"]")}function _i(t,e,n){if(!e)return t;const r=n&&n.encode||Ya,s=n&&n.serialize;let i;if(s?i=s(e,n):i=h.isURLSearchParams(e)?e.toString():new gr(e,n).toString(r),i){const o=t.indexOf("#");o!==-1&&(t=t.slice(0,o)),t+=(t.indexOf("?")===-1?"?":"&")+i}return t}class ss{constructor(){this.handlers=[]}use(e,n,r){return this.handlers.push({fulfilled:e,rejected:n,synchronous:r?r.synchronous:!1,runWhen:r?r.runWhen:null}),this.handlers.length-1}eject(e){this.handlers[e]&&(this.handlers[e]=null)}clear(){this.handlers&&(this.handlers=[])}forEach(e){h.forEach(this.handlers,function(r){r!==null&&e(r)})}}const wi={silentJSONParsing:!0,forcedJSONParsing:!0,clarifyTimeoutError:!1},Qa=typeof URLSearchParams<"u"?URLSearchParams:gr,Za=FormData,el=(()=>{let t;return typeof navigator<"u"&&((t=navigator.product)==="ReactNative"||t==="NativeScript"||t==="NS")?!1:typeof window<"u"&&typeof document<"u"})(),fe={isBrowser:!0,classes:{URLSearchParams:Qa,FormData:Za,Blob},isStandardBrowserEnv:el,protocols:["http","https","file","blob","url","data"]};function tl(t,e){return an(t,new fe.classes.URLSearchParams,Object.assign({visitor:function(n,r,s,i){return fe.isNode&&h.isBuffer(n)?(this.append(r,n.toString("base64")),!1):i.defaultVisitor.apply(this,arguments)}},e))}function nl(t){return h.matchAll(/\w+|\[(\w*)]/g,t).map(e=>e[0]==="[]"?"":e[1]||e[0])}function rl(t){const e={},n=Object.keys(t);let r;const s=n.length;let i;for(r=0;r<s;r++)i=n[r],e[i]=t[i];return e}function xi(t){function e(n,r,s,i){let o=n[i++];const a=Number.isFinite(+o),l=i>=n.length;return o=!o&&h.isArray(s)?s.length:o,l?(h.hasOwnProp(s,o)?s[o]=[s[o],r]:s[o]=r,!a):((!s[o]||!h.isObject(s[o]))&&(s[o]=[]),e(n,r,s[o],i)&&h.isArray(s[o])&&(s[o]=rl(s[o])),!a)}if(h.isFormData(t)&&h.isFunction(t.entries)){const n={};return h.forEachEntry(t,(r,s)=>{e(nl(r),s,n,0)}),n}return null}function sl(t,e,n){const r=n.config.validateStatus;!n.status||!r||r(n.status)?t(n):e(new O("Request failed with status code "+n.status,[O.ERR_BAD_REQUEST,O.ERR_BAD_RESPONSE][Math.floor(n.status/100)-4],n.config,n.request,n))}const il=fe.isStandardBrowserEnv?function(){return{write:function(n,r,s,i,o,a){const l=[];l.push(n+"="+encodeURIComponent(r)),h.isNumber(s)&&l.push("expires="+new Date(s).toGMTString()),h.isString(i)&&l.push("path="+i),h.isString(o)&&l.push("domain="+o),a===!0&&l.push("secure"),document.cookie=l.join("; ")},read:function(n){const r=document.cookie.match(new RegExp("(^|;\\s*)("+n+")=([^;]*)"));return r?decodeURIComponent(r[3]):null},remove:function(n){this.write(n,"",Date.now()-864e5)}}}():function(){return{write:function(){},read:function(){return null},remove:function(){}}}();function ol(t){return/^([a-z][a-z\d+\-.]*:)?\/\//i.test(t)}function al(t,e){return e?t.replace(/\/+$/,"")+"/"+e.replace(/^\/+/,""):t}function Ei(t,e){return t&&!ol(e)?al(t,e):e}const ll=fe.isStandardBrowserEnv?function(){const e=/(msie|trident)/i.test(navigator.userAgent),n=document.createElement("a");let r;function s(i){let o=i;return e&&(n.setAttribute("href",o),o=n.href),n.setAttribute("href",o),{href:n.href,protocol:n.protocol?n.protocol.replace(/:$/,""):"",host:n.host,search:n.search?n.search.replace(/^\?/,""):"",hash:n.hash?n.hash.replace(/^#/,""):"",hostname:n.hostname,port:n.port,pathname:n.pathname.charAt(0)==="/"?n.pathname:"/"+n.pathname}}return r=s(window.location.href),function(o){const a=h.isString(o)?s(o):o;return a.protocol===r.protocol&&a.host===r.host}}():function(){return function(){return!0}}();function wt(t,e,n){O.call(this,t??"canceled",O.ERR_CANCELED,e,n),this.name="CanceledError"}h.inherits(wt,O,{__CANCEL__:!0});function cl(t){const e=/^([-+\w]{1,25})(:?\/\/|:)/.exec(t);return e&&e[1]||""}const ul=h.toObjectSet(["age","authorization","content-length","content-type","etag","expires","from","host","if-modified-since","if-unmodified-since","last-modified","location","max-forwards","proxy-authorization","referer","retry-after","user-agent"]),dl=t=>{const e={};let n,r,s;return t&&t.split(`
`).forEach(function(o){s=o.indexOf(":"),n=o.substring(0,s).trim().toLowerCase(),r=o.substring(s+1).trim(),!(!n||e[n]&&ul[n])&&(n==="set-cookie"?e[n]?e[n].push(r):e[n]=[r]:e[n]=e[n]?e[n]+", "+r:r)}),e},is=Symbol("internals"),Ii=Symbol("defaults");function at(t){return t&&String(t).trim().toLowerCase()}function Mt(t){return t===!1||t==null?t:h.isArray(t)?t.map(Mt):String(t)}function fl(t){const e=Object.create(null),n=/([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;let r;for(;r=n.exec(t);)e[r[1]]=r[2];return e}function os(t,e,n,r){if(h.isFunction(r))return r.call(this,e,n);if(!!h.isString(e)){if(h.isString(r))return e.indexOf(r)!==-1;if(h.isRegExp(r))return r.test(e)}}function hl(t){return t.trim().toLowerCase().replace(/([a-z\d])(\w*)/g,(e,n,r)=>n.toUpperCase()+r)}function gl(t,e){const n=h.toCamelCase(" "+e);["get","set","has"].forEach(r=>{Object.defineProperty(t,r+n,{value:function(s,i,o){return this[r].call(this,e,s,i,o)},configurable:!0})})}function it(t,e){e=e.toLowerCase();const n=Object.keys(t);let r=n.length,s;for(;r-- >0;)if(s=n[r],e===s.toLowerCase())return s;return null}function ne(t,e){t&&this.set(t),this[Ii]=e||null}Object.assign(ne.prototype,{set:function(t,e,n){const r=this;function s(i,o,a){const l=at(o);if(!l)throw new Error("header name must be a non-empty string");const c=it(r,l);c&&a!==!0&&(r[c]===!1||a===!1)||(r[c||o]=Mt(i))}return h.isPlainObject(t)?h.forEach(t,(i,o)=>{s(i,o,e)}):s(e,t,n),this},get:function(t,e){if(t=at(t),!t)return;const n=it(this,t);if(n){const r=this[n];if(!e)return r;if(e===!0)return fl(r);if(h.isFunction(e))return e.call(this,r,n);if(h.isRegExp(e))return e.exec(r);throw new TypeError("parser must be boolean|regexp|function")}},has:function(t,e){if(t=at(t),t){const n=it(this,t);return!!(n&&(!e||os(this,this[n],n,e)))}return!1},delete:function(t,e){const n=this;let r=!1;function s(i){if(i=at(i),i){const o=it(n,i);o&&(!e||os(n,n[o],o,e))&&(delete n[o],r=!0)}}return h.isArray(t)?t.forEach(s):s(t),r},clear:function(){return Object.keys(this).forEach(this.delete.bind(this))},normalize:function(t){const e=this,n={};return h.forEach(this,(r,s)=>{const i=it(n,s);if(i){e[i]=Mt(r),delete e[s];return}const o=t?hl(s):String(s).trim();o!==s&&delete e[s],e[o]=Mt(r),n[o]=!0}),this},toJSON:function(t){const e=Object.create(null);return h.forEach(Object.assign({},this[Ii]||null,this),(n,r)=>{n==null||n===!1||(e[r]=t&&h.isArray(n)?n.join(", "):n)}),e}});Object.assign(ne,{from:function(t){return h.isString(t)?new this(dl(t)):t instanceof this?t:new this(t)},accessor:function(t){const n=(this[is]=this[is]={accessors:{}}).accessors,r=this.prototype;function s(i){const o=at(i);n[o]||(gl(r,i),n[o]=!0)}return h.isArray(t)?t.forEach(s):s(t),this}});ne.accessor(["Content-Type","Content-Length","Accept","Accept-Encoding","User-Agent"]);h.freezeMethods(ne.prototype);h.freezeMethods(ne);function ml(t,e){t=t||10;const n=new Array(t),r=new Array(t);let s=0,i=0,o;return e=e!==void 0?e:1e3,function(l){const c=Date.now(),u=r[i];o||(o=c),n[s]=l,r[s]=c;let v=i,g=0;for(;v!==s;)g+=n[v++],v=v%t;if(s=(s+1)%t,s===i&&(i=(i+1)%t),c-o<e)return;const b=u&&c-u;return b?Math.round(g*1e3/b):void 0}}function as(t,e){let n=0;const r=ml(50,250);return s=>{const i=s.loaded,o=s.lengthComputable?s.total:void 0,a=i-n,l=r(a),c=i<=o;n=i;const u={loaded:i,total:o,progress:o?i/o:void 0,bytes:a,rate:l||void 0,estimated:l&&o&&c?(o-i)/l:void 0};u[e?"download":"upload"]=!0,t(u)}}function ls(t){return new Promise(function(n,r){let s=t.data;const i=ne.from(t.headers).normalize(),o=t.responseType;let a;function l(){t.cancelToken&&t.cancelToken.unsubscribe(a),t.signal&&t.signal.removeEventListener("abort",a)}h.isFormData(s)&&fe.isStandardBrowserEnv&&i.setContentType(!1);let c=new XMLHttpRequest;if(t.auth){const b=t.auth.username||"",m=t.auth.password?unescape(encodeURIComponent(t.auth.password)):"";i.set("Authorization","Basic "+btoa(b+":"+m))}const u=Ei(t.baseURL,t.url);c.open(t.method.toUpperCase(),_i(u,t.params,t.paramsSerializer),!0),c.timeout=t.timeout;function v(){if(!c)return;const b=ne.from("getAllResponseHeaders"in c&&c.getAllResponseHeaders()),p={data:!o||o==="text"||o==="json"?c.responseText:c.response,status:c.status,statusText:c.statusText,headers:b,config:t,request:c};sl(function(x){n(x),l()},function(x){r(x),l()},p),c=null}if("onloadend"in c?c.onloadend=v:c.onreadystatechange=function(){!c||c.readyState!==4||c.status===0&&!(c.responseURL&&c.responseURL.indexOf("file:")===0)||setTimeout(v)},c.onabort=function(){!c||(r(new O("Request aborted",O.ECONNABORTED,t,c)),c=null)},c.onerror=function(){r(new O("Network Error",O.ERR_NETWORK,t,c)),c=null},c.ontimeout=function(){let m=t.timeout?"timeout of "+t.timeout+"ms exceeded":"timeout exceeded";const p=t.transitional||wi;t.timeoutErrorMessage&&(m=t.timeoutErrorMessage),r(new O(m,p.clarifyTimeoutError?O.ETIMEDOUT:O.ECONNABORTED,t,c)),c=null},fe.isStandardBrowserEnv){const b=(t.withCredentials||ll(u))&&t.xsrfCookieName&&il.read(t.xsrfCookieName);b&&i.set(t.xsrfHeaderName,b)}s===void 0&&i.setContentType(null),"setRequestHeader"in c&&h.forEach(i.toJSON(),function(m,p){c.setRequestHeader(p,m)}),h.isUndefined(t.withCredentials)||(c.withCredentials=!!t.withCredentials),o&&o!=="json"&&(c.responseType=t.responseType),typeof t.onDownloadProgress=="function"&&c.addEventListener("progress",as(t.onDownloadProgress,!0)),typeof t.onUploadProgress=="function"&&c.upload&&c.upload.addEventListener("progress",as(t.onUploadProgress)),(t.cancelToken||t.signal)&&(a=b=>{!c||(r(!b||b.type?new wt(null,t,c):b),c.abort(),c=null)},t.cancelToken&&t.cancelToken.subscribe(a),t.signal&&(t.signal.aborted?a():t.signal.addEventListener("abort",a)));const g=cl(u);if(g&&fe.protocols.indexOf(g)===-1){r(new O("Unsupported protocol "+g+":",O.ERR_BAD_REQUEST,t));return}c.send(s||null)})}const cs={http:ls,xhr:ls},us={getAdapter:t=>{if(h.isString(t)){const e=cs[t];if(!t)throw Error(h.hasOwnProp(t)?`Adapter '${t}' is not available in the build`:`Can not resolve adapter '${t}'`);return e}if(!h.isFunction(t))throw new TypeError("adapter is not a function");return t},adapters:cs},pl={"Content-Type":"application/x-www-form-urlencoded"};function bl(){let t;return typeof XMLHttpRequest<"u"?t=us.getAdapter("xhr"):typeof process<"u"&&h.kindOf(process)==="process"&&(t=us.getAdapter("http")),t}function vl(t,e,n){if(h.isString(t))try{return(e||JSON.parse)(t),h.trim(t)}catch(r){if(r.name!=="SyntaxError")throw r}return(n||JSON.stringify)(t)}const Qe={transitional:wi,adapter:bl(),transformRequest:[function(e,n){const r=n.getContentType()||"",s=r.indexOf("application/json")>-1,i=h.isObject(e);if(i&&h.isHTMLForm(e)&&(e=new FormData(e)),h.isFormData(e))return s&&s?JSON.stringify(xi(e)):e;if(h.isArrayBuffer(e)||h.isBuffer(e)||h.isStream(e)||h.isFile(e)||h.isBlob(e))return e;if(h.isArrayBufferView(e))return e.buffer;if(h.isURLSearchParams(e))return n.setContentType("application/x-www-form-urlencoded;charset=utf-8",!1),e.toString();let a;if(i){if(r.indexOf("application/x-www-form-urlencoded")>-1)return tl(e,this.formSerializer).toString();if((a=h.isFileList(e))||r.indexOf("multipart/form-data")>-1){const l=this.env&&this.env.FormData;return an(a?{"files[]":e}:e,l&&new l,this.formSerializer)}}return i||s?(n.setContentType("application/json",!1),vl(e)):e}],transformResponse:[function(e){const n=this.transitional||Qe.transitional,r=n&&n.forcedJSONParsing,s=this.responseType==="json";if(e&&h.isString(e)&&(r&&!this.responseType||s)){const o=!(n&&n.silentJSONParsing)&&s;try{return JSON.parse(e)}catch(a){if(o)throw a.name==="SyntaxError"?O.from(a,O.ERR_BAD_RESPONSE,this,null,this.response):a}}return e}],timeout:0,xsrfCookieName:"XSRF-TOKEN",xsrfHeaderName:"X-XSRF-TOKEN",maxContentLength:-1,maxBodyLength:-1,env:{FormData:fe.classes.FormData,Blob:fe.classes.Blob},validateStatus:function(e){return e>=200&&e<300},headers:{common:{Accept:"application/json, text/plain, */*"}}};h.forEach(["delete","get","head"],function(e){Qe.headers[e]={}});h.forEach(["post","put","patch"],function(e){Qe.headers[e]=h.merge(pl)});function Nn(t,e){const n=this||Qe,r=e||n,s=ne.from(r.headers);let i=r.data;return h.forEach(t,function(a){i=a.call(n,i,s.normalize(),e?e.status:void 0)}),s.normalize(),i}function Si(t){return!!(t&&t.__CANCEL__)}function Rn(t){if(t.cancelToken&&t.cancelToken.throwIfRequested(),t.signal&&t.signal.aborted)throw new wt}function ds(t){return Rn(t),t.headers=ne.from(t.headers),t.data=Nn.call(t,t.transformRequest),(t.adapter||Qe.adapter)(t).then(function(r){return Rn(t),r.data=Nn.call(t,t.transformResponse,r),r.headers=ne.from(r.headers),r},function(r){return Si(r)||(Rn(t),r&&r.response&&(r.response.data=Nn.call(t,t.transformResponse,r.response),r.response.headers=ne.from(r.response.headers))),Promise.reject(r)})}function ft(t,e){e=e||{};const n={};function r(c,u){return h.isPlainObject(c)&&h.isPlainObject(u)?h.merge(c,u):h.isPlainObject(u)?h.merge({},u):h.isArray(u)?u.slice():u}function s(c){if(h.isUndefined(e[c])){if(!h.isUndefined(t[c]))return r(void 0,t[c])}else return r(t[c],e[c])}function i(c){if(!h.isUndefined(e[c]))return r(void 0,e[c])}function o(c){if(h.isUndefined(e[c])){if(!h.isUndefined(t[c]))return r(void 0,t[c])}else return r(void 0,e[c])}function a(c){if(c in e)return r(t[c],e[c]);if(c in t)return r(void 0,t[c])}const l={url:i,method:i,data:i,baseURL:o,transformRequest:o,transformResponse:o,paramsSerializer:o,timeout:o,timeoutMessage:o,withCredentials:o,adapter:o,responseType:o,xsrfCookieName:o,xsrfHeaderName:o,onUploadProgress:o,onDownloadProgress:o,decompress:o,maxContentLength:o,maxBodyLength:o,beforeRedirect:o,transport:o,httpAgent:o,httpsAgent:o,cancelToken:o,socketPath:o,responseEncoding:o,validateStatus:a};return h.forEach(Object.keys(t).concat(Object.keys(e)),function(u){const v=l[u]||s,g=v(u);h.isUndefined(g)&&v!==a||(n[u]=g)}),n}const $i="1.1.3",mr={};["object","boolean","number","function","string","symbol"].forEach((t,e)=>{mr[t]=function(r){return typeof r===t||"a"+(e<1?"n ":" ")+t}});const fs={};mr.transitional=function(e,n,r){function s(i,o){return"[Axios v"+$i+"] Transitional option '"+i+"'"+o+(r?". "+r:"")}return(i,o,a)=>{if(e===!1)throw new O(s(o," has been removed"+(n?" in "+n:"")),O.ERR_DEPRECATED);return n&&!fs[o]&&(fs[o]=!0,console.warn(s(o," has been deprecated since v"+n+" and will be removed in the near future"))),e?e(i,o,a):!0}};function yl(t,e,n){if(typeof t!="object")throw new O("options must be an object",O.ERR_BAD_OPTION_VALUE);const r=Object.keys(t);let s=r.length;for(;s-- >0;){const i=r[s],o=e[i];if(o){const a=t[i],l=a===void 0||o(a,i,t);if(l!==!0)throw new O("option "+i+" must be "+l,O.ERR_BAD_OPTION_VALUE);continue}if(n!==!0)throw new O("Unknown option "+i,O.ERR_BAD_OPTION)}}const Zn={assertOptions:yl,validators:mr},we=Zn.validators;class Le{constructor(e){this.defaults=e,this.interceptors={request:new ss,response:new ss}}request(e,n){typeof e=="string"?(n=n||{},n.url=e):n=e||{},n=ft(this.defaults,n);const{transitional:r,paramsSerializer:s}=n;r!==void 0&&Zn.assertOptions(r,{silentJSONParsing:we.transitional(we.boolean),forcedJSONParsing:we.transitional(we.boolean),clarifyTimeoutError:we.transitional(we.boolean)},!1),s!==void 0&&Zn.assertOptions(s,{encode:we.function,serialize:we.function},!0),n.method=(n.method||this.defaults.method||"get").toLowerCase();const i=n.headers&&h.merge(n.headers.common,n.headers[n.method]);i&&h.forEach(["delete","get","head","post","put","patch","common"],function(m){delete n.headers[m]}),n.headers=new ne(n.headers,i);const o=[];let a=!0;this.interceptors.request.forEach(function(m){typeof m.runWhen=="function"&&m.runWhen(n)===!1||(a=a&&m.synchronous,o.unshift(m.fulfilled,m.rejected))});const l=[];this.interceptors.response.forEach(function(m){l.push(m.fulfilled,m.rejected)});let c,u=0,v;if(!a){const b=[ds.bind(this),void 0];for(b.unshift.apply(b,o),b.push.apply(b,l),v=b.length,c=Promise.resolve(n);u<v;)c=c.then(b[u++],b[u++]);return c}v=o.length;let g=n;for(u=0;u<v;){const b=o[u++],m=o[u++];try{g=b(g)}catch(p){m.call(this,p);break}}try{c=ds.call(this,g)}catch(b){return Promise.reject(b)}for(u=0,v=l.length;u<v;)c=c.then(l[u++],l[u++]);return c}getUri(e){e=ft(this.defaults,e);const n=Ei(e.baseURL,e.url);return _i(n,e.params,e.paramsSerializer)}}h.forEach(["delete","get","head","options"],function(e){Le.prototype[e]=function(n,r){return this.request(ft(r||{},{method:e,url:n,data:(r||{}).data}))}});h.forEach(["post","put","patch"],function(e){function n(r){return function(i,o,a){return this.request(ft(a||{},{method:e,headers:r?{"Content-Type":"multipart/form-data"}:{},url:i,data:o}))}}Le.prototype[e]=n(),Le.prototype[e+"Form"]=n(!0)});class pr{constructor(e){if(typeof e!="function")throw new TypeError("executor must be a function.");let n;this.promise=new Promise(function(i){n=i});const r=this;this.promise.then(s=>{if(!r._listeners)return;let i=r._listeners.length;for(;i-- >0;)r._listeners[i](s);r._listeners=null}),this.promise.then=s=>{let i;const o=new Promise(a=>{r.subscribe(a),i=a}).then(s);return o.cancel=function(){r.unsubscribe(i)},o},e(function(i,o,a){r.reason||(r.reason=new wt(i,o,a),n(r.reason))})}throwIfRequested(){if(this.reason)throw this.reason}subscribe(e){if(this.reason){e(this.reason);return}this._listeners?this._listeners.push(e):this._listeners=[e]}unsubscribe(e){if(!this._listeners)return;const n=this._listeners.indexOf(e);n!==-1&&this._listeners.splice(n,1)}static source(){let e;return{token:new pr(function(s){e=s}),cancel:e}}}function _l(t){return function(n){return t.apply(null,n)}}function wl(t){return h.isObject(t)&&t.isAxiosError===!0}function ki(t){const e=new Le(t),n=ui(Le.prototype.request,e);return h.extend(n,Le.prototype,e,{allOwnKeys:!0}),h.extend(n,e,null,{allOwnKeys:!0}),n.create=function(s){return ki(ft(t,s))},n}const j=ki(Qe);j.Axios=Le;j.CanceledError=wt;j.CancelToken=pr;j.isCancel=Si;j.VERSION=$i;j.toFormData=an;j.AxiosError=O;j.Cancel=j.CanceledError;j.all=function(e){return Promise.all(e)};j.spread=_l;j.isAxiosError=wl;j.formToJSON=t=>xi(h.isHTMLForm(t)?new FormData(t):t);const hs="http://0.0.0.0:3000",xl="http://0.0.0.0:8080",gs=window.location.origin;function El(){let t;gs==hs?t=xl:t="";const[e,n]=_(t),r=gs==hs;return{serverUrl:e,setServerUrl:n,withCredentials:r}}const ee=Q(El);function Il(){const[t,e]=_("submit");return{tabName:t,setTabName:e}}const Ze=Q(Il),Sl=y('<a id="tabhead_{props.tabName}" href="#" class="tabhead"></a>');function ln(t){const{tabName:e,setTabName:n}=Ze;return(()=>{const r=Sl.cloneNode(!0);return r.$$click=()=>n(t.tabName),d(r,()=>t.svg,null),d(r,()=>t.title,null),$(()=>r.classList.toggle("selected",e()==t.tabName)),r})()}R(["click"]);const $l=y('<svg fill="currentColor" stroke-width="0" xmlns="http://www.w3.org/2000/svg"></svg>'),kl=y("<title></title>");function te(t,e){const n=ta(t.a,e);return(()=>{const r=$l.cloneNode(!0);return da(r,n,!0,!0),d(r,()=>ma,null),d(r,(()=>{const s=ge(()=>!!e.title,!0);return()=>s()&&(()=>{const i=kl.cloneNode(!0);return d(i,()=>e.title),i})()})(),null),$(s=>{const i=t.a.stroke,o={...e.style,overflow:"visible",color:e.color||"currentColor"},a=e.size||"1em",l=e.size||"1em",c=t.c;return i!==s._v$&&q(r,"stroke",s._v$=i),s._v$2=ci(r,o,s._v$2),a!==s._v$3&&q(r,"height",s._v$3=a),l!==s._v$4&&q(r,"width",s._v$4=l),c!==s._v$5&&(r.innerHTML=s._v$5=c),s},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0}),r})()}function Tl(t){return te({a:{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",viewBox:"0 0 24 24"},c:'<path stroke="none" d="M0 0h24v24H0z"/><path d="M9 13L5 9l4-4M5 9h11a4 4 0 010 8h-1"/>'},t)}function Cl(t){return te({a:{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",viewBox:"0 0 24 24"},c:'<path stroke="none" d="M0 0h24v24H0z"/><path d="M14 3v4a1 1 0 001 1h4"/><path d="M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2zM12 11v6"/><path d="M9.5 13.5L12 11l2.5 2.5"/>'},t)}function Al(){const t=f(Cl,{class:"tabheadicon",color:"rgb(156 163 175)"});return f(ln,{tabName:"submit",title:"Submit",svg:t})}function Ol(t){return te({a:{viewBox:"0 0 1024 1024"},c:'<path d="M518.3 459a8 8 0 00-12.6 0l-112 141.7a7.98 7.98 0 006.3 12.9h73.9V856c0 4.4 3.6 8 8 8h60c4.4 0 8-3.6 8-8V613.7H624c6.7 0 10.4-7.7 6.3-12.9L518.3 459z"/><path d="M811.4 366.7C765.6 245.9 648.9 160 512.2 160S258.8 245.8 213 366.6C127.3 389.1 64 467.2 64 560c0 110.5 89.5 200 199.9 200H304c4.4 0 8-3.6 8-8v-60c0-4.4-3.6-8-8-8h-40.1c-33.7 0-65.4-13.4-89-37.7-23.5-24.2-36-56.8-34.9-90.6.9-26.4 9.9-51.2 26.2-72.1 16.7-21.3 40.1-36.8 66.1-43.7l37.9-9.9 13.9-36.6c8.6-22.8 20.6-44.1 35.7-63.4a245.6 245.6 0 0152.4-49.9c41.1-28.9 89.5-44.2 140-44.2s98.9 15.3 140 44.2c19.9 14 37.5 30.8 52.4 49.9 15.1 19.3 27.1 40.7 35.7 63.4l13.8 36.5 37.8 10C846.1 454.5 884 503.8 884 560c0 33.1-12.9 64.3-36.3 87.7a123.07 123.07 0 01-87.6 36.3H720c-4.4 0-8 3.6-8 8v60c0 4.4 3.6 8 8 8h40.1C870.5 760 960 670.5 960 560c0-92.7-63.1-170.7-148.6-193.3z"/>'},t)}function Nl(t){return te({a:{viewBox:"0 0 1024 1024"},c:'<path d="M920 760H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0-568H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0 284H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM216 712H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h72.4v20.5h-35.7c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h35.7V838H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4V716c0-2.2-1.8-4-4-4zM100 188h38v120c0 2.2 1.8 4 4 4h40c2.2 0 4-1.8 4-4V152c0-4.4-3.6-8-8-8h-78c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4zm116 240H100c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4h68.4l-70.3 77.7a8.3 8.3 0 00-2.1 5.4V592c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4v-36c0-2.2-1.8-4-4-4h-68.4l70.3-77.7a8.3 8.3 0 002.1-5.4V432c0-2.2-1.8-4-4-4z"/>'},t)}function Rl(){const t=f(Nl,{class:"tabheadicon",color:"rgb(156 163 175)"});return f(ln,{tabName:"jobs",title:"Jobs",svg:t})}const Dl=y('<svg class="tabheadicon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"></path></svg>');function Pl(){const t=Dl.cloneNode(!0);return f(ln,{tabName:"system",title:"System",svg:t})}function Ll(t){return te({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>'},t)}function Ml(t){return te({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>'},t)}function Ul(t){return te({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>'},t)}function br(t){return te({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>'},t)}function jl(t){return te({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>'},t)}function Fl(t){return te({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>'},t)}function Bl(t){return te({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>'},t)}function Hl(t){return te({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>'},t)}function zl(){const t=f(Hl,{class:"tabheadicon",color:"rgb(156 163 175)"});return f(ln,{tabName:"account",title:"Account",svg:t})}const Vl=y('<div id="verdiv" class="text-xs absolute left-4 bottom-2 text-gray-400"><span class="text-xs">v</span><span class="curverspan text-xs"></span></div>');function Wl(){return Vl.cloneNode(!0)}function Jl(){const[t,e]=_(!1);return{multiuser:t,setMultiuser:e}}const Ce=Q(Jl),ql=y('<div id="sidebar_static" class="md:flex md:w-36 md:flex-col md:fixed md:inset-y-0"><div class="flex-1 flex flex-col min-h-0 border-r border-gray-200"><div class="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto"><div class="flex items-center flex-shrink-0 px-4"><img class="h-16 w-auto" alt="Logo"></div><nav class="mt-5 flex-1 px-2 space-y-1"></nav></div></div></div>'),{serverUrl:Gl,setServerUrl:xm,withCredentials:Em}=ee,{multiuser:Kl,setMultiuser:Im}=Ce;function Xl(){return(()=>{const t=ql.cloneNode(!0),e=t.firstChild,n=e.firstChild,r=n.firstChild,s=r.firstChild,i=r.nextSibling;return d(i,f(Al,{}),null),d(i,f(Rl,{}),null),d(i,f(Pl,{}),null),d(i,f(Z,{get when(){return Kl()==!0},get children(){return f(zl,{})}}),null),d(n,f(Wl,{}),null),$(()=>q(s,"src",Gl()+"/submit/images/logo_transparent_bw.png")),t})()}function Yl(t){return te({a:{fill:"currentColor",viewBox:"0 0 16 16"},c:'<path d="M11.42 2l3.428 6-3.428 6H4.58L1.152 8 4.58 2h6.84zM4.58 1a1 1 0 00-.868.504l-3.428 6a1 1 0 000 .992l3.428 6A1 1 0 004.58 15h6.84a1 1 0 00.868-.504l3.429-6a1 1 0 000-.992l-3.429-6A1 1 0 0011.42 1H4.58z"/><path d="M6.848 5.933a2.5 2.5 0 102.5 4.33 2.5 2.5 0 00-2.5-4.33zm-1.78 3.915a3.5 3.5 0 116.061-3.5 3.5 3.5 0 01-6.062 3.5z"/>'},t)}async function Ti(t){const{serverUrl:e,setServerUrl:n}=ee;return(await fetch(e()+t)).json()}async function Ql(t){}function Zl(){const[t,e]=_({}),[n,r]=_({});function s(l){return l in t()?t()[l]:null}function i(l){var c=t();c[l.name]=l,e(c)}function o(){Ti("/store/local").then(function(l){e(l)})}function a(l){return l in n()?n()[l]:(Ql(),f(Yl,{}))}return{localModules:t,setLocalModules:e,getLocalModule:s,addLocalModule:i,loadAllModules:o,localModuleLogos:n,setLocalModuleLogos:r,getLocalModuleLogo:a}}const cn=Q(Zl),ec=y('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function Nt(t){function e(){t.setAssembly(t.value),t.setShow(!1)}return(()=>{const n=ec.cloneNode(!0);return n.$$click=e,d(n,()=>t.title),n})()}R(["click"]);const tc=y('<div id="assembly-select" class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabindex="-1"><div class="py-1" role="none"></div></div>');function nc(t){return(()=>{const e=tc.cloneNode(!0),n=e.firstChild;return d(n,f(Nt,{value:"auto",title:"Auto",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),d(n,f(Nt,{value:"hg38",title:"GRCh38/hg38",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),d(n,f(Nt,{value:"hg19",title:"GRCh37/hg19",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),d(n,f(Nt,{value:"hg18",title:"GRCh36/hg18",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),$(()=>e.classList.toggle("hidden",!t.show)),e})()}const rc=y('<div id="assembly-select-panel" class="select-div relative inline-block text-left" value=""><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="assembly-select-div" title="Genome assembly">Genome assembly: </button></div></div>');function sc(t){const[e,n]=_(!1),r={"":"Auto",hg38:"GRCh38/hg38",hg19:"GRCh37/hg19",hg18:"GRCh36/hg18"};function s(i){n(!e())}return(()=>{const i=rc.cloneNode(!0),o=i.firstChild,a=o.firstChild;return a.firstChild,a.$$click=s,d(a,()=>r[t.assembly],null),d(a,f(br,{class:"-mr-1 ml-2 h-5 w-5"}),null),d(i,f(nc,{get show(){return e()},get setAssembly(){return t.setAssembly},setShow:n}),null),i})()}R(["click"]);const ic=y('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function ms(t){function e(){t.setInputFormat(t.value),t.setShow(!1)}return(()=>{const n=ic.cloneNode(!0);return n.$$click=e,d(n,()=>t.title),n})()}R(["click"]);function oc(){const[t,e]=_(!1);return{logged:t,setLogged:e}}const Be=Q(oc),ac=y('<div id="input-format-select" class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabindex="-1"><div class="py-1" role="none"></div></div>'),{multiuser:lc,setMultiuser:Sm}=Ce,{logged:cc,setLogged:$m}=Be;async function uc(){if(lc()==!1||cc()==!0)return await Ti("/submit/converters")}function dc(t){const[e]=ur(uc);return Fe(()=>{var n={"":"Auto"};if(!!e()){for(var r=0;r<e().length;r++)n[e()[r].format]=e()[r].title;t.setInputFormats(n)}}),(()=>{const n=ac.cloneNode(!0),r=n.firstChild;return d(r,f(ms,{value:"",title:"Auto",get setInputFormat(){return t.setInputFormat},get setShow(){return t.setShow}}),null),d(r,f(be,{get each(){return e()},children:function(s){return f(ms,{get value(){return s.format},get title(){return s.title},get setInputFormat(){return t.setInputFormat},get setShow(){return t.setShow}})}}),null),$(()=>n.classList.toggle("hidden",!t.show)),n})()}const fc=y('<div id="input-format-select-panel" class="select-div relative inline-block text-left ml-6" value=""><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="input-format-select-div" title="Format">Format: </button></div></div>');function hc(t){const[e,n]=_(!1),[r,s]=_({"":"Auto"});function i(o){n(!e())}return(()=>{const o=fc.cloneNode(!0),a=o.firstChild,l=a.firstChild;return l.firstChild,l.$$click=i,d(l,()=>r()[t.inputFormat],null),d(l,f(br,{class:"-mr-1 ml-2 h-5 w-5"}),null),d(o,f(dc,{get show(){return e()},get setInputFormat(){return t.setInputFormat},setInputFormats:s,setShow:n}),null),o})()}R(["click"]);const gc=y('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100"><svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v3.75m-9.303 3.376C1.83 19.126 2.914 21 4.645 21h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 4.88c-.866-1.501-3.032-1.501-3.898 0L2.697 17.626zM12 17.25h.007v.008H12v-.008z"></path></svg></div><div class="mt-3 text-center sm:mt-5"><h3 class="text-lg font-medium leading-6 text-gray-900"></h3><div class="mt-2"><p class="text-sm text-gray-500"></p></div></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:text-sm">Dismiss</button></div></div></div></div></div>');function Ci(t){return(()=>{const e=gc.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,l=a.nextSibling,c=l.firstChild,u=c.nextSibling,v=u.firstChild,g=o.nextSibling,b=g.firstChild;return d(c,()=>t.title),d(v,()=>t.text),b.$$click=t.setShowDialog,b.$$clickData=!1,e})()}R(["click"]);const mc=y('<div id="input-upload-list-div" class="w-1/2 flex flex-col justify-center items-center p-2 relative h-full bg-gray-50"><button id="clear_inputfilelist_button" class="text-gray-500 bg-neutral-200 hover:bg-neutral-300 p-1 w-16 rounded-md absolute top-1 left-1" onclick="clearInputUploadList()">Clear</button><div id="input-upload-list-wrapper" class="flex w-full overflow-auto h-[13rem] absolute bottom-1 bg-gray-50"><div id="input-upload-list" class="h-full overflow-auto"></div></div></div>'),pc=y('<label id="input-drop-area" for="input-file" class="flex items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-md cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600"><div id="input-drop-box" class="w-1/2"><div class="flex flex-col items-center justify-center pt-5 pb-6"><p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> input files</p><p class="text-gray-500 mb-2"> or </p><button class="mb-2 text-sm text-gray-500 dark:text-gray-400 bg-neutral-200 hover:bg-neutral-300 p-2 rounded-md">Manually enter variants</button></div><input type="file" class="hidden" name="input-file" id="input-file" multiple></div></label>'),bc=y('<span class="pl-2 text-sm text-gray-600 hover:text-gray-400 cursor-pointer round-md inline-block w-5/6" title="Click to remove"></span>');function vc(t){const[e,n]=_(!1),[r,s]=_({title:"Problem",text:"?"});Fe(function(){});function i(a,l){l.preventDefault();for(var c=0;c<t.inputDataDrop.length;c++)if(t.inputDataDrop[c].name==a){t.setInputDataDrop([...t.inputDataDrop.slice(0,c),...t.inputDataDrop.slice(c+1,t.inputDataDrop.length)]);break}}function o(a){const l=a.target.files;for(var c=0;c<l.length;c++)if(l[c].name.indexOf(" ")>=0){s({title:"Problem",text:"Input file names should not have space."}),n(!0);break}t.setInputDataDrop([...t.inputDataDrop,...l])}return(()=>{const a=pc.cloneNode(!0),l=a.firstChild,c=l.firstChild,u=c.firstChild,v=u.nextSibling,g=v.nextSibling,b=c.nextSibling;return d(a,f(Z,{get when(){return t.inputDataDrop.length>0},get children(){const m=mc.cloneNode(!0),p=m.firstChild,w=p.nextSibling,x=w.firstChild;return d(x,f(be,{get each(){return t.inputDataDrop},children:S=>(()=>{const C=bc.cloneNode(!0);return C.$$click=i,C.$$clickData=S.name,d(C,()=>S.name),C})()})),m}}),l),d(c,f(Ol,{class:"w-10 h-10",color:"#9ca3af"}),u),g.$$click=t.setInputMode,g.$$clickData="paste",b.addEventListener("change",o),d(a,f(va,{get children(){return f(Z,{get when(){return e()},get children(){return f(Ci,{get title(){return r().title},get text(){return r().text},setShowErrorDialog:n})}})}}),null),a})()}R(["click"]);const yc=y(`<div id="input-paste-area" class="relative w-full h-64 border-2 border-gray-300 border-dashed rounded-md"><textarea id="input-text" class="font-mono border-0 bg-gray-50 text-gray-600 p-4 resize-none w-full h-full" placeholder="Copy and paste or type input variants. VCF is supported. A quick and simple format is space-delimited one:

chr1 9384934 + A T

which is chromosome, position, strand, a reference allele, and an alternate allele.

Alternatively, paths to input files in the server can be used as well. For example,

/mnt/oakvar/input/sample/sample_1.vcf
"></textarea><div class="top-2 right-3 absolute cursor-pointer" title="Click to go back"></div><div class="absolute bottom-1 right-1 text-gray-400 text-sm"><button value="cravat" class="p-1 text-gray-500 bg-neutral-200 hover:bg-neutral-300">Try an example</button></div></div>`);function _c(t){function e(r){const{serverUrl:s,setServerUrl:i}=ee;t.setAssembly("hg38"),t.setInputFormat("vcf"),fetch(`${s()}/submit/input-examples/${t.inputFormat}.${t.assembly}.txt`).then(o=>o.text()).then(o=>{t.changeInputData("paste",o)})}function n(r){t.changeInputData("paste",r.target.value)}return(()=>{const r=yc.cloneNode(!0),s=r.firstChild,i=s.nextSibling,o=i.nextSibling,a=o.firstChild;return s.$$keyup=n,i.$$click=t.setInputMode,i.$$clickData="drop",d(i,f(Tl,{class:"w-5 h-5 mr-2"})),a.$$click=e,$(()=>s.value=t.inputDataPaste),r})()}R(["keyup","click"]);const wc=y('<div id="job-name-div" class="mt-4 w-full"><textarea id="job-name" class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full " placeholder="(Optional) job name"></textarea></div>');function xc(t){function e(n){t.setJobName(n.target.value)}return(()=>{const n=wc.cloneNode(!0),r=n.firstChild;return r.$$keyup=e,$(()=>n.classList.toggle("hidden",!t.inputExists)),$(()=>r.value=t.jobName),n})()}R(["keyup"]);const Ec=y('<div id="submit-note-div" class="mt-4 w-full"><textarea id="submit-note" class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full" placeholder="(Optional) note for this job"></textarea></div>');function Ic(t){function e(n){t.setJobNote(n.target.value)}return(()=>{const n=Ec.cloneNode(!0),r=n.firstChild;return r.$$keyup=e,$(()=>n.classList.toggle("hidden",!t.inputExists)),$(()=>r.value=t.jobNote),n})()}R(["keyup"]);const Sc=y('<div id="submit-job-button-div" class="mt-4"><button id="submit-job-button" type="button" class="inline-flex items-center h-12 rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Annotate</button></div>');function $c(t){return(()=>{const e=Sc.cloneNode(!0),n=e.firstChild;return rn(n,"click",t.submitFn,!0),$(()=>e.classList.toggle("hidden",!t.inputExists)),e})()}R(["click"]);const kc=y('<div id="input-div" class="w-[40rem] items-center flex flex-col" style="height: calc(100vh - 10rem);"><div class="flex"></div><div class="w-full flex items-center justify-center mt-1" ondragenter="onDragEnterInputFiles(event)" ondragover="onDragOverInputFiles(event)" ondragleave="onDragLeaveInputFiles(event)" ondrop="onDropInputFiles(event)"></div></div>');function Tc(t){function e(n,r){t.setInputMode(n),n=="drop"?t.setInputDataDrop(r):n=="paste"&&t.setInputDataPaste(r)}return Fe(function(){t.inputMode=="drop"?t.setInputExists(t.inputDataDrop.length>0):t.inputMode=="paste"&&t.setInputExists(t.inputDataPaste.length>0)}),(()=>{const n=kc.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return d(r,f(sc,{get assembly(){return t.assembly},get setAssembly(){return t.setAssembly}}),null),d(r,f(hc,{get inputFormat(){return t.inputFormat},get setInputFormat(){return t.setInputFormat}}),null),d(s,f(ai,{get children(){return[f(Gn,{get when(){return t.inputMode=="drop"},get children(){return f(vc,{get setInputMode(){return t.setInputMode},get inputDataDrop(){return t.inputDataDrop},get setInputDataDrop(){return t.setInputDataDrop}})}}),f(Gn,{get when(){return t.inputMode=="paste"},get children(){return f(_c,{get setInputMode(){return t.setInputMode},changeInputData:e,get inputDataPaste(){return t.inputDataPaste},get assembly(){return t.assembly},get setAssembly(){return t.setAssembly},get inputFormat(){return t.inputFormat},get setInputFormat(){return t.setInputFormat}})}})]}})),d(n,f(xc,{get inputExists(){return t.inputExists},get jobName(){return t.jobName},get setJobName(){return t.setJobName}}),null),d(n,f(Ic,{get inputExists(){return t.inputExists},get jobNote(){return t.jobNote},get setJobNote(){return t.setJobNote}}),null),d(n,f($c,{get inputExists(){return t.inputExists},get submitFn(){return t.submitFn}}),null),n})()}const Cc=y("<a></a>");function qt(t){return(()=>{const e=Cc.cloneNode(!0);return rn(e,"click",t.clickFn,!0),d(e,()=>t.children),$(n=>{const r="relative inline-flex items-center rounded-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-500 focus:z-20 "+t.bgColor+" "+t.bgHoverColor,s=t.hrefValue,i=t.targetValue;return r!==n._v$&&li(e,n._v$=r),s!==n._v$2&&q(e,"href",n._v$2=s),i!==n._v$3&&q(e,"target",n._v$3=i),n},{_v$:void 0,_v$2:void 0,_v$3:void 0}),e})()}R(["click"]);const Ac=y('<div class="modulecard relative items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400 p-2"><div class="absolute left-0 bottom-0 w-full z-10 p-2 cursor-default" style="background-color: rgba(68, 64, 60, 0.3);"></div><div><div class="float-left w-24 h-24 mr-2 flex justify-center items-center"><img class="w-20 rounded-lg"></div><div class="min-w-0 flex-1" style="min-height: 6rem;"><a class="focus:online-none"><p class="text-md font-semibold text-gray-700"></p><p class="text-sm text-gray-500"></p></a></div></div><div class="w-full"></div></div>'),Oc=y('<input class="block w-full text-xs text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" type="file">'),Nc=y('<div class="flex flex-col"><span></span></div>'),Rc=y('<input type="text">'),{serverUrl:Dc,setServerUrl:km}=ee,{localModules:Pc,setLocalModules:Tm,getLocalModule:Cm,addLocalModule:Am,loadAllModules:Om,getLocalModuleLogo:Nm}=cn;function vr(t){const e=Pc()[t.moduleName],n=e.type,[r,s]=_(!1);function i(g){for(const b in g)if(t.moduleName==b)return!0;return!1}function o(){return i(t.annotators)||i(t.postaggregators)||i(t.reporters)}function a(){let g;return n=="annotator"?g={...t.annotators}:n=="postaggregator"?g={...t.postaggregators}:n=="reporter"&&(g={...t.reporters}),g}function l(g){o()?delete g[t.moduleName]:g[t.moduleName]=e}function c(g){n=="annotator"?t.setAnnotators(g):n=="postaggregator"?t.setPostaggregators(g):n=="reporter"&&t.setReporters(g)}function u(){if(t.cardType=="selected")return;let g=a();l(g),c(g)}function v(){let g=a();l(g),c(g)}return(()=>{const g=Ac.cloneNode(!0),b=g.firstChild,m=b.nextSibling,p=m.firstChild,w=p.firstChild,x=p.nextSibling,S=x.firstChild,C=S.firstChild,D=C.nextSibling,M=m.nextSibling;return g.$$click=u,g.addEventListener("mouseleave",k=>s(!1,k)),g.addEventListener("mouseenter",k=>s(!0,k)),b.$$click=v,d(b,f(Z,{get when(){return t.cardType!="selected"},get children(){return f(qt,{class:"w-full text-sm h-8 cursor-pointer",bgColor:"bg-white",bgHoverColor:"hover:bg-gray-100",children:"Details"})}}),null),d(b,f(Z,{get when(){return t.cardType=="selected"},get children(){return f(qt,{class:"w-full text-sm h-8 cursor-pointer",bgColor:"bg-white",bgHoverColor:"hover:bg-gray-100",children:"Remove"})}}),null),d(C,()=>e&&e.title),d(D,()=>e&&e.conf.description),d(M,f(Z,{get when(){return t.cardType=="selected"&&e.conf.module_options},get children(){return f(be,{get each(){return e.conf.module_options},children:function(k){return(()=>{const z=Nc.cloneNode(!0),F=z.firstChild;return d(F,()=>k.title),d(z,f(ai,{get fallback(){return Rc.cloneNode(!0)},get children(){return f(Gn,{get when(){return k.type=="file"},get children(){return Oc.cloneNode(!0)}})}}),null),z})()}})}})),$(k=>{const z=!!o(),F=t.cardType!="selected",A=t.cardType!="selected",P=!!(t.cardType=="selected"&&e.conf.module_options),N=e&&e.name,Y=e&&e.kind,V=!r()||t.cardType!="selected",W=Dc()+"/store/locallogo?module="+t.moduleName;return z!==k._v$&&g.classList.toggle("checked",k._v$=z),F!==k._v$2&&g.classList.toggle("cursor-copy",k._v$2=F),A!==k._v$3&&g.classList.toggle("max-h-64",k._v$3=A),P!==k._v$4&&g.classList.toggle("pb-16",k._v$4=P),N!==k._v$5&&q(g,"name",k._v$5=N),Y!==k._v$6&&q(g,"kind",k._v$6=Y),V!==k._v$7&&b.classList.toggle("hidden",k._v$7=V),W!==k._v$8&&q(w,"src",k._v$8=W),k},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0,_v$6:void 0,_v$7:void 0,_v$8:void 0}),g})()}R(["click"]);const Lc=y('<div id="report-choice-div" class="w-[36rem] flex flex-col justify-center items-center"><div class="text-md text-gray-600">Select optional reporters to run.</div><div id="report-choice-items" class="w-96 grid gap-2 justify-center overflow-y-auto bg-gray-100 py-4 rounded-md" style="height: calc(100vh - 10rem);"></div></div>'),Mc=async()=>{const{serverUrl:t,setServerUrl:e}=ee;return(await(await fetch(t()+"/submit/reporttypes")).json()).valid};function Uc(t){const[e]=ur(Mc);return(()=>{const n=Lc.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return d(s,f(be,{get each(){return e()},children:i=>f(vr,{moduleName:i+"reporter",get reporters(){return t.reporters},get setReporters(){return t.setReporters}})})),n})()}const jc=y('<div id="cta-analysis-module-choice" class="absolute inset-x-0 bottom-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Scroll down or click to select analysis modules</span></p></div></div></div></div></div>');function Fc(t){function e(){document.querySelector("#analysis-module-choice-div").scrollIntoView({behavior:"smooth"})}return(()=>{const n=jc.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild;return n.$$click=e,d(o,f(Ll,{color:"#6b7280"}),a),n})()}R(["click"]);const Bc=y('<button class="filter-category" role="filter-category" type="button"></button>');function ps(t){function e(n){t.setFilterCategory(t.value)}return(()=>{const n=Bc.cloneNode(!0);return n.$$click=e,d(n,()=>t.title),$(()=>n.classList.toggle("pinned",t.value==t.filterCategory)),$(()=>n.value=t.value),n})()}R(["click"]);const Hc=y('<div class="flex mb-2"><label for="search" class="sr-only">Search</label><input type="text" name="search" class="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm mr-2" placeholder="Search"><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Select all</button><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-2">Deselect all</button></div>');function Ai(t){function e(n){t.setSearchText(n.target.value)}return(()=>{const n=Hc.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return s.$$keyup=e,$(()=>q(n,"id",`search-filtered-modules-${t.kind}`)),$(()=>s.value=t.searchText),n})()}R(["keyup"]);const{localModules:zc,setLocalModules:Rm,getLocalModule:Dm,addLocalModule:Pm,loadAllModules:Lm}=cn;function Oi(t){for(let e in t)return!1;return!0}function Vc(t,e){let n=[];for(const[r,s]of Object.entries(zc())){let i=!0;r=="tagsampler"||r=="vcfinfo"||r=="varmeta"||s.type!="annotator"&&s.type!="postaggregator"?i=!1:e!=null&&(e=="no tag"?s.tags.length>0&&(i=!1):s.tags.indexOf(e)==-1&&(i=!1)),i&&t!=null&&(i=!1,(r.indexOf(t)>=0||s.title.indexOf(t)>=0||s.description&&s.description.indexOf(t)>=0)&&(i=!0)),i&&n.push(r)}return n.sort(),n}const Wc=y('<div class="filtered-modules-div overflow-auto pr-2 grid grid-cols-2 gap-1" style="height: calc(95vh - 8rem);"></div>');function Ni(t){return(()=>{const e=Wc.cloneNode(!0);return d(e,f(be,{get each(){return Vc(t.searchText,t.selectedTag)},children:n=>f(vr,{moduleName:n,get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}})})),$(n=>{const r=`filtered-modules-${t.kind}`,s=t.noCols==2,i=t.noCols==1;return r!==n._v$&&q(e,"id",n._v$=r),s!==n._v$2&&e.classList.toggle("grid-cols-2",n._v$2=s),i!==n._v$3&&e.classList.toggle("grid-cols-1",n._v$3=i),n},{_v$:void 0,_v$2:void 0,_v$3:void 0}),e})()}const Jc=y('<div id="analysis-module-filter-panel-all" class="analysis-module-filter-panel w-full mt-4 overflow-auto"></div>');function qc(t){const[e,n]=_(null);return(()=>{const r=Jc.cloneNode(!0);return d(r,f(Ai,{kind:"all",get searchText(){return e()},setSearchText:n}),null),d(r,f(Ni,{kind:"all",noCols:2,get searchText(){return e()},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),$(()=>r.classList.toggle("hidden",t.filterCategory!="all")),r})()}const Gc=y('<div class="relative flex items-start mb-2"><div class="flex items-center"><input type="radio" name="module-tag" class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"><label class="ml-3 block text-sm font-medium text-gray-600"></label></div></div>');function Kc(t){return t.replace(" ","_")}function Xc(t){return t.replace(/\w\S*/g,function(e){return e.charAt(0).toUpperCase()+e.substr(1).toLowerCase()})}function Yc(t){const e=`module-tag-radio-${Kc(t.value)}`;return(()=>{const n=Gc.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.nextSibling;return s.$$click=t.setSelectedTag,s.$$clickData=t.value,q(s,"id",e),q(i,"for",e),d(i,()=>Xc(t.value)),$(()=>s.value=t.value),n})()}R(["click"]);const Qc=y('<div id="analysis-module-filter-panel-tags" class="analysis-module-filter-panel w-full mt-4 overflow-auto grid grid-cols-3"><div id="analysis-module-filter-items-tags" class="col-span-1 flex flex-col justify-leading pl-1 overflow-y-auto" style="height: calc(95vh - 8rem);"></div><div class="col-span-2"></div></div>'),Zc=async()=>{const{serverUrl:t,setServerUrl:e}=ee;let n=await(await fetch(t()+"/submit/tags_annotators_postaggregators")).json();return n.push("no tag"),n};function eu(t){const[e]=ur(Zc),[n,r]=_(null),[s,i]=_(null);return(()=>{const o=Qc.cloneNode(!0),a=o.firstChild,l=a.nextSibling;return d(a,f(be,{get each(){return e()},children:c=>f(Yc,{value:c,setSelectedTag:r})})),d(l,f(Ai,{kind:"tags",get searchText(){return s()},setSearchText:i}),null),d(l,f(Ni,{kind:"tags",noCols:1,get selectedTag(){return n()},get searchText(){return s()},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),$(()=>o.classList.toggle("hidden",t.filterCategory!="tags")),o})()}const tu=y('<div class="analysis-module-filter-wrapper col-span-7"><div id="analysis-module-filter-kinds" class="w-full"></div></div>');function nu(t){const[e,n]=_("all");return(()=>{const r=tu.cloneNode(!0),s=r.firstChild;return d(s,f(ps,{value:"all",title:"All",get filterCategory(){return e()},setFilterCategory:n}),null),d(s,f(ps,{value:"tags",title:"Tags",get filterCategory(){return e()},setFilterCategory:n}),null),d(r,f(qc,{get filterCategory(){return e()},get localModules(){return t.localModules},get setLocalModules(){return t.setLocalModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),d(r,f(eu,{get filterCategory(){return e()},get localModules(){return t.localModules},get setLocalModules(){return t.setLocalModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),r})()}const ru=y('<div class="col-span-4"><div class="text-gray-600 bg-gray-100 rounded-md border border-transparent font-medium px-3 py-1.5 h-[34px]">Selected analysis modules</div><div class="flex mb-2 mt-4"><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 h-[38px]">Clear</button></div><div class="filtered-modules-div overflow-auto pr-2 grid grid-cols-2 gap-1 grid-cols-1" style="height: calc(95vh - 8rem);"></div></div>');function su(t){function e(){let r=[];for(const s in t.annotators)r.push(s);for(const s in t.postaggregators)r.push(s);return r.sort(),r}function n(){t.setAnnotators({}),t.setPostaggregators({})}return(()=>{const r=ru.cloneNode(!0),s=r.firstChild,i=s.nextSibling,o=i.firstChild,a=i.nextSibling;return o.$$click=n,d(a,f(be,{get each(){return e()},children:function(l){return f(vr,{moduleName:l,get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators},cardType:"selected"})}})),r})()}R(["click"]);const iu=y('<div id="cta-input" class="absolute inset-x-0 top-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Scroll up or click to go to the input panel</span></p></div></div></div></div></div>');function ou(t){function e(){document.querySelector("#input-div").scrollIntoView({behavior:"smooth"})}return(()=>{const n=iu.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild;return n.$$click=e,d(o,f(Ul,{color:"#6b7280"}),a),n})()}R(["click"]);const au=y('<div id="analysis-module-choice-div" class="relative container mt-6 mb-4 snap-center flex justify-center max-w-7xl h-[95vh] max-w-7xl"><div id="analysis-module-filter-div" class="bg-white p-4 rounded-md ml-4 mt-4 overflow-auto flex flex-col gap-8 text-gray-600 h-[95vh] w-full"><div id="analysis-module-div" class="grid grid-cols-12 gap-2 mt-8" style="height: calc(95vh - 20rem);"><div class="col-span-1 flex flex-col justify-center content-center items-center"></div></div></div></div>');function lu(t){return(()=>{const e=au.cloneNode(!0),n=e.firstChild,r=n.firstChild,s=r.firstChild;return d(e,f(ou,{}),n),d(r,f(nu,{get localModules(){return t.localModules},get setLocalModules(){return t.setLocalModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),s),d(s,f(Ml,{})),d(r,f(su,{get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),e})()}const cu=y('<li><a href="#" class="block hover:bg-gray-50"><div class="py-4"><div class="flex items-center justify-between"><p class="truncate text-sm font-medium text-indigo-600"></p></div><div class="mt-2 sm:flex sm:justify-between"><div class="mt-2 w-full flex items-center text-sm text-gray-500 sm:mt-0"><div class="w-full bg-gray-200 rounded-full dark:bg-gray-700"><div class="bg-blue-600 text-xs font-medium text-blue-100 text-center p-0.5 leading-none rounded-full">%</div></div></div></div></div></a></li>');function uu(t){return(()=>{const e=cu.cloneNode(!0),n=e.firstChild,r=n.firstChild,s=r.firstChild,i=s.firstChild,o=s.nextSibling,a=o.firstChild,l=a.firstChild,c=l.firstChild,u=c.firstChild;return d(i,()=>t.fileName),d(c,()=>t.progress,u),$(()=>c.style.setProperty("width",t.progress+"%")),e})()}const du=y('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6"><div><div class="mt-3 text-center sm:mt-5"><ul role="list" class="divide-y divide-gray-200"></ul></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm">Cancel</button></div></div></div></div></div>');function fu(t){function e(){t.controller.abort()}return(()=>{const n=du.cloneNode(!0),r=n.firstChild,s=r.nextSibling,i=s.firstChild,o=i.firstChild,a=o.firstChild,l=a.firstChild,c=l.firstChild,u=a.nextSibling,v=u.firstChild;return d(c,f(uu,{fileName:"Uploading...",get progress(){return t.uploadState.progress}})),v.$$click=e,n})()}R(["click"]);const hu=y('<div class="tabcontent p-4 snap-y snap-mandatory h-screen overflow-y-auto"><div class="relative container flex gap-8 snap-center max-w-7xl h-[95vh] justify-center items-start"></div></div>'),gu=y("<div>Loading...</div>"),{tabName:mu}=Ze,{localModules:pu}=cn,{serverUrl:bu,withCredentials:vu}=ee,{logged:yu}=Be,{multiuser:_u}=Ce;function wu(t){const[e,n]=_("drop"),[r,s]=_(""),[i,o]=_([]),[a,l]=_(""),[c,u]=_([]),[v,g]=_([]),[b,m]=_([]),[p,w]=_(""),[x,S]=_(!1),[C,D]=_(null),[M,k]=_(null),[z,F]=_(!1),[A,P]=_({});let N=[],Y=null,V={},W;Fe(function(){_u()&&!yu()&&Ct()});function Ct(){n("drop"),s(""),o([]),l([]),u([]),g([]),m([]),w(""),S(!1),D(null),k(null),F(!1),P({})}function pn(){return a().startsWith("#serverfile")}function bn(){let T=[],B=a().split(`
`);for(var _e=1;_e<B.length;_e++){let He=B[_e];He==""||He.startsWith("#")||T.push(He.trim())}T.length>0&&(V.inputServerFiles=T)}function vn(){N=[];const T=new Blob([a()],{type:"text/plain"});N.push(new File([T],"input"))}function yn(){pn()?bn():vn()}function nt(T){if(T!=null&&(e()=="drop"?N=i():e()=="paste"&&yn(),N.length>0))for(var B=0;B<N.length;B++)T.append("file_"+B,N[B])}function _n(){V.annotators=[];for(const T in c())V.annotators.push(T)}function ye(){V.postaggregators=[];for(const T in v())V.postaggregators.push(T)}function wn(){V.reports=[];for(const T in b())V.reports.push(T.substring(0,T.lastIndexOf("reporter")))}function xn(){V.genome=p()}function En(){V.input_format=r()}function rt(){V.job_name=C()}function In(){V.note=M()}function Sn(T){W=new AbortController,F(!0),P({progress:0}),j({method:"post",url:bu()+"/submit/submit?"+Math.random(),data:T,transformRequest:()=>T,signal:W.signal,withCredentials:vu,onUploadProgress:B=>{let _e=Math.round(B.progress*100);P({progress:_e})}}).then(function(B){F(!1),setTimeout(function(){t.setJobsTrigger(!t.jobsTrigger)},500)}).catch(function(B){console.error(B),B.code!="ERR_CANCELED"&&alert(B),P({}),F(!1)})}function E(){N={},V={},Y=new FormData,nt(Y),_n(),ye(),wn(),xn(),En(),rt(),In(),V.writeadmindb=!0,Y.append("options",JSON.stringify(V)),Sn(Y)}return(()=>{const T=hu.cloneNode(!0),B=T.firstChild;return d(B,f(Tc,{get inputMode(){return e()},setInputMode:n,get inputDataDrop(){return i()},setInputDataDrop:o,get inputDataPaste(){return a()},setInputDataPaste:l,get assembly(){return p()},setAssembly:w,get inputFormat(){return r()},setInputFormat:s,get inputExists(){return x()},setInputExists:S,get jobName(){return C()},setJobName:D,get jobNote(){return M()},setJobNote:k,submitFn:E}),null),d(B,f(Z,{get when(){return x()},get children(){return[f(Z,{get when(){return!Oi(pu())},get fallback(){return gu.cloneNode(!0)},get children(){return f(Uc,{get reporters(){return b()},setReporters:m})}}),f(Fc,{})]}}),null),d(T,f(Z,{get when(){return x()},get children(){return f(lu,{get annotators(){return c()},setAnnotators:u,get postaggregators(){return v()},setPostaggregators:g})}}),null),d(T,f(Z,{get when(){return z()},get children(){return f(fu,{get uploadState(){return A()},controller:W})}}),null),$(()=>T.classList.toggle("hidden",mu()!="submit")),T})()}const er=Symbol("store-raw"),ht=Symbol("store-node"),xu=Symbol("store-name");function Ri(t,e){let n=t[he];if(!n&&(Object.defineProperty(t,he,{value:n=new Proxy(t,Su)}),!Array.isArray(t))){const r=Object.keys(t),s=Object.getOwnPropertyDescriptors(t);for(let i=0,o=r.length;i<o;i++){const a=r[i];if(s[a].get){const l=s[a].get.bind(n);Object.defineProperty(t,a,{enumerable:s[a].enumerable,get:l})}}}return n}function Gt(t){let e;return t!=null&&typeof t=="object"&&(t[he]||!(e=Object.getPrototypeOf(t))||e===Object.prototype||Array.isArray(t))}function gt(t,e=new Set){let n,r,s,i;if(n=t!=null&&t[er])return n;if(!Gt(t)||e.has(t))return t;if(Array.isArray(t)){Object.isFrozen(t)?t=t.slice(0):e.add(t);for(let o=0,a=t.length;o<a;o++)s=t[o],(r=gt(s,e))!==s&&(t[o]=r)}else{Object.isFrozen(t)?t=Object.assign({},t):e.add(t);const o=Object.keys(t),a=Object.getOwnPropertyDescriptors(t);for(let l=0,c=o.length;l<c;l++)i=o[l],!a[i].get&&(s=t[i],(r=gt(s,e))!==s&&(t[i]=r))}return t}function yr(t){let e=t[ht];return e||Object.defineProperty(t,ht,{value:e={}}),e}function tr(t,e,n){return t[e]||(t[e]=Pi(n))}function Eu(t,e){const n=Reflect.getOwnPropertyDescriptor(t,e);return!n||n.get||!n.configurable||e===he||e===ht||e===xu||(delete n.value,delete n.writable,n.get=()=>t[he][e]),n}function Di(t){if(ei()){const e=yr(t);(e._||(e._=Pi()))()}}function Iu(t){return Di(t),Reflect.ownKeys(t)}function Pi(t){const[e,n]=_(t,{equals:!1,internal:!0});return e.$=n,e}const Su={get(t,e,n){if(e===er)return t;if(e===he)return n;if(e===Jn)return Di(t),n;const r=yr(t),s=r.hasOwnProperty(e);let i=s?r[e]():t[e];if(e===ht||e==="__proto__")return i;if(!s){const o=Object.getOwnPropertyDescriptor(t,e);ei()&&(typeof i!="function"||t.hasOwnProperty(e))&&!(o&&o.get)&&(i=tr(r,e,i)())}return Gt(i)?Ri(i):i},has(t,e){return e===er||e===he||e===Jn||e===ht||e==="__proto__"?!0:(this.get(t,e,t),e in t)},set(){return!0},deleteProperty(){return!0},ownKeys:Iu,getOwnPropertyDescriptor:Eu};function Kt(t,e,n,r=!1){if(!r&&t[e]===n)return;const s=t[e],i=t.length;n===void 0?delete t[e]:t[e]=n;let o=yr(t),a;(a=tr(o,e,s))&&a.$(()=>n),Array.isArray(t)&&t.length!==i&&(a=tr(o,"length",i))&&a.$(t.length),(a=o._)&&a.$()}function Li(t,e){const n=Object.keys(e);for(let r=0;r<n.length;r+=1){const s=n[r];Kt(t,s,e[s])}}function $u(t,e){if(typeof e=="function"&&(e=e(t)),e=gt(e),Array.isArray(e)){if(t===e)return;let n=0,r=e.length;for(;n<r;n++){const s=e[n];t[n]!==s&&Kt(t,n,s)}Kt(t,"length",r)}else Li(t,e)}function lt(t,e,n=[]){let r,s=t;if(e.length>1){r=e.shift();const o=typeof r,a=Array.isArray(t);if(Array.isArray(r)){for(let l=0;l<r.length;l++)lt(t,[r[l]].concat(e),n);return}else if(a&&o==="function"){for(let l=0;l<t.length;l++)r(t[l],l)&&lt(t,[l].concat(e),n);return}else if(a&&o==="object"){const{from:l=0,to:c=t.length-1,by:u=1}=r;for(let v=l;v<=c;v+=u)lt(t,[v].concat(e),n);return}else if(e.length>1){lt(t[r],e,[r].concat(n));return}s=t[r],n=[r].concat(n)}let i=e[0];typeof i=="function"&&(i=i(s,n),i===s)||r===void 0&&i==null||(i=gt(i),r===void 0||Gt(s)&&Gt(i)&&!Array.isArray(i)?Li(s,i):Kt(t,r,i))}function ku(...[t,e]){const n=gt(t||{}),r=Array.isArray(n),s=Ri(n);function i(...o){Jo(()=>{r&&o.length===1?$u(n,o[0]):lt(n,o)})}return[s,i]}const Tu=y('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function Cu(t){function e(){t.setAction(t.optionValue),t.execute(),t.setShow(!1)}return(()=>{const n=Tu.cloneNode(!0);return n.$$click=e,d(n,()=>t.optionTitle),n})()}R(["click"]);const Au=y('<div class="option-list ease-in absolute right-0 z-10 mt-12 w-24 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu"><div class="py-1" role="none"></div></div>');function Ou(t){return(()=>{const e=Au.cloneNode(!0),n=e.firstChild;return d(n,f(be,{get each(){return t.options},children:function(r){return f(Cu,{get optionValue(){return r.value},get optionTitle(){return r.title},get execute(){return t.execute},get setAction(){return t.setAction},get setShow(){return t.setShow}})}})),$(()=>e.classList.toggle("hidden",!t.show)),e})()}const Nu=y('<div class="select-div relative inline-flex text-left"><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="assembly-select-div" title="Job action">Action</button></div></div>');function Ru(t){const[e,n]=_(!1),[r,s]=_(""),i=[{value:"abort",title:"Abort"},{value:"delete",title:"Delete"}];function o(){t.performJobAction(r())}function a(l){n(!e())}return(()=>{const l=Nu.cloneNode(!0),c=l.firstChild,u=c.firstChild;return u.firstChild,u.$$click=a,d(u,f(br,{class:"-mr-1 ml-2 h-5 w-5"}),null),d(l,f(Ou,{get show(){return e()},options:i,execute:o,setAction:s,setShow:n}),null),l})()}R(["click"]);const Du=y('<div class="flex bg-white pb-2 mt-2"><div class="flex"><nav class="isolate inline-flex rounded-md shadow-sm ml-8" aria-label="Pagination"><a href="#" class="jobs-table-page-nav-btn relative inline-flex items-center rounded-l-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span aria-current="page" class="relative z-10 inline-flex items-center border bg-white border-gray-300 text-gray-500 px-4 py-2 text-sm font-medium focus:z-20"></span><a href="#" class="jobs-table-page-nav-btn relative inline-flex items-center rounded-r-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Go to page</span><input type="text" class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">Go</a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Show</span><input type="text" class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">jobs per page</a><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20 ml-4"></a></nav></div></div>');function Pu(t){function e(){let o=t.pageno;o=o-1,o<=0&&(o=1),o!=t.pageno&&t.setPageno(o)}function n(){let o=t.pageno;o=o+1,o!=t.pageno&&t.setPageno(o)}function r(o){let a=o.target.value;try{a=parseInt(a)}catch(l){console.error(l);return}a<1&&(a=1),t.setPageno(a)}function s(o){let a=o.target.value;try{a=parseInt(a)}catch(l){console.error(l);return}t.setPagesize(a)}function i(o){t.setJobsTrigger(!t.jobsTrigger)}return(()=>{const o=Du.cloneNode(!0),a=o.firstChild,l=a.firstChild,c=l.firstChild,u=c.nextSibling,v=u.nextSibling,g=v.nextSibling,b=g.nextSibling,m=b.nextSibling,p=m.nextSibling,w=p.nextSibling,x=w.nextSibling,S=x.nextSibling;return d(a,f(Ru,{get performJobAction(){return t.performJobAction}}),l),c.$$click=e,d(c,f(jl,{class:"w-5 h-5"})),d(u,()=>t.pageno),v.$$click=n,d(v,f(Fl,{class:"w-5 h-5"})),b.addEventListener("change",r),w.addEventListener("change",s),S.$$click=i,d(S,f(Bl,{class:"w-5 h-5"})),$(()=>b.value=t.pageno),$(()=>w.value=t.pagesize),o})()}R(["click"]);const Lu=y('<span class="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800"></span>'),Mu=y('<span class="inline-flex rounded-full bg-amber-100 px-2 text-xs font-semibold leading-5 text-amber-800"></span>'),Uu=y('<span class="inline-flex rounded-full bg-red-100 px-2 text-xs font-semibold leading-5 text-red-800"></span>'),ju=y('<span class="inline-flex text-xs"></span>'),Fu=y('<tr class="text-sm h-16"><td scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8 bg-gray-50"><input type="checkbox" class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></td><td class="jobs-table-td"></td><td class="jobs-table-td bg-gray-50"></td><td class="jobs-table-td"></td><td class="jobs-table-td bg-gray-50"></td><td class="jobs-table-td"></td><td class="jobs-table-td bg-gray-50 text-xs"></td><td class="jobs-table-td"></td></tr>');function Bu(t){return t=="Finished"||t=="Error"||t=="Aborted"}function Hu(t){const{serverUrl:e,withCredentials:n}=ee,r=1e3;let s=null;Vt(()=>clearInterval(s));function i(){t.changeJobChecked(t.job.uid),t.setAllMarksOn(null)}function o(){j.get(e()+"/submit/jobstatus",{params:{uid:t.job.uid},withCredentials:n}).then(function(m){const p=m.data;Bu(p)&&clearInterval(s),t.changeJobStatus(t.job.uid,p)}).catch(function(m){console.error(m)})}function a(){const m=t.job.status;m!="Finished"&&m!="Error"&&m!="Aborted"&&(s=setInterval(function(){o()},r))}function l(){return t.job.status=="Finished"}function c(){return l()?f(qt,{children:"View",get hrefValue(){return e()+"/result/nocache/index.html?uid="+t.job.uid},targetValue:"_blank",bgColor:"bg-sky-100",bgHoverColor:"hover:bg-sky-200"}):f(qt,{children:"Log",get hrefValue(){return e()+"/submit/joblog?uid="+t.job.uid},targetValue:"_blank",bgColor:"bg-gray-100",bgHoverColor:"hover:bg-gray-200"})}function u(){const m=t.job.status;return m=="Finished"?(()=>{const p=Lu.cloneNode(!0);return d(p,()=>t.job.status),p})():m=="Aborted"?(()=>{const p=Mu.cloneNode(!0);return d(p,()=>t.job.status),p})():m=="Error"?(()=>{const p=Uu.cloneNode(!0);return d(p,()=>t.job.status),p})():(()=>{const p=ju.cloneNode(!0);return d(p,()=>t.job.status),p})()}function v(){return t.job.info_json.orig_input_fname?t.job.info_json.orig_input_fname.join(", "):""}function g(){return(""+new Date(t.job.info_json.submission_time)).split("GMT")[0]}function b(){let m=[];const p=t.job.info_json;if(!p)return"";const w=p.annotators;if(w)for(const S of w)S!="original_input"&&m.push(S);const x=p.postaggregators;if(x)for(const S of x)m.push(S);return m.join(", ")}return a(),(()=>{const m=Fu.cloneNode(!0),p=m.firstChild,w=p.firstChild,x=p.nextSibling,S=x.nextSibling,C=S.nextSibling,D=C.nextSibling,M=D.nextSibling,k=M.nextSibling,z=k.nextSibling;return w.addEventListener("change",i),d(x,()=>t.job.name),d(S,u),d(C,c),d(D,v),d(M,b),d(k,g),d(z,()=>t.job.info_json.note),$(()=>w.checked=t.job.checked),m})()}const zu=y('<div class="flex flex-col"><div class="relative shadow ring-1 ring-black ring-opacity-5 md:rounded-lg overflow-auto"><table class="table-fixed divide-y divide-gray-300"><thead class="table-header-group bg-gray-50 block"><tr><th scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8"><input type="checkbox" class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></th><th scope="col" class="jobs-table-th min-w-[10rem]">Name</th><th scope="col" class="jobs-table-th min-w-[5rem]">State</th><th scope="col" class="jobs-table-th min-w-[5rem]">View</th><th scope="col" class="jobs-table-th min-w-[20rem]">Input</th><th scope="col" class="jobs-table-th min-w-[10rem]">Modules</th><th scope="col" class="jobs-table-th min-w-[8rem]">Submitted</th><th scope="col" class="jobs-table-th w-full">Note</th></tr></thead><tbody class="table-row-group divide-y divide-gray-200 bg-white block overflow-auto h-[36rem]"></tbody></table></div></div>');function Vu(t){const[e,n]=_(null);function r(){if(e()==!0?n(!1):(e()==null||e()==!1)&&n(!0),e()==!0)for(const s of t.jobs)t.changeJobChecked(s.uid,!0);else if(e()==!1)for(const s of t.jobs)t.changeJobChecked(s.uid,!1)}return(()=>{const s=zu.cloneNode(!0),i=s.firstChild,o=i.firstChild,a=o.firstChild,l=a.firstChild,c=l.firstChild,u=c.firstChild,v=a.nextSibling;return u.$$click=r,d(v,f(be,{get each(){return t.jobs},children:g=>f(Hu,{job:g,get changeJobStatus(){return t.changeJobStatus},get changeJobChecked(){return t.changeJobChecked},setAllMarksOn:n})})),$(()=>u.value=e()),s})()}R(["click"]);const Wu=y('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="text-center"><p class="text-sm text-gray-500"></p></div></div></div></div></div></div>');function Ju(t){return(()=>{const e=Wu.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,l=a.firstChild;return d(l,()=>t.msg),$(()=>e.classList.toggle("hidden",t.msg==null)),e})()}const qu=y('<div id="tab_jobs" class="tabcontent px-6 mb-4"><div></div></div>'),{serverUrl:bs,withCredentials:vs}=ee,{logged:Gu,setLogged:Ku}=Be,{multiuser:Xu}=Ce;function Yu(t){const{tabName:e}=Ze,[n,r]=ku([]),[s,i]=_(1),[o,a]=_(10),[l,c]=_(null);Fe(function(){s(),o(),t.jobsTrigger,(Xu()==!1||Gu()==!0)&&g()});function u(p,w){r(x=>x.uid==p,"status",w)}function v(p,w){w==null?r(x=>x.uid==p,"checked",x=>!x):r(x=>x.uid==p,"checked",w)}function g(){j.post(bs()+"/submit/jobs",{pageno:s(),pagesize:o()},{withCredentials:vs}).then(function(p){if(p.status=="error"){Ku(!1);return}const w=p.data;r(w)}).catch(function(p){console.error(p),p.response.status==404&&i(s()-1)})}function b(p,w){const x=p.map(S=>S.uid);j.post(bs()+"/submit/delete_jobs",{uids:x,abort_only:w},{withCredentials:vs}).then(function(){t.setJobsTrigger(!t.jobsTrigger),c(null)}).catch(function(S){console.error(S),c(null)})}function m(p){const w=n.filter(x=>x.checked);p=="delete"?(c("Deleting jobs..."),b(w,!1)):p=="abort"&&(c("Aborting jobs..."),b(w,!0))}return(()=>{const p=qu.cloneNode(!0),w=p.firstChild;return d(w,f(Pu,{get pageno(){return s()},setPageno:i,get pagesize(){return o()},setPagesize:a,get jobsTrigger(){return t.jobsTrigger},get setJobsTrigger(){return t.setJobsTrigger},performJobAction:m}),null),d(w,f(Vu,{jobs:n,changeJobStatus:u,changeJobChecked:v}),null),d(p,f(Ju,{get msg(){return l()}}),null),$(()=>p.classList.toggle("hidden",e()!="jobs")),p})()}const Qu=y('<div id="tab_system" class="tabcontent"><div class="p-4"><button type="button" class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 text-sm font-medium leading-4 text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Download system log</button></div></div>'),{serverUrl:Zu,setServerUrl:Mm,withCredentials:Um}=ee;function ed(){const{tabName:t,setTabName:e}=Ze;function n(){j({url:Zu()+"/submit/systemlog",method:"GET",responseType:"blob"}).then(function(r){let s=document.createElement("a");s.href=window.URL.createObjectURL(new Blob([r.data],{type:"text/plain"})),s.download=r.headers["content-disposition"].split("=")[1],document.body.appendChild(s),s.click(),document.body.removeChild(s)}).catch(function(r){console.error(r)})}return(()=>{const r=Qu.cloneNode(!0),s=r.firstChild,i=s.firstChild;return i.$$click=n,$(()=>r.classList.toggle("hidden",t()!="system")),r})()}R(["click"]);/**
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
 */const Mi=function(t){const e=[];let n=0;for(let r=0;r<t.length;r++){let s=t.charCodeAt(r);s<128?e[n++]=s:s<2048?(e[n++]=s>>6|192,e[n++]=s&63|128):(s&64512)===55296&&r+1<t.length&&(t.charCodeAt(r+1)&64512)===56320?(s=65536+((s&1023)<<10)+(t.charCodeAt(++r)&1023),e[n++]=s>>18|240,e[n++]=s>>12&63|128,e[n++]=s>>6&63|128,e[n++]=s&63|128):(e[n++]=s>>12|224,e[n++]=s>>6&63|128,e[n++]=s&63|128)}return e},td=function(t){const e=[];let n=0,r=0;for(;n<t.length;){const s=t[n++];if(s<128)e[r++]=String.fromCharCode(s);else if(s>191&&s<224){const i=t[n++];e[r++]=String.fromCharCode((s&31)<<6|i&63)}else if(s>239&&s<365){const i=t[n++],o=t[n++],a=t[n++],l=((s&7)<<18|(i&63)<<12|(o&63)<<6|a&63)-65536;e[r++]=String.fromCharCode(55296+(l>>10)),e[r++]=String.fromCharCode(56320+(l&1023))}else{const i=t[n++],o=t[n++];e[r++]=String.fromCharCode((s&15)<<12|(i&63)<<6|o&63)}}return e.join("")},Ui={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(t,e){if(!Array.isArray(t))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let s=0;s<t.length;s+=3){const i=t[s],o=s+1<t.length,a=o?t[s+1]:0,l=s+2<t.length,c=l?t[s+2]:0,u=i>>2,v=(i&3)<<4|a>>4;let g=(a&15)<<2|c>>6,b=c&63;l||(b=64,o||(g=64)),r.push(n[u],n[v],n[g],n[b])}return r.join("")},encodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(t):this.encodeByteArray(Mi(t),e)},decodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(t):td(this.decodeStringToByteArray(t,e))},decodeStringToByteArray(t,e){this.init_();const n=e?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let s=0;s<t.length;){const i=n[t.charAt(s++)],a=s<t.length?n[t.charAt(s)]:0;++s;const c=s<t.length?n[t.charAt(s)]:64;++s;const v=s<t.length?n[t.charAt(s)]:64;if(++s,i==null||a==null||c==null||v==null)throw Error();const g=i<<2|a>>4;if(r.push(g),c!==64){const b=a<<4&240|c>>2;if(r.push(b),v!==64){const m=c<<6&192|v;r.push(m)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let t=0;t<this.ENCODED_VALS.length;t++)this.byteToCharMap_[t]=this.ENCODED_VALS.charAt(t),this.charToByteMap_[this.byteToCharMap_[t]]=t,this.byteToCharMapWebSafe_[t]=this.ENCODED_VALS_WEBSAFE.charAt(t),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[t]]=t,t>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(t)]=t,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(t)]=t)}}},nd=function(t){const e=Mi(t);return Ui.encodeByteArray(e,!0)},ji=function(t){return nd(t).replace(/\./g,"")},Fi=function(t){try{return Ui.decodeString(t,!0)}catch(e){console.error("base64Decode failed: ",e)}return null};/**
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
 */function X(){return typeof navigator<"u"&&typeof navigator.userAgent=="string"?navigator.userAgent:""}function rd(){return typeof window<"u"&&!!(window.cordova||window.phonegap||window.PhoneGap)&&/ios|iphone|ipod|ipad|android|blackberry|iemobile/i.test(X())}function sd(){const t=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof t=="object"&&t.id!==void 0}function id(){return typeof navigator=="object"&&navigator.product==="ReactNative"}function od(){const t=X();return t.indexOf("MSIE ")>=0||t.indexOf("Trident/")>=0}function ad(){return typeof indexedDB=="object"}function ld(){return new Promise((t,e)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(r);s.onsuccess=()=>{s.result.close(),n||self.indexedDB.deleteDatabase(r),t(!0)},s.onupgradeneeded=()=>{n=!1},s.onerror=()=>{var i;e(((i=s.error)===null||i===void 0?void 0:i.message)||"")}}catch(n){e(n)}})}function cd(){if(typeof self<"u")return self;if(typeof window<"u")return window;if(typeof global<"u")return global;throw new Error("Unable to locate global object.")}/**
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
 */const ud=()=>cd().__FIREBASE_DEFAULTS__,dd=()=>{if(typeof process>"u"||typeof process.env>"u")return;const t=process.env.__FIREBASE_DEFAULTS__;if(t)return JSON.parse(t)},fd=()=>{if(typeof document>"u")return;let t;try{t=document.cookie.match(/__FIREBASE_DEFAULTS__=([^;]+)/)}catch{return}const e=t&&Fi(t[1]);return e&&JSON.parse(e)},_r=()=>{try{return ud()||dd()||fd()}catch(t){console.info(`Unable to get __FIREBASE_DEFAULTS__ due to: ${t}`);return}},hd=t=>{var e,n;return(n=(e=_r())===null||e===void 0?void 0:e.emulatorHosts)===null||n===void 0?void 0:n[t]},gd=()=>{var t;return(t=_r())===null||t===void 0?void 0:t.config},Bi=t=>{var e;return(e=_r())===null||e===void 0?void 0:e[`_${t}`]};/**
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
 */class md{constructor(){this.reject=()=>{},this.resolve=()=>{},this.promise=new Promise((e,n)=>{this.resolve=e,this.reject=n})}wrapCallback(e){return(n,r)=>{n?this.reject(n):this.resolve(r),typeof e=="function"&&(this.promise.catch(()=>{}),e.length===1?e(n):e(n,r))}}}/**
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
 */const pd="FirebaseError";class Ae extends Error{constructor(e,n,r){super(n),this.code=e,this.customData=r,this.name=pd,Object.setPrototypeOf(this,Ae.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,xt.prototype.create)}}class xt{constructor(e,n,r){this.service=e,this.serviceName=n,this.errors=r}create(e,...n){const r=n[0]||{},s=`${this.service}/${e}`,i=this.errors[e],o=i?bd(i,r):"Error",a=`${this.serviceName}: ${o} (${s}).`;return new Ae(s,a,r)}}function bd(t,e){return t.replace(vd,(n,r)=>{const s=e[r];return s!=null?String(s):`<${r}?>`})}const vd=/\{\$([^}]+)}/g;function yd(t){for(const e in t)if(Object.prototype.hasOwnProperty.call(t,e))return!1;return!0}function Xt(t,e){if(t===e)return!0;const n=Object.keys(t),r=Object.keys(e);for(const s of n){if(!r.includes(s))return!1;const i=t[s],o=e[s];if(ys(i)&&ys(o)){if(!Xt(i,o))return!1}else if(i!==o)return!1}for(const s of r)if(!n.includes(s))return!1;return!0}function ys(t){return t!==null&&typeof t=="object"}/**
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
 */function Et(t){const e=[];for(const[n,r]of Object.entries(t))Array.isArray(r)?r.forEach(s=>{e.push(encodeURIComponent(n)+"="+encodeURIComponent(s))}):e.push(encodeURIComponent(n)+"="+encodeURIComponent(r));return e.length?"&"+e.join("&"):""}function ct(t){const e={};return t.replace(/^\?/,"").split("&").forEach(r=>{if(r){const[s,i]=r.split("=");e[decodeURIComponent(s)]=decodeURIComponent(i)}}),e}function ut(t){const e=t.indexOf("?");if(!e)return"";const n=t.indexOf("#",e);return t.substring(e,n>0?n:void 0)}function _d(t,e){const n=new wd(t,e);return n.subscribe.bind(n)}class wd{constructor(e,n){this.observers=[],this.unsubscribes=[],this.observerCount=0,this.task=Promise.resolve(),this.finalized=!1,this.onNoObservers=n,this.task.then(()=>{e(this)}).catch(r=>{this.error(r)})}next(e){this.forEachObserver(n=>{n.next(e)})}error(e){this.forEachObserver(n=>{n.error(e)}),this.close(e)}complete(){this.forEachObserver(e=>{e.complete()}),this.close()}subscribe(e,n,r){let s;if(e===void 0&&n===void 0&&r===void 0)throw new Error("Missing Observer.");xd(e,["next","error","complete"])?s=e:s={next:e,error:n,complete:r},s.next===void 0&&(s.next=Dn),s.error===void 0&&(s.error=Dn),s.complete===void 0&&(s.complete=Dn);const i=this.unsubscribeOne.bind(this,this.observers.length);return this.finalized&&this.task.then(()=>{try{this.finalError?s.error(this.finalError):s.complete()}catch{}}),this.observers.push(s),i}unsubscribeOne(e){this.observers===void 0||this.observers[e]===void 0||(delete this.observers[e],this.observerCount-=1,this.observerCount===0&&this.onNoObservers!==void 0&&this.onNoObservers(this))}forEachObserver(e){if(!this.finalized)for(let n=0;n<this.observers.length;n++)this.sendOne(n,e)}sendOne(e,n){this.task.then(()=>{if(this.observers!==void 0&&this.observers[e]!==void 0)try{n(this.observers[e])}catch(r){typeof console<"u"&&console.error&&console.error(r)}})}close(e){this.finalized||(this.finalized=!0,e!==void 0&&(this.finalError=e),this.task.then(()=>{this.observers=void 0,this.onNoObservers=void 0}))}}function xd(t,e){if(typeof t!="object"||t===null)return!1;for(const n of e)if(n in t&&typeof t[n]=="function")return!0;return!1}function Dn(){}/**
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
 */function oe(t){return t&&t._delegate?t._delegate:t}class Ge{constructor(e,n,r){this.name=e,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}/**
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
 */const Re="[DEFAULT]";/**
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
 */class Ed{constructor(e,n){this.name=e,this.container=n,this.component=null,this.instances=new Map,this.instancesDeferred=new Map,this.instancesOptions=new Map,this.onInitCallbacks=new Map}get(e){const n=this.normalizeInstanceIdentifier(e);if(!this.instancesDeferred.has(n)){const r=new md;if(this.instancesDeferred.set(n,r),this.isInitialized(n)||this.shouldAutoInitialize())try{const s=this.getOrInitializeService({instanceIdentifier:n});s&&r.resolve(s)}catch{}}return this.instancesDeferred.get(n).promise}getImmediate(e){var n;const r=this.normalizeInstanceIdentifier(e?.identifier),s=(n=e?.optional)!==null&&n!==void 0?n:!1;if(this.isInitialized(r)||this.shouldAutoInitialize())try{return this.getOrInitializeService({instanceIdentifier:r})}catch(i){if(s)return null;throw i}else{if(s)return null;throw Error(`Service ${this.name} is not available`)}}getComponent(){return this.component}setComponent(e){if(e.name!==this.name)throw Error(`Mismatching Component ${e.name} for Provider ${this.name}.`);if(this.component)throw Error(`Component for ${this.name} has already been provided`);if(this.component=e,!!this.shouldAutoInitialize()){if(Sd(e))try{this.getOrInitializeService({instanceIdentifier:Re})}catch{}for(const[n,r]of this.instancesDeferred.entries()){const s=this.normalizeInstanceIdentifier(n);try{const i=this.getOrInitializeService({instanceIdentifier:s});r.resolve(i)}catch{}}}}clearInstance(e=Re){this.instancesDeferred.delete(e),this.instancesOptions.delete(e),this.instances.delete(e)}async delete(){const e=Array.from(this.instances.values());await Promise.all([...e.filter(n=>"INTERNAL"in n).map(n=>n.INTERNAL.delete()),...e.filter(n=>"_delete"in n).map(n=>n._delete())])}isComponentSet(){return this.component!=null}isInitialized(e=Re){return this.instances.has(e)}getOptions(e=Re){return this.instancesOptions.get(e)||{}}initialize(e={}){const{options:n={}}=e,r=this.normalizeInstanceIdentifier(e.instanceIdentifier);if(this.isInitialized(r))throw Error(`${this.name}(${r}) has already been initialized`);if(!this.isComponentSet())throw Error(`Component ${this.name} has not been registered yet`);const s=this.getOrInitializeService({instanceIdentifier:r,options:n});for(const[i,o]of this.instancesDeferred.entries()){const a=this.normalizeInstanceIdentifier(i);r===a&&o.resolve(s)}return s}onInit(e,n){var r;const s=this.normalizeInstanceIdentifier(n),i=(r=this.onInitCallbacks.get(s))!==null&&r!==void 0?r:new Set;i.add(e),this.onInitCallbacks.set(s,i);const o=this.instances.get(s);return o&&e(o,s),()=>{i.delete(e)}}invokeOnInitCallbacks(e,n){const r=this.onInitCallbacks.get(n);if(!!r)for(const s of r)try{s(e,n)}catch{}}getOrInitializeService({instanceIdentifier:e,options:n={}}){let r=this.instances.get(e);if(!r&&this.component&&(r=this.component.instanceFactory(this.container,{instanceIdentifier:Id(e),options:n}),this.instances.set(e,r),this.instancesOptions.set(e,n),this.invokeOnInitCallbacks(r,e),this.component.onInstanceCreated))try{this.component.onInstanceCreated(this.container,e,r)}catch{}return r||null}normalizeInstanceIdentifier(e=Re){return this.component?this.component.multipleInstances?e:Re:e}shouldAutoInitialize(){return!!this.component&&this.component.instantiationMode!=="EXPLICIT"}}function Id(t){return t===Re?void 0:t}function Sd(t){return t.instantiationMode==="EAGER"}/**
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
 */class $d{constructor(e){this.name=e,this.providers=new Map}addComponent(e){const n=this.getProvider(e.name);if(n.isComponentSet())throw new Error(`Component ${e.name} has already been registered with ${this.name}`);n.setComponent(e)}addOrOverwriteComponent(e){this.getProvider(e.name).isComponentSet()&&this.providers.delete(e.name),this.addComponent(e)}getProvider(e){if(this.providers.has(e))return this.providers.get(e);const n=new Ed(e,this);return this.providers.set(e,n),n}getProviders(){return Array.from(this.providers.values())}}/**
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
 */var U;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(U||(U={}));const kd={debug:U.DEBUG,verbose:U.VERBOSE,info:U.INFO,warn:U.WARN,error:U.ERROR,silent:U.SILENT},Td=U.INFO,Cd={[U.DEBUG]:"log",[U.VERBOSE]:"log",[U.INFO]:"info",[U.WARN]:"warn",[U.ERROR]:"error"},Ad=(t,e,...n)=>{if(e<t.logLevel)return;const r=new Date().toISOString(),s=Cd[e];if(s)console[s](`[${r}]  ${t.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class Hi{constructor(e){this.name=e,this._logLevel=Td,this._logHandler=Ad,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in U))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?kd[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,U.DEBUG,...e),this._logHandler(this,U.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,U.VERBOSE,...e),this._logHandler(this,U.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,U.INFO,...e),this._logHandler(this,U.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,U.WARN,...e),this._logHandler(this,U.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,U.ERROR,...e),this._logHandler(this,U.ERROR,...e)}}const Od=(t,e)=>e.some(n=>t instanceof n);let _s,ws;function Nd(){return _s||(_s=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Rd(){return ws||(ws=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const zi=new WeakMap,nr=new WeakMap,Vi=new WeakMap,Pn=new WeakMap,wr=new WeakMap;function Dd(t){const e=new Promise((n,r)=>{const s=()=>{t.removeEventListener("success",i),t.removeEventListener("error",o)},i=()=>{n(Se(t.result)),s()},o=()=>{r(t.error),s()};t.addEventListener("success",i),t.addEventListener("error",o)});return e.then(n=>{n instanceof IDBCursor&&zi.set(n,t)}).catch(()=>{}),wr.set(e,t),e}function Pd(t){if(nr.has(t))return;const e=new Promise((n,r)=>{const s=()=>{t.removeEventListener("complete",i),t.removeEventListener("error",o),t.removeEventListener("abort",o)},i=()=>{n(),s()},o=()=>{r(t.error||new DOMException("AbortError","AbortError")),s()};t.addEventListener("complete",i),t.addEventListener("error",o),t.addEventListener("abort",o)});nr.set(t,e)}let rr={get(t,e,n){if(t instanceof IDBTransaction){if(e==="done")return nr.get(t);if(e==="objectStoreNames")return t.objectStoreNames||Vi.get(t);if(e==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return Se(t[e])},set(t,e,n){return t[e]=n,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function Ld(t){rr=t(rr)}function Md(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...n){const r=t.call(Ln(this),e,...n);return Vi.set(r,e.sort?e.sort():[e]),Se(r)}:Rd().includes(t)?function(...e){return t.apply(Ln(this),e),Se(zi.get(this))}:function(...e){return Se(t.apply(Ln(this),e))}}function Ud(t){return typeof t=="function"?Md(t):(t instanceof IDBTransaction&&Pd(t),Od(t,Nd())?new Proxy(t,rr):t)}function Se(t){if(t instanceof IDBRequest)return Dd(t);if(Pn.has(t))return Pn.get(t);const e=Ud(t);return e!==t&&(Pn.set(t,e),wr.set(e,t)),e}const Ln=t=>wr.get(t);function jd(t,e,{blocked:n,upgrade:r,blocking:s,terminated:i}={}){const o=indexedDB.open(t,e),a=Se(o);return r&&o.addEventListener("upgradeneeded",l=>{r(Se(o.result),l.oldVersion,l.newVersion,Se(o.transaction))}),n&&o.addEventListener("blocked",()=>n()),a.then(l=>{i&&l.addEventListener("close",()=>i()),s&&l.addEventListener("versionchange",()=>s())}).catch(()=>{}),a}const Fd=["get","getKey","getAll","getAllKeys","count"],Bd=["put","add","delete","clear"],Mn=new Map;function xs(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if(Mn.get(e))return Mn.get(e);const n=e.replace(/FromIndex$/,""),r=e!==n,s=Bd.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(s||Fd.includes(n)))return;const i=async function(o,...a){const l=this.transaction(o,s?"readwrite":"readonly");let c=l.store;return r&&(c=c.index(a.shift())),(await Promise.all([c[n](...a),s&&l.done]))[0]};return Mn.set(e,i),i}Ld(t=>({...t,get:(e,n,r)=>xs(e,n)||t.get(e,n,r),has:(e,n)=>!!xs(e,n)||t.has(e,n)}));/**
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
 */class Hd{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(zd(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function zd(t){const e=t.getComponent();return e?.type==="VERSION"}const sr="@firebase/app",Es="0.8.4";/**
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
 */const Ue=new Hi("@firebase/app"),Vd="@firebase/app-compat",Wd="@firebase/analytics-compat",Jd="@firebase/analytics",qd="@firebase/app-check-compat",Gd="@firebase/app-check",Kd="@firebase/auth",Xd="@firebase/auth-compat",Yd="@firebase/database",Qd="@firebase/database-compat",Zd="@firebase/functions",ef="@firebase/functions-compat",tf="@firebase/installations",nf="@firebase/installations-compat",rf="@firebase/messaging",sf="@firebase/messaging-compat",of="@firebase/performance",af="@firebase/performance-compat",lf="@firebase/remote-config",cf="@firebase/remote-config-compat",uf="@firebase/storage",df="@firebase/storage-compat",ff="@firebase/firestore",hf="@firebase/firestore-compat",gf="firebase",mf="9.14.0";/**
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
 */const ir="[DEFAULT]",pf={[sr]:"fire-core",[Vd]:"fire-core-compat",[Jd]:"fire-analytics",[Wd]:"fire-analytics-compat",[Gd]:"fire-app-check",[qd]:"fire-app-check-compat",[Kd]:"fire-auth",[Xd]:"fire-auth-compat",[Yd]:"fire-rtdb",[Qd]:"fire-rtdb-compat",[Zd]:"fire-fn",[ef]:"fire-fn-compat",[tf]:"fire-iid",[nf]:"fire-iid-compat",[rf]:"fire-fcm",[sf]:"fire-fcm-compat",[of]:"fire-perf",[af]:"fire-perf-compat",[lf]:"fire-rc",[cf]:"fire-rc-compat",[uf]:"fire-gcs",[df]:"fire-gcs-compat",[ff]:"fire-fst",[hf]:"fire-fst-compat","fire-js":"fire-js",[gf]:"fire-js-all"};/**
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
 */const Yt=new Map,or=new Map;function bf(t,e){try{t.container.addComponent(e)}catch(n){Ue.debug(`Component ${e.name} failed to register with FirebaseApp ${t.name}`,n)}}function mt(t){const e=t.name;if(or.has(e))return Ue.debug(`There were multiple attempts to register component ${e}.`),!1;or.set(e,t);for(const n of Yt.values())bf(n,t);return!0}function Wi(t,e){const n=t.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),t.container.getProvider(e)}/**
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
 */const vf={["no-app"]:"No Firebase App '{$appName}' has been created - call Firebase App.initializeApp()",["bad-app-name"]:"Illegal App name: '{$appName}",["duplicate-app"]:"Firebase App named '{$appName}' already exists with different options or config",["app-deleted"]:"Firebase App named '{$appName}' already deleted",["no-options"]:"Need to provide options, when not being deployed to hosting via source.",["invalid-app-argument"]:"firebase.{$appName}() takes either no argument or a Firebase App instance.",["invalid-log-argument"]:"First argument to `onLog` must be null or a function.",["idb-open"]:"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.",["idb-get"]:"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.",["idb-set"]:"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.",["idb-delete"]:"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}."},$e=new xt("app","Firebase",vf);/**
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
 */class yf{constructor(e,n,r){this._isDeleted=!1,this._options=Object.assign({},e),this._config=Object.assign({},n),this._name=n.name,this._automaticDataCollectionEnabled=n.automaticDataCollectionEnabled,this._container=r,this.container.addComponent(new Ge("app",()=>this,"PUBLIC"))}get automaticDataCollectionEnabled(){return this.checkDestroyed(),this._automaticDataCollectionEnabled}set automaticDataCollectionEnabled(e){this.checkDestroyed(),this._automaticDataCollectionEnabled=e}get name(){return this.checkDestroyed(),this._name}get options(){return this.checkDestroyed(),this._options}get config(){return this.checkDestroyed(),this._config}get container(){return this._container}get isDeleted(){return this._isDeleted}set isDeleted(e){this._isDeleted=e}checkDestroyed(){if(this.isDeleted)throw $e.create("app-deleted",{appName:this._name})}}/**
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
 */const un=mf;function Ji(t,e={}){let n=t;typeof e!="object"&&(e={name:e});const r=Object.assign({name:ir,automaticDataCollectionEnabled:!1},e),s=r.name;if(typeof s!="string"||!s)throw $e.create("bad-app-name",{appName:String(s)});if(n||(n=gd()),!n)throw $e.create("no-options");const i=Yt.get(s);if(i){if(Xt(n,i.options)&&Xt(r,i.config))return i;throw $e.create("duplicate-app",{appName:s})}const o=new $d(s);for(const l of or.values())o.addComponent(l);const a=new yf(n,r,o);return Yt.set(s,a),a}function _f(t=ir){const e=Yt.get(t);if(!e&&t===ir)return Ji();if(!e)throw $e.create("no-app",{appName:t});return e}function Ve(t,e,n){var r;let s=(r=pf[t])!==null&&r!==void 0?r:t;n&&(s+=`-${n}`);const i=s.match(/\s|\//),o=e.match(/\s|\//);if(i||o){const a=[`Unable to register library "${s}" with version "${e}":`];i&&a.push(`library name "${s}" contains illegal characters (whitespace or "/")`),i&&o&&a.push("and"),o&&a.push(`version name "${e}" contains illegal characters (whitespace or "/")`),Ue.warn(a.join(" "));return}mt(new Ge(`${s}-version`,()=>({library:s,version:e}),"VERSION"))}/**
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
 */const wf="firebase-heartbeat-database",xf=1,pt="firebase-heartbeat-store";let Un=null;function qi(){return Un||(Un=jd(wf,xf,{upgrade:(t,e)=>{switch(e){case 0:t.createObjectStore(pt)}}}).catch(t=>{throw $e.create("idb-open",{originalErrorMessage:t.message})})),Un}async function Ef(t){var e;try{return(await qi()).transaction(pt).objectStore(pt).get(Gi(t))}catch(n){if(n instanceof Ae)Ue.warn(n.message);else{const r=$e.create("idb-get",{originalErrorMessage:(e=n)===null||e===void 0?void 0:e.message});Ue.warn(r.message)}}}async function Is(t,e){var n;try{const s=(await qi()).transaction(pt,"readwrite");return await s.objectStore(pt).put(e,Gi(t)),s.done}catch(r){if(r instanceof Ae)Ue.warn(r.message);else{const s=$e.create("idb-set",{originalErrorMessage:(n=r)===null||n===void 0?void 0:n.message});Ue.warn(s.message)}}}function Gi(t){return`${t.name}!${t.options.appId}`}/**
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
 */const If=1024,Sf=30*24*60*60*1e3;class $f{constructor(e){this.container=e,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new Tf(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){const n=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),r=Ss();if(this._heartbeatsCache===null&&(this._heartbeatsCache=await this._heartbeatsCachePromise),!(this._heartbeatsCache.lastSentHeartbeatDate===r||this._heartbeatsCache.heartbeats.some(s=>s.date===r)))return this._heartbeatsCache.heartbeats.push({date:r,agent:n}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(s=>{const i=new Date(s.date).valueOf();return Date.now()-i<=Sf}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,this._heartbeatsCache===null||this._heartbeatsCache.heartbeats.length===0)return"";const e=Ss(),{heartbeatsToSend:n,unsentEntries:r}=kf(this._heartbeatsCache.heartbeats),s=ji(JSON.stringify({version:2,heartbeats:n}));return this._heartbeatsCache.lastSentHeartbeatDate=e,r.length>0?(this._heartbeatsCache.heartbeats=r,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}}function Ss(){return new Date().toISOString().substring(0,10)}function kf(t,e=If){const n=[];let r=t.slice();for(const s of t){const i=n.find(o=>o.agent===s.agent);if(i){if(i.dates.push(s.date),$s(n)>e){i.dates.pop();break}}else if(n.push({agent:s.agent,dates:[s.date]}),$s(n)>e){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class Tf{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return ad()?ld().then(()=>!0).catch(()=>!1):!1}async read(){return await this._canUseIndexedDBPromise?await Ef(this.app)||{heartbeats:[]}:{heartbeats:[]}}async overwrite(e){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return Is(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return Is(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:[...s.heartbeats,...e.heartbeats]})}else return}}function $s(t){return ji(JSON.stringify({version:2,heartbeats:t})).length}/**
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
 */function Cf(t){mt(new Ge("platform-logger",e=>new Hd(e),"PRIVATE")),mt(new Ge("heartbeat",e=>new $f(e),"PRIVATE")),Ve(sr,Es,t),Ve(sr,Es,"esm2017"),Ve("fire-js","")}Cf("");function xr(t,e){var n={};for(var r in t)Object.prototype.hasOwnProperty.call(t,r)&&e.indexOf(r)<0&&(n[r]=t[r]);if(t!=null&&typeof Object.getOwnPropertySymbols=="function")for(var s=0,r=Object.getOwnPropertySymbols(t);s<r.length;s++)e.indexOf(r[s])<0&&Object.prototype.propertyIsEnumerable.call(t,r[s])&&(n[r[s]]=t[r[s]]);return n}function Ki(){return{["dependent-sdk-initialized-before-auth"]:"Another Firebase SDK was initialized and is trying to use Auth before Auth is initialized. Please be sure to call `initializeAuth` or `getAuth` before starting any other Firebase SDK."}}const Af=Ki,Xi=new xt("auth","Firebase",Ki());/**
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
 */const ks=new Hi("@firebase/auth");function Ut(t,...e){ks.logLevel<=U.ERROR&&ks.error(`Auth (${un}): ${t}`,...e)}/**
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
 */function re(t,...e){throw Er(t,...e)}function se(t,...e){return Er(t,...e)}function Yi(t,e,n){const r=Object.assign(Object.assign({},Af()),{[e]:n});return new xt("auth","Firebase",r).create(e,{appName:t.name})}function Of(t,e,n){const r=n;if(!(e instanceof r))throw r.name!==e.constructor.name&&re(t,"argument-error"),Yi(t,"argument-error",`Type of ${e.constructor.name} does not match expected instance.Did you pass a reference from a different Auth SDK?`)}function Er(t,...e){if(typeof t!="string"){const n=e[0],r=[...e.slice(1)];return r[0]&&(r[0].appName=t.name),t._errorFactory.create(n,...r)}return Xi.create(t,...e)}function I(t,e,...n){if(!t)throw Er(e,...n)}function ce(t){const e="INTERNAL ASSERTION FAILED: "+t;throw Ut(e),new Error(e)}function me(t,e){t||ce(e)}/**
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
 */const Ts=new Map;function ue(t){me(t instanceof Function,"Expected a class definition");let e=Ts.get(t);return e?(me(e instanceof t,"Instance stored in cache mismatched with class"),e):(e=new t,Ts.set(t,e),e)}/**
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
 */function Nf(t,e){const n=Wi(t,"auth");if(n.isInitialized()){const s=n.getImmediate(),i=n.getOptions();if(Xt(i,e??{}))return s;re(s,"already-initialized")}return n.initialize({options:e})}function Rf(t,e){const n=e?.persistence||[],r=(Array.isArray(n)?n:[n]).map(ue);e?.errorMap&&t._updateErrorMap(e.errorMap),t._initializeWithPersistence(r,e?.popupRedirectResolver)}/**
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
 */function ar(){var t;return typeof self<"u"&&((t=self.location)===null||t===void 0?void 0:t.href)||""}function Df(){return Cs()==="http:"||Cs()==="https:"}function Cs(){var t;return typeof self<"u"&&((t=self.location)===null||t===void 0?void 0:t.protocol)||null}/**
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
 */function Pf(){return typeof navigator<"u"&&navigator&&"onLine"in navigator&&typeof navigator.onLine=="boolean"&&(Df()||sd()||"connection"in navigator)?navigator.onLine:!0}function Lf(){if(typeof navigator>"u")return null;const t=navigator;return t.languages&&t.languages[0]||t.language||null}/**
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
 */class It{constructor(e,n){this.shortDelay=e,this.longDelay=n,me(n>e,"Short delay should be less than long delay!"),this.isMobile=rd()||id()}get(){return Pf()?this.isMobile?this.longDelay:this.shortDelay:Math.min(5e3,this.shortDelay)}}/**
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
 */function Ir(t,e){me(t.emulator,"Emulator should always be set here");const{url:n}=t.emulator;return e?`${n}${e.startsWith("/")?e.slice(1):e}`:n}/**
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
 */class Qi{static initialize(e,n,r){this.fetchImpl=e,n&&(this.headersImpl=n),r&&(this.responseImpl=r)}static fetch(){if(this.fetchImpl)return this.fetchImpl;if(typeof self<"u"&&"fetch"in self)return self.fetch;ce("Could not find fetch implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static headers(){if(this.headersImpl)return this.headersImpl;if(typeof self<"u"&&"Headers"in self)return self.Headers;ce("Could not find Headers implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static response(){if(this.responseImpl)return this.responseImpl;if(typeof self<"u"&&"Response"in self)return self.Response;ce("Could not find Response implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}}/**
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
 */const Mf={CREDENTIAL_MISMATCH:"custom-token-mismatch",MISSING_CUSTOM_TOKEN:"internal-error",INVALID_IDENTIFIER:"invalid-email",MISSING_CONTINUE_URI:"internal-error",INVALID_PASSWORD:"wrong-password",MISSING_PASSWORD:"internal-error",EMAIL_EXISTS:"email-already-in-use",PASSWORD_LOGIN_DISABLED:"operation-not-allowed",INVALID_IDP_RESPONSE:"invalid-credential",INVALID_PENDING_TOKEN:"invalid-credential",FEDERATED_USER_ID_ALREADY_LINKED:"credential-already-in-use",MISSING_REQ_TYPE:"internal-error",EMAIL_NOT_FOUND:"user-not-found",RESET_PASSWORD_EXCEED_LIMIT:"too-many-requests",EXPIRED_OOB_CODE:"expired-action-code",INVALID_OOB_CODE:"invalid-action-code",MISSING_OOB_CODE:"internal-error",CREDENTIAL_TOO_OLD_LOGIN_AGAIN:"requires-recent-login",INVALID_ID_TOKEN:"invalid-user-token",TOKEN_EXPIRED:"user-token-expired",USER_NOT_FOUND:"user-token-expired",TOO_MANY_ATTEMPTS_TRY_LATER:"too-many-requests",INVALID_CODE:"invalid-verification-code",INVALID_SESSION_INFO:"invalid-verification-id",INVALID_TEMPORARY_PROOF:"invalid-credential",MISSING_SESSION_INFO:"missing-verification-id",SESSION_EXPIRED:"code-expired",MISSING_ANDROID_PACKAGE_NAME:"missing-android-pkg-name",UNAUTHORIZED_DOMAIN:"unauthorized-continue-uri",INVALID_OAUTH_CLIENT_ID:"invalid-oauth-client-id",ADMIN_ONLY_OPERATION:"admin-restricted-operation",INVALID_MFA_PENDING_CREDENTIAL:"invalid-multi-factor-session",MFA_ENROLLMENT_NOT_FOUND:"multi-factor-info-not-found",MISSING_MFA_ENROLLMENT_ID:"missing-multi-factor-info",MISSING_MFA_PENDING_CREDENTIAL:"missing-multi-factor-session",SECOND_FACTOR_EXISTS:"second-factor-already-in-use",SECOND_FACTOR_LIMIT_EXCEEDED:"maximum-second-factor-count-exceeded",BLOCKING_FUNCTION_ERROR_RESPONSE:"internal-error"};/**
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
 */const Uf=new It(3e4,6e4);function St(t,e){return t.tenantId&&!e.tenantId?Object.assign(Object.assign({},e),{tenantId:t.tenantId}):e}async function et(t,e,n,r,s={}){return Zi(t,s,async()=>{let i={},o={};r&&(e==="GET"?o=r:i={body:JSON.stringify(r)});const a=Et(Object.assign({key:t.config.apiKey},o)).slice(1),l=await t._getAdditionalHeaders();return l["Content-Type"]="application/json",t.languageCode&&(l["X-Firebase-Locale"]=t.languageCode),Qi.fetch()(eo(t,t.config.apiHost,n,a),Object.assign({method:e,headers:l,referrerPolicy:"no-referrer"},i))})}async function Zi(t,e,n){t._canInitEmulator=!1;const r=Object.assign(Object.assign({},Mf),e);try{const s=new jf(t),i=await Promise.race([n(),s.promise]);s.clearNetworkTimeout();const o=await i.json();if("needConfirmation"in o)throw Rt(t,"account-exists-with-different-credential",o);if(i.ok&&!("errorMessage"in o))return o;{const a=i.ok?o.errorMessage:o.error.message,[l,c]=a.split(" : ");if(l==="FEDERATED_USER_ID_ALREADY_LINKED")throw Rt(t,"credential-already-in-use",o);if(l==="EMAIL_EXISTS")throw Rt(t,"email-already-in-use",o);if(l==="USER_DISABLED")throw Rt(t,"user-disabled",o);const u=r[l]||l.toLowerCase().replace(/[_\s]+/g,"-");if(c)throw Yi(t,u,c);re(t,u)}}catch(s){if(s instanceof Ae)throw s;re(t,"network-request-failed")}}async function dn(t,e,n,r,s={}){const i=await et(t,e,n,r,s);return"mfaPendingCredential"in i&&re(t,"multi-factor-auth-required",{_serverResponse:i}),i}function eo(t,e,n,r){const s=`${e}${n}?${r}`;return t.config.emulator?Ir(t.config,s):`${t.config.apiScheme}://${s}`}class jf{constructor(e){this.auth=e,this.timer=null,this.promise=new Promise((n,r)=>{this.timer=setTimeout(()=>r(se(this.auth,"network-request-failed")),Uf.get())})}clearNetworkTimeout(){clearTimeout(this.timer)}}function Rt(t,e,n){const r={appName:t.name};n.email&&(r.email=n.email),n.phoneNumber&&(r.phoneNumber=n.phoneNumber);const s=se(t,e,r);return s.customData._tokenResponse=n,s}/**
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
 */async function Ff(t,e){return et(t,"POST","/v1/accounts:delete",e)}async function Bf(t,e){return et(t,"POST","/v1/accounts:lookup",e)}/**
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
 */function dt(t){if(!!t)try{const e=new Date(Number(t));if(!isNaN(e.getTime()))return e.toUTCString()}catch{}}async function Hf(t,e=!1){const n=oe(t),r=await n.getIdToken(e),s=Sr(r);I(s&&s.exp&&s.auth_time&&s.iat,n.auth,"internal-error");const i=typeof s.firebase=="object"?s.firebase:void 0,o=i?.sign_in_provider;return{claims:s,token:r,authTime:dt(jn(s.auth_time)),issuedAtTime:dt(jn(s.iat)),expirationTime:dt(jn(s.exp)),signInProvider:o||null,signInSecondFactor:i?.sign_in_second_factor||null}}function jn(t){return Number(t)*1e3}function Sr(t){var e;const[n,r,s]=t.split(".");if(n===void 0||r===void 0||s===void 0)return Ut("JWT malformed, contained fewer than 3 sections"),null;try{const i=Fi(r);return i?JSON.parse(i):(Ut("Failed to decode base64 JWT payload"),null)}catch(i){return Ut("Caught error parsing JWT payload as JSON",(e=i)===null||e===void 0?void 0:e.toString()),null}}function zf(t){const e=Sr(t);return I(e,"internal-error"),I(typeof e.exp<"u","internal-error"),I(typeof e.iat<"u","internal-error"),Number(e.exp)-Number(e.iat)}/**
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
 */async function bt(t,e,n=!1){if(n)return e;try{return await e}catch(r){throw r instanceof Ae&&Vf(r)&&t.auth.currentUser===t&&await t.auth.signOut(),r}}function Vf({code:t}){return t==="auth/user-disabled"||t==="auth/user-token-expired"}/**
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
 */class Wf{constructor(e){this.user=e,this.isRunning=!1,this.timerId=null,this.errorBackoff=3e4}_start(){this.isRunning||(this.isRunning=!0,this.schedule())}_stop(){!this.isRunning||(this.isRunning=!1,this.timerId!==null&&clearTimeout(this.timerId))}getInterval(e){var n;if(e){const r=this.errorBackoff;return this.errorBackoff=Math.min(this.errorBackoff*2,96e4),r}else{this.errorBackoff=3e4;const s=((n=this.user.stsTokenManager.expirationTime)!==null&&n!==void 0?n:0)-Date.now()-3e5;return Math.max(0,s)}}schedule(e=!1){if(!this.isRunning)return;const n=this.getInterval(e);this.timerId=setTimeout(async()=>{await this.iteration()},n)}async iteration(){var e;try{await this.user.getIdToken(!0)}catch(n){((e=n)===null||e===void 0?void 0:e.code)==="auth/network-request-failed"&&this.schedule(!0);return}this.schedule()}}/**
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
 */class to{constructor(e,n){this.createdAt=e,this.lastLoginAt=n,this._initializeTime()}_initializeTime(){this.lastSignInTime=dt(this.lastLoginAt),this.creationTime=dt(this.createdAt)}_copy(e){this.createdAt=e.createdAt,this.lastLoginAt=e.lastLoginAt,this._initializeTime()}toJSON(){return{createdAt:this.createdAt,lastLoginAt:this.lastLoginAt}}}/**
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
 */async function Qt(t){var e;const n=t.auth,r=await t.getIdToken(),s=await bt(t,Bf(n,{idToken:r}));I(s?.users.length,n,"internal-error");const i=s.users[0];t._notifyReloadListener(i);const o=!((e=i.providerUserInfo)===null||e===void 0)&&e.length?Gf(i.providerUserInfo):[],a=qf(t.providerData,o),l=t.isAnonymous,c=!(t.email&&i.passwordHash)&&!a?.length,u=l?c:!1,v={uid:i.localId,displayName:i.displayName||null,photoURL:i.photoUrl||null,email:i.email||null,emailVerified:i.emailVerified||!1,phoneNumber:i.phoneNumber||null,tenantId:i.tenantId||null,providerData:a,metadata:new to(i.createdAt,i.lastLoginAt),isAnonymous:u};Object.assign(t,v)}async function Jf(t){const e=oe(t);await Qt(e),await e.auth._persistUserIfCurrent(e),e.auth._notifyListenersIfCurrent(e)}function qf(t,e){return[...t.filter(r=>!e.some(s=>s.providerId===r.providerId)),...e]}function Gf(t){return t.map(e=>{var{providerId:n}=e,r=xr(e,["providerId"]);return{providerId:n,uid:r.rawId||"",displayName:r.displayName||null,email:r.email||null,phoneNumber:r.phoneNumber||null,photoURL:r.photoUrl||null}})}/**
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
 */async function Kf(t,e){const n=await Zi(t,{},async()=>{const r=Et({grant_type:"refresh_token",refresh_token:e}).slice(1),{tokenApiHost:s,apiKey:i}=t.config,o=eo(t,s,"/v1/token",`key=${i}`),a=await t._getAdditionalHeaders();return a["Content-Type"]="application/x-www-form-urlencoded",Qi.fetch()(o,{method:"POST",headers:a,body:r})});return{accessToken:n.access_token,expiresIn:n.expires_in,refreshToken:n.refresh_token}}/**
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
 */class vt{constructor(){this.refreshToken=null,this.accessToken=null,this.expirationTime=null}get isExpired(){return!this.expirationTime||Date.now()>this.expirationTime-3e4}updateFromServerResponse(e){I(e.idToken,"internal-error"),I(typeof e.idToken<"u","internal-error"),I(typeof e.refreshToken<"u","internal-error");const n="expiresIn"in e&&typeof e.expiresIn<"u"?Number(e.expiresIn):zf(e.idToken);this.updateTokensAndExpiration(e.idToken,e.refreshToken,n)}async getToken(e,n=!1){return I(!this.accessToken||this.refreshToken,e,"user-token-expired"),!n&&this.accessToken&&!this.isExpired?this.accessToken:this.refreshToken?(await this.refresh(e,this.refreshToken),this.accessToken):null}clearRefreshToken(){this.refreshToken=null}async refresh(e,n){const{accessToken:r,refreshToken:s,expiresIn:i}=await Kf(e,n);this.updateTokensAndExpiration(r,s,Number(i))}updateTokensAndExpiration(e,n,r){this.refreshToken=n||null,this.accessToken=e||null,this.expirationTime=Date.now()+r*1e3}static fromJSON(e,n){const{refreshToken:r,accessToken:s,expirationTime:i}=n,o=new vt;return r&&(I(typeof r=="string","internal-error",{appName:e}),o.refreshToken=r),s&&(I(typeof s=="string","internal-error",{appName:e}),o.accessToken=s),i&&(I(typeof i=="number","internal-error",{appName:e}),o.expirationTime=i),o}toJSON(){return{refreshToken:this.refreshToken,accessToken:this.accessToken,expirationTime:this.expirationTime}}_assign(e){this.accessToken=e.accessToken,this.refreshToken=e.refreshToken,this.expirationTime=e.expirationTime}_clone(){return Object.assign(new vt,this.toJSON())}_performRefresh(){return ce("not implemented")}}/**
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
 */function xe(t,e){I(typeof t=="string"||typeof t>"u","internal-error",{appName:e})}class Me{constructor(e){var{uid:n,auth:r,stsTokenManager:s}=e,i=xr(e,["uid","auth","stsTokenManager"]);this.providerId="firebase",this.proactiveRefresh=new Wf(this),this.reloadUserInfo=null,this.reloadListener=null,this.uid=n,this.auth=r,this.stsTokenManager=s,this.accessToken=s.accessToken,this.displayName=i.displayName||null,this.email=i.email||null,this.emailVerified=i.emailVerified||!1,this.phoneNumber=i.phoneNumber||null,this.photoURL=i.photoURL||null,this.isAnonymous=i.isAnonymous||!1,this.tenantId=i.tenantId||null,this.providerData=i.providerData?[...i.providerData]:[],this.metadata=new to(i.createdAt||void 0,i.lastLoginAt||void 0)}async getIdToken(e){const n=await bt(this,this.stsTokenManager.getToken(this.auth,e));return I(n,this.auth,"internal-error"),this.accessToken!==n&&(this.accessToken=n,await this.auth._persistUserIfCurrent(this),this.auth._notifyListenersIfCurrent(this)),n}getIdTokenResult(e){return Hf(this,e)}reload(){return Jf(this)}_assign(e){this!==e&&(I(this.uid===e.uid,this.auth,"internal-error"),this.displayName=e.displayName,this.photoURL=e.photoURL,this.email=e.email,this.emailVerified=e.emailVerified,this.phoneNumber=e.phoneNumber,this.isAnonymous=e.isAnonymous,this.tenantId=e.tenantId,this.providerData=e.providerData.map(n=>Object.assign({},n)),this.metadata._copy(e.metadata),this.stsTokenManager._assign(e.stsTokenManager))}_clone(e){return new Me(Object.assign(Object.assign({},this),{auth:e,stsTokenManager:this.stsTokenManager._clone()}))}_onReload(e){I(!this.reloadListener,this.auth,"internal-error"),this.reloadListener=e,this.reloadUserInfo&&(this._notifyReloadListener(this.reloadUserInfo),this.reloadUserInfo=null)}_notifyReloadListener(e){this.reloadListener?this.reloadListener(e):this.reloadUserInfo=e}_startProactiveRefresh(){this.proactiveRefresh._start()}_stopProactiveRefresh(){this.proactiveRefresh._stop()}async _updateTokensIfNecessary(e,n=!1){let r=!1;e.idToken&&e.idToken!==this.stsTokenManager.accessToken&&(this.stsTokenManager.updateFromServerResponse(e),r=!0),n&&await Qt(this),await this.auth._persistUserIfCurrent(this),r&&this.auth._notifyListenersIfCurrent(this)}async delete(){const e=await this.getIdToken();return await bt(this,Ff(this.auth,{idToken:e})),this.stsTokenManager.clearRefreshToken(),this.auth.signOut()}toJSON(){return Object.assign(Object.assign({uid:this.uid,email:this.email||void 0,emailVerified:this.emailVerified,displayName:this.displayName||void 0,isAnonymous:this.isAnonymous,photoURL:this.photoURL||void 0,phoneNumber:this.phoneNumber||void 0,tenantId:this.tenantId||void 0,providerData:this.providerData.map(e=>Object.assign({},e)),stsTokenManager:this.stsTokenManager.toJSON(),_redirectEventId:this._redirectEventId},this.metadata.toJSON()),{apiKey:this.auth.config.apiKey,appName:this.auth.name})}get refreshToken(){return this.stsTokenManager.refreshToken||""}static _fromJSON(e,n){var r,s,i,o,a,l,c,u;const v=(r=n.displayName)!==null&&r!==void 0?r:void 0,g=(s=n.email)!==null&&s!==void 0?s:void 0,b=(i=n.phoneNumber)!==null&&i!==void 0?i:void 0,m=(o=n.photoURL)!==null&&o!==void 0?o:void 0,p=(a=n.tenantId)!==null&&a!==void 0?a:void 0,w=(l=n._redirectEventId)!==null&&l!==void 0?l:void 0,x=(c=n.createdAt)!==null&&c!==void 0?c:void 0,S=(u=n.lastLoginAt)!==null&&u!==void 0?u:void 0,{uid:C,emailVerified:D,isAnonymous:M,providerData:k,stsTokenManager:z}=n;I(C&&z,e,"internal-error");const F=vt.fromJSON(this.name,z);I(typeof C=="string",e,"internal-error"),xe(v,e.name),xe(g,e.name),I(typeof D=="boolean",e,"internal-error"),I(typeof M=="boolean",e,"internal-error"),xe(b,e.name),xe(m,e.name),xe(p,e.name),xe(w,e.name),xe(x,e.name),xe(S,e.name);const A=new Me({uid:C,auth:e,email:g,emailVerified:D,displayName:v,isAnonymous:M,photoURL:m,phoneNumber:b,tenantId:p,stsTokenManager:F,createdAt:x,lastLoginAt:S});return k&&Array.isArray(k)&&(A.providerData=k.map(P=>Object.assign({},P))),w&&(A._redirectEventId=w),A}static async _fromIdTokenResponse(e,n,r=!1){const s=new vt;s.updateFromServerResponse(n);const i=new Me({uid:n.localId,auth:e,stsTokenManager:s,isAnonymous:r});return await Qt(i),i}}/**
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
 */function jt(t,e,n){return`firebase:${t}:${e}:${n}`}class We{constructor(e,n,r){this.persistence=e,this.auth=n,this.userKey=r;const{config:s,name:i}=this.auth;this.fullUserKey=jt(this.userKey,s.apiKey,i),this.fullPersistenceKey=jt("persistence",s.apiKey,i),this.boundEventHandler=n._onStorageEvent.bind(n),this.persistence._addListener(this.fullUserKey,this.boundEventHandler)}setCurrentUser(e){return this.persistence._set(this.fullUserKey,e.toJSON())}async getCurrentUser(){const e=await this.persistence._get(this.fullUserKey);return e?Me._fromJSON(this.auth,e):null}removeCurrentUser(){return this.persistence._remove(this.fullUserKey)}savePersistenceForRedirect(){return this.persistence._set(this.fullPersistenceKey,this.persistence.type)}async setPersistence(e){if(this.persistence===e)return;const n=await this.getCurrentUser();if(await this.removeCurrentUser(),this.persistence=e,n)return this.setCurrentUser(n)}delete(){this.persistence._removeListener(this.fullUserKey,this.boundEventHandler)}static async create(e,n,r="authUser"){if(!n.length)return new We(ue(As),e,r);const s=(await Promise.all(n.map(async c=>{if(await c._isAvailable())return c}))).filter(c=>c);let i=s[0]||ue(As);const o=jt(r,e.config.apiKey,e.name);let a=null;for(const c of n)try{const u=await c._get(o);if(u){const v=Me._fromJSON(e,u);c!==i&&(a=v),i=c;break}}catch{}const l=s.filter(c=>c._shouldAllowMigration);return!i._shouldAllowMigration||!l.length?new We(i,e,r):(i=l[0],a&&await i._set(o,a.toJSON()),await Promise.all(n.map(async c=>{if(c!==i)try{await c._remove(o)}catch{}})),new We(i,e,r))}}/**
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
 */function Os(t){const e=t.toLowerCase();if(e.includes("opera/")||e.includes("opr/")||e.includes("opios/"))return"Opera";if(io(e))return"IEMobile";if(e.includes("msie")||e.includes("trident/"))return"IE";if(e.includes("edge/"))return"Edge";if(ro(e))return"Firefox";if(e.includes("silk/"))return"Silk";if(ao(e))return"Blackberry";if(lo(e))return"Webos";if($r(e))return"Safari";if((e.includes("chrome/")||so(e))&&!e.includes("edge/"))return"Chrome";if(oo(e))return"Android";{const n=/([a-zA-Z\d\.]+)\/[a-zA-Z\d\.]*$/,r=t.match(n);if(r?.length===2)return r[1]}return"Other"}function ro(t=X()){return/firefox\//i.test(t)}function $r(t=X()){const e=t.toLowerCase();return e.includes("safari/")&&!e.includes("chrome/")&&!e.includes("crios/")&&!e.includes("android")}function so(t=X()){return/crios\//i.test(t)}function io(t=X()){return/iemobile/i.test(t)}function oo(t=X()){return/android/i.test(t)}function ao(t=X()){return/blackberry/i.test(t)}function lo(t=X()){return/webos/i.test(t)}function fn(t=X()){return/iphone|ipad|ipod/i.test(t)||/macintosh/i.test(t)&&/mobile/i.test(t)}function Xf(t=X()){var e;return fn(t)&&!!(!((e=window.navigator)===null||e===void 0)&&e.standalone)}function Yf(){return od()&&document.documentMode===10}function co(t=X()){return fn(t)||oo(t)||lo(t)||ao(t)||/windows phone/i.test(t)||io(t)}function Qf(){try{return!!(window&&window!==window.top)}catch{return!1}}/**
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
 */function uo(t,e=[]){let n;switch(t){case"Browser":n=Os(X());break;case"Worker":n=`${Os(X())}-${t}`;break;default:n=t}const r=e.length?e.join(","):"FirebaseCore-web";return`${n}/JsCore/${un}/${r}`}/**
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
 */class Zf{constructor(e){this.auth=e,this.queue=[]}pushCallback(e,n){const r=i=>new Promise((o,a)=>{try{const l=e(i);o(l)}catch(l){a(l)}});r.onAbort=n,this.queue.push(r);const s=this.queue.length-1;return()=>{this.queue[s]=()=>Promise.resolve()}}async runMiddleware(e){var n;if(this.auth.currentUser===e)return;const r=[];try{for(const s of this.queue)await s(e),s.onAbort&&r.push(s.onAbort)}catch(s){r.reverse();for(const i of r)try{i()}catch{}throw this.auth._errorFactory.create("login-blocked",{originalMessage:(n=s)===null||n===void 0?void 0:n.message})}}}/**
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
 */class eh{constructor(e,n,r){this.app=e,this.heartbeatServiceProvider=n,this.config=r,this.currentUser=null,this.emulatorConfig=null,this.operations=Promise.resolve(),this.authStateSubscription=new Ns(this),this.idTokenSubscription=new Ns(this),this.beforeStateQueue=new Zf(this),this.redirectUser=null,this.isProactiveRefreshEnabled=!1,this._canInitEmulator=!0,this._isInitialized=!1,this._deleted=!1,this._initializationPromise=null,this._popupRedirectResolver=null,this._errorFactory=Xi,this.lastNotifiedUid=void 0,this.languageCode=null,this.tenantId=null,this.settings={appVerificationDisabledForTesting:!1},this.frameworks=[],this.name=e.name,this.clientVersion=r.sdkClientVersion}_initializeWithPersistence(e,n){return n&&(this._popupRedirectResolver=ue(n)),this._initializationPromise=this.queue(async()=>{var r,s;if(!this._deleted&&(this.persistenceManager=await We.create(this,e),!this._deleted)){if(!((r=this._popupRedirectResolver)===null||r===void 0)&&r._shouldInitProactively)try{await this._popupRedirectResolver._initialize(this)}catch{}await this.initializeCurrentUser(n),this.lastNotifiedUid=((s=this.currentUser)===null||s===void 0?void 0:s.uid)||null,!this._deleted&&(this._isInitialized=!0)}}),this._initializationPromise}async _onStorageEvent(){if(this._deleted)return;const e=await this.assertedPersistence.getCurrentUser();if(!(!this.currentUser&&!e)){if(this.currentUser&&e&&this.currentUser.uid===e.uid){this._currentUser._assign(e),await this.currentUser.getIdToken();return}await this._updateCurrentUser(e,!0)}}async initializeCurrentUser(e){var n;const r=await this.assertedPersistence.getCurrentUser();let s=r,i=!1;if(e&&this.config.authDomain){await this.getOrInitRedirectPersistenceManager();const o=(n=this.redirectUser)===null||n===void 0?void 0:n._redirectEventId,a=s?._redirectEventId,l=await this.tryRedirectSignIn(e);(!o||o===a)&&l?.user&&(s=l.user,i=!0)}if(!s)return this.directlySetCurrentUser(null);if(!s._redirectEventId){if(i)try{await this.beforeStateQueue.runMiddleware(s)}catch(o){s=r,this._popupRedirectResolver._overrideRedirectResult(this,()=>Promise.reject(o))}return s?this.reloadAndSetCurrentUserOrClear(s):this.directlySetCurrentUser(null)}return I(this._popupRedirectResolver,this,"argument-error"),await this.getOrInitRedirectPersistenceManager(),this.redirectUser&&this.redirectUser._redirectEventId===s._redirectEventId?this.directlySetCurrentUser(s):this.reloadAndSetCurrentUserOrClear(s)}async tryRedirectSignIn(e){let n=null;try{n=await this._popupRedirectResolver._completeRedirectFn(this,e,!0)}catch{await this._setRedirectUser(null)}return n}async reloadAndSetCurrentUserOrClear(e){var n;try{await Qt(e)}catch(r){if(((n=r)===null||n===void 0?void 0:n.code)!=="auth/network-request-failed")return this.directlySetCurrentUser(null)}return this.directlySetCurrentUser(e)}useDeviceLanguage(){this.languageCode=Lf()}async _delete(){this._deleted=!0}async updateCurrentUser(e){const n=e?oe(e):null;return n&&I(n.auth.config.apiKey===this.config.apiKey,this,"invalid-user-token"),this._updateCurrentUser(n&&n._clone(this))}async _updateCurrentUser(e,n=!1){if(!this._deleted)return e&&I(this.tenantId===e.tenantId,this,"tenant-id-mismatch"),n||await this.beforeStateQueue.runMiddleware(e),this.queue(async()=>{await this.directlySetCurrentUser(e),this.notifyAuthListeners()})}async signOut(){return await this.beforeStateQueue.runMiddleware(null),(this.redirectPersistenceManager||this._popupRedirectResolver)&&await this._setRedirectUser(null),this._updateCurrentUser(null,!0)}setPersistence(e){return this.queue(async()=>{await this.assertedPersistence.setPersistence(ue(e))})}_getPersistence(){return this.assertedPersistence.persistence.type}_updateErrorMap(e){this._errorFactory=new xt("auth","Firebase",e())}onAuthStateChanged(e,n,r){return this.registerStateListener(this.authStateSubscription,e,n,r)}beforeAuthStateChanged(e,n){return this.beforeStateQueue.pushCallback(e,n)}onIdTokenChanged(e,n,r){return this.registerStateListener(this.idTokenSubscription,e,n,r)}toJSON(){var e;return{apiKey:this.config.apiKey,authDomain:this.config.authDomain,appName:this.name,currentUser:(e=this._currentUser)===null||e===void 0?void 0:e.toJSON()}}async _setRedirectUser(e,n){const r=await this.getOrInitRedirectPersistenceManager(n);return e===null?r.removeCurrentUser():r.setCurrentUser(e)}async getOrInitRedirectPersistenceManager(e){if(!this.redirectPersistenceManager){const n=e&&ue(e)||this._popupRedirectResolver;I(n,this,"argument-error"),this.redirectPersistenceManager=await We.create(this,[ue(n._redirectPersistence)],"redirectUser"),this.redirectUser=await this.redirectPersistenceManager.getCurrentUser()}return this.redirectPersistenceManager}async _redirectUserForId(e){var n,r;return this._isInitialized&&await this.queue(async()=>{}),((n=this._currentUser)===null||n===void 0?void 0:n._redirectEventId)===e?this._currentUser:((r=this.redirectUser)===null||r===void 0?void 0:r._redirectEventId)===e?this.redirectUser:null}async _persistUserIfCurrent(e){if(e===this.currentUser)return this.queue(async()=>this.directlySetCurrentUser(e))}_notifyListenersIfCurrent(e){e===this.currentUser&&this.notifyAuthListeners()}_key(){return`${this.config.authDomain}:${this.config.apiKey}:${this.name}`}_startProactiveRefresh(){this.isProactiveRefreshEnabled=!0,this.currentUser&&this._currentUser._startProactiveRefresh()}_stopProactiveRefresh(){this.isProactiveRefreshEnabled=!1,this.currentUser&&this._currentUser._stopProactiveRefresh()}get _currentUser(){return this.currentUser}notifyAuthListeners(){var e,n;if(!this._isInitialized)return;this.idTokenSubscription.next(this.currentUser);const r=(n=(e=this.currentUser)===null||e===void 0?void 0:e.uid)!==null&&n!==void 0?n:null;this.lastNotifiedUid!==r&&(this.lastNotifiedUid=r,this.authStateSubscription.next(this.currentUser))}registerStateListener(e,n,r,s){if(this._deleted)return()=>{};const i=typeof n=="function"?n:n.next.bind(n),o=this._isInitialized?Promise.resolve():this._initializationPromise;return I(o,this,"internal-error"),o.then(()=>i(this.currentUser)),typeof n=="function"?e.addObserver(n,r,s):e.addObserver(n)}async directlySetCurrentUser(e){this.currentUser&&this.currentUser!==e&&this._currentUser._stopProactiveRefresh(),e&&this.isProactiveRefreshEnabled&&e._startProactiveRefresh(),this.currentUser=e,e?await this.assertedPersistence.setCurrentUser(e):await this.assertedPersistence.removeCurrentUser()}queue(e){return this.operations=this.operations.then(e,e),this.operations}get assertedPersistence(){return I(this.persistenceManager,this,"internal-error"),this.persistenceManager}_logFramework(e){!e||this.frameworks.includes(e)||(this.frameworks.push(e),this.frameworks.sort(),this.clientVersion=uo(this.config.clientPlatform,this._getFrameworks()))}_getFrameworks(){return this.frameworks}async _getAdditionalHeaders(){var e;const n={["X-Client-Version"]:this.clientVersion};this.app.options.appId&&(n["X-Firebase-gmpid"]=this.app.options.appId);const r=await((e=this.heartbeatServiceProvider.getImmediate({optional:!0}))===null||e===void 0?void 0:e.getHeartbeatsHeader());return r&&(n["X-Firebase-Client"]=r),n}}function $t(t){return oe(t)}class Ns{constructor(e){this.auth=e,this.observer=null,this.addObserver=_d(n=>this.observer=n)}get next(){return I(this.observer,this.auth,"internal-error"),this.observer.next.bind(this.observer)}}function th(t,e,n){const r=$t(t);I(r._canInitEmulator,r,"emulator-config-failed"),I(/^https?:\/\//.test(e),r,"invalid-emulator-scheme");const s=!!n?.disableWarnings,i=fo(e),{host:o,port:a}=nh(e),l=a===null?"":`:${a}`;r.config.emulator={url:`${i}//${o}${l}/`},r.settings.appVerificationDisabledForTesting=!0,r.emulatorConfig=Object.freeze({host:o,port:a,protocol:i.replace(":",""),options:Object.freeze({disableWarnings:s})}),s||rh()}function fo(t){const e=t.indexOf(":");return e<0?"":t.substr(0,e+1)}function nh(t){const e=fo(t),n=/(\/\/)?([^?#/]+)/.exec(t.substr(e.length));if(!n)return{host:"",port:null};const r=n[2].split("@").pop()||"",s=/^(\[[^\]]+\])(:|$)/.exec(r);if(s){const i=s[1];return{host:i,port:Rs(r.substr(i.length+1))}}else{const[i,o]=r.split(":");return{host:i,port:Rs(o)}}}function Rs(t){if(!t)return null;const e=Number(t);return isNaN(e)?null:e}function rh(){function t(){const e=document.createElement("p"),n=e.style;e.innerText="Running in emulator mode. Do not use with production credentials.",n.position="fixed",n.width="100%",n.backgroundColor="#ffffff",n.border=".1em solid #000000",n.color="#b50000",n.bottom="0px",n.left="0px",n.margin="0px",n.zIndex="10000",n.textAlign="center",e.classList.add("firebase-emulator-warning"),document.body.appendChild(e)}typeof console<"u"&&typeof console.info=="function"&&console.info("WARNING: You are using the Auth Emulator, which is intended for local testing only.  Do not use with production credentials."),typeof window<"u"&&typeof document<"u"&&(document.readyState==="loading"?window.addEventListener("DOMContentLoaded",t):t())}/**
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
 */class kr{constructor(e,n){this.providerId=e,this.signInMethod=n}toJSON(){return ce("not implemented")}_getIdTokenResponse(e){return ce("not implemented")}_linkToIdToken(e,n){return ce("not implemented")}_getReauthenticationResolver(e){return ce("not implemented")}}async function sh(t,e){return et(t,"POST","/v1/accounts:update",e)}/**
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
 */async function ih(t,e){return dn(t,"POST","/v1/accounts:signInWithPassword",St(t,e))}async function oh(t,e){return et(t,"POST","/v1/accounts:sendOobCode",St(t,e))}async function ah(t,e){return oh(t,e)}/**
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
 */async function lh(t,e){return dn(t,"POST","/v1/accounts:signInWithEmailLink",St(t,e))}async function ch(t,e){return dn(t,"POST","/v1/accounts:signInWithEmailLink",St(t,e))}/**
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
 */class yt extends kr{constructor(e,n,r,s=null){super("password",r),this._email=e,this._password=n,this._tenantId=s}static _fromEmailAndPassword(e,n){return new yt(e,n,"password")}static _fromEmailAndCode(e,n,r=null){return new yt(e,n,"emailLink",r)}toJSON(){return{email:this._email,password:this._password,signInMethod:this.signInMethod,tenantId:this._tenantId}}static fromJSON(e){const n=typeof e=="string"?JSON.parse(e):e;if(n?.email&&n?.password){if(n.signInMethod==="password")return this._fromEmailAndPassword(n.email,n.password);if(n.signInMethod==="emailLink")return this._fromEmailAndCode(n.email,n.password,n.tenantId)}return null}async _getIdTokenResponse(e){switch(this.signInMethod){case"password":return ih(e,{returnSecureToken:!0,email:this._email,password:this._password});case"emailLink":return lh(e,{email:this._email,oobCode:this._password});default:re(e,"internal-error")}}async _linkToIdToken(e,n){switch(this.signInMethod){case"password":return sh(e,{idToken:n,returnSecureToken:!0,email:this._email,password:this._password});case"emailLink":return ch(e,{idToken:n,email:this._email,oobCode:this._password});default:re(e,"internal-error")}}_getReauthenticationResolver(e){return this._getIdTokenResponse(e)}}/**
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
 */async function Je(t,e){return dn(t,"POST","/v1/accounts:signInWithIdp",St(t,e))}/**
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
 */const uh="http://localhost";class je extends kr{constructor(){super(...arguments),this.pendingToken=null}static _fromParams(e){const n=new je(e.providerId,e.signInMethod);return e.idToken||e.accessToken?(e.idToken&&(n.idToken=e.idToken),e.accessToken&&(n.accessToken=e.accessToken),e.nonce&&!e.pendingToken&&(n.nonce=e.nonce),e.pendingToken&&(n.pendingToken=e.pendingToken)):e.oauthToken&&e.oauthTokenSecret?(n.accessToken=e.oauthToken,n.secret=e.oauthTokenSecret):re("argument-error"),n}toJSON(){return{idToken:this.idToken,accessToken:this.accessToken,secret:this.secret,nonce:this.nonce,pendingToken:this.pendingToken,providerId:this.providerId,signInMethod:this.signInMethod}}static fromJSON(e){const n=typeof e=="string"?JSON.parse(e):e,{providerId:r,signInMethod:s}=n,i=xr(n,["providerId","signInMethod"]);if(!r||!s)return null;const o=new je(r,s);return o.idToken=i.idToken||void 0,o.accessToken=i.accessToken||void 0,o.secret=i.secret,o.nonce=i.nonce,o.pendingToken=i.pendingToken||null,o}_getIdTokenResponse(e){const n=this.buildRequest();return Je(e,n)}_linkToIdToken(e,n){const r=this.buildRequest();return r.idToken=n,Je(e,r)}_getReauthenticationResolver(e){const n=this.buildRequest();return n.autoCreate=!1,Je(e,n)}buildRequest(){const e={requestUri:uh,returnSecureToken:!0};if(this.pendingToken)e.pendingToken=this.pendingToken;else{const n={};this.idToken&&(n.id_token=this.idToken),this.accessToken&&(n.access_token=this.accessToken),this.secret&&(n.oauth_token_secret=this.secret),n.providerId=this.providerId,this.nonce&&!this.pendingToken&&(n.nonce=this.nonce),e.postBody=Et(n)}return e}}/**
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
 */function dh(t){switch(t){case"recoverEmail":return"RECOVER_EMAIL";case"resetPassword":return"PASSWORD_RESET";case"signIn":return"EMAIL_SIGNIN";case"verifyEmail":return"VERIFY_EMAIL";case"verifyAndChangeEmail":return"VERIFY_AND_CHANGE_EMAIL";case"revertSecondFactorAddition":return"REVERT_SECOND_FACTOR_ADDITION";default:return null}}function fh(t){const e=ct(ut(t)).link,n=e?ct(ut(e)).deep_link_id:null,r=ct(ut(t)).deep_link_id;return(r?ct(ut(r)).link:null)||r||n||e||t}class Tr{constructor(e){var n,r,s,i,o,a;const l=ct(ut(e)),c=(n=l.apiKey)!==null&&n!==void 0?n:null,u=(r=l.oobCode)!==null&&r!==void 0?r:null,v=dh((s=l.mode)!==null&&s!==void 0?s:null);I(c&&u&&v,"argument-error"),this.apiKey=c,this.operation=v,this.code=u,this.continueUrl=(i=l.continueUrl)!==null&&i!==void 0?i:null,this.languageCode=(o=l.languageCode)!==null&&o!==void 0?o:null,this.tenantId=(a=l.tenantId)!==null&&a!==void 0?a:null}static parseLink(e){const n=fh(e);try{return new Tr(n)}catch{return null}}}/**
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
 */class tt{constructor(){this.providerId=tt.PROVIDER_ID}static credential(e,n){return yt._fromEmailAndPassword(e,n)}static credentialWithLink(e,n){const r=Tr.parseLink(n);return I(r,"argument-error"),yt._fromEmailAndCode(e,r.code,r.tenantId)}}tt.PROVIDER_ID="password";tt.EMAIL_PASSWORD_SIGN_IN_METHOD="password";tt.EMAIL_LINK_SIGN_IN_METHOD="emailLink";/**
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
 */class Cr{constructor(e){this.providerId=e,this.defaultLanguageCode=null,this.customParameters={}}setDefaultLanguage(e){this.defaultLanguageCode=e}setCustomParameters(e){return this.customParameters=e,this}getCustomParameters(){return this.customParameters}}/**
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
 */class kt extends Cr{constructor(){super(...arguments),this.scopes=[]}addScope(e){return this.scopes.includes(e)||this.scopes.push(e),this}getScopes(){return[...this.scopes]}}/**
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
 */class Ee extends kt{constructor(){super("facebook.com")}static credential(e){return je._fromParams({providerId:Ee.PROVIDER_ID,signInMethod:Ee.FACEBOOK_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return Ee.credentialFromTaggedObject(e)}static credentialFromError(e){return Ee.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return Ee.credential(e.oauthAccessToken)}catch{return null}}}Ee.FACEBOOK_SIGN_IN_METHOD="facebook.com";Ee.PROVIDER_ID="facebook.com";/**
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
 */class ae extends kt{constructor(){super("google.com"),this.addScope("profile")}static credential(e,n){return je._fromParams({providerId:ae.PROVIDER_ID,signInMethod:ae.GOOGLE_SIGN_IN_METHOD,idToken:e,accessToken:n})}static credentialFromResult(e){return ae.credentialFromTaggedObject(e)}static credentialFromError(e){return ae.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthIdToken:n,oauthAccessToken:r}=e;if(!n&&!r)return null;try{return ae.credential(n,r)}catch{return null}}}ae.GOOGLE_SIGN_IN_METHOD="google.com";ae.PROVIDER_ID="google.com";/**
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
 */class le extends kt{constructor(){super("github.com")}static credential(e){return je._fromParams({providerId:le.PROVIDER_ID,signInMethod:le.GITHUB_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return le.credentialFromTaggedObject(e)}static credentialFromError(e){return le.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return le.credential(e.oauthAccessToken)}catch{return null}}}le.GITHUB_SIGN_IN_METHOD="github.com";le.PROVIDER_ID="github.com";/**
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
 */class Ie extends kt{constructor(){super("twitter.com")}static credential(e,n){return je._fromParams({providerId:Ie.PROVIDER_ID,signInMethod:Ie.TWITTER_SIGN_IN_METHOD,oauthToken:e,oauthTokenSecret:n})}static credentialFromResult(e){return Ie.credentialFromTaggedObject(e)}static credentialFromError(e){return Ie.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthAccessToken:n,oauthTokenSecret:r}=e;if(!n||!r)return null;try{return Ie.credential(n,r)}catch{return null}}}Ie.TWITTER_SIGN_IN_METHOD="twitter.com";Ie.PROVIDER_ID="twitter.com";/**
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
 */class Ke{constructor(e){this.user=e.user,this.providerId=e.providerId,this._tokenResponse=e._tokenResponse,this.operationType=e.operationType}static async _fromIdTokenResponse(e,n,r,s=!1){const i=await Me._fromIdTokenResponse(e,r,s),o=Ds(r);return new Ke({user:i,providerId:o,_tokenResponse:r,operationType:n})}static async _forOperation(e,n,r){await e._updateTokensIfNecessary(r,!0);const s=Ds(r);return new Ke({user:e,providerId:s,_tokenResponse:r,operationType:n})}}function Ds(t){return t.providerId?t.providerId:"phoneNumber"in t?"phone":null}/**
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
 */class Zt extends Ae{constructor(e,n,r,s){var i;super(n.code,n.message),this.operationType=r,this.user=s,Object.setPrototypeOf(this,Zt.prototype),this.customData={appName:e.name,tenantId:(i=e.tenantId)!==null&&i!==void 0?i:void 0,_serverResponse:n.customData._serverResponse,operationType:r}}static _fromErrorAndOperation(e,n,r,s){return new Zt(e,n,r,s)}}function ho(t,e,n,r){return(e==="reauthenticate"?n._getReauthenticationResolver(t):n._getIdTokenResponse(t)).catch(i=>{throw i.code==="auth/multi-factor-auth-required"?Zt._fromErrorAndOperation(t,i,e,r):i})}async function hh(t,e,n=!1){const r=await bt(t,e._linkToIdToken(t.auth,await t.getIdToken()),n);return Ke._forOperation(t,"link",r)}/**
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
 */async function gh(t,e,n=!1){var r;const{auth:s}=t,i="reauthenticate";try{const o=await bt(t,ho(s,i,e,t),n);I(o.idToken,s,"internal-error");const a=Sr(o.idToken);I(a,s,"internal-error");const{sub:l}=a;return I(t.uid===l,s,"user-mismatch"),Ke._forOperation(t,i,o)}catch(o){throw((r=o)===null||r===void 0?void 0:r.code)==="auth/user-not-found"&&re(s,"user-mismatch"),o}}/**
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
 */async function go(t,e,n=!1){const r="signIn",s=await ho(t,r,e),i=await Ke._fromIdTokenResponse(t,r,s);return n||await t._updateCurrentUser(i.user),i}async function mh(t,e){return go($t(t),e)}/**
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
 */function ph(t,e,n){var r;I(((r=n.url)===null||r===void 0?void 0:r.length)>0,t,"invalid-continue-uri"),I(typeof n.dynamicLinkDomain>"u"||n.dynamicLinkDomain.length>0,t,"invalid-dynamic-link-domain"),e.continueUrl=n.url,e.dynamicLinkDomain=n.dynamicLinkDomain,e.canHandleCodeInApp=n.handleCodeInApp,n.iOS&&(I(n.iOS.bundleId.length>0,t,"missing-ios-bundle-id"),e.iOSBundleId=n.iOS.bundleId),n.android&&(I(n.android.packageName.length>0,t,"missing-android-pkg-name"),e.androidInstallApp=n.android.installApp,e.androidMinimumVersionCode=n.android.minimumVersion,e.androidPackageName=n.android.packageName)}/**
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
 */async function bh(t,e,n){const r=oe(t),s={requestType:"PASSWORD_RESET",email:e};n&&ph(r,s,n),await ah(r,s)}function vh(t,e,n){return mh(oe(t),tt.credential(e,n))}function yh(t,e,n,r){return oe(t).onIdTokenChanged(e,n,r)}function _h(t,e,n){return oe(t).beforeAuthStateChanged(e,n)}function wh(t,e,n,r){return oe(t).onAuthStateChanged(e,n,r)}function xh(t){return oe(t).signOut()}const en="__sak";/**
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
 */class mo{constructor(e,n){this.storageRetriever=e,this.type=n}_isAvailable(){try{return this.storage?(this.storage.setItem(en,"1"),this.storage.removeItem(en),Promise.resolve(!0)):Promise.resolve(!1)}catch{return Promise.resolve(!1)}}_set(e,n){return this.storage.setItem(e,JSON.stringify(n)),Promise.resolve()}_get(e){const n=this.storage.getItem(e);return Promise.resolve(n?JSON.parse(n):null)}_remove(e){return this.storage.removeItem(e),Promise.resolve()}get storage(){return this.storageRetriever()}}/**
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
 */function Eh(){const t=X();return $r(t)||fn(t)}const Ih=1e3,Sh=10;class po extends mo{constructor(){super(()=>window.localStorage,"LOCAL"),this.boundEventHandler=(e,n)=>this.onStorageEvent(e,n),this.listeners={},this.localCache={},this.pollTimer=null,this.safariLocalStorageNotSynced=Eh()&&Qf(),this.fallbackToPolling=co(),this._shouldAllowMigration=!0}forAllChangedKeys(e){for(const n of Object.keys(this.listeners)){const r=this.storage.getItem(n),s=this.localCache[n];r!==s&&e(n,s,r)}}onStorageEvent(e,n=!1){if(!e.key){this.forAllChangedKeys((o,a,l)=>{this.notifyListeners(o,l)});return}const r=e.key;if(n?this.detachListener():this.stopPolling(),this.safariLocalStorageNotSynced){const o=this.storage.getItem(r);if(e.newValue!==o)e.newValue!==null?this.storage.setItem(r,e.newValue):this.storage.removeItem(r);else if(this.localCache[r]===e.newValue&&!n)return}const s=()=>{const o=this.storage.getItem(r);!n&&this.localCache[r]===o||this.notifyListeners(r,o)},i=this.storage.getItem(r);Yf()&&i!==e.newValue&&e.newValue!==e.oldValue?setTimeout(s,Sh):s()}notifyListeners(e,n){this.localCache[e]=n;const r=this.listeners[e];if(r)for(const s of Array.from(r))s(n&&JSON.parse(n))}startPolling(){this.stopPolling(),this.pollTimer=setInterval(()=>{this.forAllChangedKeys((e,n,r)=>{this.onStorageEvent(new StorageEvent("storage",{key:e,oldValue:n,newValue:r}),!0)})},Ih)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}attachListener(){window.addEventListener("storage",this.boundEventHandler)}detachListener(){window.removeEventListener("storage",this.boundEventHandler)}_addListener(e,n){Object.keys(this.listeners).length===0&&(this.fallbackToPolling?this.startPolling():this.attachListener()),this.listeners[e]||(this.listeners[e]=new Set,this.localCache[e]=this.storage.getItem(e)),this.listeners[e].add(n)}_removeListener(e,n){this.listeners[e]&&(this.listeners[e].delete(n),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&(this.detachListener(),this.stopPolling())}async _set(e,n){await super._set(e,n),this.localCache[e]=JSON.stringify(n)}async _get(e){const n=await super._get(e);return this.localCache[e]=JSON.stringify(n),n}async _remove(e){await super._remove(e),delete this.localCache[e]}}po.type="LOCAL";const $h=po;/**
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
 */function kh(t){return Promise.all(t.map(async e=>{try{return{fulfilled:!0,value:await e}}catch(n){return{fulfilled:!1,reason:n}}}))}/**
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
 */class hn{constructor(e){this.eventTarget=e,this.handlersMap={},this.boundEventHandler=this.handleEvent.bind(this)}static _getInstance(e){const n=this.receivers.find(s=>s.isListeningto(e));if(n)return n;const r=new hn(e);return this.receivers.push(r),r}isListeningto(e){return this.eventTarget===e}async handleEvent(e){const n=e,{eventId:r,eventType:s,data:i}=n.data,o=this.handlersMap[s];if(!o?.size)return;n.ports[0].postMessage({status:"ack",eventId:r,eventType:s});const a=Array.from(o).map(async c=>c(n.origin,i)),l=await kh(a);n.ports[0].postMessage({status:"done",eventId:r,eventType:s,response:l})}_subscribe(e,n){Object.keys(this.handlersMap).length===0&&this.eventTarget.addEventListener("message",this.boundEventHandler),this.handlersMap[e]||(this.handlersMap[e]=new Set),this.handlersMap[e].add(n)}_unsubscribe(e,n){this.handlersMap[e]&&n&&this.handlersMap[e].delete(n),(!n||this.handlersMap[e].size===0)&&delete this.handlersMap[e],Object.keys(this.handlersMap).length===0&&this.eventTarget.removeEventListener("message",this.boundEventHandler)}}hn.receivers=[];/**
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
 */function Ar(t="",e=10){let n="";for(let r=0;r<e;r++)n+=Math.floor(Math.random()*10);return t+n}/**
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
 */class Th{constructor(e){this.target=e,this.handlers=new Set}removeMessageHandler(e){e.messageChannel&&(e.messageChannel.port1.removeEventListener("message",e.onMessage),e.messageChannel.port1.close()),this.handlers.delete(e)}async _send(e,n,r=50){const s=typeof MessageChannel<"u"?new MessageChannel:null;if(!s)throw new Error("connection_unavailable");let i,o;return new Promise((a,l)=>{const c=Ar("",20);s.port1.start();const u=setTimeout(()=>{l(new Error("unsupported_event"))},r);o={messageChannel:s,onMessage(v){const g=v;if(g.data.eventId===c)switch(g.data.status){case"ack":clearTimeout(u),i=setTimeout(()=>{l(new Error("timeout"))},3e3);break;case"done":clearTimeout(i),a(g.data.response);break;default:clearTimeout(u),clearTimeout(i),l(new Error("invalid_response"));break}}},this.handlers.add(o),s.port1.addEventListener("message",o.onMessage),this.target.postMessage({eventType:e,eventId:c,data:n},[s.port2])}).finally(()=>{o&&this.removeMessageHandler(o)})}}/**
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
 */function ie(){return window}function Ch(t){ie().location.href=t}/**
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
 */function yo(){return typeof ie().WorkerGlobalScope<"u"&&typeof ie().importScripts=="function"}async function Ah(){if(!navigator?.serviceWorker)return null;try{return(await navigator.serviceWorker.ready).active}catch{return null}}function Oh(){var t;return((t=navigator?.serviceWorker)===null||t===void 0?void 0:t.controller)||null}function Nh(){return yo()?self:null}/**
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
 */const _o="firebaseLocalStorageDb",Rh=1,tn="firebaseLocalStorage",wo="fbase_key";class Tt{constructor(e){this.request=e}toPromise(){return new Promise((e,n)=>{this.request.addEventListener("success",()=>{e(this.request.result)}),this.request.addEventListener("error",()=>{n(this.request.error)})})}}function gn(t,e){return t.transaction([tn],e?"readwrite":"readonly").objectStore(tn)}function Dh(){const t=indexedDB.deleteDatabase(_o);return new Tt(t).toPromise()}function lr(){const t=indexedDB.open(_o,Rh);return new Promise((e,n)=>{t.addEventListener("error",()=>{n(t.error)}),t.addEventListener("upgradeneeded",()=>{const r=t.result;try{r.createObjectStore(tn,{keyPath:wo})}catch(s){n(s)}}),t.addEventListener("success",async()=>{const r=t.result;r.objectStoreNames.contains(tn)?e(r):(r.close(),await Dh(),e(await lr()))})})}async function Ps(t,e,n){const r=gn(t,!0).put({[wo]:e,value:n});return new Tt(r).toPromise()}async function Ph(t,e){const n=gn(t,!1).get(e),r=await new Tt(n).toPromise();return r===void 0?null:r.value}function Ls(t,e){const n=gn(t,!0).delete(e);return new Tt(n).toPromise()}const Lh=800,Mh=3;class xo{constructor(){this.type="LOCAL",this._shouldAllowMigration=!0,this.listeners={},this.localCache={},this.pollTimer=null,this.pendingWrites=0,this.receiver=null,this.sender=null,this.serviceWorkerReceiverAvailable=!1,this.activeServiceWorker=null,this._workerInitializationPromise=this.initializeServiceWorkerMessaging().then(()=>{},()=>{})}async _openDb(){return this.db?this.db:(this.db=await lr(),this.db)}async _withRetries(e){let n=0;for(;;)try{const r=await this._openDb();return await e(r)}catch(r){if(n++>Mh)throw r;this.db&&(this.db.close(),this.db=void 0)}}async initializeServiceWorkerMessaging(){return yo()?this.initializeReceiver():this.initializeSender()}async initializeReceiver(){this.receiver=hn._getInstance(Nh()),this.receiver._subscribe("keyChanged",async(e,n)=>({keyProcessed:(await this._poll()).includes(n.key)})),this.receiver._subscribe("ping",async(e,n)=>["keyChanged"])}async initializeSender(){var e,n;if(this.activeServiceWorker=await Ah(),!this.activeServiceWorker)return;this.sender=new Th(this.activeServiceWorker);const r=await this.sender._send("ping",{},800);!r||((e=r[0])===null||e===void 0?void 0:e.fulfilled)&&((n=r[0])===null||n===void 0?void 0:n.value.includes("keyChanged"))&&(this.serviceWorkerReceiverAvailable=!0)}async notifyServiceWorker(e){if(!(!this.sender||!this.activeServiceWorker||Oh()!==this.activeServiceWorker))try{await this.sender._send("keyChanged",{key:e},this.serviceWorkerReceiverAvailable?800:50)}catch{}}async _isAvailable(){try{if(!indexedDB)return!1;const e=await lr();return await Ps(e,en,"1"),await Ls(e,en),!0}catch{}return!1}async _withPendingWrite(e){this.pendingWrites++;try{await e()}finally{this.pendingWrites--}}async _set(e,n){return this._withPendingWrite(async()=>(await this._withRetries(r=>Ps(r,e,n)),this.localCache[e]=n,this.notifyServiceWorker(e)))}async _get(e){const n=await this._withRetries(r=>Ph(r,e));return this.localCache[e]=n,n}async _remove(e){return this._withPendingWrite(async()=>(await this._withRetries(n=>Ls(n,e)),delete this.localCache[e],this.notifyServiceWorker(e)))}async _poll(){const e=await this._withRetries(s=>{const i=gn(s,!1).getAll();return new Tt(i).toPromise()});if(!e)return[];if(this.pendingWrites!==0)return[];const n=[],r=new Set;for(const{fbase_key:s,value:i}of e)r.add(s),JSON.stringify(this.localCache[s])!==JSON.stringify(i)&&(this.notifyListeners(s,i),n.push(s));for(const s of Object.keys(this.localCache))this.localCache[s]&&!r.has(s)&&(this.notifyListeners(s,null),n.push(s));return n}notifyListeners(e,n){this.localCache[e]=n;const r=this.listeners[e];if(r)for(const s of Array.from(r))s(n)}startPolling(){this.stopPolling(),this.pollTimer=setInterval(async()=>this._poll(),Lh)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}_addListener(e,n){Object.keys(this.listeners).length===0&&this.startPolling(),this.listeners[e]||(this.listeners[e]=new Set,this._get(e)),this.listeners[e].add(n)}_removeListener(e,n){this.listeners[e]&&(this.listeners[e].delete(n),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&this.stopPolling()}}xo.type="LOCAL";const Uh=xo;/**
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
 */function jh(){var t,e;return(e=(t=document.getElementsByTagName("head"))===null||t===void 0?void 0:t[0])!==null&&e!==void 0?e:document}function Fh(t){return new Promise((e,n)=>{const r=document.createElement("script");r.setAttribute("src",t),r.onload=e,r.onerror=s=>{const i=se("internal-error");i.customData=s,n(i)},r.type="text/javascript",r.charset="UTF-8",jh().appendChild(r)})}function Bh(t){return`__${t}${Math.floor(Math.random()*1e6)}`}new It(3e4,6e4);/**
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
 */function Eo(t,e){return e?ue(e):(I(t._popupRedirectResolver,t,"argument-error"),t._popupRedirectResolver)}/**
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
 */class Or extends kr{constructor(e){super("custom","custom"),this.params=e}_getIdTokenResponse(e){return Je(e,this._buildIdpRequest())}_linkToIdToken(e,n){return Je(e,this._buildIdpRequest(n))}_getReauthenticationResolver(e){return Je(e,this._buildIdpRequest())}_buildIdpRequest(e){const n={requestUri:this.params.requestUri,sessionId:this.params.sessionId,postBody:this.params.postBody,tenantId:this.params.tenantId,pendingToken:this.params.pendingToken,returnSecureToken:!0,returnIdpCredential:!0};return e&&(n.idToken=e),n}}function Hh(t){return go(t.auth,new Or(t),t.bypassAuthState)}function zh(t){const{auth:e,user:n}=t;return I(n,e,"internal-error"),gh(n,new Or(t),t.bypassAuthState)}async function Vh(t){const{auth:e,user:n}=t;return I(n,e,"internal-error"),hh(n,new Or(t),t.bypassAuthState)}/**
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
 */class Io{constructor(e,n,r,s,i=!1){this.auth=e,this.resolver=r,this.user=s,this.bypassAuthState=i,this.pendingPromise=null,this.eventManager=null,this.filter=Array.isArray(n)?n:[n]}execute(){return new Promise(async(e,n)=>{this.pendingPromise={resolve:e,reject:n};try{this.eventManager=await this.resolver._initialize(this.auth),await this.onExecution(),this.eventManager.registerConsumer(this)}catch(r){this.reject(r)}})}async onAuthEvent(e){const{urlResponse:n,sessionId:r,postBody:s,tenantId:i,error:o,type:a}=e;if(o){this.reject(o);return}const l={auth:this.auth,requestUri:n,sessionId:r,tenantId:i||void 0,postBody:s||void 0,user:this.user,bypassAuthState:this.bypassAuthState};try{this.resolve(await this.getIdpTask(a)(l))}catch(c){this.reject(c)}}onError(e){this.reject(e)}getIdpTask(e){switch(e){case"signInViaPopup":case"signInViaRedirect":return Hh;case"linkViaPopup":case"linkViaRedirect":return Vh;case"reauthViaPopup":case"reauthViaRedirect":return zh;default:re(this.auth,"internal-error")}}resolve(e){me(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.resolve(e),this.unregisterAndCleanUp()}reject(e){me(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.reject(e),this.unregisterAndCleanUp()}unregisterAndCleanUp(){this.eventManager&&this.eventManager.unregisterConsumer(this),this.pendingPromise=null,this.cleanUp()}}/**
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
 */const Wh=new It(2e3,1e4);async function Ms(t,e,n){const r=$t(t);Of(t,e,Cr);const s=Eo(r,n);return new De(r,"signInViaPopup",e,s).executeNotNull()}class De extends Io{constructor(e,n,r,s,i){super(e,n,s,i),this.provider=r,this.authWindow=null,this.pollId=null,De.currentPopupAction&&De.currentPopupAction.cancel(),De.currentPopupAction=this}async executeNotNull(){const e=await this.execute();return I(e,this.auth,"internal-error"),e}async onExecution(){me(this.filter.length===1,"Popup operations only handle one event");const e=Ar();this.authWindow=await this.resolver._openPopup(this.auth,this.provider,this.filter[0],e),this.authWindow.associatedEvent=e,this.resolver._originValidation(this.auth).catch(n=>{this.reject(n)}),this.resolver._isIframeWebStorageSupported(this.auth,n=>{n||this.reject(se(this.auth,"web-storage-unsupported"))}),this.pollUserCancellation()}get eventId(){var e;return((e=this.authWindow)===null||e===void 0?void 0:e.associatedEvent)||null}cancel(){this.reject(se(this.auth,"cancelled-popup-request"))}cleanUp(){this.authWindow&&this.authWindow.close(),this.pollId&&window.clearTimeout(this.pollId),this.authWindow=null,this.pollId=null,De.currentPopupAction=null}pollUserCancellation(){const e=()=>{var n,r;if(!((r=(n=this.authWindow)===null||n===void 0?void 0:n.window)===null||r===void 0)&&r.closed){this.pollId=window.setTimeout(()=>{this.pollId=null,this.reject(se(this.auth,"popup-closed-by-user"))},2e3);return}this.pollId=window.setTimeout(e,Wh.get())};e()}}De.currentPopupAction=null;/**
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
 */const Jh="pendingRedirect",Ft=new Map;class qh extends Io{constructor(e,n,r=!1){super(e,["signInViaRedirect","linkViaRedirect","reauthViaRedirect","unknown"],n,void 0,r),this.eventId=null}async execute(){let e=Ft.get(this.auth._key());if(!e){try{const r=await Gh(this.resolver,this.auth)?await super.execute():null;e=()=>Promise.resolve(r)}catch(n){e=()=>Promise.reject(n)}Ft.set(this.auth._key(),e)}return this.bypassAuthState||Ft.set(this.auth._key(),()=>Promise.resolve(null)),e()}async onAuthEvent(e){if(e.type==="signInViaRedirect")return super.onAuthEvent(e);if(e.type==="unknown"){this.resolve(null);return}if(e.eventId){const n=await this.auth._redirectUserForId(e.eventId);if(n)return this.user=n,super.onAuthEvent(e);this.resolve(null)}}async onExecution(){}cleanUp(){}}async function Gh(t,e){const n=Yh(e),r=Xh(t);if(!await r._isAvailable())return!1;const s=await r._get(n)==="true";return await r._remove(n),s}function Kh(t,e){Ft.set(t._key(),e)}function Xh(t){return ue(t._redirectPersistence)}function Yh(t){return jt(Jh,t.config.apiKey,t.name)}async function Qh(t,e,n=!1){const r=$t(t),s=Eo(r,e),o=await new qh(r,s,n).execute();return o&&!n&&(delete o.user._redirectEventId,await r._persistUserIfCurrent(o.user),await r._setRedirectUser(null,e)),o}/**
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
 */const Zh=10*60*1e3;class eg{constructor(e){this.auth=e,this.cachedEventUids=new Set,this.consumers=new Set,this.queuedRedirectEvent=null,this.hasHandledPotentialRedirect=!1,this.lastProcessedEventTime=Date.now()}registerConsumer(e){this.consumers.add(e),this.queuedRedirectEvent&&this.isEventForConsumer(this.queuedRedirectEvent,e)&&(this.sendToConsumer(this.queuedRedirectEvent,e),this.saveEventToCache(this.queuedRedirectEvent),this.queuedRedirectEvent=null)}unregisterConsumer(e){this.consumers.delete(e)}onEvent(e){if(this.hasEventBeenHandled(e))return!1;let n=!1;return this.consumers.forEach(r=>{this.isEventForConsumer(e,r)&&(n=!0,this.sendToConsumer(e,r),this.saveEventToCache(e))}),this.hasHandledPotentialRedirect||!tg(e)||(this.hasHandledPotentialRedirect=!0,n||(this.queuedRedirectEvent=e,n=!0)),n}sendToConsumer(e,n){var r;if(e.error&&!So(e)){const s=((r=e.error.code)===null||r===void 0?void 0:r.split("auth/")[1])||"internal-error";n.onError(se(this.auth,s))}else n.onAuthEvent(e)}isEventForConsumer(e,n){const r=n.eventId===null||!!e.eventId&&e.eventId===n.eventId;return n.filter.includes(e.type)&&r}hasEventBeenHandled(e){return Date.now()-this.lastProcessedEventTime>=Zh&&this.cachedEventUids.clear(),this.cachedEventUids.has(Us(e))}saveEventToCache(e){this.cachedEventUids.add(Us(e)),this.lastProcessedEventTime=Date.now()}}function Us(t){return[t.type,t.eventId,t.sessionId,t.tenantId].filter(e=>e).join("-")}function So({type:t,error:e}){return t==="unknown"&&e?.code==="auth/no-auth-event"}function tg(t){switch(t.type){case"signInViaRedirect":case"linkViaRedirect":case"reauthViaRedirect":return!0;case"unknown":return So(t);default:return!1}}/**
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
 */async function ng(t,e={}){return et(t,"GET","/v1/projects",e)}/**
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
 */const rg=/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,sg=/^https?/;async function ig(t){if(t.config.emulator)return;const{authorizedDomains:e}=await ng(t);for(const n of e)try{if(og(n))return}catch{}re(t,"unauthorized-domain")}function og(t){const e=ar(),{protocol:n,hostname:r}=new URL(e);if(t.startsWith("chrome-extension://")){const o=new URL(t);return o.hostname===""&&r===""?n==="chrome-extension:"&&t.replace("chrome-extension://","")===e.replace("chrome-extension://",""):n==="chrome-extension:"&&o.hostname===r}if(!sg.test(n))return!1;if(rg.test(t))return r===t;const s=t.replace(/\./g,"\\.");return new RegExp("^(.+\\."+s+"|"+s+")$","i").test(r)}/**
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
 */const ag=new It(3e4,6e4);function js(){const t=ie().___jsl;if(t?.H){for(const e of Object.keys(t.H))if(t.H[e].r=t.H[e].r||[],t.H[e].L=t.H[e].L||[],t.H[e].r=[...t.H[e].L],t.CP)for(let n=0;n<t.CP.length;n++)t.CP[n]=null}}function lg(t){return new Promise((e,n)=>{var r,s,i;function o(){js(),gapi.load("gapi.iframes",{callback:()=>{e(gapi.iframes.getContext())},ontimeout:()=>{js(),n(se(t,"network-request-failed"))},timeout:ag.get()})}if(!((s=(r=ie().gapi)===null||r===void 0?void 0:r.iframes)===null||s===void 0)&&s.Iframe)e(gapi.iframes.getContext());else if(!((i=ie().gapi)===null||i===void 0)&&i.load)o();else{const a=Bh("iframefcb");return ie()[a]=()=>{gapi.load?o():n(se(t,"network-request-failed"))},Fh(`https://apis.google.com/js/api.js?onload=${a}`).catch(l=>n(l))}}).catch(e=>{throw Bt=null,e})}let Bt=null;function cg(t){return Bt=Bt||lg(t),Bt}/**
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
 */const ug=new It(5e3,15e3),dg="__/auth/iframe",fg="emulator/auth/iframe",hg={style:{position:"absolute",top:"-100px",width:"1px",height:"1px"},"aria-hidden":"true",tabindex:"-1"},gg=new Map([["identitytoolkit.googleapis.com","p"],["staging-identitytoolkit.sandbox.googleapis.com","s"],["test-identitytoolkit.sandbox.googleapis.com","t"]]);function mg(t){const e=t.config;I(e.authDomain,t,"auth-domain-config-required");const n=e.emulator?Ir(e,fg):`https://${t.config.authDomain}/${dg}`,r={apiKey:e.apiKey,appName:t.name,v:un},s=gg.get(t.config.apiHost);s&&(r.eid=s);const i=t._getFrameworks();return i.length&&(r.fw=i.join(",")),`${n}?${Et(r).slice(1)}`}async function pg(t){const e=await cg(t),n=ie().gapi;return I(n,t,"internal-error"),e.open({where:document.body,url:mg(t),messageHandlersFilter:n.iframes.CROSS_ORIGIN_IFRAMES_FILTER,attributes:hg,dontclear:!0},r=>new Promise(async(s,i)=>{await r.restyle({setHideOnLeave:!1});const o=se(t,"network-request-failed"),a=ie().setTimeout(()=>{i(o)},ug.get());function l(){ie().clearTimeout(a),s(r)}r.ping(l).then(l,()=>{i(o)})}))}/**
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
 */const bg={location:"yes",resizable:"yes",statusbar:"yes",toolbar:"no"},vg=500,yg=600,_g="_blank",wg="http://localhost";class Fs{constructor(e){this.window=e,this.associatedEvent=null}close(){if(this.window)try{this.window.close()}catch{}}}function xg(t,e,n,r=vg,s=yg){const i=Math.max((window.screen.availHeight-s)/2,0).toString(),o=Math.max((window.screen.availWidth-r)/2,0).toString();let a="";const l=Object.assign(Object.assign({},bg),{width:r.toString(),height:s.toString(),top:i,left:o}),c=X().toLowerCase();n&&(a=so(c)?_g:n),ro(c)&&(e=e||wg,l.scrollbars="yes");const u=Object.entries(l).reduce((g,[b,m])=>`${g}${b}=${m},`,"");if(Xf(c)&&a!=="_self")return Eg(e||"",a),new Fs(null);const v=window.open(e||"",a,u);I(v,t,"popup-blocked");try{v.focus()}catch{}return new Fs(v)}function Eg(t,e){const n=document.createElement("a");n.href=t,n.target=e;const r=document.createEvent("MouseEvent");r.initMouseEvent("click",!0,!0,window,1,0,0,0,0,!1,!1,!1,!1,1,null),n.dispatchEvent(r)}/**
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
 */const Ig="__/auth/handler",Sg="emulator/auth/handler";function Bs(t,e,n,r,s,i){I(t.config.authDomain,t,"auth-domain-config-required"),I(t.config.apiKey,t,"invalid-api-key");const o={apiKey:t.config.apiKey,appName:t.name,authType:n,redirectUrl:r,v:un,eventId:s};if(e instanceof Cr){e.setDefaultLanguage(t.languageCode),o.providerId=e.providerId||"",yd(e.getCustomParameters())||(o.customParameters=JSON.stringify(e.getCustomParameters()));for(const[l,c]of Object.entries(i||{}))o[l]=c}if(e instanceof kt){const l=e.getScopes().filter(c=>c!=="");l.length>0&&(o.scopes=l.join(","))}t.tenantId&&(o.tid=t.tenantId);const a=o;for(const l of Object.keys(a))a[l]===void 0&&delete a[l];return`${$g(t)}?${Et(a).slice(1)}`}function $g({config:t}){return t.emulator?Ir(t,Sg):`https://${t.authDomain}/${Ig}`}/**
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
 */const Fn="webStorageSupport";class kg{constructor(){this.eventManagers={},this.iframes={},this.originValidationPromises={},this._redirectPersistence=vo,this._completeRedirectFn=Qh,this._overrideRedirectResult=Kh}async _openPopup(e,n,r,s){var i;me((i=this.eventManagers[e._key()])===null||i===void 0?void 0:i.manager,"_initialize() not called before _openPopup()");const o=Bs(e,n,r,ar(),s);return xg(e,o,Ar())}async _openRedirect(e,n,r,s){return await this._originValidation(e),Ch(Bs(e,n,r,ar(),s)),new Promise(()=>{})}_initialize(e){const n=e._key();if(this.eventManagers[n]){const{manager:s,promise:i}=this.eventManagers[n];return s?Promise.resolve(s):(me(i,"If manager is not set, promise should be"),i)}const r=this.initAndGetManager(e);return this.eventManagers[n]={promise:r},r.catch(()=>{delete this.eventManagers[n]}),r}async initAndGetManager(e){const n=await pg(e),r=new eg(e);return n.register("authEvent",s=>(I(s?.authEvent,e,"invalid-auth-event"),{status:r.onEvent(s.authEvent)?"ACK":"ERROR"}),gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER),this.eventManagers[e._key()]={manager:r},this.iframes[e._key()]=n,r}_isIframeWebStorageSupported(e,n){this.iframes[e._key()].send(Fn,{type:Fn},s=>{var i;const o=(i=s?.[0])===null||i===void 0?void 0:i[Fn];o!==void 0&&n(!!o),re(e,"internal-error")},gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER)}_originValidation(e){const n=e._key();return this.originValidationPromises[n]||(this.originValidationPromises[n]=ig(e)),this.originValidationPromises[n]}get _shouldInitProactively(){return co()||$r()||fn()}}const Tg=kg;var Hs="@firebase/auth",zs="0.20.11";/**
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
 */class Cg{constructor(e){this.auth=e,this.internalListeners=new Map}getUid(){var e;return this.assertAuthConfigured(),((e=this.auth.currentUser)===null||e===void 0?void 0:e.uid)||null}async getToken(e){return this.assertAuthConfigured(),await this.auth._initializationPromise,this.auth.currentUser?{accessToken:await this.auth.currentUser.getIdToken(e)}:null}addAuthTokenListener(e){if(this.assertAuthConfigured(),this.internalListeners.has(e))return;const n=this.auth.onIdTokenChanged(r=>{var s;e(((s=r)===null||s===void 0?void 0:s.stsTokenManager.accessToken)||null)});this.internalListeners.set(e,n),this.updateProactiveRefresh()}removeAuthTokenListener(e){this.assertAuthConfigured();const n=this.internalListeners.get(e);!n||(this.internalListeners.delete(e),n(),this.updateProactiveRefresh())}assertAuthConfigured(){I(this.auth._initializationPromise,"dependent-sdk-initialized-before-auth")}updateProactiveRefresh(){this.internalListeners.size>0?this.auth._startProactiveRefresh():this.auth._stopProactiveRefresh()}}/**
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
 */function Ag(t){switch(t){case"Node":return"node";case"ReactNative":return"rn";case"Worker":return"webworker";case"Cordova":return"cordova";default:return}}function Og(t){mt(new Ge("auth",(e,{options:n})=>{const r=e.getProvider("app").getImmediate(),s=e.getProvider("heartbeat"),{apiKey:i,authDomain:o}=r.options;return((a,l)=>{I(i&&!i.includes(":"),"invalid-api-key",{appName:a.name}),I(!o?.includes(":"),"argument-error",{appName:a.name});const c={apiKey:i,authDomain:o,clientPlatform:t,apiHost:"identitytoolkit.googleapis.com",tokenApiHost:"securetoken.googleapis.com",apiScheme:"https",sdkClientVersion:uo(t)},u=new eh(a,l,c);return Rf(u,n),u})(r,s)},"PUBLIC").setInstantiationMode("EXPLICIT").setInstanceCreatedCallback((e,n,r)=>{e.getProvider("auth-internal").initialize()})),mt(new Ge("auth-internal",e=>{const n=$t(e.getProvider("auth").getImmediate());return(r=>new Cg(r))(n)},"PRIVATE").setInstantiationMode("EXPLICIT")),Ve(Hs,zs,Ag(t)),Ve(Hs,zs,"esm2017")}/**
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
 */const Ng=5*60,Rg=Bi("authIdTokenMaxAge")||Ng;let Vs=null;const Dg=t=>async e=>{const n=e&&await e.getIdTokenResult(),r=n&&(new Date().getTime()-Date.parse(n.issuedAtTime))/1e3;if(r&&r>Rg)return;const s=n?.token;Vs!==s&&(Vs=s,await fetch(t,{method:s?"POST":"DELETE",headers:s?{Authorization:`Bearer ${s}`}:{}}))};function Pg(t=_f()){const e=Wi(t,"auth");if(e.isInitialized())return e.getImmediate();const n=Nf(t,{popupRedirectResolver:Tg,persistence:[Uh,$h,vo]}),r=Bi("authTokenSyncURL");if(r){const i=Dg(r);_h(n,i,()=>i(n.currentUser)),yh(n,o=>i(o))}const s=hd("auth");return s&&th(n,`http://${s}`),n}Og("Browser");function Lg(){const[t,e]=_(null);return{email:t,setEmail:e}}const $o=Q(Lg);var Mg="firebase",Ug="9.14.0";/**
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
 */Ve(Mg,Ug,"app");const jg={apiKey:"AIzaSyAX9a9qLUzLoVFy9YrRprTWuf7lwZ-cEi0",authDomain:"fabled-pivot-305219.firebaseapp.com",projectId:"fabled-pivot-305219",storageBucket:"fabled-pivot-305219.appspot.com",messagingSenderId:"293220208202",appId:"1:293220208202:web:59eabbc4f981ead408e0b3",measurementId:"G-7E7PGPVJ99"},Fg=Ji(jg);function Bg(){const[t,e]=_(null);return e(Pg(Fg)),{auth:t}}const ko=Q(Bg),Hg=y('<div id="tab_account" class="tabcontent p-4"><p class="text-gray-600"></p><button type="button" class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 text-sm font-medium leading-4 text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 mt-2">Logout</button></div>'),{tabName:zg}=Ze,{email:Vg}=$o,{auth:Wg}=ko;function Jg(){function t(){xh(Wg()).catch(function(e){console.error(e)})}return(()=>{const e=Hg.cloneNode(!0),n=e.firstChild,r=n.nextSibling;return d(n,Vg),r.$$click=t,$(()=>e.classList.toggle("hidden",zg()!="account")),e})()}R(["click"]);const qg=y('<div class="md:pl-36 flex flex-col flex-1"><main class="flex-1"><div class=""><div class="mx-auto"><div></div></div></div></main></div>'),{multiuser:Ws}=Ce,{logged:Gg}=Be,{localModules:Kg,loadAllModules:Xg}=cn;function Yg(){const[t,e]=_(!1);return Fe(function(){(Ws()==!1||Gg()==!0)&&Oi(Kg())&&Xg()}),(()=>{const n=qg.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild;return d(o,f(wu,{get jobsTrigger(){return t()},setJobsTrigger:e}),null),d(o,f(Yu,{get jobsTrigger(){return t()},setJobsTrigger:e}),null),d(o,f(ed,{}),null),d(o,f(Z,{get when(){return Ws()==!0},get children(){return f(Jg,{})}}),null),n})()}function Qg(){const[t,e]=_(!0);return{systemReady:t,setSystemReady:e}}const Zg=Q(Qg),em=y('<div id="tab_systemnotready" class="tabcontent"><div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-md bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"><div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4"><div class="sm:flex sm:items-start"><div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"><svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v3.75m-9.303 3.376C1.83 19.126 2.914 21 4.645 21h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 4.88c-.866-1.501-3.032-1.501-3.898 0L2.697 17.626zM12 17.25h.007v.008H12v-.008z"></path></svg></div><div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left"><h3 class="text-lg font-medium leading-6 text-gray-900" id="modal-title">System not ready</h3><div class="mt-2"><p class="text-sm text-gray-500">OakVar server is not running or it is having a problem. Please contact your system administrator.</p></div></div></div></div></div></div></div></div></div>');function tm(){const{systemReady:t,setSystemReady:e}=Zg;return(()=>{const n=em.cloneNode(!0);return $(()=>n.classList.toggle("hidden",!!t())),n})()}function nm(){const[t,e]=_(!0);return{appLoading:t,setAppLoading:e}}const mn=Q(nm),rm=y('<div class="h-full"></div>'),{multiuser:sm}=Ce,{appLoading:im}=mn;function om(){const{logged:t}=Be;return(()=>{const e=rm.cloneNode(!0);return d(e,f(Xl,{}),null),d(e,f(Yg,{}),null),d(e,f(tm,{}),null),$(()=>e.classList.toggle("hidden",!!(im()||sm()&&!t()))),e})()}const am=y('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100"><svg class="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"></path></svg></div><div class="mt-3 text-center sm:mt-5"><h3 class="text-lg font-medium leading-6 text-gray-900"></h3><div class="mt-2"><p class="text-sm text-gray-500"></p></div></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm">Dismiss</button></div></div></div></div></div>');function lm(t){return(()=>{const e=am.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,l=a.nextSibling,c=l.firstChild,u=c.nextSibling,v=u.firstChild,g=o.nextSibling,b=g.firstChild;return d(c,()=>t.title),d(v,()=>t.text),rn(b,"click",t.callback,!0),e})()}R(["click"]);const cm=y('<svg class="hide animate-spin ml-1 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>');function Js(t){return(()=>{const e=cm.cloneNode(!0);return $(()=>e.classList.toggle("hidden",!t.show)),e})()}const um=y('<div class="flex w-screen h-screen items-center justify-center"><div id="container" class="w-[64rem]"><div class="flex min-h-full flex-col justify-center py-12 sm:px-6 lg:px-8"><div class="sm:mx-auto sm:w-full sm:max-w-md"><img class="mx-auto h-16 w-auto" alt="OakVar"><h2 class="mt-4 text-center text-3xl font-bold tracking-tight text-gray-900">Sign in</h2><h2 class="hide mt-4 text-center text-3xl font-bold tracking-tight text-gray-900">Sign up</h2></div><p class="mt-2 text-center text-sm text-gray-600">Or&nbsp;<a href="#" class="font-medium text-indigo-600 hover:text-indigo-500">sign up</a><a href="#" class="hide font-medium text-indigo-600 hover:text-indigo-500">sign in</a></p><div class="mt-6 sm:mx-auto sm:w-full sm:max-w-md"><div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10"><div class="space-y-6" method="POST"><div><label for="email" class="block text-sm font-medium text-gray-700">Email address</label><div class="mt-1"><input id="email" name="email" type="email" autocomplete="email" required class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"><div class="text-xs text-orange-600 mt-2"></div></div></div><div><label for="password" class="block text-sm font-medium text-gray-700">Password</label><div class="mt-1"><input id="password" name="password" type="password" autocomplete="current-password" required class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"><div class="text-xs text-orange-600 mt-2"></div></div></div><div class="flex items-center justify-between"><div class="flex items-center"></div><div class="text-sm"><a href="#" class="font-medium">Forgot your password?</a></div></div><div><button id="signin_btn" type="submit" class="flex w-full justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Sign in</button><button id="signup_btn" type="submit" class="flex w-full justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Sign up</button></div></div></div></div></div></div></div>'),{serverUrl:Dt,withCredentials:Bn}=ee,{email:Ne,setEmail:qs}=$o,{setTabName:dm}=Ze,{auth:ot}=ko,{appLoading:fm,setAppLoading:Hn}=mn,{multiuser:hm}=Ce,{logged:gm,setLogged:zn}=Be;let Gs=null;function mm(){const[t,e]=_("signin"),[n,r]=_(!1),[s,i]=_(!1),[o,a]=_(null),[l,c]=_(!1),[u,v]=_(null),[g,b]=_(null),[m,p]=_(!1),[w,x]=_(null),[S,C]=_(null),[D,M]=_(""),[k,z]=_(""),[F,A]=_(!0),[P,N]=_(!0),Y={"auth/user-not-found":"Account was not found. Please sign up first.","auth/account-exists-with-different-credential":"Account exists with different credential.","auth/wrong-password":"Wrong password. Please check your password or use Forget Your Password? link.","auth/missing-email":"Please provide an email address.","missing-password":"Please provide a password.","account-exists":"Account already exists.","auth/too-many-requests":"Too many failed attempts. Wait for a while and try again, or use Forgot your password? link."};let V=()=>{c(!1)};Gs||(Gs=wh(ot(),function(E){E?(Hn(!0),nt(E.email)):_n()}));function W(){return!F()&&!P()}function Ct(){bn(),yn()}function pn(E){qs(E.target.value),Ct(),E.keyCode==13&&W()&&rt("email")}function bn(){if(!Ne()||Ne().length==0){M("Please enter an email."),A(!0);return}let E=/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9]+)+$/;if(!Ne().match(E)){M("Email is invalid."),A(!0);return}M(""),A(!1)}function vn(E){a(E.target.value),Ct(),E.keyCode==13&&W()&&rt("email")}function yn(){if(!o()||o().length==0){z("Please enter a password."),N(!0);return}let E=/^[a-zA-Z0-9.!?#$%&^_@*]+$/;if(!o().match(E)){z("Password is invalid (a-z, A-Z, 0-9, .!?#$%&^_@* allowed)."),N(!0);return}return z(""),N(!1),!0}function nt(E){j.post(Dt()+"/server/loginsuccess",{email:E},{withCredentials:Bn}).then(function(T){qs(T.data.email),r(!1),dm("submit"),zn(!0),Hn(!1)}).catch(function(T){ye(T,"Login failed"),r(!1)})}function _n(){j.get(Dt()+"/server/logout",{withCredentials:Bn}).then(function(E){E.status==200&&zn(!1)}).catch(function(E){console.error(E)}),Hn(!1)}function ye(E,T){if(E.response&&(E=E.response.data),E.code=="auth/popup-closed-by-user"){r(!1);return}x(T);let B=Y[E.code];B?C(B):(C("Error code: "+E.code),console.error(E)),p(!0)}function wn(){r(!0),vh(ot(),Ne(),o()).catch(function(E){ye(E,"Login failed"),r(!1)})}function xn(){r(!0);const E=new ae;Ms(ot(),E).then(function(T){nt(T)}).catch(function(T){ye(T,"Login failed"),r(!1)})}function En(){r(!0);const E=new le;Ms(ot(),E).then(function(T){nt(T)}).catch(function(T){ye(T,"Login failed"),r(!1)})}function rt(E){E=="email"?wn():E=="google"?xn():E=="github"&&En()}function In(){i(!0),j.post(Dt()+"/server/signup",{email:Ne(),password:o()},{withCredentials:Bn}).then(function(E){E.data.code&&(v("Success"),b(E.data.code),V=()=>{i(!1),zn(!0)},c(!0))}).catch(function(E){ye(E,"Signup failed"),i(!1)})}function Sn(){bh(ot(),Ne()).then(function(){v("Success"),b("Please check your email for a password reset link."),c(!0)}).catch(function(E){ye(E,"Password reset failed")})}return(()=>{const E=um.cloneNode(!0),T=E.firstChild,B=T.firstChild,_e=B.firstChild,He=_e.firstChild,Nr=He.nextSibling,To=Nr.nextSibling,Rr=_e.nextSibling,Co=Rr.firstChild,At=Co.nextSibling,$n=At.nextSibling,Ao=Rr.nextSibling,Oo=Ao.firstChild,No=Oo.firstChild,Dr=No.firstChild,Ro=Dr.firstChild,Do=Ro.nextSibling,kn=Do.firstChild,Po=kn.nextSibling,Pr=Dr.nextSibling,Lo=Pr.firstChild,Mo=Lo.nextSibling,Tn=Mo.firstChild,Uo=Tn.nextSibling,Lr=Pr.nextSibling,jo=Lr.firstChild,Mr=jo.nextSibling,Cn=Mr.firstChild,Fo=Lr.nextSibling,Oe=Fo.firstChild;Oe.firstChild;const st=Oe.nextSibling;return st.firstChild,At.$$click=e,At.$$clickData="signup",$n.$$click=e,$n.$$clickData="signin",kn.$$keyup=pn,d(Po,D),Tn.$$keyup=vn,d(Uo,k),Cn.$$click=Sn,Oe.$$click=rt,Oe.$$clickData="email",d(Oe,f(Js,{get show(){return n()}}),null),st.$$click=In,d(st,f(Js,{get show(){return s()}}),null),d(E,f(Z,{get when(){return m()},get children(){return f(Ci,{get title(){return w()},get text(){return S()},setShowDialog:p})}}),null),d(E,f(Z,{get when(){return l()},get children(){return f(lm,{get title(){return u()},get text(){return g()},callback:V})}}),null),$(L=>{const Ur=!!(fm()||!hm()||gm()),jr=Dt()+"/submit/images/logo_only.png",Fr=t()!="signin",Br=t()!="signup",Hr=t()!="signin",zr=t()!="signup",Vr=t()!="signin",Bo={"text-indigo-600":!F(),"hover:text-indigo-500":!F(),"text-gray-500":F(),"cursor-default":F()},Wr=F(),Ho={hidden:t()!="signin","bg-indigo-600":W(),"hover:bg-indigo-700":W(),"bg-gray-500":!W()},Jr=!W(),zo={hidden:t()!="signup","bg-indigo-600":W(),"hover:bg-indigo-700":W(),"bg-gray-500":!W()},qr=!W();return Ur!==L._v$&&E.classList.toggle("hidden",L._v$=Ur),jr!==L._v$2&&q(He,"src",L._v$2=jr),Fr!==L._v$3&&Nr.classList.toggle("hidden",L._v$3=Fr),Br!==L._v$4&&To.classList.toggle("hidden",L._v$4=Br),Hr!==L._v$5&&At.classList.toggle("hidden",L._v$5=Hr),zr!==L._v$6&&$n.classList.toggle("hidden",L._v$6=zr),Vr!==L._v$7&&Mr.classList.toggle("hidden",L._v$7=Vr),L._v$8=Pt(Cn,Bo,L._v$8),Wr!==L._v$9&&(Cn.disabled=L._v$9=Wr),L._v$10=Pt(Oe,Ho,L._v$10),Jr!==L._v$11&&(Oe.disabled=L._v$11=Jr),L._v$12=Pt(st,zo,L._v$12),qr!==L._v$13&&(st.disabled=L._v$13=qr),L},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0,_v$6:void 0,_v$7:void 0,_v$8:void 0,_v$9:void 0,_v$10:void 0,_v$11:void 0,_v$12:void 0,_v$13:void 0}),$(()=>kn.value=Ne()),$(()=>Tn.value=o()),E})()}R(["click","keyup"]);const pm=y('<div class="h-screen w-screen grid place-items-center"><img class="h-96 animate-pulse"></div>'),{serverUrl:bm}=ee,{appLoading:vm}=mn;function ym(){return(()=>{const t=pm.cloneNode(!0),e=t.firstChild;return $(n=>{const r=!vm(),s=bm()+"/submit/images/logo_transparent.png";return r!==n._v$&&t.classList.toggle("hidden",n._v$=r),s!==n._v$2&&q(e,"src",n._v$2=s),n},{_v$:void 0,_v$2:void 0}),t})()}const{serverUrl:Vn}=ee,{logged:Ks,setLogged:Xs}=Be,{multiuser:Wn,setMultiuser:Ys}=Ce,{setAppLoading:_m}=mn;function wm(){Ys(null),Xs(null),Fe(function(){Wn()!=null&&Ks()!=null&&_m(!1)});function t(){j.get(Vn()+"/server/deletetoken").then(function(){}).catch(function(r){console.error(r)})}function e(){j.get(Vn()+"/submit/servermode").then(function(r){Ys(r.data.servermode),Wn()||t()}).catch(function(r){console.error(r)})}function n(){j.get(Vn()+"/submit/loginstate").then(function(r){Xs(r.data.loggedin)}).catch(function(r){console.error(r)})}return Wn()==null&&e(),Ks()==null&&n(),[f(ym,{}),f(mm,{}),f(om,{})]}ca(()=>f(wm,{}),document.getElementById("root"));
