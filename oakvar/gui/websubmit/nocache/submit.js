function enableSubmitJobBtn() {
  getSubmitJobButton().disabled = false
}

function disableSubmitJobBtn() {
  getSubmitJobButton().disabled = true
}

function addSpinnerToSubmitJobBtn() {
  var spinner = getSpinner()
  addEl(getSubmitJobButton(), spinner)
}

function removeSpinnerFromSubmitJobBtn() {
  getSubmitJobButton().querySelector(".spinner").remove()
}

function commitSubmit(formData) {
  disableSubmitJobBtn()
  addSpinnerToSubmitJobBtn()
  var req = new XMLHttpRequest();
  req.open("POST", "/submit/submit");
  req.upload.onprogress = function (evt) {
    var uploadPerc = (evt.loaded / evt.total) * 100;
    document.querySelector("#spinner-div-progress-bar").style.width =
      uploadPerc + "%";
    document.querySelector("#spinner-div-progress-num").textContent =
      uploadPerc.toFixed(0) + "%";
  };
  req.onload = function (evt) {
    const status = evt.currentTarget.status;
    if (status === 200) {
      var response = JSON.parse(evt.currentTarget.response);
      if (response["status"]["status"] == "Submitted") {
        submittedJobs.push(response);
        addJob(response, true);
        //buildJobsTable();
      }
      if (response.expected_runtime > 0) {
      }
      jobRunning[response["id"]] = true;
      removeSpinnerFromSubmitJobBtn()
      enableSubmitJobBtn()
    } else if (status >= 400 && status < 600) {
      var response = JSON.parse(evt.currentTarget.response)
      showErrorDialog("Upload failure", "Check your input files. Or contact info@oakbioinformatics.com for support.", function(_) {
        hideErrorDialog()
        removeSpinnerFromSubmitJobBtn()
        enableSubmitJobBtn()
      })
    }
  }
  req.onerror = function (_) {
    document.querySelector("#submit-job-button").disabled = false;
    removeSpinnerFromSubmitJobBtn()
    enableSubmitJobBtn()
  };
  req.onabort = function (_) {
    document.querySelector("#submit-job-button").disabled = false;
    removeSpinnerFromSubmitJobBtn()
    enableSubmitJobBtn()
  };
  req.send(formData);
}

function isValidInputText(inputText) {
  return inputText.length > 0
}

function inputTextIsServerFileList(inputText) {
  return inputText.startsWith("#serverfile")
}

function processInputServerFiles(inputText, inputServerFiles) {
  let toks = inputText.split("\n");
  for (var i = 1; i < toks.length; i++) {
    let tok = toks[i];
    if (tok == "") {
      continue;
    }
    inputServerFiles.push(tok.trim());
  }
}

function makeInputTextFile(inputText, inputFiles) {
  var textBlob = new Blob([inputText], { type: "text/plain" });
  inputFiles.push(new File([textBlob], "example_input"));
}

function processInputText(inputFiles, inputServerFiles) {
  var inputTextarea = getInputTextarea()
  var inputText = inputTextarea.value
  if (! isValidInputText(inputText)) {
    return
  }
  if (inputTextIsServerFileList(inputText)) {
    processInputServerFiles(inputText, inputServerFiles)
  } else {
    makeInputTextFile(inputText, inputFiles)
  }
}

function processInputUpload() {
  inputFiles = inputFileList
  return inputFiles
}

function addInputFilesToSubmitForm(inputFiles, formData) {
  for (var i = 0; i < inputFiles.length; i++) {
    formData.append("file_" + i, inputFiles[i]);
  }
}

function addAnnotatorsToSubmitOption(submitOption) {
  submitOption.annotators = []
  var els = getSelectedModuleCards()
  for (var i = 0; i < els.length; i++) {
    var name = els[i].getAttribute("name")
    var data = moduleDatas[AP_KEY][name]
    var ty = data.type
    if (ty == "annotator") {
      submitOption.annotators.push(name);
    } 
  }
}

function addPostaggregatorsToSubmitOption(submitOption) {
  submitOption.postaggregators = []
  var els = getSelectedModuleCards()
  for (var i = 0; i < els.length; i++) {
    var name = els[i].getAttribute("name")
    var data = moduleDatas[AP_KEY][name]
    var ty = data.type
    if (ty == "postaggregator") {
      submitOption.postaggregators.push(name);
    } 
  }
}

function reportModuleCardIsChecked(card) {
  return card.classList.contains("checked")
}

function addReportersToSubmitOption(submitOption) {
  submitOption.reports = []
  var cards = getReportChoiceItemsDiv().children
  for (var i = 0; i < cards.length; i++) {
    var card = cards[i]
    var name = card.getAttribute("name")
    if (reportModuleCardIsChecked(card)) {
      submitOption.reports.push(name.substring(0, name.lastIndexOf("reporter")))
    } 
  }
}

function addAssemblyToSubmitOption(submitOption) {
  var val = getAssemblySelectBtn().getAttribute("value")
  if (val) {
    submitOption["genome"] = val
  }
}

function addInputFormatToSubmitOption(submitOption) {
  var val = getInputFormatSelectBtn().getAttribute("value")
  if (val) {
    submitOption["input_format"] = val
  }
}

function addNoteToSubmitOption(submitOption) {
  var val = getSubmitNoteTextarea().value
  if (val) {
    submitOption["note"] = val
  }
}

function addJobNameToSubmitOption(submitOption) {
  var val = getJobNameTextarea().value
  if (val) {
    submitOption["job_name"] = val
  }
}

function inputFileSizeIsWithinLimit() {
  var guiInputSizeLimit = parseInt(
    document.getElementById("settings_gui_input_size_limit").value
  );
  var sumInputSize = 0;
  for (var i = 0; i < inputFiles.length; i++) {
    sumInputSize += inputFiles[i].size;
  }
  sumInputSize = sumInputSize / 1024 / 1024;
  return sumInputSize <= guiInputSizeLimit
}

function processInput(inputFiles, inputServerFiles, formData, submitOption) {
  var inputPasteArea = getInputPasteArea()
  if (! inputPasteArea.classList.contains("hidden")) {
    processInputText(inputFiles, inputServerFiles)
  } else {
    inputFiles = processInputUpload()
  }
  if (inputFiles.length === 0 && inputServerFiles.length == 0) {
    throw new Error("Input is empty")
  }
  addInputFilesToSubmitForm(inputFiles, formData)
  submitOption["inputServerFiles"] = inputServerFiles
}

function processSubmitOptions(submitOption, formData) {
  addAnnotatorsToSubmitOption(submitOption)
  addPostaggregatorsToSubmitOption(submitOption)
  addReportersToSubmitOption(submitOption)
  addAssemblyToSubmitOption(submitOption)
  addInputFormatToSubmitOption(submitOption)
  addJobNameToSubmitOption(submitOption)
  addNoteToSubmitOption(submitOption)
  formData.append("options", JSON.stringify(submitOption))
}

function submit() {
  let inputFiles = []
  let inputServerFiles = []
  var submitOption = {}
  formData = new FormData()
  try {
    processInput(inputFiles, inputServerFiles, formData, submitOption)
    processSubmitOptions(submitOption, formData)
    /*if (! inputFileSizeIsWithinLimit()) {
      launchInputSizeLimitAlert()
    } else {
      commitSubmit()
    }*/
    commitSubmit(formData)
  } catch (err) {
    showErrorDialog("Problem with job submission", err.message)
  }
}


