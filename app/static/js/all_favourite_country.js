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

    function addArticles($list, articles) {
        articles.forEach(function (article) {
            var formattedDate = formatDateTime(article.created_at);

            // Используем поле "is_favorite" для определения иконки избранного
            var favoriteIcon = article.is_favorite ?
                `<a href="#" class="toggle-favorite" data-action="/remove_favorite/${article.website__id}/"><i class="fas fa-star"></i></a>` :
                `<a href="#" class="toggle-favorite" data-action="/add_favorite/${article.website__id}/"><i class="far fa-star"></i></a>`;

            var listItem = `
              <li data-id="${article.id}">
                  <div class="website-url highlight ">
                      <div class="country">${article.website__country__name}</div>
                        <!-- Добавляем иконку избранного здесь -->
                      <div class="article-title">
                          <a href="${article.url}">${article.title}</a>
                      </div>
                      <div class="article-date">
                          <span class="publish-date">${favoriteIcon} ${article.website__name}</span>
                          <span class="publish-date">${formattedDate}</span>
                      </div>
                  </div>
              </li>
          `;
            $list.prepend(listItem);
            $list.find(`li[data-id="${article.id}"]`).fadeIn(400);
            setTimeout(function () {
                $list.find('.website-url.highlight').removeClass('highlight');
            }, 399);
        });
    }


    function updateArticlesWithClear() {
        var $list = $('.website-block ul');
        $list.empty();
        updateArticles();
    }

    function updateArticles() {
        var $list = $('.website-block ul');
        var onlyFavorites = $('#showOnlyFavorites').prop('checked');
        var updateUrl = "/api/articles_from_favourite_countries/";
        var websiteBlock = document.querySelector('.website-block');
        var countryCode = websiteBlock.id;
        if (onlyFavorites) {
            updateUrl += "?only_favorites=true";
            if (countryCode) {
                updateUrl += "&country=" + countryCode;
            }
        } else if (countryCode) {
            updateUrl += "?country=" + countryCode;
        }

        $.ajax({
            url: updateUrl,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
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
                    var excessArticles = $list.find('li').slice(100 - newArticles.length);
                    excessArticles.fadeOut(400, function () {
                        $(this).remove();
                    });

                    setTimeout(function () {
                        addArticles($list, newArticles);
                    }, 1000);
                }
            }
        });
    }
    $('#showOnlyFavorites').change(updateArticlesWithClear);
    updateArticles();
    setInterval(updateArticles, 15000);

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
                console.error("There was an error!");
                alert("Ошибка при выполнении операции.");
            }
        });
        setTimeout(function () {
            updateArticlesWithClear();
        }, 500);

    });

});