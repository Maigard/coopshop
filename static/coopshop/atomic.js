jQuery(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
             var cookies = document.cookie.split(';');
             for (var i = 0; i < cookies.length; i++) {
                 var cookie = jQuery.trim(cookies[i]);
                 // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

updateOrder = function(prodId, quantity, description, price) {
	if(quantity > 0) {
		var quantity = $("<input>").attr({type: "text", name: "quantity", value:quantity, class:"short" });
		quantity.keyup(function() {
			if( $(this).val() != "") {
				$.post(cartUrl,
					{ "quantity": $(this).val(),
					  "productId": prodId,
					  "action": "setOrderItem"},
					function(data) {
						updateOrder(data.item.prodId, data.item.quantity, data.item.description, data.item.price);
						updateTotals(data.subtotal, data.tax, data.nonmemberFee, data.total);
					},
					"json"
				);
			}
		});
		row = $("<tr>").attr({id: "item-"+prodId});
		row.append($("<td>").append(quantity));
		row.append($("<td>").append(description));
		row.append($("<td>").append(price.toFixed(2)));
		newrow = $("#item-"+prodId);
		$("#item-empty").remove();
		if(newrow.length != 0) {
			newrow.replaceWith(row);
		} else {
			$(".receipt .top").before(row);
		}
		quantity.focus();
	} else {
		$("#item-"+prodId).remove();
	}

}

updateTotals = function(subtotal, tax, nonmemberFee, total) {
	$("#subtotal").text("$"+subtotal.toFixed(2));
	$("#tax").text("$"+tax.toFixed(2));
	$("#nonmemberFee").text("$"+nonmemberFee.toFixed(2));
	$("#total").text("$"+total.toFixed(2));
}

initializeOrder = function(order) {
	$.each(order.items, function(prodId, prod) {
		updateOrder(prodId, prod.quantity, prod.description, prod.price);
	});
	updateTotals(order.subtotal, order.tax, order.nonmemberFee, order.total);
}

$(document).ready(function(){
        $( ".bin form").each(function() {
                $(this).submit( function() {
                        $.post(cartUrl,
                                        $(this).serialize(),
                                        function(data) {
                                        	updateOrder(data.item.prodId, data.item.quantity, data.item.description, data.item.price);
                                        	updateTotals(data.subtotal, data.tax, data.nonmemberFee, data.total);
					},
					"json"
                                );
			return false;
                });
        });
});

$(function() {
        $( "#dialog" ).dialog({
                autoOpen: false,
                modal: true,
                //show: "drop",
                position: ['right', 'top'],
                show: {"effect": "drop", "direction": "right"},
                hide: {"effect": "drop", "direction": "right"},
                buttons: [
                {
                        text: "Cancel",
                        click: function() { $(this).dialog("close"); }
                },
                {
                        text: "Ok",
                        click: function() {
                                $("#loginForm").submit();
                        }
                }
        ]});
        $( "#login" ).click(function() {
                $("#dialog").dialog("open");
        });
        $( "#dialog > form").submit(function() {
                $("input[name='next']").val(document.URL);
        });
});
