function stringToArray(s) {
  return s.split(" ")
}

function getModuleInfoByType(ty) {
  var ret = []
  for (var i=0; i<localModuleNames.length; i++) {
    var name = localModuleNames[i]
    var module = localModuleInfo[name]
    if (module.type == ty) {
      ret.push(module)
    }
  }
  return ret
}

function titleSortFunc(a, b) {
  var x = a.title.toLowerCase();
  var y = b.title.toLowerCase();
  if (x < y) {
    return -1;
  }
  if (x > y) {
    return 1;
  }
  return 0;
}

