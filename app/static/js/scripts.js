function formatDateTime(dateTimeStr) {
    var date = new Date(dateTimeStr);
    var day = String(date.getDate()).padStart(2, '0');
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var year = date.getFullYear();
    var hours = String(date.getHours()).padStart(2, '0');
    var minutes = String(date.getMinutes()).padStart(2, '0');

    return `${day}.${month}.${year} г. ${hours}:${minutes}`;
}


function updateArticles(type) {
    // Получаем все website IDs сразу
    var $activeTab = $(`#${type}`);
    var ids = $activeTab.find('.website-block').map(function () {
        return $(this).data('id');
    }).get();

    var idsString = ids.join(',');
    if (ids.length > 0) {
        $.ajax({
            url: "/api/websites/",
            type: 'GET',
            data: {
                'ids': idsString,
                'type': type // Добавили тип для параметров запроса
            },
            dataType: 'json',
            success: function (data) {
                $activeTab.find('.website-block').each(function () {
                    var $block = $(this);
                    var websiteId = $block.data('id').toString();
                    var articles = data.websites[websiteId];
                    var $list = $block.find('.website-list'); // Используйте класс вместо id

                    var currentIds = $list.find('li').map(function () {
                        return $(this).data('id');
                    }).get();

                    if (currentIds.length === 0) {
                        addArticles($list, articles);
                        return;
                    }

                    var newArticles = articles.filter(function (article) {
                        return !currentIds.includes(article.id);
                    });

                    if (newArticles.length) {
                        var excessArticles = $list.find('li').slice(3 - newArticles.length);
                        excessArticles.fadeOut(400, function () {
                            $(this).remove();
                        });

                        setTimeout(function () {
                            addArticles($list, newArticles);
                        }, 1000);
                    }
                });
            }
        });
    }
}

function addArticles($list, articles) {
    // Добавляем статьи в начало списка
    articles.forEach(function (article) {
        var formattedDate = formatDateTime(article.created_at);
        var listItem = `
                    <li data-id="${article.id}" style="display: none;">
                        <div class="website-url highlight">
                            <a href="${article.url}">${article.title}</a>
                            <span class="publish-date">${formattedDate}</span>
                        </div>
                    </li>
                `;
        $list.prepend(listItem);
        $list.find(`li[data-id="${article.id}"]`).fadeIn(400);
    });

    // Убираем подсветку через 1 секунду
    setTimeout(function () {
        $list.find('.website-url.highlight').removeClass('highlight');
    }, 399);
}

function setActiveTabUpdate() {
    var activeTab = document.querySelector(".tablinks.active").getAttribute("onclick");
    var type = activeTab.match(/openTab\(event, '(\w+)'\)/)[1];
    updateArticles(type);
}

function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
    // Это удалит все дочерние элементы, сбрасывая список
    if (evt.currentTarget.className.indexOf("active") > -1) {
        updateArticles(tabName);
    }

    // Вызов функции обновления с нужным типом
}
document.addEventListener('DOMContentLoaded', function () {
    document.getElementsByClassName("tablinks")[0].click();
    setInterval(setActiveTabUpdate, 15000);
});
