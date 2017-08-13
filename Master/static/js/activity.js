var GENERAL_SOCKET = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/general');
var PULL_LOGS_SOCKET = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/pull_logs');

$(document).ready(function () {
    //hide individual service pages at startup, only show the services summary table
    $('[id^=service_]').hide();

    //hide container pull logs at the startup
    $('[id^=container_pull_logs_]').hide();

    GENERAL_SOCKET.on('log_run_status', function (msg) {
        var service = msg.service;
        var status = msg.status;
        var status_service = $('#status_' + service);
        var status_service_btn = $('#status_btn_' + service);

        status_service.text(status);

        if (status == "STOPPED") {
            // change button text to start
            status_service_btn.text("START");
            //enable button in case its disabled while pulling
            status_service_btn.attr("disabled", false);
            // hide pulling logs if there're any
            $('#container_pull_logs_' + service).hide();
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-danger');
        }
        else if (status == "RUNNING") {
            // change button text to stop
            status_service_btn.text("STOP");
            //enable button in case its disabled while pulling
            status_service_btn.attr("disabled", false);
            // hide pulling logs if there're any
            $('#container_pull_logs_' + service).hide();
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-success');
        }
        else if (status == "NOT AVAILABLE") {
            // change button text to pull
            status_service_btn.text("PULL");
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-primary');
        }
    });

    GENERAL_SOCKET.on('log_init_status', function (msg) {
        // service initialization flag in home
        var service_init = $('#init');

        if (msg.status == "SUCCESS") {
            service_init.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-success');
            service_init.text("SUCCESS");
        }
        else if (msg.status == "INITIALIZATION FAILED") {
            service_init.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-danger');
            service_init.text("INITIALIZATION FAILED");
        }
    });

    PULL_LOGS_SOCKET.on('log_pull_status', function (msg) {
        var logs = JSON.parse(msg.data);
        var name = msg.name;

        for (var key in logs) {
            if (logs.hasOwnProperty(key)) {
                var div_name = "progress_" + name + "_" + key;
                var div_name_progress_text = div_name + '_progress_text';
                var div_name_progress_number = div_name + '_progress_number';
                var div_name_progress_bar = div_name + '_progress_bar';

                if (logs[key][0] == "Pulling fs layer") {
                    // if doesn't exist append a new progress bar
                    if (!(document.getElementById(div_name))) {
                        $("#progress_bar_" + name).append(
                            '<div class="progress-group" id=' + div_name + '>\
                                <span class="progress-text" id=' + div_name_progress_text + '>' + key + ': Pulling fs layer</span>\
                                <span class="progress-number" id =' + div_name_progress_number + '><b>0/100</b></span>\
                                <div class="progress sm">\
                                    <div class="progress-bar progress-bar-aqua" id=' + div_name_progress_bar + '></div>\
                                </div>\
                             </div>\
                        ');
                    }
                }
                else {
                    $("#" + div_name_progress_text).text(key + ": " + logs[key][0]);
                    $("#" + div_name_progress_number + " b").text(logs[key][1] + "/100");
                    $("#" + div_name_progress_bar).css("width", logs[key][1] + "%");
                }
            }
        }
    });
});

// for highlighting elements in left panel
$('#service-list').on('click', 'li', function () {
    $(this).addClass('active').siblings().removeClass('active');
});

// hide individual services, show services summary table
function showHome() {
    $('#service-list').children().removeClass('active');
    $('#home').show();
    $('[id^=service_]').hide();
}

//hide services summary table, show the individual service page
function showService(service) {
    $('#home').hide();
    $('[id^=service_]').hide();
    $('#service_' + service).show();
}

// start, stop a container or pull an image
function getAction(name, image_name, virtual_host, object) {
    if ($(object).text() == "START") {
        // if start button is clicked, emit start
        GENERAL_SOCKET.emit('start', {image_name: image_name, virtual_host: virtual_host});
    }
    else if ($(object).text() == "STOP") {
        // if stop button is clicked, emit stop
        GENERAL_SOCKET.emit('stop', {image_name: image_name});
    }
    else if ($(object).text() == "PULL") {
        //disable button to avoid clicking PULL button multiple times
        $(object).attr("disabled", true);
        //show container pull logs
        $('#container_pull_logs_' + name).show();
        // if pull button is clicked, emit pull
        GENERAL_SOCKET.emit('pull', {image_name: image_name, name: name});
    }
    return false;
}