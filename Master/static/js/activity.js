var general_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/general');
var pull_logs_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/pull_logs');

$(document).ready(function () {
    //hide individual service pages at startup, only show the services summary table
    $('[id^=service_]').hide();

    //hide container pull logs at the startup
    $('[id^=container_pull_logs_]').hide();

    general_socket.on('log_run_status', function (msg) {
        var service = msg.service;
        var status = msg.status;
        var status_service = $('#status_' + service);
        var status_service_btn = $('#status_btn_' + service);

        status_service.text(status);

        if (status == "STOPPED") {
            // change button text to start
            status_service_btn.text("START");
            // hide pulling logs if there're any
            $('#container_pull_logs_' + service).hide();
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-danger');
        }
        else if (status == "RUNNING") {
            // change button text to stop
            status_service_btn.text("STOP");
            // hide pulling logs if there're any
            $('#container_pull_logs_' + service).hide();
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-success');
        }
        else if (status == "NOT AVAILABLE") {
            status_service_btn.text("PULL");
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-primary');
        }
    });

    general_socket.on('log_init_status', function (msg) {
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


    pull_logs_socket.on('log_pull_status', function (msg) {
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
function goHome() {
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
function doAction(name, image_name, virtual_host, object) {
    if ($(object).text() == "START") {
        general_socket.emit('start', {image_name: image_name, virtual_host: virtual_host});
    }
    else if ($(object).text() == "STOP") {
        general_socket.emit('stop', {image_name: image_name});
    }
    else if ($(object).text() == "PULL") {
        //show container pull logs
        $('#container_pull_logs_' + name).show();
        general_socket.emit('pull', {image_name: image_name, name: name});
    }
    return false;
}