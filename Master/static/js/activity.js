$(document).ready(function () {

    //hide individual service pages at startup, only show the services summary table
    $('[id^=service_]').hide();

    //hide container pull logs at the startup
    $('[id^=container_pull_logs_]').hide();

    namespace = '/test';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('log_run_status', function (msg) {
        var service = msg.service;
        var status = msg.status;
        var status_service = $('#status_' + service);

        var status_service_btn = $('#status_btn_' + service);
        status_service.text(status);
        if (status == "STOPPED") {
            status_service_btn.text("START");
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-danger');
        }
        else if (status == "RUNNING") {
            status_service_btn.text("STOP");
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

    namespace_build = '/build';
    var socket_build = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace_build);

    socket_build.on('log_build_status', function (msg) {
        var logs = JSON.parse(msg.data);
        var name = msg.name;

        for (var key in logs) {
            if (logs.hasOwnProperty(key)) {
                if (logs[key][0] == "Pulling fs layer") {
                    // if doesn't exist
                    var div_name = "#progress_" + name + "_" + key;
                    if (document.getElementById(div_name)) {
                        console.log("already exists");
                    }
                    else {
                        $("#progress_bar_" + name).append(
                            '<div class="progress-group" id=' + div_name + '>\
                                <span class="progress-text">Add Products to Cart</span>\
                                <span class="progress-number"><b>160</b>/200</span>\
                                <div class="progress sm">\
                                    <div class="progress-bar progress-bar-aqua" style="width: 80%"></div>\
                                </div>\
                             </div>\
                        ');
                    }
                }
                console.log(logs[key]);
            }
        }
    });


    $('#init').click(function () {
        socket_build.emit('init')
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
    namespace = '/test';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    if ($(object).text() == "START") {
        socket.emit('start', {image_name: image_name, virtual_host: virtual_host});
    }
    else if ($(object).text() == "STOP") {
        socket.emit('stop', {image_name: image_name});
    }
    else if ($(object).text() == "PULL") {
        //show container pull logs
        $('#container_pull_logs_' + name).show();
        socket.emit('pull', {image_name: image_name, name: name});
    }
    return false;
}

