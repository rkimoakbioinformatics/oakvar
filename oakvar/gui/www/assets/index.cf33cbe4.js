(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))r(s);new MutationObserver(s=>{for(const i of s)if(i.type==="childList")for(const o of i.addedNodes)o.tagName==="LINK"&&o.rel==="modulepreload"&&r(o)}).observe(document,{childList:!0,subtree:!0});function n(s){const i={};return s.integrity&&(i.integrity=s.integrity),s.referrerpolicy&&(i.referrerPolicy=s.referrerpolicy),s.crossorigin==="use-credentials"?i.credentials="include":s.crossorigin==="anonymous"?i.credentials="omit":i.credentials="same-origin",i}function r(s){if(s.ep)return;s.ep=!0;const i=n(s);fetch(s.href,i)}})();const B={};function oo(t){B.context=t}const ao=(t,e)=>t===e,Ne=Symbol("solid-proxy"),Dn=Symbol("solid-track"),Ut={equals:ao};let Rs=Us;const he=1,Ft=2,Ds={owned:null,cleanups:null,context:null,owner:null},Sn={};var H=null;let ke=null,P=null,z=null,ce=null,Xn=0;function X(t,e){const n=P,r=H,s=t.length===0,i=s?Ds:{owned:null,cleanups:null,context:null,owner:e||r},o=s?t:()=>t(()=>xe(()=>Qn(i)));H=i,P=null;try{return Se(o,!0)}finally{P=n,H=r}}function S(t,e){e=e?Object.assign({},Ut,e):Ut;const n={value:t,observers:null,observerSlots:null,comparator:e.equals||void 0},r=s=>(typeof s=="function"&&(s=s(n.value)),Ms(n,s));return[Ls.bind(n),r]}function Ar(t,e,n){const r=Qt(t,e,!0,he);Ge(r)}function T(t,e,n){const r=Qt(t,e,!1,he);Ge(r)}function qe(t,e,n){Rs=go;const r=Qt(t,e,!1,he);r.user=!0,ce?ce.push(r):Ge(r)}function de(t,e,n){n=n?Object.assign({},Ut,n):Ut;const r=Qt(t,e,!0,0);return r.observers=null,r.observerSlots=null,r.comparator=n.equals||void 0,Ge(r),Ls.bind(r)}function Yn(t,e,n){let r,s,i;arguments.length===2&&typeof e=="object"||arguments.length===1?(r=!0,s=t,i=e||{}):(r=t,s=e,i=n||{});let o=null,a=Sn,c=null,l=!1,u="initialValue"in i,m=typeof r=="function"&&de(r);const b=new Set,[p,h]=(i.storage||S)(i.initialValue),[v,x]=S(void 0),[y,I]=S(void 0,{equals:!1}),[_,k]=S(u?"ready":"unresolved");if(B.context){c=`${B.context.id}${B.context.count++}`;let A;i.ssrLoadFrom==="initial"?a=i.initialValue:B.load&&(A=B.load(c))&&(a=A[0])}function C(A,L,M,Z){return o===A&&(o=null,u=!0,(A===a||L===a)&&i.onHydrated&&queueMicrotask(()=>i.onHydrated(Z,{value:L})),a=Sn,J(L,M)),L}function J(A,L){Se(()=>{L||h(()=>A),x(L),k(L?"errored":"ready");for(const M of b.keys())M.decrement();b.clear()},!1)}function K(){const A=uo,L=p(),M=v();if(M&&!o)throw M;return P&&!P.user&&A&&Ar(()=>{y(),o&&(A.resolved||b.has(A)||(A.increment(),b.add(A)))}),L}function ee(A=!0){if(A!==!1&&l)return;l=!1;const L=m?m():r;if(L==null||L===!1){C(o,xe(p));return}const M=a!==Sn?a:xe(()=>s(L,{value:p(),refetching:A}));return typeof M!="object"||!(M&&"then"in M)?(C(o,M),M):(o=M,l=!0,queueMicrotask(()=>l=!1),Se(()=>{k(u?"refreshing":"pending"),I()},!1),M.then(Z=>C(M,Z,void 0,L),Z=>C(M,void 0,js(Z))))}return Object.defineProperties(K,{state:{get:()=>_()},error:{get:()=>v()},loading:{get(){const A=_();return A==="pending"||A==="refreshing"}},latest:{get(){if(!u)return K();const A=v();if(A&&!o)throw A;return p()}}}),m?Ar(()=>ee(!1)):ee(!1),[K,{refetch:ee,mutate:h}]}function lo(t){return Se(t,!1)}function xe(t){let e,n=P;return P=null,e=t(),P=n,e}function jt(t){return H===null||(H.cleanups===null?H.cleanups=[t]:H.cleanups.push(t)),t}function Ps(){return P}function co(t){const e=de(t),n=de(()=>Pn(e()));return n.toArray=()=>{const r=n();return Array.isArray(r)?r:r!=null?[r]:[]},n}let uo;function Ls(){const t=ke;if(this.sources&&(this.state||t))if(this.state===he||t)Ge(this);else{const e=z;z=null,Se(()=>Ht(this),!1),z=e}if(P){const e=this.observers?this.observers.length:0;P.sources?(P.sources.push(this),P.sourceSlots.push(e)):(P.sources=[this],P.sourceSlots=[e]),this.observers?(this.observers.push(P),this.observerSlots.push(P.sources.length-1)):(this.observers=[P],this.observerSlots=[P.sources.length-1])}return this.value}function Ms(t,e,n){let r=t.value;return(!t.comparator||!t.comparator(r,e))&&(t.value=e,t.observers&&t.observers.length&&Se(()=>{for(let s=0;s<t.observers.length;s+=1){const i=t.observers[s],o=ke&&ke.running;o&&ke.disposed.has(i),(o&&!i.tState||!o&&!i.state)&&(i.pure?z.push(i):ce.push(i),i.observers&&Fs(i)),o||(i.state=he)}if(z.length>1e6)throw z=[],new Error},!1)),e}function Ge(t){if(!t.fn)return;Qn(t);const e=H,n=P,r=Xn;P=H=t,fo(t,t.value,r),P=n,H=e}function fo(t,e,n){let r;try{r=t.fn(e)}catch(s){t.pure&&(t.state=he),Bs(s)}(!t.updatedAt||t.updatedAt<=n)&&(t.updatedAt!=null&&"observers"in t?Ms(t,r):t.value=r,t.updatedAt=n)}function Qt(t,e,n,r=he,s){const i={fn:t,state:r,updatedAt:null,owned:null,sources:null,sourceSlots:null,cleanups:null,value:e,owner:H,context:null,pure:n};return H===null||H!==Ds&&(H.owned?H.owned.push(i):H.owned=[i]),i}function Bt(t){const e=ke;if(t.state===0||e)return;if(t.state===Ft||e)return Ht(t);if(t.suspense&&xe(t.suspense.inFallback))return t.suspense.effects.push(t);const n=[t];for(;(t=t.owner)&&(!t.updatedAt||t.updatedAt<Xn);)(t.state||e)&&n.push(t);for(let r=n.length-1;r>=0;r--)if(t=n[r],t.state===he||e)Ge(t);else if(t.state===Ft||e){const s=z;z=null,Se(()=>Ht(t,n[0]),!1),z=s}}function Se(t,e){if(z)return t();let n=!1;e||(z=[]),ce?n=!0:ce=[],Xn++;try{const r=t();return ho(n),r}catch(r){z||(ce=null),Bs(r)}}function ho(t){if(z&&(Us(z),z=null),t)return;const e=ce;ce=null,e.length&&Se(()=>Rs(e),!1)}function Us(t){for(let e=0;e<t.length;e++)Bt(t[e])}function go(t){let e,n=0;for(e=0;e<t.length;e++){const r=t[e];r.user?t[n++]=r:Bt(r)}for(B.context&&oo(),e=0;e<n;e++)Bt(t[e])}function Ht(t,e){const n=ke;t.state=0;for(let r=0;r<t.sources.length;r+=1){const s=t.sources[r];s.sources&&(s.state===he||n?s!==e&&Bt(s):(s.state===Ft||n)&&Ht(s,e))}}function Fs(t){const e=ke;for(let n=0;n<t.observers.length;n+=1){const r=t.observers[n];(!r.state||e)&&(r.state=Ft,r.pure?z.push(r):ce.push(r),r.observers&&Fs(r))}}function Qn(t){let e;if(t.sources)for(;t.sources.length;){const n=t.sources.pop(),r=t.sourceSlots.pop(),s=n.observers;if(s&&s.length){const i=s.pop(),o=n.observerSlots.pop();r<s.length&&(i.sourceSlots[o]=r,s[r]=i,n.observerSlots[r]=o)}}if(t.owned){for(e=0;e<t.owned.length;e++)Qn(t.owned[e]);t.owned=null}if(t.cleanups){for(e=0;e<t.cleanups.length;e++)t.cleanups[e]();t.cleanups=null}t.state=0,t.context=null}function js(t){return t instanceof Error||typeof t=="string"?t:new Error("Unknown error")}function Bs(t){throw t=js(t),t}function Pn(t){if(typeof t=="function"&&!t.length)return Pn(t());if(Array.isArray(t)){const e=[];for(let n=0;n<t.length;n++){const r=Pn(t[n]);Array.isArray(r)?e.push.apply(e,r):e.push(r)}return e}return t}const mo=Symbol("fallback");function Nr(t){for(let e=0;e<t.length;e++)t[e]()}function po(t,e,n={}){let r=[],s=[],i=[],o=0,a=e.length>1?[]:null;return jt(()=>Nr(i)),()=>{let c=t()||[],l,u;return c[Dn],xe(()=>{let b=c.length,p,h,v,x,y,I,_,k,C;if(b===0)o!==0&&(Nr(i),i=[],r=[],s=[],o=0,a&&(a=[])),n.fallback&&(r=[mo],s[0]=X(J=>(i[0]=J,n.fallback())),o=1);else if(o===0){for(s=new Array(b),u=0;u<b;u++)r[u]=c[u],s[u]=X(m);o=b}else{for(v=new Array(b),x=new Array(b),a&&(y=new Array(b)),I=0,_=Math.min(o,b);I<_&&r[I]===c[I];I++);for(_=o-1,k=b-1;_>=I&&k>=I&&r[_]===c[k];_--,k--)v[k]=s[_],x[k]=i[_],a&&(y[k]=a[_]);for(p=new Map,h=new Array(k+1),u=k;u>=I;u--)C=c[u],l=p.get(C),h[u]=l===void 0?-1:l,p.set(C,u);for(l=I;l<=_;l++)C=r[l],u=p.get(C),u!==void 0&&u!==-1?(v[u]=s[l],x[u]=i[l],a&&(y[u]=a[l]),u=h[u],p.set(C,u)):i[l]();for(u=I;u<b;u++)u in v?(s[u]=v[u],i[u]=x[u],a&&(a[u]=y[u],a[u](u))):s[u]=X(m);s=s.slice(0,o=b),r=c.slice(0)}return s});function m(b){if(i[u]=b,a){const[p,h]=S(u);return a[u]=h,e(c[u],p)}return e(c[u])}}}function g(t,e){return xe(()=>t(e||{}))}function Ee(t){const e="fallback"in t&&{fallback:()=>t.fallback};return de(po(()=>t.each,t.children,e||void 0))}function oe(t){let e=!1;const n=t.keyed,r=de(()=>t.when,void 0,{equals:(s,i)=>e?s===i:!s==!i});return de(()=>{const s=r();if(s){const i=t.children,o=typeof i=="function"&&i.length>0;return e=n||o,o?xe(()=>i(s)):i}return t.fallback})}function bo(t){let e=!1,n=!1;const r=co(()=>t.children),s=de(()=>{let i=r();Array.isArray(i)||(i=[i]);for(let o=0;o<i.length;o++){const a=i[o].when;if(a)return n=!!i[o].keyed,[o,a,i[o]]}return[-1]},void 0,{equals:(i,o)=>i[0]===o[0]&&(e?i[1]===o[1]:!i[1]==!o[1])&&i[2]===o[2]});return de(()=>{const[i,o,a]=s();if(i<0)return t.fallback;const c=a.children,l=typeof c=="function"&&c.length>0;return e=n||l,l?xe(()=>c(o)):c})}function Or(t){return t}const vo=["allowfullscreen","async","autofocus","autoplay","checked","controls","default","disabled","formnovalidate","hidden","indeterminate","ismap","loop","multiple","muted","nomodule","novalidate","open","playsinline","readonly","required","reversed","seamless","selected"],yo=new Set(["className","value","readOnly","formNoValidate","isMap","noModule","playsInline",...vo]),_o=new Set(["innerHTML","textContent","innerText","children"]),wo={className:"class",htmlFor:"for"},Rr={class:"className",formnovalidate:"formNoValidate",ismap:"isMap",nomodule:"noModule",playsinline:"playsInline",readonly:"readOnly"},xo=new Set(["beforeinput","click","dblclick","contextmenu","focusin","focusout","input","keydown","keyup","mousedown","mousemove","mouseout","mouseover","mouseup","pointerdown","pointermove","pointerout","pointerover","pointerup","touchend","touchmove","touchstart"]),So={xlink:"http://www.w3.org/1999/xlink",xml:"http://www.w3.org/XML/1998/namespace"};function Eo(t,e){return de(t,void 0,e?void 0:{equals:e})}function Io(t,e,n){let r=n.length,s=e.length,i=r,o=0,a=0,c=e[s-1].nextSibling,l=null;for(;o<s||a<i;){if(e[o]===n[a]){o++,a++;continue}for(;e[s-1]===n[i-1];)s--,i--;if(s===o){const u=i<r?a?n[a-1].nextSibling:n[i-a]:c;for(;a<i;)t.insertBefore(n[a++],u)}else if(i===a)for(;o<s;)(!l||!l.has(e[o]))&&e[o].remove(),o++;else if(e[o]===n[i-1]&&n[a]===e[s-1]){const u=e[--s].nextSibling;t.insertBefore(n[a++],e[o++].nextSibling),t.insertBefore(n[--i],u),e[s]=n[i]}else{if(!l){l=new Map;let m=a;for(;m<i;)l.set(n[m],m++)}const u=l.get(e[o]);if(u!=null)if(a<u&&u<i){let m=o,b=1,p;for(;++m<s&&m<i&&!((p=l.get(e[m]))==null||p!==u+b);)b++;if(b>u-a){const h=e[o];for(;a<u;)t.insertBefore(n[a++],h)}else t.replaceChild(n[a++],e[o++])}else o++;else e[o++].remove()}}}const Dr="_$DX_DELEGATE";function To(t,e,n){let r;return X(s=>{r=s,e===document?t():f(e,t(),e.firstChild?null:void 0,n)}),()=>{r(),e.textContent=""}}function w(t,e,n){const r=document.createElement("template");r.innerHTML=t;let s=r.content.firstChild;return n&&(s=s.firstChild),s}function N(t,e=window.document){const n=e[Dr]||(e[Dr]=new Set);for(let r=0,s=t.length;r<s;r++){const i=t[r];n.has(i)||(n.add(i),e.addEventListener(i,Oo))}}function V(t,e,n){n==null?t.removeAttribute(e):t.setAttribute(e,n)}function Co(t,e,n,r){r==null?t.removeAttributeNS(e,n):t.setAttributeNS(e,n,r)}function ko(t,e){e==null?t.removeAttribute("class"):t.className=e}function Zn(t,e,n,r){if(r)Array.isArray(n)?(t[`$$${e}`]=n[0],t[`$$${e}Data`]=n[1]):t[`$$${e}`]=n;else if(Array.isArray(n)){const s=n[0];t.addEventListener(e,n[0]=i=>s.call(t,n[1],i))}else t.addEventListener(e,n)}function $o(t,e,n={}){const r=Object.keys(e||{}),s=Object.keys(n);let i,o;for(i=0,o=s.length;i<o;i++){const a=s[i];!a||a==="undefined"||e[a]||(Lr(t,a,!1),delete n[a])}for(i=0,o=r.length;i<o;i++){const a=r[i],c=!!e[a];!a||a==="undefined"||n[a]===c||!c||(Lr(t,a,!0),n[a]=c)}return n}function Hs(t,e,n){if(!e)return n?V(t,"style"):e;const r=t.style;if(typeof e=="string")return r.cssText=e;typeof n=="string"&&(r.cssText=n=void 0),n||(n={}),e||(e={});let s,i;for(i in n)e[i]==null&&r.removeProperty(i),delete n[i];for(i in e)s=e[i],s!==n[i]&&(r.setProperty(i,s),n[i]=s);return n}function Pr(t,e,n,r){typeof e=="function"?T(s=>Ur(t,e(),s,n,r)):Ur(t,e,void 0,n,r)}function f(t,e,n,r){if(n!==void 0&&!r&&(r=[]),typeof e!="function")return Ve(t,e,r,n);T(s=>Ve(t,e(),s,n),r)}function Ao(t,e,n,r,s={},i=!1){e||(e={});for(const o in s)if(!(o in e)){if(o==="children")continue;s[o]=Mr(t,o,null,s[o],n,i)}for(const o in e){if(o==="children"){r||Ve(t,e.children);continue}const a=e[o];s[o]=Mr(t,o,a,s[o],n,i)}}function No(t){return t.toLowerCase().replace(/-([a-z])/g,(e,n)=>n.toUpperCase())}function Lr(t,e,n){const r=e.trim().split(/\s+/);for(let s=0,i=r.length;s<i;s++)t.classList.toggle(r[s],n)}function Mr(t,e,n,r,s,i){let o,a,c;if(e==="style")return Hs(t,n,r);if(e==="classList")return $o(t,n,r);if(n===r)return r;if(e==="ref")i||n(t);else if(e.slice(0,3)==="on:"){const l=e.slice(3);r&&t.removeEventListener(l,r),n&&t.addEventListener(l,n)}else if(e.slice(0,10)==="oncapture:"){const l=e.slice(10);r&&t.removeEventListener(l,r,!0),n&&t.addEventListener(l,n,!0)}else if(e.slice(0,2)==="on"){const l=e.slice(2).toLowerCase(),u=xo.has(l);if(!u&&r){const m=Array.isArray(r)?r[0]:r;t.removeEventListener(l,m)}(u||n)&&(Zn(t,l,n,u),u&&N([l]))}else if((c=_o.has(e))||!s&&(Rr[e]||(a=yo.has(e)))||(o=t.nodeName.includes("-")))e==="class"||e==="className"?ko(t,n):o&&!a&&!c?t[No(e)]=n:t[Rr[e]||e]=n;else{const l=s&&e.indexOf(":")>-1&&So[e.split(":")[0]];l?Co(t,l,e,n):V(t,wo[e]||e,n)}return n}function Oo(t){const e=`$$${t.type}`;let n=t.composedPath&&t.composedPath()[0]||t.target;for(t.target!==n&&Object.defineProperty(t,"target",{configurable:!0,value:n}),Object.defineProperty(t,"currentTarget",{configurable:!0,get(){return n||document}}),B.registry&&!B.done&&(B.done=!0,document.querySelectorAll("[id^=pl-]").forEach(r=>r.remove()));n!==null;){const r=n[e];if(r&&!n.disabled){const s=n[`${e}Data`];if(s!==void 0?r.call(n,s,t):r.call(n,t),t.cancelBubble)return}n=n.host&&n.host!==n&&n.host instanceof Node?n.host:n.parentNode}}function Ur(t,e,n={},r,s){return e||(e={}),s||T(()=>n.children=Ve(t,e.children,n.children)),T(()=>e.ref&&e.ref(t)),T(()=>Ao(t,e,r,!0,n,!0)),n}function Ve(t,e,n,r,s){for(B.context&&!n&&(n=[...t.childNodes]);typeof n=="function";)n=n();if(e===n)return n;const i=typeof e,o=r!==void 0;if(t=o&&n[0]&&n[0].parentNode||t,i==="string"||i==="number"){if(B.context)return n;if(i==="number"&&(e=e.toString()),o){let a=n[0];a&&a.nodeType===3?a.data=e:a=document.createTextNode(e),n=je(t,n,r,a)}else n!==""&&typeof n=="string"?n=t.firstChild.data=e:n=t.textContent=e}else if(e==null||i==="boolean"){if(B.context)return n;n=je(t,n,r)}else{if(i==="function")return T(()=>{let a=e();for(;typeof a=="function";)a=a();n=Ve(t,a,n,r)}),()=>n;if(Array.isArray(e)){const a=[],c=n&&Array.isArray(n);if(Ln(a,e,n,s))return T(()=>n=Ve(t,a,n,r,!0)),()=>n;if(B.context){if(!a.length)return n;for(let l=0;l<a.length;l++)if(a[l].parentNode)return n=a}if(a.length===0){if(n=je(t,n,r),o)return n}else c?n.length===0?Fr(t,a,r):Io(t,n,a):(n&&je(t),Fr(t,a));n=a}else if(e instanceof Node){if(B.context&&e.parentNode)return n=o?[e]:e;if(Array.isArray(n)){if(o)return n=je(t,n,r,e);je(t,n,null,e)}else n==null||n===""||!t.firstChild?t.appendChild(e):t.replaceChild(e,t.firstChild);n=e}}return n}function Ln(t,e,n,r){let s=!1;for(let i=0,o=e.length;i<o;i++){let a=e[i],c=n&&n[i];if(a instanceof Node)t.push(a);else if(!(a==null||a===!0||a===!1))if(Array.isArray(a))s=Ln(t,a,c)||s;else if(typeof a=="function")if(r){for(;typeof a=="function";)a=a();s=Ln(t,Array.isArray(a)?a:[a],Array.isArray(c)?c:[c])||s}else t.push(a),s=!0;else{const l=String(a);c&&c.nodeType===3&&c.data===l?t.push(c):t.push(document.createTextNode(l))}}return s}function Fr(t,e,n){for(let r=0,s=e.length;r<s;r++)t.insertBefore(e[r],n)}function je(t,e,n,r){if(n===void 0)return t.textContent="";const s=r||document.createTextNode("");if(e.length){let i=!1;for(let o=e.length-1;o>=0;o--){const a=e[o];if(s!==a){const c=a.parentNode===t;!i&&!o?c?t.replaceChild(s,a):t.insertBefore(s,n):c&&a.remove()}else i=!0}}else t.insertBefore(s,n);return[s]}const Ro=!1,Do="http://www.w3.org/2000/svg";function Po(t,e=!1){return e?document.createElementNS(Do,t):document.createElement(t)}function Lo(t){const{useShadow:e}=t,n=document.createTextNode(""),r=t.mount||document.body;function s(){if(B.context){const[i,o]=S(!1);return queueMicrotask(()=>o(!0)),()=>i()&&t.children}else return()=>t.children}if(r instanceof HTMLHeadElement){const[i,o]=S(!1),a=()=>o(!0);X(c=>f(r,()=>i()?c():s()(),null)),jt(()=>{B.context?queueMicrotask(a):a()})}else{const i=Po(t.isSVG?"g":"div",t.isSVG),o=e&&i.attachShadow?i.attachShadow({mode:"open"}):i;Object.defineProperty(i,"host",{get(){return n.parentNode}}),f(o,s()),r.appendChild(i),t.ref&&t.ref(i),jt(()=>r.removeChild(i))}return n}function zs(t,e){return function(){return t.apply(e,arguments)}}const{toString:Vs}=Object.prototype,{getPrototypeOf:er}=Object,tr=(t=>e=>{const n=Vs.call(e);return t[n]||(t[n]=n.slice(8,-1).toLowerCase())})(Object.create(null)),ge=t=>(t=t.toLowerCase(),e=>tr(e)===t),Zt=t=>e=>typeof e===t,{isArray:vt}=Array,Mn=Zt("undefined");function Mo(t){return t!==null&&!Mn(t)&&t.constructor!==null&&!Mn(t.constructor)&&Ke(t.constructor.isBuffer)&&t.constructor.isBuffer(t)}const Ws=ge("ArrayBuffer");function Uo(t){let e;return typeof ArrayBuffer<"u"&&ArrayBuffer.isView?e=ArrayBuffer.isView(t):e=t&&t.buffer&&Ws(t.buffer),e}const Fo=Zt("string"),Ke=Zt("function"),Js=Zt("number"),qs=t=>t!==null&&typeof t=="object",jo=t=>t===!0||t===!1,Ot=t=>{if(tr(t)!=="object")return!1;const e=er(t);return(e===null||e===Object.prototype||Object.getPrototypeOf(e)===null)&&!(Symbol.toStringTag in t)&&!(Symbol.iterator in t)},Bo=ge("Date"),Ho=ge("File"),zo=ge("Blob"),Vo=ge("FileList"),Wo=t=>qs(t)&&Ke(t.pipe),Jo=t=>{const e="[object FormData]";return t&&(typeof FormData=="function"&&t instanceof FormData||Vs.call(t)===e||Ke(t.toString)&&t.toString()===e)},qo=ge("URLSearchParams"),Go=t=>t.trim?t.trim():t.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g,"");function en(t,e,{allOwnKeys:n=!1}={}){if(t===null||typeof t>"u")return;let r,s;if(typeof t!="object"&&(t=[t]),vt(t))for(r=0,s=t.length;r<s;r++)e.call(null,t[r],r,t);else{const i=n?Object.getOwnPropertyNames(t):Object.keys(t),o=i.length;let a;for(r=0;r<o;r++)a=i[r],e.call(null,t[a],a,t)}}function Un(){const t={},e=(n,r)=>{Ot(t[r])&&Ot(n)?t[r]=Un(t[r],n):Ot(n)?t[r]=Un({},n):vt(n)?t[r]=n.slice():t[r]=n};for(let n=0,r=arguments.length;n<r;n++)arguments[n]&&en(arguments[n],e);return t}const Ko=(t,e,n,{allOwnKeys:r}={})=>(en(e,(s,i)=>{n&&Ke(s)?t[i]=zs(s,n):t[i]=s},{allOwnKeys:r}),t),Xo=t=>(t.charCodeAt(0)===65279&&(t=t.slice(1)),t),Yo=(t,e,n,r)=>{t.prototype=Object.create(e.prototype,r),t.prototype.constructor=t,Object.defineProperty(t,"super",{value:e.prototype}),n&&Object.assign(t.prototype,n)},Qo=(t,e,n,r)=>{let s,i,o;const a={};if(e=e||{},t==null)return e;do{for(s=Object.getOwnPropertyNames(t),i=s.length;i-- >0;)o=s[i],(!r||r(o,t,e))&&!a[o]&&(e[o]=t[o],a[o]=!0);t=n!==!1&&er(t)}while(t&&(!n||n(t,e))&&t!==Object.prototype);return e},Zo=(t,e,n)=>{t=String(t),(n===void 0||n>t.length)&&(n=t.length),n-=e.length;const r=t.indexOf(e,n);return r!==-1&&r===n},ea=t=>{if(!t)return null;if(vt(t))return t;let e=t.length;if(!Js(e))return null;const n=new Array(e);for(;e-- >0;)n[e]=t[e];return n},ta=(t=>e=>t&&e instanceof t)(typeof Uint8Array<"u"&&er(Uint8Array)),na=(t,e)=>{const r=(t&&t[Symbol.iterator]).call(t);let s;for(;(s=r.next())&&!s.done;){const i=s.value;e.call(t,i[0],i[1])}},ra=(t,e)=>{let n;const r=[];for(;(n=t.exec(e))!==null;)r.push(n);return r},sa=ge("HTMLFormElement"),ia=t=>t.toLowerCase().replace(/[_-\s]([a-z\d])(\w*)/g,function(n,r,s){return r.toUpperCase()+s}),jr=(({hasOwnProperty:t})=>(e,n)=>t.call(e,n))(Object.prototype),oa=ge("RegExp"),Gs=(t,e)=>{const n=Object.getOwnPropertyDescriptors(t),r={};en(n,(s,i)=>{e(s,i,t)!==!1&&(r[i]=s)}),Object.defineProperties(t,r)},aa=t=>{Gs(t,(e,n)=>{const r=t[n];if(!!Ke(r)){if(e.enumerable=!1,"writable"in e){e.writable=!1;return}e.set||(e.set=()=>{throw Error("Can not read-only method '"+n+"'")})}})},la=(t,e)=>{const n={},r=s=>{s.forEach(i=>{n[i]=!0})};return vt(t)?r(t):r(String(t).split(e)),n},ca=()=>{},ua=(t,e)=>(t=+t,Number.isFinite(t)?t:e),d={isArray:vt,isArrayBuffer:Ws,isBuffer:Mo,isFormData:Jo,isArrayBufferView:Uo,isString:Fo,isNumber:Js,isBoolean:jo,isObject:qs,isPlainObject:Ot,isUndefined:Mn,isDate:Bo,isFile:Ho,isBlob:zo,isRegExp:oa,isFunction:Ke,isStream:Wo,isURLSearchParams:qo,isTypedArray:ta,isFileList:Vo,forEach:en,merge:Un,extend:Ko,trim:Go,stripBOM:Xo,inherits:Yo,toFlatObject:Qo,kindOf:tr,kindOfTest:ge,endsWith:Zo,toArray:ea,forEachEntry:na,matchAll:ra,isHTMLForm:sa,hasOwnProperty:jr,hasOwnProp:jr,reduceDescriptors:Gs,freezeMethods:aa,toObjectSet:la,toCamelCase:ia,noop:ca,toFiniteNumber:ua};function $(t,e,n,r,s){Error.call(this),Error.captureStackTrace?Error.captureStackTrace(this,this.constructor):this.stack=new Error().stack,this.message=t,this.name="AxiosError",e&&(this.code=e),n&&(this.config=n),r&&(this.request=r),s&&(this.response=s)}d.inherits($,Error,{toJSON:function(){return{message:this.message,name:this.name,description:this.description,number:this.number,fileName:this.fileName,lineNumber:this.lineNumber,columnNumber:this.columnNumber,stack:this.stack,config:this.config,code:this.code,status:this.response&&this.response.status?this.response.status:null}}});const Ks=$.prototype,Xs={};["ERR_BAD_OPTION_VALUE","ERR_BAD_OPTION","ECONNABORTED","ETIMEDOUT","ERR_NETWORK","ERR_FR_TOO_MANY_REDIRECTS","ERR_DEPRECATED","ERR_BAD_RESPONSE","ERR_BAD_REQUEST","ERR_CANCELED","ERR_NOT_SUPPORT","ERR_INVALID_URL"].forEach(t=>{Xs[t]={value:t}});Object.defineProperties($,Xs);Object.defineProperty(Ks,"isAxiosError",{value:!0});$.from=(t,e,n,r,s,i)=>{const o=Object.create(Ks);return d.toFlatObject(t,o,function(c){return c!==Error.prototype},a=>a!=="isAxiosError"),$.call(o,t.message,e,n,r,s),o.cause=t,o.name=t.name,i&&Object.assign(o,i),o};var da=typeof self=="object"?self.FormData:window.FormData;function Fn(t){return d.isPlainObject(t)||d.isArray(t)}function Ys(t){return d.endsWith(t,"[]")?t.slice(0,-2):t}function Br(t,e,n){return t?t.concat(e).map(function(s,i){return s=Ys(s),!n&&i?"["+s+"]":s}).join(n?".":""):e}function fa(t){return d.isArray(t)&&!t.some(Fn)}const ha=d.toFlatObject(d,{},null,function(e){return/^is[A-Z]/.test(e)});function ga(t){return t&&d.isFunction(t.append)&&t[Symbol.toStringTag]==="FormData"&&t[Symbol.iterator]}function tn(t,e,n){if(!d.isObject(t))throw new TypeError("target must be an object");e=e||new(da||FormData),n=d.toFlatObject(n,{metaTokens:!0,dots:!1,indexes:!1},!1,function(v,x){return!d.isUndefined(x[v])});const r=n.metaTokens,s=n.visitor||u,i=n.dots,o=n.indexes,c=(n.Blob||typeof Blob<"u"&&Blob)&&ga(e);if(!d.isFunction(s))throw new TypeError("visitor must be a function");function l(h){if(h===null)return"";if(d.isDate(h))return h.toISOString();if(!c&&d.isBlob(h))throw new $("Blob is not supported. Use a Buffer instead.");return d.isArrayBuffer(h)||d.isTypedArray(h)?c&&typeof Blob=="function"?new Blob([h]):Buffer.from(h):h}function u(h,v,x){let y=h;if(h&&!x&&typeof h=="object"){if(d.endsWith(v,"{}"))v=r?v:v.slice(0,-2),h=JSON.stringify(h);else if(d.isArray(h)&&fa(h)||d.isFileList(h)||d.endsWith(v,"[]")&&(y=d.toArray(h)))return v=Ys(v),y.forEach(function(_,k){!(d.isUndefined(_)||_===null)&&e.append(o===!0?Br([v],k,i):o===null?v:v+"[]",l(_))}),!1}return Fn(h)?!0:(e.append(Br(x,v,i),l(h)),!1)}const m=[],b=Object.assign(ha,{defaultVisitor:u,convertValue:l,isVisitable:Fn});function p(h,v){if(!d.isUndefined(h)){if(m.indexOf(h)!==-1)throw Error("Circular reference detected in "+v.join("."));m.push(h),d.forEach(h,function(y,I){(!(d.isUndefined(y)||y===null)&&s.call(e,y,d.isString(I)?I.trim():I,v,b))===!0&&p(y,v?v.concat(I):[I])}),m.pop()}}if(!d.isObject(t))throw new TypeError("data must be an object");return p(t),e}function Hr(t){const e={"!":"%21","'":"%27","(":"%28",")":"%29","~":"%7E","%20":"+","%00":"\0"};return encodeURIComponent(t).replace(/[!'()~]|%20|%00/g,function(r){return e[r]})}function nr(t,e){this._pairs=[],t&&tn(t,this,e)}const Qs=nr.prototype;Qs.append=function(e,n){this._pairs.push([e,n])};Qs.toString=function(e){const n=e?function(r){return e.call(this,r,Hr)}:Hr;return this._pairs.map(function(s){return n(s[0])+"="+n(s[1])},"").join("&")};function ma(t){return encodeURIComponent(t).replace(/%3A/gi,":").replace(/%24/g,"$").replace(/%2C/gi,",").replace(/%20/g,"+").replace(/%5B/gi,"[").replace(/%5D/gi,"]")}function Zs(t,e,n){if(!e)return t;const r=n&&n.encode||ma,s=n&&n.serialize;let i;if(s?i=s(e,n):i=d.isURLSearchParams(e)?e.toString():new nr(e,n).toString(r),i){const o=t.indexOf("#");o!==-1&&(t=t.slice(0,o)),t+=(t.indexOf("?")===-1?"?":"&")+i}return t}class zr{constructor(){this.handlers=[]}use(e,n,r){return this.handlers.push({fulfilled:e,rejected:n,synchronous:r?r.synchronous:!1,runWhen:r?r.runWhen:null}),this.handlers.length-1}eject(e){this.handlers[e]&&(this.handlers[e]=null)}clear(){this.handlers&&(this.handlers=[])}forEach(e){d.forEach(this.handlers,function(r){r!==null&&e(r)})}}const ei={silentJSONParsing:!0,forcedJSONParsing:!0,clarifyTimeoutError:!1},pa=typeof URLSearchParams<"u"?URLSearchParams:nr,ba=FormData,va=(()=>{let t;return typeof navigator<"u"&&((t=navigator.product)==="ReactNative"||t==="NativeScript"||t==="NS")?!1:typeof window<"u"&&typeof document<"u"})(),ue={isBrowser:!0,classes:{URLSearchParams:pa,FormData:ba,Blob},isStandardBrowserEnv:va,protocols:["http","https","file","blob","url","data"]};function ya(t,e){return tn(t,new ue.classes.URLSearchParams,Object.assign({visitor:function(n,r,s,i){return ue.isNode&&d.isBuffer(n)?(this.append(r,n.toString("base64")),!1):i.defaultVisitor.apply(this,arguments)}},e))}function _a(t){return d.matchAll(/\w+|\[(\w*)]/g,t).map(e=>e[0]==="[]"?"":e[1]||e[0])}function wa(t){const e={},n=Object.keys(t);let r;const s=n.length;let i;for(r=0;r<s;r++)i=n[r],e[i]=t[i];return e}function ti(t){function e(n,r,s,i){let o=n[i++];const a=Number.isFinite(+o),c=i>=n.length;return o=!o&&d.isArray(s)?s.length:o,c?(d.hasOwnProp(s,o)?s[o]=[s[o],r]:s[o]=r,!a):((!s[o]||!d.isObject(s[o]))&&(s[o]=[]),e(n,r,s[o],i)&&d.isArray(s[o])&&(s[o]=wa(s[o])),!a)}if(d.isFormData(t)&&d.isFunction(t.entries)){const n={};return d.forEachEntry(t,(r,s)=>{e(_a(r),s,n,0)}),n}return null}function xa(t,e,n){const r=n.config.validateStatus;!n.status||!r||r(n.status)?t(n):e(new $("Request failed with status code "+n.status,[$.ERR_BAD_REQUEST,$.ERR_BAD_RESPONSE][Math.floor(n.status/100)-4],n.config,n.request,n))}const Sa=ue.isStandardBrowserEnv?function(){return{write:function(n,r,s,i,o,a){const c=[];c.push(n+"="+encodeURIComponent(r)),d.isNumber(s)&&c.push("expires="+new Date(s).toGMTString()),d.isString(i)&&c.push("path="+i),d.isString(o)&&c.push("domain="+o),a===!0&&c.push("secure"),document.cookie=c.join("; ")},read:function(n){const r=document.cookie.match(new RegExp("(^|;\\s*)("+n+")=([^;]*)"));return r?decodeURIComponent(r[3]):null},remove:function(n){this.write(n,"",Date.now()-864e5)}}}():function(){return{write:function(){},read:function(){return null},remove:function(){}}}();function Ea(t){return/^([a-z][a-z\d+\-.]*:)?\/\//i.test(t)}function Ia(t,e){return e?t.replace(/\/+$/,"")+"/"+e.replace(/^\/+/,""):t}function ni(t,e){return t&&!Ea(e)?Ia(t,e):e}const Ta=ue.isStandardBrowserEnv?function(){const e=/(msie|trident)/i.test(navigator.userAgent),n=document.createElement("a");let r;function s(i){let o=i;return e&&(n.setAttribute("href",o),o=n.href),n.setAttribute("href",o),{href:n.href,protocol:n.protocol?n.protocol.replace(/:$/,""):"",host:n.host,search:n.search?n.search.replace(/^\?/,""):"",hash:n.hash?n.hash.replace(/^#/,""):"",hostname:n.hostname,port:n.port,pathname:n.pathname.charAt(0)==="/"?n.pathname:"/"+n.pathname}}return r=s(window.location.href),function(o){const a=d.isString(o)?s(o):o;return a.protocol===r.protocol&&a.host===r.host}}():function(){return function(){return!0}}();function yt(t,e,n){$.call(this,t??"canceled",$.ERR_CANCELED,e,n),this.name="CanceledError"}d.inherits(yt,$,{__CANCEL__:!0});function Ca(t){const e=/^([-+\w]{1,25})(:?\/\/|:)/.exec(t);return e&&e[1]||""}const ka=d.toObjectSet(["age","authorization","content-length","content-type","etag","expires","from","host","if-modified-since","if-unmodified-since","last-modified","location","max-forwards","proxy-authorization","referer","retry-after","user-agent"]),$a=t=>{const e={};let n,r,s;return t&&t.split(`
`).forEach(function(o){s=o.indexOf(":"),n=o.substring(0,s).trim().toLowerCase(),r=o.substring(s+1).trim(),!(!n||e[n]&&ka[n])&&(n==="set-cookie"?e[n]?e[n].push(r):e[n]=[r]:e[n]=e[n]?e[n]+", "+r:r)}),e},Vr=Symbol("internals"),ri=Symbol("defaults");function it(t){return t&&String(t).trim().toLowerCase()}function Rt(t){return t===!1||t==null?t:d.isArray(t)?t.map(Rt):String(t)}function Aa(t){const e=Object.create(null),n=/([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;let r;for(;r=n.exec(t);)e[r[1]]=r[2];return e}function Wr(t,e,n,r){if(d.isFunction(r))return r.call(this,e,n);if(!!d.isString(e)){if(d.isString(r))return e.indexOf(r)!==-1;if(d.isRegExp(r))return r.test(e)}}function Na(t){return t.trim().toLowerCase().replace(/([a-z\d])(\w*)/g,(e,n,r)=>n.toUpperCase()+r)}function Oa(t,e){const n=d.toCamelCase(" "+e);["get","set","has"].forEach(r=>{Object.defineProperty(t,r+n,{value:function(s,i,o){return this[r].call(this,e,s,i,o)},configurable:!0})})}function rt(t,e){e=e.toLowerCase();const n=Object.keys(t);let r=n.length,s;for(;r-- >0;)if(s=n[r],e===s.toLowerCase())return s;return null}function Y(t,e){t&&this.set(t),this[ri]=e||null}Object.assign(Y.prototype,{set:function(t,e,n){const r=this;function s(i,o,a){const c=it(o);if(!c)throw new Error("header name must be a non-empty string");const l=rt(r,c);l&&a!==!0&&(r[l]===!1||a===!1)||(r[l||o]=Rt(i))}return d.isPlainObject(t)?d.forEach(t,(i,o)=>{s(i,o,e)}):s(e,t,n),this},get:function(t,e){if(t=it(t),!t)return;const n=rt(this,t);if(n){const r=this[n];if(!e)return r;if(e===!0)return Aa(r);if(d.isFunction(e))return e.call(this,r,n);if(d.isRegExp(e))return e.exec(r);throw new TypeError("parser must be boolean|regexp|function")}},has:function(t,e){if(t=it(t),t){const n=rt(this,t);return!!(n&&(!e||Wr(this,this[n],n,e)))}return!1},delete:function(t,e){const n=this;let r=!1;function s(i){if(i=it(i),i){const o=rt(n,i);o&&(!e||Wr(n,n[o],o,e))&&(delete n[o],r=!0)}}return d.isArray(t)?t.forEach(s):s(t),r},clear:function(){return Object.keys(this).forEach(this.delete.bind(this))},normalize:function(t){const e=this,n={};return d.forEach(this,(r,s)=>{const i=rt(n,s);if(i){e[i]=Rt(r),delete e[s];return}const o=t?Na(s):String(s).trim();o!==s&&delete e[s],e[o]=Rt(r),n[o]=!0}),this},toJSON:function(t){const e=Object.create(null);return d.forEach(Object.assign({},this[ri]||null,this),(n,r)=>{n==null||n===!1||(e[r]=t&&d.isArray(n)?n.join(", "):n)}),e}});Object.assign(Y,{from:function(t){return d.isString(t)?new this($a(t)):t instanceof this?t:new this(t)},accessor:function(t){const n=(this[Vr]=this[Vr]={accessors:{}}).accessors,r=this.prototype;function s(i){const o=it(i);n[o]||(Oa(r,i),n[o]=!0)}return d.isArray(t)?t.forEach(s):s(t),this}});Y.accessor(["Content-Type","Content-Length","Accept","Accept-Encoding","User-Agent"]);d.freezeMethods(Y.prototype);d.freezeMethods(Y);function Ra(t,e){t=t||10;const n=new Array(t),r=new Array(t);let s=0,i=0,o;return e=e!==void 0?e:1e3,function(c){const l=Date.now(),u=r[i];o||(o=l),n[s]=c,r[s]=l;let m=i,b=0;for(;m!==s;)b+=n[m++],m=m%t;if(s=(s+1)%t,s===i&&(i=(i+1)%t),l-o<e)return;const p=u&&l-u;return p?Math.round(b*1e3/p):void 0}}function Jr(t,e){let n=0;const r=Ra(50,250);return s=>{const i=s.loaded,o=s.lengthComputable?s.total:void 0,a=i-n,c=r(a),l=i<=o;n=i;const u={loaded:i,total:o,progress:o?i/o:void 0,bytes:a,rate:c||void 0,estimated:c&&o&&l?(o-i)/c:void 0};u[e?"download":"upload"]=!0,t(u)}}function qr(t){return new Promise(function(n,r){let s=t.data;const i=Y.from(t.headers).normalize(),o=t.responseType;let a;function c(){t.cancelToken&&t.cancelToken.unsubscribe(a),t.signal&&t.signal.removeEventListener("abort",a)}d.isFormData(s)&&ue.isStandardBrowserEnv&&i.setContentType(!1);let l=new XMLHttpRequest;if(t.auth){const p=t.auth.username||"",h=t.auth.password?unescape(encodeURIComponent(t.auth.password)):"";i.set("Authorization","Basic "+btoa(p+":"+h))}const u=ni(t.baseURL,t.url);l.open(t.method.toUpperCase(),Zs(u,t.params,t.paramsSerializer),!0),l.timeout=t.timeout;function m(){if(!l)return;const p=Y.from("getAllResponseHeaders"in l&&l.getAllResponseHeaders()),v={data:!o||o==="text"||o==="json"?l.responseText:l.response,status:l.status,statusText:l.statusText,headers:p,config:t,request:l};xa(function(y){n(y),c()},function(y){r(y),c()},v),l=null}if("onloadend"in l?l.onloadend=m:l.onreadystatechange=function(){!l||l.readyState!==4||l.status===0&&!(l.responseURL&&l.responseURL.indexOf("file:")===0)||setTimeout(m)},l.onabort=function(){!l||(r(new $("Request aborted",$.ECONNABORTED,t,l)),l=null)},l.onerror=function(){r(new $("Network Error",$.ERR_NETWORK,t,l)),l=null},l.ontimeout=function(){let h=t.timeout?"timeout of "+t.timeout+"ms exceeded":"timeout exceeded";const v=t.transitional||ei;t.timeoutErrorMessage&&(h=t.timeoutErrorMessage),r(new $(h,v.clarifyTimeoutError?$.ETIMEDOUT:$.ECONNABORTED,t,l)),l=null},ue.isStandardBrowserEnv){const p=(t.withCredentials||Ta(u))&&t.xsrfCookieName&&Sa.read(t.xsrfCookieName);p&&i.set(t.xsrfHeaderName,p)}s===void 0&&i.setContentType(null),"setRequestHeader"in l&&d.forEach(i.toJSON(),function(h,v){l.setRequestHeader(v,h)}),d.isUndefined(t.withCredentials)||(l.withCredentials=!!t.withCredentials),o&&o!=="json"&&(l.responseType=t.responseType),typeof t.onDownloadProgress=="function"&&l.addEventListener("progress",Jr(t.onDownloadProgress,!0)),typeof t.onUploadProgress=="function"&&l.upload&&l.upload.addEventListener("progress",Jr(t.onUploadProgress)),(t.cancelToken||t.signal)&&(a=p=>{!l||(r(!p||p.type?new yt(null,t,l):p),l.abort(),l=null)},t.cancelToken&&t.cancelToken.subscribe(a),t.signal&&(t.signal.aborted?a():t.signal.addEventListener("abort",a)));const b=Ca(u);if(b&&ue.protocols.indexOf(b)===-1){r(new $("Unsupported protocol "+b+":",$.ERR_BAD_REQUEST,t));return}l.send(s||null)})}const Gr={http:qr,xhr:qr},Kr={getAdapter:t=>{if(d.isString(t)){const e=Gr[t];if(!t)throw Error(d.hasOwnProp(t)?`Adapter '${t}' is not available in the build`:`Can not resolve adapter '${t}'`);return e}if(!d.isFunction(t))throw new TypeError("adapter is not a function");return t},adapters:Gr},Da={"Content-Type":"application/x-www-form-urlencoded"};function Pa(){let t;return typeof XMLHttpRequest<"u"?t=Kr.getAdapter("xhr"):typeof process<"u"&&d.kindOf(process)==="process"&&(t=Kr.getAdapter("http")),t}function La(t,e,n){if(d.isString(t))try{return(e||JSON.parse)(t),d.trim(t)}catch(r){if(r.name!=="SyntaxError")throw r}return(n||JSON.stringify)(t)}const Xe={transitional:ei,adapter:Pa(),transformRequest:[function(e,n){const r=n.getContentType()||"",s=r.indexOf("application/json")>-1,i=d.isObject(e);if(i&&d.isHTMLForm(e)&&(e=new FormData(e)),d.isFormData(e))return s&&s?JSON.stringify(ti(e)):e;if(d.isArrayBuffer(e)||d.isBuffer(e)||d.isStream(e)||d.isFile(e)||d.isBlob(e))return e;if(d.isArrayBufferView(e))return e.buffer;if(d.isURLSearchParams(e))return n.setContentType("application/x-www-form-urlencoded;charset=utf-8",!1),e.toString();let a;if(i){if(r.indexOf("application/x-www-form-urlencoded")>-1)return ya(e,this.formSerializer).toString();if((a=d.isFileList(e))||r.indexOf("multipart/form-data")>-1){const c=this.env&&this.env.FormData;return tn(a?{"files[]":e}:e,c&&new c,this.formSerializer)}}return i||s?(n.setContentType("application/json",!1),La(e)):e}],transformResponse:[function(e){const n=this.transitional||Xe.transitional,r=n&&n.forcedJSONParsing,s=this.responseType==="json";if(e&&d.isString(e)&&(r&&!this.responseType||s)){const o=!(n&&n.silentJSONParsing)&&s;try{return JSON.parse(e)}catch(a){if(o)throw a.name==="SyntaxError"?$.from(a,$.ERR_BAD_RESPONSE,this,null,this.response):a}}return e}],timeout:0,xsrfCookieName:"XSRF-TOKEN",xsrfHeaderName:"X-XSRF-TOKEN",maxContentLength:-1,maxBodyLength:-1,env:{FormData:ue.classes.FormData,Blob:ue.classes.Blob},validateStatus:function(e){return e>=200&&e<300},headers:{common:{Accept:"application/json, text/plain, */*"}}};d.forEach(["delete","get","head"],function(e){Xe.headers[e]={}});d.forEach(["post","put","patch"],function(e){Xe.headers[e]=d.merge(Da)});function En(t,e){const n=this||Xe,r=e||n,s=Y.from(r.headers);let i=r.data;return d.forEach(t,function(a){i=a.call(n,i,s.normalize(),e?e.status:void 0)}),s.normalize(),i}function si(t){return!!(t&&t.__CANCEL__)}function In(t){if(t.cancelToken&&t.cancelToken.throwIfRequested(),t.signal&&t.signal.aborted)throw new yt}function Xr(t){return In(t),t.headers=Y.from(t.headers),t.data=En.call(t,t.transformRequest),(t.adapter||Xe.adapter)(t).then(function(r){return In(t),r.data=En.call(t,t.transformResponse,r),r.headers=Y.from(r.headers),r},function(r){return si(r)||(In(t),r&&r.response&&(r.response.data=En.call(t,t.transformResponse,r.response),r.response.headers=Y.from(r.response.headers))),Promise.reject(r)})}function ut(t,e){e=e||{};const n={};function r(l,u){return d.isPlainObject(l)&&d.isPlainObject(u)?d.merge(l,u):d.isPlainObject(u)?d.merge({},u):d.isArray(u)?u.slice():u}function s(l){if(d.isUndefined(e[l])){if(!d.isUndefined(t[l]))return r(void 0,t[l])}else return r(t[l],e[l])}function i(l){if(!d.isUndefined(e[l]))return r(void 0,e[l])}function o(l){if(d.isUndefined(e[l])){if(!d.isUndefined(t[l]))return r(void 0,t[l])}else return r(void 0,e[l])}function a(l){if(l in e)return r(t[l],e[l]);if(l in t)return r(void 0,t[l])}const c={url:i,method:i,data:i,baseURL:o,transformRequest:o,transformResponse:o,paramsSerializer:o,timeout:o,timeoutMessage:o,withCredentials:o,adapter:o,responseType:o,xsrfCookieName:o,xsrfHeaderName:o,onUploadProgress:o,onDownloadProgress:o,decompress:o,maxContentLength:o,maxBodyLength:o,beforeRedirect:o,transport:o,httpAgent:o,httpsAgent:o,cancelToken:o,socketPath:o,responseEncoding:o,validateStatus:a};return d.forEach(Object.keys(t).concat(Object.keys(e)),function(u){const m=c[u]||s,b=m(u);d.isUndefined(b)&&m!==a||(n[u]=b)}),n}const ii="1.1.3",rr={};["object","boolean","number","function","string","symbol"].forEach((t,e)=>{rr[t]=function(r){return typeof r===t||"a"+(e<1?"n ":" ")+t}});const Yr={};rr.transitional=function(e,n,r){function s(i,o){return"[Axios v"+ii+"] Transitional option '"+i+"'"+o+(r?". "+r:"")}return(i,o,a)=>{if(e===!1)throw new $(s(o," has been removed"+(n?" in "+n:"")),$.ERR_DEPRECATED);return n&&!Yr[o]&&(Yr[o]=!0,console.warn(s(o," has been deprecated since v"+n+" and will be removed in the near future"))),e?e(i,o,a):!0}};function Ma(t,e,n){if(typeof t!="object")throw new $("options must be an object",$.ERR_BAD_OPTION_VALUE);const r=Object.keys(t);let s=r.length;for(;s-- >0;){const i=r[s],o=e[i];if(o){const a=t[i],c=a===void 0||o(a,i,t);if(c!==!0)throw new $("option "+i+" must be "+c,$.ERR_BAD_OPTION_VALUE);continue}if(n!==!0)throw new $("Unknown option "+i,$.ERR_BAD_OPTION)}}const jn={assertOptions:Ma,validators:rr},pe=jn.validators;class $e{constructor(e){this.defaults=e,this.interceptors={request:new zr,response:new zr}}request(e,n){typeof e=="string"?(n=n||{},n.url=e):n=e||{},n=ut(this.defaults,n);const{transitional:r,paramsSerializer:s}=n;r!==void 0&&jn.assertOptions(r,{silentJSONParsing:pe.transitional(pe.boolean),forcedJSONParsing:pe.transitional(pe.boolean),clarifyTimeoutError:pe.transitional(pe.boolean)},!1),s!==void 0&&jn.assertOptions(s,{encode:pe.function,serialize:pe.function},!0),n.method=(n.method||this.defaults.method||"get").toLowerCase();const i=n.headers&&d.merge(n.headers.common,n.headers[n.method]);i&&d.forEach(["delete","get","head","post","put","patch","common"],function(h){delete n.headers[h]}),n.headers=new Y(n.headers,i);const o=[];let a=!0;this.interceptors.request.forEach(function(h){typeof h.runWhen=="function"&&h.runWhen(n)===!1||(a=a&&h.synchronous,o.unshift(h.fulfilled,h.rejected))});const c=[];this.interceptors.response.forEach(function(h){c.push(h.fulfilled,h.rejected)});let l,u=0,m;if(!a){const p=[Xr.bind(this),void 0];for(p.unshift.apply(p,o),p.push.apply(p,c),m=p.length,l=Promise.resolve(n);u<m;)l=l.then(p[u++],p[u++]);return l}m=o.length;let b=n;for(u=0;u<m;){const p=o[u++],h=o[u++];try{b=p(b)}catch(v){h.call(this,v);break}}try{l=Xr.call(this,b)}catch(p){return Promise.reject(p)}for(u=0,m=c.length;u<m;)l=l.then(c[u++],c[u++]);return l}getUri(e){e=ut(this.defaults,e);const n=ni(e.baseURL,e.url);return Zs(n,e.params,e.paramsSerializer)}}d.forEach(["delete","get","head","options"],function(e){$e.prototype[e]=function(n,r){return this.request(ut(r||{},{method:e,url:n,data:(r||{}).data}))}});d.forEach(["post","put","patch"],function(e){function n(r){return function(i,o,a){return this.request(ut(a||{},{method:e,headers:r?{"Content-Type":"multipart/form-data"}:{},url:i,data:o}))}}$e.prototype[e]=n(),$e.prototype[e+"Form"]=n(!0)});class sr{constructor(e){if(typeof e!="function")throw new TypeError("executor must be a function.");let n;this.promise=new Promise(function(i){n=i});const r=this;this.promise.then(s=>{if(!r._listeners)return;let i=r._listeners.length;for(;i-- >0;)r._listeners[i](s);r._listeners=null}),this.promise.then=s=>{let i;const o=new Promise(a=>{r.subscribe(a),i=a}).then(s);return o.cancel=function(){r.unsubscribe(i)},o},e(function(i,o,a){r.reason||(r.reason=new yt(i,o,a),n(r.reason))})}throwIfRequested(){if(this.reason)throw this.reason}subscribe(e){if(this.reason){e(this.reason);return}this._listeners?this._listeners.push(e):this._listeners=[e]}unsubscribe(e){if(!this._listeners)return;const n=this._listeners.indexOf(e);n!==-1&&this._listeners.splice(n,1)}static source(){let e;return{token:new sr(function(s){e=s}),cancel:e}}}function Ua(t){return function(n){return t.apply(null,n)}}function Fa(t){return d.isObject(t)&&t.isAxiosError===!0}function oi(t){const e=new $e(t),n=zs($e.prototype.request,e);return d.extend(n,$e.prototype,e,{allOwnKeys:!0}),d.extend(n,e,null,{allOwnKeys:!0}),n.create=function(s){return oi(ut(t,s))},n}const D=oi(Xe);D.Axios=$e;D.CanceledError=yt;D.CancelToken=sr;D.isCancel=si;D.VERSION=ii;D.toFormData=tn;D.AxiosError=$;D.Cancel=D.CanceledError;D.all=function(e){return Promise.all(e)};D.spread=Ua;D.isAxiosError=Fa;D.formToJSON=t=>ti(d.isHTMLForm(t)?new FormData(t):t);const Qr="http://0.0.0.0:3000",ja="http://0.0.0.0:8080",Zr=window.location.origin;function Ba(){let t;Zr==Qr?t=ja:t="";const[e,n]=S(t),r=Zr==Qr;return{serverUrl:e,setServerUrl:n,withCredentials:r}}const q=X(Ba);function Ha(){const[t,e]=S("submit");return{tabName:t,setTabName:e}}const Ye=X(Ha),za=w('<a id="tabhead_{props.tabName}" href="#" class="tabhead"></a>');function nn(t){const{tabName:e,setTabName:n}=Ye;return(()=>{const r=za.cloneNode(!0);return r.$$click=()=>n(t.tabName),f(r,()=>t.svg,null),f(r,()=>t.title,null),T(()=>r.classList.toggle("selected",e()==t.tabName)),r})()}N(["click"]);const Va=w('<svg fill="currentColor" stroke-width="0" xmlns="http://www.w3.org/2000/svg"></svg>'),Wa=w("<title></title>");function G(t,e){return(()=>{const n=Va.cloneNode(!0);return Pr(n,()=>t.a,!0,!0),Pr(n,e,!0,!0),f(n,()=>Ro,null),f(n,(()=>{const r=Eo(()=>!!e.title,!0);return()=>r()&&(()=>{const s=Wa.cloneNode(!0);return f(s,()=>e.title),s})()})(),null),T(r=>{const s=t.a.stroke,i={...e.style,overflow:"visible",color:e.color||"currentColor"},o=e.size||"1em",a=e.size||"1em",c=t.c;return s!==r._v$&&V(n,"stroke",r._v$=s),r._v$2=Hs(n,i,r._v$2),o!==r._v$3&&V(n,"height",r._v$3=o),a!==r._v$4&&V(n,"width",r._v$4=a),c!==r._v$5&&(n.innerHTML=r._v$5=c),r},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0}),n})()}function Ja(t){return G({a:{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",viewBox:"0 0 24 24"},c:'<path stroke="none" d="M0 0h24v24H0z"/><path d="M9 13L5 9l4-4M5 9h11a4 4 0 010 8h-1"/>'},t)}function qa(t){return G({a:{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",viewBox:"0 0 24 24"},c:'<path stroke="none" d="M0 0h24v24H0z"/><path d="M14 3v4a1 1 0 001 1h4"/><path d="M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2zM12 11v6"/><path d="M9.5 13.5L12 11l2.5 2.5"/>'},t)}function Ga(){const t=g(qa,{class:"tabheadicon",color:"rgb(156 163 175)"});return g(nn,{tabName:"submit",title:"Submit",svg:t})}function Ka(t){return G({a:{viewBox:"0 0 1024 1024"},c:'<path d="M518.3 459a8 8 0 00-12.6 0l-112 141.7a7.98 7.98 0 006.3 12.9h73.9V856c0 4.4 3.6 8 8 8h60c4.4 0 8-3.6 8-8V613.7H624c6.7 0 10.4-7.7 6.3-12.9L518.3 459z"/><path d="M811.4 366.7C765.6 245.9 648.9 160 512.2 160S258.8 245.8 213 366.6C127.3 389.1 64 467.2 64 560c0 110.5 89.5 200 199.9 200H304c4.4 0 8-3.6 8-8v-60c0-4.4-3.6-8-8-8h-40.1c-33.7 0-65.4-13.4-89-37.7-23.5-24.2-36-56.8-34.9-90.6.9-26.4 9.9-51.2 26.2-72.1 16.7-21.3 40.1-36.8 66.1-43.7l37.9-9.9 13.9-36.6c8.6-22.8 20.6-44.1 35.7-63.4a245.6 245.6 0 0152.4-49.9c41.1-28.9 89.5-44.2 140-44.2s98.9 15.3 140 44.2c19.9 14 37.5 30.8 52.4 49.9 15.1 19.3 27.1 40.7 35.7 63.4l13.8 36.5 37.8 10C846.1 454.5 884 503.8 884 560c0 33.1-12.9 64.3-36.3 87.7a123.07 123.07 0 01-87.6 36.3H720c-4.4 0-8 3.6-8 8v60c0 4.4 3.6 8 8 8h40.1C870.5 760 960 670.5 960 560c0-92.7-63.1-170.7-148.6-193.3z"/>'},t)}function Xa(t){return G({a:{viewBox:"0 0 1024 1024"},c:'<path d="M920 760H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0-568H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0 284H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM216 712H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h72.4v20.5h-35.7c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h35.7V838H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4V716c0-2.2-1.8-4-4-4zM100 188h38v120c0 2.2 1.8 4 4 4h40c2.2 0 4-1.8 4-4V152c0-4.4-3.6-8-8-8h-78c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4zm116 240H100c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4h68.4l-70.3 77.7a8.3 8.3 0 00-2.1 5.4V592c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4v-36c0-2.2-1.8-4-4-4h-68.4l70.3-77.7a8.3 8.3 0 002.1-5.4V432c0-2.2-1.8-4-4-4z"/>'},t)}function Ya(){const t=g(Xa,{class:"tabheadicon",color:"rgb(156 163 175)"});return g(nn,{tabName:"jobs",title:"Jobs",svg:t})}const Qa=w('<svg class="tabheadicon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"></path></svg>');function Za(){const t=Qa.cloneNode(!0);return g(nn,{tabName:"system",title:"System",svg:t})}function el(t){return G({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>'},t)}function tl(t){return G({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>'},t)}function nl(t){return G({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>'},t)}function ir(t){return G({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>'},t)}function rl(t){return G({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>'},t)}function sl(t){return G({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>'},t)}function il(t){return G({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>'},t)}function ol(t){return G({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>'},t)}function al(){const t=g(ol,{class:"tabheadicon",color:"rgb(156 163 175)"});return g(nn,{tabName:"account",title:"Account",svg:t})}const ll=w('<div id="verdiv" class="text-xs absolute left-4 bottom-2 text-gray-400"><span class="text-xs">v</span><span class="curverspan text-xs"></span></div>');function cl(){return ll.cloneNode(!0)}const ul=w('<div id="sidebar_static" class="md:flex md:w-36 md:flex-col md:fixed md:inset-y-0"><div class="flex-1 flex flex-col min-h-0 border-r border-gray-200"><div class="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto"><div class="flex items-center flex-shrink-0 px-4"><img class="h-16 w-auto" alt="Logo"></div><nav class="mt-5 flex-1 px-2 space-y-1"></nav></div></div></div>'),{serverUrl:dl,setServerUrl:dg,withCredentials:fg}=q;function fl(){return(()=>{const t=ul.cloneNode(!0),e=t.firstChild,n=e.firstChild,r=n.firstChild,s=r.firstChild,i=r.nextSibling;return f(i,g(Ga,{}),null),f(i,g(Ya,{}),null),f(i,g(Za,{}),null),f(i,g(al,{}),null),f(n,g(cl,{}),null),T(()=>V(s,"src",dl()+"/submit/images/logo_transparent_bw.png")),t})()}function hl(t){return G({a:{fill:"currentColor",viewBox:"0 0 16 16"},c:'<path d="M11.42 2l3.428 6-3.428 6H4.58L1.152 8 4.58 2h6.84zM4.58 1a1 1 0 00-.868.504l-3.428 6a1 1 0 000 .992l3.428 6A1 1 0 004.58 15h6.84a1 1 0 00.868-.504l3.429-6a1 1 0 000-.992l-3.429-6A1 1 0 0011.42 1H4.58z"/><path d="M6.848 5.933a2.5 2.5 0 102.5 4.33 2.5 2.5 0 00-2.5-4.33zm-1.78 3.915a3.5 3.5 0 116.061-3.5 3.5 3.5 0 01-6.062 3.5z"/>'},t)}async function ai(t){const{serverUrl:e,setServerUrl:n}=q;return(await fetch(e()+t)).json()}async function gl(t){}function ml(){const[t,e]=S({}),[n,r]=S({});function s(c){return c in t()?t()[c]:null}function i(c){var l=t();l[c.name]=c,e(l)}function o(){ai("/store/local").then(function(c){e(c)})}function a(c){return c in n()?n()[c]:(gl(),g(hl,{}))}return{localModules:t,setLocalModules:e,getLocalModule:s,addLocalModule:i,loadAllModules:o,localModuleLogos:n,setLocalModuleLogos:r,getLocalModuleLogo:a}}const rn=X(ml),pl=w('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function At(t){function e(){t.setAssembly(t.value),t.setShow(!1)}return(()=>{const n=pl.cloneNode(!0);return n.$$click=e,f(n,()=>t.title),n})()}N(["click"]);const bl=w('<div id="assembly-select" class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabindex="-1"><div class="py-1" role="none"></div></div>');function vl(t){return(()=>{const e=bl.cloneNode(!0),n=e.firstChild;return f(n,g(At,{value:"auto",title:"Auto",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),f(n,g(At,{value:"hg38",title:"GRCh38/hg38",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),f(n,g(At,{value:"hg19",title:"GRCh37/hg19",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),f(n,g(At,{value:"hg18",title:"GRCh36/hg18",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),T(()=>e.classList.toggle("hidden",!t.show)),e})()}const yl=w('<div id="assembly-select-panel" class="select-div relative inline-block text-left" value=""><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="assembly-select-div" title="Genome assembly">Genome assembly: </button></div></div>');function _l(t){const[e,n]=S(!1),r={"":"Auto",hg38:"GRCh38/hg38",hg19:"GRCh37/hg19",hg18:"GRCh36/hg18"};function s(i){n(!e())}return(()=>{const i=yl.cloneNode(!0),o=i.firstChild,a=o.firstChild;return a.firstChild,a.$$click=s,f(a,()=>r[t.assembly],null),f(a,g(ir,{class:"-mr-1 ml-2 h-5 w-5"}),null),f(i,g(vl,{get show(){return e()},get setAssembly(){return t.setAssembly},setShow:n}),null),i})()}N(["click"]);const wl=w('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function es(t){function e(){t.setInputFormat(t.value),t.setShow(!1)}return(()=>{const n=wl.cloneNode(!0);return n.$$click=e,f(n,()=>t.title),n})()}N(["click"]);function xl(){const[t,e]=S(!1);return{multiuser:t,setMultiuser:e}}const sn=X(xl);function Sl(){const[t,e]=S(!1);return{logged:t,setLogged:e}}const Qe=X(Sl),El=w('<div id="input-format-select" class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabindex="-1"><div class="py-1" role="none"></div></div>'),{multiuser:Il,setMultiuser:hg}=sn,{logged:Tl,setLogged:gg}=Qe;async function Cl(){if(Il()==!1||Tl()==!0)return await ai("/submit/converters")}function kl(t){const[e]=Yn(Cl);return qe(()=>{var n={"":"Auto"};if(!!e()){for(var r=0;r<e().length;r++)n[e()[r].format]=e()[r].title;t.setInputFormats(n)}}),(()=>{const n=El.cloneNode(!0),r=n.firstChild;return f(r,g(es,{value:"",title:"Auto",get setInputFormat(){return t.setInputFormat},get setShow(){return t.setShow}}),null),f(r,g(Ee,{get each(){return e()},children:function(s){return g(es,{get value(){return s.format},get title(){return s.title},get setInputFormat(){return t.setInputFormat},get setShow(){return t.setShow}})}}),null),T(()=>n.classList.toggle("hidden",!t.show)),n})()}const $l=w('<div id="input-format-select-panel" class="select-div relative inline-block text-left ml-6" value=""><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="input-format-select-div" title="Format">Format: </button></div></div>');function Al(t){const[e,n]=S(!1),[r,s]=S({"":"Auto"});function i(o){n(!e())}return(()=>{const o=$l.cloneNode(!0),a=o.firstChild,c=a.firstChild;return c.firstChild,c.$$click=i,f(c,()=>r()[t.inputFormat],null),f(c,g(ir,{class:"-mr-1 ml-2 h-5 w-5"}),null),f(o,g(kl,{get show(){return e()},get setInputFormat(){return t.setInputFormat},setInputFormats:s,setShow:n}),null),o})()}N(["click"]);const Nl=w('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"><div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4"><div class="sm:flex sm:items-start"><div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"><svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v3.75m-9.303 3.376C1.83 19.126 2.914 21 4.645 21h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 4.88c-.866-1.501-3.032-1.501-3.898 0L2.697 17.626zM12 17.25h.007v.008H12v-.008z"></path></svg></div><div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left"><h3 id="error-dialog-title" class="text-lg font-medium leading-6 text-gray-900"></h3><div class="mt-2"><p id="error-dialog-text" class="text-sm text-gray-500"></p></div></div></div></div><div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6"><button id="error-dialog-dismiss-button" type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm">Dismiss</button></div></div></div></div></div>');function Ol(t){return(()=>{const e=Nl.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.firstChild,l=c.nextSibling,u=l.firstChild,m=u.nextSibling,b=m.firstChild,p=o.nextSibling,h=p.firstChild;return f(u,()=>t.title),f(b,()=>t.text),h.$$click=t.setShowErrorDialog,h.$$clickData=!1,e})()}N(["click"]);const Rl=w('<div id="input-upload-list-div" class="w-1/2 flex flex-col justify-center items-center p-2 relative h-full bg-gray-50"><button id="clear_inputfilelist_button" class="text-gray-500 bg-neutral-200 hover:bg-neutral-300 p-1 w-16 rounded-md absolute top-1 left-1" onclick="clearInputUploadList()">Clear</button><div id="input-upload-list-wrapper" class="flex w-full overflow-auto h-[13rem] absolute bottom-1 bg-gray-50"><div id="input-upload-list" class="h-full overflow-auto"></div></div></div>'),Dl=w('<label id="input-drop-area" for="input-file" class="flex items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-md cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600"><div id="input-drop-box" class="w-1/2"><div class="flex flex-col items-center justify-center pt-5 pb-6"><p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop input files</p><p class="text-gray-500 mb-2"> or </p><button class="mb-2 text-sm text-gray-500 dark:text-gray-400 bg-neutral-200 hover:bg-neutral-300 p-2 rounded-md">Manually enter variants</button></div><input type="file" class="hidden" name="input-file" id="input-file" multiple></div></label>'),Pl=w('<span class="pl-2 text-sm text-gray-600 hover:text-gray-400 cursor-pointer round-md inline-block w-5/6" title="Click to remove"></span>');function Ll(t){const[e,n]=S(!1),[r,s]=S({title:"Problem",text:"?"});qe(function(){});function i(a,c){c.preventDefault();for(var l=0;l<t.inputDataDrop.length;l++)if(t.inputDataDrop[l].name==a){t.setInputDataDrop([...t.inputDataDrop.slice(0,l),...t.inputDataDrop.slice(l+1,t.inputDataDrop.length)]);break}}function o(a){const c=a.target.files;for(var l=0;l<c.length;l++)if(c[l].name.indexOf(" ")>=0){s({title:"Problem",text:"Input file names should not have space."}),n(!0);break}t.setInputDataDrop([...t.inputDataDrop,...c])}return(()=>{const a=Dl.cloneNode(!0),c=a.firstChild,l=c.firstChild,u=l.firstChild,m=u.nextSibling,b=m.nextSibling,p=l.nextSibling;return f(a,g(oe,{get when(){return t.inputDataDrop.length>0},get children(){const h=Rl.cloneNode(!0),v=h.firstChild,x=v.nextSibling,y=x.firstChild;return f(y,g(Ee,{get each(){return t.inputDataDrop},children:I=>(()=>{const _=Pl.cloneNode(!0);return _.$$click=i,_.$$clickData=I.name,f(_,()=>I.name),_})()})),h}}),c),f(l,g(Ka,{class:"w-10 h-10",color:"#9ca3af"}),u),b.$$click=t.setInputMode,b.$$clickData="paste",p.addEventListener("change",o),f(a,g(Lo,{get children(){return g(oe,{get when(){return e()},get children(){return g(Ol,{get title(){return r().title},get text(){return r().text},setShowErrorDialog:n})}})}}),null),a})()}N(["click"]);const Ml=w(`<div id="input-paste-area" class="relative w-full h-64 border-2 border-gray-300 border-dashed rounded-md"><textarea id="input-text" class="font-mono border-0 bg-gray-50 text-gray-600 p-4 resize-none w-full h-full" placeholder="Copy and paste or type input variants. VCF is supported. A quick and simple format is space-delimited one:

chr1 9384934 + A T

which is chromosome, position, strand, a reference allele, and an alternate allele.

Alternatively, paths to input files in the server can be used as well. For example,

/mnt/oakvar/input/sample/sample_1.vcf
"></textarea><div class="top-2 right-3 absolute cursor-pointer" title="Click to go back"></div><div class="absolute bottom-1 right-1 text-gray-400 text-sm"><button value="cravat" class="p-1 text-gray-500 bg-neutral-200 hover:bg-neutral-300">Try an example</button></div></div>`);function Ul(t){function e(r){const{serverUrl:s,setServerUrl:i}=q;t.setAssembly("hg38"),t.setInputFormat("vcf"),fetch(`${s()}/submit/input-examples/${t.inputFormat}.${t.assembly}.txt`).then(o=>o.text()).then(o=>{t.changeInputData("paste",o)})}function n(r){t.changeInputData("paste",r.target.value)}return(()=>{const r=Ml.cloneNode(!0),s=r.firstChild,i=s.nextSibling,o=i.nextSibling,a=o.firstChild;return s.$$keyup=n,i.$$click=t.setInputMode,i.$$clickData="drop",f(i,g(Ja,{class:"w-5 h-5 mr-2"})),a.$$click=e,T(()=>s.value=t.inputDataPaste),r})()}N(["keyup","click"]);const Fl=w('<div id="job-name-div" class="mt-4 w-full"><textarea id="job-name" class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full " placeholder="(Optional) job name"></textarea></div>');function jl(t){function e(n){t.setJobName(n.target.value)}return(()=>{const n=Fl.cloneNode(!0),r=n.firstChild;return r.$$keyup=e,T(()=>n.classList.toggle("hidden",!t.inputExists)),T(()=>r.value=t.jobName),n})()}N(["keyup"]);const Bl=w('<div id="submit-note-div" class="mt-4 w-full"><textarea id="submit-note" class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full" placeholder="(Optional) note for this job"></textarea></div>');function Hl(t){function e(n){t.setJobNote(n.target.value)}return(()=>{const n=Bl.cloneNode(!0),r=n.firstChild;return r.$$keyup=e,T(()=>n.classList.toggle("hidden",!t.inputExists)),T(()=>r.value=t.jobNote),n})()}N(["keyup"]);const zl=w('<div id="submit-job-button-div" class="mt-4"><button id="submit-job-button" type="button" class="inline-flex items-center h-12 rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Annotate</button></div>');function Vl(t){return(()=>{const e=zl.cloneNode(!0),n=e.firstChild;return Zn(n,"click",t.submitFn,!0),T(()=>e.classList.toggle("hidden",!t.inputExists)),e})()}N(["click"]);const Wl=w('<div id="input-div" class="w-[40rem] justify-center items-center flex flex-col" style="height: calc(100vh - 10rem);"><div class="flex"></div><div class="w-full flex items-center justify-center mt-1" ondragenter="onDragEnterInputFiles(event)" ondragover="onDragOverInputFiles(event)" ondragleave="onDragLeaveInputFiles(event)" ondrop="onDropInputFiles(event)"></div></div>');function Jl(t){function e(n,r){t.setInputMode(n),n=="drop"?t.setInputDataDrop(r):n=="paste"&&t.setInputDataPaste(r)}return qe(function(){t.inputMode=="drop"?t.setInputExists(t.inputDataDrop.length>0):t.inputMode=="paste"&&t.setInputExists(t.inputDataPaste.length>0)}),(()=>{const n=Wl.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return f(r,g(_l,{get assembly(){return t.assembly},get setAssembly(){return t.setAssembly}}),null),f(r,g(Al,{get inputFormat(){return t.inputFormat},get setInputFormat(){return t.setInputFormat}}),null),f(s,g(bo,{get children(){return[g(Or,{get when(){return t.inputMode=="drop"},get children(){return g(Ll,{get setInputMode(){return t.setInputMode},get inputDataDrop(){return t.inputDataDrop},get setInputDataDrop(){return t.setInputDataDrop}})}}),g(Or,{get when(){return t.inputMode=="paste"},get children(){return g(Ul,{get setInputMode(){return t.setInputMode},changeInputData:e,get inputDataPaste(){return t.inputDataPaste},get assembly(){return t.assembly},get setAssembly(){return t.setAssembly},get inputFormat(){return t.inputFormat},get setInputFormat(){return t.setInputFormat}})}})]}})),f(n,g(jl,{get inputExists(){return t.inputExists},get jobName(){return t.jobName},get setJobName(){return t.setJobName}}),null),f(n,g(Hl,{get inputExists(){return t.inputExists},get jobNote(){return t.jobNote},get setJobNote(){return t.setJobNote}}),null),f(n,g(Vl,{get inputExists(){return t.inputExists},get submitFn(){return t.submitFn}}),null),n})()}const ql=w('<div class="modulecard relative items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400 p-2 max-h-64"><div class="float-left w-24 h-24 mr-2 flex justify-center items-center"><img class="w-20 rounded-lg"></div><div class="min-w-0 flex-1"><a class="focus:online-none"><span class="absolute inset-0"></span><p class="text-md font-semibold text-gray-700"></p><p class="text-sm text-gray-500"></p></a></div></div>'),{serverUrl:Gl,setServerUrl:mg}=q,{localModules:Kl,setLocalModules:pg,getLocalModule:bg,addLocalModule:vg,loadAllModules:yg,getLocalModuleLogo:_g}=rn;function or(t){const e=Kl()[t.moduleName],n=e.type;function r(l){for(const u in l)if(t.moduleName==u)return!0;return!1}function s(){return r(t.annotators)||r(t.postaggregators)||r(t.reporters)}function i(){let l;return n=="annotator"?l={...t.annotators}:n=="postaggregator"?l={...t.postaggregators}:n=="reporter"&&(l={...t.reporters}),l}function o(l){s()?delete l[t.moduleName]:l[t.moduleName]=e}function a(l){n=="annotator"?t.setAnnotators(l):n=="postaggregator"?t.setPostaggregators(l):n=="reporter"&&t.setReporters(l)}function c(){let l=i();o(l),a(l)}return(()=>{const l=ql.cloneNode(!0),u=l.firstChild,m=u.firstChild,b=u.nextSibling,p=b.firstChild,h=p.firstChild,v=h.nextSibling,x=v.nextSibling;return l.$$click=c,f(v,()=>e&&e.title),f(x,()=>e&&e.conf.description),T(y=>{const I=!!s(),_=e&&e.name,k=e&&e.kind,C=Gl()+"/store/locallogo?module="+t.moduleName;return I!==y._v$&&l.classList.toggle("checked",y._v$=I),_!==y._v$2&&V(l,"name",y._v$2=_),k!==y._v$3&&V(l,"kind",y._v$3=k),C!==y._v$4&&V(m,"src",y._v$4=C),y},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0}),l})()}N(["click"]);const Xl=w('<div id="report-choice-div" class="w-[36rem] flex flex-col justify-center items-center"><div class="text-md text-gray-600">Select optional reporters to run.</div><div id="report-choice-items" class="w-96 grid gap-2 justify-center overflow-y-auto bg-gray-100 py-4 rounded-md" style="height: calc(100vh - 10rem);"></div></div>'),Yl=async()=>{const{serverUrl:t,setServerUrl:e}=q;return(await(await fetch(t()+"/submit/reporttypes")).json()).valid};function Ql(t){const[e]=Yn(Yl);return(()=>{const n=Xl.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return f(s,g(Ee,{get each(){return e()},children:i=>g(or,{moduleName:i+"reporter",get reporters(){return t.reporters},get setReporters(){return t.setReporters}})})),n})()}const Zl=w('<div id="cta-analysis-module-choice" class="absolute inset-x-0 bottom-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Scroll down or click to select analysis modules</span></p></div></div></div></div></div>');function ec(t){function e(){document.querySelector("#analysis-module-choice-div").scrollIntoView({behavior:"smooth"})}return(()=>{const n=Zl.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild;return n.$$click=e,f(o,g(el,{color:"#6b7280"}),a),n})()}N(["click"]);const tc=w('<button class="filter-category" role="filter-category" type="button"></button>');function ts(t){function e(n){t.setFilterCategory(t.value)}return(()=>{const n=tc.cloneNode(!0);return n.$$click=e,f(n,()=>t.title),T(()=>n.classList.toggle("pinned",t.value==t.filterCategory)),T(()=>n.value=t.value),n})()}N(["click"]);const nc=w('<div class="flex mb-2"><label for="search" class="sr-only">Search</label><input type="text" name="search" class="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm mr-2" placeholder="Search"><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Select all</button><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-2">Deselect all</button></div>');function li(t){function e(n){t.setSearchText(n.target.value)}return(()=>{const n=nc.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return s.$$keyup=e,T(()=>V(n,"id",`search-filtered-modules-${t.kind}`)),T(()=>s.value=t.searchText),n})()}N(["keyup"]);const{localModules:rc,setLocalModules:wg,getLocalModule:xg,addLocalModule:Sg,loadAllModules:Eg}=rn;function ci(t){for(let e in t)return!1;return!0}function sc(t,e){let n=[];for(const[r,s]of Object.entries(rc())){let i=!0;s.type!="annotator"&&s.type!="postaggregator"?i=!1:e!=null&&(e=="no tag"?s.tags.length>0&&(i=!1):s.tags.indexOf(e)==-1&&(i=!1)),i&&t!=null&&(i=!1,(r.indexOf(t)>=0||s.title.indexOf(t)>=0||s.description&&s.description.indexOf(t)>=0)&&(i=!0)),i&&n.push(r)}return n.sort(),n}const ic=w('<div class="filtered-modules-div overflow-auto pr-2 grid grid-cols-2 gap-1" style="height: calc(95vh - 8rem);"></div>');function ui(t){return(()=>{const e=ic.cloneNode(!0);return f(e,g(Ee,{get each(){return sc(t.searchText,t.selectedTag)},children:n=>g(or,{moduleName:n,get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}})})),T(n=>{const r=`filtered-modules-${t.kind}`,s=t.noCols==2,i=t.noCols==1;return r!==n._v$&&V(e,"id",n._v$=r),s!==n._v$2&&e.classList.toggle("grid-cols-2",n._v$2=s),i!==n._v$3&&e.classList.toggle("grid-cols-1",n._v$3=i),n},{_v$:void 0,_v$2:void 0,_v$3:void 0}),e})()}const oc=w('<div id="analysis-module-filter-panel-all" class="analysis-module-filter-panel w-full mt-4 overflow-auto"></div>');function ac(t){const[e,n]=S(null);return(()=>{const r=oc.cloneNode(!0);return f(r,g(li,{kind:"all",get searchText(){return e()},setSearchText:n}),null),f(r,g(ui,{kind:"all",noCols:2,get searchText(){return e()},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),T(()=>r.classList.toggle("hidden",t.filterCategory!="all")),r})()}const lc=w('<div class="relative flex items-start mb-2"><div class="flex items-center"><input type="radio" name="module-tag" class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"><label class="ml-3 block text-sm font-medium text-gray-600"></label></div></div>');function cc(t){return t.replace(" ","_")}function uc(t){return t.replace(/\w\S*/g,function(e){return e.charAt(0).toUpperCase()+e.substr(1).toLowerCase()})}function dc(t){const e=`module-tag-radio-${cc(t.value)}`;return(()=>{const n=lc.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.nextSibling;return s.$$click=t.setSelectedTag,s.$$clickData=t.value,V(s,"id",e),V(i,"for",e),f(i,()=>uc(t.value)),T(()=>s.value=t.value),n})()}N(["click"]);const fc=w('<div id="analysis-module-filter-panel-tags" class="analysis-module-filter-panel w-full mt-4 overflow-auto grid grid-cols-3"><div id="analysis-module-filter-items-tags" class="col-span-1 flex flex-col justify-leading pl-1 overflow-y-auto" style="height: calc(95vh - 8rem);"></div><div class="col-span-2"></div></div>'),hc=async()=>{const{serverUrl:t,setServerUrl:e}=q;let n=await(await fetch(t()+"/submit/tags_annotators_postaggregators")).json();return n.push("no tag"),n};function gc(t){const[e]=Yn(hc),[n,r]=S(null),[s,i]=S(null);return(()=>{const o=fc.cloneNode(!0),a=o.firstChild,c=a.nextSibling;return f(a,g(Ee,{get each(){return e()},children:l=>g(dc,{value:l,setSelectedTag:r})})),f(c,g(li,{kind:"tags",get searchText(){return s()},setSearchText:i}),null),f(c,g(ui,{kind:"tags",noCols:1,get selectedTag(){return n()},get searchText(){return s()},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),T(()=>o.classList.toggle("hidden",t.filterCategory!="tags")),o})()}const mc=w('<div class="analysis-module-filter-wrapper col-span-7"><div id="analysis-module-filter-kinds" class="w-full"></div></div>');function pc(t){const[e,n]=S("all");return(()=>{const r=mc.cloneNode(!0),s=r.firstChild;return f(s,g(ts,{value:"all",title:"All",get filterCategory(){return e()},setFilterCategory:n}),null),f(s,g(ts,{value:"tags",title:"Tags",get filterCategory(){return e()},setFilterCategory:n}),null),f(r,g(ac,{get filterCategory(){return e()},get localModules(){return t.localModules},get setLocalModules(){return t.setLocalModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),f(r,g(gc,{get filterCategory(){return e()},get localModules(){return t.localModules},get setLocalModules(){return t.setLocalModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),r})()}const bc=w('<div class="col-span-4"><div class="text-gray-600 bg-gray-100 rounded-md border border-transparent font-medium px-3 py-1.5 h-[34px]">Selected analysis modules</div><div class="flex mb-2 mt-4"><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 h-[38px]">Clear</button></div><div class="filtered-modules-div overflow-auto pr-2 grid grid-cols-2 gap-1 grid-cols-1" style="height: calc(95vh - 8rem);"></div></div>');function vc(t){function e(){let r=[];for(const s in t.annotators)r.push(s);for(const s in t.postaggregators)r.push(s);return r}function n(){t.setAnnotators({}),t.setPostaggregators({})}return(()=>{const r=bc.cloneNode(!0),s=r.firstChild,i=s.nextSibling,o=i.firstChild,a=i.nextSibling;return o.$$click=n,f(a,g(Ee,{get each(){return e()},children:function(c){return g(or,{moduleName:c,get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}})}})),r})()}N(["click"]);const yc=w('<div id="cta-input" class="absolute inset-x-0 top-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Scroll up or click to go to the input panel</span></p></div></div></div></div></div>');function _c(t){function e(){document.querySelector("#input-div").scrollIntoView({behavior:"smooth"})}return(()=>{const n=yc.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild;return n.$$click=e,f(o,g(nl,{color:"#6b7280"}),a),n})()}N(["click"]);const wc=w('<div id="analysis-module-choice-div" class="relative container mt-6 mb-4 snap-center flex justify-center max-w-7xl h-[95vh] max-w-7xl"><div id="analysis-module-filter-div" class="bg-white p-4 rounded-md ml-4 mt-4 overflow-auto flex flex-col gap-8 text-gray-600 h-[95vh] w-full"><div id="analysis-module-div" class="grid grid-cols-12 gap-2 mt-8" style="height: calc(95vh - 20rem);"><div class="col-span-1 flex flex-col justify-center content-center items-center"></div></div></div></div>');function xc(t){return(()=>{const e=wc.cloneNode(!0),n=e.firstChild,r=n.firstChild,s=r.firstChild;return f(e,g(_c,{}),n),f(r,g(pc,{get localModules(){return t.localModules},get setLocalModules(){return t.setLocalModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),s),f(s,g(tl,{})),f(r,g(vc,{get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),e})()}const Sc=w('<li><a href="#" class="block hover:bg-gray-50"><div class="py-4"><div class="flex items-center justify-between"><p class="truncate text-sm font-medium text-indigo-600"></p></div><div class="mt-2 sm:flex sm:justify-between"><div class="mt-2 w-full flex items-center text-sm text-gray-500 sm:mt-0"><div class="w-full bg-gray-200 rounded-full dark:bg-gray-700"><div class="bg-blue-600 text-xs font-medium text-blue-100 text-center p-0.5 leading-none rounded-full">%</div></div></div></div></div></a></li>');function Ec(t){return(()=>{const e=Sc.cloneNode(!0),n=e.firstChild,r=n.firstChild,s=r.firstChild,i=s.firstChild,o=s.nextSibling,a=o.firstChild,c=a.firstChild,l=c.firstChild,u=l.firstChild;return f(i,()=>t.fileName),f(l,()=>t.progress,u),T(()=>l.style.setProperty("width",t.progress+"%")),e})()}const Ic=w('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6"><div><div class="mt-3 text-center sm:mt-5"><ul role="list" class="divide-y divide-gray-200"></ul></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm">Cancel</button></div></div></div></div></div>');function Tc(t){function e(){t.controller.abort()}return(()=>{const n=Ic.cloneNode(!0),r=n.firstChild,s=r.nextSibling,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.firstChild,l=c.firstChild,u=a.nextSibling,m=u.firstChild;return f(l,g(Ec,{fileName:"Uploading...",get progress(){return t.uploadState.progress}})),m.$$click=e,n})()}N(["click"]);const Bn=Symbol("store-raw"),dt=Symbol("store-node"),Cc=Symbol("store-name");function di(t,e){let n=t[Ne];if(!n&&(Object.defineProperty(t,Ne,{value:n=new Proxy(t,Ac)}),!Array.isArray(t))){const r=Object.keys(t),s=Object.getOwnPropertyDescriptors(t);for(let i=0,o=r.length;i<o;i++){const a=r[i];if(s[a].get){const c=s[a].get.bind(n);Object.defineProperty(t,a,{get:c})}}}return n}function zt(t){let e;return t!=null&&typeof t=="object"&&(t[Ne]||!(e=Object.getPrototypeOf(t))||e===Object.prototype||Array.isArray(t))}function ft(t,e=new Set){let n,r,s,i;if(n=t!=null&&t[Bn])return n;if(!zt(t)||e.has(t))return t;if(Array.isArray(t)){Object.isFrozen(t)?t=t.slice(0):e.add(t);for(let o=0,a=t.length;o<a;o++)s=t[o],(r=ft(s,e))!==s&&(t[o]=r)}else{Object.isFrozen(t)?t=Object.assign({},t):e.add(t);const o=Object.keys(t),a=Object.getOwnPropertyDescriptors(t);for(let c=0,l=o.length;c<l;c++)i=o[c],!a[i].get&&(s=t[i],(r=ft(s,e))!==s&&(t[i]=r))}return t}function Vt(t){let e=t[dt];return e||Object.defineProperty(t,dt,{value:e={}}),e}function Hn(t,e,n){return t[e]||(t[e]=hi(n))}function kc(t,e){const n=Reflect.getOwnPropertyDescriptor(t,e);return!n||n.get||!n.configurable||e===Ne||e===dt||e===Cc||(delete n.value,delete n.writable,n.get=()=>t[Ne][e]),n}function fi(t){if(Ps()){const e=Vt(t);(e._||(e._=hi()))()}}function $c(t){return fi(t),Reflect.ownKeys(t)}function hi(t){const[e,n]=S(t,{equals:!1,internal:!0});return e.$=n,e}const Ac={get(t,e,n){if(e===Bn)return t;if(e===Ne)return n;if(e===Dn)return fi(t),n;const r=Vt(t),s=r.hasOwnProperty(e);let i=s?r[e]():t[e];if(e===dt||e==="__proto__")return i;if(!s){const o=Object.getOwnPropertyDescriptor(t,e);Ps()&&(typeof i!="function"||t.hasOwnProperty(e))&&!(o&&o.get)&&(i=Hn(r,e,i)())}return zt(i)?di(i):i},has(t,e){if(e===Bn||e===Ne||e===Dn||e===dt||e==="__proto__")return!0;const n=Vt(t)[e];return n&&n(),e in t},set(){return!0},deleteProperty(){return!0},ownKeys:$c,getOwnPropertyDescriptor:kc};function Wt(t,e,n,r=!1){if(!r&&t[e]===n)return;const s=t[e],i=t.length;n===void 0?delete t[e]:t[e]=n;let o=Vt(t),a;(a=Hn(o,e,s))&&a.$(()=>n),Array.isArray(t)&&t.length!==i&&(a=Hn(o,"length",i))&&a.$(t.length),(a=o._)&&a.$()}function gi(t,e){const n=Object.keys(e);for(let r=0;r<n.length;r+=1){const s=n[r];Wt(t,s,e[s])}}function Nc(t,e){if(typeof e=="function"&&(e=e(t)),e=ft(e),Array.isArray(e)){if(t===e)return;let n=0,r=e.length;for(;n<r;n++){const s=e[n];t[n]!==s&&Wt(t,n,s)}Wt(t,"length",r)}else gi(t,e)}function ot(t,e,n=[]){let r,s=t;if(e.length>1){r=e.shift();const o=typeof r,a=Array.isArray(t);if(Array.isArray(r)){for(let c=0;c<r.length;c++)ot(t,[r[c]].concat(e),n);return}else if(a&&o==="function"){for(let c=0;c<t.length;c++)r(t[c],c)&&ot(t,[c].concat(e),n);return}else if(a&&o==="object"){const{from:c=0,to:l=t.length-1,by:u=1}=r;for(let m=c;m<=l;m+=u)ot(t,[m].concat(e),n);return}else if(e.length>1){ot(t[r],e,[r].concat(n));return}s=t[r],n=[r].concat(n)}let i=e[0];typeof i=="function"&&(i=i(s,n),i===s)||r===void 0&&i==null||(i=ft(i),r===void 0||zt(s)&&zt(i)&&!Array.isArray(i)?gi(s,i):Wt(t,r,i))}function Oc(...[t,e]){const n=ft(t||{}),r=Array.isArray(n),s=di(n);function i(...o){lo(()=>{r&&o.length===1?Nc(n,o[0]):ot(n,o)})}return[s,i]}const Rc=w('<div class="tabcontent p-4 snap-y snap-mandatory h-screen overflow-y-auto"><div class="relative container flex gap-8 snap-center max-w-7xl h-[95vh] justify-center items-start"></div></div>'),Dc=w("<div>Loading...</div>");function Pc(t){const{tabName:e,setTabName:n}=Ye,[r,s]=S("drop"),[i,o]=S([]),[a,c]=S(""),[l,u]=S([]),[m,b]=S([]),[p,h]=S([]),[v,x]=S(""),[y,I]=S(""),[_,k]=S(!1),[C,J]=S(null),[K,ee]=S(null),[A,L]=S(!1),[M,Z]=S(!1),{localModules:Pe}=rn,{serverUrl:et,setServerUrl:yr,withCredentials:fn}=q,[Ct,Le]=S({});let re=[],Me=null,j={},Ue;function hn(){return a().startsWith("#serverfile")}function gn(){let O=[],F=a().split(`
`);for(var me=1;me<F.length;me++){let nt=F[me];nt==""||nt.startsWith("#")||O.push(nt.trim())}O.length>0&&(j.inputServerFiles=O)}function kt(){re=[];const O=new Blob([a()],{type:"text/plain"});re.push(new File([O],"input"))}function $t(){hn()?gn():kt()}function mn(O){if(O!=null&&(r()=="drop"?re=i():r()=="paste"&&$t(),re.length>0))for(var F=0;F<re.length;F++)O.append("file_"+F,re[F])}function pn(){j.annotators=[];for(const O in m())j.annotators.push(O)}function bn(){j.postaggregators=[];for(const O in p())j.postaggregators.push(O)}function Fe(){j.reports=[];for(const O in l())j.reports.push(O.substring(0,O.lastIndexOf("reporter")))}function vn(){j.genome=y()}function yn(){j.input_format=v()}function tt(){j.job_name=C()}function _n(){j.note=K()}function wn(O){Ue=new AbortController,Z(!0),Le({progress:0}),D({method:"post",url:et()+"/submit/submit?"+Math.random(),data:O,transformRequest:()=>O,signal:Ue.signal,withCredentials:fn,onUploadProgress:F=>{let me=Math.round(F.progress*100);Le({progress:me})}}).then(function(F){Z(!1),setTimeout(function(){t.setJobsTrigger(!t.jobsTrigger)},500)}).catch(function(F){console.error(F),F.code!="ERR_CANCELED"&&alert(F),Le({}),Z(!1)})}function xn(){L(!0),re={},j={},Me=new FormData,mn(Me),pn(),bn(),Fe(),vn(),yn(),tt(),_n(),j.writeadmindb=!0,Me.append("options",JSON.stringify(j)),wn(Me)}return(()=>{const O=Rc.cloneNode(!0),F=O.firstChild;return f(F,g(Jl,{get inputMode(){return r()},setInputMode:s,get inputDataDrop(){return i()},setInputDataDrop:o,get inputDataPaste(){return a()},setInputDataPaste:c,get assembly(){return y()},setAssembly:I,get inputFormat(){return v()},setInputFormat:x,get inputExists(){return _()},setInputExists:k,get jobName(){return C()},setJobName:J,get jobNote(){return K()},setJobNote:ee,submitFn:xn}),null),f(F,g(oe,{get when(){return _()},get children(){return[g(oe,{get when(){return!ci(Pe())},get fallback(){return Dc.cloneNode(!0)},get children(){return g(Ql,{get reporters(){return l()},setReporters:u})}}),g(ec,{})]}}),null),f(O,g(oe,{get when(){return _()},get children(){return g(xc,{get annotators(){return m()},setAnnotators:b,get postaggregators(){return p()},setPostaggregators:h})}}),null),f(O,g(oe,{get when(){return M()},get children(){return g(Tc,{get uploadState(){return Ct()},controller:Ue})}}),null),T(()=>O.classList.toggle("hidden",e()!="submit")),O})()}const Lc=w('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function Mc(t){function e(){t.setAction(t.optionValue),t.execute(),t.setShow(!1)}return(()=>{const n=Lc.cloneNode(!0);return n.$$click=e,f(n,()=>t.optionTitle),n})()}N(["click"]);const Uc=w('<div class="option-list ease-in absolute right-0 z-10 mt-12 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu"><div class="py-1" role="none"></div></div>');function Fc(t){return(()=>{const e=Uc.cloneNode(!0),n=e.firstChild;return f(n,g(Ee,{get each(){return t.options},children:function(r){return g(Mc,{get optionValue(){return r.value},get optionTitle(){return r.title},get execute(){return t.execute},get setAction(){return t.setAction},get setShow(){return t.setShow}})}})),T(()=>e.classList.toggle("hidden",!t.show)),e})()}const jc=w('<div class="select-div relative inline-flex text-left"><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="assembly-select-div" title="Job action">Action</button></div></div>');function Bc(t){const[e,n]=S(!1),[r,s]=S(""),i=[{value:"abort",title:"Abort"},{value:"delete",title:"Delete"}];function o(){t.performJobAction(r())}function a(c){n(!e())}return(()=>{const c=jc.cloneNode(!0),l=c.firstChild,u=l.firstChild;return u.firstChild,u.$$click=a,f(u,g(ir,{class:"-mr-1 ml-2 h-5 w-5"}),null),f(c,g(Fc,{get show(){return e()},options:i,execute:o,setAction:s,setShow:n}),null),c})()}N(["click"]);const Hc=w('<div class="flex bg-white px-4 pb-2 sm:px-6"><div><nav class="isolate inline-flex rounded-md shadow-sm ml-8" aria-label="Pagination"><a href="#" class="jobs-table-page-nav-btn relative inline-flex items-center rounded-l-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span aria-current="page" class="relative z-10 inline-flex items-center border bg-white border-gray-300 text-gray-500 px-4 py-2 text-sm font-medium focus:z-20"></span><a href="#" class="jobs-table-page-nav-btn relative inline-flex items-center rounded-r-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Go to page</span><input type="text" class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">Go</a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Show</span><input type="text" class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">jobs per page</a><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20 ml-4"></a></nav></div></div>');function zc(t){function e(){let o=t.pageno;o=o-1,o<=0&&(o=1),o!=t.pageno&&t.setPageno(o)}function n(){let o=t.pageno;o=o+1,o!=t.pageno&&t.setPageno(o)}function r(o){let a=o.target.value;try{a=parseInt(a)}catch(c){console.error(c);return}a<1&&(a=1),t.setPageno(a)}function s(o){let a=o.target.value;try{a=parseInt(a)}catch(c){console.error(c);return}t.setPagesize(a)}function i(o){t.setJobsTrigger(!t.jobsTrigger)}return(()=>{const o=Hc.cloneNode(!0),a=o.firstChild,c=a.firstChild,l=c.firstChild,u=l.nextSibling,m=u.nextSibling,b=m.nextSibling,p=b.nextSibling,h=p.nextSibling,v=h.nextSibling,x=v.nextSibling,y=x.nextSibling,I=y.nextSibling;return f(a,g(Bc,{get performJobAction(){return t.performJobAction}}),c),l.$$click=e,f(l,g(rl,{class:"w-5 h-5"})),f(u,()=>t.pageno),m.$$click=n,f(m,g(sl,{class:"w-5 h-5"})),p.addEventListener("change",r),x.addEventListener("change",s),I.$$click=i,f(I,g(il,{class:"w-5 h-5"})),T(()=>p.value=t.pageno),T(()=>x.value=t.pagesize),o})()}N(["click"]);const Vc=w('<a class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a>');function Wc(t){return(()=>{const e=Vc.cloneNode(!0);return Zn(e,"click",t.clickFn,!0),f(e,()=>t.children),T(n=>{const r=t.hrefValue,s=t.targetValue;return r!==n._v$&&V(e,"href",n._v$=r),s!==n._v$2&&V(e,"target",n._v$2=s),n},{_v$:void 0,_v$2:void 0}),e})()}N(["click"]);const Jc=w('<span class="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800"></span>'),qc=w('<span class="inline-flex rounded-full bg-amber-100 px-2 text-xs font-semibold leading-5 text-amber-800"></span>'),Gc=w('<span class="inline-flex rounded-full bg-red-100 px-2 text-xs font-semibold leading-5 text-red-800"></span>'),Kc=w('<tr class="text-sm h-16"><td scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8 bg-gray-50"><input type="checkbox" class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></td><td></td><td class="bg-gray-50"></td><td class="text-xs"></td><td class="bg-gray-50"></td><td></td><td class="bg-gray-50"></td></tr>');function Xc(t){return t=="Finished"||t=="Error"||t=="Aborted"}function Yc(t){const{serverUrl:e,setServerUrl:n,withCredentials:r}=q,s=1e3;let i=null;jt(()=>clearInterval(i));function o(){t.changeJobChecked(t.job.uid)}function a(){D.get(e()+"/submit/jobstatus",{params:{uid:t.job.uid},withCredentials:r}).then(function(h){const v=h.data;Xc(v)&&clearInterval(i),t.changeJobStatus(t.job.uid,v)}).catch(function(h){console.error(h)})}function c(){const h=t.job.status;h!="Finished"&&h!="Error"&&h!="Aborted"&&(i=setInterval(function(){a()},s))}function l(){return t.job.status=="Finished"}function u(){return l()?g(Wc,{children:"View",get hrefValue(){return e()+"/result/nocache/index.html?uid="+t.job.uid},targetValue:"_blank"}):""}function m(){const h=t.job.status;if(h=="Finished")return(()=>{const v=Jc.cloneNode(!0);return f(v,()=>t.job.status),v})();if(h=="Aborted")return(()=>{const v=qc.cloneNode(!0);return f(v,()=>t.job.status),v})();if(h=="Error")return(()=>{const v=Gc.cloneNode(!0);return f(v,()=>t.job.status),v})()}function b(){return t.job.statusjson.orig_input_fname?t.job.statusjson.orig_input_fname.join(", "):""}function p(){let h=new Date(t.job.statusjson.submission_time);return(""+h).split("GMT")[0]}return c(),(()=>{const h=Kc.cloneNode(!0),v=h.firstChild,x=v.firstChild,y=v.nextSibling,I=y.nextSibling,_=I.nextSibling,k=_.nextSibling,C=k.nextSibling,J=C.nextSibling;return x.addEventListener("change",o),f(y,()=>t.job.name),f(I,b),f(_,p),f(k,m),f(C,()=>t.job.statusjson.note),f(J,u),h})()}const Qc=w('<div class="flex flex-col"><div class="relative shadow ring-1 ring-black ring-opacity-5 md:rounded-lg overflow-auto"><table class="table-fixed divide-y divide-gray-300"><thead class="table-header-group bg-gray-50 block"><tr><th scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8"><input type="checkbox" class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></th><th scope="col" class="jobs-table-th min-w-[10rem]">Name</th><th scope="col" class="jobs-table-th min-w-[20rem]">Input</th><th scope="col" class="jobs-table-th min-w-[11rem]">Submitted</th><th scope="col" class="jobs-table-th min-w-[5rem]">State</th><th scope="col" class="jobs-table-th min-w-[10rem]">Note</th><th scope="col" class="jobs-table-th min-w-[5rem]">View</th></tr></thead><tbody class="table-row-group divide-y divide-gray-200 bg-white block overflow-auto h-[36rem]"></tbody></table></div></div>');function Zc(t){return(()=>{const e=Qc.cloneNode(!0),n=e.firstChild,r=n.firstChild,s=r.firstChild,i=s.nextSibling;return f(i,g(Ee,{get each(){return t.jobs},children:o=>g(Yc,{job:o,get changeJobStatus(){return t.changeJobStatus},get changeJobChecked(){return t.changeJobChecked}})})),e})()}const eu=w('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="text-center"><p class="text-sm text-gray-500"></p></div></div></div></div></div></div>');function tu(t){return(()=>{const e=eu.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.firstChild;return f(c,()=>t.msg),T(()=>e.classList.toggle("hidden",t.msg==null)),e})()}const nu=w('<div id="tab_jobs" class="tabcontent px-6"><div></div></div>'),{serverUrl:ns,setServerUrl:Ig,withCredentials:rs}=q,{logged:ru,setLogged:su}=Qe,{multiuser:iu,setMultiuser:Tg}=sn;function ou(t){const{tabName:e,setTabName:n}=Ye,[r,s]=Oc([]),[i,o]=S(1),[a,c]=S(10),[l,u]=S(null);qe(function(){i(),a(),t.jobsTrigger,(iu()==!1||ru()==!0)&&p()});function m(x,y){s(I=>I.uid==x,"status",y)}function b(x){s(y=>y.uid==x,"checked",y=>!y)}function p(){D.post(ns()+"/submit/jobs",{pageno:i(),pagesize:a()},{withCredentials:rs}).then(function(x){if(x.status=="error"){su(!1);return}const y=x.data;y&&y.length>0?s(y):o(i()-1)}).catch(function(x){console.error(x)})}function h(x,y){const I=x.map(_=>_.uid);D.post(ns()+"/submit/delete_jobs",{uids:I,abort_only:y},{withCredentials:rs}).then(function(_){t.setJobsTrigger(!t.jobsTrigger),u(null)}).catch(function(_){console.error(_),u(null)})}function v(x){const y=r.filter(I=>I.checked);x=="delete"?(u("Deleting jobs..."),h(y,!1)):x=="abort"&&(u("Aborting jobs..."),h(y,!0))}return(()=>{const x=nu.cloneNode(!0),y=x.firstChild;return f(y,g(zc,{get pageno(){return i()},setPageno:o,get pagesize(){return a()},setPagesize:c,get jobsTrigger(){return t.jobsTrigger},get setJobsTrigger(){return t.setJobsTrigger},performJobAction:v}),null),f(y,g(Zc,{jobs:r,changeJobStatus:m,changeJobChecked:b}),null),f(x,g(tu,{get msg(){return l()}}),null),T(()=>x.classList.toggle("hidden",e()!="jobs")),x})()}const au=w('<div id="tab_system" class="tabcontent"><div class="p-4"><button type="button" class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 text-sm font-medium leading-4 text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Download system log</button></div></div>'),{serverUrl:lu,setServerUrl:Cg,withCredentials:kg}=q;function cu(){const{tabName:t,setTabName:e}=Ye;function n(){D({url:lu()+"/submit/systemlog",method:"GET",responseType:"blob"}).then(function(r){let s=document.createElement("a");s.href=window.URL.createObjectURL(new Blob([r.data],{type:"text/plain"})),s.download=r.headers["content-disposition"].split("=")[1],document.body.appendChild(s),s.click(),document.body.removeChild(s)}).catch(function(r){console.error(r)})}return(()=>{const r=au.cloneNode(!0),s=r.firstChild,i=s.firstChild;return i.$$click=n,T(()=>r.classList.toggle("hidden",t()!="system")),r})()}N(["click"]);function uu(){const[t,e]=S(null);return{email:t,setEmail:e}}const mi=X(uu),du=w('<button type="button" class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 text-sm font-medium leading-4 text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Logout</button>'),fu=w('<div id="tab_account" class="tabcontent p-4"><p></p></div>'),{tabName:hu,setTabName:$g}=Ye,{logged:gu,setLogged:mu}=Qe,{serverUrl:pu,setServerUrl:Ag,withCredentials:bu}=q,{email:vu,setEmail:Ng}=mi;function yu(){function t(){D.get(pu()+"/server/logout",{withCredentials:bu}).then(function(e){e.status==200&&mu(!1)}).catch(function(e){console.error(e)})}return(()=>{const e=fu.cloneNode(!0),n=e.firstChild;return f(n,vu),f(e,g(oe,{get when(){return gu()},get children(){const r=du.cloneNode(!0);return r.$$click=t,r}}),null),T(()=>e.classList.toggle("hidden",hu()!="account")),e})()}N(["click"]);const _u=w('<div class="md:pl-36 flex flex-col flex-1"><main class="flex-1"><div class=""><div class="mx-auto"><div></div></div></div></main></div>'),{multiuser:ss,setMultiuser:Og}=sn,{logged:wu,setLogged:Rg}=Qe,{localModules:xu,setLocalModules:Dg,getLocalModule:Pg,addLocalModule:Lg,loadAllModules:Su}=rn;function Eu(){const[t,e]=S(!1);return qe(function(){(ss()==!1||wu()==!0)&&ci(xu())&&Su()}),(()=>{const n=_u.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild;return f(o,g(Pc,{get jobsTrigger(){return t()},setJobsTrigger:e}),null),f(o,g(ou,{get jobsTrigger(){return t()},setJobsTrigger:e}),null),f(o,g(cu,{}),null),f(o,g(oe,{get when(){return ss()==!0},get children(){return g(yu,{})}}),null),n})()}function Iu(){const[t,e]=S(!0);return{systemReady:t,setSystemReady:e}}const Tu=X(Iu),Cu=w('<div id="tab_systemnotready" class="tabcontent"><div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-md bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"><div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4"><div class="sm:flex sm:items-start"><div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"><svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v3.75m-9.303 3.376C1.83 19.126 2.914 21 4.645 21h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 4.88c-.866-1.501-3.032-1.501-3.898 0L2.697 17.626zM12 17.25h.007v.008H12v-.008z"></path></svg></div><div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left"><h3 class="text-lg font-medium leading-6 text-gray-900" id="modal-title">System not ready</h3><div class="mt-2"><p class="text-sm text-gray-500">OakVar server is not running or it is having a problem. Please contact your system administrator.</p></div></div></div></div></div></div></div></div></div>');function ku(){const{systemReady:t,setSystemReady:e}=Tu;return(()=>{const n=Cu.cloneNode(!0);return T(()=>n.classList.toggle("hidden",!!t())),n})()}const $u=w('<div class="h-full"></div>');function Au(t){return(()=>{const e=$u.cloneNode(!0);return f(e,g(fl,{}),null),f(e,g(Eu,{}),null),f(e,g(ku,{}),null),e})()}/**
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
 */const pi=function(t){const e=[];let n=0;for(let r=0;r<t.length;r++){let s=t.charCodeAt(r);s<128?e[n++]=s:s<2048?(e[n++]=s>>6|192,e[n++]=s&63|128):(s&64512)===55296&&r+1<t.length&&(t.charCodeAt(r+1)&64512)===56320?(s=65536+((s&1023)<<10)+(t.charCodeAt(++r)&1023),e[n++]=s>>18|240,e[n++]=s>>12&63|128,e[n++]=s>>6&63|128,e[n++]=s&63|128):(e[n++]=s>>12|224,e[n++]=s>>6&63|128,e[n++]=s&63|128)}return e},Nu=function(t){const e=[];let n=0,r=0;for(;n<t.length;){const s=t[n++];if(s<128)e[r++]=String.fromCharCode(s);else if(s>191&&s<224){const i=t[n++];e[r++]=String.fromCharCode((s&31)<<6|i&63)}else if(s>239&&s<365){const i=t[n++],o=t[n++],a=t[n++],c=((s&7)<<18|(i&63)<<12|(o&63)<<6|a&63)-65536;e[r++]=String.fromCharCode(55296+(c>>10)),e[r++]=String.fromCharCode(56320+(c&1023))}else{const i=t[n++],o=t[n++];e[r++]=String.fromCharCode((s&15)<<12|(i&63)<<6|o&63)}}return e.join("")},bi={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(t,e){if(!Array.isArray(t))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let s=0;s<t.length;s+=3){const i=t[s],o=s+1<t.length,a=o?t[s+1]:0,c=s+2<t.length,l=c?t[s+2]:0,u=i>>2,m=(i&3)<<4|a>>4;let b=(a&15)<<2|l>>6,p=l&63;c||(p=64,o||(b=64)),r.push(n[u],n[m],n[b],n[p])}return r.join("")},encodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(t):this.encodeByteArray(pi(t),e)},decodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(t):Nu(this.decodeStringToByteArray(t,e))},decodeStringToByteArray(t,e){this.init_();const n=e?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let s=0;s<t.length;){const i=n[t.charAt(s++)],a=s<t.length?n[t.charAt(s)]:0;++s;const l=s<t.length?n[t.charAt(s)]:64;++s;const m=s<t.length?n[t.charAt(s)]:64;if(++s,i==null||a==null||l==null||m==null)throw Error();const b=i<<2|a>>4;if(r.push(b),l!==64){const p=a<<4&240|l>>2;if(r.push(p),m!==64){const h=l<<6&192|m;r.push(h)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let t=0;t<this.ENCODED_VALS.length;t++)this.byteToCharMap_[t]=this.ENCODED_VALS.charAt(t),this.charToByteMap_[this.byteToCharMap_[t]]=t,this.byteToCharMapWebSafe_[t]=this.ENCODED_VALS_WEBSAFE.charAt(t),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[t]]=t,t>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(t)]=t,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(t)]=t)}}},Ou=function(t){const e=pi(t);return bi.encodeByteArray(e,!0)},vi=function(t){return Ou(t).replace(/\./g,"")},yi=function(t){try{return bi.decodeString(t,!0)}catch(e){console.error("base64Decode failed: ",e)}return null};/**
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
 */function W(){return typeof navigator<"u"&&typeof navigator.userAgent=="string"?navigator.userAgent:""}function Ru(){return typeof window<"u"&&!!(window.cordova||window.phonegap||window.PhoneGap)&&/ios|iphone|ipod|ipad|android|blackberry|iemobile/i.test(W())}function Du(){const t=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof t=="object"&&t.id!==void 0}function Pu(){return typeof navigator=="object"&&navigator.product==="ReactNative"}function Lu(){const t=W();return t.indexOf("MSIE ")>=0||t.indexOf("Trident/")>=0}function Mu(){return typeof indexedDB=="object"}function Uu(){return new Promise((t,e)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(r);s.onsuccess=()=>{s.result.close(),n||self.indexedDB.deleteDatabase(r),t(!0)},s.onupgradeneeded=()=>{n=!1},s.onerror=()=>{var i;e(((i=s.error)===null||i===void 0?void 0:i.message)||"")}}catch(n){e(n)}})}function Fu(){if(typeof self<"u")return self;if(typeof window<"u")return window;if(typeof global<"u")return global;throw new Error("Unable to locate global object.")}/**
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
 */const ju=()=>Fu().__FIREBASE_DEFAULTS__,Bu=()=>{if(typeof process>"u"||typeof process.env>"u")return;const t=process.env.__FIREBASE_DEFAULTS__;if(t)return JSON.parse(t)},Hu=()=>{if(typeof document>"u")return;let t;try{t=document.cookie.match(/__FIREBASE_DEFAULTS__=([^;]+)/)}catch{return}const e=t&&yi(t[1]);return e&&JSON.parse(e)},ar=()=>{try{return ju()||Bu()||Hu()}catch(t){console.info(`Unable to get __FIREBASE_DEFAULTS__ due to: ${t}`);return}},zu=t=>{var e,n;return(n=(e=ar())===null||e===void 0?void 0:e.emulatorHosts)===null||n===void 0?void 0:n[t]},Vu=()=>{var t;return(t=ar())===null||t===void 0?void 0:t.config},_i=t=>{var e;return(e=ar())===null||e===void 0?void 0:e[`_${t}`]};/**
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
 */class Wu{constructor(){this.reject=()=>{},this.resolve=()=>{},this.promise=new Promise((e,n)=>{this.resolve=e,this.reject=n})}wrapCallback(e){return(n,r)=>{n?this.reject(n):this.resolve(r),typeof e=="function"&&(this.promise.catch(()=>{}),e.length===1?e(n):e(n,r))}}}/**
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
 */const Ju="FirebaseError";class Ie extends Error{constructor(e,n,r){super(n),this.code=e,this.customData=r,this.name=Ju,Object.setPrototypeOf(this,Ie.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,_t.prototype.create)}}class _t{constructor(e,n,r){this.service=e,this.serviceName=n,this.errors=r}create(e,...n){const r=n[0]||{},s=`${this.service}/${e}`,i=this.errors[e],o=i?qu(i,r):"Error",a=`${this.serviceName}: ${o} (${s}).`;return new Ie(s,a,r)}}function qu(t,e){return t.replace(Gu,(n,r)=>{const s=e[r];return s!=null?String(s):`<${r}?>`})}const Gu=/\{\$([^}]+)}/g;function Ku(t){for(const e in t)if(Object.prototype.hasOwnProperty.call(t,e))return!1;return!0}function Jt(t,e){if(t===e)return!0;const n=Object.keys(t),r=Object.keys(e);for(const s of n){if(!r.includes(s))return!1;const i=t[s],o=e[s];if(is(i)&&is(o)){if(!Jt(i,o))return!1}else if(i!==o)return!1}for(const s of r)if(!n.includes(s))return!1;return!0}function is(t){return t!==null&&typeof t=="object"}/**
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
 */function wt(t){const e=[];for(const[n,r]of Object.entries(t))Array.isArray(r)?r.forEach(s=>{e.push(encodeURIComponent(n)+"="+encodeURIComponent(s))}):e.push(encodeURIComponent(n)+"="+encodeURIComponent(r));return e.length?"&"+e.join("&"):""}function at(t){const e={};return t.replace(/^\?/,"").split("&").forEach(r=>{if(r){const[s,i]=r.split("=");e[decodeURIComponent(s)]=decodeURIComponent(i)}}),e}function lt(t){const e=t.indexOf("?");if(!e)return"";const n=t.indexOf("#",e);return t.substring(e,n>0?n:void 0)}function Xu(t,e){const n=new Yu(t,e);return n.subscribe.bind(n)}class Yu{constructor(e,n){this.observers=[],this.unsubscribes=[],this.observerCount=0,this.task=Promise.resolve(),this.finalized=!1,this.onNoObservers=n,this.task.then(()=>{e(this)}).catch(r=>{this.error(r)})}next(e){this.forEachObserver(n=>{n.next(e)})}error(e){this.forEachObserver(n=>{n.error(e)}),this.close(e)}complete(){this.forEachObserver(e=>{e.complete()}),this.close()}subscribe(e,n,r){let s;if(e===void 0&&n===void 0&&r===void 0)throw new Error("Missing Observer.");Qu(e,["next","error","complete"])?s=e:s={next:e,error:n,complete:r},s.next===void 0&&(s.next=Tn),s.error===void 0&&(s.error=Tn),s.complete===void 0&&(s.complete=Tn);const i=this.unsubscribeOne.bind(this,this.observers.length);return this.finalized&&this.task.then(()=>{try{this.finalError?s.error(this.finalError):s.complete()}catch{}}),this.observers.push(s),i}unsubscribeOne(e){this.observers===void 0||this.observers[e]===void 0||(delete this.observers[e],this.observerCount-=1,this.observerCount===0&&this.onNoObservers!==void 0&&this.onNoObservers(this))}forEachObserver(e){if(!this.finalized)for(let n=0;n<this.observers.length;n++)this.sendOne(n,e)}sendOne(e,n){this.task.then(()=>{if(this.observers!==void 0&&this.observers[e]!==void 0)try{n(this.observers[e])}catch(r){typeof console<"u"&&console.error&&console.error(r)}})}close(e){this.finalized||(this.finalized=!0,e!==void 0&&(this.finalError=e),this.task.then(()=>{this.observers=void 0,this.onNoObservers=void 0}))}}function Qu(t,e){if(typeof t!="object"||t===null)return!1;for(const n of e)if(n in t&&typeof t[n]=="function")return!0;return!1}function Tn(){}/**
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
 */function De(t){return t&&t._delegate?t._delegate:t}class We{constructor(e,n,r){this.name=e,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}/**
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
 */const Te="[DEFAULT]";/**
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
 */class Zu{constructor(e,n){this.name=e,this.container=n,this.component=null,this.instances=new Map,this.instancesDeferred=new Map,this.instancesOptions=new Map,this.onInitCallbacks=new Map}get(e){const n=this.normalizeInstanceIdentifier(e);if(!this.instancesDeferred.has(n)){const r=new Wu;if(this.instancesDeferred.set(n,r),this.isInitialized(n)||this.shouldAutoInitialize())try{const s=this.getOrInitializeService({instanceIdentifier:n});s&&r.resolve(s)}catch{}}return this.instancesDeferred.get(n).promise}getImmediate(e){var n;const r=this.normalizeInstanceIdentifier(e?.identifier),s=(n=e?.optional)!==null&&n!==void 0?n:!1;if(this.isInitialized(r)||this.shouldAutoInitialize())try{return this.getOrInitializeService({instanceIdentifier:r})}catch(i){if(s)return null;throw i}else{if(s)return null;throw Error(`Service ${this.name} is not available`)}}getComponent(){return this.component}setComponent(e){if(e.name!==this.name)throw Error(`Mismatching Component ${e.name} for Provider ${this.name}.`);if(this.component)throw Error(`Component for ${this.name} has already been provided`);if(this.component=e,!!this.shouldAutoInitialize()){if(td(e))try{this.getOrInitializeService({instanceIdentifier:Te})}catch{}for(const[n,r]of this.instancesDeferred.entries()){const s=this.normalizeInstanceIdentifier(n);try{const i=this.getOrInitializeService({instanceIdentifier:s});r.resolve(i)}catch{}}}}clearInstance(e=Te){this.instancesDeferred.delete(e),this.instancesOptions.delete(e),this.instances.delete(e)}async delete(){const e=Array.from(this.instances.values());await Promise.all([...e.filter(n=>"INTERNAL"in n).map(n=>n.INTERNAL.delete()),...e.filter(n=>"_delete"in n).map(n=>n._delete())])}isComponentSet(){return this.component!=null}isInitialized(e=Te){return this.instances.has(e)}getOptions(e=Te){return this.instancesOptions.get(e)||{}}initialize(e={}){const{options:n={}}=e,r=this.normalizeInstanceIdentifier(e.instanceIdentifier);if(this.isInitialized(r))throw Error(`${this.name}(${r}) has already been initialized`);if(!this.isComponentSet())throw Error(`Component ${this.name} has not been registered yet`);const s=this.getOrInitializeService({instanceIdentifier:r,options:n});for(const[i,o]of this.instancesDeferred.entries()){const a=this.normalizeInstanceIdentifier(i);r===a&&o.resolve(s)}return s}onInit(e,n){var r;const s=this.normalizeInstanceIdentifier(n),i=(r=this.onInitCallbacks.get(s))!==null&&r!==void 0?r:new Set;i.add(e),this.onInitCallbacks.set(s,i);const o=this.instances.get(s);return o&&e(o,s),()=>{i.delete(e)}}invokeOnInitCallbacks(e,n){const r=this.onInitCallbacks.get(n);if(!!r)for(const s of r)try{s(e,n)}catch{}}getOrInitializeService({instanceIdentifier:e,options:n={}}){let r=this.instances.get(e);if(!r&&this.component&&(r=this.component.instanceFactory(this.container,{instanceIdentifier:ed(e),options:n}),this.instances.set(e,r),this.instancesOptions.set(e,n),this.invokeOnInitCallbacks(r,e),this.component.onInstanceCreated))try{this.component.onInstanceCreated(this.container,e,r)}catch{}return r||null}normalizeInstanceIdentifier(e=Te){return this.component?this.component.multipleInstances?e:Te:e}shouldAutoInitialize(){return!!this.component&&this.component.instantiationMode!=="EXPLICIT"}}function ed(t){return t===Te?void 0:t}function td(t){return t.instantiationMode==="EAGER"}/**
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
 */class nd{constructor(e){this.name=e,this.providers=new Map}addComponent(e){const n=this.getProvider(e.name);if(n.isComponentSet())throw new Error(`Component ${e.name} has already been registered with ${this.name}`);n.setComponent(e)}addOrOverwriteComponent(e){this.getProvider(e.name).isComponentSet()&&this.providers.delete(e.name),this.addComponent(e)}getProvider(e){if(this.providers.has(e))return this.providers.get(e);const n=new Zu(e,this);return this.providers.set(e,n),n}getProviders(){return Array.from(this.providers.values())}}/**
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
 */var R;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(R||(R={}));const rd={debug:R.DEBUG,verbose:R.VERBOSE,info:R.INFO,warn:R.WARN,error:R.ERROR,silent:R.SILENT},sd=R.INFO,id={[R.DEBUG]:"log",[R.VERBOSE]:"log",[R.INFO]:"info",[R.WARN]:"warn",[R.ERROR]:"error"},od=(t,e,...n)=>{if(e<t.logLevel)return;const r=new Date().toISOString(),s=id[e];if(s)console[s](`[${r}]  ${t.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class wi{constructor(e){this.name=e,this._logLevel=sd,this._logHandler=od,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in R))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?rd[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,R.DEBUG,...e),this._logHandler(this,R.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,R.VERBOSE,...e),this._logHandler(this,R.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,R.INFO,...e),this._logHandler(this,R.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,R.WARN,...e),this._logHandler(this,R.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,R.ERROR,...e),this._logHandler(this,R.ERROR,...e)}}const ad=(t,e)=>e.some(n=>t instanceof n);let os,as;function ld(){return os||(os=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function cd(){return as||(as=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const xi=new WeakMap,zn=new WeakMap,Si=new WeakMap,Cn=new WeakMap,lr=new WeakMap;function ud(t){const e=new Promise((n,r)=>{const s=()=>{t.removeEventListener("success",i),t.removeEventListener("error",o)},i=()=>{n(_e(t.result)),s()},o=()=>{r(t.error),s()};t.addEventListener("success",i),t.addEventListener("error",o)});return e.then(n=>{n instanceof IDBCursor&&xi.set(n,t)}).catch(()=>{}),lr.set(e,t),e}function dd(t){if(zn.has(t))return;const e=new Promise((n,r)=>{const s=()=>{t.removeEventListener("complete",i),t.removeEventListener("error",o),t.removeEventListener("abort",o)},i=()=>{n(),s()},o=()=>{r(t.error||new DOMException("AbortError","AbortError")),s()};t.addEventListener("complete",i),t.addEventListener("error",o),t.addEventListener("abort",o)});zn.set(t,e)}let Vn={get(t,e,n){if(t instanceof IDBTransaction){if(e==="done")return zn.get(t);if(e==="objectStoreNames")return t.objectStoreNames||Si.get(t);if(e==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return _e(t[e])},set(t,e,n){return t[e]=n,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function fd(t){Vn=t(Vn)}function hd(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...n){const r=t.call(kn(this),e,...n);return Si.set(r,e.sort?e.sort():[e]),_e(r)}:cd().includes(t)?function(...e){return t.apply(kn(this),e),_e(xi.get(this))}:function(...e){return _e(t.apply(kn(this),e))}}function gd(t){return typeof t=="function"?hd(t):(t instanceof IDBTransaction&&dd(t),ad(t,ld())?new Proxy(t,Vn):t)}function _e(t){if(t instanceof IDBRequest)return ud(t);if(Cn.has(t))return Cn.get(t);const e=gd(t);return e!==t&&(Cn.set(t,e),lr.set(e,t)),e}const kn=t=>lr.get(t);function md(t,e,{blocked:n,upgrade:r,blocking:s,terminated:i}={}){const o=indexedDB.open(t,e),a=_e(o);return r&&o.addEventListener("upgradeneeded",c=>{r(_e(o.result),c.oldVersion,c.newVersion,_e(o.transaction))}),n&&o.addEventListener("blocked",()=>n()),a.then(c=>{i&&c.addEventListener("close",()=>i()),s&&c.addEventListener("versionchange",()=>s())}).catch(()=>{}),a}const pd=["get","getKey","getAll","getAllKeys","count"],bd=["put","add","delete","clear"],$n=new Map;function ls(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if($n.get(e))return $n.get(e);const n=e.replace(/FromIndex$/,""),r=e!==n,s=bd.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(s||pd.includes(n)))return;const i=async function(o,...a){const c=this.transaction(o,s?"readwrite":"readonly");let l=c.store;return r&&(l=l.index(a.shift())),(await Promise.all([l[n](...a),s&&c.done]))[0]};return $n.set(e,i),i}fd(t=>({...t,get:(e,n,r)=>ls(e,n)||t.get(e,n,r),has:(e,n)=>!!ls(e,n)||t.has(e,n)}));/**
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
 */class vd{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(yd(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function yd(t){const e=t.getComponent();return e?.type==="VERSION"}const Wn="@firebase/app",cs="0.8.3";/**
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
 */const Oe=new wi("@firebase/app"),_d="@firebase/app-compat",wd="@firebase/analytics-compat",xd="@firebase/analytics",Sd="@firebase/app-check-compat",Ed="@firebase/app-check",Id="@firebase/auth",Td="@firebase/auth-compat",Cd="@firebase/database",kd="@firebase/database-compat",$d="@firebase/functions",Ad="@firebase/functions-compat",Nd="@firebase/installations",Od="@firebase/installations-compat",Rd="@firebase/messaging",Dd="@firebase/messaging-compat",Pd="@firebase/performance",Ld="@firebase/performance-compat",Md="@firebase/remote-config",Ud="@firebase/remote-config-compat",Fd="@firebase/storage",jd="@firebase/storage-compat",Bd="@firebase/firestore",Hd="@firebase/firestore-compat",zd="firebase",Vd="9.13.0";/**
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
 */const Jn="[DEFAULT]",Wd={[Wn]:"fire-core",[_d]:"fire-core-compat",[xd]:"fire-analytics",[wd]:"fire-analytics-compat",[Ed]:"fire-app-check",[Sd]:"fire-app-check-compat",[Id]:"fire-auth",[Td]:"fire-auth-compat",[Cd]:"fire-rtdb",[kd]:"fire-rtdb-compat",[$d]:"fire-fn",[Ad]:"fire-fn-compat",[Nd]:"fire-iid",[Od]:"fire-iid-compat",[Rd]:"fire-fcm",[Dd]:"fire-fcm-compat",[Pd]:"fire-perf",[Ld]:"fire-perf-compat",[Md]:"fire-rc",[Ud]:"fire-rc-compat",[Fd]:"fire-gcs",[jd]:"fire-gcs-compat",[Bd]:"fire-fst",[Hd]:"fire-fst-compat","fire-js":"fire-js",[zd]:"fire-js-all"};/**
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
 */const qt=new Map,qn=new Map;function Jd(t,e){try{t.container.addComponent(e)}catch(n){Oe.debug(`Component ${e.name} failed to register with FirebaseApp ${t.name}`,n)}}function ht(t){const e=t.name;if(qn.has(e))return Oe.debug(`There were multiple attempts to register component ${e}.`),!1;qn.set(e,t);for(const n of qt.values())Jd(n,t);return!0}function Ei(t,e){const n=t.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),t.container.getProvider(e)}/**
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
 */const qd={["no-app"]:"No Firebase App '{$appName}' has been created - call Firebase App.initializeApp()",["bad-app-name"]:"Illegal App name: '{$appName}",["duplicate-app"]:"Firebase App named '{$appName}' already exists with different options or config",["app-deleted"]:"Firebase App named '{$appName}' already deleted",["no-options"]:"Need to provide options, when not being deployed to hosting via source.",["invalid-app-argument"]:"firebase.{$appName}() takes either no argument or a Firebase App instance.",["invalid-log-argument"]:"First argument to `onLog` must be null or a function.",["idb-open"]:"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.",["idb-get"]:"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.",["idb-set"]:"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.",["idb-delete"]:"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}."},we=new _t("app","Firebase",qd);/**
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
 */class Gd{constructor(e,n,r){this._isDeleted=!1,this._options=Object.assign({},e),this._config=Object.assign({},n),this._name=n.name,this._automaticDataCollectionEnabled=n.automaticDataCollectionEnabled,this._container=r,this.container.addComponent(new We("app",()=>this,"PUBLIC"))}get automaticDataCollectionEnabled(){return this.checkDestroyed(),this._automaticDataCollectionEnabled}set automaticDataCollectionEnabled(e){this.checkDestroyed(),this._automaticDataCollectionEnabled=e}get name(){return this.checkDestroyed(),this._name}get options(){return this.checkDestroyed(),this._options}get config(){return this.checkDestroyed(),this._config}get container(){return this._container}get isDeleted(){return this._isDeleted}set isDeleted(e){this._isDeleted=e}checkDestroyed(){if(this.isDeleted)throw we.create("app-deleted",{appName:this._name})}}/**
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
 */const on=Vd;function Ii(t,e={}){let n=t;typeof e!="object"&&(e={name:e});const r=Object.assign({name:Jn,automaticDataCollectionEnabled:!1},e),s=r.name;if(typeof s!="string"||!s)throw we.create("bad-app-name",{appName:String(s)});if(n||(n=Vu()),!n)throw we.create("no-options");const i=qt.get(s);if(i){if(Jt(n,i.options)&&Jt(r,i.config))return i;throw we.create("duplicate-app",{appName:s})}const o=new nd(s);for(const c of qn.values())o.addComponent(c);const a=new Gd(n,r,o);return qt.set(s,a),a}function Kd(t=Jn){const e=qt.get(t);if(!e&&t===Jn)return Ii();if(!e)throw we.create("no-app",{appName:t});return e}function Be(t,e,n){var r;let s=(r=Wd[t])!==null&&r!==void 0?r:t;n&&(s+=`-${n}`);const i=s.match(/\s|\//),o=e.match(/\s|\//);if(i||o){const a=[`Unable to register library "${s}" with version "${e}":`];i&&a.push(`library name "${s}" contains illegal characters (whitespace or "/")`),i&&o&&a.push("and"),o&&a.push(`version name "${e}" contains illegal characters (whitespace or "/")`),Oe.warn(a.join(" "));return}ht(new We(`${s}-version`,()=>({library:s,version:e}),"VERSION"))}/**
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
 */const Xd="firebase-heartbeat-database",Yd=1,gt="firebase-heartbeat-store";let An=null;function Ti(){return An||(An=md(Xd,Yd,{upgrade:(t,e)=>{switch(e){case 0:t.createObjectStore(gt)}}}).catch(t=>{throw we.create("idb-open",{originalErrorMessage:t.message})})),An}async function Qd(t){var e;try{return(await Ti()).transaction(gt).objectStore(gt).get(Ci(t))}catch(n){if(n instanceof Ie)Oe.warn(n.message);else{const r=we.create("idb-get",{originalErrorMessage:(e=n)===null||e===void 0?void 0:e.message});Oe.warn(r.message)}}}async function us(t,e){var n;try{const s=(await Ti()).transaction(gt,"readwrite");return await s.objectStore(gt).put(e,Ci(t)),s.done}catch(r){if(r instanceof Ie)Oe.warn(r.message);else{const s=we.create("idb-set",{originalErrorMessage:(n=r)===null||n===void 0?void 0:n.message});Oe.warn(s.message)}}}function Ci(t){return`${t.name}!${t.options.appId}`}/**
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
 */const Zd=1024,ef=30*24*60*60*1e3;class tf{constructor(e){this.container=e,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new rf(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){const n=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),r=ds();if(this._heartbeatsCache===null&&(this._heartbeatsCache=await this._heartbeatsCachePromise),!(this._heartbeatsCache.lastSentHeartbeatDate===r||this._heartbeatsCache.heartbeats.some(s=>s.date===r)))return this._heartbeatsCache.heartbeats.push({date:r,agent:n}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(s=>{const i=new Date(s.date).valueOf();return Date.now()-i<=ef}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,this._heartbeatsCache===null||this._heartbeatsCache.heartbeats.length===0)return"";const e=ds(),{heartbeatsToSend:n,unsentEntries:r}=nf(this._heartbeatsCache.heartbeats),s=vi(JSON.stringify({version:2,heartbeats:n}));return this._heartbeatsCache.lastSentHeartbeatDate=e,r.length>0?(this._heartbeatsCache.heartbeats=r,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}}function ds(){return new Date().toISOString().substring(0,10)}function nf(t,e=Zd){const n=[];let r=t.slice();for(const s of t){const i=n.find(o=>o.agent===s.agent);if(i){if(i.dates.push(s.date),fs(n)>e){i.dates.pop();break}}else if(n.push({agent:s.agent,dates:[s.date]}),fs(n)>e){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class rf{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return Mu()?Uu().then(()=>!0).catch(()=>!1):!1}async read(){return await this._canUseIndexedDBPromise?await Qd(this.app)||{heartbeats:[]}:{heartbeats:[]}}async overwrite(e){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return us(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return us(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:[...s.heartbeats,...e.heartbeats]})}else return}}function fs(t){return vi(JSON.stringify({version:2,heartbeats:t})).length}/**
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
 */function sf(t){ht(new We("platform-logger",e=>new vd(e),"PRIVATE")),ht(new We("heartbeat",e=>new tf(e),"PRIVATE")),Be(Wn,cs,t),Be(Wn,cs,"esm2017"),Be("fire-js","")}sf("");function cr(t,e){var n={};for(var r in t)Object.prototype.hasOwnProperty.call(t,r)&&e.indexOf(r)<0&&(n[r]=t[r]);if(t!=null&&typeof Object.getOwnPropertySymbols=="function")for(var s=0,r=Object.getOwnPropertySymbols(t);s<r.length;s++)e.indexOf(r[s])<0&&Object.prototype.propertyIsEnumerable.call(t,r[s])&&(n[r[s]]=t[r[s]]);return n}function ki(){return{["dependent-sdk-initialized-before-auth"]:"Another Firebase SDK was initialized and is trying to use Auth before Auth is initialized. Please be sure to call `initializeAuth` or `getAuth` before starting any other Firebase SDK."}}const of=ki,$i=new _t("auth","Firebase",ki());/**
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
 */const hs=new wi("@firebase/auth");function Dt(t,...e){hs.logLevel<=R.ERROR&&hs.error(`Auth (${on}): ${t}`,...e)}/**
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
 */function Q(t,...e){throw ur(t,...e)}function te(t,...e){return ur(t,...e)}function Ai(t,e,n){const r=Object.assign(Object.assign({},of()),{[e]:n});return new _t("auth","Firebase",r).create(e,{appName:t.name})}function af(t,e,n){const r=n;if(!(e instanceof r))throw r.name!==e.constructor.name&&Q(t,"argument-error"),Ai(t,"argument-error",`Type of ${e.constructor.name} does not match expected instance.Did you pass a reference from a different Auth SDK?`)}function ur(t,...e){if(typeof t!="string"){const n=e[0],r=[...e.slice(1)];return r[0]&&(r[0].appName=t.name),t._errorFactory.create(n,...r)}return $i.create(t,...e)}function E(t,e,...n){if(!t)throw ur(e,...n)}function ae(t){const e="INTERNAL ASSERTION FAILED: "+t;throw Dt(e),new Error(e)}function fe(t,e){t||ae(e)}/**
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
 */const gs=new Map;function le(t){fe(t instanceof Function,"Expected a class definition");let e=gs.get(t);return e?(fe(e instanceof t,"Instance stored in cache mismatched with class"),e):(e=new t,gs.set(t,e),e)}/**
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
 */function lf(t,e){const n=Ei(t,"auth");if(n.isInitialized()){const s=n.getImmediate(),i=n.getOptions();if(Jt(i,e??{}))return s;Q(s,"already-initialized")}return n.initialize({options:e})}function cf(t,e){const n=e?.persistence||[],r=(Array.isArray(n)?n:[n]).map(le);e?.errorMap&&t._updateErrorMap(e.errorMap),t._initializeWithPersistence(r,e?.popupRedirectResolver)}/**
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
 */function Gn(){var t;return typeof self<"u"&&((t=self.location)===null||t===void 0?void 0:t.href)||""}function uf(){return ms()==="http:"||ms()==="https:"}function ms(){var t;return typeof self<"u"&&((t=self.location)===null||t===void 0?void 0:t.protocol)||null}/**
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
 */function df(){return typeof navigator<"u"&&navigator&&"onLine"in navigator&&typeof navigator.onLine=="boolean"&&(uf()||Du()||"connection"in navigator)?navigator.onLine:!0}function ff(){if(typeof navigator>"u")return null;const t=navigator;return t.languages&&t.languages[0]||t.language||null}/**
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
 */class xt{constructor(e,n){this.shortDelay=e,this.longDelay=n,fe(n>e,"Short delay should be less than long delay!"),this.isMobile=Ru()||Pu()}get(){return df()?this.isMobile?this.longDelay:this.shortDelay:Math.min(5e3,this.shortDelay)}}/**
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
 */function dr(t,e){fe(t.emulator,"Emulator should always be set here");const{url:n}=t.emulator;return e?`${n}${e.startsWith("/")?e.slice(1):e}`:n}/**
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
 */class Ni{static initialize(e,n,r){this.fetchImpl=e,n&&(this.headersImpl=n),r&&(this.responseImpl=r)}static fetch(){if(this.fetchImpl)return this.fetchImpl;if(typeof self<"u"&&"fetch"in self)return self.fetch;ae("Could not find fetch implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static headers(){if(this.headersImpl)return this.headersImpl;if(typeof self<"u"&&"Headers"in self)return self.Headers;ae("Could not find Headers implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static response(){if(this.responseImpl)return this.responseImpl;if(typeof self<"u"&&"Response"in self)return self.Response;ae("Could not find Response implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}}/**
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
 */const hf={CREDENTIAL_MISMATCH:"custom-token-mismatch",MISSING_CUSTOM_TOKEN:"internal-error",INVALID_IDENTIFIER:"invalid-email",MISSING_CONTINUE_URI:"internal-error",INVALID_PASSWORD:"wrong-password",MISSING_PASSWORD:"internal-error",EMAIL_EXISTS:"email-already-in-use",PASSWORD_LOGIN_DISABLED:"operation-not-allowed",INVALID_IDP_RESPONSE:"invalid-credential",INVALID_PENDING_TOKEN:"invalid-credential",FEDERATED_USER_ID_ALREADY_LINKED:"credential-already-in-use",MISSING_REQ_TYPE:"internal-error",EMAIL_NOT_FOUND:"user-not-found",RESET_PASSWORD_EXCEED_LIMIT:"too-many-requests",EXPIRED_OOB_CODE:"expired-action-code",INVALID_OOB_CODE:"invalid-action-code",MISSING_OOB_CODE:"internal-error",CREDENTIAL_TOO_OLD_LOGIN_AGAIN:"requires-recent-login",INVALID_ID_TOKEN:"invalid-user-token",TOKEN_EXPIRED:"user-token-expired",USER_NOT_FOUND:"user-token-expired",TOO_MANY_ATTEMPTS_TRY_LATER:"too-many-requests",INVALID_CODE:"invalid-verification-code",INVALID_SESSION_INFO:"invalid-verification-id",INVALID_TEMPORARY_PROOF:"invalid-credential",MISSING_SESSION_INFO:"missing-verification-id",SESSION_EXPIRED:"code-expired",MISSING_ANDROID_PACKAGE_NAME:"missing-android-pkg-name",UNAUTHORIZED_DOMAIN:"unauthorized-continue-uri",INVALID_OAUTH_CLIENT_ID:"invalid-oauth-client-id",ADMIN_ONLY_OPERATION:"admin-restricted-operation",INVALID_MFA_PENDING_CREDENTIAL:"invalid-multi-factor-session",MFA_ENROLLMENT_NOT_FOUND:"multi-factor-info-not-found",MISSING_MFA_ENROLLMENT_ID:"missing-multi-factor-info",MISSING_MFA_PENDING_CREDENTIAL:"missing-multi-factor-session",SECOND_FACTOR_EXISTS:"second-factor-already-in-use",SECOND_FACTOR_LIMIT_EXCEEDED:"maximum-second-factor-count-exceeded",BLOCKING_FUNCTION_ERROR_RESPONSE:"internal-error"};/**
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
 */const gf=new xt(3e4,6e4);function an(t,e){return t.tenantId&&!e.tenantId?Object.assign(Object.assign({},e),{tenantId:t.tenantId}):e}async function St(t,e,n,r,s={}){return Oi(t,s,async()=>{let i={},o={};r&&(e==="GET"?o=r:i={body:JSON.stringify(r)});const a=wt(Object.assign({key:t.config.apiKey},o)).slice(1),c=await t._getAdditionalHeaders();return c["Content-Type"]="application/json",t.languageCode&&(c["X-Firebase-Locale"]=t.languageCode),Ni.fetch()(Ri(t,t.config.apiHost,n,a),Object.assign({method:e,headers:c,referrerPolicy:"no-referrer"},i))})}async function Oi(t,e,n){t._canInitEmulator=!1;const r=Object.assign(Object.assign({},hf),e);try{const s=new mf(t),i=await Promise.race([n(),s.promise]);s.clearNetworkTimeout();const o=await i.json();if("needConfirmation"in o)throw Nt(t,"account-exists-with-different-credential",o);if(i.ok&&!("errorMessage"in o))return o;{const a=i.ok?o.errorMessage:o.error.message,[c,l]=a.split(" : ");if(c==="FEDERATED_USER_ID_ALREADY_LINKED")throw Nt(t,"credential-already-in-use",o);if(c==="EMAIL_EXISTS")throw Nt(t,"email-already-in-use",o);if(c==="USER_DISABLED")throw Nt(t,"user-disabled",o);const u=r[c]||c.toLowerCase().replace(/[_\s]+/g,"-");if(l)throw Ai(t,u,l);Q(t,u)}}catch(s){if(s instanceof Ie)throw s;Q(t,"network-request-failed")}}async function ln(t,e,n,r,s={}){const i=await St(t,e,n,r,s);return"mfaPendingCredential"in i&&Q(t,"multi-factor-auth-required",{_serverResponse:i}),i}function Ri(t,e,n,r){const s=`${e}${n}?${r}`;return t.config.emulator?dr(t.config,s):`${t.config.apiScheme}://${s}`}class mf{constructor(e){this.auth=e,this.timer=null,this.promise=new Promise((n,r)=>{this.timer=setTimeout(()=>r(te(this.auth,"network-request-failed")),gf.get())})}clearNetworkTimeout(){clearTimeout(this.timer)}}function Nt(t,e,n){const r={appName:t.name};n.email&&(r.email=n.email),n.phoneNumber&&(r.phoneNumber=n.phoneNumber);const s=te(t,e,r);return s.customData._tokenResponse=n,s}/**
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
 */async function pf(t,e){return St(t,"POST","/v1/accounts:delete",e)}async function bf(t,e){return St(t,"POST","/v1/accounts:lookup",e)}/**
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
 */function ct(t){if(!!t)try{const e=new Date(Number(t));if(!isNaN(e.getTime()))return e.toUTCString()}catch{}}async function vf(t,e=!1){const n=De(t),r=await n.getIdToken(e),s=fr(r);E(s&&s.exp&&s.auth_time&&s.iat,n.auth,"internal-error");const i=typeof s.firebase=="object"?s.firebase:void 0,o=i?.sign_in_provider;return{claims:s,token:r,authTime:ct(Nn(s.auth_time)),issuedAtTime:ct(Nn(s.iat)),expirationTime:ct(Nn(s.exp)),signInProvider:o||null,signInSecondFactor:i?.sign_in_second_factor||null}}function Nn(t){return Number(t)*1e3}function fr(t){var e;const[n,r,s]=t.split(".");if(n===void 0||r===void 0||s===void 0)return Dt("JWT malformed, contained fewer than 3 sections"),null;try{const i=yi(r);return i?JSON.parse(i):(Dt("Failed to decode base64 JWT payload"),null)}catch(i){return Dt("Caught error parsing JWT payload as JSON",(e=i)===null||e===void 0?void 0:e.toString()),null}}function yf(t){const e=fr(t);return E(e,"internal-error"),E(typeof e.exp<"u","internal-error"),E(typeof e.iat<"u","internal-error"),Number(e.exp)-Number(e.iat)}/**
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
 */async function mt(t,e,n=!1){if(n)return e;try{return await e}catch(r){throw r instanceof Ie&&_f(r)&&t.auth.currentUser===t&&await t.auth.signOut(),r}}function _f({code:t}){return t==="auth/user-disabled"||t==="auth/user-token-expired"}/**
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
 */class wf{constructor(e){this.user=e,this.isRunning=!1,this.timerId=null,this.errorBackoff=3e4}_start(){this.isRunning||(this.isRunning=!0,this.schedule())}_stop(){!this.isRunning||(this.isRunning=!1,this.timerId!==null&&clearTimeout(this.timerId))}getInterval(e){var n;if(e){const r=this.errorBackoff;return this.errorBackoff=Math.min(this.errorBackoff*2,96e4),r}else{this.errorBackoff=3e4;const s=((n=this.user.stsTokenManager.expirationTime)!==null&&n!==void 0?n:0)-Date.now()-3e5;return Math.max(0,s)}}schedule(e=!1){if(!this.isRunning)return;const n=this.getInterval(e);this.timerId=setTimeout(async()=>{await this.iteration()},n)}async iteration(){var e;try{await this.user.getIdToken(!0)}catch(n){((e=n)===null||e===void 0?void 0:e.code)==="auth/network-request-failed"&&this.schedule(!0);return}this.schedule()}}/**
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
 */class Di{constructor(e,n){this.createdAt=e,this.lastLoginAt=n,this._initializeTime()}_initializeTime(){this.lastSignInTime=ct(this.lastLoginAt),this.creationTime=ct(this.createdAt)}_copy(e){this.createdAt=e.createdAt,this.lastLoginAt=e.lastLoginAt,this._initializeTime()}toJSON(){return{createdAt:this.createdAt,lastLoginAt:this.lastLoginAt}}}/**
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
 */async function Gt(t){var e;const n=t.auth,r=await t.getIdToken(),s=await mt(t,bf(n,{idToken:r}));E(s?.users.length,n,"internal-error");const i=s.users[0];t._notifyReloadListener(i);const o=!((e=i.providerUserInfo)===null||e===void 0)&&e.length?Ef(i.providerUserInfo):[],a=Sf(t.providerData,o),c=t.isAnonymous,l=!(t.email&&i.passwordHash)&&!a?.length,u=c?l:!1,m={uid:i.localId,displayName:i.displayName||null,photoURL:i.photoUrl||null,email:i.email||null,emailVerified:i.emailVerified||!1,phoneNumber:i.phoneNumber||null,tenantId:i.tenantId||null,providerData:a,metadata:new Di(i.createdAt,i.lastLoginAt),isAnonymous:u};Object.assign(t,m)}async function xf(t){const e=De(t);await Gt(e),await e.auth._persistUserIfCurrent(e),e.auth._notifyListenersIfCurrent(e)}function Sf(t,e){return[...t.filter(r=>!e.some(s=>s.providerId===r.providerId)),...e]}function Ef(t){return t.map(e=>{var{providerId:n}=e,r=cr(e,["providerId"]);return{providerId:n,uid:r.rawId||"",displayName:r.displayName||null,email:r.email||null,phoneNumber:r.phoneNumber||null,photoURL:r.photoUrl||null}})}/**
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
 */async function If(t,e){const n=await Oi(t,{},async()=>{const r=wt({grant_type:"refresh_token",refresh_token:e}).slice(1),{tokenApiHost:s,apiKey:i}=t.config,o=Ri(t,s,"/v1/token",`key=${i}`),a=await t._getAdditionalHeaders();return a["Content-Type"]="application/x-www-form-urlencoded",Ni.fetch()(o,{method:"POST",headers:a,body:r})});return{accessToken:n.access_token,expiresIn:n.expires_in,refreshToken:n.refresh_token}}/**
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
 */class pt{constructor(){this.refreshToken=null,this.accessToken=null,this.expirationTime=null}get isExpired(){return!this.expirationTime||Date.now()>this.expirationTime-3e4}updateFromServerResponse(e){E(e.idToken,"internal-error"),E(typeof e.idToken<"u","internal-error"),E(typeof e.refreshToken<"u","internal-error");const n="expiresIn"in e&&typeof e.expiresIn<"u"?Number(e.expiresIn):yf(e.idToken);this.updateTokensAndExpiration(e.idToken,e.refreshToken,n)}async getToken(e,n=!1){return E(!this.accessToken||this.refreshToken,e,"user-token-expired"),!n&&this.accessToken&&!this.isExpired?this.accessToken:this.refreshToken?(await this.refresh(e,this.refreshToken),this.accessToken):null}clearRefreshToken(){this.refreshToken=null}async refresh(e,n){const{accessToken:r,refreshToken:s,expiresIn:i}=await If(e,n);this.updateTokensAndExpiration(r,s,Number(i))}updateTokensAndExpiration(e,n,r){this.refreshToken=n||null,this.accessToken=e||null,this.expirationTime=Date.now()+r*1e3}static fromJSON(e,n){const{refreshToken:r,accessToken:s,expirationTime:i}=n,o=new pt;return r&&(E(typeof r=="string","internal-error",{appName:e}),o.refreshToken=r),s&&(E(typeof s=="string","internal-error",{appName:e}),o.accessToken=s),i&&(E(typeof i=="number","internal-error",{appName:e}),o.expirationTime=i),o}toJSON(){return{refreshToken:this.refreshToken,accessToken:this.accessToken,expirationTime:this.expirationTime}}_assign(e){this.accessToken=e.accessToken,this.refreshToken=e.refreshToken,this.expirationTime=e.expirationTime}_clone(){return Object.assign(new pt,this.toJSON())}_performRefresh(){return ae("not implemented")}}/**
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
 */function be(t,e){E(typeof t=="string"||typeof t>"u","internal-error",{appName:e})}class Ae{constructor(e){var{uid:n,auth:r,stsTokenManager:s}=e,i=cr(e,["uid","auth","stsTokenManager"]);this.providerId="firebase",this.proactiveRefresh=new wf(this),this.reloadUserInfo=null,this.reloadListener=null,this.uid=n,this.auth=r,this.stsTokenManager=s,this.accessToken=s.accessToken,this.displayName=i.displayName||null,this.email=i.email||null,this.emailVerified=i.emailVerified||!1,this.phoneNumber=i.phoneNumber||null,this.photoURL=i.photoURL||null,this.isAnonymous=i.isAnonymous||!1,this.tenantId=i.tenantId||null,this.providerData=i.providerData?[...i.providerData]:[],this.metadata=new Di(i.createdAt||void 0,i.lastLoginAt||void 0)}async getIdToken(e){const n=await mt(this,this.stsTokenManager.getToken(this.auth,e));return E(n,this.auth,"internal-error"),this.accessToken!==n&&(this.accessToken=n,await this.auth._persistUserIfCurrent(this),this.auth._notifyListenersIfCurrent(this)),n}getIdTokenResult(e){return vf(this,e)}reload(){return xf(this)}_assign(e){this!==e&&(E(this.uid===e.uid,this.auth,"internal-error"),this.displayName=e.displayName,this.photoURL=e.photoURL,this.email=e.email,this.emailVerified=e.emailVerified,this.phoneNumber=e.phoneNumber,this.isAnonymous=e.isAnonymous,this.tenantId=e.tenantId,this.providerData=e.providerData.map(n=>Object.assign({},n)),this.metadata._copy(e.metadata),this.stsTokenManager._assign(e.stsTokenManager))}_clone(e){return new Ae(Object.assign(Object.assign({},this),{auth:e,stsTokenManager:this.stsTokenManager._clone()}))}_onReload(e){E(!this.reloadListener,this.auth,"internal-error"),this.reloadListener=e,this.reloadUserInfo&&(this._notifyReloadListener(this.reloadUserInfo),this.reloadUserInfo=null)}_notifyReloadListener(e){this.reloadListener?this.reloadListener(e):this.reloadUserInfo=e}_startProactiveRefresh(){this.proactiveRefresh._start()}_stopProactiveRefresh(){this.proactiveRefresh._stop()}async _updateTokensIfNecessary(e,n=!1){let r=!1;e.idToken&&e.idToken!==this.stsTokenManager.accessToken&&(this.stsTokenManager.updateFromServerResponse(e),r=!0),n&&await Gt(this),await this.auth._persistUserIfCurrent(this),r&&this.auth._notifyListenersIfCurrent(this)}async delete(){const e=await this.getIdToken();return await mt(this,pf(this.auth,{idToken:e})),this.stsTokenManager.clearRefreshToken(),this.auth.signOut()}toJSON(){return Object.assign(Object.assign({uid:this.uid,email:this.email||void 0,emailVerified:this.emailVerified,displayName:this.displayName||void 0,isAnonymous:this.isAnonymous,photoURL:this.photoURL||void 0,phoneNumber:this.phoneNumber||void 0,tenantId:this.tenantId||void 0,providerData:this.providerData.map(e=>Object.assign({},e)),stsTokenManager:this.stsTokenManager.toJSON(),_redirectEventId:this._redirectEventId},this.metadata.toJSON()),{apiKey:this.auth.config.apiKey,appName:this.auth.name})}get refreshToken(){return this.stsTokenManager.refreshToken||""}static _fromJSON(e,n){var r,s,i,o,a,c,l,u;const m=(r=n.displayName)!==null&&r!==void 0?r:void 0,b=(s=n.email)!==null&&s!==void 0?s:void 0,p=(i=n.phoneNumber)!==null&&i!==void 0?i:void 0,h=(o=n.photoURL)!==null&&o!==void 0?o:void 0,v=(a=n.tenantId)!==null&&a!==void 0?a:void 0,x=(c=n._redirectEventId)!==null&&c!==void 0?c:void 0,y=(l=n.createdAt)!==null&&l!==void 0?l:void 0,I=(u=n.lastLoginAt)!==null&&u!==void 0?u:void 0,{uid:_,emailVerified:k,isAnonymous:C,providerData:J,stsTokenManager:K}=n;E(_&&K,e,"internal-error");const ee=pt.fromJSON(this.name,K);E(typeof _=="string",e,"internal-error"),be(m,e.name),be(b,e.name),E(typeof k=="boolean",e,"internal-error"),E(typeof C=="boolean",e,"internal-error"),be(p,e.name),be(h,e.name),be(v,e.name),be(x,e.name),be(y,e.name),be(I,e.name);const A=new Ae({uid:_,auth:e,email:b,emailVerified:k,displayName:m,isAnonymous:C,photoURL:h,phoneNumber:p,tenantId:v,stsTokenManager:ee,createdAt:y,lastLoginAt:I});return J&&Array.isArray(J)&&(A.providerData=J.map(L=>Object.assign({},L))),x&&(A._redirectEventId=x),A}static async _fromIdTokenResponse(e,n,r=!1){const s=new pt;s.updateFromServerResponse(n);const i=new Ae({uid:n.localId,auth:e,stsTokenManager:s,isAnonymous:r});return await Gt(i),i}}/**
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
 */class Pi{constructor(){this.type="NONE",this.storage={}}async _isAvailable(){return!0}async _set(e,n){this.storage[e]=n}async _get(e){const n=this.storage[e];return n===void 0?null:n}async _remove(e){delete this.storage[e]}_addListener(e,n){}_removeListener(e,n){}}Pi.type="NONE";const ps=Pi;/**
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
 */function Pt(t,e,n){return`firebase:${t}:${e}:${n}`}class He{constructor(e,n,r){this.persistence=e,this.auth=n,this.userKey=r;const{config:s,name:i}=this.auth;this.fullUserKey=Pt(this.userKey,s.apiKey,i),this.fullPersistenceKey=Pt("persistence",s.apiKey,i),this.boundEventHandler=n._onStorageEvent.bind(n),this.persistence._addListener(this.fullUserKey,this.boundEventHandler)}setCurrentUser(e){return this.persistence._set(this.fullUserKey,e.toJSON())}async getCurrentUser(){const e=await this.persistence._get(this.fullUserKey);return e?Ae._fromJSON(this.auth,e):null}removeCurrentUser(){return this.persistence._remove(this.fullUserKey)}savePersistenceForRedirect(){return this.persistence._set(this.fullPersistenceKey,this.persistence.type)}async setPersistence(e){if(this.persistence===e)return;const n=await this.getCurrentUser();if(await this.removeCurrentUser(),this.persistence=e,n)return this.setCurrentUser(n)}delete(){this.persistence._removeListener(this.fullUserKey,this.boundEventHandler)}static async create(e,n,r="authUser"){if(!n.length)return new He(le(ps),e,r);const s=(await Promise.all(n.map(async l=>{if(await l._isAvailable())return l}))).filter(l=>l);let i=s[0]||le(ps);const o=Pt(r,e.config.apiKey,e.name);let a=null;for(const l of n)try{const u=await l._get(o);if(u){const m=Ae._fromJSON(e,u);l!==i&&(a=m),i=l;break}}catch{}const c=s.filter(l=>l._shouldAllowMigration);return!i._shouldAllowMigration||!c.length?new He(i,e,r):(i=c[0],a&&await i._set(o,a.toJSON()),await Promise.all(n.map(async l=>{if(l!==i)try{await l._remove(o)}catch{}})),new He(i,e,r))}}/**
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
 */function bs(t){const e=t.toLowerCase();if(e.includes("opera/")||e.includes("opr/")||e.includes("opios/"))return"Opera";if(Ui(e))return"IEMobile";if(e.includes("msie")||e.includes("trident/"))return"IE";if(e.includes("edge/"))return"Edge";if(Li(e))return"Firefox";if(e.includes("silk/"))return"Silk";if(ji(e))return"Blackberry";if(Bi(e))return"Webos";if(hr(e))return"Safari";if((e.includes("chrome/")||Mi(e))&&!e.includes("edge/"))return"Chrome";if(Fi(e))return"Android";{const n=/([a-zA-Z\d\.]+)\/[a-zA-Z\d\.]*$/,r=t.match(n);if(r?.length===2)return r[1]}return"Other"}function Li(t=W()){return/firefox\//i.test(t)}function hr(t=W()){const e=t.toLowerCase();return e.includes("safari/")&&!e.includes("chrome/")&&!e.includes("crios/")&&!e.includes("android")}function Mi(t=W()){return/crios\//i.test(t)}function Ui(t=W()){return/iemobile/i.test(t)}function Fi(t=W()){return/android/i.test(t)}function ji(t=W()){return/blackberry/i.test(t)}function Bi(t=W()){return/webos/i.test(t)}function cn(t=W()){return/iphone|ipad|ipod/i.test(t)||/macintosh/i.test(t)&&/mobile/i.test(t)}function Tf(t=W()){var e;return cn(t)&&!!(!((e=window.navigator)===null||e===void 0)&&e.standalone)}function Cf(){return Lu()&&document.documentMode===10}function Hi(t=W()){return cn(t)||Fi(t)||Bi(t)||ji(t)||/windows phone/i.test(t)||Ui(t)}function kf(){try{return!!(window&&window!==window.top)}catch{return!1}}/**
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
 */function zi(t,e=[]){let n;switch(t){case"Browser":n=bs(W());break;case"Worker":n=`${bs(W())}-${t}`;break;default:n=t}const r=e.length?e.join(","):"FirebaseCore-web";return`${n}/JsCore/${on}/${r}`}/**
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
 */class $f{constructor(e){this.auth=e,this.queue=[]}pushCallback(e,n){const r=i=>new Promise((o,a)=>{try{const c=e(i);o(c)}catch(c){a(c)}});r.onAbort=n,this.queue.push(r);const s=this.queue.length-1;return()=>{this.queue[s]=()=>Promise.resolve()}}async runMiddleware(e){var n;if(this.auth.currentUser===e)return;const r=[];try{for(const s of this.queue)await s(e),s.onAbort&&r.push(s.onAbort)}catch(s){r.reverse();for(const i of r)try{i()}catch{}throw this.auth._errorFactory.create("login-blocked",{originalMessage:(n=s)===null||n===void 0?void 0:n.message})}}}/**
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
 */class Af{constructor(e,n,r){this.app=e,this.heartbeatServiceProvider=n,this.config=r,this.currentUser=null,this.emulatorConfig=null,this.operations=Promise.resolve(),this.authStateSubscription=new vs(this),this.idTokenSubscription=new vs(this),this.beforeStateQueue=new $f(this),this.redirectUser=null,this.isProactiveRefreshEnabled=!1,this._canInitEmulator=!0,this._isInitialized=!1,this._deleted=!1,this._initializationPromise=null,this._popupRedirectResolver=null,this._errorFactory=$i,this.lastNotifiedUid=void 0,this.languageCode=null,this.tenantId=null,this.settings={appVerificationDisabledForTesting:!1},this.frameworks=[],this.name=e.name,this.clientVersion=r.sdkClientVersion}_initializeWithPersistence(e,n){return n&&(this._popupRedirectResolver=le(n)),this._initializationPromise=this.queue(async()=>{var r,s;if(!this._deleted&&(this.persistenceManager=await He.create(this,e),!this._deleted)){if(!((r=this._popupRedirectResolver)===null||r===void 0)&&r._shouldInitProactively)try{await this._popupRedirectResolver._initialize(this)}catch{}await this.initializeCurrentUser(n),this.lastNotifiedUid=((s=this.currentUser)===null||s===void 0?void 0:s.uid)||null,!this._deleted&&(this._isInitialized=!0)}}),this._initializationPromise}async _onStorageEvent(){if(this._deleted)return;const e=await this.assertedPersistence.getCurrentUser();if(!(!this.currentUser&&!e)){if(this.currentUser&&e&&this.currentUser.uid===e.uid){this._currentUser._assign(e),await this.currentUser.getIdToken();return}await this._updateCurrentUser(e,!0)}}async initializeCurrentUser(e){var n;const r=await this.assertedPersistence.getCurrentUser();let s=r,i=!1;if(e&&this.config.authDomain){await this.getOrInitRedirectPersistenceManager();const o=(n=this.redirectUser)===null||n===void 0?void 0:n._redirectEventId,a=s?._redirectEventId,c=await this.tryRedirectSignIn(e);(!o||o===a)&&c?.user&&(s=c.user,i=!0)}if(!s)return this.directlySetCurrentUser(null);if(!s._redirectEventId){if(i)try{await this.beforeStateQueue.runMiddleware(s)}catch(o){s=r,this._popupRedirectResolver._overrideRedirectResult(this,()=>Promise.reject(o))}return s?this.reloadAndSetCurrentUserOrClear(s):this.directlySetCurrentUser(null)}return E(this._popupRedirectResolver,this,"argument-error"),await this.getOrInitRedirectPersistenceManager(),this.redirectUser&&this.redirectUser._redirectEventId===s._redirectEventId?this.directlySetCurrentUser(s):this.reloadAndSetCurrentUserOrClear(s)}async tryRedirectSignIn(e){let n=null;try{n=await this._popupRedirectResolver._completeRedirectFn(this,e,!0)}catch{await this._setRedirectUser(null)}return n}async reloadAndSetCurrentUserOrClear(e){var n;try{await Gt(e)}catch(r){if(((n=r)===null||n===void 0?void 0:n.code)!=="auth/network-request-failed")return this.directlySetCurrentUser(null)}return this.directlySetCurrentUser(e)}useDeviceLanguage(){this.languageCode=ff()}async _delete(){this._deleted=!0}async updateCurrentUser(e){const n=e?De(e):null;return n&&E(n.auth.config.apiKey===this.config.apiKey,this,"invalid-user-token"),this._updateCurrentUser(n&&n._clone(this))}async _updateCurrentUser(e,n=!1){if(!this._deleted)return e&&E(this.tenantId===e.tenantId,this,"tenant-id-mismatch"),n||await this.beforeStateQueue.runMiddleware(e),this.queue(async()=>{await this.directlySetCurrentUser(e),this.notifyAuthListeners()})}async signOut(){return await this.beforeStateQueue.runMiddleware(null),(this.redirectPersistenceManager||this._popupRedirectResolver)&&await this._setRedirectUser(null),this._updateCurrentUser(null,!0)}setPersistence(e){return this.queue(async()=>{await this.assertedPersistence.setPersistence(le(e))})}_getPersistence(){return this.assertedPersistence.persistence.type}_updateErrorMap(e){this._errorFactory=new _t("auth","Firebase",e())}onAuthStateChanged(e,n,r){return this.registerStateListener(this.authStateSubscription,e,n,r)}beforeAuthStateChanged(e,n){return this.beforeStateQueue.pushCallback(e,n)}onIdTokenChanged(e,n,r){return this.registerStateListener(this.idTokenSubscription,e,n,r)}toJSON(){var e;return{apiKey:this.config.apiKey,authDomain:this.config.authDomain,appName:this.name,currentUser:(e=this._currentUser)===null||e===void 0?void 0:e.toJSON()}}async _setRedirectUser(e,n){const r=await this.getOrInitRedirectPersistenceManager(n);return e===null?r.removeCurrentUser():r.setCurrentUser(e)}async getOrInitRedirectPersistenceManager(e){if(!this.redirectPersistenceManager){const n=e&&le(e)||this._popupRedirectResolver;E(n,this,"argument-error"),this.redirectPersistenceManager=await He.create(this,[le(n._redirectPersistence)],"redirectUser"),this.redirectUser=await this.redirectPersistenceManager.getCurrentUser()}return this.redirectPersistenceManager}async _redirectUserForId(e){var n,r;return this._isInitialized&&await this.queue(async()=>{}),((n=this._currentUser)===null||n===void 0?void 0:n._redirectEventId)===e?this._currentUser:((r=this.redirectUser)===null||r===void 0?void 0:r._redirectEventId)===e?this.redirectUser:null}async _persistUserIfCurrent(e){if(e===this.currentUser)return this.queue(async()=>this.directlySetCurrentUser(e))}_notifyListenersIfCurrent(e){e===this.currentUser&&this.notifyAuthListeners()}_key(){return`${this.config.authDomain}:${this.config.apiKey}:${this.name}`}_startProactiveRefresh(){this.isProactiveRefreshEnabled=!0,this.currentUser&&this._currentUser._startProactiveRefresh()}_stopProactiveRefresh(){this.isProactiveRefreshEnabled=!1,this.currentUser&&this._currentUser._stopProactiveRefresh()}get _currentUser(){return this.currentUser}notifyAuthListeners(){var e,n;if(!this._isInitialized)return;this.idTokenSubscription.next(this.currentUser);const r=(n=(e=this.currentUser)===null||e===void 0?void 0:e.uid)!==null&&n!==void 0?n:null;this.lastNotifiedUid!==r&&(this.lastNotifiedUid=r,this.authStateSubscription.next(this.currentUser))}registerStateListener(e,n,r,s){if(this._deleted)return()=>{};const i=typeof n=="function"?n:n.next.bind(n),o=this._isInitialized?Promise.resolve():this._initializationPromise;return E(o,this,"internal-error"),o.then(()=>i(this.currentUser)),typeof n=="function"?e.addObserver(n,r,s):e.addObserver(n)}async directlySetCurrentUser(e){this.currentUser&&this.currentUser!==e&&this._currentUser._stopProactiveRefresh(),e&&this.isProactiveRefreshEnabled&&e._startProactiveRefresh(),this.currentUser=e,e?await this.assertedPersistence.setCurrentUser(e):await this.assertedPersistence.removeCurrentUser()}queue(e){return this.operations=this.operations.then(e,e),this.operations}get assertedPersistence(){return E(this.persistenceManager,this,"internal-error"),this.persistenceManager}_logFramework(e){!e||this.frameworks.includes(e)||(this.frameworks.push(e),this.frameworks.sort(),this.clientVersion=zi(this.config.clientPlatform,this._getFrameworks()))}_getFrameworks(){return this.frameworks}async _getAdditionalHeaders(){var e;const n={["X-Client-Version"]:this.clientVersion};this.app.options.appId&&(n["X-Firebase-gmpid"]=this.app.options.appId);const r=await((e=this.heartbeatServiceProvider.getImmediate({optional:!0}))===null||e===void 0?void 0:e.getHeartbeatsHeader());return r&&(n["X-Firebase-Client"]=r),n}}function Et(t){return De(t)}class vs{constructor(e){this.auth=e,this.observer=null,this.addObserver=Xu(n=>this.observer=n)}get next(){return E(this.observer,this.auth,"internal-error"),this.observer.next.bind(this.observer)}}function Nf(t,e,n){const r=Et(t);E(r._canInitEmulator,r,"emulator-config-failed"),E(/^https?:\/\//.test(e),r,"invalid-emulator-scheme");const s=!!n?.disableWarnings,i=Vi(e),{host:o,port:a}=Of(e),c=a===null?"":`:${a}`;r.config.emulator={url:`${i}//${o}${c}/`},r.settings.appVerificationDisabledForTesting=!0,r.emulatorConfig=Object.freeze({host:o,port:a,protocol:i.replace(":",""),options:Object.freeze({disableWarnings:s})}),s||Rf()}function Vi(t){const e=t.indexOf(":");return e<0?"":t.substr(0,e+1)}function Of(t){const e=Vi(t),n=/(\/\/)?([^?#/]+)/.exec(t.substr(e.length));if(!n)return{host:"",port:null};const r=n[2].split("@").pop()||"",s=/^(\[[^\]]+\])(:|$)/.exec(r);if(s){const i=s[1];return{host:i,port:ys(r.substr(i.length+1))}}else{const[i,o]=r.split(":");return{host:i,port:ys(o)}}}function ys(t){if(!t)return null;const e=Number(t);return isNaN(e)?null:e}function Rf(){function t(){const e=document.createElement("p"),n=e.style;e.innerText="Running in emulator mode. Do not use with production credentials.",n.position="fixed",n.width="100%",n.backgroundColor="#ffffff",n.border=".1em solid #000000",n.color="#b50000",n.bottom="0px",n.left="0px",n.margin="0px",n.zIndex="10000",n.textAlign="center",e.classList.add("firebase-emulator-warning"),document.body.appendChild(e)}typeof console<"u"&&typeof console.info=="function"&&console.info("WARNING: You are using the Auth Emulator, which is intended for local testing only.  Do not use with production credentials."),typeof window<"u"&&typeof document<"u"&&(document.readyState==="loading"?window.addEventListener("DOMContentLoaded",t):t())}/**
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
 */class gr{constructor(e,n){this.providerId=e,this.signInMethod=n}toJSON(){return ae("not implemented")}_getIdTokenResponse(e){return ae("not implemented")}_linkToIdToken(e,n){return ae("not implemented")}_getReauthenticationResolver(e){return ae("not implemented")}}async function Df(t,e){return St(t,"POST","/v1/accounts:update",e)}/**
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
 */async function Pf(t,e){return ln(t,"POST","/v1/accounts:signInWithPassword",an(t,e))}/**
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
 */async function Lf(t,e){return ln(t,"POST","/v1/accounts:signInWithEmailLink",an(t,e))}async function Mf(t,e){return ln(t,"POST","/v1/accounts:signInWithEmailLink",an(t,e))}/**
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
 */class bt extends gr{constructor(e,n,r,s=null){super("password",r),this._email=e,this._password=n,this._tenantId=s}static _fromEmailAndPassword(e,n){return new bt(e,n,"password")}static _fromEmailAndCode(e,n,r=null){return new bt(e,n,"emailLink",r)}toJSON(){return{email:this._email,password:this._password,signInMethod:this.signInMethod,tenantId:this._tenantId}}static fromJSON(e){const n=typeof e=="string"?JSON.parse(e):e;if(n?.email&&n?.password){if(n.signInMethod==="password")return this._fromEmailAndPassword(n.email,n.password);if(n.signInMethod==="emailLink")return this._fromEmailAndCode(n.email,n.password,n.tenantId)}return null}async _getIdTokenResponse(e){switch(this.signInMethod){case"password":return Pf(e,{returnSecureToken:!0,email:this._email,password:this._password});case"emailLink":return Lf(e,{email:this._email,oobCode:this._password});default:Q(e,"internal-error")}}async _linkToIdToken(e,n){switch(this.signInMethod){case"password":return Df(e,{idToken:n,returnSecureToken:!0,email:this._email,password:this._password});case"emailLink":return Mf(e,{idToken:n,email:this._email,oobCode:this._password});default:Q(e,"internal-error")}}_getReauthenticationResolver(e){return this._getIdTokenResponse(e)}}/**
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
 */async function ze(t,e){return ln(t,"POST","/v1/accounts:signInWithIdp",an(t,e))}/**
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
 */const Uf="http://localhost";class Re extends gr{constructor(){super(...arguments),this.pendingToken=null}static _fromParams(e){const n=new Re(e.providerId,e.signInMethod);return e.idToken||e.accessToken?(e.idToken&&(n.idToken=e.idToken),e.accessToken&&(n.accessToken=e.accessToken),e.nonce&&!e.pendingToken&&(n.nonce=e.nonce),e.pendingToken&&(n.pendingToken=e.pendingToken)):e.oauthToken&&e.oauthTokenSecret?(n.accessToken=e.oauthToken,n.secret=e.oauthTokenSecret):Q("argument-error"),n}toJSON(){return{idToken:this.idToken,accessToken:this.accessToken,secret:this.secret,nonce:this.nonce,pendingToken:this.pendingToken,providerId:this.providerId,signInMethod:this.signInMethod}}static fromJSON(e){const n=typeof e=="string"?JSON.parse(e):e,{providerId:r,signInMethod:s}=n,i=cr(n,["providerId","signInMethod"]);if(!r||!s)return null;const o=new Re(r,s);return o.idToken=i.idToken||void 0,o.accessToken=i.accessToken||void 0,o.secret=i.secret,o.nonce=i.nonce,o.pendingToken=i.pendingToken||null,o}_getIdTokenResponse(e){const n=this.buildRequest();return ze(e,n)}_linkToIdToken(e,n){const r=this.buildRequest();return r.idToken=n,ze(e,r)}_getReauthenticationResolver(e){const n=this.buildRequest();return n.autoCreate=!1,ze(e,n)}buildRequest(){const e={requestUri:Uf,returnSecureToken:!0};if(this.pendingToken)e.pendingToken=this.pendingToken;else{const n={};this.idToken&&(n.id_token=this.idToken),this.accessToken&&(n.access_token=this.accessToken),this.secret&&(n.oauth_token_secret=this.secret),n.providerId=this.providerId,this.nonce&&!this.pendingToken&&(n.nonce=this.nonce),e.postBody=wt(n)}return e}}/**
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
 */function Ff(t){switch(t){case"recoverEmail":return"RECOVER_EMAIL";case"resetPassword":return"PASSWORD_RESET";case"signIn":return"EMAIL_SIGNIN";case"verifyEmail":return"VERIFY_EMAIL";case"verifyAndChangeEmail":return"VERIFY_AND_CHANGE_EMAIL";case"revertSecondFactorAddition":return"REVERT_SECOND_FACTOR_ADDITION";default:return null}}function jf(t){const e=at(lt(t)).link,n=e?at(lt(e)).deep_link_id:null,r=at(lt(t)).deep_link_id;return(r?at(lt(r)).link:null)||r||n||e||t}class mr{constructor(e){var n,r,s,i,o,a;const c=at(lt(e)),l=(n=c.apiKey)!==null&&n!==void 0?n:null,u=(r=c.oobCode)!==null&&r!==void 0?r:null,m=Ff((s=c.mode)!==null&&s!==void 0?s:null);E(l&&u&&m,"argument-error"),this.apiKey=l,this.operation=m,this.code=u,this.continueUrl=(i=c.continueUrl)!==null&&i!==void 0?i:null,this.languageCode=(o=c.languageCode)!==null&&o!==void 0?o:null,this.tenantId=(a=c.tenantId)!==null&&a!==void 0?a:null}static parseLink(e){const n=jf(e);try{return new mr(n)}catch{return null}}}/**
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
 */class Ze{constructor(){this.providerId=Ze.PROVIDER_ID}static credential(e,n){return bt._fromEmailAndPassword(e,n)}static credentialWithLink(e,n){const r=mr.parseLink(n);return E(r,"argument-error"),bt._fromEmailAndCode(e,r.code,r.tenantId)}}Ze.PROVIDER_ID="password";Ze.EMAIL_PASSWORD_SIGN_IN_METHOD="password";Ze.EMAIL_LINK_SIGN_IN_METHOD="emailLink";/**
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
 */class pr{constructor(e){this.providerId=e,this.defaultLanguageCode=null,this.customParameters={}}setDefaultLanguage(e){this.defaultLanguageCode=e}setCustomParameters(e){return this.customParameters=e,this}getCustomParameters(){return this.customParameters}}/**
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
 */class It extends pr{constructor(){super(...arguments),this.scopes=[]}addScope(e){return this.scopes.includes(e)||this.scopes.push(e),this}getScopes(){return[...this.scopes]}}/**
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
 */class ve extends It{constructor(){super("facebook.com")}static credential(e){return Re._fromParams({providerId:ve.PROVIDER_ID,signInMethod:ve.FACEBOOK_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return ve.credentialFromTaggedObject(e)}static credentialFromError(e){return ve.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return ve.credential(e.oauthAccessToken)}catch{return null}}}ve.FACEBOOK_SIGN_IN_METHOD="facebook.com";ve.PROVIDER_ID="facebook.com";/**
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
 */class se extends It{constructor(){super("google.com"),this.addScope("profile")}static credential(e,n){return Re._fromParams({providerId:se.PROVIDER_ID,signInMethod:se.GOOGLE_SIGN_IN_METHOD,idToken:e,accessToken:n})}static credentialFromResult(e){return se.credentialFromTaggedObject(e)}static credentialFromError(e){return se.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthIdToken:n,oauthAccessToken:r}=e;if(!n&&!r)return null;try{return se.credential(n,r)}catch{return null}}}se.GOOGLE_SIGN_IN_METHOD="google.com";se.PROVIDER_ID="google.com";/**
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
 */class ie extends It{constructor(){super("github.com")}static credential(e){return Re._fromParams({providerId:ie.PROVIDER_ID,signInMethod:ie.GITHUB_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return ie.credentialFromTaggedObject(e)}static credentialFromError(e){return ie.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return ie.credential(e.oauthAccessToken)}catch{return null}}}ie.GITHUB_SIGN_IN_METHOD="github.com";ie.PROVIDER_ID="github.com";/**
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
 */class ye extends It{constructor(){super("twitter.com")}static credential(e,n){return Re._fromParams({providerId:ye.PROVIDER_ID,signInMethod:ye.TWITTER_SIGN_IN_METHOD,oauthToken:e,oauthTokenSecret:n})}static credentialFromResult(e){return ye.credentialFromTaggedObject(e)}static credentialFromError(e){return ye.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthAccessToken:n,oauthTokenSecret:r}=e;if(!n||!r)return null;try{return ye.credential(n,r)}catch{return null}}}ye.TWITTER_SIGN_IN_METHOD="twitter.com";ye.PROVIDER_ID="twitter.com";/**
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
 */class Je{constructor(e){this.user=e.user,this.providerId=e.providerId,this._tokenResponse=e._tokenResponse,this.operationType=e.operationType}static async _fromIdTokenResponse(e,n,r,s=!1){const i=await Ae._fromIdTokenResponse(e,r,s),o=_s(r);return new Je({user:i,providerId:o,_tokenResponse:r,operationType:n})}static async _forOperation(e,n,r){await e._updateTokensIfNecessary(r,!0);const s=_s(r);return new Je({user:e,providerId:s,_tokenResponse:r,operationType:n})}}function _s(t){return t.providerId?t.providerId:"phoneNumber"in t?"phone":null}/**
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
 */class Kt extends Ie{constructor(e,n,r,s){var i;super(n.code,n.message),this.operationType=r,this.user=s,Object.setPrototypeOf(this,Kt.prototype),this.customData={appName:e.name,tenantId:(i=e.tenantId)!==null&&i!==void 0?i:void 0,_serverResponse:n.customData._serverResponse,operationType:r}}static _fromErrorAndOperation(e,n,r,s){return new Kt(e,n,r,s)}}function Wi(t,e,n,r){return(e==="reauthenticate"?n._getReauthenticationResolver(t):n._getIdTokenResponse(t)).catch(i=>{throw i.code==="auth/multi-factor-auth-required"?Kt._fromErrorAndOperation(t,i,e,r):i})}async function Bf(t,e,n=!1){const r=await mt(t,e._linkToIdToken(t.auth,await t.getIdToken()),n);return Je._forOperation(t,"link",r)}/**
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
 */async function Hf(t,e,n=!1){var r;const{auth:s}=t,i="reauthenticate";try{const o=await mt(t,Wi(s,i,e,t),n);E(o.idToken,s,"internal-error");const a=fr(o.idToken);E(a,s,"internal-error");const{sub:c}=a;return E(t.uid===c,s,"user-mismatch"),Je._forOperation(t,i,o)}catch(o){throw((r=o)===null||r===void 0?void 0:r.code)==="auth/user-not-found"&&Q(s,"user-mismatch"),o}}/**
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
 */async function Ji(t,e,n=!1){const r="signIn",s=await Wi(t,r,e),i=await Je._fromIdTokenResponse(t,r,s);return n||await t._updateCurrentUser(i.user),i}async function zf(t,e){return Ji(Et(t),e)}function Vf(t,e,n){return zf(De(t),Ze.credential(e,n))}function Wf(t,e,n,r){return De(t).onIdTokenChanged(e,n,r)}function Jf(t,e,n){return De(t).beforeAuthStateChanged(e,n)}const Xt="__sak";/**
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
 */class qi{constructor(e,n){this.storageRetriever=e,this.type=n}_isAvailable(){try{return this.storage?(this.storage.setItem(Xt,"1"),this.storage.removeItem(Xt),Promise.resolve(!0)):Promise.resolve(!1)}catch{return Promise.resolve(!1)}}_set(e,n){return this.storage.setItem(e,JSON.stringify(n)),Promise.resolve()}_get(e){const n=this.storage.getItem(e);return Promise.resolve(n?JSON.parse(n):null)}_remove(e){return this.storage.removeItem(e),Promise.resolve()}get storage(){return this.storageRetriever()}}/**
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
 */function qf(){const t=W();return hr(t)||cn(t)}const Gf=1e3,Kf=10;class Gi extends qi{constructor(){super(()=>window.localStorage,"LOCAL"),this.boundEventHandler=(e,n)=>this.onStorageEvent(e,n),this.listeners={},this.localCache={},this.pollTimer=null,this.safariLocalStorageNotSynced=qf()&&kf(),this.fallbackToPolling=Hi(),this._shouldAllowMigration=!0}forAllChangedKeys(e){for(const n of Object.keys(this.listeners)){const r=this.storage.getItem(n),s=this.localCache[n];r!==s&&e(n,s,r)}}onStorageEvent(e,n=!1){if(!e.key){this.forAllChangedKeys((o,a,c)=>{this.notifyListeners(o,c)});return}const r=e.key;if(n?this.detachListener():this.stopPolling(),this.safariLocalStorageNotSynced){const o=this.storage.getItem(r);if(e.newValue!==o)e.newValue!==null?this.storage.setItem(r,e.newValue):this.storage.removeItem(r);else if(this.localCache[r]===e.newValue&&!n)return}const s=()=>{const o=this.storage.getItem(r);!n&&this.localCache[r]===o||this.notifyListeners(r,o)},i=this.storage.getItem(r);Cf()&&i!==e.newValue&&e.newValue!==e.oldValue?setTimeout(s,Kf):s()}notifyListeners(e,n){this.localCache[e]=n;const r=this.listeners[e];if(r)for(const s of Array.from(r))s(n&&JSON.parse(n))}startPolling(){this.stopPolling(),this.pollTimer=setInterval(()=>{this.forAllChangedKeys((e,n,r)=>{this.onStorageEvent(new StorageEvent("storage",{key:e,oldValue:n,newValue:r}),!0)})},Gf)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}attachListener(){window.addEventListener("storage",this.boundEventHandler)}detachListener(){window.removeEventListener("storage",this.boundEventHandler)}_addListener(e,n){Object.keys(this.listeners).length===0&&(this.fallbackToPolling?this.startPolling():this.attachListener()),this.listeners[e]||(this.listeners[e]=new Set,this.localCache[e]=this.storage.getItem(e)),this.listeners[e].add(n)}_removeListener(e,n){this.listeners[e]&&(this.listeners[e].delete(n),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&(this.detachListener(),this.stopPolling())}async _set(e,n){await super._set(e,n),this.localCache[e]=JSON.stringify(n)}async _get(e){const n=await super._get(e);return this.localCache[e]=JSON.stringify(n),n}async _remove(e){await super._remove(e),delete this.localCache[e]}}Gi.type="LOCAL";const Xf=Gi;/**
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
 */class Ki extends qi{constructor(){super(()=>window.sessionStorage,"SESSION")}_addListener(e,n){}_removeListener(e,n){}}Ki.type="SESSION";const Xi=Ki;/**
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
 */function Yf(t){return Promise.all(t.map(async e=>{try{const n=await e;return{fulfilled:!0,value:n}}catch(n){return{fulfilled:!1,reason:n}}}))}/**
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
 */class un{constructor(e){this.eventTarget=e,this.handlersMap={},this.boundEventHandler=this.handleEvent.bind(this)}static _getInstance(e){const n=this.receivers.find(s=>s.isListeningto(e));if(n)return n;const r=new un(e);return this.receivers.push(r),r}isListeningto(e){return this.eventTarget===e}async handleEvent(e){const n=e,{eventId:r,eventType:s,data:i}=n.data,o=this.handlersMap[s];if(!o?.size)return;n.ports[0].postMessage({status:"ack",eventId:r,eventType:s});const a=Array.from(o).map(async l=>l(n.origin,i)),c=await Yf(a);n.ports[0].postMessage({status:"done",eventId:r,eventType:s,response:c})}_subscribe(e,n){Object.keys(this.handlersMap).length===0&&this.eventTarget.addEventListener("message",this.boundEventHandler),this.handlersMap[e]||(this.handlersMap[e]=new Set),this.handlersMap[e].add(n)}_unsubscribe(e,n){this.handlersMap[e]&&n&&this.handlersMap[e].delete(n),(!n||this.handlersMap[e].size===0)&&delete this.handlersMap[e],Object.keys(this.handlersMap).length===0&&this.eventTarget.removeEventListener("message",this.boundEventHandler)}}un.receivers=[];/**
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
 */function br(t="",e=10){let n="";for(let r=0;r<e;r++)n+=Math.floor(Math.random()*10);return t+n}/**
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
 */class Qf{constructor(e){this.target=e,this.handlers=new Set}removeMessageHandler(e){e.messageChannel&&(e.messageChannel.port1.removeEventListener("message",e.onMessage),e.messageChannel.port1.close()),this.handlers.delete(e)}async _send(e,n,r=50){const s=typeof MessageChannel<"u"?new MessageChannel:null;if(!s)throw new Error("connection_unavailable");let i,o;return new Promise((a,c)=>{const l=br("",20);s.port1.start();const u=setTimeout(()=>{c(new Error("unsupported_event"))},r);o={messageChannel:s,onMessage(m){const b=m;if(b.data.eventId===l)switch(b.data.status){case"ack":clearTimeout(u),i=setTimeout(()=>{c(new Error("timeout"))},3e3);break;case"done":clearTimeout(i),a(b.data.response);break;default:clearTimeout(u),clearTimeout(i),c(new Error("invalid_response"));break}}},this.handlers.add(o),s.port1.addEventListener("message",o.onMessage),this.target.postMessage({eventType:e,eventId:l,data:n},[s.port2])}).finally(()=>{o&&this.removeMessageHandler(o)})}}/**
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
 */function ne(){return window}function Zf(t){ne().location.href=t}/**
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
 */function Yi(){return typeof ne().WorkerGlobalScope<"u"&&typeof ne().importScripts=="function"}async function eh(){if(!navigator?.serviceWorker)return null;try{return(await navigator.serviceWorker.ready).active}catch{return null}}function th(){var t;return((t=navigator?.serviceWorker)===null||t===void 0?void 0:t.controller)||null}function nh(){return Yi()?self:null}/**
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
 */const Qi="firebaseLocalStorageDb",rh=1,Yt="firebaseLocalStorage",Zi="fbase_key";class Tt{constructor(e){this.request=e}toPromise(){return new Promise((e,n)=>{this.request.addEventListener("success",()=>{e(this.request.result)}),this.request.addEventListener("error",()=>{n(this.request.error)})})}}function dn(t,e){return t.transaction([Yt],e?"readwrite":"readonly").objectStore(Yt)}function sh(){const t=indexedDB.deleteDatabase(Qi);return new Tt(t).toPromise()}function Kn(){const t=indexedDB.open(Qi,rh);return new Promise((e,n)=>{t.addEventListener("error",()=>{n(t.error)}),t.addEventListener("upgradeneeded",()=>{const r=t.result;try{r.createObjectStore(Yt,{keyPath:Zi})}catch(s){n(s)}}),t.addEventListener("success",async()=>{const r=t.result;r.objectStoreNames.contains(Yt)?e(r):(r.close(),await sh(),e(await Kn()))})})}async function ws(t,e,n){const r=dn(t,!0).put({[Zi]:e,value:n});return new Tt(r).toPromise()}async function ih(t,e){const n=dn(t,!1).get(e),r=await new Tt(n).toPromise();return r===void 0?null:r.value}function xs(t,e){const n=dn(t,!0).delete(e);return new Tt(n).toPromise()}const oh=800,ah=3;class eo{constructor(){this.type="LOCAL",this._shouldAllowMigration=!0,this.listeners={},this.localCache={},this.pollTimer=null,this.pendingWrites=0,this.receiver=null,this.sender=null,this.serviceWorkerReceiverAvailable=!1,this.activeServiceWorker=null,this._workerInitializationPromise=this.initializeServiceWorkerMessaging().then(()=>{},()=>{})}async _openDb(){return this.db?this.db:(this.db=await Kn(),this.db)}async _withRetries(e){let n=0;for(;;)try{const r=await this._openDb();return await e(r)}catch(r){if(n++>ah)throw r;this.db&&(this.db.close(),this.db=void 0)}}async initializeServiceWorkerMessaging(){return Yi()?this.initializeReceiver():this.initializeSender()}async initializeReceiver(){this.receiver=un._getInstance(nh()),this.receiver._subscribe("keyChanged",async(e,n)=>({keyProcessed:(await this._poll()).includes(n.key)})),this.receiver._subscribe("ping",async(e,n)=>["keyChanged"])}async initializeSender(){var e,n;if(this.activeServiceWorker=await eh(),!this.activeServiceWorker)return;this.sender=new Qf(this.activeServiceWorker);const r=await this.sender._send("ping",{},800);!r||((e=r[0])===null||e===void 0?void 0:e.fulfilled)&&((n=r[0])===null||n===void 0?void 0:n.value.includes("keyChanged"))&&(this.serviceWorkerReceiverAvailable=!0)}async notifyServiceWorker(e){if(!(!this.sender||!this.activeServiceWorker||th()!==this.activeServiceWorker))try{await this.sender._send("keyChanged",{key:e},this.serviceWorkerReceiverAvailable?800:50)}catch{}}async _isAvailable(){try{if(!indexedDB)return!1;const e=await Kn();return await ws(e,Xt,"1"),await xs(e,Xt),!0}catch{}return!1}async _withPendingWrite(e){this.pendingWrites++;try{await e()}finally{this.pendingWrites--}}async _set(e,n){return this._withPendingWrite(async()=>(await this._withRetries(r=>ws(r,e,n)),this.localCache[e]=n,this.notifyServiceWorker(e)))}async _get(e){const n=await this._withRetries(r=>ih(r,e));return this.localCache[e]=n,n}async _remove(e){return this._withPendingWrite(async()=>(await this._withRetries(n=>xs(n,e)),delete this.localCache[e],this.notifyServiceWorker(e)))}async _poll(){const e=await this._withRetries(s=>{const i=dn(s,!1).getAll();return new Tt(i).toPromise()});if(!e)return[];if(this.pendingWrites!==0)return[];const n=[],r=new Set;for(const{fbase_key:s,value:i}of e)r.add(s),JSON.stringify(this.localCache[s])!==JSON.stringify(i)&&(this.notifyListeners(s,i),n.push(s));for(const s of Object.keys(this.localCache))this.localCache[s]&&!r.has(s)&&(this.notifyListeners(s,null),n.push(s));return n}notifyListeners(e,n){this.localCache[e]=n;const r=this.listeners[e];if(r)for(const s of Array.from(r))s(n)}startPolling(){this.stopPolling(),this.pollTimer=setInterval(async()=>this._poll(),oh)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}_addListener(e,n){Object.keys(this.listeners).length===0&&this.startPolling(),this.listeners[e]||(this.listeners[e]=new Set,this._get(e)),this.listeners[e].add(n)}_removeListener(e,n){this.listeners[e]&&(this.listeners[e].delete(n),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&this.stopPolling()}}eo.type="LOCAL";const lh=eo;/**
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
 */function ch(){var t,e;return(e=(t=document.getElementsByTagName("head"))===null||t===void 0?void 0:t[0])!==null&&e!==void 0?e:document}function uh(t){return new Promise((e,n)=>{const r=document.createElement("script");r.setAttribute("src",t),r.onload=e,r.onerror=s=>{const i=te("internal-error");i.customData=s,n(i)},r.type="text/javascript",r.charset="UTF-8",ch().appendChild(r)})}function dh(t){return`__${t}${Math.floor(Math.random()*1e6)}`}new xt(3e4,6e4);/**
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
 */function to(t,e){return e?le(e):(E(t._popupRedirectResolver,t,"argument-error"),t._popupRedirectResolver)}/**
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
 */class vr extends gr{constructor(e){super("custom","custom"),this.params=e}_getIdTokenResponse(e){return ze(e,this._buildIdpRequest())}_linkToIdToken(e,n){return ze(e,this._buildIdpRequest(n))}_getReauthenticationResolver(e){return ze(e,this._buildIdpRequest())}_buildIdpRequest(e){const n={requestUri:this.params.requestUri,sessionId:this.params.sessionId,postBody:this.params.postBody,tenantId:this.params.tenantId,pendingToken:this.params.pendingToken,returnSecureToken:!0,returnIdpCredential:!0};return e&&(n.idToken=e),n}}function fh(t){return Ji(t.auth,new vr(t),t.bypassAuthState)}function hh(t){const{auth:e,user:n}=t;return E(n,e,"internal-error"),Hf(n,new vr(t),t.bypassAuthState)}async function gh(t){const{auth:e,user:n}=t;return E(n,e,"internal-error"),Bf(n,new vr(t),t.bypassAuthState)}/**
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
 */class no{constructor(e,n,r,s,i=!1){this.auth=e,this.resolver=r,this.user=s,this.bypassAuthState=i,this.pendingPromise=null,this.eventManager=null,this.filter=Array.isArray(n)?n:[n]}execute(){return new Promise(async(e,n)=>{this.pendingPromise={resolve:e,reject:n};try{this.eventManager=await this.resolver._initialize(this.auth),await this.onExecution(),this.eventManager.registerConsumer(this)}catch(r){this.reject(r)}})}async onAuthEvent(e){const{urlResponse:n,sessionId:r,postBody:s,tenantId:i,error:o,type:a}=e;if(o){this.reject(o);return}const c={auth:this.auth,requestUri:n,sessionId:r,tenantId:i||void 0,postBody:s||void 0,user:this.user,bypassAuthState:this.bypassAuthState};try{this.resolve(await this.getIdpTask(a)(c))}catch(l){this.reject(l)}}onError(e){this.reject(e)}getIdpTask(e){switch(e){case"signInViaPopup":case"signInViaRedirect":return fh;case"linkViaPopup":case"linkViaRedirect":return gh;case"reauthViaPopup":case"reauthViaRedirect":return hh;default:Q(this.auth,"internal-error")}}resolve(e){fe(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.resolve(e),this.unregisterAndCleanUp()}reject(e){fe(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.reject(e),this.unregisterAndCleanUp()}unregisterAndCleanUp(){this.eventManager&&this.eventManager.unregisterConsumer(this),this.pendingPromise=null,this.cleanUp()}}/**
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
 */const mh=new xt(2e3,1e4);async function Ss(t,e,n){const r=Et(t);af(t,e,pr);const s=to(r,n);return new Ce(r,"signInViaPopup",e,s).executeNotNull()}class Ce extends no{constructor(e,n,r,s,i){super(e,n,s,i),this.provider=r,this.authWindow=null,this.pollId=null,Ce.currentPopupAction&&Ce.currentPopupAction.cancel(),Ce.currentPopupAction=this}async executeNotNull(){const e=await this.execute();return E(e,this.auth,"internal-error"),e}async onExecution(){fe(this.filter.length===1,"Popup operations only handle one event");const e=br();this.authWindow=await this.resolver._openPopup(this.auth,this.provider,this.filter[0],e),this.authWindow.associatedEvent=e,this.resolver._originValidation(this.auth).catch(n=>{this.reject(n)}),this.resolver._isIframeWebStorageSupported(this.auth,n=>{n||this.reject(te(this.auth,"web-storage-unsupported"))}),this.pollUserCancellation()}get eventId(){var e;return((e=this.authWindow)===null||e===void 0?void 0:e.associatedEvent)||null}cancel(){this.reject(te(this.auth,"cancelled-popup-request"))}cleanUp(){this.authWindow&&this.authWindow.close(),this.pollId&&window.clearTimeout(this.pollId),this.authWindow=null,this.pollId=null,Ce.currentPopupAction=null}pollUserCancellation(){const e=()=>{var n,r;if(!((r=(n=this.authWindow)===null||n===void 0?void 0:n.window)===null||r===void 0)&&r.closed){this.pollId=window.setTimeout(()=>{this.pollId=null,this.reject(te(this.auth,"popup-closed-by-user"))},2e3);return}this.pollId=window.setTimeout(e,mh.get())};e()}}Ce.currentPopupAction=null;/**
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
 */const ph="pendingRedirect",Lt=new Map;class bh extends no{constructor(e,n,r=!1){super(e,["signInViaRedirect","linkViaRedirect","reauthViaRedirect","unknown"],n,void 0,r),this.eventId=null}async execute(){let e=Lt.get(this.auth._key());if(!e){try{const r=await vh(this.resolver,this.auth)?await super.execute():null;e=()=>Promise.resolve(r)}catch(n){e=()=>Promise.reject(n)}Lt.set(this.auth._key(),e)}return this.bypassAuthState||Lt.set(this.auth._key(),()=>Promise.resolve(null)),e()}async onAuthEvent(e){if(e.type==="signInViaRedirect")return super.onAuthEvent(e);if(e.type==="unknown"){this.resolve(null);return}if(e.eventId){const n=await this.auth._redirectUserForId(e.eventId);if(n)return this.user=n,super.onAuthEvent(e);this.resolve(null)}}async onExecution(){}cleanUp(){}}async function vh(t,e){const n=wh(e),r=_h(t);if(!await r._isAvailable())return!1;const s=await r._get(n)==="true";return await r._remove(n),s}function yh(t,e){Lt.set(t._key(),e)}function _h(t){return le(t._redirectPersistence)}function wh(t){return Pt(ph,t.config.apiKey,t.name)}async function xh(t,e,n=!1){const r=Et(t),s=to(r,e),o=await new bh(r,s,n).execute();return o&&!n&&(delete o.user._redirectEventId,await r._persistUserIfCurrent(o.user),await r._setRedirectUser(null,e)),o}/**
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
 */const Sh=10*60*1e3;class Eh{constructor(e){this.auth=e,this.cachedEventUids=new Set,this.consumers=new Set,this.queuedRedirectEvent=null,this.hasHandledPotentialRedirect=!1,this.lastProcessedEventTime=Date.now()}registerConsumer(e){this.consumers.add(e),this.queuedRedirectEvent&&this.isEventForConsumer(this.queuedRedirectEvent,e)&&(this.sendToConsumer(this.queuedRedirectEvent,e),this.saveEventToCache(this.queuedRedirectEvent),this.queuedRedirectEvent=null)}unregisterConsumer(e){this.consumers.delete(e)}onEvent(e){if(this.hasEventBeenHandled(e))return!1;let n=!1;return this.consumers.forEach(r=>{this.isEventForConsumer(e,r)&&(n=!0,this.sendToConsumer(e,r),this.saveEventToCache(e))}),this.hasHandledPotentialRedirect||!Ih(e)||(this.hasHandledPotentialRedirect=!0,n||(this.queuedRedirectEvent=e,n=!0)),n}sendToConsumer(e,n){var r;if(e.error&&!ro(e)){const s=((r=e.error.code)===null||r===void 0?void 0:r.split("auth/")[1])||"internal-error";n.onError(te(this.auth,s))}else n.onAuthEvent(e)}isEventForConsumer(e,n){const r=n.eventId===null||!!e.eventId&&e.eventId===n.eventId;return n.filter.includes(e.type)&&r}hasEventBeenHandled(e){return Date.now()-this.lastProcessedEventTime>=Sh&&this.cachedEventUids.clear(),this.cachedEventUids.has(Es(e))}saveEventToCache(e){this.cachedEventUids.add(Es(e)),this.lastProcessedEventTime=Date.now()}}function Es(t){return[t.type,t.eventId,t.sessionId,t.tenantId].filter(e=>e).join("-")}function ro({type:t,error:e}){return t==="unknown"&&e?.code==="auth/no-auth-event"}function Ih(t){switch(t.type){case"signInViaRedirect":case"linkViaRedirect":case"reauthViaRedirect":return!0;case"unknown":return ro(t);default:return!1}}/**
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
 */async function Th(t,e={}){return St(t,"GET","/v1/projects",e)}/**
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
 */const Ch=/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,kh=/^https?/;async function $h(t){if(t.config.emulator)return;const{authorizedDomains:e}=await Th(t);for(const n of e)try{if(Ah(n))return}catch{}Q(t,"unauthorized-domain")}function Ah(t){const e=Gn(),{protocol:n,hostname:r}=new URL(e);if(t.startsWith("chrome-extension://")){const o=new URL(t);return o.hostname===""&&r===""?n==="chrome-extension:"&&t.replace("chrome-extension://","")===e.replace("chrome-extension://",""):n==="chrome-extension:"&&o.hostname===r}if(!kh.test(n))return!1;if(Ch.test(t))return r===t;const s=t.replace(/\./g,"\\.");return new RegExp("^(.+\\."+s+"|"+s+")$","i").test(r)}/**
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
 */const Nh=new xt(3e4,6e4);function Is(){const t=ne().___jsl;if(t?.H){for(const e of Object.keys(t.H))if(t.H[e].r=t.H[e].r||[],t.H[e].L=t.H[e].L||[],t.H[e].r=[...t.H[e].L],t.CP)for(let n=0;n<t.CP.length;n++)t.CP[n]=null}}function Oh(t){return new Promise((e,n)=>{var r,s,i;function o(){Is(),gapi.load("gapi.iframes",{callback:()=>{e(gapi.iframes.getContext())},ontimeout:()=>{Is(),n(te(t,"network-request-failed"))},timeout:Nh.get()})}if(!((s=(r=ne().gapi)===null||r===void 0?void 0:r.iframes)===null||s===void 0)&&s.Iframe)e(gapi.iframes.getContext());else if(!((i=ne().gapi)===null||i===void 0)&&i.load)o();else{const a=dh("iframefcb");return ne()[a]=()=>{gapi.load?o():n(te(t,"network-request-failed"))},uh(`https://apis.google.com/js/api.js?onload=${a}`).catch(c=>n(c))}}).catch(e=>{throw Mt=null,e})}let Mt=null;function Rh(t){return Mt=Mt||Oh(t),Mt}/**
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
 */const Dh=new xt(5e3,15e3),Ph="__/auth/iframe",Lh="emulator/auth/iframe",Mh={style:{position:"absolute",top:"-100px",width:"1px",height:"1px"},"aria-hidden":"true",tabindex:"-1"},Uh=new Map([["identitytoolkit.googleapis.com","p"],["staging-identitytoolkit.sandbox.googleapis.com","s"],["test-identitytoolkit.sandbox.googleapis.com","t"]]);function Fh(t){const e=t.config;E(e.authDomain,t,"auth-domain-config-required");const n=e.emulator?dr(e,Lh):`https://${t.config.authDomain}/${Ph}`,r={apiKey:e.apiKey,appName:t.name,v:on},s=Uh.get(t.config.apiHost);s&&(r.eid=s);const i=t._getFrameworks();return i.length&&(r.fw=i.join(",")),`${n}?${wt(r).slice(1)}`}async function jh(t){const e=await Rh(t),n=ne().gapi;return E(n,t,"internal-error"),e.open({where:document.body,url:Fh(t),messageHandlersFilter:n.iframes.CROSS_ORIGIN_IFRAMES_FILTER,attributes:Mh,dontclear:!0},r=>new Promise(async(s,i)=>{await r.restyle({setHideOnLeave:!1});const o=te(t,"network-request-failed"),a=ne().setTimeout(()=>{i(o)},Dh.get());function c(){ne().clearTimeout(a),s(r)}r.ping(c).then(c,()=>{i(o)})}))}/**
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
 */const Bh={location:"yes",resizable:"yes",statusbar:"yes",toolbar:"no"},Hh=500,zh=600,Vh="_blank",Wh="http://localhost";class Ts{constructor(e){this.window=e,this.associatedEvent=null}close(){if(this.window)try{this.window.close()}catch{}}}function Jh(t,e,n,r=Hh,s=zh){const i=Math.max((window.screen.availHeight-s)/2,0).toString(),o=Math.max((window.screen.availWidth-r)/2,0).toString();let a="";const c=Object.assign(Object.assign({},Bh),{width:r.toString(),height:s.toString(),top:i,left:o}),l=W().toLowerCase();n&&(a=Mi(l)?Vh:n),Li(l)&&(e=e||Wh,c.scrollbars="yes");const u=Object.entries(c).reduce((b,[p,h])=>`${b}${p}=${h},`,"");if(Tf(l)&&a!=="_self")return qh(e||"",a),new Ts(null);const m=window.open(e||"",a,u);E(m,t,"popup-blocked");try{m.focus()}catch{}return new Ts(m)}function qh(t,e){const n=document.createElement("a");n.href=t,n.target=e;const r=document.createEvent("MouseEvent");r.initMouseEvent("click",!0,!0,window,1,0,0,0,0,!1,!1,!1,!1,1,null),n.dispatchEvent(r)}/**
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
 */const Gh="__/auth/handler",Kh="emulator/auth/handler";function Cs(t,e,n,r,s,i){E(t.config.authDomain,t,"auth-domain-config-required"),E(t.config.apiKey,t,"invalid-api-key");const o={apiKey:t.config.apiKey,appName:t.name,authType:n,redirectUrl:r,v:on,eventId:s};if(e instanceof pr){e.setDefaultLanguage(t.languageCode),o.providerId=e.providerId||"",Ku(e.getCustomParameters())||(o.customParameters=JSON.stringify(e.getCustomParameters()));for(const[c,l]of Object.entries(i||{}))o[c]=l}if(e instanceof It){const c=e.getScopes().filter(l=>l!=="");c.length>0&&(o.scopes=c.join(","))}t.tenantId&&(o.tid=t.tenantId);const a=o;for(const c of Object.keys(a))a[c]===void 0&&delete a[c];return`${Xh(t)}?${wt(a).slice(1)}`}function Xh({config:t}){return t.emulator?dr(t,Kh):`https://${t.authDomain}/${Gh}`}/**
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
 */const On="webStorageSupport";class Yh{constructor(){this.eventManagers={},this.iframes={},this.originValidationPromises={},this._redirectPersistence=Xi,this._completeRedirectFn=xh,this._overrideRedirectResult=yh}async _openPopup(e,n,r,s){var i;fe((i=this.eventManagers[e._key()])===null||i===void 0?void 0:i.manager,"_initialize() not called before _openPopup()");const o=Cs(e,n,r,Gn(),s);return Jh(e,o,br())}async _openRedirect(e,n,r,s){return await this._originValidation(e),Zf(Cs(e,n,r,Gn(),s)),new Promise(()=>{})}_initialize(e){const n=e._key();if(this.eventManagers[n]){const{manager:s,promise:i}=this.eventManagers[n];return s?Promise.resolve(s):(fe(i,"If manager is not set, promise should be"),i)}const r=this.initAndGetManager(e);return this.eventManagers[n]={promise:r},r.catch(()=>{delete this.eventManagers[n]}),r}async initAndGetManager(e){const n=await jh(e),r=new Eh(e);return n.register("authEvent",s=>(E(s?.authEvent,e,"invalid-auth-event"),{status:r.onEvent(s.authEvent)?"ACK":"ERROR"}),gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER),this.eventManagers[e._key()]={manager:r},this.iframes[e._key()]=n,r}_isIframeWebStorageSupported(e,n){this.iframes[e._key()].send(On,{type:On},s=>{var i;const o=(i=s?.[0])===null||i===void 0?void 0:i[On];o!==void 0&&n(!!o),Q(e,"internal-error")},gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER)}_originValidation(e){const n=e._key();return this.originValidationPromises[n]||(this.originValidationPromises[n]=$h(e)),this.originValidationPromises[n]}get _shouldInitProactively(){return Hi()||hr()||cn()}}const Qh=Yh;var ks="@firebase/auth",$s="0.20.11";/**
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
 */class Zh{constructor(e){this.auth=e,this.internalListeners=new Map}getUid(){var e;return this.assertAuthConfigured(),((e=this.auth.currentUser)===null||e===void 0?void 0:e.uid)||null}async getToken(e){return this.assertAuthConfigured(),await this.auth._initializationPromise,this.auth.currentUser?{accessToken:await this.auth.currentUser.getIdToken(e)}:null}addAuthTokenListener(e){if(this.assertAuthConfigured(),this.internalListeners.has(e))return;const n=this.auth.onIdTokenChanged(r=>{var s;e(((s=r)===null||s===void 0?void 0:s.stsTokenManager.accessToken)||null)});this.internalListeners.set(e,n),this.updateProactiveRefresh()}removeAuthTokenListener(e){this.assertAuthConfigured();const n=this.internalListeners.get(e);!n||(this.internalListeners.delete(e),n(),this.updateProactiveRefresh())}assertAuthConfigured(){E(this.auth._initializationPromise,"dependent-sdk-initialized-before-auth")}updateProactiveRefresh(){this.internalListeners.size>0?this.auth._startProactiveRefresh():this.auth._stopProactiveRefresh()}}/**
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
 */function eg(t){switch(t){case"Node":return"node";case"ReactNative":return"rn";case"Worker":return"webworker";case"Cordova":return"cordova";default:return}}function tg(t){ht(new We("auth",(e,{options:n})=>{const r=e.getProvider("app").getImmediate(),s=e.getProvider("heartbeat"),{apiKey:i,authDomain:o}=r.options;return((a,c)=>{E(i&&!i.includes(":"),"invalid-api-key",{appName:a.name}),E(!o?.includes(":"),"argument-error",{appName:a.name});const l={apiKey:i,authDomain:o,clientPlatform:t,apiHost:"identitytoolkit.googleapis.com",tokenApiHost:"securetoken.googleapis.com",apiScheme:"https",sdkClientVersion:zi(t)},u=new Af(a,c,l);return cf(u,n),u})(r,s)},"PUBLIC").setInstantiationMode("EXPLICIT").setInstanceCreatedCallback((e,n,r)=>{e.getProvider("auth-internal").initialize()})),ht(new We("auth-internal",e=>{const n=Et(e.getProvider("auth").getImmediate());return(r=>new Zh(r))(n)},"PRIVATE").setInstantiationMode("EXPLICIT")),Be(ks,$s,eg(t)),Be(ks,$s,"esm2017")}/**
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
 */const ng=5*60,rg=_i("authIdTokenMaxAge")||ng;let As=null;const sg=t=>async e=>{const n=e&&await e.getIdTokenResult(),r=n&&(new Date().getTime()-Date.parse(n.issuedAtTime))/1e3;if(r&&r>rg)return;const s=n?.token;As!==s&&(As=s,await fetch(t,{method:s?"POST":"DELETE",headers:s?{Authorization:`Bearer ${s}`}:{}}))};function Rn(t=Kd()){const e=Ei(t,"auth");if(e.isInitialized())return e.getImmediate();const n=lf(t,{popupRedirectResolver:Qh,persistence:[lh,Xf,Xi]}),r=_i("authTokenSyncURL");if(r){const i=sg(r);Jf(n,i,()=>i(n.currentUser)),Wf(n,o=>i(o))}const s=zu("auth");return s&&Nf(n,`http://${s}`),n}tg("Browser");const ig=w('<div><div id="firebaseui-auth-container"></div><div id="container"><div class="flex min-h-full flex-col justify-center py-12 sm:px-6 lg:px-8"><div class="sm:mx-auto sm:w-full sm:max-w-md"><img class="mx-auto h-16 w-auto" alt="OakVar"><h2 class="mt-4 text-center text-3xl font-bold tracking-tight text-gray-900">Sign in</h2><h2 class="hide mt-4 text-center text-3xl font-bold tracking-tight text-gray-900">Sign up</h2></div><p class="mt-2 text-center text-sm text-gray-600">Or&nbsp;<a href="#" class="font-medium text-indigo-600 hover:text-indigo-500">sign up</a><a href="#" class="hide font-medium text-indigo-600 hover:text-indigo-500">sign in</a></p><div class="mt-6 sm:mx-auto sm:w-full sm:max-w-md"><div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10"><div class="space-y-6" method="POST"><div><label for="email" class="block text-sm font-medium text-gray-700">Email address</label><div class="mt-1"><input id="email" name="email" type="email" autocomplete="email" required class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"></div></div><div><label for="password" class="block text-sm font-medium text-gray-700">Password</label><div class="mt-1"><input id="password" name="password" type="password" autocomplete="current-password" required class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"></div></div><div class="flex items-center justify-between"><div class="flex items-center"></div><div class="text-sm"><a href="#" class="font-medium text-indigo-600 hover:text-indigo-500" onclick="sendPasswordResetEmail()">Forgot your password?</a></div></div><div><button id="signin_btn" type="submit" class="flex w-full justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Sign in<svg class="hide animate-spin ml-1 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg></button><button id="signup_btn" type="submit" class="hide flex w-full justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Sign up<svg class="hide animate-spin ml-1 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg></button></div></div><div class="mt-6"><div class="relative"><div class="absolute inset-0 flex items-center"><div class="w-full border-t border-gray-300"></div></div><div class="relative flex justify-center text-sm"><span class="bg-white px-2 text-gray-500">Or continue with</span></div></div><div class="mt-6 grid grid-cols-2 gap-3"><div><a href="#" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-500 shadow-sm hover:bg-gray-50" title="Sign in with Google"><span class="sr-only">Sign in with Google</span><svg class="h-5 w-5" fill="currentColor" viewBox="0 0 1024 1024"><path d="M881 442.4H519.7v148.5h206.4c-8.9 48-35.9 88.6-76.6 115.8-34.4 23-78.3 36.6-129.9 36.6-99.9 0-184.4-67.5-214.6-158.2-7.6-23-12-47.6-12-72.9s4.4-49.9 12-72.9c30.3-90.6 114.8-158.1 214.7-158.1 56.3 0 106.8 19.4 146.6 57.4l110-110.1c-66.5-62-153.2-100-256.6-100-149.9 0-279.6 86-342.7 211.4-26 51.8-40.8 110.4-40.8 172.4S151 632.8 177 684.6C240.1 810 369.8 896 519.7 896c103.6 0 190.4-34.4 253.8-93 72.5-66.8 114.4-165.2 114.4-282.1 0-27.2-2.4-53.3-6.9-78.5z"></path></svg></a></div><div><a href="#" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-500 shadow-sm hover:bg-gray-50" title="Sign in with GitHub"><span class="sr-only">Sign in with GitHub</span><svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clip-rule="evenodd"></path></svg></a></div></div></div></div></div></div></div></div>'),{logged:Mg,setLogged:Ns}=Qe,{email:st,setEmail:Os}=mi,{tabName:Ug,setTabName:og}=Ye;function ag(t){const{serverUrl:e,setServerUrl:n,withCredentials:r}=q,[s,i]=S("signin"),[o,a]=S(!1),[c,l]=S(!1),[u,m]=S(null);qe(function(){});function b(_){Os(_.target.value)}function p(_){m(_.target.value)}function h(_){const k=_.user.accessToken;D.post(e()+"/server/loginsuccess",{login_token:k},{withCredentials:r}).then(function(C){Os(C.data.email),a(!1),og("submit"),Ns(!0)}).catch(function(C){console.error(C),alert(C),a(!1)})}function v(){a(!0);const _=Rn(t.firebaseApp);Vf(_,st(),u()).then(function(k){h(k)}).catch(function(k){console.error(k),alert(k),a(!1)})}function x(){a(!0);const _=new se,k=Rn(t.firebaseApp);Ss(k,_).then(function(C){h(C)}).catch(function(C){console.error(C),alert(C),a(!1)})}function y(){a(!0);const _=new ie,k=Rn(t.firebaseApp);Ss(k,_).then(function(C){h(C)}).catch(function(C){console.error(C),alert(C),a(!1)})}function I(){if(l(!0),!st().match(/^\S+@\S+\.\S+$/)&&st()!="admin"){alert("Invalid email");return}if(u()==""){alert("Password is empty.");return}D.post(e()+"/server/signup",{email:st(),password:u()},{withCredentials:r}).then(function(_){l(!1),Ns(!0)}).catch(function(_){alert(_),console.error(_),l(!1)})}return(()=>{const _=ig.cloneNode(!0),k=_.firstChild,C=k.nextSibling,J=C.firstChild,K=J.firstChild,ee=K.firstChild,A=ee.nextSibling,L=A.nextSibling,M=K.nextSibling,Z=M.firstChild,Pe=Z.nextSibling,et=Pe.nextSibling,yr=M.nextSibling,fn=yr.firstChild,Ct=fn.firstChild,Le=Ct.firstChild,re=Le.firstChild,Me=re.nextSibling,j=Me.firstChild,Ue=Le.nextSibling,hn=Ue.firstChild,gn=hn.nextSibling,kt=gn.firstChild,$t=Ue.nextSibling,mn=$t.firstChild,pn=mn.nextSibling,bn=$t.nextSibling,Fe=bn.firstChild,vn=Fe.firstChild,yn=vn.nextSibling,tt=Fe.nextSibling,_n=tt.firstChild,wn=_n.nextSibling,xn=Ct.nextSibling,O=xn.firstChild,F=O.nextSibling,me=F.firstChild,nt=me.firstChild,so=me.nextSibling,io=so.firstChild;return Pe.$$click=i,Pe.$$clickData="signup",et.$$click=i,et.$$clickData="signin",j.$$keyup=b,kt.$$keyup=p,Fe.$$click=v,tt.$$click=I,nt.$$click=x,io.$$click=y,T(U=>{const _r=e()+"/submit/images/logo_only.png",wr=s()!="signin",xr=s()!="signup",Sr=s()!="signin",Er=s()!="signup",Ir=s()!="signin",Tr=s()!="signin",Cr=o()==!1,kr=s()!="signup",$r=c()==!1;return _r!==U._v$&&V(ee,"src",U._v$=_r),wr!==U._v$2&&A.classList.toggle("hidden",U._v$2=wr),xr!==U._v$3&&L.classList.toggle("hidden",U._v$3=xr),Sr!==U._v$4&&Pe.classList.toggle("hidden",U._v$4=Sr),Er!==U._v$5&&et.classList.toggle("hidden",U._v$5=Er),Ir!==U._v$6&&pn.classList.toggle("hidden",U._v$6=Ir),Tr!==U._v$7&&Fe.classList.toggle("hidden",U._v$7=Tr),Cr!==U._v$8&&yn.classList.toggle("hidden",U._v$8=Cr),kr!==U._v$9&&tt.classList.toggle("hidden",U._v$9=kr),$r!==U._v$10&&wn.classList.toggle("hidden",U._v$10=$r),U},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0,_v$6:void 0,_v$7:void 0,_v$8:void 0,_v$9:void 0,_v$10:void 0}),T(()=>j.value=st()),T(()=>kt.value=u()),_})()}N(["click","keyup"]);var lg="firebase",cg="9.13.0";/**
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
 */Be(lg,cg,"app");function ug(){const{serverUrl:t,setServerUrl:e}=q,{multiuser:n,setMultiuser:r}=sn,{logged:s,setLogged:i}=Qe,o={apiKey:"AIzaSyAX9a9qLUzLoVFy9YrRprTWuf7lwZ-cEi0",authDomain:"fabled-pivot-305219.firebaseapp.com",projectId:"fabled-pivot-305219",storageBucket:"fabled-pivot-305219.appspot.com",messagingSenderId:"293220208202",appId:"1:293220208202:web:59eabbc4f981ead408e0b3",measurementId:"G-7E7PGPVJ99"};let a;r(null),i(null);function c(){D.get(t()+"/server/deletetoken").then(function(m){console.log("@ res=",m)}).catch(function(m){console.error(m)})}function l(){D.get(t()+"/submit/servermode").then(function(m){r(m.data.servermode),n()?a=Ii(o):c()}).catch(function(m){console.error(m)})}function u(){D.get(t()+"/submit/loginstate").then(function(m){i(m.data.loggedin)}).catch(function(m){console.error(m)})}return n()==null&&l(),s()==null&&u(),g(oe,{get when(){return!n()||s()},get fallback(){return g(ag,{firebaseApp:a})},get children(){return g(Au,{})}})}To(()=>g(ug,{}),document.getElementById("root"));
