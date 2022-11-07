(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))r(s);new MutationObserver(s=>{for(const i of s)if(i.type==="childList")for(const o of i.addedNodes)o.tagName==="LINK"&&o.rel==="modulepreload"&&r(o)}).observe(document,{childList:!0,subtree:!0});function n(s){const i={};return s.integrity&&(i.integrity=s.integrity),s.referrerpolicy&&(i.referrerPolicy=s.referrerpolicy),s.crossorigin==="use-credentials"?i.credentials="include":s.crossorigin==="anonymous"?i.credentials="omit":i.credentials="same-origin",i}function r(s){if(s.ep)return;s.ep=!0;const i=n(s);fetch(s.href,i)}})();const H={};function Lo(t){H.context=t}const Mo=(t,e)=>t===e,Be=Symbol("solid-proxy"),Wn=Symbol("solid-track"),Kt={equals:Mo};let qs=Qs;const ye=1,Xt=2,Gs={owned:null,cleanups:null,context:null,owner:null},Dn={};var V=null;let Ue=null,j=null,W=null,me=null,ar=0;function Y(t,e){const n=j,r=V,s=t.length===0,i=s?Gs:{owned:null,cleanups:null,context:null,owner:e||r},o=s?t:()=>t(()=>$e(()=>cr(i)));V=i,j=null;try{return Ce(o,!0)}finally{j=n,V=r}}function y(t,e){e=e?Object.assign({},Kt,e):Kt;const n={value:t,observers:null,observerSlots:null,comparator:e.equals||void 0},r=s=>(typeof s=="function"&&(s=s(n.value)),Ys(n,s));return[Xs.bind(n),r]}function Hr(t,e,n){const r=un(t,e,!0,ye);Qe(r)}function k(t,e,n){const r=un(t,e,!1,ye);Qe(r)}function Et(t,e,n){qs=zo;const r=un(t,e,!1,ye);r.user=!0,me?me.push(r):Qe(r)}function be(t,e,n){n=n?Object.assign({},Kt,n):Kt;const r=un(t,e,!0,0);return r.observers=null,r.observerSlots=null,r.comparator=n.equals||void 0,Qe(r),Xs.bind(r)}function lr(t,e,n){let r,s,i;arguments.length===2&&typeof e=="object"||arguments.length===1?(r=!0,s=t,i=e||{}):(r=t,s=e,i=n||{});let o=null,a=Dn,c=null,l=!1,u="initialValue"in i,p=typeof r=="function"&&be(r);const v=new Set,[b,g]=(i.storage||y)(i.initialValue),[m,x]=y(void 0),[_,S]=y(void 0,{equals:!1}),[T,O]=y(u?"ready":"unresolved");if(H.context){c=`${H.context.id}${H.context.count++}`;let C;i.ssrLoadFrom==="initial"?a=i.initialValue:H.load&&(C=H.load(c))&&(a=C[0])}function N(C,R,U,re){return o===C&&(o=null,u=!0,(C===a||R===a)&&i.onHydrated&&queueMicrotask(()=>i.onHydrated(re,{value:R})),a=Dn,X(R,U)),R}function X(C,R){Ce(()=>{R||g(()=>C),x(R),O(R?"errored":"ready");for(const U of v.keys())U.decrement();v.clear()},!1)}function G(){const C=Fo,R=b(),U=m();if(U&&!o)throw U;return j&&!j.user&&C&&Hr(()=>{_(),o&&(C.resolved||v.has(C)||(C.increment(),v.add(C)))}),R}function le(C=!0){if(C!==!1&&l)return;l=!1;const R=p?p():r;if(R==null||R===!1){N(o,$e(b));return}const U=a!==Dn?a:$e(()=>s(R,{value:b(),refetching:C}));return typeof U!="object"||!(U&&"then"in U)?(N(o,U),U):(o=U,l=!0,queueMicrotask(()=>l=!1),Ce(()=>{O(u?"refreshing":"pending"),S()},!1),U.then(re=>N(U,re,void 0,R),re=>N(U,void 0,ei(re))))}return Object.defineProperties(G,{state:{get:()=>T()},error:{get:()=>m()},loading:{get(){const C=T();return C==="pending"||C==="refreshing"}},latest:{get(){if(!u)return G();const C=m();if(C&&!o)throw C;return b()}}}),p?Hr(()=>le(!1)):le(!1),[G,{refetch:le,mutate:g}]}function Uo(t){return Ce(t,!1)}function $e(t){let e,n=j;return j=null,e=t(),j=n,e}function Yt(t){return V===null||(V.cleanups===null?V.cleanups=[t]:V.cleanups.push(t)),t}function Ks(){return j}function jo(t){const e=be(t),n=be(()=>Jn(e()));return n.toArray=()=>{const r=n();return Array.isArray(r)?r:r!=null?[r]:[]},n}let Fo;function Xs(){const t=Ue;if(this.sources&&(this.state||t))if(this.state===ye||t)Qe(this);else{const e=W;W=null,Ce(()=>Zt(this),!1),W=e}if(j){const e=this.observers?this.observers.length:0;j.sources?(j.sources.push(this),j.sourceSlots.push(e)):(j.sources=[this],j.sourceSlots=[e]),this.observers?(this.observers.push(j),this.observerSlots.push(j.sources.length-1)):(this.observers=[j],this.observerSlots=[j.sources.length-1])}return this.value}function Ys(t,e,n){let r=t.value;return(!t.comparator||!t.comparator(r,e))&&(t.value=e,t.observers&&t.observers.length&&Ce(()=>{for(let s=0;s<t.observers.length;s+=1){const i=t.observers[s],o=Ue&&Ue.running;o&&Ue.disposed.has(i),(o&&!i.tState||!o&&!i.state)&&(i.pure?W.push(i):me.push(i),i.observers&&Zs(i)),o||(i.state=ye)}if(W.length>1e6)throw W=[],new Error},!1)),e}function Qe(t){if(!t.fn)return;cr(t);const e=V,n=j,r=ar;j=V=t,Bo(t,t.value,r),j=n,V=e}function Bo(t,e,n){let r;try{r=t.fn(e)}catch(s){t.pure&&(t.state=ye),ti(s)}(!t.updatedAt||t.updatedAt<=n)&&(t.updatedAt!=null&&"observers"in t?Ys(t,r):t.value=r,t.updatedAt=n)}function un(t,e,n,r=ye,s){const i={fn:t,state:r,updatedAt:null,owned:null,sources:null,sourceSlots:null,cleanups:null,value:e,owner:V,context:null,pure:n};return V===null||V!==Gs&&(V.owned?V.owned.push(i):V.owned=[i]),i}function Qt(t){const e=Ue;if(t.state===0||e)return;if(t.state===Xt||e)return Zt(t);if(t.suspense&&$e(t.suspense.inFallback))return t.suspense.effects.push(t);const n=[t];for(;(t=t.owner)&&(!t.updatedAt||t.updatedAt<ar);)(t.state||e)&&n.push(t);for(let r=n.length-1;r>=0;r--)if(t=n[r],t.state===ye||e)Qe(t);else if(t.state===Xt||e){const s=W;W=null,Ce(()=>Zt(t,n[0]),!1),W=s}}function Ce(t,e){if(W)return t();let n=!1;e||(W=[]),me?n=!0:me=[],ar++;try{const r=t();return Ho(n),r}catch(r){W||(me=null),ti(r)}}function Ho(t){if(W&&(Qs(W),W=null),t)return;const e=me;me=null,e.length&&Ce(()=>qs(e),!1)}function Qs(t){for(let e=0;e<t.length;e++)Qt(t[e])}function zo(t){let e,n=0;for(e=0;e<t.length;e++){const r=t[e];r.user?t[n++]=r:Qt(r)}for(H.context&&Lo(),e=0;e<n;e++)Qt(t[e])}function Zt(t,e){const n=Ue;t.state=0;for(let r=0;r<t.sources.length;r+=1){const s=t.sources[r];s.sources&&(s.state===ye||n?s!==e&&Qt(s):(s.state===Xt||n)&&Zt(s,e))}}function Zs(t){const e=Ue;for(let n=0;n<t.observers.length;n+=1){const r=t.observers[n];(!r.state||e)&&(r.state=Xt,r.pure?W.push(r):me.push(r),r.observers&&Zs(r))}}function cr(t){let e;if(t.sources)for(;t.sources.length;){const n=t.sources.pop(),r=t.sourceSlots.pop(),s=n.observers;if(s&&s.length){const i=s.pop(),o=n.observerSlots.pop();r<s.length&&(i.sourceSlots[o]=r,s[r]=i,n.observerSlots[r]=o)}}if(t.owned){for(e=0;e<t.owned.length;e++)cr(t.owned[e]);t.owned=null}if(t.cleanups){for(e=0;e<t.cleanups.length;e++)t.cleanups[e]();t.cleanups=null}t.state=0,t.context=null}function ei(t){return t instanceof Error||typeof t=="string"?t:new Error("Unknown error")}function ti(t){throw t=ei(t),t}function Jn(t){if(typeof t=="function"&&!t.length)return Jn(t());if(Array.isArray(t)){const e=[];for(let n=0;n<t.length;n++){const r=Jn(t[n]);Array.isArray(r)?e.push.apply(e,r):e.push(r)}return e}return t}const Vo=Symbol("fallback");function zr(t){for(let e=0;e<t.length;e++)t[e]()}function Wo(t,e,n={}){let r=[],s=[],i=[],o=0,a=e.length>1?[]:null;return Yt(()=>zr(i)),()=>{let c=t()||[],l,u;return c[Wn],$e(()=>{let v=c.length,b,g,m,x,_,S,T,O,N;if(v===0)o!==0&&(zr(i),i=[],r=[],s=[],o=0,a&&(a=[])),n.fallback&&(r=[Vo],s[0]=Y(X=>(i[0]=X,n.fallback())),o=1);else if(o===0){for(s=new Array(v),u=0;u<v;u++)r[u]=c[u],s[u]=Y(p);o=v}else{for(m=new Array(v),x=new Array(v),a&&(_=new Array(v)),S=0,T=Math.min(o,v);S<T&&r[S]===c[S];S++);for(T=o-1,O=v-1;T>=S&&O>=S&&r[T]===c[O];T--,O--)m[O]=s[T],x[O]=i[T],a&&(_[O]=a[T]);for(b=new Map,g=new Array(O+1),u=O;u>=S;u--)N=c[u],l=b.get(N),g[u]=l===void 0?-1:l,b.set(N,u);for(l=S;l<=T;l++)N=r[l],u=b.get(N),u!==void 0&&u!==-1?(m[u]=s[l],x[u]=i[l],a&&(_[u]=a[l]),u=g[u],b.set(N,u)):i[l]();for(u=S;u<v;u++)u in m?(s[u]=m[u],i[u]=x[u],a&&(a[u]=_[u],a[u](u))):s[u]=Y(p);s=s.slice(0,o=v),r=c.slice(0)}return s});function p(v){if(i[u]=v,a){const[b,g]=y(u);return a[u]=g,e(c[u],b)}return e(c[u])}}}function h(t,e){return $e(()=>t(e||{}))}function Ae(t){const e="fallback"in t&&{fallback:()=>t.fallback};return be(Wo(()=>t.each,t.children,e||void 0))}function se(t){let e=!1;const n=t.keyed,r=be(()=>t.when,void 0,{equals:(s,i)=>e?s===i:!s==!i});return be(()=>{const s=r();if(s){const i=t.children,o=typeof i=="function"&&i.length>0;return e=n||o,o?$e(()=>i(s)):i}return t.fallback})}function Jo(t){let e=!1,n=!1;const r=jo(()=>t.children),s=be(()=>{let i=r();Array.isArray(i)||(i=[i]);for(let o=0;o<i.length;o++){const a=i[o].when;if(a)return n=!!i[o].keyed,[o,a,i[o]]}return[-1]},void 0,{equals:(i,o)=>i[0]===o[0]&&(e?i[1]===o[1]:!i[1]==!o[1])&&i[2]===o[2]});return be(()=>{const[i,o,a]=s();if(i<0)return t.fallback;const c=a.children,l=typeof c=="function"&&c.length>0;return e=n||l,l?$e(()=>c(o)):c})}function Vr(t){return t}const qo=["allowfullscreen","async","autofocus","autoplay","checked","controls","default","disabled","formnovalidate","hidden","indeterminate","ismap","loop","multiple","muted","nomodule","novalidate","open","playsinline","readonly","required","reversed","seamless","selected"],Go=new Set(["className","value","readOnly","formNoValidate","isMap","noModule","playsInline",...qo]),Ko=new Set(["innerHTML","textContent","innerText","children"]),Xo={className:"class",htmlFor:"for"},Wr={class:"className",formnovalidate:"formNoValidate",ismap:"isMap",nomodule:"noModule",playsinline:"playsInline",readonly:"readOnly"},Yo=new Set(["beforeinput","click","dblclick","contextmenu","focusin","focusout","input","keydown","keyup","mousedown","mousemove","mouseout","mouseover","mouseup","pointerdown","pointermove","pointerout","pointerover","pointerup","touchend","touchmove","touchstart"]),Qo={xlink:"http://www.w3.org/1999/xlink",xml:"http://www.w3.org/XML/1998/namespace"};function Zo(t,e){return be(t,void 0,e?void 0:{equals:e})}function ea(t,e,n){let r=n.length,s=e.length,i=r,o=0,a=0,c=e[s-1].nextSibling,l=null;for(;o<s||a<i;){if(e[o]===n[a]){o++,a++;continue}for(;e[s-1]===n[i-1];)s--,i--;if(s===o){const u=i<r?a?n[a-1].nextSibling:n[i-a]:c;for(;a<i;)t.insertBefore(n[a++],u)}else if(i===a)for(;o<s;)(!l||!l.has(e[o]))&&e[o].remove(),o++;else if(e[o]===n[i-1]&&n[a]===e[s-1]){const u=e[--s].nextSibling;t.insertBefore(n[a++],e[o++].nextSibling),t.insertBefore(n[--i],u),e[s]=n[i]}else{if(!l){l=new Map;let p=a;for(;p<i;)l.set(n[p],p++)}const u=l.get(e[o]);if(u!=null)if(a<u&&u<i){let p=o,v=1,b;for(;++p<s&&p<i&&!((b=l.get(e[p]))==null||b!==u+v);)v++;if(v>u-a){const g=e[o];for(;a<u;)t.insertBefore(n[a++],g)}else t.replaceChild(n[a++],e[o++])}else o++;else e[o++].remove()}}}const Jr="_$DX_DELEGATE";function ta(t,e,n){let r;return Y(s=>{r=s,e===document?t():d(e,t(),e.firstChild?null:void 0,n)}),()=>{r(),e.textContent=""}}function w(t,e,n){const r=document.createElement("template");r.innerHTML=t;let s=r.content.firstChild;return n&&(s=s.firstChild),s}function A(t,e=window.document){const n=e[Jr]||(e[Jr]=new Set);for(let r=0,s=t.length;r<s;r++){const i=t[r];n.has(i)||(n.add(i),e.addEventListener(i,ia))}}function J(t,e,n){n==null?t.removeAttribute(e):t.setAttribute(e,n)}function na(t,e,n,r){r==null?t.removeAttributeNS(e,n):t.setAttributeNS(e,n,r)}function ni(t,e){e==null?t.removeAttribute("class"):t.className=e}function dn(t,e,n,r){if(r)Array.isArray(n)?(t[`$$${e}`]=n[0],t[`$$${e}Data`]=n[1]):t[`$$${e}`]=n;else if(Array.isArray(n)){const s=n[0];t.addEventListener(e,n[0]=i=>s.call(t,n[1],i))}else t.addEventListener(e,n)}function Ht(t,e,n={}){const r=Object.keys(e||{}),s=Object.keys(n);let i,o;for(i=0,o=s.length;i<o;i++){const a=s[i];!a||a==="undefined"||e[a]||(Gr(t,a,!1),delete n[a])}for(i=0,o=r.length;i<o;i++){const a=r[i],c=!!e[a];!a||a==="undefined"||n[a]===c||!c||(Gr(t,a,!0),n[a]=c)}return n}function ri(t,e,n){if(!e)return n?J(t,"style"):e;const r=t.style;if(typeof e=="string")return r.cssText=e;typeof n=="string"&&(r.cssText=n=void 0),n||(n={}),e||(e={});let s,i;for(i in n)e[i]==null&&r.removeProperty(i),delete n[i];for(i in e)s=e[i],s!==n[i]&&(r.setProperty(i,s),n[i]=s);return n}function qr(t,e,n,r){typeof e=="function"?k(s=>Xr(t,e(),s,n,r)):Xr(t,e,void 0,n,r)}function d(t,e,n,r){if(n!==void 0&&!r&&(r=[]),typeof e!="function")return Ke(t,e,r,n);k(s=>Ke(t,e(),s,n),r)}function ra(t,e,n,r,s={},i=!1){e||(e={});for(const o in s)if(!(o in e)){if(o==="children")continue;s[o]=Kr(t,o,null,s[o],n,i)}for(const o in e){if(o==="children"){r||Ke(t,e.children);continue}const a=e[o];s[o]=Kr(t,o,a,s[o],n,i)}}function sa(t){return t.toLowerCase().replace(/-([a-z])/g,(e,n)=>n.toUpperCase())}function Gr(t,e,n){const r=e.trim().split(/\s+/);for(let s=0,i=r.length;s<i;s++)t.classList.toggle(r[s],n)}function Kr(t,e,n,r,s,i){let o,a,c;if(e==="style")return ri(t,n,r);if(e==="classList")return Ht(t,n,r);if(n===r)return r;if(e==="ref")i||n(t);else if(e.slice(0,3)==="on:"){const l=e.slice(3);r&&t.removeEventListener(l,r),n&&t.addEventListener(l,n)}else if(e.slice(0,10)==="oncapture:"){const l=e.slice(10);r&&t.removeEventListener(l,r,!0),n&&t.addEventListener(l,n,!0)}else if(e.slice(0,2)==="on"){const l=e.slice(2).toLowerCase(),u=Yo.has(l);if(!u&&r){const p=Array.isArray(r)?r[0]:r;t.removeEventListener(l,p)}(u||n)&&(dn(t,l,n,u),u&&A([l]))}else if((c=Ko.has(e))||!s&&(Wr[e]||(a=Go.has(e)))||(o=t.nodeName.includes("-")))e==="class"||e==="className"?ni(t,n):o&&!a&&!c?t[sa(e)]=n:t[Wr[e]||e]=n;else{const l=s&&e.indexOf(":")>-1&&Qo[e.split(":")[0]];l?na(t,l,e,n):J(t,Xo[e]||e,n)}return n}function ia(t){const e=`$$${t.type}`;let n=t.composedPath&&t.composedPath()[0]||t.target;for(t.target!==n&&Object.defineProperty(t,"target",{configurable:!0,value:n}),Object.defineProperty(t,"currentTarget",{configurable:!0,get(){return n||document}}),H.registry&&!H.done&&(H.done=!0,document.querySelectorAll("[id^=pl-]").forEach(r=>r.remove()));n!==null;){const r=n[e];if(r&&!n.disabled){const s=n[`${e}Data`];if(s!==void 0?r.call(n,s,t):r.call(n,t),t.cancelBubble)return}n=n.host&&n.host!==n&&n.host instanceof Node?n.host:n.parentNode}}function Xr(t,e,n={},r,s){return e||(e={}),s||k(()=>n.children=Ke(t,e.children,n.children)),k(()=>e.ref&&e.ref(t)),k(()=>ra(t,e,r,!0,n,!0)),n}function Ke(t,e,n,r,s){for(H.context&&!n&&(n=[...t.childNodes]);typeof n=="function";)n=n();if(e===n)return n;const i=typeof e,o=r!==void 0;if(t=o&&n[0]&&n[0].parentNode||t,i==="string"||i==="number"){if(H.context)return n;if(i==="number"&&(e=e.toString()),o){let a=n[0];a&&a.nodeType===3?a.data=e:a=document.createTextNode(e),n=We(t,n,r,a)}else n!==""&&typeof n=="string"?n=t.firstChild.data=e:n=t.textContent=e}else if(e==null||i==="boolean"){if(H.context)return n;n=We(t,n,r)}else{if(i==="function")return k(()=>{let a=e();for(;typeof a=="function";)a=a();n=Ke(t,a,n,r)}),()=>n;if(Array.isArray(e)){const a=[],c=n&&Array.isArray(n);if(qn(a,e,n,s))return k(()=>n=Ke(t,a,n,r,!0)),()=>n;if(H.context){if(!a.length)return n;for(let l=0;l<a.length;l++)if(a[l].parentNode)return n=a}if(a.length===0){if(n=We(t,n,r),o)return n}else c?n.length===0?Yr(t,a,r):ea(t,n,a):(n&&We(t),Yr(t,a));n=a}else if(e instanceof Node){if(H.context&&e.parentNode)return n=o?[e]:e;if(Array.isArray(n)){if(o)return n=We(t,n,r,e);We(t,n,null,e)}else n==null||n===""||!t.firstChild?t.appendChild(e):t.replaceChild(e,t.firstChild);n=e}}return n}function qn(t,e,n,r){let s=!1;for(let i=0,o=e.length;i<o;i++){let a=e[i],c=n&&n[i];if(a instanceof Node)t.push(a);else if(!(a==null||a===!0||a===!1))if(Array.isArray(a))s=qn(t,a,c)||s;else if(typeof a=="function")if(r){for(;typeof a=="function";)a=a();s=qn(t,Array.isArray(a)?a:[a],Array.isArray(c)?c:[c])||s}else t.push(a),s=!0;else{const l=String(a);c&&c.nodeType===3&&c.data===l?t.push(c):t.push(document.createTextNode(l))}}return s}function Yr(t,e,n){for(let r=0,s=e.length;r<s;r++)t.insertBefore(e[r],n)}function We(t,e,n,r){if(n===void 0)return t.textContent="";const s=r||document.createTextNode("");if(e.length){let i=!1;for(let o=e.length-1;o>=0;o--){const a=e[o];if(s!==a){const c=a.parentNode===t;!i&&!o?c?t.replaceChild(s,a):t.insertBefore(s,n):c&&a.remove()}else i=!0}}else t.insertBefore(s,n);return[s]}const oa=!1,aa="http://www.w3.org/2000/svg";function la(t,e=!1){return e?document.createElementNS(aa,t):document.createElement(t)}function ca(t){const{useShadow:e}=t,n=document.createTextNode(""),r=t.mount||document.body;function s(){if(H.context){const[i,o]=y(!1);return queueMicrotask(()=>o(!0)),()=>i()&&t.children}else return()=>t.children}if(r instanceof HTMLHeadElement){const[i,o]=y(!1),a=()=>o(!0);Y(c=>d(r,()=>i()?c():s()(),null)),Yt(()=>{H.context?queueMicrotask(a):a()})}else{const i=la(t.isSVG?"g":"div",t.isSVG),o=e&&i.attachShadow?i.attachShadow({mode:"open"}):i;Object.defineProperty(i,"host",{get(){return n.parentNode}}),d(o,s()),r.appendChild(i),t.ref&&t.ref(i),Yt(()=>r.removeChild(i))}return n}function si(t,e){return function(){return t.apply(e,arguments)}}const{toString:ii}=Object.prototype,{getPrototypeOf:ur}=Object,dr=(t=>e=>{const n=ii.call(e);return t[n]||(t[n]=n.slice(8,-1).toLowerCase())})(Object.create(null)),_e=t=>(t=t.toLowerCase(),e=>dr(e)===t),fn=t=>e=>typeof e===t,{isArray:It}=Array,Gn=fn("undefined");function ua(t){return t!==null&&!Gn(t)&&t.constructor!==null&&!Gn(t.constructor)&&Ze(t.constructor.isBuffer)&&t.constructor.isBuffer(t)}const oi=_e("ArrayBuffer");function da(t){let e;return typeof ArrayBuffer<"u"&&ArrayBuffer.isView?e=ArrayBuffer.isView(t):e=t&&t.buffer&&oi(t.buffer),e}const fa=fn("string"),Ze=fn("function"),ai=fn("number"),li=t=>t!==null&&typeof t=="object",ha=t=>t===!0||t===!1,zt=t=>{if(dr(t)!=="object")return!1;const e=ur(t);return(e===null||e===Object.prototype||Object.getPrototypeOf(e)===null)&&!(Symbol.toStringTag in t)&&!(Symbol.iterator in t)},ga=_e("Date"),ma=_e("File"),pa=_e("Blob"),ba=_e("FileList"),va=t=>li(t)&&Ze(t.pipe),ya=t=>{const e="[object FormData]";return t&&(typeof FormData=="function"&&t instanceof FormData||ii.call(t)===e||Ze(t.toString)&&t.toString()===e)},_a=_e("URLSearchParams"),wa=t=>t.trim?t.trim():t.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g,"");function hn(t,e,{allOwnKeys:n=!1}={}){if(t===null||typeof t>"u")return;let r,s;if(typeof t!="object"&&(t=[t]),It(t))for(r=0,s=t.length;r<s;r++)e.call(null,t[r],r,t);else{const i=n?Object.getOwnPropertyNames(t):Object.keys(t),o=i.length;let a;for(r=0;r<o;r++)a=i[r],e.call(null,t[a],a,t)}}function Kn(){const t={},e=(n,r)=>{zt(t[r])&&zt(n)?t[r]=Kn(t[r],n):zt(n)?t[r]=Kn({},n):It(n)?t[r]=n.slice():t[r]=n};for(let n=0,r=arguments.length;n<r;n++)arguments[n]&&hn(arguments[n],e);return t}const xa=(t,e,n,{allOwnKeys:r}={})=>(hn(e,(s,i)=>{n&&Ze(s)?t[i]=si(s,n):t[i]=s},{allOwnKeys:r}),t),Ea=t=>(t.charCodeAt(0)===65279&&(t=t.slice(1)),t),Ia=(t,e,n,r)=>{t.prototype=Object.create(e.prototype,r),t.prototype.constructor=t,Object.defineProperty(t,"super",{value:e.prototype}),n&&Object.assign(t.prototype,n)},Sa=(t,e,n,r)=>{let s,i,o;const a={};if(e=e||{},t==null)return e;do{for(s=Object.getOwnPropertyNames(t),i=s.length;i-- >0;)o=s[i],(!r||r(o,t,e))&&!a[o]&&(e[o]=t[o],a[o]=!0);t=n!==!1&&ur(t)}while(t&&(!n||n(t,e))&&t!==Object.prototype);return e},ka=(t,e,n)=>{t=String(t),(n===void 0||n>t.length)&&(n=t.length),n-=e.length;const r=t.indexOf(e,n);return r!==-1&&r===n},Ta=t=>{if(!t)return null;if(It(t))return t;let e=t.length;if(!ai(e))return null;const n=new Array(e);for(;e-- >0;)n[e]=t[e];return n},$a=(t=>e=>t&&e instanceof t)(typeof Uint8Array<"u"&&ur(Uint8Array)),Ca=(t,e)=>{const r=(t&&t[Symbol.iterator]).call(t);let s;for(;(s=r.next())&&!s.done;){const i=s.value;e.call(t,i[0],i[1])}},Aa=(t,e)=>{let n;const r=[];for(;(n=t.exec(e))!==null;)r.push(n);return r},Oa=_e("HTMLFormElement"),Na=t=>t.toLowerCase().replace(/[_-\s]([a-z\d])(\w*)/g,function(n,r,s){return r.toUpperCase()+s}),Qr=(({hasOwnProperty:t})=>(e,n)=>t.call(e,n))(Object.prototype),Ra=_e("RegExp"),ci=(t,e)=>{const n=Object.getOwnPropertyDescriptors(t),r={};hn(n,(s,i)=>{e(s,i,t)!==!1&&(r[i]=s)}),Object.defineProperties(t,r)},Da=t=>{ci(t,(e,n)=>{const r=t[n];if(!!Ze(r)){if(e.enumerable=!1,"writable"in e){e.writable=!1;return}e.set||(e.set=()=>{throw Error("Can not read-only method '"+n+"'")})}})},Pa=(t,e)=>{const n={},r=s=>{s.forEach(i=>{n[i]=!0})};return It(t)?r(t):r(String(t).split(e)),n},La=()=>{},Ma=(t,e)=>(t=+t,Number.isFinite(t)?t:e),f={isArray:It,isArrayBuffer:oi,isBuffer:ua,isFormData:ya,isArrayBufferView:da,isString:fa,isNumber:ai,isBoolean:ha,isObject:li,isPlainObject:zt,isUndefined:Gn,isDate:ga,isFile:ma,isBlob:pa,isRegExp:Ra,isFunction:Ze,isStream:va,isURLSearchParams:_a,isTypedArray:$a,isFileList:ba,forEach:hn,merge:Kn,extend:xa,trim:wa,stripBOM:Ea,inherits:Ia,toFlatObject:Sa,kindOf:dr,kindOfTest:_e,endsWith:ka,toArray:Ta,forEachEntry:Ca,matchAll:Aa,isHTMLForm:Oa,hasOwnProperty:Qr,hasOwnProp:Qr,reduceDescriptors:ci,freezeMethods:Da,toObjectSet:Pa,toCamelCase:Na,noop:La,toFiniteNumber:Ma};function $(t,e,n,r,s){Error.call(this),Error.captureStackTrace?Error.captureStackTrace(this,this.constructor):this.stack=new Error().stack,this.message=t,this.name="AxiosError",e&&(this.code=e),n&&(this.config=n),r&&(this.request=r),s&&(this.response=s)}f.inherits($,Error,{toJSON:function(){return{message:this.message,name:this.name,description:this.description,number:this.number,fileName:this.fileName,lineNumber:this.lineNumber,columnNumber:this.columnNumber,stack:this.stack,config:this.config,code:this.code,status:this.response&&this.response.status?this.response.status:null}}});const ui=$.prototype,di={};["ERR_BAD_OPTION_VALUE","ERR_BAD_OPTION","ECONNABORTED","ETIMEDOUT","ERR_NETWORK","ERR_FR_TOO_MANY_REDIRECTS","ERR_DEPRECATED","ERR_BAD_RESPONSE","ERR_BAD_REQUEST","ERR_CANCELED","ERR_NOT_SUPPORT","ERR_INVALID_URL"].forEach(t=>{di[t]={value:t}});Object.defineProperties($,di);Object.defineProperty(ui,"isAxiosError",{value:!0});$.from=(t,e,n,r,s,i)=>{const o=Object.create(ui);return f.toFlatObject(t,o,function(c){return c!==Error.prototype},a=>a!=="isAxiosError"),$.call(o,t.message,e,n,r,s),o.cause=t,o.name=t.name,i&&Object.assign(o,i),o};var Ua=typeof self=="object"?self.FormData:window.FormData;function Xn(t){return f.isPlainObject(t)||f.isArray(t)}function fi(t){return f.endsWith(t,"[]")?t.slice(0,-2):t}function Zr(t,e,n){return t?t.concat(e).map(function(s,i){return s=fi(s),!n&&i?"["+s+"]":s}).join(n?".":""):e}function ja(t){return f.isArray(t)&&!t.some(Xn)}const Fa=f.toFlatObject(f,{},null,function(e){return/^is[A-Z]/.test(e)});function Ba(t){return t&&f.isFunction(t.append)&&t[Symbol.toStringTag]==="FormData"&&t[Symbol.iterator]}function gn(t,e,n){if(!f.isObject(t))throw new TypeError("target must be an object");e=e||new(Ua||FormData),n=f.toFlatObject(n,{metaTokens:!0,dots:!1,indexes:!1},!1,function(m,x){return!f.isUndefined(x[m])});const r=n.metaTokens,s=n.visitor||u,i=n.dots,o=n.indexes,c=(n.Blob||typeof Blob<"u"&&Blob)&&Ba(e);if(!f.isFunction(s))throw new TypeError("visitor must be a function");function l(g){if(g===null)return"";if(f.isDate(g))return g.toISOString();if(!c&&f.isBlob(g))throw new $("Blob is not supported. Use a Buffer instead.");return f.isArrayBuffer(g)||f.isTypedArray(g)?c&&typeof Blob=="function"?new Blob([g]):Buffer.from(g):g}function u(g,m,x){let _=g;if(g&&!x&&typeof g=="object"){if(f.endsWith(m,"{}"))m=r?m:m.slice(0,-2),g=JSON.stringify(g);else if(f.isArray(g)&&ja(g)||f.isFileList(g)||f.endsWith(m,"[]")&&(_=f.toArray(g)))return m=fi(m),_.forEach(function(T,O){!(f.isUndefined(T)||T===null)&&e.append(o===!0?Zr([m],O,i):o===null?m:m+"[]",l(T))}),!1}return Xn(g)?!0:(e.append(Zr(x,m,i),l(g)),!1)}const p=[],v=Object.assign(Fa,{defaultVisitor:u,convertValue:l,isVisitable:Xn});function b(g,m){if(!f.isUndefined(g)){if(p.indexOf(g)!==-1)throw Error("Circular reference detected in "+m.join("."));p.push(g),f.forEach(g,function(_,S){(!(f.isUndefined(_)||_===null)&&s.call(e,_,f.isString(S)?S.trim():S,m,v))===!0&&b(_,m?m.concat(S):[S])}),p.pop()}}if(!f.isObject(t))throw new TypeError("data must be an object");return b(t),e}function es(t){const e={"!":"%21","'":"%27","(":"%28",")":"%29","~":"%7E","%20":"+","%00":"\0"};return encodeURIComponent(t).replace(/[!'()~]|%20|%00/g,function(r){return e[r]})}function fr(t,e){this._pairs=[],t&&gn(t,this,e)}const hi=fr.prototype;hi.append=function(e,n){this._pairs.push([e,n])};hi.toString=function(e){const n=e?function(r){return e.call(this,r,es)}:es;return this._pairs.map(function(s){return n(s[0])+"="+n(s[1])},"").join("&")};function Ha(t){return encodeURIComponent(t).replace(/%3A/gi,":").replace(/%24/g,"$").replace(/%2C/gi,",").replace(/%20/g,"+").replace(/%5B/gi,"[").replace(/%5D/gi,"]")}function gi(t,e,n){if(!e)return t;const r=n&&n.encode||Ha,s=n&&n.serialize;let i;if(s?i=s(e,n):i=f.isURLSearchParams(e)?e.toString():new fr(e,n).toString(r),i){const o=t.indexOf("#");o!==-1&&(t=t.slice(0,o)),t+=(t.indexOf("?")===-1?"?":"&")+i}return t}class ts{constructor(){this.handlers=[]}use(e,n,r){return this.handlers.push({fulfilled:e,rejected:n,synchronous:r?r.synchronous:!1,runWhen:r?r.runWhen:null}),this.handlers.length-1}eject(e){this.handlers[e]&&(this.handlers[e]=null)}clear(){this.handlers&&(this.handlers=[])}forEach(e){f.forEach(this.handlers,function(r){r!==null&&e(r)})}}const mi={silentJSONParsing:!0,forcedJSONParsing:!0,clarifyTimeoutError:!1},za=typeof URLSearchParams<"u"?URLSearchParams:fr,Va=FormData,Wa=(()=>{let t;return typeof navigator<"u"&&((t=navigator.product)==="ReactNative"||t==="NativeScript"||t==="NS")?!1:typeof window<"u"&&typeof document<"u"})(),pe={isBrowser:!0,classes:{URLSearchParams:za,FormData:Va,Blob},isStandardBrowserEnv:Wa,protocols:["http","https","file","blob","url","data"]};function Ja(t,e){return gn(t,new pe.classes.URLSearchParams,Object.assign({visitor:function(n,r,s,i){return pe.isNode&&f.isBuffer(n)?(this.append(r,n.toString("base64")),!1):i.defaultVisitor.apply(this,arguments)}},e))}function qa(t){return f.matchAll(/\w+|\[(\w*)]/g,t).map(e=>e[0]==="[]"?"":e[1]||e[0])}function Ga(t){const e={},n=Object.keys(t);let r;const s=n.length;let i;for(r=0;r<s;r++)i=n[r],e[i]=t[i];return e}function pi(t){function e(n,r,s,i){let o=n[i++];const a=Number.isFinite(+o),c=i>=n.length;return o=!o&&f.isArray(s)?s.length:o,c?(f.hasOwnProp(s,o)?s[o]=[s[o],r]:s[o]=r,!a):((!s[o]||!f.isObject(s[o]))&&(s[o]=[]),e(n,r,s[o],i)&&f.isArray(s[o])&&(s[o]=Ga(s[o])),!a)}if(f.isFormData(t)&&f.isFunction(t.entries)){const n={};return f.forEachEntry(t,(r,s)=>{e(qa(r),s,n,0)}),n}return null}function Ka(t,e,n){const r=n.config.validateStatus;!n.status||!r||r(n.status)?t(n):e(new $("Request failed with status code "+n.status,[$.ERR_BAD_REQUEST,$.ERR_BAD_RESPONSE][Math.floor(n.status/100)-4],n.config,n.request,n))}const Xa=pe.isStandardBrowserEnv?function(){return{write:function(n,r,s,i,o,a){const c=[];c.push(n+"="+encodeURIComponent(r)),f.isNumber(s)&&c.push("expires="+new Date(s).toGMTString()),f.isString(i)&&c.push("path="+i),f.isString(o)&&c.push("domain="+o),a===!0&&c.push("secure"),document.cookie=c.join("; ")},read:function(n){const r=document.cookie.match(new RegExp("(^|;\\s*)("+n+")=([^;]*)"));return r?decodeURIComponent(r[3]):null},remove:function(n){this.write(n,"",Date.now()-864e5)}}}():function(){return{write:function(){},read:function(){return null},remove:function(){}}}();function Ya(t){return/^([a-z][a-z\d+\-.]*:)?\/\//i.test(t)}function Qa(t,e){return e?t.replace(/\/+$/,"")+"/"+e.replace(/^\/+/,""):t}function bi(t,e){return t&&!Ya(e)?Qa(t,e):e}const Za=pe.isStandardBrowserEnv?function(){const e=/(msie|trident)/i.test(navigator.userAgent),n=document.createElement("a");let r;function s(i){let o=i;return e&&(n.setAttribute("href",o),o=n.href),n.setAttribute("href",o),{href:n.href,protocol:n.protocol?n.protocol.replace(/:$/,""):"",host:n.host,search:n.search?n.search.replace(/^\?/,""):"",hash:n.hash?n.hash.replace(/^#/,""):"",hostname:n.hostname,port:n.port,pathname:n.pathname.charAt(0)==="/"?n.pathname:"/"+n.pathname}}return r=s(window.location.href),function(o){const a=f.isString(o)?s(o):o;return a.protocol===r.protocol&&a.host===r.host}}():function(){return function(){return!0}}();function St(t,e,n){$.call(this,t??"canceled",$.ERR_CANCELED,e,n),this.name="CanceledError"}f.inherits(St,$,{__CANCEL__:!0});function el(t){const e=/^([-+\w]{1,25})(:?\/\/|:)/.exec(t);return e&&e[1]||""}const tl=f.toObjectSet(["age","authorization","content-length","content-type","etag","expires","from","host","if-modified-since","if-unmodified-since","last-modified","location","max-forwards","proxy-authorization","referer","retry-after","user-agent"]),nl=t=>{const e={};let n,r,s;return t&&t.split(`
`).forEach(function(o){s=o.indexOf(":"),n=o.substring(0,s).trim().toLowerCase(),r=o.substring(s+1).trim(),!(!n||e[n]&&tl[n])&&(n==="set-cookie"?e[n]?e[n].push(r):e[n]=[r]:e[n]=e[n]?e[n]+", "+r:r)}),e},ns=Symbol("internals"),vi=Symbol("defaults");function ut(t){return t&&String(t).trim().toLowerCase()}function Vt(t){return t===!1||t==null?t:f.isArray(t)?t.map(Vt):String(t)}function rl(t){const e=Object.create(null),n=/([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;let r;for(;r=n.exec(t);)e[r[1]]=r[2];return e}function rs(t,e,n,r){if(f.isFunction(r))return r.call(this,e,n);if(!!f.isString(e)){if(f.isString(r))return e.indexOf(r)!==-1;if(f.isRegExp(r))return r.test(e)}}function sl(t){return t.trim().toLowerCase().replace(/([a-z\d])(\w*)/g,(e,n,r)=>n.toUpperCase()+r)}function il(t,e){const n=f.toCamelCase(" "+e);["get","set","has"].forEach(r=>{Object.defineProperty(t,r+n,{value:function(s,i,o){return this[r].call(this,e,s,i,o)},configurable:!0})})}function lt(t,e){e=e.toLowerCase();const n=Object.keys(t);let r=n.length,s;for(;r-- >0;)if(s=n[r],e===s.toLowerCase())return s;return null}function ee(t,e){t&&this.set(t),this[vi]=e||null}Object.assign(ee.prototype,{set:function(t,e,n){const r=this;function s(i,o,a){const c=ut(o);if(!c)throw new Error("header name must be a non-empty string");const l=lt(r,c);l&&a!==!0&&(r[l]===!1||a===!1)||(r[l||o]=Vt(i))}return f.isPlainObject(t)?f.forEach(t,(i,o)=>{s(i,o,e)}):s(e,t,n),this},get:function(t,e){if(t=ut(t),!t)return;const n=lt(this,t);if(n){const r=this[n];if(!e)return r;if(e===!0)return rl(r);if(f.isFunction(e))return e.call(this,r,n);if(f.isRegExp(e))return e.exec(r);throw new TypeError("parser must be boolean|regexp|function")}},has:function(t,e){if(t=ut(t),t){const n=lt(this,t);return!!(n&&(!e||rs(this,this[n],n,e)))}return!1},delete:function(t,e){const n=this;let r=!1;function s(i){if(i=ut(i),i){const o=lt(n,i);o&&(!e||rs(n,n[o],o,e))&&(delete n[o],r=!0)}}return f.isArray(t)?t.forEach(s):s(t),r},clear:function(){return Object.keys(this).forEach(this.delete.bind(this))},normalize:function(t){const e=this,n={};return f.forEach(this,(r,s)=>{const i=lt(n,s);if(i){e[i]=Vt(r),delete e[s];return}const o=t?sl(s):String(s).trim();o!==s&&delete e[s],e[o]=Vt(r),n[o]=!0}),this},toJSON:function(t){const e=Object.create(null);return f.forEach(Object.assign({},this[vi]||null,this),(n,r)=>{n==null||n===!1||(e[r]=t&&f.isArray(n)?n.join(", "):n)}),e}});Object.assign(ee,{from:function(t){return f.isString(t)?new this(nl(t)):t instanceof this?t:new this(t)},accessor:function(t){const n=(this[ns]=this[ns]={accessors:{}}).accessors,r=this.prototype;function s(i){const o=ut(i);n[o]||(il(r,i),n[o]=!0)}return f.isArray(t)?t.forEach(s):s(t),this}});ee.accessor(["Content-Type","Content-Length","Accept","Accept-Encoding","User-Agent"]);f.freezeMethods(ee.prototype);f.freezeMethods(ee);function ol(t,e){t=t||10;const n=new Array(t),r=new Array(t);let s=0,i=0,o;return e=e!==void 0?e:1e3,function(c){const l=Date.now(),u=r[i];o||(o=l),n[s]=c,r[s]=l;let p=i,v=0;for(;p!==s;)v+=n[p++],p=p%t;if(s=(s+1)%t,s===i&&(i=(i+1)%t),l-o<e)return;const b=u&&l-u;return b?Math.round(v*1e3/b):void 0}}function ss(t,e){let n=0;const r=ol(50,250);return s=>{const i=s.loaded,o=s.lengthComputable?s.total:void 0,a=i-n,c=r(a),l=i<=o;n=i;const u={loaded:i,total:o,progress:o?i/o:void 0,bytes:a,rate:c||void 0,estimated:c&&o&&l?(o-i)/c:void 0};u[e?"download":"upload"]=!0,t(u)}}function is(t){return new Promise(function(n,r){let s=t.data;const i=ee.from(t.headers).normalize(),o=t.responseType;let a;function c(){t.cancelToken&&t.cancelToken.unsubscribe(a),t.signal&&t.signal.removeEventListener("abort",a)}f.isFormData(s)&&pe.isStandardBrowserEnv&&i.setContentType(!1);let l=new XMLHttpRequest;if(t.auth){const b=t.auth.username||"",g=t.auth.password?unescape(encodeURIComponent(t.auth.password)):"";i.set("Authorization","Basic "+btoa(b+":"+g))}const u=bi(t.baseURL,t.url);l.open(t.method.toUpperCase(),gi(u,t.params,t.paramsSerializer),!0),l.timeout=t.timeout;function p(){if(!l)return;const b=ee.from("getAllResponseHeaders"in l&&l.getAllResponseHeaders()),m={data:!o||o==="text"||o==="json"?l.responseText:l.response,status:l.status,statusText:l.statusText,headers:b,config:t,request:l};Ka(function(_){n(_),c()},function(_){r(_),c()},m),l=null}if("onloadend"in l?l.onloadend=p:l.onreadystatechange=function(){!l||l.readyState!==4||l.status===0&&!(l.responseURL&&l.responseURL.indexOf("file:")===0)||setTimeout(p)},l.onabort=function(){!l||(r(new $("Request aborted",$.ECONNABORTED,t,l)),l=null)},l.onerror=function(){r(new $("Network Error",$.ERR_NETWORK,t,l)),l=null},l.ontimeout=function(){let g=t.timeout?"timeout of "+t.timeout+"ms exceeded":"timeout exceeded";const m=t.transitional||mi;t.timeoutErrorMessage&&(g=t.timeoutErrorMessage),r(new $(g,m.clarifyTimeoutError?$.ETIMEDOUT:$.ECONNABORTED,t,l)),l=null},pe.isStandardBrowserEnv){const b=(t.withCredentials||Za(u))&&t.xsrfCookieName&&Xa.read(t.xsrfCookieName);b&&i.set(t.xsrfHeaderName,b)}s===void 0&&i.setContentType(null),"setRequestHeader"in l&&f.forEach(i.toJSON(),function(g,m){l.setRequestHeader(m,g)}),f.isUndefined(t.withCredentials)||(l.withCredentials=!!t.withCredentials),o&&o!=="json"&&(l.responseType=t.responseType),typeof t.onDownloadProgress=="function"&&l.addEventListener("progress",ss(t.onDownloadProgress,!0)),typeof t.onUploadProgress=="function"&&l.upload&&l.upload.addEventListener("progress",ss(t.onUploadProgress)),(t.cancelToken||t.signal)&&(a=b=>{!l||(r(!b||b.type?new St(null,t,l):b),l.abort(),l=null)},t.cancelToken&&t.cancelToken.subscribe(a),t.signal&&(t.signal.aborted?a():t.signal.addEventListener("abort",a)));const v=el(u);if(v&&pe.protocols.indexOf(v)===-1){r(new $("Unsupported protocol "+v+":",$.ERR_BAD_REQUEST,t));return}l.send(s||null)})}const os={http:is,xhr:is},as={getAdapter:t=>{if(f.isString(t)){const e=os[t];if(!t)throw Error(f.hasOwnProp(t)?`Adapter '${t}' is not available in the build`:`Can not resolve adapter '${t}'`);return e}if(!f.isFunction(t))throw new TypeError("adapter is not a function");return t},adapters:os},al={"Content-Type":"application/x-www-form-urlencoded"};function ll(){let t;return typeof XMLHttpRequest<"u"?t=as.getAdapter("xhr"):typeof process<"u"&&f.kindOf(process)==="process"&&(t=as.getAdapter("http")),t}function cl(t,e,n){if(f.isString(t))try{return(e||JSON.parse)(t),f.trim(t)}catch(r){if(r.name!=="SyntaxError")throw r}return(n||JSON.stringify)(t)}const et={transitional:mi,adapter:ll(),transformRequest:[function(e,n){const r=n.getContentType()||"",s=r.indexOf("application/json")>-1,i=f.isObject(e);if(i&&f.isHTMLForm(e)&&(e=new FormData(e)),f.isFormData(e))return s&&s?JSON.stringify(pi(e)):e;if(f.isArrayBuffer(e)||f.isBuffer(e)||f.isStream(e)||f.isFile(e)||f.isBlob(e))return e;if(f.isArrayBufferView(e))return e.buffer;if(f.isURLSearchParams(e))return n.setContentType("application/x-www-form-urlencoded;charset=utf-8",!1),e.toString();let a;if(i){if(r.indexOf("application/x-www-form-urlencoded")>-1)return Ja(e,this.formSerializer).toString();if((a=f.isFileList(e))||r.indexOf("multipart/form-data")>-1){const c=this.env&&this.env.FormData;return gn(a?{"files[]":e}:e,c&&new c,this.formSerializer)}}return i||s?(n.setContentType("application/json",!1),cl(e)):e}],transformResponse:[function(e){const n=this.transitional||et.transitional,r=n&&n.forcedJSONParsing,s=this.responseType==="json";if(e&&f.isString(e)&&(r&&!this.responseType||s)){const o=!(n&&n.silentJSONParsing)&&s;try{return JSON.parse(e)}catch(a){if(o)throw a.name==="SyntaxError"?$.from(a,$.ERR_BAD_RESPONSE,this,null,this.response):a}}return e}],timeout:0,xsrfCookieName:"XSRF-TOKEN",xsrfHeaderName:"X-XSRF-TOKEN",maxContentLength:-1,maxBodyLength:-1,env:{FormData:pe.classes.FormData,Blob:pe.classes.Blob},validateStatus:function(e){return e>=200&&e<300},headers:{common:{Accept:"application/json, text/plain, */*"}}};f.forEach(["delete","get","head"],function(e){et.headers[e]={}});f.forEach(["post","put","patch"],function(e){et.headers[e]=f.merge(al)});function Pn(t,e){const n=this||et,r=e||n,s=ee.from(r.headers);let i=r.data;return f.forEach(t,function(a){i=a.call(n,i,s.normalize(),e?e.status:void 0)}),s.normalize(),i}function yi(t){return!!(t&&t.__CANCEL__)}function Ln(t){if(t.cancelToken&&t.cancelToken.throwIfRequested(),t.signal&&t.signal.aborted)throw new St}function ls(t){return Ln(t),t.headers=ee.from(t.headers),t.data=Pn.call(t,t.transformRequest),(t.adapter||et.adapter)(t).then(function(r){return Ln(t),r.data=Pn.call(t,t.transformResponse,r),r.headers=ee.from(r.headers),r},function(r){return yi(r)||(Ln(t),r&&r.response&&(r.response.data=Pn.call(t,t.transformResponse,r.response),r.response.headers=ee.from(r.response.headers))),Promise.reject(r)})}function mt(t,e){e=e||{};const n={};function r(l,u){return f.isPlainObject(l)&&f.isPlainObject(u)?f.merge(l,u):f.isPlainObject(u)?f.merge({},u):f.isArray(u)?u.slice():u}function s(l){if(f.isUndefined(e[l])){if(!f.isUndefined(t[l]))return r(void 0,t[l])}else return r(t[l],e[l])}function i(l){if(!f.isUndefined(e[l]))return r(void 0,e[l])}function o(l){if(f.isUndefined(e[l])){if(!f.isUndefined(t[l]))return r(void 0,t[l])}else return r(void 0,e[l])}function a(l){if(l in e)return r(t[l],e[l]);if(l in t)return r(void 0,t[l])}const c={url:i,method:i,data:i,baseURL:o,transformRequest:o,transformResponse:o,paramsSerializer:o,timeout:o,timeoutMessage:o,withCredentials:o,adapter:o,responseType:o,xsrfCookieName:o,xsrfHeaderName:o,onUploadProgress:o,onDownloadProgress:o,decompress:o,maxContentLength:o,maxBodyLength:o,beforeRedirect:o,transport:o,httpAgent:o,httpsAgent:o,cancelToken:o,socketPath:o,responseEncoding:o,validateStatus:a};return f.forEach(Object.keys(t).concat(Object.keys(e)),function(u){const p=c[u]||s,v=p(u);f.isUndefined(v)&&p!==a||(n[u]=v)}),n}const _i="1.1.3",hr={};["object","boolean","number","function","string","symbol"].forEach((t,e)=>{hr[t]=function(r){return typeof r===t||"a"+(e<1?"n ":" ")+t}});const cs={};hr.transitional=function(e,n,r){function s(i,o){return"[Axios v"+_i+"] Transitional option '"+i+"'"+o+(r?". "+r:"")}return(i,o,a)=>{if(e===!1)throw new $(s(o," has been removed"+(n?" in "+n:"")),$.ERR_DEPRECATED);return n&&!cs[o]&&(cs[o]=!0,console.warn(s(o," has been deprecated since v"+n+" and will be removed in the near future"))),e?e(i,o,a):!0}};function ul(t,e,n){if(typeof t!="object")throw new $("options must be an object",$.ERR_BAD_OPTION_VALUE);const r=Object.keys(t);let s=r.length;for(;s-- >0;){const i=r[s],o=e[i];if(o){const a=t[i],c=a===void 0||o(a,i,t);if(c!==!0)throw new $("option "+i+" must be "+c,$.ERR_BAD_OPTION_VALUE);continue}if(n!==!0)throw new $("Unknown option "+i,$.ERR_BAD_OPTION)}}const Yn={assertOptions:ul,validators:hr},xe=Yn.validators;class je{constructor(e){this.defaults=e,this.interceptors={request:new ts,response:new ts}}request(e,n){typeof e=="string"?(n=n||{},n.url=e):n=e||{},n=mt(this.defaults,n);const{transitional:r,paramsSerializer:s}=n;r!==void 0&&Yn.assertOptions(r,{silentJSONParsing:xe.transitional(xe.boolean),forcedJSONParsing:xe.transitional(xe.boolean),clarifyTimeoutError:xe.transitional(xe.boolean)},!1),s!==void 0&&Yn.assertOptions(s,{encode:xe.function,serialize:xe.function},!0),n.method=(n.method||this.defaults.method||"get").toLowerCase();const i=n.headers&&f.merge(n.headers.common,n.headers[n.method]);i&&f.forEach(["delete","get","head","post","put","patch","common"],function(g){delete n.headers[g]}),n.headers=new ee(n.headers,i);const o=[];let a=!0;this.interceptors.request.forEach(function(g){typeof g.runWhen=="function"&&g.runWhen(n)===!1||(a=a&&g.synchronous,o.unshift(g.fulfilled,g.rejected))});const c=[];this.interceptors.response.forEach(function(g){c.push(g.fulfilled,g.rejected)});let l,u=0,p;if(!a){const b=[ls.bind(this),void 0];for(b.unshift.apply(b,o),b.push.apply(b,c),p=b.length,l=Promise.resolve(n);u<p;)l=l.then(b[u++],b[u++]);return l}p=o.length;let v=n;for(u=0;u<p;){const b=o[u++],g=o[u++];try{v=b(v)}catch(m){g.call(this,m);break}}try{l=ls.call(this,v)}catch(b){return Promise.reject(b)}for(u=0,p=c.length;u<p;)l=l.then(c[u++],c[u++]);return l}getUri(e){e=mt(this.defaults,e);const n=bi(e.baseURL,e.url);return gi(n,e.params,e.paramsSerializer)}}f.forEach(["delete","get","head","options"],function(e){je.prototype[e]=function(n,r){return this.request(mt(r||{},{method:e,url:n,data:(r||{}).data}))}});f.forEach(["post","put","patch"],function(e){function n(r){return function(i,o,a){return this.request(mt(a||{},{method:e,headers:r?{"Content-Type":"multipart/form-data"}:{},url:i,data:o}))}}je.prototype[e]=n(),je.prototype[e+"Form"]=n(!0)});class gr{constructor(e){if(typeof e!="function")throw new TypeError("executor must be a function.");let n;this.promise=new Promise(function(i){n=i});const r=this;this.promise.then(s=>{if(!r._listeners)return;let i=r._listeners.length;for(;i-- >0;)r._listeners[i](s);r._listeners=null}),this.promise.then=s=>{let i;const o=new Promise(a=>{r.subscribe(a),i=a}).then(s);return o.cancel=function(){r.unsubscribe(i)},o},e(function(i,o,a){r.reason||(r.reason=new St(i,o,a),n(r.reason))})}throwIfRequested(){if(this.reason)throw this.reason}subscribe(e){if(this.reason){e(this.reason);return}this._listeners?this._listeners.push(e):this._listeners=[e]}unsubscribe(e){if(!this._listeners)return;const n=this._listeners.indexOf(e);n!==-1&&this._listeners.splice(n,1)}static source(){let e;return{token:new gr(function(s){e=s}),cancel:e}}}function dl(t){return function(n){return t.apply(null,n)}}function fl(t){return f.isObject(t)&&t.isAxiosError===!0}function wi(t){const e=new je(t),n=si(je.prototype.request,e);return f.extend(n,je.prototype,e,{allOwnKeys:!0}),f.extend(n,e,null,{allOwnKeys:!0}),n.create=function(s){return wi(mt(t,s))},n}const M=wi(et);M.Axios=je;M.CanceledError=St;M.CancelToken=gr;M.isCancel=yi;M.VERSION=_i;M.toFormData=gn;M.AxiosError=$;M.Cancel=M.CanceledError;M.all=function(e){return Promise.all(e)};M.spread=dl;M.isAxiosError=fl;M.formToJSON=t=>pi(f.isHTMLForm(t)?new FormData(t):t);const us="http://0.0.0.0:3000",hl="http://0.0.0.0:8080",ds=window.location.origin;function gl(){let t;ds==us?t=hl:t="";const[e,n]=y(t),r=ds==us;return{serverUrl:e,setServerUrl:n,withCredentials:r}}const ne=Y(gl);function ml(){const[t,e]=y("submit");return{tabName:t,setTabName:e}}const tt=Y(ml),pl=w('<a id="tabhead_{props.tabName}" href="#" class="tabhead"></a>');function mn(t){const{tabName:e,setTabName:n}=tt;return(()=>{const r=pl.cloneNode(!0);return r.$$click=()=>n(t.tabName),d(r,()=>t.svg,null),d(r,()=>t.title,null),k(()=>r.classList.toggle("selected",e()==t.tabName)),r})()}A(["click"]);const bl=w('<svg fill="currentColor" stroke-width="0" xmlns="http://www.w3.org/2000/svg"></svg>'),vl=w("<title></title>");function Q(t,e){return(()=>{const n=bl.cloneNode(!0);return qr(n,()=>t.a,!0,!0),qr(n,e,!0,!0),d(n,()=>oa,null),d(n,(()=>{const r=Zo(()=>!!e.title,!0);return()=>r()&&(()=>{const s=vl.cloneNode(!0);return d(s,()=>e.title),s})()})(),null),k(r=>{const s=t.a.stroke,i={...e.style,overflow:"visible",color:e.color||"currentColor"},o=e.size||"1em",a=e.size||"1em",c=t.c;return s!==r._v$&&J(n,"stroke",r._v$=s),r._v$2=ri(n,i,r._v$2),o!==r._v$3&&J(n,"height",r._v$3=o),a!==r._v$4&&J(n,"width",r._v$4=a),c!==r._v$5&&(n.innerHTML=r._v$5=c),r},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0}),n})()}function yl(t){return Q({a:{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",viewBox:"0 0 24 24"},c:'<path stroke="none" d="M0 0h24v24H0z"/><path d="M9 13L5 9l4-4M5 9h11a4 4 0 010 8h-1"/>'},t)}function _l(t){return Q({a:{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",viewBox:"0 0 24 24"},c:'<path stroke="none" d="M0 0h24v24H0z"/><path d="M14 3v4a1 1 0 001 1h4"/><path d="M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2zM12 11v6"/><path d="M9.5 13.5L12 11l2.5 2.5"/>'},t)}function wl(){const t=h(_l,{class:"tabheadicon",color:"rgb(156 163 175)"});return h(mn,{tabName:"submit",title:"Submit",svg:t})}function xl(t){return Q({a:{viewBox:"0 0 1024 1024"},c:'<path d="M518.3 459a8 8 0 00-12.6 0l-112 141.7a7.98 7.98 0 006.3 12.9h73.9V856c0 4.4 3.6 8 8 8h60c4.4 0 8-3.6 8-8V613.7H624c6.7 0 10.4-7.7 6.3-12.9L518.3 459z"/><path d="M811.4 366.7C765.6 245.9 648.9 160 512.2 160S258.8 245.8 213 366.6C127.3 389.1 64 467.2 64 560c0 110.5 89.5 200 199.9 200H304c4.4 0 8-3.6 8-8v-60c0-4.4-3.6-8-8-8h-40.1c-33.7 0-65.4-13.4-89-37.7-23.5-24.2-36-56.8-34.9-90.6.9-26.4 9.9-51.2 26.2-72.1 16.7-21.3 40.1-36.8 66.1-43.7l37.9-9.9 13.9-36.6c8.6-22.8 20.6-44.1 35.7-63.4a245.6 245.6 0 0152.4-49.9c41.1-28.9 89.5-44.2 140-44.2s98.9 15.3 140 44.2c19.9 14 37.5 30.8 52.4 49.9 15.1 19.3 27.1 40.7 35.7 63.4l13.8 36.5 37.8 10C846.1 454.5 884 503.8 884 560c0 33.1-12.9 64.3-36.3 87.7a123.07 123.07 0 01-87.6 36.3H720c-4.4 0-8 3.6-8 8v60c0 4.4 3.6 8 8 8h40.1C870.5 760 960 670.5 960 560c0-92.7-63.1-170.7-148.6-193.3z"/>'},t)}function El(t){return Q({a:{viewBox:"0 0 1024 1024"},c:'<path d="M920 760H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0-568H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0 284H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM216 712H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h72.4v20.5h-35.7c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h35.7V838H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4V716c0-2.2-1.8-4-4-4zM100 188h38v120c0 2.2 1.8 4 4 4h40c2.2 0 4-1.8 4-4V152c0-4.4-3.6-8-8-8h-78c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4zm116 240H100c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4h68.4l-70.3 77.7a8.3 8.3 0 00-2.1 5.4V592c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4v-36c0-2.2-1.8-4-4-4h-68.4l70.3-77.7a8.3 8.3 0 002.1-5.4V432c0-2.2-1.8-4-4-4z"/>'},t)}function Il(){const t=h(El,{class:"tabheadicon",color:"rgb(156 163 175)"});return h(mn,{tabName:"jobs",title:"Jobs",svg:t})}const Sl=w('<svg class="tabheadicon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"></path></svg>');function kl(){const t=Sl.cloneNode(!0);return h(mn,{tabName:"system",title:"System",svg:t})}function Tl(t){return Q({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>'},t)}function $l(t){return Q({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>'},t)}function Cl(t){return Q({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>'},t)}function mr(t){return Q({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>'},t)}function Al(t){return Q({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>'},t)}function Ol(t){return Q({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>'},t)}function Nl(t){return Q({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>'},t)}function Rl(t){return Q({a:{fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},c:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>'},t)}function Dl(){const t=h(Rl,{class:"tabheadicon",color:"rgb(156 163 175)"});return h(mn,{tabName:"account",title:"Account",svg:t})}const Pl=w('<div id="verdiv" class="text-xs absolute left-4 bottom-2 text-gray-400"><span class="text-xs">v</span><span class="curverspan text-xs"></span></div>');function Ll(){return Pl.cloneNode(!0)}function Ml(){const[t,e]=y(!1);return{multiuser:t,setMultiuser:e}}const kt=Y(Ml),Ul=w('<div id="sidebar_static" class="md:flex md:w-36 md:flex-col md:fixed md:inset-y-0"><div class="flex-1 flex flex-col min-h-0 border-r border-gray-200"><div class="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto"><div class="flex items-center flex-shrink-0 px-4"><img class="h-16 w-auto" alt="Logo"></div><nav class="mt-5 flex-1 px-2 space-y-1"></nav></div></div></div>'),{serverUrl:jl,setServerUrl:Jg,withCredentials:qg}=ne,{multiuser:Fl,setMultiuser:Gg}=kt;function Bl(){return(()=>{const t=Ul.cloneNode(!0),e=t.firstChild,n=e.firstChild,r=n.firstChild,s=r.firstChild,i=r.nextSibling;return d(i,h(wl,{}),null),d(i,h(Il,{}),null),d(i,h(kl,{}),null),d(i,h(se,{get when(){return Fl()==!0},get children(){return h(Dl,{})}}),null),d(n,h(Ll,{}),null),k(()=>J(s,"src",jl()+"/submit/images/logo_transparent_bw.png")),t})()}function Hl(t){return Q({a:{fill:"currentColor",viewBox:"0 0 16 16"},c:'<path d="M11.42 2l3.428 6-3.428 6H4.58L1.152 8 4.58 2h6.84zM4.58 1a1 1 0 00-.868.504l-3.428 6a1 1 0 000 .992l3.428 6A1 1 0 004.58 15h6.84a1 1 0 00.868-.504l3.429-6a1 1 0 000-.992l-3.429-6A1 1 0 0011.42 1H4.58z"/><path d="M6.848 5.933a2.5 2.5 0 102.5 4.33 2.5 2.5 0 00-2.5-4.33zm-1.78 3.915a3.5 3.5 0 116.061-3.5 3.5 3.5 0 01-6.062 3.5z"/>'},t)}async function xi(t){const{serverUrl:e,setServerUrl:n}=ne;return(await fetch(e()+t)).json()}async function zl(t){}function Vl(){const[t,e]=y({}),[n,r]=y({});function s(c){return c in t()?t()[c]:null}function i(c){var l=t();l[c.name]=c,e(l)}function o(){xi("/store/local").then(function(c){e(c)})}function a(c){return c in n()?n()[c]:(zl(),h(Hl,{}))}return{localModules:t,setLocalModules:e,getLocalModule:s,addLocalModule:i,loadAllModules:o,localModuleLogos:n,setLocalModuleLogos:r,getLocalModuleLogo:a}}const pn=Y(Vl),Wl=w('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function jt(t){function e(){t.setAssembly(t.value),t.setShow(!1)}return(()=>{const n=Wl.cloneNode(!0);return n.$$click=e,d(n,()=>t.title),n})()}A(["click"]);const Jl=w('<div id="assembly-select" class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabindex="-1"><div class="py-1" role="none"></div></div>');function ql(t){return(()=>{const e=Jl.cloneNode(!0),n=e.firstChild;return d(n,h(jt,{value:"auto",title:"Auto",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),d(n,h(jt,{value:"hg38",title:"GRCh38/hg38",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),d(n,h(jt,{value:"hg19",title:"GRCh37/hg19",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),d(n,h(jt,{value:"hg18",title:"GRCh36/hg18",get setAssembly(){return t.setAssembly},get setShow(){return t.setShow}}),null),k(()=>e.classList.toggle("hidden",!t.show)),e})()}const Gl=w('<div id="assembly-select-panel" class="select-div relative inline-block text-left" value=""><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="assembly-select-div" title="Genome assembly">Genome assembly: </button></div></div>');function Kl(t){const[e,n]=y(!1),r={"":"Auto",hg38:"GRCh38/hg38",hg19:"GRCh37/hg19",hg18:"GRCh36/hg18"};function s(i){n(!e())}return(()=>{const i=Gl.cloneNode(!0),o=i.firstChild,a=o.firstChild;return a.firstChild,a.$$click=s,d(a,()=>r[t.assembly],null),d(a,h(mr,{class:"-mr-1 ml-2 h-5 w-5"}),null),d(i,h(ql,{get show(){return e()},get setAssembly(){return t.setAssembly},setShow:n}),null),i})()}A(["click"]);const Xl=w('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function fs(t){function e(){t.setInputFormat(t.value),t.setShow(!1)}return(()=>{const n=Xl.cloneNode(!0);return n.$$click=e,d(n,()=>t.title),n})()}A(["click"]);function Yl(){const[t,e]=y(!1);return{logged:t,setLogged:e}}const Tt=Y(Yl),Ql=w('<div id="input-format-select" class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabindex="-1"><div class="py-1" role="none"></div></div>'),{multiuser:Zl,setMultiuser:Kg}=kt,{logged:ec,setLogged:Xg}=Tt;async function tc(){if(Zl()==!1||ec()==!0)return await xi("/submit/converters")}function nc(t){const[e]=lr(tc);return Et(()=>{var n={"":"Auto"};if(!!e()){for(var r=0;r<e().length;r++)n[e()[r].format]=e()[r].title;t.setInputFormats(n)}}),(()=>{const n=Ql.cloneNode(!0),r=n.firstChild;return d(r,h(fs,{value:"",title:"Auto",get setInputFormat(){return t.setInputFormat},get setShow(){return t.setShow}}),null),d(r,h(Ae,{get each(){return e()},children:function(s){return h(fs,{get value(){return s.format},get title(){return s.title},get setInputFormat(){return t.setInputFormat},get setShow(){return t.setShow}})}}),null),k(()=>n.classList.toggle("hidden",!t.show)),n})()}const rc=w('<div id="input-format-select-panel" class="select-div relative inline-block text-left ml-6" value=""><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="input-format-select-div" title="Format">Format: </button></div></div>');function sc(t){const[e,n]=y(!1),[r,s]=y({"":"Auto"});function i(o){n(!e())}return(()=>{const o=rc.cloneNode(!0),a=o.firstChild,c=a.firstChild;return c.firstChild,c.$$click=i,d(c,()=>r()[t.inputFormat],null),d(c,h(mr,{class:"-mr-1 ml-2 h-5 w-5"}),null),d(o,h(nc,{get show(){return e()},get setInputFormat(){return t.setInputFormat},setInputFormats:s,setShow:n}),null),o})()}A(["click"]);const ic=w('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100"><svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v3.75m-9.303 3.376C1.83 19.126 2.914 21 4.645 21h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 4.88c-.866-1.501-3.032-1.501-3.898 0L2.697 17.626zM12 17.25h.007v.008H12v-.008z"></path></svg></div><div class="mt-3 text-center sm:mt-5"><h3 class="text-lg font-medium leading-6 text-gray-900"></h3><div class="mt-2"><p class="text-sm text-gray-500"></p></div></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:text-sm">Dismiss</button></div></div></div></div></div>');function Ei(t){return(()=>{const e=ic.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.nextSibling,l=c.firstChild,u=l.nextSibling,p=u.firstChild,v=o.nextSibling,b=v.firstChild;return d(l,()=>t.title),d(p,()=>t.text),b.$$click=t.setShowDialog,b.$$clickData=!1,e})()}A(["click"]);const oc=w('<div id="input-upload-list-div" class="w-1/2 flex flex-col justify-center items-center p-2 relative h-full bg-gray-50"><button id="clear_inputfilelist_button" class="text-gray-500 bg-neutral-200 hover:bg-neutral-300 p-1 w-16 rounded-md absolute top-1 left-1" onclick="clearInputUploadList()">Clear</button><div id="input-upload-list-wrapper" class="flex w-full overflow-auto h-[13rem] absolute bottom-1 bg-gray-50"><div id="input-upload-list" class="h-full overflow-auto"></div></div></div>'),ac=w('<label id="input-drop-area" for="input-file" class="flex items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-md cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600"><div id="input-drop-box" class="w-1/2"><div class="flex flex-col items-center justify-center pt-5 pb-6"><p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop input files</p><p class="text-gray-500 mb-2"> or </p><button class="mb-2 text-sm text-gray-500 dark:text-gray-400 bg-neutral-200 hover:bg-neutral-300 p-2 rounded-md">Manually enter variants</button></div><input type="file" class="hidden" name="input-file" id="input-file" multiple></div></label>'),lc=w('<span class="pl-2 text-sm text-gray-600 hover:text-gray-400 cursor-pointer round-md inline-block w-5/6" title="Click to remove"></span>');function cc(t){const[e,n]=y(!1),[r,s]=y({title:"Problem",text:"?"});Et(function(){});function i(a,c){c.preventDefault();for(var l=0;l<t.inputDataDrop.length;l++)if(t.inputDataDrop[l].name==a){t.setInputDataDrop([...t.inputDataDrop.slice(0,l),...t.inputDataDrop.slice(l+1,t.inputDataDrop.length)]);break}}function o(a){const c=a.target.files;for(var l=0;l<c.length;l++)if(c[l].name.indexOf(" ")>=0){s({title:"Problem",text:"Input file names should not have space."}),n(!0);break}t.setInputDataDrop([...t.inputDataDrop,...c])}return(()=>{const a=ac.cloneNode(!0),c=a.firstChild,l=c.firstChild,u=l.firstChild,p=u.nextSibling,v=p.nextSibling,b=l.nextSibling;return d(a,h(se,{get when(){return t.inputDataDrop.length>0},get children(){const g=oc.cloneNode(!0),m=g.firstChild,x=m.nextSibling,_=x.firstChild;return d(_,h(Ae,{get each(){return t.inputDataDrop},children:S=>(()=>{const T=lc.cloneNode(!0);return T.$$click=i,T.$$clickData=S.name,d(T,()=>S.name),T})()})),g}}),c),d(l,h(xl,{class:"w-10 h-10",color:"#9ca3af"}),u),v.$$click=t.setInputMode,v.$$clickData="paste",b.addEventListener("change",o),d(a,h(ca,{get children(){return h(se,{get when(){return e()},get children(){return h(Ei,{get title(){return r().title},get text(){return r().text},setShowErrorDialog:n})}})}}),null),a})()}A(["click"]);const uc=w(`<div id="input-paste-area" class="relative w-full h-64 border-2 border-gray-300 border-dashed rounded-md"><textarea id="input-text" class="font-mono border-0 bg-gray-50 text-gray-600 p-4 resize-none w-full h-full" placeholder="Copy and paste or type input variants. VCF is supported. A quick and simple format is space-delimited one:

chr1 9384934 + A T

which is chromosome, position, strand, a reference allele, and an alternate allele.

Alternatively, paths to input files in the server can be used as well. For example,

/mnt/oakvar/input/sample/sample_1.vcf
"></textarea><div class="top-2 right-3 absolute cursor-pointer" title="Click to go back"></div><div class="absolute bottom-1 right-1 text-gray-400 text-sm"><button value="cravat" class="p-1 text-gray-500 bg-neutral-200 hover:bg-neutral-300">Try an example</button></div></div>`);function dc(t){function e(r){const{serverUrl:s,setServerUrl:i}=ne;t.setAssembly("hg38"),t.setInputFormat("vcf"),fetch(`${s()}/submit/input-examples/${t.inputFormat}.${t.assembly}.txt`).then(o=>o.text()).then(o=>{t.changeInputData("paste",o)})}function n(r){t.changeInputData("paste",r.target.value)}return(()=>{const r=uc.cloneNode(!0),s=r.firstChild,i=s.nextSibling,o=i.nextSibling,a=o.firstChild;return s.$$keyup=n,i.$$click=t.setInputMode,i.$$clickData="drop",d(i,h(yl,{class:"w-5 h-5 mr-2"})),a.$$click=e,k(()=>s.value=t.inputDataPaste),r})()}A(["keyup","click"]);const fc=w('<div id="job-name-div" class="mt-4 w-full"><textarea id="job-name" class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full " placeholder="(Optional) job name"></textarea></div>');function hc(t){function e(n){t.setJobName(n.target.value)}return(()=>{const n=fc.cloneNode(!0),r=n.firstChild;return r.$$keyup=e,k(()=>n.classList.toggle("hidden",!t.inputExists)),k(()=>r.value=t.jobName),n})()}A(["keyup"]);const gc=w('<div id="submit-note-div" class="mt-4 w-full"><textarea id="submit-note" class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full" placeholder="(Optional) note for this job"></textarea></div>');function mc(t){function e(n){t.setJobNote(n.target.value)}return(()=>{const n=gc.cloneNode(!0),r=n.firstChild;return r.$$keyup=e,k(()=>n.classList.toggle("hidden",!t.inputExists)),k(()=>r.value=t.jobNote),n})()}A(["keyup"]);const pc=w('<div id="submit-job-button-div" class="mt-4"><button id="submit-job-button" type="button" class="inline-flex items-center h-12 rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Annotate</button></div>');function bc(t){return(()=>{const e=pc.cloneNode(!0),n=e.firstChild;return dn(n,"click",t.submitFn,!0),k(()=>e.classList.toggle("hidden",!t.inputExists)),e})()}A(["click"]);const vc=w('<div id="input-div" class="w-[40rem] items-center flex flex-col" style="height: calc(100vh - 10rem);"><div class="flex"></div><div class="w-full flex items-center justify-center mt-1" ondragenter="onDragEnterInputFiles(event)" ondragover="onDragOverInputFiles(event)" ondragleave="onDragLeaveInputFiles(event)" ondrop="onDropInputFiles(event)"></div></div>');function yc(t){function e(n,r){t.setInputMode(n),n=="drop"?t.setInputDataDrop(r):n=="paste"&&t.setInputDataPaste(r)}return Et(function(){t.inputMode=="drop"?t.setInputExists(t.inputDataDrop.length>0):t.inputMode=="paste"&&t.setInputExists(t.inputDataPaste.length>0)}),(()=>{const n=vc.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return d(r,h(Kl,{get assembly(){return t.assembly},get setAssembly(){return t.setAssembly}}),null),d(r,h(sc,{get inputFormat(){return t.inputFormat},get setInputFormat(){return t.setInputFormat}}),null),d(s,h(Jo,{get children(){return[h(Vr,{get when(){return t.inputMode=="drop"},get children(){return h(cc,{get setInputMode(){return t.setInputMode},get inputDataDrop(){return t.inputDataDrop},get setInputDataDrop(){return t.setInputDataDrop}})}}),h(Vr,{get when(){return t.inputMode=="paste"},get children(){return h(dc,{get setInputMode(){return t.setInputMode},changeInputData:e,get inputDataPaste(){return t.inputDataPaste},get assembly(){return t.assembly},get setAssembly(){return t.setAssembly},get inputFormat(){return t.inputFormat},get setInputFormat(){return t.setInputFormat}})}})]}})),d(n,h(hc,{get inputExists(){return t.inputExists},get jobName(){return t.jobName},get setJobName(){return t.setJobName}}),null),d(n,h(mc,{get inputExists(){return t.inputExists},get jobNote(){return t.jobNote},get setJobNote(){return t.setJobNote}}),null),d(n,h(bc,{get inputExists(){return t.inputExists},get submitFn(){return t.submitFn}}),null),n})()}const _c=w('<div class="modulecard relative items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400 p-2 max-h-64"><div class="float-left w-24 h-24 mr-2 flex justify-center items-center"><img class="w-20 rounded-lg"></div><div class="min-w-0 flex-1"><a class="focus:online-none"><span class="absolute inset-0"></span><p class="text-md font-semibold text-gray-700"></p><p class="text-sm text-gray-500"></p></a></div></div>'),{serverUrl:wc,setServerUrl:Yg}=ne,{localModules:xc,setLocalModules:Qg,getLocalModule:Zg,addLocalModule:em,loadAllModules:tm,getLocalModuleLogo:nm}=pn;function pr(t){const e=xc()[t.moduleName],n=e.type;function r(l){for(const u in l)if(t.moduleName==u)return!0;return!1}function s(){return r(t.annotators)||r(t.postaggregators)||r(t.reporters)}function i(){let l;return n=="annotator"?l={...t.annotators}:n=="postaggregator"?l={...t.postaggregators}:n=="reporter"&&(l={...t.reporters}),l}function o(l){s()?delete l[t.moduleName]:l[t.moduleName]=e}function a(l){n=="annotator"?t.setAnnotators(l):n=="postaggregator"?t.setPostaggregators(l):n=="reporter"&&t.setReporters(l)}function c(){let l=i();o(l),a(l)}return(()=>{const l=_c.cloneNode(!0),u=l.firstChild,p=u.firstChild,v=u.nextSibling,b=v.firstChild,g=b.firstChild,m=g.nextSibling,x=m.nextSibling;return l.$$click=c,d(m,()=>e&&e.title),d(x,()=>e&&e.conf.description),k(_=>{const S=!!s(),T=e&&e.name,O=e&&e.kind,N=wc()+"/store/locallogo?module="+t.moduleName;return S!==_._v$&&l.classList.toggle("checked",_._v$=S),T!==_._v$2&&J(l,"name",_._v$2=T),O!==_._v$3&&J(l,"kind",_._v$3=O),N!==_._v$4&&J(p,"src",_._v$4=N),_},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0}),l})()}A(["click"]);const Ec=w('<div id="report-choice-div" class="w-[36rem] flex flex-col justify-center items-center"><div class="text-md text-gray-600">Select optional reporters to run.</div><div id="report-choice-items" class="w-96 grid gap-2 justify-center overflow-y-auto bg-gray-100 py-4 rounded-md" style="height: calc(100vh - 10rem);"></div></div>'),Ic=async()=>{const{serverUrl:t,setServerUrl:e}=ne;return(await(await fetch(t()+"/submit/reporttypes")).json()).valid};function Sc(t){const[e]=lr(Ic);return(()=>{const n=Ec.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return d(s,h(Ae,{get each(){return e()},children:i=>h(pr,{moduleName:i+"reporter",get reporters(){return t.reporters},get setReporters(){return t.setReporters}})})),n})()}const kc=w('<div id="cta-analysis-module-choice" class="absolute inset-x-0 bottom-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Scroll down or click to select analysis modules</span></p></div></div></div></div></div>');function Tc(t){function e(){document.querySelector("#analysis-module-choice-div").scrollIntoView({behavior:"smooth"})}return(()=>{const n=kc.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild;return n.$$click=e,d(o,h(Tl,{color:"#6b7280"}),a),n})()}A(["click"]);const $c=w('<button class="filter-category" role="filter-category" type="button"></button>');function hs(t){function e(n){t.setFilterCategory(t.value)}return(()=>{const n=$c.cloneNode(!0);return n.$$click=e,d(n,()=>t.title),k(()=>n.classList.toggle("pinned",t.value==t.filterCategory)),k(()=>n.value=t.value),n})()}A(["click"]);const Cc=w('<div class="flex mb-2"><label for="search" class="sr-only">Search</label><input type="text" name="search" class="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm mr-2" placeholder="Search"><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Select all</button><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-2">Deselect all</button></div>');function Ii(t){function e(n){t.setSearchText(n.target.value)}return(()=>{const n=Cc.cloneNode(!0),r=n.firstChild,s=r.nextSibling;return s.$$keyup=e,k(()=>J(n,"id",`search-filtered-modules-${t.kind}`)),k(()=>s.value=t.searchText),n})()}A(["keyup"]);const{localModules:Ac,setLocalModules:rm,getLocalModule:sm,addLocalModule:im,loadAllModules:om}=pn;function Si(t){for(let e in t)return!1;return!0}function Oc(t,e){let n=[];for(const[r,s]of Object.entries(Ac())){let i=!0;s.type!="annotator"&&s.type!="postaggregator"?i=!1:e!=null&&(e=="no tag"?s.tags.length>0&&(i=!1):s.tags.indexOf(e)==-1&&(i=!1)),i&&t!=null&&(i=!1,(r.indexOf(t)>=0||s.title.indexOf(t)>=0||s.description&&s.description.indexOf(t)>=0)&&(i=!0)),i&&n.push(r)}return n.sort(),n}const Nc=w('<div class="filtered-modules-div overflow-auto pr-2 grid grid-cols-2 gap-1" style="height: calc(95vh - 8rem);"></div>');function ki(t){return(()=>{const e=Nc.cloneNode(!0);return d(e,h(Ae,{get each(){return Oc(t.searchText,t.selectedTag)},children:n=>h(pr,{moduleName:n,get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}})})),k(n=>{const r=`filtered-modules-${t.kind}`,s=t.noCols==2,i=t.noCols==1;return r!==n._v$&&J(e,"id",n._v$=r),s!==n._v$2&&e.classList.toggle("grid-cols-2",n._v$2=s),i!==n._v$3&&e.classList.toggle("grid-cols-1",n._v$3=i),n},{_v$:void 0,_v$2:void 0,_v$3:void 0}),e})()}const Rc=w('<div id="analysis-module-filter-panel-all" class="analysis-module-filter-panel w-full mt-4 overflow-auto"></div>');function Dc(t){const[e,n]=y(null);return(()=>{const r=Rc.cloneNode(!0);return d(r,h(Ii,{kind:"all",get searchText(){return e()},setSearchText:n}),null),d(r,h(ki,{kind:"all",noCols:2,get searchText(){return e()},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),k(()=>r.classList.toggle("hidden",t.filterCategory!="all")),r})()}const Pc=w('<div class="relative flex items-start mb-2"><div class="flex items-center"><input type="radio" name="module-tag" class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"><label class="ml-3 block text-sm font-medium text-gray-600"></label></div></div>');function Lc(t){return t.replace(" ","_")}function Mc(t){return t.replace(/\w\S*/g,function(e){return e.charAt(0).toUpperCase()+e.substr(1).toLowerCase()})}function Uc(t){const e=`module-tag-radio-${Lc(t.value)}`;return(()=>{const n=Pc.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.nextSibling;return s.$$click=t.setSelectedTag,s.$$clickData=t.value,J(s,"id",e),J(i,"for",e),d(i,()=>Mc(t.value)),k(()=>s.value=t.value),n})()}A(["click"]);const jc=w('<div id="analysis-module-filter-panel-tags" class="analysis-module-filter-panel w-full mt-4 overflow-auto grid grid-cols-3"><div id="analysis-module-filter-items-tags" class="col-span-1 flex flex-col justify-leading pl-1 overflow-y-auto" style="height: calc(95vh - 8rem);"></div><div class="col-span-2"></div></div>'),Fc=async()=>{const{serverUrl:t,setServerUrl:e}=ne;let n=await(await fetch(t()+"/submit/tags_annotators_postaggregators")).json();return n.push("no tag"),n};function Bc(t){const[e]=lr(Fc),[n,r]=y(null),[s,i]=y(null);return(()=>{const o=jc.cloneNode(!0),a=o.firstChild,c=a.nextSibling;return d(a,h(Ae,{get each(){return e()},children:l=>h(Uc,{value:l,setSelectedTag:r})})),d(c,h(Ii,{kind:"tags",get searchText(){return s()},setSearchText:i}),null),d(c,h(ki,{kind:"tags",noCols:1,get selectedTag(){return n()},get searchText(){return s()},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),k(()=>o.classList.toggle("hidden",t.filterCategory!="tags")),o})()}const Hc=w('<div class="analysis-module-filter-wrapper col-span-7"><div id="analysis-module-filter-kinds" class="w-full"></div></div>');function zc(t){const[e,n]=y("all");return(()=>{const r=Hc.cloneNode(!0),s=r.firstChild;return d(s,h(hs,{value:"all",title:"All",get filterCategory(){return e()},setFilterCategory:n}),null),d(s,h(hs,{value:"tags",title:"Tags",get filterCategory(){return e()},setFilterCategory:n}),null),d(r,h(Dc,{get filterCategory(){return e()},get localModules(){return t.localModules},get setLocalModules(){return t.setLocalModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),d(r,h(Bc,{get filterCategory(){return e()},get localModules(){return t.localModules},get setLocalModules(){return t.setLocalModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),r})()}const Vc=w('<div class="col-span-4"><div class="text-gray-600 bg-gray-100 rounded-md border border-transparent font-medium px-3 py-1.5 h-[34px]">Selected analysis modules</div><div class="flex mb-2 mt-4"><button type="button" class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 h-[38px]">Clear</button></div><div class="filtered-modules-div overflow-auto pr-2 grid grid-cols-2 gap-1 grid-cols-1" style="height: calc(95vh - 8rem);"></div></div>');function Wc(t){function e(){let r=[];for(const s in t.annotators)r.push(s);for(const s in t.postaggregators)r.push(s);return r}function n(){t.setAnnotators({}),t.setPostaggregators({})}return(()=>{const r=Vc.cloneNode(!0),s=r.firstChild,i=s.nextSibling,o=i.firstChild,a=i.nextSibling;return o.$$click=n,d(a,h(Ae,{get each(){return e()},children:function(c){return h(pr,{moduleName:c,get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}})}})),r})()}A(["click"]);const Jc=w('<div id="cta-input" class="absolute inset-x-0 top-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Scroll up or click to go to the input panel</span></p></div></div></div></div></div>');function qc(t){function e(){document.querySelector("#input-div").scrollIntoView({behavior:"smooth"})}return(()=>{const n=Jc.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild;return n.$$click=e,d(o,h(Cl,{color:"#6b7280"}),a),n})()}A(["click"]);const Gc=w('<div id="analysis-module-choice-div" class="relative container mt-6 mb-4 snap-center flex justify-center max-w-7xl h-[95vh] max-w-7xl"><div id="analysis-module-filter-div" class="bg-white p-4 rounded-md ml-4 mt-4 overflow-auto flex flex-col gap-8 text-gray-600 h-[95vh] w-full"><div id="analysis-module-div" class="grid grid-cols-12 gap-2 mt-8" style="height: calc(95vh - 20rem);"><div class="col-span-1 flex flex-col justify-center content-center items-center"></div></div></div></div>');function Kc(t){return(()=>{const e=Gc.cloneNode(!0),n=e.firstChild,r=n.firstChild,s=r.firstChild;return d(e,h(qc,{}),n),d(r,h(zc,{get localModules(){return t.localModules},get setLocalModules(){return t.setLocalModules},get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),s),d(s,h($l,{})),d(r,h(Wc,{get annotators(){return t.annotators},get setAnnotators(){return t.setAnnotators},get postaggregators(){return t.postaggregators},get setPostaggregators(){return t.setPostaggregators}}),null),e})()}const Xc=w('<li><a href="#" class="block hover:bg-gray-50"><div class="py-4"><div class="flex items-center justify-between"><p class="truncate text-sm font-medium text-indigo-600"></p></div><div class="mt-2 sm:flex sm:justify-between"><div class="mt-2 w-full flex items-center text-sm text-gray-500 sm:mt-0"><div class="w-full bg-gray-200 rounded-full dark:bg-gray-700"><div class="bg-blue-600 text-xs font-medium text-blue-100 text-center p-0.5 leading-none rounded-full">%</div></div></div></div></div></a></li>');function Yc(t){return(()=>{const e=Xc.cloneNode(!0),n=e.firstChild,r=n.firstChild,s=r.firstChild,i=s.firstChild,o=s.nextSibling,a=o.firstChild,c=a.firstChild,l=c.firstChild,u=l.firstChild;return d(i,()=>t.fileName),d(l,()=>t.progress,u),k(()=>l.style.setProperty("width",t.progress+"%")),e})()}const Qc=w('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6"><div><div class="mt-3 text-center sm:mt-5"><ul role="list" class="divide-y divide-gray-200"></ul></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm">Cancel</button></div></div></div></div></div>');function Zc(t){function e(){t.controller.abort()}return(()=>{const n=Qc.cloneNode(!0),r=n.firstChild,s=r.nextSibling,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.firstChild,l=c.firstChild,u=a.nextSibling,p=u.firstChild;return d(l,h(Yc,{fileName:"Uploading...",get progress(){return t.uploadState.progress}})),p.$$click=e,n})()}A(["click"]);const Qn=Symbol("store-raw"),pt=Symbol("store-node"),eu=Symbol("store-name");function Ti(t,e){let n=t[Be];if(!n&&(Object.defineProperty(t,Be,{value:n=new Proxy(t,ru)}),!Array.isArray(t))){const r=Object.keys(t),s=Object.getOwnPropertyDescriptors(t);for(let i=0,o=r.length;i<o;i++){const a=r[i];if(s[a].get){const c=s[a].get.bind(n);Object.defineProperty(t,a,{get:c})}}}return n}function en(t){let e;return t!=null&&typeof t=="object"&&(t[Be]||!(e=Object.getPrototypeOf(t))||e===Object.prototype||Array.isArray(t))}function bt(t,e=new Set){let n,r,s,i;if(n=t!=null&&t[Qn])return n;if(!en(t)||e.has(t))return t;if(Array.isArray(t)){Object.isFrozen(t)?t=t.slice(0):e.add(t);for(let o=0,a=t.length;o<a;o++)s=t[o],(r=bt(s,e))!==s&&(t[o]=r)}else{Object.isFrozen(t)?t=Object.assign({},t):e.add(t);const o=Object.keys(t),a=Object.getOwnPropertyDescriptors(t);for(let c=0,l=o.length;c<l;c++)i=o[c],!a[i].get&&(s=t[i],(r=bt(s,e))!==s&&(t[i]=r))}return t}function tn(t){let e=t[pt];return e||Object.defineProperty(t,pt,{value:e={}}),e}function Zn(t,e,n){return t[e]||(t[e]=Ci(n))}function tu(t,e){const n=Reflect.getOwnPropertyDescriptor(t,e);return!n||n.get||!n.configurable||e===Be||e===pt||e===eu||(delete n.value,delete n.writable,n.get=()=>t[Be][e]),n}function $i(t){if(Ks()){const e=tn(t);(e._||(e._=Ci()))()}}function nu(t){return $i(t),Reflect.ownKeys(t)}function Ci(t){const[e,n]=y(t,{equals:!1,internal:!0});return e.$=n,e}const ru={get(t,e,n){if(e===Qn)return t;if(e===Be)return n;if(e===Wn)return $i(t),n;const r=tn(t),s=r.hasOwnProperty(e);let i=s?r[e]():t[e];if(e===pt||e==="__proto__")return i;if(!s){const o=Object.getOwnPropertyDescriptor(t,e);Ks()&&(typeof i!="function"||t.hasOwnProperty(e))&&!(o&&o.get)&&(i=Zn(r,e,i)())}return en(i)?Ti(i):i},has(t,e){if(e===Qn||e===Be||e===Wn||e===pt||e==="__proto__")return!0;const n=tn(t)[e];return n&&n(),e in t},set(){return!0},deleteProperty(){return!0},ownKeys:nu,getOwnPropertyDescriptor:tu};function nn(t,e,n,r=!1){if(!r&&t[e]===n)return;const s=t[e],i=t.length;n===void 0?delete t[e]:t[e]=n;let o=tn(t),a;(a=Zn(o,e,s))&&a.$(()=>n),Array.isArray(t)&&t.length!==i&&(a=Zn(o,"length",i))&&a.$(t.length),(a=o._)&&a.$()}function Ai(t,e){const n=Object.keys(e);for(let r=0;r<n.length;r+=1){const s=n[r];nn(t,s,e[s])}}function su(t,e){if(typeof e=="function"&&(e=e(t)),e=bt(e),Array.isArray(e)){if(t===e)return;let n=0,r=e.length;for(;n<r;n++){const s=e[n];t[n]!==s&&nn(t,n,s)}nn(t,"length",r)}else Ai(t,e)}function dt(t,e,n=[]){let r,s=t;if(e.length>1){r=e.shift();const o=typeof r,a=Array.isArray(t);if(Array.isArray(r)){for(let c=0;c<r.length;c++)dt(t,[r[c]].concat(e),n);return}else if(a&&o==="function"){for(let c=0;c<t.length;c++)r(t[c],c)&&dt(t,[c].concat(e),n);return}else if(a&&o==="object"){const{from:c=0,to:l=t.length-1,by:u=1}=r;for(let p=c;p<=l;p+=u)dt(t,[p].concat(e),n);return}else if(e.length>1){dt(t[r],e,[r].concat(n));return}s=t[r],n=[r].concat(n)}let i=e[0];typeof i=="function"&&(i=i(s,n),i===s)||r===void 0&&i==null||(i=bt(i),r===void 0||en(s)&&en(i)&&!Array.isArray(i)?Ai(s,i):nn(t,r,i))}function iu(...[t,e]){const n=bt(t||{}),r=Array.isArray(n),s=Ti(n);function i(...o){Uo(()=>{r&&o.length===1?su(n,o[0]):dt(n,o)})}return[s,i]}const ou=w('<div class="tabcontent p-4 snap-y snap-mandatory h-screen overflow-y-auto"><div class="relative container flex gap-8 snap-center max-w-7xl h-[95vh] justify-center items-start"></div></div>'),au=w("<div>Loading...</div>");function lu(t){const{tabName:e,setTabName:n}=tt,[r,s]=y("drop"),[i,o]=y([]),[a,c]=y(""),[l,u]=y([]),[p,v]=y([]),[b,g]=y([]),[m,x]=y(""),[_,S]=y(""),[T,O]=y(!1),[N,X]=y(null),[G,le]=y(null),[C,R]=y(!1),[U,re]=y(!1),{localModules:st}=pn,{serverUrl:xn,setServerUrl:En,withCredentials:Z}=ne,[Pt,it]=y({});let ce=[],Ve=null,z={},Ne;function ue(){return a().startsWith("#serverfile")}function In(){let D=[],B=a().split(`
`);for(var Re=1;Re<B.length;Re++){let we=B[Re];we==""||we.startsWith("#")||D.push(we.trim())}D.length>0&&(z.inputServerFiles=D)}function Sn(){ce=[];const D=new Blob([a()],{type:"text/plain"});ce.push(new File([D],"input"))}function kn(){ue()?In():Sn()}function ot(D){if(D!=null&&(r()=="drop"?ce=i():r()=="paste"&&kn(),ce.length>0))for(var B=0;B<ce.length;B++)D.append("file_"+B,ce[B])}function Tn(){z.annotators=[];for(const D in p())z.annotators.push(D)}function $n(){z.postaggregators=[];for(const D in b())z.postaggregators.push(D)}function I(){z.reports=[];for(const D in l())z.reports.push(D.substring(0,D.lastIndexOf("reporter")))}function F(){z.genome=_()}function K(){z.input_format=m()}function Cn(){z.job_name=N()}function Lt(){z.note=G()}function Mt(D){Ne=new AbortController,re(!0),it({progress:0}),M({method:"post",url:xn()+"/submit/submit?"+Math.random(),data:D,transformRequest:()=>D,signal:Ne.signal,withCredentials:Z,onUploadProgress:B=>{let Re=Math.round(B.progress*100);it({progress:Re})}}).then(function(B){re(!1),setTimeout(function(){t.setJobsTrigger(!t.jobsTrigger)},500)}).catch(function(B){console.error(B),B.code!="ERR_CANCELED"&&alert(B),it({}),re(!1)})}function Ut(){R(!0),ce={},z={},Ve=new FormData,ot(Ve),Tn(),$n(),I(),F(),K(),Cn(),Lt(),z.writeadmindb=!0,Ve.append("options",JSON.stringify(z)),Mt(Ve)}return(()=>{const D=ou.cloneNode(!0),B=D.firstChild;return d(B,h(yc,{get inputMode(){return r()},setInputMode:s,get inputDataDrop(){return i()},setInputDataDrop:o,get inputDataPaste(){return a()},setInputDataPaste:c,get assembly(){return _()},setAssembly:S,get inputFormat(){return m()},setInputFormat:x,get inputExists(){return T()},setInputExists:O,get jobName(){return N()},setJobName:X,get jobNote(){return G()},setJobNote:le,submitFn:Ut}),null),d(B,h(se,{get when(){return T()},get children(){return[h(se,{get when(){return!Si(st())},get fallback(){return au.cloneNode(!0)},get children(){return h(Sc,{get reporters(){return l()},setReporters:u})}}),h(Tc,{})]}}),null),d(D,h(se,{get when(){return T()},get children(){return h(Kc,{get annotators(){return p()},setAnnotators:v,get postaggregators(){return b()},setPostaggregators:g})}}),null),d(D,h(se,{get when(){return U()},get children(){return h(Zc,{get uploadState(){return Pt()},controller:Ne})}}),null),k(()=>D.classList.toggle("hidden",e()!="submit")),D})()}const cu=w('<a href="#" class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900" role="menuitem" tabindex="-1" value=""></a>');function uu(t){function e(){t.setAction(t.optionValue),t.execute(),t.setShow(!1)}return(()=>{const n=cu.cloneNode(!0);return n.$$click=e,d(n,()=>t.optionTitle),n})()}A(["click"]);const du=w('<div class="option-list ease-in absolute right-0 z-10 mt-12 w-24 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu"><div class="py-1" role="none"></div></div>');function fu(t){return(()=>{const e=du.cloneNode(!0),n=e.firstChild;return d(n,h(Ae,{get each(){return t.options},children:function(r){return h(uu,{get optionValue(){return r.value},get optionTitle(){return r.title},get execute(){return t.execute},get setAction(){return t.setAction},get setShow(){return t.setShow}})}})),k(()=>e.classList.toggle("hidden",!t.show)),e})()}const hu=w('<div class="select-div relative inline-flex text-left"><div><button type="button" class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100" id="assembly-select-div" title="Job action">Action</button></div></div>');function gu(t){const[e,n]=y(!1),[r,s]=y(""),i=[{value:"abort",title:"Abort"},{value:"delete",title:"Delete"}];function o(){t.performJobAction(r())}function a(c){n(!e())}return(()=>{const c=hu.cloneNode(!0),l=c.firstChild,u=l.firstChild;return u.firstChild,u.$$click=a,d(u,h(mr,{class:"-mr-1 ml-2 h-5 w-5"}),null),d(c,h(fu,{get show(){return e()},options:i,execute:o,setAction:s,setShow:n}),null),c})()}A(["click"]);const mu=w('<div class="flex bg-white pb-2 mt-2"><div class="flex"><nav class="isolate inline-flex rounded-md shadow-sm ml-8" aria-label="Pagination"><a href="#" class="jobs-table-page-nav-btn relative inline-flex items-center rounded-l-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span aria-current="page" class="relative z-10 inline-flex items-center border bg-white border-gray-300 text-gray-500 px-4 py-2 text-sm font-medium focus:z-20"></span><a href="#" class="jobs-table-page-nav-btn relative inline-flex items-center rounded-r-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Go to page</span><input type="text" class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">Go</a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Show</span><input type="text" class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">jobs per page</a><a href="#" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20 ml-4"></a></nav></div></div>');function pu(t){function e(){let o=t.pageno;o=o-1,o<=0&&(o=1),o!=t.pageno&&t.setPageno(o)}function n(){let o=t.pageno;o=o+1,o!=t.pageno&&t.setPageno(o)}function r(o){let a=o.target.value;try{a=parseInt(a)}catch(c){console.error(c);return}a<1&&(a=1),t.setPageno(a)}function s(o){let a=o.target.value;try{a=parseInt(a)}catch(c){console.error(c);return}t.setPagesize(a)}function i(o){t.setJobsTrigger(!t.jobsTrigger)}return(()=>{const o=mu.cloneNode(!0),a=o.firstChild,c=a.firstChild,l=c.firstChild,u=l.nextSibling,p=u.nextSibling,v=p.nextSibling,b=v.nextSibling,g=b.nextSibling,m=g.nextSibling,x=m.nextSibling,_=x.nextSibling,S=_.nextSibling;return d(a,h(gu,{get performJobAction(){return t.performJobAction}}),c),l.$$click=e,d(l,h(Al,{class:"w-5 h-5"})),d(u,()=>t.pageno),p.$$click=n,d(p,h(Ol,{class:"w-5 h-5"})),b.addEventListener("change",r),x.addEventListener("change",s),S.$$click=i,d(S,h(Nl,{class:"w-5 h-5"})),k(()=>b.value=t.pageno),k(()=>x.value=t.pagesize),o})()}A(["click"]);const bu=w("<a></a>");function gs(t){return(()=>{const e=bu.cloneNode(!0);return dn(e,"click",t.clickFn,!0),d(e,()=>t.children),k(n=>{const r="relative inline-flex items-center rounded-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-500 focus:z-20 "+t.bgColor+" "+t.bgHoverColor,s=t.hrefValue,i=t.targetValue;return r!==n._v$&&ni(e,n._v$=r),s!==n._v$2&&J(e,"href",n._v$2=s),i!==n._v$3&&J(e,"target",n._v$3=i),n},{_v$:void 0,_v$2:void 0,_v$3:void 0}),e})()}A(["click"]);const vu=w('<span class="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800"></span>'),yu=w('<span class="inline-flex rounded-full bg-amber-100 px-2 text-xs font-semibold leading-5 text-amber-800"></span>'),_u=w('<span class="inline-flex rounded-full bg-red-100 px-2 text-xs font-semibold leading-5 text-red-800"></span>'),wu=w('<span class="inline-flex text-xs"></span>'),xu=w('<tr class="text-sm h-16"><td scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8 bg-gray-50"><input type="checkbox" class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></td><td class="jobs-table-td"></td><td class="jobs-table-td bg-gray-50"></td><td class="jobs-table-td"></td><td class="jobs-table-td bg-gray-50"></td><td class="jobs-table-td"></td><td class="jobs-table-td bg-gray-50 text-xs"></td><td class="jobs-table-td"></td></tr>');function Eu(t){return t=="Finished"||t=="Error"||t=="Aborted"}function Iu(t){const{serverUrl:e,withCredentials:n}=ne,r=1e3;let s=null;Yt(()=>clearInterval(s));function i(){t.changeJobChecked(t.job.uid),t.setAllMarksOn(null)}function o(){M.get(e()+"/submit/jobstatus",{params:{uid:t.job.uid},withCredentials:n}).then(function(g){const m=g.data;Eu(m)&&clearInterval(s),t.changeJobStatus(t.job.uid,m)}).catch(function(g){console.error(g)})}function a(){const g=t.job.status;g!="Finished"&&g!="Error"&&g!="Aborted"&&(s=setInterval(function(){o()},r))}function c(){return t.job.status=="Finished"}function l(){return c()?h(gs,{children:"View",get hrefValue(){return e()+"/result/nocache/index.html?uid="+t.job.uid},targetValue:"_blank",bgColor:"bg-sky-100",bgHoverColor:"hover:bg-sky-200"}):h(gs,{children:"Log",get hrefValue(){return e()+"/submit/joblog?uid="+t.job.uid},targetValue:"_blank",bgColor:"bg-gray-100",bgHoverColor:"hover:bg-gray-200"})}function u(){const g=t.job.status;return g=="Finished"?(()=>{const m=vu.cloneNode(!0);return d(m,()=>t.job.status),m})():g=="Aborted"?(()=>{const m=yu.cloneNode(!0);return d(m,()=>t.job.status),m})():g=="Error"?(()=>{const m=_u.cloneNode(!0);return d(m,()=>t.job.status),m})():(()=>{const m=wu.cloneNode(!0);return d(m,()=>t.job.status),m})()}function p(){return t.job.statusjson.orig_input_fname?t.job.statusjson.orig_input_fname.join(", "):""}function v(){let g=new Date(t.job.statusjson.submission_time);return(""+g).split("GMT")[0]}function b(){let g=[];const m=t.job.statusjson;if(!m)return"";const x=m.annotators;if(x)for(const S of x)S!="original_input"&&g.push(S);const _=m.postaggregators;if(_)for(const S of _)g.push(S);return g.join(", ")}return a(),(()=>{const g=xu.cloneNode(!0),m=g.firstChild,x=m.firstChild,_=m.nextSibling,S=_.nextSibling,T=S.nextSibling,O=T.nextSibling,N=O.nextSibling,X=N.nextSibling,G=X.nextSibling;return x.addEventListener("change",i),d(_,()=>t.job.name),d(S,u),d(T,l),d(O,p),d(N,b),d(X,v),d(G,()=>t.job.statusjson.note),k(()=>x.checked=t.job.checked),g})()}const Su=w('<div class="flex flex-col"><div class="relative shadow ring-1 ring-black ring-opacity-5 md:rounded-lg overflow-auto"><table class="table-fixed divide-y divide-gray-300"><thead class="table-header-group bg-gray-50 block"><tr><th scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8"><input type="checkbox" class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></th><th scope="col" class="jobs-table-th min-w-[10rem]">Name</th><th scope="col" class="jobs-table-th min-w-[5rem]">State</th><th scope="col" class="jobs-table-th min-w-[5rem]">View</th><th scope="col" class="jobs-table-th min-w-[20rem]">Input</th><th scope="col" class="jobs-table-th min-w-[10rem]">Modules</th><th scope="col" class="jobs-table-th min-w-[8rem]">Submitted</th><th scope="col" class="jobs-table-th w-full">Note</th></tr></thead><tbody class="table-row-group divide-y divide-gray-200 bg-white block overflow-auto h-[36rem]"></tbody></table></div></div>');function ku(t){const[e,n]=y(null);function r(){if(e()==!0?n(!1):(e()==null||e()==!1)&&n(!0),e()==!0)for(const s of t.jobs)t.changeJobChecked(s.uid,!0);else if(e()==!1)for(const s of t.jobs)t.changeJobChecked(s.uid,!1)}return(()=>{const s=Su.cloneNode(!0),i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.firstChild,l=c.firstChild,u=l.firstChild,p=a.nextSibling;return u.$$click=r,d(p,h(Ae,{get each(){return t.jobs},children:v=>h(Iu,{job:v,get changeJobStatus(){return t.changeJobStatus},get changeJobChecked(){return t.changeJobChecked},setAllMarksOn:n})})),k(()=>u.value=e()),s})()}A(["click"]);const Tu=w('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="text-center"><p class="text-sm text-gray-500"></p></div></div></div></div></div></div>');function $u(t){return(()=>{const e=Tu.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.firstChild;return d(c,()=>t.msg),k(()=>e.classList.toggle("hidden",t.msg==null)),e})()}const Cu=w('<div id="tab_jobs" class="tabcontent px-6 mb-4"><div></div></div>'),{serverUrl:ms,withCredentials:ps}=ne,{logged:Au,setLogged:Ou}=Tt,{multiuser:Nu}=kt;function Ru(t){const{tabName:e}=tt,[n,r]=iu([]),[s,i]=y(1),[o,a]=y(10),[c,l]=y(null);Et(function(){s(),o(),t.jobsTrigger,(Nu()==!1||Au()==!0)&&v()});function u(m,x){r(_=>_.uid==m,"status",x)}function p(m,x){x==null?r(_=>_.uid==m,"checked",_=>!_):r(_=>_.uid==m,"checked",x)}function v(){M.post(ms()+"/submit/jobs",{pageno:s(),pagesize:o()},{withCredentials:ps}).then(function(m){if(m.status=="error"){Ou(!1);return}const x=m.data;r(x)}).catch(function(m){console.error(m),m.response.status==404&&i(s()-1)})}function b(m,x){const _=m.map(S=>S.uid);M.post(ms()+"/submit/delete_jobs",{uids:_,abort_only:x},{withCredentials:ps}).then(function(){t.setJobsTrigger(!t.jobsTrigger),l(null)}).catch(function(S){console.error(S),l(null)})}function g(m){const x=n.filter(_=>_.checked);m=="delete"?(l("Deleting jobs..."),b(x,!1)):m=="abort"&&(l("Aborting jobs..."),b(x,!0))}return(()=>{const m=Cu.cloneNode(!0),x=m.firstChild;return d(x,h(pu,{get pageno(){return s()},setPageno:i,get pagesize(){return o()},setPagesize:a,get jobsTrigger(){return t.jobsTrigger},get setJobsTrigger(){return t.setJobsTrigger},performJobAction:g}),null),d(x,h(ku,{jobs:n,changeJobStatus:u,changeJobChecked:p}),null),d(m,h($u,{get msg(){return c()}}),null),k(()=>m.classList.toggle("hidden",e()!="jobs")),m})()}const Du=w('<div id="tab_system" class="tabcontent"><div class="p-4"><button type="button" class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 text-sm font-medium leading-4 text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Download system log</button></div></div>'),{serverUrl:Pu,setServerUrl:am,withCredentials:lm}=ne;function Lu(){const{tabName:t,setTabName:e}=tt;function n(){M({url:Pu()+"/submit/systemlog",method:"GET",responseType:"blob"}).then(function(r){let s=document.createElement("a");s.href=window.URL.createObjectURL(new Blob([r.data],{type:"text/plain"})),s.download=r.headers["content-disposition"].split("=")[1],document.body.appendChild(s),s.click(),document.body.removeChild(s)}).catch(function(r){console.error(r)})}return(()=>{const r=Du.cloneNode(!0),s=r.firstChild,i=s.firstChild;return i.$$click=n,k(()=>r.classList.toggle("hidden",t()!="system")),r})()}A(["click"]);/**
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
 */const Oi=function(t){const e=[];let n=0;for(let r=0;r<t.length;r++){let s=t.charCodeAt(r);s<128?e[n++]=s:s<2048?(e[n++]=s>>6|192,e[n++]=s&63|128):(s&64512)===55296&&r+1<t.length&&(t.charCodeAt(r+1)&64512)===56320?(s=65536+((s&1023)<<10)+(t.charCodeAt(++r)&1023),e[n++]=s>>18|240,e[n++]=s>>12&63|128,e[n++]=s>>6&63|128,e[n++]=s&63|128):(e[n++]=s>>12|224,e[n++]=s>>6&63|128,e[n++]=s&63|128)}return e},Mu=function(t){const e=[];let n=0,r=0;for(;n<t.length;){const s=t[n++];if(s<128)e[r++]=String.fromCharCode(s);else if(s>191&&s<224){const i=t[n++];e[r++]=String.fromCharCode((s&31)<<6|i&63)}else if(s>239&&s<365){const i=t[n++],o=t[n++],a=t[n++],c=((s&7)<<18|(i&63)<<12|(o&63)<<6|a&63)-65536;e[r++]=String.fromCharCode(55296+(c>>10)),e[r++]=String.fromCharCode(56320+(c&1023))}else{const i=t[n++],o=t[n++];e[r++]=String.fromCharCode((s&15)<<12|(i&63)<<6|o&63)}}return e.join("")},Ni={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(t,e){if(!Array.isArray(t))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let s=0;s<t.length;s+=3){const i=t[s],o=s+1<t.length,a=o?t[s+1]:0,c=s+2<t.length,l=c?t[s+2]:0,u=i>>2,p=(i&3)<<4|a>>4;let v=(a&15)<<2|l>>6,b=l&63;c||(b=64,o||(v=64)),r.push(n[u],n[p],n[v],n[b])}return r.join("")},encodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(t):this.encodeByteArray(Oi(t),e)},decodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(t):Mu(this.decodeStringToByteArray(t,e))},decodeStringToByteArray(t,e){this.init_();const n=e?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let s=0;s<t.length;){const i=n[t.charAt(s++)],a=s<t.length?n[t.charAt(s)]:0;++s;const l=s<t.length?n[t.charAt(s)]:64;++s;const p=s<t.length?n[t.charAt(s)]:64;if(++s,i==null||a==null||l==null||p==null)throw Error();const v=i<<2|a>>4;if(r.push(v),l!==64){const b=a<<4&240|l>>2;if(r.push(b),p!==64){const g=l<<6&192|p;r.push(g)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let t=0;t<this.ENCODED_VALS.length;t++)this.byteToCharMap_[t]=this.ENCODED_VALS.charAt(t),this.charToByteMap_[this.byteToCharMap_[t]]=t,this.byteToCharMapWebSafe_[t]=this.ENCODED_VALS_WEBSAFE.charAt(t),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[t]]=t,t>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(t)]=t,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(t)]=t)}}},Uu=function(t){const e=Oi(t);return Ni.encodeByteArray(e,!0)},Ri=function(t){return Uu(t).replace(/\./g,"")},Di=function(t){try{return Ni.decodeString(t,!0)}catch(e){console.error("base64Decode failed: ",e)}return null};/**
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
 */function q(){return typeof navigator<"u"&&typeof navigator.userAgent=="string"?navigator.userAgent:""}function ju(){return typeof window<"u"&&!!(window.cordova||window.phonegap||window.PhoneGap)&&/ios|iphone|ipod|ipad|android|blackberry|iemobile/i.test(q())}function Fu(){const t=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof t=="object"&&t.id!==void 0}function Bu(){return typeof navigator=="object"&&navigator.product==="ReactNative"}function Hu(){const t=q();return t.indexOf("MSIE ")>=0||t.indexOf("Trident/")>=0}function zu(){return typeof indexedDB=="object"}function Vu(){return new Promise((t,e)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(r);s.onsuccess=()=>{s.result.close(),n||self.indexedDB.deleteDatabase(r),t(!0)},s.onupgradeneeded=()=>{n=!1},s.onerror=()=>{var i;e(((i=s.error)===null||i===void 0?void 0:i.message)||"")}}catch(n){e(n)}})}function Wu(){if(typeof self<"u")return self;if(typeof window<"u")return window;if(typeof global<"u")return global;throw new Error("Unable to locate global object.")}/**
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
 */const Ju=()=>Wu().__FIREBASE_DEFAULTS__,qu=()=>{if(typeof process>"u"||typeof process.env>"u")return;const t=process.env.__FIREBASE_DEFAULTS__;if(t)return JSON.parse(t)},Gu=()=>{if(typeof document>"u")return;let t;try{t=document.cookie.match(/__FIREBASE_DEFAULTS__=([^;]+)/)}catch{return}const e=t&&Di(t[1]);return e&&JSON.parse(e)},br=()=>{try{return Ju()||qu()||Gu()}catch(t){console.info(`Unable to get __FIREBASE_DEFAULTS__ due to: ${t}`);return}},Ku=t=>{var e,n;return(n=(e=br())===null||e===void 0?void 0:e.emulatorHosts)===null||n===void 0?void 0:n[t]},Xu=()=>{var t;return(t=br())===null||t===void 0?void 0:t.config},Pi=t=>{var e;return(e=br())===null||e===void 0?void 0:e[`_${t}`]};/**
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
 */class Yu{constructor(){this.reject=()=>{},this.resolve=()=>{},this.promise=new Promise((e,n)=>{this.resolve=e,this.reject=n})}wrapCallback(e){return(n,r)=>{n?this.reject(n):this.resolve(r),typeof e=="function"&&(this.promise.catch(()=>{}),e.length===1?e(n):e(n,r))}}}/**
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
 */const Qu="FirebaseError";class Oe extends Error{constructor(e,n,r){super(n),this.code=e,this.customData=r,this.name=Qu,Object.setPrototypeOf(this,Oe.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,$t.prototype.create)}}class $t{constructor(e,n,r){this.service=e,this.serviceName=n,this.errors=r}create(e,...n){const r=n[0]||{},s=`${this.service}/${e}`,i=this.errors[e],o=i?Zu(i,r):"Error",a=`${this.serviceName}: ${o} (${s}).`;return new Oe(s,a,r)}}function Zu(t,e){return t.replace(ed,(n,r)=>{const s=e[r];return s!=null?String(s):`<${r}?>`})}const ed=/\{\$([^}]+)}/g;function td(t){for(const e in t)if(Object.prototype.hasOwnProperty.call(t,e))return!1;return!0}function rn(t,e){if(t===e)return!0;const n=Object.keys(t),r=Object.keys(e);for(const s of n){if(!r.includes(s))return!1;const i=t[s],o=e[s];if(bs(i)&&bs(o)){if(!rn(i,o))return!1}else if(i!==o)return!1}for(const s of r)if(!n.includes(s))return!1;return!0}function bs(t){return t!==null&&typeof t=="object"}/**
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
 */function Ct(t){const e=[];for(const[n,r]of Object.entries(t))Array.isArray(r)?r.forEach(s=>{e.push(encodeURIComponent(n)+"="+encodeURIComponent(s))}):e.push(encodeURIComponent(n)+"="+encodeURIComponent(r));return e.length?"&"+e.join("&"):""}function ft(t){const e={};return t.replace(/^\?/,"").split("&").forEach(r=>{if(r){const[s,i]=r.split("=");e[decodeURIComponent(s)]=decodeURIComponent(i)}}),e}function ht(t){const e=t.indexOf("?");if(!e)return"";const n=t.indexOf("#",e);return t.substring(e,n>0?n:void 0)}function nd(t,e){const n=new rd(t,e);return n.subscribe.bind(n)}class rd{constructor(e,n){this.observers=[],this.unsubscribes=[],this.observerCount=0,this.task=Promise.resolve(),this.finalized=!1,this.onNoObservers=n,this.task.then(()=>{e(this)}).catch(r=>{this.error(r)})}next(e){this.forEachObserver(n=>{n.next(e)})}error(e){this.forEachObserver(n=>{n.error(e)}),this.close(e)}complete(){this.forEachObserver(e=>{e.complete()}),this.close()}subscribe(e,n,r){let s;if(e===void 0&&n===void 0&&r===void 0)throw new Error("Missing Observer.");sd(e,["next","error","complete"])?s=e:s={next:e,error:n,complete:r},s.next===void 0&&(s.next=Mn),s.error===void 0&&(s.error=Mn),s.complete===void 0&&(s.complete=Mn);const i=this.unsubscribeOne.bind(this,this.observers.length);return this.finalized&&this.task.then(()=>{try{this.finalError?s.error(this.finalError):s.complete()}catch{}}),this.observers.push(s),i}unsubscribeOne(e){this.observers===void 0||this.observers[e]===void 0||(delete this.observers[e],this.observerCount-=1,this.observerCount===0&&this.onNoObservers!==void 0&&this.onNoObservers(this))}forEachObserver(e){if(!this.finalized)for(let n=0;n<this.observers.length;n++)this.sendOne(n,e)}sendOne(e,n){this.task.then(()=>{if(this.observers!==void 0&&this.observers[e]!==void 0)try{n(this.observers[e])}catch(r){typeof console<"u"&&console.error&&console.error(r)}})}close(e){this.finalized||(this.finalized=!0,e!==void 0&&(this.finalError=e),this.task.then(()=>{this.observers=void 0,this.onNoObservers=void 0}))}}function sd(t,e){if(typeof t!="object"||t===null)return!1;for(const n of e)if(n in t&&typeof t[n]=="function")return!0;return!1}function Mn(){}/**
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
 */function ae(t){return t&&t._delegate?t._delegate:t}class Xe{constructor(e,n,r){this.name=e,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}/**
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
 */const Le="[DEFAULT]";/**
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
 */class id{constructor(e,n){this.name=e,this.container=n,this.component=null,this.instances=new Map,this.instancesDeferred=new Map,this.instancesOptions=new Map,this.onInitCallbacks=new Map}get(e){const n=this.normalizeInstanceIdentifier(e);if(!this.instancesDeferred.has(n)){const r=new Yu;if(this.instancesDeferred.set(n,r),this.isInitialized(n)||this.shouldAutoInitialize())try{const s=this.getOrInitializeService({instanceIdentifier:n});s&&r.resolve(s)}catch{}}return this.instancesDeferred.get(n).promise}getImmediate(e){var n;const r=this.normalizeInstanceIdentifier(e?.identifier),s=(n=e?.optional)!==null&&n!==void 0?n:!1;if(this.isInitialized(r)||this.shouldAutoInitialize())try{return this.getOrInitializeService({instanceIdentifier:r})}catch(i){if(s)return null;throw i}else{if(s)return null;throw Error(`Service ${this.name} is not available`)}}getComponent(){return this.component}setComponent(e){if(e.name!==this.name)throw Error(`Mismatching Component ${e.name} for Provider ${this.name}.`);if(this.component)throw Error(`Component for ${this.name} has already been provided`);if(this.component=e,!!this.shouldAutoInitialize()){if(ad(e))try{this.getOrInitializeService({instanceIdentifier:Le})}catch{}for(const[n,r]of this.instancesDeferred.entries()){const s=this.normalizeInstanceIdentifier(n);try{const i=this.getOrInitializeService({instanceIdentifier:s});r.resolve(i)}catch{}}}}clearInstance(e=Le){this.instancesDeferred.delete(e),this.instancesOptions.delete(e),this.instances.delete(e)}async delete(){const e=Array.from(this.instances.values());await Promise.all([...e.filter(n=>"INTERNAL"in n).map(n=>n.INTERNAL.delete()),...e.filter(n=>"_delete"in n).map(n=>n._delete())])}isComponentSet(){return this.component!=null}isInitialized(e=Le){return this.instances.has(e)}getOptions(e=Le){return this.instancesOptions.get(e)||{}}initialize(e={}){const{options:n={}}=e,r=this.normalizeInstanceIdentifier(e.instanceIdentifier);if(this.isInitialized(r))throw Error(`${this.name}(${r}) has already been initialized`);if(!this.isComponentSet())throw Error(`Component ${this.name} has not been registered yet`);const s=this.getOrInitializeService({instanceIdentifier:r,options:n});for(const[i,o]of this.instancesDeferred.entries()){const a=this.normalizeInstanceIdentifier(i);r===a&&o.resolve(s)}return s}onInit(e,n){var r;const s=this.normalizeInstanceIdentifier(n),i=(r=this.onInitCallbacks.get(s))!==null&&r!==void 0?r:new Set;i.add(e),this.onInitCallbacks.set(s,i);const o=this.instances.get(s);return o&&e(o,s),()=>{i.delete(e)}}invokeOnInitCallbacks(e,n){const r=this.onInitCallbacks.get(n);if(!!r)for(const s of r)try{s(e,n)}catch{}}getOrInitializeService({instanceIdentifier:e,options:n={}}){let r=this.instances.get(e);if(!r&&this.component&&(r=this.component.instanceFactory(this.container,{instanceIdentifier:od(e),options:n}),this.instances.set(e,r),this.instancesOptions.set(e,n),this.invokeOnInitCallbacks(r,e),this.component.onInstanceCreated))try{this.component.onInstanceCreated(this.container,e,r)}catch{}return r||null}normalizeInstanceIdentifier(e=Le){return this.component?this.component.multipleInstances?e:Le:e}shouldAutoInitialize(){return!!this.component&&this.component.instantiationMode!=="EXPLICIT"}}function od(t){return t===Le?void 0:t}function ad(t){return t.instantiationMode==="EAGER"}/**
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
 */class ld{constructor(e){this.name=e,this.providers=new Map}addComponent(e){const n=this.getProvider(e.name);if(n.isComponentSet())throw new Error(`Component ${e.name} has already been registered with ${this.name}`);n.setComponent(e)}addOrOverwriteComponent(e){this.getProvider(e.name).isComponentSet()&&this.providers.delete(e.name),this.addComponent(e)}getProvider(e){if(this.providers.has(e))return this.providers.get(e);const n=new id(e,this);return this.providers.set(e,n),n}getProviders(){return Array.from(this.providers.values())}}/**
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
 */var P;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(P||(P={}));const cd={debug:P.DEBUG,verbose:P.VERBOSE,info:P.INFO,warn:P.WARN,error:P.ERROR,silent:P.SILENT},ud=P.INFO,dd={[P.DEBUG]:"log",[P.VERBOSE]:"log",[P.INFO]:"info",[P.WARN]:"warn",[P.ERROR]:"error"},fd=(t,e,...n)=>{if(e<t.logLevel)return;const r=new Date().toISOString(),s=dd[e];if(s)console[s](`[${r}]  ${t.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class Li{constructor(e){this.name=e,this._logLevel=ud,this._logHandler=fd,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in P))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?cd[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,P.DEBUG,...e),this._logHandler(this,P.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,P.VERBOSE,...e),this._logHandler(this,P.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,P.INFO,...e),this._logHandler(this,P.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,P.WARN,...e),this._logHandler(this,P.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,P.ERROR,...e),this._logHandler(this,P.ERROR,...e)}}const hd=(t,e)=>e.some(n=>t instanceof n);let vs,ys;function gd(){return vs||(vs=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function md(){return ys||(ys=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Mi=new WeakMap,er=new WeakMap,Ui=new WeakMap,Un=new WeakMap,vr=new WeakMap;function pd(t){const e=new Promise((n,r)=>{const s=()=>{t.removeEventListener("success",i),t.removeEventListener("error",o)},i=()=>{n(ke(t.result)),s()},o=()=>{r(t.error),s()};t.addEventListener("success",i),t.addEventListener("error",o)});return e.then(n=>{n instanceof IDBCursor&&Mi.set(n,t)}).catch(()=>{}),vr.set(e,t),e}function bd(t){if(er.has(t))return;const e=new Promise((n,r)=>{const s=()=>{t.removeEventListener("complete",i),t.removeEventListener("error",o),t.removeEventListener("abort",o)},i=()=>{n(),s()},o=()=>{r(t.error||new DOMException("AbortError","AbortError")),s()};t.addEventListener("complete",i),t.addEventListener("error",o),t.addEventListener("abort",o)});er.set(t,e)}let tr={get(t,e,n){if(t instanceof IDBTransaction){if(e==="done")return er.get(t);if(e==="objectStoreNames")return t.objectStoreNames||Ui.get(t);if(e==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return ke(t[e])},set(t,e,n){return t[e]=n,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function vd(t){tr=t(tr)}function yd(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...n){const r=t.call(jn(this),e,...n);return Ui.set(r,e.sort?e.sort():[e]),ke(r)}:md().includes(t)?function(...e){return t.apply(jn(this),e),ke(Mi.get(this))}:function(...e){return ke(t.apply(jn(this),e))}}function _d(t){return typeof t=="function"?yd(t):(t instanceof IDBTransaction&&bd(t),hd(t,gd())?new Proxy(t,tr):t)}function ke(t){if(t instanceof IDBRequest)return pd(t);if(Un.has(t))return Un.get(t);const e=_d(t);return e!==t&&(Un.set(t,e),vr.set(e,t)),e}const jn=t=>vr.get(t);function wd(t,e,{blocked:n,upgrade:r,blocking:s,terminated:i}={}){const o=indexedDB.open(t,e),a=ke(o);return r&&o.addEventListener("upgradeneeded",c=>{r(ke(o.result),c.oldVersion,c.newVersion,ke(o.transaction))}),n&&o.addEventListener("blocked",()=>n()),a.then(c=>{i&&c.addEventListener("close",()=>i()),s&&c.addEventListener("versionchange",()=>s())}).catch(()=>{}),a}const xd=["get","getKey","getAll","getAllKeys","count"],Ed=["put","add","delete","clear"],Fn=new Map;function _s(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if(Fn.get(e))return Fn.get(e);const n=e.replace(/FromIndex$/,""),r=e!==n,s=Ed.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(s||xd.includes(n)))return;const i=async function(o,...a){const c=this.transaction(o,s?"readwrite":"readonly");let l=c.store;return r&&(l=l.index(a.shift())),(await Promise.all([l[n](...a),s&&c.done]))[0]};return Fn.set(e,i),i}vd(t=>({...t,get:(e,n,r)=>_s(e,n)||t.get(e,n,r),has:(e,n)=>!!_s(e,n)||t.has(e,n)}));/**
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
 */class Id{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(Sd(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function Sd(t){const e=t.getComponent();return e?.type==="VERSION"}const nr="@firebase/app",ws="0.8.3";/**
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
 */const He=new Li("@firebase/app"),kd="@firebase/app-compat",Td="@firebase/analytics-compat",$d="@firebase/analytics",Cd="@firebase/app-check-compat",Ad="@firebase/app-check",Od="@firebase/auth",Nd="@firebase/auth-compat",Rd="@firebase/database",Dd="@firebase/database-compat",Pd="@firebase/functions",Ld="@firebase/functions-compat",Md="@firebase/installations",Ud="@firebase/installations-compat",jd="@firebase/messaging",Fd="@firebase/messaging-compat",Bd="@firebase/performance",Hd="@firebase/performance-compat",zd="@firebase/remote-config",Vd="@firebase/remote-config-compat",Wd="@firebase/storage",Jd="@firebase/storage-compat",qd="@firebase/firestore",Gd="@firebase/firestore-compat",Kd="firebase",Xd="9.13.0";/**
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
 */const rr="[DEFAULT]",Yd={[nr]:"fire-core",[kd]:"fire-core-compat",[$d]:"fire-analytics",[Td]:"fire-analytics-compat",[Ad]:"fire-app-check",[Cd]:"fire-app-check-compat",[Od]:"fire-auth",[Nd]:"fire-auth-compat",[Rd]:"fire-rtdb",[Dd]:"fire-rtdb-compat",[Pd]:"fire-fn",[Ld]:"fire-fn-compat",[Md]:"fire-iid",[Ud]:"fire-iid-compat",[jd]:"fire-fcm",[Fd]:"fire-fcm-compat",[Bd]:"fire-perf",[Hd]:"fire-perf-compat",[zd]:"fire-rc",[Vd]:"fire-rc-compat",[Wd]:"fire-gcs",[Jd]:"fire-gcs-compat",[qd]:"fire-fst",[Gd]:"fire-fst-compat","fire-js":"fire-js",[Kd]:"fire-js-all"};/**
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
 */const sn=new Map,sr=new Map;function Qd(t,e){try{t.container.addComponent(e)}catch(n){He.debug(`Component ${e.name} failed to register with FirebaseApp ${t.name}`,n)}}function vt(t){const e=t.name;if(sr.has(e))return He.debug(`There were multiple attempts to register component ${e}.`),!1;sr.set(e,t);for(const n of sn.values())Qd(n,t);return!0}function ji(t,e){const n=t.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),t.container.getProvider(e)}/**
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
 */const Zd={["no-app"]:"No Firebase App '{$appName}' has been created - call Firebase App.initializeApp()",["bad-app-name"]:"Illegal App name: '{$appName}",["duplicate-app"]:"Firebase App named '{$appName}' already exists with different options or config",["app-deleted"]:"Firebase App named '{$appName}' already deleted",["no-options"]:"Need to provide options, when not being deployed to hosting via source.",["invalid-app-argument"]:"firebase.{$appName}() takes either no argument or a Firebase App instance.",["invalid-log-argument"]:"First argument to `onLog` must be null or a function.",["idb-open"]:"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.",["idb-get"]:"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.",["idb-set"]:"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.",["idb-delete"]:"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}."},Te=new $t("app","Firebase",Zd);/**
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
 */class ef{constructor(e,n,r){this._isDeleted=!1,this._options=Object.assign({},e),this._config=Object.assign({},n),this._name=n.name,this._automaticDataCollectionEnabled=n.automaticDataCollectionEnabled,this._container=r,this.container.addComponent(new Xe("app",()=>this,"PUBLIC"))}get automaticDataCollectionEnabled(){return this.checkDestroyed(),this._automaticDataCollectionEnabled}set automaticDataCollectionEnabled(e){this.checkDestroyed(),this._automaticDataCollectionEnabled=e}get name(){return this.checkDestroyed(),this._name}get options(){return this.checkDestroyed(),this._options}get config(){return this.checkDestroyed(),this._config}get container(){return this._container}get isDeleted(){return this._isDeleted}set isDeleted(e){this._isDeleted=e}checkDestroyed(){if(this.isDeleted)throw Te.create("app-deleted",{appName:this._name})}}/**
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
 */const bn=Xd;function Fi(t,e={}){let n=t;typeof e!="object"&&(e={name:e});const r=Object.assign({name:rr,automaticDataCollectionEnabled:!1},e),s=r.name;if(typeof s!="string"||!s)throw Te.create("bad-app-name",{appName:String(s)});if(n||(n=Xu()),!n)throw Te.create("no-options");const i=sn.get(s);if(i){if(rn(n,i.options)&&rn(r,i.config))return i;throw Te.create("duplicate-app",{appName:s})}const o=new ld(s);for(const c of sr.values())o.addComponent(c);const a=new ef(n,r,o);return sn.set(s,a),a}function tf(t=rr){const e=sn.get(t);if(!e&&t===rr)return Fi();if(!e)throw Te.create("no-app",{appName:t});return e}function Je(t,e,n){var r;let s=(r=Yd[t])!==null&&r!==void 0?r:t;n&&(s+=`-${n}`);const i=s.match(/\s|\//),o=e.match(/\s|\//);if(i||o){const a=[`Unable to register library "${s}" with version "${e}":`];i&&a.push(`library name "${s}" contains illegal characters (whitespace or "/")`),i&&o&&a.push("and"),o&&a.push(`version name "${e}" contains illegal characters (whitespace or "/")`),He.warn(a.join(" "));return}vt(new Xe(`${s}-version`,()=>({library:s,version:e}),"VERSION"))}/**
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
 */const nf="firebase-heartbeat-database",rf=1,yt="firebase-heartbeat-store";let Bn=null;function Bi(){return Bn||(Bn=wd(nf,rf,{upgrade:(t,e)=>{switch(e){case 0:t.createObjectStore(yt)}}}).catch(t=>{throw Te.create("idb-open",{originalErrorMessage:t.message})})),Bn}async function sf(t){var e;try{return(await Bi()).transaction(yt).objectStore(yt).get(Hi(t))}catch(n){if(n instanceof Oe)He.warn(n.message);else{const r=Te.create("idb-get",{originalErrorMessage:(e=n)===null||e===void 0?void 0:e.message});He.warn(r.message)}}}async function xs(t,e){var n;try{const s=(await Bi()).transaction(yt,"readwrite");return await s.objectStore(yt).put(e,Hi(t)),s.done}catch(r){if(r instanceof Oe)He.warn(r.message);else{const s=Te.create("idb-set",{originalErrorMessage:(n=r)===null||n===void 0?void 0:n.message});He.warn(s.message)}}}function Hi(t){return`${t.name}!${t.options.appId}`}/**
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
 */const of=1024,af=30*24*60*60*1e3;class lf{constructor(e){this.container=e,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new uf(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){const n=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),r=Es();if(this._heartbeatsCache===null&&(this._heartbeatsCache=await this._heartbeatsCachePromise),!(this._heartbeatsCache.lastSentHeartbeatDate===r||this._heartbeatsCache.heartbeats.some(s=>s.date===r)))return this._heartbeatsCache.heartbeats.push({date:r,agent:n}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(s=>{const i=new Date(s.date).valueOf();return Date.now()-i<=af}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,this._heartbeatsCache===null||this._heartbeatsCache.heartbeats.length===0)return"";const e=Es(),{heartbeatsToSend:n,unsentEntries:r}=cf(this._heartbeatsCache.heartbeats),s=Ri(JSON.stringify({version:2,heartbeats:n}));return this._heartbeatsCache.lastSentHeartbeatDate=e,r.length>0?(this._heartbeatsCache.heartbeats=r,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}}function Es(){return new Date().toISOString().substring(0,10)}function cf(t,e=of){const n=[];let r=t.slice();for(const s of t){const i=n.find(o=>o.agent===s.agent);if(i){if(i.dates.push(s.date),Is(n)>e){i.dates.pop();break}}else if(n.push({agent:s.agent,dates:[s.date]}),Is(n)>e){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class uf{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return zu()?Vu().then(()=>!0).catch(()=>!1):!1}async read(){return await this._canUseIndexedDBPromise?await sf(this.app)||{heartbeats:[]}:{heartbeats:[]}}async overwrite(e){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return xs(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return xs(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:[...s.heartbeats,...e.heartbeats]})}else return}}function Is(t){return Ri(JSON.stringify({version:2,heartbeats:t})).length}/**
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
 */function df(t){vt(new Xe("platform-logger",e=>new Id(e),"PRIVATE")),vt(new Xe("heartbeat",e=>new lf(e),"PRIVATE")),Je(nr,ws,t),Je(nr,ws,"esm2017"),Je("fire-js","")}df("");function yr(t,e){var n={};for(var r in t)Object.prototype.hasOwnProperty.call(t,r)&&e.indexOf(r)<0&&(n[r]=t[r]);if(t!=null&&typeof Object.getOwnPropertySymbols=="function")for(var s=0,r=Object.getOwnPropertySymbols(t);s<r.length;s++)e.indexOf(r[s])<0&&Object.prototype.propertyIsEnumerable.call(t,r[s])&&(n[r[s]]=t[r[s]]);return n}function zi(){return{["dependent-sdk-initialized-before-auth"]:"Another Firebase SDK was initialized and is trying to use Auth before Auth is initialized. Please be sure to call `initializeAuth` or `getAuth` before starting any other Firebase SDK."}}const ff=zi,Vi=new $t("auth","Firebase",zi());/**
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
 */const Ss=new Li("@firebase/auth");function Wt(t,...e){Ss.logLevel<=P.ERROR&&Ss.error(`Auth (${bn}): ${t}`,...e)}/**
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
 */function te(t,...e){throw _r(t,...e)}function ie(t,...e){return _r(t,...e)}function Wi(t,e,n){const r=Object.assign(Object.assign({},ff()),{[e]:n});return new $t("auth","Firebase",r).create(e,{appName:t.name})}function hf(t,e,n){const r=n;if(!(e instanceof r))throw r.name!==e.constructor.name&&te(t,"argument-error"),Wi(t,"argument-error",`Type of ${e.constructor.name} does not match expected instance.Did you pass a reference from a different Auth SDK?`)}function _r(t,...e){if(typeof t!="string"){const n=e[0],r=[...e.slice(1)];return r[0]&&(r[0].appName=t.name),t._errorFactory.create(n,...r)}return Vi.create(t,...e)}function E(t,e,...n){if(!t)throw _r(e,...n)}function he(t){const e="INTERNAL ASSERTION FAILED: "+t;throw Wt(e),new Error(e)}function ve(t,e){t||he(e)}/**
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
 */const ks=new Map;function ge(t){ve(t instanceof Function,"Expected a class definition");let e=ks.get(t);return e?(ve(e instanceof t,"Instance stored in cache mismatched with class"),e):(e=new t,ks.set(t,e),e)}/**
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
 */function gf(t,e){const n=ji(t,"auth");if(n.isInitialized()){const s=n.getImmediate(),i=n.getOptions();if(rn(i,e??{}))return s;te(s,"already-initialized")}return n.initialize({options:e})}function mf(t,e){const n=e?.persistence||[],r=(Array.isArray(n)?n:[n]).map(ge);e?.errorMap&&t._updateErrorMap(e.errorMap),t._initializeWithPersistence(r,e?.popupRedirectResolver)}/**
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
 */function ir(){var t;return typeof self<"u"&&((t=self.location)===null||t===void 0?void 0:t.href)||""}function pf(){return Ts()==="http:"||Ts()==="https:"}function Ts(){var t;return typeof self<"u"&&((t=self.location)===null||t===void 0?void 0:t.protocol)||null}/**
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
 */function bf(){return typeof navigator<"u"&&navigator&&"onLine"in navigator&&typeof navigator.onLine=="boolean"&&(pf()||Fu()||"connection"in navigator)?navigator.onLine:!0}function vf(){if(typeof navigator>"u")return null;const t=navigator;return t.languages&&t.languages[0]||t.language||null}/**
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
 */class At{constructor(e,n){this.shortDelay=e,this.longDelay=n,ve(n>e,"Short delay should be less than long delay!"),this.isMobile=ju()||Bu()}get(){return bf()?this.isMobile?this.longDelay:this.shortDelay:Math.min(5e3,this.shortDelay)}}/**
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
 */function wr(t,e){ve(t.emulator,"Emulator should always be set here");const{url:n}=t.emulator;return e?`${n}${e.startsWith("/")?e.slice(1):e}`:n}/**
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
 */class Ji{static initialize(e,n,r){this.fetchImpl=e,n&&(this.headersImpl=n),r&&(this.responseImpl=r)}static fetch(){if(this.fetchImpl)return this.fetchImpl;if(typeof self<"u"&&"fetch"in self)return self.fetch;he("Could not find fetch implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static headers(){if(this.headersImpl)return this.headersImpl;if(typeof self<"u"&&"Headers"in self)return self.Headers;he("Could not find Headers implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static response(){if(this.responseImpl)return this.responseImpl;if(typeof self<"u"&&"Response"in self)return self.Response;he("Could not find Response implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}}/**
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
 */const yf={CREDENTIAL_MISMATCH:"custom-token-mismatch",MISSING_CUSTOM_TOKEN:"internal-error",INVALID_IDENTIFIER:"invalid-email",MISSING_CONTINUE_URI:"internal-error",INVALID_PASSWORD:"wrong-password",MISSING_PASSWORD:"internal-error",EMAIL_EXISTS:"email-already-in-use",PASSWORD_LOGIN_DISABLED:"operation-not-allowed",INVALID_IDP_RESPONSE:"invalid-credential",INVALID_PENDING_TOKEN:"invalid-credential",FEDERATED_USER_ID_ALREADY_LINKED:"credential-already-in-use",MISSING_REQ_TYPE:"internal-error",EMAIL_NOT_FOUND:"user-not-found",RESET_PASSWORD_EXCEED_LIMIT:"too-many-requests",EXPIRED_OOB_CODE:"expired-action-code",INVALID_OOB_CODE:"invalid-action-code",MISSING_OOB_CODE:"internal-error",CREDENTIAL_TOO_OLD_LOGIN_AGAIN:"requires-recent-login",INVALID_ID_TOKEN:"invalid-user-token",TOKEN_EXPIRED:"user-token-expired",USER_NOT_FOUND:"user-token-expired",TOO_MANY_ATTEMPTS_TRY_LATER:"too-many-requests",INVALID_CODE:"invalid-verification-code",INVALID_SESSION_INFO:"invalid-verification-id",INVALID_TEMPORARY_PROOF:"invalid-credential",MISSING_SESSION_INFO:"missing-verification-id",SESSION_EXPIRED:"code-expired",MISSING_ANDROID_PACKAGE_NAME:"missing-android-pkg-name",UNAUTHORIZED_DOMAIN:"unauthorized-continue-uri",INVALID_OAUTH_CLIENT_ID:"invalid-oauth-client-id",ADMIN_ONLY_OPERATION:"admin-restricted-operation",INVALID_MFA_PENDING_CREDENTIAL:"invalid-multi-factor-session",MFA_ENROLLMENT_NOT_FOUND:"multi-factor-info-not-found",MISSING_MFA_ENROLLMENT_ID:"missing-multi-factor-info",MISSING_MFA_PENDING_CREDENTIAL:"missing-multi-factor-session",SECOND_FACTOR_EXISTS:"second-factor-already-in-use",SECOND_FACTOR_LIMIT_EXCEEDED:"maximum-second-factor-count-exceeded",BLOCKING_FUNCTION_ERROR_RESPONSE:"internal-error"};/**
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
 */const _f=new At(3e4,6e4);function Ot(t,e){return t.tenantId&&!e.tenantId?Object.assign(Object.assign({},e),{tenantId:t.tenantId}):e}async function nt(t,e,n,r,s={}){return qi(t,s,async()=>{let i={},o={};r&&(e==="GET"?o=r:i={body:JSON.stringify(r)});const a=Ct(Object.assign({key:t.config.apiKey},o)).slice(1),c=await t._getAdditionalHeaders();return c["Content-Type"]="application/json",t.languageCode&&(c["X-Firebase-Locale"]=t.languageCode),Ji.fetch()(Gi(t,t.config.apiHost,n,a),Object.assign({method:e,headers:c,referrerPolicy:"no-referrer"},i))})}async function qi(t,e,n){t._canInitEmulator=!1;const r=Object.assign(Object.assign({},yf),e);try{const s=new wf(t),i=await Promise.race([n(),s.promise]);s.clearNetworkTimeout();const o=await i.json();if("needConfirmation"in o)throw Ft(t,"account-exists-with-different-credential",o);if(i.ok&&!("errorMessage"in o))return o;{const a=i.ok?o.errorMessage:o.error.message,[c,l]=a.split(" : ");if(c==="FEDERATED_USER_ID_ALREADY_LINKED")throw Ft(t,"credential-already-in-use",o);if(c==="EMAIL_EXISTS")throw Ft(t,"email-already-in-use",o);if(c==="USER_DISABLED")throw Ft(t,"user-disabled",o);const u=r[c]||c.toLowerCase().replace(/[_\s]+/g,"-");if(l)throw Wi(t,u,l);te(t,u)}}catch(s){if(s instanceof Oe)throw s;te(t,"network-request-failed")}}async function vn(t,e,n,r,s={}){const i=await nt(t,e,n,r,s);return"mfaPendingCredential"in i&&te(t,"multi-factor-auth-required",{_serverResponse:i}),i}function Gi(t,e,n,r){const s=`${e}${n}?${r}`;return t.config.emulator?wr(t.config,s):`${t.config.apiScheme}://${s}`}class wf{constructor(e){this.auth=e,this.timer=null,this.promise=new Promise((n,r)=>{this.timer=setTimeout(()=>r(ie(this.auth,"network-request-failed")),_f.get())})}clearNetworkTimeout(){clearTimeout(this.timer)}}function Ft(t,e,n){const r={appName:t.name};n.email&&(r.email=n.email),n.phoneNumber&&(r.phoneNumber=n.phoneNumber);const s=ie(t,e,r);return s.customData._tokenResponse=n,s}/**
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
 */async function xf(t,e){return nt(t,"POST","/v1/accounts:delete",e)}async function Ef(t,e){return nt(t,"POST","/v1/accounts:lookup",e)}/**
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
 */function gt(t){if(!!t)try{const e=new Date(Number(t));if(!isNaN(e.getTime()))return e.toUTCString()}catch{}}async function If(t,e=!1){const n=ae(t),r=await n.getIdToken(e),s=xr(r);E(s&&s.exp&&s.auth_time&&s.iat,n.auth,"internal-error");const i=typeof s.firebase=="object"?s.firebase:void 0,o=i?.sign_in_provider;return{claims:s,token:r,authTime:gt(Hn(s.auth_time)),issuedAtTime:gt(Hn(s.iat)),expirationTime:gt(Hn(s.exp)),signInProvider:o||null,signInSecondFactor:i?.sign_in_second_factor||null}}function Hn(t){return Number(t)*1e3}function xr(t){var e;const[n,r,s]=t.split(".");if(n===void 0||r===void 0||s===void 0)return Wt("JWT malformed, contained fewer than 3 sections"),null;try{const i=Di(r);return i?JSON.parse(i):(Wt("Failed to decode base64 JWT payload"),null)}catch(i){return Wt("Caught error parsing JWT payload as JSON",(e=i)===null||e===void 0?void 0:e.toString()),null}}function Sf(t){const e=xr(t);return E(e,"internal-error"),E(typeof e.exp<"u","internal-error"),E(typeof e.iat<"u","internal-error"),Number(e.exp)-Number(e.iat)}/**
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
 */async function _t(t,e,n=!1){if(n)return e;try{return await e}catch(r){throw r instanceof Oe&&kf(r)&&t.auth.currentUser===t&&await t.auth.signOut(),r}}function kf({code:t}){return t==="auth/user-disabled"||t==="auth/user-token-expired"}/**
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
 */class Tf{constructor(e){this.user=e,this.isRunning=!1,this.timerId=null,this.errorBackoff=3e4}_start(){this.isRunning||(this.isRunning=!0,this.schedule())}_stop(){!this.isRunning||(this.isRunning=!1,this.timerId!==null&&clearTimeout(this.timerId))}getInterval(e){var n;if(e){const r=this.errorBackoff;return this.errorBackoff=Math.min(this.errorBackoff*2,96e4),r}else{this.errorBackoff=3e4;const s=((n=this.user.stsTokenManager.expirationTime)!==null&&n!==void 0?n:0)-Date.now()-3e5;return Math.max(0,s)}}schedule(e=!1){if(!this.isRunning)return;const n=this.getInterval(e);this.timerId=setTimeout(async()=>{await this.iteration()},n)}async iteration(){var e;try{await this.user.getIdToken(!0)}catch(n){((e=n)===null||e===void 0?void 0:e.code)==="auth/network-request-failed"&&this.schedule(!0);return}this.schedule()}}/**
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
 */class Ki{constructor(e,n){this.createdAt=e,this.lastLoginAt=n,this._initializeTime()}_initializeTime(){this.lastSignInTime=gt(this.lastLoginAt),this.creationTime=gt(this.createdAt)}_copy(e){this.createdAt=e.createdAt,this.lastLoginAt=e.lastLoginAt,this._initializeTime()}toJSON(){return{createdAt:this.createdAt,lastLoginAt:this.lastLoginAt}}}/**
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
 */async function on(t){var e;const n=t.auth,r=await t.getIdToken(),s=await _t(t,Ef(n,{idToken:r}));E(s?.users.length,n,"internal-error");const i=s.users[0];t._notifyReloadListener(i);const o=!((e=i.providerUserInfo)===null||e===void 0)&&e.length?Af(i.providerUserInfo):[],a=Cf(t.providerData,o),c=t.isAnonymous,l=!(t.email&&i.passwordHash)&&!a?.length,u=c?l:!1,p={uid:i.localId,displayName:i.displayName||null,photoURL:i.photoUrl||null,email:i.email||null,emailVerified:i.emailVerified||!1,phoneNumber:i.phoneNumber||null,tenantId:i.tenantId||null,providerData:a,metadata:new Ki(i.createdAt,i.lastLoginAt),isAnonymous:u};Object.assign(t,p)}async function $f(t){const e=ae(t);await on(e),await e.auth._persistUserIfCurrent(e),e.auth._notifyListenersIfCurrent(e)}function Cf(t,e){return[...t.filter(r=>!e.some(s=>s.providerId===r.providerId)),...e]}function Af(t){return t.map(e=>{var{providerId:n}=e,r=yr(e,["providerId"]);return{providerId:n,uid:r.rawId||"",displayName:r.displayName||null,email:r.email||null,phoneNumber:r.phoneNumber||null,photoURL:r.photoUrl||null}})}/**
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
 */async function Of(t,e){const n=await qi(t,{},async()=>{const r=Ct({grant_type:"refresh_token",refresh_token:e}).slice(1),{tokenApiHost:s,apiKey:i}=t.config,o=Gi(t,s,"/v1/token",`key=${i}`),a=await t._getAdditionalHeaders();return a["Content-Type"]="application/x-www-form-urlencoded",Ji.fetch()(o,{method:"POST",headers:a,body:r})});return{accessToken:n.access_token,expiresIn:n.expires_in,refreshToken:n.refresh_token}}/**
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
 */class wt{constructor(){this.refreshToken=null,this.accessToken=null,this.expirationTime=null}get isExpired(){return!this.expirationTime||Date.now()>this.expirationTime-3e4}updateFromServerResponse(e){E(e.idToken,"internal-error"),E(typeof e.idToken<"u","internal-error"),E(typeof e.refreshToken<"u","internal-error");const n="expiresIn"in e&&typeof e.expiresIn<"u"?Number(e.expiresIn):Sf(e.idToken);this.updateTokensAndExpiration(e.idToken,e.refreshToken,n)}async getToken(e,n=!1){return E(!this.accessToken||this.refreshToken,e,"user-token-expired"),!n&&this.accessToken&&!this.isExpired?this.accessToken:this.refreshToken?(await this.refresh(e,this.refreshToken),this.accessToken):null}clearRefreshToken(){this.refreshToken=null}async refresh(e,n){const{accessToken:r,refreshToken:s,expiresIn:i}=await Of(e,n);this.updateTokensAndExpiration(r,s,Number(i))}updateTokensAndExpiration(e,n,r){this.refreshToken=n||null,this.accessToken=e||null,this.expirationTime=Date.now()+r*1e3}static fromJSON(e,n){const{refreshToken:r,accessToken:s,expirationTime:i}=n,o=new wt;return r&&(E(typeof r=="string","internal-error",{appName:e}),o.refreshToken=r),s&&(E(typeof s=="string","internal-error",{appName:e}),o.accessToken=s),i&&(E(typeof i=="number","internal-error",{appName:e}),o.expirationTime=i),o}toJSON(){return{refreshToken:this.refreshToken,accessToken:this.accessToken,expirationTime:this.expirationTime}}_assign(e){this.accessToken=e.accessToken,this.refreshToken=e.refreshToken,this.expirationTime=e.expirationTime}_clone(){return Object.assign(new wt,this.toJSON())}_performRefresh(){return he("not implemented")}}/**
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
 */function Ee(t,e){E(typeof t=="string"||typeof t>"u","internal-error",{appName:e})}class Fe{constructor(e){var{uid:n,auth:r,stsTokenManager:s}=e,i=yr(e,["uid","auth","stsTokenManager"]);this.providerId="firebase",this.proactiveRefresh=new Tf(this),this.reloadUserInfo=null,this.reloadListener=null,this.uid=n,this.auth=r,this.stsTokenManager=s,this.accessToken=s.accessToken,this.displayName=i.displayName||null,this.email=i.email||null,this.emailVerified=i.emailVerified||!1,this.phoneNumber=i.phoneNumber||null,this.photoURL=i.photoURL||null,this.isAnonymous=i.isAnonymous||!1,this.tenantId=i.tenantId||null,this.providerData=i.providerData?[...i.providerData]:[],this.metadata=new Ki(i.createdAt||void 0,i.lastLoginAt||void 0)}async getIdToken(e){const n=await _t(this,this.stsTokenManager.getToken(this.auth,e));return E(n,this.auth,"internal-error"),this.accessToken!==n&&(this.accessToken=n,await this.auth._persistUserIfCurrent(this),this.auth._notifyListenersIfCurrent(this)),n}getIdTokenResult(e){return If(this,e)}reload(){return $f(this)}_assign(e){this!==e&&(E(this.uid===e.uid,this.auth,"internal-error"),this.displayName=e.displayName,this.photoURL=e.photoURL,this.email=e.email,this.emailVerified=e.emailVerified,this.phoneNumber=e.phoneNumber,this.isAnonymous=e.isAnonymous,this.tenantId=e.tenantId,this.providerData=e.providerData.map(n=>Object.assign({},n)),this.metadata._copy(e.metadata),this.stsTokenManager._assign(e.stsTokenManager))}_clone(e){return new Fe(Object.assign(Object.assign({},this),{auth:e,stsTokenManager:this.stsTokenManager._clone()}))}_onReload(e){E(!this.reloadListener,this.auth,"internal-error"),this.reloadListener=e,this.reloadUserInfo&&(this._notifyReloadListener(this.reloadUserInfo),this.reloadUserInfo=null)}_notifyReloadListener(e){this.reloadListener?this.reloadListener(e):this.reloadUserInfo=e}_startProactiveRefresh(){this.proactiveRefresh._start()}_stopProactiveRefresh(){this.proactiveRefresh._stop()}async _updateTokensIfNecessary(e,n=!1){let r=!1;e.idToken&&e.idToken!==this.stsTokenManager.accessToken&&(this.stsTokenManager.updateFromServerResponse(e),r=!0),n&&await on(this),await this.auth._persistUserIfCurrent(this),r&&this.auth._notifyListenersIfCurrent(this)}async delete(){const e=await this.getIdToken();return await _t(this,xf(this.auth,{idToken:e})),this.stsTokenManager.clearRefreshToken(),this.auth.signOut()}toJSON(){return Object.assign(Object.assign({uid:this.uid,email:this.email||void 0,emailVerified:this.emailVerified,displayName:this.displayName||void 0,isAnonymous:this.isAnonymous,photoURL:this.photoURL||void 0,phoneNumber:this.phoneNumber||void 0,tenantId:this.tenantId||void 0,providerData:this.providerData.map(e=>Object.assign({},e)),stsTokenManager:this.stsTokenManager.toJSON(),_redirectEventId:this._redirectEventId},this.metadata.toJSON()),{apiKey:this.auth.config.apiKey,appName:this.auth.name})}get refreshToken(){return this.stsTokenManager.refreshToken||""}static _fromJSON(e,n){var r,s,i,o,a,c,l,u;const p=(r=n.displayName)!==null&&r!==void 0?r:void 0,v=(s=n.email)!==null&&s!==void 0?s:void 0,b=(i=n.phoneNumber)!==null&&i!==void 0?i:void 0,g=(o=n.photoURL)!==null&&o!==void 0?o:void 0,m=(a=n.tenantId)!==null&&a!==void 0?a:void 0,x=(c=n._redirectEventId)!==null&&c!==void 0?c:void 0,_=(l=n.createdAt)!==null&&l!==void 0?l:void 0,S=(u=n.lastLoginAt)!==null&&u!==void 0?u:void 0,{uid:T,emailVerified:O,isAnonymous:N,providerData:X,stsTokenManager:G}=n;E(T&&G,e,"internal-error");const le=wt.fromJSON(this.name,G);E(typeof T=="string",e,"internal-error"),Ee(p,e.name),Ee(v,e.name),E(typeof O=="boolean",e,"internal-error"),E(typeof N=="boolean",e,"internal-error"),Ee(b,e.name),Ee(g,e.name),Ee(m,e.name),Ee(x,e.name),Ee(_,e.name),Ee(S,e.name);const C=new Fe({uid:T,auth:e,email:v,emailVerified:O,displayName:p,isAnonymous:N,photoURL:g,phoneNumber:b,tenantId:m,stsTokenManager:le,createdAt:_,lastLoginAt:S});return X&&Array.isArray(X)&&(C.providerData=X.map(R=>Object.assign({},R))),x&&(C._redirectEventId=x),C}static async _fromIdTokenResponse(e,n,r=!1){const s=new wt;s.updateFromServerResponse(n);const i=new Fe({uid:n.localId,auth:e,stsTokenManager:s,isAnonymous:r});return await on(i),i}}/**
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
 */class Xi{constructor(){this.type="NONE",this.storage={}}async _isAvailable(){return!0}async _set(e,n){this.storage[e]=n}async _get(e){const n=this.storage[e];return n===void 0?null:n}async _remove(e){delete this.storage[e]}_addListener(e,n){}_removeListener(e,n){}}Xi.type="NONE";const $s=Xi;/**
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
 */function Jt(t,e,n){return`firebase:${t}:${e}:${n}`}class qe{constructor(e,n,r){this.persistence=e,this.auth=n,this.userKey=r;const{config:s,name:i}=this.auth;this.fullUserKey=Jt(this.userKey,s.apiKey,i),this.fullPersistenceKey=Jt("persistence",s.apiKey,i),this.boundEventHandler=n._onStorageEvent.bind(n),this.persistence._addListener(this.fullUserKey,this.boundEventHandler)}setCurrentUser(e){return this.persistence._set(this.fullUserKey,e.toJSON())}async getCurrentUser(){const e=await this.persistence._get(this.fullUserKey);return e?Fe._fromJSON(this.auth,e):null}removeCurrentUser(){return this.persistence._remove(this.fullUserKey)}savePersistenceForRedirect(){return this.persistence._set(this.fullPersistenceKey,this.persistence.type)}async setPersistence(e){if(this.persistence===e)return;const n=await this.getCurrentUser();if(await this.removeCurrentUser(),this.persistence=e,n)return this.setCurrentUser(n)}delete(){this.persistence._removeListener(this.fullUserKey,this.boundEventHandler)}static async create(e,n,r="authUser"){if(!n.length)return new qe(ge($s),e,r);const s=(await Promise.all(n.map(async l=>{if(await l._isAvailable())return l}))).filter(l=>l);let i=s[0]||ge($s);const o=Jt(r,e.config.apiKey,e.name);let a=null;for(const l of n)try{const u=await l._get(o);if(u){const p=Fe._fromJSON(e,u);l!==i&&(a=p),i=l;break}}catch{}const c=s.filter(l=>l._shouldAllowMigration);return!i._shouldAllowMigration||!c.length?new qe(i,e,r):(i=c[0],a&&await i._set(o,a.toJSON()),await Promise.all(n.map(async l=>{if(l!==i)try{await l._remove(o)}catch{}})),new qe(i,e,r))}}/**
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
 */function Cs(t){const e=t.toLowerCase();if(e.includes("opera/")||e.includes("opr/")||e.includes("opios/"))return"Opera";if(Zi(e))return"IEMobile";if(e.includes("msie")||e.includes("trident/"))return"IE";if(e.includes("edge/"))return"Edge";if(Yi(e))return"Firefox";if(e.includes("silk/"))return"Silk";if(to(e))return"Blackberry";if(no(e))return"Webos";if(Er(e))return"Safari";if((e.includes("chrome/")||Qi(e))&&!e.includes("edge/"))return"Chrome";if(eo(e))return"Android";{const n=/([a-zA-Z\d\.]+)\/[a-zA-Z\d\.]*$/,r=t.match(n);if(r?.length===2)return r[1]}return"Other"}function Yi(t=q()){return/firefox\//i.test(t)}function Er(t=q()){const e=t.toLowerCase();return e.includes("safari/")&&!e.includes("chrome/")&&!e.includes("crios/")&&!e.includes("android")}function Qi(t=q()){return/crios\//i.test(t)}function Zi(t=q()){return/iemobile/i.test(t)}function eo(t=q()){return/android/i.test(t)}function to(t=q()){return/blackberry/i.test(t)}function no(t=q()){return/webos/i.test(t)}function yn(t=q()){return/iphone|ipad|ipod/i.test(t)||/macintosh/i.test(t)&&/mobile/i.test(t)}function Nf(t=q()){var e;return yn(t)&&!!(!((e=window.navigator)===null||e===void 0)&&e.standalone)}function Rf(){return Hu()&&document.documentMode===10}function ro(t=q()){return yn(t)||eo(t)||no(t)||to(t)||/windows phone/i.test(t)||Zi(t)}function Df(){try{return!!(window&&window!==window.top)}catch{return!1}}/**
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
 */function so(t,e=[]){let n;switch(t){case"Browser":n=Cs(q());break;case"Worker":n=`${Cs(q())}-${t}`;break;default:n=t}const r=e.length?e.join(","):"FirebaseCore-web";return`${n}/JsCore/${bn}/${r}`}/**
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
 */class Pf{constructor(e){this.auth=e,this.queue=[]}pushCallback(e,n){const r=i=>new Promise((o,a)=>{try{const c=e(i);o(c)}catch(c){a(c)}});r.onAbort=n,this.queue.push(r);const s=this.queue.length-1;return()=>{this.queue[s]=()=>Promise.resolve()}}async runMiddleware(e){var n;if(this.auth.currentUser===e)return;const r=[];try{for(const s of this.queue)await s(e),s.onAbort&&r.push(s.onAbort)}catch(s){r.reverse();for(const i of r)try{i()}catch{}throw this.auth._errorFactory.create("login-blocked",{originalMessage:(n=s)===null||n===void 0?void 0:n.message})}}}/**
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
 */class Lf{constructor(e,n,r){this.app=e,this.heartbeatServiceProvider=n,this.config=r,this.currentUser=null,this.emulatorConfig=null,this.operations=Promise.resolve(),this.authStateSubscription=new As(this),this.idTokenSubscription=new As(this),this.beforeStateQueue=new Pf(this),this.redirectUser=null,this.isProactiveRefreshEnabled=!1,this._canInitEmulator=!0,this._isInitialized=!1,this._deleted=!1,this._initializationPromise=null,this._popupRedirectResolver=null,this._errorFactory=Vi,this.lastNotifiedUid=void 0,this.languageCode=null,this.tenantId=null,this.settings={appVerificationDisabledForTesting:!1},this.frameworks=[],this.name=e.name,this.clientVersion=r.sdkClientVersion}_initializeWithPersistence(e,n){return n&&(this._popupRedirectResolver=ge(n)),this._initializationPromise=this.queue(async()=>{var r,s;if(!this._deleted&&(this.persistenceManager=await qe.create(this,e),!this._deleted)){if(!((r=this._popupRedirectResolver)===null||r===void 0)&&r._shouldInitProactively)try{await this._popupRedirectResolver._initialize(this)}catch{}await this.initializeCurrentUser(n),this.lastNotifiedUid=((s=this.currentUser)===null||s===void 0?void 0:s.uid)||null,!this._deleted&&(this._isInitialized=!0)}}),this._initializationPromise}async _onStorageEvent(){if(this._deleted)return;const e=await this.assertedPersistence.getCurrentUser();if(!(!this.currentUser&&!e)){if(this.currentUser&&e&&this.currentUser.uid===e.uid){this._currentUser._assign(e),await this.currentUser.getIdToken();return}await this._updateCurrentUser(e,!0)}}async initializeCurrentUser(e){var n;const r=await this.assertedPersistence.getCurrentUser();let s=r,i=!1;if(e&&this.config.authDomain){await this.getOrInitRedirectPersistenceManager();const o=(n=this.redirectUser)===null||n===void 0?void 0:n._redirectEventId,a=s?._redirectEventId,c=await this.tryRedirectSignIn(e);(!o||o===a)&&c?.user&&(s=c.user,i=!0)}if(!s)return this.directlySetCurrentUser(null);if(!s._redirectEventId){if(i)try{await this.beforeStateQueue.runMiddleware(s)}catch(o){s=r,this._popupRedirectResolver._overrideRedirectResult(this,()=>Promise.reject(o))}return s?this.reloadAndSetCurrentUserOrClear(s):this.directlySetCurrentUser(null)}return E(this._popupRedirectResolver,this,"argument-error"),await this.getOrInitRedirectPersistenceManager(),this.redirectUser&&this.redirectUser._redirectEventId===s._redirectEventId?this.directlySetCurrentUser(s):this.reloadAndSetCurrentUserOrClear(s)}async tryRedirectSignIn(e){let n=null;try{n=await this._popupRedirectResolver._completeRedirectFn(this,e,!0)}catch{await this._setRedirectUser(null)}return n}async reloadAndSetCurrentUserOrClear(e){var n;try{await on(e)}catch(r){if(((n=r)===null||n===void 0?void 0:n.code)!=="auth/network-request-failed")return this.directlySetCurrentUser(null)}return this.directlySetCurrentUser(e)}useDeviceLanguage(){this.languageCode=vf()}async _delete(){this._deleted=!0}async updateCurrentUser(e){const n=e?ae(e):null;return n&&E(n.auth.config.apiKey===this.config.apiKey,this,"invalid-user-token"),this._updateCurrentUser(n&&n._clone(this))}async _updateCurrentUser(e,n=!1){if(!this._deleted)return e&&E(this.tenantId===e.tenantId,this,"tenant-id-mismatch"),n||await this.beforeStateQueue.runMiddleware(e),this.queue(async()=>{await this.directlySetCurrentUser(e),this.notifyAuthListeners()})}async signOut(){return await this.beforeStateQueue.runMiddleware(null),(this.redirectPersistenceManager||this._popupRedirectResolver)&&await this._setRedirectUser(null),this._updateCurrentUser(null,!0)}setPersistence(e){return this.queue(async()=>{await this.assertedPersistence.setPersistence(ge(e))})}_getPersistence(){return this.assertedPersistence.persistence.type}_updateErrorMap(e){this._errorFactory=new $t("auth","Firebase",e())}onAuthStateChanged(e,n,r){return this.registerStateListener(this.authStateSubscription,e,n,r)}beforeAuthStateChanged(e,n){return this.beforeStateQueue.pushCallback(e,n)}onIdTokenChanged(e,n,r){return this.registerStateListener(this.idTokenSubscription,e,n,r)}toJSON(){var e;return{apiKey:this.config.apiKey,authDomain:this.config.authDomain,appName:this.name,currentUser:(e=this._currentUser)===null||e===void 0?void 0:e.toJSON()}}async _setRedirectUser(e,n){const r=await this.getOrInitRedirectPersistenceManager(n);return e===null?r.removeCurrentUser():r.setCurrentUser(e)}async getOrInitRedirectPersistenceManager(e){if(!this.redirectPersistenceManager){const n=e&&ge(e)||this._popupRedirectResolver;E(n,this,"argument-error"),this.redirectPersistenceManager=await qe.create(this,[ge(n._redirectPersistence)],"redirectUser"),this.redirectUser=await this.redirectPersistenceManager.getCurrentUser()}return this.redirectPersistenceManager}async _redirectUserForId(e){var n,r;return this._isInitialized&&await this.queue(async()=>{}),((n=this._currentUser)===null||n===void 0?void 0:n._redirectEventId)===e?this._currentUser:((r=this.redirectUser)===null||r===void 0?void 0:r._redirectEventId)===e?this.redirectUser:null}async _persistUserIfCurrent(e){if(e===this.currentUser)return this.queue(async()=>this.directlySetCurrentUser(e))}_notifyListenersIfCurrent(e){e===this.currentUser&&this.notifyAuthListeners()}_key(){return`${this.config.authDomain}:${this.config.apiKey}:${this.name}`}_startProactiveRefresh(){this.isProactiveRefreshEnabled=!0,this.currentUser&&this._currentUser._startProactiveRefresh()}_stopProactiveRefresh(){this.isProactiveRefreshEnabled=!1,this.currentUser&&this._currentUser._stopProactiveRefresh()}get _currentUser(){return this.currentUser}notifyAuthListeners(){var e,n;if(!this._isInitialized)return;this.idTokenSubscription.next(this.currentUser);const r=(n=(e=this.currentUser)===null||e===void 0?void 0:e.uid)!==null&&n!==void 0?n:null;this.lastNotifiedUid!==r&&(this.lastNotifiedUid=r,this.authStateSubscription.next(this.currentUser))}registerStateListener(e,n,r,s){if(this._deleted)return()=>{};const i=typeof n=="function"?n:n.next.bind(n),o=this._isInitialized?Promise.resolve():this._initializationPromise;return E(o,this,"internal-error"),o.then(()=>i(this.currentUser)),typeof n=="function"?e.addObserver(n,r,s):e.addObserver(n)}async directlySetCurrentUser(e){this.currentUser&&this.currentUser!==e&&this._currentUser._stopProactiveRefresh(),e&&this.isProactiveRefreshEnabled&&e._startProactiveRefresh(),this.currentUser=e,e?await this.assertedPersistence.setCurrentUser(e):await this.assertedPersistence.removeCurrentUser()}queue(e){return this.operations=this.operations.then(e,e),this.operations}get assertedPersistence(){return E(this.persistenceManager,this,"internal-error"),this.persistenceManager}_logFramework(e){!e||this.frameworks.includes(e)||(this.frameworks.push(e),this.frameworks.sort(),this.clientVersion=so(this.config.clientPlatform,this._getFrameworks()))}_getFrameworks(){return this.frameworks}async _getAdditionalHeaders(){var e;const n={["X-Client-Version"]:this.clientVersion};this.app.options.appId&&(n["X-Firebase-gmpid"]=this.app.options.appId);const r=await((e=this.heartbeatServiceProvider.getImmediate({optional:!0}))===null||e===void 0?void 0:e.getHeartbeatsHeader());return r&&(n["X-Firebase-Client"]=r),n}}function Nt(t){return ae(t)}class As{constructor(e){this.auth=e,this.observer=null,this.addObserver=nd(n=>this.observer=n)}get next(){return E(this.observer,this.auth,"internal-error"),this.observer.next.bind(this.observer)}}function Mf(t,e,n){const r=Nt(t);E(r._canInitEmulator,r,"emulator-config-failed"),E(/^https?:\/\//.test(e),r,"invalid-emulator-scheme");const s=!!n?.disableWarnings,i=io(e),{host:o,port:a}=Uf(e),c=a===null?"":`:${a}`;r.config.emulator={url:`${i}//${o}${c}/`},r.settings.appVerificationDisabledForTesting=!0,r.emulatorConfig=Object.freeze({host:o,port:a,protocol:i.replace(":",""),options:Object.freeze({disableWarnings:s})}),s||jf()}function io(t){const e=t.indexOf(":");return e<0?"":t.substr(0,e+1)}function Uf(t){const e=io(t),n=/(\/\/)?([^?#/]+)/.exec(t.substr(e.length));if(!n)return{host:"",port:null};const r=n[2].split("@").pop()||"",s=/^(\[[^\]]+\])(:|$)/.exec(r);if(s){const i=s[1];return{host:i,port:Os(r.substr(i.length+1))}}else{const[i,o]=r.split(":");return{host:i,port:Os(o)}}}function Os(t){if(!t)return null;const e=Number(t);return isNaN(e)?null:e}function jf(){function t(){const e=document.createElement("p"),n=e.style;e.innerText="Running in emulator mode. Do not use with production credentials.",n.position="fixed",n.width="100%",n.backgroundColor="#ffffff",n.border=".1em solid #000000",n.color="#b50000",n.bottom="0px",n.left="0px",n.margin="0px",n.zIndex="10000",n.textAlign="center",e.classList.add("firebase-emulator-warning"),document.body.appendChild(e)}typeof console<"u"&&typeof console.info=="function"&&console.info("WARNING: You are using the Auth Emulator, which is intended for local testing only.  Do not use with production credentials."),typeof window<"u"&&typeof document<"u"&&(document.readyState==="loading"?window.addEventListener("DOMContentLoaded",t):t())}/**
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
 */class Ir{constructor(e,n){this.providerId=e,this.signInMethod=n}toJSON(){return he("not implemented")}_getIdTokenResponse(e){return he("not implemented")}_linkToIdToken(e,n){return he("not implemented")}_getReauthenticationResolver(e){return he("not implemented")}}async function Ff(t,e){return nt(t,"POST","/v1/accounts:update",e)}/**
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
 */async function Bf(t,e){return vn(t,"POST","/v1/accounts:signInWithPassword",Ot(t,e))}async function Hf(t,e){return nt(t,"POST","/v1/accounts:sendOobCode",Ot(t,e))}async function zf(t,e){return Hf(t,e)}/**
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
 */async function Vf(t,e){return vn(t,"POST","/v1/accounts:signInWithEmailLink",Ot(t,e))}async function Wf(t,e){return vn(t,"POST","/v1/accounts:signInWithEmailLink",Ot(t,e))}/**
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
 */class xt extends Ir{constructor(e,n,r,s=null){super("password",r),this._email=e,this._password=n,this._tenantId=s}static _fromEmailAndPassword(e,n){return new xt(e,n,"password")}static _fromEmailAndCode(e,n,r=null){return new xt(e,n,"emailLink",r)}toJSON(){return{email:this._email,password:this._password,signInMethod:this.signInMethod,tenantId:this._tenantId}}static fromJSON(e){const n=typeof e=="string"?JSON.parse(e):e;if(n?.email&&n?.password){if(n.signInMethod==="password")return this._fromEmailAndPassword(n.email,n.password);if(n.signInMethod==="emailLink")return this._fromEmailAndCode(n.email,n.password,n.tenantId)}return null}async _getIdTokenResponse(e){switch(this.signInMethod){case"password":return Bf(e,{returnSecureToken:!0,email:this._email,password:this._password});case"emailLink":return Vf(e,{email:this._email,oobCode:this._password});default:te(e,"internal-error")}}async _linkToIdToken(e,n){switch(this.signInMethod){case"password":return Ff(e,{idToken:n,returnSecureToken:!0,email:this._email,password:this._password});case"emailLink":return Wf(e,{idToken:n,email:this._email,oobCode:this._password});default:te(e,"internal-error")}}_getReauthenticationResolver(e){return this._getIdTokenResponse(e)}}/**
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
 */async function Ge(t,e){return vn(t,"POST","/v1/accounts:signInWithIdp",Ot(t,e))}/**
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
 */const Jf="http://localhost";class ze extends Ir{constructor(){super(...arguments),this.pendingToken=null}static _fromParams(e){const n=new ze(e.providerId,e.signInMethod);return e.idToken||e.accessToken?(e.idToken&&(n.idToken=e.idToken),e.accessToken&&(n.accessToken=e.accessToken),e.nonce&&!e.pendingToken&&(n.nonce=e.nonce),e.pendingToken&&(n.pendingToken=e.pendingToken)):e.oauthToken&&e.oauthTokenSecret?(n.accessToken=e.oauthToken,n.secret=e.oauthTokenSecret):te("argument-error"),n}toJSON(){return{idToken:this.idToken,accessToken:this.accessToken,secret:this.secret,nonce:this.nonce,pendingToken:this.pendingToken,providerId:this.providerId,signInMethod:this.signInMethod}}static fromJSON(e){const n=typeof e=="string"?JSON.parse(e):e,{providerId:r,signInMethod:s}=n,i=yr(n,["providerId","signInMethod"]);if(!r||!s)return null;const o=new ze(r,s);return o.idToken=i.idToken||void 0,o.accessToken=i.accessToken||void 0,o.secret=i.secret,o.nonce=i.nonce,o.pendingToken=i.pendingToken||null,o}_getIdTokenResponse(e){const n=this.buildRequest();return Ge(e,n)}_linkToIdToken(e,n){const r=this.buildRequest();return r.idToken=n,Ge(e,r)}_getReauthenticationResolver(e){const n=this.buildRequest();return n.autoCreate=!1,Ge(e,n)}buildRequest(){const e={requestUri:Jf,returnSecureToken:!0};if(this.pendingToken)e.pendingToken=this.pendingToken;else{const n={};this.idToken&&(n.id_token=this.idToken),this.accessToken&&(n.access_token=this.accessToken),this.secret&&(n.oauth_token_secret=this.secret),n.providerId=this.providerId,this.nonce&&!this.pendingToken&&(n.nonce=this.nonce),e.postBody=Ct(n)}return e}}/**
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
 */function qf(t){switch(t){case"recoverEmail":return"RECOVER_EMAIL";case"resetPassword":return"PASSWORD_RESET";case"signIn":return"EMAIL_SIGNIN";case"verifyEmail":return"VERIFY_EMAIL";case"verifyAndChangeEmail":return"VERIFY_AND_CHANGE_EMAIL";case"revertSecondFactorAddition":return"REVERT_SECOND_FACTOR_ADDITION";default:return null}}function Gf(t){const e=ft(ht(t)).link,n=e?ft(ht(e)).deep_link_id:null,r=ft(ht(t)).deep_link_id;return(r?ft(ht(r)).link:null)||r||n||e||t}class Sr{constructor(e){var n,r,s,i,o,a;const c=ft(ht(e)),l=(n=c.apiKey)!==null&&n!==void 0?n:null,u=(r=c.oobCode)!==null&&r!==void 0?r:null,p=qf((s=c.mode)!==null&&s!==void 0?s:null);E(l&&u&&p,"argument-error"),this.apiKey=l,this.operation=p,this.code=u,this.continueUrl=(i=c.continueUrl)!==null&&i!==void 0?i:null,this.languageCode=(o=c.languageCode)!==null&&o!==void 0?o:null,this.tenantId=(a=c.tenantId)!==null&&a!==void 0?a:null}static parseLink(e){const n=Gf(e);try{return new Sr(n)}catch{return null}}}/**
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
 */class rt{constructor(){this.providerId=rt.PROVIDER_ID}static credential(e,n){return xt._fromEmailAndPassword(e,n)}static credentialWithLink(e,n){const r=Sr.parseLink(n);return E(r,"argument-error"),xt._fromEmailAndCode(e,r.code,r.tenantId)}}rt.PROVIDER_ID="password";rt.EMAIL_PASSWORD_SIGN_IN_METHOD="password";rt.EMAIL_LINK_SIGN_IN_METHOD="emailLink";/**
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
 */class kr{constructor(e){this.providerId=e,this.defaultLanguageCode=null,this.customParameters={}}setDefaultLanguage(e){this.defaultLanguageCode=e}setCustomParameters(e){return this.customParameters=e,this}getCustomParameters(){return this.customParameters}}/**
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
 */class Rt extends kr{constructor(){super(...arguments),this.scopes=[]}addScope(e){return this.scopes.includes(e)||this.scopes.push(e),this}getScopes(){return[...this.scopes]}}/**
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
 */class Ie extends Rt{constructor(){super("facebook.com")}static credential(e){return ze._fromParams({providerId:Ie.PROVIDER_ID,signInMethod:Ie.FACEBOOK_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return Ie.credentialFromTaggedObject(e)}static credentialFromError(e){return Ie.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return Ie.credential(e.oauthAccessToken)}catch{return null}}}Ie.FACEBOOK_SIGN_IN_METHOD="facebook.com";Ie.PROVIDER_ID="facebook.com";/**
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
 */class de extends Rt{constructor(){super("google.com"),this.addScope("profile")}static credential(e,n){return ze._fromParams({providerId:de.PROVIDER_ID,signInMethod:de.GOOGLE_SIGN_IN_METHOD,idToken:e,accessToken:n})}static credentialFromResult(e){return de.credentialFromTaggedObject(e)}static credentialFromError(e){return de.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthIdToken:n,oauthAccessToken:r}=e;if(!n&&!r)return null;try{return de.credential(n,r)}catch{return null}}}de.GOOGLE_SIGN_IN_METHOD="google.com";de.PROVIDER_ID="google.com";/**
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
 */class fe extends Rt{constructor(){super("github.com")}static credential(e){return ze._fromParams({providerId:fe.PROVIDER_ID,signInMethod:fe.GITHUB_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return fe.credentialFromTaggedObject(e)}static credentialFromError(e){return fe.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return fe.credential(e.oauthAccessToken)}catch{return null}}}fe.GITHUB_SIGN_IN_METHOD="github.com";fe.PROVIDER_ID="github.com";/**
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
 */class Se extends Rt{constructor(){super("twitter.com")}static credential(e,n){return ze._fromParams({providerId:Se.PROVIDER_ID,signInMethod:Se.TWITTER_SIGN_IN_METHOD,oauthToken:e,oauthTokenSecret:n})}static credentialFromResult(e){return Se.credentialFromTaggedObject(e)}static credentialFromError(e){return Se.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthAccessToken:n,oauthTokenSecret:r}=e;if(!n||!r)return null;try{return Se.credential(n,r)}catch{return null}}}Se.TWITTER_SIGN_IN_METHOD="twitter.com";Se.PROVIDER_ID="twitter.com";/**
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
 */class Ye{constructor(e){this.user=e.user,this.providerId=e.providerId,this._tokenResponse=e._tokenResponse,this.operationType=e.operationType}static async _fromIdTokenResponse(e,n,r,s=!1){const i=await Fe._fromIdTokenResponse(e,r,s),o=Ns(r);return new Ye({user:i,providerId:o,_tokenResponse:r,operationType:n})}static async _forOperation(e,n,r){await e._updateTokensIfNecessary(r,!0);const s=Ns(r);return new Ye({user:e,providerId:s,_tokenResponse:r,operationType:n})}}function Ns(t){return t.providerId?t.providerId:"phoneNumber"in t?"phone":null}/**
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
 */class an extends Oe{constructor(e,n,r,s){var i;super(n.code,n.message),this.operationType=r,this.user=s,Object.setPrototypeOf(this,an.prototype),this.customData={appName:e.name,tenantId:(i=e.tenantId)!==null&&i!==void 0?i:void 0,_serverResponse:n.customData._serverResponse,operationType:r}}static _fromErrorAndOperation(e,n,r,s){return new an(e,n,r,s)}}function oo(t,e,n,r){return(e==="reauthenticate"?n._getReauthenticationResolver(t):n._getIdTokenResponse(t)).catch(i=>{throw i.code==="auth/multi-factor-auth-required"?an._fromErrorAndOperation(t,i,e,r):i})}async function Kf(t,e,n=!1){const r=await _t(t,e._linkToIdToken(t.auth,await t.getIdToken()),n);return Ye._forOperation(t,"link",r)}/**
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
 */async function Xf(t,e,n=!1){var r;const{auth:s}=t,i="reauthenticate";try{const o=await _t(t,oo(s,i,e,t),n);E(o.idToken,s,"internal-error");const a=xr(o.idToken);E(a,s,"internal-error");const{sub:c}=a;return E(t.uid===c,s,"user-mismatch"),Ye._forOperation(t,i,o)}catch(o){throw((r=o)===null||r===void 0?void 0:r.code)==="auth/user-not-found"&&te(s,"user-mismatch"),o}}/**
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
 */async function ao(t,e,n=!1){const r="signIn",s=await oo(t,r,e),i=await Ye._fromIdTokenResponse(t,r,s);return n||await t._updateCurrentUser(i.user),i}async function Yf(t,e){return ao(Nt(t),e)}/**
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
 */function Qf(t,e,n){var r;E(((r=n.url)===null||r===void 0?void 0:r.length)>0,t,"invalid-continue-uri"),E(typeof n.dynamicLinkDomain>"u"||n.dynamicLinkDomain.length>0,t,"invalid-dynamic-link-domain"),e.continueUrl=n.url,e.dynamicLinkDomain=n.dynamicLinkDomain,e.canHandleCodeInApp=n.handleCodeInApp,n.iOS&&(E(n.iOS.bundleId.length>0,t,"missing-ios-bundle-id"),e.iOSBundleId=n.iOS.bundleId),n.android&&(E(n.android.packageName.length>0,t,"missing-android-pkg-name"),e.androidInstallApp=n.android.installApp,e.androidMinimumVersionCode=n.android.minimumVersion,e.androidPackageName=n.android.packageName)}/**
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
 */async function Zf(t,e,n){const r=ae(t),s={requestType:"PASSWORD_RESET",email:e};n&&Qf(r,s,n),await zf(r,s)}function eh(t,e,n){return Yf(ae(t),rt.credential(e,n))}function th(t,e,n,r){return ae(t).onIdTokenChanged(e,n,r)}function nh(t,e,n){return ae(t).beforeAuthStateChanged(e,n)}function rh(t,e,n,r){return ae(t).onAuthStateChanged(e,n,r)}function sh(t){return ae(t).signOut()}const ln="__sak";/**
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
 */class lo{constructor(e,n){this.storageRetriever=e,this.type=n}_isAvailable(){try{return this.storage?(this.storage.setItem(ln,"1"),this.storage.removeItem(ln),Promise.resolve(!0)):Promise.resolve(!1)}catch{return Promise.resolve(!1)}}_set(e,n){return this.storage.setItem(e,JSON.stringify(n)),Promise.resolve()}_get(e){const n=this.storage.getItem(e);return Promise.resolve(n?JSON.parse(n):null)}_remove(e){return this.storage.removeItem(e),Promise.resolve()}get storage(){return this.storageRetriever()}}/**
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
 */function ih(){const t=q();return Er(t)||yn(t)}const oh=1e3,ah=10;class co extends lo{constructor(){super(()=>window.localStorage,"LOCAL"),this.boundEventHandler=(e,n)=>this.onStorageEvent(e,n),this.listeners={},this.localCache={},this.pollTimer=null,this.safariLocalStorageNotSynced=ih()&&Df(),this.fallbackToPolling=ro(),this._shouldAllowMigration=!0}forAllChangedKeys(e){for(const n of Object.keys(this.listeners)){const r=this.storage.getItem(n),s=this.localCache[n];r!==s&&e(n,s,r)}}onStorageEvent(e,n=!1){if(!e.key){this.forAllChangedKeys((o,a,c)=>{this.notifyListeners(o,c)});return}const r=e.key;if(n?this.detachListener():this.stopPolling(),this.safariLocalStorageNotSynced){const o=this.storage.getItem(r);if(e.newValue!==o)e.newValue!==null?this.storage.setItem(r,e.newValue):this.storage.removeItem(r);else if(this.localCache[r]===e.newValue&&!n)return}const s=()=>{const o=this.storage.getItem(r);!n&&this.localCache[r]===o||this.notifyListeners(r,o)},i=this.storage.getItem(r);Rf()&&i!==e.newValue&&e.newValue!==e.oldValue?setTimeout(s,ah):s()}notifyListeners(e,n){this.localCache[e]=n;const r=this.listeners[e];if(r)for(const s of Array.from(r))s(n&&JSON.parse(n))}startPolling(){this.stopPolling(),this.pollTimer=setInterval(()=>{this.forAllChangedKeys((e,n,r)=>{this.onStorageEvent(new StorageEvent("storage",{key:e,oldValue:n,newValue:r}),!0)})},oh)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}attachListener(){window.addEventListener("storage",this.boundEventHandler)}detachListener(){window.removeEventListener("storage",this.boundEventHandler)}_addListener(e,n){Object.keys(this.listeners).length===0&&(this.fallbackToPolling?this.startPolling():this.attachListener()),this.listeners[e]||(this.listeners[e]=new Set,this.localCache[e]=this.storage.getItem(e)),this.listeners[e].add(n)}_removeListener(e,n){this.listeners[e]&&(this.listeners[e].delete(n),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&(this.detachListener(),this.stopPolling())}async _set(e,n){await super._set(e,n),this.localCache[e]=JSON.stringify(n)}async _get(e){const n=await super._get(e);return this.localCache[e]=JSON.stringify(n),n}async _remove(e){await super._remove(e),delete this.localCache[e]}}co.type="LOCAL";const lh=co;/**
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
 */class uo extends lo{constructor(){super(()=>window.sessionStorage,"SESSION")}_addListener(e,n){}_removeListener(e,n){}}uo.type="SESSION";const fo=uo;/**
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
 */function ch(t){return Promise.all(t.map(async e=>{try{const n=await e;return{fulfilled:!0,value:n}}catch(n){return{fulfilled:!1,reason:n}}}))}/**
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
 */class _n{constructor(e){this.eventTarget=e,this.handlersMap={},this.boundEventHandler=this.handleEvent.bind(this)}static _getInstance(e){const n=this.receivers.find(s=>s.isListeningto(e));if(n)return n;const r=new _n(e);return this.receivers.push(r),r}isListeningto(e){return this.eventTarget===e}async handleEvent(e){const n=e,{eventId:r,eventType:s,data:i}=n.data,o=this.handlersMap[s];if(!o?.size)return;n.ports[0].postMessage({status:"ack",eventId:r,eventType:s});const a=Array.from(o).map(async l=>l(n.origin,i)),c=await ch(a);n.ports[0].postMessage({status:"done",eventId:r,eventType:s,response:c})}_subscribe(e,n){Object.keys(this.handlersMap).length===0&&this.eventTarget.addEventListener("message",this.boundEventHandler),this.handlersMap[e]||(this.handlersMap[e]=new Set),this.handlersMap[e].add(n)}_unsubscribe(e,n){this.handlersMap[e]&&n&&this.handlersMap[e].delete(n),(!n||this.handlersMap[e].size===0)&&delete this.handlersMap[e],Object.keys(this.handlersMap).length===0&&this.eventTarget.removeEventListener("message",this.boundEventHandler)}}_n.receivers=[];/**
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
 */function Tr(t="",e=10){let n="";for(let r=0;r<e;r++)n+=Math.floor(Math.random()*10);return t+n}/**
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
 */class uh{constructor(e){this.target=e,this.handlers=new Set}removeMessageHandler(e){e.messageChannel&&(e.messageChannel.port1.removeEventListener("message",e.onMessage),e.messageChannel.port1.close()),this.handlers.delete(e)}async _send(e,n,r=50){const s=typeof MessageChannel<"u"?new MessageChannel:null;if(!s)throw new Error("connection_unavailable");let i,o;return new Promise((a,c)=>{const l=Tr("",20);s.port1.start();const u=setTimeout(()=>{c(new Error("unsupported_event"))},r);o={messageChannel:s,onMessage(p){const v=p;if(v.data.eventId===l)switch(v.data.status){case"ack":clearTimeout(u),i=setTimeout(()=>{c(new Error("timeout"))},3e3);break;case"done":clearTimeout(i),a(v.data.response);break;default:clearTimeout(u),clearTimeout(i),c(new Error("invalid_response"));break}}},this.handlers.add(o),s.port1.addEventListener("message",o.onMessage),this.target.postMessage({eventType:e,eventId:l,data:n},[s.port2])}).finally(()=>{o&&this.removeMessageHandler(o)})}}/**
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
 */function oe(){return window}function dh(t){oe().location.href=t}/**
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
 */function ho(){return typeof oe().WorkerGlobalScope<"u"&&typeof oe().importScripts=="function"}async function fh(){if(!navigator?.serviceWorker)return null;try{return(await navigator.serviceWorker.ready).active}catch{return null}}function hh(){var t;return((t=navigator?.serviceWorker)===null||t===void 0?void 0:t.controller)||null}function gh(){return ho()?self:null}/**
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
 */const go="firebaseLocalStorageDb",mh=1,cn="firebaseLocalStorage",mo="fbase_key";class Dt{constructor(e){this.request=e}toPromise(){return new Promise((e,n)=>{this.request.addEventListener("success",()=>{e(this.request.result)}),this.request.addEventListener("error",()=>{n(this.request.error)})})}}function wn(t,e){return t.transaction([cn],e?"readwrite":"readonly").objectStore(cn)}function ph(){const t=indexedDB.deleteDatabase(go);return new Dt(t).toPromise()}function or(){const t=indexedDB.open(go,mh);return new Promise((e,n)=>{t.addEventListener("error",()=>{n(t.error)}),t.addEventListener("upgradeneeded",()=>{const r=t.result;try{r.createObjectStore(cn,{keyPath:mo})}catch(s){n(s)}}),t.addEventListener("success",async()=>{const r=t.result;r.objectStoreNames.contains(cn)?e(r):(r.close(),await ph(),e(await or()))})})}async function Rs(t,e,n){const r=wn(t,!0).put({[mo]:e,value:n});return new Dt(r).toPromise()}async function bh(t,e){const n=wn(t,!1).get(e),r=await new Dt(n).toPromise();return r===void 0?null:r.value}function Ds(t,e){const n=wn(t,!0).delete(e);return new Dt(n).toPromise()}const vh=800,yh=3;class po{constructor(){this.type="LOCAL",this._shouldAllowMigration=!0,this.listeners={},this.localCache={},this.pollTimer=null,this.pendingWrites=0,this.receiver=null,this.sender=null,this.serviceWorkerReceiverAvailable=!1,this.activeServiceWorker=null,this._workerInitializationPromise=this.initializeServiceWorkerMessaging().then(()=>{},()=>{})}async _openDb(){return this.db?this.db:(this.db=await or(),this.db)}async _withRetries(e){let n=0;for(;;)try{const r=await this._openDb();return await e(r)}catch(r){if(n++>yh)throw r;this.db&&(this.db.close(),this.db=void 0)}}async initializeServiceWorkerMessaging(){return ho()?this.initializeReceiver():this.initializeSender()}async initializeReceiver(){this.receiver=_n._getInstance(gh()),this.receiver._subscribe("keyChanged",async(e,n)=>({keyProcessed:(await this._poll()).includes(n.key)})),this.receiver._subscribe("ping",async(e,n)=>["keyChanged"])}async initializeSender(){var e,n;if(this.activeServiceWorker=await fh(),!this.activeServiceWorker)return;this.sender=new uh(this.activeServiceWorker);const r=await this.sender._send("ping",{},800);!r||((e=r[0])===null||e===void 0?void 0:e.fulfilled)&&((n=r[0])===null||n===void 0?void 0:n.value.includes("keyChanged"))&&(this.serviceWorkerReceiverAvailable=!0)}async notifyServiceWorker(e){if(!(!this.sender||!this.activeServiceWorker||hh()!==this.activeServiceWorker))try{await this.sender._send("keyChanged",{key:e},this.serviceWorkerReceiverAvailable?800:50)}catch{}}async _isAvailable(){try{if(!indexedDB)return!1;const e=await or();return await Rs(e,ln,"1"),await Ds(e,ln),!0}catch{}return!1}async _withPendingWrite(e){this.pendingWrites++;try{await e()}finally{this.pendingWrites--}}async _set(e,n){return this._withPendingWrite(async()=>(await this._withRetries(r=>Rs(r,e,n)),this.localCache[e]=n,this.notifyServiceWorker(e)))}async _get(e){const n=await this._withRetries(r=>bh(r,e));return this.localCache[e]=n,n}async _remove(e){return this._withPendingWrite(async()=>(await this._withRetries(n=>Ds(n,e)),delete this.localCache[e],this.notifyServiceWorker(e)))}async _poll(){const e=await this._withRetries(s=>{const i=wn(s,!1).getAll();return new Dt(i).toPromise()});if(!e)return[];if(this.pendingWrites!==0)return[];const n=[],r=new Set;for(const{fbase_key:s,value:i}of e)r.add(s),JSON.stringify(this.localCache[s])!==JSON.stringify(i)&&(this.notifyListeners(s,i),n.push(s));for(const s of Object.keys(this.localCache))this.localCache[s]&&!r.has(s)&&(this.notifyListeners(s,null),n.push(s));return n}notifyListeners(e,n){this.localCache[e]=n;const r=this.listeners[e];if(r)for(const s of Array.from(r))s(n)}startPolling(){this.stopPolling(),this.pollTimer=setInterval(async()=>this._poll(),vh)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}_addListener(e,n){Object.keys(this.listeners).length===0&&this.startPolling(),this.listeners[e]||(this.listeners[e]=new Set,this._get(e)),this.listeners[e].add(n)}_removeListener(e,n){this.listeners[e]&&(this.listeners[e].delete(n),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&this.stopPolling()}}po.type="LOCAL";const _h=po;/**
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
 */function wh(){var t,e;return(e=(t=document.getElementsByTagName("head"))===null||t===void 0?void 0:t[0])!==null&&e!==void 0?e:document}function xh(t){return new Promise((e,n)=>{const r=document.createElement("script");r.setAttribute("src",t),r.onload=e,r.onerror=s=>{const i=ie("internal-error");i.customData=s,n(i)},r.type="text/javascript",r.charset="UTF-8",wh().appendChild(r)})}function Eh(t){return`__${t}${Math.floor(Math.random()*1e6)}`}new At(3e4,6e4);/**
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
 */function bo(t,e){return e?ge(e):(E(t._popupRedirectResolver,t,"argument-error"),t._popupRedirectResolver)}/**
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
 */class $r extends Ir{constructor(e){super("custom","custom"),this.params=e}_getIdTokenResponse(e){return Ge(e,this._buildIdpRequest())}_linkToIdToken(e,n){return Ge(e,this._buildIdpRequest(n))}_getReauthenticationResolver(e){return Ge(e,this._buildIdpRequest())}_buildIdpRequest(e){const n={requestUri:this.params.requestUri,sessionId:this.params.sessionId,postBody:this.params.postBody,tenantId:this.params.tenantId,pendingToken:this.params.pendingToken,returnSecureToken:!0,returnIdpCredential:!0};return e&&(n.idToken=e),n}}function Ih(t){return ao(t.auth,new $r(t),t.bypassAuthState)}function Sh(t){const{auth:e,user:n}=t;return E(n,e,"internal-error"),Xf(n,new $r(t),t.bypassAuthState)}async function kh(t){const{auth:e,user:n}=t;return E(n,e,"internal-error"),Kf(n,new $r(t),t.bypassAuthState)}/**
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
 */class vo{constructor(e,n,r,s,i=!1){this.auth=e,this.resolver=r,this.user=s,this.bypassAuthState=i,this.pendingPromise=null,this.eventManager=null,this.filter=Array.isArray(n)?n:[n]}execute(){return new Promise(async(e,n)=>{this.pendingPromise={resolve:e,reject:n};try{this.eventManager=await this.resolver._initialize(this.auth),await this.onExecution(),this.eventManager.registerConsumer(this)}catch(r){this.reject(r)}})}async onAuthEvent(e){const{urlResponse:n,sessionId:r,postBody:s,tenantId:i,error:o,type:a}=e;if(o){this.reject(o);return}const c={auth:this.auth,requestUri:n,sessionId:r,tenantId:i||void 0,postBody:s||void 0,user:this.user,bypassAuthState:this.bypassAuthState};try{this.resolve(await this.getIdpTask(a)(c))}catch(l){this.reject(l)}}onError(e){this.reject(e)}getIdpTask(e){switch(e){case"signInViaPopup":case"signInViaRedirect":return Ih;case"linkViaPopup":case"linkViaRedirect":return kh;case"reauthViaPopup":case"reauthViaRedirect":return Sh;default:te(this.auth,"internal-error")}}resolve(e){ve(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.resolve(e),this.unregisterAndCleanUp()}reject(e){ve(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.reject(e),this.unregisterAndCleanUp()}unregisterAndCleanUp(){this.eventManager&&this.eventManager.unregisterConsumer(this),this.pendingPromise=null,this.cleanUp()}}/**
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
 */const Th=new At(2e3,1e4);async function Ps(t,e,n){const r=Nt(t);hf(t,e,kr);const s=bo(r,n);return new Me(r,"signInViaPopup",e,s).executeNotNull()}class Me extends vo{constructor(e,n,r,s,i){super(e,n,s,i),this.provider=r,this.authWindow=null,this.pollId=null,Me.currentPopupAction&&Me.currentPopupAction.cancel(),Me.currentPopupAction=this}async executeNotNull(){const e=await this.execute();return E(e,this.auth,"internal-error"),e}async onExecution(){ve(this.filter.length===1,"Popup operations only handle one event");const e=Tr();this.authWindow=await this.resolver._openPopup(this.auth,this.provider,this.filter[0],e),this.authWindow.associatedEvent=e,this.resolver._originValidation(this.auth).catch(n=>{this.reject(n)}),this.resolver._isIframeWebStorageSupported(this.auth,n=>{n||this.reject(ie(this.auth,"web-storage-unsupported"))}),this.pollUserCancellation()}get eventId(){var e;return((e=this.authWindow)===null||e===void 0?void 0:e.associatedEvent)||null}cancel(){this.reject(ie(this.auth,"cancelled-popup-request"))}cleanUp(){this.authWindow&&this.authWindow.close(),this.pollId&&window.clearTimeout(this.pollId),this.authWindow=null,this.pollId=null,Me.currentPopupAction=null}pollUserCancellation(){const e=()=>{var n,r;if(!((r=(n=this.authWindow)===null||n===void 0?void 0:n.window)===null||r===void 0)&&r.closed){this.pollId=window.setTimeout(()=>{this.pollId=null,this.reject(ie(this.auth,"popup-closed-by-user"))},2e3);return}this.pollId=window.setTimeout(e,Th.get())};e()}}Me.currentPopupAction=null;/**
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
 */const $h="pendingRedirect",qt=new Map;class Ch extends vo{constructor(e,n,r=!1){super(e,["signInViaRedirect","linkViaRedirect","reauthViaRedirect","unknown"],n,void 0,r),this.eventId=null}async execute(){let e=qt.get(this.auth._key());if(!e){try{const r=await Ah(this.resolver,this.auth)?await super.execute():null;e=()=>Promise.resolve(r)}catch(n){e=()=>Promise.reject(n)}qt.set(this.auth._key(),e)}return this.bypassAuthState||qt.set(this.auth._key(),()=>Promise.resolve(null)),e()}async onAuthEvent(e){if(e.type==="signInViaRedirect")return super.onAuthEvent(e);if(e.type==="unknown"){this.resolve(null);return}if(e.eventId){const n=await this.auth._redirectUserForId(e.eventId);if(n)return this.user=n,super.onAuthEvent(e);this.resolve(null)}}async onExecution(){}cleanUp(){}}async function Ah(t,e){const n=Rh(e),r=Nh(t);if(!await r._isAvailable())return!1;const s=await r._get(n)==="true";return await r._remove(n),s}function Oh(t,e){qt.set(t._key(),e)}function Nh(t){return ge(t._redirectPersistence)}function Rh(t){return Jt($h,t.config.apiKey,t.name)}async function Dh(t,e,n=!1){const r=Nt(t),s=bo(r,e),o=await new Ch(r,s,n).execute();return o&&!n&&(delete o.user._redirectEventId,await r._persistUserIfCurrent(o.user),await r._setRedirectUser(null,e)),o}/**
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
 */const Ph=10*60*1e3;class Lh{constructor(e){this.auth=e,this.cachedEventUids=new Set,this.consumers=new Set,this.queuedRedirectEvent=null,this.hasHandledPotentialRedirect=!1,this.lastProcessedEventTime=Date.now()}registerConsumer(e){this.consumers.add(e),this.queuedRedirectEvent&&this.isEventForConsumer(this.queuedRedirectEvent,e)&&(this.sendToConsumer(this.queuedRedirectEvent,e),this.saveEventToCache(this.queuedRedirectEvent),this.queuedRedirectEvent=null)}unregisterConsumer(e){this.consumers.delete(e)}onEvent(e){if(this.hasEventBeenHandled(e))return!1;let n=!1;return this.consumers.forEach(r=>{this.isEventForConsumer(e,r)&&(n=!0,this.sendToConsumer(e,r),this.saveEventToCache(e))}),this.hasHandledPotentialRedirect||!Mh(e)||(this.hasHandledPotentialRedirect=!0,n||(this.queuedRedirectEvent=e,n=!0)),n}sendToConsumer(e,n){var r;if(e.error&&!yo(e)){const s=((r=e.error.code)===null||r===void 0?void 0:r.split("auth/")[1])||"internal-error";n.onError(ie(this.auth,s))}else n.onAuthEvent(e)}isEventForConsumer(e,n){const r=n.eventId===null||!!e.eventId&&e.eventId===n.eventId;return n.filter.includes(e.type)&&r}hasEventBeenHandled(e){return Date.now()-this.lastProcessedEventTime>=Ph&&this.cachedEventUids.clear(),this.cachedEventUids.has(Ls(e))}saveEventToCache(e){this.cachedEventUids.add(Ls(e)),this.lastProcessedEventTime=Date.now()}}function Ls(t){return[t.type,t.eventId,t.sessionId,t.tenantId].filter(e=>e).join("-")}function yo({type:t,error:e}){return t==="unknown"&&e?.code==="auth/no-auth-event"}function Mh(t){switch(t.type){case"signInViaRedirect":case"linkViaRedirect":case"reauthViaRedirect":return!0;case"unknown":return yo(t);default:return!1}}/**
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
 */async function Uh(t,e={}){return nt(t,"GET","/v1/projects",e)}/**
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
 */const jh=/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,Fh=/^https?/;async function Bh(t){if(t.config.emulator)return;const{authorizedDomains:e}=await Uh(t);for(const n of e)try{if(Hh(n))return}catch{}te(t,"unauthorized-domain")}function Hh(t){const e=ir(),{protocol:n,hostname:r}=new URL(e);if(t.startsWith("chrome-extension://")){const o=new URL(t);return o.hostname===""&&r===""?n==="chrome-extension:"&&t.replace("chrome-extension://","")===e.replace("chrome-extension://",""):n==="chrome-extension:"&&o.hostname===r}if(!Fh.test(n))return!1;if(jh.test(t))return r===t;const s=t.replace(/\./g,"\\.");return new RegExp("^(.+\\."+s+"|"+s+")$","i").test(r)}/**
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
 */const zh=new At(3e4,6e4);function Ms(){const t=oe().___jsl;if(t?.H){for(const e of Object.keys(t.H))if(t.H[e].r=t.H[e].r||[],t.H[e].L=t.H[e].L||[],t.H[e].r=[...t.H[e].L],t.CP)for(let n=0;n<t.CP.length;n++)t.CP[n]=null}}function Vh(t){return new Promise((e,n)=>{var r,s,i;function o(){Ms(),gapi.load("gapi.iframes",{callback:()=>{e(gapi.iframes.getContext())},ontimeout:()=>{Ms(),n(ie(t,"network-request-failed"))},timeout:zh.get()})}if(!((s=(r=oe().gapi)===null||r===void 0?void 0:r.iframes)===null||s===void 0)&&s.Iframe)e(gapi.iframes.getContext());else if(!((i=oe().gapi)===null||i===void 0)&&i.load)o();else{const a=Eh("iframefcb");return oe()[a]=()=>{gapi.load?o():n(ie(t,"network-request-failed"))},xh(`https://apis.google.com/js/api.js?onload=${a}`).catch(c=>n(c))}}).catch(e=>{throw Gt=null,e})}let Gt=null;function Wh(t){return Gt=Gt||Vh(t),Gt}/**
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
 */const Jh=new At(5e3,15e3),qh="__/auth/iframe",Gh="emulator/auth/iframe",Kh={style:{position:"absolute",top:"-100px",width:"1px",height:"1px"},"aria-hidden":"true",tabindex:"-1"},Xh=new Map([["identitytoolkit.googleapis.com","p"],["staging-identitytoolkit.sandbox.googleapis.com","s"],["test-identitytoolkit.sandbox.googleapis.com","t"]]);function Yh(t){const e=t.config;E(e.authDomain,t,"auth-domain-config-required");const n=e.emulator?wr(e,Gh):`https://${t.config.authDomain}/${qh}`,r={apiKey:e.apiKey,appName:t.name,v:bn},s=Xh.get(t.config.apiHost);s&&(r.eid=s);const i=t._getFrameworks();return i.length&&(r.fw=i.join(",")),`${n}?${Ct(r).slice(1)}`}async function Qh(t){const e=await Wh(t),n=oe().gapi;return E(n,t,"internal-error"),e.open({where:document.body,url:Yh(t),messageHandlersFilter:n.iframes.CROSS_ORIGIN_IFRAMES_FILTER,attributes:Kh,dontclear:!0},r=>new Promise(async(s,i)=>{await r.restyle({setHideOnLeave:!1});const o=ie(t,"network-request-failed"),a=oe().setTimeout(()=>{i(o)},Jh.get());function c(){oe().clearTimeout(a),s(r)}r.ping(c).then(c,()=>{i(o)})}))}/**
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
 */const Zh={location:"yes",resizable:"yes",statusbar:"yes",toolbar:"no"},eg=500,tg=600,ng="_blank",rg="http://localhost";class Us{constructor(e){this.window=e,this.associatedEvent=null}close(){if(this.window)try{this.window.close()}catch{}}}function sg(t,e,n,r=eg,s=tg){const i=Math.max((window.screen.availHeight-s)/2,0).toString(),o=Math.max((window.screen.availWidth-r)/2,0).toString();let a="";const c=Object.assign(Object.assign({},Zh),{width:r.toString(),height:s.toString(),top:i,left:o}),l=q().toLowerCase();n&&(a=Qi(l)?ng:n),Yi(l)&&(e=e||rg,c.scrollbars="yes");const u=Object.entries(c).reduce((v,[b,g])=>`${v}${b}=${g},`,"");if(Nf(l)&&a!=="_self")return ig(e||"",a),new Us(null);const p=window.open(e||"",a,u);E(p,t,"popup-blocked");try{p.focus()}catch{}return new Us(p)}function ig(t,e){const n=document.createElement("a");n.href=t,n.target=e;const r=document.createEvent("MouseEvent");r.initMouseEvent("click",!0,!0,window,1,0,0,0,0,!1,!1,!1,!1,1,null),n.dispatchEvent(r)}/**
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
 */const og="__/auth/handler",ag="emulator/auth/handler";function js(t,e,n,r,s,i){E(t.config.authDomain,t,"auth-domain-config-required"),E(t.config.apiKey,t,"invalid-api-key");const o={apiKey:t.config.apiKey,appName:t.name,authType:n,redirectUrl:r,v:bn,eventId:s};if(e instanceof kr){e.setDefaultLanguage(t.languageCode),o.providerId=e.providerId||"",td(e.getCustomParameters())||(o.customParameters=JSON.stringify(e.getCustomParameters()));for(const[c,l]of Object.entries(i||{}))o[c]=l}if(e instanceof Rt){const c=e.getScopes().filter(l=>l!=="");c.length>0&&(o.scopes=c.join(","))}t.tenantId&&(o.tid=t.tenantId);const a=o;for(const c of Object.keys(a))a[c]===void 0&&delete a[c];return`${lg(t)}?${Ct(a).slice(1)}`}function lg({config:t}){return t.emulator?wr(t,ag):`https://${t.authDomain}/${og}`}/**
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
 */const zn="webStorageSupport";class cg{constructor(){this.eventManagers={},this.iframes={},this.originValidationPromises={},this._redirectPersistence=fo,this._completeRedirectFn=Dh,this._overrideRedirectResult=Oh}async _openPopup(e,n,r,s){var i;ve((i=this.eventManagers[e._key()])===null||i===void 0?void 0:i.manager,"_initialize() not called before _openPopup()");const o=js(e,n,r,ir(),s);return sg(e,o,Tr())}async _openRedirect(e,n,r,s){return await this._originValidation(e),dh(js(e,n,r,ir(),s)),new Promise(()=>{})}_initialize(e){const n=e._key();if(this.eventManagers[n]){const{manager:s,promise:i}=this.eventManagers[n];return s?Promise.resolve(s):(ve(i,"If manager is not set, promise should be"),i)}const r=this.initAndGetManager(e);return this.eventManagers[n]={promise:r},r.catch(()=>{delete this.eventManagers[n]}),r}async initAndGetManager(e){const n=await Qh(e),r=new Lh(e);return n.register("authEvent",s=>(E(s?.authEvent,e,"invalid-auth-event"),{status:r.onEvent(s.authEvent)?"ACK":"ERROR"}),gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER),this.eventManagers[e._key()]={manager:r},this.iframes[e._key()]=n,r}_isIframeWebStorageSupported(e,n){this.iframes[e._key()].send(zn,{type:zn},s=>{var i;const o=(i=s?.[0])===null||i===void 0?void 0:i[zn];o!==void 0&&n(!!o),te(e,"internal-error")},gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER)}_originValidation(e){const n=e._key();return this.originValidationPromises[n]||(this.originValidationPromises[n]=Bh(e)),this.originValidationPromises[n]}get _shouldInitProactively(){return ro()||Er()||yn()}}const ug=cg;var Fs="@firebase/auth",Bs="0.20.11";/**
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
 */class dg{constructor(e){this.auth=e,this.internalListeners=new Map}getUid(){var e;return this.assertAuthConfigured(),((e=this.auth.currentUser)===null||e===void 0?void 0:e.uid)||null}async getToken(e){return this.assertAuthConfigured(),await this.auth._initializationPromise,this.auth.currentUser?{accessToken:await this.auth.currentUser.getIdToken(e)}:null}addAuthTokenListener(e){if(this.assertAuthConfigured(),this.internalListeners.has(e))return;const n=this.auth.onIdTokenChanged(r=>{var s;e(((s=r)===null||s===void 0?void 0:s.stsTokenManager.accessToken)||null)});this.internalListeners.set(e,n),this.updateProactiveRefresh()}removeAuthTokenListener(e){this.assertAuthConfigured();const n=this.internalListeners.get(e);!n||(this.internalListeners.delete(e),n(),this.updateProactiveRefresh())}assertAuthConfigured(){E(this.auth._initializationPromise,"dependent-sdk-initialized-before-auth")}updateProactiveRefresh(){this.internalListeners.size>0?this.auth._startProactiveRefresh():this.auth._stopProactiveRefresh()}}/**
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
 */function fg(t){switch(t){case"Node":return"node";case"ReactNative":return"rn";case"Worker":return"webworker";case"Cordova":return"cordova";default:return}}function hg(t){vt(new Xe("auth",(e,{options:n})=>{const r=e.getProvider("app").getImmediate(),s=e.getProvider("heartbeat"),{apiKey:i,authDomain:o}=r.options;return((a,c)=>{E(i&&!i.includes(":"),"invalid-api-key",{appName:a.name}),E(!o?.includes(":"),"argument-error",{appName:a.name});const l={apiKey:i,authDomain:o,clientPlatform:t,apiHost:"identitytoolkit.googleapis.com",tokenApiHost:"securetoken.googleapis.com",apiScheme:"https",sdkClientVersion:so(t)},u=new Lf(a,c,l);return mf(u,n),u})(r,s)},"PUBLIC").setInstantiationMode("EXPLICIT").setInstanceCreatedCallback((e,n,r)=>{e.getProvider("auth-internal").initialize()})),vt(new Xe("auth-internal",e=>{const n=Nt(e.getProvider("auth").getImmediate());return(r=>new dg(r))(n)},"PRIVATE").setInstantiationMode("EXPLICIT")),Je(Fs,Bs,fg(t)),Je(Fs,Bs,"esm2017")}/**
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
 */const gg=5*60,mg=Pi("authIdTokenMaxAge")||gg;let Hs=null;const pg=t=>async e=>{const n=e&&await e.getIdTokenResult(),r=n&&(new Date().getTime()-Date.parse(n.issuedAtTime))/1e3;if(r&&r>mg)return;const s=n?.token;Hs!==s&&(Hs=s,await fetch(t,{method:s?"POST":"DELETE",headers:s?{Authorization:`Bearer ${s}`}:{}}))};function bg(t=tf()){const e=ji(t,"auth");if(e.isInitialized())return e.getImmediate();const n=gf(t,{popupRedirectResolver:ug,persistence:[_h,lh,fo]}),r=Pi("authTokenSyncURL");if(r){const i=pg(r);nh(n,i,()=>i(n.currentUser)),th(n,o=>i(o))}const s=Ku("auth");return s&&Mf(n,`http://${s}`),n}hg("Browser");function vg(){const[t,e]=y(null);return{email:t,setEmail:e}}const _o=Y(vg);var yg="firebase",_g="9.13.0";/**
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
 */Je(yg,_g,"app");const wg={apiKey:"AIzaSyAX9a9qLUzLoVFy9YrRprTWuf7lwZ-cEi0",authDomain:"fabled-pivot-305219.firebaseapp.com",projectId:"fabled-pivot-305219",storageBucket:"fabled-pivot-305219.appspot.com",messagingSenderId:"293220208202",appId:"1:293220208202:web:59eabbc4f981ead408e0b3",measurementId:"G-7E7PGPVJ99"},xg=Fi(wg);function Eg(){const[t,e]=y(null);return e(bg(xg)),{auth:t}}const wo=Y(Eg),Ig=w('<div id="tab_account" class="tabcontent p-4"><p class="text-gray-600"></p><button type="button" class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 text-sm font-medium leading-4 text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 mt-2">Logout</button></div>'),{tabName:Sg}=tt,{email:kg}=_o,{auth:Tg}=wo;function $g(){function t(){sh(Tg()).catch(function(e){console.error(e)})}return(()=>{const e=Ig.cloneNode(!0),n=e.firstChild,r=n.nextSibling;return d(n,kg),r.$$click=t,k(()=>e.classList.toggle("hidden",Sg()!="account")),e})()}A(["click"]);const Cg=w('<div class="md:pl-36 flex flex-col flex-1"><main class="flex-1"><div class=""><div class="mx-auto"><div></div></div></div></main></div>'),{multiuser:zs,setMultiuser:cm}=kt,{logged:Ag,setLogged:um}=Tt,{localModules:Og,setLocalModules:dm,getLocalModule:fm,addLocalModule:hm,loadAllModules:Ng}=pn;function Rg(){const[t,e]=y(!1);return Et(function(){(zs()==!1||Ag()==!0)&&Si(Og())&&Ng()}),(()=>{const n=Cg.cloneNode(!0),r=n.firstChild,s=r.firstChild,i=s.firstChild,o=i.firstChild;return d(o,h(lu,{get jobsTrigger(){return t()},setJobsTrigger:e}),null),d(o,h(Ru,{get jobsTrigger(){return t()},setJobsTrigger:e}),null),d(o,h(Lu,{}),null),d(o,h(se,{get when(){return zs()==!0},get children(){return h($g,{})}}),null),n})()}function Dg(){const[t,e]=y(!0);return{systemReady:t,setSystemReady:e}}const Pg=Y(Dg),Lg=w('<div id="tab_systemnotready" class="tabcontent"><div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-md bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"><div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4"><div class="sm:flex sm:items-start"><div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"><svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10.5v3.75m-9.303 3.376C1.83 19.126 2.914 21 4.645 21h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 4.88c-.866-1.501-3.032-1.501-3.898 0L2.697 17.626zM12 17.25h.007v.008H12v-.008z"></path></svg></div><div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left"><h3 class="text-lg font-medium leading-6 text-gray-900" id="modal-title">System not ready</h3><div class="mt-2"><p class="text-sm text-gray-500">OakVar server is not running or it is having a problem. Please contact your system administrator.</p></div></div></div></div></div></div></div></div></div>');function Mg(){const{systemReady:t,setSystemReady:e}=Pg;return(()=>{const n=Lg.cloneNode(!0);return k(()=>n.classList.toggle("hidden",!!t())),n})()}const Ug=w('<div class="h-full"></div>');function jg(t){return(()=>{const e=Ug.cloneNode(!0);return d(e,h(Bl,{}),null),d(e,h(Rg,{}),null),d(e,h(Mg,{}),null),e})()}const Fg=w('<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true"><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100"><svg class="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"></path></svg></div><div class="mt-3 text-center sm:mt-5"><h3 class="text-lg font-medium leading-6 text-gray-900"></h3><div class="mt-2"><p class="text-sm text-gray-500"></p></div></div></div><div class="mt-5 sm:mt-6"><button type="button" class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm">Dismiss</button></div></div></div></div></div>');function Bg(t){return(()=>{const e=Fg.cloneNode(!0),n=e.firstChild,r=n.nextSibling,s=r.firstChild,i=s.firstChild,o=i.firstChild,a=o.firstChild,c=a.nextSibling,l=c.firstChild,u=l.nextSibling,p=u.firstChild,v=o.nextSibling,b=v.firstChild;return d(l,()=>t.title),d(p,()=>t.text),dn(b,"click",t.callback,!0),e})()}A(["click"]);const Hg=w('<svg class="hide animate-spin ml-1 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>');function Vs(t){return(()=>{const e=Hg.cloneNode(!0);return k(()=>e.classList.toggle("hidden",!t.show)),e})()}const zg=w('<div><div id="firebaseui-auth-container"></div><div id="container"><div class="flex min-h-full flex-col justify-center py-12 sm:px-6 lg:px-8"><div class="sm:mx-auto sm:w-full sm:max-w-md"><img class="mx-auto h-16 w-auto" alt="OakVar"><h2 class="mt-4 text-center text-3xl font-bold tracking-tight text-gray-900">Sign in</h2><h2 class="hide mt-4 text-center text-3xl font-bold tracking-tight text-gray-900">Sign up</h2></div><p class="mt-2 text-center text-sm text-gray-600">Or&nbsp;<a href="#" class="font-medium text-indigo-600 hover:text-indigo-500">sign up</a><a href="#" class="hide font-medium text-indigo-600 hover:text-indigo-500">sign in</a></p><div class="mt-6 sm:mx-auto sm:w-full sm:max-w-md"><div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10"><div class="space-y-6" method="POST"><div><label for="email" class="block text-sm font-medium text-gray-700">Email address</label><div class="mt-1"><input id="email" name="email" type="email" autocomplete="email" required class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"><div class="text-xs text-orange-600 mt-2"></div></div></div><div><label for="password" class="block text-sm font-medium text-gray-700">Password</label><div class="mt-1"><input id="password" name="password" type="password" autocomplete="current-password" required class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"><div class="text-xs text-orange-600 mt-2"></div></div></div><div class="flex items-center justify-between"><div class="flex items-center"></div><div class="text-sm"><a href="#" class="font-medium">Forgot your password?</a></div></div><div><button id="signin_btn" type="submit" class="flex w-full justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Sign in</button><button id="signup_btn" type="submit" class="flex w-full justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Sign up</button></div></div></div></div></div></div></div>'),{setLogged:Bt}=Tt,{email:Pe,setEmail:Vn}=_o,{setTabName:Ws}=tt,{auth:ct}=wo;let Js=null;function Vg(){const{serverUrl:t,withCredentials:e}=ne,[n,r]=y("signin"),[s,i]=y(!1),[o,a]=y(!1),[c,l]=y(null),[u,p]=y(!1),[v,b]=y(null),[g,m]=y(null),[x,_]=y(!1),[S,T]=y(null),[O,N]=y(null),[X,G]=y(""),[le,C]=y(""),[R,U]=y(!0),[re,st]=y(!0),xn={"auth/user-not-found":"Account was not found. Please sign up first.","auth/account-exists-with-different-credential":"Account exists with different credential.","auth/wrong-password":"Wrong password. Please check your password or use Forget Your Password? link.","auth/missing-email":"Please provide an email address.","missing-password":"Please provide a password.","account-exists":"Account already exists.","auth/too-many-requests":"Too many failed attempts. Wait for a while and try again, or use Forgot your password? link."};let En=()=>{p(!1)};Js||(Js=rh(ct(),function(I){if(I){const F=I.accessToken;M.post(t()+"/server/loginsuccess",{login_token:F},{withCredentials:e}).then(function(K){Vn(K.data.email),i(!1),Ws("submit"),Bt(!0)}).catch(function(K){ue(K,"Login failed"),console.error(K),i(!1)})}else M.get(t()+"/server/logout",{withCredentials:e}).then(function(F){F.status==200&&Bt(!1)}).catch(function(F){console.error(F)})}));function Z(){return!R()&&!re()}function Pt(){ce(),z()}function it(I){Vn(I.target.value),Pt(),I.keyCode==13&&Z()&&ot("email")}function ce(){if(!Pe()||Pe().length==0){G("Please enter an email."),U(!0);return}let I=/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9]+)+$/;if(!Pe().match(I)){G("Email is invalid."),U(!0);return}G(""),U(!1)}function Ve(I){l(I.target.value),Pt(),I.keyCode==13&&Z()&&ot("email")}function z(){if(!c()||c().length==0){C("Please enter a password."),st(!0);return}let I=/^[a-zA-Z0-9.!?#$%&^_@*]+$/;if(!c().match(I)){C("Password is invalid (a-z, A-Z, 0-9, .!?#$%&^_@* allowed)."),st(!0);return}return C(""),st(!1),!0}function Ne(I){const F=I.user.accessToken;M.post(t()+"/server/loginsuccess",{login_token:F},{withCredentials:e}).then(function(K){Vn(K.data.email),i(!1),Ws("submit"),Bt(!0)}).catch(function(K){ue(K,"Login failed"),i(!1)})}function ue(I,F){if(I.response&&(I=I.response.data),I.code=="auth/popup-closed-by-user"){i(!1);return}T(F);let K=xn[I.code];K?N(K):(N("Error code: "+I.code),console.error(I)),_(!0)}function In(){i(!0),eh(ct(),Pe(),c()).then(function(I){Ne(I)}).catch(function(I){console.log("@ err=",I,"@@",I.code),ue(I,"Login failed"),i(!1)})}function Sn(){i(!0);const I=new de;Ps(ct(),I).then(function(F){Ne(F)}).catch(function(F){ue(F,"Login failed"),i(!1)})}function kn(){i(!0);const I=new fe;Ps(ct(),I).then(function(F){Ne(F)}).catch(function(F){ue(F,"Login failed"),i(!1)})}function ot(I){I=="email"?In():I=="google"?Sn():I=="github"&&kn()}function Tn(){a(!0),M.post(t()+"/server/signup",{email:Pe(),password:c()},{withCredentials:e}).then(function(I){I.data.code&&(b("Success"),m(I.data.code),En=()=>{a(!1),Bt(!0)},p(!0))}).catch(function(I){ue(I,"Signup failed"),a(!1)})}function $n(){Zf(ct(),Pe()).then(function(){b("Success"),m("Please check your email for a password reset link."),p(!0)}).catch(function(I){ue(I,"Password reset failed")})}return(()=>{const I=zg.cloneNode(!0),F=I.firstChild,K=F.nextSibling,Cn=K.firstChild,Lt=Cn.firstChild,Mt=Lt.firstChild,Ut=Mt.nextSibling,D=Ut.nextSibling,B=Lt.nextSibling,Re=B.firstChild,we=Re.nextSibling,An=we.nextSibling,xo=B.nextSibling,Eo=xo.firstChild,Io=Eo.firstChild,Cr=Io.firstChild,So=Cr.firstChild,ko=So.nextSibling,On=ko.firstChild,To=On.nextSibling,Ar=Cr.nextSibling,$o=Ar.firstChild,Co=$o.nextSibling,Nn=Co.firstChild,Ao=Nn.nextSibling,Or=Ar.nextSibling,Oo=Or.firstChild,Nr=Oo.nextSibling,Rn=Nr.firstChild,No=Or.nextSibling,De=No.firstChild;De.firstChild;const at=De.nextSibling;return at.firstChild,we.$$click=r,we.$$clickData="signup",An.$$click=r,An.$$clickData="signin",On.$$keyup=it,d(To,X),Nn.$$keyup=Ve,d(Ao,le),Rn.$$click=$n,De.$$click=ot,De.$$clickData="email",d(De,h(Vs,{get show(){return s()}}),null),at.$$click=Tn,d(at,h(Vs,{get show(){return o()}}),null),d(I,h(se,{get when(){return x()},get children(){return h(Ei,{get title(){return S()},get text(){return O()},setShowDialog:_})}}),null),d(I,h(se,{get when(){return u()},get children(){return h(Bg,{get title(){return v()},get text(){return g()},callback:En})}}),null),k(L=>{const Rr=t()+"/submit/images/logo_only.png",Dr=n()!="signin",Pr=n()!="signup",Lr=n()!="signin",Mr=n()!="signup",Ur=n()!="signin",Ro={"text-indigo-600":!R(),"hover:text-indigo-500":!R(),"text-gray-500":R(),"cursor-default":R()},jr=R(),Do={hidden:n()!="signin","bg-indigo-600":Z(),"hover:bg-indigo-700":Z(),"bg-gray-500":!Z()},Fr=!Z(),Po={hidden:n()!="signup","bg-indigo-600":Z(),"hover:bg-indigo-700":Z(),"bg-gray-500":!Z()},Br=!Z();return Rr!==L._v$&&J(Mt,"src",L._v$=Rr),Dr!==L._v$2&&Ut.classList.toggle("hidden",L._v$2=Dr),Pr!==L._v$3&&D.classList.toggle("hidden",L._v$3=Pr),Lr!==L._v$4&&we.classList.toggle("hidden",L._v$4=Lr),Mr!==L._v$5&&An.classList.toggle("hidden",L._v$5=Mr),Ur!==L._v$6&&Nr.classList.toggle("hidden",L._v$6=Ur),L._v$7=Ht(Rn,Ro,L._v$7),jr!==L._v$8&&(Rn.disabled=L._v$8=jr),L._v$9=Ht(De,Do,L._v$9),Fr!==L._v$10&&(De.disabled=L._v$10=Fr),L._v$11=Ht(at,Po,L._v$11),Br!==L._v$12&&(at.disabled=L._v$12=Br),L},{_v$:void 0,_v$2:void 0,_v$3:void 0,_v$4:void 0,_v$5:void 0,_v$6:void 0,_v$7:void 0,_v$8:void 0,_v$9:void 0,_v$10:void 0,_v$11:void 0,_v$12:void 0}),k(()=>On.value=Pe()),k(()=>Nn.value=c()),I})()}A(["click","keyup"]);function Wg(){const{serverUrl:t}=ne,{multiuser:e,setMultiuser:n}=kt,{logged:r,setLogged:s}=Tt;n(null),s(null);function i(){M.get(t()+"/server/deletetoken").then(function(){}).catch(function(c){console.error(c)})}function o(){M.get(t()+"/submit/servermode").then(function(c){n(c.data.servermode),e()||i()}).catch(function(c){console.error(c)})}function a(){M.get(t()+"/submit/loginstate").then(function(c){s(c.data.loggedin)}).catch(function(c){console.error(c)})}return e()==null&&o(),r()==null&&a(),h(se,{get when(){return!e()||r()},get fallback(){return h(Vg,{})},get children(){return h(jg,{})}})}ta(()=>h(Wg,{}),document.getElementById("root"));
