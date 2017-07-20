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


function deleteAccount(){
    /* OnClick script for delete account button */
    $("body").append("<div id='del-dialog' title='Deleting account...' style='display:none'></div>");
    input = $("form").serializeArray();
    $("#del-dialog").dialog({
        create: function(){
            $.getJSON($SCRIPT_ROOT + '/deleteAccount', input, function(json){
                if(json.success === true){
                    console.log(json);
                    $("#del-dialog").html("Account has been deleted. "
                                        + "If you are not redirected, click "
                                        + "<a href='" + $SCRIPT_ROOT
                                        + "/'>here</a>.");
                    window.location.href = ($SCRIPT_ROOT + "/logout");
                } else {
                    $("#del-dialog").html("ERROR: " + json.returnMessage);
                }
            });
        },
        close: function(){
            $("#del-dialog").dialog("destroy");
            $("#del-dialog").remove();
        }
    });
}


function changePassword(){
    /* OnClick script for change password button */
    input = $("form").serializeArray();

    // change password if passwords match, display alert if not
    if (input[0].name !== "pwdNew" || input[1].name !== "pwdNewConfirm") {
        console.log("ERROR: form fields do not match script design; "
                    + "account.html script needs to be debugged");
        $.alert({
            title: "O noes! :(",
            content: "The person who programmed this site made a mistake, "
                     + "and this page won't work the way it's supposed to. "
                     + "If you want to help him fix it, email him at "
                     + "jacobhuntgit@gmail.com and let him know where "
                     + "it happened.",
        });
    } else if (input[0].value !== input[1].value) {
        $.alert({
            title: "O noes!",
            content: "Passwords don't match :(",
        });
    } else {
        $.getJSON($SCRIPT_ROOT + '/changePassword', input, function(json){
            if(json.success===false){
                $("body").append("<div id='pw-dialog' title='Oh no!' style='display:none'></div>");
                $("#pw-dialog").append("Could not change password:<br />" + json.returnMessage);
                $("#pw-dialog").dialog();
            } else if (json.success===true){
                $("body").append("<div id='pw-dialog' title='Password changed' style='display:none'></div>");
                $("#pw-dialog").append("If you are not redirected, click <a href='" + $SCRIPT_ROOT + "/'>here</a>.");
                $("#pw-dialog").dialog({
                    create: function(){
                        window.location.href = ($SCRIPT_ROOT + "/");
                    },
                });
            } else {
                $("body").append("<div id='pw-dialog' title='Unknown error' style='display:none'></div>");
                $("#pw-dialog").append("The writer of this program made a mistake; totally not your fault.  "
                                     + "If you want to let him know what happened so that he can fix it, "
                                     + "you can email him at jacobhuntgit@gmail.com.");
                $("#pw-dialog").dialog();
            }
        });
    }
}
