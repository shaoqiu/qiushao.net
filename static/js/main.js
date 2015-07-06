/**
 * Created by shaoqiu on 2015-6-26.
 */
function click_avatar() {
    document.getElementById("login").style.display = "block";
}
function click_close() {
    document.getElementById("login").style.display = "none";
}
function click_login() {
    var user = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    if (user == "" || password == "") {
        alert("User Name or Password is empty!");
        return false;
    }
    document.getElementById("login").style.display = "none";
    return true;
}

function click_edit() {
    document.getElementById("preview_button").style.display = "block";
    document.getElementById("edit_button").style.display = "none";
    document.getElementById("markdown_preview").style.display = "none";
    document.getElementById("markdown_edit").style.display = "block";
    document.getElementById("top_button").style.display = "none";
}

function click_preview() {
    compileMarkdown(document.getElementById("markdown_editor").value);
    document.getElementById("preview_button").style.display = "none";
    document.getElementById("edit_button").style.display = "block";
    document.getElementById("markdown_preview").style.display = "block";
    document.getElementById("markdown_edit").style.display = "none";
    document.getElementById("top_button").style.display = "block";
}

function click_del() {
    var title = document.getElementById("title_editor").value;
    var tag = document.getElementById("tag_editor").value;
    $.ajax({
        type: "post",
        async: false,
        url: "/article",
        data: {operator: "del", tag: tag, title: title},
        timeout: 10000,
        success: function () {
            alert("delete success " + title + " " + tag);
            location.reload(true);
        },
        error: function () {
            alert("delete failed");
        }
    });
}
function click_publish() {
    var title = document.getElementById("title_editor").value;
    var tag = document.getElementById("tag_editor").value;
    var markdown = document.getElementById("markdown_editor").value;
    $.ajax({
        type: "post",
        async: false,
        url: "/article",
        data: {operator: "update", tag: tag, title: title, markdown: markdown},
        timeout: 10000,
        success: function () {
            alert("public success " + title + " " + tag);
            //location.reload(true);
        },
        error: function () {
            alert("request failed");
        }
    });
}
function click_goTOP() {
    $("#content").animate({scrollTop: 0}, 'slow');
}
function click_toc() {
    $('#toc').toggle();
}
function genTOC() {
    var toc = $('#toc_ul');
    toc.empty();
    $('#content').find('h1,h2,h3,h4').each(function () {
        $(this).attr('id', function () {
            var ID = "",
                alphabet = "abcdefghijklmnopqrstuvwxyz";

            for (var i = 0; i < 5; i++) {
                ID += alphabet.charAt(Math.floor(Math.random() * alphabet.length));
            }
            return ID;
        });

        var tagName = $(this).prop("tagName");
        toc.append('<li class="toc_li toc_' + tagName.toLowerCase() + '"><a href="#' + $(this).attr('id') + '" class="anchor_link">' + $(this).text() + '</a></li>');

    });

    $('.anchor_link').off('click').on('click', function () {
        var target = $(this.hash);
        $("#content").animate({scrollTop: target.offset().top + $("#content").scrollTop() - 70}, 500, function () {
            target.addClass('flash').delay(700).queue(function () {
                $(this).removeClass('flash').dequeue();
            });
        });
    });
}
function compileMarkdown(datas) {
    markdown_preview.innerHTML = marked(datas);
    $('pre code').each(function (i, block) {
        hljs.highlightBlock(block);
    });
    $('a').attr('target', '_blank');
    $("#content").animate({scrollTop: 0}, 'slow');
    genTOC();
}
function request_markdown(tag, title) {
    $.ajax({
        type: "get",
        async: false,
        url: "/article",
        data: {tag: tag, title: title},
        timeout: 10000,
        success: function (datas) {
            document.getElementById("title_editor").value = title;
            document.getElementById("tag_editor").value = tag;
            document.getElementById("markdown_editor").value = datas;
            compileMarkdown(datas);
        },
        error: function () {
            alert("request failed");
        }
    });
}

function isMobile() {
    var userAgentInfo = navigator.userAgent;
    var Agents = ["Android", "iPhone",
        "SymbianOS", "Windows Phone",
        "iPad", "iPod"];
    for (var v = 0; v < Agents.length; v++) {
        if (userAgentInfo.indexOf(Agents[v]) > 0) {
            return true;
        }
    }
    return false;
}
function onload() {
    $(".tags_li").on("click", function () {
        $(this).addClass('active').siblings().removeClass('active');
        var filter = $(this).data('filter');
        if (filter === 'all') {
            $('.posts_li').fadeIn(350);
        } else {
            $('.posts_li').hide();
            $('[data-filter~=' + filter + ']').fadeIn(350);
        }
    });

    $(".posts_li").on("click", function () {
        $(this).addClass('active').siblings().removeClass('active');
        var tag = $(this).data('filter');
        var title = $(this).text();
        request_markdown(tag, title);
        if (isMobile()) {
            $("#sidebar").addClass("fullscreen");
        }
    });

    request_markdown("", "about");
}
