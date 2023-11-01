$(document).ready(function() {
  $(".toggle-country-favorite").click(function(e){
      e.preventDefault();
      let $this = $(this);
      let actionUrl = $this.data('action');

      $.ajax({
          url: actionUrl,
          method: 'GET',
          dataType: 'json',
          success: function(data){
              if(data.status == "added"){
                  $this.children('i').removeClass('far').addClass('fas'); // изменяем на полную звезду
                  $this.data('action', actionUrl.replace('add_favorite_country', 'remove_favorite_country'));
              } else if(data.status == "removed") {
                  $this.children('i').removeClass('fas').addClass('far'); // изменяем на пустую звезду
                  $this.data('action', actionUrl.replace('remove_favorite_country', 'add_favorite_country'));
              } else if(data.status == "error") {
                  alert("Ошибка: " + data.message);
              }
          },
          error: function(errorData){
              console.error("There was an error!");
              alert("Ошибка при выполнении операции.");
          }
      });
  });
});
