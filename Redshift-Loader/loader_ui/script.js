var idToken = null;

// Checks if the user is logged in with a valid token, otherwise they will be redirected to the sign-in page.
// If the UI webpage times out, they will still be on the webpage but their tables and metrics
// will not load where the user will have to press the logout button to sign in again.
function checkLoginAndLoadInfo() {
  idToken = window.location.hash.substr(1).split('&')[0].split('id_token=')[1]
  if (idToken != null) {
      document.getElementById("loaderUserInterfaceContent").style.visibility = 'visible'
      window.location.href = cloudFrontURLString + idToken + "&expires_in=3600&token_type=Bearer"
      document.getElementById("welcomeMsg").innerHTML = "Signed in!";
      auth();
      timeDropdownFunctionCalls();
      populateRedshiftTableDetails();
      populateLoaderParameterDetails();
  } else {
      document.getElementById("loaderUserInterfaceContent").style.visibility = 'hidden'
      window.location.href = cognitoSignInSignUpURL
  }
}

// Sets the credentials based on parameter variables pulled from the config.js file that is created from 
// launching the CloudFormation template.
function auth() {
  var creds = {};  
  AWS.config.update({
    region: awsAcctRegion,
  });

  creds["IdentityPoolId"] = cognitoIdentityPoolId;
  creds["Logins"]={}
  creds["Logins"][loginsKey]=idToken;
  AWS.config.credentials = new AWS.CognitoIdentityCredentials(creds);
}

// Sets the screen to display the Cognito sign-in page.
function loadLoginPage() {
  window.location.href = cognitoSignInSignUpURL
}

// Captures the current timestamp and calculates an adjusted timestamp based on the user's
// selection from the time filter dropdown on the UI webpage. The function returns an array
// containing both timestamps that were formatted using MomentJS.
function subtractHoursFromCurrentTimeStamp() {
  let timeSelect = document.getElementById('timeDropdown');
  let timeSelectValue = timeSelect.options[timeSelect.selectedIndex].value;
  let numHours = 0;
  const userCurrentTimeStamp = new Date();
  let adjustedTimeStamp = ""
  let formattedCurrentTimeStamp = "";
  let formattedAdjustedTimeStamp = "";
  let hoursDiff = userCurrentTimeStamp.getTimezoneOffset() / 60;

  userCurrentTimeStamp.setHours(userCurrentTimeStamp.getHours() + hoursDiff) // Converts captured timestamp to represent UTC

  formattedCurrentTimeStamp = moment(userCurrentTimeStamp).format('YYYY-MM-DD HH:mm:ss')

  if (timeSelectValue == 24) {
    numHours = 24
  } else if (timeSelectValue == 168) {
    numHours = 168
  } else if (timeSelectValue == "allTime") {
    numHours = 0
  }

  adjustedTimeStamp = userCurrentTimeStamp.setHours(userCurrentTimeStamp.getHours() - numHours)

  formattedAdjustedTimeStamp = moment(adjustedTimeStamp).format('YYYY-MM-DD HH:mm:ss')

  return [formattedCurrentTimeStamp, formattedAdjustedTimeStamp]
}

// Calls the populateCopyCommandDetailsAndCountCopyCommands() and populateFileDetails() functions
// to combine them into one function for populating all the tables in the "Load details overview" pane by
// using the time filter dropdown.
function timeDropdownFunctionCalls() {
  
  populateCopyCommandDetailsAndCountCopyCommands()
  populateFileDetails()
}

// Populates the Copy Command Details table and counts the number of loads by status by calling the countCopyCommands()
// function. This function works with the timestamp values of the array returned by the subtractHoursFromCurrentTimeStamp()
// function. If the two timestamp values are equal to each other, this means that the user chose to see the load details
// over the course of all their time with using the auto loader. The scan filter is dropped if "All Time" was selected.
function populateCopyCommandDetailsAndCountCopyCommands() {

  var docClient = new AWS.DynamoDB.DocumentClient();
  let timeStamps = subtractHoursFromCurrentTimeStamp();
  let currentTime = timeStamps[0];
  let adjustedTime = timeStamps[1];
  const currentTimeDateObject = new Date(currentTime);
  const adjustedTimeDateObject = new Date(adjustedTime);

  console.log("populateCopyCommandDetails' Current Date & Time: " + currentTime)
  console.log("populateCopyCommandDetails' Adjusted Date & Time: " + adjustedTime)

  console.log("populate Copy Command Details")
  $("#copyCommandDetails tbody")[0].innerHTML = '<tr><td colspan="9"><img src="images/loading.gif" style="width:100px;border:0px"></td></tr>';
  
  if (currentTimeDateObject.getTime() != adjustedTimeDateObject.getTime()) {
    var params = {
      TableName: 's3_data_loader_log',
      ScanFilter: {
        'finish_timestamp': {
          ComparisonOperator: "BETWEEN",
          AttributeValueList: [
            adjustedTime,
            currentTime
          ]
        }
      }
    };
  } else {
    var params = {
      TableName: 's3_data_loader_log'
    };
  }

  docClient.scan(params, function(err,result){
    if (err) {
      console.log('Error: ' + JSON.stringify(err));
    } else {
      console.log(result);
      if (result.Items.length > 0) {
        $("#copyCommandDetails tbody")[0].innerHTML = result.Items.map(row => "<tr> \
          <td>" + row.copy_command_sql + "\
          <td>" + row.copy_command_status + "\
          <td>" + row.finish_timestamp + "\
          <td>" + row.log_timestamp + "\
          <td>" + row.redshift_query_Id + "\
          <td>" + row.redshift_schema + "\
          <td>" + row.redshift_table_name + "\
          <td>" + row.s3_manifest_file_path + "\
          <td>" + row.s3_table_name).join("</tr>");
      } else {
        $("#copyCommandDetails tbody")[0].innerHTML = "<tr><td colspan=9>There are no copy command details to display.</td></tr>"
      }

      countCopyCommands()
    }
  });
}

// Populates the S3 File Details table and works with the timestamp values of the array returned by 
// the subtractHoursFromCurrentTimeStamp() function, similar to the populateCopyCommandDetailsAndCountCopyCommands() function.
function populateFileDetails() {

  var docClient = new AWS.DynamoDB.DocumentClient();
  let timeStamps = subtractHoursFromCurrentTimeStamp();
  let currentTime = timeStamps[0];
  let adjustedTime = timeStamps[1];
  const currentTimeDateObject = new Date(currentTime);
  const adjustedTimeDateObject = new Date(adjustedTime);

  console.log("populateFileDetails' Current Date & Time: " + currentTime)
  console.log("populateFileDetails' Adjusted Date & Time: " + adjustedTime)

  console.log("populate S3 File Details")
  $("#fileDetails tbody")[0].innerHTML = '<tr><td colspan="4"><img src="images/loading.gif" style="width:100px;border:0px"></td></tr>';
  
  if (currentTimeDateObject.getTime() != adjustedTimeDateObject.getTime()) {
    var params = {
      TableName: 's3_data_loader_file_metadata',
      ScanFilter: {
        'file_created_timestamp': {
          ComparisonOperator: "BETWEEN",
          AttributeValueList: [
            adjustedTime,
            currentTime
          ]
        }
      }
    };
  } else {
    var params = {
      TableName: 's3_data_loader_file_metadata'
    };
  }

  docClient.scan(params, function(err,result){
    if (err) {
      console.log('Error: ' + JSON.stringify(err));
    } else {
      console.log(result);
      if (result.Items.length > 0) {
        $("#fileDetails tbody")[0].innerHTML = result.Items.map(row => "<tr> \
          <td>" + row.s3_table_name + "\
          <td>" + row.file_created_timestamp + "\
          <td>" + row.file_content_length + "\
          <td>" + row.s3_file_path).join("</tr>");
      } else {
        $("#fileDetails tbody")[0].innerHTML = "<tr><td colspan=4>There are no S3 file details to display.</td></tr>"
      }
    }
  });
}

// Populates the Redshift Table Details table in the "Loader configuration" pane.
function populateRedshiftTableDetails() {

  var docClient = new AWS.DynamoDB.DocumentClient();

  console.log("populate Redshift Table Details")
  $("#redshiftTableDetails tbody")[0].innerHTML = '<tr><td colspan="9"><img src="images/loading.gif" style="width:100px;border:0px"></td></tr>';
  var params = {
    TableName: 's3_data_loader_table_config'
  };
  docClient.scan(params, function(err,result){
    if (err) {
      console.log('Error: ' + JSON.stringify(err));
    } else {
      console.log(result);
      if (result.Items.length > 0) {
        $("#redshiftTableDetails tbody")[0].innerHTML = result.Items.map(row => "<tr> \
          <td>" + row.s3_table_name + "\
          <td>" + row.additional_copy_options + "\
          <td>" + row.iam_role + "\
          <td>" + row.load_status + "\
          <td>" + row.max_file_proccessed_timestamp + "\
          <td>" + row.redshift_schema + "\
          <td>" + row.redshift_table_name + "\
          <td>" + row.schema_detection_completed + "\
          <td>" + row.schema_detection_failed).join("</tr>");
      } else {
        $("#redshiftTableDetails tbody")[0].innerHTML = "<tr><td colspan=9>There are no Redshift table details to display.</td></tr>"
      }
    }
  });
}

// Populates the Loader Parameter Details table in the "Loader configuration" pane.
function populateLoaderParameterDetails() {

  var docClient = new AWS.DynamoDB.DocumentClient();

  console.log("populate Loader Parameter Details")
  $("#loaderParameterDetails tbody")[0].innerHTML = '<tr><td colspan="8"><img src="images/loading.gif" style="width:100px;border:0px"></td></tr>';
  var params = {
    TableName: 's3_data_loader_params'
  };
  docClient.scan(params, function(err,result){
    if (err) {
      console.log('Error: ' + JSON.stringify(err));
    } else {
      console.log(result);
      if (result.Items.length > 0) {
        $("#loaderParameterDetails tbody")[0].innerHTML = result.Items.map(row => "<tr> \
          <td>" + row.redshift_cluster_identifier + "\
          <td>" + row.copy_default_options + "\
          <td>" + row.initiate_schema_detection_global_var + "\
          <td>" + row.no_of_copy_commands + "\
          <td>" + row.redshift_database + "\
          <td>" + row.redshift_iam_role + "\
          <td>" + row.redshift_user + "\
          <td>" + row.schedule_frequency).join("</tr>");
      } else {
        $("#loaderParameterDetails tbody")[0].innerHTML = "<tr><td colspan=8>There are no loader parameter details to display.</td></tr>"
      }
    }
  });
}

// Counts the number of loads by status directly from the rows returned in the Copy Command Details table 
// on the UI webpage itself.
function countCopyCommands() {

  let numRowsFinished = $("#copyCommandDetails tr:contains('FINISHED')").length;
  let numRowsFailed = $("#copyCommandDetails tr:contains('FAILED')").length;
  let numRowsExecuting = $("#copyCommandDetails tr:contains('Execution')").length;
  let numRowsAttempted = numRowsExecuting + numRowsFailed + numRowsFinished
  let countsRow = document.createElement('tr');
  let countsRowExecutingValue = document.createElement('td');
  let countsRowFailedValue = document.createElement('td');
  let countsRowCompletedValue = document.createElement('td');
  let countsRowAttemptedValue = document.createElement('td');

  console.log("Counting loads")

  console.log(numRowsExecuting + " Loads Executing")
  console.log(numRowsFailed + " Loads Failed")
  console.log(numRowsFinished + " Loads Finished")
  console.log(numRowsAttempted + " Loads Attempted")

  countsRowCompletedValue.innerHTML = numRowsFinished;
  countsRowFailedValue.innerHTML = numRowsFailed;
  countsRowAttemptedValue.innerHTML = numRowsAttempted;
  countsRowExecutingValue.innerHTML = numRowsExecuting;

  console.log("populate metrics table")

  countsRow.appendChild(countsRowExecutingValue)
  countsRow.appendChild(countsRowFailedValue)
  countsRow.appendChild(countsRowCompletedValue)
  countsRow.appendChild(countsRowAttemptedValue)
  
  document.getElementById("metricsTblTBody").innerHTML = ""
  document.getElementById("metricsTblTBody").appendChild(countsRow)
}