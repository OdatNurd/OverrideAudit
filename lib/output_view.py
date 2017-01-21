import sublime
import sublime_plugin

###-----------------------------------------------------------------------------

def output_to_view(window,
                   title,
                   content,
                   reuse=True,
                   syntax=None,
                   clear=True,
                   settings=None):

    if not isinstance(content, str):
        content = "\n".join (content)

    view = None

    if reuse:
        for _view in window.views ():
            if _view.name () == title:
                view = _view
                break

    if view is None:
        view = window.new_file ()
        view.set_scratch (True)
        view.set_name (title)
        if syntax is not None:
            view.assign_syntax (syntax)

    else:
        view.set_read_only (False)

        if clear is True:
            view.sel ().clear ()
            view.sel ().add (sublime.Region (0, view.size ()))
            view.run_command ("left_delete")

        if window.active_view () != view:
            window.focus_view (view)

    if settings is not None:
        for setting in settings:
            view.settings ().set (setting, settings[setting])

    # Sace current buffer size, selection information and view position
    saved_size = view.size ()
    saved_sel = list(view.sel ())
    saved_position = view.viewport_position ()

    # Single select, position cursor at end of file, insert the data
    view.sel ().clear ()
    view.sel ().add (sublime.Region (saved_size, saved_size))
    view.run_command ("insert", {"characters": content})

    # If the last selection was at the end of the buffer, replace that selection
    # with the new end of the buffer so the relative position remains the same.
    if sublime.Region (saved_size, saved_size) == saved_sel[-1]:
        saved_sel[-1] = sublime.Region (view.size (), view.size ())

    # Clear current selection and add original selection back
    view.sel ().clear ()
    for region in saved_sel:
        view.sel ().add (region)

    view.set_viewport_position (saved_position, False)
    view.set_read_only (True)

###-----------------------------------------------------------------------------
