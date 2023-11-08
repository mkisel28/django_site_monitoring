
$(document).ready(function(){
    $(document).on('click', '.toggle-favorite', function(e) {
        e.preventDefault();
        e.stopPropagation(); 
    let $this = $(this);
    let actionUrl = $this.data('action');
    let $icon = $this.find('i');

    $.ajax({
        url: actionUrl,
        method: 'GET',
        dataType: 'json',
        success: function(data){
            if(data.status == "added"){
                $icon.removeClass('far').addClass('fas');  // Замена на заполненную звезду
                $this.data('action', actionUrl.replace('add_favorite', 'remove_favorite'));
            } else if(data.status == "removed") {
                $icon.removeClass('fas').addClass('far');  // Замена на пустую звезду
                $this.data('action', actionUrl.replace('remove_favorite', 'add_favorite'));
            } else if(data.status == "error") {
                alert("Ошибка: " + data.message);
            }
        },
        error: function(errorData){
            console.error("Ошибка при выполнении операции.");
            alert("Ошибка при выполнении операции.");
        }
    });

  });
});