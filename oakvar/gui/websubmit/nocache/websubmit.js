var logged = false;
var username = null;
var prevJobTr = null;
var submittedJobs = [];
var storeModuleDivClicked = false;
var GLOBALS = {
  jobs: [],
  annotators: {},
  reports: {},
  inputExamples: {},
  idToJob: {},
  usersettings: {},
};
var currentTab = "submit";
var websubmitReportBeingGenerated = {};
var jobRunning = {};
var collectedTags = [];
var jobsPerPageInList = 15;
var jobsListCurStart = 0;
var jobsListCurEnd = jobsPerPageInList;
var systemReadyObj = {};
var formData = null;
var adminMode = false;
var inputFileList = [];
var JOB_IDS = [];
var jobListUpdateIntervalFn = null;
var reportRunning = {};
var systemConf;
var moduleDatas = {}
var moduleNames = {}
var NO_TAG = "no tag";
var DEFAULT_GENOME_ASSEMBLY = "hg38";
var AP_KEY = "ap"
var R_KEY = "r"

function showUpdateRemoteSpinner() {
  document
    .querySelector("#update-remote-spinner-div")
    .classList.remove("hidden");
}

function hideUpdateRemoteSpinner() {
  document.querySelector("#update-remote-spinner-div").classList.add("hidden");
}

function sortJobs() {
  for (var i = 0; i < GLOBALS.jobs.length - 1; i++) {
    for (var j = i + 1; j < GLOBALS.jobs.length; j++) {
      var ji1 = GLOBALS.jobs[i];
      var ji2 = GLOBALS.jobs[j];
      var j1 = GLOBALS.idToJob[ji1];
      var j2 = GLOBALS.idToJob[ji2];
      var d1 = new Date(j1.submission_time).getTime();
      var d2 = new Date(j2.submission_time).getTime();
      if (d2 > d1) {
        var tmp = ji1;
        GLOBALS.jobs[i] = GLOBALS.jobs[j];
        GLOBALS.jobs[j] = tmp;
      }
    }
  }
}

function addJob(job, prepend) {
  var trueDate = new Date(job.submission_time);
  job.submission_time = trueDate;
  if (GLOBALS.jobs.indexOf(job.id) == -1) {
    if (prepend == true) {
      GLOBALS.jobs.unshift(job.id);
    } else {
      GLOBALS.jobs.push(job.id);
    }
  }
  GLOBALS.idToJob[job.id] = job;
  var status = job.status;
  if (status != "Finished" && status != "Error" && status != "Aborted") {
    jobRunning[job.id] = true;
  } else if (jobRunning[job.id] != undefined) {
    delete jobRunning[job.id];
  }
  if (job.reports_being_generated.length > 0) {
    websubmitReportBeingGenerated[job.id] = {};
    if (reportRunning[job.id] == undefined) {
      reportRunning[job.id] = {};
    }
    for (var i = 0; i < job.reports_being_generated.length; i++) {
      var reportType = job.reports_being_generated[i];
      websubmitReportBeingGenerated[job.id][reportType] = true;
      reportRunning[job.id][reportType] = true;
    }
  }
}

function createJobReport(_) {
  var div = document.querySelector("#report_generation_div");
  var jobId = div.getAttribute("jobid");
  closeReportGenerationDiv();
  var select = document.querySelector("#report_generation_div_select");
  var reportType = select.value;
  if (websubmitReportBeingGenerated[jobId] == undefined) {
    websubmitReportBeingGenerated[jobId] = {};
  }
  websubmitReportBeingGenerated[jobId][reportType] = true;
  buildJobsTable();
  generateReport(jobId, reportType, function () {
    if (websubmitReportBeingGenerated[jobId] == undefined) {
      delete websubmitReportBeingGenerated[jobId];
    } else {
      //websubmitReportBeingGenerated[jobId][reportType] = false;
      delete websubmitReportBeingGenerated[jobId][reportType];
      populateJobs().then(function () {
        buildJobsTable();
      });
    }
  });
}

async function generateReport(jobId, reportType, callback) {
  var res = await axios.post("/submit/makereport/" + reportType, {
    job_id: jobId,
  });
  var data = res.data;
  if (data == "fail") {
    var mdiv = getEl("div");
    var span = getEl("span");
    span.textContent = reportType + " report generation failed for " + jobId;
    addEl(mdiv, span);
    addEl(mdiv, getEl("br"));
    addEl(mdiv, getEl("br"));
    var span = getEl("span");
    span.textContent = "Check your system's wcravat.log for details.";
    addEl(mdiv, span);
    showYesNoDialog(mdiv, null, false, true);
  }
  callback();
  if (reportRunning[jobId] == undefined) {
    reportRunning[jobId] = {};
  }
  reportRunning[jobId][reportType] = true;
}

function getAnnotatorsForJob(jobid) {
  var jis = GLOBALS.jobs;
  var anns = [];
  for (var j = 0; j < jis.length; j++) {
    var cji = GLOBALS.idToJob[jis[j]];
    if (cji.id == jobid) {
      anns = cji.annotators;
      break;
    }
  }
  return anns;
}

function getAnnotatorVersionForJob(jobid) {
  var jis = GLOBALS.jobs;
  var anns = {};
  for (var j = 0; j < jis.length; j++) {
    var cji = GLOBALS.idToJob[jis[j]];
    if (cji.id == jobid) {
      anns = cji.annotator_version;
      break;
    }
  }
  return anns;
}

function onClickJobTableMainTr(evt) {
  if (evt.target.parentElement.classList.contains("job-table-tr") == false) {
    return;
  }
  var clickedTr = evt.target.parentElement;
  var detailTr = clickedTr.nextSibling;
  if (clickedTr.classList.contains("highlighted-tr")) {
    clickedTr.classList.remove("highlighted-tr");
    detailTr.classList.add("hidden-tr");
  } else {
    clickedTr.classList.add("highlighted-tr");
    detailTr.classList.remove("hidden-tr");
  }
}

function emptyElement(elem) {
  while (elem.firstChild) {
    elem.removeChild(elem.firstChild);
  }
}

function populateJobTr(job) {
  var jobTr = $("tr.job-table-main-tr[jobid=" + job.id + "]")[0];
  emptyElement(jobTr);
  // Username
  if (adminMode == true) {
    var td = getEl("td");
    addEl(td, getTn(job.username));
    addEl(jobTr, td);
  }
  // Job ID
  addEl(jobTr, addEl(getEl("td"), getTn(job.id)));
  // Input file name
  if (Array.isArray(job.orig_input_fname)) {
    input_fname = job.orig_input_fname.join(", ");
  } else {
    var input_fname = job.orig_input_fname;
  }
  var input_fname_display = input_fname;
  var input_fname_display_limit = 30;
  if (input_fname.length > input_fname_display_limit) {
    input_fname_display =
      input_fname.substring(0, input_fname_display_limit) + "...";
  }
  addEl(jobTr, addEl(getEl("td"), getTn(input_fname_display)));
  // Number of unique variants
  var td = getEl("td");
  td.style.textAlign = "center";
  var num = "";
  if (job.num_unique_var != undefined) {
    num = "" + job.num_unique_var;
  }
  td.textContent = num;
  addEl(jobTr, td);
  // Number of annotators
  var annots = job.annotators;
  if (annots == undefined) {
    annots = "";
  }
  var num = annots.length;
  var td = getEl("td");
  td.style.textAlign = "center";
  td.textContent = "" + num;
  addEl(jobTr, td);
  // Genome assembly
  var td = getEl("td");
  td.style.textAlign = "center";
  addEl(td, getTn(job.assembly));
  addEl(jobTr, td);
  // Note
  var td = getEl("td");
  addEl(jobTr, addEl(td, getTn(job.note)));
  // Status
  var statusC = job.status["status"];
  if (statusC == undefined) {
    if (job.status != undefined) {
      statusC = job.status;
    } else {
      return null;
    }
  }
  var viewTd = getEl("td");
  viewTd.style.textAlign = "center";
  if (statusC == "Finished") {
    if (job.result_available) {
      var a = getEl("a");
      a.setAttribute("href", "/result/index.html?job_id=" + job.id);
      a.setAttribute("target", "_blank");
      var button = getEl("button");
      addEl(button, getTn("Open Result Viewer"));
      button.classList.add("butn");
      button.classList.add("launch-button");
      button.disabled = !job.viewable;
      addEl(a, button);
      addEl(viewTd, a);
    } else {
      var button = getEl("button");
      button.textContent = "Update to View";
      button.classList.add("butn");
      button.classList.add("launch-button");
      button.disabled = !job.viewable;
      button.setAttribute("job_id", job.id);
      button.addEventListener("click", function (_) {
        this.textContent = "Updating DB...";
        var jobId = this.getAttribute("job_id");
        $.ajax({
          url: "/submit/updateresultdb",
          type: "GET",
          data: { job_id: jobId },
          success: function (_) {
            showJobListPage();
          },
        });
      });
      addEl(viewTd, button);
    }
  } else {
    var span = getEl("span");
    span.textContent = statusC;
    addEl(viewTd, span);
    if (statusC == "Aborted" || statusC == "Error") {
      var btn = getEl("button");
      btn.classList.add("butn");
      btn.textContent = "Resubmit";
      btn.addEventListener("click", function (_) {
        $.get("/submit/resubmit", {
          job_id: job.id,
          job_dir: job.job_dir,
        }).done(function (_) {
          setTimeout(function () {
            populateJobs();
          }, 3000);
        });
      });
      addEl(viewTd, btn);
    }
  }
  addEl(jobTr, viewTd);
  var dbTd = getEl("td");
  dbTd.style.textAlign = "center";
  // Reports
  for (var i = 0; i < GLOBALS.reports.valid.length; i++) {
    var reportType = GLOBALS.reports.valid[i];
    if (
      (websubmitReportBeingGenerated[job.id] != undefined &&
        websubmitReportBeingGenerated[job.id][reportType] == true) ||
      job.reports_being_generated.includes(reportType)
    ) {
      var btn = getEl("button");
      btn.classList.add("butn");
      btn.setAttribute("jobid", job.id);
      btn.setAttribute("report-type", reportType);
      addEl(btn, getTn(reportType.toUpperCase()));
      btn.setAttribute("disabled", true);
      btn.classList.add("inactive-download-button");
      var spinner = getEl("img");
      spinner.classList.add("btn_overlay");
      spinner.src = "/result/images/arrow-spinner.gif";
      addEl(btn, spinner);
      if (job.status == "Finished") {
        addEl(dbTd, btn);
      }
    } else {
      if (job.reports.includes(reportType) == false) {
      } else {
        var btn = getEl("button");
        btn.classList.add("butn");
        btn.setAttribute("jobid", job.id);
        btn.setAttribute("report-type", reportType);
        addEl(btn, getTn(reportType.toUpperCase()));
        btn.classList.add("active-download-button");
        btn.addEventListener("click", function (evt) {
          jobReportDownloadButtonHandler(evt);
        });
        btn.title = "Click to download.";
        if (job.status == "Finished") {
          addEl(dbTd, btn);
        }
      }
    }
  }
  // Log
  var logLink = getEl("a");
  logLink.setAttribute("href", "/submit/jobs/" + job.id + "/log");
  logLink.setAttribute("target", "_blank");
  logLink.setAttribute("title", "Click to download.");
  var button = getEl("button");
  button.classList.add("butn");
  button.classList.add("active-download-button");
  addEl(button, getTn("Log"));
  addEl(logLink, button);
  addEl(dbTd, logLink);
  addEl(jobTr, dbTd);
  // + button
  var btn = getEl("button");
  btn.classList.add("butn");
  btn.setAttribute("jobid", job.id);
  addEl(btn, getTn("+"));
  btn.classList.add("inactive-download-button");
  btn.addEventListener("click", function (evt) {
    var repSelDiv = document.querySelector("#report_generation_div");
    if (repSelDiv.classList.contains("show")) {
      repSelDiv.classList.remove("show");
      return;
    }
    var jobId = evt.target.getAttribute("jobid");
    var job = GLOBALS.idToJob[jobId];
    var select = document.querySelector("#report_generation_div_select");
    while (select.options.length > 0) {
      select.remove(0);
    }
    for (var i = 0; i < GLOBALS.reports.valid.length; i++) {
      var reportType = GLOBALS.reports.valid[i];
      if (
        websubmitReportBeingGenerated[job.id] != undefined &&
        websubmitReportBeingGenerated[job.id][reportType] == true
      ) {
      } else {
        var option = new Option(reportType, reportType);
        select.add(option);
      }
    }
    var div2 = document.querySelector("#report_generation_div");
    div2.setAttribute("jobid", jobId);
    div2.style.top = evt.clientY + 2 + "px";
    div2.style.right = window.innerWidth - evt.clientX + "px";
    div2.classList.add("show");
  });
  btn.title = "Click to open report generator.";
  addEl(dbTd, btn);
  // Delete
  var deleteTd = getEl("td");
  deleteTd.title = "Click to delete.";
  deleteTd.style.textAlign = "center";
  var deleteBtn = getEl("button");
  deleteBtn.classList.add("butn");
  deleteBtn.classList.add("inactive-download-button");
  /*deleteBtn.classList.add('active-download-button');*/
  addEl(deleteBtn, getTn("X"));
  addEl(deleteTd, deleteBtn);
  deleteBtn.setAttribute("jobId", job.id);
  deleteBtn.addEventListener("click", jobDeleteButtonHandler);
  addEl(jobTr, deleteTd);
  return true;
}

function closeReportGenerationDiv(_) {
  var div = document.querySelector("#report_generation_div");
  div.classList.remove("show");
}

function populateJobDetailTr(job) {
  var ji = job.id;
  var detailTr = $("tr.job-detail-tr[jobid=" + ji + "]")[0];
  emptyElement(detailTr);
  // Job detail row
  var annots = job.annotators;
  var annotVers = job.annotator_version;
  var annotVerStr = "";
  if (annots == undefined || annots.length == 0) {
    annotVerStr = "None";
  } else {
    for (var j = 0; j < annots.length; j++) {
      var annot = annots[j];
      var ver = null;
      if (annotVers != undefined) {
        ver = annotVers[annot];
        if (ver == undefined) {
          ver = null;
        }
      }
      if (ver == null) {
        annotVerStr += annot + ", ";
      } else {
        annotVerStr += annot + "(" + ver + "), ";
      }
    }
    annotVerStr = annotVerStr.replace(/, $/, "");
  }
  var detailTd = getEl("td");
  detailTd.colSpan = "8";
  var detailTable = getEl("table");
  detailTable.style.width = "100%";
  var tbody = getEl("tbody");
  addEl(detailTable, tbody);
  var tr = getEl("tr");
  if (job.open_cravat_version != undefined) {
    var tr = getEl("tr");
    var td = getEl("td");
    td.textContent = "OakVar ver";
    addEl(tr, td);
    var td = getEl("td");
    td.textContent = job.open_cravat_version;
    addEl(tr, td);
    addEl(tbody, tr);
  }
  var tr = getEl("tr");
  var td = getEl("td");
  td.style.width = "160px";
  td.textContent = "Annotators";
  addEl(tr, td);
  var td = getEl("td");
  td.textContent = annotVerStr;
  addEl(tr, td);
  addEl(tbody, tr);
  if (job.num_unique_var != undefined) {
    var tr = getEl("tr");
    var td = getEl("td");
    td.textContent = "# unique input variants";
    addEl(tr, td);
    var td = getEl("td");
    td.textContent = job.num_unique_var;
    addEl(tr, td);
    addEl(tbody, tr);
  }
  if (job.submission_time != undefined) {
    var tr = getEl("tr");
    var td = getEl("td");
    td.textContent = "Submitted";
    addEl(tr, td);
    var td = getEl("td");
    if (job.submission_time == "Invalid Date") {
      td.textContent = "";
    } else {
      var t = new Date(job.submission_time);
      var month = t.getMonth() + 1;
      if (month < 10) {
        month = "0" + month;
      }
      var d = t.getDate();
      if (d < 10) {
        d = "0" + d;
      }
      var h = t.getHours();
      if (h < 10) {
        h = "0" + h;
      }
      var m = t.getMinutes();
      if (m < 10) {
        m = "0" + m;
      }
      var s = t.getSeconds();
      if (s < 10) {
        s = "0" + s;
      }
      td.textContent =
        t.getFullYear() + "." + month + "." + d + " " + h + ":" + m + ":" + s;
    }
    addEl(tr, td);
    addEl(tbody, tr);
  }
  if (job.db_path != undefined && job.db_path != "") {
    var tr = getEl("tr");
    var td = getEl("td");
    td.textContent = "Result DB";
    addEl(tr, td);
    var td = getEl("td");
    var button = getEl("button");
    button.textContent = "DB";
    button.setAttribute("db", job.id);
    button.addEventListener("click", function (evt) {
      window.open("/submit/jobs/" + evt.target.getAttribute("db") + "/db");
    });
    addEl(td, button);
    addEl(tr, td);
    addEl(tbody, tr);
  }
  if (job.job_dir != undefined) {
    var tr = getEl("tr");
    var td = getEl("td");
    td.textContent = "Job Directory";
    addEl(tr, td);
    var td = getEl("td");
    var a = getEl("span");
    a.textContent = job.job_dir;
    addEl(td, a);
    addEl(tr, td);
    addEl(tbody, tr);
  }
  // input files
  var input_fname = job.orig_input_fname;
  if (Array.isArray(job.orig_input_fname)) {
    input_fname = job.orig_input_fname.join(", ");
  }
  var tr = getEl("tr");
  var td = getEl("td");
  td.textContent = "Input file(s)";
  addEl(tr, td);
  var td = getEl("td");
  var sdiv = getEl("div");
  sdiv.style.maxHeight = "80px";
  sdiv.style.overflow = "auto";
  sdiv.textContent = input_fname;
  addEl(td, sdiv);
  addEl(tr, td);
  addEl(tbody, tr);
  addEl(detailTd, detailTable);
  addEl(detailTr, detailTd);
}

function buildJobsTable() {
  var allJobs = GLOBALS.jobs;
  var i = submittedJobs.length - 1;
  while (i >= 0) {
    var submittedJob = submittedJobs[i];
    var alreadyInList = false;
    var submittedJobInList = null;
    for (var j = 0; j < allJobs.length; j++) {
      if (allJobs[j] == submittedJob["id"]) {
        alreadyInList = true;
        submittedJobInList = GLOBALS.idToJob[allJobs[j]];
        break;
      }
    }
    if (alreadyInList) {
      if (submittedJobInList["status"]["status"] != "Submitted") {
        submittedJobs.pop();
      }
    } else {
      submittedJob.status = "Submitted";
      allJobs.unshift(submittedJob.id);
    }
    i--;
  }
  var reportSelectors = $(".report-type-selector");
  var curSelectedReports = {};
  for (let i = 0; i < reportSelectors.length; i++) {
    var selector = $(reportSelectors[i]);
    var jobId = selector.attr("jobId");
    var val = selector.val();
    curSelectedReports[jobId] = val;
  }
  var headerTr = document.querySelector("#jobs-table thead tr");
  if (adminMode == true) {
    var firstTd = headerTr.firstChild;
    if (firstTd.textContent != "User") {
      var td = getEl("th");
      td.textContent = "User";
      headerTr.prepend(td);
    }
  }
  var jobsTable = document.querySelector("#jobs-table tbody");
  $(jobsTable).empty();
  fillJobTable(allJobs, jobsListCurStart, jobsListCurEnd, jobsTable);
}

function fillJobTable(allJobs, start, end, jobsTable) {
  for (let i = start; i < Math.min(end, allJobs.length); i++) {
    job = GLOBALS.idToJob[allJobs[i]];
    if (job == undefined) {
      continue;
    }
    ji = job.id;
    if (ji == undefined) {
      continue;
    }
    var jobTr = getEl("tr");
    jobTr.classList.add("job-table-tr");
    jobTr.classList.add("job-table-main-tr");
    jobTr.setAttribute("jobid", ji);
    jobTr.addEventListener("click", onClickJobTableMainTr);
    addEl(jobsTable, jobTr);
    var ret = populateJobTr(job);
    if (ret == null) {
      jobsTable.removeChild(jobTr);
      continue;
    }
    var detailTr = getEl("tr");
    detailTr.classList.add("job-detail-tr");
    detailTr.classList.add("hidden-tr");
    detailTr.setAttribute("jobid", ji);
    addEl(jobsTable, detailTr);
    populateJobDetailTr(job);
  }
}

function onClickJobsListPrevPage() {
  jobsListCurEnd -= jobsPerPageInList;
  if (jobsListCurEnd < jobsPerPageInList) {
    jobsListCurEnd = jobsPerPageInList;
  }
  jobsListCurStart = jobsListCurEnd - jobsPerPageInList;
  jobsListCurStart = Math.min(
    Math.max(0, jobsListCurStart),
    GLOBALS.jobs.length
  );
  jobsListCurEnd = Math.max(0, Math.min(jobsListCurEnd, GLOBALS.jobs.length));
  showJobListPage();
}

function onClickJobsListNextPage() {
  jobsListCurStart += jobsPerPageInList;
  if (jobsListCurStart >= GLOBALS.jobs.length) {
    jobsListCurStart =
      GLOBALS.jobs.length - (GLOBALS.jobs.length % jobsPerPageInList);
  }
  jobsListCurEnd = jobsListCurStart + jobsPerPageInList;
  jobsListCurStart = Math.min(
    Math.max(0, jobsListCurStart),
    GLOBALS.jobs.length
  );
  jobsListCurEnd = Math.max(0, Math.min(jobsListCurEnd, GLOBALS.jobs.length));
  showJobListPage();
}

function reportSelectorChangeHandler(event) {
  var selector = $(event.target);
  var downloadBtn = selector.siblings(".report-download-button");
  var jobId = selector.attr("jobId");
  var reportType = selector.val();
  var job = GLOBALS.idToJob[jobId];
  /*
    for (let i=0; i<GLOBALS.jobs.length; i++) {
        if (GLOBALS.idToJob[GLOBALS.jobs[i].id] === jobId) {
            job = GLOBALS.jobs[i];
            break;
        }
    }
    */
  downloadBtn.attr("disabled", !job.reports.includes(reportType));
}

function jobReportDownloadButtonHandler(evt) {
  var btn = evt.target;
  var j = btn.getAttribute("jobid");
  var reportType = btn.getAttribute("report-type");
  downloadReport(j, reportType);
}

function downloadReport(j, reportType) {
  url = "/submit/downloadreport/" + reportType;
  var form = getEl("form");
  form.setAttribute("action", url);
  form.setAttribute("method", "post");
  var input1 = getEl("input");
  input1.setAttribute("type", "hidden");
  input1.setAttribute("name", "data");
  input1.setAttribute("value", j);
  addEl(form, input1);
  var body = document.getElementsByTagName("body")[0];
  addEl(body, form);
  form.submit();
  form.remove();
}

function getEl(tag) {
  return document.createElement(tag);
}

function jobDeleteButtonHandler(event) {
  event.stopPropagation();
  var jobId = $(event.target).attr("jobId");
  document
    .querySelectorAll('#jobs-table tr.job-table-tr[jobid="' + jobId + '"] td')
    .forEach(function (el) {
      el.classList.add("strikenout");
    });
  deleteJob(jobId);
}

function deleteJob(jobId) {
  $.ajax({
    url: "/submit/jobs/" + jobId,
    type: "DELETE",
    contentType: "application/json",
    success: function (_) {
      populateJobs().then(() => {
        showJobListPage();
      });
    },
  });
  delete jobRunning[jobId];
  let delIdx = null;
  for (var i = 0; i < submittedJobs.length; i++) {
    if (submittedJobs[i].id === jobId) {
      delIdx = i;
      break;
    }
  }
  if (delIdx !== null) {
    submittedJobs = submittedJobs
      .slice(0, delIdx)
      .concat(submittedJobs.slice(delIdx + 1));
  }
}

function getGenomeAssemblyDiv() {
  return document.querySelector("#assembly-select-panel");
}

function getGenomeAssemblySelection() {
  var assembly = getGenomeAssemblyDiv().getAttribute("value");
  if (assembly == "" || assembly == "auto") {
    assembly = DEFAULT_GENOME_ASSEMBLY;
  }
  return assembly;
}

function inputExampleChangeHandler(evt) {
  var format = evt.target.value
  var assembly = getGenomeAssemblySelection()
  var formatAssembly = format + "." + assembly
  if (GLOBALS.inputExamples[formatAssembly] == undefined) {
    var fname = formatAssembly + ".txt"
    axios.get("/submit/input-examples/" + fname)
    .then(function(res) {
      var data = res.data
      document.querySelector("#input-file").value = ""
      GLOBALS.inputExamples[formatAssembly] = data
      var inputArea = getInputTextarea()
      inputArea.value = GLOBALS.inputExamples[formatAssembly]
    })
  } else {
    var inputArea = getInputTextarea()
    inputArea.value = GLOBALS.inputExamples[formatAssembly]
  }
  setTimeout(function() {
    doSmartShowHideAnalysisModuleChoiceDiv()
  }, 100)
}

function allNoAnnotatorsHandler(event) {
  var elem = $(event.target);
  let checked;
  if (elem.attr("id") === "all-annotators-button") {
    checked = true;
  } else {
    checked = false;
  }
  var annotCheckBoxes = $(".annotator-checkbox");
  for (var i = 0; i < annotCheckBoxes.length; i++) {
    var cb = annotCheckBoxes[i];
    cb.checked = checked;
  }
}

function showJobListPage() {
  var jis = GLOBALS.jobs.slice(jobsListCurStart, jobsListCurEnd);
  document.querySelector("#jobdivspinnerdiv").classList.remove("hide");
  axios
    .get("/submit/getjobs", { params: { ids: JSON.stringify(jis) } })
    .then(function (response) {
      document.querySelector("#jobdivspinnerdiv").classList.add("hide");
      for (var i = 0; i < response.length; i++) {
        var job = response[i];
        addJob(job);
      }
      buildJobsTable();
      if (jobListUpdateIntervalFn == null) {
        jobListUpdateIntervalFn = setInterval(function () {
          var runningJobIds = Object.keys(jobRunning);
          var runningReportIds = Object.keys(reportRunning);
          var combinedIds = runningJobIds.concat(runningReportIds);
          if (combinedIds.length == 0) {
            return;
          }
          axios
            .get("/submit/getjobs", {
              params: { ids: JSON.stringify(combinedIds) },
            })
            .then(function (response) {
              try {
                for (var i = 0; i < response.length; i++) {
                  var job = response[i];
                  GLOBALS.idToJob[job.id] = job;
                  if (
                    job.status == "Finished" ||
                    job.status == "Aborted" ||
                    job.status == "Error"
                  ) {
                    delete jobRunning[job.id];
                  }
                  if (reportRunning[job.id] != undefined) {
                    var reportTypes = Object.keys(reportRunning[job.id]);
                    for (var j = 0; j < reportTypes.length; j++) {
                      var reportType = reportTypes[j];
                      if (job.reports.includes(reportType)) {
                        delete reportRunning[job.id][reportType];
                        delete websubmitReportBeingGenerated[job.id][
                          reportType
                        ];
                        if (Object.keys(reportRunning[job.id]).length == 0) {
                          delete reportRunning[job.id];
                          delete websubmitReportBeingGenerated[job.id];
                        }
                      }
                    }
                  }
                  updateRunningJobTrs(job);
                }
              } catch (e) {
                console.error(e);
              }
            })
            .catch(function (_) {
              console.error(e);
            });
        }, 1000);
      }
    })
    .catch(function (err) {
      console.error(err);
    });
}

function populateJobs() {
  return new Promise((_a, _) => {
    $.ajax({
      url: "/submit/jobs",
      type: "GET",
      async: true,
      success: function (response) {
        GLOBALS.jobs = response;
        jobsListCurStart = 0;
        jobsListCurEnd = jobsListCurStart + jobsPerPageInList;
        showJobListPage();
      },
      fail: function (_) {
        alert("fail at populate jobs");
      },
    });
  });
}

function refreshJobsTable() {
  populateJobs();
}

function titleCase(str) {
  return str.replace(/\w\S*/g, function (txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
}

function collectDeveloperProvidedTags() {
  collectedTags = [NO_TAG];
  for (var module in localModuleInfo) {
    var ty = localModuleInfo[module].type;
    if (ty != "annotator" && ty != "postaggregator") {
      continue;
    }
    var tags = localModuleInfo[module].tags;
    for (var i = 0; i < tags.length; i++) {
      var tag = tags[i];
      if (collectedTags.indexOf(tag) == -1) {
        collectedTags.push(tag);
      }
    }
  }
  collectedTags.sort();
}

function escapeTag(s) {
  return s.replace(" ", "_");
}

function getModuleFilterItem(value, kind, handler) {
  let div = getEl("div");
  div.classList.add(...stringToArray("relatve flex items-start mb-2"))
  var div2 = getEl("div");
  div2.classList.add(...stringToArray("flex items-center"))
  addEl(div, div2);
  var cb = getEl("input");
  var valueEscaped = escapeTag(value);
  var uid = "module-" + kind + "-radio-" + valueEscaped;
  cb.id = uid;
  cb.type = "radio";
  cb.name = "module-" + kind;
  cb.setAttribute("value", value);
  cb.classList.add(...stringToArray("h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"))
  if (handler) {
    cb.addEventListener("change", function (evt) {
      handler(evt);
    });
  }
  addEl(div2, cb);
  var label = getEl("label");
  label.setAttribute("for", uid);
  label.classList.add(...stringToArray("ml-3 block text-sm font-medium text-gray-600"))
  label.textContent = titleCase(value);
  addEl(div2, label);
  return div;
}

function buildAllSelector() {
  var wrapper = document.querySelector("#analysis-module-filter-items-all");
  var div = getModuleFilterItem("All", "all", null);
  addEl(wrapper, div);
}

function populateModuleFilterPanelAll() {
  populateFilteredModules("all", function (_) {
    return true;
  });
}

function populateModuleFilterPanelTags() {
  collectDeveloperProvidedTags();
  var wrapper = document.querySelector("#analysis-module-filter-items-tags");
  for (let tag of collectedTags) {
    var div = getModuleFilterItem(tag, "tag", onChangeModuleTag);
    addEl(wrapper, div);
  }
}

function getFilteredModulesDiv(kind) {
  return document.querySelector("#filtered-modules-" + kind);
}

function populateFilteredModules(kind, func) {
  var div = getFilteredModulesDiv(kind);
  div.replaceChildren();
  for (var moduleName of moduleNames[AP_KEY]) {
    var data = moduleDatas[AP_KEY][moduleName];
    if (func(data)) {
      var card = getModuleCard(data, callbackClickModuleCardAP)
      addEl(div, card);
    }
  }
}

function onChangeModuleTag(evt) {
  var tag = evt.target.value;
  var func = function (data) {
    return (
      (tag == NO_TAG && data.tags.length == 0) || data.tags.indexOf(tag) >= 0
    );
  };
  populateFilteredModules("tags", func);
}

function getModuleInfoByTypes(...types) {
  var modules = []
  for (var i=0; i<types.length; i++) {
    modules = modules.concat(getModuleInfoByType(types[i]))
  }
  modules.sort(titleSortFunc)
  return modules
}

function getModuleData(module) {
  return {
    name: module.name,
    value: module.name,
    title: module.title,
    type: module.type,
    checked: false,
    kind: "module",
    groups: module["groups"],
    desc: module.description,
    tags: module.tags,
  }
}

function makeModuleDatas(key, types) {
  var modules = getModuleInfoByTypes(...types)
  moduleDatas[key] = {}
  moduleNames[key] = []
  for (let i = 0; i < modules.length; i++) {
    var module = modules[i];
    moduleDatas[key][module.name] = getModuleData(module)
    moduleNames[key].push(module.name)
  }
}

function removeNonfileReporterModuleDatas() {
  for (var name in moduleDatas[R_KEY]) {
    var conf = localModuleInfo[name].conf
    if (! conf || conf["output_filename_schema"] == undefined) {
      delete moduleDatas[R_KEY][name]
    }
  }
}

async function makeAllModuleDatas() {
  makeModuleDatas(AP_KEY, ["annotator", "postaggregator"])
  makeModuleDatas(R_KEY, ["reporter"])
  removeNonfileReporterModuleDatas()
}

function onTabChange() {
  var submitcontentdiv = document.getElementById("submitcontentdiv");
  var jobdiv = document.getElementById("jobdiv");
  var tab = document.getElementById("tabselect").selectedIndex;
  if (tab == 0) {
    submitcontentdiv.style.display = "block";
    jobdiv.style.display = "none";
  } else if (tab == 1) {
    submitcontentdiv.style.display = "none";
    jobdiv.style.display = "block";
  }
}

function getJobsDir() {
  $.get("/submit/getjobsdir").done(function (_) {});
}

function setJobsDir(evt) {
  var d = evt.target.value;
  $.get("/submit/setjobsdir", { jobsdir: d }).done(function (_) {
    populateJobsTable();
  });
}

function transitionToStore() {
  var submitdiv = document.getElementById("submitdiv");
  var storediv = document.getElementById("storediv");
  var settingsdiv = document.getElementById("settingsdiv");
  submitdiv.style.display = "none";
  storediv.style.display = "block";
  settingsdiv.style.display = "none";
}

function transitionToSubmit() {
  var submitdiv = document.getElementById("submitdiv");
  var storediv = document.getElementById("storediv");
  var settingsdiv = document.getElementById("settingsdiv");
  submitdiv.style.display = "block";
  storediv.style.display = "none";
  settingsdiv.style.display = "none";
}

function transitionToSettings() {
  var settingsdiv = document.getElementById("settingsdiv");
  var submitdiv = document.getElementById("submitdiv");
  var storediv = document.getElementById("storediv");
  submitdiv.style.display = "none";
  storediv.style.display = "none";
  settingsdiv.style.display = "block";
}

function changePage(selectedPageId) {
  var pageselect = document.getElementById("pageselect");
  var pageIdDivs = pageselect.children;
  for (var i = 0; i < pageIdDivs.length; i++) {
    var pageIdDiv = pageIdDivs[i];
    var pageId = pageIdDiv.getAttribute("value");
    var page = document.getElementById(pageId);
    if (page.id == selectedPageId) {
      page.style.display = "block";
      pageIdDiv.setAttribute("selval", "t");
      if (selectedPageId == "storediv") {
        currentTab = "store";
      } else if (selectedPageId == "submitdiv") {
        currentTab = "submit";
      }
    } else {
      page.style.display = "none";
      pageIdDiv.setAttribute("selval", "f");
    }
  }
}

function openSubmitDiv() {
  var div = document.getElementById("submitcontentdiv");
  div.style.display = "block";
}

async function loadSystemConf() {
  var response = await axios.get("/submit/getsystemconfinfo");
  systemConf = response;
  systemConf["oc_store_url"] = "https://store.opencravat.org";
  var s = document.getElementById("sysconfpathspan");
  s.value = response["conf_path"];
  var s = document.getElementById("settings_jobs_dir_input");
  s.value = response["jobs_dir"];
  var span = document.getElementById("server_user_span");
  span.textContent = "";
  var s = document.getElementById("settings_modules_dir_input");
  s.value = response["modules_dir"];
  var s = document.getElementById("settings_gui_input_size_limit");
  var cutoff = parseInt(response["gui_input_size_limit"]);
  s.value = cutoff;
  var s = document.getElementById("settings_max_num_concurrent_jobs");
  s.value = parseInt(response["max_num_concurrent_jobs"]);
  var s = document.getElementById(
    "settings_max_num_concurrent_annotators_per_job"
  );
  s.value = parseInt(response["max_num_concurrent_annotators_per_job"]);
}

function onClickSaveSystemConf() {
  document.getElementById("settingsdiv").style.display = "none";
  updateSystemConf();
}

function updateSystemConf() {
  $.get("/submit/getsystemconfinfo").done(function (response) {
    var s = document.getElementById("sysconfpathspan");
    response["path"] = s.value;
    var s = document.getElementById("settings_jobs_dir_input");
    response["content"]["jobs_dir"] = s.value;
    var s = document.getElementById("settings_modules_dir_input");
    response["content"]["modules_dir"] = s.value;
    var s = document.getElementById("settings_gui_input_size_limit");
    response["content"]["gui_input_size_limit"] = parseInt(s.value);
    var s = document.getElementById("settings_max_num_concurrent_jobs");
    response["content"]["max_num_concurrent_jobs"] = parseInt(s.value);
    var s = document.getElementById(
      "settings_max_num_concurrent_annotators_per_job"
    );
    response["content"]["max_num_concurrent_annotators_per_job"] = parseInt(
      s.value
    );
    $.ajax({
      url: "/submit/updatesystemconf",
      data: { sysconf: JSON.stringify(response["content"]) },
      type: "GET",
      success: function (response) {
        if (response["success"] == true) {
          var mdiv = getEl("div");
          var span = getEl("span");
          span.textContent = "System configuration has been updated.";
          addEl(mdiv, span);
          addEl(mdiv, getEl("br"));
          addEl(mdiv, getEl("br"));
          var justOk = true;
          showYesNoDialog(mdiv, null, false, justOk);
        } else {
          var mdiv = getEl("div");
          var span = getEl("span");
          span.textContent = "System configuration was not successful";
          addEl(mdiv, span);
          addEl(mdiv, getEl("br"));
          addEl(mdiv, getEl("br"));
          var span = getEl("span");
          span.textContent = response["msg"];
          addEl(mdiv, span);
          addEl(mdiv, getEl("br"));
          addEl(mdiv, getEl("br"));
          var justOk = true;
          showYesNoDialog(mdiv, null, false, justOk);
          return;
        }
        if (response["sysconf"]["jobs_dir"] != undefined) {
          populateJobs();
          getLocal((callUpdateFlag = true)).then()
          makeModuleDatas().then(function (_) {});
        }
      },
    });
  });
}

function resetSystemConf() {
  loadSystemConf();
}

async function loadUserSettings() {
  var res = await axios.get("/server/usersettings");
  console.log("usersettings=", res);
  GLOBALS.usersettings = res;
  setLastAssembly();
}

async function populatePackageVersions() {
  res = await axios.get("/submit/packageversions")
  var data = res.data;
  var curverspan = document.querySelector("#verdiv .curverspan");
  if (data.update) {
    var a = getEl("a");
    a.href = "https://github.com/rkimoakbioinformatics/oakvar";
    a.target = "_blank";
    a.textContent = data.current;
    a.style.color = "red";
    addEl(curverspan, a);
  } else {
    curverspan.textContent = data.current;
  }
}

function onClickThreeDots(evt) {
  var div = document.getElementById("settingsdiv");
  var display = div.style.display;
  if (display == "block") {
    display = "none";
  } else {
    display = "block";
  }
  div.style.display = display;
  evt.stopPropagation();
}

function hideAnalysisModuleChoiceDiv() {
  var div = getAnalysisModuleChoiceDiv()
  div.classList.add("hidden")
}

function showAnalysisModuleChoiceDiv() {
  var div = getAnalysisModuleChoiceDiv()
  div.classList.remove("hidden")
}

function setupEventListeners() {
  //$("#submit-job-button").click(submit);
  //$("#input-text").change(onInputFileChange);
  //$("#input-file").change(onInputFileChange);
  //$("#all-annotators-button").click(allNoAnnotatorsHandler);
  //$("#no-annotators-button").click(allNoAnnotatorsHandler);
  //$("#refresh-jobs-table-btn").click(refreshJobsTable);
  //$(".threedotsdiv").click(onClickThreeDots);
  //$(".jobsdirinput").change(setJobsDir);
  //$("#chaticondiv").click(toggleChatBox);
  document.addEventListener("click", function (evt) {
    if (
      evt.target.classList.contains("moduledetaildiv-submit-elem") == false &&
      evt.target.closest(".moduledetailbutton") == null
    ) {
      var div = document.getElementById("moduledetaildiv_submit");
      if (div != null) {
        div.style.display = "none";
      }
    }
    if (evt.target.classList.contains("moduledetaildiv-store-elem") == false) {
      var div = document.getElementById("moduledetaildiv_store");
      if (div != null) {
        div.style.display = "none";
      }
      storeModuleDivClicked = false;
    } else {
      storeModuleDivClicked = true;
    }
    if (
      evt.target.id != "settingsdots" &&
      evt.target.id != "settingsdiv" &&
      evt.target.classList.contains("settingsdiv-elem") == false
    ) {
      var div = document.getElementById("settingsdiv");
      if (div != null) {
        div.style.display = "none";
      }
    }
    if (evt.target.id == "report_generation_generate_button") {
      createJobReport(evt);
    } else if (evt.target.id == "report_generation_close_button") {
      closeReportGenerationDiv();
    }
  });
  window.addEventListener("resize", function (_) {
    var moduledetaildiv = document.getElementById("moduledetaildiv_submit");
    if (moduledetaildiv != null) {
      var tdHeight = window.innerHeight * 0.8 - 150 + "px";
      var tds = document
        .getElementById("moduledetaildiv_submit")
        .getElementsByTagName("table")[1]
        .getElementsByTagName("td");
      tds[0].style.height = tdHeight;
      tds[1].style.height = tdHeight;
    }
    var moduledetaildiv = document.getElementById("moduledetaildiv_store");
    if (moduledetaildiv != null) {
      var tdHeight = window.innerHeight * 0.8 - 150 + "px";
      var tds = document
        .getElementById("moduledetaildiv_store")
        .getElementsByTagName("table")[1]
        .getElementsByTagName("td");
      tds[0].style.height = tdHeight;
      tds[1].style.height = tdHeight;
    }
  });
  document.addEventListener("keyup", function (evt) {
    if (storeModuleDivClicked) {
      var k = evt.key;
      var moduleDiv = document.getElementById("moduledetaildiv_store");
      var moduleListName = moduleDiv.getAttribute("modulelistname");
      var moduleListPos = moduleDiv.getAttribute("modulelistpos");
      var moduleList = moduleLists[moduleListName];
      if (k == "ArrowRight") {
        moduleListPos++;
        if (moduleListPos >= moduleList.length) {
          moduleListPos = 0;
        }
        var moduleName = moduleList[moduleListPos];
        makeModuleDetailDialog(moduleName, moduleListName, moduleListPos);
        evt.stopPropagation();
      } else if (k == "ArrowLeft") {
        moduleListPos--;
        if (moduleListPos < 0) {
          moduleListPos = moduleList.length - 1;
        }
        var moduleName = moduleList[moduleListPos];
        makeModuleDetailDialog(moduleName, moduleListName, moduleListPos);
        evt.stopPropagation();
      }
    }
  });
}

function setLastAssembly() {
  let sel = document.getElementById("assembly-select");
  if (GLOBALS.usersettings.hasOwnProperty("lastAssembly")) {
    sel.value = GLOBALS.usersettings.lastAssembly;
  }
}

function getJobById(jobId) {
  return GLOBALS.idToJob[jobId];
}

function updateRunningJobTrs(job) {
  var idx = GLOBALS.jobs.indexOf(job.id);
  if (idx < jobsListCurStart || idx >= jobsListCurEnd) {
    return;
  }
  populateJobTr(job);
  populateJobDetailTr(job);
}

function onSubmitClickTagBoxCheck(evt) {
  var div = document.getElementById("analysis-module-filter-div");
  if (evt.target.checked) {
    div.className = "on";
  } else {
    div.className = "off";
  }
}

function getChevronDown() {
  var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.classList.add("-mr-1", "ml-2", "h-5", "w-5");
  svg.setAttribute("viewBox", "0 0 20 20");
  svg.setAttribute("fill", "currentColor");
  svg.setAttribute("aria-hidden", "true");
  var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("fill-rule", "evenodd");
  path.setAttribute("clip-rule", "evenodd");
  path.setAttribute(
    "d",
    "M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
  );
  addEl(svg, path);
  return svg;
}

function populateInputFormats() {
  var div = document.querySelector("#input-format-select").querySelector("div");
  var modules = getModuleInfoByType("converter")
  for (var i=0; i<modules.length; i++) {
    let format = modules[i].name.split("-")[0];
    let a = getEl("a");
    a.classList.add(
      "text-gray-600",
      "block",
      "px-4",
      "py-2",
      "text-sm",
      "text-right",
      "hover:bg-gray-100",
      "hover:text-gray-900"
    );
    a.setAttribute("role", "menuitem");
    a.addEventListener("click", function (evt) {
      onClickSelectItem(evt);
    });
    a.textContent = format;
    addEl(div, a);
  }
}

function importJob() {
  let fileSel = document.querySelector("#job-import-file");
  if (fileSel.files.length === 0) return;
  var req = new XMLHttpRequest();
  req.open("POST", "/submit/import");
  req.setRequestHeader(
    "Content-Disposition",
    `attachment; filename=${fileSel.files[0].name}`
  );
  req.upload.onprogress = function (evt) {
    var uploadPerc = (evt.loaded / evt.total) * 100;
    document.querySelector("#spinner-div-progress-bar").style.width =
      uploadPerc + "%";
    document.querySelector("#spinner-div-progress-num").textContent =
      uploadPerc.toFixed(0) + "%";
  };
  req.onloadend = function (_) {
    hideSpinner();
    refreshJobsTable();
  };
  showSpinner();
  req.send(fileSel.files[0]);
}

function switchToInputPaste() {
  hide(getInputDropArea())
  show(getInputPasteArea())
  doSmartShowHideAnalysisModuleChoiceDiv()
}

function switchToInputUpload() {
  show(getInputDropArea())
  hide(getInputPasteArea())
  doSmartShowHideAnalysisModuleChoiceDiv()
}

function showReportChoiceItemsDiv() {
  show(getReportChoiceDiv())
}

function hideReportChoiceItemsDiv() {
  hide(getReportChoiceDiv())
}

function showSubmitNoteDiv() {
  show(getSubmitNoteDiv())
}

function hideSubmitNoteDiv() {
  hide(getSubmitNoteDiv())
}

function showSubmitJobButtonDiv() {
  show(getSubmitJobButtonDiv())
}

function hideSubmitJobButtonDiv() {
  hide(getSubmitJobButtonDiv())
}

function showCtaAnalysisModuleChoice() {
  show(getCtaAnalysisModuleChoice())
}

function hideCtaAnalysisModuleChoice() {
  hide(getCtaAnalysisModuleChoice())
}

function showJobNameDir() {
  show(getJobNameDir())
}

function hideJobNameDir() {
  hide(getJobNameDir())
}

function hide(el) {
  el.classList.add("hidden")
}

function show(el) {
  el.classList.remove("hidden")
}

function showDivsWhenInputPresent() {
  showAnalysisModuleChoiceDiv()
  showReportChoiceItemsDiv()
  showSubmitNoteDiv()
  showSubmitJobButtonDiv()
  showCtaAnalysisModuleChoice()
  showJobNameDir()
}

function hideDivsWhenInputPresent() {
  hideAnalysisModuleChoiceDiv()
  hideReportChoiceItemsDiv()
  hideSubmitNoteDiv()
  hideSubmitJobButtonDiv()
  hideCtaAnalysisModuleChoice()
  hideJobNameDir()
}

function doSmartShowHideAnalysisModuleChoiceDiv() {
  if (! getInputDropArea().classList.contains("hidden")) {
    if (inputFileList.length > 0) {
      showDivsWhenInputPresent()
    } else {
      hideDivsWhenInputPresent()
    }
  } else if (! getInputPasteArea().classList.contains("hidden")) {
    if (getInputTextarea().value != "") {
      showDivsWhenInputPresent()
    } else {
      hideDivsWhenInputPresent()
    }
  }
}

function getOptionList(evt) {
  return evt.target.closest(".select-div").querySelector(".option-list");
}

function getSelectDiv(evt) {
  return evt.target.closest(".select-div").querySelector("button");
}

function onClickSelectBtn(evt) {
  var el = getOptionList(evt);
  el.classList.toggle("hidden");
}

function getAssemblySelectBtn() {
  return document.querySelector("#assembly-select-div");
}

function onClickSelectItem(evt) {
  var btn = getSelectDiv(evt);
  btn.innerHTML = "";
  addEl(btn, getTn(btn.title + ": " + evt.target.textContent));
  addEl(btn, getChevronDown());
  btn.setAttribute("value", evt.target.getAttribute("value"))
  var el = getOptionList(evt);
  el.classList.toggle("hidden");
}

function onClickInputFormatBtn(_) {
  document.querySelector("#input-format-select").classList.toggle("hidden");
}

function hideAllTabs() {
  document.querySelectorAll(".tabcontent").forEach(function (el) {
    el.classList.add("hidden");
  });
}

function showTab(tabName) {
  var el = document.querySelector("#tab_" + tabName);
  if (el) {
    el.classList.remove("hidden");
  }
}

function showSystemNotReady() {
  hideAllTabs();
  showTab("systemnotready");
}

function getModuleFilterPanel(kind) {
  return document.querySelector("#analysis-module-filter-panel-" + kind);
}

function getModuleFilterItemsDiv(kind) {
  return document.querySelector("#analysis-module-filter-items-" + kind);
}

function shouldUpdateModuleFilterPanelAll() {
  var div = getFilteredModulesDiv("all");
  return div.innerHTML == "";
}

function shouldUpdateModuleFilterPanelTags() {
  var div = getModuleFilterItemsDiv("tags");
  return div.innerHTML == "";
}

function populateModuleFilterPanel(kind) {
  if (kind == "all" && shouldUpdateModuleFilterPanelAll()) {
    populateModuleFilterPanelAll();
  } else if (kind == "tags" && shouldUpdateModuleFilterPanelTags()) {
    populateModuleFilterPanelTags();
  }
}

function unpinAnalysisModuleFilterKindBtns() {
  var els = document.querySelector("#analysis-module-filter-kinds").children
  for (var i = 0; i < els.length; i++) {
    els[i].classList.remove("pinned")
  }
}

function callbackClickModuleCardAP(evt) {
  var target = evt.target.closest(".modulecard");
  var moduleName = target.getAttribute("name");
  var data = moduleDatas[AP_KEY][moduleName];
  toggleSelectedModule(data)
}

function callbackClickModuleCardR(evt) {
  var target = evt.target.closest(".modulecard")
  var moduleName = target.getAttribute("name")
  var data = moduleDatas[R_KEY][moduleName]
  data.checked = ! data.checked
  setModuleCardCheckedStatus(target, data.checked)
}

function populateReportTypes() {
  var div = getReportChoiceItemsDiv()
  for (var name in moduleDatas[R_KEY]) {
    var card = getModuleCard(moduleDatas[R_KEY][name], callbackClickModuleCardR)
    card.classList.add("max-w-xs")
    addEl(div, card)
  }
}

function onClickCtaAnalysisModuleChoice() {
  getAnalysisModuleChoiceDiv().scrollIntoView({behavior: "smooth"})
}

async function websubmit_run() {
  if ((await checkSystemReady()) == false) {
    showSystemNotReady();
    return;
  }
  multiuser_setup();
  if ((await checkLogged(username)) == false) {
    openLoginPage();
  }
  console.log("@ username=", username);
  await loadUserSettings();
  connectWebSocket();
  // Submit
  var taskLocal = getLocal().then(async function() {
    await makeAllModuleDatas()
    populateInputFormats()
    populateReportTypes()
    changeFilterCategory("all")
  })
  // Store
  await getRemote();
  complementRemoteWithLocal();
  setBaseInstalled();
  populateStorePages();
  populateStoreTagPanel();
  updateModuleGroupInfo();
  makeInstalledGroup();
  getBaseModuleNames();
  //setupEventListeners();
  await loadSystemConf();
  //setUploadedInputFilesDiv();
  populatePackageVersions();
}
