$(document).ready(function() {
    /*title modify start*/
    var titleElement = $('title')[0];
	var titleText = titleElement.textContent;
	var capitalizedTitle = titleText[0].toUpperCase() + titleText.substring(1);

	titleElement.textContent = capitalizedTitle;
    /*title modify end*/

    /*quantity modify start*/
    $(".qtyminus").on("click",function(){
        id = $(this).parent().parent().attr('id')
        var now = $(".qty").val();

        if (typeof now == 'undefined') {
            now = $('#count'+id).text();
            if ($.isNumeric(now)){
                if (parseInt(now) -1> 0)
                { now--;}
                $("#count"+id).text(now);
                window.location.href = window.location.origin + '/' + username + '/update/' + id + '/' + $("#count"+id).text()
            }
        }

        if ($.isNumeric(now)){
            if (parseInt(now) -1> 0)
            { now--;}
            $(".qty").val(now);
        }

    });

    $(".qtyplus").on("click",function(){
        id = $(this).parent().parent().attr('id')
        var now = $(".qty").val();

        if (typeof now == 'undefined') {
            now = $('#count'+id).text();
            if ($.isNumeric(now)){
                $("#count"+id).text(parseInt(now)+1);
                window.location.href = window.location.origin + '/' + username + '/update/' + id + '/' + $("#count"+id).text()
            }
        }

        if ($.isNumeric(now)){
            $(".qty").val(parseInt(now)+1);
        }
    });
    /*quantity modify end*/

    /*cart modify start*/
    if (typeof len !== 'undefined') {
        if (len == 0) {
            $('.Cart-Container').children().hide()
            $('.Cart-Container').append('<table><tr><td><h1>There is no item at all</h1></td></tr><tr><td><a href="../../username">Order?</a></td></tr></table>'.replace('username', username))
            $('.Cart-Container').css('display', 'flex')
            $('.Cart-Container').css('align-items', 'center')
            $('.Cart-Container').css('justify-content', 'center')
            $('.Cart-Container table').css('text-align', 'center')
        }     
    }
    
    $(".checkout .button").on("click",function(){
        window.location.href = window.location.origin + '/' + username + '/payment'
    });
    /*cart modify end*/

    /*phone modify start*/
    $('#phone').on('focus', function() {
        $(this).val('');
    }).on('input', function() {
        var phone = $(this).val().replace(/[^\d()-]/g, '');
        if (phone.length === 10) {
            phone = phone.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
            $(this).val(phone);
        }
    });
    /*phone modify end*/
    
    /*payment modify start*/
    if (typeof stripe !== 'undefined') {
        $('#adr').val(address.split('(')[0])
        $('#state').val(address.split('(')[1].replace(')', ''))

        var elements = stripe.elements();

        var style = {
            base: {
            color: '#32325d',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            backgroundColor: '#ffffff',
            fontSize: '20px',
            '::placeholder': {
                color: '#757575',
                fontSize: '14px'
            }
            },
            invalid: {
            color: '#fa755a',
            iconColor: '#fa755a'
            }
        };

        var card = elements.create('cardNumber', {style: style});
        card.mount('#card-number');

        var exp = elements.create('cardExpiry', {style: style});
        exp.mount('#card-exp');

        var cvc = elements.create('cardCvc', {style: style});
        cvc.mount('#card-cvc');

        function adapter(object) {
            object.addEventListener('change', function(event) {
                var displayError = $('#card-errors')[0];
                if (event.error) {
                    displayError.textContent = event.error.message;
                } else {
                    displayError.textContent = '';
                }
            });
        }

        adapter(card)
        adapter(exp)
        adapter(cvc)

        function stripeTokenHandler(token) {
            var form = $('#payment-form');
            var existingInput = $('input[name="stripeToken"]');
            if (existingInput.length === 0) {
                var hiddenInput = $('<input>').attr({
                    type: 'hidden',
                    name: 'stripeToken',
                    value: token.id
                });
                form.append(hiddenInput);
            } else {
                existingInput.val(token.id);
            }

            if (form[0].checkValidity()) {
                form.submit();
            } else {
                form[0].reportValidity()
            }
        }

        $("#payment-form .checkout_btn").on("click", function(e) {
            e.preventDefault();
            var cardData = {
            'name': $('#cname').val()
            };
            stripe.createToken(card, cardData).then(function(result) {
                var displayError = $('#card-errors')[0];
                if(result.error && result.error.message) {
                    displayError.textContent = result.error.message;
                } else {
                    displayError.textContent = '';
                    stripeTokenHandler(result.token);
                }
            });
        });
    }
    /*payment modify end*/

    /*supply modify start*/
    function renderType() {
        type_lst = types.split(', ')
        for (i=0; i<type_lst.length; i++) {
            $('#type').append('<option value="type" style="text-transform:Capitalize">type</option>'.replaceAll('type', type_lst[i]))
        }
        $('#type').css('text-transform', 'Capitalize')
    }

    function setUp(object) {
        $.ajax({
            url: $(object).attr('href'),
            success: function(data) {
                $(object).addClass('active')
                $('#main-content').html(data);
                if (object == '#add-pro-link') {
                    $('#supply-form').append($('<div>').attr({
                        id: 'message',
                        style: 'text-align: center; color: green',
                    }));
                    $('#message').text(message)
                    if (message.indexOf("failed") >= 0) {
                        $('#message').css('color', 'red')
                    }
                    renderType()
                }
            }
        });
    }

    if (message.length < 1) {
        setUp('#view-or-link')
    } else {
        setUp('#add-pro-link')
    }

    function addlink(object) {
        $(object).click(function(e) {
            current_active_id = $('.active').attr('id')
            if (current_active_id != $(this).attr('id')) {
                $('#'+current_active_id).removeClass('active')
            }
            e.preventDefault();
            $(this).addClass('active')
            
            $.ajax({
                url: $(this).attr('href'),
                success: function(data) {
                    $('#main-content').html(data);
                    if ($('#supply-form').length > 0) {
                        $('#supply-form').append($('<input>').attr({
                            type: 'hidden',
                            name: 'csrfmiddlewaretoken',
                            value: csrf_token
                        }));
                        renderType(type)
                    }
                }
            });
        });
    }

    addlink('#add-pro-link');
    addlink('#view-or-link');
    /*supply modify end*/
});