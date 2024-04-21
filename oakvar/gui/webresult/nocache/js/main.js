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
  var colGroupTitles = [];
  var colGroupNumCols = {};
  for (var colGroupNo = 0; colGroupNo < colGroups.length; colGroupNo++) {
    var colGroup = colGroups[colGroupNo];
    var cols = colGroup.colModel;
    var colExist = false;
    var numCols = 0;
    for (var j = 0; j < cols.length; j++) {
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

function afterDragNSBar(_, _) {
}

function resizesTheWindow(tabName = currentTab) {
  setTableDetailLayout(tabName);
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
    params: { uid: uid, username: username, dbpath: dbPath },
  });
  var data = response.data
  var levels = data.levels;
  //pageSize = parseInt(data["gui_result_pagesize"]);
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

function disableUpdateButton() {
  var btn = document.getElementById("load_button");
  btn.disabled = true;
}

function enableUpdateButton() {
  var btn = document.getElementById("load_button");
  if (btn) {
    btn.disabled = false;
  }
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
  infomgr.geneRows = geneRows;
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

function updateTableDataOnly () {
  addGeneLevelToVariantLevel();
  if ($grids[currentTab] != undefined) {
    $grids[currentTab].pqGrid("option", "dataModel", {
      data: infomgr.datas[currentTab],
    });
    $grids[currentTab].pqGrid("refreshDataAndView");
    updateTableFooterTotalRows(currentTab);
  }
};

async function loadGeneResultTableDataOnly () {
  if (! usedAnnotators["gene"]) {
    return
  }
  await infomgr.load_job(uid, "gene", (setResetTab = false))
}

function loadTableDataOnly() {
  var pageNoInput = document.getElementById("page-no-input_" + currentTab);
  var pageNoS = pageNoInput.value;
  pageNos[currentTab] = parseInt(pageNoS);
  if (isNaN(pageNos[currentTab])) {
    return;
  }
  enableLoadingDiv()
  infomgr.load_job(uid, currentTab, (setResetTab = false)).then(function() {
    updateTableDataOnly()
    removeLoadingDiv()
    filterArmed = filterJson;
  })
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

async function loadData() {
  //lockTabs();
  resetTab = { info: true }
  resetTab["variant"] = true
  resetTab["gene"] = true
  infomgr.datas = {};
  var removeSpinner = async function () {
    addGeneLevelToVariantLevel();
    if (spinner != null) {
      spinner.remove();
    }
    if (currentTab == "info") {
      changeMenu();
    }
    setupTab("variant");
    setupTab("gene");
    setupTab("info")
    enableUpdateButton();
    removeLoadingDiv()
  };
  var loadGeneResult = async function () {
    if (document.getElementById("infonoticediv")) {
      notifyOfReadyToLoad();
    }
    if (resultLevels.indexOf("gene") != -1) {
      var ret = await infomgr.load_job(uid, "gene")
      if (ret == false) {
        removeLoadingDiv()
        return
      }
      await removeSpinner()
    } else {
      await removeSpinner();
    }
  };
  async function loadVariantResult() {
    async function callLoadVariant() {
      var callback = null;
      if (usedAnnotators["gene"]) {
        callback = loadGeneResult;
      } else {
        callback = removeSpinner;
      }
      if (resultLevels.indexOf("variant") != -1) {
        ret = await infomgr.load_job(uid, "variant")
        if (ret == false) {
          removeLoadingDiv()
          return
        }
        await callback()
      } else {
        await callback();
      }
    }
    if (firstLoad) {
      firstLoad = false;
      if (filterJson.length != 0) {
        infomgr.count(dbPath, "variant", async function (_) {
          await callLoadVariant();
        });
      } else {
        await callLoadVariant();
      }
    } else {
      await callLoadVariant();
    }
  };
  try {
    await loadVariantResult();
  } catch (error) {
    console.error(error);
  }
  filterArmed = filterJson;
}

function setFilterButtonText() {
  var tot = infomgr.get_total_num_variants();
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
    jobDataLoadingDiv.remove()
    jobDataLoadingDiv = null
  }
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
    $.getScript("/result/widgetfile/" + "wg" + widgetName + "/wg" + widgetName + ".js",
        function (_, _, _) {
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
            //setupTab("info");
          }
        }
    );
  }
}

async function loadJobInfo() {
  await infomgr.load(
    uid,
    "info",
    null,
    null,
    filterJson,
    "info"
  );
}

async function firstLoadData() {
  //disableAllTabheads()
  var infoReset = resetTab["info"];
  resetTab = { info: infoReset };
  setupTab("job");
  setupTab("report")
  setupTab("filter");
  var t1 = loadWidgets();
  var t2 = loadFilterSettings(quickSaveName, true);
  var t3 = loadLayoutSetting(quickSaveName, true);
  Promise.all([t1, t2, t3]).then(async function() {
    await infomgr.load_info(uid, "info")
    populateInfoDiv(document.getElementById("info_div"));
    await loadData()
  })
}

async function checkWidgets() {
  /*const response = await axios.get("/result/service/getnowgannotmodules", {
    params: { username: username, uid: uid, dbpath: dbPath },
  });*/
}

function drawingRetrievingDataDiv(_) {
  if (jobDataLoadingDiv == null) {
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
    loadingDiv.style.top = 0;
    loadingDiv.style.left = 0;
    jobDataLoadingDiv = loadingDiv;
    var parentDiv = document.body;
    addEl(parentDiv, loadingDiv);
  }
  return loadingDiv;
}

function drawingWidgetCaptureSpinnerDiv() {
  var loadingDiv = getEl("div");
  loadingDiv.className = "data-retrieving-msg-div";
  var loadingTxtDiv = getEl("div");
  loadingTxtDiv.className = "store-noconnect-msg-div";
  var span = getEl("span");
  span.textContent = "Capturing widget content...";
  addEl(loadingTxtDiv, span);
  addEl(loadingTxtDiv, getEl("br"));
  var loadingSpinCircleImg = getEl("img");
  loadingSpinCircleImg.src = "images/bigSpinner.gif";
  addEl(loadingTxtDiv, loadingSpinCircleImg);
  addEl(loadingDiv, loadingTxtDiv);
  loadingDiv.style.top = 0;
  loadingDiv.style.left = 0;
  jobDataLoadingDiv = loadingDiv;
  var parentDiv = document.body;
  addEl(parentDiv, loadingDiv);
  return loadingDiv;
}

function writeLogDiv(_) {
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
  const response = await axios.get("/result/service/variantcols", {
    params: {
      uid: uid,
      username: username,
      dbpath: dbPath,
      confpath: confPath,
      filter: JSON.stringify(filterJson),
      add_summary: false,
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
    params: { uid: uid, username: username, dbpath: dbPath },
  });
  variantdbcols = response.data;
}

async function getSummaryVarLimit() {
  var response = await axios.get("/result/service/summaryvarlimit")
  summaryVarLimit = response.data["num_var_limit"]
}

async function startData() {
  //checkConnection();
  var t1 = getPageSize()
  var t2 = getVariantDbCols();
  var t3 = getResultLevels();
  var t4 = getVariantCols();
  var t5 = getSummaryVarLimit()
  Promise.all([t1, t2, t3, t4, t5]).then(async function() {
    await firstLoadData();
  })
}

function getDetailcontainerdiv(tabName) {
  return document.querySelector("#detailcontainerdiv_" + tabName)
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
    var div = getDetailcontainerdiv(tabName)
    if (div.children.length == 0) {
      populateSummaryWidgetDiv()
    }
  }
  changeMenu();
  setTableDetailLayout(tabName);
  selectTableFirstRow(tabName);
}

function parseUrl() {
  var urlParams = new URLSearchParams(window.location.search);
  username = urlParams.get("username");
  if (!username) {
    username = "default"
  }
  uid = urlParams.get("uid");
  jobId = uid;
  dbPath = urlParams.get("dbpath");
  confPath = urlParams.get("confpath");
  if (urlParams.get("separatesample") == "true") {
    separateSample = true;
  } else {
    separateSample = false;
  }
}

function setTitle() {
  if (uid != null) {
    document.title = "OakVar: " + uid;
  } else if (dbPath != null) {
    var toks = dbPath.split("/");
    document.title = "OakVar: " + toks[toks.length - 1];
  }
}

function setupResizeHandler() {
  var resizeTimeout = null;
  $(window).resize(function (_) {
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
}

function triggerAutosave() {
  if (autoSaveLayout) {
    filterJson = filterArmed;
    saveLayoutSetting(quickSaveName);
    saveFilterSetting(quickSaveName, true);
  }
}

function setupAutosave() {
  //window.onbeforeunload = triggerAutosave;
}

function setupClickHandler() {
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
}

async function getPageSize() {
  const res = await axios.get("/result/service/pagesize")
  const data = res.data
  if (data) {
    pageSize = data["gui_result_pagesize"]
  }
}

function enableLoadingDiv() {
  jobDataLoadingDiv = drawingRetrievingDataDiv(currentTab);
}

async function webresult_run() {
  currentTab = "info";
  enableLoadingDiv()
  parseUrl()
  setTitle()
  setupResizeHandler()
  //setupAutosave()
  setupClickHandler()
  startData().then((_) => {
  })
}
