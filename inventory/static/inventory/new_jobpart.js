$(document).ready(function() {
    $('select[name=quantity]').empty(); // quantity selection is intially filled with placeholder values, so empty out upon load (to be populated with true values upon selecting part)
    $('select[name=part]').change(function(){ // occurs when selecting a new part
        // empty out any current quantity / price values
        $('select[name=quantity]').empty(); 
        $('input[name=unit_price]').val('');
        part_id = $(this).val();
        if(part_id) {
        request_url = "/parts/get_data/" + part_id; // get selected part data with ajax call
        $.ajax({
            url: request_url,
            success: function(data){
                json = JSON.parse(data);
                // populate fields with selected part's data
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