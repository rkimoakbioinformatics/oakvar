function deselectAllTabHeads() {
  var els = getTabHeads()
  for (var i=0; i<els.length; i++) {
    els[i].classList.remove("selected")
  }
}

function selectTabHead(tabName) {
  getTabHead(tabName).classList.add("selected")
}

