$(document).ready(function () {
    function formatDateTime(dateTimeStr) {
        var date = new Date(dateTimeStr);
        var day = String(date.getDate()).padStart(2, '0');
        var month = String(date.getMonth() + 1).padStart(2, '0');
        var year = date.getFullYear();
        var hours = String(date.getHours()).padStart(2, '0');
        var minutes = String(date.getMinutes()).padStart(2, '0');
        return `${day}.${month}.${year} г. ${hours}:${minutes}`;
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    

    function addArticles($list, articles) {
        articles.forEach(function (article) {
            var formattedDate = formatDateTime(article.published_at);


            var favoriteIcon = article.is_favorite ?
                `<a href="#" class="toggle-favorite" data-action="/api/remove_favorite/${article.website__id}/"><i class="fas fa-star"></i></a>` :
                `<a href="#" class="toggle-favorite" data-action="/api/add_favorite/${article.website__id}/"><i class="far fa-star"></i></a>`;
            
            var taskIcon = article.task_status ?
                `<a href="#" class="toggle-task" data-action="/update_task/${article.id}/"><i class="fas fa-tasks" style="color: #005eff;"></i></a>` :
                `<a href="#" class="toggle-task" data-action="/add_task/${article.id}/"><i class="fas fa-tasks"></i></a>`;


            var taskClass = '';
            if (article.task_status === 'pending') {
                taskClass = 'task-pending';
            } else if (article.task_status === 'in_progress') {
                taskClass = 'task-in-progress';
            } else if (article.task_status === 'completed') {
                taskClass = 'task-completed';
            }
            var listItem = `
            <li data-id="${article.id}" class="${taskClass}">
                <div class="website-url highlight ">
                    <div class="icons">${favoriteIcon} ${taskIcon}</div>
                    <div class="article-info">
                        <div class="category">
                            <span>${article.readable_category}</span>
                        </div>
                        <div class="article-title">
                            <a href="${article.url}">${article.title}</a>
                        </div>
                        <div class="article-date">
                            <div>
                                <span class="publish-date">${formattedDate}</span>
                                <span class="publish-date">${article.website__name}</span>
                            </div>                  
                            <div class="country">${article.website__country__name}</div>      
                        </div>
                    </div>
                </div>
            </li>
            `;

            $list.prepend(listItem);
            $list.find(`li[data-id="${article.id}"]`).fadeIn(400);
            //обработчик событий для кнопки добавления в задачи

            $list.find(`li[data-id="${article.id}"] .toggle-task`).on('click', function() {
                showTaskDialog(article.id);
            });


            
            setTimeout(function () {
                $list.find('.website-url.highlight').removeClass('highlight');
            }, 399);
        });
    }
    // обновление статьи при изменении даты, страны, сайта
    $('#startDate, #endDate, #countriesSelect, #websitesSelect, #trackwordSelect, #excludedCountriesSelect, #excludedWebsitesSelect, #excludedTrackwordSelect, .filters input[type="checkbox"]').on('change', function () {
        if (!window.isUpdatingArticles) {
            updateArticlesWithClear();
        }
    });



    function showTaskDialogForAddTask(articleId) {
        Swal.fire({
            title: 'Добавить в задачи',
            html: `
                <select id="task-status" class="swal2-input">
                    <option value="pending">Отложено</option>
                    <option value="in_progress">В Процессе</option>
                    <option value="completed">Отработано</option>
                </select>
                <select id="task-priority" class="swal2-input">
                    <option value="1">Низкий</option>
                    <option value="2" selected="selected">Средний</option>
                    <option value="3">Высокий</option>
                </select>
            `,
            confirmButtonText: 'Добавить',
            focusConfirm: false,
            preConfirm: () => {
                const status = document.getElementById('task-status').value;
                const priority = document.getElementById('task-priority').value;
                return { status: status, priority: priority };
            }
        }).then((result) => {
            if (result.isConfirmed) {
                // Вызов функции для добавления задачи с выбранными параметрами
                addTask(articleId, result.value.status, result.value.priority);
            }
        });
    }
    
    function addTask(articleId, status, priority) {
        var csrftoken = getCookie('csrftoken');


        $.ajax({
            url: '/api/tasks/create/', 
            type: 'POST',
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
              },
            data: {
                article_id: articleId,
                status: status,
                priority: priority
            },
            success: function(response) {

                if(response.success) {
                    updateArticleHighlight(articleId, status);
                    updateTaskIcon(articleId, true); 
                    Swal.fire('Успешно', 'Задача добавлена', 'success');
                } else {
                    Swal.fire('Ошибка', 'Не удалось добавить задачу', 'error');
                }
            },
            error: function() {
                Swal.fire('Ошибка', 'Произошла ошибка при добавлении задачи', 'error');
            }
        });
    }

    function getTaskInfo(articleId) {
        return $.ajax({
            url: `/api/tasks/info/${articleId}/`,
            method: 'GET',
            dataType: 'json'
        });
    }
    function showTaskDialog(articleId) {
        getTaskInfo(articleId).then(taskInfo => {
            // Если задача существует, показываем диалог обновления
            showTaskDialogForUpdateTask(articleId, taskInfo);
        }).catch(error => {
            // Если задачи нет, показываем диалог добавления
            showTaskDialogForAddTask(articleId);
        });
    }
    
    function showTaskDialogForUpdateTask(articleId, taskInfo) {

            Swal.fire({
                title: 'Обновить задачу',
                html: `
                    <select id="task-status" class="swal2-input">
                        <option value="pending" ${taskInfo.status === 'pending' ? 'selected' : ''}>Отложено</option>
                        <option value="in_progress" ${taskInfo.status === 'in_progress' ? 'selected' : ''}>В Процессе</option>
                        <option value="completed" ${taskInfo.status === 'completed' ? 'selected' : ''}>Отработано</option>
                    </select>
                    <select id="task-priority" class="swal2-input">
                        <option value="1" ${taskInfo.priority === 1 ? 'selected' : ''}>Низкий</option>
                        <option value="2" ${taskInfo.priority === 2 ? 'selected' : ''}>Средний</option>
                        <option value="3" ${taskInfo.priority === 3 ? 'selected' : ''}>Высокий</option>
                    </select>
                `,
                confirmButtonText: 'Обновить',
                focusConfirm: false,
                preConfirm: () => {
                    const status = document.getElementById('task-status').value;
                    const priority = document.getElementById('task-priority').value;
                    return { status: status, priority: priority };
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    updateTask(articleId, result.value.status, result.value.priority);
                }
            });

    }


    function updateTask(articleId, status, priority) {
        var csrftoken = getCookie('csrftoken');

        $.ajax({
            url: '/api/tasks/update/',
            method: 'POST',
            data: {
                csrfmiddlewaretoken: csrftoken, 
                article_id: articleId, 
                status: status, 
                priority: priority 
            },
            success: function(response) {
                if(response.status === 'success') {
                    Swal.fire('Успешно', 'Задача обновлена', 'success');
                    updateArticleHighlight(articleId, status);
                } else {
                    Swal.fire('Ошибка', 'Ошибка при обновлении задачи', 'error');
                }
            },
            error: function(error) {
                console.error('Ошибка AJAX запроса:', error);
            }
        });
    }
        
    function updateTaskIcon(articleId, isInTask) {
        var $article = $(`li[data-id="${articleId}"]`);
        var $taskIconLink = $article.find('.fas.fa-tasks').closest('a');
    
        if (isInTask) {
            // Обновление для сценария, когда статья добавляется в задачи
            $taskIconLink.removeClass('add-task').addClass('update-task');
            $taskIconLink.attr('data-action', `/update_task/${articleId}/`);
            $taskIconLink.find('.fas.fa-tasks').css('color', '#005eff');
            
        } else {
            // Возврат к исходному состоянию, если статья удаляется из задач
            $taskIconLink.removeClass('update-task').addClass('add-task');
            $taskIconLink.attr('data-action', `/add_task/${articleId}/`);
            $taskIconLink.find('.fas.fa-tasks').css('color', ''); 
        }
    }
    

    function updateArticleHighlight(articleId, status) {
        var $article = $(`li[data-id="${articleId}"]`);
        $article.removeClass('task-pending task-in-progress task-completed');

        var highlightClass = '';
        if (status === 'pending') {
            highlightClass = 'task-pending';
        } else if (status === 'in_progress') {
            highlightClass = 'task-in-progress';
        } else if (status === 'completed') {
            highlightClass = 'task-completed';
        }

        $article.addClass(highlightClass);
    }

    function updateArticlesWithClear() {
        clearTimeout(updateTimer);
        var $list = $('.website-block .list');
        $list.empty();

        updateArticles();
    }

    var updateTimer;

    function scheduleNextUpdate() {
        clearTimeout(updateTimer); // Очистка предыдущего таймера, если он был установлен
        updateTimer = setTimeout(updateArticles, 12000); //следующее обновление через 12 секунд
    }

    function addParameterToURL(url, paramName, paramValue) {
        if (url.indexOf('?') === -1) {
            url += "?" + paramName + "=" + paramValue;
        } else {
            url += "&" + paramName + "=" + paramValue;
        }
        return url;
    }

    function updateArticles() {
        var updateUrl = "/api/test/";

        var $list = $('.website-block .list');

        var websiteBlock = document.querySelector('.website-block');
        var countryCode = websiteBlock.id;

        var onlyFavorites = $('#showOnlyFavorites').prop('checked');

        var startDate = $('#startDate').val();
        var endDate = $('#endDate').val();
        // Фильтры для Live Tracking (Добавить фильтры)
        var selectedCountries = $('#countriesSelect').val();
        var selectedWebsites = $('#websitesSelect').val();
        var selectedTrackwords = $('#trackwordSelect').val();

        var selectedCategories = [];
        $('.filters input[type="checkbox"]:checked').each(function() {
            selectedCategories.push($(this).val());
        });

        //Исключение из фильтрации для Live Tracking
        var excludedCountriesSelect = $('#excludedCountriesSelect').val();
        var excludedWebsitesSelect = $('#excludedWebsitesSelect').val();
        var excludedTrackwordSelect = $('#excludedTrackwordSelect').val();

        // Добавление чекбоксов рубрик
        if (selectedCategories.length > 0) {
            updateUrl = addParameterToURL(updateUrl, "categories", selectedCategories.join(','));
        }
        // Добавление фильтра startDate
        if (startDate) {
            updateUrl = addParameterToURL(updateUrl, "start_date", startDate);
        }

        // Добавление фильтра endDate
        if (endDate) {
            updateUrl = addParameterToURL(updateUrl, "end_date", endDate);
        }

        // Добавление фильтра для Live Tracking
        if ($('#live-tracking-page').length) {
            updateUrl = addParameterToURL(updateUrl, "live", "true");
        }

        // Добавление фильтра onlyFavorites
        if (onlyFavorites) {
            updateUrl = addParameterToURL(updateUrl, "only_favorites", "true");
            if (countryCode) {
                updateUrl = addParameterToURL(updateUrl, "country", countryCode);
            }
        } else if (countryCode) {
            updateUrl = addParameterToURL(updateUrl, "country", countryCode);
        }



        // Добавление фильтра selectedCountries
        if (selectedCountries && selectedCountries.length > 0) {
            updateUrl = addParameterToURL(updateUrl, "selected_countries", selectedCountries.join(','));
        }

        // Добавление фильтра selectedWebsites
        if (selectedWebsites && selectedWebsites.length > 0) {
            updateUrl = addParameterToURL(updateUrl, "websites", selectedWebsites.join(','));
        }

        if (selectedTrackwords && selectedTrackwords.length > 0) {
            updateUrl = addParameterToURL(updateUrl, "trackwords", selectedTrackwords.join(','));
        }

        // Добавление фильтра excludedCountriesSelect
        if (excludedCountriesSelect && excludedCountriesSelect.length > 0) {
            updateUrl = addParameterToURL(updateUrl, "excluded_countries", excludedCountriesSelect.join(','));
        }

        // Добавление фильтра excludedWebsitesSelect
        if (excludedWebsitesSelect && excludedWebsitesSelect.length > 0) {
            updateUrl = addParameterToURL(updateUrl, "excluded_websites", excludedWebsitesSelect.join(','));
        }

        // Добавление фильтра excludedTrackwordSelect
        if (excludedTrackwordSelect && excludedTrackwordSelect.length > 0) {
            updateUrl = addParameterToURL(updateUrl, "excluded_trackwords", excludedTrackwordSelect.join(','));
        }
        
        $.ajax({
            url: updateUrl,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                if (!data.articles || data.articles.length === 0) {
                    Swal.fire('Ничего не найдено.', 'Проверьте фильтры.', 'error'); // Вывод сообщения об отсутствии статей
                    return; 
                }
                var currentIds = $list.find('li').map(function () {
                    return parseInt($(this).data('id'));
                }).get();
                if (currentIds.length === 0) {
                    addArticles($list, data.articles);
                    return;
                }

                var newArticles = data.articles.filter(function (article) {
                    return !currentIds.includes(article.id);
                });

                if (newArticles.length) {
                    var excessArticles = $list.find('li').slice(-newArticles.length); //11!!
                    excessArticles.fadeOut(400, function () {
                        $(this).remove();
                    });
                    setTimeout(function () {
                        addArticles($list, newArticles);
                    }, 1000);
                }

            },
            error: function () {


            }
        });
        scheduleNextUpdate();
    }
    $('#showOnlyFavorites').change(updateArticlesWithClear); // обновление статьи при изменении   чекбокса showOnlyFavorites
    updateArticles();


    $(document).on('click', '.toggle-favorite', function (e) {
        e.preventDefault();
        e.stopPropagation();
        let $this = $(this);
        let actionUrl = $this.data('action');
        let $icon = $this.find('i');

        $.ajax({
            url: actionUrl,
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                if (data.status == "added") {
                    $icon.removeClass('far').addClass('fas'); // Замена на заполненную звезду
                    $this.data('action', actionUrl.replace('add_favorite', 'remove_favorite'));
                } else if (data.status == "removed") {
                    $icon.removeClass('fas').addClass('far'); // Замена на пустую звезду
                    $this.data('action', actionUrl.replace('remove_favorite', 'add_favorite'));
                } else if (data.status == "error") {
                    alert("Ошибка: " + data.message);
                }
            },
            error: function (errorData) {
                console.error("Ошибка при выполнении операции!");
                alert("Ошибка при выполнении операции.");
            }
        });
        setTimeout(function () {
            updateArticlesWithClear();
        }, 500);

    });
    ////////////////////////////  Добавление в задачи внутри облака  ////////////////////////////
    const articlesListDiv = document.querySelector('.tags-list');

    articlesListDiv.addEventListener('click', function(event) {
        // Проверяем, был ли клик сделан на элементе с классом .toggle-task
        if (event.target.closest('.toggle-task')) {
            const li = event.target.closest('li');
            const articleId = li.getAttribute('data-id');
            showTaskDialog(articleId);
        }
    });
    ////////////////////////////................................////////////////////////////


    // Обновление  фильтров в select при выборе набора фильтров в select через AJAX
    $('#tabsSelect').on('change', function () {
        var tabId = $(this).val();

        // Если вкладка не выбрана, очищаем поля и выходим
        if (!tabId) {
            window.isUpdatingArticles = true;
            $('#countriesSelect').val(null).trigger('change');
            $('#websitesSelect').val(null).trigger('change');
            $('#trackwordSelect').val(null).trigger('change');
            window.isUpdatingArticles = false;
            updateArticlesWithClear();
            return;
        }
        window.isUpdatingArticles = true;
        $.ajax({
            url: '/api/get_tab_data/',
            data: {
                'tab_id': tabId
            },
            success: function (response) {

                // Обновление select элементов
                if (response.countries) {
                    $('#countriesSelect').val(response.countries).trigger('change');
                }
                if (response.websites) {
                    $('#websitesSelect').val(response.websites).trigger('change');
                }
                if (response.tracked_words) {
                    $('#trackwordSelect').val(response.tracked_words).trigger('change');
                }
                window.isUpdatingArticles = false;
                updateArticlesWithClear();


            },
            error: function (xhr, status, error) {
                // Обработка ошибок
                console.error("Ошибка при получении данных из набора фильтров: ", status, error);
                window.isUpdatingArticles = false;
            }
        });
    });

});