adminMode = false;
noRemDays = null;

function openSubmitPage() {
  location.href =
    location.protocol +
    "//" +
    window.location.host +
    "/submit/nocache/index.html";
}

function openLoginPage() {
  location.href =
    location.protocol +
    "//" +
    window.location.host +
    "/server/nocache/login.html";
}

function loginInternal() {
  var email = document.getElementById("email").value;
  var password = document.getElementById("password").value;
  axios
    .get("/server/login", {
      headers: {
        Authorization: "Basic " + btoa(email + ":" + password),
      },
    })
    .then(function (res) {
      data = res.data;
      if (data.startsWith("guestsuccess_")) {
        openSubmitPage();
      } else if (data == "success") {
        username = res["email"];
        openSubmitPage();
      } else if (data == "fail") {
        msgAccountDiv("Login failed");
      }
    })
    .catch(function (err) {
      console.error("error with login:", err);
    });
  return false;
}

function getSignInBtn() {
  return document.getElementById("signin_btn")
}

function getSignInSpinner() {
  return document.getElementById("signin_spinner")
}

function showSpinnerOnSignInBtn() {
  getSignInSpinner().classList.remove("hide")
}

function hideSpinnerOnSignInBtn() {
  getSignInSpinner().classList.add("hide")
}

function getEmail() {
  var div = document.getElementById("email")
  if (div != null) {
    return div.value
  } else {
    return username
  }
}

function sendPasswordResetEmail() {
  var email = getEmail()
  firebase.auth().sendPasswordResetEmail(email)
  .then(function(_) {
    alert("Check your inbox for a password reset link.")
  })
  .catch(function(err) {
    alert(err)
  })
}

function logout() {
  axios.get("/server/logout")
  .then(function(res) {
    if (res.data.status == "success") {
      openLoginPage()
    }
  }).catch(function(err) {
    console.error(err)
  })
}

function getPasswordQuestion() {
  var email = document.getElementById("forgotpasswordemail").value;
  $.ajax({
    url: "/server/passwordquestion",
    data: { email: email },
    success: function (response) {
      var status = response["status"];
      var msg = response["msg"];
      if (status == "fail") {
        msgAccountDiv(msg);
      } else {
        document.getElementById("forgotpasswordgetquestiondiv").style.display =
          "none";
        document.getElementById("forgotpasswordquestion").textContent = msg;
        document.getElementById(
          "forgotpasswordquestionanswerdiv"
        ).style.display = "block";
      }
    },
  });
}

function showSignupDiv() {
  document.getElementById("logindiv").style.display = "none";
  document.getElementById("signupdiv").style.display = "block";
}

function showLoginDiv() {
  document.getElementById("logindiv").style.display = "block";
  document.getElementById("signupdiv").style.display = "none";
  document.getElementById("forgotpassworddiv").style.display = "none";
}

function hideloginsignupdiv() {
  document.getElementById("loginsignupdialog").style.display = "none";
}

function toggleloginsignupdiv() {
  document.getElementById("logindiv").style.display = "block";
  document.getElementById("signupdiv").style.display = "none";
  var dialog = document.getElementById("loginsignupdialog");
  var display = dialog.style.display;
  if (display == "none") {
    display = "block";
  } else {
    display = "none";
  }
  dialog.style.display = display;
}

function signupSubmit() {
  var username = document.getElementById("email").value.trim();
  var password = document.getElementById("password").value.trim();
  processSignup(username, password, password, "q", "a");
}

function processSignup(username, password, retypepassword, question, answer) {
  if (
    !username.match(/^\S+@\S+\.\S+$/) &&
    username != "admin" &&
    !username.includes("guest_")
  ) {
    msgAccountDiv("Invalid email.");
    return;
  }
  if (password == "") {
    msgAccountDiv("Password is empty.");
    return;
  }
  if (retypepassword == "") {
    msgAccountDiv("Re-typed password is empty.");
    return;
  }
  if (question == "") {
    msgAccountDiv("Question is empty.");
    return;
  }
  if (answer == "") {
    msgAccountDiv("Answer is empty.");
    return;
  }
  if (password != retypepassword) {
    msgAccountDiv("Password mismatch");
    return;
  }
  axios
    .get("/server/signup", {
      params: {
        username: username,
        password: password,
        question: question,
        answer: answer,
      },
    })
    .then(function (_) {
    });
}

async function checkLogged(inUsername) {
  var res = await axios.get("/server/checklogged", { params: { username: inUsername } })
  var data = res.data
  logged = data["logged"]
  if (logged == true) {
    username = data["email"]
    adminMode = data["admin"]
    return true
  } else {
    username = null
    adminMode = null
    return false
  }
}

function showUnloggedControl() {
  openLoginPage();
}

function getDateStr(d) {
  var year = d.getFullYear();
  var month = d.getMonth() + 1;
  if (month < 10) {
    month = "0" + month;
  } else {
    month = "" + month;
  }
  var day = d.getDate();
  if (day < 10) {
    day = "0" + day;
  } else {
    day = "" + day;
  }
  var datestr = year + "-" + month + "-" + day;
  return datestr;
}

function populateAdminTab() {
  var div = document.getElementById("admindiv");
  // date range
  var sdiv = getEl("div");
  sdiv.className = "adminsection-div";
  var span = getEl("span");
  span.className = "adminsection-title";
  span.textContent = "Date range";
  addEl(sdiv, span);
  var ssdiv = getEl("div");
  var input = getEl("input");
  input.id = "admindiv-startdate-input";
  input.type = "date";
  input.style.marginLeft = "10px";
  var startDate = new Date();
  var startDate = new Date(startDate.setDate(startDate.getDate() - 7));
  var datestr = getDateStr(startDate);
  input.value = datestr;
  addEl(ssdiv, input);
  var span = getEl("span");
  span.textContent = "~";
  span.style.marginLeft = "10px";
  addEl(ssdiv, span);
  var input = getEl("input");
  input.id = "admindiv-enddate-input";
  input.type = "date";
  input.style.marginLeft = "10px";
  var datestr = getDateStr(new Date());
  input.value = datestr;
  addEl(ssdiv, input);
  var btn = getEl("button");
  btn.classList.add("butn");
  btn.textContent = "Update";
  btn.style.marginLeft = "10px";
  btn.addEventListener("click", function (_) {
    updateAdminTabContent();
  });
  addEl(ssdiv, btn);
  var btn = getEl("button");
  btn.classList.add("butn");
  btn.textContent = "Export";
  btn.style.marginLeft = "10px";
  btn.addEventListener("click", function (_) {
    exportContentAdminPanel();
  });
  addEl(ssdiv, btn);
  addEl(sdiv, ssdiv);
  addEl(div, sdiv);
  // input stat
  var sdiv = getEl("div");
  sdiv.id = "admindiv-inputstat-div";
  sdiv.className = "adminsection-div";
  addEl(div, sdiv);
  var span = getEl("span");
  span.className = "adminsection-title";
  span.textContent = "Input Stats";
  addEl(sdiv, span);
  var ssdiv = getEl("div");
  ssdiv.id = "admindiv-inputstat-contentdiv";
  addEl(sdiv, ssdiv);
  // job stat
  var sdiv = getEl("div");
  sdiv.id = "admindiv-jobstat-div";
  sdiv.className = "adminsection-div";
  addEl(div, sdiv);
  var span = getEl("span");
  span.className = "adminsection-title";
  span.textContent = "Job Stats";
  addEl(sdiv, span);
  var ssdiv = getEl("div");
  ssdiv.id = "admindiv-jobstat-contentdiv";
  addEl(sdiv, ssdiv);
  // user stat
  var sdiv = getEl("div");
  sdiv.id = "admindiv-userstat-div";
  sdiv.className = "adminsection-div";
  addEl(div, sdiv);
  var span = getEl("span");
  span.className = "adminsection-title";
  span.textContent = "User Stats";
  addEl(sdiv, span);
  var ssdiv = getEl("div");
  ssdiv.id = "admindiv-userstat-contentdiv";
  addEl(sdiv, ssdiv);
  // annotation stat
  var sdiv = getEl("div");
  sdiv.id = "admindiv-annotstat-div";
  sdiv.className = "adminsection-div";
  addEl(div, sdiv);
  var span = getEl("span");
  span.className = "adminsection-title";
  span.textContent = "Annotation Stats";
  addEl(sdiv, span);
  var ssdiv = getEl("div");
  ssdiv.id = "admindiv-annotstat-contentdiv";
  addEl(sdiv, ssdiv);
  // assembly stat
  var sdiv = getEl("div");
  sdiv.id = "admindiv-assemblystat-div";
  sdiv.className = "adminsection-div";
  addEl(div, sdiv);
  var span = getEl("span");
  span.className = "adminsection-title";
  span.textContent = "Assembly Stats";
  addEl(sdiv, span);
  var ssdiv = getEl("div");
  ssdiv.id = "admindiv-assemblystat-contentdiv";
  addEl(sdiv, ssdiv);
  // Restart button
  var btn = getEl("button");
  btn.textContent = "Restart Server";
  btn.addEventListener("click", function (_) {
    var url = "/server/restart";
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.send();
    location.href = "/server/nocache/login.html";
  });
  addEl(sdiv, btn);
  addEl(div, getEl("br"));
  // Final
  updateAdminTabContent();
}

function updateAdminTabContent() {
  populateInputStatDiv();
  populateUserStatDiv();
  populateAssemblyStatDiv();
}

function populateInputStatDiv() {
  var startDate = document.getElementById("admindiv-startdate-input").value;
  var endDate = document.getElementById("admindiv-enddate-input").value;
  var sdiv = document.getElementById("admindiv-inputstat-contentdiv");
  $(sdiv).empty();
  var table = getEl("table");
  addEl(sdiv, table);
  $.ajax({
    url: "/server/inputstat",
    data: { start_date: startDate, end_date: endDate },
    success: function (response) {
      var totN = response[0];
      var maxN = response[1];
      var avgN = response[2];
      var tr = getEl("tr");
      var td = getEl("td");
      td.textContent = "Total number of input lines:\xa0";
      addEl(tr, td);
      var td = getEl("td");
      td.textContent = totN;
      addEl(tr, td);
      addEl(table, tr);
      var tr = getEl("tr");
      var td = getEl("td");
      td.textContent = "Maximum number of input lines:\xa0";
      addEl(tr, td);
      var td = getEl("td");
      td.textContent = maxN;
      addEl(tr, td);
      addEl(table, tr);
      var tr = getEl("tr");
      var td = getEl("td");
      td.textContent = "Average number of input lines:\xa0";
      addEl(tr, td);
      var td = getEl("td");
      td.textContent = Math.round(avgN);
      addEl(tr, td);
      addEl(table, tr);
    },
  });
}

function populateUserStatDiv() {
  var startDate = document.getElementById("admindiv-startdate-input").value;
  var endDate = document.getElementById("admindiv-enddate-input").value;
  var sdiv = document.getElementById("admindiv-userstat-contentdiv");
  $(sdiv).empty();
  var table = getEl("table");
  addEl(sdiv, table);
  $.ajax({
    url: "/server/userstat",
    data: { start_date: startDate, end_date: endDate },
    success: function (response) {
      //
      var num_uniq_user = response["num_uniq_user"];
      var tr = getEl("tr");
      var td = getEl("td");
      td.textContent = "Number of unique users:\xa0";
      addEl(tr, td);
      var td = getEl("td");
      td.textContent = num_uniq_user;
      addEl(tr, td);
      addEl(table, tr);
      //
      var frequent = response["frequent"];
      var tr = getEl("tr");
      var td = getEl("td");
      td.textContent = "Most frequent user:\xa0";
      addEl(tr, td);
      var td = getEl("td");
      td.textContent = frequent[0];
      addEl(tr, td);
      addEl(table, tr);
      var tr = getEl("tr");
      var td = getEl("td");
      td.textContent = "\xa0\xa0Number of jobs:\xa0";
      addEl(tr, td);
      var td = getEl("td");
      td.textContent = frequent[1];
      addEl(tr, td);
      addEl(table, tr);
      //
      var heaviest = response["heaviest"];
      var tr = getEl("tr");
      var td = getEl("td");
      td.textContent = "Heaviest user:\xa0";
      addEl(tr, td);
      var td = getEl("td");
      td.textContent = heaviest[0];
      addEl(tr, td);
      addEl(table, tr);
      var tr = getEl("tr");
      var td = getEl("td");
      td.textContent = "\xa0\xa0Number of input:\xa0";
      addEl(tr, td);
      var td = getEl("td");
      td.textContent = heaviest[1];
      addEl(tr, td);
      addEl(table, tr);
    },
  });
}

function msgAccountDiv(msg, callback) {
  var div = getEl("div");
  if (typeof msg == "string") {
    div.textContent = msg;
  } else if (typeof msg == "object") {
    addEl(div, msg);
  }
  showYesNoDialog(div, callback, false, true);
}

function isGuestAccount(username) {
  if (username.startsWith("guest_") && username.indexOf("@") == -1) {
    return true;
  } else {
    return false;
  }
}

function exportContentAdminPanel(_) {
  var content = "";
  document.querySelectorAll(".adminsection-div").forEach(function (div) {
    var title = div.querySelector("span").textContent;
    content += "* " + title + "\n";
    var contentDiv = div.querySelector("div");
    var table = contentDiv.querySelector("table");
    if (table != undefined) {
      var trs = table.querySelectorAll("tr");
      for (var i = 0; i < trs.length; i++) {
        var tr = trs[i];
        var tds = tr.querySelectorAll("td");
        var line = "";
        for (var j = 0; j < tds.length; j++) {
          var td = tds[j];
          line += td.textContent.replace(/\xa0/g, " ") + "\t";
        }
        content += line + "\n";
      }
    } else {
      var line = "";
      var sdivs = contentDiv.children;
      for (var i = 0; i < sdivs.length; i++) {
        var sdiv = sdivs[i];
        var tagName = sdiv.tagName;
        if (tagName == "BUTTON") {
          continue;
        }
        var value = sdiv.textContent;
        if (tagName == "INPUT") {
          value = sdiv.value;
        }
        line += value + "\t";
      }
      content += line + "\n";
    }
    content += "\n";
  });
  content += "\n";
  var a = getEl("a");
  a.href = window.URL.createObjectURL(
    new Blob([content], { type: "text/tsv" })
  );
  a.download = "OpenCRAVAT_admin_stats.tsv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function multiuser_setup() {
  const firebaseConfig = {
    apiKey: "AIzaSyC9oGhGaax8DlSh-w9pC3TCeIJZzxAw-XU",
    authDomain: "oakvar-app.firebaseapp.com",
    projectId: "oakvar-app",
    storageBucket: "oakvar-app.appspot.com",
    messagingSenderId: "1070951630158",
    appId: "1:1070951630158:web:885d40bf4a42a1fc4cca1f",
    measurementId: "G-0PV5B1ZF6B"
  };
  firebase.initializeApp(firebaseConfig);
}

function afterLoginSuccess(result) {
  if (result) {
    hideSpinnerOnSignInBtn()
    user = result.user
    idToken = user.Aa
    axios.post("/server/loginsuccess", {"login_token": idToken})
    .then(function(_) {
      openSubmitPage()
    })
  }
}

function signInWithEmail() {
  var email = getEmail()
  var password = document.getElementById("password").value;
  showSpinnerOnSignInBtn()
  firebase
    .auth()
    .signInWithEmailAndPassword(email, password)
    .then(function (result) {
      afterLoginSuccess(result)
    })
    .catch(function (err) {
      hideSpinnerOnSignInBtn()
      alert(err.message)
    });
  return false;
}

function signInWithGitHub() {
  var provider = new firebase.auth.GithubAuthProvider();
  firebase
    .auth()
    .signInWithPopup(provider)
    .then(function (result) {
      afterLoginSuccess(result)
    })
    .catch(function (err) {
      hideSpinnerOnSignInBtn()
      alert(err.message)
    });
}

function signInWithGoogle() {
  var provider = new firebase.auth.GoogleAuthProvider();
  firebase
    .auth()
    .signInWithPopup(provider)
    .then(function (result) {
      afterLoginSuccess(result)
    })
    .catch(function (err) {
      hideSpinnerOnSignInBtn()
      alert(err.message)
    });
}

function onClickSignupSecondary() {
  document.getElementById("forgot_password_div").classList.add("hide");
  document.getElementById("signin_title").classList.add("hide");
  document.getElementById("signup_title").classList.remove("hide");
  document.getElementById("signup_secondary_a").classList.add("hide");
  document.getElementById("signin_secondary_a").classList.remove("hide");
  document.getElementById("signin_btn").classList.add("hide");
  document.getElementById("signup_btn").classList.remove("hide");
}

function onClickSigninSecondary() {
  document.getElementById("forgot_password_div").classList.remove("hide");
  document.getElementById("signin_title").classList.remove("hide");
  document.getElementById("signup_title").classList.add("hide");
  document.getElementById("signup_secondary_a").classList.remove("hide");
  document.getElementById("signin_secondary_a").classList.add("hide");
  document.getElementById("signin_btn").classList.remove("hide");
  document.getElementById("signup_btn").classList.add("hide");
}

window.onload = function (_) {};
