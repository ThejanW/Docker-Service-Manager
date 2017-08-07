/**
 * Created by thejan on 8/1/17.
 */
$(document).ready(function () {
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
            status_service_btn.text("BUILD");
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-primary');
        }
    });

    namespace_build = '/build';
    var socket_build = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace_build);

    socket_build.on('log_build_status', function (msg) {
        $('#log_build_status').append('<br>' + $('<div/>').text(msg.data).html());
    });


    $('#init').click(function () {
        socket_build.emit('init')
    });
});

function doAction(pattern, object) {
    namespace = '/test';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    if ($(object).text() == "START") {
        socket.emit('start', {service: pattern});
    }
    else if ($(object).text() == "STOP") {
        socket.emit('stop', {service: pattern});
    }
    else if ($(object).text() == "BUILD") {
        socket.emit('build', {service: pattern});
    }
    return false;
}
