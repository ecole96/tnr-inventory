$(document).ready(function() {
    $('select[name=quantity]').empty();

    $('select[name=part]').change(function(){
        $('select[name=quantity]').empty();
        $('input[name=unit_price]').val('');
        part_id = $(this).val();
        if(part_id) {
        request_url = "/parts/get_data/" + part_id;
        $.ajax({
            url: request_url,
            success: function(data){
                json = JSON.parse(data);
                $('input[name=unit_price]').val(json.unit_price);
                for (i = 1; i <= json.quantity; i++) {
                    $('select[name=quantity]').append(
                        $('<option></option>').val(i).html(i)
                    );
                }
            }
        });
        }
        return false;
    })
});