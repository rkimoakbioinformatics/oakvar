function getEl(tag) {
  var div = document.createElement(tag);
  return div;
}

function getTn(text) {
  return document.createTextNode(text);
}

function addEl(parent, child) {
  parent.appendChild(child);
  return parent;
}

function getTrimmedTn(text) {
  var textLengthCutoff = 10;
  var span = getEl("span");
  var tn = getTn(text);
  if (text.length > textLengthCutoff) {
    span.title = text;
    text = text.substring(0, textLengthCutoff) + "...";
    tn.textContent = text;
  }
  addEl(span, tn);
  return span;
}

function getExclamationTd(flag) {
  var td = document.createElement("td");
  td.style.width = 50;
  if (flag == true) {
    var img = new Image();
    img.src = "/result/images/exclamation.png";
    img.width = 14;
    img.height = 14;
    td.appendChild(img);
  }
  return td;
}

function getTextTd(text) {
  var td = document.createElement("td");
  td.style.width = 150;
  td.appendChild(document.createTextNode(text));
  return td;
}

//Function to convert seconds to HH:MM:SS
function toHHMMSS(sec_num) {
  var hours = Math.floor(sec_num / 3600);
  var minutes = Math.floor((sec_num - hours * 3600) / 60);
  var seconds = sec_num - hours * 3600 - minutes * 60;

  if (hours < 10) {
    hours = "0" + hours;
  }
  if (minutes < 10) {
    minutes = "0" + minutes;
  }
  if (seconds < 10) {
    seconds = "0" + seconds;
  }

  return hours + ":" + minutes + ":" + seconds;
}

function addSpinner(parentDiv, scaleFactor, minDim, spinnerDivId) {
  var parentRect = parentDiv.getBoundingClientRect();
  var scaleDim = Math.floor(
    scaleFactor * Math.min(parentRect.width, parentRect.height)
  );
  var spinnerDim = Math.max(scaleDim, minDim);
  var spinnerDiv = getEl("div");
  spinnerDiv.id = spinnerDivId;
  spinnerDiv.style.position = "absolute";
  spinnerDiv.style.textAlign = "center";
  var spinnerImg = getEl("img");
  spinnerImg.src = "/result/images/bigSpinner.gif";
  spinnerImg.style.width = spinnerDim + "px";
  spinnerImg.style.height = spinnerDim + "px";
  addEl(spinnerDiv, spinnerImg);
  addEl(parentDiv, spinnerDiv);
  var spinnerRect = spinnerDiv.getBoundingClientRect();

  spinnerDiv.style.top =
    parentRect.top + parentRect.height / 2 - spinnerRect.height / 2;
  spinnerDiv.style.left =
    parentRect.left + parentRect.width / 2 - spinnerRect.width / 2;
  return spinnerDiv;
}

function addSpinnerById(parentDivId, scaleFactor, minDim, spinnerDivId) {
  var parentDiv = document.getElementById(parentDivId);
  var spinnerDiv = addSpinner(parentDiv, scaleFactor, minDim, spinnerDivId);
  return spinnerDiv;
}

function saveFilterSetting(name, useFilterJson) {
  return new Promise((resolve, _) => {
    var saveData = {};
    if (useFilterJson == undefined) {
      makeFilterJson();
    }
    saveData["filterSet"] = filterJson;
    var saveDataStr = JSON.stringify(saveData);
    $.ajax({
      type: "GET",
      async: true,
      url: "/result/service/savefiltersetting",
      data: {
        username: username,
        uid: uid,
        dbpath: dbPath,
        name: name,
        savedata: saveDataStr,
      },
      success: function (_) {
        writeLogDiv("Filter setting has been saved.");
        resolve();
        lastUsedFilterName = name;
      },
    });
  });
}

function deleteFilterSetting(name) {
  return new Promise((resolve, _) => {
    $.get("/result/service/deletefiltersetting", {
      username: username,
      uid: uid,
      dbpath: dbPath,
      name: name,
    }).done(function (response) {
      if (response == "deleted") {
        writeLogDiv("Filter setting has been deleted.");
      } else {
        alert(response);
      }
      resolve();
    });
  });
}

async function saveLayoutSettingAs(evt) {
  //toggleSubmenu("save_layout_div", evt)
  evt.stopPropagation()
  hideAllMenu3()
  var res = await axios.get("/result/service/getlayoutsavenames", {
    params: { uid: uid, dbpath: dbPath },
  });
  var response = res.data
  var quickSaveNameIdx = response.indexOf(quickSaveName);
  if (quickSaveNameIdx >= 0) {
    response.splice(quickSaveNameIdx, 1);
  }
  var names = response.join(", ");
  var msg = "Please enter layout name to save.";
  if (names != "") {
    msg = msg + " Saved layout names are: " + names;
  }
  if (lastUsedLayoutName == quickSaveName) {
    lastUsedLayoutName = "";
  }
  var name = prompt(msg, lastUsedLayoutName);
  if (name != null) {
    await saveLayoutSetting(name)
  }
}

function saveFilterSettingAs() {
  return new Promise((resolve, _) => {
    $.get("/result/service/getfiltersavenames", {
      username: username,
      uid: uid,
      dbpath: dbPath,
    }).done(function (response) {
      var quickSaveNameIdx = response.indexOf(quickSaveName);
      if (quickSaveNameIdx >= 0) {
        response.splice(quickSaveNameIdx, 1);
      }
      var names = response.join("\n");
      var msg = "Enter filter name.";
      if (names != "") {
        msg = msg + "\nSaved names are:\n" + names;
      }
      if (lastUsedLayoutName == quickSaveName) {
        lastUsedLayoutName = "";
      }
      var name = prompt(msg, lastUsedLayoutName);
      if (name != null) {
        saveFilterSetting(name).then((_) => {
          resolve();
        });
      }
    });
  });
}

function saveWidgetSetting(name) {
  var saveData = {};
  saveData["widgetSettings"] = {};
  var widgets = {};
  var detailContainerDiv = document.getElementById(
    "detailcontainerdiv_variant"
  );
  if (detailContainerDiv != null) {
    saveData["widgetSettings"]["variant"] = [];
    widgets = $(detailContainerDiv).packery("getItemElements");
    for (var i = 0; i < widgets.length; i++) {
      var widget = widgets[i];
      saveData["widgetSettings"]["variant"].push({
        id: widget.id,
        widgetkey: widget.getAttribute("widgetkey"),
        top: widget.style.top,
        left: widget.style.left,
        width: widget.style.width,
        height: widget.style.height,
      });
    }
  }
  var detailContainerDiv = document.getElementById("detailcontainerdiv_gene");
  if (detailContainerDiv != null) {
    saveData["widgetSettings"]["gene"] = [];
    widgets = $(detailContainerDiv).packery("getItemElements");
    for (var i = 0; i < widgets.length; i++) {
      var widget = widgets[i];
      saveData["widgetSettings"]["gene"].push({
        id: widget.id,
        widgetkey: widget.getAttribute("widgetkey"),
        top: widget.style.top,
        left: widget.style.left,
        width: widget.style.width,
        height: widget.style.height,
      });
    }
  }
  var detailContainerDiv = document.getElementById("detailcontainerdiv_info");
  if (detailContainerDiv != null) {
    saveData["widgetSettings"]["info"] = [];
    widgets = $(detailContainerDiv).packery("getItemElements");
    for (var i = 0; i < widgets.length; i++) {
      var widget = widgets[i];
      saveData["widgetSettings"]["info"].push({
        id: widget.id,
        widgetkey: widget.getAttribute("widgetkey"),
        top: widget.style.top,
        left: widget.style.left,
        width: widget.style.width,
        height: widget.style.height,
      });
    }
  }
  var saveDataStr = JSON.stringify(saveData);
  $.ajax({
    url: "/result/service/savewidgetsetting",
    type: "get",
    async: true,
    data: {
      username: username,
      uid: uid,
      dbpath: dbPath,
      name: name,
      savedata: saveDataStr,
    },
    success: function (_) {
      writeLogDiv("Widget setting has been saved.");
    },
  });
}

async function saveLayoutSetting(name, nextAction) {
  var saveData = {};
  // Table layout
  saveData["tableSettings"] = {};
  if ($grids["variant"] != undefined) {
    var colGroupModel = $grids["variant"].pqGrid("option", "colModel");
    var data = [];
    for (var i = 0; i < colGroupModel.length; i++) {
      var colGroup = colGroupModel[i];
      var group = {};
      group = { title: colGroup.title, cols: [] };
      var cols = colGroup.colModel;
      for (var j = 0; j < cols.length; j++) {
        var col = cols[j];
        group.cols.push({
          col: col.col,
          dataIndx: col.dataIndx,
          width: col.width,
          hidden: col.hidden,
        });
      }
      data.push(group);
    }
    saveData["tableSettings"]["variant"] = data;
  }
  if ($grids["gene"] != undefined) {
    var colGroupModel = $grids["gene"].pqGrid("option", "colModel");
    var data = [];
    for (var i = 0; i < colGroupModel.length; i++) {
      var colGroup = colGroupModel[i];
      var group = {};
      group = { title: colGroup.title, cols: [] };
      var cols = colGroup.colModel;
      for (var j = 0; j < cols.length; j++) {
        var col = cols[j];
        group.cols.push({
          col: col.col,
          dataIndx: col.dataIndx,
          width: col.width,
          hidden: col.hidden,
        });
      }
      data.push(group);
    }
    saveData["tableSettings"]["gene"] = data;
  }
  // Widget layout
  saveData["widgetSettings"] = {};
  var widgets = {};
  var detailContainerDiv = document.getElementById(
    "detailcontainerdiv_variant"
  );
  if (detailContainerDiv != null) {
    saveData["widgetSettings"]["variant"] = [];
    if (masons["variant"] != undefined) {
      widgets = masons["variant"].getItemElements();
    }
    for (var i = 0; i < widgets.length; i++) {
      var widget = widgets[i];
      var pinButtonClassList = widget.getElementsByClassName(
        "detailwidget-pinbutton"
      )[0].classList;
      var pinned = null;
      if (pinButtonClassList.contains("pinned") == true) {
        pinned = "pinned";
      } else {
        pinned = "unpinned";
      }
      saveData["widgetSettings"]["variant"].push({
        id: widget.id,
        widgetkey: widget.getAttribute("widgetkey"),
        top: widget.style.top,
        left: widget.style.left,
        width: widget.style.width,
        height: widget.style.height,
        display: widget.style.display,
        pinned: pinned,
      });
    }
  }
  var detailContainerDiv = document.getElementById("detailcontainerdiv_gene");
  if (detailContainerDiv != null) {
    saveData["widgetSettings"]["gene"] = [];
    if (masons["gene"] != undefined) {
      widgets = masons["gene"].getItemElements();
    }
    for (var i = 0; i < widgets.length; i++) {
      var widget = widgets[i];
      var pinButtonClassList = widget.getElementsByClassName(
        "detailwidget-pinbutton"
      )[0].classList;
      var pinned = null;
      if (pinButtonClassList.contains("pinned") == true) {
        pinned = "pinned";
      } else {
        pinned = "unpinned";
      }
      saveData["widgetSettings"]["gene"].push({
        id: widget.id,
        widgetkey: widget.getAttribute("widgetkey"),
        top: widget.style.top,
        left: widget.style.left,
        width: widget.style.width,
        height: widget.style.height,
        display: widget.style.display,
        pinned: pinned,
      });
    }
  }
  var detailContainerDiv = document.getElementById("detailcontainerdiv_info");
  if (detailContainerDiv != null) {
    saveData["widgetSettings"]["info"] = [];
    if (masons["info"] != undefined) {
      widgets = masons["info"].getItemElements();
    }
    for (var i = 0; i < widgets.length; i++) {
      var widget = widgets[i];
      var pinButtonClassList = widget.getElementsByClassName(
        "detailwidget-pinbutton"
      )[0].classList;
      var pinned = null;
      if (pinButtonClassList.contains("pinned") == true) {
        pinned = "pinned";
      } else {
        pinned = "unpinned";
      }
      saveData["widgetSettings"]["info"].push({
        id: widget.id,
        widgetkey: widget.getAttribute("widgetkey"),
        top: widget.style.top,
        left: widget.style.left,
        width: widget.style.width,
        height: widget.style.height,
        display: widget.style.display,
        pinned: pinned,
      });
    }
  }
  // Heights
  saveData["height"] = {};
  var tabs = ["variant", "gene"];
  for (var i = 0; i < tabs.length; i++) {
    var tab = tabs[i];
    var h = null;
    var div = document.getElementById("tablediv_" + tab);
    if (div) {
      h = div.style.height;
      saveData["height"]["table_" + tab] = h;
    }
    div = document.getElementById("detaildiv_" + tab);
    if (div) {
      h = div.style.height;
      saveData["height"]["detail_" + tab] = h;
    }
    div = document.getElementById("cellvaluediv_" + tab);
    if (div) {
      h = div.style.height;
      saveData["height"]["cellvalue_" + tab] = h;
    }
  }
  // tableDetailDivSizes
  saveData["tabledetaildivsizes"] = tableDetailDivSizes;
  // Saves.
  var saveDataStr = JSON.stringify(saveData);
  var res = await axios.post("/result/service/savelayoutsetting", {
    username: username,
    uid: uid,
    dbpath: dbPath,
    name: name,
    savedata: saveDataStr,
  });
  _ = res;
  lastUsedLayoutName = name;
  writeLogDiv("Layout setting has been saved.");
  if (nextAction == "quicksave") {
    saveFilterSetting(name, true);
  }
}

function areSameFilters(filter1, filter2) {
  var sameFilter = true;
  for (var i = 0; i < filter1.length; i++) {
    var el1 = filter1[i];
    var sameEl = false;
    for (var j = 0; j < filter2.length; j++) {
      var el2 = filter2[j];
      if (
        el1[0].col == el2[0].col &&
        el1[1] == el2[1] &&
        el1[2] == el2[2] &&
        el1[3] == el2[3]
      ) {
        sameEl = true;
        break;
      }
    }
    if (sameEl == false) {
      sameFilter = false;
      break;
    }
  }
  for (var i = 0; i < filter2.length; i++) {
    var el1 = filter2[i];
    var sameEl = false;
    for (var j = 0; j < filter1.length; j++) {
      var el2 = filter1[j];
      if (
        el1[0].col == el2[0].col &&
        el1[1] == el2[1] &&
        el1[2] == el2[2] &&
        el1[3] == el2[3]
      ) {
        sameEl = true;
        break;
      }
    }
    if (sameEl == false) {
      sameFilter = false;
      break;
    }
  }
  return sameFilter;
}

function applyWidgetSetting(level) {
  var settings = viewerWidgetSettings[level];
  if (settings == undefined) {
    return;
  }
  var outerDiv = document.getElementById("detailcontainerdiv_" + level);
  if (outerDiv == null) {
    return;
  }
  var widgets = outerDiv.children;
  if (widgets.length > 0) {
    var items = Packery.data(outerDiv).items;
    var widgetCount = 0;
    for (var i = 0; i < settings.length; i++) {
      var setting = settings[i];
      for (var j = 0; j < items.length; j++) {
        var item = items[j];
        if (item.element.getAttribute("widgetkey") == setting.widgetkey) {
          item.element.style.top = setting["top"];
          item.element.style.left = setting["left"];
          item.element.style.width = setting["width"];
          item.element.style.height = setting["height"];
          item.element.style.display = setting["display"];
          if (setting["pinned"] == "pinned") {
            $(
              item.element.getElementsByClassName("detailwidget-pinbutton")[0]
            ).click();
          }
          var tmp = items[widgetCount];
          items[widgetCount] = item;
          items[j] = tmp;
          widgetCount++;
          break;
        }
      }
    }
    $(outerDiv).packery();
  }
}

function applyTableSetting(level) {
  var settings = tableSettings[level];
  if (settings == undefined) {
    return;
  }
  var $grid = $grids[level];
  var colGroups = $grid.pqGrid("option", "colModel");
  var newColModel = [];
  for (var i = 0; i < settings.length; i++) {
    var colGroupSetting = settings[i];
    var colGroupColsSetting = colGroupSetting.cols;
    for (var j = 0; j < colGroups.length; j++) {
      var colGroup = colGroups[j];
      if (colGroup.title == colGroupSetting.title) {
        newColModel.push(colGroup);
        var newColGroupColModel = [];
        var cols = colGroup.colModel;
        for (k = 0; k < colGroupColsSetting.length; k++) {
          var colSetting = colGroupColsSetting[k];
          for (l = 0; l < cols.length; l++) {
            var col = cols[l];
            if (col.col == colSetting.col) {
              col.width = colSetting.width;
              col.hidden = colSetting.hidden;
              newColGroupColModel.push(col);
              break;
            }
          }
        }
        newColModel[i].colModel = newColGroupColModel;
      }
    }
  }
  $grid.pqGrid("option", "colModel", newColModel);
  $grid.pqGrid("refresh");
}

function loadFilterSettingAs() {
  $.get("/result/service/getfiltersavenames", {
    username: username,
    uid: uid,
    dbpath: dbPath,
  }).done(function (response) {
    var quickSaveNameIdx = response.indexOf(quickSaveName);
    if (quickSaveNameIdx >= 0) {
      response.splice(quickSaveNameIdx, 1);
    }
    //var savedNames = JSON.parse(response.replace(/'/g, '"'));
    var div = document.getElementById("load_filter_select_div");
    $(div).empty();
    div.style.display = "block";
    for (var i = 0; i < response.length; i++) {
      var name = response[i];
      var a = getEl("a");
      a.style.cursor = "pointer";
      a.style.fontSize = "13px";
      a.style.fontWeight = "normal";
      a.style.width = "100%";
      a.style.backgroundColor = "rgb(232, 232, 232)";
      addEl(a, getTn(name));
      a.addEventListener("mouseover", function (evt) {
        evt.target.style.backgroundColor = "yellow";
      });
      a.addEventListener("mouseleave", function (evt) {
        evt.target.style.backgroundColor = "white";
      });
      a.addEventListener("click", function (evt) {
        loadFilterSetting(evt.target.textContent, null, false);
        div.style.display = "none";
      });
      addEl(div, a);
      addEl(div, getEl("br"));
    }
  });
}

async function loadSamples() {
  response = await axios.get("/result/service/samples", {
    params: { username: username, uid: uid, dbpath: dbPath },
  }); //.done(response=>{
  response = response.data;
  allSamples = response;
}

async function loadSmartFilters() {
  var response = await axios.get("/result/service/smartfilters", {
    params: { username: username, uid: uid, dbpath: dbPath },
  }); //.done(function (response) {
  response = response.data;
  smartFilters = {};
  for (let source in response) {
    let sfs = response[source];
    let refac = { order: [], definitions: {} };
    for (let i = 0; i < sfs.length; i++) {
      let sf = sfs[i];
      sf.allowPartial = sf.allowPartial !== undefined ? sf.allowPartial : false;
      let reducedFilter = reduceSf(sf.filter, sf.allowPartial);
      if (reducedFilter !== null) {
        sf.filter = reducedFilter;
        refac.order.push(sf.name);
        refac.definitions[sf.name] = sf;
      }
    }
    if (refac.order.length > 0) {
      smartFilters[source] = refac;
    }
  }
}

async function loadFilterSetting() {
  response = await axios.get("/result/service/loadfiltersetting", {
    params: { username: username, uid: uid, dbpath: dbPath, name: name },
  })
  response = response.data;
  writeLogDiv("Filter setting loaded");
  var data = response;
  filterJson = data["filterSet"];
}

async function loadFilterSettings(name, doNotCount) {
  lastUsedFilterName = name;
  showFilterTabContent = true;
  //await loadSmartFilters();
  await loadSamples();
  await loadFilterSetting();
  if (!doNotCount) {
    infomgr.count(dbPath, "variant", updateLoadMsgDiv);
  }
}

function importFilterFromFile() {
  var sdiv = getEl("button");
  sdiv.style.position = "fixed";
  sdiv.style.bottom = "0px";
  sdiv.style.right = "0px";
  sdiv.textContent = "Import filter...";
  sdiv.addEventListener("click", function (_) {
    var input = getEl("input");
    input.type = "file";
    input.addEventListener("change", function (e) {
      var file = e.target.files[0];
      var reader = new FileReader();
      reader.readAsText(file, "utf-8");
      reader.addEventListener("load", function (e) {
        var fs = JSON.parse(e.target.result);
        filterMgr.updateAll(fs);
      });
    });
    input.click();
  });
  addEl(document.body, sdiv);
}

function showImportFilterDialog() {
  var content = getEl("div");
  var span = getEl("span");
  span.textContent = "Filter file to import:\xa0";
  addEl(content, span);
  var input = getEl("input");
  input.type = "file";
  addEl(content, input);
  var div = document.getElementById("yesnodialog");
  if (div != undefined) {
    $(div).remove();
  }
  var div = getEl("div");
  div.id = "yesnodialog";
  if (typeof content === "string") {
    content = getTn(content);
  }
  content.id = "yesnodialog-contentdiv";
  addEl(div, content);
  addEl(div, getEl("br"));
  var btnDiv = getEl("div");
  btnDiv.className = "buttondiv";
  var btn = getEl("button");
  btn.textContent = "Cancel";
  btn.addEventListener("click", function (_) {
    $("#yesnodialog").remove();
  });
  addEl(btnDiv, btn);
  addEl(div, btnDiv);
  addEl(document.body, div);
}

function getSavedFilter(name) {
  return new Promise((resolve, _) => {
    $.get("/result/service/loadfiltersetting", {
      username: username,
      uid: uid,
      dbpath: dbPath,
      name: name,
    }).done(function (response) {
      resolve(response);
    });
  });
}

function hideAllMenu3() {
  var menu3s = document
    .getElementById("menu_div")
    .getElementsByClassName("menu3");
  for (var i = 0; i < menu3s.length; i++) {
    menu3s[i].classList.remove("on");
  }
}

function toggleSubmenu(divId, evt) {
  if (evt != null) {
    evt.stopPropagation()
  }
  var div = document.getElementById(divId)
  div.textContent = ""
  if (div.classList.contains("on")) {
    div.classList.remove("on");
    return;
  }
  hideAllMenu3()
  div.classList.add("on")
}

async function loadLayoutSettingAs(evt) {
  var divId = "load_layout_select_div"
  toggleSubmenu(divId, evt)
  var div = document.getElementById(divId)
  var res = await axios.get("/result/service/getlayoutsavenames", {
    params: {
      username: username,
      uid: uid,
      dbpath: dbPath,
    },
  });
  var response = res.data;
  div.textContent = ""
  if (response.length == 0) {
    var a = getEl("a");
    a.className = "pl-4"
    a.textContent = "(no\xa0saved\xa0layout)";
    addEl(div, a);
  } else {
    var quickSaveNameIdx = response.indexOf(quickSaveName);
    if (quickSaveNameIdx >= 0) {
      response.splice(quickSaveNameIdx, 1);
    }
    var savedLayoutNames = response;
    for (var i = 0; i < savedLayoutNames.length; i++) {
      var name = savedLayoutNames[i];
      var a = getEl("a");
      a.className = "pl-4"
      a.textContent = name;
      a.addEventListener("click", function (evt) {
        loadLayoutSetting(evt.target.textContent);
      });
      addEl(div, a);
    }
  }
}

async function loadLayoutSetting(name) {
  var response = await axios.get("/result/service/loadlayoutsetting", {
    params: { username: username, uid: uid, dbpath: dbPath, name: name },
  });
  var data = response.data;
  loadedTableSettings = data["tableSettings"];
  if (loadedTableSettings == undefined) {
    loadedTableSettings = {};
  }
  tableSettings = loadedTableSettings;
  if (
    (currentTab == "variant" || currentTab == "gene") &&
    tableSettings[currentTab] != undefined
  ) {
    applyTableSetting(currentTab);
  }
  loadedViewerWidgetSettings = data["widgetSettings"];
  if (loadedViewerWidgetSettings == undefined) {
    loadedViewerWidgetSettings = {};
  }
  var loadedViewerWidgetSettingsKeys = Object.keys(loadedViewerWidgetSettings);
  for (var i = 0; i < loadedViewerWidgetSettingsKeys.length; i++) {
    var k = loadedViewerWidgetSettingsKeys[i];
    viewerWidgetSettings[k] = loadedViewerWidgetSettings[k];
  }
  if (
    (currentTab == "variant" || currentTab == "gene" || currentTab == "info") &&
    viewerWidgetSettings[currentTab] != undefined
  ) {
    applyWidgetSetting(currentTab);
  }
  loadedHeightSettings = data["height"];
  if (loadedHeightSettings == undefined) {
    loadedHeightSettings = {};
  }
  var v = data["tabledetaildivsizes"];
  if (v != undefined) {
    tableDetailDivSizes = v;
  }
  lastUsedLayoutName = name;
  writeLogDiv("Layout setting loaded");
  setTimeout(function() {
    for (var i=0; i<tabNames.length; i++) {
      const tabName = tabNames[i]
      if (masons[tabName] != undefined) {
        masons[tabName].layout()
      }
    }
  }, 200)
}

async function deleteLayoutSettingAs(evt) {
  var divId = "delete_layout_select_div"
  toggleSubmenu(divId, evt)
  var div = document.getElementById(divId)
  var res = await axios.get("/result/service/getlayoutsavenames", {
    params: {username: username,
      uid: uid,
      dbpath: dbPath,
  }})
  var response = res.data
  div.textContent = ""
  if (response.length == 0) {
    var a = getEl("a");
    a.textContent = "(no\xa0saved\xa0layout)";
    addEl(div, a);
  } else {
    savedLayoutNames = response;
    for (var i = 0; i < savedLayoutNames.length; i++) {
      var name = savedLayoutNames[i];
      var a = getEl("a");
      a.textContent = name;
      a.setAttribute("module", name);
      a.addEventListener("click", function (evt) {
        var name = evt.target.getAttribute("module");
        var yes = confirm("Delete " + name + "?");
        if (yes) {
          deleteLayoutSetting(evt.target.textContent, null);
        }
      });
      addEl(div, a);
    }
  }
}

async function deleteLayoutSetting(name, _) {
  await axios.get("/result/service/deletelayoutsetting", {
    params: {username: username,
      uid: uid,
      dbpath: dbPath,
      name: name,
  }})
  writeLogDiv("Layout setting deleted");
  deleteLayoutSettingAs(null);
}

async function renameLayoutSettingAs(evt) {
  var divId = "rename_layout_select_div"
  toggleSubmenu(divId, evt)
  var div = document.getElementById(divId)
  var res = await axios.get("/result/service/getlayoutsavenames", {
    params: {username: username,
      uid: uid,
      dbpath: dbPath,
  }})
  var response = res.data
  div.textContent = ""
  if (response.length == 0) {
    var a = getEl("a");
    a.textContent = "(no\xa0saved\xa0layout)";
    addEl(div, a);
  } else {
    var quickSaveNameIdx = response.indexOf(quickSaveName);
    if (quickSaveNameIdx >= 0) {
      response.splice(quickSaveNameIdx, 1);
    }
    savedLayoutNames = response;
    for (var i = 0; i < savedLayoutNames.length; i++) {
      var name = savedLayoutNames[i];
      var a = getEl("a");
      a.textContent = name;
      a.addEventListener("click", function (evt) {
        renameLayoutSetting(evt.target.textContent, null);
      });
      addEl(div, a);
    }
  }
}

function renameLayoutSetting(name, _) {
  var msg = "Please enter a new name for layout " + name + ".";
  var newName = prompt(msg, lastUsedLayoutName);
  if (newName != null) {
    $.get("/result/service/renamelayoutsetting", {
      username: username,
      uid: uid,
      dbpath: dbPath,
      name: name,
      newname: newName,
    }).done(function (_) {
      writeLogDiv("Layout name has been changed.");
    });
  }
}

function toggleAutoLayoutSave() {
  var a = document.getElementById("layout_autosave_title");
  if (autoSaveLayout == false) {
    autoSaveLayout = true;
    a.text = "V Autosave";
    writeLogDiv("Layout autosave enabled");
  } else {
    autoSaveLayout = false;
    a.text = "Autosave";
    writeLogDiv("Layout autosave disabled");
  }
}

function setServerStatus(connected) {
  var loadingDiv = document.getElementById("connection-lost-div");
  if (!connected) {
    if (loadingDiv === null) {
      var loadingDiv = getEl("div");
      loadingDiv.id = "connection-lost-div";
      loadingDiv.className = "data-retrieving-msg-div";
      var loadingTxtDiv = getEl("div");
      loadingTxtDiv.className = "store-noconnect-msg-div";
      var span = getEl("span");
      span.textContent = "Lost connection to server";
      addEl(loadingTxtDiv, span);
      addEl(loadingTxtDiv, getEl("br"));
      addEl(loadingTxtDiv, getEl("br"));
      var span = getEl("span");
      span.textContent = "Please launch OakVar again.";
      addEl(loadingTxtDiv, span);
      addEl(loadingDiv, loadingTxtDiv);
      jobDataLoadingDiv = loadingDiv;
      var parentDiv = document.body;
      addEl(parentDiv, loadingDiv);
    }
  } else {
    if (loadingDiv !== null) {
      loadingDiv.parentNode.removeChild(loadingDiv);
    }
  }
}

function checkConnection(failures) {
  failures = failures !== undefined ? failures : 0;
  var host = window.location.host;
  if (failures >= 3) {
    setServerStatus(false);
  }
  var wsprotocol = null;
  var protocol = window.location.protocol;
  if (protocol == "http:") {
    wsprotocol = "ws:";
  } else if (protocol == "https:") {
    wsprotocol = "wss:";
  }
  ws = new WebSocket(wsprotocol + "//" + host + "/heartbeat");
  ws.onopen = function (_) {
    setServerStatus(true);
    failures = 0;
  };
  ws.onclose = function (_) {
    failures += 1;
    var waitTime = 2000 * failures;
    setTimeout(function () {
      checkConnection(failures);
    }, waitTime);
  };
}
