/*********************************************************************
 *
 *   FlickFinder Alpha 0.2
 *   Copyright (C) 2017  Jacob Hunt (jacobhuntgit@gmail.com)
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License version 2,  as
 *   published by the Free Software Foundation.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see 
 *   https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html.
 *
 *********************************************************************/


/* NEW MOVIE NIGHT GLOBALS */

// dictionary to keep track of friend names user IDs
var flDict = {};
// array to keep track of users in current movie night
var mnUserList = [];
// array to keep track of genre preferences in current movie night
var mnGenreList = [];


/* MAIN MOVIE NIGHT SESSION INTERFACE GLOBALS */

var mnID = -1;
var posterBaseURL = "https://image.tmdb.org/t/p/w185//";
var posterURL = "None";
var mn_page = 0;
var mn_counter = 0;
var movieJSON = [{'0': 0}];
var ajaxLoadDiv = "<div id='ajax-loader' align='center'>"
                  + "<img src='static/ajax-loader.gif' "
                  + "alt='Loading...' /></div>";


/* FRONT PAGE */

function fp_init() {
    /* Load app front page. */

    $("#app").load("/divs #fp", function(){
        $("#fp").removeClass("invisible").addClass("animated fadeIn");
    });
}


function fp_btnNew() {
    /* 'New Movie Night' button */

    $("#fp").removeClass("animated fadeIn").addClass("animated fadeOut");

    setTimeout(function(){
        nw_init();
    }, 400);
}


function fp_btnInvite() {
    /* 'Add Friends' button */

    $("#fp").removeClass("animated fadeIn").addClass("animated fadeOut");

    setTimeout(function(){
        fr_init();
    }, 400);
}


function fp_btnMovieNights() {
    /* 'My Movie Nights' button */

    $("#fp").removeClass("animated fadeIn").addClass("animated fadeOut");

    setTimeout(function(){
        my_init();
    }, 400);
}


/* FRIEND REQUEST PAGE */

function fr_init() {
    /* Initialize friend request page */
    $("#app").load("/divs #fr", function(){
        $("#fr").removeClass("invisible").addClass("animated fadeIn");
    });
}


function fr_sendRequest() {
    /* Send friend request button */
    input = $("form").serializeArray();
    $.getJSON($SCRIPT_ROOT + '/sendFriendRequest', input)
    .done(function(data, textStatus, jqXHR) {
        displayMessage(data);
    });
}


function fr_btnView() {
    /* OnClick script for Reply To Friend Requests button */

    // Remove friend request front menu
    $("#fr").removeClass("animated fadeIn").addClass("animated fadeOut");

    // Load friend request reply menu
    setTimeout(function(){
        fr_view();
    }, 400);
}


function fr_btnBack() {
    /* OnClick script for back button */
    $("#fr").removeClass("animated fadeIn").addClass("animated fadeOut");
    setTimeout(function(){
        fp_init();
    }, 400);
}


function fr_view() {
    /* View and respond to other users' friend requests */

    // get pending friend requests
    $.getJSON($SCRIPT_ROOT + '/getFriendRequests')
    .done(function(data, textStatus, jqXHR) {

        // load friend request response menu
        $("#app").load("/divs #frr", function(){
            // animate menu display
            $("#frr").removeClass("invisible").addClass("animated fadeIn");

            // attach pending friend requests to select box form
            var n = data.idList.length;
            for(i = 0; i < n; i++){
                formItem = "<input type='radio' name='frrForm' value='" 
                           + String(data.idList[i]) + "'> " 
                           + String(data.usrNameList[i])
                           + "<br />";

                $("form").append(formItem);
            }
        });
    });
}


function fr_accept(){
    /* OnClick script for Accept Friend Request button */

    // get form input
    input = $("form").serializeArray();
    input = input[0].value;

    // call serverside script    
    $.getJSON($SCRIPT_ROOT + '/acceptFriendRequest', {usrID: input})
    .done(function(data, textStatus, jqXHR) {
        // display "friend request accepted" message
        $.alert({
            title: 'Friend request accepted!',
            content: 'Press OK to continue'
        });

        // reload fr_view menu
        fr_view();
    });
}


function fr_del(){
    /* Decline a friend request */

    // get form input
    input = $("form").serializeArray();
    input = input[0].value;

    // call serverside script    
    $.getJSON($SCRIPT_ROOT + '/declineFriendRequest', {usrID: input})
    .done(function(data, textStatus, jqXHR) {
        // display "friend request declined" message
        if(data.success === false){
            $.alert({
                title: "Error",
                content: data.returnMessage
            });
        } else if (data.success === true){
            $.alert({
                title: "Friend request declined",
                content: "Press OK to continue"
            });
        }

        // reload fr_view menu
        fr_view();
    });
}


function frr_btnBack(){
    /* OnClick script for back button on "respond to friend
       requests" page */

    $("#frr").removeClass("animated fadeIn").addClass("animated fadeOut");
    setTimeout(function(){
        fr_init();
    }, 400);
}


function displayMessage(data) {
    /* Display the return message returned from fr_sendRequest */

    $("#messageBox").html("<h1>"
                        +     data.returnMessage
                        + "</h1>"
                        + "<button type='button' "
                        + "class='btn btn-default' "
                        + "onclick='$(\"#messageBox\").dialog(\"close\")'>"
                        +     "OK"
                        + "</button>");
    $("#messageBox").dialog({
        modal: true,
    });
    
}


/* MY MOVIE NIGHTS */

function my_init() {
    /* Initialize My Movie Nights menu */

    // get movie night list
    $.getJSON($SCRIPT_ROOT + '/getMnList')
    .done(function(data, textStatus, jqXHR) {

        // shorthand variable
        mnIdList = data.mnIdList;
        mnDateTimeList = data.mnDateTimeList

        // display My Movie Nights menu
        $("#app").load("/divs #my", function(){
            // add movie nights to select menu
            n = mnIdList.length;

            for(i = 0; i < n; i++){
                formItem = "<input type='radio' name='mnForm' value='"
                           + String(mnIdList[i])
                           + "'> "
                           + String(mnDateTimeList[i])
                           + "<br />";

                // debugging
                console.log("Form item tag:");
                console.log(formItem);

                $("form").append(formItem);
            }

            // display user interface
            $("#my")
              .removeClass("invisible")
              .addClass("animated fadeIn");
        });
    });
}


function my_resume() {
    /* Continue with selected movie night */

    // get form input
    input = $("form").serializeArray();
    input = parseInt(input[0].value);

    // set value of mnID to ID of selected movie night
    mnID = input;

    // hide menu
    $("#my").removeClass("animated fadeIn").addClass("animated fadeOut");

    setTimeout(function(){
        // get JSON of movie night data
        $.getJSON($SCRIPT_ROOT + '/getUserMnPosition', {mnID: mnID})
        .done(function(data, textStatus, jqXHR){
            // resume movie night
            mn_resume(data.page, data.depth);
        });
    }, 400);
}


function my_del() {
    /* Remove user from selected movie night */

    // fetch form input
    input = $("form").serializeArray();
    input = parseInt(input[0].value);

    // call server-side script
    $.getJSON($SCRIPT_ROOT + '/leaveMovieNight', {mnID: input})
    .done(function(data, textStatus, jqXHR){
        // debugging
        console.log(data);
        my_init();
    });
}

function my_btnBack() {
    /* OnClick script for Back button in My Movie Nights menu */

    $("#my").removeClass("animated fadeIn").addClass("animated fadeOut");
    setTimeout(function(){
        $("#app").html(ajaxLoadDiv);
        fp_init();
    }, 400);

}


/* NEW MOVIE NIGHT */

function nw_init() {
    /* Initialize menu */

    // reset globals
    flDict = {};
    mnUserList = [];
    mnGenreList = [];

    // get friend list
    $.getJSON($SCRIPT_ROOT + '/getFriendList')
    .done(function(data, textStatus, jqXHR) {
        friendList = data.friendList;

        // generate a lists names of friends and their user IDs, as
        // well as reference dict
        n = friendList.length;
        nameList = [];
        idList = [];
        for (i = 0; i < n; i++) {
            nameList.push(friendList[i].firstName
                          + " -- @"
                          + friendList[i].userName);
            idList.push(friendList[i].userID);
            flDict[String(friendList[i].userID)] = (friendList[i].firstName
                                                    + " -- @"
                                                    + friendList[i].userName);
        }

        // display menu
        nw_display(nameList, idList);

    });
}


function nw_display(nameList, idList){
    /* Form to invite friends to movie night */

    $("#app").load("/divs #nw_invites", function(){
        $("#nw_invites").removeClass("invisible").addClass("animated fadeIn");

        $("form").submit(false);

        // add friend names to dropdown menu
        for (i = 0; i < n; i++) {
            $("form select").append("<option "
                                    + " value='"
                                    + idList[i]
                                    + "'>"
                                    + nameList[i]
                                    + "</option>");
        }
    });
}


function nw_btnAdd() {
    /* Add friend to movie night */
    input = $("form").serializeArray();
    $("#nw-addbox ol").append("<li>"
                              + flDict[String(input[0].value)]
                              + "</li>");
    mnUserList.push(input[0].value);
    console.log(input);
    $("#nw_friends-list option[value='" + String(input[0].value) + "']").remove();
}


function nw_btnGenres() {
    /* Button to go to form to select preferences for movie genres */
    $("#nw_invites")
        .removeClass("animated fadeIn")
        .addClass("animated fadeOut");

    setTimeout(function(){
        nw_genresInit();
    }, 400);
}


function nw_genresInit() {
    /* Show genres form */

    $.getJSON($SCRIPT_ROOT + '/getGenres')
    .done(function(data, textStatus, jqXHR) {
        genreJSON = data;

        $("#app").load("/divs #nw_genres", function(){

            n = genreJSON.length;
            for (i = 0; i < n; i++) {
                $("#nw_genre-form form")
                    .append("<input type='checkbox' name='genres' value='"
                            + genreJSON[i].id
                            + "'>"
                            + genreJSON[i].name
                            + "<br />");
            }

            $("#nw_genres")
                .removeClass("invisible")
                .addClass("animated fadeIn");
        });
    });
}


function nw_btnStart() {
    /* Begin movie night */

    // get genre preferences from form
    input = $("form").serializeArray();

    // store genre preferences
    n = input.length;
    for (i = 0; i < n; i++) {
        mnGenreList.push(input[i].value);
    }

    $("#nw_genres").removeClass("animated fadeIn").addClass("animated fadeOut");

    setTimeout(function(){
        // display loading gif
        $("#app").html(ajaxLoadDiv);
        mn_init(1, 0);
    }, 400);
}


function nw_btnBack() {
    /* OnClick script for back button on "Invite Friends" page */

    $("#nw_invites").removeClass("animated fadeIn").addClass("animated fadeOut");
    setTimeout(function(){
        fp_init();
    }, 400);
}


function nw_genresBtnBack() {
    /* OnClick script for back button on "Select Genres" page */

    $("nw_genres").removeClass("animated fadeIn").addClass("animated fadeOut");
    setTimeout(function(){
        nw_init();
    }, 400);

}


/* MAIN MOVIE NIGHT SESSION INTERFACE */

function mn_init(startPage, startPageDepth) {
    /* Initialize a new movie night */

    // reset globals
    posterBaseURL = "https://image.tmdb.org/t/p/w185//";
    posterURL = "None";
    mn_counter = startPageDepth - 1;
    mn_page = startPage;
    movieJSON = [{'0': 0}];

    // run newMovieNight serverside script
    $.getJSON($SCRIPT_ROOT + '/newMovieNight',
              {userList: String(mnUserList), genreList: String(mnGenreList)})
    .done(function(data, textStatus, jqXHR) {
        // store suggestions in global variable
        movieJSON = data.suggestions;
        console.log(movieJSON);
        mnID = data.mnID;

        // load divs
        $("#app").load("/divs #mn", function(){
            $("#mn").removeClass("invisible").addClass("animated fadeIn");
            $("#mn_poster").html(ajaxLoadDiv);
            mn_switchMovie();
        });
    });
}


function mn_resume(startPage, startQueryDepth) {
    /* Resume an existing movie night */

    // reset globals
    posterBaseURL = "https://image.tmdb.org/t/p/w185//";
    posterURL = "None";
    mn_page = startPage;
    movieJSON = [{'0': 0}];
    mn_counter = -1;

    // display loading gif
    $("#app").html(ajaxLoadDiv);

    // run loadMovieNight serverside script
    $.getJSON($SCRIPT_ROOT + '/loadMovieNight',
              {mnID: mnID, mnPage: mn_page, mnDepth: startQueryDepth})
    .done(function(data, textStatus, jqXHR) {
        // debugging
        console.log("loadMovieNight return JSON:");
        console.log(data);

        // store suggestions in global variable
        movieJSON = data.suggestions;
        mnGenreList = data.genres;
        console.log(movieJSON);

        // load divs
        $("#app").load("/divs #mn", function(){
            $("#ajax-loader").detach();
            $("#mn").removeClass("invisible").addClass("animated fadeIn");
            $("#mn_poster").html(ajaxLoadDiv);
            mn_switchMovie();
        });
    });
}


function mn_exit(initNextMenu) {
    /* Exit animation for main movie night interface,
       takes init function for next menu as argument */

    $("#mn").addClass("animated fadeOut");
    setTimeout(function(){
        initNextMenu();
    }, 1200);

}


function mn_switchMovie() {
    /* Move on to next movie in suggestion list */

    // incriment position tracker
    mn_counter++;

    // if movie has poster
    if (movieJSON[mn_counter].poster_url){
        posterURL = posterBaseURL + movieJSON[mn_counter].poster_url;
        posterTag = "<img src='"
                    + posterURL
                    + "' alt='"
                    + movieJSON[mn_counter].title
                    + "' />";
    } else {
        posterTag = "<p>POSTER NOT AVAILABLE</p>";
    }

    // Alert user if no more results are available from TMDB
    if (movieJSON[0] == "EOQ"){
        $.alert({
            title: 'No more results',
            content: ":("
        });
        return
    }

    $(posterTag).load(function() {

        // display poster
        $("#mn_poster")
            .html("<div id='mn_current-poster' class='invisible'></div>");

        $(this).appendTo("#mn_current-poster");
 
        $("#mn_current-poster")
            .removeClass("invisible")
            .addClass("animated zoomInLeft");

        // update infobox
        $("#mn_info").empty();

        $("#mn_info").append("<p>Title: <br />"
                             + movieJSON[mn_counter].title
                             + "</p>");

        $("#mn_info").append("<p>Rating: <br />"
                             + movieJSON[mn_counter].rating
                             + "</p>");

        $("#mn_info").append("<p>Release Date: <br />"
                             + movieJSON[mn_counter].release_date
                             + "</p>");

        $("#mn_info").append("<p>Description: <br />"
                             + movieJSON[mn_counter].description
                             + "</p>");
    });

    // update user_position in mn_<id>_users table
    var userPosition = movieJSON[mn_counter].query_depth;
    $.getJSON($SCRIPT_ROOT + '/updateUserPosition',
              {userPosition: userPosition, mnID: mnID})
    .done(function(data, textStatus, jqXHR){
        // debugging
        console.log(data);
    });
    
}


function mn_btnThumbsUp() {
    /* Thumbs up button */
    $("#mn_current-poster").removeClass("zoomInLeft").addClass("zoomOutRight");
    setTimeout(function(){
        mn_log(1, movieJSON[mn_counter].movie_id);
        // load next page of suggestions if user has reached end of list
        if(mn_counter >= movieJSON.length - 1){
            mn_loadNextPage();
        } else {
            mn_switchMovie();
        }
    }, 400);
}


function mn_btnThumbsDown() {
    /* Thumbs down button */
    $("#mn_current-poster").removeClass("zoomInLeft").addClass("zoomOutRight");
    setTimeout(function(){
        mn_log(-1, movieJSON[mn_counter].movie_id);
        // load next page of suggestions if user has reached end of list
        if(mn_counter >= movieJSON.length - 1){
            mn_loadNextPage();
        } else {
            mn_switchMovie();
        }
    }, 400);
}


function mn_viewMatches() {
    /* View matches button */

    // function to be called after exit animation finished
    function nextInit() {
        // display view matches menu for current movie night
        vm_init("ACTIVE_MOVIENIGHT", mnID);
    }

    // leave main movie night interface
    mn_exit(nextInit);
}


function mn_log(rating, movieID) {
    /* Record user's rating in database */

    console.log("rating: ");
    console.log(rating);

    $.getJSON($SCRIPT_ROOT + '/logRating',
              {mnID: mnID, rating: rating, movieID: movieID})
    .done(function(data, textStatus, jqXHR){

        // debugging
        console.log(data);

        // check match status
        if(data.matchStatus == true){
            mn_notifyMatch(data.movieID);
        }
    });
}


function mn_notifyMatch(movieID) {
    /* Notify user of match */

    // get movie title and poster
    $.getJSON($SCRIPT_ROOT + '/getMovie', {movieID: movieID, mnID: mnID})
    .done(function(data, textStatus, jqXHR){
        // shorthand variables
        posterURL = data.posterURL;
        title = data.title;
        alertMessage = "<div align='center'><img src='"
                       + posterURL
                       + "' alt='Movie Poster' /></div><br />Everyone in your "
                       + "group wants to watch <strong>"
                       + title
                       + "</strong>!";
        $.alert({
            title: 'Break out the popcorn!',
            content: alertMessage,
        });

        // debugging
        console.log("$.alert() called");
    });
}


function mn_loadNextPage() {
    /* Load next page of user suggestions */

    // Incriment page tracker
    mn_page++;

    // Call serverside script
    $.getJSON($SCRIPT_ROOT + '/loadNextPage',
              {mnID: mnID, mnPage: mn_page, genreList: String(mnGenreList)})
    .done(function(data, textStatus, jqXHR){
        if(data.success !== true && data.returnMessage == "EOQ"){
            $.alert({
                title: "No more results",
                content: ":("
            });
        } else if (data.success !== true){
            $.alert({
                title: data.returnMessage,
                content: ":("
            });
        }
        movieJSON = data.suggestions;

        // Switch to first suggestion of new page
        mn_counter = -1;
        mn_switchMovie();
    });
}


/* VIEW MATCHES MENU */

POSTER_URL_ROOT = "https://image.tmdb.org/t/p/w185//";
SEARCH_URL_ROOT = "https://www.fan.tv/search/";
var vm_arrivedFrom = "NONE";
var vm_matchesList = [];

function vm_init(arrivedFrom, movieNightID) {
    /* Load view-matches menu for current movie night */

    // keep track of where user arrived at view-matches menu from
    vm_arrivedFrom = arrivedFrom;

    // ajax loader
    $("#app").html(ajaxLoadDiv);

    // load divs
    $("#app").load("/divs #ml", function(){
        // add matches to slection menu
        vm_listMatches(movieNightID);
    });
}


function vm_listMatches(movieNightID) {
    /* Add match tabs to view-matches selection box */

    // show ajax loader
    $("#ml_list").append(ajaxLoadDiv);

    // get matches and associated data
    $.getJSON($SCRIPT_ROOT + '/getMatches', {mnID: movieNightID})
    .done(function(data, textStatus, jqXHR){
        // convenience variable
        vm_matchesList = data.matches;

        // debugging
        console.log(vm_matchesList);

        // clear ajax load gif
        $("#ajax-loader").remove();

        // for each match, append a button to #ml_list div
        n = vm_matchesList.length;
        for (i = 0; i < n; i++){
            vm_appendMatchButton(vm_matchesList, i);
        }
    });
}


function vm_appendMatchButton(matchJSON, i){
    /* Creates a button in selection box for matchObject */

    // debugging
    console.log("matchJSON[i].original_title is:");
    console.log(String(matchJSON[i].original_title));

    $("#ml_list ul").append("<li><a onclick='vm_displayInfo("
                         + "vm_matchesList, "
                         + String(i)
                         + ")'>"
                         + matchJSON[i].original_title
                         + "</a></li>");
}


function vm_displayInfo(matchList, index){
    /* Display a box with information about a match */

    // convenience variables
    matchObj = matchList[index];
    title = matchObj.original_title;
    posterURL = POSTER_URL_ROOT + matchObj.poster_path;
    description = matchObj.overview;
    rating = matchObj.vote_average;

    alertDiv = "<div align='center'>"
             + "<img src = '" + posterURL + "' alt='Movie Poster' />"
             + "</div><br />"
             + "<div class='textbox-black-white scrollable' style='height:75px'>"
             + "<p>"
             + description
             + "</p>"
             + "</div>"
             + "<p align='center'>"
             + "<button type='button' class='black-text' onclick='vm_searchPrompt(\""
             + title
             + "\")'>Search for "
             + title
             + " on fan.tv</button>"
             + "</p>"
             + "</div>";

    $("#matchInfoBox").html(alertDiv);
    $("#matchInfoBox").dialog();
}


function vm_searchPrompt(title){
    /* Prompt user before leaving FlickFinder */

    searchURL = SEARCH_URL_ROOT + title;

    searchPromptDiv = "<div id='searchPrompt'>"
                    +     "<div id='searchPromptText'>"
                    +         "Warning: you are about to leave this app and go "
                    +         "to a site which is not associated with FlickFinder. "
                    +         "The creators of FlickFinder are not responsible for "
                    +         "the content or availability of linked sites."
                    +     "</div>"
                    +     "<div id='searchPromptButtons' class='row'>"
                    +         "<div class='col-xs-6'>"
                    +             "<button type='button' onclick='vm_closeMatchInfo()' "
                    +             "class='btn btn-lg btn-block btn-default "
                    +             "margin-x-5px'>Cancel</button>"
                    +         "</div>"
                    +         "<div class='col-xs-6'>"
                    +             "<a href='"
                    +             searchURL
                    +             "' target='_blank'><button type='button' onclick='#' "
                    +             "class='btn btn-lg btn-block btn-default "
                    +             "margin-x-5px'>Continue</button>"
                    +         "</div>"
                    +     "</div>"
                    +  "</div>";

    $("#matchInfoBox").html(searchPromptDiv);
}


function vm_closeMatchInfo(){
    /* Close dialog box */
    $("#matchInfoBox").dialog("close");
}


function vm_btnBack(){
    /* Return to voting interface */

    $.getJSON($SCRIPT_ROOT + '/getUserMnPosition', {mnID: mnID})
    .done(function(data, textStatus, jqXHR){
        mn_resume(data.page, data.depth);
    });
}

/* TUTORIAL */

function tut_open(){
    /* OnClick script for tutorial button */

    $("body").append("<div id='tut-dialog' title='Tutorial' style='display:none'></div>");
    $("#tut-dialog").dialog({
        fluid: true,
        resizable: false,
        position: { my: "top", at: "bottom", of: "#navbar" }
    });
    $("#tut-dialog").html(ajaxLoadDiv);
    tut_pg01();
}


function tut_pg01(){
    /* Page 1 of tutorial */

    var tutDiv = ("<div id='tut-pg01'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_01.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 1' /><br />"
                +     "<div id='tut-text'>"
                +         "FlickFinder is an app designed to help a group "
                +         "of two or more people decide on a movie to "
                +         "watch.  Before you get started, make sure everyone "
                +         "in your group has a FlickFinder account."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='#' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px' disabled>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg02()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 1 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg02(){
    /* Page 2 of tutorial */

    var tutDiv = ("<div id='tut-pg02'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_02.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 2' /><br />"
                +     "<div id='tut-text'>"
                +         "You can only start a new movie night with people "
                +         "who are in your friends list.  Once everyone in "
                +         "you group is signed up,  click on \"Add Friends\" "
                +         "in the main menu to add them."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg01()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg03()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 2 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg03(){
    /* Page 3 of tutorial */

    var tutDiv = ("<div id='tut-pg03'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_03.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 3' /><br />"
                +     "<div id='tut-text'>"
                +         "Type in the username or email address of the person "
                +         "you want to add (note that your friend has to have "
                +         "a FlickFinder account to receive your friend "
                +         "request) and then click \"Send Friend Request\".  "
                +         "Repeat this process until you've added everyone "
                +         "in your group."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg02()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg04()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 3 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg04(){
    /* Page 4 of tutorial */

    var tutDiv = ("<div id='tut-pg04'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_04.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 4' /><br />"
                +     "<div id='tut-text'>"
                +         "If someone has sent you a friend request, you can "
                +         "accept or decline it using the \"Reply to Friend "
                +         "Requests\" menu.  Have everyone in your group "
                +         "accept your friend request if you're ready to get "
                +         "started."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg03()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg05()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 4 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg05(){
    /* Page 5 of tutorial */

    var tutDiv = ("<div id='tut-pg05'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_05.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 5' /><br />"
                +     "<div id='tut-text'>"
                +         "From the \"Reply to Friend Requests\" menu, "
                +         "you can select which friend request to respond "
                +         "to and accept or decline the request."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg04()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg06()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 5 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg06(){
    /* Page 6 of tutorial */

    var tutDiv = ("<div id='tut-pg06'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_06.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 6' /><br />"
                +     "<div id='tut-text'>"
                +         "Click \"New Movie Night\" to start a "
                +         "FlickFinder session."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg05()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg07()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 6 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg07(){
    /* Page 7 of tutorial */

    var tutDiv = ("<div id='tut-pg07'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_07.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 7' /><br />"
                +     "<div id='tut-text'>"
                +         "Invite everyone in your group who you want to "
                +         "watch a movie with.  When you're done, click "
                +         "\"Next.\""
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg06()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg08()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 7 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg08(){
    /* Page 8 of tutorial */

    var tutDiv = ("<div id='tut-pg08'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_08.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 8' /><br />"
                +     "<div id='tut-text'>"
                +         "Select which genres to include in your session "
                +         "(FlickFinder will look for movies which match "
                +         "your selections).  When you're done selecting, "
                +         "click \"Start.\""
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg07()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg09()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 8 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg09(){
    /* Page 9 of tutorial */

    var tutDiv = ("<div id='tut-pg09'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_09.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 9' /><br />"
                +     "<div id='tut-text'>"
                +         "Other people in your group who you have invited "
                +         "can join in too; have them click on \"My Movie "
                +         "Nights\" to do this."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg08()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg10()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 9 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg10(){
    /* Page 10 of tutorial */

    var tutDiv = ("<div id='tut-pg10'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_10.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 10' /><br />"
                +     "<div id='tut-text'>"
                +         "From the \"My Movie Nights\" menu, you can select "
                +         "which session you want to join."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg09()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg11()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 10 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg11(){
    /* Page 11 of tutorial */

    var tutDiv = ("<div id='tut-pg11'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_11.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 11' /><br />"
                +     "<div id='tut-text'>"
                +         "FlickFinder will look for movies that you might "
                +         "be interested in watching.  Click the Thumbs Up "
                +         "button if the suggestion is something you would "
                +         "be interested in watching, or the Thumbs Down if "
                +         "it's not something you're interested in right now."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg10()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg12()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 11 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg12(){
    /* Page 12 of tutorial */

    var tutDiv = ("<div id='tut-pg12'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_12.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 12' /><br />"
                +     "<div id='tut-text'>"
                +         "Once everyone in your movie night has agreed on "
                +         "a movie to watch, FlickFinder will let you know.  "
                +         "You can continue voting after a match has been "
                +         "found; FlickFinder will notify you of each "
                +         "additional match.  Note that, at this point, only "
                +         "the last person to upvote a suggestion will "
                +         "receive this notification."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg11()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg13()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 12 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg13(){
    /* Page 13 of tutorial */

    var tutDiv = ("<div id='tut-pg13'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_13.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 13' /><br />"
                +     "<div id='tut-text'>"
                +         "You can click on \"View Matches\" to see a list "
                +         "of all the movies your group has agreed on "
                +         "this session."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg12()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg14()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 13 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg14(){
    /* Page 14 of tutorial */

    var tutDiv = ("<div id='tut-pg14'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_14.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 14' /><br />"
                +     "<div id='tut-text'>"
                +         "In the \"View Matches\" menu, you can click on "
                +         "the title of a movie to bring up a description "
                +         "of it."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg13()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg15()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 14 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}


function tut_pg15(){
    /* Page 15 of tutorial */

    var tutDiv = ("<div id='tut-pg15'>"
                +     "<img class='img-fluid' src='" + $SCRIPT_ROOT
                +     "/static/tutorial-pics/tutorial_15.jpg' "
                +     "style='width: 100%; height: auto;'"
                +     "alt='Tutorial Page 15' /><br />"
                +     "<div id='tut-text'>"
                +         "In the box that comes up when you click on the "
                +         "movie title in \"View Matches,\" there is a button "
                +         "to search for the movie with fan.tv (a "
                +         "search engine to let you know where you can watch "
                +         "a given movie).  Note that this will take you to "
                +         "a separate website which is not a part of "
                +         "FlickFinder."
                +     "</div>"
                +     "<div id='tut-buttons' class='row'>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='tut_pg14()' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px'>Previous</button>"
                +         "</div>"
                +         "<div class='col-xs-6'>"
                +             "<button type='button' onclick='#' "
                +             "class='btn btn-lg btn-block btn-default "
                +             "margin-x-5px' disabled>Next</button>"
                +         "</div>"
                +     "</div>"
                +     "<div id='tut-pagenum' class='row'>"
                +         "<em style='font-size: 0.7em'>Page 15 of 15</em>"
                +     "</div>"
                + "</div>");

    $("#tut-dialog").html(tutDiv);
}
