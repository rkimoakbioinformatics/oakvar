function showVariantDetail(row, tabName) {
  if (row == undefined) {
    return;
  }
  var detailDiv = getDetailDiv(tabName)
  if (!detailDiv) {
    return;
  }
  var outerDiv = getWidgetDiv(tabName)
  // Remembers widget layout.
  var widgetDivs = outerDiv.children;
  var reuseWidgets = true;
  if (widgetDivs.length == 0) {
    reuseWidgets = false;
  } else {
    widgetDivs = masons[tabName].getItemElements() //$(outerDiv).packery("getItemElements");
  }
  if (reuseWidgets == true) {
    detailWidgetOrder[tabName] = {};
    for (var i = 0; i < widgetDivs.length; i++) {
      var widgetDiv = widgetDivs[i];
      var widgetKey = widgetDiv.getAttribute("widgetkey");
      detailWidgetOrder[tabName][i] = widgetKey;
      widgetGenerators[widgetKey]["width"] = widgetDiv.clientWidth - 10;
      widgetGenerators[widgetKey]["height"] = widgetDiv.clientHeight - 10;
      widgetGenerators[widgetKey]["top"] = widgetDiv.style.top;
      widgetGenerators[widgetKey]["left"] = widgetDiv.style.left;
    }
  }
  if (tabName == "error") {
    return;
  }
  var orderNums = Object.keys(detailWidgetOrder[tabName]);
  for (var i = 0; i < orderNums.length; i++) {
    var colGroupKey = detailWidgetOrder[tabName][orderNums[i]];
    try {
      if (widgetGenerators[colGroupKey] == undefined) {
        continue;
      }
      var colGroupTitle = infomgr.colgroupkeytotitle[colGroupKey];
      if (colGroupTitle == undefined) {
        colGroupTitle = widgetGenerators[colGroupKey]["name"];
      }
      if (
        widgetGenerators[colGroupKey][tabName] != undefined &&
        widgetGenerators[colGroupKey][tabName]["function"] != undefined
      ) {
        var generator = widgetGenerators[colGroupKey][tabName];
        var widgetDiv = null;
        var shouldDraw = false;
        if (generator["shoulddraw"] != undefined) {
          shouldDraw = generator["shoulddraw"]();
        } else {
          shouldDraw = true;
        }
        if (reuseWidgets) {
          widgetContentDiv = document.getElementById(
            "widgetcontentdiv_" + colGroupKey + "_" + tabName
          );
          if (generator["donterase"] != true) {
            $(widgetContentDiv).empty();
          }
          if (shouldDraw) {
            generator["function"](widgetContentDiv, row, tabName);
          }
        } else {
          [widgetDiv, widgetContentDiv] = getDetailWidgetDivs(
            tabName,
            colGroupKey,
            colGroupTitle
          );
          generator["variables"]["parentdiv"] = widgetContentDiv;
          if (generator["init"] != undefined) {
            generator["init"]();
          }
          widgetDiv.style.width = generator["width"] + "px";
          widgetDiv.style.height = generator["height"] + "px";
          addEl(outerDiv, widgetDiv);
          if (shouldDraw) {
            generator["function"](widgetContentDiv, row, tabName);
          }
          var setting = getViewerWidgetSettingByWidgetkey(tabName, colGroupKey);
          if (setting != null) {
            var display = setting["display"];
            if (display != undefined) {
              widgetDiv.style.display = display;
            }
          }
        }
      }
    } catch (err) {
      console.log(err);
      console.log(
        "### exception while drawing widget [" +
          colGroupKey +
          "] continuing to the next widget ###"
      );
    }
  }
  if (reuseWidgets == false) {
    packWidgets(tabName)
  }
  for (var i = 0; i < orderNums.length; i++) {
    var colGroupKey = detailWidgetOrder[tabName][orderNums[i]];
    if (widgetGenerators[colGroupKey] == undefined) {
      continue;
    }
    var widgetDiv = document.getElementById(
      "detailwidget_" + tabName + "_" + colGroupKey
    );
    var display = widgetDiv.style.display;
    if (widgetGenerators[colGroupKey][tabName] != undefined) {
      var generator = widgetGenerators[colGroupKey][tabName];
      if (generator["showhide"] != undefined) {
        var state = generator["showhide"]();
        var widgetContainerDiv = document.getElementById(
          "widgetcontentdiv_" + colGroupKey + "_" + tabName
        );
        if (state == false) {
          var span = getEl("span");
          addEl(span, getTn("No data"));
          addEl(widgetContainerDiv, span);
        } else if (state == true) {
        }
      }
    }
  }
}

function onLayoutComplete() {
  if (viewerWidgetSettings[currentTab] == undefined) {
    return;
  }
  for (var i = 0; i < viewerWidgetSettings[currentTab].length; i++) {
    var setting = viewerWidgetSettings[currentTab][i];
    var el = document.getElementById(setting.id);
    if (el) {
      el.style.top = setting.top;
      el.style.left = setting.left;
      el.style.width = setting.width;
      el.style.height = setting.height;
      el.style.display = setting.display;
      viewerWidgetSettings[currentTab].splice(i, 1);
      i--;
    }
  }
}
