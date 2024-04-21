class InfoMgr {
  constructor() {
    this.datas = {};
    this.columnnoss = {};
    this.columnss = {};
    this.colModels = {};
    this.columngroupss = {};
    this.columngroupkeys = {};
    this.colgroupkeytotitle = {};
    this.colgrouptitletokey = {};
    this.stats = {};
    this.statuss = {};
    this.jobinfo = {};
    this.widgetReq = {};
    this.colgroupdefaulthiddenexist = {};
    this.modulesInfo = {};
    this.totalNoRows = null;
    this.ftable_uid = null
  }

  getStatus(uid) {
    this.uid = uid;
  }

  async count(dbPath, tabName, callback) {
    const data = {
      username: username,
      uid: uid,
      tab: tabName,
      dbpath: dbPath,
      filter: JSON.stringify(filterJson),
    };
    const response = await axios({
      method: "post",
      url: "/result/service/count",
      headers: {
        "Content-type": "application/json",
      },
      data: data,
    });
    const jsonResponseData = response.data;
    var msg = jsonResponseData["n"] + " variants meet the criteria";
    callback(msg, jsonResponseData);
  }

  getInputPageSize() {
    var input = document.getElementById("page-input");
    var inputPageSize = null
    if (input != null) {
      inputPageSize = input.value;
      inputPageSize = parseInt(inputPageSize);
    }
    if (inputPageSize == null || isNaN(inputPageSize) || inputPageSize < 0) {
      inputPageSize = pageSize
    }
    return inputPageSize
  }

  isValidInputPageSize(inputPageSize) {
    return ! (inputPageSize == null || isNaN(inputPageSize) || inputPageSize <= 0)
  }

  setPageSize(inputPageSize) {
    pageSize = inputPageSize
  }

  async load_job(uid, tabName, setResetTab = true) {
    if (filterJson == []) {
      filterJson = {};
    }
    var inputPageSize = this.getInputPageSize()
    if (this.isValidInputPageSize(inputPageSize)) {
      this.setPageSize(inputPageSize)
    }
    if (!this.isValidInputPageSize(pageSize)) {
      return
    }
    var errHappened = false
    var response = await axios({
      method: "post",
      url: "/result/service/result",
      headers: {
        "Content-type": "application/json",
      },
      data: {
        username: username,
        uid: uid,
        tab: tabName,
        dbpath: dbPath,
        confpath: confPath,
        filter: JSON.stringify(filterJson),
        separatesample: separateSample,
        page: pageNos[tabName],
        pagesize: pageSize,
        makefilteredtable: setResetTab,
        no_summary: false,
      },
    }).catch(function(err) {
      alert(err.response.data.msg)
      removeLoadingDiv()
      errHappened = true
    })
    if (errHappened) {
      return false
    }
    const jsonResponseData = response.data;
    this.store(
      tabName,
      jsonResponseData,
      (setResetTab = setResetTab)
    );
    if (tabName == "variant") {
      var loaded = jsonResponseData["total_norows"];
      var total = this.get_total_num_variants();
      var vCountLoad = document.getElementById("filter-count-display");
      if (vCountLoad) {
        vCountLoad.innerText = loaded.toLocaleString() + "/" + total.toLocaleString() + " variants"
      }
    }
    return true
  }

  get_total_num_variants() {
    var total = parseInt(infomgr.jobinfo["num_variants"]);
    if (!total) {
      total = parseInt(infomgr.jobinfo["Number of unique input variants"]);
    }
    return total;
  }

  async load_info(_) {
    const response = await axios.get("/result/service/status", {
      params: { uid: uid, dbpath: dbPath },
    });
    this.jobinfo = response.data;
    if (this.jobinfo["dbpath"] && !dbPath) {
      dbPath = this.jobinfo["dbpath"];
    }
    if (this.jobinfo["uid"] && uid) {
      uid = this.jobinfo["job_id"];
    }
  }

  async load(_, tabName, fetchtype) {
    if (fetchtype == "single") {
      var response = await axios.get("/submit/annotate", {
        params: { mutation: onemut, dbcolumn: true },
      });
      const jsonResponseData = response.data;
      this.datas[tabName] = [jsonResponseData];
      this.jobinfo = {};
      this.jobinfo["inputcoordinate"] = "genomic";
      if (callback != null) {
        callback(callbackArgs);
      }
    }
  }

  store(
    tabName,
    jsonResponseData,
    setResetTab = true
  ) {
    if (setResetTab) {
      resetTab[tabName] = true;
    }
    if (tabName == "variant") {
      this.totalNoRows = jsonResponseData["total_norows"];
    }
    this.datas[tabName] = jsonResponseData["data"];
    this.colModels[tabName] = jsonResponseData["columns"];
    this.stats[tabName] = jsonResponseData["stat"];
    this.statuss[tabName] = jsonResponseData["status"];
    this.modulesInfo[tabName] = jsonResponseData["modules_info"];
    this.ftable_uid = jsonResponseData["ftable_uid"]
    var colModel = this.colModels[tabName];
    var columnnos = {};
    var columngroups = {};
    var columns = [];
    this.colgroupdefaulthiddenexist[tabName] = {};
    for (var i = 0; i < colModel.length; i++) {
      var colsInGroup = colModel[i]["colModel"];
      var defaultHiddenInGroup = false;
      for (var j = 0; j < colsInGroup.length; j++) {
        var column = colsInGroup[j];
        if (column.default_hidden == true) {
          defaultHiddenInGroup = true;
        }
        columns.push(column);
        column["sortType"] = function (row1, row2, dataIndx) {
          var val1 = row1[dataIndx];
          var val2 = row2[dataIndx];
          var decision = -1;
          if (val1 == null) {
            if (val2 == null) {
              decision = 0;
            } else {
              if (ascendingSort[dataIndx]) {
                decision = 1;
              } else {
                decision = -1;
              }
            }
          } else {
            if (val2 == null) {
              if (ascendingSort[dataIndx]) {
                decision = -1;
              } else {
                decision = 1;
              }
            } else if (val1 < val2) {
              decision = -1;
            } else if (val1 > val2) {
              decision = 1;
            } else if (val1 == val2) {
              decision = 0;
            }
          }
          return decision;
        };
        column["render"] = function (ui) {
          var val = ui.rowData[ui.dataIndx];
          var content;
          if (ui.column.type === "float") {
            if (val == null) {
              val = "";
              content = "";
            } else if (val === 0) {
              content = "0";
            } else if (Math.abs(val) > 1e4 || Math.abs(val) < 1e-4) {
              content = val.toExponential(3);
            } else {
              let rnd = Math.round((val + Number.EPSILON) * 1e4) / 1e4;
              content = rnd.toString();
            }
          } else {
            if (val == null) {
              val = "";
            }
            content = "" + val;
          }
          content = content.replace(/>/g, "&gt;");
          var title = content;
          if (ui.column.link_format !== null) {
            var linkFormat = ui.column.link_format;
            var linkRe = /\$\{[^{]*\}/g;
            var linkMatch = linkFormat.match(linkRe);
            var valSegment = "";
            var linkUrl = "";
            var linkText = "";
            if (linkMatch !== null) {
              var reString = linkMatch[0].substring(2, linkMatch[0].length - 1);
              var valRe = new RegExp(reString);
              var valMatch = String(val).match(valRe);
              if (valMatch !== null && valMatch[0] !== "") {
                if (valMatch.length === 1) {
                  valSegment = valMatch[0];
                } else {
                  valSegment = "";
                  for (var i = 1; i < valMatch.length; i++) {
                    valSegment += valMatch[i];
                  }
                }
                var linkUrl = linkFormat.replace(linkRe, valSegment);
                var linkText = val;
              }
            }
            content = `<a href="${linkUrl}" target="_blank">${linkText}</a>`;
            title = linkUrl;
          } else if (content.startsWith("http")) {
            content = `<a href="${content}" target="_blank">View</a>`;
          }
          return `<span title="${title}">${content}</span>`;
        };
        var filter = column["filter"];
        if (filter != undefined && filter["type"] == "select") {
          var colType = column["type"];
          var colCtg = column["ctg"];
          if (colType == "string" && colCtg == "single") {
            column["filter"]["condition"] = function (val, select) {
              if (select == "" || select == null) {
                return true;
              }
              var selects = JSON.parse(select);
              if (Array.isArray(selects) && selects.length == 0) {
                return true;
              }
              if (selects.indexOf(val) >= 0) {
                return true;
              } else {
                return false;
              }
            };
          } else if (colType == "string" && colCtg == "multi") {
            column["filter"]["condition"] = function (val, selects) {
              if (selects == null) {
                return true;
              }
              var selects = JSON.parse(selects);
              if (Array.isArray(selects) && selects.length == 0) {
                return true;
              }
              for (var i = 0; i < selects.length; i++) {
                var select = selects[i];
                if (val.indexOf(select) >= 0) {
                  return true;
                }
              }
              return false;
            };
          }
          if (column["categories"].length > 3) {
            column["filter"]["init"] = function () {
              $(this).pqSelect({
                checkbox: true,
                displayText: "&#x25BC;",
                singlePlaceholder: "&#x25BD;",
                multiplePlaceholder: "&#x25BD;",
                radio: true,
                maxDisplay: 0,
                search: false,
                selectallText: "Select all",
                width: "90%",
              });
              this[0].nextSibling.classList.add("ui-state-hover");
            };
          } else {
            column["filter"]["init"] = function () {
              $(this).pqSelect({
                checkbox: true,
                displayText: "&#x25BC;",
                singlePlaceholder: "&#x25BD;",
                multiplePlaceholder: "&#x25BD;",
                radio: true,
                maxDisplay: 0,
                search: false,
                selectallText: "",
                width: "90%",
              });
              this[0].nextSibling.classList.add("ui-state-hover");
            };
          }
        }
        var columnKey = column["col"];
        var columnNo = column["dataIndx"];
        columnnos[columnKey] = columnNo;
        var columnGroup = column["colgroup"];
        var columnGroupKey = column["colgroupkey"];
        if (columngroups[columnGroupKey] == undefined) {
          columngroups[columnGroupKey] = [];
        }
        columngroups[columnGroupKey].push(columnKey);
        this.columngroupkeys[columnGroupKey] = columnGroupKey;
        this.colgroupkeytotitle[columnGroupKey] = columnGroup;
        this.colgrouptitletokey[columnGroup] = columnGroupKey;
      }
      colModel[i].default_hidden_exist = defaultHiddenInGroup;
      this.colgroupdefaulthiddenexist[tabName][colModel[i].name] =
        defaultHiddenInGroup;
    }
    this.columnss[tabName] = columns;
    this.columnnoss[tabName] = columnnos;
    this.columngroupss[tabName] = columngroups;
  }

  getData(tabName) {
    return this.datas[tabName];
  }

  getColumns(tabName) {
    return this.columnss[tabName];
  }

  getColModel(tabName) {
    return this.colModels[tabName];
  }

  getColumnGroups(tabName) {
    return this.columngroupss[tabName];
  }

  getColumnByName(tabName, columnName) {
    return this.columnss[tabName][this.columnnoss[tabName][columnName]];
  }

  getColumnNos(tabName) {
    if (Object.keys(this.columnnoss).length == 0) {
      return undefined;
    } else {
      return this.columnnoss[tabName];
    }
  }

  getColumnNo(tabName, col) {
    if (Object.keys(this.columnnoss).length == 0) {
      return undefined;
    } else {
      return this.columnnoss[tabName][col];
    }
  }

  getStat(tabName) {
    return this.stats[tabName];
  }

  getJobInfo(_tabName) {
    return this.jobinfo;
  }

  getRowValue(tabName, row, col) {
    var val = null;
    if (Object.keys(this.columnnoss).length > 0) {
      val = row[this.columnnoss[tabName][col]];
    } else {
      val = row[col];
    }
    return val;
  }

  getGeneRowValue(_hugo) {
    var val = null;
    if (Object.keys(this.columnnoss).length > 0) {
      val = row[this.columnnoss[tabName][col]];
    } else {
      val = row[col];
    }
    return val;
  }

  getVariantColumnGroupByName(groupName) {
    var colGroups = this.colModels.variant;
    for (var i = 0; i < colGroups.length; i++) {
      var cg = colGroups[i];
      if (cg.title == groupName) {
        return cg;
      }
    }
    return null;
  }

  updateVariantCell(tabName, row, colName, value) {
    var rowKey = row[0];
    for (var i = 0; i < this.datas[tabName].length; i++) {
      var row = this.datas[tabName][i];
      if (row[0] == rowKey) {
        row[this.columnnoss[tabName][colName]] = value;
        break;
      }
    }
  }
}
