// feature detection for drag&drop upload

var isAdvancedUpload = function()
    {
        var div = document.createElement( 'div' );
        return ( ( 'draggable' in div ) || ( 'ondragstart' in div && 'ondrop' in div ) ) && 'FormData' in window && 'FileReader' in window;
    }();


// applying the effect for every form
$(document).ready(function() {
    $( '.box' ).each( function()
    {
        var $form		 = $( this ),
            $input		 = $form.find( 'input[type="file"]' ),
            $label		 = $form.find( 'label' ),
            $errorMsg	 = $form.find( '.box__error span' ),
            $restart	 = $form.find( '.box__restart' ),
            droppedFiles = false,
            showFiles	 = function( files )
            {
				switch(true) {
					case (files.length >= 2 && files.length <= 4):
						$label.text(( $input.attr( 'data-multiple-caption' ) || '' ).replace( '{count}', files.length ));
						$("#first").attr("style", "visibility: visible;");
						$("#launch").attr("class", "box__button")
						$("#launch").attr("class", "box__button ready")
						break;
					case (files.length > 4 && files.length <= 7):
						$label.text(( $input.attr( 'data-multiple-caption' ) || '' ).replace( '{count}', files.length ));
						$("#first").attr("style", "visibility: visible;");
						$("#second").attr("style", "visibility: visible;");
						$("#launch").attr("class", "box__button ready")
						break;
					case (files.length > 8 && files.length <= 10):
						$label.text(( $input.attr( 'data-multiple-caption' ) || '' ).replace( '{count}', files.length ));
						$("#first").attr("style", "visibility: visible;");
						$("#second").attr("style", "visibility: visible;");
						$("#third").attr("style", "visibility: visible;");
						$("#launch").attr("class", "box__button ready")
						break;
					default:
						$label.text( "Select between 2 and 10 pictures" );
						$("#first").attr("style", "visibility: hidden;");
						$("#second").attr("style", "visibility: hidden;");
						$("#third").attr("style", "visibility: hidden;");
						$("#launch").attr("class", "box__button")
						break;
				}
          //      $label.text( files.length > 1 ? ( $input.attr( 'data-multiple-caption' ) || '' ).replace( '{count}', files.length ) : files[ 0 ].name );
            };

        // letting the server side to know we are going to make an Ajax request
        $form.append( '<input type="hidden" name="ajax" value="1" />' );

        // automatically submit the form on file select
        $input.on( 'change', function( e )
        {
            showFiles( e.target.files );
            
        });


        // drag&drop files if the feature is available
        if( isAdvancedUpload )
        {
            $form
            .addClass( 'has-advanced-upload' ) // letting the CSS part to know drag&drop is supported by the browser
            .on( 'drag dragstart dragend dragover dragenter dragleave drop', function( e )
            {
                // preventing the unwanted behaviours
                e.preventDefault();
                e.stopPropagation();
            })
            .on( 'dragover dragenter', function() //
            {
                $form.addClass( 'is-dragover' );
            })
            .on( 'dragleave dragend drop', function()
            {
                $form.removeClass( 'is-dragover' );
            })
            .on( 'drop', function( e )
            {
                droppedFiles = e.originalEvent.dataTransfer.files; // the files that were dropped
                showFiles( droppedFiles );
            });
        }


        // if the form was submitted

        $form.on( 'submit', function( e )
        {
            // preventing the duplicate submissions if the current one is in progress
            if( $form.hasClass( 'is-uploading' ) ) return false;
			if( !$(".box__button").hasClass("ready") ) return false;
            $form.addClass( 'is-uploading' ).removeClass( 'is-error' );

            if( isAdvancedUpload ) // ajax file upload for modern browsers
            {
                e.preventDefault();

                // gathering the form data
                var ajaxData = new FormData( $form.get( 0 ) );
                if( droppedFiles )
                {
                    $.each( droppedFiles, function( i, file )
                    {
                        ajaxData.append(i, file );
                    });
                }
                console.log(ajaxData)
                // ajax request
                $.ajax(
                {
                    url: 			$form.attr( 'action' ),
                    type:			$form.attr( 'method' ),
                    data: 			ajaxData,
                    dataType:		'json',
                    cache:			false,
                    contentType:	false,
                    processData:	false,
                    complete: function()
                    {
                        $form.removeClass( 'is-uploading' );
                    },
                    success: function( data )
                    {
                        $form.addClass( data.success == true ? 'is-success' : 'is-error' );
                        if( !data.success ) $errorMsg.text( data.error );
						console.log('pressed');
                		window.location = 'http://localhost:8000/es_tool/ranking.html?target=cluster0';
                    },
                    error: function()
                    {
                        alert( 'Error. Please, contact the webmaster!' );
                    }
                });
            }
            else // fallback Ajax solution upload for older browsers
            {
                var iframeName	= 'uploadiframe' + new Date().getTime(),
                    $iframe		= $( '<iframe name="' + iframeName + '" style="display: none;"></iframe>' );

                $( 'body' ).append( $iframe );
                $form.attr( 'target', iframeName );

                $iframe.one( 'load', function()
                {
                    var data = $.parseJSON( $iframe.contents().find( 'body' ).text() );
                    $form.removeClass( 'is-uploading' ).addClass( data.success == true ? 'is-success' : 'is-error' ).removeAttr( 'target' );
                    if( !data.success ) $errorMsg.text( data.error );
                    $iframe.remove();
                });
            }
        });


        // restart the form if has a state of error/success

        $restart.on( 'click', function( e )
        {
            e.preventDefault();
            $form.removeClass( 'is-error is-success' );
            $input.trigger( 'click' );
        });

        // Firefox focus bug fix for file input
        $input
        .on( 'focus', function(){ $input.addClass( 'has-focus' ); })
        .on( 'blur', function(){ $input.removeClass( 'has-focus' ); });
	});
});