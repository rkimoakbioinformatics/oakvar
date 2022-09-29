function getAllFilteredModulesDivs() {
  return document.querySelectorAll(".filtered-modules-div")
}

function getSelectedModuleCard(data) {
  var div = getEl("div")
  div.setAttribute("name", data.name)
  div.classList.add(...stringToArray("relative flex items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400 max-h-24 mb-2"))
  div.textContent = data.title
  div.title = "Click to remove"
  div.addEventListener("click", function(evt) {
    var module = moduleDatas[AP_KEY][evt.target.getAttribute("name")]
    toggleSelectedModule(module)
  })
  return div
}

function getModuleCard(moduleData, callback) {
  var moduleCardDiv = getEl("div");
  moduleCardDiv.classList.add("modulecard");
  moduleCardDiv.classList.add(...stringToArray("relative flex items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400"))
  if (moduleData.checked) {
    moduleCardDiv.classList.add("checked");
  }
  moduleCardDiv.setAttribute("name", moduleData.name);
  moduleCardDiv.setAttribute("kind", moduleData.kind);
  moduleCardDiv.addEventListener("click", function(evt) { callback(evt) })
  var div3 = getEl("div");
  div3.classList.add("flex-shrink-0");
  addEl(moduleCardDiv, div3);
  var img = getEl("img");
  img.classList.add(...stringToArray("w-12 rounded-lg"))
  img.src = "/store/locallogo?module=" + moduleData.name;
  addEl(div3, img);
  var div4 = getEl("div");
  div4.classList.add(...stringToArray("min-w-0 flex-1"))
  addEl(moduleCardDiv, div4);
  var a = getEl("div");
  a.classList.add("focus:outline-none");
  addEl(div4, a);
  var span = getEl("span");
  span.classList.add(...stringToArray("absolute inset-0"))
  span.setAttribute("aria-hidden", true);
  addEl(a, span);
  var p = getEl("p");
  p.classList.add(...stringToArray("text-sm font-medium text-gray-700"))
  p.textContent = moduleData.title;
  addEl(a, p);
  var p2 = getEl("p");
  p2.classList.add(...stringToArray("text-sm text-gray-500"))
  p2.textContent = moduleData.desc;
  addEl(a, p2);
  return moduleCardDiv;
}

function getSelectedModulesDiv() {
  return document.querySelector("#selected-modules-div")
}

function getClearSelectedModulesBtn() {
  return document.querySelector("#clear-selected-modules-btn")
}

function getInputDropArea() {
  return document.querySelector("#input-drop-area")
}

function getInputPasteArea() {
  return document.querySelector("#input-paste-area")
}

function getInputTextarea() {
  return document.querySelector("#input-text")
}

function getAnalysisModuleChoiceDiv() {
  return document.querySelector("#analysis-module-choice-div")
}

function getInputUploadListDiv() {
  return document.querySelector("#input-upload-list-div")
}

function getInputUploadList() {
  return document.querySelector("#input-upload-list")
}

function getInputFileControl() {
  return document.querySelector("#input-file")
}

function getReportChoiceDiv() {
  return document.querySelector("#report-choice-div")
}

function getReportChoiceItemsDiv() {
  return document.querySelector("#report-choice-items")
}

function getSubmitNoteDiv() {
  return document.querySelector("#submit-note-div")
}

function getSubmitNoteTextarea() {
  return document.querySelector("#submit-note")
}

function getSubmitJobButtonDiv() {
  return document.querySelector("#submit-job-button-div")
}

function getSubmitJobButton() {
  return document.querySelector("#submit-job-button")
}

function getCtaAnalysisModuleChoice() {
  return document.querySelector("#cta-analysis-module-choice")
}

function getInputFormatSelectBtn() {
  return document.querySelector("#input-format-select")
}

function getErrorDialog() {
  return document.querySelector("#error-dialog")
}

function getErrorDialogTitleEl() {
  return document.querySelector("#error-dialog-title")
}

function getErrorDialogTextEl() {
  return document.querySelector("#error-dialog-text")
}

function getOkDialog() {
  return document.querySelector("#ok-dialog")
}

function getOkDialogTitleEl() {
  return document.querySelector("#ok-dialog-title")
}

function getOkDialogTextEl() {
  return document.querySelector("#ok-dialog-text")
}

function getJobNameDir() {
  return document.querySelector("#job-name-div")
}

function getJobNameTextarea() {
  return document.querySelector("#job-name")
}

function getSpinner() {
  var div = getEl("div")
  div.classList.add("spinner")
  var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
  svg.classList.add(...stringToArray("w-6 h-6 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600 ml-2"))
  svg.setAttribute("viewBox", "0 0 100 101")
  svg.setAttribute("fill", "none")
  addEl(div, svg)
  var path = document.createElementNS("http://www.w3.org/2000/svg", "path")
  path.setAttribute("fill", "currentColor")
  path.setAttribute("d", "M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z")
  addEl(svg, path)
  var path = document.createElementNS("http://www.w3.org/2000/svg", "path")
  path.setAttribute("fill", "currentFill")
  path.setAttribute("d", "M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z")
  addEl(svg, path)
  return div
}

function getTabContentDivs() {
  return document.querySelectorAll(".tabcontent")
}

function getTabContentDiv(tabName) {
  return document.querySelector("#tab_" + tabName)
}

function getTabHeads() {
  return document.querySelectorAll(".tabhead")
}

function getTabHead(tabName) {
  return document.querySelector("#tabhead_" + tabName)
}

function getJobsTbody() {
  return document.querySelector("#jobs-tbody")
}

function getJobsTablePageNoEl() {
  return document.querySelector("#jobs-table-pageno")
}

function getJobsTableJumpPageNoEl() {
  return document.querySelector("#jobs-table-jump-pageno")
}

