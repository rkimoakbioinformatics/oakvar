var JOB_STATUS_COLOR_CLASSES = {"Error": "text-rose-500", "Finished": "text-green-600"}

async function populateJobs(pageno, pagesize) {
  axios
    .get("/submit/jobs", { params: { pageno: pageno, pagesize: pagesize } })
    .then(function (response) {
      var data = response.data;
      if (data && data.length > 0) {
        GLOBALS.jobs = response.data;
        jobsListCurStart = 0;
        jobsListCurEnd = jobsListCurStart + jobsPerPageInList;
        showJobListPage();
        setJobsTablePageNoDisplay(pageno);
      }
    })
    .catch(function (err) {
      console.error(err);
    });
}

function setJobsTablePageNoDisplay(pageno) {
  var el = getJobsTablePageNoEl();
  el.setAttribute("value", pageno);
  el.textContent = pageno;
}

function getJobTrCheckboxTd() {
  var td = getEl("td");
  td.classList.add(...stringToArray("relative w-12 px-6 sm:w-16 sm:px-8"));
  var div = getEl("div");
  div.classList.add(
    ...stringToArray("absolute inset-y-0 left-0 w-0.5 bg-indigo-600")
  );
  addEl(td, div);
  var input = getEl("input");
  input.type = "checkbox";
  input.classList.add(
    ...stringToArray(
      "absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 sm:left-6"
    )
  );
  addEl(div, input);
  return td;
}

function getJobTd() {
  var td = getEl("td");
  var div = getEl("div")
  div.classList.add("jobs-table-td");
  addEl(td, div)
  return td;
}

function getJobNameTd(job) {
  var td = getJobTd();
  var div = td.firstChild
  //div.classList.add("min-w-[10rem]");
  div.textContent = job.name;
  return td;
}

function getJobInputTd(job) {
  var td = getJobTd();
  var div = td.firstChild
  //div.classList.add("min-w-[10rem]");
  var orig_input_fnames = job.statusjson.orig_input_fname;
  var text = "";
  if (orig_input_fnames) {
    if (orig_input_fnames.length == 1) {
      text = orig_input_fnames[0];
    } else {
      text = orig_input_fnames[0] + ", etc";
    }
  }
  div.textContent = text;
  return td;
}

function getJobSubmitTd(job) {
  var td = getJobTd();
  var div = td.firstChild
  //div.classList.add("w-[10rem]");
  var submit = job.statusjson.submission_time;
  if (submit) {
    var d = new Date(submit);
    var t = d.toLocaleString(navigator.language, {
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    });
    div.textContent = t;
  }
  return td;
}

function getJobStateTd(job) {
  var td = getJobTd();
  var div = td.firstChild
  var status = job.statusjson.status;
  div.textContent = status
  if (status in JOB_STATUS_COLOR_CLASSES) {
    div.classList.add(JOB_STATUS_COLOR_CLASSES[status])
  }
  return td;
}

function getJobNoteTd(job) {
  var td = getJobTd();
  var div = td.firstChild
  div.textContent = job.statusjson.note;
  return td;
}

function getJobViewTd(job) {
  var td = getJobTd();
  var div = td.firstChild
  if (job.statusjson.status == "Finished") {
    var a = getEl("a")
    a.href = "/result/nocache/index.html?dbpath=" + encodeURI(job.statusjson.db_path)
    a.setAttribute("target", "_blank")
    a.textContent = "View"
    addEl(div, a)
    div.classList.add(...stringToArray("cursor-pointer text-green-600"))
  }
  return td;
}

function getJobTr(job) {
  var tr = getEl("tr");
  addEl(tr, getJobTrCheckboxTd());
  addEl(tr, getJobNameTd(job));
  addEl(tr, getJobInputTd(job));
  addEl(tr, getJobSubmitTd(job));
  addEl(tr, getJobStateTd(job));
  addEl(tr, getJobNoteTd(job));
  addEl(tr, getJobViewTd(job));
  return tr;
}

function showJobListPage() {
  var tbody = getJobsTbody();
  tbody.replaceChildren();
  var jobs = GLOBALS.jobs;
  for (var i = 0; i < jobs.length; i++) {
    addEl(tbody, getJobTr(jobs[i]));
  }
  /*
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
*/
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

function getJobsTablePageNo() {
  return getJobsTablePageNoEl().getAttribute("value");
}

function onClickJobsTablePageNav(evt) {
  var curPageNo = parseInt(getJobsTablePageNo());
  var pageNoInc = parseInt(
    evt.target.closest(".jobs-table-page-nav-btn").getAttribute("value")
  );
  var newPageNo = curPageNo + pageNoInc;
  if (newPageNo <= 0) {
    return;
  }
  populateJobs(newPageNo, null);
}

function getJobsTableJumpPageNo() {
  var el = getJobsTableJumpPageNoEl()
  try {
    return parseInt(el.value)
  } catch (err) {
    console.error(err)
    return null
  }
}

function onClickJobsTablePageJumpBtn() {
  var pageno = getJobsTableJumpPageNo()
  if (pageno != null && ! isNaN(pageno)) {
    populateJobs(pageno, null)
  }
}

function onKeyupJobsTablePageJumpBtn(evt) {
  if (evt.keyCode == 13) {
    var pageno = getJobsTableJumpPageNo()
    if (pageno != null && ! isNaN(pageno)) {
      populateJobs(pageno, null)
    }
  }
}

