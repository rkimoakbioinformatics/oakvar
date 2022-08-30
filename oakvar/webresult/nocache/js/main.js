function getExportContent(tabName) {
  var conditionDic = {
    contain: "contains",
    lte: "less than",
    gte: "greater than",
  };
  // Writes job information.
  var content = "";
  content += "# OakVar Report\n";
  content += "# Result database: " + dbPath + "\n";
  content += "# Report section (tab): " + tabName + "\n";
  // Writes filters.
  content += "# Load filters: ";
  content += JSON.stringify(filterJson) + "\n";
  content += "# Table filters:\n";
  var colTitles = [];
  var colGroups = $grids[tabName].pqGrid("option", "colModel");
  var colNos = [];
  var colNo = -1;
  var colGroupTitles = [];
  var colGroupNumCols = {};
  for (var colGroupNo = 0; colGroupNo < colGroups.length; colGroupNo++) {
    var colGroup = colGroups[colGroupNo];
    var cols = colGroup.colModel;
    var colExist = false;
    var numCols = 0;
    for (var j = 0; j < cols.length; j++) {
      colNo++;
      var col = cols[j];
      if (col.hidden) {
        continue;
      }
      colExist = true;
      colNos.push(col.dataIndx);
      numCols++;
      colTitles.push(col.title.replace(" ", "_"));
      var filter = col.filter;
      if (filter != undefined) {
        if (filter.on == true) {
          var condition = filter.condition;
          var value = filter.value;
          var value2 = filter.value2;
          if (value != "") {
            if (condition in conditionDic) {
              condition = conditionDic[condition];
              content +=
                "#     " + col.title + ": " + condition + " " + value + "\n";
            } else if (condition == "between") {
              content +=
                "#     " +
                col.title +
                ": " +
                condition +
                " " +
                value +
                " and " +
                value2 +
                "\n";
            } else if (col.filter.type == "select") {
              content += "#     " + col.title + ": " + value + "\n";
            } else {
              content +=
                "#     " + col.title + ": " + condition + " " + value + "\n";
            }
          }
        }
      }
    }
    if (colExist) {
      var colGroupTitle = colGroup.title.replace(" ", "_");
      colGroupTitles.push(colGroupTitle);
      colGroupNumCols[colGroupTitle] = numCols;
    }
  }
  // Writes data headers.
  if (colGroupTitles.length == 0) {
    return "";
  }
  content += colGroupTitles[0];
  for (var j = 0; j < colGroupNumCols[colGroupTitles[0]]; j++) {
    content += "\t";
  }
  for (var i = 1; i < colGroupTitles.length; i++) {
    var colGroupTitle = colGroupTitles[i];
    content += colGroupTitle;
    var numCols = colGroupNumCols[colGroupTitle];
    for (var j = 0; j < numCols; j++) {
      content += "\t";
    }
  }
  content += "\n";
  content += colTitles[0];
  for (var i = 1; i < colTitles.length; i++) {
    content += "\t" + colTitles[i];
  }
  content += "\n";
  // Writes data rows.
  var rows = $grids[tabName].pqGrid("option", "dataModel").data;
  for (var rowNo = 0; rowNo < rows.length; rowNo++) {
    var row = rows[rowNo];
    var value = row[colNos[0]];
    if (value == null) {
      value = "";
    }
    content += value;
    for (var i = 1; i < colNos.length; i++) {
      var value = row[colNos[i]];
      if (value == null) {
        value = "";
      }
      content += "\t" + value;
    }
    content += "\n";
  }
  return content;
}

function afterDragNSBar(self, tabName) {
  return;
  var rightDiv = document.getElementById("rightdiv_" + tabName);
  var tableDiv = document.getElementById("tablediv_" + tabName);
  var detailDiv = document.getElementById("detaildiv_" + tabName);
  var cellValueDiv = document.getElementById("cellvaluediv_" + currentTab);
  var dragBar = self;
  var height_bar = self.offsetHeight;
  var dragBarTop = self.offsetTop;
  var dragBarTopUpperLimit = 100;
  if (dragBarTop < dragBarTopUpperLimit) {
    dragBarTop = dragBarTopUpperLimit;
  }
  var dragBarTopLowerLimit = rightDiv.offsetHeight - 50;
  if (dragBarTop > dragBarTopLowerLimit) {
    dragBarTop = dragBarTopLowerLimit;
  }
  self.style.top = dragBarTop - 5 + "px";
  var rightDiv_height = rightDiv.offsetHeight;
  var rightDivTop = rightDiv.offsetTop;
  var cellValueDivHeight = cellValueDiv.offsetHeight;
  var cellValueDivTop = dragBarTop - cellValueDivHeight - 13;
  var height_table = dragBarTop - rightDivTop - cellValueDivHeight;
  var height_detail_div =
    rightDiv_height - height_table - height_bar - cellValueDivHeight - 25;
  var detailDivTop = cellValueDivTop + cellValueDivHeight + 8 + 15;
  $grids[tabName].pqGrid("option", "height", height_table).pqGrid("refresh");
  cellValueDiv.style.top = cellValueDivTop;
  detailDiv.style.top = detailDivTop + "px";
  detailDiv.style.height = height_detail_div;
  var tableMinimized = tableDiv.getAttribute("minimized");
  if (tableMinimized == "true") {
    $(tableDiv).find(".ui-icon-circle-triangle-s")[0].click();
  }
}

function resizesTheWindow(tabName = currentTab) {
  setTableDetailLayout(tabName);
  return;
  var pqTable = $grids[tabName];
  if (pqTable == undefined) {
    return;
  }
  var tableDiv = document.getElementById("tablediv_" + tabName);
  var detailDiv = document.getElementById("detaildiv_" + tabName);
  var nsDragBar = document.getElementById("dragNorthSouthDiv_" + tabName);
  var rightDiv = document.getElementById("rightdiv_" + tabName);
  var cellValueDiv = document.getElementById("cellvaluediv_" + tabName);
  var browserHeight = isNaN(window.innerHeight)
    ? window.clientHeight
    : window.innerHeight;
  var rightDivHeight = browserHeight - 70;
  var tableDivHeight = 0;
  if (tableDiv) {
    tableDivHeight = tableDiv.offsetHeight;
    if (tableDivHeight > rightDivHeight - 50) {
      tableDivHeight = rightDivHeight - 50;
    }
  }
  var nsDragBarHeight = 0;
  if (nsDragBar) {
    nsDragBarHeight = nsDragBar.offsetHeight;
  }
  var cellValueDivHeight = 0;
  if (cellValueDiv) {
    cellValueDivHeight = cellValueDiv.offsetHeight;
    if (cellValueDivHeight > rightDivHeight - tableDivHeight - 100) {
      cellValueDivHeight = rightDivHeight - tableDivHeight - 100;
      cellValueDiv.style.height = cellValueDivHeight + "px";
    }
  }
  var detailDivHeight = 0;
  if (detailDiv) {
    detailDivHeight = detailDiv.offsetHeight;
    if (detailDivHeight > rightDivHeight - 50) {
      detailDivHeight = rightDivHeight - 50;
    }
  }
  var detailDivHeight =
    rightDivHeight - nsDragBarHeight - cellValueDivHeight - tableDivHeight - 28;
  detailDiv.style.height = detailDivHeight + "px";
  var tableDivWidth = "calc(100% - 10px)";
  var cellValueDivTop = tableDivHeight - 9;
  var nsDragBarTop = cellValueDivTop + cellValueDivHeight + 7;
  //rightDiv.style.height = rightDivHeight + 'px';
  tableDiv.style.width = tableDivWidth;
  tableDiv.style.height = tableDivHeight;
  pqTable
    .pqGrid("option", "width", tableDivWidth)
    .pqGrid("option", "height", tableDivHeight)
    .pqGrid("refresh");
  cellValueDiv.style.top = cellValueDivTop + "px";
  nsDragBar.style.top = nsDragBarTop + "px";
  if (detailDiv) {
    detailDiv.style.top = nsDragBarTop + 15 + "px";
    $(detailDiv.getElementsByClassName("detailcontainerdiv")[0]).packery(
      "shiftLayout"
    );
  }
  shouldResizeScreen[tabName] = false;
  onClickDetailRedraw();
  if (tableDetailDivSizes[tabName]["status"] == "detailmax") {
    applyTableDetailDivSizes();
  }
}

function showNoDB() {
  var div = getEl("div");
  div.id = "sorrydiv";
  var img = getEl("img");
  img.src = "/result/images/sorry.png";
  addEl(div, img);
  var span = getEl("p");
  span.style.fontSize = "36px";
  span.textContent = "Sorry...";
  addEl(div, span);
  var span = getEl("p");
  span.style.fontSize = "20px";
  span.textContent = "OakVar was unable to show the job result.";
  addEl(div, span);
  addEl(div, getEl("br"));
  var span = getEl("p");
  span.style.fontSize = "16px";
  span.textContent = "Usually, it is because...";
  addEl(div, span);
  addEl(div, getEl("br"));
  var span = getEl("p");
  span.style.fontSize = "16px";
  span.textContent = "\u2022 Job ID is incorrect.";
  addEl(div, span);
  var span = getEl("p");
  span.style.fontSize = "16px";
  span.textContent = "\u2022 You are not authorized to view this job result.";
  addEl(div, span);
  var span = getEl("p");
  span.style.fontSize = "16px";
  span.textContent = "\u2022 Result database path is wrong.";
  addEl(div, span);
  addEl(document.body, div);
}

async function getResultLevels() {
  const response = await axios.get("/result/service/getresulttablelevels", {
    params: { job_id: jobId, username: username, dbpath: dbPath },
  });
  var levels = response.data.levels;
  pageSize = parseInt(response.data["gui_result_pagesize"]);
  if (levels.length > 0 && levels[0] == "NODB") {
    showNoDB();
  } else {
    resultLevels = levels;
    for (var i = 0; i < resultLevels.length; i++) {
      tableDetailDivSizes[resultLevels[i]] = { status: "both" };
    }
  }
}

/*function makeTabHeadTabBody (resultTableLevel) {
	var tabHeadsDiv = document.getElementById('tabheads');
	var body = document.body;
	var span = getEl('div');
	var div = getEl('div');
	span.id = 'tabhead_' + resultTableLevel;
	div.id = 'tab_' + resultTableLevel;
	span.classList.add('tabhead');
	div.classList.add('tabcontent');
	if (resultTableLevel == currentTab) {
		span.classList.add('show');
		div.classList.add('show');
	} else {
		span.classList.add('hide');
		div.classList.add('hide');
	}
	var tabTitle = resultTableLevel;
	if (tabTitle == 'info') {
		tabTitle = 'summary';
	}
	span.textContent = tabTitle.toUpperCase();
	addEl(tabHeadsDiv, span);
	addEl(body, div);
}*/

/*function addTabHeadsAndTabContentDivs () {
	for (var i = 0; i < resultLevels.length; i++) {
		var resultTableLevel = resultLevels[i];
		makeTabHeadTabBody(resultTableLevel);
        tableDetailDivSizes[resultTableLevel] = {'status': 'both'};
	}
}*/

function disableUpdateButton({ countHigh = false } = {}) {
  var btn = document.getElementById("load_button");
  btn.disabled = true;
}

function enableUpdateButton() {
  var btn = document.getElementById("load_button");
  btn.disabled = false;
  //btn.innerText = "Load";
}

function clearVariantGeneTab() {
  var tabs = ["variant", "gene"];
  for (var i = 0; i < tabs.length; i++) {
    var tab = tabs[i];
    var div = document.getElementById("tab_" + tab);
    div.innerHTML = "";
  }
}

function iterationCopy(src) {
  var target = {};
  for (var prop in src) {
    if (src.hasOwnProperty(prop)) {
      target[prop] = src[prop];
    }
  }
  return target;
}

function copyColModel(colModelGroup) {
  var newColModelGroup = {};
  newColModelGroup.name = colModelGroup.name;
  newColModelGroup.title = colModelGroup.title;
  var newColModel = [];
  var colModel = colModelGroup.colModel;
  for (var i = 0; i < colModel.length; i++) {
    var col = colModel[i];
    var newcol = {};
    newcol.col = col.col;
    newcol.colgroup = col.colgroup;
    newcol.colgroupkey = col.colgroupkey;
    newcol.title = col.title;
    newcol.align = col.align;
    newcol.dataIndx = col.dataIndx;
    newcol.retfilt = col.retfilt;
    newcol.retfilttype = col.retfilttype;
    newcol.multiseloptions = col.multiseloptions;
    newcol.reportsub = col.reportsub;
    newcol.categories = col.categories;
    newcol.width = col.width;
    newcol.desc = col.desc;
    newcol.type = col.type;
    newcol.hidden = col.hidden;
    newcol.default_hidden = col.default_hidden;
    newcol.ctg = col.ctg;
    newcol.filterable = col.filterable;
    newcol.link_format = col.link_format;
    newcol.filter = col.filter;
    newcol.fromgenelevel = true;
    newcol.render = col.render;
    newColModel.push(newcol);
  }
  newColModelGroup.colModel = newColModel;
  return newColModelGroup;
}

function addGeneLevelToVariantLevel() {
  var oriNoColVar = infomgr.columnss.variant.length;
  var geneColModels = infomgr.colModels["gene"];
  var colNo = oriNoColVar;
  var colgroupsToSkip = [];
  var colsToSkip = [];
  for (var i = 0; i < geneColModels.length; i++) {
    var colModel = geneColModels[i];
    if (colModel.name == "base" || colModel["genesummary"] == true) {
      colgroupsToSkip.push(colModel.name);
      for (var j = 0; j < colModel.colModel.length; j++) {
        colsToSkip.push(colModel.colModel[j].col);
      }
      continue;
    }
    var colModel = copyColModel(geneColModels[i]);
    infomgr.colModels["variant"].push(colModel);
  }
  // Sorts colModel.
  var vcm = infomgr.colModels["variant"];
  for (var i = 0; i < vcm.length - 1; i++) {
    for (var j = i + 1; j < vcm.length; j++) {
      var cmi = vcm[i];
      var cmj = vcm[j];
      if (cmi.name == "base" || cmi.name == "tagsampler") {
        continue;
      }
      if (cmi.title.toLowerCase() > cmj.title.toLowerCase()) {
        var tmp = cmi;
        vcm[i] = cmj;
        vcm[j] = tmp;
      }
    }
  }
  // assigns dataIndx to variant colModels.
  var vcm = infomgr.colModels["variant"];
  var varDataIndx = 0;
  var colNoDict = {};
  var varColumnss = [];
  var varColumngroupss = {};
  var varColumnnoss = {};
  for (var i = 0; i < vcm.length; i++) {
    var varColModel = vcm[i].colModel;
    var varColNames = [];
    for (var j = 0; j < varColModel.length; j++) {
      var varCol = varColModel[j];
      var level = "variant";
      if (varCol.fromgenelevel == true) {
        level = "gene";
      }
      colNoDict[varDataIndx] = { level: level, colno: varCol.dataIndx };
      varCol.dataIndx = varDataIndx;
      varColumnnoss[varCol.col] = varDataIndx;
      varDataIndx++;
      varColumnss.push(varCol);
      varColNames.push(varCol.col);
    }
    varColumngroupss[vcm[i].name] = varColNames;
  }
  infomgr.columnss.variant = varColumnss;
  infomgr.columngroupss.variant = varColumngroupss;
  infomgr.columnnoss.variant = varColumnnoss;
  // column default hidden exist
  var vcs = Object.keys(infomgr.colgroupdefaulthiddenexist.variant);
  var gcs = Object.keys(infomgr.colgroupdefaulthiddenexist.gene);
  for (var i = 0; i < gcs.length; i++) {
    var colgrpname = gcs[i];
    if (vcs.indexOf(colgrpname) == -1) {
      infomgr.colgroupdefaulthiddenexist["variant"][colgrpname] = JSON.parse(
        JSON.stringify(infomgr.colgroupdefaulthiddenexist["gene"][colgrpname])
      );
    }
  }
  // dataModel
  var geneDataModels = infomgr.datas.gene;
  geneRows = {};
  for (var i = 0; i < geneDataModels.length; i++) {
    var row = geneDataModels[i];
    var hugo = row[0];
    geneRows[hugo] = row;
  }
  var hugoColNo = infomgr.getColumnNo("variant", "base__hugo");
  function convertToInt(v) {
    return parseInt(v);
  }
  var numCols = Math.max(...Object.keys(colNoDict).map(convertToInt)) + 1;
  for (var varRowNo = 0; varRowNo < infomgr.datas.variant.length; varRowNo++) {
    var varRow = infomgr.datas.variant[varRowNo];
    var hugo = varRow[hugoColNo];
    var geneRow = geneRows[hugo];
    var newRow = [];
    for (var colNo = 0; colNo < numCols; colNo++) {
      var colTo = colNoDict[colNo];
      var level = colTo["level"];
      var colno = colTo["colno"];
      var cell = null;
      if (level == "variant") {
        cell = infomgr.datas[level][varRowNo][colno];
      } else if (level == "gene") {
        if (geneRow == undefined) {
          cell = null;
        } else {
          cell = geneRow[colno];
        }
      }
      newRow.push(cell);
    }
    infomgr.datas.variant[varRowNo] = newRow;
  }
}

var makeVariantByGene = function () {
  if (infomgr.datas.variant != undefined) {
    varByGene = {};
    var variantRows = infomgr.datas.variant;
    var hugoColNo = infomgr.getColumnNo("variant", "base__hugo");
    for (var i = 0; i < variantRows.length; i++) {
      var row = variantRows[i];
      var hugo = row[hugoColNo];
      if (varByGene[hugo] == undefined) {
        varByGene[hugo] = [];
      }
      varByGene[hugo].push(i);
    }
  }
};

function loadTableDataOnly() {
  var pageNoInput = document.getElementById("page-no-input");
  var pageNoS = pageNoInput.value;
  pageNo = parseInt(pageNoS);
  if (isNaN(pageNo)) {
    return;
  }
  var removeSpinner = function () {
    addGeneLevelToVariantLevel()
    if (spinner != null) {
      spinner.remove();
    }
    if ($grids["variant"] != undefined) {
      $grids["variant"].pqGrid("option", "dataModel", {
        data: infomgr.datas["variant"],
      });
      $grids["variant"].pqGrid("refreshDataAndView");
      updateTableFooterTotalRows("variant");
    }
    enableUpdateButton();
    unlockTabs();
    removeLoadingDiv()
  };
  var loadGeneResult = function () {
    if ($grids["gene"] == undefined) {
      infomgr.load(
        jobId,
        "gene",
        removeSpinner,
        null,
        filterJson,
        "job",
        (setResetTab = true)
      );
    } else {
      removeSpinner();
    }
  };
  var loadVariantResult = function () {
    function callLoadVariant() {
      var callback = null;
      if (usedAnnotators["gene"]) {
        callback = loadGeneResult;
      } else {
        callback = removeSpinner;
      }
      if (resultLevels.indexOf("variant") != -1) {
        infomgr.load(
          jobId,
          "variant",
          callback,
          null,
          filterJson,
          "job",
          (setResetTab = false)
        );
      } else {
        callback();
      }
    }
    callLoadVariant();
  };
  lockTabs();
  loadVariantResult();
  filterArmed = filterJson;
}

function selectTableFirstRow(tabName) {
  const $grid = $grids[tabName];
  if ($grid == undefined) {
    return;
  }
  if (
    $grid.pqGrid("selection", { type: "cell", method: "getSelection" }).length >
    0
  ) {
    return;
  }
  var stat = infomgr.getStat(tabName);
  if (stat["rowsreturned"] && stat["norows"] > 0) {
    selectedRowIds[tabName] = null;
    $grids[tabName].pqGrid("setSelection", {
      rowIndx: 0,
      colIndx: 0,
      focus: false,
    });
    selectedRowNos[tabName] = 0;
  }
}

async function loadData(alertFlag, finalcallback) {
  lockTabs();
  var infoReset = resetTab["info"];
  resetTab = { info: infoReset };
  resetTab["summary"] = true;
  resetTab["variant"] = true;
  resetTab["gene"] = true;
  infomgr.datas = {};
  var removeSpinner = async function () {
    addGeneLevelToVariantLevel();
    if (spinner != null) {
      spinner.remove();
    }
    if (alertFlag) {
      alert("Data has been loaded.");
    }
    if (finalcallback) {
      finalcallback();
    }
    if (currentTab == "info") {
      changeMenu();
    }
    try {
      populateSummaryWidgetDiv();
    } catch (e) {
      console.log(e);
      console.trace();
    }
    //if (currentTab == 'variant' || currentTab == 'gene') {
    setupTab("variant");
    //resizesTheWindow(tabName="variant")
    setupTab("gene");
    //resizesTheWindow(tabName="gene")
    //}
    enableUpdateButton();
    unlockTabs();
    removeLoadingDiv()
  };
  var loadGeneResult = async function () {
    var numvar = infomgr.getData("variant").length;
    if (document.getElementById("infonoticediv")) {
      notifyOfReadyToLoad();
    }
    if (resultLevels.indexOf("gene") != -1) {
      await infomgr.load(jobId, "gene", removeSpinner, null, filterJson, "job");
    } else {
      removeSpinner();
    }
  };
  var loadVariantResult = async function () {
    async function callLoadVariant() {
      var callback = null;
      if (usedAnnotators["gene"]) {
        callback = loadGeneResult;
      } else {
        callback = removeSpinner;
      }
      if (resultLevels.indexOf("variant") != -1) {
        await infomgr.load(jobId, "variant", callback, null, filterJson, "job");
      } else {
        await callback();
      }
    }
    if (firstLoad) {
      firstLoad = false;
      var numvar = Number(infomgr.jobinfo["Number of unique input variants"]);
      if (filterJson.length != 0) {
        infomgr.count(dbPath, "variant", function (numvar) {
          callLoadVariant();
        });
      } else {
        callLoadVariant();
      }
    } else {
      callLoadVariant();
    }
  };
  //lockTabs();
  loadVariantResult();
  filterArmed = filterJson;
}

function setFilterButtonText() {
  var tot = infomgr.jobinfo["Number of unique input variants"];
  var cur = infomgr.datas.variant.length;
  var button = document.getElementById("filterbutton");
  if (cur < tot) {
    button.textContent = "Filtered: " + cur + "/" + tot;
  } else {
    button.textContent = "Filter";
  }
}

function removeLoadingDiv() {
  if (jobDataLoadingDiv != null) {
    jobDataLoadingDiv.parentElement.removeChild(jobDataLoadingDiv);
    jobDataLoadingDiv = null;
  }
}

function lockTabs() {
  $("#tabheads div").css("pointer-events", "none").css("opacity", "0.5");
  $("#tabhead_info").css("pointer-events", "auto").css("opacity", "1");
}

function unlockTabs() {
  $("#tabheads div").css("pointer-events", "auto").css("opacity", "1");
}

function notifyToUseFilter() {
  var div = document.getElementById("infonoticediv");
  div.style.background = "red";
  div.textContent =
    `The OakVar viewer cannot display more than ${NUMVAR_LIMIT} variants. ` +
    `Use the filter tab to load at most ${NUMVAR_LIMIT} variants.`;
  showInfonoticediv();
  document.getElementById("tabhead_filter").style.pointerEvents = "auto";
}

function hideWgnoticediv() {
  var div = document.getElementById("wgnoticediv");
  div.style.display = "none";
}

function notifyOfReadyToLoad() {
  var div = document.getElementById("infonoticediv");
  div.style.background = "white";
  div.textContent = "";
  hideInfonoticediv();
}

function getViewerWidgetSettingByWidgetkey(tabName, widgetId) {
  var settings = viewerWidgetSettings[tabName];
  if (settings == undefined) {
    return null;
  }
  for (var i = 0; i < settings.length; i++) {
    if (settings[i].widgetkey == widgetId) {
      return settings[i];
    }
  }
  return null;
}

async function loadWidgets() {
  detailWidgetOrder = { variant: {}, gene: {}, info: {} };
  const response = await axios.get("/result/service/widgetlist");
  const jsonResponseData = response.data;
  widgetInfo = {};
  var widgets = jsonResponseData;
  var widgetLoadCount = 0;
  for (var i = 0; i < widgets.length; i++) {
    var widget = widgets[i];
    // removes 'wg'.
    var widgetName = widget["name"].substring(2);
    var title = widget["title"];
    var req = widget["required_annotator"];
    widgetInfo[widgetName] = widget;
    infomgr.colgroupkeytotitle[widgetName] = title;
    infomgr.widgetReq[widgetName] = req;
    $.getScript(
      "/result/widgetfile/" + "wg" + widgetName + "/wg" + widgetName + ".js",
      function () {
        writeLogDiv(widgetName + " script loaded");
        widgetLoadCount += 1;
        if (widgetLoadCount == widgets.length) {
          // processes widget default_hidden
          var widgetNames = Object.keys(widgetGenerators);
          for (var k = 0; k < widgetNames.length; k++) {
            var widgetName = widgetNames[k];
            var widgetTabs = Object.keys(widgetGenerators[widgetName]);
            if (widgetTabs.length == 1 && widgetTabs[0] == "gene") {
              widgetTabs.unshift("variant");
            }
            var req = infomgr.widgetReq[widgetName];
            var generator = widgetGenerators[widgetName];
            if (
              generator["gene"] != undefined &&
              generator["variant"] == undefined
            ) {
              generator["variant"] = generator["gene"];
            }
            for (var j = 0; j < widgetTabs.length; j++) {
              var widgetTab = widgetTabs[j];
              if (generator[widgetTab]["variables"] == undefined) {
                generator[widgetTab]["variables"] = {};
              }
              generator[widgetTab]["variables"]["widgetname"] = widgetName;
              var dh =
                widgetGenerators[widgetName][widgetTab]["default_hidden"];
              if (dh != undefined) {
                if (dh == true) {
                  dh = "none";
                } else {
                  dh = "block";
                }
                if (viewerWidgetSettings[widgetTab] == null) {
                  viewerWidgetSettings[widgetTab] = [];
                }
                var vws = getViewerWidgetSettingByWidgetkey(
                  widgetTab,
                  widgetName
                );
                if (vws == null) {
                  viewerWidgetSettings[widgetTab].push({
                    widgetkey: widgetName,
                    display: dh,
                  });
                } else {
                  if (vws["display"] == "") {
                    vws["display"] = dh;
                  }
                }
              }
              if (
                usedAnnotators[widgetTab].includes(req) &&
                generator[widgetTab] != undefined
              ) {
                var len = Object.keys(detailWidgetOrder[widgetTab]).length;
                detailWidgetOrder[widgetTab][len] = widgetName;
              }
            }
          }
          var widgetTabs = Object.keys(detailWidgetOrder);
          for (var k = 0; k < widgetTabs.length; k++) {
            var widgetTab = widgetTabs[k];
            if (showcaseWidgets[widgetTab] == undefined) {
              continue;
            }
            var poss = Object.keys(detailWidgetOrder[widgetTab]);
            for (var i1 = 0; i1 < poss.length - 1; i1++) {
              var pos1 = poss[i1];
              for (var i2 = i1 + 1; i2 < poss.length; i2++) {
                var pos2 = poss[i2];
                var widgetName1 = detailWidgetOrder[widgetTab][pos1];
                var showcaseIdx1 =
                  showcaseWidgets[widgetTab].indexOf(widgetName1);
                var widgetName2 = detailWidgetOrder[widgetTab][pos2];
                var showcaseIdx2 =
                  showcaseWidgets[widgetTab].indexOf(widgetName2);
                var changeFlag = false;
                if (showcaseIdx2 != -1) {
                  if (showcaseIdx1 != -1) {
                    if (showcaseIdx2 < showcaseIdx1) {
                      changeFlag = true;
                    }
                  } else {
                    changeFlag = true;
                  }
                }
                if (changeFlag) {
                  detailWidgetOrder[widgetTab][pos1] = widgetName2;
                  detailWidgetOrder[widgetTab][pos2] = widgetName1;
                }
              }
            }
          }
          setupTab("info");
        }
      }
    );
  }
}

async function firstLoadData() {
  var infoReset = resetTab["info"];
  resetTab = { info: infoReset };
  await loadWidgets();
  setupTab("job");
  setupTab("info");
  setupTab("report")
  await loadFilterSettings(quickSaveName, true);
  await loadLayoutSetting(quickSaveName, true);
  infomgr.load(
    jobId,
    "info",
    async function () {
      populateInfoDiv(document.getElementById("info_div"));
      await checkWidgets();
      loadData(false, showTab("info"));
    },
    null,
    filterJson,
    "info"
  );
  setupTab("filter");
}

async function checkWidgets() {
  const response = await axios.get("/result/service/getnowgannotmodules", {
    params: { username: username, job_id: jobId, dbpath: dbPath },
  });
  const jsonResponseData = response.data;
  var noWgAnnotModules = jsonResponseData;
  //populateWgNoticeDiv(noWgAnnotModules);
}

function drawingRetrievingDataDiv(currentTab) {
  if (jobDataLoadingDiv == null) {
    var currentTabDiv = document.getElementById("tab_" + currentTab);
    var loadingDiv = getEl("div");
    loadingDiv.className = "data-retrieving-msg-div";
    var loadingTxtDiv = getEl("div");
    //loadingTxtDiv.className = "store-noconnect-msg-div spinner";
    loadingTxtDiv.className = "spinner";
    var div = getEl("div")
    div.className = "rect1"
    addEl(loadingTxtDiv, div)
    var div = getEl("div")
    div.className = "rect2"
    addEl(loadingTxtDiv, div)
    var div = getEl("div")
    div.className = "rect3"
    addEl(loadingTxtDiv, div)
    var div = getEl("div")
    div.className = "rect4"
    addEl(loadingTxtDiv, div)
    var div = getEl("div")
    div.className = "rect5"
    addEl(loadingTxtDiv, div)
    //var span = getEl("span");
    //span.textContent = "Retrieving Data...";
    //addEl(loadingTxtDiv, span);
    //addEl(loadingTxtDiv, getEl("br"));
    //var loadingSpinCircleDiv = getEl("div");
    //var loadingSpinCircleImg = getEl("img");
    //loadingSpinCircleImg.src = "images/bigSpinner.gif";
    //addEl(loadingTxtDiv, loadingSpinCircleImg);
    addEl(loadingDiv, loadingTxtDiv);
    var dW = document.body.offsetWidth;
    var dH = document.body.offsetHeight;
    loadingDiv.style.top = 0;
    loadingDiv.style.left = 0;
    jobDataLoadingDiv = loadingDiv;
    var parentDiv = document.body;
    addEl(parentDiv, loadingDiv);
  }
  return loadingDiv;
}

function drawingWidgetCaptureSpinnerDiv() {
  var currentTabDiv = document.getElementById("tab_" + currentTab);
  var loadingDiv = getEl("div");
  loadingDiv.className = "data-retrieving-msg-div";
  var loadingTxtDiv = getEl("div");
  loadingTxtDiv.className = "store-noconnect-msg-div";
  var span = getEl("span");
  span.textContent = "Capturing widget content...";
  addEl(loadingTxtDiv, span);
  addEl(loadingTxtDiv, getEl("br"));
  var loadingSpinCircleDiv = getEl("div");
  var loadingSpinCircleImg = getEl("img");
  loadingSpinCircleImg.src = "images/bigSpinner.gif";
  addEl(loadingTxtDiv, loadingSpinCircleImg);
  addEl(loadingDiv, loadingTxtDiv);
  var dW = document.body.offsetWidth;
  var dH = document.body.offsetHeight;
  loadingDiv.style.top = 0;
  loadingDiv.style.left = 0;
  jobDataLoadingDiv = loadingDiv;
  var parentDiv = document.body;
  addEl(parentDiv, loadingDiv);
  return loadingDiv;
}

function writeLogDiv(msg) {
  /*var div = document.getElementById('log_div');
	div.textContent = ' ' + msg + ' ';
	$(div).stop(true, true).css({backgroundColor: "#ff0000"}).animate({backgroundColor: "#ffffff"}, 1000);*/
}

function turnOffMenu(elemId) {
  document.getElementById(elemId).style.display = "none";
}

function turnOnMenu(elemId) {
  document.getElementById(elemId).style.display = "block";
}

function turnOffLayoutMenu() {
  var submenu = document.querySelector("#menu_div .menu1 .menu2_container");
  submenu.classList.add("hide");
  submenu.classList.remove("show-block");
}

function onClickMenu1(menu) {
  var submenus = menu.getElementsByClassName("menu2_container");
  for (var i = 0; i < submenus.length; i++) {
    var submenu = submenus[i];
    if (submenu.classList.contains("show-block")) {
      submenu.classList.add("hide");
      submenu.classList.remove("show-block");
    } else {
      submenu.classList.remove("hide");
      submenu.classList.add("show-block");
      hideAllMenu3()
    }
  }
}

function onClickColumnsMenu(evt) {
  hideAllMenu3();
  var div = document.getElementById("columns_showhide_select_div");
  div.classList.add("on")
  evt.stopPropagation();
  menu3Pinned = true
}

function onClickWidgetsMenu(evt) {
  hideAllMenu3();
  var div = document.getElementById("widgets_showhide_select_div");
  div.classList.add("on")
  evt.stopPropagation();
  menu3Pinned = true
}

function doNothing() {
  alert("saved");
}

function quicksave() {
  filterJson = filterArmed;
  saveLayoutSetting(quickSaveName, "quicksave");
}

async function getVariantCols() {
  /*$('#tabheads .tabhead').click(function(event) {
        var targetTab = "#" + this.id.replace('head', '');
        var tabName = targetTab.split('_')[1];
        currentTab = tabName;
        showTab(tabName);
        var tab = document.getElementById('tab_' + tabName);
        var detailContainer = document.getElementById('detailcontainerdiv_' + tabName);
        if (resetTab[tabName] == true || tab.innerHTML == '' || (detailContainer != null && detailContainer.innerHTML == '')) {
            setupTab(tabName);
            resizesTheWindow();
        }
        if (tabName == 'variant' || tabName == 'gene' || tabName == 'info') {
            $(detailContainer).packery();
        }
        changeMenu();
    });*/
  const response = await axios.get("/result/service/variantcols", {
    params: {
      job_id: jobId,
      username: username,
      dbpath: dbPath,
      confpath: confPath,
      filter: JSON.stringify(filterJson),
    },
  });
  const jsonResponseData = response.data;
  filterCols = jsonResponseData["columns"]["variant"];
  usedAnnotators = {};
  var cols = jsonResponseData["columns"]["variant"];
  usedAnnotators["variant"] = [];
  usedAnnotators["info"] = [];
  for (var i = 0; i < cols.length; i++) {
    var col = cols[i];
    var annotator = col.colModel[0].colgroupkey;
    usedAnnotators["variant"].push(annotator);
    usedAnnotators["info"].push(annotator);
  }
  if (jsonResponseData["columns"]["gene"]) {
    var cols = jsonResponseData["columns"]["gene"];
    usedAnnotators["gene"] = [];
    for (var i = 0; i < cols.length; i++) {
      var col = cols[i];
      var annotator = col.colModel[0].colgroupkey;
      usedAnnotators["gene"].push(annotator);
      usedAnnotators["info"].push(annotator);
    }
  }
}

function selectTab(tabName) {
  document.querySelector("#tabhead_" + tabName).click();
}

async function getVariantDbCols() {
  const response = await axios.get("/result/service/variantdbcols", {
    params: { job_id: jobId, username: username, dbpath: dbPath },
  });
  variantdbcols = response.data;
}

async function startData() {
  checkConnection();
  getVariantDbCols();
  await getResultLevels();
  //addTabHeadsAndTabContentDivs()
  //lockTabs()
  currentTab = "info";
  jobDataLoadingDiv = drawingRetrievingDataDiv(currentTab);
  await getVariantCols();
  firstLoadData();
}

function changeTab(tabName) {
  currentTab = tabName;
  for (var i = 0; i < tabNames.length; i++) {
    const divTab = document.getElementById("tab_" + tabNames[i]);
    const divHead = document.getElementById("tabhead_" + tabNames[i]);
    if (tabNames[i] == tabName) {
      divTab.classList.add("show");
      divHead.classList.add("selected");
    } else {
      divTab.classList.remove("show");
      divHead.classList.remove("selected");
    }
  }
  if (tabName == "variant" || tabName == "gene") {
    $grids[tabName].pqGrid("refresh");
  }
  if (tabName == "info") {
    $(document.getElementById("detailcontainerdiv_info")).packery();
  }
  changeMenu();
  setTableDetailLayout(tabName);
  selectTableFirstRow(tabName);
}

function webresult_run() {
  var urlParams = new URLSearchParams(window.location.search);
  username = urlParams.get("username");
  jobId = urlParams.get("job_id");
  dbPath = urlParams.get("dbpath");
  confPath = urlParams.get("confpath");
  if (urlParams.get("separatesample") == "true") {
    separateSample = true;
  } else {
    separateSample = false;
  }
  $grids = {};
  gridObjs = {};
  if (jobId != null) {
    document.title = "OakVar: " + jobId;
  } else if (dbPath != null) {
    var toks = dbPath.split("/");
    document.title = "OakVar: " + toks[toks.length - 1];
  }
  var resizeTimeout = null;
  $(window).resize(function (event) {
    shouldResizeScreen = {};
    var curWinWidth = window.innerWidth;
    var curWinHeight = window.innerHeight;
    if (curWinWidth != windowWidth || curWinHeight != windowHeight) {
      windowWidth = curWinWidth;
      windowHeight = curWinHeight;
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(function () {
        resizesTheWindow();
      }, 200);
    }
  });
  // Chrome won't let you directly set this as window.onbeforeunload = function(){}
  // it wont work on a refresh then.
  function triggerAutosave() {
    if (autoSaveLayout) {
      filterJson = filterArmed;
      saveLayoutSetting(quickSaveName);
      saveFilterSetting(quickSaveName, true);
    }
  }
  //window.onbeforeunload = triggerAutosave;
  document.addEventListener("click", function (evt) {
    var target = evt.target;
    var tableHeaderContextmenuId = "table-header-contextmenu-" + currentTab;
    if (target.closest(tableHeaderContextmenuId) == null) {
      var div = document.getElementById(tableHeaderContextmenuId);
      if (div != null) {
        div.style.display = "none";
      }
    }
    if (target.closest("#menu_div") == null) {
      turnOffLayoutMenu();
    }
  });
  startData();
}
