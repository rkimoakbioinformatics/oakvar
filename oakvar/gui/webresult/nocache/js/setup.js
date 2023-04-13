function getRightDiv(tabName) {
  return document.getElementById("rightdiv_" + tabName);
}

function setupTab(tabName) {
  if (resetTab[tabName] == false) {
    return;
  }
  var tabDiv = document.getElementById("tab_" + tabName);
  var rightDiv = getRightDiv(tabName);
  if (!rightDiv) {
    var rightDiv = getEl("div");
    rightDiv.id = "rightdiv_" + tabName;
    rightDiv.className = "rightdiv";
    addEl(tabDiv, rightDiv);
    if (tabName == "job") {
      makeJobTab(rightDiv);
      resetTab[tabName] = false;
    } else if (tabName == "info") {
      makeInfoTab(rightDiv);
      resetTab[tabName] = false;
    } else if (tabName == "variant" || tabName == "gene") {
      makeVariantGeneTab(tabName, rightDiv);
      resetTab[tabName] = false;
    } else if (tabName == "sample" || tabName == "mapping") {
      makeSampleMappingTab(tabName, rightDiv);
      resetTab[tabName] = false;
    } else if (tabName == "filter") {
      resetTab[tabName] = !makeFilterTab(rightDiv);
    } else if (tabName == "report") {
      makeReportTab(rightDiv)
      resetTab[tabName] = false;
    }
  }
  if (tabName == "variant" || tabName == "gene") {
    var columns = infomgr.getColumns(tabName);
    var data = infomgr.getData(tabName);
    makeGrid(columns, data, tabName);
    $grids[tabName].pqGrid("refreshDataAndView");
  }
  if (
    loadedTableSettings != undefined &&
    loadedTableSettings[currentTab] != undefined
  ) {
    applyTableSetting(currentTab);
  }
  if (
    loadedViewerWidgetSettings != undefined &&
    loadedViewerWidgetSettings[currentTab] != undefined
  ) {
    applyWidgetSetting(currentTab);
  }
  if (
    (currentTab == "variant" || currentTab == "gene") &&
    tableDetailDivSizes[currentTab] != undefined
  ) {
    applyTableDetailDivSizes();
  }
  changeMenu();
  setTableDetailLayout(tabName);
  //enableTabhead(tabName)
}

function filterHeaderClick(_) {
  $(this).toggleClass("inactive");
}

class FilterManager {
  constructor() {
    this.sampleContId = "filter-cont-sample";
    this.geneContId = "filter-cont-gene";
    this.variantContId = "filter-cont-variant";

    this.sampleControlClass = "sample-control";
    this.sampleFilterId = "sample-select-filt";
    this.sampleFileId = "sample-list-file";
    this.sampleFileDisplayId = "sample-list-file-display";
    this.sampleFileClearId = "sample-list-file-clear";
    this.sampleSelectId = "sample-select-cont";
    this.sampleReqCountId = "sample-req-count";
    this.sampleRejCountId = "sample-rej-count";
    this.sampleInFilterCountId = "sample-infiliter-count";
    this.sampleRuleClass = "filter-sample-hasrule-span";
    this.sampleShownCount = "sample-shown-count";
    this.sampleInteractedSpan = "sample-interacted-cont";
    this.geneTextId = "gene-list-text";
    this.geneFileId = "gene-list-file";
    this.vpropSelectId = "vprop-sel";
    this.vpropSfId = "vprop-sf";
    this.vpropQbId = "vprop-qb";
    this.qbRootId = "qb-root";
    this.qbBannedColumns = ["base__samples"];
    this.allSamples = [];
    this.requireSamples = new Set();
    this.rejectSamples = new Set();
  }

  getFilterSection(headerTitle, active) {
    active = active === undefined ? false : active;

    let rootDiv = $(getEl("div")).addClass("filter-section");
    let header = $(getEl("div"))
      .addClass("filter-header")
      .click(this.sectionHeaderClick);
    if (!active) {
      header.addClass("inactive");
    }
    rootDiv.append(header);
    header.append($(getEl("span")).addClass("filter-header-arrow"));
    header.append(
      $(getEl("span")).addClass("filter-header-text").text(headerTitle)
    );
    let filterBody = $(getEl("div")).addClass("filter-body");
    rootDiv.append(filterBody);
    let filterContent = $(getEl("div")).addClass("filter-content");
    filterBody.append(filterContent);
    let filterControls = $(getEl("div")).addClass("filter-controls");
    filterBody.append(filterControls);
    filterControls.append(
      $(getEl("button"))
        .addClass("filter-section-clear")
        .addClass("butn")
        .text("Clear")
        .click(this.sectionClearClick.bind(this))
    );
    // Apply button
    var filterApply = getEl("button");
    filterApply.id = "load_button";
    filterApply.classList.add("butn");
    filterApply.style.marginLeft = "0.25rem";
    addEl(filterApply, getTn("Apply"));
    filterApply.addEventListener("click", function (_) {
      makeFilterJson();
      drawingRetrievingDataDiv("filter");
      loadData()
      loadLayoutSetting(quickSaveName, null);
    });
    filterControls.append(filterApply);

    return rootDiv;
  }

  sectionHeaderClick(_) {
    $(this).toggleClass("inactive");
  }

  sectionClearClick(event) {
    let elem = $(event.target);
    let contentId = $(elem).parent().siblings(".filter-content").attr("id");
    if (contentId === this.sampleContId) {
      this.updateSampleSelect();
    } else if (contentId === this.geneContId) {
      this.updateGeneSelect();
    } else if (contentId === this.variantContId) {
      this.updateVpropUI();
    }
    event.stopPropagation();
  }

  addSampleSelect(outerDiv, filter) {
    filter = new CravatFilter(filter);
    this.requireSamples.clear();
    this.rejectSamples.clear();
    filter.sample.require.forEach(this.requireSamples.add, this.requireSamples);
    filter.sample.reject.forEach(this.rejectSamples.add, this.rejectSamples);
    this.allSamples = allSamples;

    outerDiv.attr("id", this.sampleContId);

    const controlsL1 = $(getEl("div")).addClass(this.sampleControlClass);
    outerDiv.append(controlsL1);

    // Show all

    controlsL1.append(
      $(getEl("button"))
        .click(() => {
          this.drawSamples(this.allSamples);
        })
        .text(`Show all`)
        .addClass("butn")
    );

    // Filter down the show samples
    controlsL1.append(
      $(getEl("input"))
        .attr("id", this.sampleFilterId)
        .attr("placeholder", "Search samples")
        .on("input", (event) => {
          const q = event.target.value;
          if (q) {
            this.drawSamples(this.matchingSamples(q));
          } else {
            this.drawSamples(this.allSamples);
          }
        })
    );

    // File filter
    controlsL1.append(
      $(getEl("input"))
        .attr("id", this.sampleFileId)
        .attr("type", "file")
        .on("input", this.sampleListFile.bind(this))
        .css("display", "none")
    );
    controlsL1.append(
      $(getEl("button"))
        .text("Upload")
        .addClass("butn")
        .attr("title", "Upload a list of sample IDs. One per line.")
        .click(() => {
          const fileInput = $("#" + this.sampleFileId);
          fileInput.val(null);
          $("#" + this.sampleFileId).click();
        })
    );
    controlsL1.append(
      $(getEl("span"))
        .attr("id", this.sampleFileDisplayId)
        .click((_) => {
          $("#" + this.sampleFileId).trigger("input");
        })
    );
    controlsL1.append(
      $(getEl("button"))
        .attr("id", this.sampleFileClearId)
        .text("X")
        .click(() => {
          $("#" + this.sampleFileId)
            .val(null)
            .trigger("input");
        })
        .addClass("butn")
    );

    // Show in filter
    const interactedSpan = $(getEl("span")).addClass(this.sampleInteractedSpan);
    controlsL1.append(interactedSpan);
    interactedSpan.append(
      $(getEl("span"))
        .attr("id", this.sampleInFilterCountId)
        .addClass(this.sampleRuleClass)
        .text("In filter: 0")
        .click(() => {
          this.drawSamples(
            [...this.requireSamples].concat([...this.rejectSamples])
          );
        })
    );
    interactedSpan.append(
      $(getEl("span"))
        .attr("id", this.sampleReqCountId)
        .addClass(this.sampleRuleClass)
        .text("Include: 0")
        .click(() => {
          this.drawSamples([...this.requireSamples]);
        })
    );
    interactedSpan.append(
      $(getEl("span"))
        .attr("id", this.sampleRejCountId)
        .addClass(this.sampleRuleClass)
        .text("Exclude: 0")
        .click(() => {
          this.drawSamples([...this.rejectSamples]);
        })
    );

    // Clear selection
    controlsL1.append(
      $(getEl("button"))
        .addClass("butn")
        .click((_) => {
          this.sampleSelectionClear();
          this.drawSamples();
        })
        .text("Clear")
    );

    const controlsL2 = $(getEl("div")).addClass(this.sampleControlClass);
    outerDiv.append(controlsL2);

    const allChange = (event) => {
      const target = $(event.target);
      if (target.prop("checked")) {
        this.samplePickShown(target.val());
      }
    };
    const reqRejClick = (event) => {
      const rd = $(event.target).prev("input:radio");
      let toClick;
      if (rd.prop("checked")) {
        toClick = $('input[name="sample-sel-all"][value="neutral"]');
      } else {
        toClick = rd;
      }
      toClick.prop("checked", true).trigger("change");
    };
    controlsL2.append(
      $(getEl("input"))
        .attr("type", "radio")
        .attr("name", "sample-sel-all")
        .val("neutral")
        .change(allChange)
        .attr("hidden", true)
    );
    controlsL2.append(
      $(getEl("input"))
        .attr("type", "radio")
        .attr("name", "sample-sel-all")
        .val("require")
        .change(allChange)
        .attr("hidden", true)
    );
    controlsL2.append(
      $(getEl("span"))
        .addClass("sample-rd")
        .addClass("sample-rd-req")
        .click(reqRejClick)
    );
    controlsL2.append(
      $(getEl("input"))
        .attr("type", "radio")
        .attr("name", "sample-sel-all")
        .val("reject")
        .change(allChange)
        .attr("hidden", true)
    );
    controlsL2.append(
      $(getEl("span"))
        .addClass("sample-rd")
        .addClass("sample-rd-rej")
        .click(reqRejClick)
    );

    // Count shown
    controlsL2.append(
      $(getEl("span"))
        .attr("id", this.sampleShownCount)
        .text(`${this.allSamples.length}/${this.allSamples.length}`)
    );

    const sampleSelDiv = $(getEl("div")).attr("id", this.sampleSelectId);
    outerDiv.append(sampleSelDiv);
    if (
      this.allSamples.length == 0 ||
      (this.allSamples.length == 1 && !this.allSamples[0])
    ) {
      outerDiv.closest(".filter-section").css("display", "none");
    }
    this.drawSamples(this.allSamples, sampleSelDiv);
    this.sampleSelChange();
    return outerDiv;
  }

  drawSamples(sampleIds, sampleSelDiv) {
    sampleIds = sampleIds == undefined ? this.allSamples : sampleIds;
    sampleIds = sampleIds
      .filter((sid) => this.allSamples.indexOf(sid) >= 0)
      .sort();
    sampleSelDiv =
      sampleSelDiv == undefined ? $("#" + this.sampleSelectId) : sampleSelDiv;
    sampleSelDiv.empty();
    for (let i = 0; i < sampleIds.length; i++) {
      let sid = sampleIds[i];
      let sampleBox = $(getEl("div"))
        .addClass("sample-selector")
        .click(this.onSampleSelectorClick.bind(this))
        .addClass("sample-neutral")
        .attr("title", sid);
      sampleSelDiv.append(sampleBox);
      sampleBox.append($(getEl("span")).addClass("sample-state-span"));
      sampleBox.append(
        $(getEl("span")).text(sid).addClass("sample-selector-label")
      );
      if (this.requireSamples.has(sid)) {
        sampleBox.removeClass("sample-neutral");
        sampleBox.addClass("sample-require");
      } else if (this.rejectSamples.has(sid)) {
        sampleBox.removeClass("sample-neutral");
        sampleBox.addClass("sample-reject");
      }
    }
    if (sampleIds.length === 0) {
      sampleSelDiv.text("No samples to show");
    }
    $("#" + this.sampleShownCount).text(
      `${sampleIds.length}/${this.allSamples.length}`
    );
    $('input[name="sample-sel-all"][value="neutral"]').prop("checked", true);
  }

  sampleSelChange() {
    const nReq = this.requireSamples.size;
    const nRej = this.rejectSamples.size;
    const nRule = nReq + nRej;
    $("#" + this.sampleReqCountId).text(`Include: ${nReq}`);
    $("#" + this.sampleRejCountId).text(`Exclude: ${nRej}`);
    $("#" + this.sampleInFilterCountId).text(`In filter: ${nRule}`);
  }

  sampleSelectionClear() {
    this.rejectSamples.clear();
    this.requireSamples.clear();
    this.sampleSelChange();
  }

  matchingSamples(q) {
    return this.allSamples.filter((sid) => sid.includes(q));
  }

  samplePickShown(state) {
    const selectors = $("#" + this.sampleSelectId).children(".sample-selector");
    for (let sbox of selectors) {
      this.setSampleSelector($(sbox), state);
    }
    this.sampleSelChange();
  }

  updateSampleSelect(filter) {
    filter = new CravatFilter(filter);
    let sampleContent = $("#" + this.sampleSelectId).parent();
    sampleContent.empty();
    this.addSampleSelect(sampleContent, filter);
    let sampleHeader = sampleContent
      .closest(".filter-body")
      .siblings(".filter-header");
    if (filter.sample.require.length > 0 || filter.sample.reject.length > 0) {
      sampleHeader.removeClass("inactive");
    }
  }

  setSampleSelector(sbox, state) {
    const sid = sbox.text();
    if (state === "require") {
      // Set to require
      sbox.addClass("sample-require");
      sbox.removeClass("sample-reject");
      sbox.removeClass("sample-neutral");
      sbox.attr("title", `${sid}\nVariants MUST be in this sample`);
      this.requireSamples.add(sid);
      this.rejectSamples.delete(sid);
    } else if (state === "reject") {
      // Set to reject
      sbox.removeClass("sample-require");
      sbox.addClass("sample-reject");
      sbox.removeClass("sample-neutral");
      sbox.attr("title", `${sid}\nVariants MUST NOT be in this sample`);
      this.requireSamples.delete(sid);
      this.rejectSamples.add(sid);
    } else if (state === "neutral") {
      // Set to neutral
      sbox.removeClass("sample-require");
      sbox.removeClass("sample-reject");
      sbox.addClass("sample-neutral");
      sbox.attr("title", sid);
      this.requireSamples.delete(sid);
      this.rejectSamples.delete(sid);
    }
  }

  onSampleSelectorClick(event) {
    let sbox = $(event.currentTarget);
    if (sbox.hasClass("sample-neutral")) {
      // Set to require
      this.setSampleSelector(sbox, "require");
    } else if (sbox.hasClass("sample-require")) {
      // Set to reject
      this.setSampleSelector(sbox, "reject");
    } else if (sbox.hasClass("sample-reject")) {
      // Set to neutral
      this.setSampleSelector(sbox, "neutral");
    }
    this.sampleSelChange();
  }

  sampleListFile(event) {
    const fileInput = $(event.target);
    const nameDisplay = $("#" + this.sampleFileDisplayId);
    const files = fileInput.prop("files");
    if (files.length) {
      const file = files[0];
      const fr = new FileReader();
      fr.onloadend = (loadEnd) => {
        const text = loadEnd.target.result;
        const samples = text.split(/\r?\n/g);
        this.drawSamples(samples);
      };
      fr.readAsText(file);
      nameDisplay.text(file.name);
    } else {
      nameDisplay.text(null);
    }
  }

  addGeneSelect(outerDiv, filter) {
    filter = new CravatFilter(filter);
    outerDiv.attr("id", this.geneContId);
    outerDiv.append(
      $(getEl("div")).text(
        "Type a list of gene names to include. One per line. Or, load a gene list from a file."
      )
    );
    let geneTextArea = $(getEl("textarea"))
      .attr("id", this.geneTextId)
      .change(this.onGeneListSelectorChange.bind(this));
    outerDiv.append(geneTextArea);
    let geneFileInput = $(getEl("input"))
      .attr("type", "file")
      .attr("id", this.geneFileId)
      .change(this.onGeneListSelectorChange.bind(this));
    outerDiv.append(geneFileInput);
    if (filter.genes.length > 0) {
      geneTextArea.val(filter.genes.join("\n"));
    }
    return outerDiv;
  }

  onGeneListSelectorChange(e) {
    //Arrow function to maintain this=FilterManager
    let target = $(e.target);
    let id = target.attr("id");
    if (id === this.geneTextId) {
      let fileInput = $("#gene-list-file");
      fileInput.val("");
    } else if (id === this.geneFileId) {
      let fileInput = target;
      let textArea = $("#" + this.geneTextId);
      let fr = new FileReader();
      fr.onloadend = function (_) {
        //Not an arrow function so that this=FileReader
        textArea.val(this.result);
      };
      fr.readAsText(fileInput.prop("files")[0]);
    }
  }

  updateGeneSelect(filter) {
    filter = new CravatFilter(filter);
    let geneSelect = $("#" + this.geneTextId).parent();
    geneSelect.empty();
    this.addGeneSelect(geneSelect, filter);
    let geneHeader = geneSelect
      .closest(".filter-body")
      .siblings(".filter-header");
    if (filter.genes.length > 0) {
      geneHeader.removeClass("inactive");
    }
  }

  addVpropUI(vPropCont, filter) {
    filter = new CravatFilter(filter);
    vPropCont.attr("id", this.variantContId);
    vPropCont.append(
      $(getEl("div")).text(
        "Select variants by applying filters or building a query"
      )
    );
    let fTypeDiv = $(getEl("div"));
    vPropCont.append(fTypeDiv);
    let vPropSel = $(getEl("select"))
      .attr("id", this.vpropSelectId)
      .append($(getEl("option")).val("sf").text("sf"))
      .append($(getEl("option")).val("qb").text("qb"))
      .css("display", "none")
      .change(this.vPropSelectChange.bind(this));
    fTypeDiv.append(vPropSel);
    let sfContent = $(getEl("div")).attr("id", this.vpropSfId);
    vPropCont.append(sfContent);
    this.addSfUI(sfContent, filter);
    let qbContent = $(getEl("div")).attr("id", this.vpropQbId);
    vPropCont.append(qbContent);
    this.addQbUI(qbContent, filter);
    vPropSel.val("qb");
    vPropSel.change();
  }

  addSfUI(outerDiv, filter) {
    filter = new CravatFilter(filter);
    let orderedSources = Object.keys(smartFilters);
    if (orderedSources.length === 0) {
      return;
    }
    orderedSources.splice(orderedSources.indexOf("base"), 1);
    orderedSources.sort();
    orderedSources = ["base"].concat(orderedSources);
    outerDiv.append($(getEl("div")).text("Click a filter to apply it."));
    for (let i = 0; i < orderedSources.length; i++) {
      let sfSource = orderedSources[i];
      let sfGroup = smartFilters[sfSource];
      for (let j = 0; j < sfGroup.order.length; j++) {
        let sfName = sfGroup.order[j];
        let sfDef = sfGroup.definitions[sfName];
        let sfVal = undefined;
        if (filter.smartfilter.hasOwnProperty(sfSource)) {
          sfVal = filter.smartfilter[sfSource][sfName];
        }
        let sf = new SmartFilter(sfDef, sfVal);
        let sfDiv = sf.getDiv();
        sfDiv.attr("full-name", sfSource + "." + sfName);
        outerDiv.append(sfDiv);
      }
    }
  }

  addQbUI(outerDiv, filter) {
    filter = new CravatFilter(filter);
    outerDiv.append(
      $(getEl("div")).text(
        "Use the query builder to create a set of filter rules"
      )
    );
    let qbDiv = makeFilterGroupDiv(filter.variant);
    qbDiv.children(".filter-element-control-div").remove();
    qbDiv[0].querySelector(".addrule").style.visibility = "visible";
    qbDiv[0].querySelector(".addgroup").style.visibility = "visible";
    qbDiv[0].querySelector(".passthrough").remove();
    qbDiv.attr("id", this.qbRootId);
    outerDiv.append(qbDiv);
  }

  updateVpropUI(filter) {
    filter = new CravatFilter(filter);
    let vPropCont = $("#" + this.variantContId);
    vPropCont.empty();
    this.addVpropUI(vPropCont, filter);
    let vpropHeader = vPropCont
      .closest(".filter-body")
      .siblings(".filter-header");
    if (filter.variant.rules.length > 0) {
      vpropHeader.removeClass("inactive");
    }
  }

  vPropSelectChange(event) {
    let sel = $(event.target);
    let val = sel.val();
    if (val === "qb") {
      var toShow = $("#" + this.vpropQbId);
      var toHide = $("#" + this.vpropSfId);
    } else if (val === "sf") {
      var toShow = $("#" + this.vpropSfId);
      var toHide = $("#" + this.vpropQbId);
    }
    toShow.css("display", "");
    toHide.css("display", "none");
  }

  vPropOptionClick(event) {
    let target = $(event.target);
    let val = target.attr("value");
    let vPropSel = $("#vprop-sel");
    if (val !== vPropSel.val()) {
      vPropSel.val(val);
      vPropSel.change();
    }
    $(".vprop-option").removeClass("active");
    target.addClass("active");
  }

  updateAll(filter) {
    this.updateSampleSelect(filter);
    this.updateGeneSelect(filter);
    this.updateVpropUI(filter);
  }
}

class CravatFilter {
  constructor(f) {
    f = f !== undefined ? f : {};
    this.variant =
      f.variant !== undefined ? f.variant : { operator: "and", rules: [] };
    this.smartfilter = f.smartfilter !== undefined ? f.smartfilter : {};
    this.genes = f.genes !== undefined ? f.genes : [];
    this.sample =
      f.sample !== undefined ? f.sample : { require: [], reject: [] };
  }
}

class SmartFilter {
  constructor(sfDef, value) {
    this.sfDef = sfDef;
    this.valProvided = value !== undefined;
    this.value = this.valProvided ? value : sfDef.selector.defaultValue;
    this.selectorType = this.sfDef.selector.type;
    if (this.value === undefined || this.value === null) {
      if (this.selectorType === "inputFloat") {
        this.value = 0.0;
      } else if (this.selectorType === "select") {
        this.value = [];
      } else {
        this.value = "";
      }
    }
  }

  getDiv() {
    let outerDiv = $(getEl("div")).addClass("smartfilter");
    outerDiv[0].addEventListener(
      "click",
      (e) => {
        let sfDiv = $(e.currentTarget);
        if (sfDiv.hasClass("smartfilter-inactive")) {
          this.setSfState(sfDiv, true);
          e.preventDefault();
        }
      },
      true
    ); // Not using jquery so that event fires on capture phase
    let titleSpan = $(getEl("span")).addClass("sf-title");
    outerDiv.append(titleSpan);
    let titleLabel = $(getEl("label"))
      .attr("title", this.sfDef.description)
      .addClass("checkbox-container")
      .append(this.sfDef.title);
    titleSpan.append(titleLabel);
    let activeCb = $(getEl("input"))
      .attr("type", "checkbox")
      .addClass("smartfilter-checkbox")
      .change(this.sfCheckboxChangeHandler.bind(this));
    titleLabel.append(activeCb);
    titleLabel.append($(getEl("span")).addClass("checkmark"));
    let selectorSpan = $(getEl("span")).addClass("sf-selector");
    outerDiv.append(selectorSpan);
    if (this.selectorType === "inputFloat") {
      let valueInput = $(getEl("input")).val(this.value);
      selectorSpan.append(valueInput);
    } else if (this.selectorType === "inputInt") {
      let valueInput = $(getEl("input")).attr("type", "number").val(this.value);
      selectorSpan.append(valueInput);
    } else if (this.selectorType === "inputString") {
      let valueInput = $(getEl("input")).val(this.value);
      selectorSpan.append(valueInput);
    } else if (this.selectorType === "select") {
      let select = $(getEl("select")).addClass("filter-value-input");
      let allowMult = this.sfDef.selector.multiple;
      allowMult = allowMult === undefined ? false : allowMult;
      if (allowMult === true) {
        select.prop("multiple", "multiple");
      }
      selectorSpan.append(select);
      let options = this.sfDef.selector.options;
      if (options !== undefined) {
        if (Array.isArray(options)) {
          var optionTexts = options;
          var text2Val = {};
        } else {
          var text2Val = options;
          var optionTexts = Object.keys(text2Val);
        }
      } else {
        let optsColName = this.sfDef.selector.optionsColumn;
        let optsCol = getFilterColByName(optsColName);
        var optionTexts = optsCol.filter.options;
        var text2Val = {};
        let reportSubs = optsCol.reportsub;
        if (reportSubs !== undefined && Object.keys(reportSubs).length > 0) {
          text2Val = swapJson(reportSubs);
        }
      }
      if (Object.keys(text2Val).length === 0) {
        for (let i = 0; i < optionTexts.length; i++) {
          text2Val[optionTexts[i]] = optionTexts[i];
        }
      }
      let defaultSelections = []; //TODO improve. Probably need each sf type to be subclass
      if (this.value === undefined || this.value === null) {
        defaultSelections = [];
      } else if (Array.isArray(this.value)) {
        defaultSelections = this.value;
      } else {
        defaultSelections = [this.value];
      }
      for (let i = 0; i < optionTexts.length; i++) {
        let optText = optionTexts[i];
        let optVal = text2Val[optText];
        let opt = $(getEl("option"))
          .val(optVal)
          .prop("typedValue", optVal)
          .append(optText);
        if (defaultSelections.indexOf(optVal) >= 0) {
          opt[0].selected = true;
        }
        select.append(opt);
      }
      select.pqSelect({
        checkbox: true,
        displayText: "{0} selected",
        singlePlaceholder: "&#x25BD;",
        multiplePlaceholder: "&#x25BD;",
        maxDisplay: 0,
        width: 200,
        search: false,
        selectallText: "Select all",
      });
      activeCb.change();
    }
    this.setSfState(outerDiv, this.valProvided);

    return outerDiv;
  }

  setSfState(sfDiv, active) {
    if (active) {
      sfDiv.removeClass("smartfilter-inactive");
      sfDiv.addClass("smartfilter-active");
      sfDiv.find(".smartfilter-checkbox").prop("checked", true);
    } else {
      sfDiv.addClass("smartfilter-inactive");
      sfDiv.removeClass("smartfilter-active");
      sfDiv.find(".smartfilter-checkbox").prop("checked", false);
    }
  }

  sfCheckboxChangeHandler(event) {
    let cb = $(event.target);
    let sfDiv = cb.closest(".smartfilter");
    let sfActive = cb.prop("checked");
    this.setSfState(sfDiv, sfActive);
  }
}

// Global FilterMgr
filterMgr = new FilterManager();

function populateFilterSaveNames() {
  $.get("/result/service/getfiltersavenames", {
    username: username,
    uid: uid,
    dbpath: dbPath,
  }).done(function (response) {
    let quicksaveIndex = response.indexOf("quicksave-name-internal-use");
    if (quicksaveIndex > -1) {
      response.splice(quicksaveIndex, 1);
    }
    let savedList = $("#saved-filter-list");
    savedList.empty();
    if (response.length === 0) {
      $("#filter-left-panel").css("display", "none");
    } else {
      $("#filter-left-panel").css("display", "");
    }
    for (let i = 0; i < response.length; i++) {
      let filterName = response[i];
      let li = $(getEl("li")).addClass("filter-list-item");
      savedList.append(li);
      li.append(
        $(getEl("span"))
          .text(filterName)
          .addClass("filter-list-item-title")
          .attr("title", filterName)
          .click(savedFilterClick)
      );
      li.append(
        $(getEl("img"))
          .attr("src", "images/download-material-black.png")
          .addClass("filter-list-item-export")
          .attr("title", "Export filter to file")
          .click(() => {
            exportFilter(filterName);
          })
      );
      li.append(
        $(getEl("img"))
          .attr("src", "images/close.png")
          .addClass("filter-list-item-delete")
          .attr("title", "delete filter")
          .click(filterDeleteIconClick)
          .prop("filterName", filterName)
      );
    }
  });
}

function savedFilterClick(_) {
  let target = $(this);
  let filterName = target.text();
  getSavedFilter(filterName).then((msg) => {
    filterMgr.updateAll(msg["filterSet"]);
    lastUsedFilterName = filterName;
  });
}

function exportFilter(filterName) {
  getSavedFilter(filterName).then((msg) => {
    let text = JSON.stringify(msg["filterSet"], null, 2);
    var link = getEl("a");
    link.download = filterName + ".json";
    var blob = new Blob([text], { type: "text/plain" });
    link.href = window.URL.createObjectURL(blob);
    link.click();
    document.body.removeChild(link);
  });
}

function filterDeleteIconClick(_) {
  let target = $(this);
  let filterName = target.prop("filterName");
  deleteFilterSetting(filterName).then((_) => {
    populateFilterSaveNames();
  });
}

function makeFilterTab(rightDiv) {
  rightDiv = $(rightDiv);
  rightDiv.empty();
  /*if (!showFilterTabContent) {
    rightDiv.css("display", "grid");
    rightDiv.append(
      $(getEl("img")).attr("src", "images/bigSpinner.gif").css("margin", "auto")
    );
    return false;
  } else {
    rightDiv.css("display", "");
  }*/

  // Left panel
  let leftPanel = $(getEl("div")).attr("id", "filter-left-panel");
  rightDiv.append(leftPanel);
  leftPanel.append(
    $(getEl("div"))
      .text("Saved Filters")
      .addClass("title")
      .attr("id", "saved-filter-header")
  );
  let savedList = $(getEl("ul")).attr("id", "saved-filter-list");
  leftPanel.append(savedList);
  populateFilterSaveNames();

  // Right panel
  let rightPanel = $(getEl("div")).attr("id", "filter-right-panel");
  rightDiv.append(rightPanel);

  // Smartfilters
  let vPropSection = filterMgr.getFilterSection("Variant Properties", true);
  rightPanel.append(vPropSection);
  let vPropContent = vPropSection.find(".filter-content");
  filterMgr.addVpropUI(vPropContent);

  // Gene selector
  let geneSection = filterMgr.getFilterSection("Genes", false);
  rightPanel.append(geneSection);
  let geneContent = geneSection.find(".filter-content");
  filterMgr.addGeneSelect(geneContent);

  // Sample selector
  let sampleSection = filterMgr.getFilterSection("Samples", false);
  rightPanel.append(sampleSection);
  // Sample has it's own clear button
  sampleSection.find(".filter-controls").css("display", "none");
  let sampleContent = sampleSection.find(".filter-content");
  filterMgr.addSampleSelect(sampleContent);

  // Load controls
  let loadControls = $(getEl("div"))
    .attr("id", "filter-load-controls")
    .addClass("filter-section");
  rightPanel.append(loadControls);
  var label = getEl("span")
  label.textContent = "Count preview:"
  label.classList.add(...stringToArray("cursor-pointer mr-2"))
  addEl(loadControls[0], label)
  let countDisplay = $(getEl("span"))
    .attr("id", "filter-count-display")
    .text("Count not up to date");
  loadControls.append(countDisplay);
  var btn = getEl("button")
  btn.classList.add(...stringToArray("ml-2 butn"))
  btn.title = "Count the result of filter"
  btn.textContent = "Preview"
  btn.addEventListener("click", function(_) {
    countFilterVariants();
  })
  loadControls[0].appendChild(btn)
  //var filterApply = getEl("button");
  //filterApply.id = "load_button";
  //filterApply.classList.add("butn");
  //addEl(filterApply, getTn("Apply"));
  //filterApply.addEventListener("click", function (_) {
  //  makeFilterJson();
  //  drawingRetrievingDataDiv("filter");
  //  loadData()
  //  loadLayoutSetting(quickSaveName, null);
  //});
  //loadControls.append(filterApply);
  var saveIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  saveIcon.style.marginLeft = "auto";
  saveIcon.setAttribute("id", "filter-save");
  saveIcon.setAttribute("class", "h-5 w-5");
  saveIcon.setAttribute("title", "Save filter");
  saveIcon.setAttribute("fill", "none");
  saveIcon.setAttribute("viewBox", "0 0 24 24");
  saveIcon.setAttribute("stroke", "currentColor");
  saveIcon.setAttribute("stroke-width", "1");
  var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("stroke-linecap", "round");
  path.setAttribute("stroke-linejoin", "round");
  path.setAttribute(
    "d",
    "M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
  );

  saveIcon.addEventListener("click", function (_) {
    saveFilterSettingAs().then(function (_) {
      populateFilterSaveNames();
    });
  });
  addEl(saveIcon, path);
  addEl(loadControls[0], saveIcon);
  let importInput = $(getEl("input"))
    .attr("id", "filter-import")
    .attr("type", "file")
    .change((event) => {
      if (event.target.files.length > 0) {
        importFilter(event.target.files[0]);
        event.target.value = null;
      }
    })
    .css("display", "none");
  loadControls.append(importInput);
  let importLabel = $(getEl("label"))
    .attr("id", "filter-import-label")
    .attr("for", "filter-import")
    .attr("title", "Import filter from file");
  loadControls.append(importLabel);
  var importImg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  importImg.setAttribute("class", "h-5 w-5");
  importImg.setAttribute("fill", "none");
  importImg.setAttribute("viewBox", "0 0 24 24");
  importImg.setAttribute("stroke", "currentColor");
  importImg.setAttribute("stroke-width", "1");
  var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("stroke-linecap", "round");
  path.setAttribute("stroke-linejoin", "round");
  path.setAttribute(
    "d",
    "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
  );
  addEl(importImg, path);
  addEl(importLabel[0], importImg);
  return true;
}

function importFilter(file) {
  var reader = new FileReader();
  reader.readAsText(file, "utf-8");
  reader.addEventListener("load", (e) => {
    var filter = JSON.parse(e.target.result);
    filterMgr.updateAll(filter);
  });
}

function countFilterVariants() {
  enableLoadingDiv()
  return new Promise((resolve, _) => {
    makeFilterJson();
    infomgr.count(dbPath, "variant", (_, data) => {
      let count = data.n;
      displayFilterCount(count);
      removeLoadingDiv()
      resolve(count);
    });
  });
}

function displayFilterCount(n) {
  let t = parseInt(infomgr.get_total_num_variants());
  n = n === undefined ? t : n;
  let countDisplay = $("#filter-count-display");
  countDisplay.text(`${n.toLocaleString()}/${t.toLocaleString()} variants`);
}

function getFilterFile() {
  makeFilterJson();
  var fn = "filter.json";
  if (lastUsedFilterName != null && lastUsedFilterName != quickSaveName) {
    fn = lastUsedFilterName + ".json";
  }
  var fn = prompt("Filter file name", fn);
  if (fn == "" || fn == null || fn == undefined) {
    return;
  }
  var a = getEl("a");
  a.download = fn;
  var blob = new Blob([JSON.stringify(filterJson, null, 2)], {
    type: "text/plain",
  });
  a.href = window.URL.createObjectURL(blob);
  a.click();
}

function makeFilterJson() {
  let fjs = {};
  // Samples
  if (filterMgr.requireSamples.size > 0 || filterMgr.requireSamples.size > 0) {
    fjs.sample = {
      require: [...filterMgr.requireSamples],
      reject: [...filterMgr.rejectSamples],
    };
  }
  // Gene list
  let geneListString = document.querySelector("#" + filterMgr.geneTextId).value
  if (geneListString != "") {
    let geneList = geneListString
      .split("\n")
      .map((s) => s.trim())
      .map((s) => s.toUpperCase())
    fjs.genes = geneList;
  }
  // Variant Properties
  let activeVprop = document.querySelector("#" + filterMgr.vpropSelectId).value
  if (activeVprop === "sf") {
    let sfWrapDiv = $("#" + filterMgr.vpropSfId);
    let sfDivs = sfWrapDiv.children("div");
    let fullSf = { operator: "and", rules: [] };
    let sfState = {};
    var sfUsed = false
    for (let i = 0; i < sfDivs.length; i++) {
      sfDiv = $(sfDivs[i]);
      if (!sfDiv.hasClass("smartfilter-active")) {
        continue;
      }
      let fullName = sfDiv.attr("full-name");
      let sfSource = fullName.split(".")[0];
      let sfName = fullName.split(".")[1];
      let sfDef = smartFilters[sfSource].definitions[sfName];
      sfDef.filter.level = sfDef.level
      let val = pullSfValue(sfDiv);
      let sfResult = addSfValue(sfDef.filter, val);
      fullSf.rules.push(sfResult);
      if (!sfState.hasOwnProperty(sfSource)) {
        sfState[sfSource] = {};
      }
      sfState[sfSource][sfName] = val;
      sfUsed = true
    }
    if (sfUsed) {
      fjs.variant = fullSf;
      fjs.smartfilter = sfState;
    }
  } else if (activeVprop === "qb") {
    let qbRoot = $("#" + filterMgr.qbRootId);
    fjs.variant = makeGroupFilter(qbRoot);
    //fjs.smartfilter = {};
  }
  if (Object.keys(fjs).length == 0) {
    filterJson = null
  } else {
    filterJson = fjs;
  }
}

function addSfValue(topRule, value) {
  topRule = JSON.parse(JSON.stringify(topRule));
  if (topRule.hasOwnProperty("rules")) {
    for (let i = 0; i < topRule.rules.length; i++) {
      let subRule = topRule.rules[i];
      topRule.rules[i] = addSfValue(subRule, value);
    }
  } else {
    for (let k in topRule) {
      let v = topRule[k];
      if (v === "${value}") {
        topRule[k] = value;
      }
    }
  }
  return topRule;
}

function reduceSf(topRule, allowPartial) {
  topRule = JSON.parse(JSON.stringify(topRule));
  if (topRule.hasOwnProperty("rules")) {
    let newSubRules = [];
    for (let i = 0; i < topRule.rules.length; i++) {
      let subRule = topRule.rules[i];
      let newSubRule = reduceSf(subRule, allowPartial);
      if (newSubRule !== null) {
        if (allowPartial) {
          newSubRules.push(newSubRule);
        } else {
          return null;
        }
      }
    }
    topRule.rules = newSubRules;
    if (topRule.rules.length > 1) {
      return topRule;
    } else if (topRule.rules.length === 1) {
      return topRule.rules[0];
    } else {
      return null;
    }
  } else {
    return getFilterColByName(topRule.column) !== null ? topRule : null;
  }
}

function pullSfValue(selectorDiv) {
  let fullName = selectorDiv.attr("full-name");
  let sfSource = fullName.split(".")[0];
  let sfName = fullName.split(".")[1];
  let sfDef = smartFilters[sfSource].definitions[sfName];
  let selectorType = sfDef.selector.type;
  let selectorWrapper = selectorDiv.children(".sf-selector");
  if (selectorType === "inputFloat") {
    return parseFloat(selectorWrapper.children("input").val());
  } else if (selectorType === "inputInt") {
    return parseInt(selectorWrapper.children("input").val());
  } else if (selectorType === "inputString") {
    return selectorWrapper.children("input").val();
  } else if (selectorType === "select") {
    let selector = selectorWrapper.children(".filter-value-input").first();
    let selOpts = selector[0].selectedOptions;
    if (selector.prop("multiple")) {
      let vals = [];
      for (let i = 0; i < selOpts.length; i++) {
        vals.push($(selOpts[i]).prop("typedValue"));
      }
      return vals;
    } else {
      return $(selOpts[0]).prop("typedValue");
    }
  } else if (selectorType === "empty") {
    return null;
  }
}

function hideTableToggleBtn() {
  getTableToggleBtn().style.display = "none"
}

function showTableToggleBtn() {
  getTableToggleBtn().style.display = "block"
}

function hideDetailToggleBtn() {
  getDetailToggleBtn().style.display = "none"
}

function showDetailToggleBtn() {
  getDetailToggleBtn().style.display = "block"
}

function changeMenu() {
  if (currentTab == "variant" || currentTab == "gene") {
    if (firstLoad == false) {
      turnOnMenu("layout_columns_menu");
      turnOnMenu("layout_widgets_menu");
      populateTableColumnSelectorPanel();
      populateWidgetSelectorPanel();
      showTableToggleBtn()
      showDetailToggleBtn()
    }
  } else if (currentTab == "info") {
    turnOffMenu("layout_columns_menu");
    turnOnMenu("layout_widgets_menu");
    populateWidgetSelectorPanel();
    hideTableToggleBtn()
    hideDetailToggleBtn()
  } else {
    turnOffMenu("layout_columns_menu");
    turnOffMenu("layout_widgets_menu");
    hideTableToggleBtn()
    hideDetailToggleBtn()
  }
}

function downloadReport(j, d, reportType) {
  var data = j
  if (dbPath) {
    data = d
  }
  url = "/submit/downloadreport/" + reportType
  var form = getEl("form")
  form.setAttribute("action", url)
  form.setAttribute("method", "post")
  var input1 = getEl("input")
  input1.setAttribute("type", "hidden")
  if (uid) {
    input1.setAttribute("name", "uid")
    input1.setAttribute("value", uid)
  } else if (dbPath) {
    input1.setAttribute("name", "dbpath")
    input1.setAttribute("value", dbPath)
  }
  addEl(form, input1)
  var body = document.getElementsByTagName("body")[0]
  addEl(body, form)
  form.submit()
  form.remove()
}

function showYesNoDialog(content, yescallback, noSpace, justOk) {
    var div = document.getElementById('yesnodialog');
    if (div != undefined) {
        $(div).remove();
    }
    var div = getEl('div');
    div.id = 'yesnodialog';
    if (typeof content === 'string') {
        content = getTn(content);
    }
    content.id = 'yesnodialog-contentdiv'
    addEl(div, content);
    addEl(div, getEl('br'));
    var btnDiv = getEl('div');
    if (justOk) {
        btnDiv.className = 'buttondiv';
        var btn = getEl('button');
        btn.textContent = 'Ok';
        btn.addEventListener('click', function(_) {
            if (yescallback == undefined || yescallback == null) {
                $('#yesnodialog').remove();
            } else {
                $('#yesnodialog').remove();
                yescallback();
            }
        });
        addEl(btnDiv, btn);
    } else {
        btnDiv.className = 'buttondiv';
        var btn = getEl('button');
        btn.textContent = 'Yes';
        btn.addEventListener('click', function(_) {
            $('#yesnodialog').remove();
            yescallback(true);
        });
        if (noSpace) {
            btn.disabled = true;
            btn.style.backgroundColor = '#e0e0e0';
        }
        addEl(btnDiv, btn);
        var btn = getEl('button');
        btn.textContent = 'No';
        btn.addEventListener('click', function(_) {
            $('#yesnodialog').remove();
            yescallback(false);
        });
        addEl(btnDiv, btn);
    }
    addEl(div, btnDiv);
    addEl(document.body, div);
}

async function generateReport(j, d, reportType) {
  var res = await axios.post("/submit/makereport/" + reportType,
    { job_id: j, dbpath: d }
  )
  var data = res.data
  if (data == "fail") {
    var mdiv = getEl("div");
    var span = getEl("span");
    span.textContent =
      reportType + " report generation failed for " + uid;
    addEl(mdiv, span);
    addEl(mdiv, getEl("br"));
    addEl(mdiv, getEl("br"));
    var span = getEl("span");
    span.textContent = "Check your system's gui.log for details.";
    addEl(mdiv, span);
    showYesNoDialog(mdiv, null, false, true);
  } else {
    console.log("setting up report")
    makeReportTab(getRightDiv("report"))
  }
}

async function makeReportTab(rightDiv) {
  rightDiv.textContent = ""
  const tabName = "report";
  var rightContentDiv = getEl("div");
  rightContentDiv.id = "rightcontentdiv_" + tabName;
  rightContentDiv.className = "rightcontentdiv";
  addEl(rightDiv, rightContentDiv);
  var res = await axios.get("/submit/reporttypes")
  var reportTypes = res.data.valid;
  reportTypes.sort()
  var res = await axios.post("/submit/jobs/reports",
    {dbpath: dbPath, uid: uid}
  )
  var madeReportTypes = res.data
  var ul = getEl("ul")
  ul.className = "grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 p-6"
  ul.style.width = "calc(100% - 34px)"
  ul.setAttribute("role", "list")
  addEl(rightContentDiv, ul)
  for (var i=0; i<reportTypes.length; i++) {
    const reportType = reportTypes[i]
    const moduleName = reportType + "reporter"
    var res = await axios.get("/submit/localmodules/" + moduleName)
    const mi = res.data
    var li = getEl("li")
    li.className = "col-span-1 bg-white rounded-lg shadow divide-y divide-gray-200"
    li.setAttribute("reporttype", reportType)
    addEl(ul, li)
    var div1 = getEl("div")
    div1.className = "w-full flex items-center justify-between p-6 space-x-6"
    addEl(li, div1)
    var div2 = getEl("div")
    div2.className = "flex-1 truncate"
    addEl(div1, div2)
    var div3 = getEl("div")
    div3.className = "flex items-center space-x-3"
    addEl(div2, div3)
    var h3 = getEl("h3")
    h3.className = "text-gray-900 text-sm font-medium truncate reportname"
    h3.textContent = mi["title"]
    addEl(div3, h3)
    var p = getEl("p")
    p.className = "mt-1 text-gray-500 text-sm truncate reportdesc"
    p.textContent = mi["description"]
    p.title = mi["description"]
    addEl(div2, p)
    var p = getEl("p")
    p.className = "mt-1 text-gray-400 text-xs truncate reportdesc"
    p.textContent = mi["local_code_version"]
    addEl(div2, p)
    var imgDiv = getEl("img")
    imgDiv.className = "h-10"
    imgDiv.setAttribute("alt", "")
    var res = await axios.get("/store/locallogoexists/" + moduleName)
    if (res.data == "success") {
      imgDiv.src = "/store/locallogo?module=" + moduleName
      addEl(div1, imgDiv)
    } else {
      imgDiv.remove()
    }
    var lowerdiv = getEl("div")
    addEl(li, lowerdiv)
    var actionsDiv = getEl("div")
    actionsDiv.className = "-mt-px flex divide-x divide-gray-200"
    addEl(lowerdiv, actionsDiv)
    if (madeReportTypes.indexOf(reportType) == -1) {
      var generateDiv = getEl("div")
      generateDiv.className = "w-0 flex-1 flex"
      addEl(actionsDiv, generateDiv)
      var a = getEl("a")
      a.href = "#"
      a.className = "relative -mr-px w-0 flex-1 inline-flex items-center justify-center py-4 text-sm text-gray-700 font-medium border border-transparent rounded-bl-lg hover:text-gray-500"
      a.textContent = "Generate"
      a.addEventListener("click", async function(_) {
        this.textContent = "Generating..."
        await generateReport(uid, dbPath, reportType)
      })
      addEl(generateDiv, a)
    } else {
      var downloadDiv = getEl("div")
      downloadDiv.className = "w-0 flex-1 flex"
      addEl(actionsDiv, downloadDiv)
      var a = getEl("a")
      a.href = "#"
      a.className = "relative -mr-px w-0 flex-1 inline-flex items-center justify-center py-4 text-sm text-gray-700 font-medium border border-transparent rounded-bl-lg hover:text-gray-500"
      a.textContent = "Download"
      a.addEventListener("click", async function(_) {
        downloadReport(uid, dbPath, reportType)
      })
      addEl(downloadDiv, a)
    }
  }
}

function makeJobTab(rightDiv) {
  const tabName = "job";
  var rightContentDiv = getEl("div");
  rightContentDiv.id = "rightcontentdiv_" + tabName;
  rightContentDiv.className = "rightcontentdiv";
  addEl(rightDiv, rightContentDiv);
  var infoDiv = getEl("fieldset");
  infoDiv.id = "info_div";
  addEl(rightContentDiv, infoDiv);
  // Widget Notice
  var wgNoticeDiv = getEl("fieldset");
  wgNoticeDiv.id = "wgnoticediv";
  wgNoticeDiv.className = "detailContent";
  wgNoticeDiv.style.display = "none";
  addEl(infoDiv, wgNoticeDiv);
}

function makeInfoTab(rightDiv) {
  var tabName = "info";
  // right content div
  var rightContentDiv = getEl("div");
  rightContentDiv.id = "rightcontentdiv_" + tabName;
  rightContentDiv.className = "rightcontentdiv";
  addEl(rightDiv, rightContentDiv);
  // Notice
  var noticeDiv = getEl("div");
  noticeDiv.className = "infonoticediv";
  noticeDiv.id = "infonoticediv";
  noticeDiv.textContent = " ";
  addEl(rightContentDiv, noticeDiv);
  // detail div
  var detailDiv = getEl("div");
  detailDiv.id = "detaildiv_" + tabName;
  detailDiv.className = "detaildiv";
  addEl(rightContentDiv, detailDiv);
  // detail content div
  var widgetDiv = getEl("div");
  widgetDiv.id = "detailcontainerdiv_info";
  widgetDiv.className = "detailcontainerdiv";
  addEl(detailDiv, widgetDiv);
}

function packWidgets(tabName) {
  var mason = new Packery("#detailcontainerdiv_" + tabName, {
    itemSelector: ".detailwidget",
    columnWidth: widgetWidthGridSize,
    rowHeight: widgetHeightGridSize,
  });
  masons[tabName] = mason;
  var widgets = mason.getItemElements();
  widgets.forEach(function (widget) {
    var draggie = new Draggabilly(widget, {
      handle: ".detailwidgetheader",
    });
    mason.bindDraggabillyEvents(draggie);
  });
  $(widgets).resizable({
    grid: [widgetWidthGridSize, widgetHeightGridSize],
    autoHide: true,
    start: function (evt, _) {
      var widgetName = evt.target.getAttribute("widgetkey");
      var generator = widgetGenerators[widgetName][currentTab];
      if (generator["beforeresize"] != undefined) {
        generator["beforeresize"]();
      }
    },
    stop: function (evt, _) {
      var resizeTimeout = null
      var widgetName = evt.target.getAttribute("widgetkey");
      evt.target.style.width =
        Math.round(evt.target.offsetWidth / widgetWidthGridSize) *
        widgetWidthGridSize;
      evt.target.style.height =
        Math.round(evt.target.offsetHeight / widgetHeightGridSize) *
        widgetHeightGridSize;
      var generator = widgetGenerators[widgetName][currentTab];
      var v = generator["variables"];
      var parentDiv = v["parentdiv"];
      if (tabName != "info" && generator["donterase"] != true) {
        widgetContentDiv = evt.target.querySelector(".detailcontentdiv")
        $(widgetContentDiv).empty();
      }
      generator["variables"]["resized"] = true;
      if (tabName != "info") {
        $(parentDiv).empty();
      }
      var $grid = $grids[tabName]
      if ($grid != undefined) {
        var row = $grids[tabName].pqGrid("getData")[selectedRowNos[tabName]];
        if (generator["confirmonresize"] == true) {
          var div = getEl("div");
          div.className = "widget-redraw-confirm";
          var span = getEl("span");
          span.textContent = "Click to redraw";
          addEl(div, span);
          addEl(parentDiv, div);
          div.addEventListener("click", function () {
            generator["function"](parentDiv, row, tabName);
          });
        } else if (generator["onresize"] != undefined) {
          if (resizeTimeout) {
            clearTimeout(resizeTimeout);
          }
          resizeTimeout = setTimeout(function () {
            generator["onresize"](parentDiv, row, tabName);
          }, 100);
        } else {
          generator["function"](parentDiv, row, tabName);
        }
      }
      mason.layout();
      loadedViewerWidgetSettings[currentTab] = undefined;
    },
  });
}

function getSummaryVarLimitWarningDiv() {
  return document.querySelector("#summary-var-limit-warning-div")
}

function hideSummaryVarLimitWarningDiv() {
    getSummaryVarLimitWarningDiv().classList.add("hidden")
}

function showSummaryVarLimitWarningDiv() {
    getSummaryVarLimitWarningDiv().classList.remove("hidden")
}

function setSummaryVarLimitSpan() {
  document.querySelector("#summary-var-limit-span").textContent = summaryVarLimit
}

function populateSummaryWidgetDiv() {
  if (infomgr.totalNoRows > summaryVarLimit) {
    setSummaryVarLimitSpan()
    showSummaryVarLimitWarningDiv()
    return
  }
  var tabName = "info";
  var outerDiv = document.getElementById("detailcontainerdiv_info");
  var widgetDivs = outerDiv.children;
  var reuseWidgets = true;
  if (widgetDivs.length == 0) {
    reuseWidgets = false;
    $(widgetDiv).packery("destroy");
    emptyElement(outerDiv);
  } else {
    widgetDivs = $(outerDiv).packery("getItemElements");
  }
  var widgetNames = Object.keys(widgetGenerators);
  if (widgetNames.length == 0) {
    return;
  } else {
    var orderNums = Object.keys(detailWidgetOrder[tabName]);
    for (var i = 0; i < orderNums.length; i++) {
      var colGroupKey = detailWidgetOrder[tabName][orderNums[i]];
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
        var widgetContentDiv = null;
        if (reuseWidgets) {
          widgetDiv = document.getElementById(
            "detailwidget_" + tabName + "_" + widgetName
          );
          widgetContentDiv = document.getElementById(
            "widgetcontentdiv_" + colGroupKey + "_" + tabName
          );
          if (generator["donterase"] != true) {
            $(widgetContentDiv).empty();
          }
        } else {
          [widgetDiv, widgetContentDiv] = getDetailWidgetDivs(
            tabName,
            colGroupKey,
            colGroupTitle
          );
          generator["variables"]["parentdiv"] = widgetContentDiv;
        }
        if (reuseWidgets != true) {
          widgetDiv.clientWidth = generator["width"];
          widgetDiv.clientHeight = generator["height"];
          widgetDiv.style.width = generator["width"] + "px";
          widgetDiv.style.height = generator["height"] + "px";
        }
        var outerDiv = document.getElementById("detailcontainerdiv_info");
        addEl(outerDiv, widgetDiv);
        try {
          drawSummaryWidget(colGroupKey);
        } catch (err) {
          console.log(err);
          console.log("### continuing to the next widget ###");
        }
      }
    }
  }
  packWidgets(tabName);
  if (reuseWidgets != true) {
    applyWidgetSetting("info");
  }
}

function onClickTableColumnButton() {
  if (currentTab != "variant" && currentTab != "gene") {
    return;
  }
  var button = evt.target;
  var panel = button.parentElement.parentElement.getElementsByClassName(
    "tablecolumnselectorpanel"
  )[0];
  var display = panel.style.display;
  if (display == "none") {
    display = "block";
    button.style.backgroundColor = "#999999";
  } else {
    display = "none";
    button.style.backgroundColor = "#ffffff";
  }
  panel.style.display = display;
}

function getCellValueDiv(tabName) {
  return document.getElementById("cellvaluediv_" + tabName);
}

function getCellValueTextInput(tabName) {
  return document.getElementById("cellvaluetext_" + tabName);
}

function changeCellValueDivHeight(tabName, step) {
  var div = getCellValueTextInput(tabName);
  var divHeight = div.offsetHeight;
  divHeight = divHeight + 14 * step;
  if (divHeight < 18) {
    divHeight = 18;
  }
  div.style.height = divHeight + "px";
}

function makeVariantGeneTab(tabName, rightDiv) {
  var tableDiv = null;
  var cellValueDiv = null;
  var detailDiv = null;
  var detailContainerDiv = null;
  var contentDivId = "rightcontentdiv_" + tabName;
  var contentDiv = document.getElementById(contentDivId);
  if (contentDiv == null) {
    contentDiv = getEl("div");
    contentDiv.id = contentDivId;
    contentDiv.className = "rightcontentdiv flex flex-row";
    addEl(rightDiv, contentDiv);
  }
  // Table div
  var tableDivId = "tablediv_" + tabName;
  var tableDiv = document.getElementById(tableDivId);
  if (tableDiv == null) {
    tableDiv = getEl("div");
    tableDiv.id = tableDivId;
    tableDiv.className = "tablediv";
    addEl(contentDiv, tableDiv);
  }
  // Drag bar
  /*var northSouthDraggableDivId = "dragNorthSouthDiv_" + tabName;
  var northSouthDraggableDiv = document.getElementById(
    northSouthDraggableDivId
  );
  if (northSouthDraggableDiv == null) {
    northSouthDraggableDiv = getEl("div");
    northSouthDraggableDiv.id = northSouthDraggableDivId;
    northSouthDraggableDiv.className = "draggableDiv";
    //$(northSouthDraggableDiv).draggable({axis:"y"});
    addEl(contentDiv, northSouthDraggableDiv);
  }*/
  // Cell value div
  var cellValueDivId = "cellvaluediv_" + tabName;
  var cellValueDiv = document.getElementById(cellValueDivId);
  if (cellValueDiv == null) {
    cellValueDiv = getEl("div");
    cellValueDiv.id = cellValueDivId;
    cellValueDiv.className = "cellvaluediv";
    var h = loadedHeightSettings["cellvalue_" + currentTab];
    if (h != undefined) {
      cellValueDiv.style.height = h;
    }
    var input = getEl("textarea");
    input.id = "cellvaluetext_" + tabName;
    input.setAttribute("readonly", "true");
    input.rows = "1";
    addEl(cellValueDiv, input);
    /*var button = getEl("button");
    button.textContent = "+";
    button.addEventListener("click", function (_) {
      changeCellValueDivHeight(tabName, 1)
      setTableDetailLayout()
    });
    addEl(cellValueDiv, button);
    var button = getEl("button");
    button.textContent = "-";
    button.addEventListener("click", function (_) {
      changeCellValueDivHeight(tabName, -1)
      setTableDetailLayout()
    });
    addEl(cellValueDiv, button);*/
    addEl(contentDiv, cellValueDiv);
  }
  // Detail div
  var detailDivId = "detaildiv_" + tabName;
  var detailDiv = document.getElementById(detailDivId);
  if (detailDiv == null) {
    detailDiv = getEl("div");
    detailDiv.id = detailDivId;
    detailDiv.className = "detaildiv resultviewer xl:overflow-auto";
    addEl(contentDiv, detailDiv);
    var detailContainerWrapDiv = getEl("div");
    detailContainerWrapDiv.className = "detailcontainerwrapdiv";
    var h = loadedHeightSettings["detail_" + tabName];
    if (h != undefined) {
      detailDiv.style.height = h;
    }
    addEl(detailDiv, detailContainerWrapDiv);
    var detailContainerDivId = "detailcontainerdiv_" + tabName;
    detailContainerDiv = getEl("div");
    detailContainerDiv.id = detailContainerDivId;
    detailContainerDiv.className = "detailcontainerdiv";
    addEl(detailContainerWrapDiv, detailContainerDiv);
  }
}

function getTableDiv(tabName) {
  return document.getElementById("tablediv_" + tabName);
}

function getWidgetDiv(tabName) {
  return getDetailDiv(tabName).querySelector("#detailcontainerdiv_" + tabName);
}

function getDetailDiv(tabName) {
  return document.getElementById("detaildiv_" + tabName);
}

function setTableDetailLayout(tabName) {
  const [
    tableWidth,
    tableHeight,
    detailDivWidth,
    detailDivHeight,
    tableOn,
    detailOn,
  ] = getTableDetailWidthHeights(tabName);
  _ = tableWidth || detailDivWidth;
  const tableDiv = getTableDiv(tabName);
  const detailDiv = getDetailDiv(tabName);
  const cellValueDiv = getCellValueDiv(tabName);
  if (tableDiv) {
    if (tableOn) {
      tableDiv.classList.add("on");
      cellValueDiv.classList.add("on");
    } else {
      tableDiv.classList.remove("on");
      cellValueDiv.classList.remove("on");
    }
  }
  if (detailDiv) {
    if (detailOn) {
      detailDiv.classList.add("on");
    } else {
      detailDiv.classList.remove("on");
    }
  }
  if (tableDiv && tableOn) {
    tableDiv.style.width = tableWidth;
    tableDiv.style.height = tableHeight;
    cellValueDiv.style.width = tableWidth;
    $grids[tabName].pqGrid("option", "width", tableWidth);
    $grids[tabName].pqGrid("option", "height", tableHeight);
    setTimeout(function () {
      $grids[tabName].pqGrid("refresh");
    }, 100);
  }
  if (detailDiv && detailOn) {
    detailDiv.style.width = detailDivWidth;
    detailDiv.style.height = detailDivHeight;
    if (masons[tabName]) {
      masons[tabName].layout()
    }
    //new Packery(getWidgetDiv(tabName));
  }
}

function onClickDetailRedraw(tabName = currentTab) {
  var div = document.getElementById("detailcontainerdiv_" + tabName);
  $(div).packery();
}

function onClickDetailReset() {
  var tabName = currentTab;
  var div = document.getElementById("detailcontainerdiv_" + tabName);
  var widgets = div.children;
  for (var i = 0; i < widgets.length; i++) {
    var widget = widgets[i];
    var widgetName = widget.getAttribute("widgetkey");
    var generator = widgetGenerators[widgetName][currentTab];
    widget.style.top = "0px";
    widget.style.left = "0px";
    widget.style.width = generator["width"] + "px";
    widget.style.height = generator["height"] + "px";
  }
  $(div).packery();
}

function makeSampleMappingTab(tabName, rightDiv) {
  var tableDiv = getEl("div");
  tableDiv.id = "tablediv_" + tabName;
  tableDiv.className = "tablediv";
  addEl(rightDiv, tableDiv);
}

function populateWgNoticeDiv(noWgAnnotModules) {
  var contentDiv = document.getElementById("missing-widgets-div");
  if (Object.keys(noWgAnnotModules).length == 0) {
    $(contentDiv).empty();
    var span = getEl("span");
    span.className = "detailContent";
    span.textContent = "None";
    addEl(contentDiv, span);
    return;
  }
  emptyElement(contentDiv);
  var msg =
    "Your system does not have viwer widgets for the following annotator results are not installed in the system. ";
  msg +=
    "If you want to install viewer widgets for them, click the buttons for the annotators.";
  var span = getEl("span");
  span.className = "detailContent";
  addEl(contentDiv, addEl(span, getTn(msg)));
  addEl(contentDiv, getEl("br"));
  addEl(contentDiv, getEl("br"));
  var div = getEl("div");
  var moduleKeys = Object.keys(noWgAnnotModules);
  for (var i = 0; i < moduleKeys.length; i++) {
    var moduleKey = moduleKeys[i];
    var moduleTitle = noWgAnnotModules[moduleKey];
    var button = getEl("button");
    button.setAttribute("module", moduleKey);
    button.style.marginRight = "20px";
    button.style.marginBottom = "10px";
    button.textContent = moduleTitle;
    button.addEventListener("click", function (evt) {
      installWidgetsForModule(evt.target.getAttribute("module"));
    });
    addEl(div, button);
  }
  addEl(contentDiv, div);
}

function installWidgetsForModule(moduleKey) {
  $.get("/store/installwidgetsformodule", { name: moduleKey }).done(
    function () {
      checkWidgets();
    }
  );
}

function getInfoCardRow(key, val) {
  var valDiv = getEl("div");
  valDiv.className = "py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4";
  var dt = getEl("dt");
  dt.className = "text-sm font-medium text-gray-500";
  dt.textContent = key;
  var dd = getEl("dd");
  dd.className = "mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2";
  dd.textContent = val;
  addEl(valDiv, dt);
  addEl(valDiv, dd);
  return [valDiv, dt, dd];
}

function populateInfoDiv(infoDiv) {
  var div = getEl("div");
  div.className = "border-t border-gray-200";
  addEl(infoDiv, div);
  var dl = getEl("dl");
  dl.className = "sm:divide-y sm:divide-gray-200";
  addEl(div, dl);
  var [valDiv, _, _] = getInfoCardRow(
    "Job ID",
    uid || infomgr.jobinfo["job_id"] || "NA"
  );
  addEl(dl, valDiv);
  var keys = Object.keys(infomgr.jobinfo);
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];
    if (key == "job_id") {
      continue;
    }
    var val = infomgr.jobinfo[key];
    var [valDiv, _, _] = getInfoCardRow(key, val);
    addEl(dl, valDiv);
  }
  /*var [valDiv, _, dd] = getInfoCardRow("Missing widgets", "")
    dd.id = "missing-widgets-div"
    addEl(dl, valDiv)*/
}

function populateWidgetSelectorPanel() {
  var tabName = currentTab;
  var panelDiv = document.getElementById("widgets_showhide_select_div");
  panelDiv.innerHTML = "";
  panelDiv.style.maxHeight = "400px";
  panelDiv.style.overflow = "auto";
  panelDiv.style.cursor = "auto";

  var button = getEl("button");
  button.className = "butn ml-4 mb-2"
  button.textContent = "Redraw";
  button.addEventListener("click", function (_, _) {
    onClickDetailRedraw();
  });
  addEl(panelDiv, button);

  var button = getEl("button");
  button.className = "butn ml-2 mb-2"
  button.textContent = "Reset";
  button.addEventListener("click", function (_, _) {
    onClickDetailReset();
  });
  addEl(panelDiv, button);

  var button = getEl("button");
  button.className = "butn ml-2 mb-2"
  button.textContent = "Hide all";
  button.addEventListener("click", function (_, _) {
    changeWidgetShowHideAll(false);
  });
  addEl(panelDiv, button);

  var button = getEl("button");
  button.className = "butn ml-2 mb-2"
  button.textContent = "Show all";
  button.addEventListener("click", function (_, _) {
    changeWidgetShowHideAll(true);
  });
  addEl(panelDiv, button);

  var widgetNames = Object.keys(widgetGenerators);
  for (var i = 0; i < widgetNames.length; i++) {
    var widgetName = widgetNames[i];
    var generator = widgetGenerators[widgetName][tabName];
    if (
      generator != undefined &&
      generator["function"] != undefined &&
      usedAnnotators[tabName].includes(infomgr.widgetReq[widgetName])
    ) {
      var div = getEl("div");
      div.className = "pl-4"
      var label = getEl("label");
      label.classList.add("checkbox-container");
      var span = getEl("span")
      span.textContent = infomgr.colgroupkeytotitle[widgetName];
      addEl(label, span)
      var input = getEl("input");
      input.id = "widgettogglecheckbox_" + tabName + "_" + widgetName;
      input.type = "checkbox";
      var span = getEl("span");
      span.classList.add("checkmark");
      addEl(label, input);
      addEl(label, span);
      var vwsT = viewerWidgetSettings[tabName];
      if (vwsT == undefined) {
        vwsT = [];
        viewerWidgetSettings[tabName] = vwsT;
      }
      var vws = getViewerWidgetSettingByWidgetkey(tabName, widgetName);
      if (vws == null) {
        input.checked = true;
      } else {
        var display = vws["display"];
        if (display != "none") {
          input.checked = true;
        } else {
          input.checked = false;
        }
      }
      input.setAttribute("widgetname", widgetName);
      input.addEventListener("click", function (evt) {
        onClickWidgetSelectorCheckbox(tabName, evt);
      });
      addEl(div, label);
      if (
        generator["variables"] != undefined &&
        generator["variables"]["shoulddraw"] == false
      ) {
        input.disabled = "disabled";
        span.style.color = "gray";
      }
      addEl(panelDiv, div);
    }
  }
}

function onClickWidgetHelpButton(evt, _) {
  var widget = evt.target.parentElement.parentElement.parentElement;
  var widgetName = widget.getAttribute("widgetkey");
  var frame = getEl("iframe");
  frame.id = "widgethelpdiv";
  frame.src = "/result/widgetfile/wg" + widgetName + "/help.html";
  addEl(document.body, frame);
  frame.onload = function () {
    if (this.contentDocument) {
      var btn = getEl("span");
      btn.textContent = "\u274c";
      btn.style.position = "fixed";
      btn.style.top = "0";
      btn.style.right = "0";
      btn.style.cursor = "default";
      btn.addEventListener("click", function (_) {
        $("#widgethelpdiv").remove();
      });
      addEl(this.contentDocument.body, btn);
    } else {
      $(this).remove();
    }
  };
}

function onClickWidgetPinButton(evt, tabName) {
  var widget = evt.target.closest("fieldset");
  var button = evt.target;
  var pinned = button.classList.contains("pinned");
  if (pinned) {
    button.classList.remove("pinned");
    masons[tabName].unstamp(widget);
    //$(container).packery("unstamp", widget);
  } else {
    button.classList.add("pinned");
    masons[tabName].stamp(widget);
    //$(container).packery("stamp", widget);
  }
}

function onClickWidgetCloseButton(tabName, evt) {
  var widgetName = evt.target.closest("fieldset").getAttribute("widgetname");
  executeWidgetClose(widgetName, tabName, false);
}

function onClickWidgetDownloadButton(tabName, evt) {
  var widgetName = evt.target.closest("fiedlset").getAttribute("widgetname");
  var generator = widgetGenerators[widgetName][tabName];
  if (generator["exportdata"] != undefined) {
    var text = generator["exportdata"]();
    var b = new Blob([text], { type: "text/csv" });
    var u = window.URL.createObjectURL(b);
    var a = document.createElement("a");
    a.setAttribute("href", u);
    a.setAttribute("download", uid + "." + widgetName + ".csv");
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}

function onClickWidgetCameraButton(tabName, evt) {
  var widgetName = evt.target.closest("fieldset").getAttribute("widgetname");
  saveWidgetContent(widgetName, tabName);
}

function executeWidgetClose(widgetName, tabName, repack) {
  showHideWidget(tabName, widgetName, false, repack);
  var button = document.getElementById(
    "widgettogglecheckbox_" + tabName + "_" + widgetName
  );
  if (button != undefined) {
    button.checked = false;
  }
  onClickDetailRedraw();
}

function executeWidgetOpen(widgetName, tabName, repack) {
  showHideWidget(tabName, widgetName, true, repack);
  var button = document.getElementById(
    "widgettogglecheckbox_" + tabName + "_" + widgetName
  );
  if (button != undefined) {
    button.checked = true;
  }
  onClickDetailRedraw();
}

function grayOutWidgetSelect(widgetName, tabName) {
  var button = document.getElementById(
    "widgettogglecheckbox_" + tabName + "_" + widgetName
  );
  if (button != undefined) {
    button.disabled = "disabled";
    button.parentElement.style.color = "gray";
  }
}

function changeWidgetShowHideAll(checked) {
  var tabName = currentTab;
  var div = document.getElementById("detailcontainerdiv_" + tabName);
  var widgets = $(div).packery("getItemElements");
  for (var i = 0; i < widgets.length; i++) {
    var widget = widgets[i];
    var widgetName = widget.getAttribute("widgetkey");
    document.getElementById(
      "widgettogglecheckbox_" + tabName + "_" + widgetName
    ).checked = checked;
    showHideWidget(tabName, widgetName, checked, true);
  }
}

function onClickWidgetSelectorCheckbox(tabName, evt) {
  var button = evt.target;
  var checked = button.checked;
  var widgetName = button.getAttribute("widgetname");
  showHideWidget(tabName, widgetName, checked, true);
}

function showHideWidget(tabName, widgetName, state, repack) {
  var widget = document.getElementById(
    "detailwidget_" + tabName + "_" + widgetName
  );
  if (widget == null) {
    return;
  }
  var display = widget.style.display;
  if (state == false && display == "none") {
    return;
  } else if (state == true && display != "none") {
    return;
  }
  if (state == false) {
    widget.style.display = "none";
  } else {
    widget.style.display = "block";
    if (currentTab == "info") {
      var dcd = widget.getElementsByClassName("detailcontentdiv")[0];
      if (dcd.innerHTML == "") {
        drawSummaryWidget(widgetName);
      }
    }
  }
  var $detailContainerDiv = $(
    document.getElementById("detailcontainerdiv_" + tabName)
  );
  if (repack == true) {
    $detailContainerDiv.packery("fit", widget);
    onClickDetailReset();
  }
}

function drawSummaryWidgetGivenData(
  widgetName,
  widgetContentDiv,
  generator,
  data
) {
  try {
    if (generator["init"] != undefined) {
      generator["init"](data);
    }
    var shouldDraw = false;
    if (generator["shoulddraw"] != undefined) {
      shouldDraw = generator["shoulddraw"]();
    } else {
      shouldDraw = true;
    }
    if (generator["variables"] == undefined) {
      generator["variables"] = {};
    }
    generator["variables"]["shoulddraw"] = shouldDraw;
    if (shouldDraw) {
      generator["function"](widgetContentDiv, data);
    } else {
      setTimeout(function () {
        executeWidgetClose(widgetName, "info");
        grayOutWidgetSelect(widgetName, currentTab);
      }, 500);
    }
  } catch (e) {
    console.log(e);
  }
}

function drawSummaryWidget(widgetName) {
  var widgetContentDiv = document.getElementById(
    "widgetcontentdiv_" + widgetName + "_info"
  );
  emptyElement(widgetContentDiv);
  var generator = widgetGenerators[widgetName]["info"];
  var requestmethod = generator["requestmethod"];
  if (requestmethod != undefined && requestmethod.toLowerCase() == "post") {
    requestmethod = "POST";
  } else {
    requestmethod = "GET";
  }
  var callServer = generator["callserver"];
  if (callServer) {
    if (generator["beforecallserver"] != undefined) {
      generator["beforecallserver"]();
    }
    var callServerParams = {};
    if (generator["variables"]["callserverparams"] != undefined) {
      callServerParams = generator["variables"]["callserverparams"];
    }
    var spinner = getSpinner();
    spinner.className = "widgetspinner";
    addEl(widgetContentDiv, spinner);
    if (requestmethod == "POST") {
      var params = JSON.stringify(callServerParams);
      $.post(
        "/result/runwidget/" + widgetName,
        { username: username, uid: uid, dbpath: dbPath, params: params, ftable_uid: infomgr.ftable_uid },
        function (response) {
          var widgetContentDiv = document.getElementById(
            "widgetcontentdiv_" + widgetName + "_info"
          );
          var spinner =
            widgetContentDiv.getElementsByClassName("widgetspinner")[0];
          $(spinner).remove();
          var data = response["data"];
          drawSummaryWidgetGivenData(
            widgetName,
            widgetContentDiv,
            generator,
            data
          );
        }
      );
    } else {
      $.ajax({
        url: "/result/runwidget/" + widgetName,
        data: {
          username: username,
          uid: uid,
          dbpath: dbPath,
          params: JSON.stringify(callServerParams),
          ftable_uid: infomgr.ftable_uid,
        },
        async: true,
        method: requestmethod,
        success: function (response) {
          var widgetContentDiv = document.getElementById(
            "widgetcontentdiv_" + widgetName + "_info"
          );
          var spinner =
            widgetContentDiv.getElementsByClassName("widgetspinner")[0];
          $(spinner).remove();
          var data = response["data"];
          drawSummaryWidgetGivenData(
            widgetName,
            widgetContentDiv,
            generator,
            data
          );
        },
      });
    }
  } else {
    drawSummaryWidgetGivenData(
      widgetName,
      widgetContentDiv,
      generator,
      undefined
    );
  }
}

function addLeftPanelFieldSet(tabName, parent, fieldSetName) {
  var fieldSet = getEl("fieldset");
  var fieldSetId = fieldSetName.toLowerCase().replace(/ /g, "_");
  fieldSet.id = fieldSetId + "_fieldset_" + tabName;
  fieldSet.style.display = "block";
  var legend = getEl("legend");
  legend.className = "toggle_header_" + tabName;
  legend.style.cursor = "pointer";
  legend.style.fontSize = "14px";
  legend.style.fontWeight = "bold";
  addEl(legend, getTn(fieldSetName));
  var img = getEl("img");
  img.src = "/result/images/minus.png";
  img.style.width = "11px";
  img.style.height = "11px";
  addEl(legend, img);
  addEl(fieldSet, legend);
  var innerDiv = getEl("div");
  innerDiv.id = fieldSetId + "_innerdiv_" + tabName;
  innerDiv.className = "collapsible";
  addEl(fieldSet, innerDiv);
  addEl(parent, fieldSet);
}

function makeGrid(columns, data, tabName) {
  var tableDiv = getTableDiv(tabName);
  var $tableDiv = $(tableDiv);
  var gridObj = loadGridObject(columns, data, tabName, uid, "main");
  if (gridObj == undefined) {
    return;
  }
  gridObj.filterModel = { on: true, header: true, type: "local" };
  gridObj.headerCellClick = function (evt, _) {
    var $grid = $grids[tabName];
    var sortModel = $grid.pqGrid("option", "sortModel");
    if (evt.shiftKey) {
      sortModel.single = false;
    } else {
      sortModel.single = true;
    }
    $grid.pqGrid("option", "sortModel", sortModel);
  };
  // Creates the grid.
  try {
    $tableDiv.pqGrid("destroy");
  } catch (e) {}
  var $grid = $tableDiv.pqGrid(gridObj);
  $grids[tabName] = $grid;
  gridObjs[tabName] = gridObj;
  // Adds the footer.
  var footer = $grid.find(".pq-grid-footer")[0];
  var span = getEl("span");
  span.id = "footertext_" + tabName;
  var button = getEl("button");
  button.id = "exportbutton_" + tabName;
  button.style = "margin-left: 0.25rem;"
  button.onclick = function (_) {
    var a = getEl("a");
    var tsvContent = getExportContent(tabName);
    a.href = window.URL.createObjectURL(
      new Blob([tsvContent], { type: "text/tsv" })
    );
    a.download = uid + "_export_" + tabName + ".tsv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
  addEl(button, getTn("Export"));
  addEl(footer, span);
  addEl(footer, button);
  var prevBtn = getEl("button");
  prevBtn.id = "prev-page-btn_" + tabName;
  prevBtn.style = "margin-left: 0.25rem; background-color: #c1c1c1;"
  addEl(prevBtn, getTn("Prev"));
  prevBtn.onclick = async function (_) {
    pageNos[tabName] -= 1;
    if (pageNos[tabName] >= 1) {
      updatePageNoS();
      loadTableDataOnly();
    }
  };
  addEl(footer, prevBtn);
  var label = getEl("span");
  label.style = "margin-left: 0.25rem;"
  label.textContent = "Page";
  addEl(footer, label);
  var pageNoInput = getEl("input");
  pageNoInput.style = "margin-left: 0.25rem;"
  pageNoInput.id = "page-no-input_" + tabName;
  pageNoInput.type = "text";
  pageNoInput.size = "4";
  pageNoInput.value = pageNos[tabName];
  pageNoInput.addEventListener("keyup", async function (evt) {
    if (evt.key == "Enter") {
      loadTableDataOnly();
    }
  });
  addEl(footer, pageNoInput);
  var nextBtn = getEl("button");
  nextBtn.id = "next-page-btn_" + tabName;
  nextBtn.style = "margin-left: 0.25rem; background-color: #c1c1c1;"
  addEl(nextBtn, getTn("Next"));
  nextBtn.onclick = async function (_) {
    pageNos[tabName] += 1;
    updatePageNoS();
    loadTableDataOnly();
  };
  addEl(footer, nextBtn);
  var pageInput = getEl("input");
  pageInput.id = "page-input";
  pageInput.style = "margin-left: 0.25rem;"
  pageInput.type = "text";
  pageInput.size = "6";
  pageInput.value = pageSize;
  pageInput.addEventListener("keyup", async function (evt) {
    if (evt.key == "Enter") {
      pageNos[tabName] = 1;
      updatePageNoS();
      loadTableDataOnly();
    }
  });
  addEl(footer, pageInput);
  var label = getEl("span");
  label.textContent = "rows per page";
  addEl(footer, label);
  updateTableFooterTotalRows(tabName);
}

function updateTableFooterTotalRows(tabName) {
  var lenStr = infomgr.getData(tabName).length + " total rows";
  document.getElementById("footertext_" + tabName).textContent = lenStr;
}

function updatePageNoS() {
  var span = document.getElementById("page-no-input_" + currentTab);
  span.value = pageNos[currentTab];
}

function emptyElement(elem) {
  if (elem == null) {
    return;
  }
  var last = null;
  while ((last = elem.lastChild)) {
    elem.removeChild(last);
  }
}

function getFilterCol(columnKey) {
  for (var i = 0; i < filterCols.length; i++) {
    var colModel = filterCols[i].colModel;
    for (var j = 0; j < colModel.length; j++) {
      var column = colModel[j];
      if (column.col == columnKey) {
        return column;
      }
    }
  }
  return null;
}

function getLoadSelectorDiv(_) {
  var div = getEl("div");
  var selector = getEl("select");
  selector.id = "filterselect";
  selector.className = "inlineselect";
  var option = new Option("Choose a column to filter", "none");
  selector.options.add(option);
  for (var i = 0; i < filterCols.length; i++) {
    var filterCol = filterCols[i];
    var colModel = filterCol.colModel;
    for (var j = 0; j < colModel.length; j++) {
      var column = colModel[j];
      if (column.retfilt == true) {
        option = new Option(column.colgroup + " | " + column.title, column.col);
        selector.options.add(option);
      }
    }
  }
  selector.onchange = function (_) {
    onChangeFilterSelector(null, null, null, null);
  };
  addEl(div, selector);
  var selectDetailDiv = getEl("div");
  selectDetailDiv.id = "selectdetaildiv";
  selectDetailDiv.style.display = "inline-block";
  addEl(div, selectDetailDiv);
  return div;
}

function populateTableColumnSelectorPanel() {
  var tabName = currentTab;
  var wholeDiv = document.getElementById("columns_showhide_select_div");
  wholeDiv.style.top = "-100px"
  wholeDiv.innerHTML = "";
  var columnGroupsForTab = infomgr.getColumnGroups(tabName);
  var columnGroupNames = Object.keys(columnGroupsForTab);
  var columns = infomgr.getColumns(tabName);
  for (var i = 0; i < columnGroupNames.length; i++) {
    var columnGroupName = columnGroupNames[i];
    var columnGroupColumnKeys = columnGroupsForTab[columnGroupName];
    // Group div
    var groupDiv = document.createElement("fieldset");
    groupDiv.id =
      columnGroupPrefix + "_" + tabName + "_" + columnGroupName + "_id";
    groupDiv.className = "columngroup-control-box pl-4";
    var label = getEl("label");
    label.className = "checkbox-container"
    var span = getEl("span")
    span.textContent = infomgr.colgroupkeytotitle[columnGroupName];
    addEl(label, span)
    var checkbox = getEl("input");
    checkbox.id =
      columnGroupPrefix +
      "_" +
      tabName +
      "_" +
      columnGroupName +
      "_" +
      "_checkbox";
    checkbox.type = "checkbox";
    checkbox.checked = true;
    checkbox.setAttribute("colgroupno", i);
    checkbox.setAttribute("colgroupname", columnGroupName);
    checkbox.addEventListener("change", function (_, _) {
      var checkboxes =
        this.parentElement.parentElement.getElementsByClassName("colcheckbox");
      var checked = this.checked;
      for (var i = 0; i < checkboxes.length; i++) {
        var checkbox = checkboxes[i];
        checkbox.checked = checked;
      }
      updateTableColumns(tabName);
    });
    var span = getEl("span");
    span.className = "checkmark";
    addEl(label, checkbox);
    addEl(label, span);
    addEl(groupDiv, label);

    // Columns
    var columnsDiv = document.createElement("div");
    for (
      var columnKeyNo = 0;
      columnKeyNo < columnGroupColumnKeys.length;
      columnKeyNo++
    ) {
      var columnKey = columnGroupColumnKeys[columnKeyNo];
      var column = columns[infomgr.getColumnNo(tabName, columnKey)];
      if (column == undefined) {
        continue;
      }
      var label = getEl("label");
      label.classList.add("checkbox-container");
      label.classList.add("layout-change-button-sublevel");
      var span = getEl("span")
      span.textContent = column.title;
      addEl(label, span)
      var checkbox = getEl("input");
      checkbox.id =
        columnGroupPrefix +
        "_" +
        tabName +
        "_" +
        column.col +
        "_" +
        "_checkbox";
      checkbox.className = "colcheckbox";
      checkbox.type = "checkbox";
      checkbox.checked = !column.hidden;
      checkbox.setAttribute("colgroupname", columnGroupName);
      checkbox.setAttribute("col", column.col);
      checkbox.setAttribute("colno", columnKeyNo);
      checkbox.addEventListener("change", function (evt, _) {
        var chkbx = evt.target;
        var chkbxSdiv = chkbx.parentElement.parentElement;
        var grpChkbx = chkbxSdiv.parentElement;
        var clickPresence = false;
        Array.from(chkbxSdiv.getElementsByClassName("colcheckbox")).forEach(
          function (e) {
            if (e.checked) {
              clickPresence = true;
            }
          }
        );
        grpChkbx.querySelector("label input").checked = clickPresence;
        updateTableColumns(tabName);
      });
      var span = getEl("span");
      span.className = "checkmark";
      addEl(label, checkbox);
      addEl(label, span);
      addEl(columnsDiv, label);
    }
    addEl(groupDiv, columnsDiv);
    addEl(wholeDiv, groupDiv);
  }
  makeColgroupkeysWithMissingCols();
}

function makeColgroupkeysWithMissingCols() {
  colgroupkeysWithMissingCols = [];
  var flds = document.querySelectorAll("fieldset.columngroup-control-box");
  for (var i = 0; i < flds.length; i++) {
    var fld = flds[i];
    var colgroupkey = fld
      .querySelector("label input")
      .getAttribute("colgroupname");
    var anyColMissing = false;
    var inputs = fld.querySelectorAll("div input");
    for (var j = 0; j < inputs.length; j++) {
      if (inputs[j].checked == false) {
        anyColMissing = true;
        break;
      }
    }
    if (anyColMissing) {
      colgroupkeysWithMissingCols.push(colgroupkey);
    }
  }
}

function updateTableColumns(tabName) {
  var selectorPanel = document.getElementById("columns_showhide_select_div");
  var checkboxes = selectorPanel.getElementsByClassName("colcheckbox");
  var colModel = $grids[tabName].pqGrid("option", "colModel");
  for (var i = 0; i < checkboxes.length; i++) {
    var checkbox = checkboxes[i];
    var colgroupname = checkbox.getAttribute("colgroupname");
    var colkey = checkbox.getAttribute("col");
    var checked = !checkbox.checked;
    for (var j = 0; j < colModel.length; j++) {
      var cols = colModel[j].colModel;
      for (var k = 0; k < cols.length; k++) {
        var col = cols[k];
        if (col.colgroupkey == colgroupname && col.col == colkey) {
          cols[k].hidden = checked;
          break;
        }
      }
    }
  }
  makeColgroupkeysWithMissingCols();
  $grids[tabName].pqGrid("option", "colModel", colModel).pqGrid("refresh");
}

function pickThroughAndChangeCursorClasses(
  domElement,
  classToSkip,
  classToAdd
) {
  var classNames = domElement.className;
  var arrayClasses = classNames.split(" ");
  var newArrayClassNames = [];
  for (var i = 0; i < arrayClasses.length; i++) {
    if (arrayClasses[i] != classToSkip) {
      newArrayClassNames.push(arrayClasses[i]);
    }
  }
  newArrayClassNames.push(classToAdd);
  domElement.className = newArrayClassNames.join(" ");
}

function getTableDetailWidthHeights(tabName) {
  const tableDiv = getTableDiv(tabName);
  const detailDiv = getDetailDiv(tabName);
  const tableToggleBtn = getTableToggleBtn();
  const detailToggleBtn = getDetailToggleBtn();
  var cellValueDivHeight = 60;
  const heightMargin = 20;
  const winWidth = window.innerWidth - 50;
  const winHeight = window.innerHeight;
  // sidebar 9rem=144px (w-36)
  const sidebarWidth = 144;
  var detailDivWidth = defaultDetailDivWidth;
  var tableWidth = winWidth - sidebarWidth - detailDivWidth;
  const tableOn = tableToggleBtn.classList.contains("on");
  const detailOn = detailToggleBtn.classList.contains("on");
  if (tableDiv && tableOn) {
    if (detailOn) {
      tableWidth = winWidth - sidebarWidth - detailDivWidth;
    } else {
      tableWidth = winWidth - sidebarWidth;
    }
  } else {
    if (detailDiv && detailOn) {
      detailDivWidth = winWidth - sidebarWidth;
    } else {
      tableWidth = winWidth - sidebarWidth - detailDivWidth;
    }
  }
  const tableHeight = winHeight - heightMargin - cellValueDivHeight;
  const detailDivHeight = winHeight - 10;
  return [
    tableWidth,
    tableHeight,
    detailDivWidth,
    detailDivHeight,
    tableOn,
    detailOn,
  ];
}

function loadGridObject(_, data, tabName, tableTitle, _) {
  var rightDiv = document.getElementById("rightdiv_" + tabName);
  if (rightDiv == null) {
    return;
  }
  var [_, tableHeight, _, _, _, _] = getTableDetailWidthHeights(tabName);
  var gridObject = new Object();
  gridObject.title = tableTitle;
  gridObject.height = tableHeight;
  gridObject.virtualX = true;
  gridObject.virtualY = true;
  gridObject.wrap = false;
  gridObject.hwrap = false;
  gridObject.sortable = true;
  gridObject.numberCell = { show: false };
  gridObject.showTitle = false;
  gridObject.selectionModel = { type: "cell", mode: "block" };
  gridObject.hoverMode = "cell";
  gridObject.colModel = infomgr.getColModel(tabName);
  gridObject.dataModel = { data: Array.from(data) };
  if (tabName == "variant") {
    gridObject.freezeCols = 5;
  }
  var sortColumnToUse = "input_line_number";
  gridObject.sortModel = {
    cancel: true,
    on: true,
    type: "local",
    single: true,
    number: true,
    sorter: [
      { dataIndx: infomgr.getColumnNo(tabName, sortColumnToUse), dir: "up" },
    ],
  };
  gridObject.selectChange = function (_, ui) {
    var clickInfo = ui.selection["_areas"][0];
    var rowNo = clickInfo["r1"];
    var colNo = clickInfo["c1"];
    var rowData = $grids[tabName].pqGrid("getData")[rowNo];
    var cell = $grids[tabName].pqGrid("getCell", {
      rowIndx: rowNo,
      colIndx: colNo,
    })[0];
    var cellData = null;
    if (cell == undefined) {
      // fallback for initial open of a tab
      cellData = rowData[colNo];
    } else {
      cellData = cell.textContent;
    }
    var valueText = null;
    if (cellData == undefined || cellData == "" || cellData == null) {
      valueText = "";
    } else {
      valueText = cellData;
    }
    var celltextel = document.getElementById("cellvaluetext_" + tabName);
    if (celltextel) {
      celltextel.value = valueText;
    }
    if (selectedRowNos[tabName] != undefined) {
      var row = $grids[tabName].pqGrid("getRow", {
        rowIndxPage: selectedRowNos[tabName],
      });
      row.css("background-color", "white");
    }
    var row = $grids[tabName].pqGrid("getRow", { rowIndxPage: rowNo });
    row.css("background-color", tableHightlighBackgroundColor);
    if (rowData != undefined) {
      if (
        selectedRowIds[tabName] == null ||
        selectedRowIds[tabName] != rowData[0]
      ) {
        selectedRowIds[tabName] = rowData[0];
        selectedRowNos[tabName] = rowNo;
        showVariantDetail(rowData, tabName);
      }
    }
  };
  gridObject.beforeSort = function (evt, ui) {
    if (evt.shiftKey) {
      ascendingSort = {};
      for (var i = 0; i < ui.sorter.length; i++) {
        var sorter = ui.sorter[i];
        ascendingSort[sorter.dataIndx] = sorter.dir == "up";
      }
    } else {
      ui.sorter = [ui.sorter[ui.sorter.length - 1]];
      gridObject.sortModel.sorter = ui.sorter;
      if (ui.sorter[0] != undefined) {
        var sorter = ui.sorter[0];
        ascendingSort = {};
        ascendingSort[sorter.dataIndx] = sorter.dir == "up";
      }
    }
  };
  gridObject.sortDir = "up";
  gridObject.options = {
    showBottom: true,
    dragColumns: { enabled: false },
  };
  gridObject.filter = function () {
    this.scrollRow({ rowIndxPage: 0 });
  };
  gridObject.collapsible = { on: false, toggle: false };
  gridObject.roundCorners = false;
  gridObject.stripeRows = true;
  gridObject.cellDblClick = function (_, _) {};
  gridObject.columnOrder = function (_, _) {};
  gridObject.refresh = function (_, ui) {
    var selRowNo = selectedRowNos[tabName];
    if (selRowNo >= ui.initV && selRowNo <= ui.finalV) {
      var row = $grids[tabName].pqGrid("getRow", { rowIndxPage: selRowNo });
      row.css("background-color", tableHightlighBackgroundColor);
    }
  };
  gridObject.refreshHeader = function (_, _) {
    var colModel = null;
    if ($grids[currentTab] == undefined) {
      colModel = this.colModel;
    } else {
      colModel = $grids[currentTab].pqGrid("getColModel");
    }
    var $groupHeaderTr = $(
      $("#tab_" + currentTab + " tr.pq-grid-title-row")[0]
    );
    for (let i = 0; i < colModel.length; i++) {
      var col = colModel[i];
      var $headerCell = this.getCellHeader({ colIndx: col.leftPos });
      if ($headerCell.length == 0) {
        continue;
      }
      var desc = null;
      if (col.desc !== null) {
        desc = col.title + ": " + col.desc;
      } else {
        var colTitleLimit = 30;
        if (col.title.length > colTitleLimit) {
          $headerCell.text(col.title.substring(0, colTitleLimit) + "..");
          if (col.desc != null && col.desc != col.title) {
            desc = col.title + ": " + col.desc;
          } else {
            desc = col.title;
          }
        } else {
          desc = col.title;
        }
      }
      $headerCell.attr("title", desc).tooltip();
      $headerCell.attr("col", col.col);
      $headerCell.attr("coltitle", col.title);
      $headerCell.attr("colgroup", col.colgroup);
      $headerCell.attr("colgroupkey", col.colgroupkey);
      $headerCell[0].classList.remove("pq-align-right");
      $headerCell[0].classList.remove("pq-align-left");
      $headerCell[0].classList.add("pq-align-center");
      $headerCell.contextmenu(function (evt) {
        var headerCell = evt.target;
        if (headerCell.classList.contains("pq-td-div")) {
          headerCell = headerCell.parentElement;
        }
        var col = headerCell.getAttribute("col");
        var colgroupkey = headerCell.getAttribute("colgroupkey");
        makeTableHeaderRightClickMenu(evt, col, colgroupkey);
        return false;
      });
    }
    var $groupHeaderTds = $groupHeaderTr.children();
    for (var i = 0; i < $groupHeaderTds.length; i++) {
      var th = $groupHeaderTds[i];
      var title = $(th).children("div").text();
      var colgroupkey = infomgr.colgrouptitletokey[title];
      var desc = infomgr.modulesInfo[currentTab][colgroupkey];
      if (desc != undefined) {
        $(th).attr("title", desc).tooltip();
      }
      th.setAttribute("colgrouptitle", title);
      th.setAttribute("colgroupkey", colgroupkey);
      th.style.position = "relative";
      th.style.cursor = "default";
      $(th).children("div.pq-td-div").css("cursor", "default");
      $(th).contextmenu(function (evt) {
        var th = evt.target;
        if (th.tagName == "DIV") {
          th = th.parentElement;
        }
        var title = th.getAttribute("colgrouptitle");
        var colgroupkey = th.getAttribute("colgroupkey");
        makeTableGroupHeaderRightClickMenu(evt, th, title, colgroupkey);
        return false;
      });
      var signClassName = "module-header-plus-sign";
      $(th).children(signClassName).remove();
      var span = getEl("span");
      span.className = signClassName;
      span.style.fontSize = "7px";
      if (colgroupkeysWithMissingCols.indexOf(colgroupkey) >= 0) {
        span.textContent = "\u2795";
        span.addEventListener("click", function (evt) {
          var th = evt.target.parentElement;
          var colgroupkey = th.getAttribute("colgroupkey");
          var checkboxId =
            "columngroup__" + currentTab + "_" + colgroupkey + "__checkbox";
          var checkbox = document.getElementById(checkboxId);
          checkbox.click();
          checkbox.click();
        });
      } else {
        if (
          infomgr.colgroupdefaulthiddenexist[currentTab][colgroupkey] == true
        ) {
          span.textContent = "\u2796";
          span.addEventListener("click", function (evt) {
            var th = evt.target.parentElement;
            var colgroupkey = th.getAttribute("colgroupkey");
            var checkboxId =
              "columngroup__" + currentTab + "_" + colgroupkey + "__checkbox";
            var checkbox = document.getElementById(checkboxId);
            checkbox.click();
            checkbox.click();
            var colModel = $grids[currentTab].pqGrid("option", "colModel");
            for (var i = 0; i < colModel.length; i++) {
              if (colModel[i].name == colgroupkey) {
                var colDefs = colModel[i].colModel;
                for (var j = 0; j < colDefs.length; j++) {
                  var checkboxid =
                    "columngroup__" +
                    currentTab +
                    "_" +
                    colDefs[j].col +
                    "__checkbox";
                  document.getElementById(checkboxid).checked =
                    colDefs[j].default_hidden == false;
                }
              }
            }
            updateTableColumns(currentTab);
          });
        }
      }
      addEl(th, span);
    }
  };
  gridObject.columnDrag = function (_, ui) {
    var colGroups = $grids[currentTab].pqGrid("option", "colModel");
    var colLevel = null;
    if (ui.column.parent == undefined) {
      colLevel = "group";
    } else {
      colLevel = "column";
    }
    var uiColGroup = ui.column.colgroup;
    for (var i = 0; i < colGroups.length; i++) {
      var colGroup = colGroups[i];
      var sameColGroup = uiColGroup == colGroup.pqtitle;
      if (colLevel == "column") {
        colGroup.nodrop = true;
      } else if (colLevel == "group") {
        colGroup.nodrop = false;
      }
      var cols = colGroup.colModel;
      for (var j = 0; j < cols.length; j++) {
        var col = cols[j];
        if (colLevel == "group") {
          col.nodrop = true;
        } else if (colLevel == "column") {
          if (sameColGroup) {
            col.nodrop = false;
          } else {
            col.nodrop = true;
          }
        }
      }
    }
  };
  gridObject.flex = { on: true, all: false };
  return gridObject;
}

function makeTableGroupHeaderRightClickMenu(
  evt,
  _,
  colgrouptitle,
  colgroupkey
) {
  var rightDiv = document.getElementById("tablediv_" + currentTab);
  var divId = "table-header-contextmenu-" + currentTab;
  var div = document.getElementById(divId);
  if (div == undefined) {
    div = getEl("div");
    div.id = divId;
    div.className = "table-header-contextmenu-div";
  } else {
    $(div).empty();
  }
  div.style.top = evt.pageY;
  div.style.left = evt.pageX;
  var ul = getEl("ul");
  var li = getEl("li");
  li.setAttribute("colgroupkey", colgroupkey);
  var a = getEl("a");
  a.setAttribute("colgroupkey", colgroupkey);
  a.textContent = "Show all columns of " + colgrouptitle;
  li.addEventListener("click", function (evt) {
    var colgroupkey = evt.target.getAttribute("colgroupkey");
    var checkboxId =
      columnGroupPrefix + "_" + currentTab + "_" + colgroupkey + "__checkbox";
    var checkbox = document.getElementById(checkboxId);
    checkbox.click();
    checkbox.click();
    div.style.display = "none";
  });
  addEl(ul, addEl(li, a));
  var li = getEl("li");
  li.setAttribute("colgroupkey", colgroupkey);
  var a = getEl("a");
  a.setAttribute("colgroupkey", colgroupkey);
  a.textContent = "Show default columns of " + colgrouptitle;
  li.addEventListener("click", function (evt) {
    var colgroupkey = evt.target.getAttribute("colgroupkey");
    var checkboxId =
      columnGroupPrefix + "_" + currentTab + "_" + colgroupkey + "__checkbox";
    var checkbox = document.getElementById(checkboxId);
    checkbox.click();
    checkbox.click();
    var colModel = $grids[currentTab].pqGrid("option", "colModel");
    for (var i = 0; i < colModel.length; i++) {
      if (colModel[i].name == colgroupkey) {
        var colDefs = colModel[i].colModel;
        for (var j = 0; j < colDefs.length; j++) {
          document.getElementById(
            "columngroup__" + currentTab + "_" + colDefs[j].col + "__checkbox"
          ).checked = colDefs[j].default_hidden == false;
        }
      }
    }
    updateTableColumns(currentTab);
    div.style.display = "none";
  });
  addEl(ul, addEl(li, a));
  var li = getEl("li");
  li.setAttribute("colgroupkey", colgroupkey);
  var a = getEl("a");
  a.setAttribute("colgroupkey", colgroupkey);
  a.textContent = "Hide all columns of " + colgrouptitle;
  li.addEventListener("click", function (evt) {
    var colgroupkey = evt.target.getAttribute("colgroupkey");
    var checkboxId =
      columnGroupPrefix + "_" + currentTab + "_" + colgroupkey + "__checkbox";
    var checkbox = document.getElementById(checkboxId);
    checkbox.click();
    div.style.display = "none";
  });
  addEl(ul, addEl(li, a));
  addEl(div, ul);
  div.style.display = "block";
  addEl(rightDiv, div);
}

function makeTableHeaderRightClickMenu(evt, col) {
  var rightDiv = document.getElementById("tablediv_" + currentTab);
  var divId = "table-header-contextmenu-" + currentTab;
  var div = document.getElementById(divId);
  if (div == undefined) {
    div = getEl("div");
    div.id = divId;
    div.className = "table-header-contextmenu-div";
  } else {
    $(div).empty();
  }
  div.style.top = evt.pageY;
  div.style.left = evt.pageX;
  var ul = getEl("ul");
  var li = getEl("li");
  var a = getEl("a");
  a.textContent = "Hide column";
  li.addEventListener("click", function (_) {
    var checkboxId =
      columnGroupPrefix + "_" + currentTab + "_" + col + "__checkbox";
    var checkbox = document.getElementById(checkboxId);
    checkbox.click();
    div.style.display = "none";
  });
  addEl(ul, addEl(li, a));
  addEl(div, ul);
  div.style.display = "block";
  addEl(rightDiv, div);
}

function applyTableDetailDivSizes() {
  var tabName = currentTab;
  var tableDiv = document.getElementById("tablediv_" + tabName);
  var detailDiv = document.getElementById("detaildiv_" + tabName);
  var detailContainerDiv = document.getElementById(
    "detailcontainerdiv_" + tabName
  );
  var cell = getCellValueDiv(tabName);
  var stat = tableDetailDivSizes[tabName]["status"];
  if (stat == "tablemax") {
    detailDiv.style.display = "none";
    cell.style.display = "none";
    tableDiv.style.display = "block";
    $grids[tabName].pqGrid("refresh");
  } else if (stat == "detailmax") {
    tableDiv.style.display = "none";
    cell.style.display = "none";
    detailDiv.style.display = "block";
    $(detailContainerDiv).packery();
  } else if (stat == "both") {
    tableDiv.style.display = "block";
    detailDiv.style.display = "block";
    cell.style.display = "block";
    $grids[tabName].pqGrid("refresh");
  }
}

function getTableToggleBtn() {
  return document.getElementById("tabletogglebtn");
}

function getDetailToggleBtn() {
  return document.getElementById("detailtogglebtn");
}

function onClickTableToggleBtn() {
  var a = getTableToggleBtn();
  if (a.classList.contains("on")) {
    a.classList.remove("on");
  } else {
    a.classList.add("on");
  }
  setTableDetailLayout(currentTab);
}

function onClickDetailToggleBtn() {
  var a = getDetailToggleBtn();
  if (a.classList.contains("on")) {
    a.classList.remove("on");
  } else {
    a.classList.add("on");
  }
  setTableDetailLayout(currentTab);
}

function saveWidgetContent(widgetName, tabName) {
  var loadingDiv = drawingWidgetCaptureSpinnerDiv();
  var div = document.getElementById(
    "widgetcontentdiv_" + widgetName + "_" + tabName
  );
  var divToCapture = div;
  if (divToCapture.childNodes.length == 1) {
    divToCapture = divToCapture.childNodes[0];
  }
  var divW = div.scrollWidth;
  var divH = div.scrollHeight;
  // Table rows are taller than original somehow.
  var trs = div.getElementsByTagName("tr");
  if (trs.length > 0) {
    divH = divH * 3;
  }
  if (divW < divToCapture.scrollWidth) {
    divW = divToCapture.scrollWidth;
  }
  // 7480 is 1000 dpi double-column pixel size from
  // https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
  var maxWorH = 7480;
  var ratioW = maxWorH / divW;
  var ratioH = maxWorH / divH;
  var minRatio = Math.min(ratioW, ratioH);
  domtoimage
    .toSvg(divToCapture, { width: divW, height: divH })
    .then(function (response) {
      var img = new Image();
      img.src = response;
      img.onload = function () {
        var canvas = getEl("canvas");
        canvas.width = divW * minRatio;
        canvas.height = divH * minRatio;
        ctx = canvas.getContext("2d");
        ctx.scale(minRatio, minRatio);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        var dataUrl = canvas.toDataURL("image/png");
        download(
          dataUrl,
          uid + "_" + tabName + "_" + widgetName + ".png",
          "image/png"
        );
        loadingDiv.parentNode.removeChild(loadingDiv);
      };
    });
}

function showInfonoticediv() {
  document.getElementById("infonoticediv").classList.add("show");
  //document.getElementById("infonoticediv").classList.remove("hide");
}

function hideInfonoticediv() {
  document.getElementById("infonoticediv").classList.remove("show");
  //document.getElementById("infonoticediv").classList.add("hide");
}

function addTextToInfonoticediv(lines) {
  if (lines == undefined) {
    return;
  }
  var div = document.getElementById("infonoticediv");
  for (var i = 0; i < lines.length; i++) {
    var span = getEl("li");
    span.textContent = lines[i];
    addEl(div, span);
  }
  if (lines.length > 0) {
    //showInfonoticediv();
  }
}

function updatePageNoInput() {
  var div = document.getElementById("page-no-input");
  if (div != null) {
    div.textContent = pageNos[currentTab];
  }
}
