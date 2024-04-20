true&&(function polyfill() {
    const relList = document.createElement('link').relList;
    if (relList && relList.supports && relList.supports('modulepreload')) {
        return;
    }
    for (const link of document.querySelectorAll('link[rel="modulepreload"]')) {
        processPreload(link);
    }
    new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type !== 'childList') {
                continue;
            }
            for (const node of mutation.addedNodes) {
                if (node.tagName === 'LINK' && node.rel === 'modulepreload')
                    processPreload(node);
            }
        }
    }).observe(document, { childList: true, subtree: true });
    function getFetchOpts(link) {
        const fetchOpts = {};
        if (link.integrity)
            fetchOpts.integrity = link.integrity;
        if (link.referrerPolicy)
            fetchOpts.referrerPolicy = link.referrerPolicy;
        if (link.crossOrigin === 'use-credentials')
            fetchOpts.credentials = 'include';
        else if (link.crossOrigin === 'anonymous')
            fetchOpts.credentials = 'omit';
        else
            fetchOpts.credentials = 'same-origin';
        return fetchOpts;
    }
    function processPreload(link) {
        if (link.ep)
            // ep marker = processed
            return;
        link.ep = true;
        // prepopulate the load record
        const fetchOpts = getFetchOpts(link);
        fetch(link.href, fetchOpts);
    }
}());

const equalFn = (a, b) => a === b;
const $PROXY = Symbol("solid-proxy");
const $TRACK = Symbol("solid-track");
const signalOptions = {
  equals: equalFn
};
let runEffects = runQueue;
const STALE = 1;
const PENDING = 2;
const UNOWNED = {
  owned: null,
  cleanups: null,
  context: null,
  owner: null
};
const NO_INIT = {};
var Owner = null;
let Transition = null;
let ExternalSourceConfig = null;
let Listener = null;
let Updates = null;
let Effects = null;
let ExecCount = 0;
function createRoot(fn, detachedOwner) {
  const listener = Listener,
    owner = Owner,
    unowned = fn.length === 0,
    current = detachedOwner === undefined ? owner : detachedOwner,
    root = unowned
      ? UNOWNED
      : {
          owned: null,
          cleanups: null,
          context: current ? current.context : null,
          owner: current
        },
    updateFn = unowned ? fn : () => fn(() => untrack(() => cleanNode(root)));
  Owner = root;
  Listener = null;
  try {
    return runUpdates(updateFn, true);
  } finally {
    Listener = listener;
    Owner = owner;
  }
}
function createSignal(value, options) {
  options = options ? Object.assign({}, signalOptions, options) : signalOptions;
  const s = {
    value,
    observers: null,
    observerSlots: null,
    comparator: options.equals || undefined
  };
  const setter = value => {
    if (typeof value === "function") {
      value = value(s.value);
    }
    return writeSignal(s, value);
  };
  return [readSignal.bind(s), setter];
}
function createComputed(fn, value, options) {
  const c = createComputation(fn, value, true, STALE);
  updateComputation(c);
}
function createRenderEffect(fn, value, options) {
  const c = createComputation(fn, value, false, STALE);
  updateComputation(c);
}
function createEffect(fn, value, options) {
  runEffects = runUserEffects;
  const c = createComputation(fn, value, false, STALE);
  if (!options || !options.render) c.user = true;
  Effects ? Effects.push(c) : updateComputation(c);
}
function createMemo(fn, value, options) {
  options = options ? Object.assign({}, signalOptions, options) : signalOptions;
  const c = createComputation(fn, value, true, 0);
  c.observers = null;
  c.observerSlots = null;
  c.comparator = options.equals || undefined;
  updateComputation(c);
  return readSignal.bind(c);
}
function isPromise(v) {
  return v && typeof v === "object" && "then" in v;
}
function createResource(pSource, pFetcher, pOptions) {
  let source;
  let fetcher;
  let options;
  if ((arguments.length === 2 && typeof pFetcher === "object") || arguments.length === 1) {
    source = true;
    fetcher = pSource;
    options = pFetcher || {};
  } else {
    source = pSource;
    fetcher = pFetcher;
    options = pOptions || {};
  }
  let pr = null,
    initP = NO_INIT,
    scheduled = false,
    resolved = "initialValue" in options,
    dynamic = typeof source === "function" && createMemo(source);
  const contexts = new Set(),
    [value, setValue] = (options.storage || createSignal)(options.initialValue),
    [error, setError] = createSignal(undefined),
    [track, trigger] = createSignal(undefined, {
      equals: false
    }),
    [state, setState] = createSignal(resolved ? "ready" : "unresolved");
  function loadEnd(p, v, error, key) {
    if (pr === p) {
      pr = null;
      key !== undefined && (resolved = true);
      if ((p === initP || v === initP) && options.onHydrated)
        queueMicrotask(() =>
          options.onHydrated(key, {
            value: v
          })
        );
      initP = NO_INIT;
      completeLoad(v, error);
    }
    return v;
  }
  function completeLoad(v, err) {
    runUpdates(() => {
      if (err === undefined) setValue(() => v);
      setState(err !== undefined ? "errored" : resolved ? "ready" : "unresolved");
      setError(err);
      for (const c of contexts.keys()) c.decrement();
      contexts.clear();
    }, false);
  }
  function read() {
    const c = SuspenseContext ,
      v = value(),
      err = error();
    if (err !== undefined && !pr) throw err;
    if (Listener && !Listener.user && c) {
      createComputed(() => {
        track();
        if (pr) {
          if (c.resolved  ) ;
          else if (!contexts.has(c)) {
            c.increment();
            contexts.add(c);
          }
        }
      });
    }
    return v;
  }
  function load(refetching = true) {
    if (refetching !== false && scheduled) return;
    scheduled = false;
    const lookup = dynamic ? dynamic() : source;
    if (lookup == null || lookup === false) {
      loadEnd(pr, untrack(value));
      return;
    }
    const p =
      initP !== NO_INIT
        ? initP
        : untrack(() =>
            fetcher(lookup, {
              value: value(),
              refetching
            })
          );
    if (!isPromise(p)) {
      loadEnd(pr, p, undefined, lookup);
      return p;
    }
    pr = p;
    if ("value" in p) {
      if (p.status === "success") loadEnd(pr, p.value, undefined, lookup);
      else loadEnd(pr, undefined, undefined, lookup);
      return p;
    }
    scheduled = true;
    queueMicrotask(() => (scheduled = false));
    runUpdates(() => {
      setState(resolved ? "refreshing" : "pending");
      trigger();
    }, false);
    return p.then(
      v => loadEnd(p, v, undefined, lookup),
      e => loadEnd(p, undefined, castError(e), lookup)
    );
  }
  Object.defineProperties(read, {
    state: {
      get: () => state()
    },
    error: {
      get: () => error()
    },
    loading: {
      get() {
        const s = state();
        return s === "pending" || s === "refreshing";
      }
    },
    latest: {
      get() {
        if (!resolved) return read();
        const err = error();
        if (err && !pr) throw err;
        return value();
      }
    }
  });
  if (dynamic) createComputed(() => load(false));
  else load(false);
  return [
    read,
    {
      refetch: load,
      mutate: setValue
    }
  ];
}
function batch(fn) {
  return runUpdates(fn, false);
}
function untrack(fn) {
  if (Listener === null) return fn();
  const listener = Listener;
  Listener = null;
  try {
    if (ExternalSourceConfig) ;
    return fn();
  } finally {
    Listener = listener;
  }
}
function onCleanup(fn) {
  if (Owner === null);
  else if (Owner.cleanups === null) Owner.cleanups = [fn];
  else Owner.cleanups.push(fn);
  return fn;
}
function getListener() {
  return Listener;
}
function children(fn) {
  const children = createMemo(fn);
  const memo = createMemo(() => resolveChildren(children()));
  memo.toArray = () => {
    const c = memo();
    return Array.isArray(c) ? c : c != null ? [c] : [];
  };
  return memo;
}
let SuspenseContext;
function readSignal() {
  if (this.sources && (this.state)) {
    if ((this.state) === STALE) updateComputation(this);
    else {
      const updates = Updates;
      Updates = null;
      runUpdates(() => lookUpstream(this), false);
      Updates = updates;
    }
  }
  if (Listener) {
    const sSlot = this.observers ? this.observers.length : 0;
    if (!Listener.sources) {
      Listener.sources = [this];
      Listener.sourceSlots = [sSlot];
    } else {
      Listener.sources.push(this);
      Listener.sourceSlots.push(sSlot);
    }
    if (!this.observers) {
      this.observers = [Listener];
      this.observerSlots = [Listener.sources.length - 1];
    } else {
      this.observers.push(Listener);
      this.observerSlots.push(Listener.sources.length - 1);
    }
  }
  return this.value;
}
function writeSignal(node, value, isComp) {
  let current =
    node.value;
  if (!node.comparator || !node.comparator(current, value)) {
    node.value = value;
    if (node.observers && node.observers.length) {
      runUpdates(() => {
        for (let i = 0; i < node.observers.length; i += 1) {
          const o = node.observers[i];
          const TransitionRunning = Transition && Transition.running;
          if (TransitionRunning && Transition.disposed.has(o)) ;
          if (TransitionRunning ? !o.tState : !o.state) {
            if (o.pure) Updates.push(o);
            else Effects.push(o);
            if (o.observers) markDownstream(o);
          }
          if (!TransitionRunning) o.state = STALE;
        }
        if (Updates.length > 10e5) {
          Updates = [];
          if (false);
          throw new Error();
        }
      }, false);
    }
  }
  return value;
}
function updateComputation(node) {
  if (!node.fn) return;
  cleanNode(node);
  const time = ExecCount;
  runComputation(
    node,
    node.value,
    time
  );
}
function runComputation(node, value, time) {
  let nextValue;
  const owner = Owner,
    listener = Listener;
  Listener = Owner = node;
  try {
    nextValue = node.fn(value);
  } catch (err) {
    if (node.pure) {
      {
        node.state = STALE;
        node.owned && node.owned.forEach(cleanNode);
        node.owned = null;
      }
    }
    node.updatedAt = time + 1;
    return handleError$1(err);
  } finally {
    Listener = listener;
    Owner = owner;
  }
  if (!node.updatedAt || node.updatedAt <= time) {
    if (node.updatedAt != null && "observers" in node) {
      writeSignal(node, nextValue);
    } else node.value = nextValue;
    node.updatedAt = time;
  }
}
function createComputation(fn, init, pure, state = STALE, options) {
  const c = {
    fn,
    state: state,
    updatedAt: null,
    owned: null,
    sources: null,
    sourceSlots: null,
    cleanups: null,
    value: init,
    owner: Owner,
    context: Owner ? Owner.context : null,
    pure
  };
  if (Owner === null);
  else if (Owner !== UNOWNED) {
    {
      if (!Owner.owned) Owner.owned = [c];
      else Owner.owned.push(c);
    }
  }
  return c;
}
function runTop(node) {
  if ((node.state) === 0) return;
  if ((node.state) === PENDING) return lookUpstream(node);
  if (node.suspense && untrack(node.suspense.inFallback)) return node.suspense.effects.push(node);
  const ancestors = [node];
  while ((node = node.owner) && (!node.updatedAt || node.updatedAt < ExecCount)) {
    if (node.state) ancestors.push(node);
  }
  for (let i = ancestors.length - 1; i >= 0; i--) {
    node = ancestors[i];
    if ((node.state) === STALE) {
      updateComputation(node);
    } else if ((node.state) === PENDING) {
      const updates = Updates;
      Updates = null;
      runUpdates(() => lookUpstream(node, ancestors[0]), false);
      Updates = updates;
    }
  }
}
function runUpdates(fn, init) {
  if (Updates) return fn();
  let wait = false;
  if (!init) Updates = [];
  if (Effects) wait = true;
  else Effects = [];
  ExecCount++;
  try {
    const res = fn();
    completeUpdates(wait);
    return res;
  } catch (err) {
    if (!wait) Effects = null;
    Updates = null;
    handleError$1(err);
  }
}
function completeUpdates(wait) {
  if (Updates) {
    runQueue(Updates);
    Updates = null;
  }
  if (wait) return;
  const e = Effects;
  Effects = null;
  if (e.length) runUpdates(() => runEffects(e), false);
}
function runQueue(queue) {
  for (let i = 0; i < queue.length; i++) runTop(queue[i]);
}
function runUserEffects(queue) {
  let i,
    userLength = 0;
  for (i = 0; i < queue.length; i++) {
    const e = queue[i];
    if (!e.user) runTop(e);
    else queue[userLength++] = e;
  }
  for (i = 0; i < userLength; i++) runTop(queue[i]);
}
function lookUpstream(node, ignore) {
  node.state = 0;
  for (let i = 0; i < node.sources.length; i += 1) {
    const source = node.sources[i];
    if (source.sources) {
      const state = source.state;
      if (state === STALE) {
        if (source !== ignore && (!source.updatedAt || source.updatedAt < ExecCount))
          runTop(source);
      } else if (state === PENDING) lookUpstream(source, ignore);
    }
  }
}
function markDownstream(node) {
  for (let i = 0; i < node.observers.length; i += 1) {
    const o = node.observers[i];
    if (!o.state) {
      o.state = PENDING;
      if (o.pure) Updates.push(o);
      else Effects.push(o);
      o.observers && markDownstream(o);
    }
  }
}
function cleanNode(node) {
  let i;
  if (node.sources) {
    while (node.sources.length) {
      const source = node.sources.pop(),
        index = node.sourceSlots.pop(),
        obs = source.observers;
      if (obs && obs.length) {
        const n = obs.pop(),
          s = source.observerSlots.pop();
        if (index < obs.length) {
          n.sourceSlots[s] = index;
          obs[index] = n;
          source.observerSlots[index] = s;
        }
      }
    }
  }
  if (node.owned) {
    for (i = node.owned.length - 1; i >= 0; i--) cleanNode(node.owned[i]);
    node.owned = null;
  }
  if (node.cleanups) {
    for (i = node.cleanups.length - 1; i >= 0; i--) node.cleanups[i]();
    node.cleanups = null;
  }
  node.state = 0;
}
function castError(err) {
  if (err instanceof Error) return err;
  return new Error(typeof err === "string" ? err : "Unknown error", {
    cause: err
  });
}
function handleError$1(err, owner = Owner) {
  const error = castError(err);
  throw error;
}
function resolveChildren(children) {
  if (typeof children === "function" && !children.length) return resolveChildren(children());
  if (Array.isArray(children)) {
    const results = [];
    for (let i = 0; i < children.length; i++) {
      const result = resolveChildren(children[i]);
      Array.isArray(result) ? results.push.apply(results, result) : results.push(result);
    }
    return results;
  }
  return children;
}

const FALLBACK = Symbol("fallback");
function dispose(d) {
  for (let i = 0; i < d.length; i++) d[i]();
}
function mapArray(list, mapFn, options = {}) {
  let items = [],
    mapped = [],
    disposers = [],
    len = 0,
    indexes = mapFn.length > 1 ? [] : null;
  onCleanup(() => dispose(disposers));
  return () => {
    let newItems = list() || [],
      i,
      j;
    newItems[$TRACK];
    return untrack(() => {
      let newLen = newItems.length,
        newIndices,
        newIndicesNext,
        temp,
        tempdisposers,
        tempIndexes,
        start,
        end,
        newEnd,
        item;
      if (newLen === 0) {
        if (len !== 0) {
          dispose(disposers);
          disposers = [];
          items = [];
          mapped = [];
          len = 0;
          indexes && (indexes = []);
        }
        if (options.fallback) {
          items = [FALLBACK];
          mapped[0] = createRoot(disposer => {
            disposers[0] = disposer;
            return options.fallback();
          });
          len = 1;
        }
      } else if (len === 0) {
        mapped = new Array(newLen);
        for (j = 0; j < newLen; j++) {
          items[j] = newItems[j];
          mapped[j] = createRoot(mapper);
        }
        len = newLen;
      } else {
        temp = new Array(newLen);
        tempdisposers = new Array(newLen);
        indexes && (tempIndexes = new Array(newLen));
        for (
          start = 0, end = Math.min(len, newLen);
          start < end && items[start] === newItems[start];
          start++
        );
        for (
          end = len - 1, newEnd = newLen - 1;
          end >= start && newEnd >= start && items[end] === newItems[newEnd];
          end--, newEnd--
        ) {
          temp[newEnd] = mapped[end];
          tempdisposers[newEnd] = disposers[end];
          indexes && (tempIndexes[newEnd] = indexes[end]);
        }
        newIndices = new Map();
        newIndicesNext = new Array(newEnd + 1);
        for (j = newEnd; j >= start; j--) {
          item = newItems[j];
          i = newIndices.get(item);
          newIndicesNext[j] = i === undefined ? -1 : i;
          newIndices.set(item, j);
        }
        for (i = start; i <= end; i++) {
          item = items[i];
          j = newIndices.get(item);
          if (j !== undefined && j !== -1) {
            temp[j] = mapped[i];
            tempdisposers[j] = disposers[i];
            indexes && (tempIndexes[j] = indexes[i]);
            j = newIndicesNext[j];
            newIndices.set(item, j);
          } else disposers[i]();
        }
        for (j = start; j < newLen; j++) {
          if (j in temp) {
            mapped[j] = temp[j];
            disposers[j] = tempdisposers[j];
            if (indexes) {
              indexes[j] = tempIndexes[j];
              indexes[j](j);
            }
          } else mapped[j] = createRoot(mapper);
        }
        mapped = mapped.slice(0, (len = newLen));
        items = newItems.slice(0);
      }
      return mapped;
    });
    function mapper(disposer) {
      disposers[j] = disposer;
      if (indexes) {
        const [s, set] = createSignal(j);
        indexes[j] = set;
        return mapFn(newItems[j], s);
      }
      return mapFn(newItems[j]);
    }
  };
}
function createComponent(Comp, props) {
  return untrack(() => Comp(props || {}));
}
function trueFn() {
  return true;
}
const propTraps = {
  get(_, property, receiver) {
    if (property === $PROXY) return receiver;
    return _.get(property);
  },
  has(_, property) {
    if (property === $PROXY) return true;
    return _.has(property);
  },
  set: trueFn,
  deleteProperty: trueFn,
  getOwnPropertyDescriptor(_, property) {
    return {
      configurable: true,
      enumerable: true,
      get() {
        return _.get(property);
      },
      set: trueFn,
      deleteProperty: trueFn
    };
  },
  ownKeys(_) {
    return _.keys();
  }
};
function resolveSource(s) {
  return !(s = typeof s === "function" ? s() : s) ? {} : s;
}
function resolveSources() {
  for (let i = 0, length = this.length; i < length; ++i) {
    const v = this[i]();
    if (v !== undefined) return v;
  }
}
function mergeProps(...sources) {
  let proxy = false;
  for (let i = 0; i < sources.length; i++) {
    const s = sources[i];
    proxy = proxy || (!!s && $PROXY in s);
    sources[i] = typeof s === "function" ? ((proxy = true), createMemo(s)) : s;
  }
  if (proxy) {
    return new Proxy(
      {
        get(property) {
          for (let i = sources.length - 1; i >= 0; i--) {
            const v = resolveSource(sources[i])[property];
            if (v !== undefined) return v;
          }
        },
        has(property) {
          for (let i = sources.length - 1; i >= 0; i--) {
            if (property in resolveSource(sources[i])) return true;
          }
          return false;
        },
        keys() {
          const keys = [];
          for (let i = 0; i < sources.length; i++)
            keys.push(...Object.keys(resolveSource(sources[i])));
          return [...new Set(keys)];
        }
      },
      propTraps
    );
  }
  const sourcesMap = {};
  const defined = Object.create(null);
  for (let i = sources.length - 1; i >= 0; i--) {
    const source = sources[i];
    if (!source) continue;
    const sourceKeys = Object.getOwnPropertyNames(source);
    for (let i = sourceKeys.length - 1; i >= 0; i--) {
      const key = sourceKeys[i];
      if (key === "__proto__" || key === "constructor") continue;
      const desc = Object.getOwnPropertyDescriptor(source, key);
      if (!defined[key]) {
        defined[key] = desc.get
          ? {
              enumerable: true,
              configurable: true,
              get: resolveSources.bind((sourcesMap[key] = [desc.get.bind(source)]))
            }
          : desc.value !== undefined
          ? desc
          : undefined;
      } else {
        const sources = sourcesMap[key];
        if (sources) {
          if (desc.get) sources.push(desc.get.bind(source));
          else if (desc.value !== undefined) sources.push(() => desc.value);
        }
      }
    }
  }
  const target = {};
  const definedKeys = Object.keys(defined);
  for (let i = definedKeys.length - 1; i >= 0; i--) {
    const key = definedKeys[i],
      desc = defined[key];
    if (desc && desc.get) Object.defineProperty(target, key, desc);
    else target[key] = desc ? desc.value : undefined;
  }
  return target;
}
function splitProps(props, ...keys) {
  if ($PROXY in props) {
    const blocked = new Set(keys.length > 1 ? keys.flat() : keys[0]);
    const res = keys.map(k => {
      return new Proxy(
        {
          get(property) {
            return k.includes(property) ? props[property] : undefined;
          },
          has(property) {
            return k.includes(property) && property in props;
          },
          keys() {
            return k.filter(property => property in props);
          }
        },
        propTraps
      );
    });
    res.push(
      new Proxy(
        {
          get(property) {
            return blocked.has(property) ? undefined : props[property];
          },
          has(property) {
            return blocked.has(property) ? false : property in props;
          },
          keys() {
            return Object.keys(props).filter(k => !blocked.has(k));
          }
        },
        propTraps
      )
    );
    return res;
  }
  const otherObject = {};
  const objects = keys.map(() => ({}));
  for (const propName of Object.getOwnPropertyNames(props)) {
    const desc = Object.getOwnPropertyDescriptor(props, propName);
    const isDefaultDesc =
      !desc.get && !desc.set && desc.enumerable && desc.writable && desc.configurable;
    let blocked = false;
    let objectIndex = 0;
    for (const k of keys) {
      if (k.includes(propName)) {
        blocked = true;
        isDefaultDesc
          ? (objects[objectIndex][propName] = desc.value)
          : Object.defineProperty(objects[objectIndex], propName, desc);
      }
      ++objectIndex;
    }
    if (!blocked) {
      isDefaultDesc
        ? (otherObject[propName] = desc.value)
        : Object.defineProperty(otherObject, propName, desc);
    }
  }
  return [...objects, otherObject];
}

const narrowedError = name => `Stale read from <${name}>.`;
function For(props) {
  const fallback = "fallback" in props && {
    fallback: () => props.fallback
  };
  return createMemo(mapArray(() => props.each, props.children, fallback || undefined));
}
function Show(props) {
  const keyed = props.keyed;
  const condition = createMemo(() => props.when, undefined, {
    equals: (a, b) => (keyed ? a === b : !a === !b)
  });
  return createMemo(
    () => {
      const c = condition();
      if (c) {
        const child = props.children;
        const fn = typeof child === "function" && child.length > 0;
        return fn
          ? untrack(() =>
              child(
                keyed
                  ? c
                  : () => {
                      if (!untrack(condition)) throw narrowedError("Show");
                      return props.when;
                    }
              )
            )
          : child;
      }
      return props.fallback;
    },
    undefined,
    undefined
  );
}
function Switch(props) {
  let keyed = false;
  const equals = (a, b) => (keyed ? a[1] === b[1] : !a[1] === !b[1]) && a[2] === b[2];
  const conditions = children(() => props.children),
    evalConditions = createMemo(
      () => {
        let conds = conditions();
        if (!Array.isArray(conds)) conds = [conds];
        for (let i = 0; i < conds.length; i++) {
          const c = conds[i].when;
          if (c) {
            keyed = !!conds[i].keyed;
            return [i, c, conds[i]];
          }
        }
        return [-1];
      },
      undefined,
      {
        equals
      }
    );
  return createMemo(
    () => {
      const [index, when, cond] = evalConditions();
      if (index < 0) return props.fallback;
      const c = cond.children;
      const fn = typeof c === "function" && c.length > 0;
      return fn
        ? untrack(() =>
            c(
              keyed
                ? when
                : () => {
                    if (untrack(evalConditions)[0] !== index) throw narrowedError("Match");
                    return cond.when;
                  }
            )
          )
        : c;
    },
    undefined,
    undefined
  );
}
function Match(props) {
  return props;
}

const booleans = [
  "allowfullscreen",
  "async",
  "autofocus",
  "autoplay",
  "checked",
  "controls",
  "default",
  "disabled",
  "formnovalidate",
  "hidden",
  "indeterminate",
  "inert",
  "ismap",
  "loop",
  "multiple",
  "muted",
  "nomodule",
  "novalidate",
  "open",
  "playsinline",
  "readonly",
  "required",
  "reversed",
  "seamless",
  "selected"
];
const Properties = /*#__PURE__*/ new Set([
  "className",
  "value",
  "readOnly",
  "formNoValidate",
  "isMap",
  "noModule",
  "playsInline",
  ...booleans
]);
const ChildProperties = /*#__PURE__*/ new Set([
  "innerHTML",
  "textContent",
  "innerText",
  "children"
]);
const Aliases = /*#__PURE__*/ Object.assign(Object.create(null), {
  className: "class",
  htmlFor: "for"
});
const PropAliases = /*#__PURE__*/ Object.assign(Object.create(null), {
  class: "className",
  formnovalidate: {
    $: "formNoValidate",
    BUTTON: 1,
    INPUT: 1
  },
  ismap: {
    $: "isMap",
    IMG: 1
  },
  nomodule: {
    $: "noModule",
    SCRIPT: 1
  },
  playsinline: {
    $: "playsInline",
    VIDEO: 1
  },
  readonly: {
    $: "readOnly",
    INPUT: 1,
    TEXTAREA: 1
  }
});
function getPropAlias(prop, tagName) {
  const a = PropAliases[prop];
  return typeof a === "object" ? (a[tagName] ? a["$"] : undefined) : a;
}
const DelegatedEvents = /*#__PURE__*/ new Set([
  "beforeinput",
  "click",
  "dblclick",
  "contextmenu",
  "focusin",
  "focusout",
  "input",
  "keydown",
  "keyup",
  "mousedown",
  "mousemove",
  "mouseout",
  "mouseover",
  "mouseup",
  "pointerdown",
  "pointermove",
  "pointerout",
  "pointerover",
  "pointerup",
  "touchend",
  "touchmove",
  "touchstart"
]);
const SVGNamespace = {
  xlink: "http://www.w3.org/1999/xlink",
  xml: "http://www.w3.org/XML/1998/namespace"
};

function reconcileArrays(parentNode, a, b) {
  let bLength = b.length,
    aEnd = a.length,
    bEnd = bLength,
    aStart = 0,
    bStart = 0,
    after = a[aEnd - 1].nextSibling,
    map = null;
  while (aStart < aEnd || bStart < bEnd) {
    if (a[aStart] === b[bStart]) {
      aStart++;
      bStart++;
      continue;
    }
    while (a[aEnd - 1] === b[bEnd - 1]) {
      aEnd--;
      bEnd--;
    }
    if (aEnd === aStart) {
      const node = bEnd < bLength ? (bStart ? b[bStart - 1].nextSibling : b[bEnd - bStart]) : after;
      while (bStart < bEnd) parentNode.insertBefore(b[bStart++], node);
    } else if (bEnd === bStart) {
      while (aStart < aEnd) {
        if (!map || !map.has(a[aStart])) a[aStart].remove();
        aStart++;
      }
    } else if (a[aStart] === b[bEnd - 1] && b[bStart] === a[aEnd - 1]) {
      const node = a[--aEnd].nextSibling;
      parentNode.insertBefore(b[bStart++], a[aStart++].nextSibling);
      parentNode.insertBefore(b[--bEnd], node);
      a[aEnd] = b[bEnd];
    } else {
      if (!map) {
        map = new Map();
        let i = bStart;
        while (i < bEnd) map.set(b[i], i++);
      }
      const index = map.get(a[aStart]);
      if (index != null) {
        if (bStart < index && index < bEnd) {
          let i = aStart,
            sequence = 1,
            t;
          while (++i < aEnd && i < bEnd) {
            if ((t = map.get(a[i])) == null || t !== index + sequence) break;
            sequence++;
          }
          if (sequence > index - bStart) {
            const node = a[aStart];
            while (bStart < index) parentNode.insertBefore(b[bStart++], node);
          } else parentNode.replaceChild(b[bStart++], a[aStart++]);
        } else aStart++;
      } else a[aStart++].remove();
    }
  }
}

const $$EVENTS = "_$DX_DELEGATE";
function render(code, element, init, options = {}) {
  let disposer;
  createRoot(dispose => {
    disposer = dispose;
    element === document
      ? code()
      : insert(element, code(), element.firstChild ? null : undefined, init);
  }, options.owner);
  return () => {
    disposer();
    element.textContent = "";
  };
}
function template(html, isCE, isSVG) {
  let node;
  const create = () => {
    const t = document.createElement("template");
    t.innerHTML = html;
    return isSVG ? t.content.firstChild.firstChild : t.content.firstChild;
  };
  const fn = isCE
    ? () => untrack(() => document.importNode(node || (node = create()), true))
    : () => (node || (node = create())).cloneNode(true);
  fn.cloneNode = fn;
  return fn;
}
function delegateEvents(eventNames, document = window.document) {
  const e = document[$$EVENTS] || (document[$$EVENTS] = new Set());
  for (let i = 0, l = eventNames.length; i < l; i++) {
    const name = eventNames[i];
    if (!e.has(name)) {
      e.add(name);
      document.addEventListener(name, eventHandler);
    }
  }
}
function setAttribute(node, name, value) {
  if (value == null) node.removeAttribute(name);
  else node.setAttribute(name, value);
}
function setAttributeNS(node, namespace, name, value) {
  if (value == null) node.removeAttributeNS(namespace, name);
  else node.setAttributeNS(namespace, name, value);
}
function className(node, value) {
  if (value == null) node.removeAttribute("class");
  else node.className = value;
}
function addEventListener(node, name, handler, delegate) {
  if (delegate) {
    if (Array.isArray(handler)) {
      node[`$$${name}`] = handler[0];
      node[`$$${name}Data`] = handler[1];
    } else node[`$$${name}`] = handler;
  } else if (Array.isArray(handler)) {
    const handlerFn = handler[0];
    node.addEventListener(name, (handler[0] = e => handlerFn.call(node, handler[1], e)));
  } else node.addEventListener(name, handler);
}
function classList(node, value, prev = {}) {
  const classKeys = Object.keys(value || {}),
    prevKeys = Object.keys(prev);
  let i, len;
  for (i = 0, len = prevKeys.length; i < len; i++) {
    const key = prevKeys[i];
    if (!key || key === "undefined" || value[key]) continue;
    toggleClassKey(node, key, false);
    delete prev[key];
  }
  for (i = 0, len = classKeys.length; i < len; i++) {
    const key = classKeys[i],
      classValue = !!value[key];
    if (!key || key === "undefined" || prev[key] === classValue || !classValue) continue;
    toggleClassKey(node, key, true);
    prev[key] = classValue;
  }
  return prev;
}
function style(node, value, prev) {
  if (!value) return prev ? setAttribute(node, "style") : value;
  const nodeStyle = node.style;
  if (typeof value === "string") return (nodeStyle.cssText = value);
  typeof prev === "string" && (nodeStyle.cssText = prev = undefined);
  prev || (prev = {});
  value || (value = {});
  let v, s;
  for (s in prev) {
    value[s] == null && nodeStyle.removeProperty(s);
    delete prev[s];
  }
  for (s in value) {
    v = value[s];
    if (v !== prev[s]) {
      nodeStyle.setProperty(s, v);
      prev[s] = v;
    }
  }
  return prev;
}
function spread$1(node, props = {}, isSVG, skipChildren) {
  const prevProps = {};
  if (!skipChildren) {
    createRenderEffect(
      () => (prevProps.children = insertExpression(node, props.children, prevProps.children))
    );
  }
  createRenderEffect(() => props.ref && props.ref(node));
  createRenderEffect(() => assign(node, props, isSVG, true, prevProps, true));
  return prevProps;
}
function use(fn, element, arg) {
  return untrack(() => fn(element, arg));
}
function insert(parent, accessor, marker, initial) {
  if (marker !== undefined && !initial) initial = [];
  if (typeof accessor !== "function") return insertExpression(parent, accessor, initial, marker);
  createRenderEffect(current => insertExpression(parent, accessor(), current, marker), initial);
}
function assign(node, props, isSVG, skipChildren, prevProps = {}, skipRef = false) {
  props || (props = {});
  for (const prop in prevProps) {
    if (!(prop in props)) {
      if (prop === "children") continue;
      prevProps[prop] = assignProp(node, prop, null, prevProps[prop], isSVG, skipRef);
    }
  }
  for (const prop in props) {
    if (prop === "children") {
      if (!skipChildren) insertExpression(node, props.children);
      continue;
    }
    const value = props[prop];
    prevProps[prop] = assignProp(node, prop, value, prevProps[prop], isSVG, skipRef);
  }
}
function toPropertyName(name) {
  return name.toLowerCase().replace(/-([a-z])/g, (_, w) => w.toUpperCase());
}
function toggleClassKey(node, key, value) {
  const classNames = key.trim().split(/\s+/);
  for (let i = 0, nameLen = classNames.length; i < nameLen; i++)
    node.classList.toggle(classNames[i], value);
}
function assignProp(node, prop, value, prev, isSVG, skipRef) {
  let isCE, isProp, isChildProp, propAlias, forceProp;
  if (prop === "style") return style(node, value, prev);
  if (prop === "classList") return classList(node, value, prev);
  if (value === prev) return prev;
  if (prop === "ref") {
    if (!skipRef) value(node);
  } else if (prop.slice(0, 3) === "on:") {
    const e = prop.slice(3);
    prev && node.removeEventListener(e, prev);
    value && node.addEventListener(e, value);
  } else if (prop.slice(0, 10) === "oncapture:") {
    const e = prop.slice(10);
    prev && node.removeEventListener(e, prev, true);
    value && node.addEventListener(e, value, true);
  } else if (prop.slice(0, 2) === "on") {
    const name = prop.slice(2).toLowerCase();
    const delegate = DelegatedEvents.has(name);
    if (!delegate && prev) {
      const h = Array.isArray(prev) ? prev[0] : prev;
      node.removeEventListener(name, h);
    }
    if (delegate || value) {
      addEventListener(node, name, value, delegate);
      delegate && delegateEvents([name]);
    }
  } else if (prop.slice(0, 5) === "attr:") {
    setAttribute(node, prop.slice(5), value);
  } else if (
    (forceProp = prop.slice(0, 5) === "prop:") ||
    (isChildProp = ChildProperties.has(prop)) ||
    (!isSVG &&
      ((propAlias = getPropAlias(prop, node.tagName)) || (isProp = Properties.has(prop)))) ||
    (isCE = node.nodeName.includes("-"))
  ) {
    if (forceProp) {
      prop = prop.slice(5);
      isProp = true;
    }
    if (prop === "class" || prop === "className") className(node, value);
    else if (isCE && !isProp && !isChildProp) node[toPropertyName(prop)] = value;
    else node[propAlias || prop] = value;
  } else {
    const ns = isSVG && prop.indexOf(":") > -1 && SVGNamespace[prop.split(":")[0]];
    if (ns) setAttributeNS(node, ns, prop, value);
    else setAttribute(node, Aliases[prop] || prop, value);
  }
  return value;
}
function eventHandler(e) {
  const key = `$$${e.type}`;
  let node = (e.composedPath && e.composedPath()[0]) || e.target;
  if (e.target !== node) {
    Object.defineProperty(e, "target", {
      configurable: true,
      value: node
    });
  }
  Object.defineProperty(e, "currentTarget", {
    configurable: true,
    get() {
      return node || document;
    }
  });
  while (node) {
    const handler = node[key];
    if (handler && !node.disabled) {
      const data = node[`${key}Data`];
      data !== undefined ? handler.call(node, data, e) : handler.call(node, e);
      if (e.cancelBubble) return;
    }
    node = node._$host || node.parentNode || node.host;
  }
}
function insertExpression(parent, value, current, marker, unwrapArray) {
  while (typeof current === "function") current = current();
  if (value === current) return current;
  const t = typeof value,
    multi = marker !== undefined;
  parent = (multi && current[0] && current[0].parentNode) || parent;
  if (t === "string" || t === "number") {
    if (t === "number") value = value.toString();
    if (multi) {
      let node = current[0];
      if (node && node.nodeType === 3) {
        node.data !== value && (node.data = value);
      } else node = document.createTextNode(value);
      current = cleanChildren(parent, current, marker, node);
    } else {
      if (current !== "" && typeof current === "string") {
        current = parent.firstChild.data = value;
      } else current = parent.textContent = value;
    }
  } else if (value == null || t === "boolean") {
    current = cleanChildren(parent, current, marker);
  } else if (t === "function") {
    createRenderEffect(() => {
      let v = value();
      while (typeof v === "function") v = v();
      current = insertExpression(parent, v, current, marker);
    });
    return () => current;
  } else if (Array.isArray(value)) {
    const array = [];
    const currentArray = current && Array.isArray(current);
    if (normalizeIncomingArray(array, value, current, unwrapArray)) {
      createRenderEffect(() => (current = insertExpression(parent, array, current, marker, true)));
      return () => current;
    }
    if (array.length === 0) {
      current = cleanChildren(parent, current, marker);
      if (multi) return current;
    } else if (currentArray) {
      if (current.length === 0) {
        appendNodes(parent, array, marker);
      } else reconcileArrays(parent, current, array);
    } else {
      current && cleanChildren(parent);
      appendNodes(parent, array);
    }
    current = array;
  } else if (value.nodeType) {
    if (Array.isArray(current)) {
      if (multi) return (current = cleanChildren(parent, current, marker, value));
      cleanChildren(parent, current, null, value);
    } else if (current == null || current === "" || !parent.firstChild) {
      parent.appendChild(value);
    } else parent.replaceChild(value, parent.firstChild);
    current = value;
  } else;
  return current;
}
function normalizeIncomingArray(normalized, array, current, unwrap) {
  let dynamic = false;
  for (let i = 0, len = array.length; i < len; i++) {
    let item = array[i],
      prev = current && current[normalized.length],
      t;
    if (item == null || item === true || item === false);
    else if ((t = typeof item) === "object" && item.nodeType) {
      normalized.push(item);
    } else if (Array.isArray(item)) {
      dynamic = normalizeIncomingArray(normalized, item, prev) || dynamic;
    } else if (t === "function") {
      if (unwrap) {
        while (typeof item === "function") item = item();
        dynamic =
          normalizeIncomingArray(
            normalized,
            Array.isArray(item) ? item : [item],
            Array.isArray(prev) ? prev : [prev]
          ) || dynamic;
      } else {
        normalized.push(item);
        dynamic = true;
      }
    } else {
      const value = String(item);
      if (prev && prev.nodeType === 3 && prev.data === value) normalized.push(prev);
      else normalized.push(document.createTextNode(value));
    }
  }
  return dynamic;
}
function appendNodes(parent, array, marker = null) {
  for (let i = 0, len = array.length; i < len; i++) parent.insertBefore(array[i], marker);
}
function cleanChildren(parent, current, marker, replacement) {
  if (marker === undefined) return (parent.textContent = "");
  const node = replacement || document.createTextNode("");
  if (current.length) {
    let inserted = false;
    for (let i = current.length - 1; i >= 0; i--) {
      const el = current[i];
      if (node !== el) {
        const isParent = el.parentNode === parent;
        if (!inserted && !i)
          isParent ? parent.replaceChild(node, el) : parent.insertBefore(node, marker);
        else isParent && el.remove();
      } else inserted = true;
    }
  } else parent.insertBefore(node, marker);
  return [node];
}

const isServer = false;

function bind(fn, thisArg) {
  return function wrap() {
    return fn.apply(thisArg, arguments);
  };
}

// utils is a library of generic helper functions non-specific to axios

const {toString} = Object.prototype;
const {getPrototypeOf} = Object;

const kindOf = (cache => thing => {
    const str = toString.call(thing);
    return cache[str] || (cache[str] = str.slice(8, -1).toLowerCase());
})(Object.create(null));

const kindOfTest = (type) => {
  type = type.toLowerCase();
  return (thing) => kindOf(thing) === type
};

const typeOfTest = type => thing => typeof thing === type;

/**
 * Determine if a value is an Array
 *
 * @param {Object} val The value to test
 *
 * @returns {boolean} True if value is an Array, otherwise false
 */
const {isArray} = Array;

/**
 * Determine if a value is undefined
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if the value is undefined, otherwise false
 */
const isUndefined = typeOfTest('undefined');

/**
 * Determine if a value is a Buffer
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Buffer, otherwise false
 */
function isBuffer(val) {
  return val !== null && !isUndefined(val) && val.constructor !== null && !isUndefined(val.constructor)
    && isFunction(val.constructor.isBuffer) && val.constructor.isBuffer(val);
}

/**
 * Determine if a value is an ArrayBuffer
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is an ArrayBuffer, otherwise false
 */
const isArrayBuffer = kindOfTest('ArrayBuffer');


/**
 * Determine if a value is a view on an ArrayBuffer
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a view on an ArrayBuffer, otherwise false
 */
function isArrayBufferView(val) {
  let result;
  if ((typeof ArrayBuffer !== 'undefined') && (ArrayBuffer.isView)) {
    result = ArrayBuffer.isView(val);
  } else {
    result = (val) && (val.buffer) && (isArrayBuffer(val.buffer));
  }
  return result;
}

/**
 * Determine if a value is a String
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a String, otherwise false
 */
const isString = typeOfTest('string');

/**
 * Determine if a value is a Function
 *
 * @param {*} val The value to test
 * @returns {boolean} True if value is a Function, otherwise false
 */
const isFunction = typeOfTest('function');

/**
 * Determine if a value is a Number
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Number, otherwise false
 */
const isNumber = typeOfTest('number');

/**
 * Determine if a value is an Object
 *
 * @param {*} thing The value to test
 *
 * @returns {boolean} True if value is an Object, otherwise false
 */
const isObject$1 = (thing) => thing !== null && typeof thing === 'object';

/**
 * Determine if a value is a Boolean
 *
 * @param {*} thing The value to test
 * @returns {boolean} True if value is a Boolean, otherwise false
 */
const isBoolean = thing => thing === true || thing === false;

/**
 * Determine if a value is a plain Object
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a plain Object, otherwise false
 */
const isPlainObject = (val) => {
  if (kindOf(val) !== 'object') {
    return false;
  }

  const prototype = getPrototypeOf(val);
  return (prototype === null || prototype === Object.prototype || Object.getPrototypeOf(prototype) === null) && !(Symbol.toStringTag in val) && !(Symbol.iterator in val);
};

/**
 * Determine if a value is a Date
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Date, otherwise false
 */
const isDate = kindOfTest('Date');

/**
 * Determine if a value is a File
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a File, otherwise false
 */
const isFile = kindOfTest('File');

/**
 * Determine if a value is a Blob
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Blob, otherwise false
 */
const isBlob = kindOfTest('Blob');

/**
 * Determine if a value is a FileList
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a File, otherwise false
 */
const isFileList = kindOfTest('FileList');

/**
 * Determine if a value is a Stream
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Stream, otherwise false
 */
const isStream = (val) => isObject$1(val) && isFunction(val.pipe);

/**
 * Determine if a value is a FormData
 *
 * @param {*} thing The value to test
 *
 * @returns {boolean} True if value is an FormData, otherwise false
 */
const isFormData = (thing) => {
  let kind;
  return thing && (
    (typeof FormData === 'function' && thing instanceof FormData) || (
      isFunction(thing.append) && (
        (kind = kindOf(thing)) === 'formdata' ||
        // detect form-data instance
        (kind === 'object' && isFunction(thing.toString) && thing.toString() === '[object FormData]')
      )
    )
  )
};

/**
 * Determine if a value is a URLSearchParams object
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a URLSearchParams object, otherwise false
 */
const isURLSearchParams = kindOfTest('URLSearchParams');

/**
 * Trim excess whitespace off the beginning and end of a string
 *
 * @param {String} str The String to trim
 *
 * @returns {String} The String freed of excess whitespace
 */
const trim = (str) => str.trim ?
  str.trim() : str.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, '');

/**
 * Iterate over an Array or an Object invoking a function for each item.
 *
 * If `obj` is an Array callback will be called passing
 * the value, index, and complete array for each item.
 *
 * If 'obj' is an Object callback will be called passing
 * the value, key, and complete object for each property.
 *
 * @param {Object|Array} obj The object to iterate
 * @param {Function} fn The callback to invoke for each item
 *
 * @param {Boolean} [allOwnKeys = false]
 * @returns {any}
 */
function forEach(obj, fn, {allOwnKeys = false} = {}) {
  // Don't bother if no value provided
  if (obj === null || typeof obj === 'undefined') {
    return;
  }

  let i;
  let l;

  // Force an array if not already something iterable
  if (typeof obj !== 'object') {
    /*eslint no-param-reassign:0*/
    obj = [obj];
  }

  if (isArray(obj)) {
    // Iterate over array values
    for (i = 0, l = obj.length; i < l; i++) {
      fn.call(null, obj[i], i, obj);
    }
  } else {
    // Iterate over object keys
    const keys = allOwnKeys ? Object.getOwnPropertyNames(obj) : Object.keys(obj);
    const len = keys.length;
    let key;

    for (i = 0; i < len; i++) {
      key = keys[i];
      fn.call(null, obj[key], key, obj);
    }
  }
}

function findKey(obj, key) {
  key = key.toLowerCase();
  const keys = Object.keys(obj);
  let i = keys.length;
  let _key;
  while (i-- > 0) {
    _key = keys[i];
    if (key === _key.toLowerCase()) {
      return _key;
    }
  }
  return null;
}

const _global = (() => {
  /*eslint no-undef:0*/
  if (typeof globalThis !== "undefined") return globalThis;
  return typeof self !== "undefined" ? self : (typeof window !== 'undefined' ? window : global)
})();

const isContextDefined = (context) => !isUndefined(context) && context !== _global;

/**
 * Accepts varargs expecting each argument to be an object, then
 * immutably merges the properties of each object and returns result.
 *
 * When multiple objects contain the same key the later object in
 * the arguments list will take precedence.
 *
 * Example:
 *
 * ```js
 * var result = merge({foo: 123}, {foo: 456});
 * console.log(result.foo); // outputs 456
 * ```
 *
 * @param {Object} obj1 Object to merge
 *
 * @returns {Object} Result of all merge properties
 */
function merge(/* obj1, obj2, obj3, ... */) {
  const {caseless} = isContextDefined(this) && this || {};
  const result = {};
  const assignValue = (val, key) => {
    const targetKey = caseless && findKey(result, key) || key;
    if (isPlainObject(result[targetKey]) && isPlainObject(val)) {
      result[targetKey] = merge(result[targetKey], val);
    } else if (isPlainObject(val)) {
      result[targetKey] = merge({}, val);
    } else if (isArray(val)) {
      result[targetKey] = val.slice();
    } else {
      result[targetKey] = val;
    }
  };

  for (let i = 0, l = arguments.length; i < l; i++) {
    arguments[i] && forEach(arguments[i], assignValue);
  }
  return result;
}

/**
 * Extends object a by mutably adding to it the properties of object b.
 *
 * @param {Object} a The object to be extended
 * @param {Object} b The object to copy properties from
 * @param {Object} thisArg The object to bind function to
 *
 * @param {Boolean} [allOwnKeys]
 * @returns {Object} The resulting value of object a
 */
const extend = (a, b, thisArg, {allOwnKeys}= {}) => {
  forEach(b, (val, key) => {
    if (thisArg && isFunction(val)) {
      a[key] = bind(val, thisArg);
    } else {
      a[key] = val;
    }
  }, {allOwnKeys});
  return a;
};

/**
 * Remove byte order marker. This catches EF BB BF (the UTF-8 BOM)
 *
 * @param {string} content with BOM
 *
 * @returns {string} content value without BOM
 */
const stripBOM = (content) => {
  if (content.charCodeAt(0) === 0xFEFF) {
    content = content.slice(1);
  }
  return content;
};

/**
 * Inherit the prototype methods from one constructor into another
 * @param {function} constructor
 * @param {function} superConstructor
 * @param {object} [props]
 * @param {object} [descriptors]
 *
 * @returns {void}
 */
const inherits = (constructor, superConstructor, props, descriptors) => {
  constructor.prototype = Object.create(superConstructor.prototype, descriptors);
  constructor.prototype.constructor = constructor;
  Object.defineProperty(constructor, 'super', {
    value: superConstructor.prototype
  });
  props && Object.assign(constructor.prototype, props);
};

/**
 * Resolve object with deep prototype chain to a flat object
 * @param {Object} sourceObj source object
 * @param {Object} [destObj]
 * @param {Function|Boolean} [filter]
 * @param {Function} [propFilter]
 *
 * @returns {Object}
 */
const toFlatObject = (sourceObj, destObj, filter, propFilter) => {
  let props;
  let i;
  let prop;
  const merged = {};

  destObj = destObj || {};
  // eslint-disable-next-line no-eq-null,eqeqeq
  if (sourceObj == null) return destObj;

  do {
    props = Object.getOwnPropertyNames(sourceObj);
    i = props.length;
    while (i-- > 0) {
      prop = props[i];
      if ((!propFilter || propFilter(prop, sourceObj, destObj)) && !merged[prop]) {
        destObj[prop] = sourceObj[prop];
        merged[prop] = true;
      }
    }
    sourceObj = filter !== false && getPrototypeOf(sourceObj);
  } while (sourceObj && (!filter || filter(sourceObj, destObj)) && sourceObj !== Object.prototype);

  return destObj;
};

/**
 * Determines whether a string ends with the characters of a specified string
 *
 * @param {String} str
 * @param {String} searchString
 * @param {Number} [position= 0]
 *
 * @returns {boolean}
 */
const endsWith = (str, searchString, position) => {
  str = String(str);
  if (position === undefined || position > str.length) {
    position = str.length;
  }
  position -= searchString.length;
  const lastIndex = str.indexOf(searchString, position);
  return lastIndex !== -1 && lastIndex === position;
};


/**
 * Returns new array from array like object or null if failed
 *
 * @param {*} [thing]
 *
 * @returns {?Array}
 */
const toArray = (thing) => {
  if (!thing) return null;
  if (isArray(thing)) return thing;
  let i = thing.length;
  if (!isNumber(i)) return null;
  const arr = new Array(i);
  while (i-- > 0) {
    arr[i] = thing[i];
  }
  return arr;
};

/**
 * Checking if the Uint8Array exists and if it does, it returns a function that checks if the
 * thing passed in is an instance of Uint8Array
 *
 * @param {TypedArray}
 *
 * @returns {Array}
 */
// eslint-disable-next-line func-names
const isTypedArray = (TypedArray => {
  // eslint-disable-next-line func-names
  return thing => {
    return TypedArray && thing instanceof TypedArray;
  };
})(typeof Uint8Array !== 'undefined' && getPrototypeOf(Uint8Array));

/**
 * For each entry in the object, call the function with the key and value.
 *
 * @param {Object<any, any>} obj - The object to iterate over.
 * @param {Function} fn - The function to call for each entry.
 *
 * @returns {void}
 */
const forEachEntry = (obj, fn) => {
  const generator = obj && obj[Symbol.iterator];

  const iterator = generator.call(obj);

  let result;

  while ((result = iterator.next()) && !result.done) {
    const pair = result.value;
    fn.call(obj, pair[0], pair[1]);
  }
};

/**
 * It takes a regular expression and a string, and returns an array of all the matches
 *
 * @param {string} regExp - The regular expression to match against.
 * @param {string} str - The string to search.
 *
 * @returns {Array<boolean>}
 */
const matchAll = (regExp, str) => {
  let matches;
  const arr = [];

  while ((matches = regExp.exec(str)) !== null) {
    arr.push(matches);
  }

  return arr;
};

/* Checking if the kindOfTest function returns true when passed an HTMLFormElement. */
const isHTMLForm = kindOfTest('HTMLFormElement');

const toCamelCase = str => {
  return str.toLowerCase().replace(/[-_\s]([a-z\d])(\w*)/g,
    function replacer(m, p1, p2) {
      return p1.toUpperCase() + p2;
    }
  );
};

/* Creating a function that will check if an object has a property. */
const hasOwnProperty = (({hasOwnProperty}) => (obj, prop) => hasOwnProperty.call(obj, prop))(Object.prototype);

/**
 * Determine if a value is a RegExp object
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a RegExp object, otherwise false
 */
const isRegExp = kindOfTest('RegExp');

const reduceDescriptors = (obj, reducer) => {
  const descriptors = Object.getOwnPropertyDescriptors(obj);
  const reducedDescriptors = {};

  forEach(descriptors, (descriptor, name) => {
    let ret;
    if ((ret = reducer(descriptor, name, obj)) !== false) {
      reducedDescriptors[name] = ret || descriptor;
    }
  });

  Object.defineProperties(obj, reducedDescriptors);
};

/**
 * Makes all methods read-only
 * @param {Object} obj
 */

const freezeMethods = (obj) => {
  reduceDescriptors(obj, (descriptor, name) => {
    // skip restricted props in strict mode
    if (isFunction(obj) && ['arguments', 'caller', 'callee'].indexOf(name) !== -1) {
      return false;
    }

    const value = obj[name];

    if (!isFunction(value)) return;

    descriptor.enumerable = false;

    if ('writable' in descriptor) {
      descriptor.writable = false;
      return;
    }

    if (!descriptor.set) {
      descriptor.set = () => {
        throw Error('Can not rewrite read-only method \'' + name + '\'');
      };
    }
  });
};

const toObjectSet = (arrayOrString, delimiter) => {
  const obj = {};

  const define = (arr) => {
    arr.forEach(value => {
      obj[value] = true;
    });
  };

  isArray(arrayOrString) ? define(arrayOrString) : define(String(arrayOrString).split(delimiter));

  return obj;
};

const noop$1 = () => {};

const toFiniteNumber = (value, defaultValue) => {
  value = +value;
  return Number.isFinite(value) ? value : defaultValue;
};

const ALPHA = 'abcdefghijklmnopqrstuvwxyz';

const DIGIT = '0123456789';

const ALPHABET = {
  DIGIT,
  ALPHA,
  ALPHA_DIGIT: ALPHA + ALPHA.toUpperCase() + DIGIT
};

const generateString = (size = 16, alphabet = ALPHABET.ALPHA_DIGIT) => {
  let str = '';
  const {length} = alphabet;
  while (size--) {
    str += alphabet[Math.random() * length|0];
  }

  return str;
};

/**
 * If the thing is a FormData object, return true, otherwise return false.
 *
 * @param {unknown} thing - The thing to check.
 *
 * @returns {boolean}
 */
function isSpecCompliantForm(thing) {
  return !!(thing && isFunction(thing.append) && thing[Symbol.toStringTag] === 'FormData' && thing[Symbol.iterator]);
}

const toJSONObject = (obj) => {
  const stack = new Array(10);

  const visit = (source, i) => {

    if (isObject$1(source)) {
      if (stack.indexOf(source) >= 0) {
        return;
      }

      if(!('toJSON' in source)) {
        stack[i] = source;
        const target = isArray(source) ? [] : {};

        forEach(source, (value, key) => {
          const reducedValue = visit(value, i + 1);
          !isUndefined(reducedValue) && (target[key] = reducedValue);
        });

        stack[i] = undefined;

        return target;
      }
    }

    return source;
  };

  return visit(obj, 0);
};

const isAsyncFn = kindOfTest('AsyncFunction');

const isThenable = (thing) =>
  thing && (isObject$1(thing) || isFunction(thing)) && isFunction(thing.then) && isFunction(thing.catch);

const utils$1 = {
  isArray,
  isArrayBuffer,
  isBuffer,
  isFormData,
  isArrayBufferView,
  isString,
  isNumber,
  isBoolean,
  isObject: isObject$1,
  isPlainObject,
  isUndefined,
  isDate,
  isFile,
  isBlob,
  isRegExp,
  isFunction,
  isStream,
  isURLSearchParams,
  isTypedArray,
  isFileList,
  forEach,
  merge,
  extend,
  trim,
  stripBOM,
  inherits,
  toFlatObject,
  kindOf,
  kindOfTest,
  endsWith,
  toArray,
  forEachEntry,
  matchAll,
  isHTMLForm,
  hasOwnProperty,
  hasOwnProp: hasOwnProperty, // an alias to avoid ESLint no-prototype-builtins detection
  reduceDescriptors,
  freezeMethods,
  toObjectSet,
  toCamelCase,
  noop: noop$1,
  toFiniteNumber,
  findKey,
  global: _global,
  isContextDefined,
  ALPHABET,
  generateString,
  isSpecCompliantForm,
  toJSONObject,
  isAsyncFn,
  isThenable
};

/**
 * Create an Error with the specified message, config, error code, request and response.
 *
 * @param {string} message The error message.
 * @param {string} [code] The error code (for example, 'ECONNABORTED').
 * @param {Object} [config] The config.
 * @param {Object} [request] The request.
 * @param {Object} [response] The response.
 *
 * @returns {Error} The created error.
 */
function AxiosError(message, code, config, request, response) {
  Error.call(this);

  if (Error.captureStackTrace) {
    Error.captureStackTrace(this, this.constructor);
  } else {
    this.stack = (new Error()).stack;
  }

  this.message = message;
  this.name = 'AxiosError';
  code && (this.code = code);
  config && (this.config = config);
  request && (this.request = request);
  response && (this.response = response);
}

utils$1.inherits(AxiosError, Error, {
  toJSON: function toJSON() {
    return {
      // Standard
      message: this.message,
      name: this.name,
      // Microsoft
      description: this.description,
      number: this.number,
      // Mozilla
      fileName: this.fileName,
      lineNumber: this.lineNumber,
      columnNumber: this.columnNumber,
      stack: this.stack,
      // Axios
      config: utils$1.toJSONObject(this.config),
      code: this.code,
      status: this.response && this.response.status ? this.response.status : null
    };
  }
});

const prototype$1 = AxiosError.prototype;
const descriptors = {};

[
  'ERR_BAD_OPTION_VALUE',
  'ERR_BAD_OPTION',
  'ECONNABORTED',
  'ETIMEDOUT',
  'ERR_NETWORK',
  'ERR_FR_TOO_MANY_REDIRECTS',
  'ERR_DEPRECATED',
  'ERR_BAD_RESPONSE',
  'ERR_BAD_REQUEST',
  'ERR_CANCELED',
  'ERR_NOT_SUPPORT',
  'ERR_INVALID_URL'
// eslint-disable-next-line func-names
].forEach(code => {
  descriptors[code] = {value: code};
});

Object.defineProperties(AxiosError, descriptors);
Object.defineProperty(prototype$1, 'isAxiosError', {value: true});

// eslint-disable-next-line func-names
AxiosError.from = (error, code, config, request, response, customProps) => {
  const axiosError = Object.create(prototype$1);

  utils$1.toFlatObject(error, axiosError, function filter(obj) {
    return obj !== Error.prototype;
  }, prop => {
    return prop !== 'isAxiosError';
  });

  AxiosError.call(axiosError, error.message, code, config, request, response);

  axiosError.cause = error;

  axiosError.name = error.name;

  customProps && Object.assign(axiosError, customProps);

  return axiosError;
};

// eslint-disable-next-line strict
const httpAdapter = null;

/**
 * Determines if the given thing is a array or js object.
 *
 * @param {string} thing - The object or array to be visited.
 *
 * @returns {boolean}
 */
function isVisitable(thing) {
  return utils$1.isPlainObject(thing) || utils$1.isArray(thing);
}

/**
 * It removes the brackets from the end of a string
 *
 * @param {string} key - The key of the parameter.
 *
 * @returns {string} the key without the brackets.
 */
function removeBrackets(key) {
  return utils$1.endsWith(key, '[]') ? key.slice(0, -2) : key;
}

/**
 * It takes a path, a key, and a boolean, and returns a string
 *
 * @param {string} path - The path to the current key.
 * @param {string} key - The key of the current object being iterated over.
 * @param {string} dots - If true, the key will be rendered with dots instead of brackets.
 *
 * @returns {string} The path to the current key.
 */
function renderKey(path, key, dots) {
  if (!path) return key;
  return path.concat(key).map(function each(token, i) {
    // eslint-disable-next-line no-param-reassign
    token = removeBrackets(token);
    return !dots && i ? '[' + token + ']' : token;
  }).join(dots ? '.' : '');
}

/**
 * If the array is an array and none of its elements are visitable, then it's a flat array.
 *
 * @param {Array<any>} arr - The array to check
 *
 * @returns {boolean}
 */
function isFlatArray(arr) {
  return utils$1.isArray(arr) && !arr.some(isVisitable);
}

const predicates = utils$1.toFlatObject(utils$1, {}, null, function filter(prop) {
  return /^is[A-Z]/.test(prop);
});

/**
 * Convert a data object to FormData
 *
 * @param {Object} obj
 * @param {?Object} [formData]
 * @param {?Object} [options]
 * @param {Function} [options.visitor]
 * @param {Boolean} [options.metaTokens = true]
 * @param {Boolean} [options.dots = false]
 * @param {?Boolean} [options.indexes = false]
 *
 * @returns {Object}
 **/

/**
 * It converts an object into a FormData object
 *
 * @param {Object<any, any>} obj - The object to convert to form data.
 * @param {string} formData - The FormData object to append to.
 * @param {Object<string, any>} options
 *
 * @returns
 */
function toFormData(obj, formData, options) {
  if (!utils$1.isObject(obj)) {
    throw new TypeError('target must be an object');
  }

  // eslint-disable-next-line no-param-reassign
  formData = formData || new (FormData)();

  // eslint-disable-next-line no-param-reassign
  options = utils$1.toFlatObject(options, {
    metaTokens: true,
    dots: false,
    indexes: false
  }, false, function defined(option, source) {
    // eslint-disable-next-line no-eq-null,eqeqeq
    return !utils$1.isUndefined(source[option]);
  });

  const metaTokens = options.metaTokens;
  // eslint-disable-next-line no-use-before-define
  const visitor = options.visitor || defaultVisitor;
  const dots = options.dots;
  const indexes = options.indexes;
  const _Blob = options.Blob || typeof Blob !== 'undefined' && Blob;
  const useBlob = _Blob && utils$1.isSpecCompliantForm(formData);

  if (!utils$1.isFunction(visitor)) {
    throw new TypeError('visitor must be a function');
  }

  function convertValue(value) {
    if (value === null) return '';

    if (utils$1.isDate(value)) {
      return value.toISOString();
    }

    if (!useBlob && utils$1.isBlob(value)) {
      throw new AxiosError('Blob is not supported. Use a Buffer instead.');
    }

    if (utils$1.isArrayBuffer(value) || utils$1.isTypedArray(value)) {
      return useBlob && typeof Blob === 'function' ? new Blob([value]) : Buffer.from(value);
    }

    return value;
  }

  /**
   * Default visitor.
   *
   * @param {*} value
   * @param {String|Number} key
   * @param {Array<String|Number>} path
   * @this {FormData}
   *
   * @returns {boolean} return true to visit the each prop of the value recursively
   */
  function defaultVisitor(value, key, path) {
    let arr = value;

    if (value && !path && typeof value === 'object') {
      if (utils$1.endsWith(key, '{}')) {
        // eslint-disable-next-line no-param-reassign
        key = metaTokens ? key : key.slice(0, -2);
        // eslint-disable-next-line no-param-reassign
        value = JSON.stringify(value);
      } else if (
        (utils$1.isArray(value) && isFlatArray(value)) ||
        ((utils$1.isFileList(value) || utils$1.endsWith(key, '[]')) && (arr = utils$1.toArray(value))
        )) {
        // eslint-disable-next-line no-param-reassign
        key = removeBrackets(key);

        arr.forEach(function each(el, index) {
          !(utils$1.isUndefined(el) || el === null) && formData.append(
            // eslint-disable-next-line no-nested-ternary
            indexes === true ? renderKey([key], index, dots) : (indexes === null ? key : key + '[]'),
            convertValue(el)
          );
        });
        return false;
      }
    }

    if (isVisitable(value)) {
      return true;
    }

    formData.append(renderKey(path, key, dots), convertValue(value));

    return false;
  }

  const stack = [];

  const exposedHelpers = Object.assign(predicates, {
    defaultVisitor,
    convertValue,
    isVisitable
  });

  function build(value, path) {
    if (utils$1.isUndefined(value)) return;

    if (stack.indexOf(value) !== -1) {
      throw Error('Circular reference detected in ' + path.join('.'));
    }

    stack.push(value);

    utils$1.forEach(value, function each(el, key) {
      const result = !(utils$1.isUndefined(el) || el === null) && visitor.call(
        formData, el, utils$1.isString(key) ? key.trim() : key, path, exposedHelpers
      );

      if (result === true) {
        build(el, path ? path.concat(key) : [key]);
      }
    });

    stack.pop();
  }

  if (!utils$1.isObject(obj)) {
    throw new TypeError('data must be an object');
  }

  build(obj);

  return formData;
}

/**
 * It encodes a string by replacing all characters that are not in the unreserved set with
 * their percent-encoded equivalents
 *
 * @param {string} str - The string to encode.
 *
 * @returns {string} The encoded string.
 */
function encode$1(str) {
  const charMap = {
    '!': '%21',
    "'": '%27',
    '(': '%28',
    ')': '%29',
    '~': '%7E',
    '%20': '+',
    '%00': '\x00'
  };
  return encodeURIComponent(str).replace(/[!'()~]|%20|%00/g, function replacer(match) {
    return charMap[match];
  });
}

/**
 * It takes a params object and converts it to a FormData object
 *
 * @param {Object<string, any>} params - The parameters to be converted to a FormData object.
 * @param {Object<string, any>} options - The options object passed to the Axios constructor.
 *
 * @returns {void}
 */
function AxiosURLSearchParams(params, options) {
  this._pairs = [];

  params && toFormData(params, this, options);
}

const prototype = AxiosURLSearchParams.prototype;

prototype.append = function append(name, value) {
  this._pairs.push([name, value]);
};

prototype.toString = function toString(encoder) {
  const _encode = encoder ? function(value) {
    return encoder.call(this, value, encode$1);
  } : encode$1;

  return this._pairs.map(function each(pair) {
    return _encode(pair[0]) + '=' + _encode(pair[1]);
  }, '').join('&');
};

/**
 * It replaces all instances of the characters `:`, `$`, `,`, `+`, `[`, and `]` with their
 * URI encoded counterparts
 *
 * @param {string} val The value to be encoded.
 *
 * @returns {string} The encoded value.
 */
function encode(val) {
  return encodeURIComponent(val).
    replace(/%3A/gi, ':').
    replace(/%24/g, '$').
    replace(/%2C/gi, ',').
    replace(/%20/g, '+').
    replace(/%5B/gi, '[').
    replace(/%5D/gi, ']');
}

/**
 * Build a URL by appending params to the end
 *
 * @param {string} url The base of the url (e.g., http://www.google.com)
 * @param {object} [params] The params to be appended
 * @param {?object} options
 *
 * @returns {string} The formatted url
 */
function buildURL(url, params, options) {
  /*eslint no-param-reassign:0*/
  if (!params) {
    return url;
  }
  
  const _encode = options && options.encode || encode;

  const serializeFn = options && options.serialize;

  let serializedParams;

  if (serializeFn) {
    serializedParams = serializeFn(params, options);
  } else {
    serializedParams = utils$1.isURLSearchParams(params) ?
      params.toString() :
      new AxiosURLSearchParams(params, options).toString(_encode);
  }

  if (serializedParams) {
    const hashmarkIndex = url.indexOf("#");

    if (hashmarkIndex !== -1) {
      url = url.slice(0, hashmarkIndex);
    }
    url += (url.indexOf('?') === -1 ? '?' : '&') + serializedParams;
  }

  return url;
}

class InterceptorManager {
  constructor() {
    this.handlers = [];
  }

  /**
   * Add a new interceptor to the stack
   *
   * @param {Function} fulfilled The function to handle `then` for a `Promise`
   * @param {Function} rejected The function to handle `reject` for a `Promise`
   *
   * @return {Number} An ID used to remove interceptor later
   */
  use(fulfilled, rejected, options) {
    this.handlers.push({
      fulfilled,
      rejected,
      synchronous: options ? options.synchronous : false,
      runWhen: options ? options.runWhen : null
    });
    return this.handlers.length - 1;
  }

  /**
   * Remove an interceptor from the stack
   *
   * @param {Number} id The ID that was returned by `use`
   *
   * @returns {Boolean} `true` if the interceptor was removed, `false` otherwise
   */
  eject(id) {
    if (this.handlers[id]) {
      this.handlers[id] = null;
    }
  }

  /**
   * Clear all interceptors from the stack
   *
   * @returns {void}
   */
  clear() {
    if (this.handlers) {
      this.handlers = [];
    }
  }

  /**
   * Iterate over all the registered interceptors
   *
   * This method is particularly useful for skipping over any
   * interceptors that may have become `null` calling `eject`.
   *
   * @param {Function} fn The function to call for each interceptor
   *
   * @returns {void}
   */
  forEach(fn) {
    utils$1.forEach(this.handlers, function forEachHandler(h) {
      if (h !== null) {
        fn(h);
      }
    });
  }
}

const transitionalDefaults = {
  silentJSONParsing: true,
  forcedJSONParsing: true,
  clarifyTimeoutError: false
};

const URLSearchParams$1 = typeof URLSearchParams !== 'undefined' ? URLSearchParams : AxiosURLSearchParams;

const FormData$1 = typeof FormData !== 'undefined' ? FormData : null;

const Blob$1 = typeof Blob !== 'undefined' ? Blob : null;

const platform$1 = {
  isBrowser: true,
  classes: {
    URLSearchParams: URLSearchParams$1,
    FormData: FormData$1,
    Blob: Blob$1
  },
  protocols: ['http', 'https', 'file', 'blob', 'url', 'data']
};

const hasBrowserEnv = typeof window !== 'undefined' && typeof document !== 'undefined';

/**
 * Determine if we're running in a standard browser environment
 *
 * This allows axios to run in a web worker, and react-native.
 * Both environments support XMLHttpRequest, but not fully standard globals.
 *
 * web workers:
 *  typeof window -> undefined
 *  typeof document -> undefined
 *
 * react-native:
 *  navigator.product -> 'ReactNative'
 * nativescript
 *  navigator.product -> 'NativeScript' or 'NS'
 *
 * @returns {boolean}
 */
const hasStandardBrowserEnv = (
  (product) => {
    return hasBrowserEnv && ['ReactNative', 'NativeScript', 'NS'].indexOf(product) < 0
  })(typeof navigator !== 'undefined' && navigator.product);

/**
 * Determine if we're running in a standard browser webWorker environment
 *
 * Although the `isStandardBrowserEnv` method indicates that
 * `allows axios to run in a web worker`, the WebWorker will still be
 * filtered out due to its judgment standard
 * `typeof window !== 'undefined' && typeof document !== 'undefined'`.
 * This leads to a problem when axios post `FormData` in webWorker
 */
const hasStandardBrowserWebWorkerEnv = (() => {
  return (
    typeof WorkerGlobalScope !== 'undefined' &&
    // eslint-disable-next-line no-undef
    self instanceof WorkerGlobalScope &&
    typeof self.importScripts === 'function'
  );
})();

const utils = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
    __proto__: null,
    hasBrowserEnv,
    hasStandardBrowserEnv,
    hasStandardBrowserWebWorkerEnv
}, Symbol.toStringTag, { value: 'Module' }));

const platform = {
  ...utils,
  ...platform$1
};

function toURLEncodedForm(data, options) {
  return toFormData(data, new platform.classes.URLSearchParams(), Object.assign({
    visitor: function(value, key, path, helpers) {
      if (platform.isNode && utils$1.isBuffer(value)) {
        this.append(key, value.toString('base64'));
        return false;
      }

      return helpers.defaultVisitor.apply(this, arguments);
    }
  }, options));
}

/**
 * It takes a string like `foo[x][y][z]` and returns an array like `['foo', 'x', 'y', 'z']
 *
 * @param {string} name - The name of the property to get.
 *
 * @returns An array of strings.
 */
function parsePropPath(name) {
  // foo[x][y][z]
  // foo.x.y.z
  // foo-x-y-z
  // foo x y z
  return utils$1.matchAll(/\w+|\[(\w*)]/g, name).map(match => {
    return match[0] === '[]' ? '' : match[1] || match[0];
  });
}

/**
 * Convert an array to an object.
 *
 * @param {Array<any>} arr - The array to convert to an object.
 *
 * @returns An object with the same keys and values as the array.
 */
function arrayToObject(arr) {
  const obj = {};
  const keys = Object.keys(arr);
  let i;
  const len = keys.length;
  let key;
  for (i = 0; i < len; i++) {
    key = keys[i];
    obj[key] = arr[key];
  }
  return obj;
}

/**
 * It takes a FormData object and returns a JavaScript object
 *
 * @param {string} formData The FormData object to convert to JSON.
 *
 * @returns {Object<string, any> | null} The converted object.
 */
function formDataToJSON(formData) {
  function buildPath(path, value, target, index) {
    let name = path[index++];

    if (name === '__proto__') return true;

    const isNumericKey = Number.isFinite(+name);
    const isLast = index >= path.length;
    name = !name && utils$1.isArray(target) ? target.length : name;

    if (isLast) {
      if (utils$1.hasOwnProp(target, name)) {
        target[name] = [target[name], value];
      } else {
        target[name] = value;
      }

      return !isNumericKey;
    }

    if (!target[name] || !utils$1.isObject(target[name])) {
      target[name] = [];
    }

    const result = buildPath(path, value, target[name], index);

    if (result && utils$1.isArray(target[name])) {
      target[name] = arrayToObject(target[name]);
    }

    return !isNumericKey;
  }

  if (utils$1.isFormData(formData) && utils$1.isFunction(formData.entries)) {
    const obj = {};

    utils$1.forEachEntry(formData, (name, value) => {
      buildPath(parsePropPath(name), value, obj, 0);
    });

    return obj;
  }

  return null;
}

/**
 * It takes a string, tries to parse it, and if it fails, it returns the stringified version
 * of the input
 *
 * @param {any} rawValue - The value to be stringified.
 * @param {Function} parser - A function that parses a string into a JavaScript object.
 * @param {Function} encoder - A function that takes a value and returns a string.
 *
 * @returns {string} A stringified version of the rawValue.
 */
function stringifySafely(rawValue, parser, encoder) {
  if (utils$1.isString(rawValue)) {
    try {
      (parser || JSON.parse)(rawValue);
      return utils$1.trim(rawValue);
    } catch (e) {
      if (e.name !== 'SyntaxError') {
        throw e;
      }
    }
  }

  return (encoder || JSON.stringify)(rawValue);
}

const defaults = {

  transitional: transitionalDefaults,

  adapter: ['xhr', 'http'],

  transformRequest: [function transformRequest(data, headers) {
    const contentType = headers.getContentType() || '';
    const hasJSONContentType = contentType.indexOf('application/json') > -1;
    const isObjectPayload = utils$1.isObject(data);

    if (isObjectPayload && utils$1.isHTMLForm(data)) {
      data = new FormData(data);
    }

    const isFormData = utils$1.isFormData(data);

    if (isFormData) {
      return hasJSONContentType ? JSON.stringify(formDataToJSON(data)) : data;
    }

    if (utils$1.isArrayBuffer(data) ||
      utils$1.isBuffer(data) ||
      utils$1.isStream(data) ||
      utils$1.isFile(data) ||
      utils$1.isBlob(data)
    ) {
      return data;
    }
    if (utils$1.isArrayBufferView(data)) {
      return data.buffer;
    }
    if (utils$1.isURLSearchParams(data)) {
      headers.setContentType('application/x-www-form-urlencoded;charset=utf-8', false);
      return data.toString();
    }

    let isFileList;

    if (isObjectPayload) {
      if (contentType.indexOf('application/x-www-form-urlencoded') > -1) {
        return toURLEncodedForm(data, this.formSerializer).toString();
      }

      if ((isFileList = utils$1.isFileList(data)) || contentType.indexOf('multipart/form-data') > -1) {
        const _FormData = this.env && this.env.FormData;

        return toFormData(
          isFileList ? {'files[]': data} : data,
          _FormData && new _FormData(),
          this.formSerializer
        );
      }
    }

    if (isObjectPayload || hasJSONContentType ) {
      headers.setContentType('application/json', false);
      return stringifySafely(data);
    }

    return data;
  }],

  transformResponse: [function transformResponse(data) {
    const transitional = this.transitional || defaults.transitional;
    const forcedJSONParsing = transitional && transitional.forcedJSONParsing;
    const JSONRequested = this.responseType === 'json';

    if (data && utils$1.isString(data) && ((forcedJSONParsing && !this.responseType) || JSONRequested)) {
      const silentJSONParsing = transitional && transitional.silentJSONParsing;
      const strictJSONParsing = !silentJSONParsing && JSONRequested;

      try {
        return JSON.parse(data);
      } catch (e) {
        if (strictJSONParsing) {
          if (e.name === 'SyntaxError') {
            throw AxiosError.from(e, AxiosError.ERR_BAD_RESPONSE, this, null, this.response);
          }
          throw e;
        }
      }
    }

    return data;
  }],

  /**
   * A timeout in milliseconds to abort a request. If set to 0 (default) a
   * timeout is not created.
   */
  timeout: 0,

  xsrfCookieName: 'XSRF-TOKEN',
  xsrfHeaderName: 'X-XSRF-TOKEN',

  maxContentLength: -1,
  maxBodyLength: -1,

  env: {
    FormData: platform.classes.FormData,
    Blob: platform.classes.Blob
  },

  validateStatus: function validateStatus(status) {
    return status >= 200 && status < 300;
  },

  headers: {
    common: {
      'Accept': 'application/json, text/plain, */*',
      'Content-Type': undefined
    }
  }
};

utils$1.forEach(['delete', 'get', 'head', 'post', 'put', 'patch'], (method) => {
  defaults.headers[method] = {};
});

const defaults$1 = defaults;

// RawAxiosHeaders whose duplicates are ignored by node
// c.f. https://nodejs.org/api/http.html#http_message_headers
const ignoreDuplicateOf = utils$1.toObjectSet([
  'age', 'authorization', 'content-length', 'content-type', 'etag',
  'expires', 'from', 'host', 'if-modified-since', 'if-unmodified-since',
  'last-modified', 'location', 'max-forwards', 'proxy-authorization',
  'referer', 'retry-after', 'user-agent'
]);

/**
 * Parse headers into an object
 *
 * ```
 * Date: Wed, 27 Aug 2014 08:58:49 GMT
 * Content-Type: application/json
 * Connection: keep-alive
 * Transfer-Encoding: chunked
 * ```
 *
 * @param {String} rawHeaders Headers needing to be parsed
 *
 * @returns {Object} Headers parsed into an object
 */
const parseHeaders = rawHeaders => {
  const parsed = {};
  let key;
  let val;
  let i;

  rawHeaders && rawHeaders.split('\n').forEach(function parser(line) {
    i = line.indexOf(':');
    key = line.substring(0, i).trim().toLowerCase();
    val = line.substring(i + 1).trim();

    if (!key || (parsed[key] && ignoreDuplicateOf[key])) {
      return;
    }

    if (key === 'set-cookie') {
      if (parsed[key]) {
        parsed[key].push(val);
      } else {
        parsed[key] = [val];
      }
    } else {
      parsed[key] = parsed[key] ? parsed[key] + ', ' + val : val;
    }
  });

  return parsed;
};

const $internals = Symbol('internals');

function normalizeHeader(header) {
  return header && String(header).trim().toLowerCase();
}

function normalizeValue(value) {
  if (value === false || value == null) {
    return value;
  }

  return utils$1.isArray(value) ? value.map(normalizeValue) : String(value);
}

function parseTokens(str) {
  const tokens = Object.create(null);
  const tokensRE = /([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;
  let match;

  while ((match = tokensRE.exec(str))) {
    tokens[match[1]] = match[2];
  }

  return tokens;
}

const isValidHeaderName = (str) => /^[-_a-zA-Z0-9^`|~,!#$%&'*+.]+$/.test(str.trim());

function matchHeaderValue(context, value, header, filter, isHeaderNameFilter) {
  if (utils$1.isFunction(filter)) {
    return filter.call(this, value, header);
  }

  if (isHeaderNameFilter) {
    value = header;
  }

  if (!utils$1.isString(value)) return;

  if (utils$1.isString(filter)) {
    return value.indexOf(filter) !== -1;
  }

  if (utils$1.isRegExp(filter)) {
    return filter.test(value);
  }
}

function formatHeader(header) {
  return header.trim()
    .toLowerCase().replace(/([a-z\d])(\w*)/g, (w, char, str) => {
      return char.toUpperCase() + str;
    });
}

function buildAccessors(obj, header) {
  const accessorName = utils$1.toCamelCase(' ' + header);

  ['get', 'set', 'has'].forEach(methodName => {
    Object.defineProperty(obj, methodName + accessorName, {
      value: function(arg1, arg2, arg3) {
        return this[methodName].call(this, header, arg1, arg2, arg3);
      },
      configurable: true
    });
  });
}

class AxiosHeaders {
  constructor(headers) {
    headers && this.set(headers);
  }

  set(header, valueOrRewrite, rewrite) {
    const self = this;

    function setHeader(_value, _header, _rewrite) {
      const lHeader = normalizeHeader(_header);

      if (!lHeader) {
        throw new Error('header name must be a non-empty string');
      }

      const key = utils$1.findKey(self, lHeader);

      if(!key || self[key] === undefined || _rewrite === true || (_rewrite === undefined && self[key] !== false)) {
        self[key || _header] = normalizeValue(_value);
      }
    }

    const setHeaders = (headers, _rewrite) =>
      utils$1.forEach(headers, (_value, _header) => setHeader(_value, _header, _rewrite));

    if (utils$1.isPlainObject(header) || header instanceof this.constructor) {
      setHeaders(header, valueOrRewrite);
    } else if(utils$1.isString(header) && (header = header.trim()) && !isValidHeaderName(header)) {
      setHeaders(parseHeaders(header), valueOrRewrite);
    } else {
      header != null && setHeader(valueOrRewrite, header, rewrite);
    }

    return this;
  }

  get(header, parser) {
    header = normalizeHeader(header);

    if (header) {
      const key = utils$1.findKey(this, header);

      if (key) {
        const value = this[key];

        if (!parser) {
          return value;
        }

        if (parser === true) {
          return parseTokens(value);
        }

        if (utils$1.isFunction(parser)) {
          return parser.call(this, value, key);
        }

        if (utils$1.isRegExp(parser)) {
          return parser.exec(value);
        }

        throw new TypeError('parser must be boolean|regexp|function');
      }
    }
  }

  has(header, matcher) {
    header = normalizeHeader(header);

    if (header) {
      const key = utils$1.findKey(this, header);

      return !!(key && this[key] !== undefined && (!matcher || matchHeaderValue(this, this[key], key, matcher)));
    }

    return false;
  }

  delete(header, matcher) {
    const self = this;
    let deleted = false;

    function deleteHeader(_header) {
      _header = normalizeHeader(_header);

      if (_header) {
        const key = utils$1.findKey(self, _header);

        if (key && (!matcher || matchHeaderValue(self, self[key], key, matcher))) {
          delete self[key];

          deleted = true;
        }
      }
    }

    if (utils$1.isArray(header)) {
      header.forEach(deleteHeader);
    } else {
      deleteHeader(header);
    }

    return deleted;
  }

  clear(matcher) {
    const keys = Object.keys(this);
    let i = keys.length;
    let deleted = false;

    while (i--) {
      const key = keys[i];
      if(!matcher || matchHeaderValue(this, this[key], key, matcher, true)) {
        delete this[key];
        deleted = true;
      }
    }

    return deleted;
  }

  normalize(format) {
    const self = this;
    const headers = {};

    utils$1.forEach(this, (value, header) => {
      const key = utils$1.findKey(headers, header);

      if (key) {
        self[key] = normalizeValue(value);
        delete self[header];
        return;
      }

      const normalized = format ? formatHeader(header) : String(header).trim();

      if (normalized !== header) {
        delete self[header];
      }

      self[normalized] = normalizeValue(value);

      headers[normalized] = true;
    });

    return this;
  }

  concat(...targets) {
    return this.constructor.concat(this, ...targets);
  }

  toJSON(asStrings) {
    const obj = Object.create(null);

    utils$1.forEach(this, (value, header) => {
      value != null && value !== false && (obj[header] = asStrings && utils$1.isArray(value) ? value.join(', ') : value);
    });

    return obj;
  }

  [Symbol.iterator]() {
    return Object.entries(this.toJSON())[Symbol.iterator]();
  }

  toString() {
    return Object.entries(this.toJSON()).map(([header, value]) => header + ': ' + value).join('\n');
  }

  get [Symbol.toStringTag]() {
    return 'AxiosHeaders';
  }

  static from(thing) {
    return thing instanceof this ? thing : new this(thing);
  }

  static concat(first, ...targets) {
    const computed = new this(first);

    targets.forEach((target) => computed.set(target));

    return computed;
  }

  static accessor(header) {
    const internals = this[$internals] = (this[$internals] = {
      accessors: {}
    });

    const accessors = internals.accessors;
    const prototype = this.prototype;

    function defineAccessor(_header) {
      const lHeader = normalizeHeader(_header);

      if (!accessors[lHeader]) {
        buildAccessors(prototype, _header);
        accessors[lHeader] = true;
      }
    }

    utils$1.isArray(header) ? header.forEach(defineAccessor) : defineAccessor(header);

    return this;
  }
}

AxiosHeaders.accessor(['Content-Type', 'Content-Length', 'Accept', 'Accept-Encoding', 'User-Agent', 'Authorization']);

// reserved names hotfix
utils$1.reduceDescriptors(AxiosHeaders.prototype, ({value}, key) => {
  let mapped = key[0].toUpperCase() + key.slice(1); // map `set` => `Set`
  return {
    get: () => value,
    set(headerValue) {
      this[mapped] = headerValue;
    }
  }
});

utils$1.freezeMethods(AxiosHeaders);

const AxiosHeaders$1 = AxiosHeaders;

/**
 * Transform the data for a request or a response
 *
 * @param {Array|Function} fns A single function or Array of functions
 * @param {?Object} response The response object
 *
 * @returns {*} The resulting transformed data
 */
function transformData(fns, response) {
  const config = this || defaults$1;
  const context = response || config;
  const headers = AxiosHeaders$1.from(context.headers);
  let data = context.data;

  utils$1.forEach(fns, function transform(fn) {
    data = fn.call(config, data, headers.normalize(), response ? response.status : undefined);
  });

  headers.normalize();

  return data;
}

function isCancel(value) {
  return !!(value && value.__CANCEL__);
}

/**
 * A `CanceledError` is an object that is thrown when an operation is canceled.
 *
 * @param {string=} message The message.
 * @param {Object=} config The config.
 * @param {Object=} request The request.
 *
 * @returns {CanceledError} The created error.
 */
function CanceledError(message, config, request) {
  // eslint-disable-next-line no-eq-null,eqeqeq
  AxiosError.call(this, message == null ? 'canceled' : message, AxiosError.ERR_CANCELED, config, request);
  this.name = 'CanceledError';
}

utils$1.inherits(CanceledError, AxiosError, {
  __CANCEL__: true
});

/**
 * Resolve or reject a Promise based on response status.
 *
 * @param {Function} resolve A function that resolves the promise.
 * @param {Function} reject A function that rejects the promise.
 * @param {object} response The response.
 *
 * @returns {object} The response.
 */
function settle(resolve, reject, response) {
  const validateStatus = response.config.validateStatus;
  if (!response.status || !validateStatus || validateStatus(response.status)) {
    resolve(response);
  } else {
    reject(new AxiosError(
      'Request failed with status code ' + response.status,
      [AxiosError.ERR_BAD_REQUEST, AxiosError.ERR_BAD_RESPONSE][Math.floor(response.status / 100) - 4],
      response.config,
      response.request,
      response
    ));
  }
}

const cookies = platform.hasStandardBrowserEnv ?

  // Standard browser envs support document.cookie
  {
    write(name, value, expires, path, domain, secure) {
      const cookie = [name + '=' + encodeURIComponent(value)];

      utils$1.isNumber(expires) && cookie.push('expires=' + new Date(expires).toGMTString());

      utils$1.isString(path) && cookie.push('path=' + path);

      utils$1.isString(domain) && cookie.push('domain=' + domain);

      secure === true && cookie.push('secure');

      document.cookie = cookie.join('; ');
    },

    read(name) {
      const match = document.cookie.match(new RegExp('(^|;\\s*)(' + name + ')=([^;]*)'));
      return (match ? decodeURIComponent(match[3]) : null);
    },

    remove(name) {
      this.write(name, '', Date.now() - 86400000);
    }
  }

  :

  // Non-standard browser env (web workers, react-native) lack needed support.
  {
    write() {},
    read() {
      return null;
    },
    remove() {}
  };

/**
 * Determines whether the specified URL is absolute
 *
 * @param {string} url The URL to test
 *
 * @returns {boolean} True if the specified URL is absolute, otherwise false
 */
function isAbsoluteURL(url) {
  // A URL is considered absolute if it begins with "<scheme>://" or "//" (protocol-relative URL).
  // RFC 3986 defines scheme name as a sequence of characters beginning with a letter and followed
  // by any combination of letters, digits, plus, period, or hyphen.
  return /^([a-z][a-z\d+\-.]*:)?\/\//i.test(url);
}

/**
 * Creates a new URL by combining the specified URLs
 *
 * @param {string} baseURL The base URL
 * @param {string} relativeURL The relative URL
 *
 * @returns {string} The combined URL
 */
function combineURLs(baseURL, relativeURL) {
  return relativeURL
    ? baseURL.replace(/\/?\/$/, '') + '/' + relativeURL.replace(/^\/+/, '')
    : baseURL;
}

/**
 * Creates a new URL by combining the baseURL with the requestedURL,
 * only when the requestedURL is not already an absolute URL.
 * If the requestURL is absolute, this function returns the requestedURL untouched.
 *
 * @param {string} baseURL The base URL
 * @param {string} requestedURL Absolute or relative URL to combine
 *
 * @returns {string} The combined full path
 */
function buildFullPath(baseURL, requestedURL) {
  if (baseURL && !isAbsoluteURL(requestedURL)) {
    return combineURLs(baseURL, requestedURL);
  }
  return requestedURL;
}

const isURLSameOrigin = platform.hasStandardBrowserEnv ?

// Standard browser envs have full support of the APIs needed to test
// whether the request URL is of the same origin as current location.
  (function standardBrowserEnv() {
    const msie = /(msie|trident)/i.test(navigator.userAgent);
    const urlParsingNode = document.createElement('a');
    let originURL;

    /**
    * Parse a URL to discover its components
    *
    * @param {String} url The URL to be parsed
    * @returns {Object}
    */
    function resolveURL(url) {
      let href = url;

      if (msie) {
        // IE needs attribute set twice to normalize properties
        urlParsingNode.setAttribute('href', href);
        href = urlParsingNode.href;
      }

      urlParsingNode.setAttribute('href', href);

      // urlParsingNode provides the UrlUtils interface - http://url.spec.whatwg.org/#urlutils
      return {
        href: urlParsingNode.href,
        protocol: urlParsingNode.protocol ? urlParsingNode.protocol.replace(/:$/, '') : '',
        host: urlParsingNode.host,
        search: urlParsingNode.search ? urlParsingNode.search.replace(/^\?/, '') : '',
        hash: urlParsingNode.hash ? urlParsingNode.hash.replace(/^#/, '') : '',
        hostname: urlParsingNode.hostname,
        port: urlParsingNode.port,
        pathname: (urlParsingNode.pathname.charAt(0) === '/') ?
          urlParsingNode.pathname :
          '/' + urlParsingNode.pathname
      };
    }

    originURL = resolveURL(window.location.href);

    /**
    * Determine if a URL shares the same origin as the current location
    *
    * @param {String} requestURL The URL to test
    * @returns {boolean} True if URL shares the same origin, otherwise false
    */
    return function isURLSameOrigin(requestURL) {
      const parsed = (utils$1.isString(requestURL)) ? resolveURL(requestURL) : requestURL;
      return (parsed.protocol === originURL.protocol &&
          parsed.host === originURL.host);
    };
  })() :

  // Non standard browser envs (web workers, react-native) lack needed support.
  (function nonStandardBrowserEnv() {
    return function isURLSameOrigin() {
      return true;
    };
  })();

function parseProtocol(url) {
  const match = /^([-+\w]{1,25})(:?\/\/|:)/.exec(url);
  return match && match[1] || '';
}

/**
 * Calculate data maxRate
 * @param {Number} [samplesCount= 10]
 * @param {Number} [min= 1000]
 * @returns {Function}
 */
function speedometer(samplesCount, min) {
  samplesCount = samplesCount || 10;
  const bytes = new Array(samplesCount);
  const timestamps = new Array(samplesCount);
  let head = 0;
  let tail = 0;
  let firstSampleTS;

  min = min !== undefined ? min : 1000;

  return function push(chunkLength) {
    const now = Date.now();

    const startedAt = timestamps[tail];

    if (!firstSampleTS) {
      firstSampleTS = now;
    }

    bytes[head] = chunkLength;
    timestamps[head] = now;

    let i = tail;
    let bytesCount = 0;

    while (i !== head) {
      bytesCount += bytes[i++];
      i = i % samplesCount;
    }

    head = (head + 1) % samplesCount;

    if (head === tail) {
      tail = (tail + 1) % samplesCount;
    }

    if (now - firstSampleTS < min) {
      return;
    }

    const passed = startedAt && now - startedAt;

    return passed ? Math.round(bytesCount * 1000 / passed) : undefined;
  };
}

function progressEventReducer(listener, isDownloadStream) {
  let bytesNotified = 0;
  const _speedometer = speedometer(50, 250);

  return e => {
    const loaded = e.loaded;
    const total = e.lengthComputable ? e.total : undefined;
    const progressBytes = loaded - bytesNotified;
    const rate = _speedometer(progressBytes);
    const inRange = loaded <= total;

    bytesNotified = loaded;

    const data = {
      loaded,
      total,
      progress: total ? (loaded / total) : undefined,
      bytes: progressBytes,
      rate: rate ? rate : undefined,
      estimated: rate && total && inRange ? (total - loaded) / rate : undefined,
      event: e
    };

    data[isDownloadStream ? 'download' : 'upload'] = true;

    listener(data);
  };
}

const isXHRAdapterSupported = typeof XMLHttpRequest !== 'undefined';

const xhrAdapter = isXHRAdapterSupported && function (config) {
  return new Promise(function dispatchXhrRequest(resolve, reject) {
    let requestData = config.data;
    const requestHeaders = AxiosHeaders$1.from(config.headers).normalize();
    let {responseType, withXSRFToken} = config;
    let onCanceled;
    function done() {
      if (config.cancelToken) {
        config.cancelToken.unsubscribe(onCanceled);
      }

      if (config.signal) {
        config.signal.removeEventListener('abort', onCanceled);
      }
    }

    let contentType;

    if (utils$1.isFormData(requestData)) {
      if (platform.hasStandardBrowserEnv || platform.hasStandardBrowserWebWorkerEnv) {
        requestHeaders.setContentType(false); // Let the browser set it
      } else if ((contentType = requestHeaders.getContentType()) !== false) {
        // fix semicolon duplication issue for ReactNative FormData implementation
        const [type, ...tokens] = contentType ? contentType.split(';').map(token => token.trim()).filter(Boolean) : [];
        requestHeaders.setContentType([type || 'multipart/form-data', ...tokens].join('; '));
      }
    }

    let request = new XMLHttpRequest();

    // HTTP basic authentication
    if (config.auth) {
      const username = config.auth.username || '';
      const password = config.auth.password ? unescape(encodeURIComponent(config.auth.password)) : '';
      requestHeaders.set('Authorization', 'Basic ' + btoa(username + ':' + password));
    }

    const fullPath = buildFullPath(config.baseURL, config.url);

    request.open(config.method.toUpperCase(), buildURL(fullPath, config.params, config.paramsSerializer), true);

    // Set the request timeout in MS
    request.timeout = config.timeout;

    function onloadend() {
      if (!request) {
        return;
      }
      // Prepare the response
      const responseHeaders = AxiosHeaders$1.from(
        'getAllResponseHeaders' in request && request.getAllResponseHeaders()
      );
      const responseData = !responseType || responseType === 'text' || responseType === 'json' ?
        request.responseText : request.response;
      const response = {
        data: responseData,
        status: request.status,
        statusText: request.statusText,
        headers: responseHeaders,
        config,
        request
      };

      settle(function _resolve(value) {
        resolve(value);
        done();
      }, function _reject(err) {
        reject(err);
        done();
      }, response);

      // Clean up request
      request = null;
    }

    if ('onloadend' in request) {
      // Use onloadend if available
      request.onloadend = onloadend;
    } else {
      // Listen for ready state to emulate onloadend
      request.onreadystatechange = function handleLoad() {
        if (!request || request.readyState !== 4) {
          return;
        }

        // The request errored out and we didn't get a response, this will be
        // handled by onerror instead
        // With one exception: request that using file: protocol, most browsers
        // will return status as 0 even though it's a successful request
        if (request.status === 0 && !(request.responseURL && request.responseURL.indexOf('file:') === 0)) {
          return;
        }
        // readystate handler is calling before onerror or ontimeout handlers,
        // so we should call onloadend on the next 'tick'
        setTimeout(onloadend);
      };
    }

    // Handle browser request cancellation (as opposed to a manual cancellation)
    request.onabort = function handleAbort() {
      if (!request) {
        return;
      }

      reject(new AxiosError('Request aborted', AxiosError.ECONNABORTED, config, request));

      // Clean up request
      request = null;
    };

    // Handle low level network errors
    request.onerror = function handleError() {
      // Real errors are hidden from us by the browser
      // onerror should only fire if it's a network error
      reject(new AxiosError('Network Error', AxiosError.ERR_NETWORK, config, request));

      // Clean up request
      request = null;
    };

    // Handle timeout
    request.ontimeout = function handleTimeout() {
      let timeoutErrorMessage = config.timeout ? 'timeout of ' + config.timeout + 'ms exceeded' : 'timeout exceeded';
      const transitional = config.transitional || transitionalDefaults;
      if (config.timeoutErrorMessage) {
        timeoutErrorMessage = config.timeoutErrorMessage;
      }
      reject(new AxiosError(
        timeoutErrorMessage,
        transitional.clarifyTimeoutError ? AxiosError.ETIMEDOUT : AxiosError.ECONNABORTED,
        config,
        request));

      // Clean up request
      request = null;
    };

    // Add xsrf header
    // This is only done if running in a standard browser environment.
    // Specifically not if we're in a web worker, or react-native.
    if(platform.hasStandardBrowserEnv) {
      withXSRFToken && utils$1.isFunction(withXSRFToken) && (withXSRFToken = withXSRFToken(config));

      if (withXSRFToken || (withXSRFToken !== false && isURLSameOrigin(fullPath))) {
        // Add xsrf header
        const xsrfValue = config.xsrfHeaderName && config.xsrfCookieName && cookies.read(config.xsrfCookieName);

        if (xsrfValue) {
          requestHeaders.set(config.xsrfHeaderName, xsrfValue);
        }
      }
    }

    // Remove Content-Type if data is undefined
    requestData === undefined && requestHeaders.setContentType(null);

    // Add headers to the request
    if ('setRequestHeader' in request) {
      utils$1.forEach(requestHeaders.toJSON(), function setRequestHeader(val, key) {
        request.setRequestHeader(key, val);
      });
    }

    // Add withCredentials to request if needed
    if (!utils$1.isUndefined(config.withCredentials)) {
      request.withCredentials = !!config.withCredentials;
    }

    // Add responseType to request if needed
    if (responseType && responseType !== 'json') {
      request.responseType = config.responseType;
    }

    // Handle progress if needed
    if (typeof config.onDownloadProgress === 'function') {
      request.addEventListener('progress', progressEventReducer(config.onDownloadProgress, true));
    }

    // Not all browsers support upload events
    if (typeof config.onUploadProgress === 'function' && request.upload) {
      request.upload.addEventListener('progress', progressEventReducer(config.onUploadProgress));
    }

    if (config.cancelToken || config.signal) {
      // Handle cancellation
      // eslint-disable-next-line func-names
      onCanceled = cancel => {
        if (!request) {
          return;
        }
        reject(!cancel || cancel.type ? new CanceledError(null, config, request) : cancel);
        request.abort();
        request = null;
      };

      config.cancelToken && config.cancelToken.subscribe(onCanceled);
      if (config.signal) {
        config.signal.aborted ? onCanceled() : config.signal.addEventListener('abort', onCanceled);
      }
    }

    const protocol = parseProtocol(fullPath);

    if (protocol && platform.protocols.indexOf(protocol) === -1) {
      reject(new AxiosError('Unsupported protocol ' + protocol + ':', AxiosError.ERR_BAD_REQUEST, config));
      return;
    }


    // Send the request
    request.send(requestData || null);
  });
};

const knownAdapters = {
  http: httpAdapter,
  xhr: xhrAdapter
};

utils$1.forEach(knownAdapters, (fn, value) => {
  if (fn) {
    try {
      Object.defineProperty(fn, 'name', {value});
    } catch (e) {
      // eslint-disable-next-line no-empty
    }
    Object.defineProperty(fn, 'adapterName', {value});
  }
});

const renderReason = (reason) => `- ${reason}`;

const isResolvedHandle = (adapter) => utils$1.isFunction(adapter) || adapter === null || adapter === false;

const adapters = {
  getAdapter: (adapters) => {
    adapters = utils$1.isArray(adapters) ? adapters : [adapters];

    const {length} = adapters;
    let nameOrAdapter;
    let adapter;

    const rejectedReasons = {};

    for (let i = 0; i < length; i++) {
      nameOrAdapter = adapters[i];
      let id;

      adapter = nameOrAdapter;

      if (!isResolvedHandle(nameOrAdapter)) {
        adapter = knownAdapters[(id = String(nameOrAdapter)).toLowerCase()];

        if (adapter === undefined) {
          throw new AxiosError(`Unknown adapter '${id}'`);
        }
      }

      if (adapter) {
        break;
      }

      rejectedReasons[id || '#' + i] = adapter;
    }

    if (!adapter) {

      const reasons = Object.entries(rejectedReasons)
        .map(([id, state]) => `adapter ${id} ` +
          (state === false ? 'is not supported by the environment' : 'is not available in the build')
        );

      let s = length ?
        (reasons.length > 1 ? 'since :\n' + reasons.map(renderReason).join('\n') : ' ' + renderReason(reasons[0])) :
        'as no adapter specified';

      throw new AxiosError(
        `There is no suitable adapter to dispatch the request ` + s,
        'ERR_NOT_SUPPORT'
      );
    }

    return adapter;
  },
  adapters: knownAdapters
};

/**
 * Throws a `CanceledError` if cancellation has been requested.
 *
 * @param {Object} config The config that is to be used for the request
 *
 * @returns {void}
 */
function throwIfCancellationRequested(config) {
  if (config.cancelToken) {
    config.cancelToken.throwIfRequested();
  }

  if (config.signal && config.signal.aborted) {
    throw new CanceledError(null, config);
  }
}

/**
 * Dispatch a request to the server using the configured adapter.
 *
 * @param {object} config The config that is to be used for the request
 *
 * @returns {Promise} The Promise to be fulfilled
 */
function dispatchRequest(config) {
  throwIfCancellationRequested(config);

  config.headers = AxiosHeaders$1.from(config.headers);

  // Transform request data
  config.data = transformData.call(
    config,
    config.transformRequest
  );

  if (['post', 'put', 'patch'].indexOf(config.method) !== -1) {
    config.headers.setContentType('application/x-www-form-urlencoded', false);
  }

  const adapter = adapters.getAdapter(config.adapter || defaults$1.adapter);

  return adapter(config).then(function onAdapterResolution(response) {
    throwIfCancellationRequested(config);

    // Transform response data
    response.data = transformData.call(
      config,
      config.transformResponse,
      response
    );

    response.headers = AxiosHeaders$1.from(response.headers);

    return response;
  }, function onAdapterRejection(reason) {
    if (!isCancel(reason)) {
      throwIfCancellationRequested(config);

      // Transform response data
      if (reason && reason.response) {
        reason.response.data = transformData.call(
          config,
          config.transformResponse,
          reason.response
        );
        reason.response.headers = AxiosHeaders$1.from(reason.response.headers);
      }
    }

    return Promise.reject(reason);
  });
}

const headersToObject = (thing) => thing instanceof AxiosHeaders$1 ? { ...thing } : thing;

/**
 * Config-specific merge-function which creates a new config-object
 * by merging two configuration objects together.
 *
 * @param {Object} config1
 * @param {Object} config2
 *
 * @returns {Object} New object resulting from merging config2 to config1
 */
function mergeConfig(config1, config2) {
  // eslint-disable-next-line no-param-reassign
  config2 = config2 || {};
  const config = {};

  function getMergedValue(target, source, caseless) {
    if (utils$1.isPlainObject(target) && utils$1.isPlainObject(source)) {
      return utils$1.merge.call({caseless}, target, source);
    } else if (utils$1.isPlainObject(source)) {
      return utils$1.merge({}, source);
    } else if (utils$1.isArray(source)) {
      return source.slice();
    }
    return source;
  }

  // eslint-disable-next-line consistent-return
  function mergeDeepProperties(a, b, caseless) {
    if (!utils$1.isUndefined(b)) {
      return getMergedValue(a, b, caseless);
    } else if (!utils$1.isUndefined(a)) {
      return getMergedValue(undefined, a, caseless);
    }
  }

  // eslint-disable-next-line consistent-return
  function valueFromConfig2(a, b) {
    if (!utils$1.isUndefined(b)) {
      return getMergedValue(undefined, b);
    }
  }

  // eslint-disable-next-line consistent-return
  function defaultToConfig2(a, b) {
    if (!utils$1.isUndefined(b)) {
      return getMergedValue(undefined, b);
    } else if (!utils$1.isUndefined(a)) {
      return getMergedValue(undefined, a);
    }
  }

  // eslint-disable-next-line consistent-return
  function mergeDirectKeys(a, b, prop) {
    if (prop in config2) {
      return getMergedValue(a, b);
    } else if (prop in config1) {
      return getMergedValue(undefined, a);
    }
  }

  const mergeMap = {
    url: valueFromConfig2,
    method: valueFromConfig2,
    data: valueFromConfig2,
    baseURL: defaultToConfig2,
    transformRequest: defaultToConfig2,
    transformResponse: defaultToConfig2,
    paramsSerializer: defaultToConfig2,
    timeout: defaultToConfig2,
    timeoutMessage: defaultToConfig2,
    withCredentials: defaultToConfig2,
    withXSRFToken: defaultToConfig2,
    adapter: defaultToConfig2,
    responseType: defaultToConfig2,
    xsrfCookieName: defaultToConfig2,
    xsrfHeaderName: defaultToConfig2,
    onUploadProgress: defaultToConfig2,
    onDownloadProgress: defaultToConfig2,
    decompress: defaultToConfig2,
    maxContentLength: defaultToConfig2,
    maxBodyLength: defaultToConfig2,
    beforeRedirect: defaultToConfig2,
    transport: defaultToConfig2,
    httpAgent: defaultToConfig2,
    httpsAgent: defaultToConfig2,
    cancelToken: defaultToConfig2,
    socketPath: defaultToConfig2,
    responseEncoding: defaultToConfig2,
    validateStatus: mergeDirectKeys,
    headers: (a, b) => mergeDeepProperties(headersToObject(a), headersToObject(b), true)
  };

  utils$1.forEach(Object.keys(Object.assign({}, config1, config2)), function computeConfigValue(prop) {
    const merge = mergeMap[prop] || mergeDeepProperties;
    const configValue = merge(config1[prop], config2[prop], prop);
    (utils$1.isUndefined(configValue) && merge !== mergeDirectKeys) || (config[prop] = configValue);
  });

  return config;
}

const VERSION = "1.6.8";

const validators$1 = {};

// eslint-disable-next-line func-names
['object', 'boolean', 'number', 'function', 'string', 'symbol'].forEach((type, i) => {
  validators$1[type] = function validator(thing) {
    return typeof thing === type || 'a' + (i < 1 ? 'n ' : ' ') + type;
  };
});

const deprecatedWarnings = {};

/**
 * Transitional option validator
 *
 * @param {function|boolean?} validator - set to false if the transitional option has been removed
 * @param {string?} version - deprecated version / removed since version
 * @param {string?} message - some message with additional info
 *
 * @returns {function}
 */
validators$1.transitional = function transitional(validator, version, message) {
  function formatMessage(opt, desc) {
    return '[Axios v' + VERSION + '] Transitional option \'' + opt + '\'' + desc + (message ? '. ' + message : '');
  }

  // eslint-disable-next-line func-names
  return (value, opt, opts) => {
    if (validator === false) {
      throw new AxiosError(
        formatMessage(opt, ' has been removed' + (version ? ' in ' + version : '')),
        AxiosError.ERR_DEPRECATED
      );
    }

    if (version && !deprecatedWarnings[opt]) {
      deprecatedWarnings[opt] = true;
      // eslint-disable-next-line no-console
      console.warn(
        formatMessage(
          opt,
          ' has been deprecated since v' + version + ' and will be removed in the near future'
        )
      );
    }

    return validator ? validator(value, opt, opts) : true;
  };
};

/**
 * Assert object's properties type
 *
 * @param {object} options
 * @param {object} schema
 * @param {boolean?} allowUnknown
 *
 * @returns {object}
 */

function assertOptions(options, schema, allowUnknown) {
  if (typeof options !== 'object') {
    throw new AxiosError('options must be an object', AxiosError.ERR_BAD_OPTION_VALUE);
  }
  const keys = Object.keys(options);
  let i = keys.length;
  while (i-- > 0) {
    const opt = keys[i];
    const validator = schema[opt];
    if (validator) {
      const value = options[opt];
      const result = value === undefined || validator(value, opt, options);
      if (result !== true) {
        throw new AxiosError('option ' + opt + ' must be ' + result, AxiosError.ERR_BAD_OPTION_VALUE);
      }
      continue;
    }
    if (allowUnknown !== true) {
      throw new AxiosError('Unknown option ' + opt, AxiosError.ERR_BAD_OPTION);
    }
  }
}

const validator = {
  assertOptions,
  validators: validators$1
};

const validators = validator.validators;

/**
 * Create a new instance of Axios
 *
 * @param {Object} instanceConfig The default config for the instance
 *
 * @return {Axios} A new instance of Axios
 */
class Axios {
  constructor(instanceConfig) {
    this.defaults = instanceConfig;
    this.interceptors = {
      request: new InterceptorManager(),
      response: new InterceptorManager()
    };
  }

  /**
   * Dispatch a request
   *
   * @param {String|Object} configOrUrl The config specific for this request (merged with this.defaults)
   * @param {?Object} config
   *
   * @returns {Promise} The Promise to be fulfilled
   */
  async request(configOrUrl, config) {
    try {
      return await this._request(configOrUrl, config);
    } catch (err) {
      if (err instanceof Error) {
        let dummy;

        Error.captureStackTrace ? Error.captureStackTrace(dummy = {}) : (dummy = new Error());

        // slice off the Error: ... line
        const stack = dummy.stack ? dummy.stack.replace(/^.+\n/, '') : '';

        if (!err.stack) {
          err.stack = stack;
          // match without the 2 top stack lines
        } else if (stack && !String(err.stack).endsWith(stack.replace(/^.+\n.+\n/, ''))) {
          err.stack += '\n' + stack;
        }
      }

      throw err;
    }
  }

  _request(configOrUrl, config) {
    /*eslint no-param-reassign:0*/
    // Allow for axios('example/url'[, config]) a la fetch API
    if (typeof configOrUrl === 'string') {
      config = config || {};
      config.url = configOrUrl;
    } else {
      config = configOrUrl || {};
    }

    config = mergeConfig(this.defaults, config);

    const {transitional, paramsSerializer, headers} = config;

    if (transitional !== undefined) {
      validator.assertOptions(transitional, {
        silentJSONParsing: validators.transitional(validators.boolean),
        forcedJSONParsing: validators.transitional(validators.boolean),
        clarifyTimeoutError: validators.transitional(validators.boolean)
      }, false);
    }

    if (paramsSerializer != null) {
      if (utils$1.isFunction(paramsSerializer)) {
        config.paramsSerializer = {
          serialize: paramsSerializer
        };
      } else {
        validator.assertOptions(paramsSerializer, {
          encode: validators.function,
          serialize: validators.function
        }, true);
      }
    }

    // Set config.method
    config.method = (config.method || this.defaults.method || 'get').toLowerCase();

    // Flatten headers
    let contextHeaders = headers && utils$1.merge(
      headers.common,
      headers[config.method]
    );

    headers && utils$1.forEach(
      ['delete', 'get', 'head', 'post', 'put', 'patch', 'common'],
      (method) => {
        delete headers[method];
      }
    );

    config.headers = AxiosHeaders$1.concat(contextHeaders, headers);

    // filter out skipped interceptors
    const requestInterceptorChain = [];
    let synchronousRequestInterceptors = true;
    this.interceptors.request.forEach(function unshiftRequestInterceptors(interceptor) {
      if (typeof interceptor.runWhen === 'function' && interceptor.runWhen(config) === false) {
        return;
      }

      synchronousRequestInterceptors = synchronousRequestInterceptors && interceptor.synchronous;

      requestInterceptorChain.unshift(interceptor.fulfilled, interceptor.rejected);
    });

    const responseInterceptorChain = [];
    this.interceptors.response.forEach(function pushResponseInterceptors(interceptor) {
      responseInterceptorChain.push(interceptor.fulfilled, interceptor.rejected);
    });

    let promise;
    let i = 0;
    let len;

    if (!synchronousRequestInterceptors) {
      const chain = [dispatchRequest.bind(this), undefined];
      chain.unshift.apply(chain, requestInterceptorChain);
      chain.push.apply(chain, responseInterceptorChain);
      len = chain.length;

      promise = Promise.resolve(config);

      while (i < len) {
        promise = promise.then(chain[i++], chain[i++]);
      }

      return promise;
    }

    len = requestInterceptorChain.length;

    let newConfig = config;

    i = 0;

    while (i < len) {
      const onFulfilled = requestInterceptorChain[i++];
      const onRejected = requestInterceptorChain[i++];
      try {
        newConfig = onFulfilled(newConfig);
      } catch (error) {
        onRejected.call(this, error);
        break;
      }
    }

    try {
      promise = dispatchRequest.call(this, newConfig);
    } catch (error) {
      return Promise.reject(error);
    }

    i = 0;
    len = responseInterceptorChain.length;

    while (i < len) {
      promise = promise.then(responseInterceptorChain[i++], responseInterceptorChain[i++]);
    }

    return promise;
  }

  getUri(config) {
    config = mergeConfig(this.defaults, config);
    const fullPath = buildFullPath(config.baseURL, config.url);
    return buildURL(fullPath, config.params, config.paramsSerializer);
  }
}

// Provide aliases for supported request methods
utils$1.forEach(['delete', 'get', 'head', 'options'], function forEachMethodNoData(method) {
  /*eslint func-names:0*/
  Axios.prototype[method] = function(url, config) {
    return this.request(mergeConfig(config || {}, {
      method,
      url,
      data: (config || {}).data
    }));
  };
});

utils$1.forEach(['post', 'put', 'patch'], function forEachMethodWithData(method) {
  /*eslint func-names:0*/

  function generateHTTPMethod(isForm) {
    return function httpMethod(url, data, config) {
      return this.request(mergeConfig(config || {}, {
        method,
        headers: isForm ? {
          'Content-Type': 'multipart/form-data'
        } : {},
        url,
        data
      }));
    };
  }

  Axios.prototype[method] = generateHTTPMethod();

  Axios.prototype[method + 'Form'] = generateHTTPMethod(true);
});

const Axios$1 = Axios;

/**
 * A `CancelToken` is an object that can be used to request cancellation of an operation.
 *
 * @param {Function} executor The executor function.
 *
 * @returns {CancelToken}
 */
class CancelToken {
  constructor(executor) {
    if (typeof executor !== 'function') {
      throw new TypeError('executor must be a function.');
    }

    let resolvePromise;

    this.promise = new Promise(function promiseExecutor(resolve) {
      resolvePromise = resolve;
    });

    const token = this;

    // eslint-disable-next-line func-names
    this.promise.then(cancel => {
      if (!token._listeners) return;

      let i = token._listeners.length;

      while (i-- > 0) {
        token._listeners[i](cancel);
      }
      token._listeners = null;
    });

    // eslint-disable-next-line func-names
    this.promise.then = onfulfilled => {
      let _resolve;
      // eslint-disable-next-line func-names
      const promise = new Promise(resolve => {
        token.subscribe(resolve);
        _resolve = resolve;
      }).then(onfulfilled);

      promise.cancel = function reject() {
        token.unsubscribe(_resolve);
      };

      return promise;
    };

    executor(function cancel(message, config, request) {
      if (token.reason) {
        // Cancellation has already been requested
        return;
      }

      token.reason = new CanceledError(message, config, request);
      resolvePromise(token.reason);
    });
  }

  /**
   * Throws a `CanceledError` if cancellation has been requested.
   */
  throwIfRequested() {
    if (this.reason) {
      throw this.reason;
    }
  }

  /**
   * Subscribe to the cancel signal
   */

  subscribe(listener) {
    if (this.reason) {
      listener(this.reason);
      return;
    }

    if (this._listeners) {
      this._listeners.push(listener);
    } else {
      this._listeners = [listener];
    }
  }

  /**
   * Unsubscribe from the cancel signal
   */

  unsubscribe(listener) {
    if (!this._listeners) {
      return;
    }
    const index = this._listeners.indexOf(listener);
    if (index !== -1) {
      this._listeners.splice(index, 1);
    }
  }

  /**
   * Returns an object that contains a new `CancelToken` and a function that, when called,
   * cancels the `CancelToken`.
   */
  static source() {
    let cancel;
    const token = new CancelToken(function executor(c) {
      cancel = c;
    });
    return {
      token,
      cancel
    };
  }
}

const CancelToken$1 = CancelToken;

/**
 * Syntactic sugar for invoking a function and expanding an array for arguments.
 *
 * Common use case would be to use `Function.prototype.apply`.
 *
 *  ```js
 *  function f(x, y, z) {}
 *  var args = [1, 2, 3];
 *  f.apply(null, args);
 *  ```
 *
 * With `spread` this example can be re-written.
 *
 *  ```js
 *  spread(function(x, y, z) {})([1, 2, 3]);
 *  ```
 *
 * @param {Function} callback
 *
 * @returns {Function}
 */
function spread(callback) {
  return function wrap(arr) {
    return callback.apply(null, arr);
  };
}

/**
 * Determines whether the payload is an error thrown by Axios
 *
 * @param {*} payload The value to test
 *
 * @returns {boolean} True if the payload is an error thrown by Axios, otherwise false
 */
function isAxiosError(payload) {
  return utils$1.isObject(payload) && (payload.isAxiosError === true);
}

const HttpStatusCode = {
  Continue: 100,
  SwitchingProtocols: 101,
  Processing: 102,
  EarlyHints: 103,
  Ok: 200,
  Created: 201,
  Accepted: 202,
  NonAuthoritativeInformation: 203,
  NoContent: 204,
  ResetContent: 205,
  PartialContent: 206,
  MultiStatus: 207,
  AlreadyReported: 208,
  ImUsed: 226,
  MultipleChoices: 300,
  MovedPermanently: 301,
  Found: 302,
  SeeOther: 303,
  NotModified: 304,
  UseProxy: 305,
  Unused: 306,
  TemporaryRedirect: 307,
  PermanentRedirect: 308,
  BadRequest: 400,
  Unauthorized: 401,
  PaymentRequired: 402,
  Forbidden: 403,
  NotFound: 404,
  MethodNotAllowed: 405,
  NotAcceptable: 406,
  ProxyAuthenticationRequired: 407,
  RequestTimeout: 408,
  Conflict: 409,
  Gone: 410,
  LengthRequired: 411,
  PreconditionFailed: 412,
  PayloadTooLarge: 413,
  UriTooLong: 414,
  UnsupportedMediaType: 415,
  RangeNotSatisfiable: 416,
  ExpectationFailed: 417,
  ImATeapot: 418,
  MisdirectedRequest: 421,
  UnprocessableEntity: 422,
  Locked: 423,
  FailedDependency: 424,
  TooEarly: 425,
  UpgradeRequired: 426,
  PreconditionRequired: 428,
  TooManyRequests: 429,
  RequestHeaderFieldsTooLarge: 431,
  UnavailableForLegalReasons: 451,
  InternalServerError: 500,
  NotImplemented: 501,
  BadGateway: 502,
  ServiceUnavailable: 503,
  GatewayTimeout: 504,
  HttpVersionNotSupported: 505,
  VariantAlsoNegotiates: 506,
  InsufficientStorage: 507,
  LoopDetected: 508,
  NotExtended: 510,
  NetworkAuthenticationRequired: 511,
};

Object.entries(HttpStatusCode).forEach(([key, value]) => {
  HttpStatusCode[value] = key;
});

const HttpStatusCode$1 = HttpStatusCode;

/**
 * Create an instance of Axios
 *
 * @param {Object} defaultConfig The default config for the instance
 *
 * @returns {Axios} A new instance of Axios
 */
function createInstance(defaultConfig) {
  const context = new Axios$1(defaultConfig);
  const instance = bind(Axios$1.prototype.request, context);

  // Copy axios.prototype to instance
  utils$1.extend(instance, Axios$1.prototype, context, {allOwnKeys: true});

  // Copy context to instance
  utils$1.extend(instance, context, null, {allOwnKeys: true});

  // Factory for creating new instances
  instance.create = function create(instanceConfig) {
    return createInstance(mergeConfig(defaultConfig, instanceConfig));
  };

  return instance;
}

// Create the default instance to be exported
const axios = createInstance(defaults$1);

// Expose Axios class to allow class inheritance
axios.Axios = Axios$1;

// Expose Cancel & CancelToken
axios.CanceledError = CanceledError;
axios.CancelToken = CancelToken$1;
axios.isCancel = isCancel;
axios.VERSION = VERSION;
axios.toFormData = toFormData;

// Expose AxiosError class
axios.AxiosError = AxiosError;

// alias for CanceledError for backward compatibility
axios.Cancel = axios.CanceledError;

// Expose all/spread
axios.all = function all(promises) {
  return Promise.all(promises);
};

axios.spread = spread;

// Expose isAxiosError
axios.isAxiosError = isAxiosError;

// Expose mergeConfig
axios.mergeConfig = mergeConfig;

axios.AxiosHeaders = AxiosHeaders$1;

axios.formToJSON = thing => formDataToJSON(utils$1.isHTMLForm(thing) ? new FormData(thing) : thing);

axios.getAdapter = adapters.getAdapter;

axios.HttpStatusCode = HttpStatusCode$1;

axios.default = axios;

const devFrontendUrl = "http://0.0.0.0:3000";
const devFrontendUrlWin = "http://localhost:3000";
const devBackendUrl = "http://0.0.0.0:8080";
const devBackendUrlWin = "http://localhost:8080";
const wsPath = "/ws";
const devWsUrl = "ws://0.0.0.0:8080" + wsPath;
const devWsUrlWin = "ws://localhost:8080" + wsPath;
const origin = window.location.origin;
const protocol = window.location.protocol;
const host = window.location.host;
let wsProtocol;
if (protocol == "http:") {
  wsProtocol = "ws://";
} else if (protocol == "https:") {
  wsProtocol = "wss://";
}
function createGlobalStates$h() {
  let serverUrl;
  let wsUrl;
  if (origin == devFrontendUrl) {
    serverUrl = devBackendUrl;
    wsUrl = devWsUrl;
  } else if (origin == devFrontendUrlWin) {
    serverUrl = devBackendUrlWin;
    wsUrl = devWsUrlWin;
  } else {
    serverUrl = "";
    wsUrl = wsProtocol + host + wsPath;
  }
  const withCredentials = origin == devFrontendUrl;
  return {
    serverUrl,
    withCredentials,
    wsUrl
  };
}
const gvServer = createRoot(createGlobalStates$h);

function createGlobalStates$g() {
  const [email, setEmail] = createSignal(null);
  const [password, setPassword] = createSignal(null);
  const [errorInEmail, setErrorInEmail] = createSignal(true);
  const [errorInPassword, setErrorInPassword] = createSignal(true);
  const [emailErrorMsg, setEmailErrorMsg] = createSignal("");
  const [passwordErrorMsg, setPasswordErrorMsg] = createSignal("");
  function checkEmailAndPassword() {
    checkEmailError();
    checkPasswordError();
  }
  function checkEmailError() {
    if (!email() || email().length == 0) {
      setEmailErrorMsg("Please enter an email.");
      setErrorInEmail(true);
      return;
    }
    let regex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9]+)+$/;
    if (!email().match(regex)) {
      setEmailErrorMsg("Email is invalid.");
      setErrorInEmail(true);
      return;
    }
    setEmailErrorMsg("");
    setErrorInEmail(false);
    return;
  }
  function checkPasswordError() {
    if (!password() || password().length == 0) {
      setPasswordErrorMsg("Please enter a password.");
      setErrorInPassword(true);
      return;
    }
    let regex = /^[a-zA-Z0-9.!?#$%&^_@*]+$/;
    if (!password().match(regex)) {
      setPasswordErrorMsg("Password is invalid (a-z, A-Z, 0-9, .!?#$%&^_@* allowed).");
      setErrorInPassword(true);
      return;
    }
    setPasswordErrorMsg("");
    setErrorInPassword(false);
    return true;
  }
  return {
    email,
    setEmail,
    password,
    setPassword,
    errorInEmail,
    setErrorInEmail,
    errorInPassword,
    setErrorInPassword,
    checkEmailAndPassword,
    emailErrorMsg,
    passwordErrorMsg
  };
}
const gvEmail = createRoot(createGlobalStates$g);

var _tmpl$$1o = /* @__PURE__ */ template(`<div><span></span><br>`);
function createGlobalStates$f() {
  const [showErrorDialog, setShowErrorDialog] = createSignal(false);
  const [errorDialogTitle, setErrorDialogTitle] = createSignal("");
  const [errorDialogText, setErrorDialogText] = createSignal("");
  const [showDismiss, setShowDismiss] = createSignal(true);
  function getErrorText() {
    const lines = errorDialogText().split("\n");
    return createComponent(For, {
      each: lines,
      children: (line) => (() => {
        var _el$ = _tmpl$$1o(), _el$2 = _el$.firstChild;
        insert(_el$2, line);
        return _el$;
      })()
    });
  }
  return {
    showErrorDialog,
    setShowErrorDialog,
    errorDialogTitle,
    setErrorDialogTitle,
    errorDialogText,
    setErrorDialogText,
    getErrorText,
    showDismiss,
    setShowDismiss
  };
}
const gvErrorDialogState = createRoot(createGlobalStates$f);

function createGlobalStates$e() {
  const [systemSetupNeeded, setSystemSetupNeeded] = createSignal(false);
  return {
    systemSetupNeeded,
    setSystemSetupNeeded
  };
}
const gvSystemSetupNeeded = createRoot(createGlobalStates$e);

const {
  setShowErrorDialog,
  setErrorDialogTitle,
  setErrorDialogText
} = gvErrorDialogState;
const {
  setSystemSetupNeeded
} = gvSystemSetupNeeded;
function handleError(err) {
  console.error(err);
  setErrorDialogTitle("Error");
  if (err.response == void 0) {
    return;
  } else if (err.response.status == 404) {
    setErrorDialogText("Resource not found");
  } else if (err.response.status == 403) {
    setErrorDialogText("You are not authorized for " + err.request.responseURL);
  } else if (err.response.statusText == "SYSTEM_SETUP_NEEDED") {
    setSystemSetupNeeded(true);
    return;
  } else {
    let msg = "";
    if (err.response.data.msg) {
      msg = err.response.data.msg;
    } else if (err.response.data) {
      msg = err.response.data;
    }
    setErrorDialogText(msg + "\n\nPlease contact the system admin if help is needed.");
  }
  setShowErrorDialog(true);
}

var define_process_env_default = {};
/**
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
 */
const stringToByteArray$1 = function(str) {
  const out = [];
  let p = 0;
  for (let i = 0; i < str.length; i++) {
    let c = str.charCodeAt(i);
    if (c < 128) {
      out[p++] = c;
    } else if (c < 2048) {
      out[p++] = c >> 6 | 192;
      out[p++] = c & 63 | 128;
    } else if ((c & 64512) === 55296 && i + 1 < str.length && (str.charCodeAt(i + 1) & 64512) === 56320) {
      c = 65536 + ((c & 1023) << 10) + (str.charCodeAt(++i) & 1023);
      out[p++] = c >> 18 | 240;
      out[p++] = c >> 12 & 63 | 128;
      out[p++] = c >> 6 & 63 | 128;
      out[p++] = c & 63 | 128;
    } else {
      out[p++] = c >> 12 | 224;
      out[p++] = c >> 6 & 63 | 128;
      out[p++] = c & 63 | 128;
    }
  }
  return out;
};
const byteArrayToString = function(bytes) {
  const out = [];
  let pos = 0, c = 0;
  while (pos < bytes.length) {
    const c1 = bytes[pos++];
    if (c1 < 128) {
      out[c++] = String.fromCharCode(c1);
    } else if (c1 > 191 && c1 < 224) {
      const c2 = bytes[pos++];
      out[c++] = String.fromCharCode((c1 & 31) << 6 | c2 & 63);
    } else if (c1 > 239 && c1 < 365) {
      const c2 = bytes[pos++];
      const c3 = bytes[pos++];
      const c4 = bytes[pos++];
      const u = ((c1 & 7) << 18 | (c2 & 63) << 12 | (c3 & 63) << 6 | c4 & 63) - 65536;
      out[c++] = String.fromCharCode(55296 + (u >> 10));
      out[c++] = String.fromCharCode(56320 + (u & 1023));
    } else {
      const c2 = bytes[pos++];
      const c3 = bytes[pos++];
      out[c++] = String.fromCharCode((c1 & 15) << 12 | (c2 & 63) << 6 | c3 & 63);
    }
  }
  return out.join("");
};
const base64 = {
  /**
   * Maps bytes to characters.
   */
  byteToCharMap_: null,
  /**
   * Maps characters to bytes.
   */
  charToByteMap_: null,
  /**
   * Maps bytes to websafe characters.
   * @private
   */
  byteToCharMapWebSafe_: null,
  /**
   * Maps websafe characters to bytes.
   * @private
   */
  charToByteMapWebSafe_: null,
  /**
   * Our default alphabet, shared between
   * ENCODED_VALS and ENCODED_VALS_WEBSAFE
   */
  ENCODED_VALS_BASE: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
  /**
   * Our default alphabet. Value 64 (=) is special; it means "nothing."
   */
  get ENCODED_VALS() {
    return this.ENCODED_VALS_BASE + "+/=";
  },
  /**
   * Our websafe alphabet.
   */
  get ENCODED_VALS_WEBSAFE() {
    return this.ENCODED_VALS_BASE + "-_.";
  },
  /**
   * Whether this browser supports the atob and btoa functions. This extension
   * started at Mozilla but is now implemented by many browsers. We use the
   * ASSUME_* variables to avoid pulling in the full useragent detection library
   * but still allowing the standard per-browser compilations.
   *
   */
  HAS_NATIVE_SUPPORT: typeof atob === "function",
  /**
   * Base64-encode an array of bytes.
   *
   * @param input An array of bytes (numbers with
   *     value in [0, 255]) to encode.
   * @param webSafe Boolean indicating we should use the
   *     alternative alphabet.
   * @return The base64 encoded string.
   */
  encodeByteArray(input, webSafe) {
    if (!Array.isArray(input)) {
      throw Error("encodeByteArray takes an array as a parameter");
    }
    this.init_();
    const byteToCharMap = webSafe ? this.byteToCharMapWebSafe_ : this.byteToCharMap_;
    const output = [];
    for (let i = 0; i < input.length; i += 3) {
      const byte1 = input[i];
      const haveByte2 = i + 1 < input.length;
      const byte2 = haveByte2 ? input[i + 1] : 0;
      const haveByte3 = i + 2 < input.length;
      const byte3 = haveByte3 ? input[i + 2] : 0;
      const outByte1 = byte1 >> 2;
      const outByte2 = (byte1 & 3) << 4 | byte2 >> 4;
      let outByte3 = (byte2 & 15) << 2 | byte3 >> 6;
      let outByte4 = byte3 & 63;
      if (!haveByte3) {
        outByte4 = 64;
        if (!haveByte2) {
          outByte3 = 64;
        }
      }
      output.push(byteToCharMap[outByte1], byteToCharMap[outByte2], byteToCharMap[outByte3], byteToCharMap[outByte4]);
    }
    return output.join("");
  },
  /**
   * Base64-encode a string.
   *
   * @param input A string to encode.
   * @param webSafe If true, we should use the
   *     alternative alphabet.
   * @return The base64 encoded string.
   */
  encodeString(input, webSafe) {
    if (this.HAS_NATIVE_SUPPORT && !webSafe) {
      return btoa(input);
    }
    return this.encodeByteArray(stringToByteArray$1(input), webSafe);
  },
  /**
   * Base64-decode a string.
   *
   * @param input to decode.
   * @param webSafe True if we should use the
   *     alternative alphabet.
   * @return string representing the decoded value.
   */
  decodeString(input, webSafe) {
    if (this.HAS_NATIVE_SUPPORT && !webSafe) {
      return atob(input);
    }
    return byteArrayToString(this.decodeStringToByteArray(input, webSafe));
  },
  /**
   * Base64-decode a string.
   *
   * In base-64 decoding, groups of four characters are converted into three
   * bytes.  If the encoder did not apply padding, the input length may not
   * be a multiple of 4.
   *
   * In this case, the last group will have fewer than 4 characters, and
   * padding will be inferred.  If the group has one or two characters, it decodes
   * to one byte.  If the group has three characters, it decodes to two bytes.
   *
   * @param input Input to decode.
   * @param webSafe True if we should use the web-safe alphabet.
   * @return bytes representing the decoded value.
   */
  decodeStringToByteArray(input, webSafe) {
    this.init_();
    const charToByteMap = webSafe ? this.charToByteMapWebSafe_ : this.charToByteMap_;
    const output = [];
    for (let i = 0; i < input.length; ) {
      const byte1 = charToByteMap[input.charAt(i++)];
      const haveByte2 = i < input.length;
      const byte2 = haveByte2 ? charToByteMap[input.charAt(i)] : 0;
      ++i;
      const haveByte3 = i < input.length;
      const byte3 = haveByte3 ? charToByteMap[input.charAt(i)] : 64;
      ++i;
      const haveByte4 = i < input.length;
      const byte4 = haveByte4 ? charToByteMap[input.charAt(i)] : 64;
      ++i;
      if (byte1 == null || byte2 == null || byte3 == null || byte4 == null) {
        throw new DecodeBase64StringError();
      }
      const outByte1 = byte1 << 2 | byte2 >> 4;
      output.push(outByte1);
      if (byte3 !== 64) {
        const outByte2 = byte2 << 4 & 240 | byte3 >> 2;
        output.push(outByte2);
        if (byte4 !== 64) {
          const outByte3 = byte3 << 6 & 192 | byte4;
          output.push(outByte3);
        }
      }
    }
    return output;
  },
  /**
   * Lazy static initialization function. Called before
   * accessing any of the static map variables.
   * @private
   */
  init_() {
    if (!this.byteToCharMap_) {
      this.byteToCharMap_ = {};
      this.charToByteMap_ = {};
      this.byteToCharMapWebSafe_ = {};
      this.charToByteMapWebSafe_ = {};
      for (let i = 0; i < this.ENCODED_VALS.length; i++) {
        this.byteToCharMap_[i] = this.ENCODED_VALS.charAt(i);
        this.charToByteMap_[this.byteToCharMap_[i]] = i;
        this.byteToCharMapWebSafe_[i] = this.ENCODED_VALS_WEBSAFE.charAt(i);
        this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[i]] = i;
        if (i >= this.ENCODED_VALS_BASE.length) {
          this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(i)] = i;
          this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(i)] = i;
        }
      }
    }
  }
};
class DecodeBase64StringError extends Error {
  constructor() {
    super(...arguments);
    this.name = "DecodeBase64StringError";
  }
}
const base64Encode = function(str) {
  const utf8Bytes = stringToByteArray$1(str);
  return base64.encodeByteArray(utf8Bytes, true);
};
const base64urlEncodeWithoutPadding = function(str) {
  return base64Encode(str).replace(/\./g, "");
};
const base64Decode = function(str) {
  try {
    return base64.decodeString(str, true);
  } catch (e) {
    console.error("base64Decode failed: ", e);
  }
  return null;
};
/**
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
 */
function getGlobal() {
  if (typeof self !== "undefined") {
    return self;
  }
  if (typeof window !== "undefined") {
    return window;
  }
  if (typeof global !== "undefined") {
    return global;
  }
  throw new Error("Unable to locate global object.");
}
/**
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
 */
const getDefaultsFromGlobal = () => getGlobal().__FIREBASE_DEFAULTS__;
const getDefaultsFromEnvVariable = () => {
  if (typeof process === "undefined" || typeof define_process_env_default === "undefined") {
    return;
  }
  const defaultsJsonString = define_process_env_default.__FIREBASE_DEFAULTS__;
  if (defaultsJsonString) {
    return JSON.parse(defaultsJsonString);
  }
};
const getDefaultsFromCookie = () => {
  if (typeof document === "undefined") {
    return;
  }
  let match;
  try {
    match = document.cookie.match(/__FIREBASE_DEFAULTS__=([^;]+)/);
  } catch (e) {
    return;
  }
  const decoded = match && base64Decode(match[1]);
  return decoded && JSON.parse(decoded);
};
const getDefaults = () => {
  try {
    return getDefaultsFromGlobal() || getDefaultsFromEnvVariable() || getDefaultsFromCookie();
  } catch (e) {
    console.info(`Unable to get __FIREBASE_DEFAULTS__ due to: ${e}`);
    return;
  }
};
const getDefaultEmulatorHost = (productName) => {
  var _a, _b;
  return (_b = (_a = getDefaults()) === null || _a === void 0 ? void 0 : _a.emulatorHosts) === null || _b === void 0 ? void 0 : _b[productName];
};
const getDefaultAppConfig = () => {
  var _a;
  return (_a = getDefaults()) === null || _a === void 0 ? void 0 : _a.config;
};
const getExperimentalSetting = (name) => {
  var _a;
  return (_a = getDefaults()) === null || _a === void 0 ? void 0 : _a[`_${name}`];
};
/**
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
 */
class Deferred {
  constructor() {
    this.reject = () => {
    };
    this.resolve = () => {
    };
    this.promise = new Promise((resolve, reject) => {
      this.resolve = resolve;
      this.reject = reject;
    });
  }
  /**
   * Our API internals are not promiseified and cannot because our callback APIs have subtle expectations around
   * invoking promises inline, which Promises are forbidden to do. This method accepts an optional node-style callback
   * and returns a node-style callback which will resolve or reject the Deferred's promise.
   */
  wrapCallback(callback) {
    return (error, value) => {
      if (error) {
        this.reject(error);
      } else {
        this.resolve(value);
      }
      if (typeof callback === "function") {
        this.promise.catch(() => {
        });
        if (callback.length === 1) {
          callback(error);
        } else {
          callback(error, value);
        }
      }
    };
  }
}
/**
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
 */
function getUA() {
  if (typeof navigator !== "undefined" && typeof navigator["userAgent"] === "string") {
    return navigator["userAgent"];
  } else {
    return "";
  }
}
function isMobileCordova() {
  return typeof window !== "undefined" && // @ts-ignore Setting up an broadly applicable index signature for Window
  // just to deal with this case would probably be a bad idea.
  !!(window["cordova"] || window["phonegap"] || window["PhoneGap"]) && /ios|iphone|ipod|ipad|android|blackberry|iemobile/i.test(getUA());
}
function isBrowserExtension() {
  const runtime = typeof chrome === "object" ? chrome.runtime : typeof browser === "object" ? browser.runtime : void 0;
  return typeof runtime === "object" && runtime.id !== void 0;
}
function isReactNative() {
  return typeof navigator === "object" && navigator["product"] === "ReactNative";
}
function isIE() {
  const ua = getUA();
  return ua.indexOf("MSIE ") >= 0 || ua.indexOf("Trident/") >= 0;
}
function isIndexedDBAvailable() {
  try {
    return typeof indexedDB === "object";
  } catch (e) {
    return false;
  }
}
function validateIndexedDBOpenable() {
  return new Promise((resolve, reject) => {
    try {
      let preExist = true;
      const DB_CHECK_NAME = "validate-browser-context-for-indexeddb-analytics-module";
      const request = self.indexedDB.open(DB_CHECK_NAME);
      request.onsuccess = () => {
        request.result.close();
        if (!preExist) {
          self.indexedDB.deleteDatabase(DB_CHECK_NAME);
        }
        resolve(true);
      };
      request.onupgradeneeded = () => {
        preExist = false;
      };
      request.onerror = () => {
        var _a;
        reject(((_a = request.error) === null || _a === void 0 ? void 0 : _a.message) || "");
      };
    } catch (error) {
      reject(error);
    }
  });
}
/**
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
 */
const ERROR_NAME = "FirebaseError";
class FirebaseError extends Error {
  constructor(code, message, customData) {
    super(message);
    this.code = code;
    this.customData = customData;
    this.name = ERROR_NAME;
    Object.setPrototypeOf(this, FirebaseError.prototype);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ErrorFactory.prototype.create);
    }
  }
}
class ErrorFactory {
  constructor(service, serviceName, errors) {
    this.service = service;
    this.serviceName = serviceName;
    this.errors = errors;
  }
  create(code, ...data) {
    const customData = data[0] || {};
    const fullCode = `${this.service}/${code}`;
    const template = this.errors[code];
    const message = template ? replaceTemplate(template, customData) : "Error";
    const fullMessage = `${this.serviceName}: ${message} (${fullCode}).`;
    const error = new FirebaseError(fullCode, fullMessage, customData);
    return error;
  }
}
function replaceTemplate(template, data) {
  return template.replace(PATTERN, (_, key) => {
    const value = data[key];
    return value != null ? String(value) : `<${key}?>`;
  });
}
const PATTERN = /\{\$([^}]+)}/g;
function isEmpty(obj) {
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      return false;
    }
  }
  return true;
}
function deepEqual(a, b) {
  if (a === b) {
    return true;
  }
  const aKeys = Object.keys(a);
  const bKeys = Object.keys(b);
  for (const k of aKeys) {
    if (!bKeys.includes(k)) {
      return false;
    }
    const aProp = a[k];
    const bProp = b[k];
    if (isObject(aProp) && isObject(bProp)) {
      if (!deepEqual(aProp, bProp)) {
        return false;
      }
    } else if (aProp !== bProp) {
      return false;
    }
  }
  for (const k of bKeys) {
    if (!aKeys.includes(k)) {
      return false;
    }
  }
  return true;
}
function isObject(thing) {
  return thing !== null && typeof thing === "object";
}
/**
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
 */
function querystring(querystringParams) {
  const params = [];
  for (const [key, value] of Object.entries(querystringParams)) {
    if (Array.isArray(value)) {
      value.forEach((arrayVal) => {
        params.push(encodeURIComponent(key) + "=" + encodeURIComponent(arrayVal));
      });
    } else {
      params.push(encodeURIComponent(key) + "=" + encodeURIComponent(value));
    }
  }
  return params.length ? "&" + params.join("&") : "";
}
function querystringDecode(querystring2) {
  const obj = {};
  const tokens = querystring2.replace(/^\?/, "").split("&");
  tokens.forEach((token) => {
    if (token) {
      const [key, value] = token.split("=");
      obj[decodeURIComponent(key)] = decodeURIComponent(value);
    }
  });
  return obj;
}
function extractQuerystring(url) {
  const queryStart = url.indexOf("?");
  if (!queryStart) {
    return "";
  }
  const fragmentStart = url.indexOf("#", queryStart);
  return url.substring(queryStart, fragmentStart > 0 ? fragmentStart : void 0);
}
function createSubscribe(executor, onNoObservers) {
  const proxy = new ObserverProxy(executor, onNoObservers);
  return proxy.subscribe.bind(proxy);
}
class ObserverProxy {
  /**
   * @param executor Function which can make calls to a single Observer
   *     as a proxy.
   * @param onNoObservers Callback when count of Observers goes to zero.
   */
  constructor(executor, onNoObservers) {
    this.observers = [];
    this.unsubscribes = [];
    this.observerCount = 0;
    this.task = Promise.resolve();
    this.finalized = false;
    this.onNoObservers = onNoObservers;
    this.task.then(() => {
      executor(this);
    }).catch((e) => {
      this.error(e);
    });
  }
  next(value) {
    this.forEachObserver((observer) => {
      observer.next(value);
    });
  }
  error(error) {
    this.forEachObserver((observer) => {
      observer.error(error);
    });
    this.close(error);
  }
  complete() {
    this.forEachObserver((observer) => {
      observer.complete();
    });
    this.close();
  }
  /**
   * Subscribe function that can be used to add an Observer to the fan-out list.
   *
   * - We require that no event is sent to a subscriber sychronously to their
   *   call to subscribe().
   */
  subscribe(nextOrObserver, error, complete) {
    let observer;
    if (nextOrObserver === void 0 && error === void 0 && complete === void 0) {
      throw new Error("Missing Observer.");
    }
    if (implementsAnyMethods(nextOrObserver, [
      "next",
      "error",
      "complete"
    ])) {
      observer = nextOrObserver;
    } else {
      observer = {
        next: nextOrObserver,
        error,
        complete
      };
    }
    if (observer.next === void 0) {
      observer.next = noop;
    }
    if (observer.error === void 0) {
      observer.error = noop;
    }
    if (observer.complete === void 0) {
      observer.complete = noop;
    }
    const unsub = this.unsubscribeOne.bind(this, this.observers.length);
    if (this.finalized) {
      this.task.then(() => {
        try {
          if (this.finalError) {
            observer.error(this.finalError);
          } else {
            observer.complete();
          }
        } catch (e) {
        }
        return;
      });
    }
    this.observers.push(observer);
    return unsub;
  }
  // Unsubscribe is synchronous - we guarantee that no events are sent to
  // any unsubscribed Observer.
  unsubscribeOne(i) {
    if (this.observers === void 0 || this.observers[i] === void 0) {
      return;
    }
    delete this.observers[i];
    this.observerCount -= 1;
    if (this.observerCount === 0 && this.onNoObservers !== void 0) {
      this.onNoObservers(this);
    }
  }
  forEachObserver(fn) {
    if (this.finalized) {
      return;
    }
    for (let i = 0; i < this.observers.length; i++) {
      this.sendOne(i, fn);
    }
  }
  // Call the Observer via one of it's callback function. We are careful to
  // confirm that the observe has not been unsubscribed since this asynchronous
  // function had been queued.
  sendOne(i, fn) {
    this.task.then(() => {
      if (this.observers !== void 0 && this.observers[i] !== void 0) {
        try {
          fn(this.observers[i]);
        } catch (e) {
          if (typeof console !== "undefined" && console.error) {
            console.error(e);
          }
        }
      }
    });
  }
  close(err) {
    if (this.finalized) {
      return;
    }
    this.finalized = true;
    if (err !== void 0) {
      this.finalError = err;
    }
    this.task.then(() => {
      this.observers = void 0;
      this.onNoObservers = void 0;
    });
  }
}
function implementsAnyMethods(obj, methods) {
  if (typeof obj !== "object" || obj === null) {
    return false;
  }
  for (const method of methods) {
    if (method in obj && typeof obj[method] === "function") {
      return true;
    }
  }
  return false;
}
function noop() {
}
/**
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
 */
function getModularInstance(service) {
  if (service && service._delegate) {
    return service._delegate;
  } else {
    return service;
  }
}

/**
 * Component for service name T, e.g. `auth`, `auth-internal`
 */
class Component {
    /**
     *
     * @param name The public service name, e.g. app, auth, firestore, database
     * @param instanceFactory Service factory responsible for creating the public interface
     * @param type whether the service provided by the component is public or private
     */
    constructor(name, instanceFactory, type) {
        this.name = name;
        this.instanceFactory = instanceFactory;
        this.type = type;
        this.multipleInstances = false;
        /**
         * Properties to be added to the service namespace
         */
        this.serviceProps = {};
        this.instantiationMode = "LAZY" /* InstantiationMode.LAZY */;
        this.onInstanceCreated = null;
    }
    setInstantiationMode(mode) {
        this.instantiationMode = mode;
        return this;
    }
    setMultipleInstances(multipleInstances) {
        this.multipleInstances = multipleInstances;
        return this;
    }
    setServiceProps(props) {
        this.serviceProps = props;
        return this;
    }
    setInstanceCreatedCallback(callback) {
        this.onInstanceCreated = callback;
        return this;
    }
}

/**
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
 */
const DEFAULT_ENTRY_NAME$1 = '[DEFAULT]';

/**
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
 */
/**
 * Provider for instance for service name T, e.g. 'auth', 'auth-internal'
 * NameServiceMapping[T] is an alias for the type of the instance
 */
class Provider {
    constructor(name, container) {
        this.name = name;
        this.container = container;
        this.component = null;
        this.instances = new Map();
        this.instancesDeferred = new Map();
        this.instancesOptions = new Map();
        this.onInitCallbacks = new Map();
    }
    /**
     * @param identifier A provider can provide mulitple instances of a service
     * if this.component.multipleInstances is true.
     */
    get(identifier) {
        // if multipleInstances is not supported, use the default name
        const normalizedIdentifier = this.normalizeInstanceIdentifier(identifier);
        if (!this.instancesDeferred.has(normalizedIdentifier)) {
            const deferred = new Deferred();
            this.instancesDeferred.set(normalizedIdentifier, deferred);
            if (this.isInitialized(normalizedIdentifier) ||
                this.shouldAutoInitialize()) {
                // initialize the service if it can be auto-initialized
                try {
                    const instance = this.getOrInitializeService({
                        instanceIdentifier: normalizedIdentifier
                    });
                    if (instance) {
                        deferred.resolve(instance);
                    }
                }
                catch (e) {
                    // when the instance factory throws an exception during get(), it should not cause
                    // a fatal error. We just return the unresolved promise in this case.
                }
            }
        }
        return this.instancesDeferred.get(normalizedIdentifier).promise;
    }
    getImmediate(options) {
        var _a;
        // if multipleInstances is not supported, use the default name
        const normalizedIdentifier = this.normalizeInstanceIdentifier(options === null || options === void 0 ? void 0 : options.identifier);
        const optional = (_a = options === null || options === void 0 ? void 0 : options.optional) !== null && _a !== void 0 ? _a : false;
        if (this.isInitialized(normalizedIdentifier) ||
            this.shouldAutoInitialize()) {
            try {
                return this.getOrInitializeService({
                    instanceIdentifier: normalizedIdentifier
                });
            }
            catch (e) {
                if (optional) {
                    return null;
                }
                else {
                    throw e;
                }
            }
        }
        else {
            // In case a component is not initialized and should/can not be auto-initialized at the moment, return null if the optional flag is set, or throw
            if (optional) {
                return null;
            }
            else {
                throw Error(`Service ${this.name} is not available`);
            }
        }
    }
    getComponent() {
        return this.component;
    }
    setComponent(component) {
        if (component.name !== this.name) {
            throw Error(`Mismatching Component ${component.name} for Provider ${this.name}.`);
        }
        if (this.component) {
            throw Error(`Component for ${this.name} has already been provided`);
        }
        this.component = component;
        // return early without attempting to initialize the component if the component requires explicit initialization (calling `Provider.initialize()`)
        if (!this.shouldAutoInitialize()) {
            return;
        }
        // if the service is eager, initialize the default instance
        if (isComponentEager(component)) {
            try {
                this.getOrInitializeService({ instanceIdentifier: DEFAULT_ENTRY_NAME$1 });
            }
            catch (e) {
                // when the instance factory for an eager Component throws an exception during the eager
                // initialization, it should not cause a fatal error.
                // TODO: Investigate if we need to make it configurable, because some component may want to cause
                // a fatal error in this case?
            }
        }
        // Create service instances for the pending promises and resolve them
        // NOTE: if this.multipleInstances is false, only the default instance will be created
        // and all promises with resolve with it regardless of the identifier.
        for (const [instanceIdentifier, instanceDeferred] of this.instancesDeferred.entries()) {
            const normalizedIdentifier = this.normalizeInstanceIdentifier(instanceIdentifier);
            try {
                // `getOrInitializeService()` should always return a valid instance since a component is guaranteed. use ! to make typescript happy.
                const instance = this.getOrInitializeService({
                    instanceIdentifier: normalizedIdentifier
                });
                instanceDeferred.resolve(instance);
            }
            catch (e) {
                // when the instance factory throws an exception, it should not cause
                // a fatal error. We just leave the promise unresolved.
            }
        }
    }
    clearInstance(identifier = DEFAULT_ENTRY_NAME$1) {
        this.instancesDeferred.delete(identifier);
        this.instancesOptions.delete(identifier);
        this.instances.delete(identifier);
    }
    // app.delete() will call this method on every provider to delete the services
    // TODO: should we mark the provider as deleted?
    async delete() {
        const services = Array.from(this.instances.values());
        await Promise.all([
            ...services
                .filter(service => 'INTERNAL' in service) // legacy services
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                .map(service => service.INTERNAL.delete()),
            ...services
                .filter(service => '_delete' in service) // modularized services
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                .map(service => service._delete())
        ]);
    }
    isComponentSet() {
        return this.component != null;
    }
    isInitialized(identifier = DEFAULT_ENTRY_NAME$1) {
        return this.instances.has(identifier);
    }
    getOptions(identifier = DEFAULT_ENTRY_NAME$1) {
        return this.instancesOptions.get(identifier) || {};
    }
    initialize(opts = {}) {
        const { options = {} } = opts;
        const normalizedIdentifier = this.normalizeInstanceIdentifier(opts.instanceIdentifier);
        if (this.isInitialized(normalizedIdentifier)) {
            throw Error(`${this.name}(${normalizedIdentifier}) has already been initialized`);
        }
        if (!this.isComponentSet()) {
            throw Error(`Component ${this.name} has not been registered yet`);
        }
        const instance = this.getOrInitializeService({
            instanceIdentifier: normalizedIdentifier,
            options
        });
        // resolve any pending promise waiting for the service instance
        for (const [instanceIdentifier, instanceDeferred] of this.instancesDeferred.entries()) {
            const normalizedDeferredIdentifier = this.normalizeInstanceIdentifier(instanceIdentifier);
            if (normalizedIdentifier === normalizedDeferredIdentifier) {
                instanceDeferred.resolve(instance);
            }
        }
        return instance;
    }
    /**
     *
     * @param callback - a function that will be invoked  after the provider has been initialized by calling provider.initialize().
     * The function is invoked SYNCHRONOUSLY, so it should not execute any longrunning tasks in order to not block the program.
     *
     * @param identifier An optional instance identifier
     * @returns a function to unregister the callback
     */
    onInit(callback, identifier) {
        var _a;
        const normalizedIdentifier = this.normalizeInstanceIdentifier(identifier);
        const existingCallbacks = (_a = this.onInitCallbacks.get(normalizedIdentifier)) !== null && _a !== void 0 ? _a : new Set();
        existingCallbacks.add(callback);
        this.onInitCallbacks.set(normalizedIdentifier, existingCallbacks);
        const existingInstance = this.instances.get(normalizedIdentifier);
        if (existingInstance) {
            callback(existingInstance, normalizedIdentifier);
        }
        return () => {
            existingCallbacks.delete(callback);
        };
    }
    /**
     * Invoke onInit callbacks synchronously
     * @param instance the service instance`
     */
    invokeOnInitCallbacks(instance, identifier) {
        const callbacks = this.onInitCallbacks.get(identifier);
        if (!callbacks) {
            return;
        }
        for (const callback of callbacks) {
            try {
                callback(instance, identifier);
            }
            catch (_a) {
                // ignore errors in the onInit callback
            }
        }
    }
    getOrInitializeService({ instanceIdentifier, options = {} }) {
        let instance = this.instances.get(instanceIdentifier);
        if (!instance && this.component) {
            instance = this.component.instanceFactory(this.container, {
                instanceIdentifier: normalizeIdentifierForFactory(instanceIdentifier),
                options
            });
            this.instances.set(instanceIdentifier, instance);
            this.instancesOptions.set(instanceIdentifier, options);
            /**
             * Invoke onInit listeners.
             * Note this.component.onInstanceCreated is different, which is used by the component creator,
             * while onInit listeners are registered by consumers of the provider.
             */
            this.invokeOnInitCallbacks(instance, instanceIdentifier);
            /**
             * Order is important
             * onInstanceCreated() should be called after this.instances.set(instanceIdentifier, instance); which
             * makes `isInitialized()` return true.
             */
            if (this.component.onInstanceCreated) {
                try {
                    this.component.onInstanceCreated(this.container, instanceIdentifier, instance);
                }
                catch (_a) {
                    // ignore errors in the onInstanceCreatedCallback
                }
            }
        }
        return instance || null;
    }
    normalizeInstanceIdentifier(identifier = DEFAULT_ENTRY_NAME$1) {
        if (this.component) {
            return this.component.multipleInstances ? identifier : DEFAULT_ENTRY_NAME$1;
        }
        else {
            return identifier; // assume multiple instances are supported before the component is provided.
        }
    }
    shouldAutoInitialize() {
        return (!!this.component &&
            this.component.instantiationMode !== "EXPLICIT" /* InstantiationMode.EXPLICIT */);
    }
}
// undefined should be passed to the service factory for the default instance
function normalizeIdentifierForFactory(identifier) {
    return identifier === DEFAULT_ENTRY_NAME$1 ? undefined : identifier;
}
function isComponentEager(component) {
    return component.instantiationMode === "EAGER" /* InstantiationMode.EAGER */;
}

/**
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
 */
/**
 * ComponentContainer that provides Providers for service name T, e.g. `auth`, `auth-internal`
 */
class ComponentContainer {
    constructor(name) {
        this.name = name;
        this.providers = new Map();
    }
    /**
     *
     * @param component Component being added
     * @param overwrite When a component with the same name has already been registered,
     * if overwrite is true: overwrite the existing component with the new component and create a new
     * provider with the new component. It can be useful in tests where you want to use different mocks
     * for different tests.
     * if overwrite is false: throw an exception
     */
    addComponent(component) {
        const provider = this.getProvider(component.name);
        if (provider.isComponentSet()) {
            throw new Error(`Component ${component.name} has already been registered with ${this.name}`);
        }
        provider.setComponent(component);
    }
    addOrOverwriteComponent(component) {
        const provider = this.getProvider(component.name);
        if (provider.isComponentSet()) {
            // delete the existing provider from the container, so we can register the new component
            this.providers.delete(component.name);
        }
        this.addComponent(component);
    }
    /**
     * getProvider provides a type safe interface where it can only be called with a field name
     * present in NameServiceMapping interface.
     *
     * Firebase SDKs providing services should extend NameServiceMapping interface to register
     * themselves.
     */
    getProvider(name) {
        if (this.providers.has(name)) {
            return this.providers.get(name);
        }
        // create a Provider for a service that hasn't registered with Firebase
        const provider = new Provider(name, this);
        this.providers.set(name, provider);
        return provider;
    }
    getProviders() {
        return Array.from(this.providers.values());
    }
}

/**
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
 */
/**
 * A container for all of the Logger instances
 */
/**
 * The JS SDK supports 5 log levels and also allows a user the ability to
 * silence the logs altogether.
 *
 * The order is a follows:
 * DEBUG < VERBOSE < INFO < WARN < ERROR
 *
 * All of the log types above the current log level will be captured (i.e. if
 * you set the log level to `INFO`, errors will still be logged, but `DEBUG` and
 * `VERBOSE` logs will not)
 */
var LogLevel;
(function (LogLevel) {
    LogLevel[LogLevel["DEBUG"] = 0] = "DEBUG";
    LogLevel[LogLevel["VERBOSE"] = 1] = "VERBOSE";
    LogLevel[LogLevel["INFO"] = 2] = "INFO";
    LogLevel[LogLevel["WARN"] = 3] = "WARN";
    LogLevel[LogLevel["ERROR"] = 4] = "ERROR";
    LogLevel[LogLevel["SILENT"] = 5] = "SILENT";
})(LogLevel || (LogLevel = {}));
const levelStringToEnum = {
    'debug': LogLevel.DEBUG,
    'verbose': LogLevel.VERBOSE,
    'info': LogLevel.INFO,
    'warn': LogLevel.WARN,
    'error': LogLevel.ERROR,
    'silent': LogLevel.SILENT
};
/**
 * The default log level
 */
const defaultLogLevel = LogLevel.INFO;
/**
 * By default, `console.debug` is not displayed in the developer console (in
 * chrome). To avoid forcing users to have to opt-in to these logs twice
 * (i.e. once for firebase, and once in the console), we are sending `DEBUG`
 * logs to the `console.log` function.
 */
const ConsoleMethod = {
    [LogLevel.DEBUG]: 'log',
    [LogLevel.VERBOSE]: 'log',
    [LogLevel.INFO]: 'info',
    [LogLevel.WARN]: 'warn',
    [LogLevel.ERROR]: 'error'
};
/**
 * The default log handler will forward DEBUG, VERBOSE, INFO, WARN, and ERROR
 * messages on to their corresponding console counterparts (if the log method
 * is supported by the current log level)
 */
const defaultLogHandler = (instance, logType, ...args) => {
    if (logType < instance.logLevel) {
        return;
    }
    const now = new Date().toISOString();
    const method = ConsoleMethod[logType];
    if (method) {
        console[method](`[${now}]  ${instance.name}:`, ...args);
    }
    else {
        throw new Error(`Attempted to log a message with an invalid logType (value: ${logType})`);
    }
};
class Logger {
    /**
     * Gives you an instance of a Logger to capture messages according to
     * Firebase's logging scheme.
     *
     * @param name The name that the logs will be associated with
     */
    constructor(name) {
        this.name = name;
        /**
         * The log level of the given Logger instance.
         */
        this._logLevel = defaultLogLevel;
        /**
         * The main (internal) log handler for the Logger instance.
         * Can be set to a new function in internal package code but not by user.
         */
        this._logHandler = defaultLogHandler;
        /**
         * The optional, additional, user-defined log handler for the Logger instance.
         */
        this._userLogHandler = null;
    }
    get logLevel() {
        return this._logLevel;
    }
    set logLevel(val) {
        if (!(val in LogLevel)) {
            throw new TypeError(`Invalid value "${val}" assigned to \`logLevel\``);
        }
        this._logLevel = val;
    }
    // Workaround for setter/getter having to be the same type.
    setLogLevel(val) {
        this._logLevel = typeof val === 'string' ? levelStringToEnum[val] : val;
    }
    get logHandler() {
        return this._logHandler;
    }
    set logHandler(val) {
        if (typeof val !== 'function') {
            throw new TypeError('Value assigned to `logHandler` must be a function');
        }
        this._logHandler = val;
    }
    get userLogHandler() {
        return this._userLogHandler;
    }
    set userLogHandler(val) {
        this._userLogHandler = val;
    }
    /**
     * The functions below are all based on the `console` interface
     */
    debug(...args) {
        this._userLogHandler && this._userLogHandler(this, LogLevel.DEBUG, ...args);
        this._logHandler(this, LogLevel.DEBUG, ...args);
    }
    log(...args) {
        this._userLogHandler &&
            this._userLogHandler(this, LogLevel.VERBOSE, ...args);
        this._logHandler(this, LogLevel.VERBOSE, ...args);
    }
    info(...args) {
        this._userLogHandler && this._userLogHandler(this, LogLevel.INFO, ...args);
        this._logHandler(this, LogLevel.INFO, ...args);
    }
    warn(...args) {
        this._userLogHandler && this._userLogHandler(this, LogLevel.WARN, ...args);
        this._logHandler(this, LogLevel.WARN, ...args);
    }
    error(...args) {
        this._userLogHandler && this._userLogHandler(this, LogLevel.ERROR, ...args);
        this._logHandler(this, LogLevel.ERROR, ...args);
    }
}

const instanceOfAny = (object, constructors) => constructors.some((c) => object instanceof c);

let idbProxyableTypes;
let cursorAdvanceMethods;
// This is a function to prevent it throwing up in node environments.
function getIdbProxyableTypes() {
    return (idbProxyableTypes ||
        (idbProxyableTypes = [
            IDBDatabase,
            IDBObjectStore,
            IDBIndex,
            IDBCursor,
            IDBTransaction,
        ]));
}
// This is a function to prevent it throwing up in node environments.
function getCursorAdvanceMethods() {
    return (cursorAdvanceMethods ||
        (cursorAdvanceMethods = [
            IDBCursor.prototype.advance,
            IDBCursor.prototype.continue,
            IDBCursor.prototype.continuePrimaryKey,
        ]));
}
const cursorRequestMap = new WeakMap();
const transactionDoneMap = new WeakMap();
const transactionStoreNamesMap = new WeakMap();
const transformCache = new WeakMap();
const reverseTransformCache = new WeakMap();
function promisifyRequest(request) {
    const promise = new Promise((resolve, reject) => {
        const unlisten = () => {
            request.removeEventListener('success', success);
            request.removeEventListener('error', error);
        };
        const success = () => {
            resolve(wrap(request.result));
            unlisten();
        };
        const error = () => {
            reject(request.error);
            unlisten();
        };
        request.addEventListener('success', success);
        request.addEventListener('error', error);
    });
    promise
        .then((value) => {
        // Since cursoring reuses the IDBRequest (*sigh*), we cache it for later retrieval
        // (see wrapFunction).
        if (value instanceof IDBCursor) {
            cursorRequestMap.set(value, request);
        }
        // Catching to avoid "Uncaught Promise exceptions"
    })
        .catch(() => { });
    // This mapping exists in reverseTransformCache but doesn't doesn't exist in transformCache. This
    // is because we create many promises from a single IDBRequest.
    reverseTransformCache.set(promise, request);
    return promise;
}
function cacheDonePromiseForTransaction(tx) {
    // Early bail if we've already created a done promise for this transaction.
    if (transactionDoneMap.has(tx))
        return;
    const done = new Promise((resolve, reject) => {
        const unlisten = () => {
            tx.removeEventListener('complete', complete);
            tx.removeEventListener('error', error);
            tx.removeEventListener('abort', error);
        };
        const complete = () => {
            resolve();
            unlisten();
        };
        const error = () => {
            reject(tx.error || new DOMException('AbortError', 'AbortError'));
            unlisten();
        };
        tx.addEventListener('complete', complete);
        tx.addEventListener('error', error);
        tx.addEventListener('abort', error);
    });
    // Cache it for later retrieval.
    transactionDoneMap.set(tx, done);
}
let idbProxyTraps = {
    get(target, prop, receiver) {
        if (target instanceof IDBTransaction) {
            // Special handling for transaction.done.
            if (prop === 'done')
                return transactionDoneMap.get(target);
            // Polyfill for objectStoreNames because of Edge.
            if (prop === 'objectStoreNames') {
                return target.objectStoreNames || transactionStoreNamesMap.get(target);
            }
            // Make tx.store return the only store in the transaction, or undefined if there are many.
            if (prop === 'store') {
                return receiver.objectStoreNames[1]
                    ? undefined
                    : receiver.objectStore(receiver.objectStoreNames[0]);
            }
        }
        // Else transform whatever we get back.
        return wrap(target[prop]);
    },
    set(target, prop, value) {
        target[prop] = value;
        return true;
    },
    has(target, prop) {
        if (target instanceof IDBTransaction &&
            (prop === 'done' || prop === 'store')) {
            return true;
        }
        return prop in target;
    },
};
function replaceTraps(callback) {
    idbProxyTraps = callback(idbProxyTraps);
}
function wrapFunction(func) {
    // Due to expected object equality (which is enforced by the caching in `wrap`), we
    // only create one new func per func.
    // Edge doesn't support objectStoreNames (booo), so we polyfill it here.
    if (func === IDBDatabase.prototype.transaction &&
        !('objectStoreNames' in IDBTransaction.prototype)) {
        return function (storeNames, ...args) {
            const tx = func.call(unwrap$1(this), storeNames, ...args);
            transactionStoreNamesMap.set(tx, storeNames.sort ? storeNames.sort() : [storeNames]);
            return wrap(tx);
        };
    }
    // Cursor methods are special, as the behaviour is a little more different to standard IDB. In
    // IDB, you advance the cursor and wait for a new 'success' on the IDBRequest that gave you the
    // cursor. It's kinda like a promise that can resolve with many values. That doesn't make sense
    // with real promises, so each advance methods returns a new promise for the cursor object, or
    // undefined if the end of the cursor has been reached.
    if (getCursorAdvanceMethods().includes(func)) {
        return function (...args) {
            // Calling the original function with the proxy as 'this' causes ILLEGAL INVOCATION, so we use
            // the original object.
            func.apply(unwrap$1(this), args);
            return wrap(cursorRequestMap.get(this));
        };
    }
    return function (...args) {
        // Calling the original function with the proxy as 'this' causes ILLEGAL INVOCATION, so we use
        // the original object.
        return wrap(func.apply(unwrap$1(this), args));
    };
}
function transformCachableValue(value) {
    if (typeof value === 'function')
        return wrapFunction(value);
    // This doesn't return, it just creates a 'done' promise for the transaction,
    // which is later returned for transaction.done (see idbObjectHandler).
    if (value instanceof IDBTransaction)
        cacheDonePromiseForTransaction(value);
    if (instanceOfAny(value, getIdbProxyableTypes()))
        return new Proxy(value, idbProxyTraps);
    // Return the same value back if we're not going to transform it.
    return value;
}
function wrap(value) {
    // We sometimes generate multiple promises from a single IDBRequest (eg when cursoring), because
    // IDB is weird and a single IDBRequest can yield many responses, so these can't be cached.
    if (value instanceof IDBRequest)
        return promisifyRequest(value);
    // If we've already transformed this value before, reuse the transformed value.
    // This is faster, but it also provides object equality.
    if (transformCache.has(value))
        return transformCache.get(value);
    const newValue = transformCachableValue(value);
    // Not all types are transformed.
    // These may be primitive types, so they can't be WeakMap keys.
    if (newValue !== value) {
        transformCache.set(value, newValue);
        reverseTransformCache.set(newValue, value);
    }
    return newValue;
}
const unwrap$1 = (value) => reverseTransformCache.get(value);

/**
 * Open a database.
 *
 * @param name Name of the database.
 * @param version Schema version.
 * @param callbacks Additional callbacks.
 */
function openDB(name, version, { blocked, upgrade, blocking, terminated } = {}) {
    const request = indexedDB.open(name, version);
    const openPromise = wrap(request);
    if (upgrade) {
        request.addEventListener('upgradeneeded', (event) => {
            upgrade(wrap(request.result), event.oldVersion, event.newVersion, wrap(request.transaction), event);
        });
    }
    if (blocked) {
        request.addEventListener('blocked', (event) => blocked(
        // Casting due to https://github.com/microsoft/TypeScript-DOM-lib-generator/pull/1405
        event.oldVersion, event.newVersion, event));
    }
    openPromise
        .then((db) => {
        if (terminated)
            db.addEventListener('close', () => terminated());
        if (blocking) {
            db.addEventListener('versionchange', (event) => blocking(event.oldVersion, event.newVersion, event));
        }
    })
        .catch(() => { });
    return openPromise;
}

const readMethods = ['get', 'getKey', 'getAll', 'getAllKeys', 'count'];
const writeMethods = ['put', 'add', 'delete', 'clear'];
const cachedMethods = new Map();
function getMethod(target, prop) {
    if (!(target instanceof IDBDatabase &&
        !(prop in target) &&
        typeof prop === 'string')) {
        return;
    }
    if (cachedMethods.get(prop))
        return cachedMethods.get(prop);
    const targetFuncName = prop.replace(/FromIndex$/, '');
    const useIndex = prop !== targetFuncName;
    const isWrite = writeMethods.includes(targetFuncName);
    if (
    // Bail if the target doesn't exist on the target. Eg, getAll isn't in Edge.
    !(targetFuncName in (useIndex ? IDBIndex : IDBObjectStore).prototype) ||
        !(isWrite || readMethods.includes(targetFuncName))) {
        return;
    }
    const method = async function (storeName, ...args) {
        // isWrite ? 'readwrite' : undefined gzipps better, but fails in Edge :(
        const tx = this.transaction(storeName, isWrite ? 'readwrite' : 'readonly');
        let target = tx.store;
        if (useIndex)
            target = target.index(args.shift());
        // Must reject if op rejects.
        // If it's a write operation, must reject if tx.done rejects.
        // Must reject with op rejection first.
        // Must resolve with op value.
        // Must handle both promises (no unhandled rejections)
        return (await Promise.all([
            target[targetFuncName](...args),
            isWrite && tx.done,
        ]))[0];
    };
    cachedMethods.set(prop, method);
    return method;
}
replaceTraps((oldTraps) => ({
    ...oldTraps,
    get: (target, prop, receiver) => getMethod(target, prop) || oldTraps.get(target, prop, receiver),
    has: (target, prop) => !!getMethod(target, prop) || oldTraps.has(target, prop),
}));

/**
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
 */
class PlatformLoggerServiceImpl {
    constructor(container) {
        this.container = container;
    }
    // In initial implementation, this will be called by installations on
    // auth token refresh, and installations will send this string.
    getPlatformInfoString() {
        const providers = this.container.getProviders();
        // Loop through providers and get library/version pairs from any that are
        // version components.
        return providers
            .map(provider => {
            if (isVersionServiceProvider(provider)) {
                const service = provider.getImmediate();
                return `${service.library}/${service.version}`;
            }
            else {
                return null;
            }
        })
            .filter(logString => logString)
            .join(' ');
    }
}
/**
 *
 * @param provider check if this provider provides a VersionService
 *
 * NOTE: Using Provider<'app-version'> is a hack to indicate that the provider
 * provides VersionService. The provider is not necessarily a 'app-version'
 * provider.
 */
function isVersionServiceProvider(provider) {
    const component = provider.getComponent();
    return (component === null || component === void 0 ? void 0 : component.type) === "VERSION" /* ComponentType.VERSION */;
}

const name$o = "@firebase/app";
const version$1$1 = "0.10.1";

/**
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
 */
const logger = new Logger('@firebase/app');

const name$n = "@firebase/app-compat";

const name$m = "@firebase/analytics-compat";

const name$l = "@firebase/analytics";

const name$k = "@firebase/app-check-compat";

const name$j = "@firebase/app-check";

const name$i = "@firebase/auth";

const name$h = "@firebase/auth-compat";

const name$g = "@firebase/database";

const name$f = "@firebase/database-compat";

const name$e = "@firebase/functions";

const name$d = "@firebase/functions-compat";

const name$c = "@firebase/installations";

const name$b = "@firebase/installations-compat";

const name$a = "@firebase/messaging";

const name$9 = "@firebase/messaging-compat";

const name$8 = "@firebase/performance";

const name$7 = "@firebase/performance-compat";

const name$6 = "@firebase/remote-config";

const name$5 = "@firebase/remote-config-compat";

const name$4 = "@firebase/storage";

const name$3 = "@firebase/storage-compat";

const name$2 = "@firebase/firestore";

const name$1$1 = "@firebase/firestore-compat";

const name$p = "firebase";
const version$2 = "10.11.0";

/**
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
 */
/**
 * The default app name
 *
 * @internal
 */
const DEFAULT_ENTRY_NAME = '[DEFAULT]';
const PLATFORM_LOG_STRING = {
    [name$o]: 'fire-core',
    [name$n]: 'fire-core-compat',
    [name$l]: 'fire-analytics',
    [name$m]: 'fire-analytics-compat',
    [name$j]: 'fire-app-check',
    [name$k]: 'fire-app-check-compat',
    [name$i]: 'fire-auth',
    [name$h]: 'fire-auth-compat',
    [name$g]: 'fire-rtdb',
    [name$f]: 'fire-rtdb-compat',
    [name$e]: 'fire-fn',
    [name$d]: 'fire-fn-compat',
    [name$c]: 'fire-iid',
    [name$b]: 'fire-iid-compat',
    [name$a]: 'fire-fcm',
    [name$9]: 'fire-fcm-compat',
    [name$8]: 'fire-perf',
    [name$7]: 'fire-perf-compat',
    [name$6]: 'fire-rc',
    [name$5]: 'fire-rc-compat',
    [name$4]: 'fire-gcs',
    [name$3]: 'fire-gcs-compat',
    [name$2]: 'fire-fst',
    [name$1$1]: 'fire-fst-compat',
    'fire-js': 'fire-js',
    [name$p]: 'fire-js-all'
};

/**
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
 */
/**
 * @internal
 */
const _apps = new Map();
/**
 * @internal
 */
const _serverApps = new Map();
/**
 * Registered components.
 *
 * @internal
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const _components = new Map();
/**
 * @param component - the component being added to this app's container
 *
 * @internal
 */
function _addComponent(app, component) {
    try {
        app.container.addComponent(component);
    }
    catch (e) {
        logger.debug(`Component ${component.name} failed to register with FirebaseApp ${app.name}`, e);
    }
}
/**
 *
 * @param component - the component to register
 * @returns whether or not the component is registered successfully
 *
 * @internal
 */
function _registerComponent(component) {
    const componentName = component.name;
    if (_components.has(componentName)) {
        logger.debug(`There were multiple attempts to register component ${componentName}.`);
        return false;
    }
    _components.set(componentName, component);
    // add the component to existing app instances
    for (const app of _apps.values()) {
        _addComponent(app, component);
    }
    for (const serverApp of _serverApps.values()) {
        _addComponent(serverApp, component);
    }
    return true;
}
/**
 *
 * @param app - FirebaseApp instance
 * @param name - service name
 *
 * @returns the provider for the service with the matching name
 *
 * @internal
 */
function _getProvider(app, name) {
    const heartbeatController = app.container
        .getProvider('heartbeat')
        .getImmediate({ optional: true });
    if (heartbeatController) {
        void heartbeatController.triggerHeartbeat();
    }
    return app.container.getProvider(name);
}
/**
 *
 * @param obj - an object of type FirebaseApp.
 *
 * @returns true if the provided object is of type FirebaseServerAppImpl.
 *
 * @internal
 */
function _isFirebaseServerApp(obj) {
    return obj.settings !== undefined;
}

/**
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
 */
const ERRORS = {
    ["no-app" /* AppError.NO_APP */]: "No Firebase App '{$appName}' has been created - " +
        'call initializeApp() first',
    ["bad-app-name" /* AppError.BAD_APP_NAME */]: "Illegal App name: '{$appName}'",
    ["duplicate-app" /* AppError.DUPLICATE_APP */]: "Firebase App named '{$appName}' already exists with different options or config",
    ["app-deleted" /* AppError.APP_DELETED */]: "Firebase App named '{$appName}' already deleted",
    ["server-app-deleted" /* AppError.SERVER_APP_DELETED */]: 'Firebase Server App has been deleted',
    ["no-options" /* AppError.NO_OPTIONS */]: 'Need to provide options, when not being deployed to hosting via source.',
    ["invalid-app-argument" /* AppError.INVALID_APP_ARGUMENT */]: 'firebase.{$appName}() takes either no argument or a ' +
        'Firebase App instance.',
    ["invalid-log-argument" /* AppError.INVALID_LOG_ARGUMENT */]: 'First argument to `onLog` must be null or a function.',
    ["idb-open" /* AppError.IDB_OPEN */]: 'Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.',
    ["idb-get" /* AppError.IDB_GET */]: 'Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.',
    ["idb-set" /* AppError.IDB_WRITE */]: 'Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.',
    ["idb-delete" /* AppError.IDB_DELETE */]: 'Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.',
    ["finalization-registry-not-supported" /* AppError.FINALIZATION_REGISTRY_NOT_SUPPORTED */]: 'FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.',
    ["invalid-server-app-environment" /* AppError.INVALID_SERVER_APP_ENVIRONMENT */]: 'FirebaseServerApp is not for use in browser environments.'
};
const ERROR_FACTORY = new ErrorFactory('app', 'Firebase', ERRORS);

/**
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
 */
class FirebaseAppImpl {
    constructor(options, config, container) {
        this._isDeleted = false;
        this._options = Object.assign({}, options);
        this._config = Object.assign({}, config);
        this._name = config.name;
        this._automaticDataCollectionEnabled =
            config.automaticDataCollectionEnabled;
        this._container = container;
        this.container.addComponent(new Component('app', () => this, "PUBLIC" /* ComponentType.PUBLIC */));
    }
    get automaticDataCollectionEnabled() {
        this.checkDestroyed();
        return this._automaticDataCollectionEnabled;
    }
    set automaticDataCollectionEnabled(val) {
        this.checkDestroyed();
        this._automaticDataCollectionEnabled = val;
    }
    get name() {
        this.checkDestroyed();
        return this._name;
    }
    get options() {
        this.checkDestroyed();
        return this._options;
    }
    get config() {
        this.checkDestroyed();
        return this._config;
    }
    get container() {
        return this._container;
    }
    get isDeleted() {
        return this._isDeleted;
    }
    set isDeleted(val) {
        this._isDeleted = val;
    }
    /**
     * This function will throw an Error if the App has already been deleted -
     * use before performing API actions on the App.
     */
    checkDestroyed() {
        if (this.isDeleted) {
            throw ERROR_FACTORY.create("app-deleted" /* AppError.APP_DELETED */, { appName: this._name });
        }
    }
}

/**
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
 */
/**
 * The current SDK version.
 *
 * @public
 */
const SDK_VERSION = version$2;
function initializeApp(_options, rawConfig = {}) {
    let options = _options;
    if (typeof rawConfig !== 'object') {
        const name = rawConfig;
        rawConfig = { name };
    }
    const config = Object.assign({ name: DEFAULT_ENTRY_NAME, automaticDataCollectionEnabled: false }, rawConfig);
    const name = config.name;
    if (typeof name !== 'string' || !name) {
        throw ERROR_FACTORY.create("bad-app-name" /* AppError.BAD_APP_NAME */, {
            appName: String(name)
        });
    }
    options || (options = getDefaultAppConfig());
    if (!options) {
        throw ERROR_FACTORY.create("no-options" /* AppError.NO_OPTIONS */);
    }
    const existingApp = _apps.get(name);
    if (existingApp) {
        // return the existing app if options and config deep equal the ones in the existing app.
        if (deepEqual(options, existingApp.options) &&
            deepEqual(config, existingApp.config)) {
            return existingApp;
        }
        else {
            throw ERROR_FACTORY.create("duplicate-app" /* AppError.DUPLICATE_APP */, { appName: name });
        }
    }
    const container = new ComponentContainer(name);
    for (const component of _components.values()) {
        container.addComponent(component);
    }
    const newApp = new FirebaseAppImpl(options, config, container);
    _apps.set(name, newApp);
    return newApp;
}
/**
 * Retrieves a {@link @firebase/app#FirebaseApp} instance.
 *
 * When called with no arguments, the default app is returned. When an app name
 * is provided, the app corresponding to that name is returned.
 *
 * An exception is thrown if the app being retrieved has not yet been
 * initialized.
 *
 * @example
 * ```javascript
 * // Return the default app
 * const app = getApp();
 * ```
 *
 * @example
 * ```javascript
 * // Return a named app
 * const otherApp = getApp("otherApp");
 * ```
 *
 * @param name - Optional name of the app to return. If no name is
 *   provided, the default is `"[DEFAULT]"`.
 *
 * @returns The app corresponding to the provided app name.
 *   If no app name is provided, the default app is returned.
 *
 * @public
 */
function getApp(name = DEFAULT_ENTRY_NAME) {
    const app = _apps.get(name);
    if (!app && name === DEFAULT_ENTRY_NAME && getDefaultAppConfig()) {
        return initializeApp();
    }
    if (!app) {
        throw ERROR_FACTORY.create("no-app" /* AppError.NO_APP */, { appName: name });
    }
    return app;
}
/**
 * Registers a library's name and version for platform logging purposes.
 * @param library - Name of 1p or 3p library (e.g. firestore, angularfire)
 * @param version - Current version of that library.
 * @param variant - Bundle variant, e.g., node, rn, etc.
 *
 * @public
 */
function registerVersion(libraryKeyOrName, version, variant) {
    var _a;
    // TODO: We can use this check to whitelist strings when/if we set up
    // a good whitelist system.
    let library = (_a = PLATFORM_LOG_STRING[libraryKeyOrName]) !== null && _a !== void 0 ? _a : libraryKeyOrName;
    if (variant) {
        library += `-${variant}`;
    }
    const libraryMismatch = library.match(/\s|\//);
    const versionMismatch = version.match(/\s|\//);
    if (libraryMismatch || versionMismatch) {
        const warning = [
            `Unable to register library "${library}" with version "${version}":`
        ];
        if (libraryMismatch) {
            warning.push(`library name "${library}" contains illegal characters (whitespace or "/")`);
        }
        if (libraryMismatch && versionMismatch) {
            warning.push('and');
        }
        if (versionMismatch) {
            warning.push(`version name "${version}" contains illegal characters (whitespace or "/")`);
        }
        logger.warn(warning.join(' '));
        return;
    }
    _registerComponent(new Component(`${library}-version`, () => ({ library, version }), "VERSION" /* ComponentType.VERSION */));
}

/**
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
 */
const DB_NAME$1 = 'firebase-heartbeat-database';
const DB_VERSION$1 = 1;
const STORE_NAME = 'firebase-heartbeat-store';
let dbPromise = null;
function getDbPromise() {
    if (!dbPromise) {
        dbPromise = openDB(DB_NAME$1, DB_VERSION$1, {
            upgrade: (db, oldVersion) => {
                // We don't use 'break' in this switch statement, the fall-through
                // behavior is what we want, because if there are multiple versions between
                // the old version and the current version, we want ALL the migrations
                // that correspond to those versions to run, not only the last one.
                // eslint-disable-next-line default-case
                switch (oldVersion) {
                    case 0:
                        try {
                            db.createObjectStore(STORE_NAME);
                        }
                        catch (e) {
                            // Safari/iOS browsers throw occasional exceptions on
                            // db.createObjectStore() that may be a bug. Avoid blocking
                            // the rest of the app functionality.
                            console.warn(e);
                        }
                }
            }
        }).catch(e => {
            throw ERROR_FACTORY.create("idb-open" /* AppError.IDB_OPEN */, {
                originalErrorMessage: e.message
            });
        });
    }
    return dbPromise;
}
async function readHeartbeatsFromIndexedDB(app) {
    try {
        const db = await getDbPromise();
        const tx = db.transaction(STORE_NAME);
        const result = await tx.objectStore(STORE_NAME).get(computeKey(app));
        // We already have the value but tx.done can throw,
        // so we need to await it here to catch errors
        await tx.done;
        return result;
    }
    catch (e) {
        if (e instanceof FirebaseError) {
            logger.warn(e.message);
        }
        else {
            const idbGetError = ERROR_FACTORY.create("idb-get" /* AppError.IDB_GET */, {
                originalErrorMessage: e === null || e === void 0 ? void 0 : e.message
            });
            logger.warn(idbGetError.message);
        }
    }
}
async function writeHeartbeatsToIndexedDB(app, heartbeatObject) {
    try {
        const db = await getDbPromise();
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const objectStore = tx.objectStore(STORE_NAME);
        await objectStore.put(heartbeatObject, computeKey(app));
        await tx.done;
    }
    catch (e) {
        if (e instanceof FirebaseError) {
            logger.warn(e.message);
        }
        else {
            const idbGetError = ERROR_FACTORY.create("idb-set" /* AppError.IDB_WRITE */, {
                originalErrorMessage: e === null || e === void 0 ? void 0 : e.message
            });
            logger.warn(idbGetError.message);
        }
    }
}
function computeKey(app) {
    return `${app.name}!${app.options.appId}`;
}

/**
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
 */
const MAX_HEADER_BYTES = 1024;
// 30 days
const STORED_HEARTBEAT_RETENTION_MAX_MILLIS = 30 * 24 * 60 * 60 * 1000;
class HeartbeatServiceImpl {
    constructor(container) {
        this.container = container;
        /**
         * In-memory cache for heartbeats, used by getHeartbeatsHeader() to generate
         * the header string.
         * Stores one record per date. This will be consolidated into the standard
         * format of one record per user agent string before being sent as a header.
         * Populated from indexedDB when the controller is instantiated and should
         * be kept in sync with indexedDB.
         * Leave public for easier testing.
         */
        this._heartbeatsCache = null;
        const app = this.container.getProvider('app').getImmediate();
        this._storage = new HeartbeatStorageImpl(app);
        this._heartbeatsCachePromise = this._storage.read().then(result => {
            this._heartbeatsCache = result;
            return result;
        });
    }
    /**
     * Called to report a heartbeat. The function will generate
     * a HeartbeatsByUserAgent object, update heartbeatsCache, and persist it
     * to IndexedDB.
     * Note that we only store one heartbeat per day. So if a heartbeat for today is
     * already logged, subsequent calls to this function in the same day will be ignored.
     */
    async triggerHeartbeat() {
        var _a, _b;
        const platformLogger = this.container
            .getProvider('platform-logger')
            .getImmediate();
        // This is the "Firebase user agent" string from the platform logger
        // service, not the browser user agent.
        const agent = platformLogger.getPlatformInfoString();
        const date = getUTCDateString();
        if (((_a = this._heartbeatsCache) === null || _a === void 0 ? void 0 : _a.heartbeats) == null) {
            this._heartbeatsCache = await this._heartbeatsCachePromise;
            // If we failed to construct a heartbeats cache, then return immediately.
            if (((_b = this._heartbeatsCache) === null || _b === void 0 ? void 0 : _b.heartbeats) == null) {
                return;
            }
        }
        // Do not store a heartbeat if one is already stored for this day
        // or if a header has already been sent today.
        if (this._heartbeatsCache.lastSentHeartbeatDate === date ||
            this._heartbeatsCache.heartbeats.some(singleDateHeartbeat => singleDateHeartbeat.date === date)) {
            return;
        }
        else {
            // There is no entry for this date. Create one.
            this._heartbeatsCache.heartbeats.push({ date, agent });
        }
        // Remove entries older than 30 days.
        this._heartbeatsCache.heartbeats = this._heartbeatsCache.heartbeats.filter(singleDateHeartbeat => {
            const hbTimestamp = new Date(singleDateHeartbeat.date).valueOf();
            const now = Date.now();
            return now - hbTimestamp <= STORED_HEARTBEAT_RETENTION_MAX_MILLIS;
        });
        return this._storage.overwrite(this._heartbeatsCache);
    }
    /**
     * Returns a base64 encoded string which can be attached to the heartbeat-specific header directly.
     * It also clears all heartbeats from memory as well as in IndexedDB.
     *
     * NOTE: Consuming product SDKs should not send the header if this method
     * returns an empty string.
     */
    async getHeartbeatsHeader() {
        var _a;
        if (this._heartbeatsCache === null) {
            await this._heartbeatsCachePromise;
        }
        // If it's still null or the array is empty, there is no data to send.
        if (((_a = this._heartbeatsCache) === null || _a === void 0 ? void 0 : _a.heartbeats) == null ||
            this._heartbeatsCache.heartbeats.length === 0) {
            return '';
        }
        const date = getUTCDateString();
        // Extract as many heartbeats from the cache as will fit under the size limit.
        const { heartbeatsToSend, unsentEntries } = extractHeartbeatsForHeader(this._heartbeatsCache.heartbeats);
        const headerString = base64urlEncodeWithoutPadding(JSON.stringify({ version: 2, heartbeats: heartbeatsToSend }));
        // Store last sent date to prevent another being logged/sent for the same day.
        this._heartbeatsCache.lastSentHeartbeatDate = date;
        if (unsentEntries.length > 0) {
            // Store any unsent entries if they exist.
            this._heartbeatsCache.heartbeats = unsentEntries;
            // This seems more likely than emptying the array (below) to lead to some odd state
            // since the cache isn't empty and this will be called again on the next request,
            // and is probably safest if we await it.
            await this._storage.overwrite(this._heartbeatsCache);
        }
        else {
            this._heartbeatsCache.heartbeats = [];
            // Do not wait for this, to reduce latency.
            void this._storage.overwrite(this._heartbeatsCache);
        }
        return headerString;
    }
}
function getUTCDateString() {
    const today = new Date();
    // Returns date format 'YYYY-MM-DD'
    return today.toISOString().substring(0, 10);
}
function extractHeartbeatsForHeader(heartbeatsCache, maxSize = MAX_HEADER_BYTES) {
    // Heartbeats grouped by user agent in the standard format to be sent in
    // the header.
    const heartbeatsToSend = [];
    // Single date format heartbeats that are not sent.
    let unsentEntries = heartbeatsCache.slice();
    for (const singleDateHeartbeat of heartbeatsCache) {
        // Look for an existing entry with the same user agent.
        const heartbeatEntry = heartbeatsToSend.find(hb => hb.agent === singleDateHeartbeat.agent);
        if (!heartbeatEntry) {
            // If no entry for this user agent exists, create one.
            heartbeatsToSend.push({
                agent: singleDateHeartbeat.agent,
                dates: [singleDateHeartbeat.date]
            });
            if (countBytes(heartbeatsToSend) > maxSize) {
                // If the header would exceed max size, remove the added heartbeat
                // entry and stop adding to the header.
                heartbeatsToSend.pop();
                break;
            }
        }
        else {
            heartbeatEntry.dates.push(singleDateHeartbeat.date);
            // If the header would exceed max size, remove the added date
            // and stop adding to the header.
            if (countBytes(heartbeatsToSend) > maxSize) {
                heartbeatEntry.dates.pop();
                break;
            }
        }
        // Pop unsent entry from queue. (Skipped if adding the entry exceeded
        // quota and the loop breaks early.)
        unsentEntries = unsentEntries.slice(1);
    }
    return {
        heartbeatsToSend,
        unsentEntries
    };
}
class HeartbeatStorageImpl {
    constructor(app) {
        this.app = app;
        this._canUseIndexedDBPromise = this.runIndexedDBEnvironmentCheck();
    }
    async runIndexedDBEnvironmentCheck() {
        if (!isIndexedDBAvailable()) {
            return false;
        }
        else {
            return validateIndexedDBOpenable()
                .then(() => true)
                .catch(() => false);
        }
    }
    /**
     * Read all heartbeats.
     */
    async read() {
        const canUseIndexedDB = await this._canUseIndexedDBPromise;
        if (!canUseIndexedDB) {
            return { heartbeats: [] };
        }
        else {
            const idbHeartbeatObject = await readHeartbeatsFromIndexedDB(this.app);
            if (idbHeartbeatObject === null || idbHeartbeatObject === void 0 ? void 0 : idbHeartbeatObject.heartbeats) {
                return idbHeartbeatObject;
            }
            else {
                return { heartbeats: [] };
            }
        }
    }
    // overwrite the storage with the provided heartbeats
    async overwrite(heartbeatsObject) {
        var _a;
        const canUseIndexedDB = await this._canUseIndexedDBPromise;
        if (!canUseIndexedDB) {
            return;
        }
        else {
            const existingHeartbeatsObject = await this.read();
            return writeHeartbeatsToIndexedDB(this.app, {
                lastSentHeartbeatDate: (_a = heartbeatsObject.lastSentHeartbeatDate) !== null && _a !== void 0 ? _a : existingHeartbeatsObject.lastSentHeartbeatDate,
                heartbeats: heartbeatsObject.heartbeats
            });
        }
    }
    // add heartbeats
    async add(heartbeatsObject) {
        var _a;
        const canUseIndexedDB = await this._canUseIndexedDBPromise;
        if (!canUseIndexedDB) {
            return;
        }
        else {
            const existingHeartbeatsObject = await this.read();
            return writeHeartbeatsToIndexedDB(this.app, {
                lastSentHeartbeatDate: (_a = heartbeatsObject.lastSentHeartbeatDate) !== null && _a !== void 0 ? _a : existingHeartbeatsObject.lastSentHeartbeatDate,
                heartbeats: [
                    ...existingHeartbeatsObject.heartbeats,
                    ...heartbeatsObject.heartbeats
                ]
            });
        }
    }
}
/**
 * Calculate bytes of a HeartbeatsByUserAgent array after being wrapped
 * in a platform logging header JSON object, stringified, and converted
 * to base 64.
 */
function countBytes(heartbeatsCache) {
    // base64 has a restricted set of characters, all of which should be 1 byte.
    return base64urlEncodeWithoutPadding(
    // heartbeatsCache wrapper properties
    JSON.stringify({ version: 2, heartbeats: heartbeatsCache })).length;
}

/**
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
 */
function registerCoreComponents(variant) {
    _registerComponent(new Component('platform-logger', container => new PlatformLoggerServiceImpl(container), "PRIVATE" /* ComponentType.PRIVATE */));
    _registerComponent(new Component('heartbeat', container => new HeartbeatServiceImpl(container), "PRIVATE" /* ComponentType.PRIVATE */));
    // Register `app` package.
    registerVersion(name$o, version$1$1, variant);
    // BUILD_TARGET will be replaced by values like esm5, esm2017, cjs5, etc during the compilation
    registerVersion(name$o, version$1$1, 'esm2017');
    // Register platform SDK identifier (no version).
    registerVersion('fire-js', '');
}

/**
 * Firebase App
 *
 * @remarks This package coordinates the communication between the different Firebase components
 * @packageDocumentation
 */
registerCoreComponents('');

/******************************************************************************
Copyright (c) Microsoft Corporation.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
***************************************************************************** */
/* global Reflect, Promise */


function __rest(s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
}

function _prodErrorMap() {
    // We will include this one message in the prod error map since by the very
    // nature of this error, developers will never be able to see the message
    // using the debugErrorMap (which is installed during auth initialization).
    return {
        ["dependent-sdk-initialized-before-auth" /* AuthErrorCode.DEPENDENT_SDK_INIT_BEFORE_AUTH */]: 'Another Firebase SDK was initialized and is trying to use Auth before Auth is ' +
            'initialized. Please be sure to call `initializeAuth` or `getAuth` before ' +
            'starting any other Firebase SDK.'
    };
}
/**
 * A minimal error map with all verbose error messages stripped.
 *
 * See discussion at {@link AuthErrorMap}
 *
 * @public
 */
const prodErrorMap = _prodErrorMap;
const _DEFAULT_AUTH_ERROR_FACTORY = new ErrorFactory('auth', 'Firebase', _prodErrorMap());

/**
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
 */
const logClient = new Logger('@firebase/auth');
function _logWarn(msg, ...args) {
    if (logClient.logLevel <= LogLevel.WARN) {
        logClient.warn(`Auth (${SDK_VERSION}): ${msg}`, ...args);
    }
}
function _logError(msg, ...args) {
    if (logClient.logLevel <= LogLevel.ERROR) {
        logClient.error(`Auth (${SDK_VERSION}): ${msg}`, ...args);
    }
}

/**
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
 */
function _fail(authOrCode, ...rest) {
    throw createErrorInternal(authOrCode, ...rest);
}
function _createError(authOrCode, ...rest) {
    return createErrorInternal(authOrCode, ...rest);
}
function _errorWithCustomMessage(auth, code, message) {
    const errorMap = Object.assign(Object.assign({}, prodErrorMap()), { [code]: message });
    const factory = new ErrorFactory('auth', 'Firebase', errorMap);
    return factory.create(code, {
        appName: auth.name
    });
}
function _serverAppCurrentUserOperationNotSupportedError(auth) {
    return _errorWithCustomMessage(auth, "operation-not-supported-in-this-environment" /* AuthErrorCode.OPERATION_NOT_SUPPORTED */, 'Operations that alter the current user are not supported in conjunction with FirebaseServerApp');
}
function createErrorInternal(authOrCode, ...rest) {
    if (typeof authOrCode !== 'string') {
        const code = rest[0];
        const fullParams = [...rest.slice(1)];
        if (fullParams[0]) {
            fullParams[0].appName = authOrCode.name;
        }
        return authOrCode._errorFactory.create(code, ...fullParams);
    }
    return _DEFAULT_AUTH_ERROR_FACTORY.create(authOrCode, ...rest);
}
function _assert(assertion, authOrCode, ...rest) {
    if (!assertion) {
        throw createErrorInternal(authOrCode, ...rest);
    }
}
/**
 * Unconditionally fails, throwing an internal error with the given message.
 *
 * @param failure type of failure encountered
 * @throws Error
 */
function debugFail(failure) {
    // Log the failure in addition to throw an exception, just in case the
    // exception is swallowed.
    const message = `INTERNAL ASSERTION FAILED: ` + failure;
    _logError(message);
    // NOTE: We don't use FirebaseError here because these are internal failures
    // that cannot be handled by the user. (Also it would create a circular
    // dependency between the error and assert modules which doesn't work.)
    throw new Error(message);
}
/**
 * Fails if the given assertion condition is false, throwing an Error with the
 * given message if it did.
 *
 * @param assertion
 * @param message
 */
function debugAssert(assertion, message) {
    if (!assertion) {
        debugFail(message);
    }
}

/**
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
 */
function _getCurrentUrl() {
    var _a;
    return (typeof self !== 'undefined' && ((_a = self.location) === null || _a === void 0 ? void 0 : _a.href)) || '';
}
function _isHttpOrHttps() {
    return _getCurrentScheme() === 'http:' || _getCurrentScheme() === 'https:';
}
function _getCurrentScheme() {
    var _a;
    return (typeof self !== 'undefined' && ((_a = self.location) === null || _a === void 0 ? void 0 : _a.protocol)) || null;
}

/**
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
 */
/**
 * Determine whether the browser is working online
 */
function _isOnline() {
    if (typeof navigator !== 'undefined' &&
        navigator &&
        'onLine' in navigator &&
        typeof navigator.onLine === 'boolean' &&
        // Apply only for traditional web apps and Chrome extensions.
        // This is especially true for Cordova apps which have unreliable
        // navigator.onLine behavior unless cordova-plugin-network-information is
        // installed which overwrites the native navigator.onLine value and
        // defines navigator.connection.
        (_isHttpOrHttps() || isBrowserExtension() || 'connection' in navigator)) {
        return navigator.onLine;
    }
    // If we can't determine the state, assume it is online.
    return true;
}
function _getUserLanguage() {
    if (typeof navigator === 'undefined') {
        return null;
    }
    const navigatorLanguage = navigator;
    return (
    // Most reliable, but only supported in Chrome/Firefox.
    (navigatorLanguage.languages && navigatorLanguage.languages[0]) ||
        // Supported in most browsers, but returns the language of the browser
        // UI, not the language set in browser settings.
        navigatorLanguage.language ||
        // Couldn't determine language.
        null);
}

/**
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
 */
/**
 * A structure to help pick between a range of long and short delay durations
 * depending on the current environment. In general, the long delay is used for
 * mobile environments whereas short delays are used for desktop environments.
 */
class Delay {
    constructor(shortDelay, longDelay) {
        this.shortDelay = shortDelay;
        this.longDelay = longDelay;
        // Internal error when improperly initialized.
        debugAssert(longDelay > shortDelay, 'Short delay should be less than long delay!');
        this.isMobile = isMobileCordova() || isReactNative();
    }
    get() {
        if (!_isOnline()) {
            // Pick the shorter timeout.
            return Math.min(5000 /* DelayMin.OFFLINE */, this.shortDelay);
        }
        // If running in a mobile environment, return the long delay, otherwise
        // return the short delay.
        // This could be improved in the future to dynamically change based on other
        // variables instead of just reading the current environment.
        return this.isMobile ? this.longDelay : this.shortDelay;
    }
}

/**
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
 */
function _emulatorUrl(config, path) {
    debugAssert(config.emulator, 'Emulator should always be set here');
    const { url } = config.emulator;
    if (!path) {
        return url;
    }
    return `${url}${path.startsWith('/') ? path.slice(1) : path}`;
}

/**
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
 */
class FetchProvider {
    static initialize(fetchImpl, headersImpl, responseImpl) {
        this.fetchImpl = fetchImpl;
        if (headersImpl) {
            this.headersImpl = headersImpl;
        }
        if (responseImpl) {
            this.responseImpl = responseImpl;
        }
    }
    static fetch() {
        if (this.fetchImpl) {
            return this.fetchImpl;
        }
        if (typeof self !== 'undefined' && 'fetch' in self) {
            return self.fetch;
        }
        if (typeof globalThis !== 'undefined' && globalThis.fetch) {
            return globalThis.fetch;
        }
        if (typeof fetch !== 'undefined') {
            return fetch;
        }
        debugFail('Could not find fetch implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill');
    }
    static headers() {
        if (this.headersImpl) {
            return this.headersImpl;
        }
        if (typeof self !== 'undefined' && 'Headers' in self) {
            return self.Headers;
        }
        if (typeof globalThis !== 'undefined' && globalThis.Headers) {
            return globalThis.Headers;
        }
        if (typeof Headers !== 'undefined') {
            return Headers;
        }
        debugFail('Could not find Headers implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill');
    }
    static response() {
        if (this.responseImpl) {
            return this.responseImpl;
        }
        if (typeof self !== 'undefined' && 'Response' in self) {
            return self.Response;
        }
        if (typeof globalThis !== 'undefined' && globalThis.Response) {
            return globalThis.Response;
        }
        if (typeof Response !== 'undefined') {
            return Response;
        }
        debugFail('Could not find Response implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill');
    }
}

/**
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
 */
/**
 * Map from errors returned by the server to errors to developer visible errors
 */
const SERVER_ERROR_MAP = {
    // Custom token errors.
    ["CREDENTIAL_MISMATCH" /* ServerError.CREDENTIAL_MISMATCH */]: "custom-token-mismatch" /* AuthErrorCode.CREDENTIAL_MISMATCH */,
    // This can only happen if the SDK sends a bad request.
    ["MISSING_CUSTOM_TOKEN" /* ServerError.MISSING_CUSTOM_TOKEN */]: "internal-error" /* AuthErrorCode.INTERNAL_ERROR */,
    // Create Auth URI errors.
    ["INVALID_IDENTIFIER" /* ServerError.INVALID_IDENTIFIER */]: "invalid-email" /* AuthErrorCode.INVALID_EMAIL */,
    // This can only happen if the SDK sends a bad request.
    ["MISSING_CONTINUE_URI" /* ServerError.MISSING_CONTINUE_URI */]: "internal-error" /* AuthErrorCode.INTERNAL_ERROR */,
    // Sign in with email and password errors (some apply to sign up too).
    ["INVALID_PASSWORD" /* ServerError.INVALID_PASSWORD */]: "wrong-password" /* AuthErrorCode.INVALID_PASSWORD */,
    // This can only happen if the SDK sends a bad request.
    ["MISSING_PASSWORD" /* ServerError.MISSING_PASSWORD */]: "missing-password" /* AuthErrorCode.MISSING_PASSWORD */,
    // Thrown if Email Enumeration Protection is enabled in the project and the email or password is
    // invalid.
    ["INVALID_LOGIN_CREDENTIALS" /* ServerError.INVALID_LOGIN_CREDENTIALS */]: "invalid-credential" /* AuthErrorCode.INVALID_CREDENTIAL */,
    // Sign up with email and password errors.
    ["EMAIL_EXISTS" /* ServerError.EMAIL_EXISTS */]: "email-already-in-use" /* AuthErrorCode.EMAIL_EXISTS */,
    ["PASSWORD_LOGIN_DISABLED" /* ServerError.PASSWORD_LOGIN_DISABLED */]: "operation-not-allowed" /* AuthErrorCode.OPERATION_NOT_ALLOWED */,
    // Verify assertion for sign in with credential errors:
    ["INVALID_IDP_RESPONSE" /* ServerError.INVALID_IDP_RESPONSE */]: "invalid-credential" /* AuthErrorCode.INVALID_CREDENTIAL */,
    ["INVALID_PENDING_TOKEN" /* ServerError.INVALID_PENDING_TOKEN */]: "invalid-credential" /* AuthErrorCode.INVALID_CREDENTIAL */,
    ["FEDERATED_USER_ID_ALREADY_LINKED" /* ServerError.FEDERATED_USER_ID_ALREADY_LINKED */]: "credential-already-in-use" /* AuthErrorCode.CREDENTIAL_ALREADY_IN_USE */,
    // This can only happen if the SDK sends a bad request.
    ["MISSING_REQ_TYPE" /* ServerError.MISSING_REQ_TYPE */]: "internal-error" /* AuthErrorCode.INTERNAL_ERROR */,
    // Send Password reset email errors:
    ["EMAIL_NOT_FOUND" /* ServerError.EMAIL_NOT_FOUND */]: "user-not-found" /* AuthErrorCode.USER_DELETED */,
    ["RESET_PASSWORD_EXCEED_LIMIT" /* ServerError.RESET_PASSWORD_EXCEED_LIMIT */]: "too-many-requests" /* AuthErrorCode.TOO_MANY_ATTEMPTS_TRY_LATER */,
    ["EXPIRED_OOB_CODE" /* ServerError.EXPIRED_OOB_CODE */]: "expired-action-code" /* AuthErrorCode.EXPIRED_OOB_CODE */,
    ["INVALID_OOB_CODE" /* ServerError.INVALID_OOB_CODE */]: "invalid-action-code" /* AuthErrorCode.INVALID_OOB_CODE */,
    // This can only happen if the SDK sends a bad request.
    ["MISSING_OOB_CODE" /* ServerError.MISSING_OOB_CODE */]: "internal-error" /* AuthErrorCode.INTERNAL_ERROR */,
    // Operations that require ID token in request:
    ["CREDENTIAL_TOO_OLD_LOGIN_AGAIN" /* ServerError.CREDENTIAL_TOO_OLD_LOGIN_AGAIN */]: "requires-recent-login" /* AuthErrorCode.CREDENTIAL_TOO_OLD_LOGIN_AGAIN */,
    ["INVALID_ID_TOKEN" /* ServerError.INVALID_ID_TOKEN */]: "invalid-user-token" /* AuthErrorCode.INVALID_AUTH */,
    ["TOKEN_EXPIRED" /* ServerError.TOKEN_EXPIRED */]: "user-token-expired" /* AuthErrorCode.TOKEN_EXPIRED */,
    ["USER_NOT_FOUND" /* ServerError.USER_NOT_FOUND */]: "user-token-expired" /* AuthErrorCode.TOKEN_EXPIRED */,
    // Other errors.
    ["TOO_MANY_ATTEMPTS_TRY_LATER" /* ServerError.TOO_MANY_ATTEMPTS_TRY_LATER */]: "too-many-requests" /* AuthErrorCode.TOO_MANY_ATTEMPTS_TRY_LATER */,
    ["PASSWORD_DOES_NOT_MEET_REQUIREMENTS" /* ServerError.PASSWORD_DOES_NOT_MEET_REQUIREMENTS */]: "password-does-not-meet-requirements" /* AuthErrorCode.PASSWORD_DOES_NOT_MEET_REQUIREMENTS */,
    // Phone Auth related errors.
    ["INVALID_CODE" /* ServerError.INVALID_CODE */]: "invalid-verification-code" /* AuthErrorCode.INVALID_CODE */,
    ["INVALID_SESSION_INFO" /* ServerError.INVALID_SESSION_INFO */]: "invalid-verification-id" /* AuthErrorCode.INVALID_SESSION_INFO */,
    ["INVALID_TEMPORARY_PROOF" /* ServerError.INVALID_TEMPORARY_PROOF */]: "invalid-credential" /* AuthErrorCode.INVALID_CREDENTIAL */,
    ["MISSING_SESSION_INFO" /* ServerError.MISSING_SESSION_INFO */]: "missing-verification-id" /* AuthErrorCode.MISSING_SESSION_INFO */,
    ["SESSION_EXPIRED" /* ServerError.SESSION_EXPIRED */]: "code-expired" /* AuthErrorCode.CODE_EXPIRED */,
    // Other action code errors when additional settings passed.
    // MISSING_CONTINUE_URI is getting mapped to INTERNAL_ERROR above.
    // This is OK as this error will be caught by client side validation.
    ["MISSING_ANDROID_PACKAGE_NAME" /* ServerError.MISSING_ANDROID_PACKAGE_NAME */]: "missing-android-pkg-name" /* AuthErrorCode.MISSING_ANDROID_PACKAGE_NAME */,
    ["UNAUTHORIZED_DOMAIN" /* ServerError.UNAUTHORIZED_DOMAIN */]: "unauthorized-continue-uri" /* AuthErrorCode.UNAUTHORIZED_DOMAIN */,
    // getProjectConfig errors when clientId is passed.
    ["INVALID_OAUTH_CLIENT_ID" /* ServerError.INVALID_OAUTH_CLIENT_ID */]: "invalid-oauth-client-id" /* AuthErrorCode.INVALID_OAUTH_CLIENT_ID */,
    // User actions (sign-up or deletion) disabled errors.
    ["ADMIN_ONLY_OPERATION" /* ServerError.ADMIN_ONLY_OPERATION */]: "admin-restricted-operation" /* AuthErrorCode.ADMIN_ONLY_OPERATION */,
    // Multi factor related errors.
    ["INVALID_MFA_PENDING_CREDENTIAL" /* ServerError.INVALID_MFA_PENDING_CREDENTIAL */]: "invalid-multi-factor-session" /* AuthErrorCode.INVALID_MFA_SESSION */,
    ["MFA_ENROLLMENT_NOT_FOUND" /* ServerError.MFA_ENROLLMENT_NOT_FOUND */]: "multi-factor-info-not-found" /* AuthErrorCode.MFA_INFO_NOT_FOUND */,
    ["MISSING_MFA_ENROLLMENT_ID" /* ServerError.MISSING_MFA_ENROLLMENT_ID */]: "missing-multi-factor-info" /* AuthErrorCode.MISSING_MFA_INFO */,
    ["MISSING_MFA_PENDING_CREDENTIAL" /* ServerError.MISSING_MFA_PENDING_CREDENTIAL */]: "missing-multi-factor-session" /* AuthErrorCode.MISSING_MFA_SESSION */,
    ["SECOND_FACTOR_EXISTS" /* ServerError.SECOND_FACTOR_EXISTS */]: "second-factor-already-in-use" /* AuthErrorCode.SECOND_FACTOR_ALREADY_ENROLLED */,
    ["SECOND_FACTOR_LIMIT_EXCEEDED" /* ServerError.SECOND_FACTOR_LIMIT_EXCEEDED */]: "maximum-second-factor-count-exceeded" /* AuthErrorCode.SECOND_FACTOR_LIMIT_EXCEEDED */,
    // Blocking functions related errors.
    ["BLOCKING_FUNCTION_ERROR_RESPONSE" /* ServerError.BLOCKING_FUNCTION_ERROR_RESPONSE */]: "internal-error" /* AuthErrorCode.INTERNAL_ERROR */,
    // Recaptcha related errors.
    ["RECAPTCHA_NOT_ENABLED" /* ServerError.RECAPTCHA_NOT_ENABLED */]: "recaptcha-not-enabled" /* AuthErrorCode.RECAPTCHA_NOT_ENABLED */,
    ["MISSING_RECAPTCHA_TOKEN" /* ServerError.MISSING_RECAPTCHA_TOKEN */]: "missing-recaptcha-token" /* AuthErrorCode.MISSING_RECAPTCHA_TOKEN */,
    ["INVALID_RECAPTCHA_TOKEN" /* ServerError.INVALID_RECAPTCHA_TOKEN */]: "invalid-recaptcha-token" /* AuthErrorCode.INVALID_RECAPTCHA_TOKEN */,
    ["INVALID_RECAPTCHA_ACTION" /* ServerError.INVALID_RECAPTCHA_ACTION */]: "invalid-recaptcha-action" /* AuthErrorCode.INVALID_RECAPTCHA_ACTION */,
    ["MISSING_CLIENT_TYPE" /* ServerError.MISSING_CLIENT_TYPE */]: "missing-client-type" /* AuthErrorCode.MISSING_CLIENT_TYPE */,
    ["MISSING_RECAPTCHA_VERSION" /* ServerError.MISSING_RECAPTCHA_VERSION */]: "missing-recaptcha-version" /* AuthErrorCode.MISSING_RECAPTCHA_VERSION */,
    ["INVALID_RECAPTCHA_VERSION" /* ServerError.INVALID_RECAPTCHA_VERSION */]: "invalid-recaptcha-version" /* AuthErrorCode.INVALID_RECAPTCHA_VERSION */,
    ["INVALID_REQ_TYPE" /* ServerError.INVALID_REQ_TYPE */]: "invalid-req-type" /* AuthErrorCode.INVALID_REQ_TYPE */
};

/**
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
 */
const DEFAULT_API_TIMEOUT_MS = new Delay(30000, 60000);
function _addTidIfNecessary(auth, request) {
    if (auth.tenantId && !request.tenantId) {
        return Object.assign(Object.assign({}, request), { tenantId: auth.tenantId });
    }
    return request;
}
async function _performApiRequest(auth, method, path, request, customErrorMap = {}) {
    return _performFetchWithErrorHandling(auth, customErrorMap, async () => {
        let body = {};
        let params = {};
        if (request) {
            if (method === "GET" /* HttpMethod.GET */) {
                params = request;
            }
            else {
                body = {
                    body: JSON.stringify(request)
                };
            }
        }
        const query = querystring(Object.assign({ key: auth.config.apiKey }, params)).slice(1);
        const headers = await auth._getAdditionalHeaders();
        headers["Content-Type" /* HttpHeader.CONTENT_TYPE */] = 'application/json';
        if (auth.languageCode) {
            headers["X-Firebase-Locale" /* HttpHeader.X_FIREBASE_LOCALE */] = auth.languageCode;
        }
        return FetchProvider.fetch()(_getFinalTarget(auth, auth.config.apiHost, path, query), Object.assign({ method,
            headers, referrerPolicy: 'no-referrer' }, body));
    });
}
async function _performFetchWithErrorHandling(auth, customErrorMap, fetchFn) {
    auth._canInitEmulator = false;
    const errorMap = Object.assign(Object.assign({}, SERVER_ERROR_MAP), customErrorMap);
    try {
        const networkTimeout = new NetworkTimeout(auth);
        const response = await Promise.race([
            fetchFn(),
            networkTimeout.promise
        ]);
        // If we've reached this point, the fetch succeeded and the networkTimeout
        // didn't throw; clear the network timeout delay so that Node won't hang
        networkTimeout.clearNetworkTimeout();
        const json = await response.json();
        if ('needConfirmation' in json) {
            throw _makeTaggedError(auth, "account-exists-with-different-credential" /* AuthErrorCode.NEED_CONFIRMATION */, json);
        }
        if (response.ok && !('errorMessage' in json)) {
            return json;
        }
        else {
            const errorMessage = response.ok ? json.errorMessage : json.error.message;
            const [serverErrorCode, serverErrorMessage] = errorMessage.split(' : ');
            if (serverErrorCode === "FEDERATED_USER_ID_ALREADY_LINKED" /* ServerError.FEDERATED_USER_ID_ALREADY_LINKED */) {
                throw _makeTaggedError(auth, "credential-already-in-use" /* AuthErrorCode.CREDENTIAL_ALREADY_IN_USE */, json);
            }
            else if (serverErrorCode === "EMAIL_EXISTS" /* ServerError.EMAIL_EXISTS */) {
                throw _makeTaggedError(auth, "email-already-in-use" /* AuthErrorCode.EMAIL_EXISTS */, json);
            }
            else if (serverErrorCode === "USER_DISABLED" /* ServerError.USER_DISABLED */) {
                throw _makeTaggedError(auth, "user-disabled" /* AuthErrorCode.USER_DISABLED */, json);
            }
            const authError = errorMap[serverErrorCode] ||
                serverErrorCode
                    .toLowerCase()
                    .replace(/[_\s]+/g, '-');
            if (serverErrorMessage) {
                throw _errorWithCustomMessage(auth, authError, serverErrorMessage);
            }
            else {
                _fail(auth, authError);
            }
        }
    }
    catch (e) {
        if (e instanceof FirebaseError) {
            throw e;
        }
        // Changing this to a different error code will log user out when there is a network error
        // because we treat any error other than NETWORK_REQUEST_FAILED as token is invalid.
        // https://github.com/firebase/firebase-js-sdk/blob/4fbc73610d70be4e0852e7de63a39cb7897e8546/packages/auth/src/core/auth/auth_impl.ts#L309-L316
        _fail(auth, "network-request-failed" /* AuthErrorCode.NETWORK_REQUEST_FAILED */, { 'message': String(e) });
    }
}
async function _performSignInRequest(auth, method, path, request, customErrorMap = {}) {
    const serverResponse = (await _performApiRequest(auth, method, path, request, customErrorMap));
    if ('mfaPendingCredential' in serverResponse) {
        _fail(auth, "multi-factor-auth-required" /* AuthErrorCode.MFA_REQUIRED */, {
            _serverResponse: serverResponse
        });
    }
    return serverResponse;
}
function _getFinalTarget(auth, host, path, query) {
    const base = `${host}${path}?${query}`;
    if (!auth.config.emulator) {
        return `${auth.config.apiScheme}://${base}`;
    }
    return _emulatorUrl(auth.config, base);
}
function _parseEnforcementState(enforcementStateStr) {
    switch (enforcementStateStr) {
        case 'ENFORCE':
            return "ENFORCE" /* EnforcementState.ENFORCE */;
        case 'AUDIT':
            return "AUDIT" /* EnforcementState.AUDIT */;
        case 'OFF':
            return "OFF" /* EnforcementState.OFF */;
        default:
            return "ENFORCEMENT_STATE_UNSPECIFIED" /* EnforcementState.ENFORCEMENT_STATE_UNSPECIFIED */;
    }
}
class NetworkTimeout {
    constructor(auth) {
        this.auth = auth;
        // Node timers and browser timers are fundamentally incompatible, but we
        // don't care about the value here
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        this.timer = null;
        this.promise = new Promise((_, reject) => {
            this.timer = setTimeout(() => {
                return reject(_createError(this.auth, "network-request-failed" /* AuthErrorCode.NETWORK_REQUEST_FAILED */));
            }, DEFAULT_API_TIMEOUT_MS.get());
        });
    }
    clearNetworkTimeout() {
        clearTimeout(this.timer);
    }
}
function _makeTaggedError(auth, code, response) {
    const errorParams = {
        appName: auth.name
    };
    if (response.email) {
        errorParams.email = response.email;
    }
    if (response.phoneNumber) {
        errorParams.phoneNumber = response.phoneNumber;
    }
    const error = _createError(auth, code, errorParams);
    // We know customData is defined on error because errorParams is defined
    error.customData._tokenResponse = response;
    return error;
}
function isEnterprise(grecaptcha) {
    return (grecaptcha !== undefined &&
        grecaptcha.enterprise !== undefined);
}
class RecaptchaConfig {
    constructor(response) {
        /**
         * The reCAPTCHA site key.
         */
        this.siteKey = '';
        /**
         * The list of providers and their enablement status for reCAPTCHA Enterprise.
         */
        this.recaptchaEnforcementState = [];
        if (response.recaptchaKey === undefined) {
            throw new Error('recaptchaKey undefined');
        }
        // Example response.recaptchaKey: "projects/proj123/keys/sitekey123"
        this.siteKey = response.recaptchaKey.split('/')[3];
        this.recaptchaEnforcementState = response.recaptchaEnforcementState;
    }
    /**
     * Returns the reCAPTCHA Enterprise enforcement state for the given provider.
     *
     * @param providerStr - The provider whose enforcement state is to be returned.
     * @returns The reCAPTCHA Enterprise enforcement state for the given provider.
     */
    getProviderEnforcementState(providerStr) {
        if (!this.recaptchaEnforcementState ||
            this.recaptchaEnforcementState.length === 0) {
            return null;
        }
        for (const recaptchaEnforcementState of this.recaptchaEnforcementState) {
            if (recaptchaEnforcementState.provider &&
                recaptchaEnforcementState.provider === providerStr) {
                return _parseEnforcementState(recaptchaEnforcementState.enforcementState);
            }
        }
        return null;
    }
    /**
     * Returns true if the reCAPTCHA Enterprise enforcement state for the provider is set to ENFORCE or AUDIT.
     *
     * @param providerStr - The provider whose enablement state is to be returned.
     * @returns Whether or not reCAPTCHA Enterprise protection is enabled for the given provider.
     */
    isProviderEnabled(providerStr) {
        return (this.getProviderEnforcementState(providerStr) ===
            "ENFORCE" /* EnforcementState.ENFORCE */ ||
            this.getProviderEnforcementState(providerStr) === "AUDIT" /* EnforcementState.AUDIT */);
    }
}
async function getRecaptchaConfig(auth, request) {
    return _performApiRequest(auth, "GET" /* HttpMethod.GET */, "/v2/recaptchaConfig" /* Endpoint.GET_RECAPTCHA_CONFIG */, _addTidIfNecessary(auth, request));
}

/**
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
 */
async function deleteAccount(auth, request) {
    return _performApiRequest(auth, "POST" /* HttpMethod.POST */, "/v1/accounts:delete" /* Endpoint.DELETE_ACCOUNT */, request);
}
async function getAccountInfo(auth, request) {
    return _performApiRequest(auth, "POST" /* HttpMethod.POST */, "/v1/accounts:lookup" /* Endpoint.GET_ACCOUNT_INFO */, request);
}

/**
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
 */
function utcTimestampToDateString(utcTimestamp) {
    if (!utcTimestamp) {
        return undefined;
    }
    try {
        // Convert to date object.
        const date = new Date(Number(utcTimestamp));
        // Test date is valid.
        if (!isNaN(date.getTime())) {
            // Convert to UTC date string.
            return date.toUTCString();
        }
    }
    catch (e) {
        // Do nothing. undefined will be returned.
    }
    return undefined;
}
/**
 * Returns a deserialized JSON Web Token (JWT) used to identify the user to a Firebase service.
 *
 * @remarks
 * Returns the current token if it has not expired or if it will not expire in the next five
 * minutes. Otherwise, this will refresh the token and return a new one.
 *
 * @param user - The user.
 * @param forceRefresh - Force refresh regardless of token expiration.
 *
 * @public
 */
async function getIdTokenResult(user, forceRefresh = false) {
    const userInternal = getModularInstance(user);
    const token = await userInternal.getIdToken(forceRefresh);
    const claims = _parseToken(token);
    _assert(claims && claims.exp && claims.auth_time && claims.iat, userInternal.auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
    const firebase = typeof claims.firebase === 'object' ? claims.firebase : undefined;
    const signInProvider = firebase === null || firebase === void 0 ? void 0 : firebase['sign_in_provider'];
    return {
        claims,
        token,
        authTime: utcTimestampToDateString(secondsStringToMilliseconds(claims.auth_time)),
        issuedAtTime: utcTimestampToDateString(secondsStringToMilliseconds(claims.iat)),
        expirationTime: utcTimestampToDateString(secondsStringToMilliseconds(claims.exp)),
        signInProvider: signInProvider || null,
        signInSecondFactor: (firebase === null || firebase === void 0 ? void 0 : firebase['sign_in_second_factor']) || null
    };
}
function secondsStringToMilliseconds(seconds) {
    return Number(seconds) * 1000;
}
function _parseToken(token) {
    const [algorithm, payload, signature] = token.split('.');
    if (algorithm === undefined ||
        payload === undefined ||
        signature === undefined) {
        _logError('JWT malformed, contained fewer than 3 sections');
        return null;
    }
    try {
        const decoded = base64Decode(payload);
        if (!decoded) {
            _logError('Failed to decode base64 JWT payload');
            return null;
        }
        return JSON.parse(decoded);
    }
    catch (e) {
        _logError('Caught error parsing JWT payload as JSON', e === null || e === void 0 ? void 0 : e.toString());
        return null;
    }
}
/**
 * Extract expiresIn TTL from a token by subtracting the expiration from the issuance.
 */
function _tokenExpiresIn(token) {
    const parsedToken = _parseToken(token);
    _assert(parsedToken, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
    _assert(typeof parsedToken.exp !== 'undefined', "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
    _assert(typeof parsedToken.iat !== 'undefined', "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
    return Number(parsedToken.exp) - Number(parsedToken.iat);
}

/**
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
 */
async function _logoutIfInvalidated(user, promise, bypassAuthState = false) {
    if (bypassAuthState) {
        return promise;
    }
    try {
        return await promise;
    }
    catch (e) {
        if (e instanceof FirebaseError && isUserInvalidated(e)) {
            if (user.auth.currentUser === user) {
                await user.auth.signOut();
            }
        }
        throw e;
    }
}
function isUserInvalidated({ code }) {
    return (code === `auth/${"user-disabled" /* AuthErrorCode.USER_DISABLED */}` ||
        code === `auth/${"user-token-expired" /* AuthErrorCode.TOKEN_EXPIRED */}`);
}

/**
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
 */
class ProactiveRefresh {
    constructor(user) {
        this.user = user;
        this.isRunning = false;
        // Node timers and browser timers return fundamentally different types.
        // We don't actually care what the value is but TS won't accept unknown and
        // we can't cast properly in both environments.
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        this.timerId = null;
        this.errorBackoff = 30000 /* Duration.RETRY_BACKOFF_MIN */;
    }
    _start() {
        if (this.isRunning) {
            return;
        }
        this.isRunning = true;
        this.schedule();
    }
    _stop() {
        if (!this.isRunning) {
            return;
        }
        this.isRunning = false;
        if (this.timerId !== null) {
            clearTimeout(this.timerId);
        }
    }
    getInterval(wasError) {
        var _a;
        if (wasError) {
            const interval = this.errorBackoff;
            this.errorBackoff = Math.min(this.errorBackoff * 2, 960000 /* Duration.RETRY_BACKOFF_MAX */);
            return interval;
        }
        else {
            // Reset the error backoff
            this.errorBackoff = 30000 /* Duration.RETRY_BACKOFF_MIN */;
            const expTime = (_a = this.user.stsTokenManager.expirationTime) !== null && _a !== void 0 ? _a : 0;
            const interval = expTime - Date.now() - 300000 /* Duration.OFFSET */;
            return Math.max(0, interval);
        }
    }
    schedule(wasError = false) {
        if (!this.isRunning) {
            // Just in case...
            return;
        }
        const interval = this.getInterval(wasError);
        this.timerId = setTimeout(async () => {
            await this.iteration();
        }, interval);
    }
    async iteration() {
        try {
            await this.user.getIdToken(true);
        }
        catch (e) {
            // Only retry on network errors
            if ((e === null || e === void 0 ? void 0 : e.code) ===
                `auth/${"network-request-failed" /* AuthErrorCode.NETWORK_REQUEST_FAILED */}`) {
                this.schedule(/* wasError */ true);
            }
            return;
        }
        this.schedule();
    }
}

/**
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
 */
class UserMetadata {
    constructor(createdAt, lastLoginAt) {
        this.createdAt = createdAt;
        this.lastLoginAt = lastLoginAt;
        this._initializeTime();
    }
    _initializeTime() {
        this.lastSignInTime = utcTimestampToDateString(this.lastLoginAt);
        this.creationTime = utcTimestampToDateString(this.createdAt);
    }
    _copy(metadata) {
        this.createdAt = metadata.createdAt;
        this.lastLoginAt = metadata.lastLoginAt;
        this._initializeTime();
    }
    toJSON() {
        return {
            createdAt: this.createdAt,
            lastLoginAt: this.lastLoginAt
        };
    }
}

/**
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
 */
async function _reloadWithoutSaving(user) {
    var _a;
    const auth = user.auth;
    const idToken = await user.getIdToken();
    const response = await _logoutIfInvalidated(user, getAccountInfo(auth, { idToken }));
    _assert(response === null || response === void 0 ? void 0 : response.users.length, auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
    const coreAccount = response.users[0];
    user._notifyReloadListener(coreAccount);
    const newProviderData = ((_a = coreAccount.providerUserInfo) === null || _a === void 0 ? void 0 : _a.length)
        ? extractProviderData(coreAccount.providerUserInfo)
        : [];
    const providerData = mergeProviderData(user.providerData, newProviderData);
    // Preserves the non-nonymous status of the stored user, even if no more
    // credentials (federated or email/password) are linked to the user. If
    // the user was previously anonymous, then use provider data to update.
    // On the other hand, if it was not anonymous before, it should never be
    // considered anonymous now.
    const oldIsAnonymous = user.isAnonymous;
    const newIsAnonymous = !(user.email && coreAccount.passwordHash) && !(providerData === null || providerData === void 0 ? void 0 : providerData.length);
    const isAnonymous = !oldIsAnonymous ? false : newIsAnonymous;
    const updates = {
        uid: coreAccount.localId,
        displayName: coreAccount.displayName || null,
        photoURL: coreAccount.photoUrl || null,
        email: coreAccount.email || null,
        emailVerified: coreAccount.emailVerified || false,
        phoneNumber: coreAccount.phoneNumber || null,
        tenantId: coreAccount.tenantId || null,
        providerData,
        metadata: new UserMetadata(coreAccount.createdAt, coreAccount.lastLoginAt),
        isAnonymous
    };
    Object.assign(user, updates);
}
/**
 * Reloads user account data, if signed in.
 *
 * @param user - The user.
 *
 * @public
 */
async function reload(user) {
    const userInternal = getModularInstance(user);
    await _reloadWithoutSaving(userInternal);
    // Even though the current user hasn't changed, update
    // current user will trigger a persistence update w/ the
    // new info.
    await userInternal.auth._persistUserIfCurrent(userInternal);
    userInternal.auth._notifyListenersIfCurrent(userInternal);
}
function mergeProviderData(original, newData) {
    const deduped = original.filter(o => !newData.some(n => n.providerId === o.providerId));
    return [...deduped, ...newData];
}
function extractProviderData(providers) {
    return providers.map((_a) => {
        var { providerId } = _a, provider = __rest(_a, ["providerId"]);
        return {
            providerId,
            uid: provider.rawId || '',
            displayName: provider.displayName || null,
            email: provider.email || null,
            phoneNumber: provider.phoneNumber || null,
            photoURL: provider.photoUrl || null
        };
    });
}

/**
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
 */
async function requestStsToken(auth, refreshToken) {
    const response = await _performFetchWithErrorHandling(auth, {}, async () => {
        const body = querystring({
            'grant_type': 'refresh_token',
            'refresh_token': refreshToken
        }).slice(1);
        const { tokenApiHost, apiKey } = auth.config;
        const url = _getFinalTarget(auth, tokenApiHost, "/v1/token" /* Endpoint.TOKEN */, `key=${apiKey}`);
        const headers = await auth._getAdditionalHeaders();
        headers["Content-Type" /* HttpHeader.CONTENT_TYPE */] = 'application/x-www-form-urlencoded';
        return FetchProvider.fetch()(url, {
            method: "POST" /* HttpMethod.POST */,
            headers,
            body
        });
    });
    // The response comes back in snake_case. Convert to camel:
    return {
        accessToken: response.access_token,
        expiresIn: response.expires_in,
        refreshToken: response.refresh_token
    };
}
async function revokeToken(auth, request) {
    return _performApiRequest(auth, "POST" /* HttpMethod.POST */, "/v2/accounts:revokeToken" /* Endpoint.REVOKE_TOKEN */, _addTidIfNecessary(auth, request));
}

/**
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
 */
/**
 * We need to mark this class as internal explicitly to exclude it in the public typings, because
 * it references AuthInternal which has a circular dependency with UserInternal.
 *
 * @internal
 */
class StsTokenManager {
    constructor() {
        this.refreshToken = null;
        this.accessToken = null;
        this.expirationTime = null;
    }
    get isExpired() {
        return (!this.expirationTime ||
            Date.now() > this.expirationTime - 30000 /* Buffer.TOKEN_REFRESH */);
    }
    updateFromServerResponse(response) {
        _assert(response.idToken, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        _assert(typeof response.idToken !== 'undefined', "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        _assert(typeof response.refreshToken !== 'undefined', "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        const expiresIn = 'expiresIn' in response && typeof response.expiresIn !== 'undefined'
            ? Number(response.expiresIn)
            : _tokenExpiresIn(response.idToken);
        this.updateTokensAndExpiration(response.idToken, response.refreshToken, expiresIn);
    }
    updateFromIdToken(idToken) {
        _assert(idToken.length !== 0, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        const expiresIn = _tokenExpiresIn(idToken);
        this.updateTokensAndExpiration(idToken, null, expiresIn);
    }
    async getToken(auth, forceRefresh = false) {
        if (!forceRefresh && this.accessToken && !this.isExpired) {
            return this.accessToken;
        }
        _assert(this.refreshToken, auth, "user-token-expired" /* AuthErrorCode.TOKEN_EXPIRED */);
        if (this.refreshToken) {
            await this.refresh(auth, this.refreshToken);
            return this.accessToken;
        }
        return null;
    }
    clearRefreshToken() {
        this.refreshToken = null;
    }
    async refresh(auth, oldToken) {
        const { accessToken, refreshToken, expiresIn } = await requestStsToken(auth, oldToken);
        this.updateTokensAndExpiration(accessToken, refreshToken, Number(expiresIn));
    }
    updateTokensAndExpiration(accessToken, refreshToken, expiresInSec) {
        this.refreshToken = refreshToken || null;
        this.accessToken = accessToken || null;
        this.expirationTime = Date.now() + expiresInSec * 1000;
    }
    static fromJSON(appName, object) {
        const { refreshToken, accessToken, expirationTime } = object;
        const manager = new StsTokenManager();
        if (refreshToken) {
            _assert(typeof refreshToken === 'string', "internal-error" /* AuthErrorCode.INTERNAL_ERROR */, {
                appName
            });
            manager.refreshToken = refreshToken;
        }
        if (accessToken) {
            _assert(typeof accessToken === 'string', "internal-error" /* AuthErrorCode.INTERNAL_ERROR */, {
                appName
            });
            manager.accessToken = accessToken;
        }
        if (expirationTime) {
            _assert(typeof expirationTime === 'number', "internal-error" /* AuthErrorCode.INTERNAL_ERROR */, {
                appName
            });
            manager.expirationTime = expirationTime;
        }
        return manager;
    }
    toJSON() {
        return {
            refreshToken: this.refreshToken,
            accessToken: this.accessToken,
            expirationTime: this.expirationTime
        };
    }
    _assign(stsTokenManager) {
        this.accessToken = stsTokenManager.accessToken;
        this.refreshToken = stsTokenManager.refreshToken;
        this.expirationTime = stsTokenManager.expirationTime;
    }
    _clone() {
        return Object.assign(new StsTokenManager(), this.toJSON());
    }
    _performRefresh() {
        return debugFail('not implemented');
    }
}

/**
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
 */
function assertStringOrUndefined(assertion, appName) {
    _assert(typeof assertion === 'string' || typeof assertion === 'undefined', "internal-error" /* AuthErrorCode.INTERNAL_ERROR */, { appName });
}
class UserImpl {
    constructor(_a) {
        var { uid, auth, stsTokenManager } = _a, opt = __rest(_a, ["uid", "auth", "stsTokenManager"]);
        // For the user object, provider is always Firebase.
        this.providerId = "firebase" /* ProviderId.FIREBASE */;
        this.proactiveRefresh = new ProactiveRefresh(this);
        this.reloadUserInfo = null;
        this.reloadListener = null;
        this.uid = uid;
        this.auth = auth;
        this.stsTokenManager = stsTokenManager;
        this.accessToken = stsTokenManager.accessToken;
        this.displayName = opt.displayName || null;
        this.email = opt.email || null;
        this.emailVerified = opt.emailVerified || false;
        this.phoneNumber = opt.phoneNumber || null;
        this.photoURL = opt.photoURL || null;
        this.isAnonymous = opt.isAnonymous || false;
        this.tenantId = opt.tenantId || null;
        this.providerData = opt.providerData ? [...opt.providerData] : [];
        this.metadata = new UserMetadata(opt.createdAt || undefined, opt.lastLoginAt || undefined);
    }
    async getIdToken(forceRefresh) {
        const accessToken = await _logoutIfInvalidated(this, this.stsTokenManager.getToken(this.auth, forceRefresh));
        _assert(accessToken, this.auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        if (this.accessToken !== accessToken) {
            this.accessToken = accessToken;
            await this.auth._persistUserIfCurrent(this);
            this.auth._notifyListenersIfCurrent(this);
        }
        return accessToken;
    }
    getIdTokenResult(forceRefresh) {
        return getIdTokenResult(this, forceRefresh);
    }
    reload() {
        return reload(this);
    }
    _assign(user) {
        if (this === user) {
            return;
        }
        _assert(this.uid === user.uid, this.auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        this.displayName = user.displayName;
        this.photoURL = user.photoURL;
        this.email = user.email;
        this.emailVerified = user.emailVerified;
        this.phoneNumber = user.phoneNumber;
        this.isAnonymous = user.isAnonymous;
        this.tenantId = user.tenantId;
        this.providerData = user.providerData.map(userInfo => (Object.assign({}, userInfo)));
        this.metadata._copy(user.metadata);
        this.stsTokenManager._assign(user.stsTokenManager);
    }
    _clone(auth) {
        const newUser = new UserImpl(Object.assign(Object.assign({}, this), { auth, stsTokenManager: this.stsTokenManager._clone() }));
        newUser.metadata._copy(this.metadata);
        return newUser;
    }
    _onReload(callback) {
        // There should only ever be one listener, and that is a single instance of MultiFactorUser
        _assert(!this.reloadListener, this.auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        this.reloadListener = callback;
        if (this.reloadUserInfo) {
            this._notifyReloadListener(this.reloadUserInfo);
            this.reloadUserInfo = null;
        }
    }
    _notifyReloadListener(userInfo) {
        if (this.reloadListener) {
            this.reloadListener(userInfo);
        }
        else {
            // If no listener is subscribed yet, save the result so it's available when they do subscribe
            this.reloadUserInfo = userInfo;
        }
    }
    _startProactiveRefresh() {
        this.proactiveRefresh._start();
    }
    _stopProactiveRefresh() {
        this.proactiveRefresh._stop();
    }
    async _updateTokensIfNecessary(response, reload = false) {
        let tokensRefreshed = false;
        if (response.idToken &&
            response.idToken !== this.stsTokenManager.accessToken) {
            this.stsTokenManager.updateFromServerResponse(response);
            tokensRefreshed = true;
        }
        if (reload) {
            await _reloadWithoutSaving(this);
        }
        await this.auth._persistUserIfCurrent(this);
        if (tokensRefreshed) {
            this.auth._notifyListenersIfCurrent(this);
        }
    }
    async delete() {
        if (_isFirebaseServerApp(this.auth.app)) {
            return Promise.reject(_serverAppCurrentUserOperationNotSupportedError(this.auth));
        }
        const idToken = await this.getIdToken();
        await _logoutIfInvalidated(this, deleteAccount(this.auth, { idToken }));
        this.stsTokenManager.clearRefreshToken();
        // TODO: Determine if cancellable-promises are necessary to use in this class so that delete()
        //       cancels pending actions...
        return this.auth.signOut();
    }
    toJSON() {
        return Object.assign(Object.assign({ uid: this.uid, email: this.email || undefined, emailVerified: this.emailVerified, displayName: this.displayName || undefined, isAnonymous: this.isAnonymous, photoURL: this.photoURL || undefined, phoneNumber: this.phoneNumber || undefined, tenantId: this.tenantId || undefined, providerData: this.providerData.map(userInfo => (Object.assign({}, userInfo))), stsTokenManager: this.stsTokenManager.toJSON(), 
            // Redirect event ID must be maintained in case there is a pending
            // redirect event.
            _redirectEventId: this._redirectEventId }, this.metadata.toJSON()), { 
            // Required for compatibility with the legacy SDK (go/firebase-auth-sdk-persistence-parsing):
            apiKey: this.auth.config.apiKey, appName: this.auth.name });
    }
    get refreshToken() {
        return this.stsTokenManager.refreshToken || '';
    }
    static _fromJSON(auth, object) {
        var _a, _b, _c, _d, _e, _f, _g, _h;
        const displayName = (_a = object.displayName) !== null && _a !== void 0 ? _a : undefined;
        const email = (_b = object.email) !== null && _b !== void 0 ? _b : undefined;
        const phoneNumber = (_c = object.phoneNumber) !== null && _c !== void 0 ? _c : undefined;
        const photoURL = (_d = object.photoURL) !== null && _d !== void 0 ? _d : undefined;
        const tenantId = (_e = object.tenantId) !== null && _e !== void 0 ? _e : undefined;
        const _redirectEventId = (_f = object._redirectEventId) !== null && _f !== void 0 ? _f : undefined;
        const createdAt = (_g = object.createdAt) !== null && _g !== void 0 ? _g : undefined;
        const lastLoginAt = (_h = object.lastLoginAt) !== null && _h !== void 0 ? _h : undefined;
        const { uid, emailVerified, isAnonymous, providerData, stsTokenManager: plainObjectTokenManager } = object;
        _assert(uid && plainObjectTokenManager, auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        const stsTokenManager = StsTokenManager.fromJSON(this.name, plainObjectTokenManager);
        _assert(typeof uid === 'string', auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        assertStringOrUndefined(displayName, auth.name);
        assertStringOrUndefined(email, auth.name);
        _assert(typeof emailVerified === 'boolean', auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        _assert(typeof isAnonymous === 'boolean', auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        assertStringOrUndefined(phoneNumber, auth.name);
        assertStringOrUndefined(photoURL, auth.name);
        assertStringOrUndefined(tenantId, auth.name);
        assertStringOrUndefined(_redirectEventId, auth.name);
        assertStringOrUndefined(createdAt, auth.name);
        assertStringOrUndefined(lastLoginAt, auth.name);
        const user = new UserImpl({
            uid,
            auth,
            email,
            emailVerified,
            displayName,
            isAnonymous,
            photoURL,
            phoneNumber,
            tenantId,
            stsTokenManager,
            createdAt,
            lastLoginAt
        });
        if (providerData && Array.isArray(providerData)) {
            user.providerData = providerData.map(userInfo => (Object.assign({}, userInfo)));
        }
        if (_redirectEventId) {
            user._redirectEventId = _redirectEventId;
        }
        return user;
    }
    /**
     * Initialize a User from an idToken server response
     * @param auth
     * @param idTokenResponse
     */
    static async _fromIdTokenResponse(auth, idTokenResponse, isAnonymous = false) {
        const stsTokenManager = new StsTokenManager();
        stsTokenManager.updateFromServerResponse(idTokenResponse);
        // Initialize the Firebase Auth user.
        const user = new UserImpl({
            uid: idTokenResponse.localId,
            auth,
            stsTokenManager,
            isAnonymous
        });
        // Updates the user info and data and resolves with a user instance.
        await _reloadWithoutSaving(user);
        return user;
    }
    /**
     * Initialize a User from an idToken server response
     * @param auth
     * @param idTokenResponse
     */
    static async _fromGetAccountInfoResponse(auth, response, idToken) {
        const coreAccount = response.users[0];
        _assert(coreAccount.localId !== undefined, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        const providerData = coreAccount.providerUserInfo !== undefined
            ? extractProviderData(coreAccount.providerUserInfo)
            : [];
        const isAnonymous = !(coreAccount.email && coreAccount.passwordHash) && !(providerData === null || providerData === void 0 ? void 0 : providerData.length);
        const stsTokenManager = new StsTokenManager();
        stsTokenManager.updateFromIdToken(idToken);
        // Initialize the Firebase Auth user.
        const user = new UserImpl({
            uid: coreAccount.localId,
            auth,
            stsTokenManager,
            isAnonymous
        });
        // update the user with data from the GetAccountInfo response.
        const updates = {
            uid: coreAccount.localId,
            displayName: coreAccount.displayName || null,
            photoURL: coreAccount.photoUrl || null,
            email: coreAccount.email || null,
            emailVerified: coreAccount.emailVerified || false,
            phoneNumber: coreAccount.phoneNumber || null,
            tenantId: coreAccount.tenantId || null,
            providerData,
            metadata: new UserMetadata(coreAccount.createdAt, coreAccount.lastLoginAt),
            isAnonymous: !(coreAccount.email && coreAccount.passwordHash) &&
                !(providerData === null || providerData === void 0 ? void 0 : providerData.length)
        };
        Object.assign(user, updates);
        return user;
    }
}

/**
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
 */
const instanceCache = new Map();
function _getInstance(cls) {
    debugAssert(cls instanceof Function, 'Expected a class definition');
    let instance = instanceCache.get(cls);
    if (instance) {
        debugAssert(instance instanceof cls, 'Instance stored in cache mismatched with class');
        return instance;
    }
    instance = new cls();
    instanceCache.set(cls, instance);
    return instance;
}

/**
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
 */
class InMemoryPersistence {
    constructor() {
        this.type = "NONE" /* PersistenceType.NONE */;
        this.storage = {};
    }
    async _isAvailable() {
        return true;
    }
    async _set(key, value) {
        this.storage[key] = value;
    }
    async _get(key) {
        const value = this.storage[key];
        return value === undefined ? null : value;
    }
    async _remove(key) {
        delete this.storage[key];
    }
    _addListener(_key, _listener) {
        // Listeners are not supported for in-memory storage since it cannot be shared across windows/workers
        return;
    }
    _removeListener(_key, _listener) {
        // Listeners are not supported for in-memory storage since it cannot be shared across windows/workers
        return;
    }
}
InMemoryPersistence.type = 'NONE';
/**
 * An implementation of {@link Persistence} of type 'NONE'.
 *
 * @public
 */
const inMemoryPersistence = InMemoryPersistence;

/**
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
 */
function _persistenceKeyName(key, apiKey, appName) {
    return `${"firebase" /* Namespace.PERSISTENCE */}:${key}:${apiKey}:${appName}`;
}
class PersistenceUserManager {
    constructor(persistence, auth, userKey) {
        this.persistence = persistence;
        this.auth = auth;
        this.userKey = userKey;
        const { config, name } = this.auth;
        this.fullUserKey = _persistenceKeyName(this.userKey, config.apiKey, name);
        this.fullPersistenceKey = _persistenceKeyName("persistence" /* KeyName.PERSISTENCE_USER */, config.apiKey, name);
        this.boundEventHandler = auth._onStorageEvent.bind(auth);
        this.persistence._addListener(this.fullUserKey, this.boundEventHandler);
    }
    setCurrentUser(user) {
        return this.persistence._set(this.fullUserKey, user.toJSON());
    }
    async getCurrentUser() {
        const blob = await this.persistence._get(this.fullUserKey);
        return blob ? UserImpl._fromJSON(this.auth, blob) : null;
    }
    removeCurrentUser() {
        return this.persistence._remove(this.fullUserKey);
    }
    savePersistenceForRedirect() {
        return this.persistence._set(this.fullPersistenceKey, this.persistence.type);
    }
    async setPersistence(newPersistence) {
        if (this.persistence === newPersistence) {
            return;
        }
        const currentUser = await this.getCurrentUser();
        await this.removeCurrentUser();
        this.persistence = newPersistence;
        if (currentUser) {
            return this.setCurrentUser(currentUser);
        }
    }
    delete() {
        this.persistence._removeListener(this.fullUserKey, this.boundEventHandler);
    }
    static async create(auth, persistenceHierarchy, userKey = "authUser" /* KeyName.AUTH_USER */) {
        if (!persistenceHierarchy.length) {
            return new PersistenceUserManager(_getInstance(inMemoryPersistence), auth, userKey);
        }
        // Eliminate any persistences that are not available
        const availablePersistences = (await Promise.all(persistenceHierarchy.map(async (persistence) => {
            if (await persistence._isAvailable()) {
                return persistence;
            }
            return undefined;
        }))).filter(persistence => persistence);
        // Fall back to the first persistence listed, or in memory if none available
        let selectedPersistence = availablePersistences[0] ||
            _getInstance(inMemoryPersistence);
        const key = _persistenceKeyName(userKey, auth.config.apiKey, auth.name);
        // Pull out the existing user, setting the chosen persistence to that
        // persistence if the user exists.
        let userToMigrate = null;
        // Note, here we check for a user in _all_ persistences, not just the
        // ones deemed available. If we can migrate a user out of a broken
        // persistence, we will (but only if that persistence supports migration).
        for (const persistence of persistenceHierarchy) {
            try {
                const blob = await persistence._get(key);
                if (blob) {
                    const user = UserImpl._fromJSON(auth, blob); // throws for unparsable blob (wrong format)
                    if (persistence !== selectedPersistence) {
                        userToMigrate = user;
                    }
                    selectedPersistence = persistence;
                    break;
                }
            }
            catch (_a) { }
        }
        // If we find the user in a persistence that does support migration, use
        // that migration path (of only persistences that support migration)
        const migrationHierarchy = availablePersistences.filter(p => p._shouldAllowMigration);
        // If the persistence does _not_ allow migration, just finish off here
        if (!selectedPersistence._shouldAllowMigration ||
            !migrationHierarchy.length) {
            return new PersistenceUserManager(selectedPersistence, auth, userKey);
        }
        selectedPersistence = migrationHierarchy[0];
        if (userToMigrate) {
            // This normally shouldn't throw since chosenPersistence.isAvailable() is true, but if it does
            // we'll just let it bubble to surface the error.
            await selectedPersistence._set(key, userToMigrate.toJSON());
        }
        // Attempt to clear the key in other persistences but ignore errors. This helps prevent issues
        // such as users getting stuck with a previous account after signing out and refreshing the tab.
        await Promise.all(persistenceHierarchy.map(async (persistence) => {
            if (persistence !== selectedPersistence) {
                try {
                    await persistence._remove(key);
                }
                catch (_a) { }
            }
        }));
        return new PersistenceUserManager(selectedPersistence, auth, userKey);
    }
}

/**
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
 */
/**
 * Determine the browser for the purposes of reporting usage to the API
 */
function _getBrowserName(userAgent) {
    const ua = userAgent.toLowerCase();
    if (ua.includes('opera/') || ua.includes('opr/') || ua.includes('opios/')) {
        return "Opera" /* BrowserName.OPERA */;
    }
    else if (_isIEMobile(ua)) {
        // Windows phone IEMobile browser.
        return "IEMobile" /* BrowserName.IEMOBILE */;
    }
    else if (ua.includes('msie') || ua.includes('trident/')) {
        return "IE" /* BrowserName.IE */;
    }
    else if (ua.includes('edge/')) {
        return "Edge" /* BrowserName.EDGE */;
    }
    else if (_isFirefox(ua)) {
        return "Firefox" /* BrowserName.FIREFOX */;
    }
    else if (ua.includes('silk/')) {
        return "Silk" /* BrowserName.SILK */;
    }
    else if (_isBlackBerry(ua)) {
        // Blackberry browser.
        return "Blackberry" /* BrowserName.BLACKBERRY */;
    }
    else if (_isWebOS(ua)) {
        // WebOS default browser.
        return "Webos" /* BrowserName.WEBOS */;
    }
    else if (_isSafari(ua)) {
        return "Safari" /* BrowserName.SAFARI */;
    }
    else if ((ua.includes('chrome/') || _isChromeIOS(ua)) &&
        !ua.includes('edge/')) {
        return "Chrome" /* BrowserName.CHROME */;
    }
    else if (_isAndroid(ua)) {
        // Android stock browser.
        return "Android" /* BrowserName.ANDROID */;
    }
    else {
        // Most modern browsers have name/version at end of user agent string.
        const re = /([a-zA-Z\d\.]+)\/[a-zA-Z\d\.]*$/;
        const matches = userAgent.match(re);
        if ((matches === null || matches === void 0 ? void 0 : matches.length) === 2) {
            return matches[1];
        }
    }
    return "Other" /* BrowserName.OTHER */;
}
function _isFirefox(ua = getUA()) {
    return /firefox\//i.test(ua);
}
function _isSafari(userAgent = getUA()) {
    const ua = userAgent.toLowerCase();
    return (ua.includes('safari/') &&
        !ua.includes('chrome/') &&
        !ua.includes('crios/') &&
        !ua.includes('android'));
}
function _isChromeIOS(ua = getUA()) {
    return /crios\//i.test(ua);
}
function _isIEMobile(ua = getUA()) {
    return /iemobile/i.test(ua);
}
function _isAndroid(ua = getUA()) {
    return /android/i.test(ua);
}
function _isBlackBerry(ua = getUA()) {
    return /blackberry/i.test(ua);
}
function _isWebOS(ua = getUA()) {
    return /webos/i.test(ua);
}
function _isIOS(ua = getUA()) {
    return (/iphone|ipad|ipod/i.test(ua) ||
        (/macintosh/i.test(ua) && /mobile/i.test(ua)));
}
function _isIOSStandalone(ua = getUA()) {
    var _a;
    return _isIOS(ua) && !!((_a = window.navigator) === null || _a === void 0 ? void 0 : _a.standalone);
}
function _isIE10() {
    return isIE() && document.documentMode === 10;
}
function _isMobileBrowser(ua = getUA()) {
    // TODO: implement getBrowserName equivalent for OS.
    return (_isIOS(ua) ||
        _isAndroid(ua) ||
        _isWebOS(ua) ||
        _isBlackBerry(ua) ||
        /windows phone/i.test(ua) ||
        _isIEMobile(ua));
}
function _isIframe() {
    try {
        // Check that the current window is not the top window.
        // If so, return true.
        return !!(window && window !== window.top);
    }
    catch (e) {
        return false;
    }
}

/**
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
 */
/*
 * Determine the SDK version string
 */
function _getClientVersion(clientPlatform, frameworks = []) {
    let reportedPlatform;
    switch (clientPlatform) {
        case "Browser" /* ClientPlatform.BROWSER */:
            // In a browser environment, report the browser name.
            reportedPlatform = _getBrowserName(getUA());
            break;
        case "Worker" /* ClientPlatform.WORKER */:
            // Technically a worker runs from a browser but we need to differentiate a
            // worker from a browser.
            // For example: Chrome-Worker/JsCore/4.9.1/FirebaseCore-web.
            reportedPlatform = `${_getBrowserName(getUA())}-${clientPlatform}`;
            break;
        default:
            reportedPlatform = clientPlatform;
    }
    const reportedFrameworks = frameworks.length
        ? frameworks.join(',')
        : 'FirebaseCore-web'; /* default value if no other framework is used */
    return `${reportedPlatform}/${"JsCore" /* ClientImplementation.CORE */}/${SDK_VERSION}/${reportedFrameworks}`;
}

/**
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
 */
class AuthMiddlewareQueue {
    constructor(auth) {
        this.auth = auth;
        this.queue = [];
    }
    pushCallback(callback, onAbort) {
        // The callback could be sync or async. Wrap it into a
        // function that is always async.
        const wrappedCallback = (user) => new Promise((resolve, reject) => {
            try {
                const result = callback(user);
                // Either resolve with existing promise or wrap a non-promise
                // return value into a promise.
                resolve(result);
            }
            catch (e) {
                // Sync callback throws.
                reject(e);
            }
        });
        // Attach the onAbort if present
        wrappedCallback.onAbort = onAbort;
        this.queue.push(wrappedCallback);
        const index = this.queue.length - 1;
        return () => {
            // Unsubscribe. Replace with no-op. Do not remove from array, or it will disturb
            // indexing of other elements.
            this.queue[index] = () => Promise.resolve();
        };
    }
    async runMiddleware(nextUser) {
        if (this.auth.currentUser === nextUser) {
            return;
        }
        // While running the middleware, build a temporary stack of onAbort
        // callbacks to call if one middleware callback rejects.
        const onAbortStack = [];
        try {
            for (const beforeStateCallback of this.queue) {
                await beforeStateCallback(nextUser);
                // Only push the onAbort if the callback succeeds
                if (beforeStateCallback.onAbort) {
                    onAbortStack.push(beforeStateCallback.onAbort);
                }
            }
        }
        catch (e) {
            // Run all onAbort, with separate try/catch to ignore any errors and
            // continue
            onAbortStack.reverse();
            for (const onAbort of onAbortStack) {
                try {
                    onAbort();
                }
                catch (_) {
                    /* swallow error */
                }
            }
            throw this.auth._errorFactory.create("login-blocked" /* AuthErrorCode.LOGIN_BLOCKED */, {
                originalMessage: e === null || e === void 0 ? void 0 : e.message
            });
        }
    }
}

/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
/**
 * Fetches the password policy for the currently set tenant or the project if no tenant is set.
 *
 * @param auth Auth object.
 * @param request Password policy request.
 * @returns Password policy response.
 */
async function _getPasswordPolicy(auth, request = {}) {
    return _performApiRequest(auth, "GET" /* HttpMethod.GET */, "/v2/passwordPolicy" /* Endpoint.GET_PASSWORD_POLICY */, _addTidIfNecessary(auth, request));
}

/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
// Minimum min password length enforced by the backend, even if no minimum length is set.
const MINIMUM_MIN_PASSWORD_LENGTH = 6;
/**
 * Stores password policy requirements and provides password validation against the policy.
 *
 * @internal
 */
class PasswordPolicyImpl {
    constructor(response) {
        var _a, _b, _c, _d;
        // Only include custom strength options defined in the response.
        const responseOptions = response.customStrengthOptions;
        this.customStrengthOptions = {};
        // TODO: Remove once the backend is updated to include the minimum min password length instead of undefined when there is no minimum length set.
        this.customStrengthOptions.minPasswordLength =
            (_a = responseOptions.minPasswordLength) !== null && _a !== void 0 ? _a : MINIMUM_MIN_PASSWORD_LENGTH;
        if (responseOptions.maxPasswordLength) {
            this.customStrengthOptions.maxPasswordLength =
                responseOptions.maxPasswordLength;
        }
        if (responseOptions.containsLowercaseCharacter !== undefined) {
            this.customStrengthOptions.containsLowercaseLetter =
                responseOptions.containsLowercaseCharacter;
        }
        if (responseOptions.containsUppercaseCharacter !== undefined) {
            this.customStrengthOptions.containsUppercaseLetter =
                responseOptions.containsUppercaseCharacter;
        }
        if (responseOptions.containsNumericCharacter !== undefined) {
            this.customStrengthOptions.containsNumericCharacter =
                responseOptions.containsNumericCharacter;
        }
        if (responseOptions.containsNonAlphanumericCharacter !== undefined) {
            this.customStrengthOptions.containsNonAlphanumericCharacter =
                responseOptions.containsNonAlphanumericCharacter;
        }
        this.enforcementState = response.enforcementState;
        if (this.enforcementState === 'ENFORCEMENT_STATE_UNSPECIFIED') {
            this.enforcementState = 'OFF';
        }
        // Use an empty string if no non-alphanumeric characters are specified in the response.
        this.allowedNonAlphanumericCharacters =
            (_c = (_b = response.allowedNonAlphanumericCharacters) === null || _b === void 0 ? void 0 : _b.join('')) !== null && _c !== void 0 ? _c : '';
        this.forceUpgradeOnSignin = (_d = response.forceUpgradeOnSignin) !== null && _d !== void 0 ? _d : false;
        this.schemaVersion = response.schemaVersion;
    }
    validatePassword(password) {
        var _a, _b, _c, _d, _e, _f;
        const status = {
            isValid: true,
            passwordPolicy: this
        };
        // Check the password length and character options.
        this.validatePasswordLengthOptions(password, status);
        this.validatePasswordCharacterOptions(password, status);
        // Combine the status into single isValid property.
        status.isValid && (status.isValid = (_a = status.meetsMinPasswordLength) !== null && _a !== void 0 ? _a : true);
        status.isValid && (status.isValid = (_b = status.meetsMaxPasswordLength) !== null && _b !== void 0 ? _b : true);
        status.isValid && (status.isValid = (_c = status.containsLowercaseLetter) !== null && _c !== void 0 ? _c : true);
        status.isValid && (status.isValid = (_d = status.containsUppercaseLetter) !== null && _d !== void 0 ? _d : true);
        status.isValid && (status.isValid = (_e = status.containsNumericCharacter) !== null && _e !== void 0 ? _e : true);
        status.isValid && (status.isValid = (_f = status.containsNonAlphanumericCharacter) !== null && _f !== void 0 ? _f : true);
        return status;
    }
    /**
     * Validates that the password meets the length options for the policy.
     *
     * @param password Password to validate.
     * @param status Validation status.
     */
    validatePasswordLengthOptions(password, status) {
        const minPasswordLength = this.customStrengthOptions.minPasswordLength;
        const maxPasswordLength = this.customStrengthOptions.maxPasswordLength;
        if (minPasswordLength) {
            status.meetsMinPasswordLength = password.length >= minPasswordLength;
        }
        if (maxPasswordLength) {
            status.meetsMaxPasswordLength = password.length <= maxPasswordLength;
        }
    }
    /**
     * Validates that the password meets the character options for the policy.
     *
     * @param password Password to validate.
     * @param status Validation status.
     */
    validatePasswordCharacterOptions(password, status) {
        // Assign statuses for requirements even if the password is an empty string.
        this.updatePasswordCharacterOptionsStatuses(status, 
        /* containsLowercaseCharacter= */ false, 
        /* containsUppercaseCharacter= */ false, 
        /* containsNumericCharacter= */ false, 
        /* containsNonAlphanumericCharacter= */ false);
        let passwordChar;
        for (let i = 0; i < password.length; i++) {
            passwordChar = password.charAt(i);
            this.updatePasswordCharacterOptionsStatuses(status, 
            /* containsLowercaseCharacter= */ passwordChar >= 'a' &&
                passwordChar <= 'z', 
            /* containsUppercaseCharacter= */ passwordChar >= 'A' &&
                passwordChar <= 'Z', 
            /* containsNumericCharacter= */ passwordChar >= '0' &&
                passwordChar <= '9', 
            /* containsNonAlphanumericCharacter= */ this.allowedNonAlphanumericCharacters.includes(passwordChar));
        }
    }
    /**
     * Updates the running validation status with the statuses for the character options.
     * Expected to be called each time a character is processed to update each option status
     * based on the current character.
     *
     * @param status Validation status.
     * @param containsLowercaseCharacter Whether the character is a lowercase letter.
     * @param containsUppercaseCharacter Whether the character is an uppercase letter.
     * @param containsNumericCharacter Whether the character is a numeric character.
     * @param containsNonAlphanumericCharacter Whether the character is a non-alphanumeric character.
     */
    updatePasswordCharacterOptionsStatuses(status, containsLowercaseCharacter, containsUppercaseCharacter, containsNumericCharacter, containsNonAlphanumericCharacter) {
        if (this.customStrengthOptions.containsLowercaseLetter) {
            status.containsLowercaseLetter || (status.containsLowercaseLetter = containsLowercaseCharacter);
        }
        if (this.customStrengthOptions.containsUppercaseLetter) {
            status.containsUppercaseLetter || (status.containsUppercaseLetter = containsUppercaseCharacter);
        }
        if (this.customStrengthOptions.containsNumericCharacter) {
            status.containsNumericCharacter || (status.containsNumericCharacter = containsNumericCharacter);
        }
        if (this.customStrengthOptions.containsNonAlphanumericCharacter) {
            status.containsNonAlphanumericCharacter || (status.containsNonAlphanumericCharacter = containsNonAlphanumericCharacter);
        }
    }
}

/**
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
 */
class AuthImpl {
    constructor(app, heartbeatServiceProvider, appCheckServiceProvider, config) {
        this.app = app;
        this.heartbeatServiceProvider = heartbeatServiceProvider;
        this.appCheckServiceProvider = appCheckServiceProvider;
        this.config = config;
        this.currentUser = null;
        this.emulatorConfig = null;
        this.operations = Promise.resolve();
        this.authStateSubscription = new Subscription(this);
        this.idTokenSubscription = new Subscription(this);
        this.beforeStateQueue = new AuthMiddlewareQueue(this);
        this.redirectUser = null;
        this.isProactiveRefreshEnabled = false;
        this.EXPECTED_PASSWORD_POLICY_SCHEMA_VERSION = 1;
        // Any network calls will set this to true and prevent subsequent emulator
        // initialization
        this._canInitEmulator = true;
        this._isInitialized = false;
        this._deleted = false;
        this._initializationPromise = null;
        this._popupRedirectResolver = null;
        this._errorFactory = _DEFAULT_AUTH_ERROR_FACTORY;
        this._agentRecaptchaConfig = null;
        this._tenantRecaptchaConfigs = {};
        this._projectPasswordPolicy = null;
        this._tenantPasswordPolicies = {};
        // Tracks the last notified UID for state change listeners to prevent
        // repeated calls to the callbacks. Undefined means it's never been
        // called, whereas null means it's been called with a signed out user
        this.lastNotifiedUid = undefined;
        this.languageCode = null;
        this.tenantId = null;
        this.settings = { appVerificationDisabledForTesting: false };
        this.frameworks = [];
        this.name = app.name;
        this.clientVersion = config.sdkClientVersion;
    }
    _initializeWithPersistence(persistenceHierarchy, popupRedirectResolver) {
        if (popupRedirectResolver) {
            this._popupRedirectResolver = _getInstance(popupRedirectResolver);
        }
        // Have to check for app deletion throughout initialization (after each
        // promise resolution)
        this._initializationPromise = this.queue(async () => {
            var _a, _b;
            if (this._deleted) {
                return;
            }
            this.persistenceManager = await PersistenceUserManager.create(this, persistenceHierarchy);
            if (this._deleted) {
                return;
            }
            // Initialize the resolver early if necessary (only applicable to web:
            // this will cause the iframe to load immediately in certain cases)
            if ((_a = this._popupRedirectResolver) === null || _a === void 0 ? void 0 : _a._shouldInitProactively) {
                // If this fails, don't halt auth loading
                try {
                    await this._popupRedirectResolver._initialize(this);
                }
                catch (e) {
                    /* Ignore the error */
                }
            }
            await this.initializeCurrentUser(popupRedirectResolver);
            this.lastNotifiedUid = ((_b = this.currentUser) === null || _b === void 0 ? void 0 : _b.uid) || null;
            if (this._deleted) {
                return;
            }
            this._isInitialized = true;
        });
        return this._initializationPromise;
    }
    /**
     * If the persistence is changed in another window, the user manager will let us know
     */
    async _onStorageEvent() {
        if (this._deleted) {
            return;
        }
        const user = await this.assertedPersistence.getCurrentUser();
        if (!this.currentUser && !user) {
            // No change, do nothing (was signed out and remained signed out).
            return;
        }
        // If the same user is to be synchronized.
        if (this.currentUser && user && this.currentUser.uid === user.uid) {
            // Data update, simply copy data changes.
            this._currentUser._assign(user);
            // If tokens changed from previous user tokens, this will trigger
            // notifyAuthListeners_.
            await this.currentUser.getIdToken();
            return;
        }
        // Update current Auth state. Either a new login or logout.
        // Skip blocking callbacks, they should not apply to a change in another tab.
        await this._updateCurrentUser(user, /* skipBeforeStateCallbacks */ true);
    }
    async initializeCurrentUserFromIdToken(idToken) {
        try {
            const response = await getAccountInfo(this, { idToken });
            const user = await UserImpl._fromGetAccountInfoResponse(this, response, idToken);
            await this.directlySetCurrentUser(user);
        }
        catch (err) {
            console.warn('FirebaseServerApp could not login user with provided authIdToken: ', err);
            await this.directlySetCurrentUser(null);
        }
    }
    async initializeCurrentUser(popupRedirectResolver) {
        var _a;
        if (_isFirebaseServerApp(this.app)) {
            const idToken = this.app.settings.authIdToken;
            if (idToken) {
                // Start the auth operation in the next tick to allow a moment for the customer's app to
                // attach an emulator, if desired.
                return new Promise(resolve => {
                    setTimeout(() => this.initializeCurrentUserFromIdToken(idToken).then(resolve, resolve));
                });
            }
            else {
                return this.directlySetCurrentUser(null);
            }
        }
        // First check to see if we have a pending redirect event.
        const previouslyStoredUser = (await this.assertedPersistence.getCurrentUser());
        let futureCurrentUser = previouslyStoredUser;
        let needsTocheckMiddleware = false;
        if (popupRedirectResolver && this.config.authDomain) {
            await this.getOrInitRedirectPersistenceManager();
            const redirectUserEventId = (_a = this.redirectUser) === null || _a === void 0 ? void 0 : _a._redirectEventId;
            const storedUserEventId = futureCurrentUser === null || futureCurrentUser === void 0 ? void 0 : futureCurrentUser._redirectEventId;
            const result = await this.tryRedirectSignIn(popupRedirectResolver);
            // If the stored user (i.e. the old "currentUser") has a redirectId that
            // matches the redirect user, then we want to initially sign in with the
            // new user object from result.
            // TODO(samgho): More thoroughly test all of this
            if ((!redirectUserEventId || redirectUserEventId === storedUserEventId) &&
                (result === null || result === void 0 ? void 0 : result.user)) {
                futureCurrentUser = result.user;
                needsTocheckMiddleware = true;
            }
        }
        // If no user in persistence, there is no current user. Set to null.
        if (!futureCurrentUser) {
            return this.directlySetCurrentUser(null);
        }
        if (!futureCurrentUser._redirectEventId) {
            // This isn't a redirect link operation, we can reload and bail.
            // First though, ensure that we check the middleware is happy.
            if (needsTocheckMiddleware) {
                try {
                    await this.beforeStateQueue.runMiddleware(futureCurrentUser);
                }
                catch (e) {
                    futureCurrentUser = previouslyStoredUser;
                    // We know this is available since the bit is only set when the
                    // resolver is available
                    this._popupRedirectResolver._overrideRedirectResult(this, () => Promise.reject(e));
                }
            }
            if (futureCurrentUser) {
                return this.reloadAndSetCurrentUserOrClear(futureCurrentUser);
            }
            else {
                return this.directlySetCurrentUser(null);
            }
        }
        _assert(this._popupRedirectResolver, this, "argument-error" /* AuthErrorCode.ARGUMENT_ERROR */);
        await this.getOrInitRedirectPersistenceManager();
        // If the redirect user's event ID matches the current user's event ID,
        // DO NOT reload the current user, otherwise they'll be cleared from storage.
        // This is important for the reauthenticateWithRedirect() flow.
        if (this.redirectUser &&
            this.redirectUser._redirectEventId === futureCurrentUser._redirectEventId) {
            return this.directlySetCurrentUser(futureCurrentUser);
        }
        return this.reloadAndSetCurrentUserOrClear(futureCurrentUser);
    }
    async tryRedirectSignIn(redirectResolver) {
        // The redirect user needs to be checked (and signed in if available)
        // during auth initialization. All of the normal sign in and link/reauth
        // flows call back into auth and push things onto the promise queue. We
        // need to await the result of the redirect sign in *inside the promise
        // queue*. This presents a problem: we run into deadlock. See:
        //    ┌> [Initialization] ─────┐
        //    ┌> [<other queue tasks>] │
        //    └─ [getRedirectResult] <─┘
        //    where [] are tasks on the queue and arrows denote awaits
        // Initialization will never complete because it's waiting on something
        // that's waiting for initialization to complete!
        //
        // Instead, this method calls getRedirectResult() (stored in
        // _completeRedirectFn) with an optional parameter that instructs all of
        // the underlying auth operations to skip anything that mutates auth state.
        let result = null;
        try {
            // We know this._popupRedirectResolver is set since redirectResolver
            // is passed in. The _completeRedirectFn expects the unwrapped extern.
            result = await this._popupRedirectResolver._completeRedirectFn(this, redirectResolver, true);
        }
        catch (e) {
            // Swallow any errors here; the code can retrieve them in
            // getRedirectResult().
            await this._setRedirectUser(null);
        }
        return result;
    }
    async reloadAndSetCurrentUserOrClear(user) {
        try {
            await _reloadWithoutSaving(user);
        }
        catch (e) {
            if ((e === null || e === void 0 ? void 0 : e.code) !==
                `auth/${"network-request-failed" /* AuthErrorCode.NETWORK_REQUEST_FAILED */}`) {
                // Something's wrong with the user's token. Log them out and remove
                // them from storage
                return this.directlySetCurrentUser(null);
            }
        }
        return this.directlySetCurrentUser(user);
    }
    useDeviceLanguage() {
        this.languageCode = _getUserLanguage();
    }
    async _delete() {
        this._deleted = true;
    }
    async updateCurrentUser(userExtern) {
        if (_isFirebaseServerApp(this.app)) {
            return Promise.reject(_serverAppCurrentUserOperationNotSupportedError(this));
        }
        // The public updateCurrentUser method needs to make a copy of the user,
        // and also check that the project matches
        const user = userExtern
            ? getModularInstance(userExtern)
            : null;
        if (user) {
            _assert(user.auth.config.apiKey === this.config.apiKey, this, "invalid-user-token" /* AuthErrorCode.INVALID_AUTH */);
        }
        return this._updateCurrentUser(user && user._clone(this));
    }
    async _updateCurrentUser(user, skipBeforeStateCallbacks = false) {
        if (this._deleted) {
            return;
        }
        if (user) {
            _assert(this.tenantId === user.tenantId, this, "tenant-id-mismatch" /* AuthErrorCode.TENANT_ID_MISMATCH */);
        }
        if (!skipBeforeStateCallbacks) {
            await this.beforeStateQueue.runMiddleware(user);
        }
        return this.queue(async () => {
            await this.directlySetCurrentUser(user);
            this.notifyAuthListeners();
        });
    }
    async signOut() {
        if (_isFirebaseServerApp(this.app)) {
            return Promise.reject(_serverAppCurrentUserOperationNotSupportedError(this));
        }
        // Run first, to block _setRedirectUser() if any callbacks fail.
        await this.beforeStateQueue.runMiddleware(null);
        // Clear the redirect user when signOut is called
        if (this.redirectPersistenceManager || this._popupRedirectResolver) {
            await this._setRedirectUser(null);
        }
        // Prevent callbacks from being called again in _updateCurrentUser, as
        // they were already called in the first line.
        return this._updateCurrentUser(null, /* skipBeforeStateCallbacks */ true);
    }
    setPersistence(persistence) {
        if (_isFirebaseServerApp(this.app)) {
            return Promise.reject(_serverAppCurrentUserOperationNotSupportedError(this));
        }
        return this.queue(async () => {
            await this.assertedPersistence.setPersistence(_getInstance(persistence));
        });
    }
    _getRecaptchaConfig() {
        if (this.tenantId == null) {
            return this._agentRecaptchaConfig;
        }
        else {
            return this._tenantRecaptchaConfigs[this.tenantId];
        }
    }
    async validatePassword(password) {
        if (!this._getPasswordPolicyInternal()) {
            await this._updatePasswordPolicy();
        }
        // Password policy will be defined after fetching.
        const passwordPolicy = this._getPasswordPolicyInternal();
        // Check that the policy schema version is supported by the SDK.
        // TODO: Update this logic to use a max supported policy schema version once we have multiple schema versions.
        if (passwordPolicy.schemaVersion !==
            this.EXPECTED_PASSWORD_POLICY_SCHEMA_VERSION) {
            return Promise.reject(this._errorFactory.create("unsupported-password-policy-schema-version" /* AuthErrorCode.UNSUPPORTED_PASSWORD_POLICY_SCHEMA_VERSION */, {}));
        }
        return passwordPolicy.validatePassword(password);
    }
    _getPasswordPolicyInternal() {
        if (this.tenantId === null) {
            return this._projectPasswordPolicy;
        }
        else {
            return this._tenantPasswordPolicies[this.tenantId];
        }
    }
    async _updatePasswordPolicy() {
        const response = await _getPasswordPolicy(this);
        const passwordPolicy = new PasswordPolicyImpl(response);
        if (this.tenantId === null) {
            this._projectPasswordPolicy = passwordPolicy;
        }
        else {
            this._tenantPasswordPolicies[this.tenantId] = passwordPolicy;
        }
    }
    _getPersistence() {
        return this.assertedPersistence.persistence.type;
    }
    _updateErrorMap(errorMap) {
        this._errorFactory = new ErrorFactory('auth', 'Firebase', errorMap());
    }
    onAuthStateChanged(nextOrObserver, error, completed) {
        return this.registerStateListener(this.authStateSubscription, nextOrObserver, error, completed);
    }
    beforeAuthStateChanged(callback, onAbort) {
        return this.beforeStateQueue.pushCallback(callback, onAbort);
    }
    onIdTokenChanged(nextOrObserver, error, completed) {
        return this.registerStateListener(this.idTokenSubscription, nextOrObserver, error, completed);
    }
    authStateReady() {
        return new Promise((resolve, reject) => {
            if (this.currentUser) {
                resolve();
            }
            else {
                const unsubscribe = this.onAuthStateChanged(() => {
                    unsubscribe();
                    resolve();
                }, reject);
            }
        });
    }
    /**
     * Revokes the given access token. Currently only supports Apple OAuth access tokens.
     */
    async revokeAccessToken(token) {
        if (this.currentUser) {
            const idToken = await this.currentUser.getIdToken();
            // Generalize this to accept other providers once supported.
            const request = {
                providerId: 'apple.com',
                tokenType: "ACCESS_TOKEN" /* TokenType.ACCESS_TOKEN */,
                token,
                idToken
            };
            if (this.tenantId != null) {
                request.tenantId = this.tenantId;
            }
            await revokeToken(this, request);
        }
    }
    toJSON() {
        var _a;
        return {
            apiKey: this.config.apiKey,
            authDomain: this.config.authDomain,
            appName: this.name,
            currentUser: (_a = this._currentUser) === null || _a === void 0 ? void 0 : _a.toJSON()
        };
    }
    async _setRedirectUser(user, popupRedirectResolver) {
        const redirectManager = await this.getOrInitRedirectPersistenceManager(popupRedirectResolver);
        return user === null
            ? redirectManager.removeCurrentUser()
            : redirectManager.setCurrentUser(user);
    }
    async getOrInitRedirectPersistenceManager(popupRedirectResolver) {
        if (!this.redirectPersistenceManager) {
            const resolver = (popupRedirectResolver && _getInstance(popupRedirectResolver)) ||
                this._popupRedirectResolver;
            _assert(resolver, this, "argument-error" /* AuthErrorCode.ARGUMENT_ERROR */);
            this.redirectPersistenceManager = await PersistenceUserManager.create(this, [_getInstance(resolver._redirectPersistence)], "redirectUser" /* KeyName.REDIRECT_USER */);
            this.redirectUser =
                await this.redirectPersistenceManager.getCurrentUser();
        }
        return this.redirectPersistenceManager;
    }
    async _redirectUserForId(id) {
        var _a, _b;
        // Make sure we've cleared any pending persistence actions if we're not in
        // the initializer
        if (this._isInitialized) {
            await this.queue(async () => { });
        }
        if (((_a = this._currentUser) === null || _a === void 0 ? void 0 : _a._redirectEventId) === id) {
            return this._currentUser;
        }
        if (((_b = this.redirectUser) === null || _b === void 0 ? void 0 : _b._redirectEventId) === id) {
            return this.redirectUser;
        }
        return null;
    }
    async _persistUserIfCurrent(user) {
        if (user === this.currentUser) {
            return this.queue(async () => this.directlySetCurrentUser(user));
        }
    }
    /** Notifies listeners only if the user is current */
    _notifyListenersIfCurrent(user) {
        if (user === this.currentUser) {
            this.notifyAuthListeners();
        }
    }
    _key() {
        return `${this.config.authDomain}:${this.config.apiKey}:${this.name}`;
    }
    _startProactiveRefresh() {
        this.isProactiveRefreshEnabled = true;
        if (this.currentUser) {
            this._currentUser._startProactiveRefresh();
        }
    }
    _stopProactiveRefresh() {
        this.isProactiveRefreshEnabled = false;
        if (this.currentUser) {
            this._currentUser._stopProactiveRefresh();
        }
    }
    /** Returns the current user cast as the internal type */
    get _currentUser() {
        return this.currentUser;
    }
    notifyAuthListeners() {
        var _a, _b;
        if (!this._isInitialized) {
            return;
        }
        this.idTokenSubscription.next(this.currentUser);
        const currentUid = (_b = (_a = this.currentUser) === null || _a === void 0 ? void 0 : _a.uid) !== null && _b !== void 0 ? _b : null;
        if (this.lastNotifiedUid !== currentUid) {
            this.lastNotifiedUid = currentUid;
            this.authStateSubscription.next(this.currentUser);
        }
    }
    registerStateListener(subscription, nextOrObserver, error, completed) {
        if (this._deleted) {
            return () => { };
        }
        const cb = typeof nextOrObserver === 'function'
            ? nextOrObserver
            : nextOrObserver.next.bind(nextOrObserver);
        let isUnsubscribed = false;
        const promise = this._isInitialized
            ? Promise.resolve()
            : this._initializationPromise;
        _assert(promise, this, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        // The callback needs to be called asynchronously per the spec.
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        promise.then(() => {
            if (isUnsubscribed) {
                return;
            }
            cb(this.currentUser);
        });
        if (typeof nextOrObserver === 'function') {
            const unsubscribe = subscription.addObserver(nextOrObserver, error, completed);
            return () => {
                isUnsubscribed = true;
                unsubscribe();
            };
        }
        else {
            const unsubscribe = subscription.addObserver(nextOrObserver);
            return () => {
                isUnsubscribed = true;
                unsubscribe();
            };
        }
    }
    /**
     * Unprotected (from race conditions) method to set the current user. This
     * should only be called from within a queued callback. This is necessary
     * because the queue shouldn't rely on another queued callback.
     */
    async directlySetCurrentUser(user) {
        if (this.currentUser && this.currentUser !== user) {
            this._currentUser._stopProactiveRefresh();
        }
        if (user && this.isProactiveRefreshEnabled) {
            user._startProactiveRefresh();
        }
        this.currentUser = user;
        if (user) {
            await this.assertedPersistence.setCurrentUser(user);
        }
        else {
            await this.assertedPersistence.removeCurrentUser();
        }
    }
    queue(action) {
        // In case something errors, the callback still should be called in order
        // to keep the promise chain alive
        this.operations = this.operations.then(action, action);
        return this.operations;
    }
    get assertedPersistence() {
        _assert(this.persistenceManager, this, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        return this.persistenceManager;
    }
    _logFramework(framework) {
        if (!framework || this.frameworks.includes(framework)) {
            return;
        }
        this.frameworks.push(framework);
        // Sort alphabetically so that "FirebaseCore-web,FirebaseUI-web" and
        // "FirebaseUI-web,FirebaseCore-web" aren't viewed as different.
        this.frameworks.sort();
        this.clientVersion = _getClientVersion(this.config.clientPlatform, this._getFrameworks());
    }
    _getFrameworks() {
        return this.frameworks;
    }
    async _getAdditionalHeaders() {
        var _a;
        // Additional headers on every request
        const headers = {
            ["X-Client-Version" /* HttpHeader.X_CLIENT_VERSION */]: this.clientVersion
        };
        if (this.app.options.appId) {
            headers["X-Firebase-gmpid" /* HttpHeader.X_FIREBASE_GMPID */] = this.app.options.appId;
        }
        // If the heartbeat service exists, add the heartbeat string
        const heartbeatsHeader = await ((_a = this.heartbeatServiceProvider
            .getImmediate({
            optional: true
        })) === null || _a === void 0 ? void 0 : _a.getHeartbeatsHeader());
        if (heartbeatsHeader) {
            headers["X-Firebase-Client" /* HttpHeader.X_FIREBASE_CLIENT */] = heartbeatsHeader;
        }
        // If the App Check service exists, add the App Check token in the headers
        const appCheckToken = await this._getAppCheckToken();
        if (appCheckToken) {
            headers["X-Firebase-AppCheck" /* HttpHeader.X_FIREBASE_APP_CHECK */] = appCheckToken;
        }
        return headers;
    }
    async _getAppCheckToken() {
        var _a;
        const appCheckTokenResult = await ((_a = this.appCheckServiceProvider
            .getImmediate({ optional: true })) === null || _a === void 0 ? void 0 : _a.getToken());
        if (appCheckTokenResult === null || appCheckTokenResult === void 0 ? void 0 : appCheckTokenResult.error) {
            // Context: appCheck.getToken() will never throw even if an error happened.
            // In the error case, a dummy token will be returned along with an error field describing
            // the error. In general, we shouldn't care about the error condition and just use
            // the token (actual or dummy) to send requests.
            _logWarn(`Error while retrieving App Check token: ${appCheckTokenResult.error}`);
        }
        return appCheckTokenResult === null || appCheckTokenResult === void 0 ? void 0 : appCheckTokenResult.token;
    }
}
/**
 * Method to be used to cast down to our private implmentation of Auth.
 * It will also handle unwrapping from the compat type if necessary
 *
 * @param auth Auth object passed in from developer
 */
function _castAuth(auth) {
    return getModularInstance(auth);
}
/** Helper class to wrap subscriber logic */
class Subscription {
    constructor(auth) {
        this.auth = auth;
        this.observer = null;
        this.addObserver = createSubscribe(observer => (this.observer = observer));
    }
    get next() {
        _assert(this.observer, this.auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        return this.observer.next.bind(this.observer);
    }
}

/**
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
 */
let externalJSProvider = {
    async loadJS() {
        throw new Error('Unable to load external scripts');
    },
    recaptchaV2Script: '',
    recaptchaEnterpriseScript: '',
    gapiScript: ''
};
function _setExternalJSProvider(p) {
    externalJSProvider = p;
}
function _loadJS(url) {
    return externalJSProvider.loadJS(url);
}
function _recaptchaEnterpriseScriptUrl() {
    return externalJSProvider.recaptchaEnterpriseScript;
}
function _gapiScriptUrl() {
    return externalJSProvider.gapiScript;
}
function _generateCallbackName(prefix) {
    return `__${prefix}${Math.floor(Math.random() * 1000000)}`;
}

/* eslint-disable @typescript-eslint/no-require-imports */
const RECAPTCHA_ENTERPRISE_VERIFIER_TYPE = 'recaptcha-enterprise';
const FAKE_TOKEN = 'NO_RECAPTCHA';
class RecaptchaEnterpriseVerifier {
    /**
     *
     * @param authExtern - The corresponding Firebase {@link Auth} instance.
     *
     */
    constructor(authExtern) {
        /**
         * Identifies the type of application verifier (e.g. "recaptcha-enterprise").
         */
        this.type = RECAPTCHA_ENTERPRISE_VERIFIER_TYPE;
        this.auth = _castAuth(authExtern);
    }
    /**
     * Executes the verification process.
     *
     * @returns A Promise for a token that can be used to assert the validity of a request.
     */
    async verify(action = 'verify', forceRefresh = false) {
        async function retrieveSiteKey(auth) {
            if (!forceRefresh) {
                if (auth.tenantId == null && auth._agentRecaptchaConfig != null) {
                    return auth._agentRecaptchaConfig.siteKey;
                }
                if (auth.tenantId != null &&
                    auth._tenantRecaptchaConfigs[auth.tenantId] !== undefined) {
                    return auth._tenantRecaptchaConfigs[auth.tenantId].siteKey;
                }
            }
            return new Promise(async (resolve, reject) => {
                getRecaptchaConfig(auth, {
                    clientType: "CLIENT_TYPE_WEB" /* RecaptchaClientType.WEB */,
                    version: "RECAPTCHA_ENTERPRISE" /* RecaptchaVersion.ENTERPRISE */
                })
                    .then(response => {
                    if (response.recaptchaKey === undefined) {
                        reject(new Error('recaptcha Enterprise site key undefined'));
                    }
                    else {
                        const config = new RecaptchaConfig(response);
                        if (auth.tenantId == null) {
                            auth._agentRecaptchaConfig = config;
                        }
                        else {
                            auth._tenantRecaptchaConfigs[auth.tenantId] = config;
                        }
                        return resolve(config.siteKey);
                    }
                })
                    .catch(error => {
                    reject(error);
                });
            });
        }
        function retrieveRecaptchaToken(siteKey, resolve, reject) {
            const grecaptcha = window.grecaptcha;
            if (isEnterprise(grecaptcha)) {
                grecaptcha.enterprise.ready(() => {
                    grecaptcha.enterprise
                        .execute(siteKey, { action })
                        .then(token => {
                        resolve(token);
                    })
                        .catch(() => {
                        resolve(FAKE_TOKEN);
                    });
                });
            }
            else {
                reject(Error('No reCAPTCHA enterprise script loaded.'));
            }
        }
        return new Promise((resolve, reject) => {
            retrieveSiteKey(this.auth)
                .then(siteKey => {
                if (!forceRefresh && isEnterprise(window.grecaptcha)) {
                    retrieveRecaptchaToken(siteKey, resolve, reject);
                }
                else {
                    if (typeof window === 'undefined') {
                        reject(new Error('RecaptchaVerifier is only supported in browser'));
                        return;
                    }
                    let url = _recaptchaEnterpriseScriptUrl();
                    if (url.length !== 0) {
                        url += siteKey;
                    }
                    _loadJS(url)
                        .then(() => {
                        retrieveRecaptchaToken(siteKey, resolve, reject);
                    })
                        .catch(error => {
                        reject(error);
                    });
                }
            })
                .catch(error => {
                reject(error);
            });
        });
    }
}
async function injectRecaptchaFields(auth, request, action, captchaResp = false) {
    const verifier = new RecaptchaEnterpriseVerifier(auth);
    let captchaResponse;
    try {
        captchaResponse = await verifier.verify(action);
    }
    catch (error) {
        captchaResponse = await verifier.verify(action, true);
    }
    const newRequest = Object.assign({}, request);
    if (!captchaResp) {
        Object.assign(newRequest, { captchaResponse });
    }
    else {
        Object.assign(newRequest, { 'captchaResp': captchaResponse });
    }
    Object.assign(newRequest, { 'clientType': "CLIENT_TYPE_WEB" /* RecaptchaClientType.WEB */ });
    Object.assign(newRequest, {
        'recaptchaVersion': "RECAPTCHA_ENTERPRISE" /* RecaptchaVersion.ENTERPRISE */
    });
    return newRequest;
}
async function handleRecaptchaFlow(authInstance, request, actionName, actionMethod) {
    var _a;
    if ((_a = authInstance
        ._getRecaptchaConfig()) === null || _a === void 0 ? void 0 : _a.isProviderEnabled("EMAIL_PASSWORD_PROVIDER" /* RecaptchaProvider.EMAIL_PASSWORD_PROVIDER */)) {
        const requestWithRecaptcha = await injectRecaptchaFields(authInstance, request, actionName, actionName === "getOobCode" /* RecaptchaActionName.GET_OOB_CODE */);
        return actionMethod(authInstance, requestWithRecaptcha);
    }
    else {
        return actionMethod(authInstance, request).catch(async (error) => {
            if (error.code === `auth/${"missing-recaptcha-token" /* AuthErrorCode.MISSING_RECAPTCHA_TOKEN */}`) {
                console.log(`${actionName} is protected by reCAPTCHA Enterprise for this project. Automatically triggering the reCAPTCHA flow and restarting the flow.`);
                const requestWithRecaptcha = await injectRecaptchaFields(authInstance, request, actionName, actionName === "getOobCode" /* RecaptchaActionName.GET_OOB_CODE */);
                return actionMethod(authInstance, requestWithRecaptcha);
            }
            else {
                return Promise.reject(error);
            }
        });
    }
}

/**
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
 */
/**
 * Initializes an {@link Auth} instance with fine-grained control over
 * {@link Dependencies}.
 *
 * @remarks
 *
 * This function allows more control over the {@link Auth} instance than
 * {@link getAuth}. `getAuth` uses platform-specific defaults to supply
 * the {@link Dependencies}. In general, `getAuth` is the easiest way to
 * initialize Auth and works for most use cases. Use `initializeAuth` if you
 * need control over which persistence layer is used, or to minimize bundle
 * size if you're not using either `signInWithPopup` or `signInWithRedirect`.
 *
 * For example, if your app only uses anonymous accounts and you only want
 * accounts saved for the current session, initialize `Auth` with:
 *
 * ```js
 * const auth = initializeAuth(app, {
 *   persistence: browserSessionPersistence,
 *   popupRedirectResolver: undefined,
 * });
 * ```
 *
 * @public
 */
function initializeAuth(app, deps) {
    const provider = _getProvider(app, 'auth');
    if (provider.isInitialized()) {
        const auth = provider.getImmediate();
        const initialOptions = provider.getOptions();
        if (deepEqual(initialOptions, deps !== null && deps !== void 0 ? deps : {})) {
            return auth;
        }
        else {
            _fail(auth, "already-initialized" /* AuthErrorCode.ALREADY_INITIALIZED */);
        }
    }
    const auth = provider.initialize({ options: deps });
    return auth;
}
function _initializeAuthInstance(auth, deps) {
    const persistence = (deps === null || deps === void 0 ? void 0 : deps.persistence) || [];
    const hierarchy = (Array.isArray(persistence) ? persistence : [persistence]).map(_getInstance);
    if (deps === null || deps === void 0 ? void 0 : deps.errorMap) {
        auth._updateErrorMap(deps.errorMap);
    }
    // This promise is intended to float; auth initialization happens in the
    // background, meanwhile the auth object may be used by the app.
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    auth._initializeWithPersistence(hierarchy, deps === null || deps === void 0 ? void 0 : deps.popupRedirectResolver);
}

/**
 * Changes the {@link Auth} instance to communicate with the Firebase Auth Emulator, instead of production
 * Firebase Auth services.
 *
 * @remarks
 * This must be called synchronously immediately following the first call to
 * {@link initializeAuth}.  Do not use with production credentials as emulator
 * traffic is not encrypted.
 *
 *
 * @example
 * ```javascript
 * connectAuthEmulator(auth, 'http://127.0.0.1:9099', { disableWarnings: true });
 * ```
 *
 * @param auth - The {@link Auth} instance.
 * @param url - The URL at which the emulator is running (eg, 'http://localhost:9099').
 * @param options - Optional. `options.disableWarnings` defaults to `false`. Set it to
 * `true` to disable the warning banner attached to the DOM.
 *
 * @public
 */
function connectAuthEmulator(auth, url, options) {
    const authInternal = _castAuth(auth);
    _assert(authInternal._canInitEmulator, authInternal, "emulator-config-failed" /* AuthErrorCode.EMULATOR_CONFIG_FAILED */);
    _assert(/^https?:\/\//.test(url), authInternal, "invalid-emulator-scheme" /* AuthErrorCode.INVALID_EMULATOR_SCHEME */);
    const disableWarnings = !!(options === null || options === void 0 ? void 0 : options.disableWarnings);
    const protocol = extractProtocol(url);
    const { host, port } = extractHostAndPort(url);
    const portStr = port === null ? '' : `:${port}`;
    // Always replace path with "/" (even if input url had no path at all, or had a different one).
    authInternal.config.emulator = { url: `${protocol}//${host}${portStr}/` };
    authInternal.settings.appVerificationDisabledForTesting = true;
    authInternal.emulatorConfig = Object.freeze({
        host,
        port,
        protocol: protocol.replace(':', ''),
        options: Object.freeze({ disableWarnings })
    });
    if (!disableWarnings) {
        emitEmulatorWarning();
    }
}
function extractProtocol(url) {
    const protocolEnd = url.indexOf(':');
    return protocolEnd < 0 ? '' : url.substr(0, protocolEnd + 1);
}
function extractHostAndPort(url) {
    const protocol = extractProtocol(url);
    const authority = /(\/\/)?([^?#/]+)/.exec(url.substr(protocol.length)); // Between // and /, ? or #.
    if (!authority) {
        return { host: '', port: null };
    }
    const hostAndPort = authority[2].split('@').pop() || ''; // Strip out "username:password@".
    const bracketedIPv6 = /^(\[[^\]]+\])(:|$)/.exec(hostAndPort);
    if (bracketedIPv6) {
        const host = bracketedIPv6[1];
        return { host, port: parsePort(hostAndPort.substr(host.length + 1)) };
    }
    else {
        const [host, port] = hostAndPort.split(':');
        return { host, port: parsePort(port) };
    }
}
function parsePort(portStr) {
    if (!portStr) {
        return null;
    }
    const port = Number(portStr);
    if (isNaN(port)) {
        return null;
    }
    return port;
}
function emitEmulatorWarning() {
    function attachBanner() {
        const el = document.createElement('p');
        const sty = el.style;
        el.innerText =
            'Running in emulator mode. Do not use with production credentials.';
        sty.position = 'fixed';
        sty.width = '100%';
        sty.backgroundColor = '#ffffff';
        sty.border = '.1em solid #000000';
        sty.color = '#b50000';
        sty.bottom = '0px';
        sty.left = '0px';
        sty.margin = '0px';
        sty.zIndex = '10000';
        sty.textAlign = 'center';
        el.classList.add('firebase-emulator-warning');
        document.body.appendChild(el);
    }
    if (typeof console !== 'undefined' && typeof console.info === 'function') {
        console.info('WARNING: You are using the Auth Emulator,' +
            ' which is intended for local testing only.  Do not use with' +
            ' production credentials.');
    }
    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            window.addEventListener('DOMContentLoaded', attachBanner);
        }
        else {
            attachBanner();
        }
    }
}

/**
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
 */
/**
 * Interface that represents the credentials returned by an {@link AuthProvider}.
 *
 * @remarks
 * Implementations specify the details about each auth provider's credential requirements.
 *
 * @public
 */
class AuthCredential {
    /** @internal */
    constructor(
    /**
     * The authentication provider ID for the credential.
     *
     * @remarks
     * For example, 'facebook.com', or 'google.com'.
     */
    providerId, 
    /**
     * The authentication sign in method for the credential.
     *
     * @remarks
     * For example, {@link SignInMethod}.EMAIL_PASSWORD, or
     * {@link SignInMethod}.EMAIL_LINK. This corresponds to the sign-in method
     * identifier as returned in {@link fetchSignInMethodsForEmail}.
     */
    signInMethod) {
        this.providerId = providerId;
        this.signInMethod = signInMethod;
    }
    /**
     * Returns a JSON-serializable representation of this object.
     *
     * @returns a JSON-serializable representation of this object.
     */
    toJSON() {
        return debugFail('not implemented');
    }
    /** @internal */
    _getIdTokenResponse(_auth) {
        return debugFail('not implemented');
    }
    /** @internal */
    _linkToIdToken(_auth, _idToken) {
        return debugFail('not implemented');
    }
    /** @internal */
    _getReauthenticationResolver(_auth) {
        return debugFail('not implemented');
    }
}
// Used for linking an email/password account to an existing idToken. Uses the same request/response
// format as updateEmailPassword.
async function linkEmailPassword(auth, request) {
    return _performApiRequest(auth, "POST" /* HttpMethod.POST */, "/v1/accounts:signUp" /* Endpoint.SIGN_UP */, request);
}

/**
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
 */
async function signInWithPassword(auth, request) {
    return _performSignInRequest(auth, "POST" /* HttpMethod.POST */, "/v1/accounts:signInWithPassword" /* Endpoint.SIGN_IN_WITH_PASSWORD */, _addTidIfNecessary(auth, request));
}
async function sendOobCode(auth, request) {
    return _performApiRequest(auth, "POST" /* HttpMethod.POST */, "/v1/accounts:sendOobCode" /* Endpoint.SEND_OOB_CODE */, _addTidIfNecessary(auth, request));
}
async function sendPasswordResetEmail$1(auth, request) {
    return sendOobCode(auth, request);
}
async function sendSignInLinkToEmail$1(auth, request) {
    return sendOobCode(auth, request);
}

/**
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
 */
async function signInWithEmailLink$1(auth, request) {
    return _performSignInRequest(auth, "POST" /* HttpMethod.POST */, "/v1/accounts:signInWithEmailLink" /* Endpoint.SIGN_IN_WITH_EMAIL_LINK */, _addTidIfNecessary(auth, request));
}
async function signInWithEmailLinkForLinking(auth, request) {
    return _performSignInRequest(auth, "POST" /* HttpMethod.POST */, "/v1/accounts:signInWithEmailLink" /* Endpoint.SIGN_IN_WITH_EMAIL_LINK */, _addTidIfNecessary(auth, request));
}

/**
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
 */
/**
 * Interface that represents the credentials returned by {@link EmailAuthProvider} for
 * {@link ProviderId}.PASSWORD
 *
 * @remarks
 * Covers both {@link SignInMethod}.EMAIL_PASSWORD and
 * {@link SignInMethod}.EMAIL_LINK.
 *
 * @public
 */
class EmailAuthCredential extends AuthCredential {
    /** @internal */
    constructor(
    /** @internal */
    _email, 
    /** @internal */
    _password, signInMethod, 
    /** @internal */
    _tenantId = null) {
        super("password" /* ProviderId.PASSWORD */, signInMethod);
        this._email = _email;
        this._password = _password;
        this._tenantId = _tenantId;
    }
    /** @internal */
    static _fromEmailAndPassword(email, password) {
        return new EmailAuthCredential(email, password, "password" /* SignInMethod.EMAIL_PASSWORD */);
    }
    /** @internal */
    static _fromEmailAndCode(email, oobCode, tenantId = null) {
        return new EmailAuthCredential(email, oobCode, "emailLink" /* SignInMethod.EMAIL_LINK */, tenantId);
    }
    /** {@inheritdoc AuthCredential.toJSON} */
    toJSON() {
        return {
            email: this._email,
            password: this._password,
            signInMethod: this.signInMethod,
            tenantId: this._tenantId
        };
    }
    /**
     * Static method to deserialize a JSON representation of an object into an {@link  AuthCredential}.
     *
     * @param json - Either `object` or the stringified representation of the object. When string is
     * provided, `JSON.parse` would be called first.
     *
     * @returns If the JSON input does not represent an {@link AuthCredential}, null is returned.
     */
    static fromJSON(json) {
        const obj = typeof json === 'string' ? JSON.parse(json) : json;
        if ((obj === null || obj === void 0 ? void 0 : obj.email) && (obj === null || obj === void 0 ? void 0 : obj.password)) {
            if (obj.signInMethod === "password" /* SignInMethod.EMAIL_PASSWORD */) {
                return this._fromEmailAndPassword(obj.email, obj.password);
            }
            else if (obj.signInMethod === "emailLink" /* SignInMethod.EMAIL_LINK */) {
                return this._fromEmailAndCode(obj.email, obj.password, obj.tenantId);
            }
        }
        return null;
    }
    /** @internal */
    async _getIdTokenResponse(auth) {
        switch (this.signInMethod) {
            case "password" /* SignInMethod.EMAIL_PASSWORD */:
                const request = {
                    returnSecureToken: true,
                    email: this._email,
                    password: this._password,
                    clientType: "CLIENT_TYPE_WEB" /* RecaptchaClientType.WEB */
                };
                return handleRecaptchaFlow(auth, request, "signInWithPassword" /* RecaptchaActionName.SIGN_IN_WITH_PASSWORD */, signInWithPassword);
            case "emailLink" /* SignInMethod.EMAIL_LINK */:
                return signInWithEmailLink$1(auth, {
                    email: this._email,
                    oobCode: this._password
                });
            default:
                _fail(auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        }
    }
    /** @internal */
    async _linkToIdToken(auth, idToken) {
        switch (this.signInMethod) {
            case "password" /* SignInMethod.EMAIL_PASSWORD */:
                const request = {
                    idToken,
                    returnSecureToken: true,
                    email: this._email,
                    password: this._password,
                    clientType: "CLIENT_TYPE_WEB" /* RecaptchaClientType.WEB */
                };
                return handleRecaptchaFlow(auth, request, "signUpPassword" /* RecaptchaActionName.SIGN_UP_PASSWORD */, linkEmailPassword);
            case "emailLink" /* SignInMethod.EMAIL_LINK */:
                return signInWithEmailLinkForLinking(auth, {
                    idToken,
                    email: this._email,
                    oobCode: this._password
                });
            default:
                _fail(auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        }
    }
    /** @internal */
    _getReauthenticationResolver(auth) {
        return this._getIdTokenResponse(auth);
    }
}

/**
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
 */
async function signInWithIdp(auth, request) {
    return _performSignInRequest(auth, "POST" /* HttpMethod.POST */, "/v1/accounts:signInWithIdp" /* Endpoint.SIGN_IN_WITH_IDP */, _addTidIfNecessary(auth, request));
}

/**
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
 */
const IDP_REQUEST_URI$1 = 'http://localhost';
/**
 * Represents the OAuth credentials returned by an {@link OAuthProvider}.
 *
 * @remarks
 * Implementations specify the details about each auth provider's credential requirements.
 *
 * @public
 */
class OAuthCredential extends AuthCredential {
    constructor() {
        super(...arguments);
        this.pendingToken = null;
    }
    /** @internal */
    static _fromParams(params) {
        const cred = new OAuthCredential(params.providerId, params.signInMethod);
        if (params.idToken || params.accessToken) {
            // OAuth 2 and either ID token or access token.
            if (params.idToken) {
                cred.idToken = params.idToken;
            }
            if (params.accessToken) {
                cred.accessToken = params.accessToken;
            }
            // Add nonce if available and no pendingToken is present.
            if (params.nonce && !params.pendingToken) {
                cred.nonce = params.nonce;
            }
            if (params.pendingToken) {
                cred.pendingToken = params.pendingToken;
            }
        }
        else if (params.oauthToken && params.oauthTokenSecret) {
            // OAuth 1 and OAuth token with token secret
            cred.accessToken = params.oauthToken;
            cred.secret = params.oauthTokenSecret;
        }
        else {
            _fail("argument-error" /* AuthErrorCode.ARGUMENT_ERROR */);
        }
        return cred;
    }
    /** {@inheritdoc AuthCredential.toJSON}  */
    toJSON() {
        return {
            idToken: this.idToken,
            accessToken: this.accessToken,
            secret: this.secret,
            nonce: this.nonce,
            pendingToken: this.pendingToken,
            providerId: this.providerId,
            signInMethod: this.signInMethod
        };
    }
    /**
     * Static method to deserialize a JSON representation of an object into an
     * {@link  AuthCredential}.
     *
     * @param json - Input can be either Object or the stringified representation of the object.
     * When string is provided, JSON.parse would be called first.
     *
     * @returns If the JSON input does not represent an {@link  AuthCredential}, null is returned.
     */
    static fromJSON(json) {
        const obj = typeof json === 'string' ? JSON.parse(json) : json;
        const { providerId, signInMethod } = obj, rest = __rest(obj, ["providerId", "signInMethod"]);
        if (!providerId || !signInMethod) {
            return null;
        }
        const cred = new OAuthCredential(providerId, signInMethod);
        cred.idToken = rest.idToken || undefined;
        cred.accessToken = rest.accessToken || undefined;
        cred.secret = rest.secret;
        cred.nonce = rest.nonce;
        cred.pendingToken = rest.pendingToken || null;
        return cred;
    }
    /** @internal */
    _getIdTokenResponse(auth) {
        const request = this.buildRequest();
        return signInWithIdp(auth, request);
    }
    /** @internal */
    _linkToIdToken(auth, idToken) {
        const request = this.buildRequest();
        request.idToken = idToken;
        return signInWithIdp(auth, request);
    }
    /** @internal */
    _getReauthenticationResolver(auth) {
        const request = this.buildRequest();
        request.autoCreate = false;
        return signInWithIdp(auth, request);
    }
    buildRequest() {
        const request = {
            requestUri: IDP_REQUEST_URI$1,
            returnSecureToken: true
        };
        if (this.pendingToken) {
            request.pendingToken = this.pendingToken;
        }
        else {
            const postBody = {};
            if (this.idToken) {
                postBody['id_token'] = this.idToken;
            }
            if (this.accessToken) {
                postBody['access_token'] = this.accessToken;
            }
            if (this.secret) {
                postBody['oauth_token_secret'] = this.secret;
            }
            postBody['providerId'] = this.providerId;
            if (this.nonce && !this.pendingToken) {
                postBody['nonce'] = this.nonce;
            }
            request.postBody = querystring(postBody);
        }
        return request;
    }
}

/**
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
 */
/**
 * Maps the mode string in action code URL to Action Code Info operation.
 *
 * @param mode
 */
function parseMode(mode) {
    switch (mode) {
        case 'recoverEmail':
            return "RECOVER_EMAIL" /* ActionCodeOperation.RECOVER_EMAIL */;
        case 'resetPassword':
            return "PASSWORD_RESET" /* ActionCodeOperation.PASSWORD_RESET */;
        case 'signIn':
            return "EMAIL_SIGNIN" /* ActionCodeOperation.EMAIL_SIGNIN */;
        case 'verifyEmail':
            return "VERIFY_EMAIL" /* ActionCodeOperation.VERIFY_EMAIL */;
        case 'verifyAndChangeEmail':
            return "VERIFY_AND_CHANGE_EMAIL" /* ActionCodeOperation.VERIFY_AND_CHANGE_EMAIL */;
        case 'revertSecondFactorAddition':
            return "REVERT_SECOND_FACTOR_ADDITION" /* ActionCodeOperation.REVERT_SECOND_FACTOR_ADDITION */;
        default:
            return null;
    }
}
/**
 * Helper to parse FDL links
 *
 * @param url
 */
function parseDeepLink(url) {
    const link = querystringDecode(extractQuerystring(url))['link'];
    // Double link case (automatic redirect).
    const doubleDeepLink = link
        ? querystringDecode(extractQuerystring(link))['deep_link_id']
        : null;
    // iOS custom scheme links.
    const iOSDeepLink = querystringDecode(extractQuerystring(url))['deep_link_id'];
    const iOSDoubleDeepLink = iOSDeepLink
        ? querystringDecode(extractQuerystring(iOSDeepLink))['link']
        : null;
    return iOSDoubleDeepLink || iOSDeepLink || doubleDeepLink || link || url;
}
/**
 * A utility class to parse email action URLs such as password reset, email verification,
 * email link sign in, etc.
 *
 * @public
 */
class ActionCodeURL {
    /**
     * @param actionLink - The link from which to extract the URL.
     * @returns The {@link ActionCodeURL} object, or null if the link is invalid.
     *
     * @internal
     */
    constructor(actionLink) {
        var _a, _b, _c, _d, _e, _f;
        const searchParams = querystringDecode(extractQuerystring(actionLink));
        const apiKey = (_a = searchParams["apiKey" /* QueryField.API_KEY */]) !== null && _a !== void 0 ? _a : null;
        const code = (_b = searchParams["oobCode" /* QueryField.CODE */]) !== null && _b !== void 0 ? _b : null;
        const operation = parseMode((_c = searchParams["mode" /* QueryField.MODE */]) !== null && _c !== void 0 ? _c : null);
        // Validate API key, code and mode.
        _assert(apiKey && code && operation, "argument-error" /* AuthErrorCode.ARGUMENT_ERROR */);
        this.apiKey = apiKey;
        this.operation = operation;
        this.code = code;
        this.continueUrl = (_d = searchParams["continueUrl" /* QueryField.CONTINUE_URL */]) !== null && _d !== void 0 ? _d : null;
        this.languageCode = (_e = searchParams["languageCode" /* QueryField.LANGUAGE_CODE */]) !== null && _e !== void 0 ? _e : null;
        this.tenantId = (_f = searchParams["tenantId" /* QueryField.TENANT_ID */]) !== null && _f !== void 0 ? _f : null;
    }
    /**
     * Parses the email action link string and returns an {@link ActionCodeURL} if the link is valid,
     * otherwise returns null.
     *
     * @param link  - The email action link string.
     * @returns The {@link ActionCodeURL} object, or null if the link is invalid.
     *
     * @public
     */
    static parseLink(link) {
        const actionLink = parseDeepLink(link);
        try {
            return new ActionCodeURL(actionLink);
        }
        catch (_a) {
            return null;
        }
    }
}

/**
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
 */
/**
 * Provider for generating {@link EmailAuthCredential}.
 *
 * @public
 */
class EmailAuthProvider {
    constructor() {
        /**
         * Always set to {@link ProviderId}.PASSWORD, even for email link.
         */
        this.providerId = EmailAuthProvider.PROVIDER_ID;
    }
    /**
     * Initialize an {@link AuthCredential} using an email and password.
     *
     * @example
     * ```javascript
     * const authCredential = EmailAuthProvider.credential(email, password);
     * const userCredential = await signInWithCredential(auth, authCredential);
     * ```
     *
     * @example
     * ```javascript
     * const userCredential = await signInWithEmailAndPassword(auth, email, password);
     * ```
     *
     * @param email - Email address.
     * @param password - User account password.
     * @returns The auth provider credential.
     */
    static credential(email, password) {
        return EmailAuthCredential._fromEmailAndPassword(email, password);
    }
    /**
     * Initialize an {@link AuthCredential} using an email and an email link after a sign in with
     * email link operation.
     *
     * @example
     * ```javascript
     * const authCredential = EmailAuthProvider.credentialWithLink(auth, email, emailLink);
     * const userCredential = await signInWithCredential(auth, authCredential);
     * ```
     *
     * @example
     * ```javascript
     * await sendSignInLinkToEmail(auth, email);
     * // Obtain emailLink from user.
     * const userCredential = await signInWithEmailLink(auth, email, emailLink);
     * ```
     *
     * @param auth - The {@link Auth} instance used to verify the link.
     * @param email - Email address.
     * @param emailLink - Sign-in email link.
     * @returns - The auth provider credential.
     */
    static credentialWithLink(email, emailLink) {
        const actionCodeUrl = ActionCodeURL.parseLink(emailLink);
        _assert(actionCodeUrl, "argument-error" /* AuthErrorCode.ARGUMENT_ERROR */);
        return EmailAuthCredential._fromEmailAndCode(email, actionCodeUrl.code, actionCodeUrl.tenantId);
    }
}
/**
 * Always set to {@link ProviderId}.PASSWORD, even for email link.
 */
EmailAuthProvider.PROVIDER_ID = "password" /* ProviderId.PASSWORD */;
/**
 * Always set to {@link SignInMethod}.EMAIL_PASSWORD.
 */
EmailAuthProvider.EMAIL_PASSWORD_SIGN_IN_METHOD = "password" /* SignInMethod.EMAIL_PASSWORD */;
/**
 * Always set to {@link SignInMethod}.EMAIL_LINK.
 */
EmailAuthProvider.EMAIL_LINK_SIGN_IN_METHOD = "emailLink" /* SignInMethod.EMAIL_LINK */;

/**
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
 */
/**
 * The base class for all Federated providers (OAuth (including OIDC), SAML).
 *
 * This class is not meant to be instantiated directly.
 *
 * @public
 */
class FederatedAuthProvider {
    /**
     * Constructor for generic OAuth providers.
     *
     * @param providerId - Provider for which credentials should be generated.
     */
    constructor(providerId) {
        this.providerId = providerId;
        /** @internal */
        this.defaultLanguageCode = null;
        /** @internal */
        this.customParameters = {};
    }
    /**
     * Set the language gode.
     *
     * @param languageCode - language code
     */
    setDefaultLanguage(languageCode) {
        this.defaultLanguageCode = languageCode;
    }
    /**
     * Sets the OAuth custom parameters to pass in an OAuth request for popup and redirect sign-in
     * operations.
     *
     * @remarks
     * For a detailed list, check the reserved required OAuth 2.0 parameters such as `client_id`,
     * `redirect_uri`, `scope`, `response_type`, and `state` are not allowed and will be ignored.
     *
     * @param customOAuthParameters - The custom OAuth parameters to pass in the OAuth request.
     */
    setCustomParameters(customOAuthParameters) {
        this.customParameters = customOAuthParameters;
        return this;
    }
    /**
     * Retrieve the current list of {@link CustomParameters}.
     */
    getCustomParameters() {
        return this.customParameters;
    }
}

/**
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
 */
/**
 * Common code to all OAuth providers. This is separate from the
 * {@link OAuthProvider} so that child providers (like
 * {@link GoogleAuthProvider}) don't inherit the `credential` instance method.
 * Instead, they rely on a static `credential` method.
 */
class BaseOAuthProvider extends FederatedAuthProvider {
    constructor() {
        super(...arguments);
        /** @internal */
        this.scopes = [];
    }
    /**
     * Add an OAuth scope to the credential.
     *
     * @param scope - Provider OAuth scope to add.
     */
    addScope(scope) {
        // If not already added, add scope to list.
        if (!this.scopes.includes(scope)) {
            this.scopes.push(scope);
        }
        return this;
    }
    /**
     * Retrieve the current list of OAuth scopes.
     */
    getScopes() {
        return [...this.scopes];
    }
}

/**
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
 */
/**
 * Provider for generating an {@link OAuthCredential} for {@link ProviderId}.FACEBOOK.
 *
 * @example
 * ```javascript
 * // Sign in using a redirect.
 * const provider = new FacebookAuthProvider();
 * // Start a sign in process for an unauthenticated user.
 * provider.addScope('user_birthday');
 * await signInWithRedirect(auth, provider);
 * // This will trigger a full page redirect away from your app
 *
 * // After returning from the redirect when your app initializes you can obtain the result
 * const result = await getRedirectResult(auth);
 * if (result) {
 *   // This is the signed-in user
 *   const user = result.user;
 *   // This gives you a Facebook Access Token.
 *   const credential = FacebookAuthProvider.credentialFromResult(result);
 *   const token = credential.accessToken;
 * }
 * ```
 *
 * @example
 * ```javascript
 * // Sign in using a popup.
 * const provider = new FacebookAuthProvider();
 * provider.addScope('user_birthday');
 * const result = await signInWithPopup(auth, provider);
 *
 * // The signed-in user info.
 * const user = result.user;
 * // This gives you a Facebook Access Token.
 * const credential = FacebookAuthProvider.credentialFromResult(result);
 * const token = credential.accessToken;
 * ```
 *
 * @public
 */
class FacebookAuthProvider extends BaseOAuthProvider {
    constructor() {
        super("facebook.com" /* ProviderId.FACEBOOK */);
    }
    /**
     * Creates a credential for Facebook.
     *
     * @example
     * ```javascript
     * // `event` from the Facebook auth.authResponseChange callback.
     * const credential = FacebookAuthProvider.credential(event.authResponse.accessToken);
     * const result = await signInWithCredential(credential);
     * ```
     *
     * @param accessToken - Facebook access token.
     */
    static credential(accessToken) {
        return OAuthCredential._fromParams({
            providerId: FacebookAuthProvider.PROVIDER_ID,
            signInMethod: FacebookAuthProvider.FACEBOOK_SIGN_IN_METHOD,
            accessToken
        });
    }
    /**
     * Used to extract the underlying {@link OAuthCredential} from a {@link UserCredential}.
     *
     * @param userCredential - The user credential.
     */
    static credentialFromResult(userCredential) {
        return FacebookAuthProvider.credentialFromTaggedObject(userCredential);
    }
    /**
     * Used to extract the underlying {@link OAuthCredential} from a {@link AuthError} which was
     * thrown during a sign-in, link, or reauthenticate operation.
     *
     * @param userCredential - The user credential.
     */
    static credentialFromError(error) {
        return FacebookAuthProvider.credentialFromTaggedObject((error.customData || {}));
    }
    static credentialFromTaggedObject({ _tokenResponse: tokenResponse }) {
        if (!tokenResponse || !('oauthAccessToken' in tokenResponse)) {
            return null;
        }
        if (!tokenResponse.oauthAccessToken) {
            return null;
        }
        try {
            return FacebookAuthProvider.credential(tokenResponse.oauthAccessToken);
        }
        catch (_a) {
            return null;
        }
    }
}
/** Always set to {@link SignInMethod}.FACEBOOK. */
FacebookAuthProvider.FACEBOOK_SIGN_IN_METHOD = "facebook.com" /* SignInMethod.FACEBOOK */;
/** Always set to {@link ProviderId}.FACEBOOK. */
FacebookAuthProvider.PROVIDER_ID = "facebook.com" /* ProviderId.FACEBOOK */;

/**
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
 */
/**
 * Provider for generating an {@link OAuthCredential} for {@link ProviderId}.GOOGLE.
 *
 * @example
 * ```javascript
 * // Sign in using a redirect.
 * const provider = new GoogleAuthProvider();
 * // Start a sign in process for an unauthenticated user.
 * provider.addScope('profile');
 * provider.addScope('email');
 * await signInWithRedirect(auth, provider);
 * // This will trigger a full page redirect away from your app
 *
 * // After returning from the redirect when your app initializes you can obtain the result
 * const result = await getRedirectResult(auth);
 * if (result) {
 *   // This is the signed-in user
 *   const user = result.user;
 *   // This gives you a Google Access Token.
 *   const credential = GoogleAuthProvider.credentialFromResult(result);
 *   const token = credential.accessToken;
 * }
 * ```
 *
 * @example
 * ```javascript
 * // Sign in using a popup.
 * const provider = new GoogleAuthProvider();
 * provider.addScope('profile');
 * provider.addScope('email');
 * const result = await signInWithPopup(auth, provider);
 *
 * // The signed-in user info.
 * const user = result.user;
 * // This gives you a Google Access Token.
 * const credential = GoogleAuthProvider.credentialFromResult(result);
 * const token = credential.accessToken;
 * ```
 *
 * @public
 */
class GoogleAuthProvider extends BaseOAuthProvider {
    constructor() {
        super("google.com" /* ProviderId.GOOGLE */);
        this.addScope('profile');
    }
    /**
     * Creates a credential for Google. At least one of ID token and access token is required.
     *
     * @example
     * ```javascript
     * // \`googleUser\` from the onsuccess Google Sign In callback.
     * const credential = GoogleAuthProvider.credential(googleUser.getAuthResponse().id_token);
     * const result = await signInWithCredential(credential);
     * ```
     *
     * @param idToken - Google ID token.
     * @param accessToken - Google access token.
     */
    static credential(idToken, accessToken) {
        return OAuthCredential._fromParams({
            providerId: GoogleAuthProvider.PROVIDER_ID,
            signInMethod: GoogleAuthProvider.GOOGLE_SIGN_IN_METHOD,
            idToken,
            accessToken
        });
    }
    /**
     * Used to extract the underlying {@link OAuthCredential} from a {@link UserCredential}.
     *
     * @param userCredential - The user credential.
     */
    static credentialFromResult(userCredential) {
        return GoogleAuthProvider.credentialFromTaggedObject(userCredential);
    }
    /**
     * Used to extract the underlying {@link OAuthCredential} from a {@link AuthError} which was
     * thrown during a sign-in, link, or reauthenticate operation.
     *
     * @param userCredential - The user credential.
     */
    static credentialFromError(error) {
        return GoogleAuthProvider.credentialFromTaggedObject((error.customData || {}));
    }
    static credentialFromTaggedObject({ _tokenResponse: tokenResponse }) {
        if (!tokenResponse) {
            return null;
        }
        const { oauthIdToken, oauthAccessToken } = tokenResponse;
        if (!oauthIdToken && !oauthAccessToken) {
            // This could be an oauth 1 credential or a phone credential
            return null;
        }
        try {
            return GoogleAuthProvider.credential(oauthIdToken, oauthAccessToken);
        }
        catch (_a) {
            return null;
        }
    }
}
/** Always set to {@link SignInMethod}.GOOGLE. */
GoogleAuthProvider.GOOGLE_SIGN_IN_METHOD = "google.com" /* SignInMethod.GOOGLE */;
/** Always set to {@link ProviderId}.GOOGLE. */
GoogleAuthProvider.PROVIDER_ID = "google.com" /* ProviderId.GOOGLE */;

/**
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
 */
/**
 * Provider for generating an {@link OAuthCredential} for {@link ProviderId}.GITHUB.
 *
 * @remarks
 * GitHub requires an OAuth 2.0 redirect, so you can either handle the redirect directly, or use
 * the {@link signInWithPopup} handler:
 *
 * @example
 * ```javascript
 * // Sign in using a redirect.
 * const provider = new GithubAuthProvider();
 * // Start a sign in process for an unauthenticated user.
 * provider.addScope('repo');
 * await signInWithRedirect(auth, provider);
 * // This will trigger a full page redirect away from your app
 *
 * // After returning from the redirect when your app initializes you can obtain the result
 * const result = await getRedirectResult(auth);
 * if (result) {
 *   // This is the signed-in user
 *   const user = result.user;
 *   // This gives you a Github Access Token.
 *   const credential = GithubAuthProvider.credentialFromResult(result);
 *   const token = credential.accessToken;
 * }
 * ```
 *
 * @example
 * ```javascript
 * // Sign in using a popup.
 * const provider = new GithubAuthProvider();
 * provider.addScope('repo');
 * const result = await signInWithPopup(auth, provider);
 *
 * // The signed-in user info.
 * const user = result.user;
 * // This gives you a Github Access Token.
 * const credential = GithubAuthProvider.credentialFromResult(result);
 * const token = credential.accessToken;
 * ```
 * @public
 */
class GithubAuthProvider extends BaseOAuthProvider {
    constructor() {
        super("github.com" /* ProviderId.GITHUB */);
    }
    /**
     * Creates a credential for Github.
     *
     * @param accessToken - Github access token.
     */
    static credential(accessToken) {
        return OAuthCredential._fromParams({
            providerId: GithubAuthProvider.PROVIDER_ID,
            signInMethod: GithubAuthProvider.GITHUB_SIGN_IN_METHOD,
            accessToken
        });
    }
    /**
     * Used to extract the underlying {@link OAuthCredential} from a {@link UserCredential}.
     *
     * @param userCredential - The user credential.
     */
    static credentialFromResult(userCredential) {
        return GithubAuthProvider.credentialFromTaggedObject(userCredential);
    }
    /**
     * Used to extract the underlying {@link OAuthCredential} from a {@link AuthError} which was
     * thrown during a sign-in, link, or reauthenticate operation.
     *
     * @param userCredential - The user credential.
     */
    static credentialFromError(error) {
        return GithubAuthProvider.credentialFromTaggedObject((error.customData || {}));
    }
    static credentialFromTaggedObject({ _tokenResponse: tokenResponse }) {
        if (!tokenResponse || !('oauthAccessToken' in tokenResponse)) {
            return null;
        }
        if (!tokenResponse.oauthAccessToken) {
            return null;
        }
        try {
            return GithubAuthProvider.credential(tokenResponse.oauthAccessToken);
        }
        catch (_a) {
            return null;
        }
    }
}
/** Always set to {@link SignInMethod}.GITHUB. */
GithubAuthProvider.GITHUB_SIGN_IN_METHOD = "github.com" /* SignInMethod.GITHUB */;
/** Always set to {@link ProviderId}.GITHUB. */
GithubAuthProvider.PROVIDER_ID = "github.com" /* ProviderId.GITHUB */;

/**
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
 */
/**
 * Provider for generating an {@link OAuthCredential} for {@link ProviderId}.TWITTER.
 *
 * @example
 * ```javascript
 * // Sign in using a redirect.
 * const provider = new TwitterAuthProvider();
 * // Start a sign in process for an unauthenticated user.
 * await signInWithRedirect(auth, provider);
 * // This will trigger a full page redirect away from your app
 *
 * // After returning from the redirect when your app initializes you can obtain the result
 * const result = await getRedirectResult(auth);
 * if (result) {
 *   // This is the signed-in user
 *   const user = result.user;
 *   // This gives you a Twitter Access Token and Secret.
 *   const credential = TwitterAuthProvider.credentialFromResult(result);
 *   const token = credential.accessToken;
 *   const secret = credential.secret;
 * }
 * ```
 *
 * @example
 * ```javascript
 * // Sign in using a popup.
 * const provider = new TwitterAuthProvider();
 * const result = await signInWithPopup(auth, provider);
 *
 * // The signed-in user info.
 * const user = result.user;
 * // This gives you a Twitter Access Token and Secret.
 * const credential = TwitterAuthProvider.credentialFromResult(result);
 * const token = credential.accessToken;
 * const secret = credential.secret;
 * ```
 *
 * @public
 */
class TwitterAuthProvider extends BaseOAuthProvider {
    constructor() {
        super("twitter.com" /* ProviderId.TWITTER */);
    }
    /**
     * Creates a credential for Twitter.
     *
     * @param token - Twitter access token.
     * @param secret - Twitter secret.
     */
    static credential(token, secret) {
        return OAuthCredential._fromParams({
            providerId: TwitterAuthProvider.PROVIDER_ID,
            signInMethod: TwitterAuthProvider.TWITTER_SIGN_IN_METHOD,
            oauthToken: token,
            oauthTokenSecret: secret
        });
    }
    /**
     * Used to extract the underlying {@link OAuthCredential} from a {@link UserCredential}.
     *
     * @param userCredential - The user credential.
     */
    static credentialFromResult(userCredential) {
        return TwitterAuthProvider.credentialFromTaggedObject(userCredential);
    }
    /**
     * Used to extract the underlying {@link OAuthCredential} from a {@link AuthError} which was
     * thrown during a sign-in, link, or reauthenticate operation.
     *
     * @param userCredential - The user credential.
     */
    static credentialFromError(error) {
        return TwitterAuthProvider.credentialFromTaggedObject((error.customData || {}));
    }
    static credentialFromTaggedObject({ _tokenResponse: tokenResponse }) {
        if (!tokenResponse) {
            return null;
        }
        const { oauthAccessToken, oauthTokenSecret } = tokenResponse;
        if (!oauthAccessToken || !oauthTokenSecret) {
            return null;
        }
        try {
            return TwitterAuthProvider.credential(oauthAccessToken, oauthTokenSecret);
        }
        catch (_a) {
            return null;
        }
    }
}
/** Always set to {@link SignInMethod}.TWITTER. */
TwitterAuthProvider.TWITTER_SIGN_IN_METHOD = "twitter.com" /* SignInMethod.TWITTER */;
/** Always set to {@link ProviderId}.TWITTER. */
TwitterAuthProvider.PROVIDER_ID = "twitter.com" /* ProviderId.TWITTER */;

/**
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
 */
class UserCredentialImpl {
    constructor(params) {
        this.user = params.user;
        this.providerId = params.providerId;
        this._tokenResponse = params._tokenResponse;
        this.operationType = params.operationType;
    }
    static async _fromIdTokenResponse(auth, operationType, idTokenResponse, isAnonymous = false) {
        const user = await UserImpl._fromIdTokenResponse(auth, idTokenResponse, isAnonymous);
        const providerId = providerIdForResponse(idTokenResponse);
        const userCred = new UserCredentialImpl({
            user,
            providerId,
            _tokenResponse: idTokenResponse,
            operationType
        });
        return userCred;
    }
    static async _forOperation(user, operationType, response) {
        await user._updateTokensIfNecessary(response, /* reload */ true);
        const providerId = providerIdForResponse(response);
        return new UserCredentialImpl({
            user,
            providerId,
            _tokenResponse: response,
            operationType
        });
    }
}
function providerIdForResponse(response) {
    if (response.providerId) {
        return response.providerId;
    }
    if ('phoneNumber' in response) {
        return "phone" /* ProviderId.PHONE */;
    }
    return null;
}

/**
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
 */
class MultiFactorError extends FirebaseError {
    constructor(auth, error, operationType, user) {
        var _a;
        super(error.code, error.message);
        this.operationType = operationType;
        this.user = user;
        // https://github.com/Microsoft/TypeScript-wiki/blob/master/Breaking-Changes.md#extending-built-ins-like-error-array-and-map-may-no-longer-work
        Object.setPrototypeOf(this, MultiFactorError.prototype);
        this.customData = {
            appName: auth.name,
            tenantId: (_a = auth.tenantId) !== null && _a !== void 0 ? _a : undefined,
            _serverResponse: error.customData._serverResponse,
            operationType
        };
    }
    static _fromErrorAndOperation(auth, error, operationType, user) {
        return new MultiFactorError(auth, error, operationType, user);
    }
}
function _processCredentialSavingMfaContextIfNecessary(auth, operationType, credential, user) {
    const idTokenProvider = operationType === "reauthenticate" /* OperationType.REAUTHENTICATE */
        ? credential._getReauthenticationResolver(auth)
        : credential._getIdTokenResponse(auth);
    return idTokenProvider.catch(error => {
        if (error.code === `auth/${"multi-factor-auth-required" /* AuthErrorCode.MFA_REQUIRED */}`) {
            throw MultiFactorError._fromErrorAndOperation(auth, error, operationType, user);
        }
        throw error;
    });
}
async function _link$1(user, credential, bypassAuthState = false) {
    const response = await _logoutIfInvalidated(user, credential._linkToIdToken(user.auth, await user.getIdToken()), bypassAuthState);
    return UserCredentialImpl._forOperation(user, "link" /* OperationType.LINK */, response);
}

/**
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
 */
async function _reauthenticate(user, credential, bypassAuthState = false) {
    const { auth } = user;
    if (_isFirebaseServerApp(auth.app)) {
        return Promise.reject(_serverAppCurrentUserOperationNotSupportedError(auth));
    }
    const operationType = "reauthenticate" /* OperationType.REAUTHENTICATE */;
    try {
        const response = await _logoutIfInvalidated(user, _processCredentialSavingMfaContextIfNecessary(auth, operationType, credential, user), bypassAuthState);
        _assert(response.idToken, auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        const parsed = _parseToken(response.idToken);
        _assert(parsed, auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        const { sub: localId } = parsed;
        _assert(user.uid === localId, auth, "user-mismatch" /* AuthErrorCode.USER_MISMATCH */);
        return UserCredentialImpl._forOperation(user, operationType, response);
    }
    catch (e) {
        // Convert user deleted error into user mismatch
        if ((e === null || e === void 0 ? void 0 : e.code) === `auth/${"user-not-found" /* AuthErrorCode.USER_DELETED */}`) {
            _fail(auth, "user-mismatch" /* AuthErrorCode.USER_MISMATCH */);
        }
        throw e;
    }
}

/**
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
 */
async function _signInWithCredential(auth, credential, bypassAuthState = false) {
    if (_isFirebaseServerApp(auth.app)) {
        return Promise.reject(_serverAppCurrentUserOperationNotSupportedError(auth));
    }
    const operationType = "signIn" /* OperationType.SIGN_IN */;
    const response = await _processCredentialSavingMfaContextIfNecessary(auth, operationType, credential);
    const userCredential = await UserCredentialImpl._fromIdTokenResponse(auth, operationType, response);
    if (!bypassAuthState) {
        await auth._updateCurrentUser(userCredential.user);
    }
    return userCredential;
}
/**
 * Asynchronously signs in with the given credentials.
 *
 * @remarks
 * An {@link AuthProvider} can be used to generate the credential.
 *
 * This method is not supported by {@link Auth} instances created with a
 * {@link @firebase/app#FirebaseServerApp}.
 *
 * @param auth - The {@link Auth} instance.
 * @param credential - The auth credential.
 *
 * @public
 */
async function signInWithCredential(auth, credential) {
    return _signInWithCredential(_castAuth(auth), credential);
}

/**
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
 */
function _setActionCodeSettingsOnRequest(auth, request, actionCodeSettings) {
    var _a;
    _assert(((_a = actionCodeSettings.url) === null || _a === void 0 ? void 0 : _a.length) > 0, auth, "invalid-continue-uri" /* AuthErrorCode.INVALID_CONTINUE_URI */);
    _assert(typeof actionCodeSettings.dynamicLinkDomain === 'undefined' ||
        actionCodeSettings.dynamicLinkDomain.length > 0, auth, "invalid-dynamic-link-domain" /* AuthErrorCode.INVALID_DYNAMIC_LINK_DOMAIN */);
    request.continueUrl = actionCodeSettings.url;
    request.dynamicLinkDomain = actionCodeSettings.dynamicLinkDomain;
    request.canHandleCodeInApp = actionCodeSettings.handleCodeInApp;
    if (actionCodeSettings.iOS) {
        _assert(actionCodeSettings.iOS.bundleId.length > 0, auth, "missing-ios-bundle-id" /* AuthErrorCode.MISSING_IOS_BUNDLE_ID */);
        request.iOSBundleId = actionCodeSettings.iOS.bundleId;
    }
    if (actionCodeSettings.android) {
        _assert(actionCodeSettings.android.packageName.length > 0, auth, "missing-android-pkg-name" /* AuthErrorCode.MISSING_ANDROID_PACKAGE_NAME */);
        request.androidInstallApp = actionCodeSettings.android.installApp;
        request.androidMinimumVersionCode =
            actionCodeSettings.android.minimumVersion;
        request.androidPackageName = actionCodeSettings.android.packageName;
    }
}

/**
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
 */
/**
 * Updates the password policy cached in the {@link Auth} instance if a policy is already
 * cached for the project or tenant.
 *
 * @remarks
 * We only fetch the password policy if the password did not meet policy requirements and
 * there is an existing policy cached. A developer must call validatePassword at least
 * once for the cache to be automatically updated.
 *
 * @param auth - The {@link Auth} instance.
 *
 * @private
 */
async function recachePasswordPolicy(auth) {
    const authInternal = _castAuth(auth);
    if (authInternal._getPasswordPolicyInternal()) {
        await authInternal._updatePasswordPolicy();
    }
}
/**
 * Sends a password reset email to the given email address. This method does not throw an error when
 * there's no user account with the given email address and
 * [Email Enumeration Protection](https://cloud.google.com/identity-platform/docs/admin/email-enumeration-protection) is enabled.
 *
 * @remarks
 * To complete the password reset, call {@link confirmPasswordReset} with the code supplied in
 * the email sent to the user, along with the new password specified by the user.
 *
 * @example
 * ```javascript
 * const actionCodeSettings = {
 *   url: 'https://www.example.com/?email=user@example.com',
 *   iOS: {
 *      bundleId: 'com.example.ios'
 *   },
 *   android: {
 *     packageName: 'com.example.android',
 *     installApp: true,
 *     minimumVersion: '12'
 *   },
 *   handleCodeInApp: true
 * };
 * await sendPasswordResetEmail(auth, 'user@example.com', actionCodeSettings);
 * // Obtain code from user.
 * await confirmPasswordReset('user@example.com', code);
 * ```
 *
 * @param auth - The {@link Auth} instance.
 * @param email - The user's email address.
 * @param actionCodeSettings - The {@link ActionCodeSettings}.
 *
 * @public
 */
async function sendPasswordResetEmail(auth, email, actionCodeSettings) {
    const authInternal = _castAuth(auth);
    const request = {
        requestType: "PASSWORD_RESET" /* ActionCodeOperation.PASSWORD_RESET */,
        email,
        clientType: "CLIENT_TYPE_WEB" /* RecaptchaClientType.WEB */
    };
    if (actionCodeSettings) {
        _setActionCodeSettingsOnRequest(authInternal, request, actionCodeSettings);
    }
    await handleRecaptchaFlow(authInternal, request, "getOobCode" /* RecaptchaActionName.GET_OOB_CODE */, sendPasswordResetEmail$1);
}
/**
 * Asynchronously signs in using an email and password.
 *
 * @remarks
 * Fails with an error if the email address and password do not match.
 * When [Email Enumeration Protection](https://cloud.google.com/identity-platform/docs/admin/email-enumeration-protection) is enabled,
 * this method fails with "auth/invalid-credential" in case of an invalid email/password.
 *
 * This method is not supported on {@link Auth} instances created with a
 * {@link @firebase/app#FirebaseServerApp}.
 *
 * Note: The user's password is NOT the password used to access the user's email account. The
 * email address serves as a unique identifier for the user, and the password is used to access
 * the user's account in your Firebase project. See also: {@link createUserWithEmailAndPassword}.
 *
 *
 * @param auth - The {@link Auth} instance.
 * @param email - The users email address.
 * @param password - The users password.
 *
 * @public
 */
function signInWithEmailAndPassword(auth, email, password) {
    if (_isFirebaseServerApp(auth.app)) {
        return Promise.reject(_serverAppCurrentUserOperationNotSupportedError(auth));
    }
    return signInWithCredential(getModularInstance(auth), EmailAuthProvider.credential(email, password)).catch(async (error) => {
        if (error.code === `auth/${"password-does-not-meet-requirements" /* AuthErrorCode.PASSWORD_DOES_NOT_MEET_REQUIREMENTS */}`) {
            void recachePasswordPolicy(auth);
        }
        throw error;
    });
}

/**
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
 */
/**
 * Sends a sign-in email link to the user with the specified email.
 *
 * @remarks
 * The sign-in operation has to always be completed in the app unlike other out of band email
 * actions (password reset and email verifications). This is because, at the end of the flow,
 * the user is expected to be signed in and their Auth state persisted within the app.
 *
 * To complete sign in with the email link, call {@link signInWithEmailLink} with the email
 * address and the email link supplied in the email sent to the user.
 *
 * @example
 * ```javascript
 * const actionCodeSettings = {
 *   url: 'https://www.example.com/?email=user@example.com',
 *   iOS: {
 *      bundleId: 'com.example.ios'
 *   },
 *   android: {
 *     packageName: 'com.example.android',
 *     installApp: true,
 *     minimumVersion: '12'
 *   },
 *   handleCodeInApp: true
 * };
 * await sendSignInLinkToEmail(auth, 'user@example.com', actionCodeSettings);
 * // Obtain emailLink from the user.
 * if(isSignInWithEmailLink(auth, emailLink)) {
 *   await signInWithEmailLink(auth, 'user@example.com', emailLink);
 * }
 * ```
 *
 * @param authInternal - The {@link Auth} instance.
 * @param email - The user's email address.
 * @param actionCodeSettings - The {@link ActionCodeSettings}.
 *
 * @public
 */
async function sendSignInLinkToEmail(auth, email, actionCodeSettings) {
    const authInternal = _castAuth(auth);
    const request = {
        requestType: "EMAIL_SIGNIN" /* ActionCodeOperation.EMAIL_SIGNIN */,
        email,
        clientType: "CLIENT_TYPE_WEB" /* RecaptchaClientType.WEB */
    };
    function setActionCodeSettings(request, actionCodeSettings) {
        _assert(actionCodeSettings.handleCodeInApp, authInternal, "argument-error" /* AuthErrorCode.ARGUMENT_ERROR */);
        if (actionCodeSettings) {
            _setActionCodeSettingsOnRequest(authInternal, request, actionCodeSettings);
        }
    }
    setActionCodeSettings(request, actionCodeSettings);
    await handleRecaptchaFlow(authInternal, request, "getOobCode" /* RecaptchaActionName.GET_OOB_CODE */, sendSignInLinkToEmail$1);
}
/**
 * Adds an observer for changes to the signed-in user's ID token.
 *
 * @remarks
 * This includes sign-in, sign-out, and token refresh events.
 * This will not be triggered automatically upon ID token expiration. Use {@link User.getIdToken} to refresh the ID token.
 *
 * @param auth - The {@link Auth} instance.
 * @param nextOrObserver - callback triggered on change.
 * @param error - Deprecated. This callback is never triggered. Errors
 * on signing in/out can be caught in promises returned from
 * sign-in/sign-out functions.
 * @param completed - Deprecated. This callback is never triggered.
 *
 * @public
 */
function onIdTokenChanged(auth, nextOrObserver, error, completed) {
    return getModularInstance(auth).onIdTokenChanged(nextOrObserver, error, completed);
}
/**
 * Adds a blocking callback that runs before an auth state change
 * sets a new user.
 *
 * @param auth - The {@link Auth} instance.
 * @param callback - callback triggered before new user value is set.
 *   If this throws, it blocks the user from being set.
 * @param onAbort - callback triggered if a later `beforeAuthStateChanged()`
 *   callback throws, allowing you to undo any side effects.
 */
function beforeAuthStateChanged(auth, callback, onAbort) {
    return getModularInstance(auth).beforeAuthStateChanged(callback, onAbort);
}
/**
 * Adds an observer for changes to the user's sign-in state.
 *
 * @remarks
 * To keep the old behavior, see {@link onIdTokenChanged}.
 *
 * @param auth - The {@link Auth} instance.
 * @param nextOrObserver - callback triggered on change.
 * @param error - Deprecated. This callback is never triggered. Errors
 * on signing in/out can be caught in promises returned from
 * sign-in/sign-out functions.
 * @param completed - Deprecated. This callback is never triggered.
 *
 * @public
 */
function onAuthStateChanged(auth, nextOrObserver, error, completed) {
    return getModularInstance(auth).onAuthStateChanged(nextOrObserver, error, completed);
}
/**
 * Signs out the current user.
 *
 * @remarks
 * This method is not supported by {@link Auth} instances created with a
 * {@link @firebase/app#FirebaseServerApp}.
 *
 * @param auth - The {@link Auth} instance.
 *
 * @public
 */
function signOut(auth) {
    return getModularInstance(auth).signOut();
}

const STORAGE_AVAILABLE_KEY = '__sak';

/**
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
 */
// There are two different browser persistence types: local and session.
// Both have the same implementation but use a different underlying storage
// object.
class BrowserPersistenceClass {
    constructor(storageRetriever, type) {
        this.storageRetriever = storageRetriever;
        this.type = type;
    }
    _isAvailable() {
        try {
            if (!this.storage) {
                return Promise.resolve(false);
            }
            this.storage.setItem(STORAGE_AVAILABLE_KEY, '1');
            this.storage.removeItem(STORAGE_AVAILABLE_KEY);
            return Promise.resolve(true);
        }
        catch (_a) {
            return Promise.resolve(false);
        }
    }
    _set(key, value) {
        this.storage.setItem(key, JSON.stringify(value));
        return Promise.resolve();
    }
    _get(key) {
        const json = this.storage.getItem(key);
        return Promise.resolve(json ? JSON.parse(json) : null);
    }
    _remove(key) {
        this.storage.removeItem(key);
        return Promise.resolve();
    }
    get storage() {
        return this.storageRetriever();
    }
}

/**
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
 */
function _iframeCannotSyncWebStorage() {
    const ua = getUA();
    return _isSafari(ua) || _isIOS(ua);
}
// The polling period in case events are not supported
const _POLLING_INTERVAL_MS$1 = 1000;
// The IE 10 localStorage cross tab synchronization delay in milliseconds
const IE10_LOCAL_STORAGE_SYNC_DELAY = 10;
class BrowserLocalPersistence extends BrowserPersistenceClass {
    constructor() {
        super(() => window.localStorage, "LOCAL" /* PersistenceType.LOCAL */);
        this.boundEventHandler = (event, poll) => this.onStorageEvent(event, poll);
        this.listeners = {};
        this.localCache = {};
        // setTimeout return value is platform specific
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        this.pollTimer = null;
        // Safari or iOS browser and embedded in an iframe.
        this.safariLocalStorageNotSynced = _iframeCannotSyncWebStorage() && _isIframe();
        // Whether to use polling instead of depending on window events
        this.fallbackToPolling = _isMobileBrowser();
        this._shouldAllowMigration = true;
    }
    forAllChangedKeys(cb) {
        // Check all keys with listeners on them.
        for (const key of Object.keys(this.listeners)) {
            // Get value from localStorage.
            const newValue = this.storage.getItem(key);
            const oldValue = this.localCache[key];
            // If local map value does not match, trigger listener with storage event.
            // Differentiate this simulated event from the real storage event.
            if (newValue !== oldValue) {
                cb(key, oldValue, newValue);
            }
        }
    }
    onStorageEvent(event, poll = false) {
        // Key would be null in some situations, like when localStorage is cleared
        if (!event.key) {
            this.forAllChangedKeys((key, _oldValue, newValue) => {
                this.notifyListeners(key, newValue);
            });
            return;
        }
        const key = event.key;
        // Check the mechanism how this event was detected.
        // The first event will dictate the mechanism to be used.
        if (poll) {
            // Environment detects storage changes via polling.
            // Remove storage event listener to prevent possible event duplication.
            this.detachListener();
        }
        else {
            // Environment detects storage changes via storage event listener.
            // Remove polling listener to prevent possible event duplication.
            this.stopPolling();
        }
        // Safari embedded iframe. Storage event will trigger with the delta
        // changes but no changes will be applied to the iframe localStorage.
        if (this.safariLocalStorageNotSynced) {
            // Get current iframe page value.
            const storedValue = this.storage.getItem(key);
            // Value not synchronized, synchronize manually.
            if (event.newValue !== storedValue) {
                if (event.newValue !== null) {
                    // Value changed from current value.
                    this.storage.setItem(key, event.newValue);
                }
                else {
                    // Current value deleted.
                    this.storage.removeItem(key);
                }
            }
            else if (this.localCache[key] === event.newValue && !poll) {
                // Already detected and processed, do not trigger listeners again.
                return;
            }
        }
        const triggerListeners = () => {
            // Keep local map up to date in case storage event is triggered before
            // poll.
            const storedValue = this.storage.getItem(key);
            if (!poll && this.localCache[key] === storedValue) {
                // Real storage event which has already been detected, do nothing.
                // This seems to trigger in some IE browsers for some reason.
                return;
            }
            this.notifyListeners(key, storedValue);
        };
        const storedValue = this.storage.getItem(key);
        if (_isIE10() &&
            storedValue !== event.newValue &&
            event.newValue !== event.oldValue) {
            // IE 10 has this weird bug where a storage event would trigger with the
            // correct key, oldValue and newValue but localStorage.getItem(key) does
            // not yield the updated value until a few milliseconds. This ensures
            // this recovers from that situation.
            setTimeout(triggerListeners, IE10_LOCAL_STORAGE_SYNC_DELAY);
        }
        else {
            triggerListeners();
        }
    }
    notifyListeners(key, value) {
        this.localCache[key] = value;
        const listeners = this.listeners[key];
        if (listeners) {
            for (const listener of Array.from(listeners)) {
                listener(value ? JSON.parse(value) : value);
            }
        }
    }
    startPolling() {
        this.stopPolling();
        this.pollTimer = setInterval(() => {
            this.forAllChangedKeys((key, oldValue, newValue) => {
                this.onStorageEvent(new StorageEvent('storage', {
                    key,
                    oldValue,
                    newValue
                }), 
                /* poll */ true);
            });
        }, _POLLING_INTERVAL_MS$1);
    }
    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }
    attachListener() {
        window.addEventListener('storage', this.boundEventHandler);
    }
    detachListener() {
        window.removeEventListener('storage', this.boundEventHandler);
    }
    _addListener(key, listener) {
        if (Object.keys(this.listeners).length === 0) {
            // Whether browser can detect storage event when it had already been pushed to the background.
            // This may happen in some mobile browsers. A localStorage change in the foreground window
            // will not be detected in the background window via the storage event.
            // This was detected in iOS 7.x mobile browsers
            if (this.fallbackToPolling) {
                this.startPolling();
            }
            else {
                this.attachListener();
            }
        }
        if (!this.listeners[key]) {
            this.listeners[key] = new Set();
            // Populate the cache to avoid spuriously triggering on first poll.
            this.localCache[key] = this.storage.getItem(key);
        }
        this.listeners[key].add(listener);
    }
    _removeListener(key, listener) {
        if (this.listeners[key]) {
            this.listeners[key].delete(listener);
            if (this.listeners[key].size === 0) {
                delete this.listeners[key];
            }
        }
        if (Object.keys(this.listeners).length === 0) {
            this.detachListener();
            this.stopPolling();
        }
    }
    // Update local cache on base operations:
    async _set(key, value) {
        await super._set(key, value);
        this.localCache[key] = JSON.stringify(value);
    }
    async _get(key) {
        const value = await super._get(key);
        this.localCache[key] = JSON.stringify(value);
        return value;
    }
    async _remove(key) {
        await super._remove(key);
        delete this.localCache[key];
    }
}
BrowserLocalPersistence.type = 'LOCAL';
/**
 * An implementation of {@link Persistence} of type `LOCAL` using `localStorage`
 * for the underlying storage.
 *
 * @public
 */
const browserLocalPersistence = BrowserLocalPersistence;

/**
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
 */
class BrowserSessionPersistence extends BrowserPersistenceClass {
    constructor() {
        super(() => window.sessionStorage, "SESSION" /* PersistenceType.SESSION */);
    }
    _addListener(_key, _listener) {
        // Listeners are not supported for session storage since it cannot be shared across windows
        return;
    }
    _removeListener(_key, _listener) {
        // Listeners are not supported for session storage since it cannot be shared across windows
        return;
    }
}
BrowserSessionPersistence.type = 'SESSION';
/**
 * An implementation of {@link Persistence} of `SESSION` using `sessionStorage`
 * for the underlying storage.
 *
 * @public
 */
const browserSessionPersistence = BrowserSessionPersistence;

/**
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
 */
/**
 * Shim for Promise.allSettled, note the slightly different format of `fulfilled` vs `status`.
 *
 * @param promises - Array of promises to wait on.
 */
function _allSettled(promises) {
    return Promise.all(promises.map(async (promise) => {
        try {
            const value = await promise;
            return {
                fulfilled: true,
                value
            };
        }
        catch (reason) {
            return {
                fulfilled: false,
                reason
            };
        }
    }));
}

/**
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
 */
/**
 * Interface class for receiving messages.
 *
 */
class Receiver {
    constructor(eventTarget) {
        this.eventTarget = eventTarget;
        this.handlersMap = {};
        this.boundEventHandler = this.handleEvent.bind(this);
    }
    /**
     * Obtain an instance of a Receiver for a given event target, if none exists it will be created.
     *
     * @param eventTarget - An event target (such as window or self) through which the underlying
     * messages will be received.
     */
    static _getInstance(eventTarget) {
        // The results are stored in an array since objects can't be keys for other
        // objects. In addition, setting a unique property on an event target as a
        // hash map key may not be allowed due to CORS restrictions.
        const existingInstance = this.receivers.find(receiver => receiver.isListeningto(eventTarget));
        if (existingInstance) {
            return existingInstance;
        }
        const newInstance = new Receiver(eventTarget);
        this.receivers.push(newInstance);
        return newInstance;
    }
    isListeningto(eventTarget) {
        return this.eventTarget === eventTarget;
    }
    /**
     * Fans out a MessageEvent to the appropriate listeners.
     *
     * @remarks
     * Sends an {@link Status.ACK} upon receipt and a {@link Status.DONE} once all handlers have
     * finished processing.
     *
     * @param event - The MessageEvent.
     *
     */
    async handleEvent(event) {
        const messageEvent = event;
        const { eventId, eventType, data } = messageEvent.data;
        const handlers = this.handlersMap[eventType];
        if (!(handlers === null || handlers === void 0 ? void 0 : handlers.size)) {
            return;
        }
        messageEvent.ports[0].postMessage({
            status: "ack" /* _Status.ACK */,
            eventId,
            eventType
        });
        const promises = Array.from(handlers).map(async (handler) => handler(messageEvent.origin, data));
        const response = await _allSettled(promises);
        messageEvent.ports[0].postMessage({
            status: "done" /* _Status.DONE */,
            eventId,
            eventType,
            response
        });
    }
    /**
     * Subscribe an event handler for a particular event.
     *
     * @param eventType - Event name to subscribe to.
     * @param eventHandler - The event handler which should receive the events.
     *
     */
    _subscribe(eventType, eventHandler) {
        if (Object.keys(this.handlersMap).length === 0) {
            this.eventTarget.addEventListener('message', this.boundEventHandler);
        }
        if (!this.handlersMap[eventType]) {
            this.handlersMap[eventType] = new Set();
        }
        this.handlersMap[eventType].add(eventHandler);
    }
    /**
     * Unsubscribe an event handler from a particular event.
     *
     * @param eventType - Event name to unsubscribe from.
     * @param eventHandler - Optinoal event handler, if none provided, unsubscribe all handlers on this event.
     *
     */
    _unsubscribe(eventType, eventHandler) {
        if (this.handlersMap[eventType] && eventHandler) {
            this.handlersMap[eventType].delete(eventHandler);
        }
        if (!eventHandler || this.handlersMap[eventType].size === 0) {
            delete this.handlersMap[eventType];
        }
        if (Object.keys(this.handlersMap).length === 0) {
            this.eventTarget.removeEventListener('message', this.boundEventHandler);
        }
    }
}
Receiver.receivers = [];

/**
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
 */
function _generateEventId(prefix = '', digits = 10) {
    let random = '';
    for (let i = 0; i < digits; i++) {
        random += Math.floor(Math.random() * 10);
    }
    return prefix + random;
}

/**
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
 */
/**
 * Interface for sending messages and waiting for a completion response.
 *
 */
class Sender {
    constructor(target) {
        this.target = target;
        this.handlers = new Set();
    }
    /**
     * Unsubscribe the handler and remove it from our tracking Set.
     *
     * @param handler - The handler to unsubscribe.
     */
    removeMessageHandler(handler) {
        if (handler.messageChannel) {
            handler.messageChannel.port1.removeEventListener('message', handler.onMessage);
            handler.messageChannel.port1.close();
        }
        this.handlers.delete(handler);
    }
    /**
     * Send a message to the Receiver located at {@link target}.
     *
     * @remarks
     * We'll first wait a bit for an ACK , if we get one we will wait significantly longer until the
     * receiver has had a chance to fully process the event.
     *
     * @param eventType - Type of event to send.
     * @param data - The payload of the event.
     * @param timeout - Timeout for waiting on an ACK from the receiver.
     *
     * @returns An array of settled promises from all the handlers that were listening on the receiver.
     */
    async _send(eventType, data, timeout = 50 /* _TimeoutDuration.ACK */) {
        const messageChannel = typeof MessageChannel !== 'undefined' ? new MessageChannel() : null;
        if (!messageChannel) {
            throw new Error("connection_unavailable" /* _MessageError.CONNECTION_UNAVAILABLE */);
        }
        // Node timers and browser timers return fundamentally different types.
        // We don't actually care what the value is but TS won't accept unknown and
        // we can't cast properly in both environments.
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        let completionTimer;
        let handler;
        return new Promise((resolve, reject) => {
            const eventId = _generateEventId('', 20);
            messageChannel.port1.start();
            const ackTimer = setTimeout(() => {
                reject(new Error("unsupported_event" /* _MessageError.UNSUPPORTED_EVENT */));
            }, timeout);
            handler = {
                messageChannel,
                onMessage(event) {
                    const messageEvent = event;
                    if (messageEvent.data.eventId !== eventId) {
                        return;
                    }
                    switch (messageEvent.data.status) {
                        case "ack" /* _Status.ACK */:
                            // The receiver should ACK first.
                            clearTimeout(ackTimer);
                            completionTimer = setTimeout(() => {
                                reject(new Error("timeout" /* _MessageError.TIMEOUT */));
                            }, 3000 /* _TimeoutDuration.COMPLETION */);
                            break;
                        case "done" /* _Status.DONE */:
                            // Once the receiver's handlers are finished we will get the results.
                            clearTimeout(completionTimer);
                            resolve(messageEvent.data.response);
                            break;
                        default:
                            clearTimeout(ackTimer);
                            clearTimeout(completionTimer);
                            reject(new Error("invalid_response" /* _MessageError.INVALID_RESPONSE */));
                            break;
                    }
                }
            };
            this.handlers.add(handler);
            messageChannel.port1.addEventListener('message', handler.onMessage);
            this.target.postMessage({
                eventType,
                eventId,
                data
            }, [messageChannel.port2]);
        }).finally(() => {
            if (handler) {
                this.removeMessageHandler(handler);
            }
        });
    }
}

/**
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
 */
/**
 * Lazy accessor for window, since the compat layer won't tree shake this out,
 * we need to make sure not to mess with window unless we have to
 */
function _window() {
    return window;
}
function _setWindowLocation(url) {
    _window().location.href = url;
}

/**
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
 */
function _isWorker() {
    return (typeof _window()['WorkerGlobalScope'] !== 'undefined' &&
        typeof _window()['importScripts'] === 'function');
}
async function _getActiveServiceWorker() {
    if (!(navigator === null || navigator === void 0 ? void 0 : navigator.serviceWorker)) {
        return null;
    }
    try {
        const registration = await navigator.serviceWorker.ready;
        return registration.active;
    }
    catch (_a) {
        return null;
    }
}
function _getServiceWorkerController() {
    var _a;
    return ((_a = navigator === null || navigator === void 0 ? void 0 : navigator.serviceWorker) === null || _a === void 0 ? void 0 : _a.controller) || null;
}
function _getWorkerGlobalScope() {
    return _isWorker() ? self : null;
}

/**
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
 */
const DB_NAME = 'firebaseLocalStorageDb';
const DB_VERSION = 1;
const DB_OBJECTSTORE_NAME = 'firebaseLocalStorage';
const DB_DATA_KEYPATH = 'fbase_key';
/**
 * Promise wrapper for IDBRequest
 *
 * Unfortunately we can't cleanly extend Promise<T> since promises are not callable in ES6
 *
 */
class DBPromise {
    constructor(request) {
        this.request = request;
    }
    toPromise() {
        return new Promise((resolve, reject) => {
            this.request.addEventListener('success', () => {
                resolve(this.request.result);
            });
            this.request.addEventListener('error', () => {
                reject(this.request.error);
            });
        });
    }
}
function getObjectStore(db, isReadWrite) {
    return db
        .transaction([DB_OBJECTSTORE_NAME], isReadWrite ? 'readwrite' : 'readonly')
        .objectStore(DB_OBJECTSTORE_NAME);
}
function _deleteDatabase() {
    const request = indexedDB.deleteDatabase(DB_NAME);
    return new DBPromise(request).toPromise();
}
function _openDatabase() {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    return new Promise((resolve, reject) => {
        request.addEventListener('error', () => {
            reject(request.error);
        });
        request.addEventListener('upgradeneeded', () => {
            const db = request.result;
            try {
                db.createObjectStore(DB_OBJECTSTORE_NAME, { keyPath: DB_DATA_KEYPATH });
            }
            catch (e) {
                reject(e);
            }
        });
        request.addEventListener('success', async () => {
            const db = request.result;
            // Strange bug that occurs in Firefox when multiple tabs are opened at the
            // same time. The only way to recover seems to be deleting the database
            // and re-initializing it.
            // https://github.com/firebase/firebase-js-sdk/issues/634
            if (!db.objectStoreNames.contains(DB_OBJECTSTORE_NAME)) {
                // Need to close the database or else you get a `blocked` event
                db.close();
                await _deleteDatabase();
                resolve(await _openDatabase());
            }
            else {
                resolve(db);
            }
        });
    });
}
async function _putObject(db, key, value) {
    const request = getObjectStore(db, true).put({
        [DB_DATA_KEYPATH]: key,
        value
    });
    return new DBPromise(request).toPromise();
}
async function getObject(db, key) {
    const request = getObjectStore(db, false).get(key);
    const data = await new DBPromise(request).toPromise();
    return data === undefined ? null : data.value;
}
function _deleteObject(db, key) {
    const request = getObjectStore(db, true).delete(key);
    return new DBPromise(request).toPromise();
}
const _POLLING_INTERVAL_MS = 800;
const _TRANSACTION_RETRY_COUNT = 3;
class IndexedDBLocalPersistence {
    constructor() {
        this.type = "LOCAL" /* PersistenceType.LOCAL */;
        this._shouldAllowMigration = true;
        this.listeners = {};
        this.localCache = {};
        // setTimeout return value is platform specific
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        this.pollTimer = null;
        this.pendingWrites = 0;
        this.receiver = null;
        this.sender = null;
        this.serviceWorkerReceiverAvailable = false;
        this.activeServiceWorker = null;
        // Fire & forget the service worker registration as it may never resolve
        this._workerInitializationPromise =
            this.initializeServiceWorkerMessaging().then(() => { }, () => { });
    }
    async _openDb() {
        if (this.db) {
            return this.db;
        }
        this.db = await _openDatabase();
        return this.db;
    }
    async _withRetries(op) {
        let numAttempts = 0;
        while (true) {
            try {
                const db = await this._openDb();
                return await op(db);
            }
            catch (e) {
                if (numAttempts++ > _TRANSACTION_RETRY_COUNT) {
                    throw e;
                }
                if (this.db) {
                    this.db.close();
                    this.db = undefined;
                }
                // TODO: consider adding exponential backoff
            }
        }
    }
    /**
     * IndexedDB events do not propagate from the main window to the worker context.  We rely on a
     * postMessage interface to send these events to the worker ourselves.
     */
    async initializeServiceWorkerMessaging() {
        return _isWorker() ? this.initializeReceiver() : this.initializeSender();
    }
    /**
     * As the worker we should listen to events from the main window.
     */
    async initializeReceiver() {
        this.receiver = Receiver._getInstance(_getWorkerGlobalScope());
        // Refresh from persistence if we receive a KeyChanged message.
        this.receiver._subscribe("keyChanged" /* _EventType.KEY_CHANGED */, async (_origin, data) => {
            const keys = await this._poll();
            return {
                keyProcessed: keys.includes(data.key)
            };
        });
        // Let the sender know that we are listening so they give us more timeout.
        this.receiver._subscribe("ping" /* _EventType.PING */, async (_origin, _data) => {
            return ["keyChanged" /* _EventType.KEY_CHANGED */];
        });
    }
    /**
     * As the main window, we should let the worker know when keys change (set and remove).
     *
     * @remarks
     * {@link https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerContainer/ready | ServiceWorkerContainer.ready}
     * may not resolve.
     */
    async initializeSender() {
        var _a, _b;
        // Check to see if there's an active service worker.
        this.activeServiceWorker = await _getActiveServiceWorker();
        if (!this.activeServiceWorker) {
            return;
        }
        this.sender = new Sender(this.activeServiceWorker);
        // Ping the service worker to check what events they can handle.
        const results = await this.sender._send("ping" /* _EventType.PING */, {}, 800 /* _TimeoutDuration.LONG_ACK */);
        if (!results) {
            return;
        }
        if (((_a = results[0]) === null || _a === void 0 ? void 0 : _a.fulfilled) &&
            ((_b = results[0]) === null || _b === void 0 ? void 0 : _b.value.includes("keyChanged" /* _EventType.KEY_CHANGED */))) {
            this.serviceWorkerReceiverAvailable = true;
        }
    }
    /**
     * Let the worker know about a changed key, the exact key doesn't technically matter since the
     * worker will just trigger a full sync anyway.
     *
     * @remarks
     * For now, we only support one service worker per page.
     *
     * @param key - Storage key which changed.
     */
    async notifyServiceWorker(key) {
        if (!this.sender ||
            !this.activeServiceWorker ||
            _getServiceWorkerController() !== this.activeServiceWorker) {
            return;
        }
        try {
            await this.sender._send("keyChanged" /* _EventType.KEY_CHANGED */, { key }, 
            // Use long timeout if receiver has previously responded to a ping from us.
            this.serviceWorkerReceiverAvailable
                ? 800 /* _TimeoutDuration.LONG_ACK */
                : 50 /* _TimeoutDuration.ACK */);
        }
        catch (_a) {
            // This is a best effort approach. Ignore errors.
        }
    }
    async _isAvailable() {
        try {
            if (!indexedDB) {
                return false;
            }
            const db = await _openDatabase();
            await _putObject(db, STORAGE_AVAILABLE_KEY, '1');
            await _deleteObject(db, STORAGE_AVAILABLE_KEY);
            return true;
        }
        catch (_a) { }
        return false;
    }
    async _withPendingWrite(write) {
        this.pendingWrites++;
        try {
            await write();
        }
        finally {
            this.pendingWrites--;
        }
    }
    async _set(key, value) {
        return this._withPendingWrite(async () => {
            await this._withRetries((db) => _putObject(db, key, value));
            this.localCache[key] = value;
            return this.notifyServiceWorker(key);
        });
    }
    async _get(key) {
        const obj = (await this._withRetries((db) => getObject(db, key)));
        this.localCache[key] = obj;
        return obj;
    }
    async _remove(key) {
        return this._withPendingWrite(async () => {
            await this._withRetries((db) => _deleteObject(db, key));
            delete this.localCache[key];
            return this.notifyServiceWorker(key);
        });
    }
    async _poll() {
        // TODO: check if we need to fallback if getAll is not supported
        const result = await this._withRetries((db) => {
            const getAllRequest = getObjectStore(db, false).getAll();
            return new DBPromise(getAllRequest).toPromise();
        });
        if (!result) {
            return [];
        }
        // If we have pending writes in progress abort, we'll get picked up on the next poll
        if (this.pendingWrites !== 0) {
            return [];
        }
        const keys = [];
        const keysInResult = new Set();
        if (result.length !== 0) {
            for (const { fbase_key: key, value } of result) {
                keysInResult.add(key);
                if (JSON.stringify(this.localCache[key]) !== JSON.stringify(value)) {
                    this.notifyListeners(key, value);
                    keys.push(key);
                }
            }
        }
        for (const localKey of Object.keys(this.localCache)) {
            if (this.localCache[localKey] && !keysInResult.has(localKey)) {
                // Deleted
                this.notifyListeners(localKey, null);
                keys.push(localKey);
            }
        }
        return keys;
    }
    notifyListeners(key, newValue) {
        this.localCache[key] = newValue;
        const listeners = this.listeners[key];
        if (listeners) {
            for (const listener of Array.from(listeners)) {
                listener(newValue);
            }
        }
    }
    startPolling() {
        this.stopPolling();
        this.pollTimer = setInterval(async () => this._poll(), _POLLING_INTERVAL_MS);
    }
    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }
    _addListener(key, listener) {
        if (Object.keys(this.listeners).length === 0) {
            this.startPolling();
        }
        if (!this.listeners[key]) {
            this.listeners[key] = new Set();
            // Populate the cache to avoid spuriously triggering on first poll.
            void this._get(key); // This can happen in the background async and we can return immediately.
        }
        this.listeners[key].add(listener);
    }
    _removeListener(key, listener) {
        if (this.listeners[key]) {
            this.listeners[key].delete(listener);
            if (this.listeners[key].size === 0) {
                delete this.listeners[key];
            }
        }
        if (Object.keys(this.listeners).length === 0) {
            this.stopPolling();
        }
    }
}
IndexedDBLocalPersistence.type = 'LOCAL';
/**
 * An implementation of {@link Persistence} of type `LOCAL` using `indexedDB`
 * for the underlying storage.
 *
 * @public
 */
const indexedDBLocalPersistence = IndexedDBLocalPersistence;
new Delay(30000, 60000);

/**
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
 */
/**
 * Chooses a popup/redirect resolver to use. This prefers the override (which
 * is directly passed in), and falls back to the property set on the auth
 * object. If neither are available, this function errors w/ an argument error.
 */
function _withDefaultResolver(auth, resolverOverride) {
    if (resolverOverride) {
        return _getInstance(resolverOverride);
    }
    _assert(auth._popupRedirectResolver, auth, "argument-error" /* AuthErrorCode.ARGUMENT_ERROR */);
    return auth._popupRedirectResolver;
}

/**
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
 */
class IdpCredential extends AuthCredential {
    constructor(params) {
        super("custom" /* ProviderId.CUSTOM */, "custom" /* ProviderId.CUSTOM */);
        this.params = params;
    }
    _getIdTokenResponse(auth) {
        return signInWithIdp(auth, this._buildIdpRequest());
    }
    _linkToIdToken(auth, idToken) {
        return signInWithIdp(auth, this._buildIdpRequest(idToken));
    }
    _getReauthenticationResolver(auth) {
        return signInWithIdp(auth, this._buildIdpRequest());
    }
    _buildIdpRequest(idToken) {
        const request = {
            requestUri: this.params.requestUri,
            sessionId: this.params.sessionId,
            postBody: this.params.postBody,
            tenantId: this.params.tenantId,
            pendingToken: this.params.pendingToken,
            returnSecureToken: true,
            returnIdpCredential: true
        };
        if (idToken) {
            request.idToken = idToken;
        }
        return request;
    }
}
function _signIn(params) {
    return _signInWithCredential(params.auth, new IdpCredential(params), params.bypassAuthState);
}
function _reauth(params) {
    const { auth, user } = params;
    _assert(user, auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
    return _reauthenticate(user, new IdpCredential(params), params.bypassAuthState);
}
async function _link(params) {
    const { auth, user } = params;
    _assert(user, auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
    return _link$1(user, new IdpCredential(params), params.bypassAuthState);
}

/**
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
 */
/**
 * Popup event manager. Handles the popup's entire lifecycle; listens to auth
 * events
 */
class AbstractPopupRedirectOperation {
    constructor(auth, filter, resolver, user, bypassAuthState = false) {
        this.auth = auth;
        this.resolver = resolver;
        this.user = user;
        this.bypassAuthState = bypassAuthState;
        this.pendingPromise = null;
        this.eventManager = null;
        this.filter = Array.isArray(filter) ? filter : [filter];
    }
    execute() {
        return new Promise(async (resolve, reject) => {
            this.pendingPromise = { resolve, reject };
            try {
                this.eventManager = await this.resolver._initialize(this.auth);
                await this.onExecution();
                this.eventManager.registerConsumer(this);
            }
            catch (e) {
                this.reject(e);
            }
        });
    }
    async onAuthEvent(event) {
        const { urlResponse, sessionId, postBody, tenantId, error, type } = event;
        if (error) {
            this.reject(error);
            return;
        }
        const params = {
            auth: this.auth,
            requestUri: urlResponse,
            sessionId: sessionId,
            tenantId: tenantId || undefined,
            postBody: postBody || undefined,
            user: this.user,
            bypassAuthState: this.bypassAuthState
        };
        try {
            this.resolve(await this.getIdpTask(type)(params));
        }
        catch (e) {
            this.reject(e);
        }
    }
    onError(error) {
        this.reject(error);
    }
    getIdpTask(type) {
        switch (type) {
            case "signInViaPopup" /* AuthEventType.SIGN_IN_VIA_POPUP */:
            case "signInViaRedirect" /* AuthEventType.SIGN_IN_VIA_REDIRECT */:
                return _signIn;
            case "linkViaPopup" /* AuthEventType.LINK_VIA_POPUP */:
            case "linkViaRedirect" /* AuthEventType.LINK_VIA_REDIRECT */:
                return _link;
            case "reauthViaPopup" /* AuthEventType.REAUTH_VIA_POPUP */:
            case "reauthViaRedirect" /* AuthEventType.REAUTH_VIA_REDIRECT */:
                return _reauth;
            default:
                _fail(this.auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        }
    }
    resolve(cred) {
        debugAssert(this.pendingPromise, 'Pending promise was never set');
        this.pendingPromise.resolve(cred);
        this.unregisterAndCleanUp();
    }
    reject(error) {
        debugAssert(this.pendingPromise, 'Pending promise was never set');
        this.pendingPromise.reject(error);
        this.unregisterAndCleanUp();
    }
    unregisterAndCleanUp() {
        if (this.eventManager) {
            this.eventManager.unregisterConsumer(this);
        }
        this.pendingPromise = null;
        this.cleanUp();
    }
}

/**
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
 */
const _POLL_WINDOW_CLOSE_TIMEOUT = new Delay(2000, 10000);
/**
 * Popup event manager. Handles the popup's entire lifecycle; listens to auth
 * events
 *
 */
class PopupOperation extends AbstractPopupRedirectOperation {
    constructor(auth, filter, provider, resolver, user) {
        super(auth, filter, resolver, user);
        this.provider = provider;
        this.authWindow = null;
        this.pollId = null;
        if (PopupOperation.currentPopupAction) {
            PopupOperation.currentPopupAction.cancel();
        }
        PopupOperation.currentPopupAction = this;
    }
    async executeNotNull() {
        const result = await this.execute();
        _assert(result, this.auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        return result;
    }
    async onExecution() {
        debugAssert(this.filter.length === 1, 'Popup operations only handle one event');
        const eventId = _generateEventId();
        this.authWindow = await this.resolver._openPopup(this.auth, this.provider, this.filter[0], // There's always one, see constructor
        eventId);
        this.authWindow.associatedEvent = eventId;
        // Check for web storage support and origin validation _after_ the popup is
        // loaded. These operations are slow (~1 second or so) Rather than
        // waiting on them before opening the window, optimistically open the popup
        // and check for storage support at the same time. If storage support is
        // not available, this will cause the whole thing to reject properly. It
        // will also close the popup, but since the promise has already rejected,
        // the popup closed by user poll will reject into the void.
        this.resolver._originValidation(this.auth).catch(e => {
            this.reject(e);
        });
        this.resolver._isIframeWebStorageSupported(this.auth, isSupported => {
            if (!isSupported) {
                this.reject(_createError(this.auth, "web-storage-unsupported" /* AuthErrorCode.WEB_STORAGE_UNSUPPORTED */));
            }
        });
        // Handle user closure. Notice this does *not* use await
        this.pollUserCancellation();
    }
    get eventId() {
        var _a;
        return ((_a = this.authWindow) === null || _a === void 0 ? void 0 : _a.associatedEvent) || null;
    }
    cancel() {
        this.reject(_createError(this.auth, "cancelled-popup-request" /* AuthErrorCode.EXPIRED_POPUP_REQUEST */));
    }
    cleanUp() {
        if (this.authWindow) {
            this.authWindow.close();
        }
        if (this.pollId) {
            window.clearTimeout(this.pollId);
        }
        this.authWindow = null;
        this.pollId = null;
        PopupOperation.currentPopupAction = null;
    }
    pollUserCancellation() {
        const poll = () => {
            var _a, _b;
            if ((_b = (_a = this.authWindow) === null || _a === void 0 ? void 0 : _a.window) === null || _b === void 0 ? void 0 : _b.closed) {
                // Make sure that there is sufficient time for whatever action to
                // complete. The window could have closed but the sign in network
                // call could still be in flight. This is specifically true for
                // Firefox or if the opener is in an iframe, in which case the oauth
                // helper closes the popup.
                this.pollId = window.setTimeout(() => {
                    this.pollId = null;
                    this.reject(_createError(this.auth, "popup-closed-by-user" /* AuthErrorCode.POPUP_CLOSED_BY_USER */));
                }, 8000 /* _Timeout.AUTH_EVENT */);
                return;
            }
            this.pollId = window.setTimeout(poll, _POLL_WINDOW_CLOSE_TIMEOUT.get());
        };
        poll();
    }
}
// Only one popup is ever shown at once. The lifecycle of the current popup
// can be managed / cancelled by the constructor.
PopupOperation.currentPopupAction = null;

/**
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
 */
const PENDING_REDIRECT_KEY = 'pendingRedirect';
// We only get one redirect outcome for any one auth, so just store it
// in here.
const redirectOutcomeMap = new Map();
class RedirectAction extends AbstractPopupRedirectOperation {
    constructor(auth, resolver, bypassAuthState = false) {
        super(auth, [
            "signInViaRedirect" /* AuthEventType.SIGN_IN_VIA_REDIRECT */,
            "linkViaRedirect" /* AuthEventType.LINK_VIA_REDIRECT */,
            "reauthViaRedirect" /* AuthEventType.REAUTH_VIA_REDIRECT */,
            "unknown" /* AuthEventType.UNKNOWN */
        ], resolver, undefined, bypassAuthState);
        this.eventId = null;
    }
    /**
     * Override the execute function; if we already have a redirect result, then
     * just return it.
     */
    async execute() {
        let readyOutcome = redirectOutcomeMap.get(this.auth._key());
        if (!readyOutcome) {
            try {
                const hasPendingRedirect = await _getAndClearPendingRedirectStatus(this.resolver, this.auth);
                const result = hasPendingRedirect ? await super.execute() : null;
                readyOutcome = () => Promise.resolve(result);
            }
            catch (e) {
                readyOutcome = () => Promise.reject(e);
            }
            redirectOutcomeMap.set(this.auth._key(), readyOutcome);
        }
        // If we're not bypassing auth state, the ready outcome should be set to
        // null.
        if (!this.bypassAuthState) {
            redirectOutcomeMap.set(this.auth._key(), () => Promise.resolve(null));
        }
        return readyOutcome();
    }
    async onAuthEvent(event) {
        if (event.type === "signInViaRedirect" /* AuthEventType.SIGN_IN_VIA_REDIRECT */) {
            return super.onAuthEvent(event);
        }
        else if (event.type === "unknown" /* AuthEventType.UNKNOWN */) {
            // This is a sentinel value indicating there's no pending redirect
            this.resolve(null);
            return;
        }
        if (event.eventId) {
            const user = await this.auth._redirectUserForId(event.eventId);
            if (user) {
                this.user = user;
                return super.onAuthEvent(event);
            }
            else {
                this.resolve(null);
            }
        }
    }
    async onExecution() { }
    cleanUp() { }
}
async function _getAndClearPendingRedirectStatus(resolver, auth) {
    const key = pendingRedirectKey(auth);
    const persistence = resolverPersistence(resolver);
    if (!(await persistence._isAvailable())) {
        return false;
    }
    const hasPendingRedirect = (await persistence._get(key)) === 'true';
    await persistence._remove(key);
    return hasPendingRedirect;
}
function _overrideRedirectResult(auth, result) {
    redirectOutcomeMap.set(auth._key(), result);
}
function resolverPersistence(resolver) {
    return _getInstance(resolver._redirectPersistence);
}
function pendingRedirectKey(auth) {
    return _persistenceKeyName(PENDING_REDIRECT_KEY, auth.config.apiKey, auth.name);
}
async function _getRedirectResult(auth, resolverExtern, bypassAuthState = false) {
    if (_isFirebaseServerApp(auth.app)) {
        return Promise.reject(_serverAppCurrentUserOperationNotSupportedError(auth));
    }
    const authInternal = _castAuth(auth);
    const resolver = _withDefaultResolver(authInternal, resolverExtern);
    const action = new RedirectAction(authInternal, resolver, bypassAuthState);
    const result = await action.execute();
    if (result && !bypassAuthState) {
        delete result.user._redirectEventId;
        await authInternal._persistUserIfCurrent(result.user);
        await authInternal._setRedirectUser(null, resolverExtern);
    }
    return result;
}

/**
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
 */
// The amount of time to store the UIDs of seen events; this is
// set to 10 min by default
const EVENT_DUPLICATION_CACHE_DURATION_MS = 10 * 60 * 1000;
class AuthEventManager {
    constructor(auth) {
        this.auth = auth;
        this.cachedEventUids = new Set();
        this.consumers = new Set();
        this.queuedRedirectEvent = null;
        this.hasHandledPotentialRedirect = false;
        this.lastProcessedEventTime = Date.now();
    }
    registerConsumer(authEventConsumer) {
        this.consumers.add(authEventConsumer);
        if (this.queuedRedirectEvent &&
            this.isEventForConsumer(this.queuedRedirectEvent, authEventConsumer)) {
            this.sendToConsumer(this.queuedRedirectEvent, authEventConsumer);
            this.saveEventToCache(this.queuedRedirectEvent);
            this.queuedRedirectEvent = null;
        }
    }
    unregisterConsumer(authEventConsumer) {
        this.consumers.delete(authEventConsumer);
    }
    onEvent(event) {
        // Check if the event has already been handled
        if (this.hasEventBeenHandled(event)) {
            return false;
        }
        let handled = false;
        this.consumers.forEach(consumer => {
            if (this.isEventForConsumer(event, consumer)) {
                handled = true;
                this.sendToConsumer(event, consumer);
                this.saveEventToCache(event);
            }
        });
        if (this.hasHandledPotentialRedirect || !isRedirectEvent(event)) {
            // If we've already seen a redirect before, or this is a popup event,
            // bail now
            return handled;
        }
        this.hasHandledPotentialRedirect = true;
        // If the redirect wasn't handled, hang on to it
        if (!handled) {
            this.queuedRedirectEvent = event;
            handled = true;
        }
        return handled;
    }
    sendToConsumer(event, consumer) {
        var _a;
        if (event.error && !isNullRedirectEvent(event)) {
            const code = ((_a = event.error.code) === null || _a === void 0 ? void 0 : _a.split('auth/')[1]) ||
                "internal-error" /* AuthErrorCode.INTERNAL_ERROR */;
            consumer.onError(_createError(this.auth, code));
        }
        else {
            consumer.onAuthEvent(event);
        }
    }
    isEventForConsumer(event, consumer) {
        const eventIdMatches = consumer.eventId === null ||
            (!!event.eventId && event.eventId === consumer.eventId);
        return consumer.filter.includes(event.type) && eventIdMatches;
    }
    hasEventBeenHandled(event) {
        if (Date.now() - this.lastProcessedEventTime >=
            EVENT_DUPLICATION_CACHE_DURATION_MS) {
            this.cachedEventUids.clear();
        }
        return this.cachedEventUids.has(eventUid(event));
    }
    saveEventToCache(event) {
        this.cachedEventUids.add(eventUid(event));
        this.lastProcessedEventTime = Date.now();
    }
}
function eventUid(e) {
    return [e.type, e.eventId, e.sessionId, e.tenantId].filter(v => v).join('-');
}
function isNullRedirectEvent({ type, error }) {
    return (type === "unknown" /* AuthEventType.UNKNOWN */ &&
        (error === null || error === void 0 ? void 0 : error.code) === `auth/${"no-auth-event" /* AuthErrorCode.NO_AUTH_EVENT */}`);
}
function isRedirectEvent(event) {
    switch (event.type) {
        case "signInViaRedirect" /* AuthEventType.SIGN_IN_VIA_REDIRECT */:
        case "linkViaRedirect" /* AuthEventType.LINK_VIA_REDIRECT */:
        case "reauthViaRedirect" /* AuthEventType.REAUTH_VIA_REDIRECT */:
            return true;
        case "unknown" /* AuthEventType.UNKNOWN */:
            return isNullRedirectEvent(event);
        default:
            return false;
    }
}

/**
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
 */
async function _getProjectConfig(auth, request = {}) {
    return _performApiRequest(auth, "GET" /* HttpMethod.GET */, "/v1/projects" /* Endpoint.GET_PROJECT_CONFIG */, request);
}

/**
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
 */
const IP_ADDRESS_REGEX = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
const HTTP_REGEX = /^https?/;
async function _validateOrigin(auth) {
    // Skip origin validation if we are in an emulated environment
    if (auth.config.emulator) {
        return;
    }
    const { authorizedDomains } = await _getProjectConfig(auth);
    for (const domain of authorizedDomains) {
        try {
            if (matchDomain(domain)) {
                return;
            }
        }
        catch (_a) {
            // Do nothing if there's a URL error; just continue searching
        }
    }
    // In the old SDK, this error also provides helpful messages.
    _fail(auth, "unauthorized-domain" /* AuthErrorCode.INVALID_ORIGIN */);
}
function matchDomain(expected) {
    const currentUrl = _getCurrentUrl();
    const { protocol, hostname } = new URL(currentUrl);
    if (expected.startsWith('chrome-extension://')) {
        const ceUrl = new URL(expected);
        if (ceUrl.hostname === '' && hostname === '') {
            // For some reason we're not parsing chrome URLs properly
            return (protocol === 'chrome-extension:' &&
                expected.replace('chrome-extension://', '') ===
                    currentUrl.replace('chrome-extension://', ''));
        }
        return protocol === 'chrome-extension:' && ceUrl.hostname === hostname;
    }
    if (!HTTP_REGEX.test(protocol)) {
        return false;
    }
    if (IP_ADDRESS_REGEX.test(expected)) {
        // The domain has to be exactly equal to the pattern, as an IP domain will
        // only contain the IP, no extra character.
        return hostname === expected;
    }
    // Dots in pattern should be escaped.
    const escapedDomainPattern = expected.replace(/\./g, '\\.');
    // Non ip address domains.
    // domain.com = *.domain.com OR domain.com
    const re = new RegExp('^(.+\\.' + escapedDomainPattern + '|' + escapedDomainPattern + ')$', 'i');
    return re.test(hostname);
}

/**
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
 */
const NETWORK_TIMEOUT = new Delay(30000, 60000);
/**
 * Reset unlaoded GApi modules. If gapi.load fails due to a network error,
 * it will stop working after a retrial. This is a hack to fix this issue.
 */
function resetUnloadedGapiModules() {
    // Clear last failed gapi.load state to force next gapi.load to first
    // load the failed gapi.iframes module.
    // Get gapix.beacon context.
    const beacon = _window().___jsl;
    // Get current hint.
    if (beacon === null || beacon === void 0 ? void 0 : beacon.H) {
        // Get gapi hint.
        for (const hint of Object.keys(beacon.H)) {
            // Requested modules.
            beacon.H[hint].r = beacon.H[hint].r || [];
            // Loaded modules.
            beacon.H[hint].L = beacon.H[hint].L || [];
            // Set requested modules to a copy of the loaded modules.
            beacon.H[hint].r = [...beacon.H[hint].L];
            // Clear pending callbacks.
            if (beacon.CP) {
                for (let i = 0; i < beacon.CP.length; i++) {
                    // Remove all failed pending callbacks.
                    beacon.CP[i] = null;
                }
            }
        }
    }
}
function loadGapi(auth) {
    return new Promise((resolve, reject) => {
        var _a, _b, _c;
        // Function to run when gapi.load is ready.
        function loadGapiIframe() {
            // The developer may have tried to previously run gapi.load and failed.
            // Run this to fix that.
            resetUnloadedGapiModules();
            gapi.load('gapi.iframes', {
                callback: () => {
                    resolve(gapi.iframes.getContext());
                },
                ontimeout: () => {
                    // The above reset may be sufficient, but having this reset after
                    // failure ensures that if the developer calls gapi.load after the
                    // connection is re-established and before another attempt to embed
                    // the iframe, it would work and would not be broken because of our
                    // failed attempt.
                    // Timeout when gapi.iframes.Iframe not loaded.
                    resetUnloadedGapiModules();
                    reject(_createError(auth, "network-request-failed" /* AuthErrorCode.NETWORK_REQUEST_FAILED */));
                },
                timeout: NETWORK_TIMEOUT.get()
            });
        }
        if ((_b = (_a = _window().gapi) === null || _a === void 0 ? void 0 : _a.iframes) === null || _b === void 0 ? void 0 : _b.Iframe) {
            // If gapi.iframes.Iframe available, resolve.
            resolve(gapi.iframes.getContext());
        }
        else if (!!((_c = _window().gapi) === null || _c === void 0 ? void 0 : _c.load)) {
            // Gapi loader ready, load gapi.iframes.
            loadGapiIframe();
        }
        else {
            // Create a new iframe callback when this is called so as not to overwrite
            // any previous defined callback. This happens if this method is called
            // multiple times in parallel and could result in the later callback
            // overwriting the previous one. This would end up with a iframe
            // timeout.
            const cbName = _generateCallbackName('iframefcb');
            // GApi loader not available, dynamically load platform.js.
            _window()[cbName] = () => {
                // GApi loader should be ready.
                if (!!gapi.load) {
                    loadGapiIframe();
                }
                else {
                    // Gapi loader failed, throw error.
                    reject(_createError(auth, "network-request-failed" /* AuthErrorCode.NETWORK_REQUEST_FAILED */));
                }
            };
            // Load GApi loader.
            return _loadJS(`${_gapiScriptUrl()}?onload=${cbName}`)
                .catch(e => reject(e));
        }
    }).catch(error => {
        // Reset cached promise to allow for retrial.
        cachedGApiLoader = null;
        throw error;
    });
}
let cachedGApiLoader = null;
function _loadGapi(auth) {
    cachedGApiLoader = cachedGApiLoader || loadGapi(auth);
    return cachedGApiLoader;
}

/**
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
 */
const PING_TIMEOUT = new Delay(5000, 15000);
const IFRAME_PATH = '__/auth/iframe';
const EMULATED_IFRAME_PATH = 'emulator/auth/iframe';
const IFRAME_ATTRIBUTES = {
    style: {
        position: 'absolute',
        top: '-100px',
        width: '1px',
        height: '1px'
    },
    'aria-hidden': 'true',
    tabindex: '-1'
};
// Map from apiHost to endpoint ID for passing into iframe. In current SDK, apiHost can be set to
// anything (not from a list of endpoints with IDs as in legacy), so this is the closest we can get.
const EID_FROM_APIHOST = new Map([
    ["identitytoolkit.googleapis.com" /* DefaultConfig.API_HOST */, 'p'],
    ['staging-identitytoolkit.sandbox.googleapis.com', 's'],
    ['test-identitytoolkit.sandbox.googleapis.com', 't'] // test
]);
function getIframeUrl(auth) {
    const config = auth.config;
    _assert(config.authDomain, auth, "auth-domain-config-required" /* AuthErrorCode.MISSING_AUTH_DOMAIN */);
    const url = config.emulator
        ? _emulatorUrl(config, EMULATED_IFRAME_PATH)
        : `https://${auth.config.authDomain}/${IFRAME_PATH}`;
    const params = {
        apiKey: config.apiKey,
        appName: auth.name,
        v: SDK_VERSION
    };
    const eid = EID_FROM_APIHOST.get(auth.config.apiHost);
    if (eid) {
        params.eid = eid;
    }
    const frameworks = auth._getFrameworks();
    if (frameworks.length) {
        params.fw = frameworks.join(',');
    }
    return `${url}?${querystring(params).slice(1)}`;
}
async function _openIframe(auth) {
    const context = await _loadGapi(auth);
    const gapi = _window().gapi;
    _assert(gapi, auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
    return context.open({
        where: document.body,
        url: getIframeUrl(auth),
        messageHandlersFilter: gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER,
        attributes: IFRAME_ATTRIBUTES,
        dontclear: true
    }, (iframe) => new Promise(async (resolve, reject) => {
        await iframe.restyle({
            // Prevent iframe from closing on mouse out.
            setHideOnLeave: false
        });
        const networkError = _createError(auth, "network-request-failed" /* AuthErrorCode.NETWORK_REQUEST_FAILED */);
        // Confirm iframe is correctly loaded.
        // To fallback on failure, set a timeout.
        const networkErrorTimer = _window().setTimeout(() => {
            reject(networkError);
        }, PING_TIMEOUT.get());
        // Clear timer and resolve pending iframe ready promise.
        function clearTimerAndResolve() {
            _window().clearTimeout(networkErrorTimer);
            resolve(iframe);
        }
        // This returns an IThenable. However the reject part does not call
        // when the iframe is not loaded.
        iframe.ping(clearTimerAndResolve).then(clearTimerAndResolve, () => {
            reject(networkError);
        });
    }));
}

/**
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
 */
const BASE_POPUP_OPTIONS = {
    location: 'yes',
    resizable: 'yes',
    statusbar: 'yes',
    toolbar: 'no'
};
const DEFAULT_WIDTH = 500;
const DEFAULT_HEIGHT = 600;
const TARGET_BLANK = '_blank';
const FIREFOX_EMPTY_URL = 'http://localhost';
class AuthPopup {
    constructor(window) {
        this.window = window;
        this.associatedEvent = null;
    }
    close() {
        if (this.window) {
            try {
                this.window.close();
            }
            catch (e) { }
        }
    }
}
function _open(auth, url, name, width = DEFAULT_WIDTH, height = DEFAULT_HEIGHT) {
    const top = Math.max((window.screen.availHeight - height) / 2, 0).toString();
    const left = Math.max((window.screen.availWidth - width) / 2, 0).toString();
    let target = '';
    const options = Object.assign(Object.assign({}, BASE_POPUP_OPTIONS), { width: width.toString(), height: height.toString(), top,
        left });
    // Chrome iOS 7 and 8 is returning an undefined popup win when target is
    // specified, even though the popup is not necessarily blocked.
    const ua = getUA().toLowerCase();
    if (name) {
        target = _isChromeIOS(ua) ? TARGET_BLANK : name;
    }
    if (_isFirefox(ua)) {
        // Firefox complains when invalid URLs are popped out. Hacky way to bypass.
        url = url || FIREFOX_EMPTY_URL;
        // Firefox disables by default scrolling on popup windows, which can create
        // issues when the user has many Google accounts, for instance.
        options.scrollbars = 'yes';
    }
    const optionsString = Object.entries(options).reduce((accum, [key, value]) => `${accum}${key}=${value},`, '');
    if (_isIOSStandalone(ua) && target !== '_self') {
        openAsNewWindowIOS(url || '', target);
        return new AuthPopup(null);
    }
    // about:blank getting sanitized causing browsers like IE/Edge to display
    // brief error message before redirecting to handler.
    const newWin = window.open(url || '', target, optionsString);
    _assert(newWin, auth, "popup-blocked" /* AuthErrorCode.POPUP_BLOCKED */);
    // Flaky on IE edge, encapsulate with a try and catch.
    try {
        newWin.focus();
    }
    catch (e) { }
    return new AuthPopup(newWin);
}
function openAsNewWindowIOS(url, target) {
    const el = document.createElement('a');
    el.href = url;
    el.target = target;
    const click = document.createEvent('MouseEvent');
    click.initMouseEvent('click', true, true, window, 1, 0, 0, 0, 0, false, false, false, false, 1, null);
    el.dispatchEvent(click);
}

/**
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
 */
/**
 * URL for Authentication widget which will initiate the OAuth handshake
 *
 * @internal
 */
const WIDGET_PATH = '__/auth/handler';
/**
 * URL for emulated environment
 *
 * @internal
 */
const EMULATOR_WIDGET_PATH = 'emulator/auth/handler';
/**
 * Fragment name for the App Check token that gets passed to the widget
 *
 * @internal
 */
const FIREBASE_APP_CHECK_FRAGMENT_ID = encodeURIComponent('fac');
async function _getRedirectUrl(auth, provider, authType, redirectUrl, eventId, additionalParams) {
    _assert(auth.config.authDomain, auth, "auth-domain-config-required" /* AuthErrorCode.MISSING_AUTH_DOMAIN */);
    _assert(auth.config.apiKey, auth, "invalid-api-key" /* AuthErrorCode.INVALID_API_KEY */);
    const params = {
        apiKey: auth.config.apiKey,
        appName: auth.name,
        authType,
        redirectUrl,
        v: SDK_VERSION,
        eventId
    };
    if (provider instanceof FederatedAuthProvider) {
        provider.setDefaultLanguage(auth.languageCode);
        params.providerId = provider.providerId || '';
        if (!isEmpty(provider.getCustomParameters())) {
            params.customParameters = JSON.stringify(provider.getCustomParameters());
        }
        // TODO set additionalParams from the provider as well?
        for (const [key, value] of Object.entries(additionalParams || {})) {
            params[key] = value;
        }
    }
    if (provider instanceof BaseOAuthProvider) {
        const scopes = provider.getScopes().filter(scope => scope !== '');
        if (scopes.length > 0) {
            params.scopes = scopes.join(',');
        }
    }
    if (auth.tenantId) {
        params.tid = auth.tenantId;
    }
    // TODO: maybe set eid as endipointId
    // TODO: maybe set fw as Frameworks.join(",")
    const paramsDict = params;
    for (const key of Object.keys(paramsDict)) {
        if (paramsDict[key] === undefined) {
            delete paramsDict[key];
        }
    }
    // Sets the App Check token to pass to the widget
    const appCheckToken = await auth._getAppCheckToken();
    const appCheckTokenFragment = appCheckToken
        ? `#${FIREBASE_APP_CHECK_FRAGMENT_ID}=${encodeURIComponent(appCheckToken)}`
        : '';
    // Start at index 1 to skip the leading '&' in the query string
    return `${getHandlerBase(auth)}?${querystring(paramsDict).slice(1)}${appCheckTokenFragment}`;
}
function getHandlerBase({ config }) {
    if (!config.emulator) {
        return `https://${config.authDomain}/${WIDGET_PATH}`;
    }
    return _emulatorUrl(config, EMULATOR_WIDGET_PATH);
}

/**
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
 */
/**
 * The special web storage event
 *
 */
const WEB_STORAGE_SUPPORT_KEY = 'webStorageSupport';
class BrowserPopupRedirectResolver {
    constructor() {
        this.eventManagers = {};
        this.iframes = {};
        this.originValidationPromises = {};
        this._redirectPersistence = browserSessionPersistence;
        this._completeRedirectFn = _getRedirectResult;
        this._overrideRedirectResult = _overrideRedirectResult;
    }
    // Wrapping in async even though we don't await anywhere in order
    // to make sure errors are raised as promise rejections
    async _openPopup(auth, provider, authType, eventId) {
        var _a;
        debugAssert((_a = this.eventManagers[auth._key()]) === null || _a === void 0 ? void 0 : _a.manager, '_initialize() not called before _openPopup()');
        const url = await _getRedirectUrl(auth, provider, authType, _getCurrentUrl(), eventId);
        return _open(auth, url, _generateEventId());
    }
    async _openRedirect(auth, provider, authType, eventId) {
        await this._originValidation(auth);
        const url = await _getRedirectUrl(auth, provider, authType, _getCurrentUrl(), eventId);
        _setWindowLocation(url);
        return new Promise(() => { });
    }
    _initialize(auth) {
        const key = auth._key();
        if (this.eventManagers[key]) {
            const { manager, promise } = this.eventManagers[key];
            if (manager) {
                return Promise.resolve(manager);
            }
            else {
                debugAssert(promise, 'If manager is not set, promise should be');
                return promise;
            }
        }
        const promise = this.initAndGetManager(auth);
        this.eventManagers[key] = { promise };
        // If the promise is rejected, the key should be removed so that the
        // operation can be retried later.
        promise.catch(() => {
            delete this.eventManagers[key];
        });
        return promise;
    }
    async initAndGetManager(auth) {
        const iframe = await _openIframe(auth);
        const manager = new AuthEventManager(auth);
        iframe.register('authEvent', (iframeEvent) => {
            _assert(iframeEvent === null || iframeEvent === void 0 ? void 0 : iframeEvent.authEvent, auth, "invalid-auth-event" /* AuthErrorCode.INVALID_AUTH_EVENT */);
            // TODO: Consider splitting redirect and popup events earlier on
            const handled = manager.onEvent(iframeEvent.authEvent);
            return { status: handled ? "ACK" /* GapiOutcome.ACK */ : "ERROR" /* GapiOutcome.ERROR */ };
        }, gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER);
        this.eventManagers[auth._key()] = { manager };
        this.iframes[auth._key()] = iframe;
        return manager;
    }
    _isIframeWebStorageSupported(auth, cb) {
        const iframe = this.iframes[auth._key()];
        iframe.send(WEB_STORAGE_SUPPORT_KEY, { type: WEB_STORAGE_SUPPORT_KEY }, result => {
            var _a;
            const isSupported = (_a = result === null || result === void 0 ? void 0 : result[0]) === null || _a === void 0 ? void 0 : _a[WEB_STORAGE_SUPPORT_KEY];
            if (isSupported !== undefined) {
                cb(!!isSupported);
            }
            _fail(auth, "internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
        }, gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER);
    }
    _originValidation(auth) {
        const key = auth._key();
        if (!this.originValidationPromises[key]) {
            this.originValidationPromises[key] = _validateOrigin(auth);
        }
        return this.originValidationPromises[key];
    }
    get _shouldInitProactively() {
        // Mobile browsers and Safari need to optimistically initialize
        return _isMobileBrowser() || _isSafari() || _isIOS();
    }
}
/**
 * An implementation of {@link PopupRedirectResolver} suitable for browser
 * based applications.
 *
 * @remarks
 * This method does not work in a Node.js environment.
 *
 * @public
 */
const browserPopupRedirectResolver = BrowserPopupRedirectResolver;

var name$1 = "@firebase/auth";
var version$1 = "1.7.1";

/**
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
 */
class AuthInterop {
    constructor(auth) {
        this.auth = auth;
        this.internalListeners = new Map();
    }
    getUid() {
        var _a;
        this.assertAuthConfigured();
        return ((_a = this.auth.currentUser) === null || _a === void 0 ? void 0 : _a.uid) || null;
    }
    async getToken(forceRefresh) {
        this.assertAuthConfigured();
        await this.auth._initializationPromise;
        if (!this.auth.currentUser) {
            return null;
        }
        const accessToken = await this.auth.currentUser.getIdToken(forceRefresh);
        return { accessToken };
    }
    addAuthTokenListener(listener) {
        this.assertAuthConfigured();
        if (this.internalListeners.has(listener)) {
            return;
        }
        const unsubscribe = this.auth.onIdTokenChanged(user => {
            listener((user === null || user === void 0 ? void 0 : user.stsTokenManager.accessToken) || null);
        });
        this.internalListeners.set(listener, unsubscribe);
        this.updateProactiveRefresh();
    }
    removeAuthTokenListener(listener) {
        this.assertAuthConfigured();
        const unsubscribe = this.internalListeners.get(listener);
        if (!unsubscribe) {
            return;
        }
        this.internalListeners.delete(listener);
        unsubscribe();
        this.updateProactiveRefresh();
    }
    assertAuthConfigured() {
        _assert(this.auth._initializationPromise, "dependent-sdk-initialized-before-auth" /* AuthErrorCode.DEPENDENT_SDK_INIT_BEFORE_AUTH */);
    }
    updateProactiveRefresh() {
        if (this.internalListeners.size > 0) {
            this.auth._startProactiveRefresh();
        }
        else {
            this.auth._stopProactiveRefresh();
        }
    }
}

/**
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
 */
function getVersionForPlatform(clientPlatform) {
    switch (clientPlatform) {
        case "Node" /* ClientPlatform.NODE */:
            return 'node';
        case "ReactNative" /* ClientPlatform.REACT_NATIVE */:
            return 'rn';
        case "Worker" /* ClientPlatform.WORKER */:
            return 'webworker';
        case "Cordova" /* ClientPlatform.CORDOVA */:
            return 'cordova';
        case "WebExtension" /* ClientPlatform.WEB_EXTENSION */:
            return 'web-extension';
        default:
            return undefined;
    }
}
/** @internal */
function registerAuth(clientPlatform) {
    _registerComponent(new Component("auth" /* _ComponentName.AUTH */, (container, { options: deps }) => {
        const app = container.getProvider('app').getImmediate();
        const heartbeatServiceProvider = container.getProvider('heartbeat');
        const appCheckServiceProvider = container.getProvider('app-check-internal');
        const { apiKey, authDomain } = app.options;
        _assert(apiKey && !apiKey.includes(':'), "invalid-api-key" /* AuthErrorCode.INVALID_API_KEY */, { appName: app.name });
        const config = {
            apiKey,
            authDomain,
            clientPlatform,
            apiHost: "identitytoolkit.googleapis.com" /* DefaultConfig.API_HOST */,
            tokenApiHost: "securetoken.googleapis.com" /* DefaultConfig.TOKEN_API_HOST */,
            apiScheme: "https" /* DefaultConfig.API_SCHEME */,
            sdkClientVersion: _getClientVersion(clientPlatform)
        };
        const authInstance = new AuthImpl(app, heartbeatServiceProvider, appCheckServiceProvider, config);
        _initializeAuthInstance(authInstance, deps);
        return authInstance;
    }, "PUBLIC" /* ComponentType.PUBLIC */)
        /**
         * Auth can only be initialized by explicitly calling getAuth() or initializeAuth()
         * For why we do this, See go/firebase-next-auth-init
         */
        .setInstantiationMode("EXPLICIT" /* InstantiationMode.EXPLICIT */)
        /**
         * Because all firebase products that depend on auth depend on auth-internal directly,
         * we need to initialize auth-internal after auth is initialized to make it available to other firebase products.
         */
        .setInstanceCreatedCallback((container, _instanceIdentifier, _instance) => {
        const authInternalProvider = container.getProvider("auth-internal" /* _ComponentName.AUTH_INTERNAL */);
        authInternalProvider.initialize();
    }));
    _registerComponent(new Component("auth-internal" /* _ComponentName.AUTH_INTERNAL */, container => {
        const auth = _castAuth(container.getProvider("auth" /* _ComponentName.AUTH */).getImmediate());
        return (auth => new AuthInterop(auth))(auth);
    }, "PRIVATE" /* ComponentType.PRIVATE */).setInstantiationMode("EXPLICIT" /* InstantiationMode.EXPLICIT */));
    registerVersion(name$1, version$1, getVersionForPlatform(clientPlatform));
    // BUILD_TARGET will be replaced by values like esm5, esm2017, cjs5, etc during the compilation
    registerVersion(name$1, version$1, 'esm2017');
}

/**
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
 */
const DEFAULT_ID_TOKEN_MAX_AGE = 5 * 60;
const authIdTokenMaxAge = getExperimentalSetting('authIdTokenMaxAge') || DEFAULT_ID_TOKEN_MAX_AGE;
let lastPostedIdToken = null;
const mintCookieFactory = (url) => async (user) => {
    const idTokenResult = user && (await user.getIdTokenResult());
    const idTokenAge = idTokenResult &&
        (new Date().getTime() - Date.parse(idTokenResult.issuedAtTime)) / 1000;
    if (idTokenAge && idTokenAge > authIdTokenMaxAge) {
        return;
    }
    // Specifically trip null => undefined when logged out, to delete any existing cookie
    const idToken = idTokenResult === null || idTokenResult === void 0 ? void 0 : idTokenResult.token;
    if (lastPostedIdToken === idToken) {
        return;
    }
    lastPostedIdToken = idToken;
    await fetch(url, {
        method: idToken ? 'POST' : 'DELETE',
        headers: idToken
            ? {
                'Authorization': `Bearer ${idToken}`
            }
            : {}
    });
};
/**
 * Returns the Auth instance associated with the provided {@link @firebase/app#FirebaseApp}.
 * If no instance exists, initializes an Auth instance with platform-specific default dependencies.
 *
 * @param app - The Firebase App.
 *
 * @public
 */
function getAuth(app = getApp()) {
    const provider = _getProvider(app, 'auth');
    if (provider.isInitialized()) {
        return provider.getImmediate();
    }
    const auth = initializeAuth(app, {
        popupRedirectResolver: browserPopupRedirectResolver,
        persistence: [
            indexedDBLocalPersistence,
            browserLocalPersistence,
            browserSessionPersistence
        ]
    });
    const authTokenSyncPath = getExperimentalSetting('authTokenSyncURL');
    // Only do the Cookie exchange in a secure context
    if (authTokenSyncPath &&
        typeof isSecureContext === 'boolean' &&
        isSecureContext) {
        // Don't allow urls (XSS possibility), only paths on the same domain
        const authTokenSyncUrl = new URL(authTokenSyncPath, location.origin);
        if (location.origin === authTokenSyncUrl.origin) {
            const mintCookie = mintCookieFactory(authTokenSyncUrl.toString());
            beforeAuthStateChanged(auth, mintCookie, () => mintCookie(auth.currentUser));
            onIdTokenChanged(auth, user => mintCookie(user));
        }
    }
    const authEmulatorHost = getDefaultEmulatorHost('auth');
    if (authEmulatorHost) {
        connectAuthEmulator(auth, `http://${authEmulatorHost}`);
    }
    return auth;
}
function getScriptParentElement() {
    var _a, _b;
    return (_b = (_a = document.getElementsByTagName('head')) === null || _a === void 0 ? void 0 : _a[0]) !== null && _b !== void 0 ? _b : document;
}
_setExternalJSProvider({
    loadJS(url) {
        // TODO: consider adding timeout support & cancellation
        return new Promise((resolve, reject) => {
            const el = document.createElement('script');
            el.setAttribute('src', url);
            el.onload = resolve;
            el.onerror = e => {
                const error = _createError("internal-error" /* AuthErrorCode.INTERNAL_ERROR */);
                error.customData = e;
                reject(error);
            };
            el.type = 'text/javascript';
            el.charset = 'UTF-8';
            getScriptParentElement().appendChild(el);
        });
    },
    gapiScript: 'https://apis.google.com/js/api.js',
    recaptchaV2Script: 'https://www.google.com/recaptcha/api.js',
    recaptchaEnterpriseScript: 'https://www.google.com/recaptcha/enterprise.js?render='
});
registerAuth("Browser" /* ClientPlatform.BROWSER */);

var name = "firebase";
var version = "10.11.0";

/**
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
 */
registerVersion(name, version, 'app');

function createGlobalStates$d() {
  const [multiuser, setMultiuser] = createSignal(false);
  return {
    multiuser,
    setMultiuser
  };
}
const gvMultiuser = createRoot(createGlobalStates$d);

const firebaseConfig = {
  apiKey: "AIzaSyC9oGhGaax8DlSh-w9pC3TCeIJZzxAw-XU",
  authDomain: "oakvar-app.firebaseapp.com",
  projectId: "oakvar-app",
  storageBucket: "oakvar-app.appspot.com",
  messagingSenderId: "1070951630158",
  appId: "1:1070951630158:web:885d40bf4a42a1fc4cca1f",
  measurementId: "G-0PV5B1ZF6B"
};
const firebaseApp = initializeApp(firebaseConfig);
function createGlobalStates$c() {
  const {
    multiuser
  } = gvMultiuser;
  const [auth, setAuth] = createSignal(null);
  const {
    systemSetupNeeded
  } = gvSystemSetupNeeded;
  createEffect(function() {
    if (multiuser() == true || systemSetupNeeded()) {
      try {
        setAuth(getAuth(firebaseApp));
      } catch (err) {
        console.error(err);
      }
    }
  });
  return {
    auth,
    sendSignInLinkToEmail
  };
}
const gvFirebase = createRoot(createGlobalStates$c);

function createGlobalStates$b() {
  const [tabName, setTabName] = createSignal("home");
  return {
    tabName,
    setTabName
  };
}
const gvTabName = createRoot(createGlobalStates$b);

function createGlobalStates$a() {
  const [logged, setLogged] = createSignal(false);
  const [showAuth, setShowAuth] = createSignal(false);
  const [admin, setAdmin] = createSignal(false);
  const {
    setEmail,
    setPassword
  } = gvEmail;
  const {
    serverUrl,
    withCredentials
  } = gvServer;
  const {
    setTabName
  } = gvTabName;
  const {
    auth
  } = gvFirebase;
  const [reloginChecked, setReloginChecked] = createSignal(false);
  function getEmailFromUserResponse(user) {
    let email = user.email;
    if (email) {
      return email;
    }
    for (const data of user.providerData) {
      email = data.email;
      if (email) {
        return email;
      }
    }
    return null;
  }
  function afterLogin(user) {
    const email = getEmailFromUserResponse(user);
    if (!email) {
      handleError({
        "response": {
          "data": "No email was found in login data."
        }
      });
      return;
    }
    axios.post(serverUrl + "/server/loginsuccess", {
      email
    }, {
      withCredentials
    }).then(function(res) {
      setEmail(res.data.email);
      setAdmin(res.data.admin);
      setLogged(true);
      setShowAuth(false);
    }).catch(function(err) {
      handleError(err);
    });
  }
  function afterLogout() {
    signOut(auth()).catch(function(err) {
      handleError(err);
    });
    axios.get(serverUrl + "/server/logout", {
      withCredentials
    }).then(function(res) {
      if (res.status == 200) {
        setLogged(false);
        setEmail(null);
        setPassword(null);
        setTabName("home");
        setAdmin(false);
      }
    }).catch(function(err) {
      handleError(err);
    });
  }
  return {
    logged,
    setLogged,
    admin,
    setAdmin,
    showAuth,
    setShowAuth,
    afterLogin,
    afterLogout,
    reloginChecked,
    setReloginChecked
  };
}
const gvLogin = createRoot(createGlobalStates$a);

function createGlobalStates$9() {
  const [appLoading, setAppLoading] = createSignal(true);
  return {
    appLoading,
    setAppLoading
  };
}
const gvAppLoading = createRoot(createGlobalStates$9);

var _tmpl$$1n = /* @__PURE__ */ template(`<a id=tabhead_{props.tabName} href=# class=tabhead>`);
function TabHead(props) {
  const {
    tabName,
    setTabName
  } = gvTabName;
  return (() => {
    var _el$ = _tmpl$$1n();
    _el$.$$click = function(evt) {
      if (props.callback) {
        props.callback(evt);
      } else {
        setTabName(props.tabName);
      }
    };
    insert(_el$, () => props.svg, null);
    insert(_el$, () => props.title, null);
    createRenderEffect((_p$) => {
      var _v$ = !!(tabName() == props.tabName), _v$2 = !!props.disable, _v$3 = !!props.disable, _v$4 = !props.disable;
      _v$ !== _p$.e && _el$.classList.toggle("selected", _p$.e = _v$);
      _v$2 !== _p$.t && _el$.classList.toggle("pointer-events-none", _p$.t = _v$2);
      _v$3 !== _p$.a && _el$.classList.toggle("text-gray-400", _p$.a = _v$3);
      _v$4 !== _p$.o && _el$.classList.toggle("text-gray-600", _p$.o = _v$4);
      return _p$;
    }, {
      e: void 0,
      t: void 0,
      a: void 0,
      o: void 0
    });
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$1m = /* @__PURE__ */ template(`<svg stroke-width=0>`);
function IconTemplate(iconSrc, props) {
  const mergedProps = mergeProps(iconSrc.a, props);
  const [_, svgProps] = splitProps(mergedProps, ["src"]);
  const [content, setContent] = createSignal("");
  const rawContent = createMemo(() => props.title ? `${iconSrc.c}<title>${props.title}</title>` : iconSrc.c);
  createEffect(() => setContent(rawContent()));
  onCleanup(() => {
    setContent("");
  });
  return (() => {
    var _el$ = _tmpl$$1m();
    spread$1(_el$, mergeProps({
      get stroke() {
        return iconSrc.a?.stroke;
      },
      get color() {
        return props.color || "currentColor";
      },
      get fill() {
        return props.color || "currentColor";
      },
      get style() {
        return {
          ...props.style,
          overflow: "visible"
        };
      }
    }, svgProps, {
      get height() {
        return props.size || "1em";
      },
      get width() {
        return props.size || "1em";
      },
      "xmlns": "http://www.w3.org/2000/svg",
      get innerHTML() {
        return content();
      }
    }), true, true);
    insert(_el$, () => isServer );
    return _el$;
  })();
}

function HiOutlineArrowDown(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 13.5 12 21m0 0-7.5-7.5M12 21V3"/>'
      }, props)
  }
  function HiOutlineArrowPath(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"/>'
      }, props)
  }
  function HiOutlineArrowRight(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/>'
      }, props)
  }
  function HiOutlineArrowUp(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18"/>'
      }, props)
  }
  function HiOutlineChevronDown(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m19.5 8.25-7.5 7.5-7.5-7.5"/>'
      }, props)
  }
  function HiOutlineChevronLeft(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.75 19.5 8.25 12l7.5-7.5"/>'
      }, props)
  }
  function HiOutlineChevronRight(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>'
      }, props)
  }
  function HiOutlineHome(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>'
      }, props)
  }
  function HiOutlineMinus(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 12h-15"/>'
      }, props)
  }
  function HiOutlineXCircle(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>'
      }, props)
  }
  function HiOutlineXMark(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","viewBox":"0 0 24 24"},
        c: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18 18 6M6 6l12 12"/>'
      }, props)
  }

function TabHeadHome() {
  const svg = createComponent(HiOutlineHome, {
    "class": "tabheadicon",
    color: "rgb(156 163 175)"
  });
  return createComponent(TabHead, {
    tabName: "home",
    title: "Home",
    svg
  });
}

function TbArrowBackUp(props) {
      return IconTemplate({
        a: {"xmlns":"http://www.w3.org/2000/svg","class":"icon icon-tabler icon-tabler-arrow-back-up","width":"24","height":"24","viewBox":"0 0 24 24","stroke-width":"2","stroke":"currentColor","fill":"none","stroke-linecap":"round","stroke-linejoin":"round"},
        c: '<path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M9 14l-4 -4l4 -4"/><path d="M5 10h11a4 4 0 1 1 0 8h-1"/>'
      }, props)
  }
  function TbFileUpload(props) {
      return IconTemplate({
        a: {"xmlns":"http://www.w3.org/2000/svg","class":"icon icon-tabler icon-tabler-file-upload","width":"24","height":"24","viewBox":"0 0 24 24","stroke-width":"2","stroke":"currentColor","fill":"none","stroke-linecap":"round","stroke-linejoin":"round"},
        c: '<path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z"/><path d="M12 11v6"/><path d="M9.5 13.5l2.5 -2.5l2.5 2.5"/>'
      }, props)
  }
  function TbServerOff(props) {
      return IconTemplate({
        a: {"xmlns":"http://www.w3.org/2000/svg","class":"icon icon-tabler icon-tabler-server-off","width":"24","height":"24","viewBox":"0 0 24 24","stroke-width":"2","stroke":"currentColor","fill":"none","stroke-linecap":"round","stroke-linejoin":"round"},
        c: '<path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 12h-6a3 3 0 0 1 -3 -3v-2c0 -1.083 .574 -2.033 1.435 -2.56m3.565 -.44h10a3 3 0 0 1 3 3v2a3 3 0 0 1 -3 3h-2"/><path d="M16 12h2a3 3 0 0 1 3 3v2m-1.448 2.568a2.986 2.986 0 0 1 -1.552 .432h-12a3 3 0 0 1 -3 -3v-2a3 3 0 0 1 3 -3h6"/><path d="M7 8v.01"/><path d="M7 16v.01"/><path d="M3 3l18 18"/>'
      }, props)
  }

function TabHeadSubmit() {
  const {
    logged
  } = gvLogin;
  const {
    multiuser
  } = gvMultiuser;
  const svg = createComponent(TbFileUpload, {
    "class": "tabheadicon",
    color: "rgb(156 163 175)"
  });
  return createComponent(TabHead, {
    tabName: "submit",
    title: "Analyze",
    svg,
    get disable() {
      return createMemo(() => !!multiuser())() && !logged();
    }
  });
}

function AiOutlineCloudUpload(props) {
      return IconTemplate({
        a: {"viewBox":"0 0 1024 1024"},
        c: '<path d="M518.3 459a8 8 0 0 0-12.6 0l-112 141.7a7.98 7.98 0 0 0 6.3 12.9h73.9V856c0 4.4 3.6 8 8 8h60c4.4 0 8-3.6 8-8V613.7H624c6.7 0 10.4-7.7 6.3-12.9L518.3 459z"/><path d="M811.4 366.7C765.6 245.9 648.9 160 512.2 160S258.8 245.8 213 366.6C127.3 389.1 64 467.2 64 560c0 110.5 89.5 200 199.9 200H304c4.4 0 8-3.6 8-8v-60c0-4.4-3.6-8-8-8h-40.1c-33.7 0-65.4-13.4-89-37.7-23.5-24.2-36-56.8-34.9-90.6.9-26.4 9.9-51.2 26.2-72.1 16.7-21.3 40.1-36.8 66.1-43.7l37.9-9.9 13.9-36.6c8.6-22.8 20.6-44.1 35.7-63.4a245.6 245.6 0 0 1 52.4-49.9c41.1-28.9 89.5-44.2 140-44.2s98.9 15.3 140 44.2c19.9 14 37.5 30.8 52.4 49.9 15.1 19.3 27.1 40.7 35.7 63.4l13.8 36.5 37.8 10C846.1 454.5 884 503.8 884 560c0 33.1-12.9 64.3-36.3 87.7a123.07 123.07 0 0 1-87.6 36.3H720c-4.4 0-8 3.6-8 8v60c0 4.4 3.6 8 8 8h40.1C870.5 760 960 670.5 960 560c0-92.7-63.1-170.7-148.6-193.3z"/>'
      }, props)
  }
  function AiOutlineOrderedList(props) {
      return IconTemplate({
        a: {"viewBox":"0 0 1024 1024"},
        c: '<path d="M920 760H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0-568H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0 284H336c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h584c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM216 712H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h72.4v20.5h-35.7c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h35.7V838H100c-2.2 0-4 1.8-4 4v34c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4V716c0-2.2-1.8-4-4-4zM100 188h38v120c0 2.2 1.8 4 4 4h40c2.2 0 4-1.8 4-4V152c0-4.4-3.6-8-8-8h-78c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4zm116 240H100c-2.2 0-4 1.8-4 4v36c0 2.2 1.8 4 4 4h68.4l-70.3 77.7a8.3 8.3 0 0 0-2.1 5.4V592c0 2.2 1.8 4 4 4h116c2.2 0 4-1.8 4-4v-36c0-2.2-1.8-4-4-4h-68.4l70.3-77.7a8.3 8.3 0 0 0 2.1-5.4V432c0-2.2-1.8-4-4-4z"/>'
      }, props)
  }

function TabHeadJobs() {
  const {
    logged
  } = gvLogin;
  const {
    multiuser
  } = gvMultiuser;
  const svg = createComponent(AiOutlineOrderedList, {
    "class": "tabheadicon",
    color: "rgb(156 163 175)"
  });
  return createComponent(TabHead, {
    tabName: "jobs",
    title: "Results",
    svg,
    get disable() {
      return createMemo(() => !!multiuser())() && !logged();
    }
  });
}

function RiBuildingsStore2Line(props) {
      return IconTemplate({
        a: {"viewBox":"0 0 24 24"},
        c: '<path fill="currentColor" d="M21 13.242V20h1v2H2v-2h1v-6.758A4.496 4.496 0 0 1 1 9.5c0-.827.224-1.624.633-2.303L4.345 2.5a1 1 0 0 1 .866-.5H18.79a1 1 0 0 1 .866.5l2.703 4.682c.418.694.642 1.49.642 2.318 0 1.56-.794 2.935-2 3.742Zm-2 .73a4.496 4.496 0 0 1-3.75-1.36A4.496 4.496 0 0 1 12 14.001a4.496 4.496 0 0 1-3.25-1.387A4.496 4.496 0 0 1 5 13.973V20h14v-6.027ZM5.789 4 3.356 8.213a2.5 2.5 0 1 0 4.466 2.216c.335-.837 1.52-.837 1.856 0a2.5 2.5 0 0 0 4.644 0c.335-.837 1.52-.837 1.856 0a2.5 2.5 0 1 0 4.457-2.232L18.21 4H5.79Z"/>'
      }, props)
  }
  function RiSystemLoginCircleLine(props) {
      return IconTemplate({
        a: {"viewBox":"0 0 24 24"},
        c: '<path fill="currentColor" d="M10 11V8l5 4-5 4v-3H1v-2h9Zm-7.542 4h2.124A8.003 8.003 0 0 0 20 12 8 8 0 0 0 4.582 9H2.458C3.732 4.943 7.522 2 12 2c5.523 0 10 4.477 10 10s-4.477 10-10 10c-4.478 0-8.268-2.943-9.542-7Z"/>'
      }, props)
  }
  function RiSystemLogoutCircleRLine(props) {
      return IconTemplate({
        a: {"viewBox":"0 0 24 24"},
        c: '<path fill="currentColor" d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2a9.985 9.985 0 0 1 8 4h-2.71a8 8 0 1 0 .001 12h2.71A9.985 9.985 0 0 1 12 22Zm7-6v-3h-8v-2h8V8l5 4-5 4Z"/>'
      }, props)
  }

function TabHeadStore() {
  const svg = createComponent(RiBuildingsStore2Line, {
    "class": "tabheadicon",
    color: "rgb(156 163 175)"
  });
  return createComponent(TabHead, {
    tabName: "store",
    title: "Store",
    svg
  });
}

var _tmpl$$1l = /* @__PURE__ */ template(`<svg class=tabheadicon xmlns=http://www.w3.org/2000/svg fill=none viewBox="0 0 24 24"stroke-width=2 stroke=currentColor><path stroke-linecap=round stroke-linejoin=round d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75">`);
function TabHeadSystem() {
  const svg = _tmpl$$1l();
  return createComponent(TabHead, {
    tabName: "system",
    title: "System",
    svg
  });
}

var _tmpl$$1k = /* @__PURE__ */ template(`<div class="px-2 pb-8">`), _tmpl$2$g = /* @__PURE__ */ template(`<div class="px-2 text-xs text-gray-600 truncate cursor-default">`), _tmpl$3$a = /* @__PURE__ */ template(`<div>`);
function TabHeadLogging() {
  const {
    logged,
    setLogged,
    showAuth,
    setShowAuth,
    afterLogout
  } = gvLogin;
  const {
    multiuser
  } = gvMultiuser;
  const {
    email,
    setEmail,
    setPassword
  } = gvEmail;
  const svgLogin = createComponent(RiSystemLoginCircleLine, {
    "class": "tabheadicon",
    color: "rgb(156 163 175)"
  });
  const svgLogout = createComponent(RiSystemLogoutCircleRLine, {
    "class": "tabheadicon",
    color: "rgb(156 163 175)"
  });
  function onClickLogin(_) {
    setShowAuth(!showAuth());
  }
  function onClickLogout(_) {
    afterLogout();
  }
  return (() => {
    var _el$ = _tmpl$$1k();
    insert(_el$, createComponent(Show, {
      get when() {
        return multiuser();
      },
      get children() {
        return createComponent(Show, {
          get when() {
            return !logged();
          },
          get fallback() {
            return (() => {
              var _el$2 = _tmpl$3$a();
              insert(_el$2, createComponent(Show, {
                get when() {
                  return email();
                },
                get children() {
                  var _el$3 = _tmpl$2$g();
                  insert(_el$3, email);
                  createRenderEffect(() => setAttribute(_el$3, "title", email()));
                  return _el$3;
                }
              }), null);
              insert(_el$2, createComponent(TabHead, {
                tabName: "",
                title: "Sign out",
                svg: svgLogout,
                callback: onClickLogout
              }), null);
              return _el$2;
            })();
          },
          get children() {
            return createComponent(TabHead, {
              tabName: "",
              title: "Sign in",
              svg: svgLogin,
              callback: onClickLogin
            });
          }
        });
      }
    }));
    return _el$;
  })();
}

var _tmpl$$1j = /* @__PURE__ */ template(`<div id=verdiv class="text-xs absolute left-4 bottom-2 text-gray-400"><span class=text-xs>OakVar </span><span class="curverspan text-xs">`);
const {
  serverUrl: serverUrl$5
} = gvServer;
function VersionSlot() {
  const [pkg_ver] = createResource(fetchPkgVer);
  async function fetchPkgVer() {
    if (serverUrl$5 == void 0) {
      return null;
    }
    try {
      const res = await axios.get(serverUrl$5 + "/submit/pkgver");
      return res.data.pkg_ver;
    } catch (err) {
      console.error(err);
      handleError(err);
    }
  }
  return createComponent(Show, {
    get when() {
      return pkg_ver() != null;
    },
    get children() {
      var _el$ = _tmpl$$1j(), _el$2 = _el$.firstChild; _el$2.firstChild;
      insert(_el$2, pkg_ver, null);
      return _el$;
    }
  });
}

const $RAW = Symbol("store-raw"),
  $NODE = Symbol("store-node"),
  $HAS = Symbol("store-has"),
  $SELF = Symbol("store-self");
function wrap$1(value) {
  let p = value[$PROXY];
  if (!p) {
    Object.defineProperty(value, $PROXY, {
      value: (p = new Proxy(value, proxyTraps$1))
    });
    if (!Array.isArray(value)) {
      const keys = Object.keys(value),
        desc = Object.getOwnPropertyDescriptors(value);
      for (let i = 0, l = keys.length; i < l; i++) {
        const prop = keys[i];
        if (desc[prop].get) {
          Object.defineProperty(value, prop, {
            enumerable: desc[prop].enumerable,
            get: desc[prop].get.bind(p)
          });
        }
      }
    }
  }
  return p;
}
function isWrappable(obj) {
  let proto;
  return (
    obj != null &&
    typeof obj === "object" &&
    (obj[$PROXY] ||
      !(proto = Object.getPrototypeOf(obj)) ||
      proto === Object.prototype ||
      Array.isArray(obj))
  );
}
function unwrap(item, set = new Set()) {
  let result, unwrapped, v, prop;
  if ((result = item != null && item[$RAW])) return result;
  if (!isWrappable(item) || set.has(item)) return item;
  if (Array.isArray(item)) {
    if (Object.isFrozen(item)) item = item.slice(0);
    else set.add(item);
    for (let i = 0, l = item.length; i < l; i++) {
      v = item[i];
      if ((unwrapped = unwrap(v, set)) !== v) item[i] = unwrapped;
    }
  } else {
    if (Object.isFrozen(item)) item = Object.assign({}, item);
    else set.add(item);
    const keys = Object.keys(item),
      desc = Object.getOwnPropertyDescriptors(item);
    for (let i = 0, l = keys.length; i < l; i++) {
      prop = keys[i];
      if (desc[prop].get) continue;
      v = item[prop];
      if ((unwrapped = unwrap(v, set)) !== v) item[prop] = unwrapped;
    }
  }
  return item;
}
function getNodes(target, symbol) {
  let nodes = target[symbol];
  if (!nodes)
    Object.defineProperty(target, symbol, {
      value: (nodes = Object.create(null))
    });
  return nodes;
}
function getNode(nodes, property, value) {
  if (nodes[property]) return nodes[property];
  const [s, set] = createSignal(value, {
    equals: false,
    internal: true
  });
  s.$ = set;
  return (nodes[property] = s);
}
function proxyDescriptor$1(target, property) {
  const desc = Reflect.getOwnPropertyDescriptor(target, property);
  if (!desc || desc.get || !desc.configurable || property === $PROXY || property === $NODE)
    return desc;
  delete desc.value;
  delete desc.writable;
  desc.get = () => target[$PROXY][property];
  return desc;
}
function trackSelf(target) {
  getListener() && getNode(getNodes(target, $NODE), $SELF)();
}
function ownKeys(target) {
  trackSelf(target);
  return Reflect.ownKeys(target);
}
const proxyTraps$1 = {
  get(target, property, receiver) {
    if (property === $RAW) return target;
    if (property === $PROXY) return receiver;
    if (property === $TRACK) {
      trackSelf(target);
      return receiver;
    }
    const nodes = getNodes(target, $NODE);
    const tracked = nodes[property];
    let value = tracked ? tracked() : target[property];
    if (property === $NODE || property === $HAS || property === "__proto__") return value;
    if (!tracked) {
      const desc = Object.getOwnPropertyDescriptor(target, property);
      if (
        getListener() &&
        (typeof value !== "function" || target.hasOwnProperty(property)) &&
        !(desc && desc.get)
      )
        value = getNode(nodes, property, value)();
    }
    return isWrappable(value) ? wrap$1(value) : value;
  },
  has(target, property) {
    if (
      property === $RAW ||
      property === $PROXY ||
      property === $TRACK ||
      property === $NODE ||
      property === $HAS ||
      property === "__proto__"
    )
      return true;
    getListener() && getNode(getNodes(target, $HAS), property)();
    return property in target;
  },
  set() {
    return true;
  },
  deleteProperty() {
    return true;
  },
  ownKeys: ownKeys,
  getOwnPropertyDescriptor: proxyDescriptor$1
};
function setProperty(state, property, value, deleting = false) {
  if (!deleting && state[property] === value) return;
  const prev = state[property],
    len = state.length;
  if (value === undefined) {
    delete state[property];
    if (state[$HAS] && state[$HAS][property] && prev !== undefined) state[$HAS][property].$();
  } else {
    state[property] = value;
    if (state[$HAS] && state[$HAS][property] && prev === undefined) state[$HAS][property].$();
  }
  let nodes = getNodes(state, $NODE),
    node;
  if ((node = getNode(nodes, property, prev))) node.$(() => value);
  if (Array.isArray(state) && state.length !== len) {
    for (let i = state.length; i < len; i++) (node = nodes[i]) && node.$();
    (node = getNode(nodes, "length", len)) && node.$(state.length);
  }
  (node = nodes[$SELF]) && node.$();
}
function mergeStoreNode(state, value) {
  const keys = Object.keys(value);
  for (let i = 0; i < keys.length; i += 1) {
    const key = keys[i];
    setProperty(state, key, value[key]);
  }
}
function updateArray(current, next) {
  if (typeof next === "function") next = next(current);
  next = unwrap(next);
  if (Array.isArray(next)) {
    if (current === next) return;
    let i = 0,
      len = next.length;
    for (; i < len; i++) {
      const value = next[i];
      if (current[i] !== value) setProperty(current, i, value);
    }
    setProperty(current, "length", len);
  } else mergeStoreNode(current, next);
}
function updatePath(current, path, traversed = []) {
  let part,
    prev = current;
  if (path.length > 1) {
    part = path.shift();
    const partType = typeof part,
      isArray = Array.isArray(current);
    if (Array.isArray(part)) {
      for (let i = 0; i < part.length; i++) {
        updatePath(current, [part[i]].concat(path), traversed);
      }
      return;
    } else if (isArray && partType === "function") {
      for (let i = 0; i < current.length; i++) {
        if (part(current[i], i)) updatePath(current, [i].concat(path), traversed);
      }
      return;
    } else if (isArray && partType === "object") {
      const { from = 0, to = current.length - 1, by = 1 } = part;
      for (let i = from; i <= to; i += by) {
        updatePath(current, [i].concat(path), traversed);
      }
      return;
    } else if (path.length > 1) {
      updatePath(current[part], path, [part].concat(traversed));
      return;
    }
    prev = current[part];
    traversed = [part].concat(traversed);
  }
  let value = path[0];
  if (typeof value === "function") {
    value = value(prev, traversed);
    if (value === prev) return;
  }
  if (part === undefined && value == undefined) return;
  value = unwrap(value);
  if (part === undefined || (isWrappable(prev) && isWrappable(value) && !Array.isArray(value))) {
    mergeStoreNode(prev, value);
  } else setProperty(current, part, value);
}
function createStore(...[store, options]) {
  const unwrappedStore = unwrap(store || {});
  const isArray = Array.isArray(unwrappedStore);
  const wrappedStore = wrap$1(unwrappedStore);
  function setStore(...args) {
    batch(() => {
      isArray && args.length === 1
        ? updateArray(unwrappedStore, args[0])
        : updatePath(unwrappedStore, args);
    });
  }
  return [wrappedStore, setStore];
}

const $ROOT = Symbol("store-root");
function applyState(target, parent, property, merge, key) {
  const previous = parent[property];
  if (target === previous) return;
  const isArray = Array.isArray(target);
  if (
    property !== $ROOT &&
    (!isWrappable(target) ||
      !isWrappable(previous) ||
      isArray !== Array.isArray(previous) ||
      (key && target[key] !== previous[key]))
  ) {
    setProperty(parent, property, target);
    return;
  }
  if (isArray) {
    if (
      target.length &&
      previous.length &&
      (!merge || (key && target[0] && target[0][key] != null))
    ) {
      let i, j, start, end, newEnd, item, newIndicesNext, keyVal;
      for (
        start = 0, end = Math.min(previous.length, target.length);
        start < end &&
        (previous[start] === target[start] ||
          (key && previous[start] && target[start] && previous[start][key] === target[start][key]));
        start++
      ) {
        applyState(target[start], previous, start, merge, key);
      }
      const temp = new Array(target.length),
        newIndices = new Map();
      for (
        end = previous.length - 1, newEnd = target.length - 1;
        end >= start &&
        newEnd >= start &&
        (previous[end] === target[newEnd] ||
          (key && previous[start] && target[start] && previous[end][key] === target[newEnd][key]));
        end--, newEnd--
      ) {
        temp[newEnd] = previous[end];
      }
      if (start > newEnd || start > end) {
        for (j = start; j <= newEnd; j++) setProperty(previous, j, target[j]);
        for (; j < target.length; j++) {
          setProperty(previous, j, temp[j]);
          applyState(target[j], previous, j, merge, key);
        }
        if (previous.length > target.length) setProperty(previous, "length", target.length);
        return;
      }
      newIndicesNext = new Array(newEnd + 1);
      for (j = newEnd; j >= start; j--) {
        item = target[j];
        keyVal = key && item ? item[key] : item;
        i = newIndices.get(keyVal);
        newIndicesNext[j] = i === undefined ? -1 : i;
        newIndices.set(keyVal, j);
      }
      for (i = start; i <= end; i++) {
        item = previous[i];
        keyVal = key && item ? item[key] : item;
        j = newIndices.get(keyVal);
        if (j !== undefined && j !== -1) {
          temp[j] = previous[i];
          j = newIndicesNext[j];
          newIndices.set(keyVal, j);
        }
      }
      for (j = start; j < target.length; j++) {
        if (j in temp) {
          setProperty(previous, j, temp[j]);
          applyState(target[j], previous, j, merge, key);
        } else setProperty(previous, j, target[j]);
      }
    } else {
      for (let i = 0, len = target.length; i < len; i++) {
        applyState(target[i], previous, i, merge, key);
      }
    }
    if (previous.length > target.length) setProperty(previous, "length", target.length);
    return;
  }
  const targetKeys = Object.keys(target);
  for (let i = 0, len = targetKeys.length; i < len; i++) {
    applyState(target[targetKeys[i]], previous, targetKeys[i], merge, key);
  }
  const previousKeys = Object.keys(previous);
  for (let i = 0, len = previousKeys.length; i < len; i++) {
    if (target[previousKeys[i]] === undefined) setProperty(previous, previousKeys[i], undefined);
  }
}
function reconcile(value, options = {}) {
  const { merge, key = "id" } = options,
    v = unwrap(value);
  return state => {
    if (!isWrappable(state) || !isWrappable(v)) return v;
    const res = applyState(
      v,
      {
        [$ROOT]: state
      },
      $ROOT,
      merge,
      key
    );
    return res === undefined ? state : res;
  };
}

function createGlobalStates$8() {
  const [remoteModules, setRemoteModules] = createStore({
    __initial: true
  });
  const [remoteModuleLogos, setRemoteModuleLogos] = createSignal({});
  const [remoteTags, setRemoteTags] = createSignal({});
  const {
    serverUrl
  } = gvServer;
  let remoteBeingQueried = false;
  createEffect(function() {
    if (remoteModules["__initial"] == true) {
      setRemoteModules(reconcile({}));
      loadAllRemoteModules("false");
    }
  });
  function getRemoteModule(moduleName) {
    if (moduleName in remoteModules) {
      return remoteModules[moduleName];
    } else {
      return null;
    }
  }
  function addRemoteModule(module) {
    var d = remoteModules;
    d[module.name] = module;
  }
  function loadAllRemoteModules(refresh) {
    if (remoteBeingQueried) {
      return;
    }
    remoteBeingQueried = true;
    setRemoteModules(reconcile({}));
    axios.get(serverUrl + "/store/remote?refresh=" + refresh).then(function(res) {
      let rms = res.data.data;
      let tagdesc = res.data.tagdesc;
      delete rms["aggregator"];
      const tags = {};
      const converterTag = "input coversion";
      const reporterTag = "reporting";
      for (const mn in rms) {
        const m = rms[mn];
        if (m.tags && m.tags.length > 0) {
          for (const tag of m.tags) {
            if (tag == "reporters") {
              continue;
            }
            if (tag == "input/output") {
              continue;
            }
            tags[tag] = tagdesc[tag] || tag;
          }
        } else {
          m.tags = [];
        }
        if (m.type == "converter") {
          tags[converterTag] = "Input format conversion modules";
          m.tags.push(converterTag);
        } else if (m.type == "reporter") {
          tags[reporterTag] = "Report generation modules";
          m.tags.push(reporterTag);
        }
      }
      tags["no tag"] = "No tag provided";
      setRemoteTags(tags);
      setRemoteModules(rms);
      remoteBeingQueried = false;
    }).catch(function(err) {
      console.error(err);
    });
  }
  function getFilteredRemoteModules(searchText, selectedTypes, selectedTag, sort) {
    var text = searchText;
    if (text != null) {
      text = text.toLowerCase();
    }
    let moduleNames = [];
    for (const [moduleName, module] of Object.entries(remoteModules)) {
      let add = true;
      if (selectedTypes.length > 0) {
        if (!(module.type in selectedTypes)) {
          add = false;
        }
      }
      if (selectedTag != null) {
        if (selectedTag == "no tag") {
          if (module.tags.length > 0) {
            add = false;
          }
        } else if (module.tags.indexOf(selectedTag) == -1) {
          add = false;
        }
      }
      if (add && text != null) {
        add = false;
        if (moduleName.toLowerCase().indexOf(text) >= 0) {
          add = true;
        } else if (module.title.toLowerCase().indexOf(text) >= 0) {
          add = true;
        } else if (module.description && module.description.toLowerCase().indexOf(searchText) >= 0) {
          add = true;
        }
      }
      if (moduleName == "casecontrol" || moduleName == "cravat-converter" || moduleName == "oldcravat-converter" || moduleName.endsWith("package")) {
        add = false;
      }
      if (add) {
        moduleNames.push(moduleName);
      }
    }
    if (sort == void 0 || sort == "Name") {
      moduleNames.sort();
    } else if (sort == "Size") {
      moduleNames.sort((a, b) => remoteModules[b].size - remoteModules[a].size);
    }
    return moduleNames;
  }
  return {
    remoteModules,
    setRemoteModules,
    getRemoteModule,
    addRemoteModule,
    loadAllRemoteModules,
    remoteModuleLogos,
    setRemoteModuleLogos,
    getFilteredRemoteModules,
    remoteTags
  };
}
const gvRemoteModules = createRoot(createGlobalStates$8);

function BsArrowLeft(props) {
      return IconTemplate({
        a: {"fill":"currentColor","viewBox":"0 0 16 16"},
        c: '<path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>'
      }, props)
  }
  function BsBoxFill(props) {
      return IconTemplate({
        a: {"fill":"currentColor","viewBox":"0 0 16 16"},
        c: '<path fill-rule="evenodd" d="M15.528 2.973a.75.75 0 0 1 .472.696v8.662a.75.75 0 0 1-.472.696l-7.25 2.9a.75.75 0 0 1-.557 0l-7.25-2.9A.75.75 0 0 1 0 12.331V3.669a.75.75 0 0 1 .471-.696L7.443.184l.004-.001.274-.11a.75.75 0 0 1 .558 0l.274.11.004.001 6.971 2.789Zm-1.374.527L8 5.962 1.846 3.5 1 3.839v.4l6.5 2.6v7.922l.5.2.5-.2V6.84l6.5-2.6v-.4l-.846-.339Z"/>'
      }, props)
  }
  function BsBox(props) {
      return IconTemplate({
        a: {"fill":"currentColor","viewBox":"0 0 16 16"},
        c: '<path d="M8.186 1.113a.5.5 0 0 0-.372 0L1.846 3.5 8 5.961 14.154 3.5 8.186 1.113zM15 4.239l-6.5 2.6v7.922l6.5-2.6V4.24zM7.5 14.762V6.838L1 4.239v7.923l6.5 2.6zM7.443.184a1.5 1.5 0 0 1 1.114 0l7.129 2.852A.5.5 0 0 1 16 3.5v8.662a1 1 0 0 1-.629.928l-7.185 2.874a.5.5 0 0 1-.372 0L.63 13.09a1 1 0 0 1-.63-.928V3.5a.5.5 0 0 1 .314-.464L7.443.184z"/>'
      }, props)
  }
  function BsDiscord(props) {
      return IconTemplate({
        a: {"fill":"currentColor","viewBox":"0 0 16 16"},
        c: '<path d="M13.545 2.907a13.227 13.227 0 0 0-3.257-1.011.05.05 0 0 0-.052.025c-.141.25-.297.577-.406.833a12.19 12.19 0 0 0-3.658 0 8.258 8.258 0 0 0-.412-.833.051.051 0 0 0-.052-.025c-1.125.194-2.22.534-3.257 1.011a.041.041 0 0 0-.021.018C.356 6.024-.213 9.047.066 12.032c.001.014.01.028.021.037a13.276 13.276 0 0 0 3.995 2.02.05.05 0 0 0 .056-.019c.308-.42.582-.863.818-1.329a.05.05 0 0 0-.01-.059.051.051 0 0 0-.018-.011 8.875 8.875 0 0 1-1.248-.595.05.05 0 0 1-.02-.066.051.051 0 0 1 .015-.019c.084-.063.168-.129.248-.195a.05.05 0 0 1 .051-.007c2.619 1.196 5.454 1.196 8.041 0a.052.052 0 0 1 .053.007c.08.066.164.132.248.195a.051.051 0 0 1-.004.085 8.254 8.254 0 0 1-1.249.594.05.05 0 0 0-.03.03.052.052 0 0 0 .003.041c.24.465.515.909.817 1.329a.05.05 0 0 0 .056.019 13.235 13.235 0 0 0 4.001-2.02.049.049 0 0 0 .021-.037c.334-3.451-.559-6.449-2.366-9.106a.034.034 0 0 0-.02-.019Zm-8.198 7.307c-.789 0-1.438-.724-1.438-1.612 0-.889.637-1.613 1.438-1.613.807 0 1.45.73 1.438 1.613 0 .888-.637 1.612-1.438 1.612Zm5.316 0c-.788 0-1.438-.724-1.438-1.612 0-.889.637-1.613 1.438-1.613.807 0 1.451.73 1.438 1.613 0 .888-.631 1.612-1.438 1.612Z"/>'
      }, props)
  }
  function BsNut(props) {
      return IconTemplate({
        a: {"fill":"currentColor","viewBox":"0 0 16 16"},
        c: '<path d="m11.42 2 3.428 6-3.428 6H4.58L1.152 8 4.58 2h6.84zM4.58 1a1 1 0 0 0-.868.504l-3.428 6a1 1 0 0 0 0 .992l3.428 6A1 1 0 0 0 4.58 15h6.84a1 1 0 0 0 .868-.504l3.429-6a1 1 0 0 0 0-.992l-3.429-6A1 1 0 0 0 11.42 1H4.58z"/><path d="M6.848 5.933a2.5 2.5 0 1 0 2.5 4.33 2.5 2.5 0 0 0-2.5-4.33zm-1.78 3.915a3.5 3.5 0 1 1 6.061-3.5 3.5 3.5 0 0 1-6.062 3.5z"/>'
      }, props)
  }

async function fetchJson(url) {
  const {
    serverUrl
  } = gvServer;
  const res = await fetch(serverUrl + url).catch(function(err) {
    handleError(err);
  });
  if (res == void 0) {
    return {};
  } else {
    return res.json();
  }
}

const MODULE_OPTION_FILE_PREFIX = "module_option_file__";
function createGlobalStates$7() {
  const [localModules, setLocalModules] = createStore({
    "__initial": true
  });
  const [localModuleLogos, setLocalModuleLogos] = createSignal({});
  const {
    serverUrl
  } = gvServer;
  createEffect(function() {
    if (localModules["__initial"] == true) {
      setLocalModules(reconcile({}));
      loadAllLocalModules("false");
    }
  });
  function getLocalModule(moduleName) {
    if (moduleName in localModules) {
      return localModules[moduleName];
    } else {
      return null;
    }
  }
  function addLocalModule(module) {
    var d = {
      ...localModules
    };
    d[module.name] = module;
    setLocalModules(d);
  }
  function loadAllLocalModules(refresh) {
    setLocalModules(reconcile({}));
    axios.get(serverUrl + "/store/local?refresh=" + refresh).then(function(res) {
      setLocalModules(reconcile(res.data));
    }).catch(function(err) {
      handleError(err);
    });
  }
  function loadOneLocalModule(moduleName) {
    const params = new URLSearchParams({
      moduleName
    });
    fetchJson(serverUrl + "/store/addlocal?" + params).then(function(res) {
      addLocalModule(res);
    }).catch(function(err) {
      console.log(err);
    });
  }
  function getLocalModuleLogo(moduleName) {
    if (moduleName in localModuleLogos()) {
      return localModuleLogos()[moduleName];
    } else {
      return createComponent(BsNut, {});
    }
  }
  function setModuleOption(moduleName, option, value) {
    const d = localModules;
    const moduleInfo = d[moduleName];
    let module_options = moduleInfo.module_options;
    if (module_options == void 0) {
      setLocalModules(moduleName, "module_options", {});
    }
    if (option.type == "int") {
      value = parseInt(value);
    } else if (option.type == "float") {
      value = parseFloat(value);
    }
    const vd = {
      value,
      method: option.method,
      type: option.type
    };
    setLocalModules(moduleName, "module_options", option.name, vd);
  }
  function getModuleOptions(modules, formData) {
    let moduleOptions = {};
    for (const moduleName in modules) {
      const m = modules[moduleName];
      if (m.module_options) {
        moduleOptions[moduleName] = {};
        for (const optionName in m.module_options) {
          const d = m.module_options[optionName];
          if (d.method == "file") {
            const key = MODULE_OPTION_FILE_PREFIX + moduleName + "__" + optionName;
            formData.append(key, d.value);
          } else {
            moduleOptions[moduleName][optionName] = d.value;
          }
        }
        if (Object.keys(moduleOptions[moduleName]).length == 0) {
          delete moduleOptions[moduleName];
        }
      }
    }
    return moduleOptions;
  }
  function getModuleOption(moduleName, optionName) {
    const m = localModules[moduleName];
    if (m && m.module_options) {
      const v = m.module_options[optionName];
      if (v) {
        return v;
      } else {
        return null;
      }
    } else {
      return null;
    }
  }
  return {
    localModules,
    setLocalModules,
    getLocalModule,
    addLocalModule,
    loadAllLocalModules,
    localModuleLogos,
    setLocalModuleLogos,
    getLocalModuleLogo,
    setModuleOption,
    getModuleOptions,
    getModuleOption,
    loadOneLocalModule
  };
}
const gvLocalModules = createRoot(createGlobalStates$7);

const {
  serverUrl: serverUrl$4,
  withCredentials: withCredentials$2
} = gvServer;
const {
  getRemoteModule
} = gvRemoteModules;
function createGlobalStates$6() {
  const [installQueue, setInstallQueue] = createStore([]);
  const [installState, setInstallState] = createStore({});
  const {
    loadAllLocalModules
  } = gvLocalModules;
  fetchInstallQueue();
  fetchInstallState();
  function fetchInstallQueue() {
    const {
      serverUrl: serverUrl2
    } = gvServer;
    axios.get(serverUrl2 + "/store/getqueue").then(function(res) {
      setInstallQueue(reconcile(res.data));
      let d = {
        ...installState
      };
      for (const moduleName of installQueue) {
        if (!(moduleName in d)) {
          removeFromInstallState(moduleName);
        }
      }
    }).catch(function(err) {
      handleError(err);
    });
  }
  function fetchInstallState() {
    const {
      serverUrl: serverUrl2
    } = gvServer;
    axios.get(serverUrl2 + "/store/getinstallstate").then(function(res) {
      let d = {
        ...res.data
      };
      for (const moduleName in d) {
        let mObj = d[moduleName];
        if (moduleName in installState) {
          mObj.progress = installState[moduleName].progress;
        }
      }
      setInstallState(reconcile(d));
    }).catch(function(err) {
      handleError(err);
    });
  }
  function lastOfInstallQueue() {
    if (installQueue.length == 0) {
      return null;
    } else {
      return installQueue[installQueue.length - 1];
    }
  }
  function sendInstallJob(moduleName) {
    if (moduleName == null) {
      return;
    }
    if (moduleName in installState) {
      return;
    }
    const moduleInfo = getRemoteModule(moduleName);
    if (moduleInfo == null) {
      return;
    }
    axios.get(serverUrl$4 + "/store/queueinstall", {
      params: {
        module: moduleName,
        version: moduleInfo.latest_version
      },
      withCredentials: withCredentials$2
    }).then(function(_) {
      fetchInstallQueue();
      fetchInstallState();
    }).catch(function(err) {
      handleError(err);
    });
  }
  function addToInstallQueue(moduleName) {
    if (lastOfInstallQueue() != moduleName) {
      sendInstallJob(moduleName);
    }
  }
  function removeFromInstallState(moduleName) {
    let d = {
      ...installState
    };
    delete d[moduleName];
    setInstallState(reconcile(d));
  }
  function removeFromInstallQueue(moduleName) {
    axios.get(serverUrl$4 + "/store/unqueue", {
      params: {
        module_name: moduleName
      },
      withCredentials: withCredentials$2
    }).then(function(_) {
      fetchInstallQueue();
      fetchInstallState();
    }).catch(function(err) {
      handleError(err);
    });
  }
  function inQueue(moduleName) {
    if (installQueue.length == 0) {
      return false;
    } else {
      return installQueue.indexOf(moduleName) >= 0;
    }
  }
  function uninstallModule(moduleName) {
    axios.get(serverUrl$4 + "/store/uninstall", {
      params: {
        moduleName
      },
      withCredentials: withCredentials$2
    }).then(function(_) {
      loadAllLocalModules();
    }).catch(function(err) {
      handleError(err);
      fetchInstallQueue();
    });
  }
  function undividable(cur, total) {
    return cur == 0 && total == 0 || isNaN(cur) || isNaN(total);
  }
  function getInstallProgress(stage, cur_size, total_size) {
    const cur = parseFloat(cur_size);
    const total = parseFloat(total_size);
    if (stage == "start") {
      return 5;
    } else if (stage == "killed" || stage == "error" || stage == "skip" || stage == "finished" || stage == "finish") {
      return 100;
    } else if (stage == "extract_code") {
      return 10;
    } else if (stage == "extract_data") {
      return 90;
    } else if (stage == "download_code") {
      if (undividable(cur, total)) {
        return void 0;
      }
      return cur / total * 5 + 5;
    } else if (stage == "download_data") {
      if (undividable(cur, total)) {
        return void 0;
      }
      return cur / total * 75 + 15;
    }
  }
  return {
    installQueue,
    addToInstallQueue,
    removeFromInstallQueue,
    removeFromInstallState,
    inQueue,
    uninstallModule,
    installState,
    setInstallState,
    getInstallProgress,
    fetchInstallQueue
  };
}
const gvInstallQueue = createRoot(createGlobalStates$6);

function createGlobalStates$5() {
  const [systemMsg, setSystemMsg] = createSignal(null);
  return {
    systemMsg,
    setSystemMsg
  };
}
const gvSystemMessage = createRoot(createGlobalStates$5);

const SYSTEM_STATE_CONNECTION_KEY = "connection";
const SYSTEM_STATE_SETUP_KEY = "setup";
const SYSTEM_STATE_SETUP_ERROR_KEY = "setup_error";
const SYSTEM_STATE_INSTALL_KEY = "install";
const SYSTEM_STATE_INSTALL_ERROR_KEY = "install_error";
function createGlobalStates$4() {
  const [ws, setWs] = createSignal(null);
  const [wsOpened, setWsOpened] = createSignal(false);
  const {
    fetchInstallQueue,
    installState,
    setInstallState,
    removeFromInstallState,
    getInstallProgress
  } = gvInstallQueue;
  const {
    wsUrl
  } = gvServer;
  const {
    setSystemMsg
  } = gvSystemMessage;
  const [setupStateMsg, setSetupStateMsg] = createSignal("");
  const [callbackAfterSetup, setCallbackAfterSetup] = createSignal(null);
  const [setupFinished, setSetupFinished] = createSignal(false);
  const {
    loadAllLocalModules
  } = gvLocalModules;
  let reconnectCount = 0;
  const maxReconnectCount = 10;
  createEffect(function() {
    if (ws() == null) {
      setTimeout(function() {
        setWs(createWebSocket());
      });
    }
    if (setupFinished() == true) {
      if (callbackAfterSetup) {
        callbackAfterSetup();
      }
    }
  });
  function getSetupStageMsg() {
    return setupStateMsg();
  }
  function createWebSocket() {
    const ws2 = new WebSocket(wsUrl);
    ws2.onopen = function(_) {
      setWsOpened(true);
    };
    ws2.onclose = function(_) {
      reconnectCount += 1;
      if (reconnectCount >= maxReconnectCount) {
        const err = {};
        err.response = void 0;
        handleError(err);
      } else {
        setWsOpened(false);
        setTimeout(function() {
          setWs(null);
        }, 3e3);
      }
    };
    ws2.onmessage = function(evt) {
      const data = JSON.parse(evt.data);
      processWsData(data);
    };
    ws2.onerror = function(err) {
      handleError(err);
    };
    return ws2;
  }
  function processSetupLine(line) {
    if (line == "Logging in...") {
      setSetupStateMsg("Logging in...");
    } else if (line == "Setting up store cache...") {
      setSetupStateMsg("Setting up store cache...");
    } else if (line == "Setting up administrative database...") {
      setSetupStateMsg("Setting up administrative database...");
    } else if (line == "Installing system modules...") {
      setSetupStateMsg("Installing system modules...");
    } else if (line.startsWith("Installing")) {
      setSetupStateMsg(line);
    } else if (line.startsWith("Installed") || line.includes("already exists")) {
      setSetupStateMsg(line);
    } else if (line == "Done setting up the system.") {
      setSetupStateMsg("Done setting up the system.");
      setSetupFinished(true);
    }
  }
  function processSetupItem(item) {
    let l = [];
    const lines = item.msg.split("\n");
    for (const line of lines) {
      l.push({
        kind: item.kind,
        msg: line,
        dt: item.dt
      });
      processSetupLine(line);
    }
    setSystemMsg(l);
  }
  function processSetupErrorItem(item) {
    const err = JSON.parse(item.msg);
    handleError(err);
    setSystemMsg([{
      msg: err.response.data.msg,
      dt: item.dt
    }]);
  }
  function processSetupItems(items) {
    for (const item of items) {
      if (item.kind == SYSTEM_STATE_SETUP_ERROR_KEY) {
        processSetupErrorItem(item);
      } else {
        processSetupItem(item);
      }
    }
  }
  function processInstallItem(item) {
    const msg = item.msg;
    const words = msg.split(":");
    const stage = words[0];
    const moduleName = words[1];
    const cur_size = parseInt(words[2]);
    const total_size = parseInt(words[3]);
    const progress = getInstallProgress(stage, cur_size, total_size);
    if (moduleName in installState) {
      setInstallState(moduleName, "stage", stage);
      if (progress != void 0) {
        setInstallState(moduleName, "progress", progress);
      }
    }
    if (stage == "error") {
      const err = {
        response: {
          status: 500,
          data: {
            msg
          }
        }
      };
      handleError(err);
    } else if (stage == "killed" || stage == "finished" || stage == "error" || stage == "skip") {
      fetchInstallQueue();
      removeFromInstallState(moduleName);
      if (stage == "finished") {
        loadAllLocalModules();
      }
    }
  }
  function processInstallItems(items) {
    for (const item of items) {
      if (item.kind == SYSTEM_STATE_INSTALL_KEY) {
        processInstallItem(item);
      } else if (item.kind == SYSTEM_STATE_INSTALL_ERROR_KEY) ;
    }
  }
  function processWsData(data) {
    const msgKind = data.msg_kind;
    if (msgKind == SYSTEM_STATE_CONNECTION_KEY) {
      document.cookie = "ws_id=" + data.ws_id;
    } else if (msgKind == SYSTEM_STATE_SETUP_KEY) {
      processSetupItems(data.items);
    } else if (msgKind == SYSTEM_STATE_INSTALL_KEY) {
      processInstallItems(data.items);
    } else ;
  }
  return {
    wsOpened,
    getSetupStageMsg,
    setCallbackAfterSetup,
    setSetupStateMsg
  };
}
const gvWebSocket = createRoot(createGlobalStates$4);

function NoServerConnectionPanel() {
  const {
    wsOpened
  } = gvWebSocket;
  return createComponent(Show, {
    get classList() {
      return {
        "hidden": wsOpened() == true
      };
    },
    get children() {
      return createComponent(TbServerOff, {
        color: "#dc2626",
        size: 48
      });
    }
  });
}

var _tmpl$$1i = /* @__PURE__ */ template(`<div id=sidebar_static class="md:flex md:w-36 md:flex-col md:fixed md:inset-y-0"><div class="flex-1 flex flex-col min-h-0 border-r border-gray-200"><div class="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto"><div class="flex items-center flex-shrink-0 px-4"><img class="h-16 w-auto"alt=Logo></div><nav class="mt-5 flex-1 px-2 space-y-1">`);
function SideBar() {
  const {
    serverUrl
  } = gvServer;
  const {
    logged
  } = gvLogin;
  const {
    multiuser
  } = gvMultiuser;
  const {
    admin
  } = gvLogin;
  return (() => {
    var _el$ = _tmpl$$1i(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$4.nextSibling;
    setAttribute(_el$5, "src", serverUrl + "/submit/images/logo_transparent_bw.png");
    insert(_el$6, createComponent(TabHeadHome, {}), null);
    insert(_el$6, createComponent(TabHeadSubmit, {}), null);
    insert(_el$6, createComponent(TabHeadJobs, {}), null);
    insert(_el$6, createComponent(TabHeadStore, {}), null);
    insert(_el$6, createComponent(Show, {
      get when() {
        return multiuser() == false || logged() == true && admin() == true;
      },
      get children() {
        return createComponent(TabHeadSystem, {});
      }
    }), null);
    insert(_el$3, createComponent(TabHeadLogging, {}), null);
    insert(_el$3, createComponent(VersionSlot, {}), null);
    insert(_el$3, createComponent(NoServerConnectionPanel, {}), null);
    return _el$;
  })();
}

var _tmpl$$1h = /* @__PURE__ */ template(`<a target=_blank><button class="relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-cyan-500 to-blue-500 group-hover:from-cyan-500 group-hover:to-blue-500 hover:text-white dark:text-white focus:ring-4 focus:outline-none focus:ring-cyan-200 dark:focus:ring-cyan-800"><span class="relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-opacity-0">`);
function LinkButton(props) {
  return (() => {
    var _el$ = _tmpl$$1h(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild;
    insert(_el$3, () => props.icon, null);
    insert(_el$3, () => props.text, null);
    createRenderEffect(() => setAttribute(_el$, "href", props.url));
    return _el$;
  })();
}

function FaBrandsGithub(props) {
      return IconTemplate({
        a: {"viewBox":"0 0 496 512"},
        c: '<path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"/>'
      }, props)
  }

function FiBookOpen(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2","viewBox":"0 0 24 24"},
        c: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>'
      }, props)
  }
  function FiMinusCircle(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2","viewBox":"0 0 24 24"},
        c: '<path d="M12 2A10 10 0 1 0 12 22 10 10 0 1 0 12 2z"/><path d="M8 12 16 12"/>'
      }, props)
  }
  function FiPlusCircle(props) {
      return IconTemplate({
        a: {"fill":"none","stroke":"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2","viewBox":"0 0 24 24"},
        c: '<path d="M12 2A10 10 0 1 0 12 22 10 10 0 1 0 12 2z"/><path d="M12 8 12 16"/><path d="M8 12 16 12"/>'
      }, props)
  }

function IoLogoMedium(props) {
      return IconTemplate({
        a: {"xml:space":"preserve","x":"0","y":"0","enable-background":"new 0 0 512 512","viewBox":"0 0 512 512"},
        c: '<path id="icons" d="M28 28v456h456V28H28zm378.83 108.04-24.46 23.45a7.162 7.162 0 0 0-2.72 6.86v172.28c-.44 2.61.61 5.26 2.72 6.86l23.88 23.45v5.15H286.13v-5.15l24.74-24.02c2.43-2.43 2.43-3.15 2.43-6.86V198.81l-68.79 174.71h-9.3l-80.09-174.71v117.1c-.67 4.92.97 9.88 4.43 13.44l32.18 39.03v5.15h-91.24v-5.15l32.18-39.03c3.44-3.57 4.98-8.56 4.15-13.44V180.5c.38-3.76-1.05-7.48-3.86-10.01l-28.6-34.46v-5.15h88.81l68.65 150.55 60.35-150.55h84.66v5.16z"/>'
      }, props)
  }
  function IoLogoReddit(props) {
      return IconTemplate({
        a: {"viewBox":"0 0 512 512"},
        c: '<path d="M324 256a36 36 0 1 0 36 36 36 36 0 0 0-36-36Z"/><path d="M188 256A36 36 0 1 0 188 328 36 36 0 1 0 188 256z" transform="rotate(-22.5 187.997 291.992)"/><path d="M496 253.77c0-31.19-25.14-56.56-56-56.56a55.72 55.72 0 0 0-35.61 12.86c-35-23.77-80.78-38.32-129.65-41.27l22-79 66.41 13.2c1.9 26.48 24 47.49 50.65 47.49 28 0 50.78-23 50.78-51.21S441 48 413 48c-19.53 0-36.31 11.19-44.85 28.77l-90-17.89-31.1 109.52-4.63.13c-50.63 2.21-98.34 16.93-134.77 41.53A55.38 55.38 0 0 0 72 197.21c-30.89 0-56 25.37-56 56.56a56.43 56.43 0 0 0 28.11 49.06 98.65 98.65 0 0 0-.89 13.34c.11 39.74 22.49 77 63 105C146.36 448.77 199.51 464 256 464s109.76-15.23 149.83-42.89c40.53-28 62.85-65.27 62.85-105.06a109.32 109.32 0 0 0-.84-13.3A56.32 56.32 0 0 0 496 253.77ZM414 75a24 24 0 1 1-24 24 24 24 0 0 1 24-24ZM42.72 253.77a29.6 29.6 0 0 1 29.42-29.71 29 29 0 0 1 13.62 3.43c-15.5 14.41-26.93 30.41-34.07 47.68a30.23 30.23 0 0 1-8.97-21.4ZM390.82 399c-35.74 24.59-83.6 38.14-134.77 38.14S157 423.61 121.29 399c-33-22.79-51.24-52.26-51.24-83A78.5 78.5 0 0 1 75 288.72c5.68-15.74 16.16-30.48 31.15-43.79a155.17 155.17 0 0 1 14.76-11.53l.3-.21.24-.17c35.72-24.52 83.52-38 134.61-38s98.9 13.51 134.62 38l.23.17.34.25A156.57 156.57 0 0 1 406 244.92c15 13.32 25.48 28.05 31.16 43.81a85.44 85.44 0 0 1 4.31 17.67 77.29 77.29 0 0 1 .6 9.65c-.01 30.72-18.21 60.19-51.25 82.95Zm69.6-123.92c-7.13-17.28-18.56-33.29-34.07-47.72A29.09 29.09 0 0 1 440 224a29.59 29.59 0 0 1 29.41 29.71 30.07 30.07 0 0 1-8.99 21.39Z"/><path d="M323.23 362.22c-.25.25-25.56 26.07-67.15 26.27-42-.2-66.28-25.23-67.31-26.27a4.14 4.14 0 0 0-5.83 0l-13.7 13.47a4.15 4.15 0 0 0 0 5.89c3.4 3.4 34.7 34.23 86.78 34.45 51.94-.22 83.38-31.05 86.78-34.45a4.16 4.16 0 0 0 0-5.9l-13.71-13.47a4.13 4.13 0 0 0-5.81 0Z"/>'
      }, props)
  }
  function IoMailOutline(props) {
      return IconTemplate({
        a: {"viewBox":"0 0 512 512"},
        c: '<rect width="416" height="320" x="48" y="96" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32" rx="40" ry="40"/><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32" d="M112 160 256 272 400 160"/>'
      }, props)
  }
  function IoWarningOutline(props) {
      return IconTemplate({
        a: {"viewBox":"0 0 512 512"},
        c: '<path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32" d="M85.57 446.25h340.86a32 32 0 0 0 28.17-47.17L284.18 82.58c-12.09-22.44-44.27-22.44-56.36 0L57.4 399.08a32 32 0 0 0 28.17 47.17Z"/><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32" d="m250.26 195.39 5.74 122 5.73-121.95a5.74 5.74 0 0 0-5.79-6h0a5.74 5.74 0 0 0-5.68 5.95Z"/><path d="M256 397.25a20 20 0 1 1 20-20 20 20 0 0 1-20 20Z"/>'
      }, props)
  }

var _tmpl$$1g = /* @__PURE__ */ template(`<span class=font-semibold>`), _tmpl$2$f = /* @__PURE__ */ template(`<div id=tab_home class="tabcontent px-6 my-6 text-gray-700"><h1 class="text-4xl font-extrabold dark:text-white">OakVar</h1><p class="mb-6 text-lg font-normal text-gray-500 lg:text-xl dark:text-gray-400">Genomic variant analysis platform</p><div class="mt-4 text-base w-[64rem]"><p>OakVar is a platform for analyzing and exploring genomic variants.</p><p class=my-2>Use <!> tab to submit analysis jobs. Use <!> tab to monitor your past and current jobs. <!> shows analysis and reporting modules available through OakVar. In <!> tab, you can perform system admin tasks. </p><div class=my-2><h3 class="mb-2 font-semibold dark:text-white">Benefits:</h3><ul class="space-y-1 list-disc list-inside"><li> genomic variants with diverse annotation sources.</li><li>Make <!> of annotated variants.</li><li>Query annotated variants with <!> sets.</li><li>Make <!> in diverse formats.</li><li> annotated variants with graphical user interface.</li><li>Works via <!> and <!>.</li><li>Easily develop, run, and distribute CLI and GUI <!>. OakVar acts as an operating system for genomics apps.</li><li>Connect genomic data to AI/ML models.</li></ul></div><div><h3 class="mb-2 font-semibold dark:text-white">Resources:</h3></div><div><h3 class="mb-2 font-semibold dark:text-white">Follow us:</h3></div><div><h3 class="mb-2 font-semibold dark:text-white">Help and support:`);
const {
  multiuser: multiuser$3
} = gvMultiuser;
function bold(s) {
  return (() => {
    var _el$ = _tmpl$$1g();
    insert(_el$, s);
    return _el$;
  })();
}
function TabHome() {
  const {
    tabName
  } = gvTabName;
  return (() => {
    var _el$2 = _tmpl$2$f(), _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling, _el$5 = _el$4.nextSibling, _el$6 = _el$5.firstChild, _el$7 = _el$6.nextSibling, _el$8 = _el$7.firstChild, _el$16 = _el$8.nextSibling, _el$9 = _el$16.nextSibling, _el$17 = _el$9.nextSibling, _el$10 = _el$17.nextSibling, _el$18 = _el$10.nextSibling, _el$12 = _el$18.nextSibling, _el$19 = _el$12.nextSibling; _el$19.nextSibling; var _el$20 = _el$7.nextSibling, _el$21 = _el$20.firstChild, _el$22 = _el$21.nextSibling, _el$23 = _el$22.firstChild, _el$24 = _el$23.firstChild, _el$25 = _el$23.nextSibling, _el$26 = _el$25.firstChild, _el$28 = _el$26.nextSibling; _el$28.nextSibling; var _el$29 = _el$25.nextSibling, _el$30 = _el$29.firstChild, _el$32 = _el$30.nextSibling; _el$32.nextSibling; var _el$33 = _el$29.nextSibling, _el$34 = _el$33.firstChild, _el$36 = _el$34.nextSibling; _el$36.nextSibling; var _el$37 = _el$33.nextSibling, _el$38 = _el$37.firstChild, _el$39 = _el$37.nextSibling, _el$40 = _el$39.firstChild, _el$43 = _el$40.nextSibling, _el$41 = _el$43.nextSibling, _el$44 = _el$41.nextSibling; _el$44.nextSibling; var _el$45 = _el$39.nextSibling, _el$46 = _el$45.firstChild, _el$49 = _el$46.nextSibling; _el$49.nextSibling; var _el$50 = _el$20.nextSibling; _el$50.firstChild; var _el$52 = _el$50.nextSibling; _el$52.firstChild; var _el$54 = _el$52.nextSibling; _el$54.firstChild;
    insert(_el$7, () => bold("Submit"), _el$16);
    insert(_el$7, () => bold("Jobs"), _el$17);
    insert(_el$7, () => bold("Store"), _el$18);
    insert(_el$7, () => bold("System"), _el$19);
    insert(_el$7, createComponent(Show, {
      get when() {
        return multiuser$3();
      },
      get children() {
        return ["In ", createMemo(() => bold("Account")), " tab, you can perform account tasks including logging out."];
      }
    }), null);
    insert(_el$23, () => bold("Annotate"), _el$24);
    insert(_el$25, () => bold("databases"), _el$28);
    insert(_el$29, () => bold("filter"), _el$32);
    insert(_el$33, () => bold("reports"), _el$36);
    insert(_el$37, () => bold("Visualize"), _el$38);
    insert(_el$39, () => bold("CLI"), _el$43);
    insert(_el$39, () => bold("GUI"), _el$44);
    insert(_el$45, () => bold("genomics apps"), _el$49);
    insert(_el$50, createComponent(LinkButton, {
      url: "https://docs.oakvar.com/",
      get icon() {
        return createComponent(FiBookOpen, {
          "class": "inline mr-1"
        });
      },
      text: "Documentation"
    }), null);
    insert(_el$50, createComponent(LinkButton, {
      url: "https://github.com/rkimoakbioinformatics/oakvar",
      get icon() {
        return createComponent(FaBrandsGithub, {
          "class": "inline mr-1"
        });
      },
      text: "GitHub"
    }), null);
    insert(_el$52, createComponent(LinkButton, {
      url: "https://medium.com/oakvar",
      get icon() {
        return createComponent(IoLogoMedium, {
          "class": "inline mr-1"
        });
      },
      text: "Medium (Announcements)"
    }), null);
    insert(_el$52, createComponent(LinkButton, {
      url: "https://discord.gg/wZfkTMKTjG",
      get icon() {
        return createComponent(BsDiscord, {
          "class": "inline mr-1"
        });
      },
      text: "Discord (Messaging)"
    }), null);
    insert(_el$52, createComponent(LinkButton, {
      url: "https://www.reddit.com/r/oakvar",
      get icon() {
        return createComponent(IoLogoReddit, {
          "class": "inline mr-1"
        });
      },
      text: "Reddit (Discussion)"
    }), null);
    insert(_el$52, createComponent(LinkButton, {
      url: "https://dashboard.mailerlite.com/forms/21170/56038572068701589/share",
      icon: "",
      text: "Join the mailing list"
    }), null);
    insert(_el$54, createComponent(LinkButton, {
      url: "https://github.com/rkimoakbioinformatics/oakvar/issues",
      get icon() {
        return createComponent(FaBrandsGithub, {
          "class": "inline mr-1"
        });
      },
      text: "Issues"
    }), null);
    insert(_el$54, createComponent(LinkButton, {
      url: "mailto:info@oakbioinformatics.com",
      get icon() {
        return createComponent(IoMailOutline, {
          "class": "inline mr-1"
        });
      },
      text: "Mail"
    }), null);
    createRenderEffect(() => _el$2.classList.toggle("hidden", !!(tabName() != "home")));
    return _el$2;
  })();
}

var _tmpl$$1f = /* @__PURE__ */ template(`<a href=# class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900"role=menuitem tabindex=-1 value="">`);
function AssemblySelectPanelOption(props) {
  function changeAssembly() {
    props.setAssembly(props.value);
    props.setShow(false);
  }
  return (() => {
    var _el$ = _tmpl$$1f();
    _el$.$$click = changeAssembly;
    insert(_el$, () => props.title);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$1e = /* @__PURE__ */ template(`<div id=assembly-select class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"role=menu aria-orientation=vertical aria-labelledby=menu-button tabindex=-1><div class=py-1 role=none>`);
function AssemblySelectPanelSelect(props) {
  return (() => {
    var _el$ = _tmpl$$1e(), _el$2 = _el$.firstChild;
    insert(_el$2, createComponent(AssemblySelectPanelOption, {
      value: "auto",
      title: "Auto",
      get setAssembly() {
        return props.setAssembly;
      },
      get setShow() {
        return props.setShow;
      }
    }), null);
    insert(_el$2, createComponent(AssemblySelectPanelOption, {
      value: "hg38",
      title: "GRCh38/hg38",
      get setAssembly() {
        return props.setAssembly;
      },
      get setShow() {
        return props.setShow;
      }
    }), null);
    insert(_el$2, createComponent(AssemblySelectPanelOption, {
      value: "hg19",
      title: "GRCh37/hg19",
      get setAssembly() {
        return props.setAssembly;
      },
      get setShow() {
        return props.setShow;
      }
    }), null);
    insert(_el$2, createComponent(AssemblySelectPanelOption, {
      value: "hg18",
      title: "GRCh36/hg18",
      get setAssembly() {
        return props.setAssembly;
      },
      get setShow() {
        return props.setShow;
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !props.show));
    return _el$;
  })();
}

var _tmpl$$1d = /* @__PURE__ */ template(`<div id=assembly-select-panel class="select-div relative inline-block text-left"value=""><div><button type=button class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100"id=assembly-select-div title="Genome assembly">Genome assembly: `);
function AssemblySelectPanel(props) {
  const [show, setShow] = createSignal(false);
  const assemblies = {
    "": "Auto",
    hg38: "GRCh38/hg38",
    hg19: "GRCh37/hg19",
    hg18: "GRCh36/hg18"
  };
  function toggleShowSelect(_) {
    setShow(!show());
  }
  return (() => {
    var _el$ = _tmpl$$1d(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild; _el$3.firstChild;
    _el$3.$$click = toggleShowSelect;
    insert(_el$3, () => assemblies[props.assembly], null);
    insert(_el$3, createComponent(HiOutlineChevronDown, {
      "class": "-mr-1 ml-2 h-5 w-5"
    }), null);
    insert(_el$, createComponent(AssemblySelectPanelSelect, {
      get show() {
        return show();
      },
      get setAssembly() {
        return props.setAssembly;
      },
      setShow
    }), null);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$1c = /* @__PURE__ */ template(`<a href=# class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900"role=menuitem tabindex=-1 value="">`);
function InputFormatSelectPanelOption(props) {
  function changeInputFormat() {
    props.setInputFormat(props.value);
    props.setShow(false);
  }
  return (() => {
    var _el$ = _tmpl$$1c();
    _el$.$$click = changeInputFormat;
    insert(_el$, () => props.title);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$1b = /* @__PURE__ */ template(`<div id=input-format-select class="option-list ease-in absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"role=menu aria-orientation=vertical aria-labelledby=menu-button tabindex=-1><div class=py-1 role=none>`);
function InputFormatSelectPanelSelect(props) {
  return (() => {
    var _el$ = _tmpl$$1b(), _el$2 = _el$.firstChild;
    insert(_el$2, createComponent(InputFormatSelectPanelOption, {
      value: "",
      title: "Auto",
      get setInputFormat() {
        return props.setInputFormat;
      },
      get setShow() {
        return props.setShow;
      }
    }), null);
    insert(_el$2, createComponent(For, {
      get each() {
        return props.converters;
      },
      children: function(module) {
        return createComponent(InputFormatSelectPanelOption, {
          get value() {
            return module.format;
          },
          get title() {
            return module.title;
          },
          get setInputFormat() {
            return props.setInputFormat;
          },
          get setShow() {
            return props.setShow;
          }
        });
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !props.show));
    return _el$;
  })();
}

var _tmpl$$1a = /* @__PURE__ */ template(`<div id=input-format-select-panel class="select-div relative inline-block text-left ml-6"value=""><div><button type=button class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100"id=input-format-select-div title=Format>Format: `);
const {
  multiuser: multiuser$2
} = gvMultiuser;
const {
  logged: logged$2
} = gvLogin;
const {
  serverUrl: serverUrl$3
} = gvServer;
async function fetchInputFormat() {
  if (multiuser$2() == false || logged$2() == true) {
    try {
      const res = await axios.get(serverUrl$3 + "/submit/converters");
      const cs = await res.data;
      return cs;
    } catch (err) {
      console.error(err);
      if (err.response.responseText == "system_not_ready") ;
    }
  }
}
function InputFormatSelectPanel(props) {
  const [show, setShow] = createSignal(false);
  const [inputFormats, setInputFormats] = createSignal({
    "": "Auto"
  });
  const [converters] = createResource(fetchInputFormat);
  createEffect(() => {
    var ipfs = {
      "": "Auto"
    };
    if (converters() == void 0 || converters() == null) {
      return;
    }
    for (var i = 0; i < converters().length; i++) {
      ipfs[converters()[i].format] = converters()[i].title;
    }
    setInputFormats(ipfs);
  });
  function toggleShow(_) {
    setShow(!show());
  }
  return (() => {
    var _el$ = _tmpl$$1a(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild; _el$3.firstChild;
    _el$3.$$click = toggleShow;
    insert(_el$3, () => inputFormats()[props.inputFormat], null);
    insert(_el$3, createComponent(HiOutlineChevronDown, {
      "class": "-mr-1 ml-2 h-5 w-5"
    }), null);
    insert(_el$, createComponent(InputFormatSelectPanelSelect, {
      get show() {
        return show();
      },
      get converters() {
        return converters();
      },
      get setInputFormat() {
        return props.setInputFormat;
      },
      setInputFormats,
      setShow
    }), null);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$19 = /* @__PURE__ */ template(`<div id=input-upload-list-div class="w-1/2 flex flex-col justify-center items-center p-2 relative h-full bg-gray-50"><button id=clear_inputfilelist_button class="text-gray-500 bg-neutral-200 hover:bg-neutral-300 p-1 w-16 rounded-md absolute top-1 left-1">Clear</button><div id=input-upload-list-wrapper class="flex w-full overflow-auto h-[13rem] absolute bottom-1 bg-gray-50"><div id=input-upload-list class="h-full overflow-auto">`), _tmpl$2$e = /* @__PURE__ */ template(`<label id=input-drop-area for=input-file class="flex items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-md cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600 relative"><div id=input-drop-box class=w-1/2><div class="flex flex-col items-center justify-center pt-5 pb-6"><p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class=font-semibold>Click to upload</span> input files</p><button class="mb-2 text-sm text-gray-500 dark:text-gray-400 bg-neutral-200 hover:bg-neutral-300 p-2 rounded-md absolute top-0 right-0">Manually enter variants instead</button></div><input type=file class=hidden name=input-file id=input-file multiple>`), _tmpl$3$9 = /* @__PURE__ */ template(`<span class="pl-2 text-sm text-gray-600 hover:text-gray-400 cursor-pointer round-md inline-block w-5/6"title="Click to remove">`);
function InputDropArea(props) {
  const {
    setShowErrorDialog,
    setErrorDialogTitle,
    setErrorDialogText
  } = gvErrorDialogState;
  function removeFile(name, evt) {
    evt.preventDefault();
    for (var i = 0; i < props.inputDataDrop.length; i++) {
      if (props.inputDataDrop[i].name == name) {
        props.setInputDataDrop([...props.inputDataDrop.slice(0, i), ...props.inputDataDrop.slice(i + 1, props.inputDataDrop.length)]);
        break;
      }
    }
  }
  function onInputFileChange(evt) {
    const files = evt.target.files;
    for (var i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.name.indexOf(" ") >= 0) {
        setErrorDialogTitle("Problem");
        setErrorDialogText("Input file names should not have space.");
        setShowErrorDialog(true);
        break;
      }
    }
    props.setInputDataDrop([...props.inputDataDrop, ...files]);
    evt.target.value = null;
  }
  function clearInputFiles(evt) {
    evt.preventDefault();
    props.setInputDataDrop([]);
  }
  return (() => {
    var _el$ = _tmpl$2$e(), _el$6 = _el$.firstChild, _el$7 = _el$6.firstChild, _el$8 = _el$7.firstChild, _el$9 = _el$8.nextSibling, _el$10 = _el$7.nextSibling;
    insert(_el$, createComponent(Show, {
      get when() {
        return props.inputDataDrop.length > 0;
      },
      get children() {
        var _el$2 = _tmpl$$19(), _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling, _el$5 = _el$4.firstChild;
        _el$3.$$click = clearInputFiles;
        insert(_el$5, createComponent(For, {
          get each() {
            return props.inputDataDrop;
          },
          children: (file) => (() => {
            var _el$11 = _tmpl$3$9();
            _el$11.$$click = removeFile;
            _el$11.$$clickData = file.name;
            insert(_el$11, () => file.name);
            return _el$11;
          })()
        }));
        return _el$2;
      }
    }), _el$6);
    insert(_el$7, createComponent(AiOutlineCloudUpload, {
      "class": "w-10 h-10",
      color: "#9ca3af"
    }), _el$8);
    _el$9.$$click = props.setInputMode;
    _el$9.$$clickData = "paste";
    _el$10.addEventListener("change", onInputFileChange);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$18 = /* @__PURE__ */ template(`<div id=input-paste-area class="relative w-full h-[20rem] border-2 border-gray-300 border-dashed rounded-md"><textarea id=input-text class="font-mono border-0 bg-gray-50 text-gray-600 p-4 resize-none w-full h-full"placeholder="Copy and paste or type input variants. VCF is supported. A quick and simple format is space-delimited one:

chr1 9384934 + A T

which is chromosome, position, strand, a reference allele, and an alternate allele.

Alternatively, if 'Server files' box is checked, paths to input files in the server can be used as well. For example,

/mnt/oakvar/input/sample/sample_1.vcf
"></textarea><div class="top-2 right-3 absolute cursor-pointer"title="Click to go back"></div><div class="absolute bottom-1 right-1 text-gray-400 text-sm"><button value=cravat class="p-1 text-gray-500 bg-neutral-200 hover:bg-neutral-300">Try an example`);
function InputPasteArea(props) {
  function setInputExample() {
    const {
      serverUrl,
      withCredentials
    } = gvServer;
    props.setAssembly("hg38");
    props.setInputFormat("csv");
    axios({
      method: "get",
      url: `${serverUrl}/submit/inputexamples/exampleinput`,
      withCredentials
    }).then(function(res) {
      let data = res.data;
      props.changeInputData("paste", data);
    });
  }
  function onKeyup(evt) {
    props.changeInputData("paste", evt.target.value);
  }
  return (() => {
    var _el$ = _tmpl$$18(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.nextSibling, _el$5 = _el$4.firstChild;
    _el$2.$$keyup = onKeyup;
    _el$3.$$click = props.setInputMode;
    _el$3.$$clickData = "drop";
    insert(_el$3, createComponent(TbArrowBackUp, {
      "class": "w-5 h-5 mr-2"
    }));
    _el$5.$$click = setInputExample;
    createRenderEffect(() => _el$2.value = props.inputDataPaste);
    return _el$;
  })();
}
delegateEvents(["keyup", "click"]);

var _tmpl$$17 = /* @__PURE__ */ template(`<div id=job-name-div class="mt-4 w-full"><textarea id=job-name class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full "placeholder="(Optional) job name">`);
function JobNameInput(props) {
  function changeJobName(evt) {
    props.setJobName(evt.target.value);
  }
  return (() => {
    var _el$ = _tmpl$$17(), _el$2 = _el$.firstChild;
    _el$2.$$keyup = changeJobName;
    createRenderEffect(() => _el$.classList.toggle("hidden", !props.inputExists));
    createRenderEffect(() => _el$2.value = props.jobName);
    return _el$;
  })();
}
delegateEvents(["keyup"]);

var _tmpl$$16 = /* @__PURE__ */ template(`<div id=submit-note-div class="mt-4 w-full"><textarea id=submit-note class="font-mono text-sm border-0 bg-gray-100 text-gray-600 p-4 resize-none rounded-md w-full"placeholder="(Optional) note for this job">`);
function JobNoteInput(props) {
  function changeJobNote(evt) {
    props.setJobNote(evt.target.value);
  }
  return (() => {
    var _el$ = _tmpl$$16(), _el$2 = _el$.firstChild;
    _el$2.$$keyup = changeJobNote;
    createRenderEffect(() => _el$.classList.toggle("hidden", !props.inputExists));
    createRenderEffect(() => _el$2.value = props.jobNote);
    return _el$;
  })();
}
delegateEvents(["keyup"]);

var _tmpl$$15 = /* @__PURE__ */ template(`<div id=submit-job-button-div class=mt-4><button id=submit-job-button type=button class="inline-flex items-center h-12 rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Annotate`);
function JobSubmitButton(props) {
  return (() => {
    var _el$ = _tmpl$$15(), _el$2 = _el$.firstChild;
    addEventListener(_el$2, "click", props.submitFn, true);
    createRenderEffect(() => _el$.classList.toggle("hidden", !props.inputExists));
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$14 = /* @__PURE__ */ template(`<div class="flex items-center justify-center ml-6"><input id=default-checkbox type=checkbox value=""title="If checked, each input files will be processed separately."class="w-4 h-4 text-blue-600 bg-gray-100 rounded border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"><label for=default-checkbox class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300"title="If checked, each input files will be processed separately.">Separate job per file`), _tmpl$2$d = /* @__PURE__ */ template(`<div class="flex items-center justify-center ml-6"><input id=default-checkbox type=checkbox title="If checked, each input line should be a path to an input file in the server."class="w-4 h-4 text-blue-600 bg-gray-100 checked:bg-gray-500 rounded border-gray-300 focus:ring-0 focus:ring-offset-0 dark:bg-gray-700 dark:border-gray-600"><label for=default-checkbox class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300"title="If checked, each input line should be a path to an input file in the server.">Server files`), _tmpl$3$8 = /* @__PURE__ */ template(`<div id=input-div class="w-[40rem] items-center flex flex-col"style="height:calc(100vh - 10rem);"><div class=flex></div><div class="w-full flex items-center justify-center mt-1"ondragenter=onDragEnterInputFiles(event) ondragover=onDragOverInputFiles(event) ondragleave=onDragLeaveInputFiles(event) ondrop=onDropInputFiles(event)>`);
function InputPanel(props) {
  function changeInputData(mode, data) {
    props.setInputMode(mode);
    if (mode == "drop") {
      props.setInputDataDrop(data);
    } else if (mode == "paste") {
      props.setInputDataPaste(data);
    }
  }
  createEffect(function() {
    if (props.inputMode == "drop") {
      props.setInputExists(props.inputDataDrop.length > 0);
    } else if (props.inputMode == "paste") {
      props.setInputExists(props.inputDataPaste.length > 0);
    }
  });
  function onChangeSeparateJobPerFile(_) {
    props.setSeparateJobPerFile(!props.separateJobPerFile);
  }
  function onChangeServerFileMode(_) {
    props.setServerFileMode(!props.serverFileMode());
  }
  return (() => {
    var _el$ = _tmpl$3$8(), _el$2 = _el$.firstChild, _el$7 = _el$2.nextSibling;
    insert(_el$2, createComponent(AssemblySelectPanel, {
      get assembly() {
        return props.assembly;
      },
      get setAssembly() {
        return props.setAssembly;
      }
    }), null);
    insert(_el$2, createComponent(InputFormatSelectPanel, {
      get inputFormat() {
        return props.inputFormat;
      },
      get setInputFormat() {
        return props.setInputFormat;
      }
    }), null);
    insert(_el$2, createComponent(Show, {
      get when() {
        return props.inputMode == "drop";
      },
      get children() {
        var _el$3 = _tmpl$$14(), _el$4 = _el$3.firstChild;
        _el$4.$$click = onChangeSeparateJobPerFile;
        createRenderEffect(() => _el$4.checked = props.separateJobPerFile);
        return _el$3;
      }
    }), null);
    insert(_el$2, createComponent(Show, {
      get when() {
        return props.inputMode == "paste";
      },
      get children() {
        var _el$5 = _tmpl$2$d(), _el$6 = _el$5.firstChild;
        _el$6.$$click = onChangeServerFileMode;
        return _el$5;
      }
    }), null);
    insert(_el$7, createComponent(Switch, {
      get children() {
        return [createComponent(Match, {
          get when() {
            return props.inputMode == "drop";
          },
          get children() {
            return createComponent(InputDropArea, {
              get setInputMode() {
                return props.setInputMode;
              },
              get inputDataDrop() {
                return props.inputDataDrop;
              },
              get setInputDataDrop() {
                return props.setInputDataDrop;
              }
            });
          }
        }), createComponent(Match, {
          get when() {
            return props.inputMode == "paste";
          },
          get children() {
            return createComponent(InputPasteArea, {
              get setInputMode() {
                return props.setInputMode;
              },
              changeInputData,
              get inputDataPaste() {
                return props.inputDataPaste;
              },
              get assembly() {
                return props.assembly;
              },
              get setAssembly() {
                return props.setAssembly;
              },
              get inputFormat() {
                return props.inputFormat;
              },
              get setInputFormat() {
                return props.setInputFormat;
              }
            });
          }
        })];
      }
    }));
    insert(_el$, createComponent(JobNameInput, {
      get inputExists() {
        return props.inputExists;
      },
      get jobName() {
        return props.jobName;
      },
      get setJobName() {
        return props.setJobName;
      }
    }), null);
    insert(_el$, createComponent(JobNoteInput, {
      get inputExists() {
        return props.inputExists;
      },
      get jobNote() {
        return props.jobNote;
      },
      get setJobNote() {
        return props.setJobNote;
      }
    }), null);
    insert(_el$, createComponent(JobSubmitButton, {
      get inputExists() {
        return props.inputExists;
      },
      get submitFn() {
        return props.submitFn;
      }
    }), null);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$13 = /* @__PURE__ */ template(`<input class="block w-full text-xs text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"type=file>`), _tmpl$2$c = /* @__PURE__ */ template(`<select class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">`), _tmpl$3$7 = /* @__PURE__ */ template(`<div class="flex flex-col mb-4"><span class="mb-2 font-xs">`), _tmpl$4$5 = /* @__PURE__ */ template(`<input type=text>`), _tmpl$5$3 = /* @__PURE__ */ template(`<option>`);
const {
  setModuleOption,
  getModuleOptions: getModuleOptions$1,
  getModuleOption
} = gvLocalModules;
function ModuleOption(props) {
  const [optionValue, setOptionValue] = createSignal(null);
  createEffect(function() {
    const prevModuleOption = getModuleOption(props.moduleName, props.option.name);
    if (optionValue() == null && prevModuleOption != null) {
      setOptionValue(prevModuleOption.value);
    }
  });
  function onChange(evt) {
    const value = evt.target.value;
    setOptionValue(evt.target.value);
    setModuleOption(props.moduleName, props.option, value);
  }
  return (() => {
    var _el$ = _tmpl$3$7(), _el$2 = _el$.firstChild;
    insert(_el$2, () => props.option.title);
    insert(_el$, createComponent(Switch, {
      get fallback() {
        return (() => {
          var _el$5 = _tmpl$4$5();
          _el$5.$$keyup = onChange;
          createRenderEffect(() => _el$5.value = optionValue());
          return _el$5;
        })();
      },
      get children() {
        return [createComponent(Match, {
          get when() {
            return props.option.method == "file";
          },
          get children() {
            var _el$3 = _tmpl$$13();
            _el$3.addEventListener("change", onChange);
            return _el$3;
          }
        }), createComponent(Match, {
          get when() {
            return props.option.method == "select";
          },
          get children() {
            var _el$4 = _tmpl$2$c();
            _el$4.addEventListener("change", onChange);
            _el$4.$$click = function(evt) {
              evt.stopPropagation();
            };
            insert(_el$4, createComponent(For, {
              get each() {
                return props.option.options;
              },
              children: (option) => (() => {
                var _el$6 = _tmpl$5$3();
                _el$6.value = option;
                insert(_el$6, option);
                return _el$6;
              })()
            }));
            createRenderEffect(() => setAttribute(_el$4, "title", props.option.help));
            createRenderEffect(() => _el$4.value = optionValue());
            return _el$4;
          }
        })];
      }
    }), null);
    createRenderEffect(() => setAttribute(_el$2, "title", props.option.help));
    return _el$;
  })();
}
delegateEvents(["click", "keyup"]);

function createGlobalStates$3() {
  const [annotators, setAnnotators] = createStore({
    __initial: true
  });
  const [postaggregators, setPostaggregators] = createStore({
    __initial: true
  });
  const [reporters, setReporters] = createStore({
    __initial: true
  });
  createEffect(function() {
    if (annotators["__initial"] == true) {
      setAnnotators(reconcile({}));
    }
    if (postaggregators["__initial"] == true) {
      setPostaggregators(reconcile({}));
    }
    if (reporters["__initial"] == true) {
      setReporters(reconcile({}));
    }
  });
  return {
    annotators,
    setAnnotators,
    postaggregators,
    setPostaggregators,
    reporters,
    setReporters
  };
}
const gvSubmitModules = createRoot(createGlobalStates$3);

const {
  localModules: localModules$2
} = gvLocalModules;
const {
  remoteModules: remoteModules$1
} = gvRemoteModules;
const {
  annotators,
  setAnnotators: setAnnotators$1,
  postaggregators,
  setPostaggregators: setPostaggregators$1,
  reporters,
  setReporters: setReporters$1
} = gvSubmitModules;
function deleteModule(mn) {
  const mI = localModules$2[mn];
  const ty = mI.type;
  let l = [];
  let missingList = [];
  findModulesRequiredByParam(mn, l, missingList);
  if (ty == "annotator") {
    setAnnotators$1(mn, void 0);
  } else if (ty == "postaggregator") {
    setPostaggregators$1(mn, void 0);
  } else if (ty == "reporter") {
    setReporters$1(mn, void 0);
  }
  for (const mn2 of l) {
    if (mn2 in annotators) {
      setAnnotators$1(mn2, void 0);
    } else if (mn2 in postaggregators) {
      setPostaggregators$1(mn2, void 0);
    } else if (mn2 in reporters) {
      setReporters$1(mn2, void 0);
    }
  }
  for (const mn2 in {
    ...annotators
  }) {
    addModuleDown(mn2);
  }
  for (const mn2 in {
    ...postaggregators
  }) {
    addModuleDown(mn2);
  }
  for (const mn2 in {
    ...reporters
  }) {
    addModuleDown(mn2);
  }
}
function deleteModuleUp(moduleName) {
  const l = [];
  findModulesDependingOnParam(moduleName, l);
  for (const mn of l) {
    deleteModule(mn);
  }
}
function deleteModuleDown(moduleName) {
  const l = [];
  const missingList = [];
  findModulesRequiredByParam(moduleName, l, missingList);
  for (const mn of l) {
    deleteModule(mn);
  }
}
function addModuleDown(moduleName) {
  addModuleDownNewList(moduleName);
}
function findModulesRequiredByParam(mn, l, missingList) {
  var mI = localModules$2[mn];
  if (mI == void 0) {
    mI = localModules$2[mn + "reporter"];
    if (mI == void 0) {
      if (missingList.includes(mn) == false) {
        missingList.push(mn);
      }
      return;
    }
  }
  if (l.includes(mn) == false) {
    l.push(mn);
  }
  const conf = mI.conf;
  if (conf == void 0) {
    return;
  }
  const depModuleNames = conf.requires;
  if (depModuleNames == void 0) {
    return;
  }
  for (const reqMn of depModuleNames) {
    if (l.indexOf(reqMn) == -1) {
      findModulesRequiredByParam(reqMn, l, missingList);
    }
  }
}
function findModulesDependingOnParam(moduleName, l) {
  for (const mn in localModules$2) {
    const mI = localModules$2[mn];
    const requires = mI.conf.requires;
    if (requires == void 0 || requires.length == 0) {
      continue;
    }
    const requiresCopy = [...requires];
    if (requiresCopy.includes(moduleName) && l.indexOf(moduleName) == -1) {
      if (l.indexOf(mn) == -1) {
        l.push(mn);
        findModulesDependingOnParam(mn, l);
      }
    }
  }
  l.push(moduleName);
  return l;
}
function addModuleDownNewList(mn) {
  const l = [mn];
  const missingList = [];
  findModulesRequiredByParam(mn, l, missingList);
  const notIgnoredMissingL = [];
  for (const missingMn of missingList) {
    const remoteM = remoteModules$1[missingMn];
    if (remoteM == void 0) {
      notIgnoredMissingL.push(remoteM);
    } else if (remoteM.type != "webviewerwidget") {
      notIgnoredMissingL.push(remoteM);
    }
  }
  if (notIgnoredMissingL.length > 0) {
    let msg = "The following modules should be installed to run this module:\n";
    for (const mn2 of notIgnoredMissingL) {
      msg += mn2.name + "\n";
    }
    let err = {
      response: {
        data: {
          msg
        }
      }
    };
    handleError(err);
    return;
  }
  for (var addMn of l) {
    var mI = localModules$2[addMn];
    if (mI == void 0) {
      addMn = addMn + "reporter";
      mI = localModules$2[addMn];
    }
    const ty = mI.type;
    if (ty == "annotator") {
      setAnnotators$1(addMn, mI);
    } else if (ty == "postaggregator") {
      setPostaggregators$1(addMn, mI);
    } else if (ty == "reporter") {
      setReporters$1(addMn, mI);
    } else {
      continue;
    }
  }
}

var _tmpl$$12 = /* @__PURE__ */ template(`<div class="relative modulecard relative items-center space-x-3 rounded-lg border border-gray-300 px-6 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400 p-2 z-0 mb-2"><div class="absolute left-0 bottom-0 w-full p-2 cursor-default"style="background-color:rgba(68, 64, 60, 0.3);"><a class="relative remove-up text-sm h-8 inline-flex items-center rounded-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-500 cursor-pointer focus:z-20 bg-white hover:bg-gray-100"title="Remove this module and any module depending on this module from analysis"></a><a class="ml-2 relative remove-up-down text-sm h-8 inline-flex items-center rounded-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-500 cursor-pointer focus:z-20 bg-white hover:bg-gray-100"title="Remove this module and all modules required by this module from analysis"></a></div><div><div class="float-left w-24 h-24 mr-2 flex justify-center items-center"><img class="w-20 rounded-lg"></div><div class="min-w-0 flex-1"style=min-height:6rem;><a class=focus:online-none><p class="text-md font-semibold text-gray-700"></p><p class="text-sm text-gray-500"></p></a></div></div><div class=w-full>`);
function ModuleCard$1(props) {
  const {
    serverUrl
  } = gvServer;
  const {
    localModules
  } = gvLocalModules;
  const [showX, setShowX] = createSignal(false);
  const {
    annotators,
    postaggregators,
    reporters
  } = gvSubmitModules;
  const moduleInfo = localModules[props.moduleName];
  function checkedInSelectedModules(modules) {
    return modules && props.moduleName in modules;
  }
  function checked() {
    return checkedInSelectedModules(annotators) || checkedInSelectedModules(postaggregators) || checkedInSelectedModules(reporters);
  }
  function onClickCard(evt) {
    evt.stopPropagation();
    const target = evt.target.closest("a");
    let removeUp = false;
    let removeUpDown = false;
    if (target != null) {
      removeUp = target.classList.contains("remove-up");
      removeUpDown = target.classList.contains("remove-up-down");
    }
    if (props.cardType == "selected") {
      if (removeUp) {
        deleteModuleUp(props.moduleName);
      } else if (removeUpDown) {
        deleteModuleUp(props.moduleName);
        deleteModuleDown(props.moduleName);
      } else if (moduleInfo.type == "reporter") {
        addModuleDown(props.moduleName);
      }
    } else {
      if (checked()) {
        if (removeUp) {
          deleteModuleUp(props.moduleName);
        } else if (removeUpDown) {
          deleteModuleUp(props.moduleName);
          deleteModuleDown(props.moduleName);
        }
      } else {
        addModuleDown(props.moduleName);
      }
    }
  }
  return (() => {
    var _el$ = _tmpl$$12(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling, _el$5 = _el$2.nextSibling, _el$6 = _el$5.firstChild, _el$7 = _el$6.firstChild, _el$8 = _el$6.nextSibling, _el$9 = _el$8.firstChild, _el$10 = _el$9.firstChild, _el$11 = _el$10.nextSibling, _el$12 = _el$5.nextSibling;
    _el$.$$click = onClickCard;
    _el$.addEventListener("mouseleave", (e) => setShowX(false, e));
    _el$.addEventListener("mouseenter", (e) => setShowX(true, e));
    insert(_el$3, createComponent(HiOutlineMinus, {}));
    insert(_el$4, createComponent(HiOutlineXMark, {}));
    insert(_el$10, () => moduleInfo && moduleInfo.title);
    insert(_el$11, () => moduleInfo && moduleInfo.conf.description);
    insert(_el$12, createComponent(Show, {
      get when() {
        return (props.cardType == "selected" || moduleInfo.type == "reporter") && moduleInfo.conf.module_options;
      },
      get children() {
        return createComponent(For, {
          get each() {
            return moduleInfo.conf.module_options;
          },
          children: (option) => createComponent(ModuleOption, {
            get moduleName() {
              return props.moduleName;
            },
            option
          })
        });
      }
    }));
    createRenderEffect((_p$) => {
      var _v$ = !!checked(), _v$2 = !!(props.cardType != "selected" || moduleInfo.type == "reporter"), _v$3 = !!(props.cardType != "selected"), _v$4 = !!(props.cardType == "selected" && moduleInfo.conf.module_options && checked()), _v$5 = moduleInfo && moduleInfo.name, _v$6 = moduleInfo && moduleInfo.kind, _v$7 = !!(!showX() || !checked()), _v$8 = serverUrl + "/store/locallogo?module=" + props.moduleName;
      _v$ !== _p$.e && _el$.classList.toggle("checked", _p$.e = _v$);
      _v$2 !== _p$.t && _el$.classList.toggle("cursor-copy", _p$.t = _v$2);
      _v$3 !== _p$.a && _el$.classList.toggle("max-h-64", _p$.a = _v$3);
      _v$4 !== _p$.o && _el$.classList.toggle("pb-16", _p$.o = _v$4);
      _v$5 !== _p$.i && setAttribute(_el$, "name", _p$.i = _v$5);
      _v$6 !== _p$.n && setAttribute(_el$, "kind", _p$.n = _v$6);
      _v$7 !== _p$.s && _el$2.classList.toggle("hidden", _p$.s = _v$7);
      _v$8 !== _p$.h && setAttribute(_el$7, "src", _p$.h = _v$8);
      return _p$;
    }, {
      e: void 0,
      t: void 0,
      a: void 0,
      o: void 0,
      i: void 0,
      n: void 0,
      s: void 0,
      h: void 0
    });
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$11 = /* @__PURE__ */ template(`<div id=report-choice-div class="w-[36rem] flex flex-col justify-center items-center"><div class="text-md text-gray-600">(Optional) reporters to run</div><div id=report-choice-items class="w-96 grid gap-2 justify-center overflow-y-auto bg-gray-100 py-4 rounded-md"style="height:calc(100vh - 10rem);">`);
const fetchReportTypes = async () => {
  const {
    serverUrl
  } = gvServer;
  const res = await fetch(serverUrl + "/submit/reporttypes");
  const reportTypes = (await res.json())["valid"];
  return reportTypes;
};
function ReportChoicePanel() {
  const [reportTypes] = createResource(fetchReportTypes);
  return (() => {
    var _el$ = _tmpl$$11(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling;
    insert(_el$3, createComponent(For, {
      get each() {
        return reportTypes();
      },
      children: (reportType) => createComponent(ModuleCard$1, {
        moduleName: reportType + "reporter",
        cardType: "selected"
      })
    }));
    return _el$;
  })();
}

var _tmpl$$10 = /* @__PURE__ */ template(`<div id=cta-analysis-module-choice class="absolute inset-x-0 bottom-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Click to select analysis modules`);
function CtaScrollDownToAnalysisModule(props) {
  function scrollToAnalysisModuleChoice() {
    const div = document.querySelector("#analysis-module-choice-div");
    div.scrollIntoView({
      behavior: "smooth"
    });
  }
  return (() => {
    var _el$ = _tmpl$$10(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild;
    _el$.$$click = scrollToAnalysisModuleChoice;
    insert(_el$5, createComponent(HiOutlineArrowDown, {
      color: "#6b7280"
    }), _el$6);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$$ = /* @__PURE__ */ template(`<button type=button class=filter-category>`);
function ModuleFilterCategoryButton(props) {
  function onChangeFilterCategoryRadio(_) {
    props.setFilterCategory(props.value);
  }
  return (() => {
    var _el$ = _tmpl$$$();
    _el$.$$click = onChangeFilterCategoryRadio;
    insert(_el$, () => props.title);
    createRenderEffect((_p$) => {
      var _v$ = !!(props.value == props.filterCategory), _v$2 = !!(props.pos == "left"), _v$3 = !!(props.pos == "right");
      _v$ !== _p$.e && _el$.classList.toggle("pinned", _p$.e = _v$);
      _v$2 !== _p$.t && _el$.classList.toggle("rounded-l-lg", _p$.t = _v$2);
      _v$3 !== _p$.a && _el$.classList.toggle("rounded-r-md", _p$.a = _v$3);
      return _p$;
    }, {
      e: void 0,
      t: void 0,
      a: void 0
    });
    createRenderEffect(() => _el$.value = props.value);
    return _el$;
  })();
}
delegateEvents(["click"]);

const {
  localModules: localModules$1
} = gvLocalModules;
function objectIsEmpty(o) {
  if (Object.keys(o).length == 0) {
    return true;
  } else {
    return false;
  }
}
function getAnnotatorsAndPostaggregators(searchText, selectedTag) {
  var text = searchText;
  if (text != null) {
    text = text.toLowerCase();
  }
  let moduleNames = [];
  for (const [moduleName, module] of Object.entries(localModules$1)) {
    let add = true;
    if (moduleName == "tagsampler" || moduleName == "vcfinfo" || moduleName == "varmeta") {
      add = false;
    } else if (module.type != "annotator" && module.type != "postaggregator") {
      add = false;
    } else if (selectedTag != null) {
      if (selectedTag == "no tag") {
        if (module.tags.length > 0) {
          add = false;
        }
      } else if (module.tags.indexOf(selectedTag) == -1) {
        add = false;
      }
    }
    if (add && text != null) {
      add = false;
      if (moduleName.toLowerCase().indexOf(text) >= 0) {
        add = true;
      } else if (module.title.toLowerCase().indexOf(text) >= 0) {
        add = true;
      } else if (module.description && module.description.toLowerCase().indexOf(text) >= 0) {
        add = true;
      }
    }
    if (add) {
      moduleNames.push(moduleName);
    }
  }
  moduleNames.sort();
  return moduleNames;
}
function getSizeString(size) {
  const dm = 1;
  const kilo = 1024;
  const mega = kilo * kilo;
  const giga = mega * kilo;
  const tera = giga * kilo;
  let sizeS = "";
  if (size > tera) {
    sizeS = (size / tera).toFixed(dm) + " TB";
  } else if (size > giga) {
    sizeS = (size / giga).toFixed(dm) + " GB";
  } else if (size > mega) {
    sizeS = (size / mega).toFixed(dm) + " MB";
  } else if (size > kilo) {
    sizeS = (size / kilo).toFixed(dm) + " KB";
  } else {
    sizeS = size + "B";
  }
  return sizeS;
}

var _tmpl$$_ = /* @__PURE__ */ template(`<div class="flex mb-2"><label for=search class=sr-only>Search</label><input type=text name=search class="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm mr-2 w-48"placeholder=Search><button type=button class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Add all</button><button type=button class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-2">Remove all`);
function ModuleSearchPanel$1(props) {
  function updateSearchText(evt) {
    props.setSearchText(evt.target.value);
  }
  function selectAll() {
    const moduleNames = getAnnotatorsAndPostaggregators(props.searchText, props.selectedTag);
    for (const mn of moduleNames) {
      addModuleDown(mn);
    }
  }
  function deselectAll() {
    const moduleNames = getAnnotatorsAndPostaggregators(props.searchText, props.selectedTag);
    for (const mn of moduleNames) {
      deleteModuleUp(mn);
      deleteModuleDown(mn);
    }
  }
  return (() => {
    var _el$ = _tmpl$$_(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.nextSibling, _el$5 = _el$4.nextSibling;
    _el$3.$$keyup = updateSearchText;
    _el$4.$$click = selectAll;
    _el$5.$$click = deselectAll;
    createRenderEffect(() => _el$3.value = props.searchText);
    return _el$;
  })();
}
delegateEvents(["keyup", "click"]);

var _tmpl$$Z = /* @__PURE__ */ template(`<div class="filtered-modules-div overflow-auto pr-2"style="height:calc(95vh - 10rem);">`);
function ModuleDisplayPanel$1(props) {
  return (() => {
    var _el$ = _tmpl$$Z();
    insert(_el$, createComponent(For, {
      get each() {
        return getAnnotatorsAndPostaggregators(props.searchText, props.selectedTag);
      },
      children: (moduleName) => createComponent(ModuleCard$1, {
        moduleName
      })
    }));
    createRenderEffect((_p$) => {
      var _v$ = `filtered-modules-${props.kind}`, _v$2 = !!(props.noCols == 2), _v$3 = !!(props.noCols == 1);
      _v$ !== _p$.e && setAttribute(_el$, "id", _p$.e = _v$);
      _v$2 !== _p$.t && _el$.classList.toggle("grid-cols-2", _p$.t = _v$2);
      _v$3 !== _p$.a && _el$.classList.toggle("grid-cols-1", _p$.a = _v$3);
      return _p$;
    }, {
      e: void 0,
      t: void 0,
      a: void 0
    });
    return _el$;
  })();
}

var _tmpl$$Y = /* @__PURE__ */ template(`<div id=analysis-module-filter-panel-all class="analysis-module-filter-panel w-full mt-4 overflow-auto">`);
function AnalysisModuleFilterPanelAll(props) {
  const [searchText, setSearchText] = createSignal(null);
  const [selectedTag, setSelectedTag] = createSignal(null);
  return (() => {
    var _el$ = _tmpl$$Y();
    insert(_el$, createComponent(ModuleSearchPanel$1, {
      kind: "all",
      get searchText() {
        return searchText();
      },
      setSearchText,
      get selectedTag() {
        return selectedTag();
      }
    }), null);
    insert(_el$, createComponent(ModuleDisplayPanel$1, {
      kind: "all",
      side: "local",
      noCols: 1,
      get searchText() {
        return searchText();
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.filterCategory != "all")));
    return _el$;
  })();
}

var _tmpl$$X = /* @__PURE__ */ template(`<div class="relative flex items-start mb-2"><div class="flex items-center"><input type=radio name=module-tag class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"><label class="ml-3 block text-sm font-medium text-gray-600">`);
function escapeTag(s) {
  return s.replace(" ", "_");
}
function titleCase(s) {
  return s.replace(/\w\S*/g, function(t) {
    return t.charAt(0).toUpperCase() + t.substr(1).toLowerCase();
  });
}
function AnalysisModuleFilterPanelTagItem(props) {
  const uid = `module-tag-radio-${escapeTag(props.value)}`;
  return (() => {
    var _el$ = _tmpl$$X(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling;
    _el$3.$$click = props.setSelectedTag;
    _el$3.$$clickData = props.value;
    setAttribute(_el$3, "id", uid);
    setAttribute(_el$4, "for", uid);
    insert(_el$4, () => titleCase(props.value));
    createRenderEffect(() => setAttribute(_el$, "title", props.title));
    createRenderEffect(() => _el$3.value = props.value);
    createRenderEffect(() => _el$3.checked = props.selectedTag == props.value);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$W = /* @__PURE__ */ template(`<div id=analysis-module-filter-panel-tags class="analysis-module-filter-panel w-full mt-4 overflow-auto grid grid-cols-3"><div id=analysis-module-filter-items-tags class="col-span-1 flex flex-col justify-leading pl-1 overflow-y-auto"style="height:calc(95vh - 8rem);"></div><div class=col-span-2>`);
const fetchTags = async () => {
  const {
    serverUrl
  } = gvServer;
  let tags = await (await fetch(serverUrl + "/submit/tags_annotators_postaggregators")).json();
  tags.push("no tag");
  return tags;
};
function AnalysisModuleFilterPanelTags(props) {
  const [tags] = createResource(fetchTags);
  const [searchText, setSearchText] = createSignal(null);
  const [selectedTag, setSelectedTag] = createSignal(null);
  return (() => {
    var _el$ = _tmpl$$W(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling;
    insert(_el$2, createComponent(For, {
      get each() {
        return tags();
      },
      children: (tag) => createComponent(AnalysisModuleFilterPanelTagItem, {
        value: tag,
        setSelectedTag
      })
    }));
    insert(_el$3, createComponent(ModuleSearchPanel$1, {
      kind: "tags",
      get searchText() {
        return searchText();
      },
      setSearchText,
      get selectedTag() {
        return selectedTag();
      }
    }), null);
    insert(_el$3, createComponent(ModuleDisplayPanel$1, {
      kind: "tags",
      noCols: 1,
      get selectedTag() {
        return selectedTag();
      },
      get searchText() {
        return searchText();
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.filterCategory != "tags")));
    return _el$;
  })();
}

var _tmpl$$V = /* @__PURE__ */ template(`<div class="analysis-module-filter-wrapper col-span-7"><div id=analysis-module-filter-kinds class=w-full><div class="inline-flex rounded-md shadow-sm"role=group>`);
function AnalysisModuleFilterWrapper(props) {
  const [filterCategory, setFilterCategory] = createSignal("all");
  return (() => {
    var _el$ = _tmpl$$V(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild;
    insert(_el$3, createComponent(ModuleFilterCategoryButton, {
      value: "all",
      title: "All",
      pos: "left",
      get filterCategory() {
        return filterCategory();
      },
      setFilterCategory
    }), null);
    insert(_el$3, createComponent(ModuleFilterCategoryButton, {
      value: "tags",
      title: "Tags",
      pos: "right",
      get filterCategory() {
        return filterCategory();
      },
      setFilterCategory
    }), null);
    insert(_el$, createComponent(AnalysisModuleFilterPanelAll, {
      get filterCategory() {
        return filterCategory();
      },
      get localModules() {
        return props.localModules;
      }
    }), null);
    insert(_el$, createComponent(AnalysisModuleFilterPanelTags, {
      get filterCategory() {
        return filterCategory();
      },
      get localModules() {
        return props.localModules;
      }
    }), null);
    return _el$;
  })();
}

var _tmpl$$U = /* @__PURE__ */ template(`<div class=col-span-4><div class="text-gray-600 bg-gray-100 rounded-md border border-transparent font-medium px-3 py-1.5 h-[34px]">Selected analysis modules</div><div class="flex mb-2 mt-4"><button type=button class="items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 h-[38px]">Clear</button></div><div class="relative filtered-modules-div overflow-auto pr-2">`);
function SelectedAnalysisModules() {
  const {
    annotators,
    setAnnotators,
    postaggregators,
    setPostaggregators
  } = gvSubmitModules;
  function selectedModules() {
    let moduleNames = [];
    for (const moduleName in annotators) {
      moduleNames.push(moduleName);
    }
    for (const moduleName in postaggregators) {
      moduleNames.push(moduleName);
    }
    moduleNames.sort();
    return moduleNames;
  }
  function clearSelectedModules() {
    setAnnotators({});
    setPostaggregators({});
  }
  return (() => {
    var _el$ = _tmpl$$U(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.firstChild, _el$5 = _el$3.nextSibling;
    _el$4.$$click = clearSelectedModules;
    _el$5.style.setProperty("height", "calc(100vh - 12rem)");
    insert(_el$5, createComponent(For, {
      get each() {
        return selectedModules();
      },
      children: function(moduleName) {
        return createComponent(ModuleCard$1, {
          moduleName,
          cardType: "selected"
        });
      }
    }));
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$T = /* @__PURE__ */ template(`<div id=cta-input class="absolute inset-x-0 top-0 cursor-pointer"><div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8"><div class="rounded-lg bg-indigo-50 p-2 shadow-md sm:p-3"><div class="flex flex-wrap items-center justify-between"><div class="flex w-0 flex-1 items-center"><p class="ml-3 truncate font-medium text-gray-500 text-center"><span>Go back to the input panel`);
function CtaScrollUpToInput(props) {
  function scrollToInput() {
    const div = document.querySelector("#input-div");
    div.scrollIntoView({
      behavior: "smooth"
    });
  }
  return (() => {
    var _el$ = _tmpl$$T(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild;
    _el$.$$click = scrollToInput;
    insert(_el$5, createComponent(HiOutlineArrowUp, {
      color: "#6b7280"
    }), _el$6);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$S = /* @__PURE__ */ template(`<div id=analysis-module-choice-div class="relative container mt-6 mb-4 snap-center flex justify-center max-w-7xl max-w-7xl"><div id=analysis-module-filter-div class="bg-white p-4 rounded-md ml-4 mt-4 overflow-auto flex flex-col gap-8 text-gray-600 h-[95vh] w-full"><div id=analysis-module-div class="grid grid-cols-12 gap-2 mt-8"style="height:calc(95vh - 20rem);"><div class="col-span-1 flex flex-col justify-center content-center items-center">`);
function AnalysisModuleChoice(props) {
  return (() => {
    var _el$ = _tmpl$$S(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild;
    _el$.style.setProperty("height", "calc(100vh - 3rem)");
    insert(_el$, createComponent(CtaScrollUpToInput, {}), _el$2);
    insert(_el$3, createComponent(AnalysisModuleFilterWrapper, {
      get localModules() {
        return props.localModules;
      }
    }), _el$4);
    insert(_el$4, createComponent(HiOutlineArrowRight, {}));
    insert(_el$3, createComponent(SelectedAnalysisModules, {}), null);
    return _el$;
  })();
}

var _tmpl$$R = /* @__PURE__ */ template(`<li><a href=# class="block hover:bg-gray-50"><div class=py-4><div class="flex items-center justify-between"><p class="truncate text-sm font-medium text-indigo-600"></p></div><div class="mt-2 sm:flex sm:justify-between"><div class="mt-2 w-full flex items-center text-sm text-gray-500 sm:mt-0"><div class="w-full bg-gray-200 rounded-full dark:bg-gray-700"><div class="bg-blue-600 text-xs font-medium text-blue-100 text-center p-0.5 leading-none rounded-full">%`);
function UploadProgressFile(props) {
  return (() => {
    var _el$ = _tmpl$$R(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$4.nextSibling, _el$7 = _el$6.firstChild, _el$8 = _el$7.firstChild, _el$9 = _el$8.firstChild, _el$10 = _el$9.firstChild;
    insert(_el$5, () => props.fileName);
    insert(_el$9, () => props.progress, _el$10);
    createRenderEffect(() => props.progress + "%" != null ? _el$9.style.setProperty("width", props.progress + "%") : _el$9.style.removeProperty("width"));
    return _el$;
  })();
}

var _tmpl$$Q = /* @__PURE__ */ template(`<div class="relative z-10"aria-labelledby=modal-title role=dialog aria-modal=true><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6"><div><div class="mt-3 text-center sm:mt-5"><ul role=list class="divide-y divide-gray-200"></ul></div></div><div class="mt-5 sm:mt-6"><button type=button class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm">Cancel`);
function UploadProgressDialog(props) {
  function abort() {
    props.controller.abort();
  }
  return (() => {
    var _el$ = _tmpl$$Q(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild, _el$7 = _el$6.firstChild, _el$8 = _el$7.firstChild, _el$9 = _el$6.nextSibling, _el$10 = _el$9.firstChild;
    insert(_el$8, createComponent(UploadProgressFile, {
      fileName: "Uploading...",
      get progress() {
        return props.uploadState.progress;
      }
    }));
    _el$10.$$click = abort;
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$P = /* @__PURE__ */ template(`<div class="relative z-10"aria-labelledby=modal-title role=dialog aria-modal=true><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100"><svg class="h-6 w-6 text-green-600"xmlns=http://www.w3.org/2000/svg fill=none viewBox="0 0 24 24"stroke-width=1.5 stroke=currentColor aria-hidden=true><path stroke-linecap=round stroke-linejoin=round d="M4.5 12.75l6 6 9-13.5"></path></svg></div><div class="mt-3 text-center sm:mt-5"><h3 class="text-lg font-medium leading-6 text-gray-900"></h3><div class=mt-2><p class="text-sm text-gray-500"></p></div></div></div><div class="mt-5 sm:mt-6"><button type=button class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm">Dismiss`);
function OkDialog(props) {
  return (() => {
    var _el$ = _tmpl$$P(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild, _el$7 = _el$6.firstChild, _el$8 = _el$7.nextSibling, _el$9 = _el$8.firstChild, _el$10 = _el$9.nextSibling, _el$11 = _el$10.firstChild, _el$12 = _el$6.nextSibling, _el$13 = _el$12.firstChild;
    insert(_el$9, () => props.title);
    insert(_el$11, () => props.text);
    addEventListener(_el$13, "click", props.callback, true);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$O = /* @__PURE__ */ template(`<div class="tabcontent p-4 snap-y snap-mandatory h-screen overflow-y-auto"><div class="relative container flex gap-8 snap-center max-w-7xl h-[95vh] justify-center items-start">`), _tmpl$2$b = /* @__PURE__ */ template(`<div>Loading...`), _tmpl$3$6 = /* @__PURE__ */ template(`<div><span>Analysis submission was successful.</span><br><span>You can find the status of your analysis submission on the Results section.</span><br><span>`);
const {
  tabName: tabName$1
} = gvTabName;
const {
  localModules,
  getModuleOptions
} = gvLocalModules;
const {
  serverUrl: serverUrl$2,
  withCredentials: withCredentials$1
} = gvServer;
const {
  logged: logged$1
} = gvLogin;
const {
  multiuser: multiuser$1
} = gvMultiuser;
function TabSubmit(props) {
  const [inputMode, setInputMode] = createSignal("drop");
  const [inputFormat, setInputFormat] = createSignal("");
  const [inputDataDrop, setInputDataDrop] = createSignal([]);
  const [inputDataPaste, setInputDataPaste] = createSignal("");
  const {
    annotators,
    setAnnotators,
    postaggregators,
    setPostaggregators,
    reporters,
    setReporters
  } = gvSubmitModules;
  const [assembly, setAssembly] = createSignal("");
  const [inputExists, setInputExists] = createSignal(false);
  const [jobName, setJobName] = createSignal(null);
  const [jobNote, setJobNote] = createSignal(null);
  const [uploading, setUploading] = createSignal(false);
  const [uploadState, setUploadState] = createSignal({});
  const [submissionSuccessful, setSubmissionSuccessful] = createSignal(false);
  const [submittedJobName, setSubmittedJobName] = createSignal(null);
  const [separateJobPerFile, setSeparateJobPerFile] = createSignal(false);
  const [serverFileMode, setServerFileMode] = createSignal(false);
  let inputFiles = [];
  let formData = null;
  let submitOption = {};
  let controller;
  createEffect(function() {
    if (multiuser$1() && !logged$1()) {
      resetData();
    }
  });
  function resetData() {
    setInputMode("drop");
    setInputFormat("");
    setInputDataDrop([]);
    setInputDataPaste([]);
    setAnnotators(reconcile({}));
    setPostaggregators(reconcile({}));
    setReporters(reconcile({}));
    setAssembly("");
    setInputExists(false);
    setJobName(null);
    setJobNote(null);
    setUploading(false);
    setUploadState({});
  }
  function isServerFileList() {
    return serverFileMode();
  }
  function processInputServerFiles() {
    let inputServerFiles = [];
    let words = inputDataPaste().split("\n");
    for (var i = 0; i < words.length; i++) {
      let word = words[i];
      if (word == "" || word.startsWith("#")) {
        continue;
      }
      inputServerFiles.push(word.trim());
    }
    if (inputServerFiles.length > 0) {
      submitOption["inputServerFiles"] = inputServerFiles;
    }
  }
  function processInputText() {
    inputFiles = [];
    const textBlob = new Blob([inputDataPaste()], {
      type: "text/plain"
    });
    inputFiles.push(new File([textBlob], "input"));
  }
  function processTextInput() {
    if (isServerFileList()) {
      processInputServerFiles();
    } else {
      processInputText();
    }
  }
  function addAnnotatorsToSubmitOption() {
    submitOption.annotators = [];
    for (const moduleName in annotators) {
      submitOption.annotators.push(moduleName);
    }
  }
  function addPostaggregatorsToSubmitOption() {
    submitOption.postaggregators = [];
    for (const moduleName in postaggregators) {
      submitOption.postaggregators.push(moduleName);
    }
  }
  function addReportersToSubmitOption() {
    submitOption.report_types = [];
    for (const moduleName in reporters) {
      submitOption.report_types.push(moduleName.substring(0, moduleName.lastIndexOf("reporter")));
    }
  }
  function addAssemblyToSubmitOption() {
    if (assembly() != "auto") {
      submitOption["genome"] = assembly();
    }
  }
  function addInputFormatToSubmitOption() {
    submitOption["input_format"] = inputFormat();
  }
  function addJobNameToSubmitOption() {
    submitOption["job_name"] = jobName();
  }
  function addNoteToSubmitOption() {
    submitOption["note"] = jobNote();
  }
  function addModuleOptions(formData2) {
    let modules = {};
    for (const moduleName in annotators) {
      modules[moduleName] = annotators[moduleName];
    }
    for (const moduleName in postaggregators) {
      modules[moduleName] = postaggregators[moduleName];
    }
    for (const moduleName in reporters) {
      modules[moduleName] = reporters[moduleName];
    }
    const moduleOptions = getModuleOptions(modules, formData2);
    submitOption["module_options"] = moduleOptions;
  }
  function commitSubmit() {
    controller = new AbortController();
    setUploading(true);
    setUploadState({
      progress: 0
    });
    axios({
      method: "post",
      url: serverUrl$2 + "/submit/submit?" + Math.random(),
      data: formData,
      transformRequest: () => formData,
      signal: controller.signal,
      withCredentials: withCredentials$1,
      onUploadProgress: (p) => {
        let progress = Math.round(p.progress * 100);
        setUploadState({
          progress
        });
      }
    }).then(function(res) {
      setUploading(false);
      setSubmittedJobName(res.data.job_name);
      setSubmissionSuccessful(true);
      setTimeout(function() {
        props.setJobsTrigger(!props.jobsTrigger);
      }, 500);
    }).catch(function(err) {
      if (err.code != "ERR_CANCELED") {
        handleError(err);
      }
      setUploadState({});
      setUploading(false);
    });
  }
  function addCombineInputToJobOption() {
    submitOption["combine_input"] = !(separateJobPerFile() == true);
  }
  function makeInputFiles() {
    inputFiles = {};
    if (inputMode() == "drop") {
      inputFiles = inputDataDrop();
    } else if (inputMode() == "paste") {
      processTextInput();
    }
  }
  function addAllInputFilesToFormData() {
    if (inputFiles.length > 0) {
      for (var i = 0; i < inputFiles.length; i++) {
        formData.append("file_" + i, inputFiles[i]);
      }
    }
  }
  function addOneInputFileToFormData(inputNo) {
    formData.append("file_" + inputNo, inputFiles[inputNo]);
  }
  function initializeFormData() {
    formData = new FormData();
  }
  function makeFormData(inputNo) {
    initializeFormData();
    if (separateJobPerFile() != true) {
      addAllInputFilesToFormData();
    } else {
      addOneInputFileToFormData(inputNo);
    }
    addSubmitOptionsToFormData();
  }
  function addSubmitOptionsToFormData() {
    addAnnotatorsToSubmitOption();
    addPostaggregatorsToSubmitOption();
    addReportersToSubmitOption();
    addAssemblyToSubmitOption();
    addInputFormatToSubmitOption();
    addCombineInputToJobOption();
    addJobNameToSubmitOption();
    addNoteToSubmitOption();
    addModuleOptions(formData);
    submitOption["writeadmindb"] = true;
    formData.append("options", JSON.stringify(submitOption));
  }
  function processCombineInputSubmit() {
    submitOption = {};
    makeInputFiles();
    makeFormData();
    commitSubmit();
  }
  function processSeparateInputSubmit() {
    submitOption = {};
    makeInputFiles();
    for (let inputNo = 0; inputNo < inputFiles.length; inputNo++) {
      makeFormData(inputNo);
      commitSubmit();
    }
  }
  function submitFn() {
    if (separateJobPerFile() == true) {
      processSeparateInputSubmit();
    } else {
      processCombineInputSubmit();
    }
  }
  return (() => {
    var _el$ = _tmpl$$O(), _el$2 = _el$.firstChild;
    insert(_el$2, createComponent(Show, {
      get when() {
        return multiuser$1() == false || logged$1() == true;
      },
      get children() {
        return createComponent(InputPanel, {
          get inputMode() {
            return inputMode();
          },
          setInputMode,
          get inputDataDrop() {
            return inputDataDrop();
          },
          setInputDataDrop,
          get inputDataPaste() {
            return inputDataPaste();
          },
          setInputDataPaste,
          get assembly() {
            return assembly();
          },
          setAssembly,
          get inputFormat() {
            return inputFormat();
          },
          setInputFormat,
          get inputExists() {
            return inputExists();
          },
          setInputExists,
          get jobName() {
            return jobName();
          },
          setJobName,
          get jobNote() {
            return jobNote();
          },
          setJobNote,
          submitFn,
          get separateJobPerFile() {
            return separateJobPerFile();
          },
          setSeparateJobPerFile,
          serverFileMode,
          setServerFileMode
        });
      }
    }), null);
    insert(_el$2, createComponent(Show, {
      get when() {
        return inputExists();
      },
      get children() {
        return [createComponent(Show, {
          get when() {
            return !objectIsEmpty(localModules);
          },
          get fallback() {
            return _tmpl$2$b();
          },
          get children() {
            return createComponent(ReportChoicePanel, {});
          }
        }), createComponent(CtaScrollDownToAnalysisModule, {})];
      }
    }), null);
    insert(_el$, createComponent(Show, {
      get when() {
        return inputExists();
      },
      get children() {
        return createComponent(AnalysisModuleChoice, {});
      }
    }), null);
    insert(_el$, createComponent(Show, {
      get when() {
        return uploading();
      },
      get children() {
        return createComponent(UploadProgressDialog, {
          get uploadState() {
            return uploadState();
          },
          controller
        });
      }
    }), null);
    insert(_el$, createComponent(Show, {
      get when() {
        return submissionSuccessful() == true;
      },
      get children() {
        return createComponent(OkDialog, {
          get title() {
            return "Success: " + submittedJobName();
          },
          get text() {
            return (() => {
              var _el$4 = _tmpl$3$6(), _el$5 = _el$4.firstChild, _el$6 = _el$5.nextSibling, _el$7 = _el$6.nextSibling, _el$8 = _el$7.nextSibling, _el$9 = _el$8.nextSibling;
              insert(_el$9, () => "Look for the name " + submittedJobName() + ".");
              return _el$4;
            })();
          },
          callback: function() {
            setSubmissionSuccessful(false);
          }
        });
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(tabName$1() != "submit")));
    return _el$;
  })();
}

var _tmpl$$N = /* @__PURE__ */ template(`<a href=# class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900"role=menuitem tabindex=-1 value="">`);
function ActionPanelOption(props) {
  function changeAction() {
    props.setAction(props.optionValue);
    props.execute();
    props.setShow(false);
  }
  return (() => {
    var _el$ = _tmpl$$N();
    _el$.$$click = changeAction;
    insert(_el$, () => props.optionTitle);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$M = /* @__PURE__ */ template(`<div class="option-list ease-in absolute right-0 z-10 mt-12 w-24 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"role=menu><div class=py-1 role=none>`);
function ActionPanelSelect(props) {
  return (() => {
    var _el$ = _tmpl$$M(), _el$2 = _el$.firstChild;
    insert(_el$2, createComponent(For, {
      get each() {
        return props.options;
      },
      children: function(option) {
        return createComponent(ActionPanelOption, {
          get optionValue() {
            return option.value;
          },
          get optionTitle() {
            return option.title;
          },
          get execute() {
            return props.execute;
          },
          get setAction() {
            return props.setAction;
          },
          get setShow() {
            return props.setShow;
          }
        });
      }
    }));
    createRenderEffect(() => _el$.classList.toggle("hidden", !props.show));
    return _el$;
  })();
}

var _tmpl$$L = /* @__PURE__ */ template(`<div class="select-div relative inline-flex text-left"><div><button type=button class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100"id=assembly-select-div title="Job action">Action`);
function ActionPanel(props) {
  const [show, setShow] = createSignal(false);
  const [action, setAction] = createSignal("");
  const options = [{
    value: "abort",
    title: "Abort"
  }, {
    value: "delete",
    title: "Delete"
  }, {
    value: "copy_to_submit",
    title: "Copy to submit"
  }];
  function execute() {
    props.performJobAction(action());
  }
  function toggleShowSelect(_) {
    setShow(!show());
  }
  return (() => {
    var _el$ = _tmpl$$L(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild; _el$3.firstChild;
    _el$3.$$click = toggleShowSelect;
    insert(_el$3, createComponent(HiOutlineChevronDown, {
      "class": "-mr-1 ml-2 h-5 w-5"
    }), null);
    insert(_el$, createComponent(ActionPanelSelect, {
      get show() {
        return show();
      },
      options,
      execute,
      setAction,
      setShow
    }), null);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$K = /* @__PURE__ */ template(`<div class="flex bg-white pb-2 mt-2"><div class=flex><nav class="isolate inline-flex rounded-md shadow-sm ml-8"aria-label=Pagination><a href=# class="jobs-table-page-nav-btn relative inline-flex items-center rounded-l-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span aria-current=page class="relative z-10 inline-flex items-center border bg-white border-gray-300 text-gray-500 px-4 py-2 text-sm font-medium focus:z-20"></span><a href=# class="jobs-table-page-nav-btn relative inline-flex items-center rounded-r-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20"></a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Go to page</span><input type=text class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href=# class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">Go</a><span class="relative inline-flex items-center border-gray-300 bg-white ml-4 px-2 py-2 text-sm font-medium text-gray-500">Show</span><input type=text class="relative inline-flex items-center rounded-md w-12 border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500"><a href=# class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20">jobs per page</a><a href=# class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20 ml-4">`);
function PageNavigation(props) {
  function decreasePageno() {
    let pageno = props.pageno;
    pageno = pageno - 1;
    if (pageno <= 0) {
      pageno = 1;
    }
    if (pageno != props.pageno) {
      props.setPageno(pageno);
    }
  }
  function increasePageno() {
    let pageno = props.pageno;
    pageno = pageno + 1;
    if (pageno != props.pageno) {
      props.setPageno(pageno);
    }
  }
  function changePageno(evt) {
    let pageno = evt.target.value;
    try {
      pageno = parseInt(pageno);
    } catch (err) {
      console.error(err);
      return;
    }
    if (pageno < 1) {
      pageno = 1;
    }
    props.setPageno(pageno);
  }
  function changePagesize(evt) {
    let pagesize = evt.target.value;
    try {
      pagesize = parseInt(pagesize);
    } catch (err) {
      console.error(err);
      return;
    }
    props.setPagesize(pagesize);
  }
  function reload(_) {
    props.setJobsTrigger(!props.jobsTrigger);
  }
  return (() => {
    var _el$ = _tmpl$$K(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.nextSibling, _el$6 = _el$5.nextSibling, _el$7 = _el$6.nextSibling, _el$8 = _el$7.nextSibling, _el$9 = _el$8.nextSibling, _el$10 = _el$9.nextSibling, _el$11 = _el$10.nextSibling, _el$12 = _el$11.nextSibling, _el$13 = _el$12.nextSibling;
    insert(_el$2, createComponent(ActionPanel, {
      get performJobAction() {
        return props.performJobAction;
      }
    }), _el$3);
    _el$4.$$click = decreasePageno;
    insert(_el$4, createComponent(HiOutlineChevronLeft, {
      "class": "w-5 h-5"
    }));
    insert(_el$5, () => props.pageno);
    _el$6.$$click = increasePageno;
    insert(_el$6, createComponent(HiOutlineChevronRight, {
      "class": "w-5 h-5"
    }));
    _el$8.addEventListener("change", changePageno);
    _el$11.addEventListener("change", changePagesize);
    _el$13.$$click = reload;
    insert(_el$13, createComponent(HiOutlineArrowPath, {
      "class": "w-5 h-5"
    }));
    createRenderEffect(() => _el$8.value = props.pageno);
    createRenderEffect(() => _el$11.value = props.pagesize);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$J = /* @__PURE__ */ template(`<a>`);
function Button(props) {
  return (() => {
    var _el$ = _tmpl$$J();
    addEventListener(_el$, "click", props.clickFn, true);
    insert(_el$, () => props.children);
    createRenderEffect((_p$) => {
      var _v$ = "relative text-sm h-8 inline-flex items-center rounded-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-500 cursor-pointer focus:z-20 " + props.bgColor + " " + props.bgHoverColor, _v$2 = props.hrefValue, _v$3 = props.targetValue;
      _v$ !== _p$.e && className(_el$, _p$.e = _v$);
      _v$2 !== _p$.t && setAttribute(_el$, "href", _p$.t = _v$2);
      _v$3 !== _p$.a && setAttribute(_el$, "target", _p$.a = _v$3);
      return _p$;
    }, {
      e: void 0,
      t: void 0,
      a: void 0
    });
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$I = /* @__PURE__ */ template(`<div>`), _tmpl$2$a = /* @__PURE__ */ template(`<span class="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800">`), _tmpl$3$5 = /* @__PURE__ */ template(`<span class="inline-flex rounded-full bg-amber-100 px-2 text-xs font-semibold leading-5 text-amber-800">`), _tmpl$4$4 = /* @__PURE__ */ template(`<span class="inline-flex rounded-full bg-red-100 px-2 text-xs font-semibold leading-5 text-red-800">`), _tmpl$5$2 = /* @__PURE__ */ template(`<span class="inline-flex text-xs">`), _tmpl$6$2 = /* @__PURE__ */ template(`<tr class="text-sm h-16"><td scope=col class="relative w-12 px-6 sm:w-16 sm:px-8 bg-gray-50"><input type=checkbox class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></td><td class=jobs-table-td></td><td class="jobs-table-td bg-gray-50"></td><td class=jobs-table-td></td><td class="jobs-table-td bg-gray-50"></td><td class=jobs-table-td></td><td class="jobs-table-td bg-gray-50 text-xs"></td><td class=jobs-table-td></td><td class="jobs-table-td bg-gray-50"></td><td class=jobs-table-td>`);
function noStatusFetchNeeded(status) {
  return status == "Finished" || status == "Error" || status == "Aborted";
}
function JobRow(props) {
  const {
    serverUrl,
    withCredentials
  } = gvServer;
  const fetchInterval = 1e4;
  let timer = null;
  onCleanup(() => clearInterval(timer));
  function toggleChecked() {
    props.changeJobChecked(props.job.uid);
    props.setAllMarksOn(null);
  }
  function fetchStatus() {
    axios.get(serverUrl + "/submit/jobstatus", {
      params: {
        uid: props.job.uid
      },
      withCredentials
    }).then(function(response) {
      const data = response.data;
      if (noStatusFetchNeeded(data)) {
        clearInterval(timer);
      }
      props.changeJobStatus(props.job.uid, data);
    }).catch(function(err) {
      console.error(err);
    });
  }
  function checkNeedToFetchStatus() {
    const status = props.job.status;
    const need = status != "Finished" && status != "Error" && status != "Aborted";
    if (need) {
      timer = setInterval(function() {
        fetchStatus();
      }, fetchInterval);
    }
  }
  function viewable() {
    return props.job.status == "Finished";
  }
  function viewComponent() {
    if (viewable()) {
      return createComponent(Button, {
        children: "View",
        get hrefValue() {
          return serverUrl + "/result/nocache/index.html?uid=" + props.job.uid;
        },
        targetValue: "_blank",
        bgColor: "bg-sky-100",
        bgHoverColor: "hover:bg-sky-200"
      });
    } else {
      return _tmpl$$I();
    }
  }
  function logComponent() {
    return createComponent(Button, {
      children: "Log",
      get hrefValue() {
        return serverUrl + "/submit/joblog?uid=" + props.job.uid;
      },
      targetValue: "_blank",
      bgColor: "bg-gray-100",
      bgHoverColor: "hover:bg-gray-200"
    });
  }
  function dbComponent() {
    if (viewable()) {
      return createComponent(Button, {
        children: "DB",
        get hrefValue() {
          return serverUrl + "/submit/jobdb?uid=" + props.job.uid;
        },
        targetValue: "_blank",
        bgColor: "bg-gray-100",
        bgHoverColor: "hover:bg-gray-200"
      });
    } else {
      return _tmpl$$I();
    }
  }
  function statusComponent() {
    const status = props.job.status;
    if (status == "Finished") {
      return (() => {
        var _el$3 = _tmpl$2$a();
        insert(_el$3, () => props.job.status);
        return _el$3;
      })();
    } else if (status == "Aborted") {
      return (() => {
        var _el$4 = _tmpl$3$5();
        insert(_el$4, () => props.job.status);
        return _el$4;
      })();
    } else if (status == "Error") {
      return (() => {
        var _el$5 = _tmpl$4$4();
        insert(_el$5, () => props.job.status);
        return _el$5;
      })();
    } else {
      return (() => {
        var _el$6 = _tmpl$5$2();
        insert(_el$6, () => props.job.status);
        return _el$6;
      })();
    }
  }
  function inputComponent() {
    if (props.job.info_json.orig_input_fname) {
      return props.job.info_json.orig_input_fname.join(", ");
    } else {
      return "";
    }
  }
  function submitTime() {
    let d = new Date(props.job.info_json.submission_time);
    return ("" + d).split("GMT")[0];
  }
  function modulesComponent() {
    let modules = [];
    const info_json = props.job.info_json;
    if (!info_json) {
      return "";
    }
    const annotators = info_json.annotators;
    if (annotators) {
      for (const m of annotators) {
        if (m != "original_input") {
          modules.push(m);
        }
      }
    }
    const postaggs = info_json.postaggregators;
    if (postaggs) {
      for (const m of postaggs) {
        modules.push(m);
      }
    }
    return modules.join(", ");
  }
  checkNeedToFetchStatus();
  return (() => {
    var _el$7 = _tmpl$6$2(), _el$8 = _el$7.firstChild, _el$9 = _el$8.firstChild, _el$10 = _el$8.nextSibling, _el$11 = _el$10.nextSibling, _el$12 = _el$11.nextSibling, _el$13 = _el$12.nextSibling, _el$14 = _el$13.nextSibling, _el$15 = _el$14.nextSibling, _el$16 = _el$15.nextSibling, _el$17 = _el$16.nextSibling, _el$18 = _el$17.nextSibling;
    _el$8.$$click = toggleChecked;
    insert(_el$10, () => props.job.name);
    insert(_el$11, statusComponent);
    insert(_el$12, viewComponent);
    insert(_el$13, inputComponent);
    insert(_el$14, modulesComponent);
    insert(_el$15, submitTime);
    insert(_el$16, logComponent);
    insert(_el$17, dbComponent);
    insert(_el$18, () => props.job.info_json.note);
    createRenderEffect(() => _el$9.checked = props.job.checked);
    return _el$7;
  })();
}
delegateEvents(["click"]);

var _tmpl$$H = /* @__PURE__ */ template(`<div class="flex flex-col"><div class="relative shadow ring-1 ring-black ring-opacity-5 md:rounded-lg overflow-auto"><table class="table-fixed divide-y divide-gray-300"><thead class="table-header-group bg-gray-50 block"><tr><th scope=col class="relative w-12 px-6 sm:w-16 sm:px-8"><input type=checkbox class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"></th><th scope=col class="jobs-table-th min-w-[10rem]">Name</th><th scope=col class="jobs-table-th min-w-[5rem]">State</th><th scope=col class="jobs-table-th min-w-[5rem]">View</th><th scope=col class="jobs-table-th min-w-[20rem]">Input</th><th scope=col class="jobs-table-th min-w-[10rem]">Modules</th><th scope=col class="jobs-table-th min-w-[8rem]">Submitted</th><th scope=col class="jobs-table-th min-w-[5rem]">Log</th><th scope=col class="jobs-table-th min-w-[5rem]">DB</th><th scope=col class="jobs-table-th w-full">Note</th></tr></thead><tbody class="table-row-group divide-y divide-gray-200 bg-white block overflow-auto h-[36rem]">`);
function JobTable(props) {
  const [allMarksOn, setAllMarksOn] = createSignal(null);
  function toggleAllMarks() {
    if (allMarksOn() == true) {
      setAllMarksOn(false);
    } else if (allMarksOn() == null) {
      setAllMarksOn(true);
    } else if (allMarksOn() == false) {
      setAllMarksOn(true);
    }
    if (allMarksOn() == true) {
      for (const job of props.jobs) {
        props.changeJobChecked(job.uid, true);
      }
    } else if (allMarksOn() == false) {
      for (const job of props.jobs) {
        props.changeJobChecked(job.uid, false);
      }
    }
  }
  return (() => {
    var _el$ = _tmpl$$H(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild, _el$7 = _el$6.firstChild, _el$8 = _el$4.nextSibling;
    _el$7.$$click = toggleAllMarks;
    insert(_el$8, createComponent(For, {
      get each() {
        return props.jobs;
      },
      children: (job) => {
        return createComponent(JobRow, {
          job,
          get changeJobStatus() {
            return props.changeJobStatus;
          },
          get changeJobChecked() {
            return props.changeJobChecked;
          },
          setAllMarksOn
        });
      }
    }));
    createRenderEffect(() => _el$7.checked = allMarksOn());
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$G = /* @__PURE__ */ template(`<div class="relative z-10"aria-labelledby=modal-title role=dialog aria-modal=true><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"><div><div class=text-center><p class="text-sm text-gray-500">`);
function MsgDialog(props) {
  return (() => {
    var _el$ = _tmpl$$G(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild, _el$7 = _el$6.firstChild, _el$8 = _el$7.firstChild;
    insert(_el$8, () => props.msg);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.msg == null)));
    return _el$;
  })();
}

var _tmpl$$F = /* @__PURE__ */ template(`<div id=tab_jobs class="tabcontent px-6 mb-4"><div>`);
const {
  serverUrl: serverUrl$1,
  withCredentials
} = gvServer;
const {
  logged,
  setLogged
} = gvLogin;
const {
  multiuser
} = gvMultiuser;
const {
  email: email$1
} = gvEmail;
const {
  setAnnotators,
  setPostaggregators,
  setReporters
} = gvSubmitModules;
function TabJobs(props) {
  const {
    tabName
  } = gvTabName;
  const [jobs, setJobs] = createStore([]);
  const [pageno, setPageno] = createSignal(1);
  const [pagesize, setPagesize] = createSignal(10);
  const [msg, setMsg] = createSignal(null);
  createEffect(function() {
    if (multiuser() == false || logged() == true) {
      getJobs(pageno(), pagesize(), props.jobsTrigger);
    }
  });
  function changeJobStatus(uid, status) {
    setJobs((job) => job.uid == uid, "status", status);
  }
  function changeJobChecked(uid, checkedParam) {
    if (checkedParam == void 0) {
      setJobs((job) => job.uid == uid, "checked", (c) => !c);
    } else {
      setJobs((job) => job.uid == uid, "checked", checkedParam);
    }
  }
  function getJobs(pgno, pgsze, _) {
    axios.post(serverUrl$1 + "/submit/jobs", {
      pageno: pgno,
      pagesize: pgsze
    }, {
      withCredentials
    }).then(function(response) {
      if (response.status == "error") {
        setLogged(false);
        return;
      }
      const data = response.data;
      setJobs(data);
    }).catch(function(err) {
      console.error(err);
      if (err.response.status == 404) {
        setPageno(pageno() - 1);
      }
    });
  }
  function deleteJobs(checkedJobs, abortOnly) {
    const uids = checkedJobs.map((v) => v.uid);
    axios.post(serverUrl$1 + "/submit/delete_jobs", {
      uids,
      abort_only: abortOnly
    }, {
      withCredentials
    }).then(function() {
      props.setJobsTrigger(!props.jobsTrigger);
      setMsg(null);
    }).catch(function(err) {
      console.error(err);
      setMsg(null);
    });
  }
  function copyToSubmit(checkedJobs) {
    const uids = checkedJobs.map((v) => v.uid);
    if (uids.length == 0) {
      return;
    }
    const uid = uids[0];
    axios.post(serverUrl$1 + "/submit/jobinfo", {
      username: email$1(),
      uid
    }, {
      withCredentials
    }).then(function(response) {
      const data = response.data;
      const annotators = data.annotators;
      const postaggregators = data.postaggregators;
      var reporters = data.report_types;
      setAnnotators(reconcile({}));
      setPostaggregators(reconcile({}));
      setReporters(reconcile({}));
      for (const mn of annotators) {
        addModuleDown(mn);
      }
      for (const mn of postaggregators) {
        addModuleDown(mn);
      }
      for (const mn of reporters) {
        addModuleDown(mn);
      }
      setMsg(null);
    }).catch(function(err) {
      console.error(err);
      setMsg(null);
    });
  }
  function performJobAction(action) {
    const checkedJobs = jobs.filter((job) => job.checked);
    if (action == "delete") {
      setMsg("Deleting jobs...");
      deleteJobs(checkedJobs, false);
    } else if (action == "abort") {
      setMsg("Aborting jobs...");
      deleteJobs(checkedJobs, true);
    } else if (action == "copy_to_submit") {
      setMsg("Copying job setting to submit...");
      copyToSubmit(checkedJobs);
    }
  }
  return (() => {
    var _el$ = _tmpl$$F(), _el$2 = _el$.firstChild;
    insert(_el$2, createComponent(PageNavigation, {
      get pageno() {
        return pageno();
      },
      setPageno,
      get pagesize() {
        return pagesize();
      },
      setPagesize,
      get jobsTrigger() {
        return props.jobsTrigger;
      },
      get setJobsTrigger() {
        return props.setJobsTrigger;
      },
      performJobAction
    }), null);
    insert(_el$2, createComponent(JobTable, {
      jobs,
      changeJobStatus,
      changeJobChecked
    }), null);
    insert(_el$, createComponent(MsgDialog, {
      get msg() {
        return msg();
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(tabName() != "jobs")));
    return _el$;
  })();
}

const semver = /^[v^~<>=]*?(\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+))?(?:-([\da-z\-]+(?:\.[\da-z\-]+)*))?(?:\+[\da-z\-]+(?:\.[\da-z\-]+)*)?)?)?$/i;
const validateAndParse = (version) => {
    if (typeof version !== 'string') {
        throw new TypeError('Invalid argument expected string');
    }
    const match = version.match(semver);
    if (!match) {
        throw new Error(`Invalid argument not valid semver ('${version}' received)`);
    }
    match.shift();
    return match;
};
const isWildcard = (s) => s === '*' || s === 'x' || s === 'X';
const tryParse = (v) => {
    const n = parseInt(v, 10);
    return isNaN(n) ? v : n;
};
const forceType = (a, b) => typeof a !== typeof b ? [String(a), String(b)] : [a, b];
const compareStrings = (a, b) => {
    if (isWildcard(a) || isWildcard(b))
        return 0;
    const [ap, bp] = forceType(tryParse(a), tryParse(b));
    if (ap > bp)
        return 1;
    if (ap < bp)
        return -1;
    return 0;
};
const compareSegments = (a, b) => {
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
        const r = compareStrings(a[i] || '0', b[i] || '0');
        if (r !== 0)
            return r;
    }
    return 0;
};

/**
 * Compare [semver](https://semver.org/) version strings to find greater, equal or lesser.
 * This library supports the full semver specification, including comparing versions with different number of digits like `1.0.0`, `1.0`, `1`, and pre-release versions like `1.0.0-alpha`.
 * @param v1 - First version to compare
 * @param v2 - Second version to compare
 * @returns Numeric value compatible with the [Array.sort(fn) interface](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Parameters).
 */
const compareVersions = (v1, v2) => {
    // validate input and split into segments
    const n1 = validateAndParse(v1);
    const n2 = validateAndParse(v2);
    // pop off the patch
    const p1 = n1.pop();
    const p2 = n2.pop();
    // validate numbers
    const r = compareSegments(n1, n2);
    if (r !== 0)
        return r;
    // validate pre-release
    if (p1 && p2) {
        return compareSegments(p1.split('.'), p2.split('.'));
    }
    else if (p1 || p2) {
        return p1 ? -1 : 1;
    }
    return 0;
};

/**
 * Compare [semver](https://semver.org/) version strings using the specified operator.
 *
 * @param v1 First version to compare
 * @param v2 Second version to compare
 * @param operator Allowed arithmetic operator to use
 * @returns `true` if the comparison between the firstVersion and the secondVersion satisfies the operator, `false` otherwise.
 *
 * @example
 * ```
 * compare('10.1.8', '10.0.4', '>'); // return true
 * compare('10.0.1', '10.0.1', '='); // return true
 * compare('10.1.1', '10.2.2', '<'); // return true
 * compare('10.1.1', '10.2.2', '<='); // return true
 * compare('10.1.1', '10.2.2', '>='); // return false
 * ```
 */
const compare = (v1, v2, operator) => {
    // validate input operator
    assertValidOperator(operator);
    // since result of compareVersions can only be -1 or 0 or 1
    // a simple map can be used to replace switch
    const res = compareVersions(v1, v2);
    return operatorResMap[operator].includes(res);
};
const operatorResMap = {
    '>': [1],
    '>=': [0, 1],
    '=': [0],
    '<=': [-1, 0],
    '<': [-1],
    '!=': [-1, 1],
};
const allowedOperators = Object.keys(operatorResMap);
const assertValidOperator = (op) => {
    if (typeof op !== 'string') {
        throw new TypeError(`Invalid operator type, expected string but got ${typeof op}`);
    }
    if (allowedOperators.indexOf(op) === -1) {
        throw new Error(`Invalid operator, expected one of ${allowedOperators.join('|')}`);
    }
};

function createGlobalStates$2() {
  const [moduleInstallStates, setModuleInstallStates] = createStore({});
  const [updateAvailable, setUpdateAvailable] = createSignal(false);
  const [numUpdateAvailable, setNumUpdateAvailable] = createSignal(false);
  const {
    localModules
  } = gvLocalModules;
  const {
    remoteModules,
    getFilteredRemoteModules
  } = gvRemoteModules;
  const [initialLoaded, setInitialLoaded] = createSignal(false);
  const [refreshOn, setRefreshOn] = createSignal(false);
  createEffect(function() {
    if (!objectIsEmpty(localModules) && !objectIsEmpty(remoteModules) && localModules["__initial"] == void 0 && remoteModules["__initial"] == void 0 && initialLoaded() == false) {
      makeModuleInstallStates();
      setInitialLoaded(true);
      setRefreshOn(false);
    }
  });
  function makeModuleInstallStates() {
    let d = {};
    let n = 0;
    for (const moduleName in remoteModules) {
      if (moduleName in localModules) {
        d[moduleName] = {
          installed: true
        };
        const localModule = localModules[moduleName];
        const remoteModule = remoteModules[moduleName];
        const localVer = localModule.version;
        const remoteVer = remoteModule.latest_version;
        if (compare(remoteVer, localVer, ">") == true) {
          d[moduleName]["update_available"] = true;
          n += 1;
        } else {
          d[moduleName]["update_available"] = false;
        }
      } else {
        d[moduleName] = {
          installed: false,
          update_available: false
        };
      }
    }
    setModuleInstallStates(d);
    setNumUpdateAvailable(n);
    setUpdateAvailable(n > 0);
  }
  function getInstalledModules(searchText, selectedTyes, selectedTag, updateAvailableOnly, sort) {
    const l = [];
    if (moduleInstallStates == null || Object.keys(remoteModules).length == 0) {
      return l;
    }
    for (const moduleName of getFilteredRemoteModules(searchText, selectedTyes, selectedTag, sort)) {
      const m = moduleInstallStates[moduleName];
      let add = false;
      if (m.installed == true) {
        if (updateAvailableOnly == true) {
          if (m.update_available == true) {
            add = true;
          }
        } else {
          add = true;
        }
      }
      if (add == true) {
        l.push(moduleName);
      }
    }
    return l;
  }
  function getNotInstalledModules(searchText, selectedTypes, selectedTag, sort) {
    const l = [];
    if (moduleInstallStates == null || Object.keys(remoteModules).length == 0) {
      return l;
    }
    for (const moduleName of getFilteredRemoteModules(searchText, selectedTypes, selectedTag, sort)) {
      const m = moduleInstallStates[moduleName];
      if (m.installed != true) {
        l.push(moduleName);
      }
    }
    return l;
  }
  function installed(moduleName) {
    if (moduleInstallStates == null) {
      return false;
    }
    return moduleInstallStates[moduleName].installed;
  }
  function updateAvailableForModule(moduleName) {
    return moduleInstallStates[moduleName].update_available;
  }
  return {
    moduleInstallStates,
    setModuleInstallStates,
    makeModuleInstallStates,
    updateAvailable,
    numUpdateAvailable,
    getInstalledModules,
    getNotInstalledModules,
    installed,
    updateAvailableForModule,
    initialLoaded,
    setInitialLoaded,
    refreshOn,
    setRefreshOn
  };
}
const gvModuleInstallStates = createRoot(createGlobalStates$2);

function createGlobalStates$1() {
  const [showDetailCard, setShowDetailCard] = createSignal(null);
  const [detailModuleName, setDetailModuleName] = createSignal(null);
  return {
    showDetailCard,
    setShowDetailCard,
    detailModuleName,
    setDetailModuleName
  };
}
const gvDetailCardState = createRoot(createGlobalStates$1);

var _tmpl$$E = /* @__PURE__ */ template(`<img class="w-20 rounded-lg">`), _tmpl$2$9 = /* @__PURE__ */ template(`<p class="text-sm text-gray-500">`), _tmpl$3$4 = /* @__PURE__ */ template(`<span class="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">Installed`), _tmpl$4$3 = /* @__PURE__ */ template(`<span class="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">New`), _tmpl$5$1 = /* @__PURE__ */ template(`<span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800">Installed `), _tmpl$6$1 = /* @__PURE__ */ template(`<div class="absolute top-1 right-1">`), _tmpl$7 = /* @__PURE__ */ template(`<div class="group relative modulecard relative items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400 p-2 z-0 mb-2"><div class="absolute left-0 bottom-0 w-full p-2 cursor-default"style="background-color:rgba(68, 64, 60, 0.3);"><a class="relative remove-button text-sm h-8 inline-flex items-center rounded-md border border-gray-300 px-2 py-2 text-sm font-medium text-gray-500 cursor-pointer focus:z-20 bg-white hover:bg-gray-100">Remove</a></div><div class=flex><div class="w-24 h-24 mr-2 flex justify-center items-center cursor-help"></div><div class="min-w-0 flex-1"style=min-height:6rem;><p><span class="text-md font-semibold text-gray-700"></span><span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800"></span></p><p><span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800"></span><span class="ml-2 inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800"></span></p><p>`), _tmpl$8 = /* @__PURE__ */ template(`<span class=break-all>`);
function ModuleCard(props) {
  const [showX, setShowX] = createSignal(false);
  const {
    serverUrl
  } = gvServer;
  const {
    remoteModules
  } = gvRemoteModules;
  const {
    localModules
  } = gvLocalModules;
  const {
    installed,
    updateAvailableForModule
  } = gvModuleInstallStates;
  const {
    setShowDetailCard,
    setDetailModuleName
  } = gvDetailCardState;
  const moduleInfo = remoteModules[props.moduleName];
  const localModule = localModules[props.moduleName];
  const {
    addToInstallQueue,
    removeFromInstallQueue,
    inQueue,
    uninstallModule
  } = gvInstallQueue;
  const {
    admin
  } = gvLogin;
  const {
    multiuser
  } = gvMultiuser;
  function moduleInstalled() {
    return installed(props.moduleName);
  }
  function onClickLogo(_) {
    setDetailModuleName(props.moduleName);
    setShowDetailCard(true);
  }
  function uninstallOrRemoveFromInstallQueue() {
    if (inQueue(props.moduleName)) {
      removeFromInstallQueue(props.moduleName);
    } else if (moduleInstalled()) {
      uninstallModule(props.moduleName);
    }
  }
  return createComponent(Show, {
    when: moduleInfo != void 0,
    get children() {
      var _el$ = _tmpl$7(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$2.nextSibling, _el$5 = _el$4.firstChild, _el$7 = _el$5.nextSibling, _el$8 = _el$7.firstChild, _el$9 = _el$8.firstChild, _el$10 = _el$9.nextSibling, _el$12 = _el$8.nextSibling, _el$13 = _el$12.firstChild, _el$14 = _el$13.nextSibling, _el$15 = _el$12.nextSibling;
      _el$.addEventListener("mouseleave", (e) => setShowX(false, e));
      _el$.addEventListener("mouseenter", (e) => setShowX(true, e));
      insert(_el$2, createComponent(Button, {
        "class": "details-button w-full text-sm h-8 cursor-pointer",
        get classList() {
          return {
            hidden: props.cardType == "selected"
          };
        },
        bgColor: "bg-white",
        bgHoverColor: "hover:bg-gray-100",
        children: "Details"
      }), _el$3);
      _el$5.$$click = onClickLogo;
      insert(_el$5, createComponent(Show, {
        get when() {
          return moduleInfo.has_logo;
        },
        get fallback() {
          return (() => {
            var _el$21 = _tmpl$8();
            insert(_el$21, () => moduleInfo.title);
            return _el$21;
          })();
        },
        get children() {
          var _el$6 = _tmpl$$E();
          createRenderEffect(() => setAttribute(_el$6, "src", `${serverUrl}/store/remotelogo?module=${props.moduleName}&store=${moduleInfo.store}`));
          return _el$6;
        }
      }));
      insert(_el$9, () => moduleInfo.title);
      insert(_el$10, () => moduleInfo.latest_version);
      insert(_el$7, createComponent(Show, {
        get when() {
          return moduleInfo.conf;
        },
        get children() {
          var _el$11 = _tmpl$2$9();
          insert(_el$11, () => moduleInfo.conf.description);
          return _el$11;
        }
      }), _el$12);
      insert(_el$13, () => getSizeString(moduleInfo.size));
      insert(_el$14, () => moduleInfo.type);
      insert(_el$15, createComponent(Show, {
        get when() {
          return moduleInstalled();
        },
        get children() {
          return _tmpl$3$4();
        }
      }), null);
      insert(_el$15, createComponent(Show, {
        get when() {
          return updateAvailableForModule(props.moduleName);
        },
        get children() {
          return [_tmpl$4$3(), (() => {
            var _el$18 = _tmpl$5$1(); _el$18.firstChild;
            insert(_el$18, () => localModule.version, null);
            return _el$18;
          })()];
        }
      }), null);
      insert(_el$7, createComponent(Show, {
        get when() {
          return multiuser() == false || admin() == true;
        },
        get children() {
          var _el$20 = _tmpl$6$1();
          insert(_el$20, createComponent(Show, {
            get when() {
              return createMemo(() => !!(!moduleInstalled() || updateAvailableForModule(props.moduleName)))() && !inQueue(props.moduleName);
            },
            get children() {
              return createComponent(FiPlusCircle, {
                "class": "group-hover:block hidden cursor-pointer",
                color: "rgb(3 105 161)",
                size: "24",
                get onClick() {
                  return [addToInstallQueue, props.moduleName];
                }
              });
            }
          }), null);
          insert(_el$20, createComponent(Show, {
            get when() {
              return moduleInstalled() || inQueue(props.moduleName);
            },
            get children() {
              return createComponent(FiMinusCircle, {
                "class": "group-hover:block hidden cursor-pointer",
                color: "rgb(251 146 60)",
                size: "24",
                onClick: uninstallOrRemoveFromInstallQueue
              });
            }
          }), null);
          return _el$20;
        }
      }), null);
      createRenderEffect((_p$) => {
        var _v$ = moduleInfo.name, _v$2 = moduleInfo.kind, _v$3 = !!(!showX() || props.cardType != "selected"), _v$4 = !!(props.cardType != "selected");
        _v$ !== _p$.e && setAttribute(_el$, "name", _p$.e = _v$);
        _v$2 !== _p$.t && setAttribute(_el$, "kind", _p$.t = _v$2);
        _v$3 !== _p$.a && _el$2.classList.toggle("hidden", _p$.a = _v$3);
        _v$4 !== _p$.o && _el$3.classList.toggle("hidden", _p$.o = _v$4);
        return _p$;
      }, {
        e: void 0,
        t: void 0,
        a: void 0,
        o: void 0
      });
      return _el$;
    }
  });
}
delegateEvents(["click"]);

var _tmpl$$D = /* @__PURE__ */ template(`<div class="remote-module-filter-panel w-full mt-4 overflow-auto"><div class=store-filtered-modules><h1 class="text-4xl font-extrabold dark:text-white">Welcome to Module Store!</h1><p class="mb-6 text-lg font-normal text-gray-500 lg:text-xl dark:text-gray-400">Ultimate store of genomic variant analysis modules</p><div class="mt-4 text-base pr-4"><p><span class=font-bold>All</span> tab lists all available modules. In <span class=font-bold>Tags</span> tab, modules can be searched by the tags provided by the developers of modules. To quickly see all the modules already installed in the system, click <span class=font-bold>Installed</span> tab. When an updated version of any of installed modules is available, <span class=font-bold>Updates available</span> tab will appear.</p><p class=mt-2>To install a module, hover on the module card and click <span class=font-bold>Install</span>. Module installation is queued at the bottom. If you cancel the installation of a module, click the module card in the queue area.</p><p class=mt-2>Below are some of popular modules for you to get started!</p><p class=my-2>For cancer research:</p><p class="mt-4 mb-2">For clinical implications of variants:</p><p class="mt-4 mb-2">For allele frequencies in different populations:</p><p class="mt-4 mb-2">For actionable gene-drug associations:</p><p class="mt-4 mb-2">For the prediction of varinat effect:</p></div><p class=mt-2>Look around and happy annotating!`);
function ModuleFilterPanelHome(props) {
  const {
    installQueue
  } = gvInstallQueue;
  function getHeight() {
    if (installQueue.length > 0) {
      return "calc(100vh - 15rem)";
    } else {
      return "calc(100vh - 9rem)";
    }
  }
  return (() => {
    var _el$ = _tmpl$$D(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling, _el$5 = _el$4.nextSibling, _el$6 = _el$5.firstChild, _el$7 = _el$6.nextSibling, _el$8 = _el$7.nextSibling, _el$9 = _el$8.nextSibling, _el$10 = _el$9.nextSibling, _el$11 = _el$10.nextSibling, _el$12 = _el$11.nextSibling, _el$13 = _el$12.nextSibling;
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "civic",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$10);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "cosmic",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$10);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "oncokb",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$10);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "clinvar",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$11);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "grasp",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$11);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "gwas_catalog",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$11);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "omim",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$11);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "thousandgenomes",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$12);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "gnomad",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$12);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "pharmgkb",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), _el$13);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "cadd",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), null);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "fathmm",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), null);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "sift",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), null);
    insert(_el$5, createComponent(ModuleCard, {
      moduleName: "polyphen2",
      get addToInstallQueue() {
        return props.addToInstallQueue;
      }
    }), null);
    createRenderEffect((_p$) => {
      var _v$ = !!(props.filterCategory != "home"), _v$2 = getHeight();
      _v$ !== _p$.e && _el$.classList.toggle("hidden", _p$.e = _v$);
      _v$2 !== _p$.t && ((_p$.t = _v$2) != null ? _el$.style.setProperty("height", _v$2) : _el$.style.removeProperty("height"));
      return _p$;
    }, {
      e: void 0,
      t: void 0
    });
    return _el$;
  })();
}

var _tmpl$$C = /* @__PURE__ */ template(`<a href=# class="text-gray-600 block px-4 py-2 text-sm text-right hover:bg-gray-100 hover:text-gray-900"role=menuitem tabindex=-1 value="">`);
function SortOption(props) {
  function changeSort() {
    props.setSort(props.value);
    props.setShow(false);
  }
  return (() => {
    var _el$ = _tmpl$$C();
    _el$.$$click = changeSort;
    insert(_el$, () => props.title);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$B = /* @__PURE__ */ template(`<div class="option-list ease-in absolute right-0 z-10 mt-2 w-24 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"role=menu aria-orientation=vertical aria-labelledby=menu-button tabindex=-1><div class=py-1 role=none>`);
function SortSelect(props) {
  return (() => {
    var _el$ = _tmpl$$B(), _el$2 = _el$.firstChild;
    insert(_el$2, createComponent(SortOption, {
      value: "Name",
      title: "Name",
      get setSort() {
        return props.setSort;
      },
      get setShow() {
        return props.setShow;
      }
    }), null);
    insert(_el$2, createComponent(SortOption, {
      value: "Size",
      title: "Size",
      get setSort() {
        return props.setSort;
      },
      get setShow() {
        return props.setShow;
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !props.show));
    return _el$;
  })();
}

var _tmpl$$A = /* @__PURE__ */ template(`<div class="select-div relative inline-block text-left"value=""><div class="flex justify-center"><button name=sort type=button class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-1 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100"><span class=ml-2>Sort by `);
function SortPanel(props) {
  const [show, setShow] = createSignal(false);
  function toggleShowSelect(_) {
    setShow(!show());
  }
  return (() => {
    var _el$ = _tmpl$$A(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild; _el$4.firstChild;
    _el$3.$$click = toggleShowSelect;
    insert(_el$4, () => props.sort, null);
    insert(_el$3, createComponent(HiOutlineChevronDown, {
      "class": "ml-2 h-5 w-5"
    }), null);
    insert(_el$, createComponent(SortSelect, {
      get show() {
        return show();
      },
      get setSort() {
        return props.setSort;
      },
      setShow
    }), null);
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$z = /* @__PURE__ */ template(`<button type=button class="graybutton inline-flex items-center rounded border border-transparent bg-gray-50 px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-300 focus:outline-none drop-shadow-lg">`), _tmpl$2$8 = /* @__PURE__ */ template(`<div class="flex mb-2"><label for=search class=sr-only>Search</label><input type=text name=search class="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm mr-2"placeholder=Search><div class="relative flex text-xs font-medium text-gray-700 shadow-sm items-center"><div class="flex items-center mr-4">`);
function ModuleSearchPanel(props) {
  function updateSearchText(evt) {
    props.setSearchText(evt.target.value);
  }
  function onChangeUninstalledOnly(_) {
    props.setNotInstalledOnly(!props.notInstalledOnly);
  }
  function getTitle() {
    if (props.notInstalledOnly) {
      return "Click to show all modules";
    } else {
      return "Click to show uninstalled modules only";
    }
  }
  return (() => {
    var _el$ = _tmpl$2$8(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.nextSibling, _el$5 = _el$4.firstChild;
    _el$3.$$keyup = updateSearchText;
    insert(_el$5, createComponent(Show, {
      get when() {
        return props.showUninstalledOnly;
      },
      get children() {
        var _el$6 = _tmpl$$z();
        _el$6.$$click = onChangeUninstalledOnly;
        insert(_el$6, createComponent(Show, {
          get when() {
            return props.notInstalledOnly;
          },
          get fallback() {
            return createComponent(BsBox, {
              size: 22
            });
          },
          get children() {
            return createComponent(BsBoxFill, {
              size: 22
            });
          }
        }));
        createRenderEffect((_p$) => {
          var _v$ = getTitle(), _v$2 = !!props.notInstalledOnly;
          _v$ !== _p$.e && setAttribute(_el$6, "title", _p$.e = _v$);
          _v$2 !== _p$.t && _el$6.classList.toggle("checked", _p$.t = _v$2);
          return _p$;
        }, {
          e: void 0,
          t: void 0
        });
        return _el$6;
      }
    }));
    insert(_el$4, createComponent(SortPanel, {
      get sort() {
        return props.sort;
      },
      get setSort() {
        return props.setSort;
      }
    }), null);
    createRenderEffect(() => _el$3.value = props.searchText);
    return _el$;
  })();
}
delegateEvents(["keyup", "click"]);

var _tmpl$$y = /* @__PURE__ */ template(`<div class="flex items-center justify-center"><p class="text-lg text-gray-700">No module met the criteria.`), _tmpl$2$7 = /* @__PURE__ */ template(`<div>`);
function ModuleDisplayPanel(props) {
  const {
    installQueue
  } = gvInstallQueue;
  function getHeight() {
    if (installQueue.length > 0) {
      return "calc(100vh - 19rem)";
    } else {
      return "calc(100vh - 9rem)";
    }
  }
  function noModuleSection() {
    return _tmpl$$y();
  }
  return (() => {
    var _el$2 = _tmpl$2$7();
    insert(_el$2, createComponent(Show, {
      get when() {
        return props.moduleNames && props.moduleNames.length > 0;
      },
      get fallback() {
        return noModuleSection();
      },
      get children() {
        return createComponent(For, {
          get each() {
            return props.moduleNames;
          },
          children: (moduleName) => createComponent(Switch, {
            get children() {
              return [createComponent(Match, {
                get when() {
                  return props.side == "local";
                },
                get children() {
                  return createComponent(ModuleCard$1, {
                    moduleName,
                    get annotators() {
                      return props.annotators;
                    },
                    get setAnnotators() {
                      return props.setAnnotators;
                    },
                    get postaggregators() {
                      return props.postaggregators;
                    },
                    get setPostaggregators() {
                      return props.setPostaggregators;
                    }
                  });
                }
              }), createComponent(Match, {
                get when() {
                  return props.side == "remote";
                },
                get children() {
                  return createComponent(ModuleCard, {
                    moduleName
                  });
                }
              })];
            }
          })
        });
      }
    }));
    createRenderEffect((_p$) => {
      var _v$ = `store-filtered-modules pr-4 overflow-auto grid grid-cols-${props.noCols}`, _v$2 = getHeight();
      _v$ !== _p$.e && className(_el$2, _p$.e = _v$);
      _v$2 !== _p$.t && ((_p$.t = _v$2) != null ? _el$2.style.setProperty("height", _v$2) : _el$2.style.removeProperty("height"));
      return _p$;
    }, {
      e: void 0,
      t: void 0
    });
    return _el$2;
  })();
}

var _tmpl$$x = /* @__PURE__ */ template(`<div class="remote-module-filter-panel w-full mt-4 overflow-auto">`);
const {
  getFilteredRemoteModules: getFilteredRemoteModules$1
} = gvRemoteModules;
const {
  getNotInstalledModules: getNotInstalledModules$1
} = gvModuleInstallStates;
function ModuleFilterPanelAll(props) {
  const [searchText, setSearchText] = createSignal(null);
  const [selectedTypes, _] = createSignal([]);
  const [notInstalledOnly, setNotInstalledOnly] = createSignal(false);
  const [sort, setSort] = createSignal("Name");
  const [moduleNames, setModuleNames] = createSignal([]);
  createEffect(function() {
    if (notInstalledOnly() == true) {
      setModuleNames(getNotInstalledModules$1(searchText(), selectedTypes(), null, sort()));
    } else {
      setModuleNames(getFilteredRemoteModules$1(searchText(), selectedTypes(), null, sort()));
    }
  });
  return (() => {
    var _el$ = _tmpl$$x();
    insert(_el$, createComponent(ModuleSearchPanel, {
      kind: "all",
      side: "remote",
      get searchText() {
        return searchText();
      },
      setSearchText,
      get notInstalledOnly() {
        return notInstalledOnly();
      },
      setNotInstalledOnly,
      showUninstalledOnly: true,
      get sort() {
        return sort();
      },
      setSort
    }), null);
    insert(_el$, createComponent(ModuleDisplayPanel, {
      kind: "all",
      side: "remote",
      noCols: 1,
      get moduleNames() {
        return moduleNames();
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.filterCategory != "all")));
    return _el$;
  })();
}

var _tmpl$$w = /* @__PURE__ */ template(`<div class="remote-module-filter-panel w-full mt-4 overflow-auto flex"><div class="store-filtered-modules col-span-1 flex flex-col justify-leading pl-1 overflow-y-auto w-[20rem]"></div><div class="ml-8 w-full">`);
const {
  getFilteredRemoteModules,
  remoteTags
} = gvRemoteModules;
const {
  getNotInstalledModules
} = gvModuleInstallStates;
function ModuleFilterPanelTags(props) {
  const [searchText, setSearchText] = createSignal(null);
  const [selectedTypes, setSelectedTypes] = createSignal([]);
  const [selectedTag, setSelectedTag] = createSignal("clinical relevance");
  const [sort, setSort] = createSignal("Name");
  const [notInstalledOnly, setNotInstalledOnly] = createSignal(false);
  const [moduleNames, setModuleNames] = createSignal([]);
  createEffect(function() {
    if (notInstalledOnly() == true) {
      setModuleNames(getNotInstalledModules(searchText(), selectedTypes(), selectedTag(), sort()));
    } else {
      setModuleNames(getFilteredRemoteModules(searchText(), selectedTypes(), selectedTag(), sort()));
    }
  });
  return (() => {
    var _el$ = _tmpl$$w(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling;
    insert(_el$2, createComponent(For, {
      get each() {
        return Object.keys(remoteTags()).sort();
      },
      children: (tag) => createComponent(AnalysisModuleFilterPanelTagItem, {
        value: tag,
        get title() {
          return remoteTags()[tag];
        },
        get selectedTag() {
          return selectedTag();
        },
        setSelectedTag
      })
    }));
    insert(_el$3, createComponent(ModuleSearchPanel, {
      kind: "all",
      side: "remote",
      get searchText() {
        return searchText();
      },
      setSearchText,
      get notInstalledOnly() {
        return notInstalledOnly();
      },
      setNotInstalledOnly,
      showUninstalledOnly: true,
      get sort() {
        return sort();
      },
      setSort
    }), null);
    insert(_el$3, createComponent(ModuleDisplayPanel, {
      kind: "all",
      side: "remote",
      noCols: 1,
      get moduleNames() {
        return moduleNames();
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.filterCategory != "tags")));
    return _el$;
  })();
}

var _tmpl$$v = /* @__PURE__ */ template(`<div class="remote-module-filter-panel w-full mt-4 overflow-auto">`);
const {
  getInstalledModules: getInstalledModules$1
} = gvModuleInstallStates;
function ModuleFilterPanelInstalled(props) {
  const [searchText, setSearchText] = createSignal(null);
  const [selectedTypes, _] = createSignal([]);
  const [sort, setSort] = createSignal("Name");
  const [moduleNames, setModuleNames] = createSignal([]);
  createEffect(function() {
    setModuleNames(getInstalledModules$1(searchText(), selectedTypes(), null, null, sort()));
  });
  return (() => {
    var _el$ = _tmpl$$v();
    insert(_el$, createComponent(ModuleSearchPanel, {
      kind: "install",
      side: "remote",
      get searchText() {
        return searchText();
      },
      setSearchText,
      get sort() {
        return sort();
      },
      setSort
    }), null);
    insert(_el$, createComponent(ModuleDisplayPanel, {
      kind: "install",
      side: "remote",
      noCols: 1,
      get moduleNames() {
        return moduleNames();
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.filterCategory != "installed")));
    return _el$;
  })();
}

var _tmpl$$u = /* @__PURE__ */ template(`<div class="remote-module-filter-panel w-full mt-4 overflow-auto">`);
const {
  getInstalledModules
} = gvModuleInstallStates;
function ModuleFilterPanelUpdate(props) {
  const [searchText, setSearchText] = createSignal(null);
  const [selectedTypes, _] = createSignal([]);
  const [sort, setSort] = createSignal("Name");
  const [moduleNames, setModuleNames] = createSignal([]);
  createEffect(function() {
    setModuleNames(getInstalledModules(searchText(), selectedTypes(), null, true, sort()));
  });
  return (() => {
    var _el$ = _tmpl$$u();
    insert(_el$, createComponent(ModuleSearchPanel, {
      kind: "update",
      side: "remote",
      get searchText() {
        return searchText();
      },
      setSearchText,
      get sort() {
        return sort();
      },
      setSort
    }), null);
    insert(_el$, createComponent(ModuleDisplayPanel, {
      kind: "update",
      side: "remote",
      noCols: 1,
      get moduleNames() {
        return moduleNames();
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.filterCategory != "update")));
    return _el$;
  })();
}

var _tmpl$$t = /* @__PURE__ */ template(`<div class="flex-inline mr-2"><svg xmlns=http://www.w3.org/2000/svg fill=none viewBox="0 0 24 24"><circle class=opacity-25 cx=12 cy=12 r=10 stroke-width=4></circle><path class=opacity-75 fill=currentColor d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">`);
function InlineSpinner(props) {
  let width = props.width || 5;
  let height = props.height || 5;
  let stroke = props.stroke || "currentColor";
  return (() => {
    var _el$ = _tmpl$$t(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild;
    setAttribute(_el$2, "class", `hide animate-spin ml-1 h-${width} w-${height} text-white m-auto`);
    setAttribute(_el$3, "stroke", stroke);
    createRenderEffect(() => _el$2.classList.toggle("hidden", !props.show));
    return _el$;
  })();
}

var _tmpl$$s = /* @__PURE__ */ template(`<button type=button class="ml-4 inline-flex items-center px-5 py-2.5 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Updates available<span class="inline-flex justify-center items-center ml-2 w-4 h-4 text-xs font-semibold text-blue-800 bg-blue-200 rounded-full">`), _tmpl$2$6 = /* @__PURE__ */ template(`<div class="analysis-module-filter-wrapper col-span-7 grow"><div class=w-full><div class="inline-flex rounded-md shadow-sm"role=group><button type=button class="ml-4 inline-flex items-center px-5 py-2.5 text-sm font-medium text-center text-white bg-gray-500 rounded-lg hover:bg-gray-600 focus:ring-4 focus:outline-none focus:ring-gray-300 dark:bg-gray-600 dark:hover:bg-gray-700 dark:focus:ring-gray-800 min-w-[6rem] place-content-center">`);
const {
  updateAvailable,
  numUpdateAvailable,
  setInitialLoaded,
  refreshOn,
  setRefreshOn
} = gvModuleInstallStates;
function RemoteModuleFilterWrapper(props) {
  const [filterCategory, setFilterCategory] = createSignal("home");
  const {
    setLocalModules,
    loadAllLocalModules
  } = gvLocalModules;
  const {
    setRemoteModules,
    loadAllRemoteModules
  } = gvRemoteModules;
  function refreshUpdatesAvailable() {
    setRefreshOn(true);
    setLocalModules(reconcile({}));
    setRemoteModules(reconcile({}));
    setInitialLoaded(false);
    loadAllLocalModules("true");
    loadAllRemoteModules("true");
  }
  return (() => {
    var _el$ = _tmpl$2$6(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild;
    insert(_el$3, createComponent(ModuleFilterCategoryButton, {
      value: "home",
      title: "Home",
      pos: "left",
      get filterCategory() {
        return filterCategory();
      },
      setFilterCategory
    }), _el$4);
    insert(_el$3, createComponent(ModuleFilterCategoryButton, {
      value: "all",
      title: "All",
      pos: "center",
      get filterCategory() {
        return filterCategory();
      },
      setFilterCategory
    }), _el$4);
    insert(_el$3, createComponent(ModuleFilterCategoryButton, {
      value: "tags",
      title: "Tags",
      pos: "center",
      get filterCategory() {
        return filterCategory();
      },
      setFilterCategory
    }), _el$4);
    insert(_el$3, createComponent(ModuleFilterCategoryButton, {
      value: "installed",
      title: "Installed",
      pos: "right",
      get filterCategory() {
        return filterCategory();
      },
      setFilterCategory
    }), _el$4);
    _el$4.$$click = refreshUpdatesAvailable;
    insert(_el$4, createComponent(Show, {
      get when() {
        return refreshOn() == true;
      },
      fallback: "Refresh",
      get children() {
        return createComponent(InlineSpinner, {
          show: true,
          width: 5,
          height: 5,
          stroke: "#000000"
        });
      }
    }));
    insert(_el$3, createComponent(Show, {
      get when() {
        return updateAvailable() == true;
      },
      get children() {
        var _el$5 = _tmpl$$s(), _el$6 = _el$5.firstChild, _el$7 = _el$6.nextSibling;
        _el$5.$$click = setFilterCategory;
        _el$5.$$clickData = "update";
        insert(_el$7, numUpdateAvailable);
        return _el$5;
      }
    }), null);
    insert(_el$, createComponent(ModuleFilterPanelHome, {
      get modules() {
        return props.modules;
      },
      get filterCategory() {
        return filterCategory();
      }
    }), null);
    insert(_el$, createComponent(ModuleFilterPanelAll, {
      get modules() {
        return props.modules;
      },
      get filterCategory() {
        return filterCategory();
      }
    }), null);
    insert(_el$, createComponent(ModuleFilterPanelTags, {
      get modules() {
        return props.modules;
      },
      get filterCategory() {
        return filterCategory();
      }
    }), null);
    insert(_el$, createComponent(ModuleFilterPanelInstalled, {
      get modules() {
        return props.modules;
      },
      get filterCategory() {
        return filterCategory();
      }
    }), null);
    insert(_el$, createComponent(ModuleFilterPanelUpdate, {
      get modules() {
        return props.modules;
      },
      get filterCategory() {
        return filterCategory();
      }
    }), null);
    createRenderEffect(() => _el$4.disabled = refreshOn());
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$r = /* @__PURE__ */ template(`<img class="w-24 rounded-lg">`), _tmpl$2$5 = /* @__PURE__ */ template(`<div class="group-hover:block absolute z-10 w-[6.5rem] h-[6.5rem]"><div class="install_pie absolute top-[1.25rem] left-[1.25rem]">`), _tmpl$3$3 = /* @__PURE__ */ template(`<div class="relative modulecard items-center rounded-lg border border-gray-300 bg-white shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400 flex items-center group h-[6.5rem] w-[6.5rem] shrink-0"><div class="flex justify-center items-center h-full w-full"></div><div class="group-hover:block hidden bg-gray-900/60 absolute z-20 w-full h-full">`), _tmpl$4$2 = /* @__PURE__ */ template(`<span class=break-all>`);
const {
  serverUrl
} = gvServer;
const {
  remoteModules
} = gvRemoteModules;
const {
  removeFromInstallQueue
} = gvInstallQueue;
function InstallQueueModuleCard(props) {
  const moduleInfo = remoteModules[props.moduleName];
  function onClickX() {
    removeFromInstallQueue(props.moduleName);
    props.setTooltipShow(false);
  }
  function onMouseEnter(evt) {
    const card = evt.target.closest(".modulecard");
    let rect = card.getBoundingClientRect();
    let left = rect.left;
    if (rect.left > window.innerWidth / 2) {
      left = left - 280;
    }
    props.setTooltipText(props.moduleName);
    props.setTooltipTop(card.offsetTop - 80);
    props.setTooltipLeft(left);
    props.setTooltipShow(true);
  }
  function onMouseLeave() {
    props.setTooltipShow(false);
  }
  return (() => {
    var _el$ = _tmpl$3$3(), _el$2 = _el$.firstChild, _el$4 = _el$2.nextSibling;
    insert(_el$2, createComponent(Show, {
      get when() {
        return moduleInfo.has_logo;
      },
      get fallback() {
        return (() => {
          var _el$7 = _tmpl$4$2();
          insert(_el$7, () => moduleInfo.title);
          return _el$7;
        })();
      },
      get children() {
        var _el$3 = _tmpl$$r();
        createRenderEffect(() => setAttribute(_el$3, "src", `${serverUrl}/store/remotelogo?module=${props.moduleName}&store=${moduleInfo.store}`));
        return _el$3;
      }
    }));
    _el$4.addEventListener("mouseleave", onMouseLeave);
    _el$4.addEventListener("mouseenter", onMouseEnter);
    insert(_el$4, createComponent(HiOutlineXCircle, {
      color: "#ffffff",
      size: 48,
      "class": "m-auto cursor-pointer",
      style: "height: 6rem;",
      onClick: onClickX
    }));
    insert(_el$, createComponent(Show, {
      get when() {
        return props.state && props.state.progress > 0;
      },
      get children() {
        var _el$5 = _tmpl$2$5(), _el$6 = _el$5.firstChild;
        _el$6.style.setProperty("--b", "10px");
        _el$6.style.setProperty("--c", "rgb(3 105 161)");
        createRenderEffect(() => props.state.progress != null ? _el$6.style.setProperty("--p", props.state.progress) : _el$6.style.removeProperty("--p"));
        return _el$5;
      }
    }), null);
    createRenderEffect((_p$) => {
      var _v$ = moduleInfo && moduleInfo.name, _v$2 = moduleInfo && moduleInfo.kind;
      _v$ !== _p$.e && setAttribute(_el$, "name", _p$.e = _v$);
      _v$2 !== _p$.t && setAttribute(_el$, "kind", _p$.t = _v$2);
      return _p$;
    }, {
      e: void 0,
      t: void 0
    });
    return _el$;
  })();
}

var _tmpl$2$4 = /* @__PURE__ */ template(`<div class="h-[8rem] px-2 flex items-center rounded-lg border border-gray-300 bg-white shadow-sm"><div class="flex overflow-auto w-full">`);
const {
  installQueue,
  installState
} = gvInstallQueue;
function InstallQueuePanel(props) {
  return createComponent(Show, {
    get when() {
      return installQueue.length > 0;
    },
    get children() {
      var _el$2 = _tmpl$2$4(), _el$3 = _el$2.firstChild;
      insert(_el$3, createComponent(For, {
        each: installQueue,
        children: (moduleName) => createComponent(InstallQueueModuleCard, {
          moduleName,
          get state() {
            return installState[moduleName];
          },
          get setTooltipText() {
            return props.setTooltipText;
          },
          get setTooltipShow() {
            return props.setTooltipShow;
          },
          get setTooltipTop() {
            return props.setTooltipTop;
          },
          get setTooltipLeft() {
            return props.setTooltipLeft;
          }
        })
      }));
      createRenderEffect(() => _el$2.classList.toggle("border-blue-500", !!(installQueue.length > 0)));
      return _el$2;
    }
  });
}

var _tmpl$$q = /* @__PURE__ */ template(`<div class="h-64 w-64 m-auto flex"><div class="m-auto flex flex-col"><div class=mb-4>Loading store modules...</div><div class=m-auto>`);
function LoadingPanel() {
  return (() => {
    var _el$ = _tmpl$$q(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling;
    insert(_el$4, createComponent(InlineSpinner, {
      show: true,
      width: 20,
      height: 20,
      stroke: "#000000"
    }));
    return _el$;
  })();
}

var _tmpl$$p = /* @__PURE__ */ template(`<div role=tooltip class="absolute inline-block z-10 p-4 text-sm font-medium text-gray-700 bg-gray-200 border border-gray-200 rounded-lg shadow-lg transition-opacity duration-300 tooltip dark:bg-gray-700 opacity-0 w-[24rem] break-word"><div class=tooltip-arrow data-popper-arrow>`);
function Tooltip(props) {
  let tooltip;
  return (() => {
    var _el$ = _tmpl$$p(), _el$2 = _el$.firstChild;
    var _ref$ = tooltip;
    typeof _ref$ === "function" ? use(_ref$, _el$) : tooltip = _el$;
    insert(_el$, () => props.text, _el$2);
    createRenderEffect((_p$) => {
      var _v$ = !!props.tooltipShow, _v$2 = !!props.tooltipShow, _v$3 = props.tooltipTop + "px", _v$4 = props.tooltipLeft + "px";
      _v$ !== _p$.e && _el$.classList.toggle("opacity-100", _p$.e = _v$);
      _v$2 !== _p$.t && _el$.classList.toggle("visible", _p$.t = _v$2);
      _v$3 !== _p$.a && ((_p$.a = _v$3) != null ? _el$.style.setProperty("top", _v$3) : _el$.style.removeProperty("top"));
      _v$4 !== _p$.o && ((_p$.o = _v$4) != null ? _el$.style.setProperty("left", _v$4) : _el$.style.removeProperty("left"));
      return _p$;
    }, {
      e: void 0,
      t: void 0,
      a: void 0,
      o: void 0
    });
    return _el$;
  })();
}

var _tmpl$$o = /* @__PURE__ */ template(`<div id=tab-store class="tabcontent p-4 snap-y snap-mandatory h-screen overflow-y-auto flex flex-col">`);
function TabStore() {
  const {
    remoteModules
  } = gvRemoteModules;
  const {
    tabName
  } = gvTabName;
  const {
    addToInstallQueue
  } = gvInstallQueue;
  const {
    moduleInstallStates
  } = gvModuleInstallStates;
  const [tooltipText, setTooltipText] = createSignal(null);
  const [tooltipShow, setTooltipShow] = createSignal(false);
  const [tooltipTop, setTooltipTop] = createSignal(0);
  const [tooltipLeft, setTooltipLeft] = createSignal(null);
  return (() => {
    var _el$ = _tmpl$$o();
    insert(_el$, createComponent(Show, {
      get when() {
        return !objectIsEmpty(moduleInstallStates);
      },
      get fallback() {
        return createComponent(LoadingPanel, {});
      },
      get children() {
        return [createComponent(RemoteModuleFilterWrapper, {
          addToInstallQueue,
          modules: remoteModules
        }), createComponent(InstallQueuePanel, {
          setTooltipText,
          setTooltipShow,
          setTooltipTop,
          setTooltipLeft
        }), createComponent(Tooltip, {
          get text() {
            return tooltipText();
          },
          get tooltipShow() {
            return tooltipShow();
          },
          get tooltipTop() {
            return tooltipTop();
          },
          get tooltipLeft() {
            return tooltipLeft();
          }
        })];
      }
    }));
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(tabName() != "store")));
    return _el$;
  })();
}

function createGlobalStates() {
  const [users, setUsers] = createSignal(null);
  const {
    serverUrl,
    withCredentials
  } = gvServer;
  const {
    admin
  } = gvLogin;
  createEffect(function() {
    if (admin() == true) {
      loadAllUsers();
    }
  });
  function loadAllUsers() {
    axios.get(serverUrl + "/server/users", {
      withCredentials
    }).then(function(res) {
      const l = [];
      for (const data of res.data) {
        if (data.email != "default") {
          l.push(data);
        }
      }
      setUsers(l);
    }).catch(function(err) {
      console.error(err);
      handleError(err);
    });
  }
  function makeAdmin(email) {
    axios.get(serverUrl + "/server/makeadmin", {
      params: {
        email
      },
      withCredentials
    }).then(function(_) {
      loadAllUsers();
    }).catch(function(err) {
      handleError(err);
    });
  }
  function removeAdmin(email) {
    axios.get(serverUrl + "/server/removeadmin", {
      params: {
        email
      },
      withCredentials
    }).then(function(_) {
      loadAllUsers();
    }).catch(function(err) {
      handleError(err);
    });
  }
  function removeUser(email) {
    axios.get(serverUrl + "/server/removeuser", {
      params: {
        email
      },
      withCredentials
    }).then(function(_) {
      loadAllUsers();
    }).catch(function(err) {
      handleError(err);
    });
  }
  return {
    users,
    setUsers,
    loadAllUsers,
    makeAdmin,
    removeAdmin,
    removeUser
  };
}
const gvUsers = createRoot(createGlobalStates);

var _tmpl$$n = /* @__PURE__ */ template(`<div class=mt-4><h3 class="text-lg font-semibold">Users</h3><div class="rounded-lg bg-white shadow mt-2"><table class="w-full text-sm text-left text-gray-500 dark:text-gray-400"><thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"><tr><th scope=col class="py-3 px-6">Email</th><th scope=col class="py-3 px-6">Role</th></tr></thead><tbody>`), _tmpl$2$3 = /* @__PURE__ */ template(`<span class="ml-2 inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">Admin`), _tmpl$3$2 = /* @__PURE__ */ template(`<button type=button class="invisible inline-flex items-center rounded border border-transparent bg-blue-600 px-2.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-4 group-hover:visible">Remove admin`), _tmpl$4$1 = /* @__PURE__ */ template(`<button type=button class="invisible inline-flex items-center rounded border border-transparent bg-blue-600 px-2.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-4 group-hover:visible">Remove user`), _tmpl$5 = /* @__PURE__ */ template(`<tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 group"><td scope=row class="py-4 px-6 font-medium text-gray-900 whitespace-nowrap dark:text-white"></td><td class="py-4 px-6">`), _tmpl$6 = /* @__PURE__ */ template(`<button type=button class="invisible inline-flex items-center rounded border border-transparent bg-blue-600 px-2.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-4 group-hover:visible">Make admin`);
function UserManagement() {
  const {
    users,
    makeAdmin,
    removeAdmin,
    removeUser
  } = gvUsers;
  return (() => {
    var _el$ = _tmpl$$n(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.nextSibling;
    insert(_el$6, createComponent(For, {
      get each() {
        return users();
      },
      children: (user) => (() => {
        var _el$7 = _tmpl$5(), _el$8 = _el$7.firstChild, _el$10 = _el$8.nextSibling;
        insert(_el$8, () => user.email, null);
        insert(_el$8, createComponent(Show, {
          get when() {
            return user.role == "admin";
          },
          get children() {
            return _tmpl$2$3();
          }
        }), null);
        insert(_el$10, () => user.role, null);
        insert(_el$10, createComponent(Show, {
          get when() {
            return user.role == "admin";
          },
          get fallback() {
            return (() => {
              var _el$13 = _tmpl$6();
              _el$13.$$click = makeAdmin;
              _el$13.$$clickData = user.email;
              return _el$13;
            })();
          },
          get children() {
            var _el$11 = _tmpl$3$2();
            _el$11.$$click = removeAdmin;
            _el$11.$$clickData = user.email;
            return _el$11;
          }
        }), null);
        insert(_el$10, createComponent(Show, {
          get when() {
            return user.role != "admin";
          },
          get children() {
            var _el$12 = _tmpl$4$1();
            _el$12.$$click = removeUser;
            _el$12.$$clickData = user.email;
            return _el$12;
          }
        }), null);
        return _el$7;
      })()
    }));
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$m = /* @__PURE__ */ template(`<div class=""><h3 class="text-lg font-semibold mt-8 mb-2">Log</h3><button type=button class="inline-flex items-center px-5 py-2.5 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Download system log`);
function LogPanel() {
  const {
    serverUrl
  } = gvServer;
  function getSystemLog() {
    axios({
      url: serverUrl + "/submit/systemlog",
      method: "GET",
      responseType: "blob"
    }).then(function(res) {
      let a = document.createElement("a");
      a.href = window.URL.createObjectURL(new Blob([res.data], {
        type: "text/plain"
      }));
      a.download = res.headers["content-disposition"].split("=")[1];
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }).catch(function(err) {
      console.error(err);
    });
  }
  return (() => {
    var _el$ = _tmpl$$m(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling;
    _el$3.$$click = getSystemLog;
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$l = /* @__PURE__ */ template(`<div id=tab_system class=tabcontent><div class=p-4>`);
function TabSystem() {
  const {
    tabName
  } = gvTabName;
  const {
    multiuser
  } = gvMultiuser;
  return (() => {
    var _el$ = _tmpl$$l(), _el$2 = _el$.firstChild;
    insert(_el$2, createComponent(Show, {
      get when() {
        return multiuser() == true;
      },
      get children() {
        return createComponent(UserManagement, {});
      }
    }), null);
    insert(_el$2, createComponent(LogPanel, {}), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(tabName() != "system")));
    return _el$;
  })();
}

var _tmpl$$k = /* @__PURE__ */ template(`<div id=tab_account class="tabcontent p-4"><p class=text-gray-600></p><button type=button class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 text-sm font-medium leading-4 text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 mt-2">Logout`);
const {
  tabName
} = gvTabName;
const {
  email
} = gvEmail;
const {
  auth
} = gvFirebase;
function TabAccount() {
  function logout() {
    signOut(auth()).catch(function(err) {
      console.error(err);
    });
  }
  return (() => {
    var _el$ = _tmpl$$k(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling;
    insert(_el$2, email);
    _el$3.$$click = logout;
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(tabName() != "account")));
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$j = /* @__PURE__ */ template(`<main class="h-screen md:pl-36 flex flex-col flex-1"><div>`);
function Content() {
  const [jobsTrigger, setJobsTrigger] = createSignal(false);
  const {
    multiuser
  } = gvMultiuser;
  const {
    admin
  } = gvLogin;
  return (() => {
    var _el$ = _tmpl$$j(), _el$2 = _el$.firstChild;
    insert(_el$2, createComponent(TabHome, {}), null);
    insert(_el$2, createComponent(TabSubmit, {
      get jobsTrigger() {
        return jobsTrigger();
      },
      setJobsTrigger
    }), null);
    insert(_el$2, createComponent(TabJobs, {
      get jobsTrigger() {
        return jobsTrigger();
      },
      setJobsTrigger
    }), null);
    insert(_el$2, createComponent(TabStore, {}), null);
    insert(_el$2, createComponent(Show, {
      get when() {
        return multiuser() == false || admin() == true;
      },
      get children() {
        return createComponent(TabSystem, {});
      }
    }), null);
    insert(_el$2, createComponent(Show, {
      get when() {
        return multiuser() == true;
      },
      get children() {
        return createComponent(TabAccount, {});
      }
    }), null);
    return _el$;
  })();
}

/**
 * marked v12.0.2 - a markdown parser
 * Copyright (c) 2011-2024, Christopher Jeffrey. (MIT Licensed)
 * https://github.com/markedjs/marked
 */

/**
 * DO NOT EDIT THIS FILE
 * The code in this file is generated from files in ./src/
 */

/**
 * Gets the original marked default options.
 */
function _getDefaults() {
    return {
        async: false,
        breaks: false,
        extensions: null,
        gfm: true,
        hooks: null,
        pedantic: false,
        renderer: null,
        silent: false,
        tokenizer: null,
        walkTokens: null
    };
}
let _defaults = _getDefaults();
function changeDefaults(newDefaults) {
    _defaults = newDefaults;
}

/**
 * Helpers
 */
const escapeTest = /[&<>"']/;
const escapeReplace = new RegExp(escapeTest.source, 'g');
const escapeTestNoEncode = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/;
const escapeReplaceNoEncode = new RegExp(escapeTestNoEncode.source, 'g');
const escapeReplacements = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
};
const getEscapeReplacement = (ch) => escapeReplacements[ch];
function escape$1(html, encode) {
    if (encode) {
        if (escapeTest.test(html)) {
            return html.replace(escapeReplace, getEscapeReplacement);
        }
    }
    else {
        if (escapeTestNoEncode.test(html)) {
            return html.replace(escapeReplaceNoEncode, getEscapeReplacement);
        }
    }
    return html;
}
const unescapeTest = /&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig;
function unescape$1(html) {
    // explicitly match decimal, hex, and named HTML entities
    return html.replace(unescapeTest, (_, n) => {
        n = n.toLowerCase();
        if (n === 'colon')
            return ':';
        if (n.charAt(0) === '#') {
            return n.charAt(1) === 'x'
                ? String.fromCharCode(parseInt(n.substring(2), 16))
                : String.fromCharCode(+n.substring(1));
        }
        return '';
    });
}
const caret = /(^|[^\[])\^/g;
function edit(regex, opt) {
    let source = typeof regex === 'string' ? regex : regex.source;
    opt = opt || '';
    const obj = {
        replace: (name, val) => {
            let valSource = typeof val === 'string' ? val : val.source;
            valSource = valSource.replace(caret, '$1');
            source = source.replace(name, valSource);
            return obj;
        },
        getRegex: () => {
            return new RegExp(source, opt);
        }
    };
    return obj;
}
function cleanUrl(href) {
    try {
        href = encodeURI(href).replace(/%25/g, '%');
    }
    catch (e) {
        return null;
    }
    return href;
}
const noopTest = { exec: () => null };
function splitCells(tableRow, count) {
    // ensure that every cell-delimiting pipe has a space
    // before it to distinguish it from an escaped pipe
    const row = tableRow.replace(/\|/g, (match, offset, str) => {
        let escaped = false;
        let curr = offset;
        while (--curr >= 0 && str[curr] === '\\')
            escaped = !escaped;
        if (escaped) {
            // odd number of slashes means | is escaped
            // so we leave it alone
            return '|';
        }
        else {
            // add space before unescaped |
            return ' |';
        }
    }), cells = row.split(/ \|/);
    let i = 0;
    // First/last cell in a row cannot be empty if it has no leading/trailing pipe
    if (!cells[0].trim()) {
        cells.shift();
    }
    if (cells.length > 0 && !cells[cells.length - 1].trim()) {
        cells.pop();
    }
    if (count) {
        if (cells.length > count) {
            cells.splice(count);
        }
        else {
            while (cells.length < count)
                cells.push('');
        }
    }
    for (; i < cells.length; i++) {
        // leading or trailing whitespace is ignored per the gfm spec
        cells[i] = cells[i].trim().replace(/\\\|/g, '|');
    }
    return cells;
}
/**
 * Remove trailing 'c's. Equivalent to str.replace(/c*$/, '').
 * /c*$/ is vulnerable to REDOS.
 *
 * @param str
 * @param c
 * @param invert Remove suffix of non-c chars instead. Default falsey.
 */
function rtrim(str, c, invert) {
    const l = str.length;
    if (l === 0) {
        return '';
    }
    // Length of suffix matching the invert condition.
    let suffLen = 0;
    // Step left until we fail to match the invert condition.
    while (suffLen < l) {
        const currChar = str.charAt(l - suffLen - 1);
        if (currChar === c && !invert) {
            suffLen++;
        }
        else if (currChar !== c && invert) {
            suffLen++;
        }
        else {
            break;
        }
    }
    return str.slice(0, l - suffLen);
}
function findClosingBracket(str, b) {
    if (str.indexOf(b[1]) === -1) {
        return -1;
    }
    let level = 0;
    for (let i = 0; i < str.length; i++) {
        if (str[i] === '\\') {
            i++;
        }
        else if (str[i] === b[0]) {
            level++;
        }
        else if (str[i] === b[1]) {
            level--;
            if (level < 0) {
                return i;
            }
        }
    }
    return -1;
}

function outputLink(cap, link, raw, lexer) {
    const href = link.href;
    const title = link.title ? escape$1(link.title) : null;
    const text = cap[1].replace(/\\([\[\]])/g, '$1');
    if (cap[0].charAt(0) !== '!') {
        lexer.state.inLink = true;
        const token = {
            type: 'link',
            raw,
            href,
            title,
            text,
            tokens: lexer.inlineTokens(text)
        };
        lexer.state.inLink = false;
        return token;
    }
    return {
        type: 'image',
        raw,
        href,
        title,
        text: escape$1(text)
    };
}
function indentCodeCompensation(raw, text) {
    const matchIndentToCode = raw.match(/^(\s+)(?:```)/);
    if (matchIndentToCode === null) {
        return text;
    }
    const indentToCode = matchIndentToCode[1];
    return text
        .split('\n')
        .map(node => {
        const matchIndentInNode = node.match(/^\s+/);
        if (matchIndentInNode === null) {
            return node;
        }
        const [indentInNode] = matchIndentInNode;
        if (indentInNode.length >= indentToCode.length) {
            return node.slice(indentToCode.length);
        }
        return node;
    })
        .join('\n');
}
/**
 * Tokenizer
 */
class _Tokenizer {
    options;
    rules; // set by the lexer
    lexer; // set by the lexer
    constructor(options) {
        this.options = options || _defaults;
    }
    space(src) {
        const cap = this.rules.block.newline.exec(src);
        if (cap && cap[0].length > 0) {
            return {
                type: 'space',
                raw: cap[0]
            };
        }
    }
    code(src) {
        const cap = this.rules.block.code.exec(src);
        if (cap) {
            const text = cap[0].replace(/^ {1,4}/gm, '');
            return {
                type: 'code',
                raw: cap[0],
                codeBlockStyle: 'indented',
                text: !this.options.pedantic
                    ? rtrim(text, '\n')
                    : text
            };
        }
    }
    fences(src) {
        const cap = this.rules.block.fences.exec(src);
        if (cap) {
            const raw = cap[0];
            const text = indentCodeCompensation(raw, cap[3] || '');
            return {
                type: 'code',
                raw,
                lang: cap[2] ? cap[2].trim().replace(this.rules.inline.anyPunctuation, '$1') : cap[2],
                text
            };
        }
    }
    heading(src) {
        const cap = this.rules.block.heading.exec(src);
        if (cap) {
            let text = cap[2].trim();
            // remove trailing #s
            if (/#$/.test(text)) {
                const trimmed = rtrim(text, '#');
                if (this.options.pedantic) {
                    text = trimmed.trim();
                }
                else if (!trimmed || / $/.test(trimmed)) {
                    // CommonMark requires space before trailing #s
                    text = trimmed.trim();
                }
            }
            return {
                type: 'heading',
                raw: cap[0],
                depth: cap[1].length,
                text,
                tokens: this.lexer.inline(text)
            };
        }
    }
    hr(src) {
        const cap = this.rules.block.hr.exec(src);
        if (cap) {
            return {
                type: 'hr',
                raw: cap[0]
            };
        }
    }
    blockquote(src) {
        const cap = this.rules.block.blockquote.exec(src);
        if (cap) {
            // precede setext continuation with 4 spaces so it isn't a setext
            let text = cap[0].replace(/\n {0,3}((?:=+|-+) *)(?=\n|$)/g, '\n    $1');
            text = rtrim(text.replace(/^ *>[ \t]?/gm, ''), '\n');
            const top = this.lexer.state.top;
            this.lexer.state.top = true;
            const tokens = this.lexer.blockTokens(text);
            this.lexer.state.top = top;
            return {
                type: 'blockquote',
                raw: cap[0],
                tokens,
                text
            };
        }
    }
    list(src) {
        let cap = this.rules.block.list.exec(src);
        if (cap) {
            let bull = cap[1].trim();
            const isordered = bull.length > 1;
            const list = {
                type: 'list',
                raw: '',
                ordered: isordered,
                start: isordered ? +bull.slice(0, -1) : '',
                loose: false,
                items: []
            };
            bull = isordered ? `\\d{1,9}\\${bull.slice(-1)}` : `\\${bull}`;
            if (this.options.pedantic) {
                bull = isordered ? bull : '[*+-]';
            }
            // Get next list item
            const itemRegex = new RegExp(`^( {0,3}${bull})((?:[\t ][^\\n]*)?(?:\\n|$))`);
            let raw = '';
            let itemContents = '';
            let endsWithBlankLine = false;
            // Check if current bullet point can start a new List Item
            while (src) {
                let endEarly = false;
                if (!(cap = itemRegex.exec(src))) {
                    break;
                }
                if (this.rules.block.hr.test(src)) { // End list if bullet was actually HR (possibly move into itemRegex?)
                    break;
                }
                raw = cap[0];
                src = src.substring(raw.length);
                let line = cap[2].split('\n', 1)[0].replace(/^\t+/, (t) => ' '.repeat(3 * t.length));
                let nextLine = src.split('\n', 1)[0];
                let indent = 0;
                if (this.options.pedantic) {
                    indent = 2;
                    itemContents = line.trimStart();
                }
                else {
                    indent = cap[2].search(/[^ ]/); // Find first non-space char
                    indent = indent > 4 ? 1 : indent; // Treat indented code blocks (> 4 spaces) as having only 1 indent
                    itemContents = line.slice(indent);
                    indent += cap[1].length;
                }
                let blankLine = false;
                if (!line && /^ *$/.test(nextLine)) { // Items begin with at most one blank line
                    raw += nextLine + '\n';
                    src = src.substring(nextLine.length + 1);
                    endEarly = true;
                }
                if (!endEarly) {
                    const nextBulletRegex = new RegExp(`^ {0,${Math.min(3, indent - 1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ \t][^\\n]*)?(?:\\n|$))`);
                    const hrRegex = new RegExp(`^ {0,${Math.min(3, indent - 1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`);
                    const fencesBeginRegex = new RegExp(`^ {0,${Math.min(3, indent - 1)}}(?:\`\`\`|~~~)`);
                    const headingBeginRegex = new RegExp(`^ {0,${Math.min(3, indent - 1)}}#`);
                    // Check if following lines should be included in List Item
                    while (src) {
                        const rawLine = src.split('\n', 1)[0];
                        nextLine = rawLine;
                        // Re-align to follow commonmark nesting rules
                        if (this.options.pedantic) {
                            nextLine = nextLine.replace(/^ {1,4}(?=( {4})*[^ ])/g, '  ');
                        }
                        // End list item if found code fences
                        if (fencesBeginRegex.test(nextLine)) {
                            break;
                        }
                        // End list item if found start of new heading
                        if (headingBeginRegex.test(nextLine)) {
                            break;
                        }
                        // End list item if found start of new bullet
                        if (nextBulletRegex.test(nextLine)) {
                            break;
                        }
                        // Horizontal rule found
                        if (hrRegex.test(src)) {
                            break;
                        }
                        if (nextLine.search(/[^ ]/) >= indent || !nextLine.trim()) { // Dedent if possible
                            itemContents += '\n' + nextLine.slice(indent);
                        }
                        else {
                            // not enough indentation
                            if (blankLine) {
                                break;
                            }
                            // paragraph continuation unless last line was a different block level element
                            if (line.search(/[^ ]/) >= 4) { // indented code block
                                break;
                            }
                            if (fencesBeginRegex.test(line)) {
                                break;
                            }
                            if (headingBeginRegex.test(line)) {
                                break;
                            }
                            if (hrRegex.test(line)) {
                                break;
                            }
                            itemContents += '\n' + nextLine;
                        }
                        if (!blankLine && !nextLine.trim()) { // Check if current line is blank
                            blankLine = true;
                        }
                        raw += rawLine + '\n';
                        src = src.substring(rawLine.length + 1);
                        line = nextLine.slice(indent);
                    }
                }
                if (!list.loose) {
                    // If the previous item ended with a blank line, the list is loose
                    if (endsWithBlankLine) {
                        list.loose = true;
                    }
                    else if (/\n *\n *$/.test(raw)) {
                        endsWithBlankLine = true;
                    }
                }
                let istask = null;
                let ischecked;
                // Check for task list items
                if (this.options.gfm) {
                    istask = /^\[[ xX]\] /.exec(itemContents);
                    if (istask) {
                        ischecked = istask[0] !== '[ ] ';
                        itemContents = itemContents.replace(/^\[[ xX]\] +/, '');
                    }
                }
                list.items.push({
                    type: 'list_item',
                    raw,
                    task: !!istask,
                    checked: ischecked,
                    loose: false,
                    text: itemContents,
                    tokens: []
                });
                list.raw += raw;
            }
            // Do not consume newlines at end of final item. Alternatively, make itemRegex *start* with any newlines to simplify/speed up endsWithBlankLine logic
            list.items[list.items.length - 1].raw = raw.trimEnd();
            (list.items[list.items.length - 1]).text = itemContents.trimEnd();
            list.raw = list.raw.trimEnd();
            // Item child tokens handled here at end because we needed to have the final item to trim it first
            for (let i = 0; i < list.items.length; i++) {
                this.lexer.state.top = false;
                list.items[i].tokens = this.lexer.blockTokens(list.items[i].text, []);
                if (!list.loose) {
                    // Check if list should be loose
                    const spacers = list.items[i].tokens.filter(t => t.type === 'space');
                    const hasMultipleLineBreaks = spacers.length > 0 && spacers.some(t => /\n.*\n/.test(t.raw));
                    list.loose = hasMultipleLineBreaks;
                }
            }
            // Set all items to loose if list is loose
            if (list.loose) {
                for (let i = 0; i < list.items.length; i++) {
                    list.items[i].loose = true;
                }
            }
            return list;
        }
    }
    html(src) {
        const cap = this.rules.block.html.exec(src);
        if (cap) {
            const token = {
                type: 'html',
                block: true,
                raw: cap[0],
                pre: cap[1] === 'pre' || cap[1] === 'script' || cap[1] === 'style',
                text: cap[0]
            };
            return token;
        }
    }
    def(src) {
        const cap = this.rules.block.def.exec(src);
        if (cap) {
            const tag = cap[1].toLowerCase().replace(/\s+/g, ' ');
            const href = cap[2] ? cap[2].replace(/^<(.*)>$/, '$1').replace(this.rules.inline.anyPunctuation, '$1') : '';
            const title = cap[3] ? cap[3].substring(1, cap[3].length - 1).replace(this.rules.inline.anyPunctuation, '$1') : cap[3];
            return {
                type: 'def',
                tag,
                raw: cap[0],
                href,
                title
            };
        }
    }
    table(src) {
        const cap = this.rules.block.table.exec(src);
        if (!cap) {
            return;
        }
        if (!/[:|]/.test(cap[2])) {
            // delimiter row must have a pipe (|) or colon (:) otherwise it is a setext heading
            return;
        }
        const headers = splitCells(cap[1]);
        const aligns = cap[2].replace(/^\||\| *$/g, '').split('|');
        const rows = cap[3] && cap[3].trim() ? cap[3].replace(/\n[ \t]*$/, '').split('\n') : [];
        const item = {
            type: 'table',
            raw: cap[0],
            header: [],
            align: [],
            rows: []
        };
        if (headers.length !== aligns.length) {
            // header and align columns must be equal, rows can be different.
            return;
        }
        for (const align of aligns) {
            if (/^ *-+: *$/.test(align)) {
                item.align.push('right');
            }
            else if (/^ *:-+: *$/.test(align)) {
                item.align.push('center');
            }
            else if (/^ *:-+ *$/.test(align)) {
                item.align.push('left');
            }
            else {
                item.align.push(null);
            }
        }
        for (const header of headers) {
            item.header.push({
                text: header,
                tokens: this.lexer.inline(header)
            });
        }
        for (const row of rows) {
            item.rows.push(splitCells(row, item.header.length).map(cell => {
                return {
                    text: cell,
                    tokens: this.lexer.inline(cell)
                };
            }));
        }
        return item;
    }
    lheading(src) {
        const cap = this.rules.block.lheading.exec(src);
        if (cap) {
            return {
                type: 'heading',
                raw: cap[0],
                depth: cap[2].charAt(0) === '=' ? 1 : 2,
                text: cap[1],
                tokens: this.lexer.inline(cap[1])
            };
        }
    }
    paragraph(src) {
        const cap = this.rules.block.paragraph.exec(src);
        if (cap) {
            const text = cap[1].charAt(cap[1].length - 1) === '\n'
                ? cap[1].slice(0, -1)
                : cap[1];
            return {
                type: 'paragraph',
                raw: cap[0],
                text,
                tokens: this.lexer.inline(text)
            };
        }
    }
    text(src) {
        const cap = this.rules.block.text.exec(src);
        if (cap) {
            return {
                type: 'text',
                raw: cap[0],
                text: cap[0],
                tokens: this.lexer.inline(cap[0])
            };
        }
    }
    escape(src) {
        const cap = this.rules.inline.escape.exec(src);
        if (cap) {
            return {
                type: 'escape',
                raw: cap[0],
                text: escape$1(cap[1])
            };
        }
    }
    tag(src) {
        const cap = this.rules.inline.tag.exec(src);
        if (cap) {
            if (!this.lexer.state.inLink && /^<a /i.test(cap[0])) {
                this.lexer.state.inLink = true;
            }
            else if (this.lexer.state.inLink && /^<\/a>/i.test(cap[0])) {
                this.lexer.state.inLink = false;
            }
            if (!this.lexer.state.inRawBlock && /^<(pre|code|kbd|script)(\s|>)/i.test(cap[0])) {
                this.lexer.state.inRawBlock = true;
            }
            else if (this.lexer.state.inRawBlock && /^<\/(pre|code|kbd|script)(\s|>)/i.test(cap[0])) {
                this.lexer.state.inRawBlock = false;
            }
            return {
                type: 'html',
                raw: cap[0],
                inLink: this.lexer.state.inLink,
                inRawBlock: this.lexer.state.inRawBlock,
                block: false,
                text: cap[0]
            };
        }
    }
    link(src) {
        const cap = this.rules.inline.link.exec(src);
        if (cap) {
            const trimmedUrl = cap[2].trim();
            if (!this.options.pedantic && /^</.test(trimmedUrl)) {
                // commonmark requires matching angle brackets
                if (!(/>$/.test(trimmedUrl))) {
                    return;
                }
                // ending angle bracket cannot be escaped
                const rtrimSlash = rtrim(trimmedUrl.slice(0, -1), '\\');
                if ((trimmedUrl.length - rtrimSlash.length) % 2 === 0) {
                    return;
                }
            }
            else {
                // find closing parenthesis
                const lastParenIndex = findClosingBracket(cap[2], '()');
                if (lastParenIndex > -1) {
                    const start = cap[0].indexOf('!') === 0 ? 5 : 4;
                    const linkLen = start + cap[1].length + lastParenIndex;
                    cap[2] = cap[2].substring(0, lastParenIndex);
                    cap[0] = cap[0].substring(0, linkLen).trim();
                    cap[3] = '';
                }
            }
            let href = cap[2];
            let title = '';
            if (this.options.pedantic) {
                // split pedantic href and title
                const link = /^([^'"]*[^\s])\s+(['"])(.*)\2/.exec(href);
                if (link) {
                    href = link[1];
                    title = link[3];
                }
            }
            else {
                title = cap[3] ? cap[3].slice(1, -1) : '';
            }
            href = href.trim();
            if (/^</.test(href)) {
                if (this.options.pedantic && !(/>$/.test(trimmedUrl))) {
                    // pedantic allows starting angle bracket without ending angle bracket
                    href = href.slice(1);
                }
                else {
                    href = href.slice(1, -1);
                }
            }
            return outputLink(cap, {
                href: href ? href.replace(this.rules.inline.anyPunctuation, '$1') : href,
                title: title ? title.replace(this.rules.inline.anyPunctuation, '$1') : title
            }, cap[0], this.lexer);
        }
    }
    reflink(src, links) {
        let cap;
        if ((cap = this.rules.inline.reflink.exec(src))
            || (cap = this.rules.inline.nolink.exec(src))) {
            const linkString = (cap[2] || cap[1]).replace(/\s+/g, ' ');
            const link = links[linkString.toLowerCase()];
            if (!link) {
                const text = cap[0].charAt(0);
                return {
                    type: 'text',
                    raw: text,
                    text
                };
            }
            return outputLink(cap, link, cap[0], this.lexer);
        }
    }
    emStrong(src, maskedSrc, prevChar = '') {
        let match = this.rules.inline.emStrongLDelim.exec(src);
        if (!match)
            return;
        // _ can't be between two alphanumerics. \p{L}\p{N} includes non-english alphabet/numbers as well
        if (match[3] && prevChar.match(/[\p{L}\p{N}]/u))
            return;
        const nextChar = match[1] || match[2] || '';
        if (!nextChar || !prevChar || this.rules.inline.punctuation.exec(prevChar)) {
            // unicode Regex counts emoji as 1 char; spread into array for proper count (used multiple times below)
            const lLength = [...match[0]].length - 1;
            let rDelim, rLength, delimTotal = lLength, midDelimTotal = 0;
            const endReg = match[0][0] === '*' ? this.rules.inline.emStrongRDelimAst : this.rules.inline.emStrongRDelimUnd;
            endReg.lastIndex = 0;
            // Clip maskedSrc to same section of string as src (move to lexer?)
            maskedSrc = maskedSrc.slice(-1 * src.length + lLength);
            while ((match = endReg.exec(maskedSrc)) != null) {
                rDelim = match[1] || match[2] || match[3] || match[4] || match[5] || match[6];
                if (!rDelim)
                    continue; // skip single * in __abc*abc__
                rLength = [...rDelim].length;
                if (match[3] || match[4]) { // found another Left Delim
                    delimTotal += rLength;
                    continue;
                }
                else if (match[5] || match[6]) { // either Left or Right Delim
                    if (lLength % 3 && !((lLength + rLength) % 3)) {
                        midDelimTotal += rLength;
                        continue; // CommonMark Emphasis Rules 9-10
                    }
                }
                delimTotal -= rLength;
                if (delimTotal > 0)
                    continue; // Haven't found enough closing delimiters
                // Remove extra characters. *a*** -> *a*
                rLength = Math.min(rLength, rLength + delimTotal + midDelimTotal);
                // char length can be >1 for unicode characters;
                const lastCharLength = [...match[0]][0].length;
                const raw = src.slice(0, lLength + match.index + lastCharLength + rLength);
                // Create `em` if smallest delimiter has odd char count. *a***
                if (Math.min(lLength, rLength) % 2) {
                    const text = raw.slice(1, -1);
                    return {
                        type: 'em',
                        raw,
                        text,
                        tokens: this.lexer.inlineTokens(text)
                    };
                }
                // Create 'strong' if smallest delimiter has even char count. **a***
                const text = raw.slice(2, -2);
                return {
                    type: 'strong',
                    raw,
                    text,
                    tokens: this.lexer.inlineTokens(text)
                };
            }
        }
    }
    codespan(src) {
        const cap = this.rules.inline.code.exec(src);
        if (cap) {
            let text = cap[2].replace(/\n/g, ' ');
            const hasNonSpaceChars = /[^ ]/.test(text);
            const hasSpaceCharsOnBothEnds = /^ /.test(text) && / $/.test(text);
            if (hasNonSpaceChars && hasSpaceCharsOnBothEnds) {
                text = text.substring(1, text.length - 1);
            }
            text = escape$1(text, true);
            return {
                type: 'codespan',
                raw: cap[0],
                text
            };
        }
    }
    br(src) {
        const cap = this.rules.inline.br.exec(src);
        if (cap) {
            return {
                type: 'br',
                raw: cap[0]
            };
        }
    }
    del(src) {
        const cap = this.rules.inline.del.exec(src);
        if (cap) {
            return {
                type: 'del',
                raw: cap[0],
                text: cap[2],
                tokens: this.lexer.inlineTokens(cap[2])
            };
        }
    }
    autolink(src) {
        const cap = this.rules.inline.autolink.exec(src);
        if (cap) {
            let text, href;
            if (cap[2] === '@') {
                text = escape$1(cap[1]);
                href = 'mailto:' + text;
            }
            else {
                text = escape$1(cap[1]);
                href = text;
            }
            return {
                type: 'link',
                raw: cap[0],
                text,
                href,
                tokens: [
                    {
                        type: 'text',
                        raw: text,
                        text
                    }
                ]
            };
        }
    }
    url(src) {
        let cap;
        if (cap = this.rules.inline.url.exec(src)) {
            let text, href;
            if (cap[2] === '@') {
                text = escape$1(cap[0]);
                href = 'mailto:' + text;
            }
            else {
                // do extended autolink path validation
                let prevCapZero;
                do {
                    prevCapZero = cap[0];
                    cap[0] = this.rules.inline._backpedal.exec(cap[0])?.[0] ?? '';
                } while (prevCapZero !== cap[0]);
                text = escape$1(cap[0]);
                if (cap[1] === 'www.') {
                    href = 'http://' + cap[0];
                }
                else {
                    href = cap[0];
                }
            }
            return {
                type: 'link',
                raw: cap[0],
                text,
                href,
                tokens: [
                    {
                        type: 'text',
                        raw: text,
                        text
                    }
                ]
            };
        }
    }
    inlineText(src) {
        const cap = this.rules.inline.text.exec(src);
        if (cap) {
            let text;
            if (this.lexer.state.inRawBlock) {
                text = cap[0];
            }
            else {
                text = escape$1(cap[0]);
            }
            return {
                type: 'text',
                raw: cap[0],
                text
            };
        }
    }
}

/**
 * Block-Level Grammar
 */
const newline = /^(?: *(?:\n|$))+/;
const blockCode = /^( {4}[^\n]+(?:\n(?: *(?:\n|$))*)?)+/;
const fences = /^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/;
const hr = /^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/;
const heading = /^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/;
const bullet = /(?:[*+-]|\d{1,9}[.)])/;
const lheading = edit(/^(?!bull |blockCode|fences|blockquote|heading|html)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html))+?)\n {0,3}(=+|-+) *(?:\n+|$)/)
    .replace(/bull/g, bullet) // lists can interrupt
    .replace(/blockCode/g, / {4}/) // indented code blocks can interrupt
    .replace(/fences/g, / {0,3}(?:`{3,}|~{3,})/) // fenced code blocks can interrupt
    .replace(/blockquote/g, / {0,3}>/) // blockquote can interrupt
    .replace(/heading/g, / {0,3}#{1,6}/) // ATX heading can interrupt
    .replace(/html/g, / {0,3}<[^\n>]+>\n/) // block html can interrupt
    .getRegex();
const _paragraph = /^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/;
const blockText = /^[^\n]+/;
const _blockLabel = /(?!\s*\])(?:\\.|[^\[\]\\])+/;
const def = edit(/^ {0,3}\[(label)\]: *(?:\n *)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n *)?| *\n *)(title))? *(?:\n+|$)/)
    .replace('label', _blockLabel)
    .replace('title', /(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/)
    .getRegex();
const list = edit(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/)
    .replace(/bull/g, bullet)
    .getRegex();
const _tag = 'address|article|aside|base|basefont|blockquote|body|caption'
    + '|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption'
    + '|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe'
    + '|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option'
    + '|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title'
    + '|tr|track|ul';
const _comment = /<!--(?:-?>|[\s\S]*?(?:-->|$))/;
const html = edit('^ {0,3}(?:' // optional indentation
    + '<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)' // (1)
    + '|comment[^\\n]*(\\n+|$)' // (2)
    + '|<\\?[\\s\\S]*?(?:\\?>\\n*|$)' // (3)
    + '|<![A-Z][\\s\\S]*?(?:>\\n*|$)' // (4)
    + '|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)' // (5)
    + '|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n *)+\\n|$)' // (6)
    + '|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$)' // (7) open tag
    + '|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$)' // (7) closing tag
    + ')', 'i')
    .replace('comment', _comment)
    .replace('tag', _tag)
    .replace('attribute', / +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/)
    .getRegex();
const paragraph = edit(_paragraph)
    .replace('hr', hr)
    .replace('heading', ' {0,3}#{1,6}(?:\\s|$)')
    .replace('|lheading', '') // setext headings don't interrupt commonmark paragraphs
    .replace('|table', '')
    .replace('blockquote', ' {0,3}>')
    .replace('fences', ' {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n')
    .replace('list', ' {0,3}(?:[*+-]|1[.)]) ') // only lists starting from 1 can interrupt
    .replace('html', '</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)')
    .replace('tag', _tag) // pars can be interrupted by type (6) html blocks
    .getRegex();
const blockquote = edit(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/)
    .replace('paragraph', paragraph)
    .getRegex();
/**
 * Normal Block Grammar
 */
const blockNormal = {
    blockquote,
    code: blockCode,
    def,
    fences,
    heading,
    hr,
    html,
    lheading,
    list,
    newline,
    paragraph,
    table: noopTest,
    text: blockText
};
/**
 * GFM Block Grammar
 */
const gfmTable = edit('^ *([^\\n ].*)\\n' // Header
    + ' {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)' // Align
    + '(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)') // Cells
    .replace('hr', hr)
    .replace('heading', ' {0,3}#{1,6}(?:\\s|$)')
    .replace('blockquote', ' {0,3}>')
    .replace('code', ' {4}[^\\n]')
    .replace('fences', ' {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n')
    .replace('list', ' {0,3}(?:[*+-]|1[.)]) ') // only lists starting from 1 can interrupt
    .replace('html', '</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)')
    .replace('tag', _tag) // tables can be interrupted by type (6) html blocks
    .getRegex();
const blockGfm = {
    ...blockNormal,
    table: gfmTable,
    paragraph: edit(_paragraph)
        .replace('hr', hr)
        .replace('heading', ' {0,3}#{1,6}(?:\\s|$)')
        .replace('|lheading', '') // setext headings don't interrupt commonmark paragraphs
        .replace('table', gfmTable) // interrupt paragraphs with table
        .replace('blockquote', ' {0,3}>')
        .replace('fences', ' {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n')
        .replace('list', ' {0,3}(?:[*+-]|1[.)]) ') // only lists starting from 1 can interrupt
        .replace('html', '</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)')
        .replace('tag', _tag) // pars can be interrupted by type (6) html blocks
        .getRegex()
};
/**
 * Pedantic grammar (original John Gruber's loose markdown specification)
 */
const blockPedantic = {
    ...blockNormal,
    html: edit('^ *(?:comment *(?:\\n|\\s*$)'
        + '|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)' // closed tag
        + '|<tag(?:"[^"]*"|\'[^\']*\'|\\s[^\'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))')
        .replace('comment', _comment)
        .replace(/tag/g, '(?!(?:'
        + 'a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub'
        + '|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)'
        + '\\b)\\w+(?!:|[^\\w\\s@]*@)\\b')
        .getRegex(),
    def: /^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,
    heading: /^(#{1,6})(.*)(?:\n+|$)/,
    fences: noopTest, // fences not supported
    lheading: /^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,
    paragraph: edit(_paragraph)
        .replace('hr', hr)
        .replace('heading', ' *#{1,6} *[^\n]')
        .replace('lheading', lheading)
        .replace('|table', '')
        .replace('blockquote', ' {0,3}>')
        .replace('|fences', '')
        .replace('|list', '')
        .replace('|html', '')
        .replace('|tag', '')
        .getRegex()
};
/**
 * Inline-Level Grammar
 */
const escape = /^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/;
const inlineCode = /^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/;
const br = /^( {2,}|\\)\n(?!\s*$)/;
const inlineText = /^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/;
// list of unicode punctuation marks, plus any missing characters from CommonMark spec
const _punctuation = '\\p{P}\\p{S}';
const punctuation = edit(/^((?![*_])[\spunctuation])/, 'u')
    .replace(/punctuation/g, _punctuation).getRegex();
// sequences em should skip over [title](link), `code`, <html>
const blockSkip = /\[[^[\]]*?\]\([^\(\)]*?\)|`[^`]*?`|<[^<>]*?>/g;
const emStrongLDelim = edit(/^(?:\*+(?:((?!\*)[punct])|[^\s*]))|^_+(?:((?!_)[punct])|([^\s_]))/, 'u')
    .replace(/punct/g, _punctuation)
    .getRegex();
const emStrongRDelimAst = edit('^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)' // Skip orphan inside strong
    + '|[^*]+(?=[^*])' // Consume to delim
    + '|(?!\\*)[punct](\\*+)(?=[\\s]|$)' // (1) #*** can only be a Right Delimiter
    + '|[^punct\\s](\\*+)(?!\\*)(?=[punct\\s]|$)' // (2) a***#, a*** can only be a Right Delimiter
    + '|(?!\\*)[punct\\s](\\*+)(?=[^punct\\s])' // (3) #***a, ***a can only be Left Delimiter
    + '|[\\s](\\*+)(?!\\*)(?=[punct])' // (4) ***# can only be Left Delimiter
    + '|(?!\\*)[punct](\\*+)(?!\\*)(?=[punct])' // (5) #***# can be either Left or Right Delimiter
    + '|[^punct\\s](\\*+)(?=[^punct\\s])', 'gu') // (6) a***a can be either Left or Right Delimiter
    .replace(/punct/g, _punctuation)
    .getRegex();
// (6) Not allowed for _
const emStrongRDelimUnd = edit('^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)' // Skip orphan inside strong
    + '|[^_]+(?=[^_])' // Consume to delim
    + '|(?!_)[punct](_+)(?=[\\s]|$)' // (1) #___ can only be a Right Delimiter
    + '|[^punct\\s](_+)(?!_)(?=[punct\\s]|$)' // (2) a___#, a___ can only be a Right Delimiter
    + '|(?!_)[punct\\s](_+)(?=[^punct\\s])' // (3) #___a, ___a can only be Left Delimiter
    + '|[\\s](_+)(?!_)(?=[punct])' // (4) ___# can only be Left Delimiter
    + '|(?!_)[punct](_+)(?!_)(?=[punct])', 'gu') // (5) #___# can be either Left or Right Delimiter
    .replace(/punct/g, _punctuation)
    .getRegex();
const anyPunctuation = edit(/\\([punct])/, 'gu')
    .replace(/punct/g, _punctuation)
    .getRegex();
const autolink = edit(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/)
    .replace('scheme', /[a-zA-Z][a-zA-Z0-9+.-]{1,31}/)
    .replace('email', /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/)
    .getRegex();
const _inlineComment = edit(_comment).replace('(?:-->|$)', '-->').getRegex();
const tag = edit('^comment'
    + '|^</[a-zA-Z][\\w:-]*\\s*>' // self-closing tag
    + '|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>' // open tag
    + '|^<\\?[\\s\\S]*?\\?>' // processing instruction, e.g. <?php ?>
    + '|^<![a-zA-Z]+\\s[\\s\\S]*?>' // declaration, e.g. <!DOCTYPE html>
    + '|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>') // CDATA section
    .replace('comment', _inlineComment)
    .replace('attribute', /\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/)
    .getRegex();
const _inlineLabel = /(?:\[(?:\\.|[^\[\]\\])*\]|\\.|`[^`]*`|[^\[\]\\`])*?/;
const link = edit(/^!?\[(label)\]\(\s*(href)(?:\s+(title))?\s*\)/)
    .replace('label', _inlineLabel)
    .replace('href', /<(?:\\.|[^\n<>\\])+>|[^\s\x00-\x1f]*/)
    .replace('title', /"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/)
    .getRegex();
const reflink = edit(/^!?\[(label)\]\[(ref)\]/)
    .replace('label', _inlineLabel)
    .replace('ref', _blockLabel)
    .getRegex();
const nolink = edit(/^!?\[(ref)\](?:\[\])?/)
    .replace('ref', _blockLabel)
    .getRegex();
const reflinkSearch = edit('reflink|nolink(?!\\()', 'g')
    .replace('reflink', reflink)
    .replace('nolink', nolink)
    .getRegex();
/**
 * Normal Inline Grammar
 */
const inlineNormal = {
    _backpedal: noopTest, // only used for GFM url
    anyPunctuation,
    autolink,
    blockSkip,
    br,
    code: inlineCode,
    del: noopTest,
    emStrongLDelim,
    emStrongRDelimAst,
    emStrongRDelimUnd,
    escape,
    link,
    nolink,
    punctuation,
    reflink,
    reflinkSearch,
    tag,
    text: inlineText,
    url: noopTest
};
/**
 * Pedantic Inline Grammar
 */
const inlinePedantic = {
    ...inlineNormal,
    link: edit(/^!?\[(label)\]\((.*?)\)/)
        .replace('label', _inlineLabel)
        .getRegex(),
    reflink: edit(/^!?\[(label)\]\s*\[([^\]]*)\]/)
        .replace('label', _inlineLabel)
        .getRegex()
};
/**
 * GFM Inline Grammar
 */
const inlineGfm = {
    ...inlineNormal,
    escape: edit(escape).replace('])', '~|])').getRegex(),
    url: edit(/^((?:ftp|https?):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/, 'i')
        .replace('email', /[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/)
        .getRegex(),
    _backpedal: /(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,
    del: /^(~~?)(?=[^\s~])([\s\S]*?[^\s~])\1(?=[^~]|$)/,
    text: /^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|https?:\/\/|ftp:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/
};
/**
 * GFM + Line Breaks Inline Grammar
 */
const inlineBreaks = {
    ...inlineGfm,
    br: edit(br).replace('{2,}', '*').getRegex(),
    text: edit(inlineGfm.text)
        .replace('\\b_', '\\b_| {2,}\\n')
        .replace(/\{2,\}/g, '*')
        .getRegex()
};
/**
 * exports
 */
const block = {
    normal: blockNormal,
    gfm: blockGfm,
    pedantic: blockPedantic
};
const inline = {
    normal: inlineNormal,
    gfm: inlineGfm,
    breaks: inlineBreaks,
    pedantic: inlinePedantic
};

/**
 * Block Lexer
 */
class _Lexer {
    tokens;
    options;
    state;
    tokenizer;
    inlineQueue;
    constructor(options) {
        // TokenList cannot be created in one go
        this.tokens = [];
        this.tokens.links = Object.create(null);
        this.options = options || _defaults;
        this.options.tokenizer = this.options.tokenizer || new _Tokenizer();
        this.tokenizer = this.options.tokenizer;
        this.tokenizer.options = this.options;
        this.tokenizer.lexer = this;
        this.inlineQueue = [];
        this.state = {
            inLink: false,
            inRawBlock: false,
            top: true
        };
        const rules = {
            block: block.normal,
            inline: inline.normal
        };
        if (this.options.pedantic) {
            rules.block = block.pedantic;
            rules.inline = inline.pedantic;
        }
        else if (this.options.gfm) {
            rules.block = block.gfm;
            if (this.options.breaks) {
                rules.inline = inline.breaks;
            }
            else {
                rules.inline = inline.gfm;
            }
        }
        this.tokenizer.rules = rules;
    }
    /**
     * Expose Rules
     */
    static get rules() {
        return {
            block,
            inline
        };
    }
    /**
     * Static Lex Method
     */
    static lex(src, options) {
        const lexer = new _Lexer(options);
        return lexer.lex(src);
    }
    /**
     * Static Lex Inline Method
     */
    static lexInline(src, options) {
        const lexer = new _Lexer(options);
        return lexer.inlineTokens(src);
    }
    /**
     * Preprocessing
     */
    lex(src) {
        src = src
            .replace(/\r\n|\r/g, '\n');
        this.blockTokens(src, this.tokens);
        for (let i = 0; i < this.inlineQueue.length; i++) {
            const next = this.inlineQueue[i];
            this.inlineTokens(next.src, next.tokens);
        }
        this.inlineQueue = [];
        return this.tokens;
    }
    blockTokens(src, tokens = []) {
        if (this.options.pedantic) {
            src = src.replace(/\t/g, '    ').replace(/^ +$/gm, '');
        }
        else {
            src = src.replace(/^( *)(\t+)/gm, (_, leading, tabs) => {
                return leading + '    '.repeat(tabs.length);
            });
        }
        let token;
        let lastToken;
        let cutSrc;
        let lastParagraphClipped;
        while (src) {
            if (this.options.extensions
                && this.options.extensions.block
                && this.options.extensions.block.some((extTokenizer) => {
                    if (token = extTokenizer.call({ lexer: this }, src, tokens)) {
                        src = src.substring(token.raw.length);
                        tokens.push(token);
                        return true;
                    }
                    return false;
                })) {
                continue;
            }
            // newline
            if (token = this.tokenizer.space(src)) {
                src = src.substring(token.raw.length);
                if (token.raw.length === 1 && tokens.length > 0) {
                    // if there's a single \n as a spacer, it's terminating the last line,
                    // so move it there so that we don't get unnecessary paragraph tags
                    tokens[tokens.length - 1].raw += '\n';
                }
                else {
                    tokens.push(token);
                }
                continue;
            }
            // code
            if (token = this.tokenizer.code(src)) {
                src = src.substring(token.raw.length);
                lastToken = tokens[tokens.length - 1];
                // An indented code block cannot interrupt a paragraph.
                if (lastToken && (lastToken.type === 'paragraph' || lastToken.type === 'text')) {
                    lastToken.raw += '\n' + token.raw;
                    lastToken.text += '\n' + token.text;
                    this.inlineQueue[this.inlineQueue.length - 1].src = lastToken.text;
                }
                else {
                    tokens.push(token);
                }
                continue;
            }
            // fences
            if (token = this.tokenizer.fences(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // heading
            if (token = this.tokenizer.heading(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // hr
            if (token = this.tokenizer.hr(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // blockquote
            if (token = this.tokenizer.blockquote(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // list
            if (token = this.tokenizer.list(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // html
            if (token = this.tokenizer.html(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // def
            if (token = this.tokenizer.def(src)) {
                src = src.substring(token.raw.length);
                lastToken = tokens[tokens.length - 1];
                if (lastToken && (lastToken.type === 'paragraph' || lastToken.type === 'text')) {
                    lastToken.raw += '\n' + token.raw;
                    lastToken.text += '\n' + token.raw;
                    this.inlineQueue[this.inlineQueue.length - 1].src = lastToken.text;
                }
                else if (!this.tokens.links[token.tag]) {
                    this.tokens.links[token.tag] = {
                        href: token.href,
                        title: token.title
                    };
                }
                continue;
            }
            // table (gfm)
            if (token = this.tokenizer.table(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // lheading
            if (token = this.tokenizer.lheading(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // top-level paragraph
            // prevent paragraph consuming extensions by clipping 'src' to extension start
            cutSrc = src;
            if (this.options.extensions && this.options.extensions.startBlock) {
                let startIndex = Infinity;
                const tempSrc = src.slice(1);
                let tempStart;
                this.options.extensions.startBlock.forEach((getStartIndex) => {
                    tempStart = getStartIndex.call({ lexer: this }, tempSrc);
                    if (typeof tempStart === 'number' && tempStart >= 0) {
                        startIndex = Math.min(startIndex, tempStart);
                    }
                });
                if (startIndex < Infinity && startIndex >= 0) {
                    cutSrc = src.substring(0, startIndex + 1);
                }
            }
            if (this.state.top && (token = this.tokenizer.paragraph(cutSrc))) {
                lastToken = tokens[tokens.length - 1];
                if (lastParagraphClipped && lastToken.type === 'paragraph') {
                    lastToken.raw += '\n' + token.raw;
                    lastToken.text += '\n' + token.text;
                    this.inlineQueue.pop();
                    this.inlineQueue[this.inlineQueue.length - 1].src = lastToken.text;
                }
                else {
                    tokens.push(token);
                }
                lastParagraphClipped = (cutSrc.length !== src.length);
                src = src.substring(token.raw.length);
                continue;
            }
            // text
            if (token = this.tokenizer.text(src)) {
                src = src.substring(token.raw.length);
                lastToken = tokens[tokens.length - 1];
                if (lastToken && lastToken.type === 'text') {
                    lastToken.raw += '\n' + token.raw;
                    lastToken.text += '\n' + token.text;
                    this.inlineQueue.pop();
                    this.inlineQueue[this.inlineQueue.length - 1].src = lastToken.text;
                }
                else {
                    tokens.push(token);
                }
                continue;
            }
            if (src) {
                const errMsg = 'Infinite loop on byte: ' + src.charCodeAt(0);
                if (this.options.silent) {
                    console.error(errMsg);
                    break;
                }
                else {
                    throw new Error(errMsg);
                }
            }
        }
        this.state.top = true;
        return tokens;
    }
    inline(src, tokens = []) {
        this.inlineQueue.push({ src, tokens });
        return tokens;
    }
    /**
     * Lexing/Compiling
     */
    inlineTokens(src, tokens = []) {
        let token, lastToken, cutSrc;
        // String with links masked to avoid interference with em and strong
        let maskedSrc = src;
        let match;
        let keepPrevChar, prevChar;
        // Mask out reflinks
        if (this.tokens.links) {
            const links = Object.keys(this.tokens.links);
            if (links.length > 0) {
                while ((match = this.tokenizer.rules.inline.reflinkSearch.exec(maskedSrc)) != null) {
                    if (links.includes(match[0].slice(match[0].lastIndexOf('[') + 1, -1))) {
                        maskedSrc = maskedSrc.slice(0, match.index) + '[' + 'a'.repeat(match[0].length - 2) + ']' + maskedSrc.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex);
                    }
                }
            }
        }
        // Mask out other blocks
        while ((match = this.tokenizer.rules.inline.blockSkip.exec(maskedSrc)) != null) {
            maskedSrc = maskedSrc.slice(0, match.index) + '[' + 'a'.repeat(match[0].length - 2) + ']' + maskedSrc.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);
        }
        // Mask out escaped characters
        while ((match = this.tokenizer.rules.inline.anyPunctuation.exec(maskedSrc)) != null) {
            maskedSrc = maskedSrc.slice(0, match.index) + '++' + maskedSrc.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);
        }
        while (src) {
            if (!keepPrevChar) {
                prevChar = '';
            }
            keepPrevChar = false;
            // extensions
            if (this.options.extensions
                && this.options.extensions.inline
                && this.options.extensions.inline.some((extTokenizer) => {
                    if (token = extTokenizer.call({ lexer: this }, src, tokens)) {
                        src = src.substring(token.raw.length);
                        tokens.push(token);
                        return true;
                    }
                    return false;
                })) {
                continue;
            }
            // escape
            if (token = this.tokenizer.escape(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // tag
            if (token = this.tokenizer.tag(src)) {
                src = src.substring(token.raw.length);
                lastToken = tokens[tokens.length - 1];
                if (lastToken && token.type === 'text' && lastToken.type === 'text') {
                    lastToken.raw += token.raw;
                    lastToken.text += token.text;
                }
                else {
                    tokens.push(token);
                }
                continue;
            }
            // link
            if (token = this.tokenizer.link(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // reflink, nolink
            if (token = this.tokenizer.reflink(src, this.tokens.links)) {
                src = src.substring(token.raw.length);
                lastToken = tokens[tokens.length - 1];
                if (lastToken && token.type === 'text' && lastToken.type === 'text') {
                    lastToken.raw += token.raw;
                    lastToken.text += token.text;
                }
                else {
                    tokens.push(token);
                }
                continue;
            }
            // em & strong
            if (token = this.tokenizer.emStrong(src, maskedSrc, prevChar)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // code
            if (token = this.tokenizer.codespan(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // br
            if (token = this.tokenizer.br(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // del (gfm)
            if (token = this.tokenizer.del(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // autolink
            if (token = this.tokenizer.autolink(src)) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // url (gfm)
            if (!this.state.inLink && (token = this.tokenizer.url(src))) {
                src = src.substring(token.raw.length);
                tokens.push(token);
                continue;
            }
            // text
            // prevent inlineText consuming extensions by clipping 'src' to extension start
            cutSrc = src;
            if (this.options.extensions && this.options.extensions.startInline) {
                let startIndex = Infinity;
                const tempSrc = src.slice(1);
                let tempStart;
                this.options.extensions.startInline.forEach((getStartIndex) => {
                    tempStart = getStartIndex.call({ lexer: this }, tempSrc);
                    if (typeof tempStart === 'number' && tempStart >= 0) {
                        startIndex = Math.min(startIndex, tempStart);
                    }
                });
                if (startIndex < Infinity && startIndex >= 0) {
                    cutSrc = src.substring(0, startIndex + 1);
                }
            }
            if (token = this.tokenizer.inlineText(cutSrc)) {
                src = src.substring(token.raw.length);
                if (token.raw.slice(-1) !== '_') { // Track prevChar before string of ____ started
                    prevChar = token.raw.slice(-1);
                }
                keepPrevChar = true;
                lastToken = tokens[tokens.length - 1];
                if (lastToken && lastToken.type === 'text') {
                    lastToken.raw += token.raw;
                    lastToken.text += token.text;
                }
                else {
                    tokens.push(token);
                }
                continue;
            }
            if (src) {
                const errMsg = 'Infinite loop on byte: ' + src.charCodeAt(0);
                if (this.options.silent) {
                    console.error(errMsg);
                    break;
                }
                else {
                    throw new Error(errMsg);
                }
            }
        }
        return tokens;
    }
}

/**
 * Renderer
 */
class _Renderer {
    options;
    constructor(options) {
        this.options = options || _defaults;
    }
    code(code, infostring, escaped) {
        const lang = (infostring || '').match(/^\S*/)?.[0];
        code = code.replace(/\n$/, '') + '\n';
        if (!lang) {
            return '<pre><code>'
                + (escaped ? code : escape$1(code, true))
                + '</code></pre>\n';
        }
        return '<pre><code class="language-'
            + escape$1(lang)
            + '">'
            + (escaped ? code : escape$1(code, true))
            + '</code></pre>\n';
    }
    blockquote(quote) {
        return `<blockquote>\n${quote}</blockquote>\n`;
    }
    html(html, block) {
        return html;
    }
    heading(text, level, raw) {
        // ignore IDs
        return `<h${level}>${text}</h${level}>\n`;
    }
    hr() {
        return '<hr>\n';
    }
    list(body, ordered, start) {
        const type = ordered ? 'ol' : 'ul';
        const startatt = (ordered && start !== 1) ? (' start="' + start + '"') : '';
        return '<' + type + startatt + '>\n' + body + '</' + type + '>\n';
    }
    listitem(text, task, checked) {
        return `<li>${text}</li>\n`;
    }
    checkbox(checked) {
        return '<input '
            + (checked ? 'checked="" ' : '')
            + 'disabled="" type="checkbox">';
    }
    paragraph(text) {
        return `<p>${text}</p>\n`;
    }
    table(header, body) {
        if (body)
            body = `<tbody>${body}</tbody>`;
        return '<table>\n'
            + '<thead>\n'
            + header
            + '</thead>\n'
            + body
            + '</table>\n';
    }
    tablerow(content) {
        return `<tr>\n${content}</tr>\n`;
    }
    tablecell(content, flags) {
        const type = flags.header ? 'th' : 'td';
        const tag = flags.align
            ? `<${type} align="${flags.align}">`
            : `<${type}>`;
        return tag + content + `</${type}>\n`;
    }
    /**
     * span level renderer
     */
    strong(text) {
        return `<strong>${text}</strong>`;
    }
    em(text) {
        return `<em>${text}</em>`;
    }
    codespan(text) {
        return `<code>${text}</code>`;
    }
    br() {
        return '<br>';
    }
    del(text) {
        return `<del>${text}</del>`;
    }
    link(href, title, text) {
        const cleanHref = cleanUrl(href);
        if (cleanHref === null) {
            return text;
        }
        href = cleanHref;
        let out = '<a href="' + href + '"';
        if (title) {
            out += ' title="' + title + '"';
        }
        out += '>' + text + '</a>';
        return out;
    }
    image(href, title, text) {
        const cleanHref = cleanUrl(href);
        if (cleanHref === null) {
            return text;
        }
        href = cleanHref;
        let out = `<img src="${href}" alt="${text}"`;
        if (title) {
            out += ` title="${title}"`;
        }
        out += '>';
        return out;
    }
    text(text) {
        return text;
    }
}

/**
 * TextRenderer
 * returns only the textual part of the token
 */
class _TextRenderer {
    // no need for block level renderers
    strong(text) {
        return text;
    }
    em(text) {
        return text;
    }
    codespan(text) {
        return text;
    }
    del(text) {
        return text;
    }
    html(text) {
        return text;
    }
    text(text) {
        return text;
    }
    link(href, title, text) {
        return '' + text;
    }
    image(href, title, text) {
        return '' + text;
    }
    br() {
        return '';
    }
}

/**
 * Parsing & Compiling
 */
class _Parser {
    options;
    renderer;
    textRenderer;
    constructor(options) {
        this.options = options || _defaults;
        this.options.renderer = this.options.renderer || new _Renderer();
        this.renderer = this.options.renderer;
        this.renderer.options = this.options;
        this.textRenderer = new _TextRenderer();
    }
    /**
     * Static Parse Method
     */
    static parse(tokens, options) {
        const parser = new _Parser(options);
        return parser.parse(tokens);
    }
    /**
     * Static Parse Inline Method
     */
    static parseInline(tokens, options) {
        const parser = new _Parser(options);
        return parser.parseInline(tokens);
    }
    /**
     * Parse Loop
     */
    parse(tokens, top = true) {
        let out = '';
        for (let i = 0; i < tokens.length; i++) {
            const token = tokens[i];
            // Run any renderer extensions
            if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[token.type]) {
                const genericToken = token;
                const ret = this.options.extensions.renderers[genericToken.type].call({ parser: this }, genericToken);
                if (ret !== false || !['space', 'hr', 'heading', 'code', 'table', 'blockquote', 'list', 'html', 'paragraph', 'text'].includes(genericToken.type)) {
                    out += ret || '';
                    continue;
                }
            }
            switch (token.type) {
                case 'space': {
                    continue;
                }
                case 'hr': {
                    out += this.renderer.hr();
                    continue;
                }
                case 'heading': {
                    const headingToken = token;
                    out += this.renderer.heading(this.parseInline(headingToken.tokens), headingToken.depth, unescape$1(this.parseInline(headingToken.tokens, this.textRenderer)));
                    continue;
                }
                case 'code': {
                    const codeToken = token;
                    out += this.renderer.code(codeToken.text, codeToken.lang, !!codeToken.escaped);
                    continue;
                }
                case 'table': {
                    const tableToken = token;
                    let header = '';
                    // header
                    let cell = '';
                    for (let j = 0; j < tableToken.header.length; j++) {
                        cell += this.renderer.tablecell(this.parseInline(tableToken.header[j].tokens), { header: true, align: tableToken.align[j] });
                    }
                    header += this.renderer.tablerow(cell);
                    let body = '';
                    for (let j = 0; j < tableToken.rows.length; j++) {
                        const row = tableToken.rows[j];
                        cell = '';
                        for (let k = 0; k < row.length; k++) {
                            cell += this.renderer.tablecell(this.parseInline(row[k].tokens), { header: false, align: tableToken.align[k] });
                        }
                        body += this.renderer.tablerow(cell);
                    }
                    out += this.renderer.table(header, body);
                    continue;
                }
                case 'blockquote': {
                    const blockquoteToken = token;
                    const body = this.parse(blockquoteToken.tokens);
                    out += this.renderer.blockquote(body);
                    continue;
                }
                case 'list': {
                    const listToken = token;
                    const ordered = listToken.ordered;
                    const start = listToken.start;
                    const loose = listToken.loose;
                    let body = '';
                    for (let j = 0; j < listToken.items.length; j++) {
                        const item = listToken.items[j];
                        const checked = item.checked;
                        const task = item.task;
                        let itemBody = '';
                        if (item.task) {
                            const checkbox = this.renderer.checkbox(!!checked);
                            if (loose) {
                                if (item.tokens.length > 0 && item.tokens[0].type === 'paragraph') {
                                    item.tokens[0].text = checkbox + ' ' + item.tokens[0].text;
                                    if (item.tokens[0].tokens && item.tokens[0].tokens.length > 0 && item.tokens[0].tokens[0].type === 'text') {
                                        item.tokens[0].tokens[0].text = checkbox + ' ' + item.tokens[0].tokens[0].text;
                                    }
                                }
                                else {
                                    item.tokens.unshift({
                                        type: 'text',
                                        text: checkbox + ' '
                                    });
                                }
                            }
                            else {
                                itemBody += checkbox + ' ';
                            }
                        }
                        itemBody += this.parse(item.tokens, loose);
                        body += this.renderer.listitem(itemBody, task, !!checked);
                    }
                    out += this.renderer.list(body, ordered, start);
                    continue;
                }
                case 'html': {
                    const htmlToken = token;
                    out += this.renderer.html(htmlToken.text, htmlToken.block);
                    continue;
                }
                case 'paragraph': {
                    const paragraphToken = token;
                    out += this.renderer.paragraph(this.parseInline(paragraphToken.tokens));
                    continue;
                }
                case 'text': {
                    let textToken = token;
                    let body = textToken.tokens ? this.parseInline(textToken.tokens) : textToken.text;
                    while (i + 1 < tokens.length && tokens[i + 1].type === 'text') {
                        textToken = tokens[++i];
                        body += '\n' + (textToken.tokens ? this.parseInline(textToken.tokens) : textToken.text);
                    }
                    out += top ? this.renderer.paragraph(body) : body;
                    continue;
                }
                default: {
                    const errMsg = 'Token with "' + token.type + '" type was not found.';
                    if (this.options.silent) {
                        console.error(errMsg);
                        return '';
                    }
                    else {
                        throw new Error(errMsg);
                    }
                }
            }
        }
        return out;
    }
    /**
     * Parse Inline Tokens
     */
    parseInline(tokens, renderer) {
        renderer = renderer || this.renderer;
        let out = '';
        for (let i = 0; i < tokens.length; i++) {
            const token = tokens[i];
            // Run any renderer extensions
            if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[token.type]) {
                const ret = this.options.extensions.renderers[token.type].call({ parser: this }, token);
                if (ret !== false || !['escape', 'html', 'link', 'image', 'strong', 'em', 'codespan', 'br', 'del', 'text'].includes(token.type)) {
                    out += ret || '';
                    continue;
                }
            }
            switch (token.type) {
                case 'escape': {
                    const escapeToken = token;
                    out += renderer.text(escapeToken.text);
                    break;
                }
                case 'html': {
                    const tagToken = token;
                    out += renderer.html(tagToken.text);
                    break;
                }
                case 'link': {
                    const linkToken = token;
                    out += renderer.link(linkToken.href, linkToken.title, this.parseInline(linkToken.tokens, renderer));
                    break;
                }
                case 'image': {
                    const imageToken = token;
                    out += renderer.image(imageToken.href, imageToken.title, imageToken.text);
                    break;
                }
                case 'strong': {
                    const strongToken = token;
                    out += renderer.strong(this.parseInline(strongToken.tokens, renderer));
                    break;
                }
                case 'em': {
                    const emToken = token;
                    out += renderer.em(this.parseInline(emToken.tokens, renderer));
                    break;
                }
                case 'codespan': {
                    const codespanToken = token;
                    out += renderer.codespan(codespanToken.text);
                    break;
                }
                case 'br': {
                    out += renderer.br();
                    break;
                }
                case 'del': {
                    const delToken = token;
                    out += renderer.del(this.parseInline(delToken.tokens, renderer));
                    break;
                }
                case 'text': {
                    const textToken = token;
                    out += renderer.text(textToken.text);
                    break;
                }
                default: {
                    const errMsg = 'Token with "' + token.type + '" type was not found.';
                    if (this.options.silent) {
                        console.error(errMsg);
                        return '';
                    }
                    else {
                        throw new Error(errMsg);
                    }
                }
            }
        }
        return out;
    }
}

class _Hooks {
    options;
    constructor(options) {
        this.options = options || _defaults;
    }
    static passThroughHooks = new Set([
        'preprocess',
        'postprocess',
        'processAllTokens'
    ]);
    /**
     * Process markdown before marked
     */
    preprocess(markdown) {
        return markdown;
    }
    /**
     * Process HTML after marked is finished
     */
    postprocess(html) {
        return html;
    }
    /**
     * Process all tokens before walk tokens
     */
    processAllTokens(tokens) {
        return tokens;
    }
}

class Marked {
    defaults = _getDefaults();
    options = this.setOptions;
    parse = this.#parseMarkdown(_Lexer.lex, _Parser.parse);
    parseInline = this.#parseMarkdown(_Lexer.lexInline, _Parser.parseInline);
    Parser = _Parser;
    Renderer = _Renderer;
    TextRenderer = _TextRenderer;
    Lexer = _Lexer;
    Tokenizer = _Tokenizer;
    Hooks = _Hooks;
    constructor(...args) {
        this.use(...args);
    }
    /**
     * Run callback for every token
     */
    walkTokens(tokens, callback) {
        let values = [];
        for (const token of tokens) {
            values = values.concat(callback.call(this, token));
            switch (token.type) {
                case 'table': {
                    const tableToken = token;
                    for (const cell of tableToken.header) {
                        values = values.concat(this.walkTokens(cell.tokens, callback));
                    }
                    for (const row of tableToken.rows) {
                        for (const cell of row) {
                            values = values.concat(this.walkTokens(cell.tokens, callback));
                        }
                    }
                    break;
                }
                case 'list': {
                    const listToken = token;
                    values = values.concat(this.walkTokens(listToken.items, callback));
                    break;
                }
                default: {
                    const genericToken = token;
                    if (this.defaults.extensions?.childTokens?.[genericToken.type]) {
                        this.defaults.extensions.childTokens[genericToken.type].forEach((childTokens) => {
                            const tokens = genericToken[childTokens].flat(Infinity);
                            values = values.concat(this.walkTokens(tokens, callback));
                        });
                    }
                    else if (genericToken.tokens) {
                        values = values.concat(this.walkTokens(genericToken.tokens, callback));
                    }
                }
            }
        }
        return values;
    }
    use(...args) {
        const extensions = this.defaults.extensions || { renderers: {}, childTokens: {} };
        args.forEach((pack) => {
            // copy options to new object
            const opts = { ...pack };
            // set async to true if it was set to true before
            opts.async = this.defaults.async || opts.async || false;
            // ==-- Parse "addon" extensions --== //
            if (pack.extensions) {
                pack.extensions.forEach((ext) => {
                    if (!ext.name) {
                        throw new Error('extension name required');
                    }
                    if ('renderer' in ext) { // Renderer extensions
                        const prevRenderer = extensions.renderers[ext.name];
                        if (prevRenderer) {
                            // Replace extension with func to run new extension but fall back if false
                            extensions.renderers[ext.name] = function (...args) {
                                let ret = ext.renderer.apply(this, args);
                                if (ret === false) {
                                    ret = prevRenderer.apply(this, args);
                                }
                                return ret;
                            };
                        }
                        else {
                            extensions.renderers[ext.name] = ext.renderer;
                        }
                    }
                    if ('tokenizer' in ext) { // Tokenizer Extensions
                        if (!ext.level || (ext.level !== 'block' && ext.level !== 'inline')) {
                            throw new Error("extension level must be 'block' or 'inline'");
                        }
                        const extLevel = extensions[ext.level];
                        if (extLevel) {
                            extLevel.unshift(ext.tokenizer);
                        }
                        else {
                            extensions[ext.level] = [ext.tokenizer];
                        }
                        if (ext.start) { // Function to check for start of token
                            if (ext.level === 'block') {
                                if (extensions.startBlock) {
                                    extensions.startBlock.push(ext.start);
                                }
                                else {
                                    extensions.startBlock = [ext.start];
                                }
                            }
                            else if (ext.level === 'inline') {
                                if (extensions.startInline) {
                                    extensions.startInline.push(ext.start);
                                }
                                else {
                                    extensions.startInline = [ext.start];
                                }
                            }
                        }
                    }
                    if ('childTokens' in ext && ext.childTokens) { // Child tokens to be visited by walkTokens
                        extensions.childTokens[ext.name] = ext.childTokens;
                    }
                });
                opts.extensions = extensions;
            }
            // ==-- Parse "overwrite" extensions --== //
            if (pack.renderer) {
                const renderer = this.defaults.renderer || new _Renderer(this.defaults);
                for (const prop in pack.renderer) {
                    if (!(prop in renderer)) {
                        throw new Error(`renderer '${prop}' does not exist`);
                    }
                    if (prop === 'options') {
                        // ignore options property
                        continue;
                    }
                    const rendererProp = prop;
                    const rendererFunc = pack.renderer[rendererProp];
                    const prevRenderer = renderer[rendererProp];
                    // Replace renderer with func to run extension, but fall back if false
                    renderer[rendererProp] = (...args) => {
                        let ret = rendererFunc.apply(renderer, args);
                        if (ret === false) {
                            ret = prevRenderer.apply(renderer, args);
                        }
                        return ret || '';
                    };
                }
                opts.renderer = renderer;
            }
            if (pack.tokenizer) {
                const tokenizer = this.defaults.tokenizer || new _Tokenizer(this.defaults);
                for (const prop in pack.tokenizer) {
                    if (!(prop in tokenizer)) {
                        throw new Error(`tokenizer '${prop}' does not exist`);
                    }
                    if (['options', 'rules', 'lexer'].includes(prop)) {
                        // ignore options, rules, and lexer properties
                        continue;
                    }
                    const tokenizerProp = prop;
                    const tokenizerFunc = pack.tokenizer[tokenizerProp];
                    const prevTokenizer = tokenizer[tokenizerProp];
                    // Replace tokenizer with func to run extension, but fall back if false
                    // @ts-expect-error cannot type tokenizer function dynamically
                    tokenizer[tokenizerProp] = (...args) => {
                        let ret = tokenizerFunc.apply(tokenizer, args);
                        if (ret === false) {
                            ret = prevTokenizer.apply(tokenizer, args);
                        }
                        return ret;
                    };
                }
                opts.tokenizer = tokenizer;
            }
            // ==-- Parse Hooks extensions --== //
            if (pack.hooks) {
                const hooks = this.defaults.hooks || new _Hooks();
                for (const prop in pack.hooks) {
                    if (!(prop in hooks)) {
                        throw new Error(`hook '${prop}' does not exist`);
                    }
                    if (prop === 'options') {
                        // ignore options property
                        continue;
                    }
                    const hooksProp = prop;
                    const hooksFunc = pack.hooks[hooksProp];
                    const prevHook = hooks[hooksProp];
                    if (_Hooks.passThroughHooks.has(prop)) {
                        // @ts-expect-error cannot type hook function dynamically
                        hooks[hooksProp] = (arg) => {
                            if (this.defaults.async) {
                                return Promise.resolve(hooksFunc.call(hooks, arg)).then(ret => {
                                    return prevHook.call(hooks, ret);
                                });
                            }
                            const ret = hooksFunc.call(hooks, arg);
                            return prevHook.call(hooks, ret);
                        };
                    }
                    else {
                        // @ts-expect-error cannot type hook function dynamically
                        hooks[hooksProp] = (...args) => {
                            let ret = hooksFunc.apply(hooks, args);
                            if (ret === false) {
                                ret = prevHook.apply(hooks, args);
                            }
                            return ret;
                        };
                    }
                }
                opts.hooks = hooks;
            }
            // ==-- Parse WalkTokens extensions --== //
            if (pack.walkTokens) {
                const walkTokens = this.defaults.walkTokens;
                const packWalktokens = pack.walkTokens;
                opts.walkTokens = function (token) {
                    let values = [];
                    values.push(packWalktokens.call(this, token));
                    if (walkTokens) {
                        values = values.concat(walkTokens.call(this, token));
                    }
                    return values;
                };
            }
            this.defaults = { ...this.defaults, ...opts };
        });
        return this;
    }
    setOptions(opt) {
        this.defaults = { ...this.defaults, ...opt };
        return this;
    }
    lexer(src, options) {
        return _Lexer.lex(src, options ?? this.defaults);
    }
    parser(tokens, options) {
        return _Parser.parse(tokens, options ?? this.defaults);
    }
    #parseMarkdown(lexer, parser) {
        return (src, options) => {
            const origOpt = { ...options };
            const opt = { ...this.defaults, ...origOpt };
            // Show warning if an extension set async to true but the parse was called with async: false
            if (this.defaults.async === true && origOpt.async === false) {
                if (!opt.silent) {
                    console.warn('marked(): The async option was set to true by an extension. The async: false option sent to parse will be ignored.');
                }
                opt.async = true;
            }
            const throwError = this.#onError(!!opt.silent, !!opt.async);
            // throw error in case of non string input
            if (typeof src === 'undefined' || src === null) {
                return throwError(new Error('marked(): input parameter is undefined or null'));
            }
            if (typeof src !== 'string') {
                return throwError(new Error('marked(): input parameter is of type '
                    + Object.prototype.toString.call(src) + ', string expected'));
            }
            if (opt.hooks) {
                opt.hooks.options = opt;
            }
            if (opt.async) {
                return Promise.resolve(opt.hooks ? opt.hooks.preprocess(src) : src)
                    .then(src => lexer(src, opt))
                    .then(tokens => opt.hooks ? opt.hooks.processAllTokens(tokens) : tokens)
                    .then(tokens => opt.walkTokens ? Promise.all(this.walkTokens(tokens, opt.walkTokens)).then(() => tokens) : tokens)
                    .then(tokens => parser(tokens, opt))
                    .then(html => opt.hooks ? opt.hooks.postprocess(html) : html)
                    .catch(throwError);
            }
            try {
                if (opt.hooks) {
                    src = opt.hooks.preprocess(src);
                }
                let tokens = lexer(src, opt);
                if (opt.hooks) {
                    tokens = opt.hooks.processAllTokens(tokens);
                }
                if (opt.walkTokens) {
                    this.walkTokens(tokens, opt.walkTokens);
                }
                let html = parser(tokens, opt);
                if (opt.hooks) {
                    html = opt.hooks.postprocess(html);
                }
                return html;
            }
            catch (e) {
                return throwError(e);
            }
        };
    }
    #onError(silent, async) {
        return (e) => {
            e.message += '\nPlease report this to https://github.com/markedjs/marked.';
            if (silent) {
                const msg = '<p>An error occurred:</p><pre>'
                    + escape$1(e.message + '', true)
                    + '</pre>';
                if (async) {
                    return Promise.resolve(msg);
                }
                return msg;
            }
            if (async) {
                return Promise.reject(e);
            }
            throw e;
        };
    }
}

const markedInstance = new Marked();
function marked(src, opt) {
    return markedInstance.parse(src, opt);
}
/**
 * Sets the default options.
 *
 * @param options Hash of options
 */
marked.options =
    marked.setOptions = function (options) {
        markedInstance.setOptions(options);
        marked.defaults = markedInstance.defaults;
        changeDefaults(marked.defaults);
        return marked;
    };
/**
 * Gets the original marked default options.
 */
marked.getDefaults = _getDefaults;
marked.defaults = _defaults;
/**
 * Use Extension
 */
marked.use = function (...args) {
    markedInstance.use(...args);
    marked.defaults = markedInstance.defaults;
    changeDefaults(marked.defaults);
    return marked;
};
/**
 * Run callback for every token
 */
marked.walkTokens = function (tokens, callback) {
    return markedInstance.walkTokens(tokens, callback);
};
/**
 * Compiles markdown to HTML without enclosing `p` tag.
 *
 * @param src String of markdown source to be compiled
 * @param options Hash of options
 * @return String of compiled HTML
 */
marked.parseInline = markedInstance.parseInline;
/**
 * Expose
 */
marked.Parser = _Parser;
marked.parser = _Parser.parse;
marked.Renderer = _Renderer;
marked.TextRenderer = _TextRenderer;
marked.Lexer = _Lexer;
marked.lexer = _Lexer.lex;
marked.Tokenizer = _Tokenizer;
marked.Hooks = _Hooks;
marked.parse = marked;
marked.options;
marked.setOptions;
marked.use;
marked.walkTokens;
marked.parseInline;
_Parser.parse;
_Lexer.lex;

var _tmpl$$i = /* @__PURE__ */ template(`<div><table class="w-full text-sm text-left text-gray-500 dark:text-gray-400 mt-4"><thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"><tr><th scope=col class="py-3 px-6">Name</th><th scope=col class="py-3 px-6">Type</th><th scope=col class="py-3 px-6">Description</th></tr></thead><tbody>`), _tmpl$2$2 = /* @__PURE__ */ template(`<tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700"><th scope=row class="py-4 px-6 font-medium text-gray-900 whitespace-nowrap dark:text-white"></th><td class="py-4 px-6"></td><td class="py-4 px-6">`);
function DetailCardOutputTable(props) {
  return (() => {
    var _el$ = _tmpl$$i(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling;
    insert(_el$4, createComponent(For, {
      get each() {
        return props.outputColumns;
      },
      children: (col) => (() => {
        var _el$5 = _tmpl$2$2(), _el$6 = _el$5.firstChild, _el$7 = _el$6.nextSibling, _el$8 = _el$7.nextSibling;
        insert(_el$6, () => col.title);
        insert(_el$7, () => col.type);
        insert(_el$8, () => col.desc, null);
        insert(_el$8, createComponent(Show, {
          get when() {
            return col.table;
          },
          get children() {
            return createComponent(DetailCardOutputTable, {
              get outputColumns() {
                return col.table_headers;
              }
            });
          }
        }), null);
        return _el$5;
      })()
    }));
    return _el$;
  })();
}

var _tmpl$$h = /* @__PURE__ */ template(`<div><h3 class="text-lg font-semibold mt-8">Developer information</h3><div class="overflow-hidden bg-white shadow sm:rounded-lg mt-4"><div class="border-t border-gray-200 px-4 py-5 sm:px-6"><dl class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2"><div class=sm:col-span-1><dt class="text-sm font-medium text-gray-500">Name</dt><dd class="mt-1 text-sm text-gray-900"></dd></div><div class=sm:col-span-1><dt class="text-sm font-medium text-gray-500">Organization</dt><dd class="mt-1 text-sm text-gray-900"></dd></div><div class=sm:col-span-1><dt class="text-sm font-medium text-gray-500">Email address</dt><dd class="mt-1 text-sm text-gray-900"><a></a></dd></div><div class=sm:col-span-1><dt class="text-sm font-medium text-gray-500">Website</dt><dd class="mt-1 text-sm text-gray-900"><a></a></dd></div><div class=sm:col-span-2><dt class="text-sm font-medium text-gray-500">Citation</dt><dd class="mt-1 text-sm text-gray-900"></dd></div></dl></div></div> `);
function DetailCardDeveloper(props) {
  return (() => {
    var _el$ = _tmpl$$h(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild, _el$7 = _el$6.firstChild, _el$8 = _el$7.nextSibling, _el$9 = _el$6.nextSibling, _el$10 = _el$9.firstChild, _el$11 = _el$10.nextSibling, _el$12 = _el$9.nextSibling, _el$13 = _el$12.firstChild, _el$14 = _el$13.nextSibling, _el$15 = _el$14.firstChild, _el$16 = _el$12.nextSibling, _el$17 = _el$16.firstChild, _el$18 = _el$17.nextSibling, _el$19 = _el$18.firstChild, _el$20 = _el$16.nextSibling, _el$21 = _el$20.firstChild, _el$22 = _el$21.nextSibling;
    insert(_el$8, () => props.module.name);
    insert(_el$11, () => props.module.organization);
    insert(_el$15, () => props.module.email);
    insert(_el$19, () => props.module.website);
    insert(_el$22, () => props.module.citation);
    createRenderEffect((_p$) => {
      var _v$ = "mailto:" + props.module.email, _v$2 = props.module.website;
      _v$ !== _p$.e && setAttribute(_el$15, "href", _p$.e = _v$);
      _v$2 !== _p$.t && setAttribute(_el$19, "href", _p$.t = _v$2);
      return _p$;
    }, {
      e: void 0,
      t: void 0
    });
    return _el$;
  })();
}

var _tmpl$$g = /* @__PURE__ */ template(`<div><h3 class="text-lg font-semibold mt-8">Data information</h3><div class="overflow-hidden bg-white shadow sm:rounded-lg mt-4"><div class="border-t border-gray-200 px-4 py-5 sm:px-6"><dl class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2"><div class=sm:col-span-1><dt class="text-sm font-medium text-gray-500">Name</dt><dd class="mt-1 text-sm text-gray-900"></dd></div><div class=sm:col-span-1><dt class="text-sm font-medium text-gray-500">Organization</dt><dd class="mt-1 text-sm text-gray-900"></dd></div><div class=sm:col-span-1><dt class="text-sm font-medium text-gray-500">Email address</dt><dd class="mt-1 text-sm text-gray-900"><a></a></dd></div><div class=sm:col-span-1><dt class="text-sm font-medium text-gray-500">Website</dt><dd class="mt-1 text-sm text-gray-900"><a></a></dd></div><div class=sm:col-span-2><dt class="text-sm font-medium text-gray-500">Citation</dt><dd class="mt-1 text-sm text-gray-900"></dd></div></dl></div></div> `);
function DetailCardData(props) {
  return (() => {
    var _el$ = _tmpl$$g(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild, _el$7 = _el$6.firstChild, _el$8 = _el$7.nextSibling, _el$9 = _el$6.nextSibling, _el$10 = _el$9.firstChild, _el$11 = _el$10.nextSibling, _el$12 = _el$9.nextSibling, _el$13 = _el$12.firstChild, _el$14 = _el$13.nextSibling, _el$15 = _el$14.firstChild, _el$16 = _el$12.nextSibling, _el$17 = _el$16.firstChild, _el$18 = _el$17.nextSibling, _el$19 = _el$18.firstChild, _el$20 = _el$16.nextSibling, _el$21 = _el$20.firstChild, _el$22 = _el$21.nextSibling;
    insert(_el$8, () => props.data.name);
    insert(_el$11, () => props.data.organization);
    insert(_el$15, () => props.data.email);
    insert(_el$19, () => props.data.website);
    insert(_el$22, () => props.data.citation);
    createRenderEffect((_p$) => {
      var _v$ = "mailto:" + props.data.email, _v$2 = props.data.website;
      _v$ !== _p$.e && setAttribute(_el$15, "href", _p$.e = _v$);
      _v$2 !== _p$.t && setAttribute(_el$19, "href", _p$.t = _v$2);
      return _p$;
    }, {
      e: void 0,
      t: void 0
    });
    return _el$;
  })();
}

var _tmpl$$f = /* @__PURE__ */ template(`<div class="absolute w-full h-full bg-white opacity-1 top-0 left-0 z-30"><div class="absolute opacity-1 top-[5vh] left-[10vw] w-[80vw] h-[80vh] overflow-auto bg-gray-50 z-30 m-4 p-8"><img class="w-0 top-0 right-0 rounded-lg"><div class="-ml-1 mb-2"><span class="relative inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800"></span><span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800"></span><span class="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">Installed</span><span class="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">Update available</span></div><div class="readme opacity-1 list-decimal mb-8"></div><h3 class="text-lg font-semibold">Module output</h3></div><div class="absolute top-0 right-0 cursor-pointer">`);
const ocImgRegex = /img src=\"(?!http)/g;
function DetailCard() {
  const {
    detailModuleName,
    setDetailModuleName,
    showDetailCard,
    setShowDetailCard
  } = gvDetailCardState;
  const {
    serverUrl
  } = gvServer;
  const [markdown, {
    mutate,
    refetch
  }] = createResource(detailModuleName, fetchReadme);
  const {
    remoteModules
  } = gvRemoteModules;
  const {
    installed,
    updateAvailableForModule
  } = gvModuleInstallStates;
  const [moduleInfo, setModuleInfo] = createSignal(null);
  createEffect(function() {
    if (detailModuleName() != null) {
      setModuleInfo(remoteModules[detailModuleName()]);
    }
  });
  async function fetchReadme(moduleName) {
    try {
      const res = await axios.get(serverUrl + "/store/getreadme", {
        params: {
          module_name: moduleName
        }
      });
      let html = marked.parse(res.data);
      html = html.replace(ocImgRegex, 'img src="https://karchinlab.org/cravatstore/modules/' + moduleName + "/" + moduleInfo().latest_version + "/");
      return html;
    } catch (err) {
      console.error(err);
      handleError(err);
    }
  }
  function onClickX() {
    setShowDetailCard(false);
    setDetailModuleName(null);
    mutate(null);
  }
  return createComponent(Show, {
    get when() {
      return createMemo(() => !!showDetailCard())() && markdown() != null;
    },
    get children() {
      var _el$ = _tmpl$$f(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling, _el$5 = _el$4.firstChild, _el$6 = _el$5.nextSibling, _el$7 = _el$6.nextSibling, _el$8 = _el$7.nextSibling, _el$9 = _el$4.nextSibling; _el$9.nextSibling; var _el$11 = _el$2.nextSibling;
      insert(_el$5, () => moduleInfo().type);
      insert(_el$6, () => getSizeString(moduleInfo().size));
      insert(_el$2, createComponent(DetailCardOutputTable, {
        get outputColumns() {
          return moduleInfo().output_columns;
        }
      }), null);
      insert(_el$2, createComponent(DetailCardDeveloper, {
        get module() {
          return moduleInfo().developer.module;
        }
      }), null);
      insert(_el$2, createComponent(DetailCardData, {
        get data() {
          return moduleInfo().developer.data;
        }
      }), null);
      _el$11.$$click = onClickX;
      insert(_el$11, createComponent(HiOutlineXMark, {
        color: "rgb(107 114 128)",
        size: 64
      }));
      createRenderEffect((_p$) => {
        var _v$ = `${serverUrl}/store/remotelogo?module=${moduleInfo().name}&store=${moduleInfo().store}`, _v$2 = !installed(detailModuleName()), _v$3 = !updateAvailableForModule(detailModuleName()), _v$4 = markdown();
        _v$ !== _p$.e && setAttribute(_el$3, "src", _p$.e = _v$);
        _v$2 !== _p$.t && _el$7.classList.toggle("hidden", _p$.t = _v$2);
        _v$3 !== _p$.a && _el$8.classList.toggle("hidden", _p$.a = _v$3);
        _v$4 !== _p$.o && (_el$9.innerHTML = _p$.o = _v$4);
        return _p$;
      }, {
        e: void 0,
        t: void 0,
        a: void 0,
        o: void 0
      });
      return _el$;
    }
  });
}
delegateEvents(["click"]);

var _tmpl$$e = /* @__PURE__ */ template(`<div id=error-dialog class="relative z-10"aria-labelledby=modal-title role=dialog aria-modal=true><div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div><div class="fixed inset-0 z-10 overflow-y-auto"><div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"><div><div><div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100"><svg class="h-6 w-6 text-red-600"xmlns=http://www.w3.org/2000/svg fill=none viewBox="0 0 24 24"stroke-width=1.5 stroke=currentColor aria-hidden=true><path stroke-linecap=round stroke-linejoin=round d="M12 10.5v3.75m-9.303 3.376C1.83 19.126 2.914 21 4.645 21h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 4.88c-.866-1.501-3.032-1.501-3.898 0L2.697 17.626zM12 17.25h.007v.008H12v-.008z"></path></svg></div><div class="mt-3 text-center sm:mt-5"><h3 class="text-lg font-medium leading-6 text-gray-900"></h3><div class=mt-2><p class="text-sm text-gray-500"></p></div></div></div><div class="mt-5 sm:mt-6"><button type=button class="inline-flex w-full justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:text-sm">Dismiss`);
function ErrorDialog(props) {
  const {
    showErrorDialog,
    setShowErrorDialog,
    errorDialogTitle,
    errorDialogText,
    getErrorText,
    showDismiss
  } = gvErrorDialogState;
  let width = props.width;
  if (!width) {
    width = "[48rem]";
  }
  return createComponent(Show, {
    get when() {
      return showErrorDialog();
    },
    get children() {
      var _el$ = _tmpl$$e(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild, _el$7 = _el$6.firstChild, _el$8 = _el$7.nextSibling, _el$9 = _el$8.firstChild, _el$10 = _el$9.nextSibling, _el$11 = _el$10.firstChild, _el$12 = _el$6.nextSibling, _el$13 = _el$12.firstChild;
      className(_el$5, `relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:p-6 w-${width}`);
      insert(_el$9, errorDialogTitle);
      insert(_el$11, getErrorText);
      _el$13.$$click = setShowErrorDialog;
      _el$13.$$clickData = false;
      createRenderEffect((_p$) => {
        var _v$ = {
          "sm:max-w-3xl": errorDialogText().length > 200
        }, _v$2 = !showDismiss();
        _p$.e = classList(_el$5, _v$, _p$.e);
        _v$2 !== _p$.t && _el$12.classList.toggle("hidden", _p$.t = _v$2);
        return _p$;
      }, {
        e: void 0,
        t: void 0
      });
      return _el$;
    }
  });
}
delegateEvents(["click"]);

var _tmpl$$d = /* @__PURE__ */ template(`<div><div class=mt-4><label for=email class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Email</label><input type=email name=email class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white"placeholder=name@company.com required></div><div><span class=text-orange-500></span></div><div class=mt-4><label for=password class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Password</label><input type=password name=password placeholder=•••••••• class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white"required></div><div><span class=text-orange-500>`);
function EmailPassword(props) {
  const {
    email,
    password,
    setEmail,
    setPassword,
    errorInEmail,
    errorInPassword,
    checkEmailAndPassword,
    emailErrorMsg,
    passwordErrorMsg
  } = gvEmail;
  function readyToSubmit() {
    return !errorInEmail() && !errorInPassword();
  }
  function onKeyupEmail(evt) {
    setEmail(evt.target.value);
    checkEmailAndPassword();
    if (evt.keyCode == 13 && readyToSubmit()) {
      props.submit("email");
    }
  }
  function onKeyupPassword(evt) {
    setPassword(evt.target.value);
    checkEmailAndPassword();
    if (evt.keyCode == 13 && readyToSubmit()) {
      props.submit("email");
    }
  }
  return (() => {
    var _el$ = _tmpl$$d(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling, _el$5 = _el$2.nextSibling, _el$6 = _el$5.firstChild, _el$7 = _el$5.nextSibling, _el$8 = _el$7.firstChild, _el$9 = _el$8.nextSibling, _el$10 = _el$7.nextSibling, _el$11 = _el$10.firstChild;
    _el$4.$$keyup = onKeyupEmail;
    insert(_el$6, emailErrorMsg);
    _el$9.$$keyup = onKeyupPassword;
    insert(_el$11, passwordErrorMsg);
    createRenderEffect(() => _el$4.value = email());
    createRenderEffect(() => _el$9.value = password());
    return _el$;
  })();
}
delegateEvents(["keyup"]);

var _tmpl$$c = /* @__PURE__ */ template(`<div class=flex><div><a href=#>Forgot password?</a><button type=submit class="flex justify-center w-full text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 mt-4"><div class=flex><p>Sign in`);
function SignIn(props) {
  const [loggingIn, setLogginIn] = createSignal(false);
  const [showOkDialog, setShowOkDialog] = createSignal(false);
  const [okDialogTitle, setOkDialogTitle] = createSignal(null);
  const [okDialogText, setOkDialogText] = createSignal(null);
  const {
    setShowErrorDialog,
    setErrorDialogTitle,
    setErrorDialogText
  } = gvErrorDialogState;
  const errorCodeToText = {
    "auth/user-not-found": "Account was not found. Please sign up first.",
    "auth/account-exists-with-different-credential": "Account exists with different credential.",
    "auth/wrong-password": "Wrong password. Please check your password or use Forget Your Password? link.",
    "auth/missing-email": "Please provide an email address.",
    "missing-password": "Please provide a password.",
    "account-exists": "Account already exists.",
    "auth/too-many-requests": "Too many failed attempts. Wait for a while and try again, or use Forgot your password? link."
  };
  const {
    email,
    password,
    errorInEmail
  } = gvEmail;
  const {
    auth
  } = gvFirebase;
  let okDialogCallback = () => {
    setShowOkDialog(false);
  };
  function handleError(err, title) {
    if (err.response) {
      err = err.response.data;
    }
    if (err.code == "auth/popup-closed-by-user") {
      setLogginIn(false);
      return;
    }
    setErrorDialogTitle(title);
    let text = errorCodeToText[err.code];
    if (text) {
      setErrorDialogText(text);
    } else {
      setErrorDialogText("Error code: " + err.code);
      console.error(err);
    }
    setShowErrorDialog(true);
  }
  function signInWithEmail() {
    setLogginIn(true);
    signInWithEmailAndPassword(auth(), email(), password()).then(function(_) {
      setLogginIn(false);
      if (props.signedInCallback) {
        props.signedInCallback();
      }
    }).catch(function(err) {
      handleError(err, "Login failed");
      setLogginIn(false);
    });
  }
  function resetPassword() {
    if (!errorInEmail()) {
      sendPasswordResetEmail(auth(), email()).then(function() {
        setOkDialogTitle("Success");
        setOkDialogText("Please check your email for a password reset link.");
        setShowOkDialog(true);
      }).catch(function(err) {
        handleError(err, "Password reset failed");
      });
    }
  }
  function getWidth() {
    if (props.width) {
      return props.width;
    } else {
      return "64";
    }
  }
  return (() => {
    var _el$ = _tmpl$$c(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild;
    insert(_el$2, createComponent(EmailPassword, {
      submit: signInWithEmail
    }), _el$3);
    _el$3.$$click = resetPassword;
    _el$4.$$click = signInWithEmail;
    insert(_el$5, createComponent(InlineSpinner, {
      get show() {
        return loggingIn();
      }
    }), _el$6);
    insert(_el$, createComponent(ErrorDialog, {}), null);
    insert(_el$, createComponent(Show, {
      get when() {
        return showOkDialog();
      },
      get children() {
        return createComponent(OkDialog, {
          get title() {
            return okDialogTitle();
          },
          get text() {
            return okDialogText();
          },
          callback: okDialogCallback
        });
      }
    }), null);
    createRenderEffect((_p$) => {
      var _v$ = "w-[" + getWidth() + "rem]", _v$2 = "text-sm font-medium text-blue-600 hover:underline dark:text-primary-500" + props.addlClass, _v$3 = !!errorInEmail(), _v$4 = !!errorInEmail();
      _v$ !== _p$.e && className(_el$2, _p$.e = _v$);
      _v$2 !== _p$.t && className(_el$3, _p$.t = _v$2);
      _v$3 !== _p$.a && _el$3.classList.toggle("pointer-events-none", _p$.a = _v$3);
      _v$4 !== _p$.o && _el$3.classList.toggle("text-blue-100", _p$.o = _v$4);
      return _p$;
    }, {
      e: void 0,
      t: void 0,
      a: void 0,
      o: void 0
    });
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$b = /* @__PURE__ */ template(`<div class=flex><div><div><button id=signup_btn type=submit class="flex justify-center mt-4 flex w-full justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"><div class=flex><p>Sign up`);
function SignUp(props) {
  const [signingIn, setSigningIn] = createSignal(false);
  const [showOkDialog, setShowOkDialog] = createSignal(false);
  const [okDialogTitle, setOkDialogTitle] = createSignal(null);
  const [okDialogText, setOkDialogText] = createSignal(null);
  const {
    setShowErrorDialog,
    setErrorDialogTitle,
    setErrorDialogText
  } = gvErrorDialogState;
  const errorCodeToText = {
    "auth/user-not-found": "Account was not found. Please sign up first.",
    "auth/account-exists-with-different-credential": "Account exists with different credential.",
    "auth/wrong-password": "Wrong password. Please check your password or use Forget Your Password? link.",
    "auth/missing-email": "Please provide an email address.",
    "missing-password": "Please provide a password.",
    "account-exists": "Account already exists.",
    "auth/too-many-requests": "Too many failed attempts. Wait for a while and try again, or use Forgot your password? link."
  };
  const {
    serverUrl,
    withCredentials
  } = gvServer;
  const {
    email,
    password,
    errorInEmail,
    errorInPassword
  } = gvEmail;
  const {
    setLogged,
    setShowAuth
  } = gvLogin;
  let okDialogCallback = () => {
    setShowOkDialog(false);
  };
  function getWidth() {
    if (props.width) {
      return props.width;
    } else {
      return "64";
    }
  }
  function readyToSubmit() {
    return !errorInEmail() && !errorInPassword();
  }
  function handleError(err, title) {
    if (err.response) {
      err = err.response.data;
    }
    if (err.code == "auth/popup-closed-by-user") {
      return;
    }
    setErrorDialogTitle(title);
    let text = errorCodeToText[err.code];
    if (text) {
      setErrorDialogText(text);
    } else {
      setErrorDialogText("Error code: " + err.code);
      console.error(err);
    }
    setShowErrorDialog(true);
  }
  function signup() {
    setSigningIn(true);
    axios.post(serverUrl + "/server/signup", {
      email: email(),
      password: password(),
      newSetup: props.newSetup
    }, {
      withCredentials
    }).then(function(res) {
      setOkDialogTitle("Success");
      setOkDialogText(res.data.code);
      okDialogCallback = () => {
        setSigningIn(false);
        setLogged(true);
        setShowOkDialog(false);
        setShowAuth(false);
        if (props.next) {
          props.next();
        }
      };
      setShowOkDialog(true);
    }).catch(function(err) {
      handleError(err, "Signup failed");
      setSigningIn(false);
    });
  }
  return (() => {
    var _el$ = _tmpl$$b(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild;
    insert(_el$2, createComponent(EmailPassword, {
      submit: signup
    }), _el$3);
    _el$4.$$click = signup;
    insert(_el$5, createComponent(InlineSpinner, {
      get show() {
        return signingIn();
      }
    }), _el$6);
    insert(_el$, createComponent(ErrorDialog, {
      width: 36
    }), null);
    insert(_el$, createComponent(Show, {
      get when() {
        return showOkDialog();
      },
      get children() {
        return createComponent(OkDialog, {
          get title() {
            return okDialogTitle();
          },
          get text() {
            return okDialogText();
          },
          callback: okDialogCallback
        });
      }
    }), null);
    createRenderEffect((_p$) => {
      var _v$ = "w-[" + getWidth() + "rem]", _v$2 = {
        "bg-indigo-600": readyToSubmit(),
        "hover:bg-indigo-700": readyToSubmit(),
        "bg-gray-500": !readyToSubmit()
      }, _v$3 = !readyToSubmit();
      _v$ !== _p$.e && className(_el$2, _p$.e = _v$);
      _p$.t = classList(_el$4, _v$2, _p$.t);
      _v$3 !== _p$.a && (_el$4.disabled = _p$.a = _v$3);
      return _p$;
    }, {
      e: void 0,
      t: void 0,
      a: void 0
    });
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$a = /* @__PURE__ */ template(`<div class="h-screen w-screen grid place-items-center fixed z-10 top-0 left-0 bg-white opacity-97"><div class="absolute top-0 right-0 cursor-pointer"></div><div><div><div class="flex justify-center text-sm mt-4 underline"><a href=#>Sign up</a></div></div><div><div class="flex justify-center text-sm mt-4 underline"><a href=#>Sign in`);
let unsubscribe = null;
function LoginEmbed(_) {
  const [mode, setMode] = createSignal("signin");
  const {
    logged,
    showAuth,
    setShowAuth,
    afterLogin,
    afterLogout,
    setReloginChecked
  } = gvLogin;
  const {
    multiuser
  } = gvMultiuser;
  const {
    auth
  } = gvFirebase;
  const {
    setAppLoading
  } = gvAppLoading;
  const {
    systemSetupNeeded
  } = gvSystemSetupNeeded;
  createEffect(function() {
    if (unsubscribe == null) {
      setAppLoading(true);
    }
    if (multiuser() == true && auth() || systemSetupNeeded()) {
      if (!unsubscribe && multiuser() && logged() != true) {
        unsubscribe = onAuthStateChanged(auth(), function(user) {
          if (user) {
            afterLogin(user);
            setReloginChecked(true);
          } else {
            afterLogout();
          }
        });
      }
    } else {
      setReloginChecked(true);
    }
  });
  function changeToSignUp() {
    setMode("signup");
  }
  function changeToSignIn() {
    setMode("signin");
  }
  function onClickX(_2) {
    setShowAuth(false);
  }
  return (() => {
    var _el$ = _tmpl$$a(), _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild, _el$7 = _el$4.nextSibling, _el$8 = _el$7.firstChild, _el$9 = _el$8.firstChild;
    _el$2.$$click = onClickX;
    insert(_el$2, createComponent(HiOutlineXMark, {
      color: "rgb(107 114 128)",
      size: 64
    }));
    insert(_el$4, createComponent(SignIn, {
      width: "36"
    }), _el$5);
    _el$6.$$click = changeToSignUp;
    insert(_el$7, createComponent(SignUp, {
      width: "36"
    }), _el$8);
    _el$9.$$click = changeToSignIn;
    createRenderEffect((_p$) => {
      var _v$ = !showAuth(), _v$2 = !!(mode() != "signin"), _v$3 = !!(mode() != "signup");
      _v$ !== _p$.e && _el$.classList.toggle("hidden", _p$.e = _v$);
      _v$2 !== _p$.t && _el$4.classList.toggle("hidden", _p$.t = _v$2);
      _v$3 !== _p$.a && _el$7.classList.toggle("hidden", _p$.a = _v$3);
      return _p$;
    }, {
      e: void 0,
      t: void 0,
      a: void 0
    });
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$9 = /* @__PURE__ */ template(`<div class=h-screen>`);
function Main() {
  const {
    appLoading
  } = gvAppLoading;
  return (() => {
    var _el$ = _tmpl$$9();
    insert(_el$, createComponent(SideBar, {}), null);
    insert(_el$, createComponent(Content, {}), null);
    insert(_el$, createComponent(DetailCard, {}), null);
    insert(_el$, createComponent(LoginEmbed, {}), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!appLoading()));
    return _el$;
  })();
}

var _tmpl$$8 = /* @__PURE__ */ template(`<div class="h-screen w-screen grid place-items-center"><img class="h-96 animate-pulse">`);
function AppLoadingScreen() {
  const {
    serverUrl
  } = gvServer;
  const {
    appLoading
  } = gvAppLoading;
  return (() => {
    var _el$ = _tmpl$$8(), _el$2 = _el$.firstChild;
    setAttribute(_el$2, "src", serverUrl + "/submit/images/logo_transparent.png");
    createRenderEffect(() => _el$.classList.toggle("hidden", !appLoading()));
    return _el$;
  })();
}

var _tmpl$$7 = /* @__PURE__ */ template(`<div tabindex=-1 class="fixed top-0 left-0 right-0 z-0 w-full p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-modal md:h-full flex items-center justify-center"><div class="relative w-[48rem]"><div class="relative bg-white rounded-lg shadow dark:bg-gray-700 text-gray-700 text-sm"><div class="px-6 py-6 lg:px-8"><img class=h-28><p class=mt-8>Welcome to OakVar!</p><p class=mt-4>Get ready to explore the world of genomics like never before with OakVar!</p><p class=mt-4>With our platform, you can effortlessly analyze your own genome or dive into exciting new research with genome data.</p><p class=mt-4>Say goodbye to complicated processes and hello to a new world of discovery.</p><p class=mt-4>- Oak Bioinformatics, LLC</p><button type=submit class="w-full text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 mt-4">Start`);
function SystemSetupWelcome(props) {
  const {
    serverUrl
  } = gvServer;
  function onClickStart() {
    props.setPageNo(2);
  }
  return (() => {
    var _el$ = _tmpl$$7(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.nextSibling, _el$7 = _el$6.nextSibling, _el$8 = _el$7.nextSibling, _el$9 = _el$8.nextSibling, _el$10 = _el$9.nextSibling, _el$11 = _el$10.nextSibling;
    setAttribute(_el$5, "src", serverUrl + "/submit/images/logo.png");
    _el$11.$$click = onClickStart;
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.pageNo != 1)));
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$6 = /* @__PURE__ */ template(`<div tabindex=-1 class="fixed top-0 left-0 right-0 z-0 w-full p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-modal md:h-full flex items-center justify-center"><div class="relative w-[48rem]"><div class="relative bg-white rounded-lg shadow dark:bg-gray-700 text-gray-700 text-sm"><div class="px-6 py-6 lg:px-8"><img class=h-28><div class="flex flex-col mt-4">Do you already have an OakVar account?<button class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 mt-4">Yes</button><button class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 mt-4">No`);
function SystemSetupAccountQuestion(props) {
  const {
    serverUrl,
    withCredentials
  } = gvServer;
  const curPageNo = 2;
  function onClickYes() {
    props.setPrevPageNo(curPageNo);
    props.setPageNo(4);
  }
  function onClickNo() {
    props.setPrevPageNo(curPageNo);
    props.setPageNo(3);
  }
  return (() => {
    var _el$ = _tmpl$$6(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.nextSibling, _el$7 = _el$6.firstChild, _el$8 = _el$7.nextSibling, _el$9 = _el$8.nextSibling;
    insert(_el$4, createComponent(BsArrowLeft, {
      size: 24,
      color: "rgb(55 65 81)",
      "class": "mb-4 cursor-pointer",
      get onClick() {
        return [props.setPageNo, props.prevPageNo];
      }
    }), _el$5);
    setAttribute(_el$5, "src", serverUrl + "/submit/images/logo.png");
    _el$8.$$click = onClickYes;
    _el$9.$$click = onClickNo;
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.pageNo != curPageNo)));
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$5 = /* @__PURE__ */ template(`<div tabindex=-1 class="fixed top-0 left-0 right-0 z-0 w-full p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-modal md:h-full flex items-center justify-center"><div class="relative w-[48rem]"><div class="relative bg-white rounded-lg shadow dark:bg-gray-700 text-gray-700 text-sm"><div class="px-6 py-6 lg:px-8"><img class=h-28><p class=mt-4>Welcome back! We're so glad to see you again. Please go ahead and sign in. We've been waiting for you!`);
function SystemSetupSignIn(props) {
  const curPageNo = 4;
  const {
    serverUrl
  } = gvServer;
  function onSignedIn() {
    props.setPrevPageNo(curPageNo);
    props.setPageNo(5);
  }
  return (() => {
    var _el$ = _tmpl$$5(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild; _el$5.nextSibling;
    insert(_el$4, createComponent(BsArrowLeft, {
      size: 24,
      color: "rgb(55 65 81)",
      "class": "mb-4 cursor-pointer",
      get onClick() {
        return [props.setPageNo, 2];
      }
    }), _el$5);
    setAttribute(_el$5, "src", serverUrl + "/submit/images/logo.png");
    insert(_el$4, createComponent(SignIn, {
      signedInCallback: onSignedIn
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.pageNo != curPageNo)));
    return _el$;
  })();
}

var _tmpl$$4 = /* @__PURE__ */ template(`<div tabindex=-1 class="fixed top-0 left-0 right-0 z-0 w-full p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-modal md:h-full flex items-center justify-center"><div class="relative w-[48rem]"><div class="relative bg-white rounded-lg shadow dark:bg-gray-700 text-gray-700 text-sm"><div class="px-6 py-6 lg:px-8"><img class=h-28><p class=mt-4>In order to use our platform, you'll need to create an OakVar store account.</p><p class=mt-4>Simply enter your email and choose a password to get started.</p><p class=mt-4>Rest assured, your information is safe with us and will only be used for your OakVar experience and communication between us.`);
function SystemSetupSignup(props) {
  const curPageNo = 3;
  const {
    serverUrl
  } = gvServer;
  function goToSetupDirectory() {
    props.setPageNo(5);
  }
  return (() => {
    var _el$ = _tmpl$$4(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.nextSibling, _el$7 = _el$6.nextSibling; _el$7.nextSibling;
    insert(_el$4, createComponent(BsArrowLeft, {
      size: 24,
      color: "rgb(55 65 81)",
      "class": "mb-4 cursor-pointer",
      get onClick() {
        return [props.setPageNo, 2];
      }
    }), _el$5);
    setAttribute(_el$5, "src", serverUrl + "/submit/images/logo.png");
    insert(_el$4, createComponent(SignUp, {
      next: goToSetupDirectory,
      newSetup: true
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.pageNo != curPageNo)));
    return _el$;
  })();
}

var _tmpl$$3 = /* @__PURE__ */ template(`<span>Change`), _tmpl$2$1 = /* @__PURE__ */ template(`<div><div class=mt-4><label class="block text-sm font-semibold text-gray-700 underline decoration-dotted cursor-help"></label><div class="mt-1 flex rounded-md shadow-sm"><div class="relative flex flex-grow items-stretch focus-within:z-10"><input class="block w-full rounded-none rounded-l-md border-gray-300 pl-10 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"></div><button type=button class="relative -ml-px inline-flex items-center space-x-2 rounded-r-md border border-gray-300 bg-gray-50 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"></button></div><p class="mt-2 text-sm text-blue-400">`), _tmpl$3$1 = /* @__PURE__ */ template(`<span>Set`);
function DirectoryPicker(props) {
  const {
    serverUrl
  } = gvServer;
  const [inputDisabled, setInputDisabled] = createSignal(true);
  const [dirMessage, setDirMessage] = createSignal(null);
  let input = null;
  createEffect(function() {
    if (!inputDisabled()) {
      return;
    }
    checkServerDir(props.dir);
  });
  function checkServerDir(serverDir) {
    if (serverDir == void 0) {
      return "";
    }
    axios.get(serverUrl + "/submit/checkserverdir", {
      params: {
        dir: serverDir
      }
    }).then(function(res) {
      if (res.data.exists == false) {
        setDirMessage("This directory will be created.");
      } else {
        setDirMessage(null);
      }
    }).catch(function(err) {
      handleError(err);
    });
  }
  function onKeyup(evt) {
    props.setDir(evt.target.value);
    if (evt.keyCode == 13) {
      setInputDisabled(true);
    }
  }
  function onClickChangeDir(_) {
    setInputDisabled(!inputDisabled());
    input.focus();
  }
  function onMouseEnterTitle(evt) {
    props.setTooltipText(props.help);
    props.setTooltipTop(evt.clientY);
    props.setTooltipShow(true);
  }
  function onMouseLeaveTitle(_) {
    props.setTooltipShow(false);
  }
  return (() => {
    var _el$ = _tmpl$2$1(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.nextSibling, _el$5 = _el$4.firstChild, _el$6 = _el$5.firstChild, _el$7 = _el$5.nextSibling, _el$9 = _el$4.nextSibling;
    _el$3.addEventListener("mouseleave", onMouseLeaveTitle);
    _el$3.addEventListener("mouseenter", onMouseEnterTitle);
    insert(_el$3, () => props.title);
    var _ref$ = input;
    typeof _ref$ === "function" ? use(_ref$, _el$6) : input = _el$6;
    _el$6.$$keyup = onKeyup;
    _el$7.$$click = onClickChangeDir;
    insert(_el$7, createComponent(Show, {
      get when() {
        return inputDisabled();
      },
      get fallback() {
        return _tmpl$3$1();
      },
      get children() {
        return _tmpl$$3();
      }
    }));
    insert(_el$9, dirMessage);
    createRenderEffect(() => _el$6.disabled = inputDisabled());
    createRenderEffect(() => _el$6.value = props.dir);
    return _el$;
  })();
}
delegateEvents(["keyup", "click"]);

var _tmpl$$2 = /* @__PURE__ */ template(`<div tabindex=-1 class="fixed top-0 left-0 right-0 z-0 w-full p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-modal md:h-full flex items-center justify-center"><div class="relative w-[48rem]"><div class="relative bg-white rounded-lg shadow dark:bg-gray-700 text-gray-700 text-sm"><div class="px-6 py-6 lg:px-8"><img class=h-28><p class=mt-4>OakVar needs to store system configuration and data files. Don't worry, we've got your back with pre-selected default locations. If you need to make any adjustment, feel free to do so. And if everything looks good, just hit the "Start setup" button.</p><div class="mt-4 mb-4 flex"><div class=ml-4>A quick heads up about the modules directory - to get the most out of your OakVar experience, we recommend having at least 2GB of storage space available. And if you're planning on diving into some larger annotation modules, keep in mind that they can take up a substantial amount of space, potentially reaching over 100GB.</div></div><div class=mt-4><button type=submit class="w-full text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Start setup`);
function SystemSetupDirectories(props) {
  const curPageNo = 5;
  const {
    serverUrl
  } = gvServer;
  const {
    email,
    password
  } = gvEmail;
  const [rootDir, setRootDir] = createSignal(null);
  const [modulesDir, setModulesDir] = createSignal(null);
  const [jobsDir, setJobsDir] = createSignal(null);
  const [logDir, setLogDir] = createSignal(null);
  const [tooltipText, setTooltipText] = createSignal(null);
  const [tooltipShow, setTooltipShow] = createSignal(false);
  const [tooltipTop, setTooltipTop] = createSignal(0);
  createEffect(function() {
    if (rootDir() == null) {
      fetchRootDir();
    }
    if (modulesDir() == null) {
      fetchModulesDir();
    }
    if (jobsDir() == null) {
      fetchJobsDir();
    }
    if (logDir() == null) {
      fetchLogDir();
    }
  });
  function onClickStartSetup(evt) {
    evt.preventDefault();
    props.setSetupData({
      email: email(),
      pw: password(),
      root_dir: rootDir(),
      modules_dir: modulesDir(),
      jobs_dir: jobsDir(),
      log_dir: logDir(),
      setupToStart: true
    });
    props.setPrevPageNo(curPageNo);
    props.setPageNo(6);
  }
  function fetchRootDir() {
    axios.get(serverUrl + "/submit/rootdir").then(function(res) {
      setRootDir(res.data.root_dir);
    }).catch(function(err) {
      console.error(err);
    });
  }
  function fetchModulesDir() {
    axios.get(serverUrl + "/submit/modulesdir").then(function(res) {
      setModulesDir(res.data.modules_dir);
    }).catch(function(err) {
      console.error(err);
    });
  }
  function fetchJobsDir() {
    axios.get(serverUrl + "/submit/jobsdir").then(function(res) {
      setJobsDir(res.data.jobs_dir);
    }).catch(function(err) {
      console.error(err);
    });
  }
  function fetchLogDir() {
    axios.get(serverUrl + "/submit/logdir").then(function(res) {
      setLogDir(res.data.log_dir);
    }).catch(function(err) {
      console.error(err);
    });
  }
  return (() => {
    var _el$ = _tmpl$$2(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild, _el$6 = _el$5.nextSibling, _el$7 = _el$6.nextSibling, _el$8 = _el$7.firstChild, _el$9 = _el$7.nextSibling, _el$10 = _el$9.firstChild;
    insert(_el$4, createComponent(BsArrowLeft, {
      size: 24,
      color: "rgb(55 65 81)",
      "class": "mb-4 cursor-pointer",
      get onClick() {
        return [props.setPageNo, 2];
      }
    }), _el$5);
    setAttribute(_el$5, "src", serverUrl + "/submit/images/logo.png");
    insert(_el$7, createComponent(IoWarningOutline, {
      "class": "inline",
      size: "28",
      color: "#fb923c"
    }), _el$8);
    insert(_el$4, createComponent(DirectoryPicker, {
      title: "System root directory",
      get dir() {
        return rootDir();
      },
      setDir: setRootDir,
      setTooltipShow,
      setTooltipText,
      setTooltipTop,
      help: "OakVar system files will be created in this directory. By default, directories for configuration, modules, and jobs will be created under this directory. However, each of them can be assigned to a different location using the input boxes following this one."
    }), _el$9);
    insert(_el$4, createComponent(DirectoryPicker, {
      title: "Modules directory",
      get dir() {
        return modulesDir();
      },
      setDir: setModulesDir,
      setTooltipShow,
      setTooltipText,
      setTooltipTop,
      help: "OakVar is a modular system. Conversion, mapping, annotation, and reporting are done by modules. Among OakVar system files, module files are the biggest, which can take up to hundreds of GB according to your choice."
    }), _el$9);
    insert(_el$4, createComponent(DirectoryPicker, {
      title: "Jobs directory",
      get dir() {
        return jobsDir();
      },
      setDir: setJobsDir,
      setTooltipShow,
      setTooltipText,
      setTooltipTop,
      help: "Jobs will be stored in this directory"
    }), _el$9);
    insert(_el$4, createComponent(DirectoryPicker, {
      title: "Log directory",
      get dir() {
        return logDir();
      },
      setDir: setLogDir,
      setTooltipShow,
      setTooltipText,
      setTooltipTop,
      help: "System logs will be stored in this directory"
    }), _el$9);
    _el$10.$$click = onClickStartSetup;
    insert(_el$, createComponent(Tooltip, {
      get text() {
        return tooltipText();
      },
      get tooltipShow() {
        return tooltipShow();
      },
      get tooltipTop() {
        return tooltipTop();
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.pageNo != curPageNo)));
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$$1 = /* @__PURE__ */ template(`<div class="mt-4 w-full flex items-center justify-center flex flex-col"><div><p class=mt-4>Congratulations, you're now ready to start using OakVar!</p><p class=mt-4>All the setup is finished and it's time to dive into the exciting world of genetics.</p><p class=mt-4>Simply click the button below and let the journey begin!</p></div><button type=button class="mt-8 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Enter OakVar!`), _tmpl$2 = /* @__PURE__ */ template(`<div tabindex=-1 class="fixed top-0 left-0 right-0 z-0 w-full h-full p-4 md:inset-0 flex items-center justify-center"><div class="relative w-[48rem]"><div class="relative bg-white rounded-lg shadow dark:bg-gray-700 text-gray-700 text-sm p-6"><div class="px-6 py-6 lg:px-8"><img class=h-28>`), _tmpl$3 = /* @__PURE__ */ template(`<div><p class=mt-4>We're getting OakVar all set up for you!</p><p class=mt-4>Just sit back and relax for a moment while we take care of everything.</p><p class=mt-4>We'll let you know as soon as we're ready for you.</p><div class="mt-4 w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700"><div class="bg-blue-600 h-2.5 rounded-full"></div></div><p class=mt-2></p><div class="mt-4 text-xs p-6 h-[24rem] overflow-auto font-mono whitespace-pre"><div class=relative><div>`), _tmpl$4 = /* @__PURE__ */ template(`<p>`);
function SystemSetupInstalling(props) {
  const curPageNo = 6;
  const {
    systemMsg,
    setSystemMsg
  } = gvSystemMessage;
  const {
    serverUrl,
    withCredentials
  } = gvServer;
  const {
    getSetupStageMsg,
    setSetupStateMsg
  } = gvWebSocket;
  const [msgs, setMsgs] = createStore([]);
  const [setupProgress, setSetupProgress] = createSignal(0);
  let msgBox = null;
  let noBaseModules = 0;
  let numInstalledBaseModules = 0;
  let prevSetupStageMsg = null;
  createEffect(function() {
    if (props.setupData && props.setupData.setupToStart == true) {
      props.setSetupData({
        ...props.setupData,
        setupToStart: false
      });
      startSetup();
    }
    if (systemMsg() != null) {
      setMsgs([...msgs, ...systemMsg()]);
      setSystemMsg(null);
      setTimeout(function() {
        msgBox.scrollTo(0, 99999);
      }, 100);
    }
    const setupStageMsg = getSetupStageMsg();
    if (setupStageMsg != prevSetupStageMsg) {
      prevSetupStageMsg = setupStageMsg;
      if (setupStageMsg == "Logging in...") {
        setSetupProgress(10);
      } else if (setupStageMsg == "Setting up store cache...") {
        setSetupProgress(20);
      } else if (setupStageMsg == "Setting up administrative database...") {
        setSetupProgress(50);
      } else if (setupStageMsg == "Installing system modules...") {
        setSetupProgress(60);
      } else if (setupStageMsg.startsWith("Installed") || setupStageMsg.includes("already exists")) {
        numInstalledBaseModules += 1;
        const n = 60 + numInstalledBaseModules / noBaseModules * 40;
        setSetupProgress(n);
      } else if (setupStageMsg == "Done setting up the system.") {
        setSetupProgress(100);
      }
    }
  });
  function startSetup() {
    numInstalledBaseModules = 0;
    prevSetupStageMsg = null;
    setSetupStateMsg("");
    axios.get(serverUrl + "/submit/basemodules", {
      withCredentials
    }).then(function(res) {
      noBaseModules = res.data.length;
      axios.post(serverUrl + "/submit/startsetup", props.setupData, {
        withCredentials
      }).then(function(_) {
      }).catch(function(err) {
        handleError(err);
      });
    }).catch(function(err) {
      handleError(err);
    });
  }
  function onSetupSuccess() {
    window.location.reload();
  }
  return (() => {
    var _el$ = _tmpl$2(), _el$2 = _el$.firstChild, _el$3 = _el$2.firstChild, _el$4 = _el$3.firstChild, _el$5 = _el$4.firstChild;
    insert(_el$4, createComponent(BsArrowLeft, {
      size: 24,
      color: "rgb(55 65 81)",
      "class": "mb-4 cursor-pointer",
      get onClick() {
        return [props.setPageNo, props.prevPageNo];
      }
    }), _el$5);
    setAttribute(_el$5, "src", serverUrl + "/submit/images/logo.png");
    insert(_el$4, createComponent(Show, {
      get when() {
        return setupProgress() == 100;
      },
      get fallback() {
        return (() => {
          var _el$9 = _tmpl$3(), _el$10 = _el$9.firstChild, _el$11 = _el$10.nextSibling, _el$12 = _el$11.nextSibling, _el$13 = _el$12.nextSibling, _el$14 = _el$13.firstChild, _el$15 = _el$13.nextSibling, _el$16 = _el$15.nextSibling, _el$17 = _el$16.firstChild, _el$18 = _el$17.firstChild;
          insert(_el$15, getSetupStageMsg);
          var _ref$ = msgBox;
          typeof _ref$ === "function" ? use(_ref$, _el$16) : msgBox = _el$16;
          insert(_el$18, createComponent(For, {
            each: msgs,
            children: (msg) => (() => {
              var _el$19 = _tmpl$4();
              insert(_el$19, () => msg.msg);
              return _el$19;
            })()
          }));
          createRenderEffect(() => setupProgress() + "%" != null ? _el$14.style.setProperty("width", setupProgress() + "%") : _el$14.style.removeProperty("width"));
          return _el$9;
        })();
      },
      get children() {
        var _el$6 = _tmpl$$1(), _el$7 = _el$6.firstChild, _el$8 = _el$7.nextSibling;
        _el$8.$$click = onSetupSuccess;
        return _el$6;
      }
    }), null);
    createRenderEffect(() => _el$.classList.toggle("hidden", !!(props.pageNo != curPageNo)));
    return _el$;
  })();
}
delegateEvents(["click"]);

var _tmpl$ = /* @__PURE__ */ template(`<div tabindex=-1 class="fixed top-0 left-0 right-0 z-0 w-full">`);
function SystemSetup() {
  const [pageNo, setPageNo] = createSignal(1);
  const [prevPageNo, setPrevPageNo] = createSignal(1);
  const [setupData, setSetupData] = createStore({});
  return (() => {
    var _el$ = _tmpl$();
    insert(_el$, createComponent(SystemSetupWelcome, {
      get pageNo() {
        return pageNo();
      },
      setPageNo,
      get prevPageNo() {
        return prevPageNo();
      },
      setPrevPageNo,
      setupData,
      setSetupData
    }), null);
    insert(_el$, createComponent(SystemSetupAccountQuestion, {
      get pageNo() {
        return pageNo();
      },
      setPageNo,
      get prevPageNo() {
        return prevPageNo();
      },
      setPrevPageNo,
      setupData,
      setSetupData
    }), null);
    insert(_el$, createComponent(SystemSetupSignup, {
      get pageNo() {
        return pageNo();
      },
      setPageNo,
      get prevPageNo() {
        return prevPageNo();
      },
      setPrevPageNo,
      setupData,
      setSetupData
    }), null);
    insert(_el$, createComponent(SystemSetupSignIn, {
      get pageNo() {
        return pageNo();
      },
      setPageNo,
      get prevPageNo() {
        return prevPageNo();
      },
      setPrevPageNo,
      setupData,
      setSetupData
    }), null);
    insert(_el$, createComponent(SystemSetupDirectories, {
      get pageNo() {
        return pageNo();
      },
      setPageNo,
      get prevPageNo() {
        return prevPageNo();
      },
      setPrevPageNo,
      setupData,
      setSetupData
    }), null);
    insert(_el$, createComponent(SystemSetupInstalling, {
      get pageNo() {
        return pageNo();
      },
      setPageNo,
      get prevPageNo() {
        return prevPageNo();
      },
      setPrevPageNo,
      setupData,
      setSetupData
    }), null);
    return _el$;
  })();
}

function App() {
  const {
    serverUrl
  } = gvServer;
  const {
    logged,
    setLogged
  } = gvLogin;
  const {
    multiuser,
    setMultiuser
  } = gvMultiuser;
  const {
    setAppLoading
  } = gvAppLoading;
  const {
    systemSetupNeeded
  } = gvSystemSetupNeeded;
  const {
    reloginChecked
  } = gvLogin;
  setMultiuser(null);
  setLogged(null);
  createEffect(function() {
    if (multiuser() == null) {
      fetchMultiuserMode();
    }
    if (multiuser() == true && logged() == null) {
      fetchLoginState();
    }
    if (multiuser() != null && logged() != null && reloginChecked() == true || multiuser() == false && logged() == true) {
      setAppLoading(false);
    }
  });
  function deleteToken() {
    axios.get(serverUrl + "/server/deletetoken").then(function() {
    }).catch(function(err) {
      handleError(err);
    });
  }
  function fetchMultiuserMode() {
    axios.get(serverUrl + "/submit/servermode").then(function(res) {
      setMultiuser(res.data.servermode);
      if (!multiuser()) {
        deleteToken();
        setLogged(true);
      }
    }).catch(function(err) {
      handleError(err);
    });
  }
  function fetchLoginState() {
    axios.get(serverUrl + "/submit/loginstate").then(function(res) {
      setLogged(res.data.loggedin);
    }).catch(function(err) {
      handleError(err);
    });
  }
  return [createComponent(Show, {
    get when() {
      return !systemSetupNeeded();
    },
    get fallback() {
      return createComponent(SystemSetup, {});
    },
    get children() {
      return [createComponent(AppLoadingScreen, {}), createComponent(Main, {})];
    }
  }), createComponent(ErrorDialog, {
    width: "[64rem]"
  })];
}

render(() => createComponent(App, {}), document.getElementById("root"));
