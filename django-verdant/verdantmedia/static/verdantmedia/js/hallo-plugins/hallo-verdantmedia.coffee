# plugin for hallo.js to allow inserting media

(($) ->
    $.widget "IKS.halloverdantmedia",
        options:
            uuid: ''
            editable: null

        populateToolbar: (toolbar) ->
            widget = this

            # Create an element for holding the button
            button = $('<span></span>')
            button.hallobutton
                uuid: @options.uuid
                editable: @options.editable
                label: 'Media'
                icon: 'icon-media'
                command: null

            # Append the button to toolbar
            toolbar.append button

            button.on "click", (event) ->
                lastSelection = widget.options.editable.getSelection()
                insertionPoint = $(lastSelection.endContainer).parentsUntil('.richtext').last()
                ModalWorkflow
                    url: '/admin/media/chooser/' # TODO: don't hard-code this, as it may be changed in urls.py
                    responses:
                        mediaChosen: (mediaData) ->
                            elem = $(mediaData).get(0)
                            if insertionPoint.length
                                # we were inside an element, so insert before it
                                insertionPoint.before(elem)
                            else
                                lastSelection.insertNode(elem)

                            if elem.getAttribute('contenteditable') == 'false'
                                insertRichTextDeleteControl(elem)
                            widget.options.editable.element.trigger('change')
)(jQuery)