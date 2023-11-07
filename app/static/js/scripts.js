
$(document).ready(function() {
    function formatDateTime(dateTimeStr) {
      var date = new Date(dateTimeStr);
      var day = String(date.getDate()).padStart(2, '0');
      var month = String(date.getMonth() + 1).padStart(2, '0');
      var year = date.getFullYear();
      var hours = String(date.getHours()).padStart(2, '0');
      var minutes = String(date.getMinutes()).padStart(2, '0');
  
      return `${day}.${month}.${year} г. ${hours}:${minutes}`;
  }


        function updateArticles() {
            // Получаем все website IDs сразу
            var websiteIds = $('.website-block').map(function() {
                return $(this).data('id'); // Извлекаем ID напрямую из data-id
            }).get();

            // Отправляем один запрос с этими IDs
            $.ajax({
                url: "/api/websites/", // Укажите здесь путь к вашему новому API
                type: 'GET',
                data: { 'website_ids[]': websiteIds },
                dataType: 'json',
                success: function(data) {
                    $('.website-block').each(function() {
                        var $block = $(this);
                        var websiteId = $block.data('id').toString(); // Преобразуем ID в строку для доступа к свойствам объекта
                        var articles = data.websites[websiteId];
                        var $list = $block.find('#website-list');
                        
                        // Теперь мы можем использовать похожую логику на ту, что у вас уже есть, для обновления статей для каждого сайта
                        var currentIds = $list.find('li').map(function() {
                            return $(this).data('id');
                        }).get();

                        if (currentIds.length === 0) {
                            addArticles($list, articles);
                            return;
                        }

                        var newArticles = articles.filter(function(article) {
                            return !currentIds.includes(article.id);
                        });

                        if (newArticles.length) {
                            var excessArticles = $list.find('li').slice(3 - newArticles.length);
                            excessArticles.fadeOut(400, function() {
                                $(this).remove();
                            });

                            setTimeout(function() {
                                addArticles($list, newArticles);
                            }, 1000);
                        }
                    });
                }
            });
        }

        function addArticles($list, articles) {
            // Добавляем статьи в начало списка
            articles.forEach(function(article) {
                var formattedDate = formatDateTime(article.published_at);
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
            setTimeout(function() {
                $list.find('.website-url.highlight').removeClass('highlight');
            }, 399);
        }
      updateArticles() 
      setInterval(updateArticles, 15000); // обновляем каждые 10 секунд
  });
  


  
//   function updateArticles() {
//     $('.website-block').each(function() {
//         var $block = $(this);
//         var updateUrl = $block.data('api');

//         $.ajax({
//             url: updateUrl,
//             type: 'GET',
//             dataType: 'json',
//             success: function(data) {
//                 var $list = $block.find('#website-list');

//                 // Получаем список текущих ID статей
//                 var currentIds = $list.find('li').map(function() {
//                     return $(this).data('id');
//                 }).get();

//                 // Если список пуст, то сразу обновляем
//                 if (currentIds.length === 0) {
//                     addArticles($list, data.articles);
//                     return;
//                 }

//                 // Фильтруем новые статьи
//                 var newArticles = data.articles.filter(function(article) {
//                     return !currentIds.includes(article.id);
//                 });

//                 // Если есть новые статьи
//                 if (newArticles.length) {
//                     // Удаляем статьи, которые больше не умещаются в новую последовательность
//                     var excessArticles = $list.find('li').slice(3 - newArticles.length);
//                     excessArticles.fadeOut(400, function() {
//                         $(this).remove();
//                     });

//                     setTimeout(function() {
//                         addArticles($list, newArticles);
//                     }, 1000);
//                 }
//             }
//         });
//     });
// }