function onInputFileChange(_) {
  setUploadedInputFilesDiv()
}

function setUploadedInputFilesDiv() {
  var fileInputElem = document.getElementById("input-file")
  var files = fileInputElem.files
  if (files.length >= 1) {
    for (var i = 0; i < files.length; i++) {
      var file = files[i];
      if (file.name.indexOf(" ") > -1) {
        showErrorDialog("Problem", "Input file names should not have space.")
        return
      }
    }
    showInputUploadListDiv();
    showInputUploadListWrapper()
    var fileListDiv = getInputUploadList()
    for (var i = 0; i < files.length; i++) {
      var file = files[i];
      if (inputFileList.indexOf(file.name) == -1) {
        var sdiv = getEl("span")
        sdiv.classList.add(...stringToArray("pl-2 text-sm text-gray-600 hover:text-gray-400 cursor-pointer round-md inline-block w-5/6"))
        sdiv.textContent = file.name
        sdiv.title = "Click to remove"
        sdiv.addEventListener("click", function (evt) {
          evt.preventDefault()
          var fileName = evt.target.textContent
          for (var j = 0; j < inputFileList.length; j++) {
            if (inputFileList[j].name == fileName) {
              inputFileList.splice(j, 1)
              break
            }
          }
          evt.target.remove()
          if (inputFileList.length == 0) {
            hideInputUploadListDiv()
            doSmartShowHideAnalysisModuleChoiceDiv()
          }
        })
        addEl(fileListDiv, sdiv)
        inputFileList.push(file)
      }
    }
  }
  if (inputFileList.length > 0) {
    showInputUploadListDiv()
    doSmartShowHideAnalysisModuleChoiceDiv()
  } else {
    hideInputUploadListDiv()
    doSmartShowHideAnalysisModuleChoiceDiv()
  }
  clearInputFileControl()
}

function clearInputFileControl() {
  getInputFileControl().value = ""
}

function onDropInputFiles(evt) {
  evt.stopPropagation()
  evt.preventDefault()
  var files = evt.dataTransfer.files
  var inputFile = document.getElementById("input-file")
  inputFile.files = files
  setUploadedInputFilesDiv()
  return false;
}

function onDragEnterInputFiles(evt) {
  evt.preventDefault();
}

function onDragOverInputFiles(evt) {
  evt.preventDefault();
}

function onDragLeaveInputFiles(evt) {
  evt.preventDefault();
}

function showInputUploadListDiv() {
  getInputUploadListDiv().classList.remove("hidden")
}

function hideInputUploadListDiv() {
  getInputUploadListDiv().classList.add("hidden")
}

function showInputUploadListWrapper() {
  getInputUploadListWrapper().classList.remove("hidden")
}

function hideInputUploadListWrapper() {
  getInputUploadListWrapper().classList.add("hidden")
}

function clearInputUploadList() {
  inputFileList = []
  getInputUploadList().replaceChildren()
  hideInputUploadListDiv()
  doSmartShowHideAnalysisModuleChoiceDiv()
}

function onChangeInputText(_) {
  doSmartShowHideAnalysisModuleChoiceDiv()
}

