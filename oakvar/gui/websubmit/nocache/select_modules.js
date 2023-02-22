function updateSelectedModulesDiv(data) {
  var div = getSelectedModulesDiv()
  var el = div.querySelector("div[name=" + data.name + "]")
  if (data.checked && el == null) {
    el = getSelectedModuleCard(data)
    addEl(div, el)
  } else if (!data.checked && el != null) {
    el.remove()
  }
  updateClearSelectedModulesBtn()
}

function updateClearSelectedModulesBtn() {
  if (getSelectedModulesDiv().children.length > 0) {
    getClearSelectedModulesBtn().classList.remove("invisible")
  } else {
    getClearSelectedModulesBtn().classList.add("invisible")
  }
}

function updateFilteredModulesDivs(data) {
  var checked = data.checked
  var divs = getAllFilteredModulesDivs()
  for (var i=0; i<divs.length; i++) {
    var el = divs[i].querySelector("div[name=" + data.name + "]")
    if (el) {
      setModuleCardCheckedStatus(el, checked)
    }
  }
}

function setModuleCardCheckedStatus(el, checked) {
  if (checked) {
    el.classList.add("checked")
  } else {
    el.classList.remove("checked")
  }
}

function toggleSelectedModule(data) {
  data.checked = ! data.checked
  updateSelectedModulesDiv(data)
  updateFilteredModulesDivs(data)
}

function hideAnalysisModuleFilterPanels() {
  els = document.querySelectorAll(".analysis-module-filter-panel");
  for (var i = 0; i < els.length; i++) {
    els[i].classList.add("hidden");
  }
}

function showModuleFilterPanel(kind) {
  var div = getModuleFilterPanel(kind)
  div.classList.remove("hidden")
}

function pinFilterCategory(parentId, kind) {
  var el = document.querySelector("#" + parentId).querySelector(".filter-category[value=" + kind + "]")
  el.classList.add("pinned");
}

function onChangeFilterCategoryRadio(evt) {
  var kind = evt.target.value
  changeFilterCategory(kind)
}

function changeFilterCategory(kind) {
  unpinAnalysisModuleFilterKindBtns()
  pinFilterCategory("analysis-module-filter-kinds", kind)
  hideAnalysisModuleFilterPanels()
  showModuleFilterPanel(kind)
  populateModuleFilterPanel(kind)
}

function onChangeFilterCategoryRadioStore(evt) {
  var kind = evt.target.value
  changeFilterCategoryStore(kind)
}

function changeFilterCategoryStore(kind) {
  unpinStoreModuleFilterKindBtns()
  pinFilterCategory("store-module-filter-kinds", kind)
  hideAnalysisModuleFilterPanels()
  showModuleFilterPanel(kind)
  populateModuleFilterPanel(kind)
}

function getSelectedModuleCards() {
  return getSelectedModulesDiv().children
}

function clearSelectedModules() {
  var els = getSelectedModuleCards()
  var names = []
  for (var i=0; i<els.length; i++) {
    names.push(els[i].getAttribute("name"))
  }
  for (var i=0; i<names.length; i++) {
    var data = moduleDatas[AP_KEY][names[i]]
    toggleSelectedModule(data)
  }
}

function onClickClearSelectedModulesBtn(_) {
  clearSelectedModules()
}

function getInputUploadListWrapper() {
  return document.querySelector("#input-upload-list-wrapper")
}

